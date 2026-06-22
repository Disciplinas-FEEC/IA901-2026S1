# Guia de Reprodução: Segmentação Semântica de Imagens Agrícolas usando NDVI e NDWI

Este manual contém as instruções passo a passo necessárias para configurar o ambiente, processar os dados e reproduzir os ensaios, métricas e resultados apresentados nesta pesquisa. O objetivo principal deste guia é garantir a **reprodutibilidade técnica**, permitindo que outros pesquisadores consigam executar o pipeline completo de forma isolada e obter os mesmos resultados.

---

## 1. Visão Geral do Pipeline

O projeto está estruturado como um pipeline sequencial dividido em três grandes etapas:
1. **Pré-processamento e Transformação:** Geração dos índices NDVI E NDWI e split dos dados.
2. **Execução do Modelo/Algoritmo:** Treino e processamento principal utilizando a arquitetura baseline e os parâmetros definidos no estudo.
3. **Avaliação e Métricas:** Geração automática de gráficos de desempenho e tabelas de métricas estatísticas.

---

## 2. Pré-requisitos e Ambiente Técnico

Para mitigar discrepâncias de hardware e software ("*na minha máquina funciona*"), o ambiente de execução foi padronizado.

### 2.1. Requisitos de Software
* **Sistema Operacional:** Linux (Ubuntu 22.04 LTS ou superior) ou Windows 11 (via WSL2 recomendado).
* **Linguagem:** Python 3.10.x (ou superior).
* **Gestor de Ambientes:** `venv` (nativo do Python), `Conda` ou UV.

### 2.2. Requisitos de Hardware (Recomendado)
* **Processador:** Mínimo de 4 cores / 8 threads.
* **Memória RAM:** Mínimo de 16 GB (devido ao volume de dados carregado em memória durante o processamento).
* **Armazenamento:** ~26GB 
    - 150 MB (AWS CLI para download do dataset)
    - 41 GB (download dataset + processo de descompactação)
    - 5.1 GB (ambiente)
* **Aceleração por Hardware (Opcional):** GPU compatível com CUDA (ex: NVIDIA GTX 1660 / RTX 2060 ou superior) se pretender acelerar o treino/inferência de modelos pesados. Caso contrário, o código correrá em CPU por omissão.

---

---

## 3. Origem e Download do Dataset

Esta pesquisa utiliza o dataset **Agriculture-Vision**. Para reproduzir os experimentos, os dados devem ser obtidos explicitamente a partir da fonte oficial:

* **Link para Download:** [Clique aqui para a página do dataset](https://www.agriculture-vision.com/agriculture-vision-2022/prize-challenge-2022/agriculture-vision-challenge-2022).
* **Instruções de Download:**
    - Para um processo automatizado, siga os passos descritos na seção 4 (Configuração do Ambiente).
    - Certifique-se de ter no mínimo 21 GB de armazenamento livre para o dataset e o dobro para o processo de descompactação.
    - O script de download gera automaticamente um arquivo `.env` na raiz do projeto com a variável `DATASET_PATH`, usada pelo `config.yaml`.
    - Se preferir configurar manualmente, o caminho para o dataset pode ser definido no arquivo `.env`, seguindo o exemplo:

```env
DATASET_PATH=/caminho/da/base/dos/arquivos/do/dataset
```

O `config.yaml` já é preparado para usar essa variável automaticamente.


## 4. Configuração do Ambiente (Instalação)

Siga rigorosamente os comandos abaixo no terminal para clonar o repositório e isolar as dependências do projeto, evitando conflitos com outras bibliotecas globais do seu sistema.

### Passo 1: Clonar o Repositório
```bash
git clone https://github.com/luisso2/IA901-2026S1.git

cd IA901-2026S1

cd "projetos/Multiespectral Agrícola"
```

### Passo 2: Prepare Dataset (opcional)

O processo de download e descompactação do dataset pode ser facilitado pelo script `src/scripts/load_dataset.sh`, que identifica se o dataset já existe, realiza o download e descompacta o arquivo apagando ao final, esse processo exige a instalação do `awscli` antes.

1 - Abra o terminal na pasta do projeto "Multiespectral Agrícola".

2 - Dê permissão de execução ao script:

```bash
chmod +x src/scripts/load_dataset.sh
```
3 - Execute o script:
```bash
./src/scripts/load_dataset.sh
```

Ao final, o script irá gerar o arquivo `.env` na raiz do projeto apontando para o diretório descompactado do dataset.


# Passo 3: Criar e ativar o ambiente virtual (exemplo em Linux)
Esse passo é simplificado com o uso de uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

uv sync
```