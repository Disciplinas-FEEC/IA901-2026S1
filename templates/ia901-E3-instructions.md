# IA901 - Projeto - Entrega final (E3)

O objetivo do projeto final desta disciplina é fazer com que os alunos tentem resolver um problema real utilizando as técnicas discutidas ao longo da disciplina, tanto de processamento de imagens quanto de reconhecimento de padrões.

## Entrega Final

A entrega final do projeto consiste em duas etapas:
* Apresentação do Projeto a ser realizada em sala de aula. 
* Atualização do repositório GitHub já criado anteriormente. A versão final do repositório será avaliada.
  
De maneira análoga à entrega E2, a atualização do repositório GitHub inclui:
* Atualização do arquivo README.md do projeto incluindo as seções do template fornecido ([IA901-E3-template.md](https://github.com/Disciplinas-FEEC/ia901-2026S1/blob/main/templates/ia901-E3-template.md)).
* Após a finalização da edição do conteúdo da segunda entrega, atribuição da tag de release `IA901_E3` no repositório de origem.
* **Pull request**  do projeto no  **branch  principal** até a data de entrega.


## Instruções para a Apresentação

Diretrizes para apresentação (sugestões de tópicos):
* Deve contextualizar o projeto e apresentar o problema
* Explicitar qual o objetivo do projeto
* Abordagem adotada: dados e métodos. Pode ser interessante comentar sobre as principais ferramentas utilizadas (incluir informações úteis para que outros possam utilizá-las)
* Resultados obtidos
* Discussão dos resultados
* Conclusões / Lições aprendidas
* Trabalhos futuros

DICA: Considerem no máximo 1 slide por minuto. Portanto, uma apresentação de 15 minutos não deve ter mais de 15 slides.

## Avaliação

A avaliação do projeto final será realizada não apenas pelos professores da disciplina, mas também passará por etapa de avaliação por pares. Instruções serão fornecidas posteriormente no ambiente Classroom da Disciplina.

# Estrutura do Repositório
A fim de uniformizar os repositórios de projetos da disciplina, os diretórios de seu repositório deverão ser nomeados e utilizados segundo a estrutura sugerida a seguir.

Note que nem todos os diretórios ou arquivos serão necessários para todos os projetos. Foque em seguir o padrão para os diretórios que forem necessários. Não crie diretórios que não serão utilizados.

~~~
├── README.md          <- apresentação do projeto
│
├── data
│   ├── processed      <- dados finais usados para a modelagem
│   ├── interim        <- dados intermediários, e.g., resultado de transformação
│   └── raw            <- dados originais sem modificações
│
├── notebooks          <- Jupyter notebooks ou equivalentes
│
├── src                <- fonte em linguagem de programação (e.g., C++)
│   └── README.md      <- instruções básicas de instalação/execução
│
└── assets             <- mídias usadas no projeto
~~~

## `README.md`

Para a entrega E3, o README.md do repositório deve ser formatado [segundo o modelo disponibilizado neste link](https://github.com/Disciplinas-FEEC/ia901-2023S1/blob/main/templates/ia901-E3-template.md).

Caso não tenha experiência com edição em Markdown, vide referência: [Mastering Markdown](https://guides.github.com/features/mastering-markdown/).
Existem também múltiplas ferramentas para edição de Markdown como, por exemplo, [StackEdit](https://stackedit.io/).

## `data`

Dados utilizados no projeto respeitadas as possíveis implicações éticas, se você tiver licença para tal e se o volume for suportado pelo Github. Você pode optar por colocar um subconjunto ilustrativo dos dados.

É importante que sejam colocados os dados originais (se for possível) para garantir a reprodutibilidade do processo. Os originais são colocados na subpasta `raw`. Dados intermediários devem ser colocados na pasta `interim`. Coloque os dados finais que serviram de entrada para as suas análises na subpasta `processed`.

## `notebooks`

Código do seu projeto que pode ser executado online sem instalação de software, tal como um notebook em Jupyter ou equivalente.

## `src`

Código em alguma linguagem ou projeto em Orange, Weka e similares.

Se for código em linguagem de programação, tente organizá-lo de forma que seja simples a sua execução por terceiros, por exemplo, acrescente as bibliotecas necessárias etc. Acrescente na raiz um arquivo `README.md` com as instruções básicas de instalação e execução.

## `assets`

Qualquer mídia usada no seu projeto: vídeo, ilustrações, arquivos PDF etc.

Note que nem todos os diretórios ou arquivos serão necessários para todos os projetos. Foque em seguir o padrão para os diretórios que forem necessários. Não crie diretórios que não serão utilizados.

