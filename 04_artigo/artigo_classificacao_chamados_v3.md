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
concluído ou métrica própria. O diferencial metodológico reside na distinção entre
concordância com o histórico administrativo e acerto validado por
revisão humana, tratando a categoria histórica como referência
preliminar imperfeita. A distinção mostrou-se decisiva, pois o acerto
validado por conferência humana (9.096 decisões) revelou-se
mais conservador do que a concordância com o histórico sugeria, à medida
que a amostra de conferência cresceu. Como a seleção não é aleatória e
prioriza divergências e casos críticos, esses resultados não estimam o
desempenho da base completa (COCHRAN, 1977). Resultados indicam superioridade do LinearSVC
tanto na concordância com o histórico (acurácia de 80,29%,
IC95%: 79,62%--80,95%) quanto no acerto validado (94,93%, IC95%:
94,47%--95,38%), enquanto o LSTM apresentou concordância de 68,13% e
acerto validado de 87,90%, após reprocessamento completo dos sete
modelos comparáveis (Subseções 4.1, 4.2 e 4.8). A normalidade da concordância por turno foi
rejeitada para todos os modelos, justificando testes não paramétricos
(Friedman, Cochran Q, McNemar, bootstrap). O custo computacional é
incorporado como dimensão de avaliação, evidenciando que modelos
lineares podem oferecer melhor relação entre desempenho e viabilidade
operacional em cenários de texto curto, ruidoso e desbalanceado.

**Palavras-chave:** manutenção predial; classificação de chamados;
processamento de linguagem natural; rótulos ruidosos; validação humana;
governança preditiva.

**ABSTRACT**

*Automatic classification of building maintenance work orders is a
strategic resource for qualifying operational triage and enhancing
evidence-based governance in public institutions. However, in historical
databases from computerized service management systems, the originally
assigned category should not be treated as an unquestionable ground
truth, since it may reflect noisy operational decisions, overlapping
taxonomies, incomplete records, and heterogeneous interpretations across
maintenance teams. This paper proposes a multi-model protocol for
classifying real university building maintenance requests in Brazilian
Portuguese, extracted from the GLPI system at the Federal University of
Southern Bahia. The experiment uses 13,965 non-empty records organized
into 55 historical categories and compares TF-IDF-based classical
classifiers (Naive Bayes, Logistic Regression, LinearSVC, SGD, Random
Forest, and Extra Trees) and a bidirectional LSTM neural network. The
Portuguese pre-trained transformer (BERTimbau) remains a planned
extension, with neither completed training nor its own metric. The
methodological contribution lies in distinguishing agreement with
administrative history from human-validated accuracy, treating the
historical category as an imperfect preliminary reference. This
distinction proved decisive, since human-validated accuracy (9,096
decisions) turned out to be more conservative than agreement with
history suggested, as the reviewed sample grew. Because the sample is
non-random and prioritizes divergences and critical cases, these results
do not estimate performance over the full database (COCHRAN, 1977).
Results indicate LinearSVC superiority both in agreement with history
(80.29% accuracy, 95%CI: 79.62%--80.95%) and in human-validated accuracy
(94.93%, 95%CI: 94.47%--95.38%), while LSTM achieved 68.13% agreement
and 87.90% validated accuracy, after full reprocessing of the seven
comparable models. Normality was rejected for all models, supporting
non-parametric tests (Friedman, Cochran Q, McNemar, bootstrap).
Computational cost is incorporated as an evaluation dimension, showing
that linear models can offer a better balance between performance and
operational feasibility in short, noisy, and imbalanced text.*

***Keywords:** building maintenance; work-order classification; natural
language processing; noisy labels; human validation; predictive
governance.*

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
chamados de manutenção predial, matéria-prima do *feedback*
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

Diante desse quadro, a pergunta que orienta este artigo não é qual
classificador mais concorda com a categoria histórica. A questão é mais
ampla e alinhada à função de governança que esses dados devem cumprir.
Como extrair de texto ruidoso, de forma confiável e auditável, o dado
estruturado capaz de alimentar um sistema de governança preditiva sem
herdar acriticamente os erros do histórico que lhe deu origem? Rótulos
ruidosos em PLN reduzem o desempenho de classificadores e ampliam o
consumo de recursos computacionais necessários para tratá-los (ZHANG
*et al.*, 2025). Soma-se a isso que *benchmarks* anotados por humanos
carregam variabilidade relevante, o que torna questionável tratar
qualquer rótulo, humano ou histórico, como verdade absoluta e não
sujeita a julgamento (KEJRIWAL *et al.*, 2024). A classificação
automática apresentada aqui constitui, portanto, a primeira camada de um
protocolo maior, e não seu produto final. Cabe a essa camada produzir
dado auditável o bastante para que divergências entre inteligência
artificial e histórico administrativo sejam tratadas como evidência de
revisão taxonômica, e não como ruído a descartar.

Com base em chamados reais da Universidade Federal do Sul da Bahia
(UFSB), este artigo propõe uma comparação multimodelo de
classificadores de texto aplicada a chamados de manutenção predial em
português brasileiro. A base experimental contém 13.965 chamados não
vazios, distribuídos em 55 categorias históricas; os campos textuais
considerados agregam título e descrição do chamado, além de informações
associadas à ordem de serviço. O estudo compara modelos clássicos
baseados em TF-IDF (Naive Bayes, Regressão Logística, LinearSVC, SGD,
Random Forest e Extra Trees) com uma rede neural LSTM bidirecional. O
BERTimbau é mantido como extensão planejada e não integra as comparações
enquanto não houver treino concluído e métricas próprias rastreáveis. O
objeto de avaliação, portanto, não é o classificador isolado, mas o
protocolo de governança preditiva que articula aprendizado de máquina,
auditoria estatística, custo computacional e validação humana. Essa
formulação é consoante à manutenção baseada em evidências preconizada
pela NBR 5674 (ABNT, 2012) e à integração
físico-humano-tecnológico-ambiental que caracteriza um biossistema
construído.

Cinco objetivos específicos orientam o trabalho. O primeiro é apresentar
um protocolo de classificação automática que produza dado estruturado
auditável a partir de texto livre. O segundo é distinguir a concordância
com o rótulo histórico do acerto validado, evitando equiparar categoria
histórica a *ground truth* incontestável. O terceiro é avaliar o
desempenho por métricas globais e balanceadas, intervalos de confiança e
testes estatísticos pareados adequados a dados não normais. O quarto é
incorporar o custo computacional como dimensão de decisão operacional. O
quinto é converter divergências entre inteligência artificial e
histórico em evidência para revisão taxonômica e retroalimentação da
base de treino.

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

![](04_artigo/figuras/fig1_pipeline_governanca.pdf)

