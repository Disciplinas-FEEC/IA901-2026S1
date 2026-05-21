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
> | Laura Vieira Malachias   | 299117  | Mestranda em Tecnologia|
> | Gabriela Morales Soto  | 299213  | Mestranda em Ciência da Computação|



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

## 3. Métodos clássicos de segmentação

### 3.1 Limiarização

Foram avaliadas diferentes estratégias de limiarização para segmentação das colônias bacterianas. A primeira abordagem utilizou um limiar fixo aplicado diretamente ao canal B da imagem. A operação de binarização é descrita por:

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

Também foi utilizada a subtração de fundo utilizando filtros gaussianos de grandes dimensões, com kernels de \(151 x 151\) e \(71 x 71\) pixels. Inicialmente, o fundo estimado foi obtido pela convolução da imagem com um kernel gaussiano:

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

E posteriormente, aplicou-se o método de Otsu para obtenção da máscara binária segmentada.

### 3.4 Clusterização K-Means

Também foi feita uma clusterização K-Means utilizando quatro grupos distintos. Nesse caso, os canais \(L\) e \(b\) do espaço Lab foram utilizados após aplicação de CLAHE. Após a convergência do algoritmo, o agrupamento correspondente às colônias foi selecionado com base nos valores de luminosidade dos centróides obtidos.

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
N_{\text{colônias}} = \# \{ k \geq 1 : A_k \geq A_{\min} \}
$$

onde $A_k$ representa a área do componente conectado.

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

### 6.1 Aumento de dados

Com o objetivo de aumentar a variabilidade do conjunto de treinamento e reduzir efeitos de sobreajuste, foram aplicadas técnicas de aumento de dados sobre o dataset AGAR. Entre as transformações empregadas destacam-se rotações, espelhamento horizontal, alterações de brilho e contraste, modificações de cor e aplicação de desfoque gaussiano.

### 6.2 Detecção com YOLOv5s

Inicialmente foi empregado o modelo YOLOv5s pré-treinado no ImageNet. O modelo foi submetido a *fine-tuning* utilizando o dataset AGAR previamente processado.

O treinamento foi realizado durante 100 épocas, utilizando *batch size* igual a 32 e imagens redimensionadas para \(640 x 640\) pixels.

### 6.3 Adaptação de domínio com segmentação

Posteriormente, o backbone treinado na etapa anterior foi utilizado como ponto de partida para um modelo de segmentação de instâncias baseado em YOLOv5s-seg.

Isso permitiu realizar adaptação de domínio utilizando as imagens anotadas manualmente no CNPEM, adequando o modelo às condições reais de aquisição presentes no novo conjunto de dados.

### 6.4 Enriquecimento de anotações com SAM 2.1

O modelo SAM 2.1 (*Segment Anything Model*) foi utilizado para geração automática de máscaras de segmentação a partir das *bounding boxes* disponíveis no dataset AGAR.

As máscaras geradas foram posteriormente utilizadas para enriquecimento das anotações destinadas ao treinamento dos modelos de segmentação.

## 7. Avaliação experimental

A avaliação foi feita utilizando os valores de referência disponíveis nos datasets empregados. Já os modelos de aprendizado profundo foram avaliados a partir das métricas de precisão, *recall*, mAP@0.5 e mAP@0.5:0.95 utilizando o conjunto de validação do dataset AGAR.


## Bases de Dados e Evolução


O datasheet for datasets pode ser consultado aqui: [Datasheet](IA901-2026S1/projetos/pattern-recognition-in-petri-dishes/assets/datasheet.md)

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
- **Ultralytics (YOLOv5 / YOLOv5-seg)** — treinamento, fine-tuning e inferência dos modelos de detecção e segmentação de instâncias
- **SAM 2.1 (Segment Anything Model — Meta AI)** — geração automática de máscaras de segmentação a partir de bounding boxes para enriquecimento das anotações
- **CVAT** — ferramenta utilizada para anotação manual das imagens do dataset CNPEM

## Workflow

O workflow do projeto foi organizado para representar as principais etapas necessárias para reproduzir os experimentos, desde a preparação das bases de dados até a avaliação dos métodos clássicos e baseados em aprendizado profundo.

![Workflow do projeto](assets/Workflow%20IA901%20%E2%80%94%20Pipeline%20Contagem%20de%20Col%C3%B4nias.jpg)

## Experimentos e Resultados preliminares

Nesta etapa do projeto, os experimentos foram organizados em três grupos principais: experimentos de pré-processamento, experimentos de segmentação e contagem com métodos clássicos, e experimentos com modelos baseados em aprendizado profundo. Essa organização permite acompanhar a evolução do pipeline desde a preparação das imagens até a avaliação preliminar das abordagens de detecção e segmentação.

