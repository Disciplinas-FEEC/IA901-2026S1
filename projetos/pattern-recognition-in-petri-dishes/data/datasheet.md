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
| AGAR dataset      | ~18.000              |
| **Total**   | **~18.100**          |

**O dataset contém todas as instâncias possíveis ou é uma amostra?**
Ambos os subconjuntos são amostras. O subconjunto do CNPEM representa uma amostra das placas processadas na instituição. O subconjunto AGAR representa a coleção publicada pela empresa, ambos datasets não contém todas as instancias possíveis de condições de colônicas em placas de petri possíveis, as instancias podem variar em outras condições de ilumininação, outra condição de aquisição da imagem ( diferentes câmeras fotográficas, scanners de mesa etc.) e outras espécies de microorganismos.

**De que consistem os dados de cada instância?**
Cada instância consiste em uma imagem digital de uma placa de Petri contendo culturas microbianas, acompanhada de seus respectivos metadados e anotações de localização. Os dados detalham-se em:
- Arquivos de Imagem: Formatos JPG e HEIC, capturados com diferentes dispositivos e configurações.
- Iluminação: Classificadas entre bright (clara), dark (escura) e vague (baixo contraste/indefinida).
- Resolução: As imagens do dataset apresentam resolução variável, com dimensões que variam de aproximadamente 4,2 MP (Megapixels) até 19 MP, Dimensões Mínimas: 2048×2048 px , Dimensões Máximas: 4740×4000 px, em média, uma largura de 3533 px e altura de 3997 px, resultando em aproximadamente 14,1 milhões de pixel. Existe uma variação (std) de cerca de 313 px na largura, indicando que a maioria das imagens orbita o padrão de alta resolução, mas há subgrupos distintos (como os de baixa resolução mencionados anteriormente).
- Complexidade Biológica: Variação no tamanho das colônias (estágios de crescimento) e na densidade (desde placas vazias até colônias incontáveis/sobrepostas).

**Há rótulos ou alvos associados a cada instância?**
Para o dataset AGAR cada imagem possui rótulos que indicam a posição de cada colônia, no formato de Bounding Boxes (caixas delimitadoras), também possui o número de colonias, e também a espécie do microorganismo (Escherichia coli, Staphylococcus aureus, Pseudomonas aeruginosa, Bacillus subtilis e Candida albican), já para o dataset do CNPEM as imagens não estão anotadas não conténdo informações sobre a espécie do microorganismos, apenas sobre o número total de colonias.

**Há informações ausentes em alguma instância?**
Não há informações ausentes para o dataset AGAR. Todas as instâncias de imagem possuem seus respectivos metadados (resolução, iluminação, tipo de microrganismo) e arquivos de anotação correspondentes, mas existem "omissões propositais" por design.
- Placas classificadas como empty (vazias): elas propositalmente não possuem bounding boxes (caixas de contagem), o que não deve ser confundido com falta de informação, mas sim como ausência de colônias.
- Imagens Uncountable: Em imagens classificadas como uncountable, as anotações individuais de colônias podem estar ausentes ou simplificadas, pois a alta densidade impede a distinção unitária

O dataset do CNPEM não possui anotações. 

**Existem relações entre instâncias?**
Não há relações explícitas entre instâncias. Imagens do CNPEM e do dataset AGAR são tratadas de forma independente.

**Há divisões recomendadas (treino/validação/teste)?**
Para o dataset AGAR os autores sugerem divisões específicas baseado na complexidade e resolução das imagens fornecidas, as recomendações é através de listas de arquivos (.txt) as divisões sugeridas são:
- Por resolução: Existem conjuntos separados para alta resolução (higher_resolution) e baixa resolução (lower_resolution), permitindo treinar e validar modelos em diferentes qualidades de entrada
- Por Complexidade: Há uma lista específica para instâncias difíceis (vague_train.txt), recomendada para testar a robustez do modelo em cenários de baixo contraste.