**Figura 1** Pipeline de governança preditiva: fluxo metodológico
completo, da extração da base à retroalimentação por validação humana.

Fonte: elaborado pelos autores (2026).

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

A base é dinâmica, pois novos chamados continuam a ser incorporados e a
taxonomia institucional pode ser revisada ao longo do tempo. Os
resultados da Seção 4 referem-se ao corpus descrito acima. Diferenças
frente a recortes anteriores refletem o crescimento da base e a
ampliação da conferência humana, não mudança metodológica.

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

O desenho experimental compara sete modelos, organizados
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
mas treina seus *embeddings* do zero, sem incorporar vetores
pré-treinados em português (GRAVES; SCHMIDHUBER, 2005). A Subseção 3.4.1
discute por que essa escolha tende a penalizar o desempenho em corpora
de porte médio como o deste estudo. Os sete modelos são avaliados na
comparação *out-of-fold* (Subseção 4.1). Em paralelo, a classificação
automática em produção opera com uma regra de contingência que aciona o
Random Forest quando a base rotulada disponível é insuficiente para
treinar a rede neural.

Um oitavo modelo, o transformador pré-treinado em português BERTimbau,
permanece como extensão planejada. Seu ajuste fino depende do avanço da
base validada e ainda não foi concluído, razão pela qual o modelo não
integra tabelas, rankings, testes inferenciais nem conclusões
comparativas deste artigo.

**3.4.1 Diferenças conceituais e operacionais entre os classificadores**

Os sete modelos comparáveis cobrem quatro famílias
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
forte poder discriminativo (JOACHIMS, 1998; SALTON; BUCKLEY, 1988),
como ocorre aqui, em que termos técnicos do domínio (*bomba*, *split*,
*disjuntor*, *vazamento*, *infiltração*, *ar-condicionado*; Subseção 3.3)
funcionam como âncoras semânticas de categoria. Essa combinação é
consistente com o LinearSVC liderando tanto a concordância com o
histórico (0,8029; Tabela 1) quanto o acerto validado (0,9493; Tabela 2).

O **Naive Bayes** assume independência condicional entre atributos dada
a classe, suposição estrutural violada em texto de manutenção predial,
onde termos técnicos co-ocorrem de forma sistemática dentro de uma mesma
categoria. Essa divergência entre a suposição do modelo e a estrutura
real dos dados explica de forma plausível a última posição do Naive
Bayes, tanto na concordância com o histórico (0,6996; Tabela 1) quanto
no acerto validado (0,8609; Tabela 2). Trata-se do comportamento
esperado do modelo mais simples da comparação, e não de problema de
implementação.

**Random Forest** e **Extra Trees** capturam interações não lineares
entre atributos por meio da estrutura de árvores, mas em espaços
esparsos de alta dimensionalidade como o TF-IDF tendem a ajustar-se
demais às co-ocorrências mais frequentes, o que se reflete no desempenho
intermediário de ambos nas Tabelas 1 e 2 (entre o LinearSVC e o Naive
Bayes). O custo computacional dessa família é também o mais alto entre
os modelos clássicos medidos. O treino por lote de 1.000 registros
consome 19,45 s no Random Forest e 21,30 s no Extra Trees, entre 7,6 e
8,4 vezes o tempo do LinearSVC (2,55 s) e entre 17,1 e 18,7 vezes o do
Naive Bayes (1,14 s) no mesmo lote (Tabela 7). Esse custo só se
justificaria se revertido em ganho de acerto validado, o que não se
confirma nos dados analisados (SCHWARTZ *et al.*, 2020; TREVISO *et
al.*, 2023).

A **LSTM Bidirecional** foi projetada para modelar dependências
sequenciais no texto, mas seus *embeddings* são inicializados
aleatoriamente e treinados do zero, sem incorporação de vetores
pré-treinados em português. A camada de *embedding* (8.000 termos × 128
dimensões) concentra sozinha cerca de 1,02 milhão de parâmetros, ordem
de grandeza próxima do número de exemplos disponíveis por partição de
treino, já que dos 13.965 chamados cerca de 11.172 compõem cada partição
em `k=5` *folds* (Subseção 3.5). Esse cenário é consistente com a
hipótese de que modelos lineares igualam ou superam redes neurais em
corpora de porte médio e ruidosos, quando não há *embeddings*
pré-treinados disponíveis no idioma (GALKE; SCHERP, 2022). A Subseção
4.8 detalha a investigação da discrepância do *ablation* do LSTM, que
confirma não se tratar de falha da arquitetura em si.

Na classificação automática em produção, distinta da comparação
*out-of-fold* desta seção, a regra de contingência opera no nível da
base de treino, não por chamado individual. A LSTM só é treinada quando
a base rotulada disponível atinge um mínimo de 200 exemplos. Abaixo
desse limiar, um classificador Random Forest sobre TF-IDF substitui a
rede neural para toda a base naquele momento. Um segundo critério, sem
relação com essa troca de modelo, classifica a confiança de cada
predição em três faixas (abaixo de 70%, entre 70% e 95%, acima de 95%),
usadas para priorização de conferência humana e para as métricas de
calibração da Subseção 4.4.

**3.5 Desenho de avaliação**

A avaliação foi realizada por predições fora da amostra em protocolo
*out-of-fold* com *KFold* embaralhado, cinco partições, semente fixa e
mesma partição determinística para todos os modelos. A partição não é
estratificada, limitação do desenho implementado. O procedimento reduz
viés de comparação e permite testes pareados (SOKOLOVA; LAPALME, 2009).
São reportadas acurácia, *macro*-F1, F1 ponderado, *balanced accuracy* e
intervalo de confiança a 95% por *bootstrap*, reamostragem com reposição
que estima a distribuição de uma estatística sem pressupor sua forma
paramétrica (EFRON, 1979; EFRON; TIBSHIRANI, 1993). DiCiccio e Efron
(1996) revisam em detalhe os métodos de construção desse intervalo,
percentil, BCa e bootstrap-*t*, e suas propriedades de cobertura.

A *macro*-F1 e a *balanced accuracy* respondem ao desbalanceamento entre
categorias, dado que a acurácia isolada pode superestimar o desempenho
em classes majoritárias e mascarar falhas em categorias raras
(SOKOLOVA; LAPALME, 2009). A correlação entre confiança e acerto é
avaliada por Spearman (SPEARMAN, 1904) e por correlação ponto-bisserial,
apropriada quando uma das variáveis é binária (TATE, 1954). Diferenças
globais entre os sete classificadores são apuradas por Cochran Q, teste
não paramétrico para proporções pareadas em três ou mais condições
(COCHRAN, 1950), e por Friedman, que dispensa o pressuposto de
normalidade da ANOVA (FRIEDMAN, 1937). As comparações pareadas seguem o
teste de McNemar (MCNEMAR, 1947), e a incerteza de acurácia é estimada
por *bootstrap* (EFRON, 1979), abordagem cuja aplicação a métricas de
modelos preditivos permanece em refinamento (NOMA *et al.*, 2021).