---

### 1. Experimentos de pré-processamento

#### 1.1 Conversão, padronização e organização das imagens

As imagens do dataset CNPEM foram inicialmente convertidas para o formato PNG, uma vez que os arquivos originais estavam majoritariamente em formato HEIC. Para isso, foi utilizada a biblioteca `pillow-heif`, enquanto imagens em JPEG foram lidas diretamente com `Pillow`. Após a conversão, os arquivos foram renomeados sequencialmente, seguindo o padrão `1.png`, `2.png`, etc. Essa etapa foi necessária para padronizar o acesso às imagens durante os experimentos e evitar problemas de leitura em diferentes bibliotecas de processamento de imagens.


#### 1.2 Definição da região de interesse com Transformada de Hough

Após a padronização dos arquivos, foi realizada a definição automática da região de interesse. Como as imagens contêm não apenas a placa de Petri, mas também partes do ambiente de aquisição, aplicou-se a Transformada de Hough para círculos sobre a imagem em escala de cinza suavizada. A partir do círculo detectado, foi criada uma máscara binária circular, mantendo apenas os pixels internos à placa e zerando a região externa. Em alguns testes, também foi removido um anel externo da placa, pois essa região frequentemente contém bordas, reflexos e anotações manuais que interferem na segmentação das colônias.

![Detecção da placa por Hough Circles](assets/experimentos/02_hough_roi.png)

#### 1.3 Análise de canais de cor e histogramas

Com a região da placa isolada, foram analisados histogramas dos canais RGB e diferentes espaços de cor, como HSV, CMYK e CIE Lab. Essa análise foi importante para observar como as intensidades estavam distribuídas dentro da placa e para identificar quais canais ofereciam melhor separação entre colônias e fundo. O uso de CLAHE também foi testado para realçar o contraste local, tornando mais visíveis algumas colônias que apresentavam baixa diferença de intensidade em relação ao ágar. Nos testes realizados, os canais `L` e `b` do espaço Lab apresentaram boa separação em algumas imagens, mas nenhum canal foi suficientemente robusto para todos os casos.

![Comparação de canais de cor e histogramas](assets/experimentos/03.png)
![Comparação de canais de cor e histogramas](assets/experimentos/04.png)
![Comparação de canais de cor e histogramas](assets/experimentos/05.png)
![Comparação de canais de cor e histogramas](assets/experimentos/06.png)

#### Síntese dos problemas observados no pré-processamento

| Etapa | Problema observado | O que ocasionou o problema | Por que não serviu bem para todas as imagens |
|---|---|---|---|
| Conversão e padronização | As imagens continuaram apresentando diferenças visuais relevantes | As bases possuem formatos, resoluções e condições de captura diferentes | A padronização do arquivo resolve a leitura, mas não corrige iluminação, escala ou enquadramento |
| Hough Circles | Em algumas imagens o círculo detectado não coincidiu perfeitamente com a placa | Variações de distância da câmera, ângulo, borda pouco definida e iluminação irregular | Um erro na ROI afeta todas as etapas seguintes, pois pode cortar colônias ou manter regiões externas indesejadas |
| Máscara circular | Presença de bordas, escritas e reflexos mesmo após o recorte | Algumas anotações estão dentro ou próximas à área útil da placa | A máscara circular remove o exterior da placa, mas não separa automaticamente colônias de artefatos internos |
| Seleção de canais | Nenhum canal funcionou de forma universal | Diferenças de cor entre ágar, colônias e microrganismos | Um canal que destaca bem uma imagem pode falhar em outra com contraste ou coloração diferente |

---

### 2. Experimentos de segmentação e contagem com métodos clássicos

#### 2.1 Limiarização global, Otsu e limiarização adaptativa

Foram testadas diferentes estratégias de limiarização para separar as colônias do fundo da placa, incluindo limiar fixo, limiarização de Otsu e limiarização adaptativa gaussiana. Esses métodos foram aplicados após a definição da região de interesse e o realce de contraste. A limiarização de Otsu apresentou limitações importantes, pois o histograma das imagens recortadas era fortemente influenciado pelos pixels zerados fora da placa. Como consequência, o limiar calculado automaticamente foi deslocado para valores pouco adequados, reduzindo a sensibilidade para detectar colônias. A limiarização adaptativa apresentou resultados melhores em algumas imagens, mas ainda foi instável diante de variações de iluminação e contraste.

