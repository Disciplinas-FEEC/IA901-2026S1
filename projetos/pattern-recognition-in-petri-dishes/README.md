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
> | Gabriela Morales Souto  | 299213  | Mestranda em Ciência da Computação|



Este projeto é dedicado ao exploracão de metodologias de reconhecimento de padrões para a contagem automatizada de colônias de bactérias em placas de Petri, utilizando técnicas clássicas de Processamento Digital de Imagens e Técnicas de Deep Learning.

---


## Descrição do Projeto

## Objetivos

### Objetivo geral

Desenvolver e avaliar um pipeline de ponta a ponta para **segmentação, detecção e contagem automática de colônias em placas de Petri**, reduzindo a dependência da contagem manual.

### Objetivos específicos

- Preparar imagens de diferentes formatos e resoluções para análise computacional.
- Detectar automaticamente a região de interesse correspondente à placa de Petri.
- Testar métodos clássicos de segmentação e contagem de colônias.
- Treinar modelos de aprendizado profundo para detecção e segmentação.
- Comparar métodos clássicos e modelos deep learning quanto a desempenho, robustez e limitações.
- Investigar estratégias de adaptação de domínio entre os datasets AGAR e CNPEM.


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

Base de Dados | Resumo descritivo | Endereço na Web
----- | ----- | -----
AGAR: A Microbial Colony Dataset for Deep Learning Detection | Dataset público composto por aproximadamente 18.000 imagens de placas de Petri, abrangendo cinco microrganismos distintos em culturas isoladas ou mistas. As imagens foram adquiridas sob diferentes condições de iluminação e com duas câmeras distintas. As anotações estão disponíveis em formato JSON e incluem bounding boxes individuais por colônia, classe do microrganismo e contagem total. Distribuído sob licença Creative Commons Attribution-NonCommercial 2.0 Generic.| https://agar.neurosys.com/
Dataset CNPEM (LNNano) — interno| Dataset coletado por pesquisadores do CNPEM (LNNano), contendo aproximadamente 300 imagens de colônias de bactérias e fungos em placas de Petri. Apresenta variação no meio de cultura, porém com condições padronizadas de aquisição (iluminação fixa e captura por smartphone). As imagens estão originalmente no formato HEIC e as anotações consistem na contagem total de colônias por imagem, sem informação espacial.|https://1drv.ms/f/c/ab5109ec6b881bc2/IgCoHt5JsShGSIm4lrKCn3rvASVMI3zXC6TBj2YiSYWSX78?e=njq0hx


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

O workflow do projeto foi organizado para representar as principais etapas necessárias para reproduzir os experimentos, desde a preparação das bases de dados até a avaliação dos métodos clássicos e baseados em aprendizado profundo.

![Workflow do projeto](assets/Pipeline Contagem de Colônias.jpg)

## Experimentos e Resultados preliminares

Nesta etapa do projeto, foram realizados experimentos com métodos clássicos de processamento de imagens e com modelos baseados em aprendizado profundo. Os experimentos tiveram como objetivo avaliar diferentes estratégias para segmentação, detecção e contagem automática de colônias em placas de Petri, considerando os desafios de variação de iluminação, presença de anotações manuscritas, colônias sobrepostas e mudança de domínio entre os datasets AGAR e CNPEM.

### Experimento 1 — Segmentação por limiarização

**Objetivo:** avaliar se métodos simples de binarização seriam suficientes para separar as colônias do fundo da placa.

**Método:** foram testadas três abordagens de limiarização: limiar fixo, limiarização de Otsu e limiarização adaptativa gaussiana. Antes da segmentação, as imagens foram recortadas usando a região de interesse da placa de Petri, realçadas com CLAHE e avaliadas em diferentes canais de cor.

**Resultado preliminar:** a limiarização de Otsu apresentou baixa robustez, pois o histograma das imagens recortadas era fortemente influenciado pelos pixels zerados fora da placa. A limiarização adaptativa apresentou melhores resultados em algumas imagens, mas não foi estável para todo o conjunto.