Diante de múltiplas comparações, aplica-se o teste de Nemenyi sobre os
postos médios (NEMENYI, 1963), conforme o protocolo consolidado por
Demšar (2006) para comparação estatística de classificadores. Esse
protocolo tem limitações já apontadas. Benavoli, Corani e Mangili (2016)
demonstram que o teste de postos médios, base do Nemenyi, pode ser
inconsistente, e recomendam testes pareados diretos como complemento.
Por essa razão, reporta-se também o McNemar par a par (Subseção 4.9), em
vez de depender apenas do Nemenyi. As comparações pareadas adicionais
entre os sete modelos são corrigidas pelo método sequencial de
Holm-Bonferroni, que controla a taxa de erro familiar sem o
conservadorismo excessivo da correção de Bonferroni simples (HOLM,
1979).

Cabe justificar a escolha do *k-fold out-of-fold* em vez de um conjunto
de teste fixo separado antes do treino. A literatura de avaliação de
modelos indica que a validação cruzada produz estimativas de menor
variância que um único *holdout*, sobretudo em bases pequenas ou
desbalanceadas, por avaliar cada exemplo em algum *fold* em vez de
descartar uma fração fixa dos dados do treino (KOHAVI, 1995). Esta base
é desbalanceada por natureza, com várias das 55 categorias históricas
apresentando suporte de dígito único (Tabela Suplementar S1).

A recomendação foi verificada empiricamente. Comparou-se o protocolo
*k*-fold com um *holdout* fixo de 15% sobre os sete modelos comparáveis
e a mesma base completa. A tentativa de estratificar esse *holdout* por
categoria, prática padrão na maioria dos protocolos, falhou de imediato,
pois a base contém categorias com um único exemplo. No *holdout*
aleatório que a substituiu, várias categorias raras ficaram sem nenhum
exemplo de teste, o que torna indefinida a métrica de desempenho dessas
classes, problema que o *k*-fold evita por avaliar todo exemplo em algum
*fold*. A acurácia global variou pouco entre os dois protocolos, mas a
*macro*-F1, que pondera todas as categorias igualmente, piorou no
*holdout* na maioria dos modelos. Constata-se, portanto, que o *holdout*
fixo não melhora a estimativa de desempenho global nesta base e degrada
sistematicamente a avaliação das categorias raras, padrão que a
literatura antecipa para corpora pequenos e desbalanceados (KOHAVI,
1995).

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
Shannon e divergência de Jensen-Shannon (SHANNON, 1948; LIN, 1991),
calculada exclusivamente sobre agregados públicos e sanitizados, sem
identificador, título ou texto livre do chamado. Essa camada não substitui acurácia,
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

**3.9 Disponibilidade de dados**

Os artefatos que sustentam os resultados relatados neste artigo são
gerados por um processo automatizado e reproduzível, reexecutado a cada
atualização do experimento. Nenhum identificador pessoal, título ou
texto livre de chamado é armazenado nos agregados publicados, e a camada
de entropia (Subseção 3.8) opera exclusivamente sobre esses agregados.

**4. RESULTADOS**

Esta seção apresenta dois conjuntos de resultados, deliberadamente
segregados: a concordância com a categoria histórica (Subseção 4.1), que
trata o registro do GLPI como referência preliminar e não como verdade
absoluta; e o desempenho validado por conferência humana (Subseções 4.2
e 4.3), calculado exclusivamente sobre os chamados com decisão validada
pela conferência humana. A base elegível contém 13.965 chamados. A
conferência humana cobre 9.534 chamados (68,3% da base), dos quais
9.096 com decisão validada e sem conflito (65,1% da base) e 438 casos
restritos, em que o avaliador eliminou as categorias conferidas sem
indicar a correta. Como
discutido na Subseção 4.2 e na Seção 5, o crescimento da conferência
humana ao longo do protocolo revela um padrão de desempenho
sensivelmente mais conservador do que amostras menores sugeriam.

Três achados resumem esta seção. Primeiro, os classificadores lineares
(liderados pelo LinearSVC) superam tanto os *ensembles* de árvores
quanto a rede neural LSTM em concordância e em acerto validado, com
vantagem adicional de custo computacional (Subseções 4.1, 4.2 e 4.7).
Segundo, a validação humana confirma que o próprio rótulo histórico
contém ruído real, cerca de 3,5% dos casos conferidos, o que
justifica metodologicamente todo o protocolo de conferência dupla
(Subseção 4.3). Terceiro, a meta de calibração do estudo (confiança
igual ou superior a 95% associada a acerto real igual ou superior a
95%) está próxima de ser atingida, mas a confiança usada ainda é bruta,
sem calibração formal por método probabilístico. O número deve ser lido
como piso e teto da faixa observada, e não como estimativa definitiva
(Subseção 4.4).

**4.1 Concordância com o histórico (base completa)**

A comparação contra a categoria histórica, sobre a base completa (n =
13.965, com intervalo de confiança por bootstrap a 95%), mantém o
LinearSVC na liderança, com acurácia de 0,8029 (IC95%:
0,7962--0,8095), seguido por Extra Trees (0,7885), Random Forest
(0,7799), SGD (0,7765), Regressão Logística (0,7677), Naive Bayes
(0,6996) e LSTM (0,6813). O teste de Cochran Q confirma diferença global
entre os sete modelos avaliados (Q = 2680,70; p < 0,001). A comparação exclui o BERTimbau,
cujo treino não foi concluído. O Kappa de Cohen entre cada modelo e o
histórico reproduz exatamente a mesma ordenação, variando de 0,7880
(LinearSVC) a 0,6598 (LSTM). A ordem entre os sete modelos permanece a mesma de
recortes anteriores, pois a atualização completa dos modelos alterou o
patamar absoluto, não o ranking. A oitava fonte de classificação, a
classificação automática em produção, mantém concordância de 77,65% e
confiança média de 71,67%, posicionando-se entre SGD e Regressão
Logística nesta métrica. A comparação direta com o LSTM *out-of-fold* da
Tabela 1 não é apropriada porque essa fonte combina a rede neural com a
regra de contingência do Random Forest (Subseção 3.4), em vez de um
único modelo isolado. Ela também não foi reprocessada junto com os sete
modelos comparáveis e pode estar sujeita à mesma defasagem discutida na
Subseção 4.8.

**Tabela 1** Concordância com a categoria histórica por modelo (n = 13.965).

