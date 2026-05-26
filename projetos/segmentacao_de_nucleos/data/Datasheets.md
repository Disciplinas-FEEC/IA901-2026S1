# Datasheets for Datasets



O presente documento tem como objetivo descrever e documentar os datasets utilizados no projeto computacional. A proposta é que ele funcione como uma espécie de ficha técnica dos conjuntos de dados considerados, inspirada nas práticas já consolidadas em outras áreas da engenharia, como discutido no artigo “Datasheets for Datasets”¹. 

A referência também discute a ausência de um processo padronizado de documentação de datasets na comunidade de aprendizado de máquina, algo que pode levar a consequências importantes em aplicações tecnológicas reais. Inspirado nessa ideia, este documento busca reunir informações essenciais sobre os conjuntos de dados utilizados no projeto, incluindo motivação, composição, processo de coleta, distribuição e limitações. Dessa forma, pretende-se facilitar a compreensão das características e restrições de cada base antes de sua utilização.

O projeto computacional desenvolvido, intitulado “Segmentação de núcleos em imagens histológicas com deep learning: comparação entre arquiteturas e datasets”, utiliza três datasets principais: MoNuSeg, PanNuke e NuInsSeg. De maneira geral, todos eles são conjuntos de dados públicos voltados para aplicações em patologia digital, sendo utilizados no treinamento e avaliação de modelos de visão computacional para segmentação de núcleos celulares em imagens histológicas. As informações apresentadas nas seções seguintes foram obtidas principalmente a partir dos artigos originais que introduziram cada uma dessas bases à comunidade científica² ³ ⁴.


## Motivação

### MoNuSeg

O MoNuSeg foi desenvolvido com o objetivo de incentivar a criação de métodos de segmentação capazes de generalizar entre diferentes órgãos, hospitais e condições patológicas. A ideia principal era construir uma base que permitisse avaliar algoritmos em cenários mais próximos da prática real, evitando soluções excessivamente dependentes de um único domínio.

### NuInsSeg

O NuInsSeg surgiu da necessidade de disponibilizar um conjunto de dados grande e totalmente anotado manualmente para segmentação de instâncias. Os autores destacam que muitos datasets médicos utilizam modelos automáticos para auxiliar nas anotações, o que pode introduzir vieses ocultos. Dessa forma, a proposta da base foi oferecer anotações produzidas integralmente de forma manual.

### PanNuke

O PanNuke foi criado com a proposta de fornecer um dataset pan-câncer mais representativo das condições reais encontradas em aplicações clínicas. Diferentemente de outras bases que selecionam apenas imagens de alta qualidade, o PanNuke inclui também regiões borradas, queimadas ou mal coradas, buscando reduzir vieses de amostragem.



## Composição

### MoNuSeg

O dataset é composto por imagens histológicas coradas com H&E, com resolução de 1000×1000 pixels e ampliação de 40x. A base contém 30 imagens de treinamento, totalizando 21.623 núcleos anotados, e 14 imagens de teste, contendo 7.223 núcleos. As amostras abrangem múltiplos órgãos, incluindo mama, fígado, rim, próstata, bexiga, pulmão, cérebro e cólon.

### NuInsSeg

O NuInsSeg contém 665 recortes de imagens histológicas de 512×512 pixels, também obtidas com ampliação de 40x. Ao todo, a base possui 30.698 núcleos provenientes de 31 órgãos diferentes de humanos e camundongos. Um diferencial importante é a presença de máscaras de áreas ambíguas, correspondentes a regiões em que nem mesmo especialistas conseguem definir com precisão os limites nucleares.

### PanNuke

O PanNuke é composto por 7904 imagens histológicas RGB de 256×256 pixels, extraídas de 455 campos visuais provenientes de mais de 20 mil lâminas histológicas inteiras (WSIs). O dataset contém aproximadamente 216 mil núcleos anotados, distribuídos entre 19 tipos de tecidos. Além das máscaras de segmentação de instância, os núcleos também são classificados em diferentes categorias celulares, como células epiteliais, inflamatórias, malignas, necróticas e estromais.



## Processo de Coleta

### MoNuSeg

