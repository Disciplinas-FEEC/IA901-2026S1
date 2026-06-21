import os
import contextlib
import json
from pathlib import Path

import time
import datetime

import torch
import torch.nn as nn
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.optim.lr_scheduler import LambdaLR
from torch.utils.tensorboard import SummaryWriter

from src.model import FPN_ResNet50_Segmentation
from src.metrics import ModifiedMIoU
from src.train_utils import (
    gerador_infinito, avaliar,
    salvar_checkpoint,
    make_poly_lr,
    getWeightsForLoss
)
from src.data import AgricultureVisionDataModule, compute_pos_weight
from src.constants import (
    DATASET_DIR, INPUT_CHANNELS, CLASSES2EVAL,
    IS_SPLIT_VALIDATION_SET, TAX_FOR_VALIDATION_SET, SEED,
    IMAGENET_MEAN, IMAGENET_STD,
    CHECKPOINT_DIR, TENSORBOARD_DIR, CACHE_DIR,
    IS_WEIGHTED_LOSS
)


def main():
    # ==========================================
    # 1. Configurações + pos_weight (SALA DE ESPERA)
    # ==========================================
    local_rank = int(os.environ["LOCAL_RANK"])
    torch.cuda.set_device(local_rank)
    device = torch.device(f"cuda:{local_rank}")
    dist.init_process_group(
    backend="nccl", 
    timeout=datetime.timedelta(hours=2))
    torch.backends.cudnn.benchmark = True

    total_iters = 25000
    warmup_iters = 1000
    constant_iters = 7000
    base_lr = 0.01

    batch_size_por_gpu = 10
    passos_acumulacao = 2
    num_classes = len(CLASSES2EVAL)

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    # cache_pos_weight = CACHE_DIR / "pos_weight.json"

    ch_mean = torch.tensor([IMAGENET_MEAN.get(c, 0.0) for c in INPUT_CHANNELS])
    ch_std  = torch.tensor([IMAGENET_STD.get(c, 1.0)  for c in INPUT_CHANNELS])


    datamodule = AgricultureVisionDataModule(
        dataset_dir=DATASET_DIR,
        input_channels=INPUT_CHANNELS,
        classes2eval=CLASSES2EVAL,
        batch_size=batch_size_por_gpu,
        isSplitValidationSet=IS_SPLIT_VALIDATION_SET,
        taxForValidationSet=TAX_FOR_VALIDATION_SET,
        seed=SEED,
        num_workers=3,
        pin_memory=True,
        persistent_workers=True,
    )
    datamodule.setup()

    if IS_WEIGHTED_LOSS:
        weights = torch.zeros(len(CLASSES2EVAL), 1, 1, device=device, dtype=torch.float32)
        if local_rank == 0:
            weights.copy_(
                getWeightsForLoss(
                    train_dataset=datamodule.train_dataset,
                    classes=CLASSES2EVAL,
                    file_path=CACHE_DIR / "pos_weight.json",
                    batch_size=32,         
                    num_workers=4,         
                    device=device
            ))

        dist.broadcast(weights, src=0)
        criterio = nn.BCEWithLogitsLoss(reduction='none', pos_weight=weights)
    else:
        criterio = nn.BCEWithLogitsLoss(reduction='none')

    # ==========================================
    # 4. Preparando o Modelo
    # ==========================================
    modelo = FPN_ResNet50_Segmentation(
        num_classes=num_classes,
        input_mean=ch_mean,
        input_std=ch_std,
        input_channels=INPUT_CHANNELS,
    ).to(device)

    modelo = DDP(modelo, device_ids=[local_rank], output_device=local_rank)

    # ==========================================
    # 5. Otimizador, Loss e Scheduler
    # ==========================================
    otimizador = torch.optim.SGD(
        modelo.parameters(),
        lr=base_lr, momentum=0.9, weight_decay=5e-4,
    )

    scheduler = LambdaLR(
        otimizador, make_poly_lr(warmup_iters, constant_iters, total_iters))

    # ==========================================
    # 6. Dataloaders com Sampler Distribuído
    # ==========================================
    dataloader_treino = datamodule.train_dataloader()
    dataloader_val    = datamodule.val_dataloader()
    iterador_dados = gerador_infinito(dataloader_treino)

    # ==========================================
    # 7. Resume + TensorBoard
    # ==========================================
    eval_every = 2500
    ckpt_every = 2500
    iteracao_real = 0
    best_miou     = 0.0

    latest_ckpt = CHECKPOINT_DIR / "latest.pth"
    if latest_ckpt.exists():
        ckpt = torch.load(latest_ckpt, map_location=device)
        modelo.module.load_state_dict(ckpt["model"])
        otimizador.load_state_dict(ckpt["optimizer"])
        scheduler.load_state_dict(ckpt["scheduler"])
        iteracao_real = ckpt["iteracao_real"]
        best_miou     = ckpt["best_miou"]
        if local_rank == 0:
            print(f"Retomando do checkpoint: iter {iteracao_real}, melhor mIoU {best_miou:.4f}")

    if local_rank == 0:
        writer_train = SummaryWriter(log_dir=str(TENSORBOARD_DIR / "train"))
        writer_val   = SummaryWriter(log_dir=str(TENSORBOARD_DIR / "val"))
    else:
        writer_train = writer_val = None

    train_metric = ModifiedMIoU(num_classes, device=device)

    # ==========================================
    # 8. O Loop de Treinamento
    # ==========================================

    modelo.train()
    otimizador.zero_grad()

    if local_rank == 0:
        print("Iniciando treinamento nas duas gpus...")

    passos_forward = 0

    while iteracao_real < total_iters:
        passos_forward += 1

        batch         = next(iterador_dados)
        imagens       = batch["image"].to(device)
        mascaras_alvo = batch["labels"].to(device)
        mask          = batch["mask"].to(device)
        boundary      = batch["boundary"].to(device)

        roi = (mask * boundary).unsqueeze(1)

        eh_ultimo_micro = (passos_forward % passos_acumulacao == 0)
        ctx_sync = contextlib.nullcontext() if eh_ultimo_micro else modelo.no_sync()
        
        with ctx_sync:
            logits = modelo(imagens)
            loss_map = criterio(logits, mascaras_alvo)
            perda_real = (loss_map * roi).sum() / (roi.sum() * num_classes)
            train_metric.update(logits, mascaras_alvo, roi)
            perda = perda_real / passos_acumulacao
            perda.backward()
        
        if passos_forward % passos_acumulacao == 0:
            otimizador.step()
            scheduler.step()
            otimizador.zero_grad()
            iteracao_real += 1
            
            if local_rank == 0 and iteracao_real % 100 == 0:
                lr_atual = scheduler.get_last_lr()[0]
                print(f"Iteração [{iteracao_real}/{total_iters}] | Loss: {perda_real.item():.4f}")
                writer_train.add_scalar("loss", perda_real.item(), iteracao_real)
                writer_train.add_scalar("lr",   lr_atual,          iteracao_real)

            if iteracao_real % eval_every == 0:
                train_metric.reduce()
                train_miou, train_iou = train_metric.compute()
                val_loss, val_miou, val_iou = avaliar(
                    modelo, dataloader_val, device, num_classes, criterio)

                if local_rank == 0:
                    print(f"  [VAL] iter {iteracao_real} | mIoU treino: {train_miou:.4f} | "
                          f"mIoU val: {val_miou:.4f} | loss val: {val_loss:.4f}")
                    writer_train.add_scalar("mIoU", train_miou, iteracao_real)
                    writer_val.add_scalar("mIoU",   val_miou,   iteracao_real)
                    writer_val.add_scalar("loss",   val_loss,   iteracao_real)
                    for nome, tr_c, va_c in zip(CLASSES2EVAL + ["background"],
                                                train_iou.tolist(), val_iou.tolist()):
                        writer_train.add_scalar(f"IoU/{nome}", tr_c, iteracao_real)
                        writer_val.add_scalar(f"IoU/{nome}",   va_c, iteracao_real)
                    
                    if val_miou > best_miou:
                        best_miou = val_miou
                        torch.save(modelo.module.state_dict(),
                                   CHECKPOINT_DIR / "best.pth")
                        print(f"  >> novo melhor mIoU val: {val_miou:.4f} (salvo em best.pth)")

                train_metric.reset()

            if local_rank == 0 and iteracao_real % ckpt_every == 0:
                salvar_checkpoint(CHECKPOINT_DIR / "latest.pth", modelo, otimizador,
                                  scheduler, iteracao_real, best_miou)

    # ==========================================
    # 9. Avaliação final + Finalização
    # ==========================================
    val_loss, val_miou, val_iou = avaliar(modelo, dataloader_val, device, num_classes, criterio)
    if local_rank == 0:
        print("Treinamento finalizado!")
        print(f"mIoU modificada final: {val_miou:.4f} | loss val: {val_loss:.4f}")
        for nome, iou_c in zip(CLASSES2EVAL + ["background"], val_iou.tolist()):
            print(f"  IoU[{nome}] = {iou_c:.4f}")
            writer_val.add_scalar(f"IoU/{nome}", iou_c, iteracao_real)
        writer_val.add_scalar("mIoU", val_miou, iteracao_real)
        writer_val.add_scalar("loss", val_loss, iteracao_real)

        if val_miou > best_miou:
            best_miou = val_miou
            torch.save(modelo.module.state_dict(),
                       CHECKPOINT_DIR / "best.pth")

        salvar_checkpoint(CHECKPOINT_DIR / "latest.pth", modelo, otimizador,
                          scheduler, iteracao_real, best_miou)

        torch.save(
            modelo.module.state_dict(),
            CHECKPOINT_DIR / "final.pth")
        
        print(f"Melhor mIoU obtida: {best_miou:.4f} (pesos em best.pth)")
        writer_train.close()
        writer_val.close()

    dist.destroy_process_group()

if __name__ == "__main__":
    main()