**Problemas encontrados:** os métodos baseados apenas em limiar não generalizaram bem para imagens com variação de iluminação, contraste reduzido entre colônias e ágar, ou presença de escritas na placa.

---

### Experimento 2 — Subtração de fundo com filtro Gaussiano

**Objetivo:** reduzir o efeito de iluminação irregular dentro da placa e realçar colônias com baixo contraste.

**Método:** foi aplicada uma filtragem Gaussiana com kernel grande, como `151 x 151`, para estimar o fundo da imagem. Em seguida, calculou-se a diferença absoluta entre a imagem suavizada e o fundo estimado. O resultado foi normalizado para o intervalo `[0, 255]` e binarizado com Otsu.

**Resultado preliminar:** o método funcionou bem em algumas imagens, principalmente quando a iluminação apresentava variação suave e as colônias tinham contraste razoável em relação ao fundo.

**Problemas encontrados:** ao trocar o conjunto de imagens, surgiram erros de contagem. O desempenho foi pior em imagens com colônias maiores, microrganismos com morfologia diferente e placas com anotações manuscritas, que foram confundidas com colônias.

---

### Experimento 3 — Segmentação por operações morfológicas

**Objetivo:** realçar estruturas pequenas e aproximadamente circulares correspondentes às colônias.

**Método:** foram testadas transformações morfológicas, como Top-Hat e Black-Hat, combinadas com binarização e operações de abertura/fechamento para remoção de ruído e preenchimento de pequenos buracos.

**Resultado preliminar:** as operações morfológicas conseguiram destacar colônias em imagens com fundo relativamente uniforme. A filtragem posterior por área e circularidade ajudou a remover pequenos artefatos.

**Problemas encontrados:** os parâmetros, como tamanho do kernel e limiar, precisaram ser ajustados manualmente. Isso dificultou a generalização para imagens com diferentes resoluções, iluminação e tamanhos de colônia.

---

### Experimento 4 — Clusterização K-Means

**Objetivo:** testar uma alternativa à limiarização, agrupando pixels por similaridade de cor e intensidade.

**Método:** foi aplicado K-Means com `k = 4` sobre os pixels internos da placa, usando principalmente os canais `L` e `b` do espaço de cor Lab após CLAHE.

**Resultado preliminar:** o K-Means apresentou resultados mais consistentes do que a limiarização em algumas imagens, especialmente porque não depende diretamente de um único valor de limiar global.

**Problemas encontrados:** o método ainda falhou quando a tonalidade das colônias era muito próxima à tonalidade do ágar. A seleção automática do cluster correspondente às colônias também permaneceu sensível às características visuais de cada imagem.

---

### Experimento 5 — Separação de colônias sobrepostas com Watershed

**Objetivo:** separar colônias conectadas ou parcialmente sobrepostas, evitando subcontagem.

**Método:** após a obtenção da máscara binária, foi aplicada a transformada de distância para localizar possíveis centros das colônias. Esses pontos foram usados como marcadores para o algoritmo Watershed.

**Resultado preliminar:** o método funcionou satisfatoriamente em casos de sobreposição parcial, quando ainda havia separação visual entre os centros das colônias.

**Problemas encontrados:** o Watershed não conseguiu separar corretamente colônias completamente fundidas ou com contornos muito pouco definidos. Nesses casos, múltiplas colônias continuaram sendo detectadas como um único objeto.

---

### Experimento 6 — Contagem por componentes conectados e filtros geométricos

**Objetivo:** transformar a máscara segmentada em uma contagem automática de colônias.

**Método:** cada região branca contígua foi rotulada como um componente conectado. Em seguida, foram aplicados filtros por área, circularidade e solidez para remover ruídos, fragmentos e partes de letras manuscritas.

**Resultado preliminar:** a combinação dos filtros reduziu falsos positivos e melhorou a contagem em imagens onde as colônias eram aproximadamente circulares e bem separadas.

