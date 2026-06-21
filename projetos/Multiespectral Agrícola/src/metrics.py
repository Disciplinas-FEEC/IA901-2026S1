import torch
import torch.distributed as dist
from tqdm.auto import tqdm


class ModifiedMIoU:
    """
    mIoU modificada do Agriculture Vision, que acomoda labels sobrepostas.

    Para cada pixel temos:
      - x : a predição (uma única classe), obtida pelo canal sigmoid de maior
            confiança; se nenhum canal passa do threshold, x = background.
      - Y : o conjunto de labels verdadeiras no pixel (pode ter mais de uma);
            se nenhuma anomalia está presente, Y = {background}.

    Acumula uma matriz de confusão M de tamanho c x c (c = K classes + background,
    com background no último índice) seguindo as regras do paper:
      (1) Se x ∈ Y:  M[y, y] += 1   para todo y ∈ Y   (predição correta vira TP
                                                        de todas as labels do pixel)
      (2) Caso contrário: M[x, y] += 1 para todo y ∈ Y

    Ao final:
        IoU_c = M[c, c] / (linha_c + coluna_c - M[c, c])
        mIoU  = média dos IoU_c
    """

    def __init__(self, num_classes, threshold=0.5, device="cpu"):
        self.num_classes = num_classes      # K (classes de anomalia)
        self.c  = num_classes + 1           # + background
        self.bg = num_classes               # índice do background (último)
        self.threshold = threshold
        self.confmat = torch.zeros(self.c, self.c, dtype=torch.float64, device=device)

    @torch.no_grad()
    def update(self, logits, labels, roi):
        # 1. Predição única por pixel: classe de maior probabilidade, ou background.
        probs = torch.sigmoid(logits)
        max_prob, argmax_k = probs.max(dim=1)                       # (N, H, W)
        x = torch.where(max_prob > self.threshold,
                        argmax_k,
                        torch.full_like(argmax_k, self.bg))         # (N, H, W)

        # 2. Conjunto de labels Y por pixel, com background como canal extra.
        bg_label = (labels.sum(dim=1, keepdim=True) == 0).to(labels.dtype)  # (N,1,H,W)
        L = torch.cat([labels, bg_label], dim=1)                    # (N, c, H, W)

        if roi.dim() == 4:
            roi = roi[:, 0]
        roi = roi > 0                                               # (N, H, W)
        x = x[roi]                                                  # (P,)
        L = L.permute(0, 2, 3, 1)[roi]                              # (P, c)

        # 4. x ∈ Y ?  ->  membership da classe predita no pixel.
        correct = L.gather(1, x.view(-1, 1)).squeeze(1) > 0         # (P,)

        # predição correta -> incrementa a diagonal de cada y in Y.
        diag_add = L[correct].sum(dim=0)                            # (c,)
        self.confmat += torch.diag(diag_add).to(self.confmat)

        # predição errada -> M[x, y] += 1 para cada y in Y.
        self.confmat.index_add_(0, x[~correct], L[~correct].to(self.confmat))

    def reduce(self):
        # Soma as matrizes de confusão entre os processos DDP (se ativo).
        if dist.is_available() and dist.is_initialized():
            dist.all_reduce(self.confmat, op=dist.ReduceOp.SUM)

    def compute(self):
        """Retorna (mIoU, IoU_por_classe) — vetor de tamanho c (último = background)."""
        tp   = torch.diag(self.confmat)
        pred = self.confmat.sum(dim=1)     # linha  = predições
        tgt  = self.confmat.sum(dim=0)     # coluna = alvos
        iou  = tp / (pred + tgt - tp + 1e-8)
        return iou.mean().item(), iou

    def reset(self):
        self.confmat.zero_()
