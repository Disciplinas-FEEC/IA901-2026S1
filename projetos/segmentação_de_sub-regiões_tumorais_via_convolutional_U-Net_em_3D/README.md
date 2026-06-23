# Extração de Características em fMRI: Segmentação de Sub-regiões Tumorais via Convolutional U-Net em 3D
# fMRI Feature Extraction: Tumor Sub-region Segmentation via 3D Convolutional U-Net

## Apresentação

O presente projeto foi originado no contexto das atividades da disciplina de pós-graduação *IA901 - Análise de Imagens e Reconhecimento de Padrões*, 
oferecida no primeiro semestre de 2026, na Unicamp, sob supervisão da Profa. Dra. Leticia Rittner, do Departamento de Engenharia de Computação e Automação (DCA) da Faculdade de Engenharia Elétrica e de Computação (FEEC).

> Incluir nome RA e foco de especialização de cada membro do grupo. Os projetos devem ser desenvolvidos em duplas ou trios.
> |Nome  | RA | Curso|
> |--|--|--|
> | Natália da Silva Guimarães  | 298997  | Mestrado em Engenharia Elétrica|
> | Oscar Eduardo Ortega Rodríguez  | 207726  | Mestrado em Engenharia Elétrica (Estudante Especial)|


## Descrição do Projeto
A segmentação e o delineamento manual de gliomas em exames de ressonância magnética (fMRI) representam uma tarefa exaustiva e sujeita a alta variabilidade intra e inter-observador. Este projeto tem como objetivo automatizar a extração de características e a segmentação de três sub-regiões tumorais críticas: o Tumor Inteiro (WT), o Núcleo do Tumor (TC) e o Tumor Realçado (ET). A motivação central é prover uma ferramenta analítica de precisão para apoiar o diagnóstico neuro-oncológico. Embora a concepção inicial do projeto englobe convoluções em 3D, o impacto e a relevância da solução atual baseiam-se em otimizar essa análise tridimensional através de técnicas 2.5D, garantindo alta precisão clínica sem incorrer em gargalos proibitivos de hardware (VRAM).

## Metodologia
A metodologia do projeto baseia-se em um pipeline de processamento de imagens médicas divididas nas seguintes etapas:

1. **Pré-processamento e Limpeza (Controle de Qualidade):**
   - **Normalização Estatística Restrita:** Aplicação de *Brain-Only Z-Score*, isolando os zeros (fundo/ar) para que o cálculo da média e desvio padrão reflita exclusivamente o contraste do tecido cerebral.
   - **Desconstrução do Ground Truth:** Conversão dos rótulos ordinais originais do dataset (1, 2, 4) em três canais binários simultâneos (Whole Tumor, Tumor Core, Enhancing Tumor) via portas lógicas.

2. **Engenharia de Dados (Fatiamento 2.5D):**
   - Implementação de um gerador de lotes (*DataGenerator*) que extrai janelas deslizantes ao longo do eixo Z. Para predizer a máscara da fatia central $z$, o modelo empilha as fatias $z-1$, $z$ e $z+1$ das 4 modalidades, gerando tensores hiper-profundos de 12 canais com uso de *Zero-Padding* nas bordas.

3. **Arquitetura de Modelagem e Otimização:**
   - Construção orientada a objetos de uma **ACU-Net (Attention-based Convolutional U-Net)** no framework PyTorch.
   - Integração de *Attention Gates* nas conexões residuais (*Skip Connections*) para focar matematicamente os pesos na região da patologia, filtrando o tecido saudável.
   - Uso da função de custo *Dice Loss* para contornar o extremo desequilíbrio espacial de classes (onde o tecido são domina >95% do volume).

## Bases de Dados e Evolução

