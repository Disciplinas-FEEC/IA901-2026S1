# Reconhecimento de padrões em Placas de Petri

# Pattern Recognition in Petri Dishes

![microbes](assets/microbes.gif)

> **Counting microbes with Math, not Magic.** 


## Apresentação

O presente projeto foi originado no contexto das atividades da disciplina de pós-graduação *IA901 - Análise de Imagens e Reconhecimento de Padrões*, 
oferecida no primeiro semestre de 2026, na Unicamp, sob supervisão da Profa. Dra. Leticia Rittner, do Departamento de Engenharia de Computação e Automação (DCA) da Faculdade de Engenharia Elétrica e de Computação (FEEC).



> |Nome  | RA | Curso|
> |--|--|--|
> | Leonardo Rafael Pires  | 178589  | Aluno Especial|
> | Laura Vieira Malachies   | 299117  | Mestranda em Tecnologia|
> | Gabriela Morales Souto  | 123456  | Mestranda em Ciência da Computação|



Este projeto é dedicado ao exploracão de metodologias de reconhecimento de padrões para a contagem automatizada de colônias de bactérias em placas de Petri, utilizando técnicas clássicas de Processamento Digital de Imagens e Técnicas de Deep Learning.

---


## Descrição do Projeto

## Objetivo
Substituir a contagem manual, cansativa e sujeita a erros por por um sistema automátizado. este projeto foca em **reconhecimento de padrões em imagem computacional** para as atividades de **detecção e segmentação de placas de Petri**.


##  Metodologia
A metodologia proposta combina técnicas clássicas de processamento digital de imagens com abordagens baseadas em aprendizado profundo para a detecção, segmentação e contagem automática de colônias bacterianas em placas de Petri. Para isso, o desenvolvimento foi organizado em três frentes complementares: pipelines clássicos de visão computacional, métodos de segmentação morfológica e modelos de deep learning voltados à detecção e segmentação de instâncias.

## 1. Aquisição e preparação dos dados

Inicialmente, foram utilizados dois conjuntos de dados distintos. O primeiro corresponde ao dataset AGAR (*AGAR: a microbial colony dataset for deep learning detection*), originalmente composto por aproximadamente 18 mil imagens anotadas com *bounding boxes*.

Além disso, foi utilizado um segundo conjunto proveniente do CNPEM (*Centro Nacional de Pesquisa em Energia e Materiais*). Nesse caso, um subconjunto contendo 100 imagens foi anotado manualmente com máscaras de segmentação de instâncias, permitindo a realização de experimentos de adaptação de domínio.

## 2. Pré-processamento

### 2.1 Definição da região de interesse

Como etapa inicial de pré-processamento, as imagens foram convertidas para escala de cinza e suavizadas por meio de um filtro de mediana \(5 x 5\), reduzindo ruídos de alta frequência. Em seguida, aplicou-se a Transformada de Hough para detecção da circunferência correspondente à placa de Petri, utilizando a relação:

$$
(x - a)^2 + (y - b)^2 = r^2
$$

em que \((a,b)\) representa o centro da circunferência e \(r\) o raio detectado.

A partir da circunferência identificada, foi gerada uma máscara binária utilizada para remover regiões externas à placa, restringindo o processamento apenas à área útil da imagem.

### 2.2 Seleção de canais e realce de contraste

Após a definição da região de interesse, diferentes espaços de cor foram avaliados, incluindo RGB, HSV, CMYK e CIE Lab. Nos experimentos clássicos realizados sobre o dataset AGAR, observou-se melhor separação das colônias utilizando o canal B do espaço RGB, que passou a ser adotado como canal principal de processamento.

Na sequência, aplicou-se o método CLAHE (*Contrast Limited Adaptive Histogram Equalization*) para realce adaptativo de contraste, favorecendo a distinção entre colônias e fundo da placa.

Adicionalmente, os histogramas dos canais foram utilizados para análise da distribuição de intensidades da imagem, definidos por:

$$
h(k) = \sum_{i=1}^{M} \sum_{j=1}^{N} \mathbf{1}[I(i,j)=k]
$$

onde \(I(i,j)\) representa a intensidade do pixel localizado na posição \((i,j)\).

### 2.3 Aumento de dados

Com o objetivo de aumentar a variabilidade do conjunto de treinamento e reduzir efeitos de sobreajuste, foram aplicadas técnicas de aumento de dados sobre o dataset AGAR. Entre as transformações empregadas destacam-se rotações, espelhamento horizontal, alterações de brilho e contraste, modificações de cor e aplicação de desfoque gaussiano.

