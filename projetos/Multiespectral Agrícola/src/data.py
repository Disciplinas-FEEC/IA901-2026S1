import json
import pickle
import random
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
from tqdm import tqdm
import torch
import torch.distributed as dist
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler

from .constants import CLASSES_DICT


def collate_fn(batch):
    return {
        "image":    torch.stack([b["image"]    for b in batch]),
        "labels":   torch.stack([b["labels"]   for b in batch]),
        "mask":     torch.stack([b["mask"]     for b in batch]),
        "boundary": torch.stack([b["boundary"] for b in batch]),
        # "id":       [b["id"] for b in batch],
    }


# def compute_channel_stats(dataset, cache_path=None, batch_size=8, num_workers=4):
#     """
#     Calcula mean/std por canal sobre o split de treino, considerando apenas os
#     pixels válidos (dentro do ROI = mask & boundary). Usado para normalizar a
#     entrada do modelo. O resultado é cacheado em disco (pickle).

#     Retorna (mean, std) como tensores 1-D de tamanho C (nº de canais de entrada).
#     """
#     cache_path = Path(cache_path) if cache_path is not None else None
#     if cache_path is not None and cache_path.exists():
#         with open(cache_path, "rb") as f:
#             stats = pickle.load(f)
#         return torch.tensor(stats["mean"]), torch.tensor(stats["std"])

#     def _collate(batch):
#         return (
#             torch.stack([b["image"]    for b in batch]),
#             torch.stack([b["mask"]     for b in batch]),
#             torch.stack([b["boundary"] for b in batch]),
#         )

#     loader = DataLoader(
#         dataset, batch_size=batch_size, shuffle=False,
#         num_workers=num_workers, collate_fn=_collate,
#     )

#     C = len(dataset.input_channels)
#     ch_sum   = torch.zeros(C, dtype=torch.float64)
#     ch_sqsum = torch.zeros(C, dtype=torch.float64)
#     n_pixels = 0

#     for imagens, mask, boundary in tqdm(loader, desc="Calculando mean/std por canal"):
#         imagens = imagens.double()                       # (N, C, H, W)
#         roi = ((mask * boundary) > 0).unsqueeze(1).double()  # (N, 1, H, W)
#         ch_sum   += (imagens * roi).sum(dim=(0, 2, 3))
#         ch_sqsum += (imagens.pow(2) * roi).sum(dim=(0, 2, 3))
#         n_pixels += int(roi.sum().item())

#     mean = ch_sum / n_pixels
#     std  = (ch_sqsum / n_pixels - mean.pow(2)).clamp_min(0).sqrt()

#     if cache_path is not None:
#         cache_path.parent.mkdir(parents=True, exist_ok=True)
#         with open(cache_path, "wb") as f:
#             pickle.dump({"mean": mean.tolist(), "std": std.tolist()}, f)

#     return mean.float(), std.float()


