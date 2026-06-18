# `Segmentação Semântica de Imagens Agrícolas usando NDVI e NDWI`
# `Semantic Segmentation of Agricultural Images using NDVI and NDWI`

## Apresentação

O presente projeto foi originado no contexto das atividades da disciplina de pós-graduação *IA901 - Análise de Imagens e Reconhecimento de Padrões*, 
oferecida no primeiro semestre de 2026, na Unicamp, sob supervisão da Profa. Dra. Leticia Rittner, do Departamento de Engenharia de Computação e Automação (DCA) da Faculdade de Engenharia Elétrica e de Computação (FEEC).

|Nome  | RA | Curso|
|--|--|--|
| Brendon Erick Euzébio Rus Peres | 256130 | Mestrado em Engenharia Elétrica |
| Luís Fernando Silva Lima | 298966 | Mestrado em Engenharia Elétrica |
| Mateus Bizzo da Silva | 200216 | Mestrado em Engenharia de Computação |


## Descrição do Projeto
A segmentação semântica de imagens aéreas agrícolas é uma das principais direções de pesquisa no campo da visão agrícola. Um algoritmo eficaz de segmentar terras agrícolas aéreas é muito importante para a detecção de áreas de anomalias no campo, como a segmentação de áreas secas, fim de linha, deficiência de nutrientes e assim por diante. O reconhecimento do padrão de anomalia é útil para monitorar o estado local das terras agrícolas, avaliar o impacto de desastres naturais. A análise de imagens aéreas agrícolas também apoia a formulação de políticas agrícolas nacionais para aumentar o rendimento dos campos agrícolas e o desenvolvimento econômico regional [[1]].


O método mais difundido para obter informações sobre a vegetação é através de imagens multiespectrais (MS). Com dados MS, é possível calcular vários índices de vegetação. Normalmente, essas imagens MS são adquiridas de aeronaves ou satélites, mas apenas uma parte das imagens de satélite disponíveis é distribuída gratuitamente [[2]]. Para compreender como esses índices diferenciam a cobertura vegetal de outros materiais, a Figura 1 apresenta a organização do espectro eletromagnético, destacando as regiões de maior interesse para o sensoriamento remoto, como o visível e o infravermelho.

<div align="center">
  <img src="assets/1718303710189.png" alt="Representação do Espectro Eletromagnético" width="600">
  
  <p>
    <b>Figura 1:</b> Representação visual do espectro eletromagnético.
    <br>
    <i>Fonte: <a href="https://www.linkedin.com/pulse/câmeras-multiespectrais-e-hiperespectrais-embarcadas-em-thiago-silva--iau3f/" target="_blank">Thiago Silva (2026)</a>.</i>
  </p>
</div>

Certas bandas, capturadas em frequências específicas ao longo do espectro eletromagnético, têm a capacidade de revelar informações distintas sobre as plantas. Entre essas bandas, a do infravermelho próximo (NIR) possui grande relevância em tarefas agrícolas, pois consegue destacar de forma eficaz a absorção da clorofila e o conteúdo de água na vegetação. Um índice amplamente utilizado que depende da banda NIR é o NDVI (Normalized Difference Vegetation Index), que fornece uma medida quantitativa do vigor e da densidade da vegetação. Em comparação com dados baseados apenas em RGB, a incorporação dessa informação espectral adicional pode potencializar a discriminação de diferentes objetos e feições dentro das imagens. Isso viabiliza uma identificação e classificação mais precisas das culturas, aprimorando o processo de segmentação de imagens [[3]].

Além disso, o NDWI (Normalized Difference Water Index) tem sido amplamente utilizado em Sensoriamento Remoto (SR) para distinguir corpos d'água de outras superfícies. Este índice baseia-se na observação de que os corpos d'água absorvem a maior parte da banda do NIR, enquanto a vegetação a reflete em sua extensão máxima [[4],[5]]. Na Tabela 1, é possível observar a correlação de diferentes circunstâncias nas lavouras com os índices abordados.

<div align="center">

<b>Tabela 1:</b> Condições de saúde da plantação de acordo com os índices NVDI e NDWI

| Significado da Correlação | NDVI | NDWI |
| :--- | :---: | :---: |
| Vegetação saudável durante a etapa de transpiração (Meio-dia) | + | + |
| Vegetação saudável, mas o solo está seco ou com baixa umidade | + | + |
| Vegetação saudável (Momento de máxima intensidade de verde) | + | - |
| Vegetação saudável em solo arenoso (ou planta em deserto), como abacaxi | + | - |
| Sem vegetação em solo úmido | - | + |
| Vegetação não saudável com algum teor de água de plantas daninhas em solo seco | - | + |
| Sem vegetação em solo frágil/friável | - | - |
| Vegetação não saudável | - | - |

<i>Fonte: Adaptado de Sa et al. [[6]].</i>
</div>

