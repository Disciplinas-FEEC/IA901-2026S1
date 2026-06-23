import torch
import torch.distributed as dist
from torch.utils.data import (Dataset,
                              DataLoader)
from .metrics import ModifiedMIoU
import json
from tqdm import tqdm
from pathlib import Path


import json
import torch
from pathlib import Path
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

import torch
import json
from pathlib import Path
from tqdm import tqdm
from torch.utils.data import Dataset, DataLoader

@torch.no_grad() # Impede o PyTorch de guardar histórico de gradientes (economiza muita RAM)
def computeWeightsForLoss(train_dataset: Dataset,
                          classes: list[str],
                          file_path: Path, 
                          batch_size: int = 64,       
                          num_workers: int = 8,       
                          device: torch.device = torch.device('cuda:0')) -> torch.Tensor:
    
    print("\n[CPU] Arquivo de cache não encontrado. Calculando pesos das classes na CPU...")
            
    loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=False,         
        prefetch_factor=2         
    )
        
    K = len(classes)
    
    pos = torch.zeros(K, dtype=torch.float32)
    total_valido = torch.zeros((), dtype=torch.float32)
    
    for batch in tqdm(loader, desc="Calculando weights (Batch 64) - CPU Mode"):
        labels   = batch["labels"]
        mask     = batch["mask"]
        boundary = batch["boundary"]
        
        roi = ((mask * boundary) > 0).unsqueeze(1).float()   
        pos += (labels * roi).sum(dim=(0, 2, 3))
        total_valido += roi.sum()

    neg = total_valido - pos
    w = (neg / pos.clamp(min=1)).tolist()
    
    pesos_dict = {nome: round(wk**0.5, 2) for nome, wk in zip(classes, w)}

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(pesos_dict, f, indent=2)
    
    return torch.tensor([pesos_dict[c] for c in classes], dtype=torch.float32, device=device).view(-1, 1, 1)


def getWeightsForLoss(train_dataset: Dataset,
                      classes: list[str],
                      file_path: Path, 
                      batch_size: int = 64,
                      num_workers: int = 8,
                      device: torch.device = torch.device('cuda:0')) -> torch.Tensor:
    
    # Se o cache JSON já existir, carrega instantaneamente
    if file_path.exists():
        with open(file_path, 'r') as f:
            pesos_dict = json.load(f)
            
        if all(c in pesos_dict for c in classes):
            print(f"[GPU 0] Pesos de perda carregados do cache JSON diretamente para {device}.")
            return torch.tensor([pesos_dict[c] for c in classes], dtype=torch.float32, device=device).view(-1, 1, 1)
    
    # Se não existir, chama a função de processamento pesado na GPU 0
    return computeWeightsForLoss(train_dataset, classes, file_path, batch_size, num_workers, device)         


def make_poly_lr(warmup_iters, constant_iters, total_iters, power=0.9):
    """
    Fábrica do schedule de learning rate usado pelo LambdaLR (curva "poly"):
      - warmup linear de 0 -> 1 nas primeiras `warmup_iters` iterações;
      - patamar constante (=1) por `constant_iters` iterações;
      - decaimento polinomial (1 - t) ** power até `total_iters`.

    Retorna a função f(current_iter) -> fator multiplicativo do lr base.
    """
    def schedule(current_iter):
        if current_iter < warmup_iters:
            return float(current_iter) / float(max(1, warmup_iters))
        elif current_iter < (warmup_iters + constant_iters):
            return 1.0
        else:
            decay_iter = current_iter - (warmup_iters + constant_iters)
            decay_max  = total_iters - (warmup_iters + constant_iters)
            return (1.0 - (decay_iter / decay_max)) ** power

    return schedule


def salvar_checkpoint(path, modelo, otimizador, scheduler, iteracao_real, best_miou):
    """Salva o estado completo do treino para permitir resume."""
    torch.save({
        "model":         modelo.module.state_dict(),
        "optimizer":     otimizador.state_dict(),
        "scheduler":     scheduler.state_dict(),
        "iteracao_real": iteracao_real,
        "best_miou":     best_miou,
    }, path)


def gerador_infinito(dataloader):
    """
    No DDP, o sampler precisa saber qual a época atual para embaralhar
    os dados corretamente a cada ciclo.
    """
    epoca = 0
    while True:
        if hasattr(dataloader.sampler, "set_epoch"):
            dataloader.sampler.set_epoch(epoca)
        for batch in dataloader:
            yield batch
        epoca += 1


