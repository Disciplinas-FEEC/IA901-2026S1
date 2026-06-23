import pickle
import random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np
import torch
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
from matplotlib.patches import Patch
from PIL import Image
from tqdm import tqdm
import yaml
import matplotlib
from .constants import CLASSES_DICT, BAND_DICT


def _render_plots_data(secao: str, plots_data: list, sample_id: str = "") -> None:
    n_cols = len(plots_data)
    fig, axes = plt.subplots(1, n_cols, figsize=(4 * n_cols, 4), squeeze=False)
    fig.suptitle(f"[{secao}]  ID: {sample_id}", fontsize=13, fontweight="bold")
    for col, (titulo, data, cmap, vmin, vmax, has_colorbar) in enumerate(plots_data):
        ax = axes[0][col]
        im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_title(titulo, fontsize=10)
        ax.set(xticks=[], yticks=[])
        for spine in ax.spines.values():
            spine.set(edgecolor="black", linewidth=0.8)
        if has_colorbar:
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    plt.tight_layout()
    plt.show()


def _build_rgb(image_np: np.ndarray, input_channels: str) -> np.ndarray:
    idx = {c: i for i, c in enumerate(input_channels)}
    H, W = image_np.shape[1], image_np.shape[2]
    rgb = np.stack([
        image_np[idx[c]].numpy() 
        if c in idx 
        else np.zeros((H, W),dtype=np.float32)
        for c in ('r', 'g', 'b')
    ], axis=-1)
    return rgb


def printInput(image: torch.Tensor, input_channels: str, mask: torch.Tensor, id: str) -> None:
    idx   = {c: i for i, c in enumerate(input_channels)}
    rgb   = _build_rgb(image, input_channels)

    H, W = image.shape[1], image.shape[2]

    facecolor = 'black'
    # Linha 0: RGB composto + canais R, G, B com Reds/Greens/Blues, inválidos em preto
    row0 = [("RGB", rgb, None, None, None, False, facecolor)]
    for letra in ('r', 'g', 'b'):
        if letra in idx:
            canal = image[idx[letra]].numpy().copy()
            canal[(mask.numpy() == 0)] = np.nan
            row0.append((BAND_DICT[letra]['name'], canal,
                        BAND_DICT[letra]['cmap'],
                        BAND_DICT[letra]['vmin'],
                        BAND_DICT[letra]['vmax'],
                        BAND_DICT[letra]['colorbar'],
                        facecolor))

    # Linha 1: NIR, NDVI, NDWI
    row1 = []
    for letra in ('n', 'v', 'w'):
        if letra in idx:
            canal = image[idx[letra]].numpy().copy()
            if letra in ('v', 'w'):
                canal[(mask.numpy() == 0)] = np.nan
            row1.append((BAND_DICT[letra]['name'],
                         canal,
                         BAND_DICT[letra]['cmap'],
                         BAND_DICT[letra]['vmin'],
                         BAND_DICT[letra]['vmax'],
                         BAND_DICT[letra]['colorbar'],
                         facecolor))


    n_cols = max(len(row0), len(row1))
    n_rows = 2 if row1 else 1

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 4 * n_rows), squeeze=False)
    fig.suptitle(f"[INPUT]  ID: {id}", fontsize=13, fontweight="bold")

    for row_idx, plots_data in enumerate([row0, row1] if row1 else [row0]):
        for col in range(n_cols):
            ax = axes[row_idx][col]
            if col < len(plots_data):
                panel = plots_data[col]
                title, img, cmap, vmin, vmax, has_colorbar = panel[:6]
                facecolor = panel[6] if len(panel) > 6 else 'white'
                ax.set_facecolor(panel[6])
                im = ax.imshow(img, cmap=cmap, vmin=vmin, vmax=vmax)
                ax.set_title(title, fontsize=10)
                ax.set(xticks=[], yticks=[])
                for spine in ax.spines.values():
                    spine.set(edgecolor="black", linewidth=0.8)
                if has_colorbar:
                    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            else:
                ax.axis("off")

    plt.tight_layout()
    plt.show()


def printOutput(image: torch.Tensor,
                input_channels: str,
                classes2eval: list,
                labels: torch.Tensor,
                mask: torch.Tensor,
                id: str) -> None:

    labels_np = labels.numpy()
    idx_band = {c: i for i, c in enumerate(input_channels)}

    K, H, W = labels_np.shape
    rgb   = _build_rgb(image, input_channels)
    ALPHA = 0.5

    class_masks = []
    for k, class_name in enumerate(classes2eval):
        class_color = np.array(CLASSES_DICT.get(class_name)['color'], dtype=np.float32)
        mascara     = labels_np[k] > 0
        if mascara.sum() == 0:
            continue
        class_masks.append((class_name, class_color, mascara))

    def _masks_overlay_img(base):
        img = base.copy()
        for _, class_color, mascara in class_masks:
            img[mascara] = (1 - ALPHA) * base[mascara] + ALPHA * class_color
        return img

    # Faz a representação visual de um único valor escalar por pixel.
    def _to_rgb(canal, cmap_name, vmin, vmax, apply_roi=False):
        arr = canal.copy().astype(np.float32)
        if apply_roi:
            arr[mask.numpy() == 0] = np.nan
        colored = plt.get_cmap(cmap_name)(plt.Normalize(vmin=vmin, vmax=vmax)(arr))[:, :, :3].astype(np.float32)
        # if apply_roi and roi is not None:
        #     colored[~roi] = 0.0
        return colored

    overlays = [("RGB + Labels", _masks_overlay_img(rgb), None, None, None, False)]
    for letra, label in [('n', 'NIR'), ('v', 'NDVI'), ('w', 'NDWI')]:
        if letra in idx_band:
            base_rgb = _to_rgb(image[idx_band[letra]].numpy(),
                               BAND_DICT[letra]['cmap'],
                               BAND_DICT[letra]['vmin'],
                               BAND_DICT[letra]['vmax'],
                                apply_roi=(letra in ('v', 'w')))
            overlays.append((f"{label} + Labels", _masks_overlay_img(base_rgb), None, None, None, False))

    panels = []
    for class_name, class_color, mascara in class_masks:
        rgba = np.ones((H, W, 4), dtype=np.float32)
        rgba[mascara, :3] = class_color
        panels.append((class_name, rgba, None, None, None, False))

    _render_plots_data("OUTPUT — Overlays", overlays, id)
    _render_plots_data("OUTPUT — Classes",  panels,   id)


