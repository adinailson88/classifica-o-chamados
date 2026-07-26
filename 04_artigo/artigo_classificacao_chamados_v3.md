**CLASSIFICAÇÃO AUTOMÁTICA MULTIMODELO DE CHAMADOS DE MANUTENÇÃO PREDIAL
UNIVERSITÁRIA EM PORTUGUÊS BRASILEIRO: PROTOCOLO DE GOVERNANÇA PREDITIVA
COM VALIDAÇÃO HUMANA SOB RÓTULOS HISTÓRICOS RUIDOSOS**

*Multi-model automatic classification of university building maintenance
work orders in Brazilian Portuguese: a predictive governance protocol
with human validation under noisy historical labels*

**Adinailson Guimarães de Oliveira** - adinailson.oliveira@cja.ufsb.edu.br
**Fabrício Berton Zanchi** - fabricio.berton@ufsb.edu.br

Universidade Federal do Sul da Bahia (UFSB), Programa de Pós-Graduação
em Biossistemas

**RESUMO**

A classificação automática de chamados de manutenção predial constitui
recurso estratégico para a qualificação da triagem operacional e para a
ampliação da governança baseada em evidências em instituições públicas.
Contudo, em bases históricas de sistemas informatizados de gestão de
chamados, a categoria originalmente registrada não deve ser tratada como
verdade absoluta, uma vez que pode refletir decisões operacionais
ruidosas, taxonomias sobrepostas, registros incompletos e interpretações
heterogêneas entre equipes de atendimento. O presente artigo propõe um
protocolo multimodelo para classificação de chamados reais de manutenção
predial universitária em português brasileiro, extraídos do sistema GLPI
da Universidade Federal do Sul da Bahia. O experimento utiliza 13.965
chamados não vazios, organizados em 55 categorias históricas, e compara
classificadores clássicos baseados em TF-IDF (Naive Bayes, Regressão
Logística, LinearSVC, SGD, Random Forest e Extra Trees) e rede neural LSTM
bidirecional. O BERTimbau permanece como extensão planejada, sem treino
concluído ou métrica própria nesta consolidação. O diferencial metodológico
reside na distinção entre concordância com o histórico administrativo e
acerto validado por revisão humana, tratando a categoria histórica como
referência preliminar imperfeita. A avaliação humana cobre 9.534
chamados, com 9.044 decisões travadas e 52
conflitos explicitamente excluídos da verdade validada. Como a seleção não
é aleatória e prioriza divergências e casos críticos, esses resultados não
estimam o desempenho da base completa (COCHRAN, 1977). O LinearSVC lidera
tanto a concordância com o histórico (80,31%, IC95%:
79,63%--80,97%) quanto o acerto
validado (95,02%, IC95%: 94,58%--
95,46%), enquanto o LSTM apresenta concordância de
67,18% e acerto validado de 88,11%.
A normalidade da concordância por turno foi rejeitada para todos os modelos,
justificando testes não paramétricos. O custo computacional é incorporado
como dimensão de avaliação, evidenciando que modelos lineares podem oferecer
melhor relação entre desempenho e viabilidade operacional em cenários de
texto curto, ruidoso e desbalanceado.

**Palavras-chave:** manutenção predial; classificação de chamados;
processamento de linguagem natural; rótulos ruidosos; validação humana;
governança preditiva.

**ABSTRACT**

*Automatic classification of building maintenance work orders is a strategic
resource for operational triage and evidence-based governance in public
institutions. Historical labels, however, may reflect noisy decisions,
overlapping taxonomies, incomplete records and heterogeneous interpretations.
This paper proposes a multi-model protocol for 13,965
real university building-maintenance work orders in Brazilian Portuguese,
organized into 55 historical categories. The comparison includes TF-IDF-based
classifiers and a bidirectional LSTM; BERTimbau remains a planned extension
without completed fine-tuning. The methodological contribution is the explicit
distinction between agreement with administrative history and accuracy against
human-validated decisions. Human review covers 9,534
records, with 9,044 locked decisions and
52 conflicts excluded from the validated
ground truth. Because the reviewed sample is non-random and prioritizes
disagreements and critical cases, the results do not estimate performance over
the complete database. LinearSVC leads both historical agreement
(80.31%, 95% CI:
79.63%--80.97%)
and human-validated accuracy (95.02%,
95% CI: 94.58%--95.46%),
whereas LSTM achieves 67.18% historical
agreement and 88.11% validated accuracy.
Normality is rejected for all models, supporting non-parametric comparisons.
Computational cost is included as an evaluation dimension, indicating that
linear models provide a favorable balance between performance and operational
feasibility for short, noisy and imbalanced technical text.*

***Keywords:** building maintenance; work-order classification; natural
language processing; noisy labels; human validation; predictive governance.*

**1. INTRODUÇÃO**

Um campus universitário pode ser descrito como um biossistema
construído: a integração dinâmica entre infraestrutura física,
atividade humana, sistemas tecnológicos e condicionantes ambientais,
cuja persistência ao longo do tempo depende de mecanismos de
retroalimentação contínua entre uso, falha e reparo (CAPRA, 1996; ODUM,
1971). A ecologia urbana descreve esse tipo de sistema como um
organismo em troca permanente de matéria, energia e informação com seu
entorno, cuja governança bem-sucedida depende da capacidade
institucional de captar sinais operacionais e convertê-los em decisão
(GRIMM *et al.*, 2008). Em instituições federais de ensino superior
(IFES), esse sinal assume, na prática, a forma de registros textuais de
chamados de manutenção predial — a matéria-prima do *feedback*
operacional do biossistema construído. Esses registros, no entanto,
nascem aprisionados em linguagem não estruturada, fragmentária e
sujeita a interpretação individual no momento do atendimento, o que
impede seu uso direto por qualquer mecanismo de decisão automatizada
(MORAIS; PAULA; REIS, 2023; MOHAMMED; AMOAH, 2025).

A exploração analítica dessas bases enfrenta ao menos três obstáculos
estruturais, agravados pela restrição orçamentária que historicamente
limita o custeio da manutenção predial em IFES a patamares inferiores a
2% do orçamento institucional (MARTINS; ESPEJO, 2024; PAMPANA *et al.*,
2022). O primeiro é a natureza textual curta, heterogênea e
frequentemente incompleta dos registros: chamados de manutenção
predial são redigidos em linguagem técnica fragmentária, com
abreviações locais e jargões de equipe que dificultam a aplicação
direta de modelos genéricos de processamento de linguagem natural (PLN)
(SUNDARAM; ZEID, 2025). O segundo é o desbalanceamento entre
categorias: demandas recorrentes de climatização, elétrica e
hidrossanitária concentram grande parte da base, enquanto categorias
raras dispõem de poucos exemplos para treinamento supervisionado (LI
*et al.*, 2024). O terceiro, talvez o mais crítico do ponto de vista
metodológico, é a qualidade do próprio rótulo histórico: a categoria
registrada no momento do chamado pode resultar de interpretação rápida,
conveniência operacional ou taxonomia ainda não estabilizada, de modo
que o histórico administrativo constitui evidência importante, mas não
verdade absoluta (ZHANG *et al.*, 2025; KEJRIWAL *et al.*, 2024).

A literatura recente sobre mineração textual de ordens de manutenção
confirma a relevância de técnicas de PLN para transformar registros
textuais em insumos de gestão. Li *et al.* (2024) demonstraram, em base
hospitalar com 15.623 ordens de serviço, que a atribuição automática de
equipes por PLN alcança acurácia de 0,83, reduzindo substancialmente a
dependência de triagem manual. Sundaram e Zeid (2025) analisaram
registros de *Maintenance Work Orders* sob a abordagem de *Technical
Language Processing*, argumentando que textos técnicos de manutenção
funcionam como *black holes* informacionais quando armazenam dados
relevantes sem serem efetivamente utilizados na tomada de decisão.
Bouabdallaoui et al. (2020), por sua vez, aplicaram modelos de PLN à
classificação de requisições de manutenção em edificação hospitalar,
reportando acurácia média de 78% com múltiplos métodos de representação
textual. Contudo, a maior parte dessas aplicações concentra-se em bases
em inglês ou chinês e em domínios industriais ou hospitalares,
configurando lacuna relevante para corpora em português brasileiro no
contexto da manutenção predial pública universitária.

Diante desse quadro, a pergunta que orienta este capítulo não é qual
classificador mais concorda com a categoria histórica, mas outra, mais
ampla e mais alinhada à função de governança que esses dados devem
cumprir: como extrair, de forma confiável e auditável, dado estruturado
a partir de texto ruidoso, de modo que esse dado possa alimentar um
sistema de governança preditiva sem herdar acriticamente os erros do
próprio histórico que lhe deu origem? Rótulos ruidosos em PLN não
apenas reduzem o desempenho de classificadores, como também podem
ampliar o consumo de recursos computacionais necessários para tratá-los
(ZHANG *et al.*, 2025); mais importante, *benchmarks* anotados por
humanos frequentemente carregam variabilidade relevante, o que torna
questionável a prática de tratar qualquer rótulo — humano ou histórico
— como verdade absoluta e não sujeita a julgamento (KEJRIWAL *et al.*,
2024). A classificação automática apresentada neste capítulo é,
portanto, a primeira camada de um protocolo maior — não seu produto
final: uma camada que precisa produzir dado auditável o bastante para
que divergências entre inteligência artificial e histórico
administrativo sejam tratadas como evidência de revisão taxonômica, não
como ruído a ser descartado.

Com base em chamados reais da Universidade Federal do Sul da Bahia
(UFSB), este capítulo propõe uma comparação multimodelo de
classificadores de texto aplicada a chamados de manutenção predial em
português brasileiro. A base experimental contém 13.965 chamados não
vazios, distribuídos em 55 categorias históricas; os campos textuais
considerados agregam título e descrição do chamado, além de informações
associadas à ordem de serviço. O estudo compara modelos clássicos
baseados em TF-IDF (Naive Bayes, Regressão Logística, LinearSVC, SGD,
Random Forest e Extra Trees) com uma rede neural LSTM bidirecional; o
BERTimbau é mantido como extensão planejada, mas não integra as
comparações enquanto não houver treino concluído e métricas próprias
rastreáveis. O objeto de avaliação, portanto, não é o classificador
isolado, mas o protocolo de governança preditiva que articula
aprendizado de máquina, auditoria estatística, custo computacional e
validação humana — em consonância com a manutenção baseada em
evidências preconizada pela NBR 5674 (ABNT, 2012) e com a integração
físico-humano-tecnológico-ambiental que caracteriza um biossistema
construído.

Os objetivos específicos deste capítulo são: (i) apresentar um
protocolo de classificação automática que produza dado estruturado
auditável a partir de texto livre, como primeira camada de um sistema
de governança preditiva; (ii) distinguir concordância com rótulo
histórico de acerto validado, evitando equiparar categoria histórica a
*ground truth* incontestável; (iii) avaliar desempenho por métricas
globais, métricas balanceadas, intervalos de confiança e testes
estatísticos pareados adequados a dados não normais; (iv) incorporar
custo computacional como dimensão de decisão operacional; e (v)
transformar divergências entre inteligência artificial e histórico em
evidência para revisão taxonômica e retroalimentação da base de treino.