**Há erros, ruídos ou redundâncias?**
Possíveis fontes de ruído incluem variações de iluminação não controladas, possível sobreposição e união de colônias em placas de alta densidade. as fotos podem apresentar bolhas de ar, rachaduras no meio de cultura ou partículas de poeira na tampa da placa de Petri As fotos também possuem um background diferente, não sendo apenas a foto da placa em um fundo branco ou preto. Redundâncias não foram verificadas formalmente.
Há também ruído de anotação (subjetividade), o  que um anotador humano considerou como uma colônia visível na categoria vague, outro poderia considerar apenas ruído de fundo. 
Embora existam artefatos visuais e variações de iluminação, estes não são erros de integridade, mas sim desafios realistas que os modelos deve aprender a superar para ser aplicado em ambientes de laboratório reais.

**O dataset é autossuficiente?**
Sim, o dataset AGAR e o CNPEM é considerado autossuficiente para tarefas de visão computacional, mas requer etapas padrão de pré-processamento para uso em frameworks específicos.

**O dataset contém dados confidenciais?**
Não. As imagens são de placas de laboratório sem qualquer informação pessoal ou sigilosa.

**O dataset contém conteúdo potencialmente ofensivo?**
Não.

## 3. Processo de Coleta

**Como os dados foram adquiridos?**
- **CNPEM**: imagens capturadas diretamente por equipamento fotográfico em ambiente de laboratório, com condições de iluminação controladas.
- **Dataset AGAR**: imagens obtidas a partir de dataset publicado em artigo científico.

**Quais mecanismos foram usados para coletar os dados?**
- **CNPEM**: celular iPhone 16 posicionado verticalmente a 20 cm da placa e placa LED de 16.000 lx sob a placa de petri
- **Dataset AGAR**: foram usadas três câmeras diferentes (Nikon D3500 com lente de 60 mm; 24 Mpx CCD e IDS UI-5370CP-M-GL com 4.19 Mpx) dependendo do conjunto de fotos (alta ou baixa resolução) com um suporte com luz para a placa.

**Quem esteve envolvido na coleta?**
- **CNPEM**: estagiária do CNPEM.
- **Dataset AGAR**: pesquisadores do artigo.

**Qual foi o período de coleta?**
- **CNPEM**: Março de 2026.
- **Dataset AGAR**: 2020-2021.

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
- O subconjunto AGAR foi utilizado na pesquisa original para tarefas de detecção de colônias.
- O subconjunto do CNPEM é inédito neste contexto.

**Para quais outras tarefas o dataset poderia ser utilizado?**
- Segmentação de colônias;
- Classificação por tipo ou morfologia de colônia;
- Estimativa de densidade microbiana;
- Benchmarking de algoritmos de visão computacional em contexto biológico;

**Há algo na composição ou coleta que possa impactar usos futuros?**
A heterogeneidade entre os dois subconjuntos (diferenças de equipamento, iluminação e protocolo) pode introduzir viés de domínio (*domain shift*). Modelos treinados apenas no subconjunto AGAR podem não generalizar bem para as condições do CNPEM.

**Para quais tarefas o dataset NÃO deve ser usado?**
Diagnóstico clínico direto sem validação adicional por especialistas e qualquer aplicação que assuma homogeneidade entre os dois subconjuntos sem tratamento do domain shift

---

## 6. Distribuição

**O dataset será distribuído externamente?**
- O subconjunto do CNPEM está sujeito às políticas de dados da instituição, sendo necessário verificar permissões antes de qualquer distribuição pública.
- O subconjunto AGAR segue os termos de licença do artigo original.

**Como será distribuído?**
Via repositório GitHub.

**O dataset será distribuído sob alguma licença?**
- **CNPEM**: a definir conforme política institucional.
- **Subconjunto externo**: respeitar a licença original da publicação (Creative Common Attribution-NonCommercial 2.0 Generic license).

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