As imagens foram obtidas a partir do The Cancer Genome Atlas (TCGA), envolvendo dados provenientes de diferentes hospitais para aumentar a variabilidade visual da base. As anotações foram realizadas manualmente com auxílio do software Aperio ImageScope e posteriormente revisadas por patologistas experientes.

### NuInsSeg

As amostras do NuInsSeg foram obtidas a partir da coleção da Universidade Médica de Viena e de tecidos de camundongos C57BL/6J. O processo de anotação foi realizado manualmente utilizando o software ImageJ, com revisão posterior por especialistas da área.

### PanNuke

O PanNuke foi construído a partir de imagens provenientes do TCGA e de conjuntos internos dos autores. O processo de anotação utilizou uma abordagem semi-automática, combinando modelos computacionais e validação humana realizada por patologistas.



## Pré-processamento / Limpeza / Rotulação

### MoNuSeg

As anotações dos núcleos foram disponibilizadas em formato XML, contendo as coordenadas dos contornos celulares. Isso facilita o treinamento de modelos capazes de separar núcleos muito próximos ou sobrepostos. Nos casos ambíguos, os autores adotaram critérios visuais para definir os limites nucleares.

### NuInsSeg

As imagens do NuInsSeg foram obtidas a partir de recortes centrais das lâminas histológicas. Além das máscaras binárias tradicionais, o dataset também disponibiliza máscaras auxiliares, como mapas de distância e pesos de borda, utilizados para auxiliar o treinamento de modelos de segmentação.

### PanNuke

Durante a construção do PanNuke, os autores utilizaram técnicas de aumento de dados e estratégias de balanceamento para melhorar a representatividade das diferentes classes celulares. O processo de refinamento das anotações também levou em consideração regiões com artefatos e falsos positivos comuns em imagens histológicas reais.



## Usos

### MoNuSeg

O MoNuSeg é amplamente utilizado na avaliação de modelos de segmentação nuclear com foco em capacidade de generalização, especialmente em tecidos não vistos durante o treinamento.

### NuInsSeg

O NuInsSeg é indicado tanto para treinamento de modelos de segmentação quanto para avaliação de generalização em bases externas. As máscaras de áreas ambíguas também permitem investigar regiões difíceis mesmo para especialistas humanos.

### PanNuke

O PanNuke foi desenvolvido para aplicações conjuntas de segmentação de instâncias e classificação celular. Sua diversidade de tecidos e presença de artefatos tornam a base particularmente útil em estudos mais próximos de cenários clínicos reais.



## Distribuição

### MoNuSeg

O MoNuSeg foi disponibilizado publicamente no contexto do desafio MICCAI 2018 e permanece acessível por meio da plataforma Grand Challenge.

### NuInsSeg

O NuInsSeg pode ser obtido em plataformas públicas de compartilhamento de dados científicos, como Zenodo e Kaggle.

### PanNuke

O PanNuke foi disponibilizado publicamente pelos autores juntamente com códigos e materiais auxiliares relacionados ao artigo original.



## Manutenção

Embora a documentação sobre atualizações das bases seja limitada, os três datasets permanecem associados às instituições de pesquisa responsáveis por sua criação. Além disso, a utilização de plataformas amplamente utilizadas pela comunidade científica, como Grand Challenge, Zenodo, Kaggle e GitHub, contribui para a preservação e disponibilidade dos dados ao longo do tempo.




## Referências

¹ GEBRU, Timnit et al. *Datasheets for Datasets*. arXiv preprint arXiv:1803.09010, 2021.

² KUMAR, Neeraj et al. *A Multi-Organ Nucleus Segmentation Challenge*. IEEE Transactions on Medical Imaging, v. 39, n. 5, p. 1380–1391, 2020.

³ LJUBENOVIĆ, M. et al. *NuInsSeg: A Fully Annotated Dataset for Nuclei Instance Segmentation in H&E-Stained Histological Images*. arXiv preprint arXiv:2207.04643, 2022.

⁴ GAMPER, Jevgenij et al. *PanNuke: An Open Pan-Cancer Histology Dataset for Nuclei Instance Segmentation and Classification*. In: European Congress on Digital Pathology. Springer, 2019. p. 11–19.