@torch.no_grad()
def avaliar(modelo, dataloader, device, num_classes, criterio):
    """
    Roda a mIoU modificada do paper + a loss média sobre o conjunto de validação.
    Cada processo varre a sua fatia; matriz de confusão e loss são somadas entre as GPUs.
    Retorna (loss, mIoU, IoU_por_classe).
    """
    modelo.eval()
    metric   = ModifiedMIoU(num_classes, device=device)
    loss_sum = torch.zeros((), device=device)
    n_lote   = torch.zeros((), device=device)
    for batch in dataloader:
        imagens  = batch["image"].to(device)
        labels   = batch["labels"].to(device)
        mask     = batch["mask"].to(device)
        boundary = batch["boundary"].to(device)
        roi = (mask * boundary).unsqueeze(1)
        logits = modelo(imagens)
        loss_map = criterio(logits, labels)
        loss_sum += (loss_map * roi).sum() / (roi.sum() * num_classes)
        n_lote   += 1
        metric.update(logits, labels, roi)

    metric.reduce()
    if dist.is_available() and dist.is_initialized():
        dist.all_reduce(loss_sum)
        dist.all_reduce(n_lote)

    miou, iou = metric.compute()
    modelo.train()
    return (loss_sum / n_lote).item(), miou, iou


# def train(modelo,
#           otimizador,
#           scheduler,
#           iterador,
#           iteracao,
#           writer_train,
#           writer_val,
#           best_mIoU,
#           iteracoes):
    
#     modelo.train()
#     otimizador.zero_grad()

#     if local_rank == 0:
#         print("Iniciando treinamento distribuído nas 2x TITAN Xp...")

#     passos_forward = 0

#     while iteracao_real < total_iters:
#         passos_forward += 1

#         batch         = next(iterador_dados)
#         imagens       = batch["image"].to(device)
#         mascaras_alvo = batch["labels"].to(device)
#         mask          = batch["mask"].to(device)
#         boundary      = batch["boundary"].to(device)

#         roi = (mask * boundary).unsqueeze(1)

#         eh_ultimo_micro = (passos_forward % passos_acumulacao == 0)
#         ctx_sync = contextlib.nullcontext() if eh_ultimo_micro else modelo.no_sync()
        
#         with ctx_sync:
#             logits = modelo(imagens)
#             loss_map = criterio(logits, mascaras_alvo)
#             perda_real = (loss_map * roi).sum() / (roi.sum() * num_classes)
#             train_metric.update(logits, mascaras_alvo, roi)
#             perda = perda_real / passos_acumulacao
#             perda.backward()
        
#         if passos_forward % passos_acumulacao == 0:
#             otimizador.step()
#             scheduler.step()
#             otimizador.zero_grad()
#             iteracao_real += 1
            
#             if local_rank == 0 and iteracao_real % 100 == 0:
#                 lr_atual = scheduler.get_last_lr()[0]
#                 print(f"Iteração [{iteracao_real}/{total_iters}] | Loss: {perda_real.item():.4f}")
#                 writer_train.add_scalar("loss", perda_real.item(), iteracao_real)
#                 writer_train.add_scalar("lr",   lr_atual,          iteracao_real)

#             if iteracao_real % eval_every == 0:
#                 train_metric.reduce()
#                 train_miou, train_iou = train_metric.compute()
#                 val_loss, val_miou, val_iou = avaliar(
#                     modelo, dataloader_val, device, num_classes, criterio)

#                 if local_rank == 0:
#                     print(f"  [VAL] iter {iteracao_real} | mIoU treino: {train_miou:.4f} | "
#                           f"mIoU val: {val_miou:.4f} | loss val: {val_loss:.4f}")
#                     writer_train.add_scalar("mIoU", train_miou, iteracao_real)
#                     writer_val.add_scalar("mIoU",   val_miou,   iteracao_real)
#                     writer_val.add_scalar("loss",   val_loss,   iteracao_real)
#                     for nome, tr_c, va_c in zip(CLASSES2EVAL + ["background"],
#                                                 train_iou.tolist(), val_iou.tolist()):
#                         writer_train.add_scalar(f"IoU/{nome}", tr_c, iteracao_real)
#                         writer_val.add_scalar(f"IoU/{nome}",   va_c, iteracao_real)
                    
#                     if val_miou > best_miou:
#                         best_miou = val_miou
#                         torch.save(modelo.module.state_dict(),
#                                    CHECKPOINT_DIR / "best.pth")
#                         print(f"  >> novo melhor mIoU val: {val_miou:.4f} (salvo em best.pth)")

#                 train_metric.reset()

#             if local_rank == 0 and iteracao_real % ckpt_every == 0:
#                 salvar_checkpoint(CHECKPOINT_DIR / "latest.pth", modelo, otimizador,
#                                   scheduler, iteracao_real, best_miou)