![Resultados da limiarização](assets/experimentos/07.png)
![Resultados da limiarização](assets/experimentos/08.png)


#### 2.2 Subtração de fundo com filtro Gaussiano

Também foi avaliada uma abordagem baseada em subtração de fundo. Nesse experimento, um filtro Gaussiano com kernel de grande dimensão foi utilizado para estimar a variação lenta de iluminação dentro da placa. Em seguida, calculou-se a diferença absoluta entre a imagem suavizada e o fundo estimado, realçando regiões que se destacavam localmente. O resultado foi normalizado e posteriormente binarizado com Otsu. Essa estratégia funcionou melhor em imagens nas quais o fundo apresentava uma variação suave de iluminação, mas perdeu desempenho quando havia colônias maiores, anotações manuscritas ou mudanças mais intensas na aparência do ágar.

![Subtração de fundo](assets/experimentos/09.png)


#### 2.3 Clusterização K-Means

Como alternativa aos métodos baseados em limiar, foi aplicado K-Means com `k = 4` sobre os pixels internos da placa, utilizando principalmente os canais `L` e `b` do espaço Lab após CLAHE. Essa abordagem agrupou os pixels por similaridade de cor e luminosidade, reduzindo a dependência de um único limiar global. Em algumas amostras, o K-Means apresentou resultados mais consistentes que a limiarização, especialmente em casos com variação moderada de iluminação. Entretanto, o método continuou apresentando dificuldades quando a tonalidade das colônias era muito próxima à do ágar, pois o cluster correspondente às colônias deixava de ser claramente separável.

![Segmentação com K-Means](assets/experimentos/13.png)

#### 2.5 Separação de colônias sobrepostas com Watershed

Após a obtenção das máscaras binárias, foi aplicado o algoritmo Watershed associado à transformada de distância para separar colônias conectadas ou parcialmente sobrepostas. A transformada de distância permitiu localizar possíveis centros das colônias, que foram usados como marcadores para a propagação das regiões. O método funcionou de forma satisfatória em casos de sobreposição parcial, nos quais ainda havia centros distinguíveis. No entanto, quando as colônias estavam completamente fundidas ou apresentavam contornos pouco definidos, o algoritmo não foi capaz de separar corretamente as instâncias, resultando em subcontagem. Essa limitação também foi observada nas anotações do grupo, especialmente para casos de colônias muito próximas ou confluentes.

![Separação com Watershed](assets/experimentos/11.png)

#### 2.6 Contagem por componentes conectados e filtros geométricos

A etapa de contagem foi realizada a partir da rotulagem de componentes conectados presentes nas máscaras binárias. Cada região branca contígua foi interpretada como uma candidata a colônia. Para reduzir falsos positivos, foram aplicados filtros por área, circularidade e solidez. A circularidade foi usada porque muitas colônias apresentam formato aproximadamente circular, enquanto fragmentos de letras e ruídos tendem a produzir formas alongadas ou irregulares. A solidez ajudou a descartar componentes com contornos muito fragmentados. Essa combinação reduziu falsos positivos, mas a contagem continuou dependente da qualidade da segmentação inicial. Quando a máscara continha colônias unidas, partes de escrita ou regiões mal segmentadas, os filtros geométricos não eram suficientes para corrigir o erro.

![Contagem por componentes conectados](assets/experimentos/12.png)

#### Síntese dos problemas observados nos métodos clássicos

| Experimento | Resultado preliminar | Problema observado | O que ocasionou o problema | Por que não serviu bem para essas imagens |
|---|---|---|---|---|
| Limiar fixo | Funcionou apenas em imagens visualmente semelhantes às usadas para calibração | Baixa generalização | Diferenças de iluminação, contraste e cor do ágar | Um único valor de limiar não representa bem todo o conjunto |
| Otsu | Automatizou a escolha do limiar, mas falhou em várias imagens | Limiar deslocado | Histograma dominado por pixels zerados da máscara e fundo | A separação estatística entre fundo e colônia não ficou bem definida |
| Limiarização adaptativa | Melhorou alguns casos locais | Resultado inconsistente | Sensibilidade ao tamanho da vizinhança e à iluminação | Detectou ruídos e falhou em regiões com baixo contraste |
| Subtração de fundo | Realçou colônias em placas com iluminação suave | Erros em colônias grandes e anotações | Escritas, variações fortes de fundo e morfologias diferentes | O método assume que o fundo varia lentamente e que as colônias são pequenas |
| K-Means | Foi mais estável que limiarização em algumas amostras | Confusão entre colônia e ágar | Tonalidades semelhantes entre classes | Quando as cores se sobrepõem, os clusters deixam de representar objetos reais |
| Watershed | Separou sobreposições parciais | Não separou colônias fundidas | Ausência de máximos locais bem definidos | Colônias completamente conectadas aparecem como uma única região |
| Componentes conectados + filtros | Reduziu falsos positivos simples | Não corrigiu erros da segmentação | Máscaras com regiões fundidas, letras ou ruídos | A filtragem geométrica atua depois da segmentação e não recupera objetos perdidos |

