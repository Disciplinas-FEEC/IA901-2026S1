# `<Título em Português do Projeto>`
# `<Project Title in in English>`

## Apresentação

O presente projeto foi originado no contexto das atividades da disciplina de pós-graduação *IA901 - Análise de Imagens e Reconhecimento de Padrões*, 
oferecida no primeiro semestre de 2026, na Unicamp, sob supervisão da Profa. Dra. Leticia Rittner, do Departamento de Engenharia de Computação e Automação (DCA) da Faculdade de Engenharia Elétrica e de Computação (FEEC).

> Incluir nome RA e foco de especialização de cada membro do grupo. Os projetos devem ser desenvolvidos em duplas ou trios.
> |Nome  | RA | Curso|
> |--|--|--|
> | Brendon Erick Euzébio Rus Peres  | 256130  | Mestrado em xxxx|
> | Luís Fernando Silva Lima  | 298966 | Mestrado em xxxx|
> | Mateus Bizzo da Silva  | 200216  | Mestrado em xxxx|


## Descrição do Projeto
> Descrição do objetivo principal do projeto, incluindo contexto gerador, motivação, etc. Qual problema você pretende solucionar? Qual a relevância do problema e o impacto da solução do mesmo?

## Metodologia
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
CHIU, Mang Tik et al. Agriculture-vision: A large aerial image database for agricultural pattern analysis. In: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. 2020. p. 2828-2838.

CHIU, Mang Tik et al. The 1st agriculture-vision challenge: Methods and results. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops. 2020. p. 48-49.

Buvanesh, Anirudh & Narang, Pratik & Sinha, Soumendu. (2021). Proposing A Deep Learning Based Architecture for Agriculture Vision. 10.13140/RG.2.2.26628.86404. 

SHEN, Yao; WANG, Lei; JIN, Yue. AAFormer: A multi-modal transformer network for aerial agricultural images. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 2022. p. 1705-1711.

INNANI, Shubham et al. Fuse-pn: A novel architecture for anomaly pattern segmentation in aerial agricultural images. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 2021. p. 2960-2968.

SAHIN, Halil Mertkan et al. Segmentation of weeds and crops using multispectral imaging and CRF-enhanced U-Net. Computers and Electronics in Agriculture, v. 211, p. 107956, 2023.

SA, Inkyu et al. WeedMap: A large-scale semantic weed mapping framework using aerial multispectral imaging and deep neural network for precision farming. Remote Sensing, v. 10, n. 9, p. 1423, 2018.

WIJITDECHAKUL, Jinmika et al. UAV-based multispectral image analysis system with semantic computing for agricultural health conditions monitoring and real-time management. In: 2016 International Electronics Symposium (IES). IEEE, 2016. p. 459-464.