def compute_pos_weight(dataset, classes2eval, cache_path=None,
                       suavizacao="sqrt", batch_size=16, num_workers=4):
    """
    Calcula o pos_weight por classe para a BCE multilabel, no split de treino,
    contando positivos vs. negativos dentro do ROI (mask & boundary):

        w_k = #pixels_negativos_k / #pixels_positivos_k

    Combate o desbalanceamento: em cada canal a esmagadora maioria dos pixels é
    negativa ("sem aquela anomalia"), então sem peso o modelo é premiado por
    prever "vazio". O pos_weight amplifica a punição dos positivos raros.

    A frequência inversa crua (#neg/#pos) costuma SUPER-corrigir as classes mais
    raras (pesos de centenas, que desestabilizam o treino). Por isso 'suavizacao'
    é aplicada ao peso:
      - "sqrt" (padrão): comprime a escala preservando a ORDEM entre as classes;
      - None: retorna o peso cru;
      - callable f(w)->w': política customizada (ex.: lambda w: min(w, 50) p/ teto).
    O cache em disco (JSON) guarda sempre o peso CRU, então dá pra trocar a
    suavização sem recalcular. Lê apenas labels/mask/boundary (pula as imagens de
    entrada, mais rápido).

    Retorna dict {nome_classe: w_k} na ordem de classes2eval.
    """
    cache_path = Path(cache_path) if cache_path is not None else None
    if cache_path is not None and cache_path.exists():
        with open(cache_path) as f:
            pesos = json.load(f)
    else:
        # Wrapper leve: entrega só os rótulos, sem carregar as imagens de entrada.
        class _SoRotulos(Dataset):
            def __init__(self, base):
                self.base = base

            def __len__(self):
                return len(self.base.lista_ids)

            def __getitem__(self, i):
                out = self.base._getOutput(self.base.lista_ids[i])
                return out["labels"], out["mask"], out["boundary"]

        loader = DataLoader(
            _SoRotulos(dataset), batch_size=batch_size, shuffle=False,
            num_workers=num_workers,
        )

        K = len(classes2eval)
        pos          = torch.zeros(K, dtype=torch.float64)
        total_valido = torch.zeros((), dtype=torch.float64)

        for labels, mask, boundary in tqdm(loader, desc="Calculando pos_weight"):
            roi = ((mask * boundary) > 0).unsqueeze(1).double()   # (N, 1, H, W)
            pos          += (labels * roi).sum(dim=(0, 2, 3)).double()
            total_valido += roi.sum()

        neg = total_valido - pos
        w   = (neg / pos.clamp(min=1)).tolist()                   # w_k = #neg/#pos
        pesos = {nome: round(wk, 2) for nome, wk in zip(classes2eval, w)}

        if cache_path is not None:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, "w") as f:
                json.dump(pesos, f, indent=2)

    # Suavização aplicada na saída (o cache mantém o peso cru).
    if suavizacao == "sqrt":
        transform = lambda w: w ** 0.5
    elif suavizacao is None:
        transform = lambda w: w
    elif callable(suavizacao):
        transform = suavizacao
    else:
        raise ValueError("suavizacao deve ser 'sqrt', None ou um callable f(w)->w'")

    return {nome: round(transform(wk), 2) for nome, wk in pesos.items()}