def printContext(mask: torch.Tensor,
                 boundary: torch.Tensor,
                 image:torch.Tensor,
                 input_channels: str,
                 id: str) -> None:
    mask_np = mask.numpy()
    boundary_np = boundary.numpy()
    rgb = _build_rgb(image, input_channels)

    plot_data = []
    plot_data.append(("Mask", mask_np, "gray", 0, 1, False))
    plot_data.append(("Boundary", boundary_np, "gray", 0, 1, False))
    roi     = np.expand_dims((mask_np > 0) & (boundary_np > 0), axis=-1)
    rgb_roi = np.where(roi, rgb, 0).astype(np.float32)
    plot_data.append(("ROI (RGB)", rgb_roi, None, None, None, False))

    _render_plots_data("Region of Interest (ROI)", plot_data, id)


def printSample(sample: dict) -> None:
    printInput(sample)
    printOutput(sample)
    printContext(sample)


def printSampleById(path: str) -> None:
    path = Path(path)
    img = Image.open(path)
    plt.imshow(img)
    plt.title(path.stem, fontsize=11)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def _limpa_mascara(mask, kernel, min_area):
    """Abertura + fechamento morfológico e remoção de blobs pequenos."""
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    n_comp, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    for i in range(1, n_comp):
        if stats[i, cv2.CC_STAT_AREA] < min_area:
            mask[labels == i] = 0
    return mask


def _desenha_contornos(base_uint8, mascaras_por_classe, roi, clean,
                       min_area=50, kernel_size=5):
    """
    Desenha, sobre uma cópia de base_uint8, o contorno de cada (nome, cor, mask).
    'clean=True' aplica limpeza morfológica (uso para predições).
    Retorna (overlay, lista de classes desenhadas).
    """
    overlay = base_uint8.copy()
    kernel  = np.ones((kernel_size, kernel_size), np.uint8)
    desenhadas = []
    for class_name, color, mask in mascaras_por_classe:
        m = mask.astype(np.uint8)
        if roi is not None:
            m = m & roi
        if m.sum() == 0:
            continue
        if clean:
            m = _limpa_mascara(m, kernel, min_area)
            if m.sum() == 0:
                continue
        contours, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cor = tuple(int(c * 255) for c in color)             # RGB 0-255
        cv2.drawContours(overlay, contours, -1, cor, 2)
        desenhadas.append((class_name, color))
    return overlay, desenhadas


def _overlay_mascaras(base_uint8, mascaras_por_classe, roi, clean,
                      min_area=50, kernel_size=5, alpha=0.5):
    """
    Pinta cada (nome, cor, mask) como overlay translúcido (preenchido) sobre uma
    cópia de base_uint8. 'clean=True' aplica limpeza morfológica (uso p/ predições).
    Retorna (overlay uint8, lista de classes desenhadas).
    """
    overlay = base_uint8.astype(np.float32)
    kernel  = np.ones((kernel_size, kernel_size), np.uint8)
    desenhadas = []
    for class_name, color, mask in mascaras_por_classe:
        m = mask.astype(np.uint8)
        if roi is not None:
            m = m & roi
        if m.sum() == 0:
            continue
        if clean:
            m = _limpa_mascara(m, kernel, min_area)
            if m.sum() == 0:
                continue
        cor = np.array([c * 255 for c in color], dtype=np.float32)   # RGB 0-255
        sel = m.astype(bool)
        overlay[sel] = (1 - alpha) * overlay[sel] + alpha * cor
        desenhadas.append((class_name, color))
    return overlay.astype(np.uint8), desenhadas


def _infer_probs(modelo, image, device):
    """Forward de inferência -> probabilidades (K, H, W)."""
    modelo.eval()
    if device is None:
        device = next(modelo.parameters()).device
    logits = modelo(image.unsqueeze(0).to(device))           # (1, K, H, W)
    return torch.sigmoid(logits)[0].cpu().numpy()            # (K, H, W)