**2. REFERENCIAL CONCEITUAL**

**2.1 Processamento de linguagem natural em ordens de manutenção**

Ordens de manutenção constituem registros operacionais com valor
informacional elevado, porém usualmente subutilizado. Elas documentam
sintomas, locais, equipamentos, procedimentos, materiais e soluções
executadas, acumulando-se ao longo de anos em sistemas informatizados
cuja forma textual e semiestruturada dificulta o uso direto em
planejamento e alocação de recursos (PAMPANA *et al.*, 2022; MORAIS;
PAULA; REIS, 2023). Li *et al.* (2024) propuseram estrutura baseada em
PLN para análise e atribuição automática de ordens de manutenção
hospitalar, utilizando 15.623 registros de hospital municipal em Xangai
e reportando acurácia de 0,83 na tarefa de atribuição de trabalhadores,
resultado que evidencia a possibilidade de automatizar processos antes
dependentes de triagem manual em contextos prediais. Esse trabalho
constitui referência-âncora para a presente pesquisa por tratar
diretamente da automação de ordens de manutenção predial, embora em
idioma, tipologia institucional e estrutura taxonômica distintos.

Sundaram e Zeid (2025), ao analisar registros textuais de *Maintenance
Work Orders* sob a abordagem de *Technical Language Processing*,
defenderam que textos técnicos de manutenção funcionam como repositórios
informacionais subutilizados quando não integrados a processos
decisórios. Essa perspectiva é especialmente pertinente à manutenção
predial universitária, na qual chamados curtos, abreviações locais,
nomes de ambientes e descrições incompletas dificultam o uso de modelos
genéricos sem adaptação ao domínio. Bouabdallaoui et al. (2020)
reportaram acurácia média de 78% na classificação de requisições de
manutenção predial hospitalar utilizando múltiplos métodos de PLN,
resultado que reforça a viabilidade da abordagem, mas também evidencia a
necessidade de adaptação lexical e semântica ao corpus específico.

**2.2 Classificação de tickets e evolução dos modelos**

A classificação automática de *tickets* em ambientes de suporte técnico
e ITSM evoluiu de representações vetoriais baseadas em frequência
lexical para *embeddings* e modelos de linguagem pré-treinados. Liu,
Benge e Jiang (2023) propuseram o Ticket-BERT para rotulagem de
*tickets* de incidentes, enfatizando desafios como atualização contínua
de rótulos e necessidade de aprendizado ativo. Entretanto, a
transferência direta de achados do ITSM para a manutenção predial deve
ser cautelosa, pois a semântica do domínio envolve sistemas físicos,
ambientes e equipamentos prediais que não coincidem com categorias de
incidentes de *software* ou infraestrutura digital (SUNDARAM; ZEID,
2025).

Modelos lineares com TF-IDF continuam competitivos em tarefas de texto
curto, especialmente quando o corpus é de porte médio, o vocabulário
possui alta especificidade técnica e as classes são desbalanceadas
(GALKE; SCHERP, 2022). Nesses cenários, modelos profundos podem não
compensar seu custo computacional caso não disponham de volume
suficiente, balanceamento adequado ou *embeddings* fortemente adaptados
ao domínio. Galke e Scherp (2022), em revisão comparativa abrangente de
métodos para classificação textual, demonstraram que classificadores
baseados em *bag-of-words* com TF-IDF e SVM permanecem altamente
competitivos frente a redes neurais em múltiplos *benchmarks*, sobretudo
quando o corpus é reduzido ou o vocabulário é altamente especializado.
Esse achado é particularmente relevante para o contexto institucional de
manutenção predial, onde a base operacional raramente atinge escala
compatível com as exigências de modelos de linguagem de grande porte.

**2.3 Rótulos ruidosos e verdade operacional**

O problema de rótulos ruidosos é central em aprendizado supervisionado
aplicado a bases administrativas. Em classificação textual, ruído de
rótulo pode decorrer de ambiguidade semântica, polissemia, insuficiência
de contexto, sobreposição taxonômica, julgamento subjetivo ou erro
humano de registro (ZHANG *et al.*, 2025). Conforme levantamento de
Zhang *et al.* (2025), rótulos ruidosos em PLN afetam o desempenho dos
modelos e podem ampliar o consumo de recursos, exigindo métodos robustos
de tratamento de ruído. Kejriwal *et al.* (2024) reforçam que
*benchmarks* rotulados por humanos podem conter variabilidade relevante,
questionando a prática de assumir uma única verdade absoluta quando há
julgamento subjetivo envolvido. No contexto do presente artigo, a
categoria histórica do chamado é tratada como referência administrativa,
não como verdade final, e a verdade operacional deve ser construída por
validação humana com registro explícito da decisão tomada.

**2.4 Custo computacional e eficiência em PLN**

A avaliação de modelos de PLN tem sido tradicionalmente orientada por
métricas de desempenho, mas a literatura recente enfatiza que custo
computacional, tempo de treino, consumo energético e reprodutibilidade
também devem compor a decisão de adoção (TREVISO *et al.*, 2023;
SCHWARTZ *et al.*, 2020). Treviso *et al.* (2023) argumentam que a
ampliação de escala em PLN tende a aumentar o consumo de dados, tempo,
armazenamento e energia, motivando métodos eficientes especialmente em
contextos de recursos limitados. Schwartz *et al.* (2020) cunharam o
conceito de *Green AI*, propondo que a eficiência computacional seja
reportada e valorizada na avaliação de modelos, não apenas a acurácia.
Em uma instituição pública, essa dimensão é operacionalmente decisiva:
um modelo que treina em segundos pode ser reexecutado frequentemente,
auditado com facilidade e mantido sem infraestrutura dedicada, ao passo
que um modelo que demanda dezenas de minutos exige *checkpoint*,
controle de versão de pesos e justificativa robusta de ganho marginal
(TREVISO *et al.*, 2023).

**3. MÉTODO**

**3.1 Delineamento geral**

O estudo adota delineamento experimental aplicado, com base
observacional retrospectiva de chamados de manutenção predial
registrados no sistema GLPI institucional da UFSB, universidade
multicampi com unidades em Itabuna, Ilhéus, Porto Seguro e Teixeira de
Freitas (MORAIS; PAULA; REIS, 2023). A unidade de análise é o chamado
individual de manutenção, representado por campos textuais concatenados
e por uma categoria histórica registrada no sistema. O fluxo
metodológico compõe-se de oito etapas sequenciais: (i) extração e
consolidação da base; (ii) higienização textual; (iii) construção da
matriz de atributos; (iv) treinamento e inferência multimodelo; (v)
geração de predições *out-of-fold*; (vi) comparação preliminar com
categoria histórica; (vii) análise estatística não paramétrica; e (viii)
validação humana das divergências e amostras críticas. A Figura 1
apresenta esse fluxo como *pipeline* de governança preditiva.

![Figura 1 — Pipeline de governança preditiva: fluxo metodológico completo, da extração da base à retroalimentação por validação humana.](04_artigo/figuras/fig1_pipeline_governanca.png)

**Figura 1** Pipeline de governança preditiva: fluxo metodológico
completo, da extração da base à retroalimentação por validação humana.

Fonte: elaborado pelos autores (2026), a partir do fluxo metodológico descrito nesta subseção.

**3.2 Corpus e variáveis**

O corpus experimental é composto por 13.965 chamados de manutenção
predial não vazios, organizados em 55 categorias históricas, extraídos
do ambiente institucional da UFSB. Os campos textuais previstos no
protocolo incluem título do chamado, descrição GLPI, título da ordem de
serviço e descrição da ordem de serviço, concatenados em uma única
representação textual para fins de classificação. A categoria histórica
é utilizada como referência preliminar de comparação, mas a avaliação
conclusiva depende da base validada por revisão humana. O idioma dos
registros é português brasileiro, com presença significativa de jargões
técnicos, nomes de ambientes, abreviações locais e descrições
incompletas, características que impõem desafios específicos de
pré-processamento e representação textual (SUNDARAM; ZEID, 2025).

A base é dinâmica: novos chamados continuam sendo sincronizados e
classificados em turnos, e a taxonomia institucional pode ser revisada
ao longo do tempo. Os resultados da Seção 4 utilizam sempre o recorte
mais recente disponível; eventuais diferenças frente a consolidações
anteriores refletem o crescimento da base e a ampliação da conferência
humana, não uma mudança metodológica.

**3.3 Pré-processamento textual**

O pré-processamento textual foi documentado de modo reprodutível, uma
vez que pequenas decisões sobre normalização podem alterar a matriz de
atributos e, consequentemente, o desempenho dos modelos (SALTON;
BUCKLEY, 1988). Para os classificadores clássicos, a representação
principal é TF-IDF com *n-gramas* de uma e duas palavras e limite
superior de 5.000 atributos para controle de dimensionalidade. Para o
modelo neural LSTM, são utilizadas tokenizações específicas com
vocabulário de 8.000 termos e comprimento máximo de sequência adequado à
distribuição textual da base. Cabe ressaltar que a etapa de
pré-processamento não elimina indiscriminadamente termos técnicos,
códigos de ambientes, nomes de equipamentos ou expressões recorrentes da
equipe, pois esses elementos possuem alto valor discriminativo em
manutenção predial, onde palavras como *bomba*, *split*, *disjuntor*,
*vazamento*, *infiltração* e *ar-condicionado* podem funcionar como
âncoras semânticas relevantes para categorias específicas.

**3.4 Modelos avaliados**

O desenho experimental compara sete modelos materializados, organizados
em três famílias conceituais, cada uma escolhida por um motivo
específico ligado às características do domínio: texto curto,
vocabulário técnico e forte desbalanceamento entre categorias (Subseção
3.2).

A família **linear** (LinearSVC, Regressão Logística e SGD) opera
diretamente sobre a representação TF-IDF esparsa (Subseção 3.3): em
espaços de alta dimensionalidade, fronteiras lineares tendem a separar
bem as classes quando o vocabulário carrega forte poder discriminativo
(JOACHIMS, 1998; SALTON; BUCKLEY, 1988), como é o caso dos termos
técnicos de manutenção predial, que funcionam como âncoras semânticas de
categoria. A família de **ensembles de árvores** (Random Forest e Extra
Trees) captura interações não lineares entre atributos, a um custo
computacional maior. O **Naive Bayes Multinomial** entra como *baseline*
probabilístico mais simples, útil para calibrar a expectativa de
desempenho mínimo (JOACHIMS, 1998; PEDREGOSA *et al.*, 2011). A **rede
neural** (LSTM Bidirecional) modela dependências sequenciais no texto,
mas, nesta consolidação, treina seus *embeddings* do zero, sem
incorporar vetores pré-treinados em português (GRAVES; SCHMIDHUBER,
2005) — a Subseção 3.4.1 discute por que essa escolha tende a penalizar
o desempenho em corpora de porte médio como o deste estudo. Todos os
sete modelos são avaliados tanto na comparação *out-of-fold* (Subseção
4.1) quanto na Etapa 1 oficial de produção, onde a LSTM opera com
*fallback* para Random Forest quando a base rotulada disponível é
insuficiente.