Além disso, Sa et al. [[6]] propuseram o WeedMap, um framework de mapeamento semântico que utiliza imagens multiespectrais para otimizar a detecção de espécies invasoras na agricultura de precisão e seus resultados mostraram que o NDVI contribui significativamente para uma classificação precisa da vegetação. Nesse contexto, Wijitdechakul [[7]] apresentaram um espaço multiespectral semântico para a análise de fazendas o qual consistia de imagens com NDVI, NDWI e SAVI (Soil Adjust Vegetation Index) o qual se mostrou capaz de detectar áreas agrícolas saudáveis e não saudáveis por meio da análise de processamento de imagens multiespectrais. A partir dessas premissas, espera-se que a inclusão dessas informações espectrais resulte em uma maior eficiência na segmentação de bordas e anomalias complexas. Ao fornecer um contraste nítido entre diferentes níveis de vigor vegetativo e corpos d'água, os índices reduzem o ruído de iluminação nas imagens aéreas, permitindo que o modelo delimite com precisão as transições de estresse foliar, como zonas de drydown ou deficiência de nutrientes.

A principal motivação deste trabalho é verificar a eficácia de modelos de segmentação semântica com a integração dos canais RGB com os índices NDVI e NDWI, haja vista a sua aplicação no monitoramento de lavouras e na identificação de anomalias em imagens aéreas agrícolas. O sistema proposto deve ser capaz de processar dados multiespectrais para delimitar com precisão regiões de estresse vegetativo e corpos d'água superficiais, correlacionando esses índices com as classes de interesse. O resultado esperado do modelo será a geração de máscaras de segmentação semanticamente consistentes, onde os limites geométricos das anomalias sejam preservados de forma estatisticamente e espacialmente coerente com os dados reais de entrada.

## Metodologia
> Abordagem adotada pelo projeto na busca pela resposta às perguntas de pesquisa. Justificar teoricamente, sempre que possível, a metodologia adotada.

## Bases de Dados
> Elencar as bases de dados utilizadas no projeto.

> Faça uma descrição sobre o que o grupo concluiu sobre esta base. Sugere-se que respondam perguntas ou forneçam informações indicadas a seguir:
> * Qual o formato dessa base, tamanho, tipo de anotação?
> * Quais as transformações e tratamentos feitos? Limpeza, reanotação, etc.
> * Utilize tabelas e/ou gráficos que descrevam os aspectos principais da base que são relevantes para o projeto.