@torch.no_grad()
def predict_and_show(modelo, sample: dict, threshold: float = 0.5,
                     min_area: int = 50, kernel_size: int = 5, device=None) -> None:
    """
    Roda a inferência e desenha os contornos das classes previstas sobre o RGB,
    no estilo das figuras do paper (com limpeza morfológica para dar o aspecto maciço).
    """
    probs = _infer_probs(modelo, sample["image"], device)
    rgb   = np.clip(_build_rgb(sample["image"], sample["input_channels"]), 0, 1)
    base  = (rgb * 255).astype(np.uint8)

    roi = None
    if sample.get("mask") is not None and sample.get("boundary") is not None:
        roi = ((sample["mask"].numpy() > 0) & (sample["boundary"].numpy() > 0)).astype(np.uint8)

    masks = [(n, CLASSES_DICT[n]['color'], probs[k] > threshold)
             for k, n in enumerate(sample["classes2eval"]) if n in CLASSES_DICT]
    overlay, desenhadas = _desenha_contornos(base, masks, roi, clean=True,
                                             min_area=min_area, kernel_size=kernel_size)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(overlay)
    ax.set_title(f"[PREDIÇÃO]  ID: {sample.get('id', '')}", fontsize=12, fontweight="bold")
    ax.axis("off")
    if desenhadas:
        ax.legend(handles=[Patch(edgecolor=cor, facecolor="none", label=nome)
                           for nome, cor in desenhadas],
                  loc="upper right", fontsize=9, framealpha=0.8)
    plt.tight_layout()
    plt.show()


@torch.no_grad()
def compare_prediction(modelo, sample: dict, threshold: float = 0.5,
                       min_area: int = 50, kernel_size: int = 5, device=None) -> None:
    """
    Compara Ground-Truth vs Predição lado a lado, mais um mapa de erros:
      [1] RGB + contornos do ground-truth
      [2] RGB + contornos da predição (limpa)
      [3] Mapa de erros COERENTE com a ModifiedMIoU (src/metrics.py): a predição é
          única por pixel (argmax acima do threshold, senão background) e "acerto"
          significa que a classe predita está entre as labels do pixel (x ∈ Y).
          verde=acerto de classe; azul=FN (era anomalia e o modelo não acertou a
          classe — previu fundo ou a classe errada); vermelho=FP (previu anomalia
          sobre fundo limpo); preto=fundo correto (TN)/fora do ROI.
    Também imprime o IoU por classe desta amostra.
    """
    image        = sample["image"]
    classes2eval = sample["classes2eval"]

    probs  = _infer_probs(modelo, image, device)             # (K, H, W) previsto
    labels = sample["labels"].numpy()                        # (K, H, W) GT binário
    rgb    = np.clip(_build_rgb(image, sample["input_channels"]), 0, 1)
    base   = (rgb * 255).astype(np.uint8)

    roi = None
    if sample.get("mask") is not None and sample.get("boundary") is not None:
        roi = ((sample["mask"].numpy() > 0) & (sample["boundary"].numpy() > 0)).astype(np.uint8)

    # Predição ÚNICA por pixel, igual à ModifiedMIoU (src/metrics.py): a classe de
    # maior probabilidade acima do threshold, ou background (índice K) se nenhuma passa.
    K = labels.shape[0]
    x = np.where(probs.max(0) > threshold, probs.argmax(0), K)   # (H, W); K = background

    # Overlay translúcido: GT (sem limpeza) e Predição (com limpeza). A predição usa
    # a classe vencedora por pixel (x == k), batendo com a métrica — não o multilabel cru.
    gt_masks   = [(n, CLASSES_DICT[n]['color'], labels[k] > 0)
                  for k, n in enumerate(classes2eval) if n in CLASSES_DICT]
    pred_masks = [(n, CLASSES_DICT[n]['color'], x == k)
                  for k, n in enumerate(classes2eval) if n in CLASSES_DICT]
    ov_gt,   des_gt   = _overlay_mascaras(base, gt_masks,   roi, clean=False)
    ov_pred, des_pred = _overlay_mascaras(base, pred_masks, roi, clean=True,
                                          min_area=min_area, kernel_size=kernel_size)

    # Mapa de erros coerente com a ModifiedMIoU: "acerto" = a classe predita por
    # pixel (x) está entre as labels verdadeiras do pixel (x ∈ Y, Y inclui background).
    bg_label = labels.sum(0) == 0                                   # pixel sem anomalia
    L        = np.concatenate([labels > 0, bg_label[None]], axis=0)  # (K+1, H, W) = Y
    correct  = np.take_along_axis(L, x[None], axis=0)[0]            # x ∈ Y ?

    x_is_anom   = x != K
    gt_has_anom = ~bg_label
    err = np.zeros((*x.shape, 3), dtype=np.uint8)                    # default preto (TN)
    err[x_is_anom & correct]      = (0, 200, 0)    # acerto de classe (verde)
    err[gt_has_anom & ~correct]   = (0, 0, 255)    # FN: era anomalia e o modelo não acertou
                                                   #     a classe (previu fundo ou classe errada)
    err[~gt_has_anom & x_is_anom] = (255, 0, 0)    # FP: previu anomalia sobre fundo limpo
    if roi is not None:
        err[roi == 0] = 0                                      # fora do ROI -> preto

    # IoU por classe desta amostra (dentro do ROI).
    print(f"IoU por classe — ID {sample.get('id', '')}:")
    ious = []
    for k, n in enumerate(classes2eval):
        p = probs[k] > threshold
        g = labels[k] > 0
        if roi is not None:
            p = p & (roi > 0)
            g = g & (roi > 0)
        inter = np.logical_and(p, g).sum()
        union = np.logical_or(p, g).sum()
        if union == 0:
            continue
        iou = inter / union
        ious.append(iou)
        print(f"  {n:20s} IoU = {iou:.3f}")
    if ious:
        print(f"  {'mIoU (classes presentes)':20s} = {np.mean(ious):.3f}")

    # ROI da amostra (mask & boundary): RGB recortado, preto fora do ROI.
    roi_vis = base.copy()
    if roi is not None:
        roi_vis[roi == 0] = 0

    # Plot
    paineis = [
        ("Ground-Truth", ov_gt,   des_gt),
        ("Predição",     ov_pred, des_pred),
        ("Mapa de erros", err,    None),
        ("ROI (mask & boundary)", roi_vis, None),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(24, 6))
    fig.suptitle(f"[GT vs PREDIÇÃO]  ID: {sample.get('id', '')}", fontsize=13, fontweight="bold")
    for ax, (titulo, img, desenhadas) in zip(axes, paineis):
        ax.imshow(img)
        ax.set_title(titulo, fontsize=11)
        ax.axis("off")
        if desenhadas:
            ax.legend(handles=[Patch(facecolor=cor, edgecolor="black", label=nome)
                               for nome, cor in desenhadas],
                      loc="upper right", fontsize=8, framealpha=0.8)
    # Legenda do mapa de erros
    axes[2].legend(handles=[
        Patch(facecolor=(0, 200/255, 0), label="Acerto de classe (TP)"),
        Patch(facecolor=(0, 0, 1),       label="FN: anomalia não acertada (fundo ou classe errada)"),
        Patch(facecolor=(1, 0, 0),       label="FP: anomalia prevista sobre fundo"),
        Patch(facecolor=(0, 0, 0), edgecolor="gray",
              label="Fundo correto (TN) / fora do ROI"),
    ], loc="upper right", fontsize=8, framealpha=0.8)
    plt.tight_layout()
    plt.show()