Um oitavo modelo, o transformador pré-treinado em português BERTimbau,
permanece como extensão planejada: seu ajuste fino depende do avanço da
base validada e, nesta consolidação, o treino ainda não foi concluído —
por isso o modelo não integra tabelas, rankings, testes inferenciais nem
conclusões comparativas deste capítulo.

**3.4.1 Diferenças conceituais e operacionais entre os classificadores**

Os sete modelos comparáveis desta consolidação cobrem quatro famílias
com suposições distintas sobre os dados: um gerador probabilístico
(Naive Bayes), discriminadores lineares (LinearSVC, Regressão Logística,
SGD), *ensembles* não lineares baseados em árvores (Random Forest, Extra
Trees) e uma rede neural sequencial (LSTM). Cada família responde de
forma diferente a um corpus de texto curto, ruidoso e com forte
desbalanceamento entre categorias (Subseção 3.2; Tabela S1), o que ajuda
a explicar por que o desempenho não é uniforme entre elas nas Tabelas 1
e 2.

O **LinearSVC** otimiza uma fronteira de decisão linear por margem
máxima sobre a representação TF-IDF esparsa de até 5.000 atributos
(Subseção 3.3). Em espaços esparsos de alta dimensionalidade, classificadores
lineares tendem a separar bem as classes quando o vocabulário carrega
forte poder discriminativo (JOACHIMS, 1998; SALTON; BUCKLEY, 1988) — como
ocorre aqui, em que termos técnicos do domínio (*bomba*, *split*,
*disjuntor*, *vazamento*, *infiltração*, *ar-condicionado*; Subseção 3.3)
funcionam como âncoras semânticas de categoria. Essa combinação é
consistente com o LinearSVC liderando tanto a concordância com o
histórico (0,8029; Tabela 1) quanto o acerto validado (0,9493; Tabela 2).

O **Naive Bayes** assume independência condicional entre atributos dado
a classe — suposição estrutural que tende a ser violada em texto de
manutenção predial, onde termos técnicos co-ocorrem de forma sistemática
dentro de uma mesma categoria. Essa divergência entre a suposição do
modelo e a estrutura real dos dados é uma explicação plausível para o
Naive Bayes ocupar a última posição tanto na concordância com o
histórico (0,6996; Tabela 1) quanto no acerto validado (0,8609; Tabela
2), sem que isso indique um problema de implementação — é o
comportamento esperado do modelo mais simples da comparação.

**Random Forest** e **Extra Trees** capturam interações não lineares
entre atributos por meio da estrutura de árvores, mas em espaços
esparsos de alta dimensionalidade como o TF-IDF tendem a ajustar-se
demais às co-ocorrências mais frequentes, o que se reflete no desempenho
intermediário de ambos nas Tabelas 1 e 2 (entre o LinearSVC e o Naive
Bayes). O custo computacional dessa família também é o mais alto entre
os modelos clássicos medidos: 19,45 s (Random Forest) e 21,30 s (Extra
Trees) de treino por lote de 1.000 registros, entre 7,6 e 8,4 vezes o
tempo do LinearSVC (2,55 s) e entre 17,1 e 18,7 vezes o do Naive Bayes
(1,14 s) no mesmo lote (Tabela 7) — um custo que só se justifica se
revertido em ganho de acerto validado, o que não se confirma nesta
consolidação (SCHWARTZ *et al.*, 2020; TREVISO *et al.*, 2023).

A **LSTM Bidirecional** foi projetada para modelar dependências
sequenciais no texto, mas nesta consolidação seus *embeddings* são
inicializados aleatoriamente e treinados do zero — não há incorporação
de vetores pré-treinados em português. A camada de *embedding* (8.000 termos × 128
dimensões) concentra sozinha cerca de 1,02 milhão de parâmetros, uma
ordem de grandeza próxima do número de exemplos disponíveis por
partição de treino nesta consolidação (13.965 chamados, dos quais cerca
de 11.172 compõem cada partição de treino em `k=5` *folds*; Subseção
3.5) — um cenário consistente com a hipótese de que modelos lineares
tendem a igualar ou superar redes neurais em corpora de porte médio e
ruidosos quando não há *embeddings* pré-treinados disponíveis no idioma
(GALKE; SCHERP, 2022), sem que isso configure uma falha da arquitetura
em si (Subseção 4.9 detalha a investigação da discrepância do *ablation*
do LSTM).

Na Etapa 1 oficial de produção — distinta da comparação *out-of-fold*
desta seção —, o mecanismo de *fallback* opera no nível da base de
treino, não por chamado individual: a LSTM só é treinada quando a base
rotulada disponível atinge um mínimo de 200 exemplos; abaixo desse
limiar, um classificador Random Forest sobre TF-IDF é usado no lugar da
rede neural para toda a base naquele momento. Um segundo critério, sem
relação com essa troca de modelo, classifica a confiança de cada
predição em três faixas (abaixo de 70%, entre 70% e 95%, acima de 95%),
usadas para priorização de conferência humana e para as métricas de
calibração da Subseção 4.4.

**3.5 Desenho de avaliação**

A avaliação foi realizada por predições fora da amostra em protocolo
*out-of-fold* com *KFold* embaralhado (5 partições, semente fixa) e
mesma partição determinística para todos os modelos. A partição não é
estratificada; esta é uma limitação do desenho implementado. O
procedimento reduz viés de comparação e permite testes pareados
(SOKOLOVA; LAPALME, 2009). As métricas principais são
acurácia, *macro*-F1, F1 ponderado, *balanced accuracy* e intervalo de
confiança por *bootstrap* — reamostragem com reposição para estimar a
distribuição de uma estatística sem pressupor sua forma paramétrica
(EFRON, 1979; EFRON; TIBSHIRANI, 1993), cuja variedade de métodos de
construção de intervalo (percentil, BCa, bootstrap-*t*) e respectivas
propriedades de cobertura é revisada em detalhe por DiCiccio e Efron
(1996) — com 95% de confiança.

A *macro*-F1 e a *balanced accuracy* são essenciais face ao
desbalanceamento entre categorias, dado que a acurácia isolada pode
superestimar desempenho em classes majoritárias e mascarar falhas em
categorias raras (SOKOLOVA; LAPALME, 2009). A correlação entre confiança
e acerto é avaliada por Spearman (SPEARMAN, 1904) e por correlação
ponto-bisserial, apropriada quando uma das variáveis é binária
(TATE, 1954); diferenças globais entre os sete classificadores são
avaliadas por Cochran Q, teste não paramétrico para proporções pareadas
em três ou mais condições (COCHRAN, 1950), e por Friedman, teste baseado
em postos que dispensa o pressuposto de normalidade da ANOVA
(FRIEDMAN, 1937); comparações pareadas são avaliadas por McNemar
(MCNEMAR, 1947); e incerteza de acurácia é estimada por *bootstrap*
(EFRON, 1979), abordagem cuja utilidade para intervalos de confiança de
métricas de modelos preditivos continua sendo estudada e refinada
recentemente (NOMA *et al.*, 2021).

Quando múltiplas comparações são
realizadas, aplica-se o teste de Nemenyi sobre os postos médios
(NEMENYI, 1963), seguindo o protocolo consolidado por Demšar (2006) para
comparação estatística de classificadores em múltiplos conjuntos de
dados — protocolo cujas limitações já foram apontadas por trabalho mais
recente: Benavoli, Corani e Mangili (2016) mostram que o teste de
postos médios (base do Nemenyi) pode ser inconsistente e recomendam
testes pareados diretos como complemento, razão pela qual este trabalho
também reporta o McNemar par a par (Subseção 4.10) em vez de depender
apenas do Nemenyi; comparações pareadas adicionais entre os sete modelos
são corrigidas pelo método sequencial de Holm-Bonferroni, que controla a
taxa de erro familiar sem o conservadorismo excessivo da correção de
Bonferroni simples (HOLM, 1979).

**Escolha entre validação cruzada e *holdout* fixo**: optou-se
deliberadamente por *k-fold out-of-fold* em vez de um conjunto de teste
fixo separado antes do treino. A literatura de avaliação de modelos
indica que a validação cruzada tende a produzir estimativas de menor
variância que um único *holdout*, sobretudo em bases pequenas ou
desbalanceadas, precisamente por avaliar cada exemplo em algum *fold* em
vez de descartar uma fração fixa dos dados do treino (KOHAVI, 1995) — e
esta base é desbalanceada por natureza, com várias das 55 categorias
históricas tendo suporte de dígito único (Tabela Suplementar S1).

Essa recomendação foi verificada empiricamente, não apenas invocada em
abstrato: comparou-se o protocolo *k*-fold com um *holdout* fixo de 15%
sobre os sete modelos comparáveis e a mesma base completa. A tentativa
de estratificar esse *holdout* por categoria — prática padrão na
maioria dos protocolos — falhou de imediato, pois a base tem categorias
com um único exemplo; no *holdout* aleatório que a substituiu, várias
categorias raras ficaram sem nenhum exemplo de teste, tornando sua
métrica de desempenho indefinida, um problema que o *k*-fold evita por
avaliar todo exemplo em algum *fold* (Tabela Suplementar S1). A
acurácia global variou pouco entre os dois protocolos, mas a
*macro*-F1 — que pondera todas as categorias igualmente, e não apenas
as mais frequentes — piorou no *holdout* na maioria dos modelos
(detalhamento completo na Tabela Suplementar S4). Em suma, um *holdout*
fixo não melhora a estimativa de desempenho global nesta base e piora
sistematicamente a avaliação das categorias raras — o padrão que a
literatura antecipa para corpora pequenos e desbalanceados como este
(KOHAVI, 1995), confirmando o *k*-fold como a escolha metodologicamente
mais adequada, não apenas a mais conveniente.

**3.6 Validação humana**

A validação humana constitui a etapa que diferencia o presente estudo de
uma simples comparação de classificadores contra histórico. A revisão
registra, para cada caso auditado, a categoria histórica, a categoria
sugerida por cada modelo, a confiança associada, a decisão humana e a
categoria travada. A priorização recai sobre chamados em que há
divergência entre modelos, alta confiança da IA contra histórico, baixa
confiança generalizada, classes raras e pares de categorias com alta
confusão recíproca. A decisão humana pode produzir quatro resultados:
manter o histórico; aceitar a sugestão do modelo; definir terceira
categoria; ou marcar o caso como ambíguo ou taxonômico. Essa estrutura
permite mensurar se a IA errou, se o histórico estava inconsistente ou
se a própria taxonomia institucional necessita de revisão, em
consonância com a perspectiva de que a verdade operacional deve ser
construída progressivamente (ZHANG *et al.*, 2025).

**3.7 Memória de decisão: veto e trava por chamado**