---

### 3. Experimentos com aprendizado profundo

#### 3.1 Detecção de colônias com YOLOv5s no dataset AGAR

Para avaliar uma abordagem baseada em aprendizado profundo, foi realizado o fine-tuning de um modelo YOLOv5s pré-treinado. O treinamento utilizou o dataset AGAR após a remoção das imagens consideradas incontáveis, resultando em 13.489 imagens. Os dados foram divididos em 70% para treino e 30% para validação, com treinamento por 100 épocas, `batch size = 32` e imagens redimensionadas para `640 x 640`. No conjunto de validação do AGAR, o modelo apresentou bons resultados, com precisão de 98%, recall de 95%, mAP@0.5 de 96% e mAP@0.5:0.95 de 94%. Esses valores indicam que o modelo aprendeu bem o padrão visual do AGAR, mas a inferência direta em imagens do CNPEM apresentou queda de desempenho, evidenciando a diferença de domínio entre as bases. 

| Métrica | Valor |
|---|---:|
| Precisão | 98% |
| Recall | 95% |
| mAP@0.5 | 96% |
| mAP@0.5:0.95 | 94% |

#### 3.2 Adaptação de domínio com YOLOv5s-seg no dataset CNPEM

Em seguida, foi testada uma estratégia de adaptação de domínio utilizando imagens do CNPEM anotadas manualmente com máscaras de segmentação. O modelo treinado anteriormente no AGAR foi utilizado como ponto de partida para um modelo de segmentação baseado em YOLOv5s-seg. Mesmo com poucas imagens anotadas, os resultados preliminares mostraram segmentações visualmente razoáveis em algumas imagens do CNPEM. No entanto, as máscaras ainda apresentaram imprecisões nos contornos, principalmente em colônias maiores, regiões de sobreposição e imagens com baixo contraste. Isso indica que a adaptação de domínio é viável, mas depende da ampliação e melhoria das anotações de segmentação.

![Segmentação com YOLOv5s-seg](assets/experimentos/cnpem-saida-yolo.png)

#### 3.3 Enriquecimento de anotações com SAM 2.1

Como proposta para melhorar o treinamento dos modelos de segmentação, foi iniciado o uso do SAM 2.1 para gerar máscaras automaticamente a partir das bounding boxes disponíveis no dataset AGAR. Como o AGAR já possui anotações de detecção, o SAM permite transformar parte dessas anotações em máscaras, enriquecendo o conjunto de dados para segmentação de instâncias. Essa etapa ainda precisa ser validada visual e quantitativamente, pois máscaras automáticas incorretas podem introduzir ruído no treinamento. Mesmo assim, a abordagem é promissora para aumentar a quantidade de dados segmentados sem depender exclusivamente de anotação manual.

![exemplo 1 de imagem segmentada pelo SAM Automaticamente](data/interim/DeepLearning/6794.png)

![exemplo 2 de imagem segmentada pelo SAM Automaticamente](data/interim/DeepLearning/6225.png)

#### Síntese dos problemas observados nos métodos de aprendizado profundo

| Experimento | Resultado preliminar | Problema observado | O que ocasionou o problema | Por que ainda não resolve completamente |
|---|---|---|---|---|
| YOLOv5s no AGAR | Alto desempenho no conjunto de validação do AGAR | Queda ao aplicar no CNPEM | Diferença de domínio entre datasets | O modelo aprendeu bem o AGAR, mas não generalizou diretamente para outro protocolo de aquisição |
| YOLOv5s-seg no CNPEM | Segmentações razoáveis com poucas imagens | Contornos imprecisos | Pouca quantidade de máscaras anotadas | O modelo precisa de mais exemplos para aprender variações de forma, tamanho e sobreposição |
| SAM 2.1 para máscaras | Geração automática de máscaras a partir de bounding boxes | Necessidade de validação das máscaras | Segmentação automática pode gerar erros | Máscaras incorretas podem prejudicar o treinamento supervisionado |
| Adaptação de domínio | Estratégia mostrou potencial | Dependência de anotação manual | O CNPEM possui poucas anotações espaciais | A qualidade final depende da ampliação do conjunto anotado |
## Próximos passos