## 3. Métodos clássicos de segmentação

### 3.1 Limiarização

Inicialmente, foram avaliadas diferentes estratégias de limiarização para segmentação das colônias bacterianas.

A primeira abordagem utilizou um limiar fixo aplicado diretamente ao canal B da imagem. A operação de binarização é descrita por:

$$
g(i,j) =
\begin{cases}
255, & \text{se } I(i,j) < T \\
0, & \text{caso contrário}
\end{cases}
$$

onde \(T\) representa o valor do limiar adotado.

Em seguida, avaliou-se o método de Otsu, responsável por selecionar automaticamente o limiar ótimo a partir da maximização da variância interclasse:

$$
\sigma_B^2(T) = \omega_0(T)\omega_1(T)[\mu_0(T)-\mu_1(T)]^2
$$

de modo que:

$$
T^* = \arg\max_T \sigma_B^2(T)
$$

Por fim, foi empregada a limiarização adaptativa gaussiana, na qual o limiar é calculado localmente para cada região da imagem:

$$
T(i,j) = \mu_{\text{local}}(i,j) - C
$$

em que $\mu_{\text{local}}(i,j)$ corresponde à média local ponderada e \(C\) representa uma constante de ajuste.

### 3.2 Top-Hat morfológico

Além das técnicas de limiarização, utilizou-se o operador morfológico Top-Hat aplicado sobre a versão invertida do canal B. Para isso, foi empregado um elemento estruturante elíptico de \(15 x 15\) pixels.

A operação é definida por:

$$
\text{TopHat}(f) = f - (f \circ B)
$$

onde \(f \circ B\) representa a abertura morfológica:

$$
f \circ B = (f \ominus B) \oplus B
$$

Após a aplicação do operador, a imagem resultante foi segmentada utilizando limiarização automática por Otsu.

### 3.3 Subtração de fundo por estimativa gaussiana

Outra estratégia investigada consistiu na subtração de fundo utilizando filtros gaussianos de grandes dimensões, com kernels de \(151 x 151\) e \(71 x 71\) pixels.

Inicialmente, o fundo estimado foi obtido pela convolução da imagem com um kernel gaussiano:

$$
\hat{B}(i,j) = (I * G_\sigma)(i,j)
$$

onde:

$$
G_\sigma(m,n) =
\frac{1}{2\pi\sigma^2}
\exp\left(
-\frac{m^2+n^2}{2\sigma^2}
\right)
$$

Posteriormente, calculou-se a imagem diferencial:

$$
D(i,j)=|\hat{B}(i,j)-I(i,j)|
$$

A imagem resultante foi então normalizada para o intervalo \([0,255]\):

$$
D_{\text{norm}}(i,j)=
255\cdot
\frac{D(i,j)-D_{\min}}
{D_{\max}-D_{\min}}
$$

Finalmente, aplicou-se o método de Otsu para obtenção da máscara binária segmentada.

### 3.4 Clusterização K-Means

Também foi avaliada uma abordagem baseada em clusterização K-Means utilizando quatro grupos distintos. Nesse caso, os canais \(L\) e \(b\) do espaço Lab foram utilizados após aplicação de CLAHE.

Após a convergência do algoritmo, o agrupamento correspondente às colônias foi selecionado com base nos valores de luminosidade dos centróides obtidos.

## 4. Separação de colônias sobrepostas

Considerando a ocorrência frequente de colônias conectadas ou parcialmente sobrepostas, aplicou-se o algoritmo Watershed associado à transformada de distância para separação das regiões segmentadas.

Inicialmente, os máximos locais da transformada de distância foram utilizados como marcadores internos para propagação das fronteiras entre objetos adjacentes. Em seguida, realizou-se um pós-processamento morfológico por fechamento utilizando um kernel \(5 x 5\), reduzindo pequenas descontinuidades nas máscaras segmentadas.

O fechamento morfológico é definido por:

$$
f \bullet B = (f \oplus B) \ominus B
$$

em que \(f\) representa a imagem de entrada, \(B\) o elemento estruturante, \(\oplus\) a operação de dilatação e \(\ominus\) a operação de erosão.

Essa operação consiste na aplicação sequencial de uma dilatação seguida de uma erosão utilizando o mesmo elemento estruturante, sendo empregada para preencher pequenas lacunas, conectar regiões próximas e suavizar contornos sem alterar significativamente a forma original dos objetos.

## 5. Contagem baseada em filtros geométricos

Após a segmentação, a contagem das colônias foi realizada por meio da rotulagem de componentes conectados presentes na máscara binária.