À medida que a conferência humana avança, o protocolo incorpora uma
memória de decisão por chamado, que evita o reprocessamento de casos já
resolvidos e impede a repetição de erros já identificados. Quando a
conferência confirma que uma categoria está correta, essa decisão é
travada e reaproveitada diretamente nas rodadas seguintes de
reclassificação, sem novo treinamento ou nova predição para aquele
chamado. Quando a conferência identifica que uma categoria está
incorreta, essa categoria passa a ser vetada especificamente para aquele
chamado: os modelos do repositório de classificadores passam a escolher
a melhor categoria alternativa fora do conjunto vetado, com a confiança
renormalizada sobre as categorias remanescentes. Essa regra é aplicada
de forma consistente na seleção de candidatos à reclassificação e no
cálculo do ganho líquido, que passa a comparar o resultado da
reclassificação contra a verdade validada quando ela está travada, e
contra o histórico apenas quando ainda não há decisão humana. O objetivo
metodológico da memória de decisão é impedir que o sistema corrija um
erro apenas para reincidir nele em ciclos futuros, convertendo cada
conferência manual em conhecimento persistente sobre o experimento, não
em um evento isolado.

**3.8 Camada de entropia de Shannon e divergência de Jensen-Shannon**

Como dimensão complementar às métricas supervisionadas, o protocolo
incorporou uma camada de análise informacional baseada em entropia de
Shannon e divergência de Jensen-Shannon (SHANNON, 1948; LIN, 1991), calculada exclusivamente sobre
os arquivos públicos e sanitizados do painel (sem identificador, título
ou texto livre do chamado). Essa camada não substitui acurácia,
calibração ou validação humana; responde a uma pergunta distinta, sobre
onde modelos, categorias e chamados individuais concentram maior
incerteza estrutural. No nível dos modelos, a entropia de Shannon sobre
a distribuição de categorias previstas indica se um classificador
dispersa suas predições por muitas classes ou as concentra
excessivamente em poucas; a divergência de Jensen-Shannon mede a
distância entre essa distribuição prevista e a distribuição histórica da
base, funcionando como indicador de deslocamento distributivo. No nível
das categorias, a entropia evidencia classes históricas cujas predições
se espalham entre múltiplas categorias, sinalizando candidatas
prioritárias a revisão taxonômica. No nível do chamado individual, a
entropia de votos entre os modelos identifica registros em que há
desacordo estrutural entre arquiteturas distintas, formando uma fila de
auditoria orientada por ambiguidade, e não apenas por baixa confiança
isolada de um único modelo.

**3.9 Disponibilidade de dados e scripts**

Os artefatos que sustentam os resultados relatados neste capítulo são
gerados por um pipeline automatizado, reproduzido a cada nova
consolidação do experimento. Nenhum identificador pessoal, título ou
texto livre de chamado é armazenado nos agregados publicados; a camada
Shannon/Jensen-Shannon (Subseção 3.8) opera exclusivamente sobre
agregados sanitizados.

**4. RESULTADOS**

Esta seção apresenta dois conjuntos de resultados, deliberadamente
segregados: a concordância com a categoria histórica (Subseção 4.1), que
trata o registro do GLPI como referência preliminar, e o desempenho validado
por conferência humana (Subseções 4.2 e 4.3). A base elegível contém
13.965 chamados; a conferência humana cobre 9.534
chamados (68,3% da base), dos quais 9.044 têm
decisão travada (64,8% da base). Os 490
casos restantes não possuem verdade validada; esse conjunto inclui
52 conflitos entre fontes conferidas.

Três achados resumem esta seção. Primeiro, os classificadores lineares,
liderados pelo LinearSVC, superam os ensembles de árvores e a rede neural
LSTM em concordância e acerto validado, com vantagem adicional de custo
computacional. Segundo, a validação humana confirma ruído real no rótulo
histórico, justificando a conferência dupla. Terceiro, a faixa de confiança
igual ou superior a 95% supera a meta de 95% de acerto validado na amostra
conferida, mas a confiança permanece bruta e a seleção da amostra não é
probabilística.

**4.1 Concordância com o histórico (base completa)**

A comparação contra a categoria histórica, sobre a base completa (n = 13.965), mantém o LinearSVC na liderança, com acurácia de 0,8031 (IC95%: 0,7963--0,8097), seguido por Extra Trees (0,7894), Random Forest (0,7816), SGD (0,7767), Regressão Logística (0,7682), Naive Bayes (0,6997) e LSTM (0,6718), O teste de Cochran Q confirma diferença global entre os sete modelos (Q = 2984,066; p < 0,001). O BERTimbau permanece excluído por não possuir treino concluído.

**Tabela 1** Concordância com a categoria histórica, base completa (n = 13.965)

| Modelo | Acurácia | IC95% bootstrap | Kappa vs. histórico |
|---|---|---|---|
| LinearSVC | 0,8031 | 0,7963 -- 0,8097 | 0,7881 |
| Extra Trees | 0,7894 | 0,7825 -- 0,7961 | 0,7716 |
| Random Forest | 0,7816 | 0,7749 -- 0,7881 | 0,7630 |
| SGD | 0,7767 | 0,7700 -- 0,7835 | 0,7604 |
| Regressão Logística | 0,7682 | 0,7613 -- 0,7751 | 0,7518 |
| Naive Bayes | 0,6997 | 0,6923 -- 0,7071 | 0,6705 |
| LSTM (out-of-fold) | 0,6718 | 0,6637 -- 0,6796 | 0,6496 |

Fonte: elaborado pelos autores (2026), com base nos agregados vigentes da comparação multimodelo.

A concordância com o histórico não é uniforme entre as 55 categorias. A
Tabela Suplementar S1 reporta suporte, precisão, revocação e F1-Score
por categoria. As cinco categorias
com menor F1 são Elétrica > Sistema Fotovoltaico (FV) (F1 = 0,0000; suporte
= 7), Manutenção Preventiva sem subcategoria (F1 = 0,0000; suporte = 2),
Estrutura Predial > Instalações Especiais (gás, ar comprimido, etc.) (F1 =
0,0732; suporte = 3), Suprimentos / Apoio Técnico > Transporte (F1 = 0,1053;
suporte = 1) e Área Externa e Ambiental > Drenagem (F1 = 0,1333; suporte =
3). As cinco categorias com maior F1 são Manutenção Preventiva > Extintor
(F1 = 1,0000; suporte = 14), Manutenção Preventiva > Gerador (F1 = 0,9908;
suporte = 1.211), Manutenção Preventiva > Sistemas de combate a incêndio
(extintores, hidrantes) (F1 = 0,9890; suporte = 45), Manutenção Preventiva >
Quadros Elétricos (F1 = 0,9869; suporte = 576) e Manutenção Preventiva > Ar
condicionado central (F1 = 0,9849; suporte = 165). A leitura das categorias
de menor F1 deve ser cautelosa porque quatro das cinco têm suporte menor ou
igual a sete registros; nesses casos, uma pequena variação absoluta altera
fortemente a métrica.

**4.2 Ranking validado por conferência humana**

A avaliação contra a verdade validada pela memória de decisão M/N/P
(n = 9.044) mantém a liderança do LinearSVC,
com acerto validado de 0,9502 (IC95%:
0,9458--0,9546). A ordenação completa é
LinearSVC (95,02%), SGD (94,11%), Regressão Logística (93,71%), Extra Trees (92,86%), Random Forest (92,41%), LSTM (88,11%) e Naive Bayes (86,27%). A diferença entre o primeiro e o segundo
colocado é de 0,91%, com McNemar p =
5.696e-08. Os ensembles avaliados foram maioria ponderada (0,9467), confianca calibrada max (0,9458), maioria simples (0,9445); nenhum
supera o LinearSVC isolado. A recomendação permanece utilizar o LinearSVC com
calibração, sem combinar modelos nesta consolidação.

**Viés estrutural da seleção da amostra validada**: a verdade validada só
existe quando ao menos uma fonte conferida é confirmada como correta. Dos
9.534 chamados com alguma conferência, 490
não possuem categoria de referência, incluindo 52 conflitos.
Por isso, o acerto validado é apresentado como limite superior, acompanhado de
um limite inferior conservador que inclui todos esses casos no denominador como
erros. A amplitude varia de 4,43% a 4,88%, sem
alterar o ranking relativo dos sete modelos.

**Tabela 2** Acerto validado contra a verdade decidida M/N/P
(n = 9.044) e intervalo de sensibilidade

| Modelo | Acerto validado (limite superior) | IC95% | Limite inferior (pior caso) |
|---|---|---|---|
| LinearSVC | 0,9502 | 0,9458 -- 0,9546 | 0,9014 |
| SGD | 0,9411 | 0,9363 -- 0,9459 | 0,8927 |
| Regressão Logística | 0,9371 | 0,9321 -- 0,9421 | 0,8889 |
| Extra Trees | 0,9286 | 0,9234 -- 0,9335 | 0,8808 |
| Random Forest | 0,9241 | 0,9186 -- 0,9295 | 0,8767 |
| LSTM | 0,8811 | 0,8743 -- 0,8880 | 0,8359 |
| Naive Bayes | 0,8627 | 0,8558 -- 0,8696 | 0,8183 |

Fonte: elaborado pelos autores (2026). O limite inferior é uma análise de pior
caso; os conflitos e demais linhas sem verdade validada não recebem crédito para
nenhum modelo.

A rematerialização completa também resolveu uma discrepância antes
registrada entre o *ablation study* do LSTM (Subseção 4.9,
86,35%--87,68% conforme o particionamento) e o valor oficial então
vigente: o valor antigo vinha de uma materialização desatualizada; o
valor oficial atual do LSTM (0,8790) está muito mais próximo do que o
*ablation* já indicava. Isso confirma que o *ablation* nunca teve um
problema metodológico de vazamento residual relevante — a discrepância
vinha da defasagem temporal da materialização de referência, não de uma
falha do *ablation* em si; a ressalva de "resultado suspeito" da Figura
6 é mantida apenas como registro histórico da investigação, não como
pendência ativa.

O patamar de acerto validado mudou de magnitude ao longo de
consolidações sucessivas deste protocolo, por dois motivos distintos:
primeiro, o crescimento genuíno da amostra validada revelou uma taxa de
acerto real mais conservadora do que amostras menores — mais
concentradas em casos fáceis de confirmar — sugeriam; segundo, uma
materialização desatualizada dos modelos, já corrigida, havia
subestimado o desempenho real numa consolidação intermediária. Como a
seleção da conferência humana não é probabilística, a comparação entre
consolidações continua sendo descritiva, não inferencial (COCHRAN,
1977); não é possível estimar, a partir dela, o desempenho da base
completa.

**4.3 A classificação oficial frente ao histórico: matriz de confusão
validada**

A classificação oficial e a categoria histórica foram comparadas contra a
mesma verdade validada em 9.044 decisões. O histórico coincide
com a decisão em 99,90%, enquanto a IA oficial coincide em
93,72%. A matriz contém 8.476
casos em que ambos acertam, 9 em que ambos
divergem da decisão, 559 em que o histórico
acerta e a IA erra e 0 em que a IA corrige o
histórico.

**Tabela 4** Matriz de confusão IA × histórico contra a verdade decidida
(M/N/P) (n = 9.044)

