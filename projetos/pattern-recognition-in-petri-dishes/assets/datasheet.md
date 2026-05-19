# Datasheet para Dataset de Imagens de Colônias de Microrganismos

---

## 1. Motivação

**Para qual propósito o dataset foi criado?**
O dataset foi criado para viabilizar o desenvolvimento e avaliação de modelos de aprendizado de máquina voltados à **contagem automática de colônias de microrganismos** em placas de Petri. O problema motivador é a automação de um processo atualmente realizado de forma manual em laboratórios, sujeito a variabilidade humana e baixa escalabilidade.

**Quem criou o dataset?**
O dataset é composto por duas fontes:
- **Subconjunto CNPEM**: imagens coletadas no Centro Nacional de Pesquisa em Energia e Materiais (CNPEM), Campinas, SP.
- **Subconjunto externo**: imagens provenientes de dataset publicado por empresa em artigo científico (MAJCHROWSKA, Sylwia et al. *AGAR: a microbial colony dataset for deep learning detection*. arXiv preprint, arXiv:2108.01234, 2021. Disponível em: <https://arxiv.org/abs/2108.01234>).

**Quem financiou a criação?**
- O subconjunto do CNPEM foi coletado no âmbito das atividades da instituição.
- O subconjunto externo foi produzido e financiado pela empresa responsável pelo artigo de origem (MAJCHROWSKA et al., 2021).

---

## 2. Composição

**O que as instâncias representam?**
Cada instância é uma imagem fotográfica de uma placa de Petri contendo colônias de microrganismos. As imagens variam em condições de iluminação (diferentes intensidades e ângulos) e apresentam colônias de diferentes tamanhos e densidades.

**Quantas instâncias existem?**

| Fonte       | Quantidade de imagens |
|-------------|----------------------|
| CNPEM       | ~100                 |
| Artigo      | ~18.000              |
| **Total**   | **~18.100**          |

**O dataset contém todas as instâncias possíveis ou é uma amostra?**
Ambos os subconjuntos são amostras. O subconjunto do CNPEM representa uma amostra das placas processadas na instituição. O subconjunto externo representa a coleção publicada pela empresa, podendo não abranger todas as condições experimentais possíveis.

**De que consistem os dados de cada instância?**
Cada instância consiste em uma imagem no formato digital (HEIC e JPG) de uma placa de Petri fotografada. As imagens variam em:
- Condições de iluminação (clara e escura)
- Resolução: alta (4000 x 6000 px), média(3840 x 2160 px) e baixa(2048 x 2048 px)
- Tamanho das colônias
- Densidade de colônias por placa

**Há rótulos ou alvos associados a cada instância?**
As imagens do conjunto AGAR (artigo) possuem rótulos de posição na imagem e quantidade total, enquanto que as imagens do CNPEM possuem apenas a quantidade por placa, mas sem definir onde esses dados estão.

**Há informações ausentes em alguma instância?**
Não, ambos os dataset incluem tanto os dados de condições experimentais bem definidos quanto as condições de fotografia.

**Existem relações entre instâncias?**
Não há relações explícitas entre instâncias. Imagens do CNPEM e do subconjunto externo são tratadas de forma independente.

**Há divisões recomendadas (treino/validação/teste)?**
Recomenda-se manter o subconjunto do CNPEM separado como conjunto de **teste** ou **validação**, dado seu menor volume e origem distinta, para avaliar a capacidade de generalização dos modelos. O subconjunto AGAR pode ser utilizado para treino. Dessa forma, no presente trabalho, será usado o conjunto AGAR para treino, o do CNPEM será dividido em treino, validação e teste (70:20:10) para realizar o fine-tunning.

**Há erros, ruídos ou redundâncias?**
Possíveis fontes de ruído incluem variações de iluminação não controladas, possível sobreposição e união de colônias em placas de alta densidade. As fotos também possuem um background diferente, não sendo apenas a foto da placa em um fundo branco ou preto. Redundâncias não foram verificadas formalmente.

**O dataset é autossuficiente?**
O subconjunto do CNPEM está armazenado localmente. O subconjunto AGAR depende da liberação dos autores do artigo original.

**O dataset contém dados confidenciais?**
Não. As imagens são de placas de laboratório sem qualquer informação pessoal ou sigilosa.

**O dataset contém conteúdo potencialmente ofensivo?**
Não.

## 3. Processo de Coleta

**Como os dados foram adquiridos?**
- **CNPEM**: imagens capturadas diretamente por equipamento fotográfico em ambiente de laboratório, com condições de iluminação controladas.
- **Subconjunto externo**: imagens obtidas a partir de dataset publicado em artigo científico.

**Quais mecanismos foram usados para coletar os dados?**
- **CNPEM**: celular iPhone 16 posicionado verticalmente a 20 cm da placa e placa LED de 16.000 lx sob a placa de petri
- **Subconjunto externo**: foram usadas três câmeras diferentes (Nikon D3500 com lente de 60 mm; 24 Mpx CCD e IDS UI-5370CP-M-GL com 4.19 Mpx) dependendo do conjunto de fotos (alta ou baixa resolução) com um suporte com luz para a placa.

**Quem esteve envolvido na coleta?**
- **CNPEM**: estagiária do CNPEM.
- **Subconjunto externo**: pesquisadores do artigo.

**Qual foi o período de coleta?**
- **CNPEM**: Março de 2026.
- **Subconjunto externo**: 2020-2021.

**Foram conduzidos processos de revisão ética?**
Não aplicável pois as imagens não envolvem seres humanos nem dados sensíveis.

---

## 4. Pré-processamento / Limpeza / Rotulagem

**Foi realizado algum pré-processamento?**

- Redimensionamento:

- Aumento de dados (*data augmentation*): 

- Anotação de dados: Os dados do CNPEM que não possuiam anotação, foram anotados utilizando o software CVAT (Computer Vision Annotation [https://www.cvat.ai/]) que possui o SAM 2.0 (Segment Anything. [https://arxiv.org/abs/2304.02643]). 

**Os dados brutos foram preservados?**
Sim, estão na subpasta `data/raw/` para garantir reprodutibilidade. Além disso, cada notebook tem seu próprio conjunto intermediário `data/interm`

**O software de pré-processamento está disponível?**
Sim, o CVAT é um software aberto com limitações para a versão gratuita, e as demais modificações foram feitas usando bibliotecas Python.

---

## 5. Usos

**O dataset já foi utilizado para alguma tarefa?**
- O subconjunto externo foi utilizado na pesquisa original para tarefas de detecção de colônias.
- O subconjunto do CNPEM é inédito neste contexto.

**Para quais outras tarefas o dataset poderia ser utilizado?**
- Segmentação de colônias
- Classificação por tipo ou morfologia de colônia
- Estimativa de densidade microbiana
- Benchmarking de algoritmos de visão computacional em contexto biológico

**Há algo na composição ou coleta que possa impactar usos futuros?**
A heterogeneidade entre os dois subconjuntos (diferenças de equipamento, iluminação e protocolo) pode introduzir viés de domínio (*domain shift*). Modelos treinados apenas no subconjunto externo podem não generalizar bem para as condições do CNPEM.

**Para quais tarefas o dataset NÃO deve ser usado?**
Diagnóstico clínico direto sem validação adicional por especialistas e qualquer aplicação que assuma homogeneidade entre os dois subconjuntos sem tratamento do domain shift

---

## 6. Distribuição

**O dataset será distribuído externamente?**
- O subconjunto do CNPEM está sujeito às políticas de dados da instituição, sendo necessário verificar permissões antes de qualquer distribuição pública.
- O subconjunto externo segue os termos de licença do artigo original.

**Como será distribuído?**
Via repositório GitHub.

**O dataset será distribuído sob alguma licença?**
- **CNPEM**: a definir conforme política institucional.
- **Subconjunto externo**: respeitar a licença original da publicação.

**Há restrições de exportação ou regulatórias?**
Não identificadas.

---

## 7. Manutenção

**Quem será responsável pela manutenção?**
Os integrantes do grupo.

**Como os responsáveis podem ser contatados?**
A ser preenchido com e-mail ou repositório do projeto.

**O dataset será atualizado?**
Possível expansão do subconjunto do CNPEM com novas coletas, sendo as atualizações comunicadas via repositório do projeto.

**Versões antigas serão mantidas?**
Sim, serão mantidas para garantir reprodutibilidade de experimentos já realizados.

**Há mecanismo para contribuições externas?**
A definir. Contribuições podem ser feitas via pull request no repositório do projeto, sujeitas à validação pela equipe responsável.

---

*Datasheet elaborado com base em: Gebru, T. et al. (2021). Datasheets for Datasets. Communications of the ACM.*