Na sequência, aplicaram-se filtros geométricos baseados em área, circularidade e solidez, permitindo remover artefatos e componentes incompatíveis com o formato esperado das colônias.

A contagem final foi definida por:

$$
N_{\text{colônias}} =
\#\{
k \geq 1 : A_k \geq A_{\min}
\}
$$

onde \(A_k\) representa a área do componente conectado.

Além disso, a circularidade utilizada nos filtros geométricos foi calculada por:

$$
C =
\frac{
4\pi \times \text{área}
}{
\text{perímetro}^2
}
$$

## 6. Métodos de aprendizado profundo

### 6.1 Detecção com YOLOv5s

No contexto dos métodos baseados em deep learning, inicialmente foi empregado o modelo YOLOv5s pré-treinado no ImageNet. O modelo foi submetido a *fine-tuning* utilizando o dataset AGAR previamente processado.

O treinamento foi realizado durante 100 épocas, utilizando *batch size* igual a 32 e imagens redimensionadas para \(640 x 640\) pixels.

### 6.2 Adaptação de domínio com segmentação

Posteriormente, o backbone treinado na etapa anterior foi utilizado como ponto de partida para um modelo de segmentação de instâncias baseado em YOLOv8s-seg.

Essa estratégia permitiu realizar adaptação de domínio utilizando as imagens anotadas manualmente no CNPEM, adequando o modelo às condições reais de aquisição presentes no novo conjunto de dados.

### 6.3 Enriquecimento de anotações com SAM 2.1

Adicionalmente, o modelo SAM 2.1 (*Segment Anything Model*) foi utilizado para geração automática de máscaras de segmentação a partir das *bounding boxes* disponíveis no dataset AGAR.

As máscaras geradas foram posteriormente utilizadas para enriquecimento das anotações destinadas ao treinamento dos modelos de segmentação.

## 7. Avaliação experimental

Por fim, os métodos clássicos foram avaliados utilizando os valores de referência disponíveis nos datasets empregados. Já os modelos de aprendizado profundo foram avaliados a partir das métricas de precisão, *recall*, mAP@0.5 e mAP@0.5:0.95 utilizando o conjunto de validação do dataset AGAR.


## Bases de Dados e Evolução
[Datasheet](IA901-2026S1/projetos/pattern-recognition-in-petri-dishes/assets/datasheet.md)

Base de Dados | Endereço na Web | Resumo descritivo
----- | ----- | -----
AGAR: A Microbial Colony Dataset for Deep Learning Detection | https://agar.neurosys.com/ | Dataset público composto por aproximadamente 18.000 imagens de placas de Petri, abrangendo cinco microrganismos distintos em culturas isoladas ou mistas. As imagens foram adquiridas sob diferentes condições de iluminação e com duas câmeras distintas. As anotações estão disponíveis em formato JSON e incluem bounding boxes individuais por colônia, classe do microrganismo e contagem total. Distribuído sob licença Creative Commons Attribution-NonCommercial 2.0 Generic.
Dataset CNPEM (LNNano) — interno | https://1drv.ms/f/c/ab5109ec6b881bc2/IgCoHt5JsShGSIm4lrKCn3rvASVMI3zXC6TBj2YiSYWSX78?e=njq0hx | Dataset coletado por pesquisadores do CNPEM (LNNano), contendo aproximadamente 300 imagens de colônias de bactérias e fungos em placas de Petri. Apresenta variação no meio de cultura, porém com condições padronizadas de aquisição (iluminação fixa e captura por smartphone). As imagens estão originalmente no formato HEIC e as anotações consistem na contagem total de colônias por imagem, sem informação espacial.


## Ferramentas
As ferramentas e bibliotecas utilizadas ao longo do projeto estão listadas a seguir:

- **Python 3** — linguagem principal utilizada no desenvolvimento de todos os pipelines
- **OpenCV** — processamento de imagens, incluindo Transformada de Hough, operações morfológicas, filtros, Watershed e rotulagem de componentes conectados
- **NumPy / SciPy** — operações matriciais e cálculo da transformada de distância
- **Pillow / pillow-heif** — leitura e conversão das imagens originais nos formatos HEIC e JPEG para PNG
- **Matplotlib** — visualização de resultados intermediários e histogramas de intensidade
- **Ultralytics (YOLOv5 / YOLOv8)** — treinamento, fine-tuning e inferência dos modelos de detecção e segmentação de instâncias
- **SAM 2.1 (Segment Anything Model — Meta AI)** — geração automática de máscaras de segmentação a partir de bounding boxes para enriquecimento das anotações
- **CVAT** — ferramenta utilizada para anotação manual das imagens do dataset CNPEM