| Modelo | Acurácia | IC95% |
|---|---|---|
| LinearSVC | 0,8029 | 0,7962 -- 0,8095 |
| Extra Trees | 0,7885 | 0,7817 -- 0,7949 |
| Random Forest | 0,7799 | 0,7732 -- 0,7864 |
| SGD | 0,7765 | 0,7697 -- 0,7833 |
| Regressão Logística | 0,7677 | 0,7608 -- 0,7745 |
| Naive Bayes | 0,6996 | 0,6921 -- 0,7070 |
| LSTM (out-of-fold) | 0,6813 | 0,6733 -- 0,6888 |

Fonte: elaborado pelos autores (2026).

A concordância com o histórico não é uniforme entre as 55 categorias. A
Tabela Suplementar S1 reporta suporte, precisão, revocação e F1-Score
por categoria. O desempenho concentra-se nas classes de maior volume. As
cinco categorias com maior F1 pertencem todas à Manutenção Preventiva,
com destaque para Gerador (F1 = 0,9908; suporte = 1.211) e Quadros
Elétricos (F1 = 0,9869; suporte = 576). No extremo oposto, as cinco
categorias de menor F1 reúnem Sistema Fotovoltaico, Manutenção Preventiva
sem subcategoria, Instalações Especiais, Transporte e Drenagem, todas com
F1 inferior a 0,14. Essa leitura pede cautela, pois quatro dessas cinco
categorias têm suporte igual ou inferior a sete registros, condição em
que pequena variação absoluta altera fortemente a métrica.

**4.2 Ranking validado por conferência humana**

Esta subseção reflete a atualização completa dos sete modelos (Subseção
4.1). Uma versão anterior, hoje descartada, reportava acerto validado
sensivelmente mais baixo. A diferença confirma a hipótese discutida na
Subseção 4.8, de que a versão antiga estava desatualizada, sem problema
de metodologia na avaliação em si.

A avaliação contra a decisão validada pela conferência humana (n =
9.096 decisões) confirma a mesma liderança da Subseção 4.1: o
LinearSVC permanece o melhor modelo isolado, com
acerto validado de 0,9493 (IC95%: 0,9447--0,9538), seguido por SGD
(0,9392), Regressão Logística (0,9355), Extra Trees (0,9274), Random
Forest (0,9227), LSTM (0,8790) e Naive Bayes (0,8609). A diferença entre o primeiro e o segundo colocado é
pequena em termos absolutos (1,01 ponto percentual), mas estatisticamente
significativa (McNemar, *p* < 0,001). Foram avaliados também três
*ensembles*, maioria ponderada (0,9445), confiança calibrada máxima
(0,9436) e maioria simples (0,9422). Nenhum supera o LinearSVC isolado
com significância (McNemar p < 0,05 em favor do LinearSVC nos três
casos). **Não compensa combinar modelos nestes dados.** A recomendação é
usar o LinearSVC isolado, com calibração.

**Viés estrutural da seleção da amostra validada**: o número pontual de
acerto validado acima é o **limite superior** de um
intervalo, não uma estimativa isenta de viés. A "verdade validada" usada
neste cálculo só existe para um chamado quando o avaliador confirma
pelo menos uma fonte como correta, seja o histórico, seja a
classificação automática, seja a reclassificação. Dos 9.534 chamados
conferidos, 438 (4,6%) caem no status "restrito", em que o avaliador
julgou **todas** as fontes erradas para aquele chamado (344 casos só com
o histórico marcado errado, 94 com histórico e classificação automática
errados simultaneamente), sem indicar qual seria a categoria certa. Esses 438
casos são **excluídos do denominador** de qualquer acerto validado por
modelo, porque não existe categoria de referência contra a qual comparar
a predição. Isso torna a amostra de 9.096 decisões, por construção, um
subconjunto em que pelo menos uma fonte já estava correta, o que infla
mecanicamente o acerto validado de qualquer modelo que tenda a
concordar com o histórico ou com a classificação automática, independentemente
da qualidade real do modelo nos casos mais difíceis (exatamente os que
ficaram de fora).

Para tornar esse viés visível sem descartar a métrica, calculou-se um
**limite inferior** de sensibilidade: o acerto de cada modelo caso os 438
restritos fossem incluídos no denominador e contados como erro para
**todos** os modelos. Trata-se do pior caso possível, pois a categoria
certa desses chamados é desconhecida e nenhum modelo pode receber
crédito neles. O intervalo entre limite inferior e superior substitui o
número pontual como leitura honesta do acerto validado: LinearSVC 0,9057--0,9493
(amplitude 4,36 p.p.), SGD 0,8961--0,9392 (4,31 p.p.), Regressão
Logística 0,8925--0,9355 (4,30 p.p.), Extra Trees 0,8848--0,9274 (4,26
p.p.), Random Forest 0,8803--0,9227 (4,24 p.p.), LSTM 0,8386--0,8790
(4,04 p.p.) e Naive Bayes 0,8214--0,8609 (3,95 p.p.). O achado
metodologicamente mais importante desta análise de sensibilidade é que o
**ranking relativo entre os sete modelos não muda em nenhum ponto do
intervalo**. Mesmo no pior caso, o LinearSVC permanece à frente e o
Naive Bayes atrás de todos. A conclusão qualitativa sobre qual modelo
usar é, portanto, robusta ao viés identificado, ao passo que o
valor absoluto do acerto validado não deve ser citado como um número
único sem essa ressalva.

**Tabela 2** Acerto validado por modelo e limite inferior de
sensibilidade ao viés de seleção (n = 9.096).

| Modelo | Acerto validado | IC95% | Limite inferior |
|---|---|---|---|
| LinearSVC | 0,9493 | 0,9447 -- 0,9538 | 0,9057 |
| SGD | 0,9392 | 0,9343 -- 0,9440 | 0,8961 |
| Regressão Logística | 0,9355 | 0,9302 -- 0,9404 | 0,8925 |
| Extra Trees | 0,9274 | 0,9222 -- 0,9325 | 0,8848 |
| Random Forest | 0,9227 | 0,9171 -- 0,9280 | 0,8803 |
| LSTM | 0,8790 | 0,8724 -- 0,8857 | 0,8386 |
| Naive Bayes | 0,8609 | 0,8533 -- 0,8680 | 0,8214 |

Fonte: elaborado pelos autores (2026). O limite inferior conta os 438
casos restritos como erro de todos os modelos.

A atualização completa dos modelos também resolveu uma discrepância
antes registrada entre o *ablation study* do LSTM (Subseção 4.8,
86,35%--87,68% conforme o particionamento) e o valor de referência então
vigente. O valor antigo vinha de uma versão desatualizada dos modelos, e
o valor atual do LSTM (0,8790) está muito mais próximo do que o
*ablation* já indicava. Isso confirma que o *ablation* nunca teve
problema metodológico de vazamento residual relevante, pois a
discrepância vinha da defasagem da referência, não de falha do
procedimento em si.