| | Histórico correto | Histórico incorreto |
|---|---|---|
| **IA correta** | 8.476 | 0 |
| **IA incorreta** | 559 | 9 |

Fonte: elaborado pelos autores (2026), usando a mesma verdade decidida da
Subseção 4.2.

**4.4 Confiança, calibração e faixas de decisão**

A calibração bruta da Etapa 1 oficial apresenta ECE histórico de
0,0656. Na faixa igual ou superior a 95% de
confiança (n = 4.810), a concordância com o histórico é de
98,75% e o acerto validado alcança
99,94% sobre 4.675 decisões.
A confiança permanece bruta, sem Platt, isotônica ou *temperature scaling*;
portanto, a meta deve ser interpretada como diagnóstico da amostra conferida.

**Tabela 3** Acerto validado por faixa de confiança bruta, executor oficial

| Faixa | n total | Concord. histórico | n validados | Acerto validado |
|---|---|---|---|---|
| <50% | 4.058 | 43,05% | 880 | 51,93% |
| 50-70% | 1.443 | 75,12% | 712 | 87,50% |
| 70-80% | 946 | 87,10% | 653 | 96,78% |
| 80-90% | 1.484 | 82,82% | 1.065 | 97,84% |
| 90-95% | 1.224 | 95,59% | 1.059 | 99,15% |
| >= 95% | 4.810 | 98,75% | 4.675 | 99,94% |

Fonte: elaborado pelos autores (2026). O snapshot foi deduplicado por
`linha_planilha`, mantendo a ocorrência mais recente. A amostra de conferência
não é probabilística.

**4.5 Reclassificação e ganho líquido**

A reclassificação dos chamados já conferidos produz resultados
heterogêneos entre modelos, medidos contra a verdade validada quando
travada e contra o histórico nos demais casos. Nesta consolidação, o
LSTM apresenta o maior ganho líquido absoluto (+99; 670 corrigidos e
571 prejudicados), seguido por Regressão Logística (+92) e LinearSVC
(+73); todos os sete modelos materializados apresentam ganho líquido
positivo. Esse resultado não autoriza aplicação indiscriminada: o ganho
combina parcelas comparadas contra verdade validada e contra histórico,
e já mudou de sinal para alguns modelos entre consolidações anteriores
e esta. Reforça-se, portanto, a decisão de não aplicar reclassificação
em massa por modelo, tratando o ganho líquido — e não apenas a acurácia
agregada — como critério de decisão operacional a ser reavaliado a cada
consolidação, não como veredito permanente sobre um classificador.

**Tabela 5** Ganho líquido de reclassificação por modelo

| Modelo | Total reclassificado | Corrigidos | Prejudicados | Ganho líquido | Reuso de decisão humana |
|---|---|---|---|---|---|
| LSTM | 13.905 | 670 | 571 | +99 | 8.805 |
| Regressão Logística | 13.932 | 245 | 153 | +92 | 8.727 |
| LinearSVC | 13.965 | 291 | 218 | +73 | 8.856 |
| Random Forest | 13.912 | 234 | 186 | +48 | 8.719 |
| SGD | 13.965 | 201 | 163 | +38 | 8.771 |
| Naive Bayes | 13.826 | 158 | 132 | +26 | 8.623 |
| Extra Trees | 13.899 | 237 | 226 | +11 | 8.713 |

Fonte: elaborado pelos autores (2026). *Nota metodológica*: o total
reclassificado do Random Forest chegava a 18.049 nesta mesma tabela em
versão anterior deste texto, valor que excedia o
tamanho da base (13.965) — matematicamente impossível sob a premissa de
uma linha por chamado. Um diagnóstico direto identificou 4.737 linhas
duplicadas, concentradas no registro do Random Forest, enquanto o
registro de referência (LinearSVC) não apresentou nenhuma duplicata —
descartando erro de leitura genérico e localizando o problema
especificamente nesse modelo. A causa raiz foi uma reenvio integral de
lote após erro transitório de API de escrita, sem confirmação prévia de
que o envio anterior já havia sido aceito; a agregação foi corrigida
para deduplicar por identificador antes de contar, mantendo a última
ocorrência. Os números atuais já refletem a remoção das 4.737 linhas
duplicadas históricas.

**4.6 Diagnóstico de taxonomia e ambiguidade estrutural
(Shannon/Jensen-Shannon)**

O diagnóstico de Shannon foi recalculado sobre oito fontes comparáveis:
a Etapa 1 oficial e os sete modelos materializados. O BERTimbau foi
excluído por não ter treino concluído. A Etapa 1 oficial apresenta a
maior diversidade de categorias previstas e a menor divergência de
Jensen-Shannon frente à distribuição histórica. No nível de chamado
individual, 3.277 dos 13.965 registros (23,5%) apresentam alta entropia
de votos entre as oito fontes, ou seja, desacordo estrutural relevante
entre arquiteturas distintas — um critério de priorização de auditoria
diferente e complementar à simples baixa confiança de um único modelo.

No nível de categoria, a análise aponta 76 ocorrências de alta
ambiguidade nas predições (com suporte mínimo de 30 registros por
categoria); a interpretação detalhada de quais categorias específicas
concentram essa ambiguidade, e sua sobreposição com os pares de maior
confusão recíproca identificados na etapa de cruzamento de taxonomia,
permanece como candidata a inspeção qualitativa dirigida futura. O que
a camada Shannon oferece é a priorização estatística de onde essa
inspeção deve começar, não a decisão de fusão ou desambiguação de
categorias, que continua sendo humana. Naive Bayes chama atenção por
combinar a menor cobertura de
categorias (19, ante 47–53 dos demais modelos) com entropia normalizada
relativamente alta (0,7848) — provável reflexo de concentração extrema
em poucas categorias com alguma dispersão residual, não investigado em
detalhe neste capítulo.

**Tabela 6** Entropia de Shannon e divergência de Jensen-Shannon por fonte de classificação

| Fonte | Categorias previstas | Entropia (nats) | Entropia normalizada | JS vs. histórico |
|---|---|---|---|---|
| Etapa 1 oficial | 53 | 4,6758 | 0,8163 | 0,0286 |
| LSTM | 52 | 4,6201 | 0,8105 | 0,0847 |
| Regressão Logística | 52 | 4,4490 | 0,7805 | 0,0716 |
| SGD | 53 | 4,4363 | 0,7745 | 0,0639 |
| LinearSVC | 53 | 4,3356 | 0,7569 | 0,0575 |
| Extra Trees | 47 | 3,9955 | 0,7193 | 0,0761 |
| Random Forest | 47 | 3,9574 | 0,7124 | 0,0804 |
| Naive Bayes | 19 | 3,3340 | 0,7848 | 0,1755 |

Fonte: elaborado pelos autores (2026). O BERTimbau foi excluído
explicitamente por não haver treino concluído. No nível de categoria, o
resumo aponta 76 ocorrências de alta ambiguidade e 3.277 chamados com
alta entropia de votos entre modelos.

**4.7 Custo computacional**

Nos recortes de comparação por lote (1.000 registros cada), os seis
modelos clássicos tiveram tempos de treino entre 1,14 s e 21,30 s.
Não há medição comparável de custo para LSTM ou BERTimbau nesta
consolidação; portanto, não é possível ordenar o custo desses dois
modelos frente aos demais. A tabela informa exclusivamente as medições
disponíveis para os modelos clássicos.

**Tabela 7** Custo computacional por lote de 1.000 registros

| Modelo | Tempo de treino (s) | Tempo de inferência (s) | Acurácia neste lote |
|---|---|---|---|
| Naive Bayes | 1,14 | 0,07 | 0,539 |
| LinearSVC | 2,55 | 0,06 | 0,655 |
| SGD | 2,60 | 0,09 | 0,624 |
| Regressão Logística | 9,43 | 0,09 | 0,624 |
| Random Forest | 19,45 | 0,13 | 0,597 |
| Extra Trees | 21,30 | 0,14 | 0,610 |

Fonte: elaborado pelos autores (2026), execução mais recente por modelo
disponível — não reexecutada nesta consolidação; único registro de
custo computacional disponível para os modelos clássicos. LSTM
e BERTimbau não constam deste arquivo. A acurácia
reportada aqui é sobre um lote de 1.000 registros (não a base completa) e
serve só para contextualizar o trade-off custo×desempenho desta subseção —
não usar como substituto das Tabelas 1 e 2.

**4.8 Figuras**

As figuras foram geradas a partir dos dados vigentes do painel público e
dos registros de treino de cada modelo. A Figura 4 usa códigos de
categoria para preservar a legibilidade; o mapeamento completo
código-categoria está na Tabela Suplementar S2.

![Figura 2 — Confiança bruta × concordância com o histórico × acerto validado, por faixa de confiança (executor oficial, Etapa 1).](04_artigo/figuras/fig2_confianca_desfecho.png)

**Figura 2** Confiança bruta × concordância com o histórico × acerto validado,
por faixa de confiança (executor oficial, Etapa 1). Mesmos números da
Tabela 3 (Subseção 4.4), em forma gráfica.

Fonte: elaborado pelos autores (2026).

![Figura 3 — Trade-off entre acerto validado e custo computacional (tempo de treino), modelos clássicos.](04_artigo/figuras/fig3_tradeoff_custo.png)

**Figura 3** Trade-off entre acerto validado (conferência humana) e custo
computacional (tempo de treino, lote de 1.000 registros), modelos
clássicos. LSTM e BERTimbau não constam desta figura por não terem
registro de tempo de treino no mesmo arquivo (Tabela 7, Subseção 4.7).

Fonte: elaborado pelos autores (2026), cruzando custo computacional e
acerto validado.

![Figura 4 — Top 15 pares de maior confusão entre categorias, agregados a partir dos top pares por modelo.](04_artigo/figuras/fig4_top_confusoes.png)

**Figura 4** Top 15 pares de maior confusão entre categorias. O par mais recorrente
foi `Climatização > Ar condicionado` → `Manutenção Preventiva > Ar
condicionado split` (1.310 ocorrências agregadas), seguido por `Instalação de
Acessórios e Mobiliário > Instalação/reparo de equipamentos (Suportes de TV,
acessórios de banheiro e quadro branco)` → `Estrutura Predial > Alvenaria /
Pisos / Estrutura` (799) e `Estrutura Predial > Alvenaria / Pisos / Estrutura`
→ `Estrutura Predial > Esquadrias, porta, portão e janelas` (726). Os códigos
C01-C10 usados no eixo vertical são descritos na Tabela Suplementar S2.

Fonte: elaborado pelos autores (2026).

![Figura 5 — Curva de aprendizado do LSTM por época.](04_artigo/figuras/fig5_curva_aprendizado_lstm.png)

**Figura 5** Curva real de aprendizado do LSTM, com 13.965 exemplos e 53
categorias. O treino foi interrompido
por `EarlyStopping` após 11 épocas. O menor `val_loss` ocorreu na época 8
(`val_loss = 1,4374`; `accuracy = 0,7073`; `val_accuracy = 0,6492`), enquanto o
maior `val_accuracy` ocorreu na época 10 (`val_accuracy = 0,6722`;
`val_loss = 1,4767`).