class AgricultureVisionDataModule:
    def __init__(
        self,
        dataset_dir: str,
        input_channels: str,
        classes2eval: list[str],
        batch_size: int,
        isSplitValidationSet: bool,
        taxForValidationSet: float,
        seed: int,
        num_workers: int = 3,
        pin_memory: bool = True,
        persistent_workers: bool = True,
    ):
        # Salvamos os parâmetros no estado da classe
        self.dataset_dir = Path(dataset_dir)
        self.batch_size = batch_size
        self.isSplitValidationSet = isSplitValidationSet
        self.taxForValidationSet = taxForValidationSet
        self.seed = seed
        self.input_channels = input_channels
        self.classes2eval = classes2eval
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.persistent_workers = persistent_workers

        # Datasets inicializados como None (serão preenchidos no setup)
        self.train_dataset = None
        self.val_dataset = None
        self.test_dataset = None

    def setup(self, stage: str = None):
        # 1. Prepara o conjunto de TREINO
        caminho_rgb_train = self.dataset_dir / "train" / "images" / "rgb"
        ids_train = [arquivo.stem for arquivo in caminho_rgb_train.glob('*.*')]
        caminho_train = self.dataset_dir / "train"
        self.train_dataset = AgricultureVisionDataset(caminho_split=caminho_train, lista_ids=ids_train, classes2eval = self.classes2eval, input_channels=self.input_channels)

        # 2. Prepara os conjuntos de VALIDAÇÃO e TESTE usando o método privado
        self.val_dataset, self.test_dataset = self._create_val_n_test_set()

    def _create_val_n_test_set(self):
        if not self.isSplitValidationSet:
            # Caso 1: As pastas 'val' e 'test' já contêm as imagens separadas
            caminho_rgb_val = self.dataset_dir / "val" / "images" / "rgb"
            caminho_rgb_test = self.dataset_dir / "test" / "images" / "rgb"
            
            ids_val = [arquivo.stem for arquivo in caminho_rgb_val.glob('*.*')]
            ids_test = [arquivo.stem for arquivo in caminho_rgb_test.glob('*.*')]
            caminho_val = self.dataset_dir / "val"
            caminho_test = self.dataset_dir / "test"
            val_dataset = AgricultureVisionDataset(caminho_split=caminho_val, lista_ids=ids_val, classes2eval = self.classes2eval, input_channels=self.input_channels)
            test_dataset = AgricultureVisionDataset(caminho_split=caminho_test, lista_ids=ids_test, classes2eval = self.classes2eval, input_channels=self.input_channels)
                
        else:
            # Caso 2: Separa dinamicamente a pasta 'val' por propriedades (farmlands)
            caminho_val = self.dataset_dir / "val" / "images" / "rgb" 
            grupos_propriedades = defaultdict(list)
            
            for arquivo in caminho_val.glob('*.*'):
                codigo_propriedade = arquivo.name.split('_')[0]
                grupos_propriedades[codigo_propriedade].append(arquivo.stem)

            farmlands_unicas = list(grupos_propriedades.keys())
            random.seed(self.seed)
            random.shuffle(farmlands_unicas)

            ponto_corte = int(len(farmlands_unicas) * self.taxForValidationSet)
            files_in_validacao = farmlands_unicas[:ponto_corte]
            files_in_test      = farmlands_unicas[ponto_corte:]

            ids_val = []
            for prop in files_in_validacao:
                ids_val.extend(grupos_propriedades[prop])

            ids_test = []
            for prop in files_in_test:
                ids_test.extend(grupos_propriedades[prop])
                
            caminho_val = self.dataset_dir / "val"
            val_dataset = AgricultureVisionDataset(caminho_split=caminho_val, lista_ids=ids_val, classes2eval = self.classes2eval, input_channels=self.input_channels)
            test_dataset = AgricultureVisionDataset(caminho_split=caminho_val, lista_ids=ids_test, classes2eval = self.classes2eval, input_channels=self.input_channels)
            
        return val_dataset, test_dataset

    def _make_sampler(self, dataset, shuffle):
        if dist.is_available() and dist.is_initialized():
            return DistributedSampler(dataset, shuffle=shuffle)
        return None

    def train_dataloader(self):
        sampler = self._make_sampler(self.train_dataset, shuffle=True)
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            sampler=sampler,
            shuffle=(sampler is None),  # só embaralha aqui se não houver sampler
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
            persistent_workers=self.persistent_workers,
            collate_fn=collate_fn,
        )

    def val_dataloader(self):
        sampler = self._make_sampler(self.val_dataset, shuffle=False)
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            sampler=sampler,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
            persistent_workers=False,  # avaliação é esporádica
            collate_fn=collate_fn,
        )

    def test_dataloader(self):
        sampler = self._make_sampler(self.test_dataset, shuffle=False)
        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            sampler=sampler,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
            persistent_workers=False,
            collate_fn=collate_fn,
        )