> Forneça também o link para o "datasheet" criado para os datasets (anexado na pasta `data`, como indicado nas [instruções E2](https://github.com/Disciplinas-FEEC/IA901-2026S1/blob/main/templates/ia901-E2-instructions.md)), contendo informações mais detalhadas e sistematizadas sobre as bases de dados.

## Ferramentas
> Panorama das ferramentas utilizadas incluindo uma breve discussão sobre o uso das mesmas.

## Workflow
> Use uma ferramenta que permita desenhar o workflow e salvá-lo como uma imagem (Draw.io, por exemplo). Insira a imagem nesta seção.
> Você pode optar por usar um gerenciador de workflow (Sacred, Pachyderm, etc) e nesse caso use o gerenciador para gerar uma figura para você.
> Lembre-se: o objetivo de desenhar o workflow é ajudar a quem quiser reproduzir seus experimentos!!!

## Experimentos e Resultados
> Descrição dos resultados mais importantes obtidos.
> Apresente os resultados da forma mais rica possível, com gráficos e tabelas. Mesmo que o seu código rode online em um notebook, copie para esta parte a figura estática. A referência a código e links para execução online pode ser feita também, mas é preciso apresentar os principais resultados neste documento.

## Discussão
> Discussão dos resultados. Relacionar os resultados com as perguntas de pesquisa ou hipóteses avaliadas.
> A discussão dos resultados também pode ser feita opcionalmente na seção de Resultados, na medida em que os resultados são apresentados. Aspectos importantes a serem discutidos: É possível tirar conclusões dos resultados? Quais? Há indicações de direções para estudo? São necessários trabalhos mais profundos?

## Conclusão
> Destacar as principais conclusões obtidas no desenvolvimento do projeto.
> Destacar os principais desafios enfrentados.
> Principais lições aprendidas.

## Trabalhos Futuros
> O que poderia ser melhorado se houvesse mais tempo?

## Uso de IA Generativa
> Adicione aqui em quais tarefas foi usada alguma ferramenta de IA Generativa. Para cada tarefa indicada detalhe qual a ferramenta e qual o prompt utilizado.

## Referências
[[1]] SHEN, Yao; WANG, Lei; JIN, Yue. AAFormer: A multi-modal transformer network for aerial agricultural images. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 2022. p. 1705-1711.

[1]: https://openaccess.thecvf.com/content/CVPR2022W/AgriVision/html/Shen_AAFormer_A_Multi-Modal_Transformer_Network_for_Aerial_Agricultural_Images_CVPRW_2022_paper.html

[[2]] M. Barjaktarovic, M. Santoni and L. Bruzzone, "Design and Verification of a Low-Cost Multispectral Camera for Precision Agriculture Application," in IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing, vol. 17, pp. 6945-6957, 2024, doi: 10.1109/JSTARS.2024.3377104. 

[2]: https://ieeexplore.ieee.org/abstract/document/10472047

[[3]] Yuan, K., Zhuang, X., Schaefer, G., Feng, J., Guan, L., Fang, H.: Deep-learningbased multispectral satellite image segmentation for water body detection. IEEE J. Sel. Topics Appl. Earth Observations Remote Sens. 14, 7422–7434 (2021).

[3]: https://ieeexplore.ieee.org/abstract/document/9492784

[[4]] E. Özelkan (2020). Water body detection analysis using NDWI indices derived from Landsat-8 OLI [J]. Polish Journal of Environmental Studies, 29(2):1759-1769.

[4]: https://www.pjoes.com/pdf-110447-47217?filename=47217.pdf


[[5]] V. Shashikant, A. Shariff, A. Wayayok, et al (2021). Utilizing TVDI and NDWI to classify severity of agricultural drought in Chuping, Malaysia [J]. Agronomy, 11(6): 1243. 

[5]: https://www.mdpi.com/2073-4395/11/6/1243

[[6]] SA, Inkyu et al. WeedMap: A large-scale semantic weed mapping framework using aerial multispectral imaging and deep neural network for precision farming. Remote Sensing, v. 10, n. 9, p. 1423, 2018.

[6]: https://www.mdpi.com/2072-4292/10/9/1423

[[7]] WIJITDECHAKUL, Jinmika et al. UAV-based multispectral image analysis system with semantic computing for agricultural health conditions monitoring and real-time management. In: 2016 International Electronics Symposium (IES). IEEE, 2016. p. 459-464.

[7]: https://ieeexplore.ieee.org/abstract/document/7861050?casa_token=ZVBJWtArFtMAAAAA:mj2V13NujgR3PuCt4vT9YSiXDYv3cyrE4v8F5_BEk20n6jfQgs8mSwvMbBdLZG-iYjO1ht0ZVrM

[[8]] SAHIN, Halil Mertkan et al. Segmentation of weeds and crops using multispectral imaging and CRF-enhanced U-Net. Computers and Electronics in Agriculture, v. 211, p. 107956, 2023.

[8]: https://www.sciencedirect.com/science/article/pii/S0168169923003447

[[9]] P. Lottes, M. Hoeferlin, S. Sander, M. Müter, P. Schulze and L. C. Stachniss, "An effective classification system for separating sugar beets and weeds for precision farming applications," 2016 IEEE International Conference on Robotics and Automation (ICRA), Stockholm, Sweden, 2016, pp. 5157-5163, doi: 10.1109/ICRA.2016.7487720.

[9]: https://ieeexplore.ieee.org/abstract/document/7487720?casa_token=WAEDZqDP2b4AAAAA:gIlJa8XbV39uWIsxHV9_fUjS4kAd8skRZOO3a1qsMCLfrN7eFAASlnF6e_YIG9NfqpUhtXnLW5I

[[10]] CHIU, Mang Tik et al. Agriculture-vision: A large aerial image database for agricultural pattern analysis. In: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. 2020. p. 2828-2838.

[10]: https://openaccess.thecvf.com/content_CVPR_2020/html/Chiu_Agriculture-Vision_A_Large_Aerial_Image_Database_for_Agricultural_Pattern_Analysis_CVPR_2020_paper.html

[[11]] INNANI, Shubham et al. Fuse-pn: A novel architecture for anomaly pattern segmentation in aerial agricultural images. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. 2021. p. 2960-2968.

[11]: https://openaccess.thecvf.com/content/CVPR2021W/AgriVision/html/Innani_Fuse-PN_A_Novel_Architecture_for_Anomaly_Pattern_Segmentation_in_Aerial_CVPRW_2021_paper.html

[[12]] Buvanesh, Anirudh & Narang, Pratik & Sinha, Soumendu. (2021). Proposing A Deep Learning Based Architecture for Agriculture Vision. 10.13140/RG.2.2.26628.86404. 

[12]: https://www.researchgate.net/profile/Anirudh-Buvanesh-2/publication/355886893_Proposing_A_Deep_Learning_Based_Architecture_for_Agriculture_Vision/links/6182a1e30be8ec17a9671be4/Proposing-A-Deep-Learning-Based-Architecture-for-Agriculture-Vision.pdf

[[13]] CHIU, Mang Tik et al. The 1st agriculture-vision challenge: Methods and results. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops. 2020. p. 48-49.

[13]: https://openaccess.thecvf.com/content_CVPRW_2020/html/w5/Chiu_The_1st_Agriculture-Vision_Challenge_Methods_and_Results_CVPRW_2020_paper.html