| Base de Dados | Endereço na Web | Resumo descritivo |
| ----- | ----- | ----- |
| BraTS 2018 | [MICCAI BraTS](http://braintumorsegmentation.org/) | Reúne exames multimodais de fMRI (T1, T1ce, T2, FLAIR) de pacientes com gliomas de alto (HGG) e baixo grau (LGG), padronizados em 240x240x155. |
| BraTS 2020 | [MICCAI BraTS](http://braintumorsegmentation.org/) | Expansão da base original agregando maior volume de exames e heterogeneidade de *scanners*, fundamental para validação cruzada. |

> O detalhamento do processo de coleta, composição e o racional das escolhas de pré-processamento encontram-se documentados no Datasheet for Datasets localizado na pasta `data`.

## Ferramentas
- **Python:** Linguagem base de todo o fluxo computacional.
- **PyTorch:** Framework escolhido para a construção arquitetural da ACU-Net, gerenciamento de gradientes e instigação do *Dice Loss*.
- **SimpleITK:** Biblioteca para modelagem física avançada, especificamente para o cálculo do *N4 Bias Field Correction*.
- **Nibabel:** Extração e manipulação dos tensores brutos no formato neuro-médico NIfTI (`.nii.gz`).
- **NumPy & Matplotlib:** Manipulação da álgebra linear geométrica (Stacking 2.5D) e auditoria visual dos histogramas e predições inferidas.

## Workflow
> *(Após definição de continuação em 3D ou 2.5D será inserido a imagem aqui)*
> 
> Fluxograma planejado (2.5D): [Volumes NIfTI] -> [Otsu Mask & N4 Bias Correction] -> [Brain-Only Z-Score] -> [DataGenerator: Extração de Blocos 2.5D (12 canais)] -> [ACU-Net: Encoder -> Attention Gate -> Decoder] -> [Máscaras Preditivas WT, TC, ET] -> [Avaliação: Dice Coefficient].

## Experimentos e Resultados preliminares

No que se refere a implementação para a modelagem 3D, realizamos experimentos de segmentação 3D de tumores cerebrais usando o modelo ACU-Net 3D nos datasets BraTS 2018 e BraTS 2020. O modelo foi treinado com todas as modalidades (FLAIR, T1, T1CE, T2) e 64 fatias de profundidade por paciente. Para validação, utilizamos métricas como Dice, Jaccard, IoU, sensibilidade e especificidade. Observamos que o modelo conseguiu identificar corretamente as regiões maiores de tumor, mas apresentou falsos positivos em regiões menores e discretas, especialmente nos tumores ET e TC. As previsões 3D demonstraram sobreposição razoável com a máscara real, mas ainda há espaço para refinamento da segmentação fina.

## Próximos passos

**Sobre a modelagem em 3D inicial:**
- Ajuste de limiares e pós-processamento para reduzir falsos positivos (estimativa: 1 semana).
- Treinamento com batch maior ou aumento de épocas, usando toda a base de pacientes para melhorar a precisão global (estimativa: 2 semanas).
- Validação cruzada para avaliar robustez do modelo entre BraTS 2018 e 2020 (estimativa: 1 semana).
- Visualização avançada 3D integrando MRI real, tumor real e tumor previsto em uma mesma figura para análise qualitativa (estimativa: 3 dias).

**Migração Estratégica para Modelagem 2.5D:**
Devido aos severos gargalos de hardware e problemas de *Out of Memory* (OOM) encontrados nas convoluções tridimensionais, os próximos passos visam otimizar a extração das características espaciais:
- Substituição das funções `Conv3D` pesadas por convoluções `Conv2D` hiper-profundas (12 canais de entrada), permitindo que a rede avalie simultaneamente o contexto da fatia $z-1$, $z$ e $z+1$.
- Execução do Bucle de Treinamento em PyTorch utilizando ambiente acelerado por GPU (Colab T4), injetando os lotes 2.5D dinamicamente.
- Avaliação comparativa do *Dice Loss* entre a arquitetura 3D original e a nova estrutura 2.5D.

## Uso de IA Generativa
Utilizamos ChatGPT para:
- Elaborar explicações e interpretações dos resultados, comparando métricas do modelo com as do artigo original.
- Criar códigos de visualização 3D avançada, incluindo sobreposição de cérebro, tumor real (azul) e tumor previsto (vermelho), para apresentações e relatórios.
- Prompt exemplo: “Crie um modelo de segmentação 3D para tumores cerebrais usando Keras/TensorFlow. O modelo deve ser baseado em U-Net com atenção (ACU-Net), receber 4 modalidades de imagem (FLAIR, T1, T1CE, T2) com tamanho 128x128x64, e gerar 3 classes de saída (WT, TC, ET). Inclua: camadas Conv3D, BatchNormalization, MaxPooling3D, Dropout, Attention, Conv3DTranspose e concatenations necessárias. Mostre o resumo completo do modelo (model.summary()).”

Utilizamos o Gemini para:
- Desconstruir o fluxo matemático da rede ACU-Net e traduzir sua lógica orientada a objetos para o PyTorch (criando os módulos `DoubleConv` e `AttentionGate`).
- Estruturar o rigor do pré-processamento focado na remoção de viés magnético (N4 Bias Correction via SimpleITK).

## Referências
[1] Zhou, Z., Rahman Siddiquee, M. M., Tajbakhsh, N., Liang, J. UNet++: A Nested U-Net Architecture for Medical Image Segmentation. Deep Learning in Medical Image Analysis, 2018.
[2] Zhang, Z., Liu, Q., Wang, Y. Road Extraction by Deep Residual U-Net. IEEE Geoscience and Remote Sensing Letters, 2018. (inspiração para skip connections e atenção)
[3] Oktay, O., Schlemper, J., Folgoc, L. L., et al. Attention U-Net: Learning Where to Look for the Pancreas. arXiv:1804.03999, 2018.
[4] Talukder, M. A., et al. ACU-Net: Attention-based Convolutional U-Net model for segmenting brain tumors in fMRI images. Expert Systems with Applications, 2025.
[5] B. H. Menze, A. Jakab, S. Bauer, J. Kalpathy-Cramer, K. Farahani, J. Kirby, et al. "The Multimodal Brain Tumor Image Segmentation Benchmark (BRATS)", IEEE Transactions on Medical Imaging 34(10), 1993-2024 (2015) DOI: 10.1109/TMI.2014.2377694
[6] S. Bakas, H. Akbari, A. Sotiras, M. Bilello, M. Rozycki, J.S. Kirby, et al., "Advancing The Cancer Genome Atlas glioma MRI collections with expert segmentation labels and radiomic features", Nature Scientific Data, 4:170117 (2017) DOI: 10.1038/sdata.2017.117
[7] S. Bakas, M. Reyes, A. Jakab, S. Bauer, M. Rempfler, A. Crimi, et al., "Identifying the Best Machine Learning Algorithms for Brain Tumor Segmentation, Progression Assessment, and Overall Survival Prediction in the BRATS Challenge", arXiv preprint arXiv:1811.02629 (2018)