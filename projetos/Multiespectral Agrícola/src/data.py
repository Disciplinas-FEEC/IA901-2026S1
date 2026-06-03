import random
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import torch
from torch.utils.data import Dataset
import pytorch_lightning as pl
from torch.utils.data import DataLoader


class AgricultureVisionDataModule(pl.LightningDataModule):
    def __init__(
        self, 
        diretorio_dados: str, 
        batch_size: int = 32, 
        isSplitValidationSet: bool = False, 
        taxForValidationSet: float = 0.5, # Assumindo 0.5 como padrão baseado na sua lógica
        seed: int = 7
    ):
        super().__init__()
        # Salvamos os parâmetros no estado da classe
        self.diretorio_dados = Path(diretorio_dados)
        self.batch_size = batch_size
        self.isSplitValidationSet = isSplitValidationSet
        self.taxForValidationSet = taxForValidationSet
        self.seed = seed

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
        caminho_rgb_train = self.diretorio_dados / "train" / "images" / "rgb"
        ids_train = [arquivo.stem for arquivo in caminho_rgb_train.glob('*.*')]
        caminho_train = self.diretorio_dados / "train"
        self.train_dataset = AgricultureVisionDataset(caminho_train, ids_train)

        # 2. Prepara os conjuntos de VALIDAÇÃO e TESTE usando o método privado
        self.val_dataset, self.test_dataset = self._create_val_n_test_set()

    def _create_val_n_test_set(self):
        """
        Método privado (indicado pelo '_') de uso exclusivo do DataModule.
        Lida com o particionamento das imagens.
        """
        if not self.isSplitValidationSet:
            # Caso 1: As pastas 'val' e 'test' já contêm as imagens separadas
            caminho_rgb_val = self.diretorio_dados / "val" / "images" / "rgb"
            caminho_rgb_test = self.diretorio_dados / "test" / "images" / "rgb"
            
            ids_val = [arquivo.stem for arquivo in caminho_rgb_val.glob('*.*')]
            ids_test = [arquivo.stem for arquivo in caminho_rgb_test.glob('*.*')]
            caminho_val = self.diretorio_dados / "val"
            caminho_test = self.diretorio_dados / "test"
            val_dataset = AgricultureVisionDataset(caminho_val, ids_val)
            test_dataset = AgricultureVisionDataset(caminho_test, ids_test)
                
        else:
            # Caso 2: Separa dinamicamente a pasta 'val' por propriedades (farmlands)
            caminho_val = self.diretorio_dados / "val" / "images" / "rgb" 
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
                
            caminho_val = self.diretorio_dados / "val"
            val_dataset = AgricultureVisionDataset(caminho_val, ids_val)
            test_dataset = AgricultureVisionDataset(caminho_val, ids_test)
            
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
    def __init__(
        self,
        caminho_split: Path,      # Ex: Caminho para a pasta 'train' ou 'val'
        lista_ids: list[str],     # Ex: ['10495_001', '88392_002'] gerados pelo DataModule
        classes_avaliadas: list[str] = None
    ):
        super().__init__()
        # Garante que é um objeto Path
        self.caminho_split = Path(caminho_split) 
        self.lista_ids = lista_ids
        self.classes_avaliadas = classes_avaliadas or []
        
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

    def __len__(self):
        # O tamanho do dataset é simplesmente o tamanho da lista de IDs
        return len(self.lista_ids)

    def __getitem__(self, idx):
        # 1. Pega o ID da imagem atual
        id_arquivo = self.lista_ids[idx]
        
        # 2. Monta os caminhos exatos na hora H
        # Supondo que a extensão seja .jpg (ajuste para .png se necessário)
        path_rgb = self.paths["rgb"] / f"{id_arquivo}.jpg"
        path_nir = self.paths["nir"] / f"{id_arquivo}.jpg"
        
        # TODO: Implementar a leitura dos arquivos usando cv2 ou PIL
        # rgb_img = cv2.imread(str(path_rgb))
        # nir_img = cv2.imread(str(path_nir))
        
        return {
            "id": id_arquivo,
            "caminho_rgb": str(path_rgb) # Apenas para teste, substitua pela imagem lida
        }