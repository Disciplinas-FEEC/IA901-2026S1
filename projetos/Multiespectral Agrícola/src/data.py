import random
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import torch
from torch.utils.data import Dataset
import pytorch_lightning as pl
from torch.utils.data import DataLoader

from .constants import CLASSES_DICT

class AgricultureVisionDataModule(pl.LightningDataModule):
    def __init__(
        self, 
        dataset_dir: str,
        input_channels: str,
        classes2eval: list[str],
        batch_size: int, 
        isSplitValidationSet: bool, 
        taxForValidationSet: float,
        seed: int
    ):
        super().__init__()
        # Salvamos os parâmetros no estado da classe
        self.dataset_dir = Path(dataset_dir)
        self.batch_size = batch_size
        self.isSplitValidationSet = isSplitValidationSet
        self.taxForValidationSet = taxForValidationSet
        self.seed = seed
        self.input_channels = input_channels
        self.classes2eval = classes2eval

        # Datasets inicializados como None (serão preenchidos no setup)
        self.train_dataset = None
        self.val_dataset = None
        self.test_dataset = None

    def setup(self, stage: str = None):
        """
        O PyTorch Lightning chama o setup() automaticamente antes do treinamento.
        É aqui que os dados devem ser carregados e instanciados.
        """
        # 1. Prepara o conjunto de TREINO
        caminho_rgb_train = self.dataset_dir / "train" / "images" / "rgb"
        ids_train = [arquivo.stem for arquivo in caminho_rgb_train.glob('*.*')]
        caminho_train = self.dataset_dir / "train"
        self.train_dataset = AgricultureVisionDataset(caminho_split=caminho_train, lista_ids=ids_train, classes2eval = self.classes2eval, input_channels=self.input_channels)

        # 2. Prepara os conjuntos de VALIDAÇÃO e TESTE usando o método privado
        self.val_dataset, self.test_dataset = self._create_val_n_test_set()

    def _create_val_n_test_set(self):
        """
        Método privado (indicado pelo '_') de uso exclusivo do DataModule.
        Lida com o particionamento das imagens.
        """
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

    def train_dataloader(self):
        return DataLoader(
            self.train_dataset, 
            batch_size=self.batch_size, 
            shuffle=True,
            # num_workers=4, # Recomendado adicionar depois
        )

    def val_dataloader(self):
        return DataLoader(
            self.val_dataset, 
            batch_size=self.batch_size, 
            shuffle=False
        )

    def test_dataloader(self):
        return DataLoader(
            self.test_dataset, 
            batch_size=self.batch_size, 
            shuffle=False
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
        # 1. Descobre quais arquivos carregar (sem duplicatas)
        fontes = set()
        input_channels = self.input_channels
        for letra in input_channels:
            if letra in self.BAND_MAP:
                fontes.add(self.BAND_MAP[letra][0])
            elif letra in self.COMPUTED_BANDS:
                _, deps = self.COMPUTED_BANDS[letra]
                fontes.update(deps)

        # 2. Carrega cada arquivo uma única vez
        arquivos = {}
        for fonte in fontes:
            if fonte == 'rgb':
                img = cv2.imread(str(self.paths['rgb'] / f"{id_arquivo}.jpg"))
                arquivos['rgb'] = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)   # H x W x 3
            else:
                arquivos[fonte] = cv2.imread(
                    str(self.paths[fonte] / f"{id_arquivo}.jpg"),
                    cv2.IMREAD_GRAYSCALE
                )[..., np.newaxis]

        # 3. Monta os canais na ordem pedida
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
        caminho_split: Path,      # Ex: Caminho para a pasta 'train' ou 'val'
        lista_ids: list[str],     # Ex: ['10495_001', '88392_002'] gerados pelo DataModule
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
        self.labels_dirs = [d for d in pasta_labels.iterdir() if d.is_dir()]


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
                label_path = dir_map[class_name] / f"{id_arquivo}.png"
                label_mask = cv2.imread(str(label_path), cv2.IMREAD_GRAYSCALE)
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