O patamar de acerto validado mudou de magnitude ao longo de recortes
sucessivos deste protocolo, por dois motivos distintos. Primeiro, o
crescimento genuíno da amostra validada revelou uma taxa de acerto mais
conservadora do que amostras menores sugeriam, por serem mais
concentradas em casos fáceis de confirmar. Segundo, uma versão
desatualizada dos modelos, já corrigida, havia subestimado o desempenho
real num recorte intermediário. A comparação entre recortes permanece,
portanto, descritiva.

**4.3 A classificação automática frente ao histórico: matriz de confusão
validada**

Um resultado adicional, obtido comparando a categoria histórica e a
classificação automática em produção contra a mesma decisão validada
pela conferência humana, qualifica a tese de rótulos ruidosos
apresentada na Introdução. Sobre as 9.096 decisões validadas, a
categoria histórica coincide com a decisão em 96,49% dos casos (8.777 de
9.096), acima do acerto da classificação automática frente à mesma
referência (90,15%; 8.200 de 9.096), repetindo em magnitude renovada o
padrão já observado em amostras menores. A matriz de confusão (Tabela 3)
mostra 8.200 casos em que ambas as fontes coincidem com a decisão, 319 em que
nenhuma coincide, 577 em que o histórico acerta e a classificação
automática erra, e **nenhum** caso em que a classificação automática
corrige uma categoria histórica considerada incorreta. Essa ausência
total tem explicação estrutural, discutida adiante.

O que o resultado sustenta com mais segurança é a outra metade da
premissa. Existe ruído real no histórico, pois 319 dos 9.096 casos
conferidos (3,51%, mais que o dobro da proporção observada em amostras
menores) têm categoria histórica que não coincide com a decisão final.
Esse ruído é proporcionalmente menor do que o risco de erro isolado da
classificação automática na mesma amostra (577 casos, 6,34%). A
implicação prática permanece, a classificação automática deve ser
tratada como instrumento de triagem e auditoria complementar ao
histórico, não como substituto ou árbitro superior a ele.

**Tabela 3** Matriz de confusão entre classificação automática e
histórico, contra a decisão validada (n = 9.096).

| | Histórico correto | Histórico incorreto |
|---|---|---|
| **Classificação automática correta** | 8.200 | 0 |
| **Classificação automática incorreta** | 577 | 319 |

Fonte: elaborado pelos autores (2026).

A ausência total de casos na célula "classificação automática correta /
histórico incorreto" tem explicação estrutural. Quando a categoria
decidida vem da confirmação da própria categoria histórica, a coluna
"histórico incorreto" fica automaticamente descartada para aquela linha.
A memória de decisão (Subseção 3.7) também reaproveita categorias já
validadas em rodadas anteriores, o que tende a alinhar a classificação
automática vigente com decisões já confirmadas. Essa célula-zero,
portanto, não demonstra que a classificação automática nunca corrija o
histórico, e uma auditoria dirigida da origem de cada decisão permanece
pendente.

**4.4 Confiança, calibração e faixas de decisão**

A classificação automática em produção mantém erro de calibração
esperado (ECE) de 0,0598 sobre a confiança bruta. Segmentada por faixa
de confiança e cruzada com a decisão validada pela conferência humana, a
faixa igual ou superior a 95% (n = 4.808; 34,4% da base) apresenta
concordância de 99,08% com o histórico e, mais relevante, acerto
validado de 96,79% sobre os 4.698 casos já decididos nessa faixa. O
resultado fica próximo da meta de referência do experimento (confiança
calibrada >= 95% associada a acerto real >= 95%), embora não a atinja
com folga.

Nas faixas inferiores (Tabela 4), a degradação de
desempenho acompanha a queda de confiança de forma consistente, do
patamar de 91,48% na faixa de 90 a 95% até 49,89% abaixo de 50%. Esse
comportamento corrobora a correlação positiva entre confiança bruta e
acerto, quantificada por Spearman entre 0,45 e 0,56 conforme o modelo
(Subseção 4.1), mesmo sem calibração formal aplicada a essa camada. A
faixa 80–90% (93,92%) supera
ligeiramente a faixa 90–95% (91,48%). Essa pequena inversão de monotonia
é plausível em dados reais com amostras desse tamanho, mas merece
acompanhamento em recortes futuros antes de ser tratada como padrão
estável.

**Tabela 4** Acerto validado por faixa de confiança da classificação
automática (n = 9.096).

| Faixa | n total | Concord. histórico | n validados | Acerto validado |
|---|---|---|---|---|
| < 50% | 3.972 | 42,35% | 876 | 49,89% |
| 50–70% | 1.504 | 73,40% | 741 | 83,94% |
| 70–80% | 972 | 87,45% | 654 | 94,95% |
| 80–90% | 1.499 | 87,99% | 1.118 | 93,92% |
| 90–95% | 1.210 | 92,98% | 1.009 | 91,48% |
| >= 95% | 4.808 | 99,08% | 4.698 | 96,79% |

Fonte: elaborado pelos autores (2026).

A Figura 2 apresenta esses mesmos valores em forma gráfica, tornando
visível o descolamento entre concordância com o histórico e acerto
validado nas faixas inferiores de confiança.

![](04_artigo/figuras/fig2_confianca_desfecho.pdf)

**Figura 2** Concordância com o histórico e acerto validado por faixa de
confiança bruta da classificação automática.

Fonte: elaborado pelos autores (2026).

**4.5 Reclassificação e ganho líquido**

A reclassificação dos chamados já conferidos produz resultados
heterogêneos entre modelos, medidos contra a decisão validada quando ela
existe e contra o histórico nos demais casos. O LSTM apresenta o maior
ganho líquido absoluto (+99; 670 corrigidos e 571 prejudicados), seguido
por Regressão Logística (+92) e LinearSVC (+73), e todos os sete modelos
apresentam ganho líquido positivo (Tabela 5). Esse resultado não autoriza aplicação
indiscriminada, porque o ganho combina parcelas comparadas contra a
decisão validada e contra o histórico, e já mudou de sinal para alguns
modelos entre recortes sucessivos. Isso reforça a decisão de não aplicar
reclassificação em massa por modelo. O ganho líquido, e não apenas a
acurácia agregada, funciona como critério operacional a ser reavaliado a
cada atualização da base, não como veredito permanente sobre um
classificador.

**Tabela 5** Ganho líquido de reclassificação por modelo.