**Problemas encontrados:** a contagem continuou sensível à qualidade da segmentação inicial. Colônias grandes, colônias fundidas e anotações manuscritas ainda causaram erros relevantes.

---

### Experimento 7 — Detecção com YOLOv5s no dataset AGAR

**Objetivo:** avaliar uma abordagem baseada em deep learning para detecção automática de colônias.

**Método:** foi realizado fine-tuning de um modelo YOLOv5s pré-treinado, utilizando imagens do dataset AGAR. Após a remoção de imagens consideradas incontáveis, foram usadas 13.489 imagens. O treinamento foi feito por 100 épocas, com `batch size = 32` e imagens redimensionadas para `640 x 640`.

**Resultado preliminar:**

| Métrica | Valor |
|---|---:|
| Precisão | 98% |
| Recall | 95% |
| mAP@0.5 | 96% |
| mAP@0.5:0.95 | 94% |

**Problemas encontrados:** apesar do bom desempenho no AGAR, o modelo apresentou queda de desempenho ao ser aplicado diretamente nas imagens do CNPEM, indicando diferença de domínio entre as bases.

---

### Experimento 8 — Adaptação de domínio com YOLOv8s-seg no CNPEM

**Objetivo:** adaptar o modelo para segmentação de instâncias nas imagens reais do CNPEM.

**Método:** o modelo treinado anteriormente foi usado como ponto de partida para um modelo YOLOv8s-seg. Foi realizado fine-tuning com imagens do CNPEM anotadas manualmente com máscaras de segmentação.

**Resultado preliminar:** mesmo com poucas imagens anotadas, o modelo apresentou segmentações visualmente razoáveis para algumas colônias do CNPEM.

**Problemas encontrados:** as máscaras ainda apresentaram contornos imprecisos, principalmente em colônias maiores, regiões de sobreposição e imagens com baixo contraste. A principal limitação foi a pequena quantidade de imagens anotadas.

---

### Experimento 9 — Enriquecimento de anotações com SAM 2.1

**Objetivo:** aumentar a quantidade e a qualidade das máscaras de segmentação disponíveis para treinamento.

**Método:** foi proposta a utilização do SAM 2.1 para gerar máscaras automaticamente a partir das bounding boxes existentes no dataset AGAR.

**Resultado preliminar:** os testes iniciais indicaram que o SAM consegue gerar máscaras úteis a partir das bounding boxes, permitindo transformar anotações de detecção em anotações de segmentação.

**Problemas encontrados:** ainda é necessário validar a qualidade das máscaras geradas automaticamente e verificar se elas melhoram de fato o treinamento dos modelos de segmentação.
## Próximos passos
- Finalizar a organização da metodologia dos métodos clássicos.
- Adicionar imagens comparativas dos resultados de cada método.
- Calcular e reportar MAE e sMAE para os métodos clássicos.
- Incluir matriz de confusão, curvas de loss e exemplos de inferência dos modelos YOLO.
- Expandir o conjunto anotado do CNPEM para melhorar a adaptação de domínio.
- Usar SAM 2.1 para enriquecer anotações do AGAR e treinar modelos de segmentação.
- Comparar custo computacional, robustez e qualidade de contagem entre métodos clássicos e deep learning.
- Revisar a seção de referências e padronizar todos os links e DOIs.

## Uso de IA Generativa
Ferramentas de IA generativa foram utilizadas como apoio à escrita, revisão textual e organização do README. As decisões metodológicas, experimentos, resultados e análise crítica foram definidos pelo grupo a partir dos dados e códigos desenvolvidos no projeto.

| Tarefa | Ferramenta | Uso |
|---|---|---|
| Revisão e reestruturação do README | ChatGPT | Organização textual, correção gramatical e padronização do Markdown |
| Apoio na redação metodológica | ChatGPT | Reformulação de trechos a partir das anotações do grupo |

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




