# Datasheet para Dataset de Imagens de Colônias de Microrganismos (CNPEM)

---

## 1. Motivação

**Para qual propósito o dataset foi criado?**
O dataset foi criado para viabilizar o desenvolvimento e avaliação de um pipeline de visão computacional voltado à **contagem automática de colônias de microrganismos** em placas de Petri. O problema motivador é a automação de um processo atualmente realizado de forma manual em laboratórios, sujeito a fadiga do analista, variabilidade entre contagens da mesma placa e baixa escalabilidade.

**Quem criou o dataset?**
O dataset é composto por imagens coletadas no **Centro Nacional de Pesquisa em Energia e Materiais (CNPEM)**, Campinas, SP.

**Quem financiou a criação?**
A coleta foi realizada no âmbito das atividades da instituição.

---

## 2. Composição

**O que as instâncias representam?**
Cada instância é uma fotografia de uma placa de Petri contendo colônias de microrganismos. As imagens variam em condições de iluminação e em densidade/tamanho de colônias.

**Quantas instâncias existem?**

| Fonte       | Quantidade de imagens |
|-------------|----------------------|
| CNPEM       | 94                 |

**O dataset contém todas as instâncias possíveis ou é uma amostra?**
É uma amostra. O dataset representa as placas processadas na instituição sob um protocolo específico de aquisição (mesmo equipamento e condição de iluminação). Não cobre outras condições de aquisição (outras câmeras, scanners de mesa), outros meios de cultura ou outras espécies de microrganismos.

**De que consistem os dados de cada instância?**
Cada instância consiste em uma imagem digital de uma placa de Petri contendo culturas microbianas, acompanhada de duas contagens de referência. Em detalhe:
- **Arquivos de imagem**: originalmente em formato HEIC, convertidos para JPG/PNG para padronizar a leitura nos notebooks do projeto.
- **Resolução**: variável, compatível com a captura por câmera de smartphone (ver Seção 3).
- **Complexidade biológica**: variação no tamanho das colônias (estágios de crescimento) e na densidade (de placas com poucas colônias até placas muito povoadas, com colônias próximas ou parcialmente sobrepostas).

**Há rótulos ou alvos associados a cada instância?**
Não há anotação espacial (bounding box ou máscara) nem rótulo de espécie de microrganismo. Cada imagem possui duas contagens numéricas de referência, usadas como alvo na avaliação do pipeline:
- `staff`: contagem original, feita pelo analista no momento do experimento, observando a placa diretamente.
- `cvat`: recontagem posterior, feita com apoio de anotação manual de instâncias na ferramenta CVAT (Computer Vision Annotation Tool).

A existência de duas contagens independentes para a mesma placa permite tratar a divergência entre elas como uma estimativa da própria margem de erro humano na tarefa, e não apenas comparar o algoritmo contra um único valor de referência.

**Há informações ausentes em alguma instância?**
Não há anotação espacial de colônia para nenhuma imagem, essa ausência é uma característica do dataset, não uma falha de coleta, já que o protocolo de referência é contagem numérica, não detecção por instância. 

**Existem relações entre instâncias?**
Não há relações explícitas entre instâncias. Cada imagem corresponde a uma placa de Petri tratada de forma independente.

**Há divisões recomendadas (treino/validação/teste)?**
Não aplicável da forma atual. O pipeline implementado é um método clássico de visão computacional (sem etapa de treinamento supervisionado), de modo que todas as imagens com `staff` e `cvat` disponíveis são usadas como conjunto de avaliação.

**Há erros, ruídos ou redundâncias?**
Possíveis fontes de ruído incluem variações de iluminação não totalmente controladas, sobreposição e coalescência de colônias em placas de alta densidade, reflexos na tampa da placa e bordas/anotações manuscritas próximas à borda do recipiente, que podem interferir na etapa de segmentação se não removidas pela máscara da região de interesse. Redundâncias não foram verificadas formalmente.

Há também ruído inerente à própria anotação humana: a divergência observada entre `staff` e `cvat` para a mesma placa (quantificada na Seção 3 do notebook de avaliação) evidencia que a contagem manual de colônias muito numerosas ou muito próximas está sujeita a inconsistência mesmo entre duas observações cuidadosas da mesma imagem — o que é tratado neste projeto como característica da tarefa, e não como erro de integridade dos dados.

**O dataset é autossuficiente?**
Sim, para a tarefa de contagem por método clássico de visão computacional. Requer apenas as etapas padrão de pré-processamento usadas no projeto (conversão de formato, leitura via OpenCV).

**O dataset contém dados confidenciais?**
Não. As imagens são de placas de laboratório sem qualquer informação pessoal ou sigilosa.

**O dataset contém conteúdo potencialmente ofensivo?**
Não.

---

## 3. Processo de Coleta

**Como os dados foram adquiridos?**
As imagens foram capturadas diretamente por equipamento fotográfico em ambiente de laboratório, sob condição de iluminação padronizada.

