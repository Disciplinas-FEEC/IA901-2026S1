# Instalação e Preparação de Dados

Este diretório contém o notebook inicial para a configuração do ambiente e download dos datasets utilizados no projeto.

## Objetivo

O notebook `00_Installation.ipynb` automatiza as seguintes etapas:
1. **Instalação de Dependências**: Garante que bibliotecas como necessarias estejam instaladas.
2. **Download de Datasets**: Baixa os arquivos compactados (`.zip`) diretamente do Google Drive utilizando IDs parametrizados em um arquivo CSV.
3. **Extração e Organização**: Descompacta os dados brutos na pasta `Datasets/Raw` e organiza os arquivos relevantes (Imagens e Máscaras) na pasta `Datasets/Interim`.

## Como usar

1. Certifique-se de que o arquivo `datasets_links.csv` existe.
2. Abra o notebook `00_Installation.ipynb`.
3. Execute todas as células em ordem.
4. Verifique a pasta `Datasets` na raiz do projeto para confirmar se os arquivos foram baixados e organizados corretamente.


## Estrutura

Após a execução, o notebook criará a seguinte estrutura no diretório raiz do projeto:

```text
Datasets/
├── Raw/            # Arquivos .zip e pastas originais extraídas
└── Interim/        # Dados organizados e prontos para processamento
    ├── MoNuSeg/
    |    ├── Images/   # Imagens .tif 
    |    ├── Masks/    # Máscaras .xml
    |    └── labels.csv
    ├── PanNuke/    
    |    ├── Images/   # Imagens .npy 
    |    ├── Masks/    # Máscaras .npy
    |    └── labels.csv
    └── NuInSeg/    # Imagens e máscaras
         ├── Images/   # Imagens .png 
         ├── Masks/    # Mascaras .png
         └── labels.csv
```

---
*Nota: O download de grandes volumes de dados pode levar algum tempo dependendo da conexão com a internet.*

## Samples

Esse diretório também contém o notebook `Sample_Generator`, utilizado para selecionar o subconjunto ilustrativo de amostras que foi carregado ao repositório do github.  