Fonte: elaborado pelos autores (2026).

![Figura 6 — Ablation study do LSTM: unidades recorrentes e dropout.](04_artigo/figuras/fig6_ablation_lstm.png)

**Figura 6** Ablation study do LSTM: quatro variantes de unidades
recorrentes (64/128) e *dropout* (0,3/0,5), avaliadas por `GroupKFold`
contra a verdade validada humana. Discussão completa da investigação da
discrepância deste *ablation* na Subseção 4.9.

Fonte: elaborado pelos autores (2026).

**4.9 Investigação da discrepância do *ablation* do LSTM**

Uma auditoria investigou por que o *ablation* da Figura 6 reportava
acerto validado muito acima do valor oficial então vigente para a mesma
arquitetura do LSTM. Duas causas foram identificadas. Primeiro, um
vazamento metodológico real, mas de magnitude modesta: no *KFold*
aleatório por linha usado originalmente, 4.250 de 9.096 linhas
validadas de teste (46,72%) tinham duplicata textual normalizada no
treino. O *ablation* foi refeito com *GroupKFold* por hash de texto
normalizado, excluindo do treino grupos textuais presentes no teste —
isso reduziu a configuração atual (64 unidades, *dropout* de 0,5) de
87,68% para 86,35% (7.854/9.096), uma correção pequena (1,33 ponto
percentual). Segundo, e principal: o valor oficial de referência usado na comparação
(0,7471, Subseção 4.2) vinha de uma materialização desatualizada em
relação à base viva. A rematerialização completa dos sete modelos (ver
Subseção 4.2) produziu um novo valor oficial do LSTM de 0,8790 — muito
mais próximo dos 0,8635 deste *ablation* corrigido (diferença residual
de 1,55 pontos percentuais, plausivelmente atribuível a diferenças
remanescentes de protocolo entre o número de *folds* e o esquema de
treino usados em cada avaliação).

**Conclusão**: o *ablation* nunca teve um problema metodológico grave; a
maior parte da discrepância original vinha de comparar um resultado
fresco com uma referência oficial desatualizada. A ordenação relativa
das quatro variantes testadas — variando número de unidades recorrentes
e taxa de *dropout* — é interpretada como evidência preliminar de baixa
sensibilidade do LSTM a esses hiperparâmetros nesta base (diferença
total entre a melhor e a pior variante inferior a 4 pontos percentuais),
não como indicação forte de que a arquitetura atual esteja
subotimizada.

Fonte: elaborado pelos autores (2026).

**4.10 Robustez estatística: pressupostos e testes de sensibilidade**

Antes de qualquer teste inferencial, verificamos os pressupostos de
robustez estatística usuais — outliers, homogeneidade de variância,
normalidade, desbalanceamento entre categorias, colinearidade entre
modelos, relação entre confiança e acerto, e independência das
observações —, adaptando o protocolo de exploração de dados de Zuur,
Ieno e Elphick (2010) da resposta contínua da ecologia para a resposta
categórica de classificação de chamados (n = 13.965). O teste de
Shapiro-Wilk (SHAPIRO; WILK, 1965) rejeita a normalidade a 5% para os
sete modelos sobre a concordância por turno, confirmando com números a
justificativa não paramétrica já adotada na Subseção 3.5; a variância de
confiança entre modelos também é fortemente heterogênea, reforçando essa
escolha. O teste de Friedman (FRIEDMAN, 1937) confirma diferença global
entre os modelos comparáveis, e o *post-hoc* de Nemenyi (NEMENYI, 1963)
reproduz a mesma ordem das Tabelas 1 e 2, com poder estatístico menor que
o McNemar par a par (MCNEMAR, 1947) — que, corrigido por
Holm-Bonferroni (HOLM, 1979), é significativo em praticamente todas as
21 comparações entre os sete modelos, confirmando que o **LinearSVC é
estatisticamente superior ao LSTM e ao Naive Bayes** (a única exceção,
sem significância, é o par SGD vs. Random Forest). A verificação de
colinearidade mostra um efeito colateral relevante: quatro dos sete
modelos têm confiança altamente correlacionada entre si (Fator de
Inflação de Variância elevado; MARQUARDT, 1970), o que ajuda a explicar
por que nenhum *ensemble* supera o LinearSVC isolado (Subseção 4.2) —
modelos redundantes contribuem pouco em informação independente a um
comitê (DIETTERICH, 2000). A correlação entre confiança bruta e acerto é
positiva e significativa em todos os sete modelos (Spearman e
ponto-bisserial, *p* < 0,001), pré-requisito para a calibração discutida
na Subseção 4.4 (GUO *et al.*, 2017). A verificação completa dos oito
pressupostos, item a item, com as tabelas de correlação, autocorrelação
e o Kappa de Fleiss entre modelos, está disponível como Material
Suplementar.

**5. DISCUSSÃO**

A comparação entre concordância histórica e desempenho validado mantém o
LinearSVC na liderança: 95,02% de acerto validado na
amostra decidida e 80,31% de concordância com o histórico.
A conferência humana não é aleatória e prioriza divergências e casos críticos;
assim, os resultados descrevem a amostra conferida, não a população completa
(COCHRAN, 1977).

A regra de decisão exclui do denominador os 490 chamados sem
verdade validada (5,14% dos conferidos), conjunto que
inclui 52 conflitos. A análise de sensibilidade mantém o
ranking dos sete modelos, mas mostra que o valor pontual de acerto validado é
um limite superior e não deve ser comparado isoladamente a benchmarks externos.

Ainda assim, a distinção entre concordância e acerto validado continua
metodologicamente necessária, e a matriz IA×histórico (Subseção 4.3)
mostra por quê: quando os dois discordam da decisão final, o histórico
está correto com frequência muito maior (577 casos) do que a IA corrige
um erro genuíno do histórico (0 casos nesta consolidação — com a ressalva
estrutural já registrada na Subseção 4.3 sobre essa célula específica).
Esse achado não invalida a premissa metodológica de que a categoria
histórica não deve ser tratada como verdade absoluta — ainda existe uma
taxa real de erro confirmado no registro original (3,51% dos casos
conferidos nesta consolidação, bem acima do observado em consolidações
anteriores com amostra menor, o que por si só recomenda cautela contra
tratar mesmo esse número como estabilizado) —, mas recomenda cautela
contra a leitura
oposta e igualmente equivocada, de que baixa concordância com o
histórico implica automaticamente acerto da IA. A validação humana,
portanto, cumpre função insubstituível: sem ela, seria impossível
distinguir as duas situações apenas observando a taxa de concordância —
e, como o achado acima demonstra, seria impossível também saber se uma
amostra de validação já é grande o bastante para ser tratada como
representativa.

Na amostra conferida, o LinearSVC lidera tanto a concordância histórica
quanto o acerto validado (Subseções 4.1 e 4.2). Isso descreve o resultado
desta base e desta amostra, sem demonstrar superioridade generalizável
de classificadores lineares sobre arquiteturas neurais. A comparação de
custo também permanece restrita aos seis modelos clássicos da Tabela 7.
Os três ensembles avaliados não superam o LinearSVC isolado; a recomendação é manter o classificador linear com calibração.

O resultado da reclassificação (Subseção 4.5) deve ser interpretado por modelo e por consolidação. Todos os modelos apresentam ganho líquido positivo (Naive Bayes, Regressão Logística, LinearSVC, SGD, Extra Trees, Random Forest, LSTM). O ganho combina comparações contra verdade validada e contra histórico; por isso, não autoriza reclassificação indiscriminada nem constitui veredito permanente sobre um classificador.

A camada de entropia de Shannon e divergência de Jensen-Shannon
(Subseção 4.6) não substitui as métricas supervisionadas ou a validação
humana, mas amplia o repertório de governança do experimento ao separar
três fenômenos que a acurácia isolada tende a confundir: erro de modelo,
ambiguidade genuína da taxonomia institucional e heterogeneidade natural
da distribuição de chamados. A identificação de 3.277 chamados (23,5% da
base) com alto desacordo estrutural entre as oito fontes comparáveis
(Etapa 1 oficial e os sete modelos materializados) oferece um critério de
priorização de auditoria distinto do simples corte por baixa confiança
de um único classificador, e complementa a fila já construída a partir
da conferência M/N/P. O achado de que a Etapa 1 oficial, não o LSTM
isolado, lidera tanto a diversidade de predições quanto a menor
divergência frente ao histórico (Subseção 4.6) descreve o resultado
desta consolidação. Esse diagnóstico não substitui acurácia ou validação
humana.

A faixa igual ou superior a 95% de confiança da Etapa 1 oficial alcança
99,94% de acerto validado sobre
4.675 decisões. O resultado supera a meta nominal de
95% nesta amostra, mas não encerra a validação: a confiança é bruta e
4.921 chamados (35,2% da base) ainda
não possuem decisão travada.

**Limitações**

As limitações deste estudo organizam-se em três dimensões.

Quanto à cobertura, os dados provêm de uma única instituição federal de
ensino superior, com textos em português brasileiro e taxonomia
institucional própria; a generalização do desempenho relatado para
outras instituições, taxonomias ou idiomas depende de validação externa
ainda não realizada.

Quanto à validação, a amostra conferida por avaliadores humanos não é
probabilística — prioriza divergências entre modelo e histórico e casos
de maior criticidade —, de modo que os números de acerto validado devem
ser lidos como descrição da amostra conferida, não como estimativa
inferencial do desempenho da base completa (COCHRAN, 1977). Uma regra de
decisão adicional exclui do denominador de acerto validado os casos em
que nenhuma fonte conferida foi confirmada como correta (5,14% dos chamados conferidos, incluindo 52 conflitos); a análise de sensibilidade correspondente mostra
uma amplitude de poucos pontos percentuais entre o cenário mais
otimista e o mais conservador, sem alterar o ranking relativo entre os
modelos.

Quanto ao modelo, o BERTimbau — único classificador contextual testado
neste protocolo — não teve o ajuste fino concluído até esta consolidação
e foi excluído de todas as comparações; de forma mais geral,
classificadores neurais sem *embeddings* pré-treinados de domínio
tendem a ser penalizados por bases de porte médio como a analisada
aqui, o que é consistente com o desempenho relativamente inferior do
LSTM frente aos modelos lineares. Persiste também, como limitação
operacional, a dependência de uma única instituição como caso empírico.

**Papel no modelo de governança preditiva**