class AgricultureVisionDataset(Dataset):
    BAND_MAP = {
        'r': ('rgb', 0),
        'g': ('rgb', 1),
        'b': ('rgb', 2),
        'n': ('nir', 0),
    }

    def _ndvi(arquivos):
        nir = arquivos['nir'][..., 0].astype(np.float32)
        r   = arquivos['rgb'][..., 0].astype(np.float32)
        return (nir - r) / (nir + r + 1e-8)

    def _ndwi(arquivos):
        g   = arquivos['rgb'][..., 1].astype(np.float32)
        nir = arquivos['nir'][..., 0].astype(np.float32)
        return (g - nir) / (g + nir + 1e-8)

    COMPUTED_BANDS = {
        'v': (lambda a, fn=_ndvi: fn(a), ['rgb', 'nir']),
        'w': (lambda a, fn=_ndwi: fn(a), ['rgb', 'nir']),
    }

    def _getInput(self, id_arquivo):
        fontes = set()
        input_channels = self.input_channels
        for letra in input_channels:
            if letra in self.BAND_MAP:
                fontes.add(self.BAND_MAP[letra][0])
            elif letra in self.COMPUTED_BANDS:
                _, deps = self.COMPUTED_BANDS[letra]
                fontes.update(deps)

        # Carrega cada arquivo uma única vez
        arquivos = {}
        for fonte in fontes:
            if fonte == 'rgb':
                img = cv2.imread(str(self.paths['rgb'] / f"{id_arquivo}.jpg"))
                arquivos['rgb'] = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                arquivos[fonte] = cv2.imread(
                    str(self.paths[fonte] / f"{id_arquivo}.jpg"),
                    cv2.IMREAD_GRAYSCALE
                )[..., np.newaxis]

        # Monta os canais na ordem pedida
        canais = []
        for letra in self.input_channels:
            if letra in self.BAND_MAP:
                fonte, idx = self.BAND_MAP[letra]
                canais.append(arquivos[fonte][..., idx].astype(np.float32) / 255)
            elif letra in self.COMPUTED_BANDS:
                fn, _ = self.COMPUTED_BANDS[letra]
                canal = fn(arquivos)            # já em [-1, 1], não divide por 255
                canais.append(canal)

        return torch.from_numpy(np.stack(canais, axis=-1)).permute(2, 0, 1)

    def __init__(
        self,
        caminho_split: Path,      
        lista_ids: list[str],     # ex: ['10495_001', '88392_002']
        classes2eval: list[str],
        input_channels: str  
    ):
        super().__init__()
        # Garante que é um objeto Path
        self.caminho_split = Path(caminho_split) 
        self.lista_ids = lista_ids
        self.classes2eval = classes2eval
        self.input_channels = input_channels
        
        # Mapeamento fixo dos diretórios para este conjunto específico de dados
        self.paths = {
            "rgb":        self.caminho_split / "images" / "rgb",
            "nir":        self.caminho_split / "images" / "nir",
            "masks":      self.caminho_split / "masks",
            "boundaries": self.caminho_split / "boundaries",
        }
        
        # Lida com as labels (a pasta test original do dataset não possui labels)
        pasta_labels = self.caminho_split / "labels"
        if pasta_labels.exists():
            self.labels_dirs = [d for d in pasta_labels.iterdir() if d.is_dir()]
        else:
            self.labels_dirs = []


    def _getOutput(self, id_arquivo):
        mask_np     = cv2.imread(str(self.paths["masks"]      / f"{id_arquivo}.png"), cv2.IMREAD_GRAYSCALE)
        boundary_np = cv2.imread(str(self.paths["boundaries"] / f"{id_arquivo}.png"), cv2.IMREAD_GRAYSCALE)

        mask     = torch.from_numpy((mask_np     > 0).astype(np.float32))
        boundary = torch.from_numpy((boundary_np > 0).astype(np.float32))

        H, W = mask_np.shape
        K = len(self.classes2eval)
        labels_np = np.zeros((K, H, W), dtype=np.float32)

        if self.labels_dirs:
            dir_map = {d.name: d for d in self.labels_dirs}
            for k, class_name in enumerate(self.classes2eval):
                if class_name not in dir_map:
                    continue
                label_path = dir_map[class_name] / f"{id_arquivo}.png"
                if not label_path.exists():
                    continue
                label_mask = cv2.imread(str(label_path), cv2.IMREAD_GRAYSCALE)
                if label_mask is not None:
                    labels_np[k] = (label_mask > 0).astype(np.float32)

        return {
            "labels":   torch.from_numpy(labels_np),
            "mask":     mask,
            "boundary": boundary,
        }

    def __len__(self):
        return len(self.lista_ids)

    def __getitem__(self, idx):
        id_arquivo = self.lista_ids[idx]
        output = self._getOutput(id_arquivo)
        return {
            "id":             id_arquivo,
            "input_channels": self.input_channels,
            "classes2eval":   self.classes2eval,
            "image":          self._getInput(id_arquivo),
            "labels":         output["labels"],
            "mask":           output["mask"],
            "boundary":       output["boundary"],
        }