Para a conclusão do projeto, as próximas etapas foram organizadas considerando as pendências técnicas, experimentais e de documentação. O foco principal será consolidar os resultados dos métodos clássicos, ampliar a adaptação de domínio para o dataset CNPEM e organizar a análise comparativa final entre as abordagens testadas.

| Etapa | Descrição | Entrega esperada |
|---|---|---|
| Revisão das anotações do CNPEM | Revisar as máscaras já anotadas manualmente, corrigindo contornos inconsistentes e removendo anotações ambíguas. Essa etapa é necessária porque a qualidade das máscaras influencia diretamente o treinamento do modelo de segmentação. | Conjunto revisado de máscaras do CNPEM |
| Ampliação do conjunto anotado | Aumentar a quantidade de imagens do CNPEM com máscaras de segmentação, priorizando imagens com colônias maiores, sobrepostas e com diferentes meios de cultura. | Novo subconjunto anotado para fine-tuning |
| Geração de máscaras com SAM 2.1 | Utilizar o SAM 2.1 para gerar máscaras a partir das bounding boxes do dataset AGAR, avaliando visualmente a qualidade das segmentações geradas automaticamente. | Máscaras geradas automaticamente para parte do AGAR |
| Validação das máscaras automáticas | Comparar qualitativamente as máscaras geradas pelo SAM 2.1 com exemplos anotados manualmente, identificando erros comuns como vazamento de contorno, segmentação parcial ou inclusão de fundo. | Conjunto filtrado de máscaras consideradas úteis |
| Novo treinamento com 5s-seg | Realizar novo fine-tuning do modelo de segmentação usando as máscaras revisadas do CNPEM e, se possível, as máscaras enriquecidas do AGAR. Modelo de segmentação atualizado |
| Consolidação dos métodos clássicos | Selecionar os melhores resultados obtidos com limiarização, subtração de fundo, morfologia, K-Means, Watershed e filtros geométricos. | Tabela comparativa dos métodos clássicos |
| Avaliação quantitativa final | Calcular métricas de contagem, detecção e segmentação, como MAE, sMAE, precisão, recall, mAP e IoU, conforme a disponibilidade de ground truth em cada base. | Resultados quantitativos finais |
| Análise crítica dos resultados | Comparar os métodos clássicos e os métodos baseados em deep learning, discutindo vantagens, limitações, capacidade de generalização e custo computacional. | Discussão crítica para o relatório final |
| Organização das figuras e workflow | Inserir no README as imagens dos experimentos, o workflow do projeto e exemplos visuais dos principais resultados obtidos. | README com figuras organizadas |
| Escrita e revisão final da entrega | Revisar o texto final, corrigir formatação em Markdown, conferir referências, datasheet, links e seção de uso de IA generativa. | Versão final da Entrega 2 |


## Uso de IA Generativa

Durante o desenvolvimento do projeto, ferramentas de IA generativa foram utilizadas como apoio em tarefas de escrita, revisão, tradução, organização do README, interpretação de erros de código e melhoria da documentação. As ferramentas não foram utilizadas para gerar resultados experimentais automaticamente nem para substituir a análise crítica do grupo. Os resultados, decisões metodológicas e interpretações finais foram revisados pelos integrantes do projeto.

| Tarefa | Ferramenta utilizada | Prompt utilizado | Uso no projeto |
|---|---|---|---|
| Revisão de texto em português | ChatGPT | "Corrija a gramática e melhore a clareza deste parágrafo mantendo o sentido original." | Revisão de trechos da descrição do projeto, metodologia e resultados preliminares |
| Tradução de trechos técnicos | ChatGPT | "Traduza este trecho do espanhol para o português acadêmico, mantendo os termos técnicos de processamento de imagens." | Tradução e adaptação de anotações internas do grupo para o README |
| Correção de código Python | ChatGPT | "Este código em Python está gerando erro. Explique o erro e sugira uma correção sem mudar a lógica principal." | Apoio na identificação de erros de sintaxe, leitura de imagens, manipulação de arrays e uso de bibliotecas |
| Criação de tabelas em Markdown | ChatGPT | "Transforme estas informações em uma tabela Markdown organizada." | Criação de tabelas comparativas de bases de dados, ferramentas, próximos passos e problemas observados |
| Geração de ideias para workflow | ChatGPT | "Sugira um workflow visual para um projeto de segmentação, detecção e contagem de colônias em placas de Petri." | Apoio na definição dos blocos principais do workflow do projeto |

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




