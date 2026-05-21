# `<Título em Português do Projeto>`
# `<Project Title in in English>`

## Apresentação

O presente projeto foi originado no contexto das atividades da disciplina de pós-graduação *IA901 - Análise de Imagens e Reconhecimento de Padrões*, 
oferecida no primeiro semestre de 2026, na Unicamp, sob supervisão da Profa. Dra. Leticia Rittner, do Departamento de Engenharia de Computação e Automação (DCA) da Faculdade de Engenharia Elétrica e de Computação (FEEC).

> Incluir nome RA e foco de especialização de cada membro do grupo. Os projetos devem ser desenvolvidos em duplas ou trios.
> |Nome  | RA | Curso|
> |--|--|--|
> | Natália da Silva Guimarães  | 298997  | Mestrado em Engenharia Elétrica|
> | Nome2  | 123456  | Graduação em xxx|
> | Nome3  | 123456  | xxxx|


## Descrição do Projeto
> Descrição do objetivo principal do projeto, incluindo contexto gerador, motivação, etc. Qual problema você pretende solucionar? Qual a relevância do problema e o impacto da solução do mesmo?

## Metodologia
> Proposta de metodologia incluindo especificação de quais técnicas pretende-se explorar. Espera-se que nesta entrega você já seja capaz de descrever de maneira mais específica (do que na Entrega 1) quais as técnicas a serem empregadas em cada etapa do projeto.

## Bases de Dados e Evolução
> Elencar as bases de dados utilizadas no projeto.

Base de Dados | Endereço na Web | Resumo descritivo
----- | ----- | -----
Título da Base | http://base1.org/ | Breve resumo (duas ou três linhas) sobre a base.

> Forneça também o link para o "datasheet" criado para os datasets (anexado na pasta `data`, como indicado nas [instruções E2](https://github.com/Disciplinas-FEEC/IA901-2026S1/blob/main/templates/ia901-E2-instructions.md)), contendo informações mais detalhadas e sistematizadas sobre as bases de dados.

## Ferramentas
> Ferramentas e/ou bibliotecas já utilizadas e/ou ainda a serem utilizadas (com base na visão atual do grupo sobre o projeto).

## Workflow
> Use uma ferramenta que permita desenhar o workflow e salvá-lo como uma imagem (Draw.io, por exemplo). Insira a imagem nesta seção.
> Você pode optar por usar um gerenciador de workflow (Sacred, Pachyderm, etc) e nesse caso use o gerenciador para gerar uma figura para você.
> Lembre-se que o objetivo de desenhar o workflow é ajudar a quem quiser reproduzir seus experimentos.
> Mais informações sobre o workflow podem ser encontradas nos materiais de apoio no Classroom (Reprodutibilidade em pesquisa computacional - workflow).

## Experimentos e Resultados preliminares

No que se refere a implementação para a modelagem 3D, realizamos experimentos de segmentação 3D de tumores cerebrais usando o modelo ACU-Net 3D nos datasets BraTS 2018 e BraTS 2020. O modelo foi treinado com todas as modalidades (FLAIR, T1, T1CE, T2) e 64 fatias de profundidade por paciente. Para validação, utilizamos métricas como Dice, Jaccard, IoU, sensibilidade e especificidade. Observamos que o modelo conseguiu identificar corretamente as regiões maiores de tumor, mas apresentou falsos positivos em regiões menores e discretas, especialmente nos tumores ET e TC. As previsões 3D demonstraram sobreposição razoável com a máscara real, mas ainda há espaço para refinamento da segmentação fina.

## Próximos passos

Sobre a modelagem em 3D: 

- Ajuste de limiares e pós-processamento para reduzir falsos positivos (estimativa: 1 semana).
- Treinamento com batch maior ou aumento de épocas, usando toda a base de pacientes para melhorar a precisão global (estimativa: 2 semanas).
- Validação cruzada para avaliar robustez do modelo entre BraTS 2018 e 2020 (estimativa: 1 semana).
- Visualização avançada 3D integrando MRI real, tumor real e tumor previsto em uma mesma figura para análise qualitativa (estimativa: 3 dias).

## Uso de IA Generativa
Utilizamos ChatGPT para:

- Elaborar explicações e interpretações dos resultados, comparando métricas do modelo com as do artigo original.
- Criar códigos de visualização 3D avançada, incluindo sobreposição de cérebro, tumor real (azul) e tumor previsto (vermelho), para apresentações e relatórios.
- Prompt exemplo: “"Crie um modelo de segmentação 3D para tumores cerebrais usando Keras/TensorFlow. O modelo deve ser baseado em U-Net com atenção (ACU-Net), receber 4 modalidades de imagem (FLAIR, T1, T1CE, T2) com tamanho 128x128x64, e gerar 3 classes de saída (WT, TC, ET). Inclua: camadas Conv3D, BatchNormalization, MaxPooling3D, Dropout, Attention, Conv3DTranspose e concatenations necessárias. Mostre o resumo completo do modelo (model.summary())."”

## Referências
- Zhou, Z., Rahman Siddiquee, M. M., Tajbakhsh, N., Liang, J. UNet++: A Nested U-Net Architecture for Medical Image Segmentation. Deep Learning in Medical Image Analysis, 2018.
- Zhang, Z., Liu, Q., Wang, Y. Road Extraction by Deep Residual U-Net. IEEE Geoscience and Remote Sensing Letters, 2018. (inspiração para skip connections e atenção)
- O conceito de atenção em redes de segmentação: Oktay, O., Schlemper, J., Folgoc, L. L., et al. Attention U-Net: Learning Where to Look for the Pancreas. arXiv:1804.03999, 2018.