## Workflow


## Experimentos e Resultados preliminares
### Experimento 1 — Limiarização (Otsu, adaptativa e limiar fixo)

Três estratégias de limiarização foram avaliadas sobre o canal B do espaço RGB após a aplicação de CLAHE. O método de Otsu apresentou limitações importantes: como o histograma das imagens recortadas é dominado pelos pixels do fundo mascarado (valor zero), o limiar calculado automaticamente foi deslocado para valores excessivamente altos, resultando em baixa sensibilidade para detecção das colônias. A limiarização adaptativa gaussiana produziu resultados melhores em parte das amostras, porém mostrou-se inconsistente ao ser aplicada sobre imagens com diferentes condições de iluminação e variação de contraste.

**Problema identificado:** nenhuma das abordagens de limiarização apresentou generalização satisfatória para o conjunto completo de imagens do dataset AGAR.

### Experimento 2 — Top-Hat morfológico

O operador Top-Hat com elemento estruturante elíptico de \(15 \times 15\) pixels, seguido de limiarização por Otsu, demonstrou boa capacidade de realce das colônias em imagens com fundo relativamente uniforme. Entretanto, o desempenho foi prejudicado em amostras com variação acentuada de iluminação ou com colônias de tonalidade próxima à do ágar.

**Problema identificado:** sensibilidade elevada à uniformidade do fundo, com degradação do desempenho em imagens com condições de captura distintas das utilizadas na calibração dos parâmetros.

### Experimento 3 — Subtração de fundo por estimativa gaussiana

A subtração de fundo com kernels gaussianos de grandes dimensões (\(151 \times 151\) e \(71 \times 71\) pixels) apresentou resultados satisfatórios para um subconjunto específico de imagens, realçando as colônias ao cancelar o gradiente de iluminação de fundo. No entanto, ao se ampliar o conjunto de imagens avaliadas, surgiram erros relevantes de contagem, com desempenho especialmente insatisfatório para colônias de maior dimensão. Adicionalmente, a presença de anotações manuscritas nas placas de AGAR interferiu na segmentação, sendo frequentemente detectadas como componentes válidos.

**Problema identificado:** baixa generalização para imagens com condições de captura distintas e dificuldade em lidar com colônias de morfologia variada.

### Experimento 4 — Clusterização K-Means

A abordagem K-Means com \(k=4\) clusters aplicada sobre os canais \(L\) e \(b\) do espaço CIE Lab após CLAHE produziu resultados mais consistentes entre amostras do que as estratégias de limiarização. A seleção do cluster correspondente às colônias pelo centróide de luminosidade mostrou-se estável frente a variações de iluminação. Contudo, o método apresentou dificuldades em imagens cujas colônias possuem tonalidade muito próxima à do ágar, gerando erros de segmentação.

**Problema identificado:** dependência do contraste entre colônia e fundo para correta identificação do cluster relevante.

### Experimento 5 — Watershed para separação de colônias sobrepostas

O algoritmo Watershed com transformada de distância foi aplicado como etapa de pós-processamento após a binarização, com o objetivo de separar colônias conectadas ou parcialmente sobrepostas. O método funcionou satisfatoriamente para sobreposições parciais, onde os picos locais da transformada de distância foram suficientes para diferenciar instâncias adjacentes. No entanto, o algoritmo não foi capaz de separar colônias completamente fundidas, situação recorrente em imagens com alta densidade de colônias.

**Problema identificado:** limitação intrínseca do método para colônias com sobreposição total ou fusão de contornos.

### Experimento 6 — Detecção com YOLOv5s (fine-tuning no dataset AGAR)

O modelo YOLOv5s pré-treinado no ImageNet foi submetido a fine-tuning utilizando 13.489 imagens do dataset AGAR, durante 100 épocas com *batch size* 32 e imagens redimensionadas para \(640 \times 640\) pixels. Os resultados obtidos no conjunto de validação foram:

| Métrica | Valor |
|---|---|
| Precisão | 98% |
| Recall | 95% |
| mAP@0.5 | 96% |
| mAP@0.5:0.95 | 94% |

Os resultados indicam que o modelo generalizou bem para o domínio do dataset AGAR. Entretanto, ao realizar inferência direta sobre imagens do CNPEM, observou-se queda de desempenho expressiva, evidenciando a necessidade de adaptação de domínio.

### Experimento 7 — Adaptação de domínio com YOLOv8s-seg (fine-tuning no dataset CNPEM)