| Modelo | Corrigidos | Prejudicados | Ganho líquido |
|---|---|---|---|
| LSTM | 670 | 571 | +99 |
| Regressão Logística | 245 | 153 | +92 |
| LinearSVC | 291 | 218 | +73 |
| Random Forest | 234 | 186 | +48 |
| SGD | 201 | 163 | +38 |
| Naive Bayes | 158 | 132 | +26 |
| Extra Trees | 237 | 226 | +11 |

Fonte: elaborado pelos autores (2026).

**4.6 Diagnóstico de taxonomia e ambiguidade estrutural
(Shannon/Jensen-Shannon)**

O diagnóstico de Shannon abrange oito fontes comparáveis, a
classificação automática em produção e os sete modelos avaliados. O
BERTimbau foi excluído por não ter treino concluído. A classificação
automática apresenta a maior diversidade de categorias previstas e a
menor divergência de Jensen-Shannon frente à distribuição histórica
(Tabela 6). No nível de chamado
individual, 3.277 dos 13.965 registros (23,5%) apresentam alta entropia
de votos entre as oito fontes, ou seja, desacordo estrutural relevante
entre arquiteturas distintas. Constitui critério de priorização de
auditoria distinto e complementar à baixa confiança de um único modelo.

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
relativamente alta (0,7848), provável reflexo de concentração extrema
em poucas categorias com alguma dispersão residual, não investigado em
detalhe neste artigo.

A Figura 3 mostra os quinze pares de categorias com maior confusão
recíproca, dominados pela fronteira entre climatização corretiva e
manutenção preventiva de ar condicionado, seguida pelas fronteiras
internas de estrutura predial.

![](04_artigo/figuras/fig3_top_confusoes.pdf)

**Figura 3** Quinze pares de categorias com maior confusão recíproca,
agregados entre modelos. Os códigos do eixo vertical são descritos na
Tabela Suplementar S2.

Fonte: elaborado pelos autores (2026).

**Tabela 6** Entropia de Shannon e divergência de Jensen-Shannon por
fonte de classificação.

| Fonte | Categorias previstas | Entropia normalizada | JS vs. histórico |
|---|---|---|---|
| Classificação automática | 53 | 0,8163 | 0,0286 |
| LSTM | 52 | 0,8105 | 0,0847 |
| Regressão Logística | 52 | 0,7805 | 0,0716 |
| SGD | 53 | 0,7745 | 0,0639 |
| LinearSVC | 53 | 0,7569 | 0,0575 |
| Extra Trees | 47 | 0,7193 | 0,0761 |
| Random Forest | 47 | 0,7124 | 0,0804 |
| Naive Bayes | 19 | 0,7848 | 0,1755 |

Fonte: elaborado pelos autores (2026).

**4.7 Custo computacional**

Nos recortes de comparação por lote (1.000 registros cada), os seis
modelos clássicos tiveram tempos de treino entre 1,14 s e 21,30 s. Não
há medição comparável de custo para LSTM ou BERTimbau, portanto não é
possível ordenar esses dois modelos frente aos demais. A tabela informa
exclusivamente as medições disponíveis para os modelos clássicos.

**Tabela 7** Custo computacional por lote de 1.000 registros.

| Modelo | Tempo de treino (s) | Tempo de inferência (s) | Acurácia neste lote |
|---|---|---|---|
| Naive Bayes | 1,14 | 0,07 | 0,539 |
| LinearSVC | 2,55 | 0,06 | 0,655 |
| SGD | 2,60 | 0,09 | 0,624 |
| Regressão Logística | 9,43 | 0,09 | 0,624 |
| Random Forest | 19,45 | 0,13 | 0,597 |
| Extra Trees | 21,30 | 0,14 | 0,610 |

Fonte: elaborado pelos autores (2026). A acurácia refere-se ao lote de
1.000 registros, não à base completa.

A Figura 4 cruza essas medições de custo com o acerto validado da Tabela
2 e mostra que o LinearSVC ocupa a posição mais favorável, com o maior
acerto validado a um custo de treino próximo do menor observado.

![](04_artigo/figuras/fig4_tradeoff_custo.pdf)

**Figura 4** Trade-off entre acerto validado e tempo de treino, modelos
clássicos.

Fonte: elaborado pelos autores (2026).

**4.8 Comportamento do LSTM: curva de aprendizado e *ablation***

A Figura 5 mostra a curva real de aprendizado do LSTM sobre os 13.965
exemplos e 53 categorias. O treino parou por interrupção antecipada após
11 épocas, com menor perda de validação na época 8 e maior acurácia de
validação na época 10 (0,6722). O padrão indica saturação precoce,
consistente com a hipótese de que *embeddings* treinados do zero são
insuficientes para um corpus deste porte (Subseção 3.4.1).

![](04_artigo/figuras/fig5_curva_aprendizado_lstm.pdf)

**Figura 5** Curva de aprendizado do LSTM por época, perda e acurácia em
treino e validação.

Fonte: elaborado pelos autores (2026).

Uma auditoria investigou por que o *ablation* da Figura 6 reportava
acerto validado muito acima do valor oficial então vigente para a mesma
arquitetura do LSTM. Duas causas foram identificadas. Primeiro, um
vazamento metodológico real, mas de magnitude modesta: no *KFold*
aleatório por linha usado originalmente, 4.250 de 9.096 linhas
validadas de teste (46,72%) tinham duplicata textual normalizada no
treino. O *ablation* foi refeito com *GroupKFold* por hash de texto
normalizado, excluindo do treino grupos textuais presentes no teste. A
correção reduziu a configuração atual (64 unidades, *dropout* de 0,5) de
87,68% para 86,35% (7.854/9.096), uma correção pequena (1,33 ponto
percentual). Segundo, e principal, o valor de referência usado na
comparação (0,7471, Subseção 4.2) vinha de uma versão desatualizada dos
modelos. O reprocessamento completo dos sete modelos (Subseção 4.2)
produziu um novo valor do LSTM de 0,8790, muito mais próximo dos 0,8635
deste *ablation* corrigido. A diferença residual de 1,55 pontos
percentuais é plausivelmente atribuível a diferenças remanescentes de
protocolo entre o número de *folds* e o esquema de treino usados em cada
avaliação.

Em síntese, o *ablation* nunca teve problema metodológico grave, e a
maior parte da discrepância original vinha de comparar um resultado
recente com uma referência desatualizada. A ordenação relativa
das quatro variantes testadas, que variam o número de unidades
recorrentes e a taxa de *dropout*, é interpretada como evidência preliminar de baixa
sensibilidade do LSTM a esses hiperparâmetros nesta base (diferença
total entre a melhor e a pior variante inferior a 4 pontos percentuais),
não como indicação forte de que a arquitetura atual esteja
subotimizada.

![](04_artigo/figuras/fig6_ablation_lstm.pdf)