Este capítulo constitui o Eixo 1 de um modelo mais amplo de governança
preditiva para manutenção predial, que trata o campus universitário
como um biossistema construído — a integração entre infraestrutura
física, atividade humana, sistemas tecnológicos e condicionantes
ambientais. A contribuição central não termina na categoria atribuída a
cada chamado: os dados estruturados e auditáveis produzidos aqui
(categoria, criticidade, confiança bruta e indicadores de calibração) são a entrada necessária
para três desenvolvimentos subsequentes do mesmo programa de pesquisa.
Primeiro, alimentam modelos de séries temporais (ARIMA, suavização
exponencial) para previsão de custos e demanda de manutenção por
categoria. Segundo, compõem a base factual de uma matriz multicritério
(MCDM/TOPSIS) que prioriza intervenções segundo critérios de
sustentabilidade técnica, ambiental, social e institucional (ESG/ODS).
Terceiro, tornam-se espacializáveis via geoprocessamento (Google Earth
Engine), permitindo leitura territorial do biossistema construído. Sem
uma camada confiável e auditável de classificação — o objeto deste
capítulo —, nenhum desses três desenvolvimentos teria dado de entrada
válido; este capítulo entrega, portanto, a fundação de dados sobre a
qual o modelo de governança preditiva se torna possível.

**6. CONSIDERAÇÕES FINAIS**

O presente capítulo consolida um protocolo multimodelo de classificação de
chamados de manutenção predial universitária em português brasileiro, com sete
modelos comparáveis, memória de decisão por validação humana e análise de
incerteza informacional. O BERTimbau permanece como extensão planejada, sem
ajuste fino concluído ou métricas próprias. A contribuição central é produzir
dado estruturado e auditável para a governança preditiva, distinguindo
concordância com o histórico de acerto contra decisões humanas.

Na amostra parcial e não probabilística de 9.044 decisões
travadas, LinearSVC (95,02%), SGD (94,11%), Regressão Logística (93,71%), Extra Trees (92,86%), Random Forest (92,41%), LSTM (88,11%) e Naive Bayes (86,27%). Nenhum dos três ensembles supera
o LinearSVC isolado; a recomendação é utilizar o LinearSVC com calibração. Os
52 conflitos permanecem fora da verdade validada até revisão
humana específica.

A faixa de confiança igual ou superior a 95% da classificação oficial apresenta
99,94% de acerto validado. O valor supera a meta nominal
na amostra conferida, mas a confiança ainda é bruta e 4.921
chamados não possuem decisão travada; portanto, o resultado não autoriza
liberação automática irrestrita em produção.

A curva real de aprendizado do LSTM (Subseção 4.9, Figura 5) é
consistente com o restante do capítulo. A discrepância do *ablation*
do mesmo modelo (Figura 6), discutida em detalhe na Subseção 4.9, não
indica arquitetura mal ajustada: com a causa principal corrigida, a
ordenação relativa das quatro variantes testadas mostra baixa
sensibilidade do LSTM a unidades e *dropout* nesta base (diferença
entre melhor e pior variante inferior a 4 pontos percentuais).

Os próximos passos deste protocolo incluem a conclusão da conferência humana pendente (35,2% da base ainda sem decisão travada), a
calibração formal por modelo (Platt, isotônica ou temperatura)
condicionada a essa conferência, o treino e a avaliação comparativa do
BERTimbau, a revisão taxonômica dirigida pelos candidatos identificados
na etapa de cruzamento de taxonomia e na entropia de Shannon, e a
estabilização da publicação automática do painel de acompanhamento.

Como direções de trabalho futuro mais amplas, este protocolo também
aponta para: (i) a validação externa do modelo em outras instituições
federais de ensino superior, testando se o padrão de desempenho
observado na UFSB se mantém sob taxonomias e volumes de chamados
distintos; e (ii) a integração dos dados de chamados tratados e
validados como entrada para um modelo multicritério (MCDM/TOPSIS) de
priorização de manutenção, conectando este capítulo empírico à lacuna,
já identificada na literatura de revisão integrativa correlata, sobre o
uso raro de dados operacionais de chamados nesse tipo de modelo. Com
isso, o protocolo pretende seguir contribuindo tanto para a literatura
de *facility management* e processamento de linguagem natural aplicado
quanto para a melhoria concreta e auditável da gestão de manutenção
predial em instituições públicas.

**Contribuições dos autores**: conceituação, Oliveira e Zanchi;
metodologia, software, análise formal, investigação, curadoria de dados
e redação do rascunho original, Oliveira; redação — revisão e edição,
Oliveira e Zanchi; supervisão e administração do projeto, Zanchi. Todos
os autores leram e concordaram com a versão publicada do manuscrito.

**Financiamento**: esta pesquisa não recebeu financiamento externo.

**Comitê de ética e consentimento informado**: não se aplica. O estudo
não envolveu pesquisa com seres humanos, procedimento clínico ou
divulgação de dados pessoais; analisa registros institucionais de
chamados de manutenção (títulos e descrições operacionais curtos) e
decisões internas de conferência de qualidade tomadas pela equipe no
exercício de suas funções rotineiras, não um protocolo experimental com
participantes humanos.

**Disponibilidade de dados**: os dados de chamados de manutenção
analisados neste estudo têm origem no sistema institucional GLPI da
Universidade Federal do Sul da Bahia (UFSB) e não estão publicamente
disponíveis, por restrição de privacidade e confidencialidade
institucional. As métricas derivadas e o código utilizados para
produzir cada figura, tabela e estatística deste artigo são de acesso
público, disponibilizados pelos autores em repositório de código aberto.

**Agradecimentos**: os autores agradecem à Universidade Federal do Sul
da Bahia pelo apoio institucional.

**Conflitos de interesse**: os autores declaram não haver conflitos de
interesse.

**REFERÊNCIAS**

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. ABNT NBR 5674: Manutenção de
edificações: Requisitos para o sistema de gestão de manutenção. Rio de
Janeiro: ABNT, 2012.

BENAVOLI, A.; CORANI, G.; MANGILI, F. Should we really use post-hoc
tests based on mean-ranks? Journal of Machine Learning Research, v. 17,
n. 5, p. 1--10, 2016.

BOUABDALLAOUI, Y.; LAFHAJ, Z.; YIM, P.; DUCOULOMBIER, L.; BENNADJI, B.
Natural Language Processing Model for Managing Maintenance Requests in
Buildings. Buildings, v. 10, n. 9, art. 160, 2020.

BOX, G. E. P.; JENKINS, G. M. Time series analysis: forecasting and
control. San Francisco: Holden-Day, 1970.

CAPRA, F. A teia da vida: uma nova compreensão científica dos sistemas
vivos. São Paulo: Cultrix, 1996.

CHAN, J. Y.-L.; LEOW, S. M. H.; BEA, K. T.; CHENG, W. K.; PHOONG, S. W.;
HONG, Z.-W.; CHEN, Y.-L. Mitigating the multicollinearity problem and
its machine learning approach: a review. Mathematics, v. 10, n. 8, art.
1283, 2022.

COCHRAN, W. G. The comparison of percentages in matched samples.
Biometrika, v. 37, n. 3-4, p. 256--266, 1950.

COCHRAN, W. G. Sampling techniques. 3. ed. New York: John Wiley & Sons,
1977.

DEMŠAR, J. Statistical comparisons of classifiers over multiple data
sets. Journal of Machine Learning Research, v. 7, p. 1--30, 2006.

DICICCIO, T. J.; EFRON, B. Bootstrap confidence intervals. Statistical
Science, v. 11, n. 3, p. 189--228, 1996.

DIETTERICH, T. G. Ensemble methods in machine learning. In:
INTERNATIONAL WORKSHOP ON MULTIPLE CLASSIFIER SYSTEMS, 1., 2000,
Cagliari. Proceedings \[\...\]. Berlin: Springer, 2000. p. 1--15.
(Lecture Notes in Computer Science, v. 1857).

DURBIN, J.; WATSON, G. S. Testing for serial correlation in least
squares regression, I. Biometrika, v. 37, n. 3-4, p. 409--428, 1950.

EFRON, B. Bootstrap methods: another look at the jackknife. The Annals
of Statistics, v. 7, n. 1, p. 1--26, 1979.

EFRON, B.; TIBSHIRANI, R. J. An introduction to the bootstrap. New York:
Chapman & Hall/CRC, 1993.

FLEISS, J. L. Measuring nominal scale agreement among many raters.
Psychological Bulletin, v. 76, n. 5, p. 378--382, 1971.

FRIEDMAN, M. The use of ranks to avoid the assumption of normality
implicit in the analysis of variance. Journal of the American
Statistical Association, v. 32, n. 200, p. 675--701, 1937.

GALKE, L.; SCHERP, A. Bag-of-words vs. graph vs. sequence in text
classification: questioning the necessity of text-graphs and the
surprising strength of a wide MLP. In: ANNUAL MEETING OF THE ASSOCIATION
FOR COMPUTATIONAL LINGUISTICS, 60., 2022, Dublin. Proceedings \[\...\].
Dublin: ACL, 2022. p. 4038--4051.

GRAVES, A.; SCHMIDHUBER, J. Framewise phoneme classification with
bidirectional LSTM and other neural network architectures. Neural
Networks, v. 18, n. 5-6, p. 602--610, 2005.

GRIMM, N. B.; FAETH, S. H.; GOLUBIEWSKI, N. E.; REDMAN, C. L.; WU, J.;
BAI, X.; BRIGGS, J. M. Global change and the ecology of cities. Science,
v. 319, n. 5864, p. 756--760, 2008.

GUO, C.; PLEISS, G.; SUN, Y.; WEINBERGER, K. Q. On calibration of modern
neural networks. In: INTERNATIONAL CONFERENCE ON MACHINE LEARNING, 34.,
2017, Sydney. Proceedings \[\...\]. Sydney: PMLR, 2017. p. 1321--1330.

HODGE, V. J.; AUSTIN, J. A survey of outlier detection methodologies.
Artificial Intelligence Review, v. 22, n. 2, p. 85--126, 2004.

HOLM, S. A simple sequentially rejective multiple test procedure.
Scandinavian Journal of Statistics, v. 6, n. 2, p. 65--70, 1979.

JOACHIMS, T. Text categorization with support vector machines: learning
with many relevant features. In: EUROPEAN CONFERENCE ON MACHINE
LEARNING, 10., 1998, Chemnitz. Proceedings \[\...\]. Berlin: Springer,
1998. p. 137--142.

KEJRIWAL, M.; SANTOS, H.; SHEN, K.; MULVEHILL, A. M.; MCGUINNESS, D. L.
A noise audit of human-labeled benchmarks for machine commonsense
reasoning. Scientific Reports, v. 14, art. 8609, 2024.

KOHAVI, R. A study of cross-validation and bootstrap for accuracy
estimation and model selection. In: INTERNATIONAL JOINT CONFERENCE ON
ARTIFICIAL INTELLIGENCE, 14., 1995, Montreal. Proceedings \[\...\]. San
Francisco: Morgan Kaufmann, 1995. p. 1137--1143.

KORNBROT, D. Point biserial correlation. In: Wiley StatsRef: Statistics
Reference Online. Chichester: Wiley, 2014.

LANDIS, J. R.; KOCH, G. G. The measurement of observer agreement for
categorical data. Biometrics, v. 33, n. 1, p. 159--174, 1977.

LIMA, L. F. M.; MAROLDI, A. M.; SILVA, D. V. O. da; HAYASHI, C. R. M.;
HAYASHI, M. C. P. I. Métricas científicas em estudos bibliométricos:
detecção de outliers para dados univariados. Em Questão, Porto Alegre, v.
23, p. 254--273, 2017.