O backbone treinado no AGAR foi utilizado como ponto de partida para um modelo de segmentação de instâncias baseado em YOLOv8s-seg, submetido a fine-tuning com 38 imagens anotadas do CNPEM. O resultado preliminar demonstrou que a adaptação de domínio com poucos exemplos é viável, com segmentação visual razoável das colônias presentes nas imagens do CNPEM. Contudo, as máscaras geradas ainda apresentam imprecisões nos contornos, especialmente em colônias maiores e em regiões de sobreposição.

**Problema identificado:** com apenas 38 imagens de treinamento, a qualidade dos contornos de segmentação é limitada. O enriquecimento das anotações com o SAM 2.1 é a principal estratégia proposta para superar essa limitação.

## Próximos passos


## Uso de IA Generativa
> Adicione aqui em quais tarefas foi usada alguma ferramenta de IA Generativa. Para cada tarefa indicada detalhe qual a ferramenta e qual o prompt utilizado.


## Referências

Beucher, S., & Meyer, F. (1993). *The morphological approach to segmentation: the watershed transformation*. Mathematical Morphology in Image Processing, 34, 433–481.

  Bradley, D., & Roth, G. (2007). *Adaptive thresholding using the integral image*. Journal of Graphics Tools, 12(2), 13–21. Disponível em: https://www.taylorfrancis.com/chapters/edit/10.1201/9781482277234-12/morphological-approach-segmentation-watershed-transformation-beucher-meyer

  Bradski, G., & Kaehler, A. (2008). *Learning OpenCV: Computer Vision with the OpenCV Library*. O'Reilly Media. Disponível em: https://www.hlevkin.com/hlevkin/45MachineDeepLearning/ML/Learning-OpenCV.pdf

  Dolu, M., Altıntaş, M. E., Duman, E., & Kılıç, G. B. (2025). YOLO-Based Counting of Small and Overlapping Bacterial Colonies: Performance Analysis and Real-Time Mobile Deployment. 2025 10th International Conference on Computer Science and Engineering (UBMK), 1042–1046. https://doi.org/10.1109/UBMK67458.2025.11206979

  Galope, R., Lisondra, C., & Nanual, A. (2024). Automated Bacteria Colony Counting using Hybrid Image Segmentation Algorithm and YOLOv5 Transfer Learning Model. International Conference on Innovative Practices in Management, Engineering & Social Sciences, IPMESS-24. https://doi.org/10.37082/IJIRMPS.IPMESS-24.6

  Gonzalez, R. C., & Woods, R. E. (2018). *Digital Image Processing* (4th ed.). Pearson.

  Haralick, R. M., Sternberg, S. R., & Zhuang, X. (1987). *Image analysis using mathematical morphology*. IEEE Transactions on Pattern Analysis and Machine Intelligence, 9(4), 532–550. Disponível em: https://ieeexplore.ieee.org/document/4767941

  He, L., Ren, X., Gao, Q., Zhao, X., Yao, B., & Chao, Y. (2017). *The connected-component labeling problem: A review of state-of-the-art algorithms*. Pattern Recognition, 70, 25–43. Disponível em: https://www.sciencedirect.com/science/article/pii/S0031320317301693

  Hough, P. V. C. (1962). *Method and means for recognizing complex patterns*. U.S. Patent 3,069,654.

  Jiang, H., Guo, Q., Zhi, X., Li, H., & Chen, Y. (2026). A weakly supervised framework for automated biological assay assessment. Virus Research, 363, 199677. https://doi.org/10.1016/j.virusres.2025.199677

  Jocher, G., et al. (2020). *ultralytics/yolov5*. Zenodo. https://doi.org/10.5281/zenodo.3908559

  Majchrowska, S., Pawłowski, J., Guła, G., Bonus, T., Hanas, A., Loch, A., Pawlak, A., Roszkowiak, J., Golan, T., & Drulis-Kawa, Z. (2021). *AGAR: A microbial colony dataset for deep learning detection*. Disponível em: arXiv. https://arxiv.org/abs/2108.01234

  Otsu, N. (1979). *A threshold selection method from gray-level histograms*. IEEE Transactions on Systems, Man, and Cybernetics, 9(1), 62–66. Disponível em: https://ieeexplore.ieee.org/document/4310076

  Ravi, N., et al. (2024). *SAM 2: Segment Anything in Images and Videos*. arXiv:2408.00714. Disponível em: https://arxiv.org/abs/2408.00714 

  Sezgin, M., & Sankur, B. (2004). *Survey over image thresholding techniques and quantitative performance evaluation*. Journal of Electronic Imaging, 13(1), 146–168.