**Quais mecanismos foram usados para coletar os dados?**
Celular iPhone 16 posicionado verticalmente a 20 cm da placa, com placa de LED de 16.000 lx posicionada sob a placa de Petri.

**Quem esteve envolvido na coleta?**
Estagiária do CNPEM.

**Qual foi o período de coleta?**
Março de 2026.

**Foram conduzidos processos de revisão ética?**
Não aplicável, pois as imagens não envolvem seres humanos nem dados sensíveis.

---

## 4. Pré-processamento / Limpeza / Rotulagem

**Foi realizado algum pré-processamento?**

- **Conversão de formato**: as imagens, originalmente em HEIC, foram convertidas para PNG/JPG para padronizar a leitura entre as bibliotecas de processamento utilizadas (OpenCV, Pillow).
- **Redimensionamento**: cada imagem é redimensionada para largura fixa de 800 px (mantendo a proporção original) no início do pipeline de contagem, para padronizar escala entre placas fotografadas a distâncias levemente diferentes.
- **Conversão para escala de cinza via PCA**: como etapa de pré-processamento do pipeline de contagem (não do dataset em si), a imagem RGB é projetada em um único canal via a primeira componente principal dos canais de cor, em vez da conversão fixa RGB→cinza, de forma a preservar melhor o contraste entre colônia e ágar.
- **Anotação de referência**: a contagem `cvat` foi obtida anotando manualmente as instâncias de colônia no software CVAT (Computer Vision Annotation Tool — https://www.cvat.ai/), que conta com suporte ao modelo SAM (Segment Anything — https://arxiv.org/abs/2304.02643) para auxiliar na segmentação durante a anotação.

**Os dados brutos foram preservados?**
Sim, estão na subpasta `data/raw/` para garantir reprodutibilidade. Cada notebook do projeto também gera seu próprio conjunto intermediário em `data/interim/`.

**O software de pré-processamento está disponível?**
Sim. O CVAT é um software aberto, com limitações na versão gratuita; as demais etapas de pré-processamento foram implementadas em Python (OpenCV, NumPy, scikit-learn).

---

## 5. Usos

**O dataset já foi utilizado para alguma tarefa?**
Sim, é utilizado neste projeto para o desenvolvimento e avaliação de um pipeline clássico de detecção e contagem de colônias (Transformada de Hough para região de interesse, conversão PCA, realce morfológico Black-Hat, limiarização, Transformada de Distância e Watershed), comparando a contagem automática contra as duas referências humanas `staff` e `cvat`.

**Para quais outras tarefas o dataset poderia ser utilizado?**
- Segmentação de instâncias de colônias, caso anotações espaciais sejam produzidas no futuro;
- Estudo de concordância entre anotadores humanos em tarefas de contagem visual repetitiva;
- Benchmarking de outros algoritmos clássicos de visão computacional em placas de Petri reais (fora de condições de estúdio controladas);
- Treinamento ou fine-tuning de modelos de detecção, caso o dataset venha a ser anotado espacialmente.

**Há algo na composição ou coleta que possa impactar usos futuros?**
O dataset reflete um único protocolo de aquisição (mesma câmera, distância e iluminação), o que limita a generalização de qualquer método ajustado especificamente a essas condições para placas fotografadas em outros contextos (outro equipamento, outra distância, luz ambiente não controlada). Além disso, como não há anotação espacial por colônia, o dataset não é diretamente utilizável para treinar modelos supervisionados de detecção ou segmentação sem etapa adicional de anotação.

**Para quais tarefas o dataset NÃO deve ser usado?**
Diagnóstico clínico direto sem validação adicional por especialistas, e qualquer aplicação que assuma que a contagem de referência (`staff` ou `cvat`) é um valor exato e livre de erro, em vez de uma estimativa humana sujeita à própria variabilidade observada entre as duas.

---

## 6. Distribuição

**O dataset será distribuído externamente?**
Está sujeito às políticas de dados da instituição (CNPEM), sendo necessário verificar permissões antes de qualquer distribuição pública.

**Como será distribuído?**
Via repositório GitHub do projeto.

**O dataset será distribuído sob alguma licença?**
A definir, conforme política institucional do CNPEM.

**Há restrições de exportação ou regulatórias?**
Não identificadas.

---

## 7. Manutenção

**Quem será responsável pela manutenção?**
Os integrantes do grupo.

**Como os responsáveis podem ser contatados?**
A ser preenchido com e-mail ou repositório do projeto.

**O dataset será atualizado?**
Possível expansão com novas coletas e novas recontagens em CVAT, com atualizações comunicadas via repositório do projeto.

**Versões antigas serão mantidas?**
Sim, serão mantidas para garantir reprodutibilidade dos experimentos já realizados.

**Há mecanismo para contribuições externas?**
A definir. Contribuições podem ser feitas via pull request no repositório do projeto, sujeitas à validação pela equipe responsável.

---

*Datasheet elaborado com base em: Gebru, T. et al. (2021). Datasheets for Datasets. Communications of the ACM.*