**Figura 6** *Ablation* do LSTM, quatro variantes de unidades
recorrentes e *dropout*, avaliadas por *GroupKFold* contra a decisão
validada.

Fonte: elaborado pelos autores (2026).

**4.9 Robustez estatística: pressupostos e testes de sensibilidade**

Antes de qualquer teste inferencial, foram verificados os pressupostos de
robustez estatística usuais, a saber, outliers, homogeneidade de
variância, normalidade, desbalanceamento entre categorias, colinearidade
entre modelos, relação entre confiança e acerto e independência das
observações, adaptando o protocolo de exploração de dados de Zuur,
Ieno e Elphick (2010) da resposta contínua da ecologia para a resposta
categórica de classificação de chamados (n = 13.965). O teste de
Shapiro-Wilk (SHAPIRO; WILK, 1965) rejeita a normalidade a 5% para os
sete modelos sobre a concordância por turno, confirmando com números a
justificativa não paramétrica já adotada na Subseção 3.5; a variância de
confiança entre modelos também é fortemente heterogênea, reforçando essa
escolha. O teste de Friedman (FRIEDMAN, 1937) confirma diferença global
entre os modelos comparáveis, e o *post-hoc* de Nemenyi (NEMENYI, 1963)
reproduz a mesma ordem das Tabelas 1 e 2, com poder estatístico menor que
o McNemar par a par (MCNEMAR, 1947). Corrigido por Holm-Bonferroni
(HOLM, 1979), o McNemar é significativo em praticamente todas as 21
comparações entre os sete modelos, e confirma que o **LinearSVC é
estatisticamente superior ao LSTM e ao Naive Bayes**. A única exceção,
sem significância, é o par SGD contra Random Forest. A verificação de
colinearidade revela um efeito colateral relevante. Quatro dos sete
modelos têm confiança altamente correlacionada entre si, com Fator de
Inflação de Variância elevado (MARQUARDT, 1970), o que ajuda a explicar
por que nenhum *ensemble* supera o LinearSVC isolado (Subseção 4.2),
dado que modelos redundantes pouco acrescentam em informação
independente a um comitê (DIETTERICH, 2000). A correlação entre confiança bruta e acerto é
positiva e significativa em todos os sete modelos (Spearman e
ponto-bisserial, *p* < 0,001), pré-requisito para a calibração discutida
na Subseção 4.4 (GUO *et al.*, 2017). A verificação completa dos oito
pressupostos, item a item, com as tabelas de correlação, autocorrelação
e o Kappa de Fleiss entre modelos, está disponível como Material
Suplementar.

**5. DISCUSSÃO**

A comparação entre concordância histórica (Subseção 4.1) e desempenho
validado (Subseção 4.2) revela um padrão que mudou de magnitude ao longo
da elaboração deste artigo, à medida que a conferência humana cresceu e
uma versão desatualizada dos modelos foi corrigida (Subseção 4.8). O
acerto validado do LinearSVC (94,93%) hoje supera com folga sua
concordância com o histórico (80,29%), depois de um período intermediário
em que os dois patamares se aproximaram. Nenhuma dessas mudanças permite
estimar o desempenho real da base completa, pois a conferência humana
prioriza divergências e casos críticos em vez de amostrar ao acaso.
Verifica-se, portanto, que os resultados descrevem a amostra conferida,
sem representar a população de chamados (COCHRAN, 1977).

Um segundo mecanismo de viés, estrutural e mais específico, soma-se à
não aleatoriedade da amostra. A regra de decisão da verdade validada
(Subseção 3.7) exclui do denominador do acerto validado os chamados em
que o avaliador julgou erradas todas as fontes conferidas, designados
"restritos". Dos 9.534 chamados conferidos, 438 (4,6%) estão nessa
condição e ficam fora dos 9.096 usados na Subseção 4.2. Como esses casos
não têm categoria de referência contra a qual comparar a predição de
cada modelo, o acerto validado reportado como número pontual constitui um
limite superior, pois mede o desempenho apenas onde pelo menos uma fonte
já estava correta por construção.

A análise de sensibilidade recalcula um limite inferior, tratando os 438
restritos como erro de todos os modelos, e apura amplitude de 3,95 a
4,36 pontos percentuais conforme o modelo. A amplitude é relevante em
termos absolutos, mas o *ranking* relativo entre os sete modelos
permanece inalterado em qualquer ponto do intervalo. Duas implicações
decorrem daí. A conclusão qualitativa sobre qual modelo priorizar é
robusta a esse viés, ao passo que o valor pontual de acerto validado
exige a ressalva do intervalo sempre que for citado isoladamente ou
comparado a *benchmarks* externos. Esse mecanismo também explica a
célula zerada da matriz de confusão (Subseção 4.3). Os casos em que o
avaliador não confirma nenhuma fonte como correta, justamente onde a
classificação automática teria mais chance de acertar sozinha, ficam
fora da amostra decidida por construção.

A distinção entre concordância e acerto validado permanece
metodologicamente necessária, e a matriz da Subseção 4.3 mostra por quê.
Quando as duas fontes divergem da decisão final, o histórico está correto
com frequência muito maior (577 casos) do que a classificação automática
corrige um erro genuíno do registro original, com a ressalva estrutural
já discutida sobre a célula zerada. O achado preserva a premissa de que
a categoria histórica não é verdade absoluta, já que persiste taxa real
de erro confirmado no registro original, em 3,51% dos casos conferidos.
Esse valor supera o observado em recortes anteriores, de amostra menor, o
que desaconselha tratá-lo como estabilizado. Ao mesmo tempo, o resultado
adverte contra a leitura oposta e igualmente equivocada, de que baixa
concordância com o histórico implicaria acerto da classificação
automática. Cabe destacar que a validação humana cumpre aqui função
insubstituível, pois só ela distingue as duas situações, que a taxa de
concordância isolada confunde.

Na amostra conferida, o LinearSVC lidera tanto a concordância histórica
quanto o acerto validado (Subseções 4.1 e 4.2). O resultado descreve
esta base e esta amostra, sem estabelecer superioridade generalizável de
classificadores lineares sobre arquiteturas neurais. A comparação de
custo permanece restrita aos seis modelos clássicos da Tabela 7.

O resultado da reclassificação (Subseção 4.5) introduz uma nuance
operacional importante, pois o ganho líquido de corrigir chamados já
classificados não é uniforme entre modelos nem estável ao longo do
tempo. Em recortes anteriores, três dos classificadores clássicos
avaliados (SGD, Random Forest e Extra Trees) tinham ganho líquido
negativo. No corpus atual, todos os sete modelos apresentam ganho
positivo, embora a amplitude varie de +11 (Extra Trees) a +99 (LSTM).
Essa oscilação reforça o argumento. Decisões de reclassificação em
produção devem ser tomadas por modelo e reavaliadas a cada atualização
da base, com base no ganho líquido medido naquele momento, e não
generalizadas a partir do desempenho médio de concordância ou acerto
validado. Um modelo pode ser competitivo na classificação inicial e,
ainda assim, não ser bom candidato a reclassificar decisões já tomadas.