@torch.no_grad()
def test_model(weights_path,
               sample_id: str = None,
               *,
               datamodule,
               mode: str = "compare",
               threshold: float = 0.5,
               device=None,
               seed: int = None) -> dict:
    """
    Carrega um checkpoint treinado e gera a predição de uma amostra do split de TEST.

    - weights_path: caminho do .pth (ex.: '../experiments/checkpoints/rgb/best.pth').
                    Aceita tanto o state_dict puro (best.pth/final.pth) quanto o
                    checkpoint completo (latest.pth, que tem a chave 'model').
    - sample_id:    ID da amostra (ex.: '10495_001'). Se None, sorteia uma
                    amostra aleatória do split de test.
    - datamodule:   AgricultureVisionDataModule já com setup() feito. A config do
                    modelo (canais e classes) é lida dele para casar com o treino.
    - mode:         'compare' -> compare_prediction (GT vs predição + mapa de
                    erros + IoU); 'predict' -> predict_and_show (só a predição).
    - threshold / device: repassados para a inferência.
    - seed:         semente do sorteio aleatório (reprodutibilidade).

    Retorna a amostra (dict) usada na predição.
    """
    from .constants import IMAGENET_MEAN, IMAGENET_STD
    from .model import FPN_ResNet50_Segmentation

    if device is None:
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device)

    input_channels = datamodule.input_channels
    classes2eval   = datamodule.classes2eval

    # 1. Reconstrói o modelo com a MESMA config do treino e carrega os pesos.
    ch_mean = [IMAGENET_MEAN.get(c, 0.0) for c in input_channels]
    ch_std  = [IMAGENET_STD.get(c, 1.0)  for c in input_channels]
    modelo = FPN_ResNet50_Segmentation(
        num_classes=len(classes2eval),
        input_mean=ch_mean, input_std=ch_std,
        input_channels=input_channels,
    ).to(device)

    estado = torch.load(str(weights_path), map_location=device)
    if isinstance(estado, dict) and "model" in estado:
        estado = estado["model"]            # checkpoint completo (latest.pth)
    modelo.load_state_dict(estado)
    modelo.eval()

    dataset = datamodule.test_dataset

    # 2. Seleciona a amostra: por ID ou aleatória (toda amostra tem anomalia).
    if sample_id is not None:
        sample = dataset[dataset.lista_ids.index(sample_id)]
    else:
        sample = dataset[random.Random(seed).randrange(len(dataset))]

    # 3. Gera a visualização.
    if mode == "compare":
        compare_prediction(modelo, sample, threshold=threshold, device=device)
    elif mode == "predict":
        predict_and_show(modelo, sample, threshold=threshold, device=device)

    return