LIN, J. Divergence measures based on the Shannon entropy. IEEE
Transactions on Information Theory, v. 37, n. 1, p. 145--151, 1991. DOI:
10.1109/18.61115.

LI, Y.; LIU, Y.; ZHANG, J.; CAO, L.; WANG, Q. Automated analysis and
assignment of maintenance work orders using natural language processing.
Automation in Construction, v. 165, art. 105501, 2024.

LIU, Z.; BENGE, C.; JIANG, S. Ticket-BERT: labeling incident management
tickets with language models. arXiv:2307.00108, 2023.

MARQUARDT, D. W. Generalized inverses, ridge regression, biased linear
estimation, and nonlinear estimation. Technometrics, v. 12, n. 3, p.
591--612, 1970.

MARTINS, R. F. B.; ESPEJO, M. M. S. B. Análise de custos de manutenção
predial em uma universidade federal brasileira com uso do modelo de SES.
ABCustos, São Leopoldo, v. 19, n. 1, p. 79--98, 2024.

MCNEMAR, Q. Note on the sampling error of the difference between
correlated proportions or percentages. Psychometrika, v. 12, n. 2, p.
153--157, 1947.

MINDERER, M.; DJOLONGA, J.; ROMIJNDERS, R.; HUBIS, F.; ZHAI, X.;
HOULSBY, N.; TRAN, D.; LUCIC, M. Revisiting the calibration of modern
neural networks. In: CONFERENCE ON NEURAL INFORMATION PROCESSING
SYSTEMS, 35., 2021. Advances in Neural Information Processing Systems,
v. 34, 2021.

MOHAMMED, A. S.; AMOAH, C. Integration of technology in decision-making
in university facilities management: a literature review. Facilities, v.
43, n. 13/14, p. 1018--1052, 2025.

MORAIS, L. S. R. de; PAULA, H. M. de; REIS, R. P. A. Promoção da
eficiência da manutenção predial em edificações públicas: abordagem
baseada em registros de ordens de serviço. Paranoá, Brasília, v. 16, n.
34, p. 1--18, 2023. DOI: 10.18830/issn.1679-0944.n34.2023.08.

NEMENYI, P. B. Distribution-free multiple comparisons. 1963. Tese
(Doutorado em Estatística) — Princeton University, Princeton, 1963.

NOMA, H.; SHINOZAKI, T.; IBA, K.; TERAMUKAI, S.; FURUKAWA, T. A.
Confidence intervals of prediction accuracy measures for multivariable
prediction models based on the bootstrap-based optimism correction
methods. Statistics in Medicine, v. 40, n. 26, p. 5691--5701, 2021.

O'BRIEN, R. M. A caution regarding rules of thumb for variance inflation
factors. Quality & Quantity, v. 41, n. 5, p. 673--690, 2007.

ODUM, H. T. Environment, power, and society. New York:
Wiley-Interscience, 1971.

OGUNLEYE, L. I.; OYEJOLA, B. A.; OBISESAN, K. O. Comparison of some
common tests for normality. International Journal of Probability and
Statistics, v. 7, n. 5, p. 130--137, 2018.

PAMPANA, A. K. et al. Data-driven analysis for facility management in
higher education institution. Buildings, v. 12, art. 2094, 2022.

PEDREGOSA, F. et al. Scikit-learn: machine learning in Python. Journal
of Machine Learning Research, v. 12, p. 2825--2830, 2011.

PLATT, J. C. Probabilistic outputs for support vector machines and
comparisons to regularized likelihood methods. In: SMOLA, A. J. et al.
(Ed.). Advances in Large Margin Classifiers. Cambridge: MIT Press, 1999.
p. 61--74.

RAZALI, N. M.; WAH, Y. B. Power comparisons of Shapiro-Wilk,
Kolmogorov-Smirnov, Lilliefors and Anderson-Darling tests. Journal of
Statistical Modeling and Analytics, v. 2, n. 1, p. 21--33, 2011.

SALTON, G.; BUCKLEY, C. Term-weighting approaches in automatic text
retrieval. Information Processing & Management, v. 24, n. 5, p.
513--523, 1988.

SCHWARTZ, R.; DODGE, J.; SMITH, N. A.; ETZIONI, O. Green AI.
Communications of the ACM, v. 63, n. 12, p. 54--63, 2020.

SHANNON, C. E. A mathematical theory of communication. Bell System
Technical Journal, v. 27, n. 3, p. 379--423, jul. 1948; v. 27, n. 4, p.
623--656, out. 1948.

SHAPIRO, S. S.; WILK, M. B. An analysis of variance test for normality
(complete samples). Biometrika, v. 52, n. 3-4, p. 591--611, 1965.

SOKOLOVA, M.; LAPALME, G. A systematic analysis of performance measures
for classification tasks. Information Processing & Management, v. 45, n.
4, p. 427--437, 2009.

SPEARMAN, C. The proof and measurement of association between two
things. American Journal of Psychology, v. 15, n. 1, p. 72--101, 1904.

SUNDARAM, S.; ZEID, A. Technical Language Processing for Prognostics and
Health Management: applying text similarity and topic modeling to
maintenance work orders. Journal of Intelligent Manufacturing, v. 36, p.
1637--1657, 2025.

TATE, R. F. Correlation between a discrete and a continuous variable.
Point-biserial correlation. The Annals of Mathematical Statistics, v.
25, n. 3, p. 603--607, 1954.

TREVISO, M. et al. Efficient methods for Natural Language Processing: a
survey. Transactions of the Association for Computational Linguistics,
v. 11, p. 826--860, 2023.

TUKEY, J. W. Exploratory data analysis. Reading: Addison-Wesley, 1977.

WONGPAKARAN, N.; WONGPAKARAN, T.; WEDDING, D.; GWET, K. L. A comparison
of Cohen's Kappa and Gwet's AC1 when calculating inter-rater reliability
coefficients: a study conducted with personality disorder samples. BMC
Medical Research Methodology, v. 13, art. 61, 2013.

ZHANG, H.; ZHANG, Y.; LI, J.; LIU, J.; JI, L. A survey on learning with
noisy labels in Natural Language Processing: how to train models with
label noise. Engineering Applications of Artificial Intelligence, v.
146, art. 110157, 2025.

ZUUR, A. F.; IENO, E. N.; ELPHICK, C. S. A protocol for data exploration
to avoid common statistical problems. Methods in Ecology and Evolution,
v. 1, n. 1, p. 3--14, 2010.

**APÊNDICES**

A estrutura completa dos dados, incluindo a arquitetura das planilhas e a
memória de decisão, está disponível no repositório público do experimento.

**Apêndice A — Checklist de itens reportados**

Adaptado do espírito do checklist tipo PRISMA-ScR do artigo-modelo de revisão
(MCDM/TOPSIS/ODS/ESG) para relato de experimento de classificação supervisionada
com validação humana. Cada item indica a subseção onde é reportado e o status na
data de publicação; **não substitui a reconferência de números antes da
submissão** — os status "Sim" abaixo atestam que o item é reportado em algum
lugar do texto, não que o número citado já foi revalidado contra os JSONs
vigentes.

| Item | Subseção | Reportado? |
|---|---|---|
| Fonte de dados e sistema de origem declarados | 3.1, 3.2 | Sim (GLPI/UFSB) |
| Tamanho da amostra e período/corte de consolidação | 3.2 | Sim, mas com data de corte a reconferir |
| Critério de inclusão/exclusão de registros | 3.2 | Parcial — "chamados não vazios" declarado; demais critérios não detalhados |
| Pré-processamento textual | 3.3 | Sim |
| Modelos avaliados e hiperparâmetros principais | 3.4 | Sim (7 materializados + 1 em extensão) |
| Justificativa conceitual das diferenças de desempenho entre modelos | 3.4.1 | Sim |
| Método de particionamento (out-of-fold, k-fold, seed) | 3.5 | Sim (out-of-fold, KFold embaralhado, `random_state=42`; sem estratificação) |
| Justificativa da escolha k-fold vs. holdout fixo, com comparação empírica | 3.5 | Sim (KOHAVI, 1995; Tabela Suplementar S4) |
| Métricas reportadas e justificativa | 3.5 | Sim (acurácia, macro-F1, balanced accuracy, IC95% bootstrap) |
| Testes estatísticos e correção para múltiplas comparações | 3.5, 4.10 | Sim — resultados numéricos completos em 4.10 |
| Verificação explícita de pressupostos (normalidade, homogeneidade, colinearidade, independência) | 4.10 | Sim — protocolo de Zuur, Ieno e Elphick (2010) adaptado; detalhamento completo em Material Suplementar |
| Critério de calibração de confiança (bruta vs. calibrada) e meta de desempenho | 3.8, 4.4 | Parcial — meta declarada (>= 95%/>= 95%); calibração formal (Platt/isotônica) ainda não aplicada |
| Protocolo de validação humana | 3.6 | Sim |
| Cobertura da validação humana na data de publicação (n e % da base) | 4 (abertura) | Sim, mas desatualizada — ver nota de revalidação de dados |
| Tratamento de conflitos de conferência | 3.7 | Sim (regra de veto/trava) |
| Reprodutibilidade (scripts e dados versionados) | 3.9 | Sim (repositório público, JSONs sanitizados) |
| Limitações declaradas | 5, 6 | Sim |
| Figuras/tabelas geradas a partir de dados verificáveis | 4.8 | Sim (scripts leem os JSONs vigentes do painel) |

**Apêndice B — Matriz de decisão M/N/P**

Contagens agregadas disponíveis nos JSONs públicos do painel:

| Métrica | n |
|---|---|
| Chamados com ao menos uma conferência (M, N ou P) | 9.534 |
| Decisões travadas (categoria decidida sem conflito) | 9.096 |
| Casos restritos (categoria eliminada, sem decisão travada) | 438 |
| Conflitos (M e N confirmam categorias diferentes) | 0 |
| Conferências da coluna N (CONFERÊNCIA IA) preenchidas | 9.096 |
| Conferências da coluna M (CONFERÊNCIA GLPI) preenchidas | 9.534 |
| Conferências da coluna P (CONFERÊNCIA IA - 2) preenchidas | 0 |

Fonte: elaborado pelos autores (2026). A coluna P (reclassificação
conferida) está zerada nesta consolidação — nenhuma reclassificação foi
conferida via essa coluna especificamente até o momento.

*Pendência explícita*: o cruzamento fino de 3 vias (contagem por combinação
exata de valores de M × N × P — ex.: quantos casos têm M=Correto e N=Errado
simultaneamente) **não está disponível em nenhum JSON público atual** e exige
extração direta da planilha experimental (`Informação insuficiente para
verificar` com os dados hoje publicados). O que se aproxima disso é a matriz
2×2 IA×histórico da Tabela 4 (Subseção 4.3), que cruza acerto da IA e do
histórico contra a verdade decidida — não é o mesmo cruzamento M×N×P bruto,
mas cobre a mesma pergunta de fundo (quando IA e histórico concordam ou
divergem da decisão final).
