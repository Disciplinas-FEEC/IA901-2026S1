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
* **Gestor de Ambientes:** `venv` (nativo do Python) ou `Conda`.

### 2.2. Requisitos de Hardware (Recomendado)
* **Processador:** Mínimo de 4 cores / 8 threads.
* **Memória RAM:** Mínimo de 16 GB (devido ao volume de dados carregado em memória durante o processamento).
* **Aceleração por Hardware (Opcional):** GPU compatível com CUDA (ex: NVIDIA GTX 1660 / RTX 2060 ou superior) se pretender acelerar o treino/inferência de modelos pesados. Caso contrário, o código correrá em CPU por omissão.

---

---

## 3. Origem e Download do Dataset

Esta pesquisa utiliza o dataset **Agriculture-Vision**. Para reproduzir os experimentos, os dados devem ser obtidos explicitamente a partir da fonte oficial:

* **Link para Download:** [Clique aqui para a página do dataset](https://www.agriculture-vision.com/agriculture-vision-2022/prize-challenge-2022/agriculture-vision-challenge-2022).
* **Instruções de Download:** Baixe os arquivos correspondentes às imagens e certifique-se de ter no mínimo 21 GB de armazenamento livre.
* O caminho para o dataset deve estar definido no arquivo `config.yaml` na raiz do projeto, seguindo o exemplo:

```yaml
dataset_path: /caminho/da/base/dos/arquivos/do/dataset
```

## 4. Configuração do Ambiente (Instalação)

Siga rigorosamente os comandos abaixo no terminal para clonar o repositório e isolar as dependências do projeto, evitando conflitos com outras bibliotecas globais do seu sistema.

### Passo 1: Clonar o Repositório
```bash
git clone https://github.com/luisso2/IA901-2026S1.git

cd IA901-2026S1

cd "projetos/Multiespectral Agrícola"
````

# 2. Criar e ativar o ambiente virtual (exemplo em Linux)
```bash
python -m venv venv
source venv/bin/activate
````

# 3. Atualizar o pip e instalar as dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
````