def evaluate_model(weights_path,
                   *,
                   datamodule,
                   device=None,
                   save_path=None,
                   usar_cache: bool = False,
                   mostrar: bool = True) -> tuple:
    """
    Carrega um checkpoint treinado e avalia a mIoU modificada sobre o split de
    TESTE inteiro. Irmão do test_model (que só visualiza uma amostra). Exclusivo
    do teste — treino e validação são avaliados pelo main.py durante o treino.

    - weights_path: caminho do .pth. Aceita o state_dict puro (best.pth/final.pth)
                    ou o checkpoint completo (latest.pth, com a chave 'model').
    - datamodule:   AgricultureVisionDataModule já com setup() feito. A config do
                    modelo (canais e classes) é lida dele para casar com o treino.
    - device:       destino dos tensores; cuda:0 se disponível.
    - save_path:    se fornecido, grava o resultado em JSON (mIoU + IoU por classe
                    + o checkpoint avaliado).
    - usar_cache:   se True e save_path já existir, LÊ o JSON e retorna sem
                    recomputar. Padrão False (sempre reavalia, evitando devolver
                    um resultado velho de outro checkpoint sem querer).
    - mostrar:      se True, imprime a mIoU e o IoU por classe.

    Retorna (mIoU: float, iou_por_classe: dict {nome: IoU}), background no fim.
    """
    import json
    from .constants import IMAGENET_MEAN, IMAGENET_STD
    from .model import FPN_ResNet50_Segmentation
    from .metrics import ModifiedMIoU

    # Atalho: lê do cache se pedido e o arquivo existir (pula modelo + varredura).
    if usar_cache and save_path is not None and Path(save_path).exists():
        with open(save_path) as f:
            cache = json.load(f)
        if mostrar:
            print(f"[TESTE] (cache: {save_path}) mIoU modificada: {cache['mIoU']:.4f}\n")
            for nome, iou_c in cache["iou_por_classe"].items():
                print(f"  IoU[{nome:22s}] = {iou_c:.4f}")
        return cache["mIoU"], cache["iou_por_classe"]

    if device is None:
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device)

    input_channels = datamodule.input_channels
    classes2eval   = datamodule.classes2eval

    # 1. Reconstrói o modelo com a MESMA config do treino e carrega os pesos.
    ch_mean = [IMAGENET_MEAN.get(c, 0.0) for c in input_channels]
    ch_std  = [IMAGENET_STD.get(c, 1.0)  for c in input_channels]
    modelo = FPN_ResNet50_Segmentation(
        num_classes=len(classes2eval),
        input_mean=ch_mean, input_std=ch_std,
        input_channels=input_channels,
    ).to(device)

    estado = torch.load(str(weights_path), map_location=device)
    if isinstance(estado, dict) and "model" in estado:
        estado = estado["model"]            # checkpoint completo (latest.pth)
    modelo.load_state_dict(estado)

    # 2. Varre o teste acumulando só a matriz de confusão da mIoU modificada.
    #    Sem loss: aqui não há treino, então um criterio seria peso morto.
    modelo.eval()
    metric = ModifiedMIoU(len(classes2eval), device=device)
    with torch.no_grad():
        for batch in tqdm(datamodule.test_dataloader(),
                          desc="Avaliando no teste", leave=False):
            imagens  = batch["image"].to(device)
            labels   = batch["labels"].to(device)
            mask     = batch["mask"].to(device)
            boundary = batch["boundary"].to(device)
            roi = (mask * boundary).unsqueeze(1)
            metric.update(modelo(imagens), labels, roi)
    metric.reduce()                       # no-op fora do DDP
    miou, iou = metric.compute()

    iou_por_classe = dict(zip(list(classes2eval) + ["background"], iou.tolist()))

    if mostrar:
        print(f"[TESTE] mIoU modificada: {miou:.4f}\n")
        for nome, iou_c in iou_por_classe.items():
            print(f"  IoU[{nome:22s}] = {iou_c:.4f}")

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w") as f:
            json.dump({
                "checkpoint":     str(weights_path),
                "mIoU":           miou,
                "iou_por_classe": iou_por_classe,
            }, f, indent=2)
        print(f"Resultado salvo em {save_path}")

    return miou, iou_por_classe