A camada de entropia de Shannon e divergência de Jensen-Shannon
(Subseção 4.6) não substitui as métricas supervisionadas ou a validação
humana, mas amplia o repertório de governança do experimento ao separar
três fenômenos que a acurácia isolada tende a confundir, o erro de
modelo, a ambiguidade genuína da taxonomia institucional e a
heterogeneidade natural da distribuição de chamados. A identificação de
3.277 chamados (23,5% da base) com alto desacordo estrutural entre as
oito fontes comparáveis oferece um critério de priorização de auditoria
distinto do simples corte por baixa confiança de um único classificador,
e complementa a fila já construída a partir da conferência humana. A
classificação automática em produção, não o LSTM isolado, lidera tanto a
diversidade de predições quanto a menor divergência frente ao histórico
(Subseção 4.6). Esse diagnóstico descreve o corpus analisado e não
substitui acurácia ou validação humana.

A meta estabelecida como critério de sucesso do protocolo associa
confiança calibrada igual ou superior a 95% a acerto real igual ou
superior a 95% (Subseção 4.4). A faixa alta de confiança da classificação
automática chega a 96,79% de acerto validado sobre 4.698 casos
conferidos, de modo que a meta fica próxima, embora sem a folga que
recortes de amostra menor sugeriam. Pondera-se que a confiança utilizada
é bruta (*softmax* ou *decision_function*), sem calibração formal por
Platt ou isotônica (PLATT, 1999; GUO *et al.*, 2017), o que mantém a
leitura provisória.

Essa retração acompanha o crescimento da conferência e repete o padrão já
discutido para o acerto validado geral. A amostra validada cobre hoje
68,3% da base, mas sua composição original privilegia divergências e
casos de menor confiança, o que pode ter inflado o acerto validado nas
faixas altas quando a cobertura era menor e a conferência tendia a
confirmar o esperado. A confirmação definitiva da meta depende de
concluir a conferência sobre os 31,7% ainda não verificados, e a leitura
de meta atingida só se sustenta a partir daí.

**Limitações**

Os dados provêm de uma única instituição federal de ensino superior,
com textos em português brasileiro e taxonomia institucional própria.
Estender o desempenho relatado a outras instituições, taxonomias ou
idiomas exige validação externa, ainda não realizada.

A amostra conferida por avaliadores humanos não é probabilística, porque
prioriza divergências entre modelo e histórico e casos de maior
criticidade. Os números de acerto validado descrevem, portanto, a
amostra conferida, e não estimam por inferência o desempenho da base
completa (COCHRAN, 1977). Uma regra de decisão adicional exclui do
denominador os casos em que nenhuma fonte conferida foi confirmada como
correta, 4,6% dos chamados conferidos. A análise de sensibilidade
correspondente mostra amplitude de 3,95 a 4,36 pontos percentuais entre
o cenário mais otimista e o mais conservador, sem alterar o ranking
relativo entre os modelos.

Duas limitações dizem respeito aos modelos. O BERTimbau, único
classificador contextual previsto no protocolo, não teve o ajuste fino
concluído e ficou fora de todas as comparações. O LSTM treina seus
*embeddings* do zero, sem vetores pré-treinados em português, condição
que penaliza redes neurais em corpora de porte médio e ajuda a explicar
seu desempenho inferior ao dos modelos lineares.

**Contribuição para a governança preditiva da manutenção**

A contribuição deste artigo não termina na categoria atribuída a cada
chamado. Ao converter texto livre em categoria, criticidade e confiança
auditáveis, o protocolo produz a camada de dados estruturados sobre a
qual a gestão pública de manutenção predial pode operar de forma
preditiva, e não apenas reativa. Previsão de demanda por categoria,
priorização de intervenções segundo critérios de sustentabilidade e
leitura territorial do parque edificado dependem, todas, de uma base
classificada de modo confiável. Este artigo entrega essa fundação e
demonstra que ela exige conferência humana para se sustentar.

**6. CONSIDERAÇÕES FINAIS**

A contribuição central deste artigo é metodológica. Em vez de apenas
eleger o melhor classificador, o protocolo separa duas grandezas que a
literatura de classificação de chamados costuma tratar como uma só, a
concordância com o rótulo histórico e o acerto validado por conferência
humana. Essa separação depende de uma camada de validação que registra a
decisão do avaliador, veta categorias já rejeitadas e trava as
confirmadas, convertendo cada conferência em conhecimento persistente.
Foi ela que permitiu medir o desempenho contra uma referência construída,
e não contra um rótulo administrativo aceito por conveniência.

O resultado prático confirma que a classificação automática serve à
triagem e à auditoria, mas não dispensa a conferência humana. Sobre
9.096 chamados com decisão validada, o LinearSVC alcançou 94,93% de
acerto validado (IC95%: 94,47%--95,38%), à frente dos demais seis
modelos, e nenhum dos três *ensembles* avaliados o superou com
significância estatística. A recomendação operacional é usar o LinearSVC
isolado, com calibração, escolha que o custo computacional reforça, já
que os modelos lineares treinam em uma fração do tempo exigido pelos
*ensembles* de árvores sem perder acerto. A matriz de confusão mostra
por que a conferência continua necessária, pois o histórico
administrativo também contém erros confirmados, em 3,51% dos casos
conferidos. Esses valores descrevem a amostra conferida, com a ressalva
de representatividade já registrada nas Limitações. As divergências
entre modelos e histórico, por sua vez, deixaram de ser ruído descartado
e passaram a alimentar a fila de revisão taxonômica, com 3.277 chamados
sinalizados por alto desacordo estrutural entre as fontes.

Duas frentes dão continuidade ao trabalho. A primeira é a validação
externa em outras instituições federais de ensino superior, para testar
se o padrão observado se mantém sob taxonomias e volumes distintos, com
o BERTimbau incorporado à comparação e a calibração formal aplicada por
modelo. A segunda é o uso desta camada classificada como entrada de
modelos de previsão de demanda e de priorização multicritério de
intervenções, lacuna já apontada na literatura de gestão de manutenção,
que raramente incorpora dados operacionais de chamados. Nas duas
direções, o protocolo aqui descrito funciona como pré-requisito, pois
previsão e priorização só são confiáveis sobre uma base cuja
classificação seja, ela própria, auditável.

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
público, disponibilizados pelos autores em repositório de código aberto,
onde também está descrita a estrutura completa dos dados.

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
