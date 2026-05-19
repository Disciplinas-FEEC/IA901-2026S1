# `<Título em Português do Projeto>`
# `<Project Title in in English>`

## Apresentação

O presente projeto foi originado no contexto das atividades da disciplina de pós-graduação *IA901 - Análise de Imagens e Reconhecimento de Padrões*, 
oferecida no primeiro semestre de 2026, na Unicamp, sob supervisão da Profa. Dra. Leticia Rittner, do Departamento de Engenharia de Computação e Automação (DCA) da Faculdade de Engenharia Elétrica e de Computação (FEEC).

|Nome  | RA | Curso|
|--|--|--|
| Brendon Erick Euzébio Rus Peres  | 256130  | Mestrado em xxxx|
| Luís Fernando Silva Lima  | 298966 | Mestrado em Engenharia Elétrica |
| Mateus Bizzo da Silva  | 200216  | Mestrado em xxxx|


## Descrição do Projeto
A segmentação semântica de imagens aéreas agrícolas é uma das principais direções de pesquisa no campo da visão agrícola. Um algoritmo eficaz de segmentar terras agrícolas aéreas é muito importante para a detecção de áreas de anomalias no campo, como a segmentação de áreas secas, fim de linha, deficiência de nutrientes e assim por diante. O reconhecimento do padrão de anomalia é útil para monitorar o estado local das terras agrícolas, avaliar o impacto de desastres naturais. A análise de imagens aéreas agrícolas também apoia a formulação de políticas agrícolas nacionais para aumentar o rendimento dos campos agrícolas e o desenvolvimento econômico regional [4].

Falar sobre imagens multiespectrais

<div align="center">
  <img src="assets/1718303710189.png" alt="Representação do Espectro Eletromagnético" width="600">
  
  <p>
    <b>Figura 1:</b> Representação visual do espectro eletromagnético.
    <br>
    <i>Fonte: <a href="https://www.linkedin.com/pulse/câmeras-multiespectrais-e-hiperespectrais-embarcadas-em-thiago-silva--iau3f/" target="_blank">Thiago Silva (2026)</a>.</i>
  </p>
</div>

Além disso, Sa et al. [7] propuseram o WeedMap, um framework de mapeamento semântico que utiliza imagens multiespectrais para otimizar a detecção de espécies invasoras na agricultura de precisão e seus resultados mostraram que o NVDI (Normalized Difference Vegetation Index) contribui significativamente para uma classificação precisa da vegetação. A partir dessa premissa, espera-se que a inclusão dessa informação espectral resulte em uma maior eficiência na segmentação de bordas e anomalias complexas. Ao fornecer um contraste nítido entre diferentes níveis de vigor vegetativo, o índice reduz o ruído de iluminação nas imagens aéreas, permitindo que o modelo delimite com precisão as transições de estresse foliar, como zonas de seca ou deficiência de nutrientes.

A principal motivação deste trabalho é verificar a eficácia de modelos de segmentação semântica integrados aos subespaços do NDVI e NDWI, com vistas à sua aplicação no monitoramento de lavouras e na identificação de anomalias em imagens aéreas agrícolas. O sistema proposto deve ser capaz de processar dados multiespectrais para delimitar com precisão regiões de estresse vegetativo e corpos d'água superficiais, correlacionando os índices radiométricos com as classes de interesse. O resultado esperado do modelo será a geração de máscaras de segmentação semanticamente consistentes, onde os limites geométricos das anomalias sejam preservados de forma estatisticamente e espacialmente coerente com os dados reais de entrada.

> Descrição do objetivo principal do projeto, incluindo contexto gerador, motivação, etc. Qual problema você pretende solucionar? Qual a relevância do problema e o impacto da solução do mesmo?

## Metodologia
#### Detecção de Vegetação Usando NDVI
Para criar o espaço semântico, o primeiro subespaço é o NDVI que é a combinação dos canais Vermelho (Red) e Infravermelho próximo (NIR). Este subespaço está relacionado ao índice de vegetação por diferença normalizada, que é um índice de verdejamento ou atividade fotossintética das plantas e um dos índices de vegetação comumente usados [8]. O NDVI é definido pela equação (1), calculada pelos pixels vermelho e infravermelho.

$$
\begin{array}{cc}
NDVI = \dfrac{NIR - RED}{NIR + RED} & \text{(1)}
\end{array}
$$

Onde NIR é o valor do pixel infravermelho próximo e RED é o valor do pixel vermelho.