def printColorPalette() -> None:
    ID_TO_CLASS = {info['id']: name for name, info in CLASSES_DICT.items()}
    items = sorted(CLASSES_DICT.values(), key=lambda x: x['id'])
    n = len(items)

    fig, axes = plt.subplots(1, n, figsize=(n * 1.4, 1.8))
    for item, ax in zip(items, axes):
        ax.set_facecolor(item['color'])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f"{item['id']}\n{ID_TO_CLASS[item['id']]}", fontsize=7, labelpad=4)
        for spine in ax.spines.values():
            spine.set(edgecolor="black", linewidth=0.5)

    plt.suptitle("Paleta de cores das classes", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.show()


# def read_parameters_inputted_by_user() -> dict:
#     with open(_CONFIG_PATH, "r") as f:
#         config = yaml.safe_load(f)
#     return config


class exploratory_data_analysis:

    @staticmethod
    def get_stats_from_splits(train_dataset, val_dataset, test_dataset):
        CACHE_DIR = Path("../data/cache")
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        cache_train = CACHE_DIR / "metricas_train.pkl"
        cache_val   = CACHE_DIR / "metricas_val.pkl"
        cache_test  = CACHE_DIR / "metricas_test.pkl"

        if cache_train.exists() and cache_val.exists() and cache_test.exists():
            metricas_train = exploratory_data_analysis.carregar_metricas(cache_train)
            metricas_val   = exploratory_data_analysis.carregar_metricas(cache_val)
            metricas_test  = exploratory_data_analysis.carregar_metricas(cache_test)
        else:
            metricas_train = exploratory_data_analysis.extrair_metricas(train_dataset)
            metricas_val   = exploratory_data_analysis.extrair_metricas(val_dataset)
            metricas_test  = exploratory_data_analysis.extrair_metricas(test_dataset)

            exploratory_data_analysis.salvar_metricas(metricas_train, cache_train)
            exploratory_data_analysis.salvar_metricas(metricas_val,   cache_val)
            exploratory_data_analysis.salvar_metricas(metricas_test,  cache_test)
        
        return metricas_train, metricas_val, metricas_test

    @staticmethod
    def _calcular_ndvi(rgb_path, nir_path):
        rgb = mpimg.imread(rgb_path)
        nir = mpimg.imread(nir_path).astype(float)
        red = rgb[:, :, 0].astype(float)
        denominador = nir + red
        numerador   = nir - red
        return np.divide(numerador, denominador, out=np.zeros_like(denominador), where=(denominador != 0))
    
    @staticmethod
    def _calcular_ndwi(rgb_path, nir_path):
        rgb = mpimg.imread(rgb_path)
        nir = mpimg.imread(nir_path).astype(float)
        green = rgb[:, :, 1].astype(float)
        denominador = nir + green
        numerador   = nir - green
        return np.divide(numerador, denominador, out=np.zeros_like(denominador), where=(denominador != 0))

    @staticmethod
    def _fusao_labels(name_arquivo, labels_dirs):
        mascara_final       = None
        classes_encontradas = []

        for label_dir in labels_dirs:
            mascara_atual = mpimg.imread(label_dir / name_arquivo)
            if np.any(mascara_atual > 0):
                classes_encontradas.append(label_dir.name)
            mascara_final = mascara_atual if mascara_final is None else np.maximum(mascara_final, mascara_atual)

        if not classes_encontradas:
            classes_encontradas = ["Background"]

        return mascara_final, classes_encontradas

    @staticmethod
    def _extrair_dados_imagem(filename: str, labels_dirs: list) -> dict:
        instancias_imagem = {}
        filename_png = f"{filename.split('.')[0]}.png"

        for label_dir in labels_dirs:
            img_path = label_dir / filename_png
            if img_path.exists():
                mask = np.array(Image.open(img_path))
                qtd_pixels = np.sum(mask > 0)
                if qtd_pixels > 0:
                    instancias_imagem[label_dir.name] = qtd_pixels

        return instancias_imagem

    @staticmethod
    def extrair_metricas(split_dataset) -> dict:
        labels_dirs   = split_dataset.labels_dirs
        paths         = split_dataset.paths
        nomes_classes = [d.name for d in labels_dirs]
        arquivos      = split_dataset.lista_ids

        print(f"Executando varredura em {len(arquivos)} imagens ({split_dataset.caminho_split.name})...")

        dados_instancias   = {}
        matriz_coocorrencia = np.zeros((len(nomes_classes), len(nomes_classes)), dtype=int)
        class_to_idx       = {nome: idx for idx, nome in enumerate(nomes_classes)}

        with ThreadPoolExecutor() as executor:
            resultados = list(tqdm(
                executor.map(
                    lambda f: exploratory_data_analysis._extrair_dados_imagem(f, labels_dirs),
                    arquivos,
                ),
                total=len(arquivos),
            ))

        for instancias_imagem in resultados:
            classes_presentes = list(instancias_imagem.keys())

            for classe, pixels in instancias_imagem.items():
                dados_instancias.setdefault(classe, []).append(pixels)

            for classe_a in classes_presentes:
                for classe_b in classes_presentes:
                    matriz_coocorrencia[class_to_idx[classe_a], class_to_idx[classe_b]] += 1

        contagem_imagens = {c: len(v) for c, v in dados_instancias.items()}
        contagem_pixels  = {c: sum(v) for c, v in dados_instancias.items()}
        df_escala        = pd.DataFrame([
            {"Classe": classe, "Pixels": area}
            for classe, tamanhos in dados_instancias.items()
            for area in tamanhos
        ])

        return {
            "contagem_imagens":    contagem_imagens,
            "contagem_pixels":     contagem_pixels,
            "matriz_coocorrencia": matriz_coocorrencia,
            "df_escala":           df_escala,
            "nomes_classes":       nomes_classes,
            "total_imagens":       len(arquivos),
        }

    @staticmethod
    def plot_consistencia_split(metricas_val: dict, metricas_test: dict) -> None:
        contagem_val  = metricas_val["contagem_imagens"]
        contagem_test = metricas_test["contagem_imagens"]
        total_val     = metricas_val["total_imagens"]
        total_test    = metricas_test["total_imagens"]
        total_original = total_val + total_test

        todas_classes = sorted(contagem_val.keys() | contagem_test.keys())

        # Reconstrói o Val Original somando val + test
        contagem_original = {
            cls: contagem_val.get(cls, 0) + contagem_test.get(cls, 0)
            for cls in todas_classes
        }

        splits_plot = [
            ("Val Original",   contagem_original, total_original),
            ("Val (adaptado)", contagem_val,       total_val),
        ]

        pcts_por_split = [
            [contagem.get(cls, 0) / total * 100 for cls in todas_classes]
            for _, contagem, total in splits_plot
        ]
        x_max = max(pct for pcts in pcts_por_split for pct in pcts) * 1.15

        fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=True)
        fig.suptitle(
            "Consistência do Split — Val Original vs Val (adaptado)",
            fontsize=15, fontweight="bold", y=1.02,
        )

        for ax, (nome_split, contagem, total), pcts in zip(axes, splits_plot, pcts_por_split):
            sns.barplot(
                x=pcts, y=todas_classes, hue=todas_classes,
                palette="viridis", legend=False, ax=ax,
            )
            ax.set_xlim(0, x_max)
            ax.set_title(f"{nome_split}\n({total} imagens)", fontsize=12, fontweight="bold")
            ax.set_xlabel("% de imagens onde a classe aparece", fontsize=10)
            ax.set_ylabel("Classes" if ax is axes[0] else "", fontsize=10)

            for i, (cls, pct) in enumerate(zip(todas_classes, pcts)):
                v = contagem.get(cls, 0)
                ax.text(pct + (x_max * 0.01), i, f"{v} ({pct:.1f}%)", va="center", fontsize=9)

            sns.despine(ax=ax)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_frequencia_classes(splits: list[tuple[str, dict, int]]) -> None:
        todas_classes = sorted({cls for _, contagem, _ in splits for cls in contagem})

        # Calcula porcentagens e define escala x uniforme com o maior valor entre os 3 splits
        pcts_por_split = [
            [contagem.get(cls, 0) / total * 100 for cls in todas_classes]
            for _, contagem, total in splits
        ]
        x_max = max(pct for pcts in pcts_por_split for pct in pcts) * 1.15

        fig, axes = plt.subplots(1, len(splits), figsize=(22, 7), sharey=True)
        fig.suptitle(
            "Frequência das Classes por Imagem - Agriculture Vision",
            fontsize=15, fontweight="bold", y=1.02,
        )

        for ax, (nome_split, contagem, total), pcts in zip(axes, splits, pcts_por_split):
            sns.barplot(
                x=pcts, y=todas_classes, hue=todas_classes,
                palette="viridis", legend=False, ax=ax,
            )
            ax.set_xlim(0, x_max)
            ax.set_title(f"{nome_split}\n({total} imagens)", fontsize=12, fontweight="bold")
            ax.set_xlabel("% de imagens onde a classe aparece", fontsize=10)
            ax.set_ylabel("Classes" if ax is axes[0] else "", fontsize=10)

            for i, (cls, pct) in enumerate(zip(todas_classes, pcts)):
                v = contagem.get(cls, 0)
                ax.text(pct + (x_max * 0.01), i, f"{v} ({pct:.1f}%)", va="center", fontsize=9)

            sns.despine(ax=ax)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_area_pixels_log(splits: list[tuple[str, dict]]) -> None:
        todas_classes = sorted({cls for _, contagem in splits for cls in contagem})

        fig, axes = plt.subplots(1, len(splits), figsize=(22, 7), sharey=True, sharex=True)
        fig.suptitle(
            "Área Total Ocupada por Classe - Agriculture Vision\n(Total de Pixels em Escala Logarítmica)",
            fontsize=15, fontweight="bold", y=1.02,
        )

        for ax, (nome_split, contagem) in zip(axes, splits):
            valores = [contagem.get(cls, 0) for cls in todas_classes]

            sns.barplot(
                x=valores, y=todas_classes, hue=todas_classes,
                palette="magma", legend=False, ax=ax,
            )
            ax.set_xscale("log")
            ax.set_title(nome_split, fontsize=12, fontweight="bold")
            ax.set_xlabel("Número de Pixels (Log)", fontsize=10)
            ax.set_ylabel("Classes" if ax is axes[0] else "", fontsize=10)

            for i, v in enumerate(valores):
                if v > 0:
                    ax.text(v * 1.15, i, f"{v:,}", va="center", fontsize=9)

            sns.despine(ax=ax)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_distribuicao_escala(splits: list[tuple[str, pd.DataFrame]]) -> None:
        todas_classes     = sorted({cls for _, df in splits for cls in df["Classe"].unique()})
        area_total_imagem = 512 * 512
        palette           = dict(zip(todas_classes, sns.color_palette("vlag", len(todas_classes))))

        fig, axes = plt.subplots(1, len(splits), figsize=(22, 8), sharey=True, sharex=True)
        fig.suptitle(
            "Distribuição de Escala das Instâncias - Agriculture Vision\n(Tamanho físico em pixels mapeado em Escala Logarítmica)",
            fontsize=15, fontweight="bold", y=1.02,
        )

        for ax, (nome_split, df_escala) in zip(axes, splits):
            sns.boxplot(
                x="Pixels", y="Classe", data=df_escala,
                order=todas_classes, ax=ax,
                hue="Classe", palette=palette,
                width=0.6, showfliers=False, legend=False,
            )
            sns.stripplot(
                x="Pixels", y="Classe", data=df_escala,
                order=todas_classes, ax=ax,
                color=".3", alpha=0.05, size=2,
            )

            ax.set_xscale("log")
            ax.set_title(nome_split, fontsize=12, fontweight="bold")
            ax.set_xlabel("Tamanho da Instância em Pixels (Log)", fontsize=10)
            ax.set_ylabel("Classes" if ax is axes[0] else "", fontsize=10)
            ax.grid(axis="x", linestyle="--", alpha=0.7)
            ax.axvline(
                area_total_imagem, color="red", linestyle=":",
                label=f"Área Total da Imagem ({area_total_imagem:,} px)",
            )
            ax.legend(loc="lower right", fontsize=8)

            sns.despine(ax=ax)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def salvar_metricas(metricas: dict, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(metricas, f)
        print(f"Métricas salvas em {path}")

    @staticmethod
    def carregar_metricas(path: str | Path) -> dict:
        with open(Path(path), "rb") as f:
            return pickle.load(f)

    @staticmethod
    def show_samples(mode: str, split_dataset, num_amostras: int = 3):
        paths       = split_dataset.paths
        labels_dirs = split_dataset.labels_dirs
        is_test     = mode.upper() == "TEST"
        num_cols    = 6 if is_test else 7

        arquivos_rgb = [f.name for f in paths["rgb"].iterdir() if f.is_file()]
        amostras     = random.sample(arquivos_rgb, num_amostras)

        for img_name in amostras:
            sample_id = img_name.split(".")[0]

            rgb_path      = paths["rgb"]        / img_name
            nir_path      = paths["nir"]        / img_name
            mask_path     = paths["masks"]      / f"{sample_id}.png"
            boundary_path = paths["boundaries"] / f"{sample_id}.png"

            img_rgb      = np.array(Image.open(rgb_path))
            img_nir      = np.array(Image.open(nir_path))
            img_mask     = np.array(Image.open(mask_path))
            img_boundary = np.array(Image.open(boundary_path))
            ndvi_array   = exploratory_data_analysis._calcular_ndvi(rgb_path, nir_path)
            ndwi_array   = exploratory_data_analysis._calcular_ndwi(rgb_path, nir_path)

            fig, axes = plt.subplots(2, num_cols, figsize=(20, 9))
            fig.suptitle(f"Sample ID: {sample_id} ({mode.upper()})", fontsize=16, fontweight="bold")

            for ax in axes.flat:
                ax.set(xticks=[], yticks=[])
                for spine in ax.spines.values():
                    spine.set(edgecolor="black", linewidth=0.8)

            axes[1, 2].axis("off")
            axes[1, 3].axis("off")
            if not is_test:
                axes[1, 4].axis("off")

            axes[0, 0].imshow(img_rgb, vmin=0, vmax=255)
            axes[0, 0].set_title("RGB (Raw)")
            axes[0, 1].imshow(img_nir, cmap="gray", vmin=0, vmax=255)
            axes[0, 1].set_title("NIR (Raw)")
            axes[0, 2].imshow(img_mask, cmap="gray", vmin=0, vmax=255)
            axes[0, 2].set_title("Mask")
            axes[0, 3].imshow(img_boundary, cmap="gray", vmin=0, vmax=255)
            axes[0, 3].set_title("Boundary")

            col_ndvi = 4 if is_test else 5
            col_ndwi = col_ndvi + 1

            if not is_test:
                img_labels, lista_classes = exploratory_data_analysis._fusao_labels(f"{sample_id}.png", labels_dirs)
                axes[0, 4].imshow(img_labels, cmap="gray", vmin=0, vmax=1)
                axes[0, 4].set_title(", ".join(lista_classes), fontsize=10)

            img_ndvi = axes[0, col_ndvi].imshow(ndvi_array, cmap="RdYlGn", vmin=-1, vmax=1)
            axes[0, col_ndvi].set_title("NDVI (Raw)")
            fig.colorbar(img_ndvi, cax=axes[0, col_ndvi].inset_axes([1.05, 0.0, 0.05, 1.0]))

            img_ndwi = axes[0, col_ndwi].imshow(ndwi_array, cmap="RdYlGn", vmin=-1, vmax=1)
            axes[0, col_ndwi].set_title("NDWI (Raw)")
            fig.colorbar(img_ndwi, cax=axes[0, col_ndwi].inset_axes([1.05, 0.0, 0.05, 1.0]))

            if is_test:
                roi = (img_mask > 0) & (img_boundary > 0)
            else:
                roi = (img_labels > 0) & (img_mask > 0) & (img_boundary > 0)

            rgb_recortado  = np.where(np.expand_dims(roi, axis=-1), img_rgb, 0).astype(img_rgb.dtype)
            nir_recortado  = np.where(roi, img_nir, 0).astype(img_nir.dtype)
            ndvi_recortado = np.where(roi, ndvi_array, np.nan)
            ndwi_recortado = np.where(roi, ndwi_array, np.nan)

            axes[1, 0].imshow(rgb_recortado, vmin=0, vmax=255)
            axes[1, 0].set_title("RGB (Region of Interest)")
            axes[1, 1].imshow(nir_recortado, cmap="gray", vmin=0, vmax=255)
            axes[1, 1].set_title("NIR (Region of Interest)")

            img_ndvi_r = axes[1, col_ndvi].imshow(ndvi_recortado, cmap="RdYlGn", vmin=-1, vmax=1)
            axes[1, col_ndvi].set_title("NDVI (Region of Interest)")
            fig.colorbar(img_ndvi_r, cax=axes[1, col_ndvi].inset_axes([1.05, 0.0, 0.05, 1.0]))

            img_ndwi_r = axes[1, col_ndwi].imshow(ndwi_recortado, cmap="RdYlGn", vmin=-1, vmax=1)
            axes[1, col_ndwi].set_title("NDWI (Region of Interest)")
            fig.colorbar(img_ndwi_r, cax=axes[1, col_ndwi].inset_axes([1.05, 0.0, 0.05, 1.0]))

            plt.tight_layout()
            plt.show()
            