#### Detecção de água usando NDWI
O segundo subespaço necessário para a criação do espaço semântico no monitoramento agrícola é o NDWI. Este subespaço é definido pelos eixos Verde (Green) e Infravermelho próximo (IR). A combinação desses dois canais pode ser utilizada tanto para analisar o teor de água nas folhas das plantas quanto para delimitar corpos d'água na superfície [8]. O NDWI pode ser obtido através da equação (2).

$$
\begin{array}{cc}
NDWI = \dfrac{GREEN - NIR}{GREEN + IR} & \text{(2)}
\end{array}
$$

Onde GREEN é o valor do pixel verde e NIR é o valor do pixel infravermelho próximo.

> Proposta de metodologia incluindo especificação de quais técnicas pretende-se explorar. Espera-se que nesta entrega você já seja capaz de descrever de maneira mais específica (do que na Entrega 1) quais as técnicas a serem empregadas em cada etapa do projeto.

## Bases de Dados e Evolução
> Elencar as bases de dados utilizadas no projeto.

Base de Dados | Endereço na Web | Resumo descritivo
----- | ----- | -----
Agriculture-Vision | https://www.agriculture-vision.com/agriculture-vision-2021/dataset-2021 | Dataset voltado para a agricultura de precisão, composto por 94.986 imagens aéreas multiespectrais (RGB e NIR). Ele apresenta nove classes de anomalias as quais podem ser utilizadas para segmentação semântica.

> [Link para o datasheet do dataset](https://docs.google.com/document/d/1QEhjC9ITwu-VQRwQzN5-8O_ES_J7Koa9mj8wCiMX2tE/edit?usp=sharing)

## Ferramentas
> Ferramentas e/ou bibliotecas já utilizadas e/ou ainda a serem utilizadas (com base na visão atual do grupo sobre o projeto).

## Workflow
> Use uma ferramenta que permita desenhar o workflow e salvá-lo como uma imagem (Draw.io, por exemplo). Insira a imagem nesta seção.
> Você pode optar por usar um gerenciador de workflow (Sacred, Pachyderm, etc) e nesse caso use o gerenciador para gerar uma figura para você.
> Lembre-se que o objetivo de desenhar o workflow é ajudar a quem quiser reproduzir seus experimentos.
> Mais informações sobre o workflow podem ser encontradas nos materiais de apoio no Classroom (Reprodutibilidade em pesquisa computacional - workflow).

## Experimentos e Resultados preliminares
> Descreva de forma sucinta e organizada os experimentos realizados.
> Para cada experimento, apresente os principais resultados obtidos.
> Aponte os problemas encontrados nas soluções testadas até aqui.

## Próximos passos
> Liste as próximas etapas planejadas para conclusão do projeto, com uma estimativa de tempo para cada etapa.

## Uso de IA Generativa
### Auxílio na parte gramatical do datasheet
O Gemini foi utilizado no ajuste gramatical e na conversão dos textos para inglês. Prompt utilizado: 
> "Escreva o seguinte trecho em inglês ajustando erros gramaticais quando necessário:"
### Auxílio na criação dos códigos
Foi utilizado o Gemini para a criação dos códigos de navegação entre os diretórios do dataset. Prompt utilizado:
> "Dado os seguintes diretórios escreva um código que permita acessar as imagens presentes nas pastas."

## Referências
[1] CHIU, Mang Tik et al. Agriculture-vision: A large aerial image database for agricultural pattern analysis. In: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. 2020. p. 2828-2838.

[2] CHIU, Mang Tik et al. The 1st agriculture-vision challenge: Methods and results. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops. 2020. p. 48-49.

[3] Buvanesh, Anirudh & Narang, Pratik & Sinha, Soumendu. (2021). Proposing A Deep Learning Based Architecture for Agriculture Vision. 10.13140/RG.2.2.26628.86404. 

[4] SHEN, Yao; WANG, Lei; JIN, Yue. AAFormer: A multi-modal transformer network for aerial agricultural images. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 2022. p. 1705-1711.

[5] INNANI, Shubham et al. Fuse-pn: A novel architecture for anomaly pattern segmentation in aerial agricultural images. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 2021. p. 2960-2968.

[6] SAHIN, Halil Mertkan et al. Segmentation of weeds and crops using multispectral imaging and CRF-enhanced U-Net. Computers and Electronics in Agriculture, v. 211, p. 107956, 2023.

[7] SA, Inkyu et al. WeedMap: A large-scale semantic weed mapping framework using aerial multispectral imaging and deep neural network for precision farming. Remote Sensing, v. 10, n. 9, p. 1423, 2018.

[8] WIJITDECHAKUL, Jinmika et al. UAV-based multispectral image analysis system with semantic computing for agricultural health conditions monitoring and real-time management. In: 2016 International Electronics Symposium (IES). IEEE, 2016. p. 459-464.
