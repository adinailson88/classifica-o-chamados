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
concluído ou métrica própria nesta consolidação. O diferencial metodológico reside na distinção entre
concordância com o histórico administrativo e acerto validado por
revisão humana, tratando a categoria histórica como referência
preliminar imperfeita — distinção que se mostrou decisiva: o acerto
validado por conferência humana (9.096 decisões travadas) revelou-se
mais conservador do que a concordância com o histórico sugeria, à medida
que a amostra de conferência cresceu. Como a seleção não é aleatória e
prioriza divergências e casos críticos, esses resultados não estimam o
desempenho da base completa (COCHRAN, 1977). Resultados indicam superioridade do LinearSVC
tanto na concordância com o histórico (acurácia de 80,29%,
IC95%: 79,62%--80,95%) quanto no acerto validado (94,93%, IC95%:
94,47%--95,38%), enquanto o LSTM apresentou concordância de 68,13% e
acerto validado de 87,90% (números atualizados em 25/07/2026, após
limpeza completa e rematerialização dos sete modelos comparáveis a
partir do zero — ver Subseções 4.1, 4.2 e 4.9). A normalidade da concordância por turno foi
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
extension, without completed training or its own metric in this
consolidation. The methodological contribution lies in distinguishing agreement with
administrative history from human-validated accuracy — a distinction
that is necessary for the present protocol: human-validated accuracy
(9,096 locked decisions) is reported only for the partial, non-random
reviewed sample, which prioritizes divergences and critical cases.
Results indicate LinearSVC superiority both
in agreement with history (80.34% accuracy, 95%CI: 79.69%--80.97%) and
in human-validated accuracy (79.89%, 95%CI: 78.99%--80.73%), while LSTM
achieved 68.47% agreement and 74.71% validated accuracy. Normality was
rejected for all models, supporting non-parametric tests (Friedman,
Cochran Q, McNemar, bootstrap). Computational cost is incorporated as an
evaluation dimension.*

***Keywords:** building maintenance; work-order classification; natural
language processing; noisy labels; human validation; predictive
governance.*

**1. INTRODUÇÃO**

A manutenção predial em instituições federais de ensino superior (IFES)
envolve decisões recorrentes de triagem, categorização, priorização e
alocação de equipes, agravadas pela dispersão territorial, pela
diversidade de sistemas prediais e pela restrição orçamentária que
historicamente limita o custeio dessas atividades a patamares inferiores
a 2% do orçamento institucional (MARTINS; ESPEJO, 2024; PAMPANA *et
al.*, 2022). Sistemas informatizados de registro de chamados, como
plataformas GLPI e ambientes de *helpdesk*, tornaram-se, nesse contexto,
não apenas instrumentos de solicitação, mas bases de conhecimento
institucional sobre falhas, recorrências e padrões de uso, cujo
potencial analítico permanece amplamente subutilizado (MORAIS; PAULA;
REIS, 2023; MOHAMMED; AMOAH, 2025).

A exploração analítica dessas bases é limitada por ao menos três fatores
estruturais. O primeiro reside na natureza textual curta, heterogênea e
frequentemente incompleta dos registros, uma vez que chamados de
manutenção predial são redigidos em linguagem técnica fragmentária, com
abreviações locais e jargões de equipe que dificultam a aplicação direta
de modelos genéricos de processamento de linguagem natural (PLN)
(SUNDARAM; ZEID, 2025). O segundo fator é o desbalanceamento entre
categorias, dado que demandas recorrentes de climatização, elétrica e
hidrossanitária tendem a concentrar grande parte da base, ao passo que
categorias raras dispõem de poucos exemplos para treinamento
supervisionado (LI *et al.*, 2024). O terceiro fator, possivelmente o
mais crítico do ponto de vista metodológico, é a qualidade dos rótulos
históricos, pois a categoria registrada no momento do chamado pode
resultar de interpretação rápida, classificação por conveniência
operacional ou taxonomia ainda não estabilizada, de modo que o histórico
administrativo constitui evidência importante, porém não verdade
absoluta (ZHANG *et al.*, 2025; KEJRIWAL *et al.*, 2024).

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

O presente artigo parte de uma tese metodológica específica: em bases
reais de chamados de manutenção, a avaliação de modelos não deve ser
reduzida à pergunta sobre qual classificador mais concorda com a
categoria histórica. Conforme Zhang *et al.* (2025), rótulos ruidosos em
PLN afetam o desempenho dos classificadores e podem ampliar o consumo de
recursos computacionais, exigindo métodos robustos de tratamento de
ruído. Kejriwal *et al.* (2024) reforçam que *benchmarks* rotulados por
humanos podem conter variabilidade relevante, questionando a prática de
assumir uma única verdade absoluta quando há julgamento subjetivo
envolvido. Dessa forma, a pergunta central deve ser mais ampla: em que
medida os modelos reproduzem o histórico, em que medida auxiliam na
identificação de inconsistências desse histórico e de que maneira a
revisão humana pode converter divergências entre inteligência artificial
e registro administrativo em melhoria progressiva da taxonomia
institucional.

Com base em chamados reais da Universidade Federal do Sul da Bahia
(UFSB), propõe-se uma comparação multimodelo de classificadores de texto
aplicados a chamados de manutenção predial em português brasileiro. A
base experimental contém 13.965 chamados não vazios (na consolidação
vigente de 23/07/2026), distribuídos em 55 categorias históricas, e os
campos textuais considerados agregam informações do título e da
descrição do chamado, além de informações associadas à ordem de serviço.
O estudo compara modelos clássicos baseados em TF-IDF (Naive Bayes,
Regressão Logística, LinearSVC, SGD, Random Forest e Extra Trees) com
abordagem neural LSTM bidirecional. O BERTimbau é mantido como extensão
planejada, mas não integra as comparações enquanto não houver treino
concluído e métricas próprias rastreáveis. O
objeto de avaliação, portanto, não é apenas o classificador isolado, mas
o protocolo de governança preditiva que articula aprendizado de máquina,
auditoria estatística, custo computacional e validação humana, em
consonância com a perspectiva de manutenção baseada em evidências
preconizada pela NBR 5674 (ABNT, 2012).

Os objetivos específicos do estudo são: (i) apresentar um protocolo de
comparação multimodelo para classificação de chamados reais de
manutenção predial universitária em português brasileiro; (ii)
distinguir concordância com rótulo histórico de acerto validado,
evitando equiparar categoria histórica a *ground truth* incontestável;
(iii) avaliar desempenho por métricas globais, métricas balanceadas,
intervalos de confiança e testes estatísticos pareados adequados a dados
não normais; (iv) incorporar custo computacional como dimensão de
decisão operacional; e (v) transformar divergências entre IA e histórico
em evidências para revisão taxonômica e retroalimentação da base de
treino.

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

Fonte: elaborado pelos autores (2026), gerado a partir da descrição desta
subseção (`04_artigo/figuras/fig1_pipeline_governanca.png`).

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
classificados em turnos. Na consolidação vigente (23/07/2026), o número
de chamados elegíveis já cresceu para 13.965, em 55 categorias
históricas (uma categoria adicional frente à contagem original de 54, em
função de uma migração de nomenclatura registrada na auditoria técnica
que acompanha este capítulo). Os resultados da Seção 4 utilizam esse
recorte mais recente; eventuais diferenças frente a valores publicados
em versões preliminares deste texto refletem o crescimento da base e a
ampliação da conferência humana, não uma mudança metodológica.

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

O desenho experimental compara sete modelos materializados nesta
consolidação. Os classificadores clássicos adotam representação
TF-IDF e algoritmos de aprendizado supervisionado amplamente
consolidados na literatura de classificação textual (JOACHIMS, 1998;
PEDREGOSA *et al.*, 2011): Naive Bayes Multinomial, como *baseline*
probabilístico; Regressão Logística, com calibração natural e boa
interpretabilidade; LinearSVC, combinando margem linear e escores de
decisão normalizados por *softmax* apenas para ordenação de confiança
(sem calibrador de Platt ajustado; PLATT, 1999); SGD, como alternativa
eficiente para matrizes esparsas de grande dimensão; Random Forest e
Extra Trees, como representantes de métodos não lineares baseados em
*ensemble* de árvores. A LSTM Bidirecional foi construída com camada de
*embedding* de 8.000 termos e 128 dimensões, camada recorrente
bidirecional de 64 unidades (GRAVES; SCHMIDHUBER, 2005), *dropout* de
0,5 e camada densa com ativação *softmax*, treinada com parada
antecipada, avaliada tanto na comparação *out-of-fold* (Subseção 4.1)
quanto na Etapa 1 oficial de produção, com *fallback* de Random Forest.

O oitavo modelo planejado é um transformador pré-treinado em português
(BERTimbau, `neuralmind/bert-base-portuguese-cased`). Seu fluxo de ajuste
fino é separado, condicionado ao avanço da base validada e pode recorrer a
*fallback* técnico quando as dependências não estão disponíveis. O estado
do treino nesta consolidação é de dados insuficientes, com treino
adiado; por isso o modelo não integra tabelas,
rankings, testes inferenciais nem conclusões comparativas deste artigo.

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
(1996) — com 95% de confiança. A
*macro*-F1 e a *balanced accuracy* são essenciais face ao
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
recentemente (NOMA *et al.*, 2021). Quando múltiplas comparações são
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
desbalanceadas, precisamente por avaliar cada exemplo em algum fold em
vez de descartar uma fração fixa dos dados do treino (KOHAVI, 1995) — e
esta base é desbalanceada por natureza (55 categorias históricas, várias
com suporte de dígito único; Tabela Suplementar S1). Para não apenas
invocar essa recomendação em abstrato, comparou-se empiricamente o
protocolo atual (*k*-fold, 5 partições) com um *holdout* fixo de 15% dos
dados, sobre os sete modelos comparáveis e a mesma base completa (n =
13.965; a comparação usa 52 das 55 categorias da Tabela Suplementar
S1 — três categorias raras não reapareceram entre duas consolidações
consecutivas, provavelmente por renomeação concorrente com este
experimento).

A tentativa de estratificar esse *holdout* por categoria — o que a
maioria dos protocolos faz por padrão — **falhou explicitamente** no
*scikit-learn*, com o erro "*the least populated class in y has only 1
member, which is too few*", confirmando que a base tem pelo menos uma
categoria com um único exemplo. No *holdout* aleatório simples que
substituiu a tentativa de estratificação, quatro categorias inteiras
ficaram sem nenhum exemplo de teste — "Manutenção Preventiva",
"Manutenção Preventiva \> Aplicação cupinicida", "Suprimentos / Apoio
Técnico \> Limpeza de equipamentos, ambiente e mobiliário" e
"Suprimentos / Apoio Técnico \> Transporte" —, tornando sua métrica de
desempenho indefinida nesse desenho, ainda que o *k*-fold as avalie
integralmente (Tabela Suplementar S1).

A acurácia global variou pouco entre os dois protocolos (média de
−0,30 ponto percentual no *holdout* frente ao *k*-fold entre os sete
modelos, variando de −1,93 a +0,73 p.p. por modelo), mas a *macro*-F1 —
que pondera todas as categorias igualmente, e não apenas as mais
frequentes — piorou no *holdout* em seis dos sete modelos, com queda
média de 1,24 ponto percentual e um pior caso de −3,98 p.p. no
LinearSVC (0,6083 no *k*-fold contra 0,5685 no *holdout*; Tabela
Suplementar S4). Em suma: um *holdout* fixo não melhora a estimativa de
desempenho global de forma relevante nesta base e piora sistematicamente
a avaliação das categorias raras — exatamente o padrão que a literatura
antecipa para corpora pequenos e desbalanceados como este (KOHAVI,
1995), o que confirma o protocolo *k*-fold como a escolha mais adequada
e não apenas a mais conveniente.

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
trata o registro do GLPI como referência preliminar e não como verdade
absoluta; e o desempenho validado por conferência humana (Subseções 4.2
e 4.3), calculado exclusivamente sobre os chamados com decisão travada
pela memória M/N/P. Na consolidação vigente (23/07/2026), a base elegível
contém 13.965 chamados e a conferência humana já cobre 9.534 chamados
(68,3% da base), dos quais 9.096 com decisão travada e sem conflito
(65,1% da base) e 438 casos restritos (categoria eliminada, ainda sem
decisão travada). Esse crescimento — de 4.737 conferências (33,9% da
base) em 16/07/2026 para 9.534 (68,3%) nesta consolidação — quase dobra a
cobertura em relação à versão anterior deste protocolo e, como discutido
na Subseção 4.2 e na Seção 5, revela um padrão de desempenho
sensivelmente mais conservador do que a amostra menor sugeria.

**4.1 Concordância com o histórico (base completa)**

*Nota de rastreabilidade (25/07/2026)*: os sete modelos comparáveis foram
**rematerializados por completo** nesta data (abas `CLASSIF__<modelo>`
limpas e reclassificadas do zero, `run` via workflow com credencial),
depois de a Subseção 4.9 revelar que a materialização anterior (16-17/07)
estava desatualizada. Os números abaixo refletem essa rematerialização.

A comparação contra a categoria histórica, sobre a base completa (n =
13.965, com intervalo de confiança por bootstrap a 95%), mantém o
LinearSVC na liderança, com acurácia de 0,8029 (IC95%:
0,7962--0,8095), seguido por Extra Trees (0,7885), Random Forest
(0,7799), SGD (0,7765), Regressão Logística (0,7677), Naive Bayes
(0,6996) e LSTM (0,6813). O teste de Cochran Q confirma diferença global
entre os sete modelos materializados (Q = 2680,70; p < 0,001); a comparação exclui o BERTimbau,
cujo estado é `sem_dados`. O Kappa de Cohen entre cada modelo e o histórico acompanha
ordenamento muito próximo (LinearSVC 0,7880; Extra Trees 0,7707; Random
Forest 0,7612; SGD 0,7603; Regressão Logística 0,7513; Naive Bayes
0,6703; LSTM 0,6598). A ordem entre os sete modelos permanece a mesma da
consolidação anterior — a rematerialização não alterou o ranking, só o
patamar absoluto. A oitava fonte de
classificação, a Etapa 1 oficial (executor LSTM/RF de produção, coluna G
da planilha), mantém concordância de 77,65% e confiança média de 71,67%
nesta consolidação, posicionando-se entre SGD e Regressão Logística
nesta métrica — não é diretamente comparável ao LSTM *out-of-fold* da
Tabela 1, pois combina LSTM com *fallback* de Random Forest conforme a
regra de produção (Subseção 3.4), não um único modelo isolado. Essa fonte
não foi rematerializada nesta rodada e pode estar sujeita à mesma
defasagem temporal identificada na Subseção 4.9.

**Tabela 1** Concordância com a categoria histórica, base completa (n = 13.965)

| Modelo | Acurácia | IC95% bootstrap | Kappa vs. histórico |
|---|---|---|---|
| LinearSVC | 0,8029 | 0,7962 -- 0,8095 | 0,7880 |
| Extra Trees | 0,7885 | 0,7817 -- 0,7949 | 0,7707 |
| Random Forest | 0,7799 | 0,7732 -- 0,7864 | 0,7612 |
| SGD | 0,7765 | 0,7697 -- 0,7833 | 0,7603 |
| Regressão Logística | 0,7677 | 0,7608 -- 0,7745 | 0,7513 |
| Naive Bayes | 0,6996 | 0,6921 -- 0,7070 | 0,6703 |
| LSTM (out-of-fold) | 0,6813 | 0,6733 -- 0,6888 | 0,6598 |

Fonte: elaborado pelos autores (2026), com base em rematerialização
completa dos sete modelos (n = 13.965) em 25/07/2026. O modelo
BERTimbau foi deliberadamente excluído por não representar treino
concluído.

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

*Nota de rastreabilidade (25/07/2026)*: esta subseção foi **regenerada
apos a rematerializacao completa** dos sete modelos (ver nota da
Subseção 4.1). A tabela anterior (gerada em 24/07/2026 04:55, a partir da
materializacao de 16-17/07/2026) reportava acerto validado entre 0,71 e
0,80; a diferenca em relacao aos numeros atuais confirma a hipotese
registrada na Subseção 4.9 -- a materializacao antiga estava
desatualizada, nao havia um problema de metodologia na avaliacao em si.

A avaliação contra a verdade validada pela memória de decisão M/N/P (n =
9.096 decisões travadas) confirma a mesma liderança da Subseção 4.1: o
LinearSVC permanece o melhor modelo isolado, com
acerto validado de 0,9493 (IC95%: 0,9447--0,9538), seguido por SGD
(0,9392), Regressão Logística (0,9355), Extra Trees (0,9274), Random
Forest (0,9227), LSTM (0,8790) e Naive Bayes (0,8609). A diferença entre o primeiro e o segundo colocado é
pequena em termos absolutos (1,01 ponto percentual), mas estatisticamente
significativa (McNemar, p ~ 3,21 × 10⁻⁹). Com os sete modelos comparáveis
já consistentes (sem a linha legada `transformer_ft`), os ensembles
puderam ser avaliados: maioria ponderada (0,9445), confiança calibrada
máxima (0,9436) e maioria simples (0,9422) — nenhum supera o LinearSVC
isolado com significância (McNemar p < 0,05 em favor do LinearSVC nos
três casos). Conclusão: **não vale combinar modelos nesta consolidação**;
usar LinearSVC isolado, com calibração.

*Vies estrutural da seleção da amostra validada (achado de 25/07/2026)*:
o número pontual de acerto validado acima é o **limite superior** de um
intervalo, não uma estimativa isenta de viés. A "verdade validada" usada
neste cálculo só existe para um chamado quando pelo menos uma
conferência marca "Correto" — ou seja, quando
o histórico, a IA oficial ou a reclassificação está confirmadamente
certa. Dos 9.534 chamados com alguma conferência preenchida, 438 (4,6%)
caem no status "restrito": o avaliador julgou **todas** as fontes
conferidas erradas para aquele chamado (344 casos só com o histórico
marcado errado; 94 com histórico e IA oficial marcados errados
simultaneamente), sem indicar qual seria a categoria certa. Esses 438
casos são **excluídos do denominador** de qualquer acerto validado por
modelo, porque não existe categoria de referência contra a qual comparar
a predição. Isso torna a amostra de 9.096 decisões, por construção, um
subconjunto em que pelo menos uma fonte (histórico ou IA) estava correta
— o que infla mecanicamente o acerto validado de qualquer modelo que
tenda a concordar com o histórico ou com a IA oficial, independentemente
da qualidade real do modelo nos casos mais difíceis (exatamente os que
ficaram de fora).

Para tornar esse viés visível sem descartar a métrica, calculamos um
**limite inferior** de sensibilidade: o acerto de cada modelo caso os 438
restritos fossem incluídos no denominador e contados como erro para
**todos** os modelos (pior caso possível, já que não sabemos a categoria
certa desses casos — nenhum modelo pode receber crédito neles). O
intervalo `[limite inferior, limite superior]` substitui o número
pontual como leitura honesta do acerto validado: LinearSVC 0,9057--0,9493
(amplitude 4,36 p.p.), SGD 0,8961--0,9392 (4,31 p.p.), Regressão
Logística 0,8925--0,9355 (4,30 p.p.), Extra Trees 0,8848--0,9274 (4,26
p.p.), Random Forest 0,8803--0,9227 (4,24 p.p.), LSTM 0,8386--0,8790
(4,04 p.p.) e Naive Bayes 0,8214--0,8609 (3,96 p.p.). O achado
metodologicamente mais importante desta análise de sensibilidade é que o
**ranking relativo entre os sete modelos não muda em nenhum ponto do
intervalo** — mesmo no pior caso, o LinearSVC permanece à frente e o
Naive Bayes permanece atrás de todos. Isso significa que a conclusão
qualitativa (qual modelo usar) é robusta ao viés identificado, mas o
valor absoluto do acerto validado não deve ser citado como um número
único sem essa ressalva.

**Tabela 2** Acerto validado contra a verdade decidida M/N/P (n = 9.096) e
intervalo de sensibilidade ao viés de seleção (n = 9.096 a 9.534)

| Modelo | Acerto validado (limite superior) | IC95% | Limite inferior (pior caso) |
|---|---|---|---|
| LinearSVC | 0,9493 | 0,9447 -- 0,9538 | 0,9057 |
| SGD | 0,9392 | 0,9343 -- 0,9440 | 0,8961 |
| Regressão Logística | 0,9355 | 0,9302 -- 0,9404 | 0,8925 |
| Extra Trees | 0,9274 | 0,9222 -- 0,9325 | 0,8848 |
| Random Forest | 0,9227 | 0,9171 -- 0,9280 | 0,8803 |
| LSTM | 0,8790 | 0,8724 -- 0,8857 | 0,8386 |
| Naive Bayes | 0,8609 | 0,8533 -- 0,8680 | 0,8214 |

Fonte: elaborado pelos autores (2026), com base em limpeza completa e
rematerialização dos 8 modelos a partir do zero, em 25/07/2026.
O limite inferior foi recalculado por derivação matemática direta a
partir do novo acerto validado, mantendo fixo o número de casos
restritos (438), que depende apenas das conferências humanas, não da
rematerialização dos modelos; a composição desses casos (344 só com o
histórico errado, 94 com histórico e IA errados) permanece a publicada
em 25/07/2026. A tabela exclui o BERTimbau (treino ainda não concluído) e
uma variante identificada como artefato de um *fallback* silencioso
para o LSTM, cuja causa já foi corrigida (ver Limitações).

*Nota metodológica sobre a resolução da discrepância do LSTM (ver Figura
6/Subseção 4.9)*: a Subseção 4.9 havia sinalizado que o ablation study do
LSTM (86,35%--87,68% conforme o particionamento) discordava em ~11-13
pontos percentuais do valor oficial então vigente (0,7471). A
rematerialização completa desta subseção confirma a causa: o valor de
0,7471 vinha de uma materialização de `CLASSIF__lstm` datada de
16-17/07/2026, mais de uma semana desatualizada. O novo valor oficial do
LSTM (0,8790, rematerializado em 25/07/2026) está muito mais próximo do
que o ablation já indicava, confirmando que **o ablation nunca teve um
bug de vazamento residual relevante** — o problema real era a defasagem
temporal da materialização oficial usada como referência, não uma falha
metodológica do ablation em si. A ressalva de "resultado suspeito" da
Figura 6 é mantida apenas como registro histórico da investigação (ver
Subseção 4.9), não como pendência ativa.

*Nota metodológica sobre a mudança de patamar entre consolidações
(92--96% em 16/07/2026 → 71--80% em 24/07/2026 → 86--95% em
25/07/2026)*: a primeira queda (16/07 → 24/07) refletiu o crescimento
genuíno da amostra validada (4.681 → 9.096 decisões); a leitura mais
provável, retomada na Seção 5, é que a amostra menor de 16/07 estava mais
concentrada em casos já fáceis de confirmar como corretos, e a ampliação
da cobertura revelou uma taxa de acerto real mais baixa nessa
consolidação. A segunda mudança (24/07 → 25/07), documentada acima, foi
causada por uma materialização desatualizada dos modelos, não por
crescimento de amostra (a amostra validada permanece 9.096 nas duas
consolidações). Ainda assim, como a seleção da conferência humana não é
probabilística, a comparação entre consolidações continua sendo
descritiva, não inferencial (COCHRAN, 1977); não é possível estimar, a
partir dessas consolidações, o desempenho da base completa.

**4.3 A classificação oficial frente ao histórico: matriz de confusão
validada**

Um resultado adicional, obtido comparando a categoria histórica e a
classificação da IA oficial (coluna G, executor LSTM/RF) contra a mesma
verdade decidida pela memória M/N/P, qualifica a tese de rótulos
ruidosos apresentada na Introdução. Sobre as 9.096 decisões travadas
desta consolidação, a categoria histórica (GLPI) coincide com a decisão
em 96,49% dos casos (8.777 de 9.096), acima do acerto da IA oficial
frente à mesma verdade (90,15%; 8.200 de 9.096) — repetindo, em
magnitude renovada, o padrão já observado em 16/07/2026 (98,54% contra
95,08%, sobre uma amostra bem menor). A matriz de confusão IA×histórico
mostra 8.200 casos em que ambos coincidem com a decisão, 319 em que
nenhum dos dois coincide, 577 em que o histórico acerta e a IA erra, e
**nenhum** caso, nesta consolidação, em que a IA corrige uma categoria
histórica que a decisão considerou incorreta. Diferentemente da
observação anterior (13 casos de correção da IA sobre 4.737
conferências), a ausência total dessa célula nesta base maior tem
explicação estrutural discutida abaixo, não deve ser lida
automaticamente como "a IA nunca corrige o histórico". O que o resultado
sustenta com mais segurança é a outra metade da premissa: existe ruído
real no histórico — 319 dos 9.096 casos conferidos (3,51%, quase o
triplo da proporção observada em 16/07/2026) têm categoria histórica
que não coincide com a decisão final —, mas esse ruído é
proporcionalmente menor do que o risco de erro isolado da IA nesta
mesma amostra (577 casos, 6,34%). A implicação prática permanece: a IA
deve ser tratada como instrumento de triagem e auditoria complementar ao
histórico, não como substituto ou árbitro superior a ele.

**Tabela 4** Matriz de confusão IA×histórico contra a verdade decidida (M/N/P) (n = 9.096)

| | Histórico correto | Histórico incorreto |
|---|---|---|
| **IA correta** | 8.200 | 0 |
| **IA incorreta** | 577 | 319 |

Fonte: elaborado pelos autores (2026), com dados de 23/07/2026. Leitura:
8.200 casos em que ambos (IA e histórico) coincidem com a categoria
decidida; 319 em que
nenhum dos dois coincide; 577 em que o histórico acerta e a IA erra; e **zero**
casos em que a IA acerta e o histórico erra. A ausência total de casos na
célula "IA correta / histórico incorreto" chama atenção e tem explicação
estrutural, não é necessariamente evidência de que a IA nunca corrige o
histórico: quando a categoria decidida vem de confirmação da própria
categoria histórica, a célula "histórico incorreto" fica
automaticamente descartada para aquela linha; a memória de decisão
(Subseção 3.7) também reaproveita categorias já travadas em
consolidações anteriores, o que tende a alinhar a classificação vigente
da IA com decisões já confirmadas. Essa célula-zero não deve, portanto,
ser lida como evidência de que a IA nunca corrige o histórico, sem uma
auditoria dirigida da origem de cada decisão, ainda pendente.

**4.4 Confiança, calibração e faixas de decisão**

A calibração bruta da Etapa 1 oficial mantém ECE histórico de 0,0598
nesta consolidação. Quando segmentada por faixa de confiança e cruzada
com a verdade decidida pela memória de decisão (M/N/P) — não mais com a
marcação bruta de uma única coluna de conferência (ver observação
metodológica adiante) —, a faixa igual ou superior a 95% de confiança (n = 4.808; 34,4% da base)
apresenta concordância de 99,08% com o histórico e, mais relevante,
acerto validado de 96,79% sobre os 4.698 casos já com decisão travada
nessa faixa — resultado que fica muito próximo da meta de referência do
experimento (confiança calibrada >= 95% associada a acerto real >= 95%),
embora não a atinja com folga. Nas faixas inferiores, a degradação de
desempenho acompanha a queda de confiança de forma consistente (90–95%:
acerto validado 91,48%; 80–90%: 93,92%; 70–80%: 94,95%; 50–70%: 83,94%;
inferior a 50%: 49,89%), o que corrobora a correlação positiva entre
confiança bruta e acerto — quantificada nesta consolidação por Spearman
entre 0,45 e 0,56 conforme o modelo (Subseção 4.1) —,
mesmo sem calibração formal (Platt/isotônica) aplicada a essa camada. A
faixa 80–90% (93,92%) supera ligeiramente a faixa 90–95% (91,48%) —
pequena inversão de monotonia plausível em dados reais com amostras
desse tamanho, mas que merece acompanhamento nas próximas consolidações
antes de ser tratada como padrão estável.

**Tabela 3** Acerto validado por faixa de confiança bruta, executor
oficial (Etapa 1), contra a verdade decidida M/N/P (n = 9.096 decisões travadas)

| Faixa | n total | Concord. histórico | n validados | Acerto validado |
|---|---|---|---|---|
| < 50% | 3.972 | 42,35% | 876 | 49,89% |
| 50–70% | 1.504 | 73,40% | 741 | 83,94% |
| 70–80% | 972 | 87,45% | 654 | 94,95% |
| 80–90% | 1.499 | 87,99% | 1.118 | 93,92% |
| 90–95% | 1.210 | 92,98% | 1.009 | 91,48% |
| >= 95% | 4.808 | 99,08% | 4.698 | 96,79% |

Fonte: elaborado pelos autores (2026), com dados de 23/07/2026. A
amostra de conferência prioriza divergências e casos de menor confiança
na composição original, não
é aleatória — a leitura acima deve ser tomada como piso/teto conforme o
desenho da conferência, não como taxa de acerto sobre amostra representativa.

*Nota metodológica*: até 22/07/2026, esta tabela comparava a classificação do
executor apenas contra a marcação bruta da coluna N (CONFERÊNCIA IA)
isolada, o que produzia acerto validado artificialmente igual a 100% em toda
faixa de confiança, inclusive abaixo de 50% — a coluna N, no uso real, quase
nunca recebe marcação "Errado" (o erro da IA costuma ficar registrado via M,
sem tocar N). Corrigido em 23/07/2026: a comparação passou a usar a
categoria decidida pela memória de decisão (M/N/P), a mesma verdade da
Subseção 4.2, eliminando o viés de seleção.

**4.5 Reclassificação e ganho líquido**

A reclassificação dos chamados já conferidos produz resultados
heterogêneos entre modelos, medidos contra a verdade validada quando
travada e contra o histórico nos demais casos. Na consolidação de
24/07/2026, o LSTM apresenta o maior ganho líquido absoluto (+99; 670
corrigidos e 571 prejudicados), seguido por Regressão Logística (+92) e
LinearSVC (+73). Todos os sete modelos materializados apresentam ganho
líquido positivo nesta execução. Esse resultado não autoriza aplicação
indiscriminada: o ganho combina parcelas comparadas contra verdade validada
e contra histórico, e pode mudar a cada rodada. Reforça-se a decisão de não aplicar
reclassificação em massa de forma indiscriminada por modelo, tratando o
ganho líquido, e não apenas a acurácia agregada, como critério de
decisão operacional por classificador — e de reavaliar esse critério a
cada rodada, não como veredito permanente: a execução de 30/06/2026
havia apontado SGD e Random Forest como negativos; ambos passaram a
positivo nesta consolidação.

**Tabela 5** Ganho líquido de reclassificação por modelo (execução de 24/07/2026)

| Modelo | Total reclassificado | Corrigidos | Prejudicados | Ganho líquido | Reuso de decisão humana |
|---|---|---|---|---|---|
| LSTM | 13.905 | 670 | 571 | +99 | 8.805 |
| Regressão Logística | 13.932 | 245 | 153 | +92 | 8.727 |
| LinearSVC | 13.965 | 291 | 218 | +73 | 8.856 |
| Random Forest | 13.912 | 234 | 186 | +48 | 8.719 |
| SGD | 13.965 | 201 | 163 | +38 | 8.771 |
| Naive Bayes | 13.826 | 158 | 132 | +26 | 8.623 |
| Extra Trees | 13.899 | 237 | 226 | +11 | 8.713 |

Fonte: elaborado pelos autores (2026), com dados de 24/07/2026. *Nota
metodológica*: o total reclassificado do Random Forest chegava a 18.049
nesta mesma tabela em versão anterior deste texto, valor que excedia o
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
a Etapa 1 oficial e os sete modelos materializados. O BERTimbau foi excluído por não ter treino concluído. A Etapa 1
oficial apresenta a maior diversidade
de categorias previstas e a menor divergência de Jensen-Shannon frente à
distribuição histórica. No nível de chamado individual, 3.277 dos 13.965
registros (23,5%) apresentam alta entropia de votos entre as oito fontes,
ou seja,
desacordo estrutural relevante entre arquiteturas distintas — um
critério de priorização de auditoria diferente e complementar à simples
baixa confiança de um único modelo. No nível de categoria, a análise
aponta 76 ocorrências de alta ambiguidade nas predições (com suporte
mínimo de 30 registros por categoria); a interpretação detalhada de
quais categorias específicas concentram essa ambiguidade, e sua
sobreposição com os pares de maior confusão recíproca identificados na
etapa de cruzamento de taxonomia, permanece como candidata a inspeção
qualitativa dirigida — nesta consolidação, essa sobreposição não pôde
ser detalhada com exemplos de categorias por causa da corrupção de
acentuação identificada na Subseção 4.8. O que a camada Shannon oferece
é a priorização estatística de onde essa inspeção deve começar, não a
decisão de fusão ou desambiguação de categorias, que continua sendo
humana. Naive Bayes chama atenção por combinar a menor cobertura de
categorias (19, ante 47–53 dos demais modelos) com entropia normalizada
relativamente alta (0,7848) — provável reflexo de concentração extrema
em poucas categorias com alguma dispersão residual, não investigado em
detalhe nesta rodada.

**Tabela 6** Entropia de Shannon e divergência de Jensen-Shannon por fonte de classificação (24/07/2026)

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

Fonte: elaborado pelos autores (2026), com dados regenerados em
24/07/2026. O BERTimbau foi excluído explicitamente
por não haver treino concluído. No nível de categoria, o resumo
aponta 76 ocorrências de alta ambiguidade e 3.277 chamados com alta
entropia de votos entre modelos. Naive Bayes chama atenção por combinar a
menor cobertura de categorias (19, ante 47–53 dos demais) com entropia
normalizada relativamente alta (0,7848) — provável reflexo de concentração
extrema em poucas categorias com alguma dispersão residual, não investigado
em detalhe nesta rodada.

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
em 18/07/2026 — não reexecutada nesta consolidação; único registro de
custo computacional disponível para os modelos clássicos. LSTM
e BERTimbau não constam deste arquivo. A acurácia
reportada aqui é sobre um lote de 1.000 registros (não a base completa) e
serve só para contextualizar o trade-off custo×desempenho desta subseção —
não usar como substituto das Tabelas 1 e 2.

**4.8 Figuras**

*Atualização de dados (24/07/2026)*: as figuras foram geradas a partir dos
JSONs vigentes do painel, da aba viva de métricas por categoria e dos treinos
executados por workflow com credencial (scripts `matplotlib`, ver
`04_artigo/figuras/`). A Figura 4 usa códigos de categoria para preservar a
legibilidade; o mapeamento completo código-categoria está na Tabela
Suplementar S2.

![Figura 2 — Confiança bruta × concordância com o histórico × acerto validado, por faixa de confiança (executor oficial, Etapa 1, 23/07/2026).](04_artigo/figuras/fig2_confianca_desfecho.png)

**Figura 2** Confiança bruta × concordância com o histórico × acerto validado,
por faixa de confiança (executor oficial, Etapa 1). Mesmos números da
Tabela 3 (Subseção 4.4), em forma gráfica.

Fonte: elaborado pelos autores (2026), com dados de 23/07/2026.

![Figura 3 — Trade-off entre acerto validado e custo computacional (tempo de treino), modelos clássicos.](04_artigo/figuras/fig3_tradeoff_custo.png)

**Figura 3** Trade-off entre acerto validado (conferência humana, 23/07/2026)
e custo computacional (tempo de treino, lote de 1.000 registros, 18/07/2026),
modelos clássicos. LSTM e BERTimbau não constam desta figura por não
terem registro de tempo de treino no mesmo arquivo (Tabela 7, Subseção
4.7).

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
C01-C10 usados no eixo vertical são descritos na Tabela Suplementar S2
(`04_artigo/figuras/tabela_S2_codigos_categorias_fig4.csv`).

Fonte: elaborado pelos autores (2026), com dados de 24/07/2026.

![Figura 5 — Curva de aprendizado do LSTM por época.](04_artigo/figuras/fig5_curva_aprendizado_lstm.png)

**Figura 5** Curva real de aprendizado do LSTM gerada pelo workflow
`30137383907`, com 13.965 exemplos e 53 categorias. O treino foi interrompido
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
percentual). Segundo, e principal: o valor oficial de referência usado
na comparação (0,7471, Subseção 4.2) vinha de uma materialização datada
de 16-17/07/2026, mais de uma semana desatualizada em relação à base
viva. A rematerialização completa dos sete modelos em 25/07/2026 (ver
nota de rastreabilidade na Subseção 4.2) produziu um novo valor oficial
do LSTM de 0,8790 — muito mais próximo dos 0,8635 deste *ablation*
corrigido (diferença residual de 1,55 pontos percentuais, plausivelmente
atribuível a diferenças remanescentes de protocolo:
`k_folds=3` no *ablation* contra `k_folds=5` na materialização oficial, e
treino por *fold* isolado contra o esquema *out-of-fold* padrão).
**Conclusão**: o *ablation* nunca teve um problema metodológico grave; a
maior parte da discrepância original vinha de comparar um resultado
fresco com uma referência oficial desatualizada. A ordenação relativa das
quatro variantes testadas (`units=128, dropout=0,3` como melhor, seguida
de `units=128, dropout=0,5`, `units=64, dropout=0,5` e `units=64,
dropout=0,3`) é interpretada como evidência preliminar de baixa
sensibilidade do LSTM a esses hiperparâmetros nesta base (diferença total
entre a melhor e a pior variante inferior a 4 pontos percentuais), não
como indicação forte de que a arquitetura atual esteja subotimizada.

Fonte: elaborado pelos autores (2026).

**4.10 Robustez estatística: pressupostos e testes de sensibilidade**

Esta subseção reúne, com números reais (não hipotéticos), os
pressupostos verificados antes de qualquer teste inferencial e os
resultados completos dos testes de robustez usados nas Subseções
anteriores — hoje apenas citados pelo nome no corpo do texto (Subseção
3.5). O protocolo de exploração de dados de Zuur, Ieno e Elphick (2010),
originalmente proposto para respostas contínuas em ecologia, foi adaptado
aqui para a resposta categórica de classificação de chamados (n = 13.965;
dados de 25/07/2026); passos sem
análogo direto na resposta categórica recebem justificativa explícita em
vez de serem omitidos.

*1) Outliers*: a distribuição da confiança bruta por modelo não apresenta
valores extremos relevantes pela regra 1,5×IQR (distância interquartil;
TUKEY, 1977) — regra amplamente adotada, mas que pressupõe distribuições
próximas da normal, ressalva sistematizada na revisão taxonômica de
métodos de detecção de outliers de Hodge e Austin (2004) e ilustrada, por
analogia de aplicação em dados reais assimétricos fora do domínio de ML,
por Lima *et al.* (2017): em métricas bibliométricas univariadas, os
autores mostram que a regra clássica de Tukey detecta mais ou menos
outliers do que uma versão ajustada pela assimetria da distribuição,
conforme o sinal e a intensidade dessa assimetria — o mesmo cuidado se
aplica aqui, já que a confiança bruta por modelo também é uma distribuição
real, não necessariamente simétrica —, exceto no LinearSVC, cujo escore
normalizado por *softmax* (não calibrado; Subseção 3.4) produz 51 valores
atipicamente altos em 13.965 — consistente com a natureza do escore de
margem, não com um problema de dados.

*2) Homogeneidade de variância*: a razão entre a maior e a menor variância
de confiança entre os sete modelos é 38,53, muito acima do limiar de
preocupação (4; ZUUR; IENO; ELPHICK, 2010) — heterogeneidade que já
motivava, mesmo antes deste detalhamento, a escolha por métodos robustos
e não paramétricos.

*3) Normalidade*: o teste de Shapiro-Wilk (SHAPIRO; WILK, 1965), apontado
por estudos comparativos de poder estatístico como um dos mais sensíveis
entre os testes de normalidade usuais para amostras pequenas e moderadas
(RAZALI; WAH, 2011), achado reproduzido por comparações mais recentes com
outras alternativas, como Anderson-Darling, Qui-quadrado e
Kolmogorov-Smirnov (OGUNLEYE; OYEJOLA; OBISESAN, 2018) — situação mais
próxima dos 931 turnos por modelo aqui analisados do que dos 13.965
chamados individuais —, aplicado sobre a concordância por turno rejeita a
normalidade a 5% para os sete modelos (Tabela 8), confirmando com
números — e não apenas por afirmação — a justificativa não paramétrica já
usada na Subseção 3.5.

**Tabela 8** Teste de normalidade de Shapiro-Wilk sobre a concordância por
turno (n = 931 turnos por modelo)

| Modelo | *W* de Shapiro-Wilk | *p* | Normal a 5%? |
|---|---|---|---|
| LSTM | 0,9720 | 2,13 × 10⁻¹² | Não |
| Naive Bayes | 0,9688 | 3,08 × 10⁻¹³ | Não |
| Regressão Logística | 0,9443 | 3,15 × 10⁻¹⁸ | Não |
| SGD | 0,9405 | 7,35 × 10⁻¹⁹ | Não |
| Random Forest | 0,9424 | 1,50 × 10⁻¹⁸ | Não |
| Extra Trees | 0,9365 | 1,75 × 10⁻¹⁹ | Não |
| LinearSVC | 0,9313 | 2,95 × 10⁻²⁰ | Não |

Fonte: elaborado pelos autores (2026).

*4) Excesso de categorias raras*: das 52 categorias históricas com
suporte identificável nesta consolidação, 27 (52%) têm suporte abaixo de
70 chamados — o análogo, na resposta categórica, do excesso de zeros
tratado no protocolo original. É o mesmo desbalanceamento já discutido na
comparação empírica holdout vs. *k*-fold (Subseção 3.5) e tratado aqui
com *macro*-F1 e intervalos de confiança em vez de acurácia isolada.

*5) Colinearidade entre modelos*: tratando a confiança de cada modelo
como uma covariável e calculando o Fator de Inflação de Variância (VIF;
formalizado por MARQUARDT, 1970, como diagnóstico de colinearidade em
regressão) entre elas, quatro modelos (Regressão Logística: 26,89; SGD:
28,20; Random Forest: 24,89; Extra Trees: 22,10) excedem em muito o
limiar de preocupação (VIF > 3; ZUUR; IENO; ELPHICK, 2010) — limiar mais
conservador que a regra de bolso mais difundida (VIF > 10), cuja
adequação geral é questionada por O'Brien (2007), que recomenda avaliar o
impacto real da colinearidade caso a caso em vez de aplicar um corte
único, ressalva reforçada por revisões recentes sobre mitigação de
multicolinearidade em modelos de aprendizado de máquina
(CHAN *et al.*, 2022) —, contra valores baixos para LinearSVC (3,64), Naive Bayes (3,74)
e LSTM (3,04). Essa colinearidade alta entre quatro dos sete modelos é
consistente com — e ajuda a explicar — o achado da Subseção 4.2 de que
nenhum ensemble supera o LinearSVC isolado: modelos com confiança
altamente correlacionada contribuem pouco em informação independente a
um comitê, no mesmo sentido em que a literatura de agregação de
classificadores associa ganho de ensemble à diversidade entre membros, não
apenas ao número de membros (DIETTERICH, 2000).

*6) Relação entre confiança e acerto*: correlação de Spearman
(SPEARMAN, 1904) e ponto-bisserial (TATE, 1954; formulação e
interpretação como tamanho de efeito também em KORNBROT, 2014) — esta
última apropriada porque o acerto é uma variável binária (certo/errado)
contra a confiança contínua — entre confiança bruta e acerto (histórico), positiva e
estatisticamente significativa (*p* < 0,001) em todos os sete modelos —
da mais fraca (LinearSVC, ρ = 0,479) à mais forte (LSTM, ρ = 0,637) —,
confirmando que a confiança carrega sinal genuíno sobre o acerto em todos
os modelos, pré-requisito para a calibração da Subseção 4.4
(GUO *et al.*, 2017), cuja relação entre confiança e acurácia real em
redes neurais modernas segue sendo revisitada e refinada na literatura
recente (MINDERER *et al.*, 2021).

**Tabela 9** Correlação entre confiança bruta e acerto contra o histórico

| Modelo | Ponto-bisserial (r) | Spearman (ρ) | *p* |
|---|---|---|---|
| LSTM | 0,6607 | 0,6373 | < 0,001 |
| Naive Bayes | 0,5885 | 0,5642 | < 0,001 |
| Random Forest | 0,5462 | 0,5320 | < 0,001 |
| Extra Trees | 0,5343 | 0,5187 | < 0,001 |
| Regressão Logística | 0,4536 | 0,4688 | < 0,001 |
| SGD | 0,4413 | 0,4605 | < 0,001 |
| LinearSVC | 0,4326 | 0,4791 | < 0,001 |

Fonte: elaborado pelos autores (2026).

*7) Interações*: a interação modelo × categoria — inaplicável ao
*coplot* contínuo do protocolo original — é tratada pela matriz de
confusões cruzadas (Subseção 4.3; Figura 4).

*8) Independência das observações*: a autocorrelação da concordância por
turno (defasagem 1 a 5), diagnosticada pela função de autocorrelação
amostral (ACF; BOX; JENKINS, 1970), é positiva e não desprezível em
todos os modelos (por exemplo, LinearSVC: 0,362 na defasagem 1, decaindo
para 0,221 na defasagem 5), e a estatística de Durbin-Watson
(DURBIN; WATSON, 1950) fica entre 1,34 e 1,44 para os sete modelos —
abaixo do valor de referência 2,0 que indicaria ausência de
autocorrelação serial nos resíduos. Isso indica que turnos consecutivos
não são inteiramente independentes (provável efeito de chamados
textualmente semelhantes chegando em sequência), uma limitação a
declarar explicitamente: os intervalos de confiança por turno podem
estar levemente subestimados, pois erros-padrão calculados sob a hipótese
de independência tendem a ser menores que os reais quando há
autocorrelação positiva (DURBIN; WATSON, 1950). A tendência ao longo dos
turnos é de leve alta na concordância para seis dos sete modelos
(*p* < 10⁻⁷ em cada, por regressão linear simples do índice do turno
sobre a concordância; Naive Bayes é o único estável, *p* = 0,51),
compatível com o crescimento e a depuração progressiva da base ao longo
do experimento, não com um artefato de curto prazo. (Nota de
transparência: não foi encontrada, até o fechamento desta rodada, uma
referência recente e suficientemente confiável que discuta a
autocorrelação/ACF ou o teste de Durbin-Watson especificamente em
contexto de aprendizado de máquina — a lacuna permanece declarada em vez
de preenchida com uma citação fraca; as referências primárias de Box e
Jenkins (1970) e Durbin e Watson (1950) continuam sustentando o método em
si.)

**Testes globais e correção para múltiplas comparações** — Cochran Q
(COCHRAN, 1950), teste não paramétrico para diferenças entre três ou mais
proporções pareadas (aqui, acerto binário por modelo sobre os mesmos
chamados), confirma diferença global entre os sete modelos comparáveis
(Q = 2984,07; *gl* = 6; *p* < 0,001; Subseção 4.1). O teste de Friedman
(FRIEDMAN, 1937), alternativa não paramétrica à ANOVA de medidas
repetidas baseada em postos, aplicado sobre 14 janelas de 1.000 chamados,
confirma diferença global entre os seis
modelos clássicos com tempo de treino medido (estatística = 44,43;
*p* = 1,89 × 10⁻⁸); o *ranking* médio de Nemenyi (NEMENYI, 1963), teste
*post-hoc* usual após Friedman, aplicado aqui seguindo o protocolo de
comparação estatística de classificadores consolidado por Demšar (2006)
(diferença crítica = 2,015 a α = 0,05), reproduz a mesma ordem das
Tabelas 1 e 2 — LinearSVC (1,68) à frente de Extra Trees (2,46), Random
Forest (3,29), SGD (3,36), Regressão Logística (4,29) e Naive Bayes
(5,93) —, mas com poder estatístico bem menor que o McNemar sobre a base
completa: apenas 5 das 15 comparações par a par superam a diferença
crítica (as que envolvem os extremos da tabela — LinearSVC vs. Regressão
Logística e vs. Naive Bayes; Extra Trees, Random Forest e SGD vs. Naive
Bayes). Isso não contradiz os resultados anteriores; reflete que o
Nemenyi opera sobre só 14 blocos (janelas), enquanto o McNemar a seguir
opera sobre as 13.965 observações pareadas — poder muito maior para
detectar diferenças entre modelos adjacentes no *ranking*, um contraste
que ilustra na prática por que Demšar (2006) recomenda cautela ao
interpretar a ausência de significância no teste *post-hoc* de Nemenyi
como equivalência prática entre modelos.

As 21 comparações pareadas de McNemar (MCNEMAR, 1947) entre os sete
modelos, corrigidas pelo método sequencial de Holm-Bonferroni (HOLM,
1979) a α = 0,05, são significativas em 20 dos 21 pares — a única
exceção é SGD vs. Random Forest (*p* = 0,0902, acima do limiar de Holm
de 0,05 para essa posição), indicando que esses dois modelos têm
desempenho estatisticamente indistinguível entre si na base completa,
ainda que ambos difiram significativamente dos demais.

Por fim, o Kappa de Fleiss
(FLEISS, 1971) — generalização do Kappa de Cohen para mais de dois
avaliadores, aqui os sete modelos avaliando a mesma categoria — entre as
sete IAs é 0,7719, concordância classificada como "substancial" pela
escala de referência de Landis e Koch (1977, intervalo 0,61–0,80); Kappa
e alternativas como o AC1 de Gwet respondem de forma diferente à
prevalência desigual entre categorias (WONGPAKARAN *et al.*, 2013),
ressalva relevante dado o desbalanceamento já discutido no item 4 desta
subseção, ainda que o presente uso — concordância entre classificadores,
não entre avaliadores humanos — não seja o cenário original desses
estudos —,
coerente com todos os modelos aprenderem o mesmo padrão subjacente da
taxonomia histórica, divergindo principalmente nas categorias raras e
ambíguas (Subseção 4.6).

Fonte: elaborado pelos autores (2026), com dados de 25/07/2026.

**5. DISCUSSÃO**

A comparação entre concordância histórica (Subseção 4.1) e desempenho
validado (Subseção 4.2) revela um padrão que mudou de magnitude ao longo
da elaboração deste capítulo e que, por isso, merece registro explícito
antes de qualquer outra leitura, agora em três consolidações: na de
16/07/2026, sobre 4.681 decisões travadas, o acerto validado (92–96%)
superava com folga a concordância com o histórico (70–80%); na de
23-24/07/2026, sobre 9.096 decisões — quase o dobro —, os dois patamares
se aproximaram (concordância 68–80%, acerto validado 71–80%), com o
LinearSVC em 80,34% de concordância e 79,89% de acerto validado; na
consolidação vigente (25/07/2026), após a rematerialização completa dos
sete modelos ter corrigido uma defasagem de mais de uma semana na
materialização anterior (Subseção 4.9), o acerto validado voltou a superar
a concordância histórica (concordância 68–80%, acerto validado 86–95%),
com o LinearSVC em 80,29% de concordância e 94,93% de acerto validado. A
primeira transição (16/07 → 24/07) refletiu crescimento genuíno da amostra
validada; a segunda (24/07 → 25/07) refletiu correção de uma
materialização desatualizada dos modelos, não mudança na amostra validada
(9.096 nas duas consolidações). Nenhuma das mudanças observadas entre
consolidações permite estimar o
desempenho real da base completa: a conferência humana não é aleatória e
prioriza divergências e casos críticos. Portanto, os resultados devem
ser lidos como descrição da amostra conferida, não como estimativa
representativa da população de chamados (COCHRAN, 1977).

Além da não aleatoriedade da amostra, identificamos nesta rodada um
segundo mecanismo de viés, estrutural e mais específico: a própria regra
de decisão da verdade validada (Subseção 3.7) exclui do denominador de
qualquer acerto validado os chamados em que o avaliador humano julgou
todas as fontes conferidas erradas ("restritos"). Dos 9.534 chamados com
alguma conferência preenchida nesta consolidação, 438 (4,6%) estão nessa
condição e ficam fora dos 9.096 usados na Subseção 4.2. Como não existe,
para esses 438 casos, uma categoria de referência contra a qual comparar
a predição de cada modelo, o acerto validado reportado como número
pontual é, na verdade, um limite superior: mede o desempenho apenas nos
casos em que pelo menos uma fonte (histórico ou IA) já estava certa, por
construção. A análise de sensibilidade publicada em
`04_artigo/figuras/sensibilidade_vies_validacao.json` recalcula um limite
inferior (pior caso, contando os 438 restritos como erro de todos os
modelos) e mostra que a amplitude do intervalo é de 3,95 a 4,36 pontos
percentuais conforme o modelo — relevante em termos absolutos, mas sem
alterar o ranking relativo entre os sete modelos em nenhum ponto do
intervalo. A implicação para a leitura deste capítulo é dupla: a
conclusão qualitativa (qual modelo priorizar) é robusta a esse viés, mas
o valor pontual de acerto validado não deveria ser citado isoladamente,
nem comparado a benchmarks externos, sem a ressalva do intervalo. Esse
mecanismo também ajuda a explicar por que a célula "IA correta / histórico
incorreto" da matriz de confusão (Subseção 4.3) permanece em zero: casos
em que o avaliador não confirma nenhuma fonte como correta — justamente
onde a IA teria mais chance de estar certa sozinha, sem confirmação do
histórico — são os que ficam de fora da amostra decidida por construção,
não porque a IA de fato nunca acerte quando o histórico erra.

Ainda assim, a distinção entre concordância e acerto validado continua
metodologicamente necessária, e a matriz IA×histórico (Subseção 4.3)
mostra por quê: quando os dois discordam da decisão final, o histórico
está correto com frequência muito maior (577 casos) do que a IA corrige
um erro genuíno do histórico (0 casos nesta consolidação — com a ressalva
estrutural já registrada na Subseção 4.3 sobre essa célula específica).
Esse achado não invalida a premissa metodológica de que a categoria
histórica não deve ser tratada como verdade absoluta — ainda existe uma
taxa real de erro confirmado no registro original (3,51% dos casos
conferidos nesta consolidação, quase o triplo do 1,2% observado em
16/07/2026, o que por si só recomenda cautela contra tratar mesmo esse
número como estabilizado) —, mas recomenda cautela contra a leitura
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
Os ensembles serão reavaliados somente após a regeneração da avaliação
final sem o BERTimbau.

O resultado da reclassificação (Subseção 4.5) introduz uma nuance
operacional importante: o ganho líquido de corrigir chamados já
classificados não é uniforme entre modelos nem estável ao longo do
tempo. Na execução de 30/06/2026, três dos seis classificadores clássicos
avaliados (SGD, Random Forest e Extra Trees) tinham ganho líquido
negativo; na execução de 23/07/2026, com o LSTM incluído na comparação,
apenas Extra Trees e Naive Bayes permanecem negativos — SGD e Random
Forest passaram a positivo. Essa oscilação, por si só, reforça o
argumento: decisões de reclassificação em produção devem ser tomadas por
modelo e reavaliadas a cada rodada, com base no ganho líquido medido
naquele momento, e não generalizadas a partir do desempenho médio de
concordância ou acerto validado, nem tratadas como um veredito
permanente sobre determinado classificador — um modelo pode ser
competitivo na classificação inicial e, ainda assim, não ser um bom
candidato a reclassificar decisões já tomadas em todas as rodadas.

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

A meta de confiança calibrada igual ou superior a 95% associada a acerto
real igual ou superior a 95% (Subseção 4.4), estabelecida como critério
de sucesso deste protocolo, fica próxima de ser atingida, mas não é mais
alcançada com folga como sugeria a consolidação anterior: a faixa alta
de confiança da Etapa 1 oficial chega a 96,79% de acerto validado sobre
4.698 casos conferidos (ante 99,73% sobre 3.284 casos em 16/07/2026),
ainda que a confiança utilizada seja bruta (softmax/decision_function),
não formalmente calibrada por Platt ou isotônica (PLATT, 1999; GUO *et al.*, 2017). Essa queda de 99,73%
para 96,79% na própria faixa de mais alta confiança, à medida que a
conferência quase dobrou de tamanho, é o mesmo padrão discutido acima
para o acerto validado geral, e reforça a mesma cautela: a amostra
validada, embora agora cubra 68,3% da base (ante 33,9% em 16/07/2026),
ainda prioriza divergências e casos de menor confiança na sua composição
original, o que pode ter inflado artificialmente o acerto validado nas
faixas de alta confiança das consolidações anteriores, onde a
conferência tendia a simplesmente confirmar o que já era esperado. A
confirmação definitiva da meta depende da conclusão da conferência
humana sobre a fração ainda não conferida da base (31,7%), e a trajetória
observada entre 16/07 e 23/07/2026 recomenda que a leitura de "meta já
atingida" só seja aceita quando essa conferência estiver
substancialmente mais completa, não a cada consolidação intermediária.

As limitações do estudo foram atualizadas em relação à versão anterior,
com seis ajustes relevantes.

Primeiro, a amostra validada deixou de ser uma amostra piloto de 305
casos (2,2% da base) e passou a cobrir 9.534 conferências (68,3% da
base, 9.096 decisões travadas sem conflito), o que aumenta
substancialmente a robustez estatística das Subseções 4.2 a 4.4 — mas,
como discutido acima, essa mesma ampliação já revelou que a robustez
estatística de uma amostra intermediária não garante estabilidade da
magnitude do resultado, apenas de sua direção geral (a ordem entre
modelos manteve-se; o patamar de acerto, não).

Segundo, os conflitos de conferência (casos em que duas fontes
confirmam categorias diferentes) permanecem em zero nos dados
publicados, o que não elimina a possibilidade de novos conflitos
surgirem à medida que a conferência avança sobre os 31,7% da base
ainda sem decisão travada.

Terceiro, o BERTimbau permanece pendente, sem treino concluído nem
métricas próprias, e foi excluído de rankings, testes e diagnósticos
comparativos; não há evidência suficiente para concluir sobre seu
desempenho neste domínio. A causa identificada é que o fluxo automático
de classificação nunca instala as dependências pesadas necessárias para
o ajuste fino real e, ao não encontrá-las, recorria silenciosamente ao
mesmo classificador LSTM usado em outra parte do experimento — sem
registrar esse desvio em nenhum resultado publicado. A materialização
publicada anteriormente sob o nome do BERTimbau (13.954 dos 13.965
chamados) foi, na verdade, produzida por esse caminho de contingência.
A causa já foi corrigida (o fluxo agora recusa publicar resultados sob
o nome de um modelo quando suas dependências não estão disponíveis, em
vez de substituí-lo silenciosamente); os resultados publicados
anteriormente sob esse nome continuam a ser tratados como não
confiáveis e devem ser desconsiderados até um treino real com as
dependências corretas instaladas.

Quarto, uma suspeita de corrupção de acentuação (*mojibake*) nos nomes
de categoria usados nas análises de confusão entre categorias (Subseção
4.8) **não se confirmou**: verificação byte a byte mostrou UTF-8 válido
em sua totalidade; os caracteres corrompidos observados antes eram
artefato de exibição do terminal usado para inspecionar os dados, não
corrupção do dado publicado.

Quinto, a discrepância do *ablation* do LSTM, uma pendência técnica
declarada em versão anterior deste texto, foi investigada e resolvida
em 25/07/2026: uma fração pequena vinha de vazamento por duplicatas
(corrigido via *GroupKFold*), e a maior parte vinha da avaliação
oficial de referência estar desatualizada. A rematerialização completa
dos sete modelos comparáveis (Subseção 4.2) substituiu o valor
histórico do LSTM (74,71%) pelo valor atual (87,90%), muito mais
próximo do *ablation* corrigido (86,35%). O *ablation* deixa de ser
tratado como diagnóstico isolado e passa a ser lido como evidência
preliminar de baixa sensibilidade do LSTM aos hiperparâmetros testados,
consistente com a nova avaliação oficial.

Sexto, identificamos e quantificamos um viés estrutural de seleção na
própria amostra validada, discutido em detalhe na Seção 5: a regra de
decisão da verdade validada exclui do denominador de acerto validado os
438 chamados (4,6% dos 9.534 conferidos) em que nenhuma fonte conferida
foi confirmada como correta, o que infla mecanicamente o número pontual
reportado na Subseção 4.2. Publicamos um intervalo de sensibilidade com
amplitude de 3,95 a 4,36 pontos percentuais conforme o modelo; o
ranking relativo entre os sete modelos permanece estável em todo o
intervalo, mas o valor absoluto de acerto validado não deve ser
interpretado como uma estimativa isenta desse viés, nem comparado ponto
a ponto com *benchmarks* externos sem essa ressalva.

Persistem também como limitações a dependência de uma única instituição
como caso empírico e a intermitência observada na publicação automática
do painel de acompanhamento dos resultados.

**6. CONSIDERAÇÕES FINAIS**

O presente capítulo atualizou o protocolo de classificação automática
multimodelo de chamados de manutenção predial universitária em português
brasileiro com os resultados acumulados até 24 de julho de 2026,
incluindo sete modelos materializados, uma camada de memória de decisão
por veto e trava de categorias já conferidas, e uma camada de análise
informacional baseada em entropia de Shannon e divergência de
Jensen-Shannon. O BERTimbau permanece como extensão planejada, sem
treino concluído ou métricas próprias. A contribuição central permanece
metodológica: não apenas identificar o melhor classificador, mas
estruturar um protocolo em que aprendizado de máquina, estatística não
paramétrica, memória de decisão e auditoria humana qualificam
progressivamente a base de dados e revelam inconsistências taxonômicas
— e, como esta rodada demonstrou, também revelam e corrigem
inconsistências no próprio pipeline de avaliação (Subseções 4.3 e 4.4).

Na amostra parcial, não aleatória, de 9.096 chamados com decisão travada
e sem conflito, o LinearSVC obteve o maior acerto validado entre os sete
modelos comparáveis: 94,93% (IC95%: 94,47%--95,38%), seguido de SGD
(93,92%), Regressão Logística (93,55%), Extra Trees (92,74%), Random
Forest (92,27%), LSTM (87,90%) e Naive Bayes (86,09%) — números
rematerializados em 25/07/2026, incluindo uma limpeza completa e
reprocessamento do zero dos oito modelos (a materialização anterior,
de 16-17/07, havia sido identificada como desatualizada;
Subseção 4.9). Nenhum dos três
ensembles avaliados (maioria ponderada, confiança calibrada máxima,
maioria simples) supera o LinearSVC isolado com significância estatística;
a recomendação é usar o LinearSVC isolado, com calibração, em vez de
combinar modelos. Esses números não estimam o desempenho da base completa, pois
a seleção da conferência prioriza divergências e casos críticos (COCHRAN, 1977). A matriz
IA × histórico registra que o histórico administrativo também contém
erros confirmados, o que mantém a validação humana como parte necessária
do protocolo; a proporção observada nessa amostra não deve ser
generalizada sem desenho probabilístico (COCHRAN, 1977).

A meta original do experimento — confiança calibrada igual ou superior a
95% associada a acerto validado igual ou superior a 95% — fica próxima
de ser atingida na faixa de alta confiança da classificação oficial
(96,79% de acerto validado, ante 99,73% na consolidação anterior sobre
amostra menor). Essa reversão recomenda cautela redobrada: a trajetória
entre 16/07 e 23/07/2026 mostrou que mesmo a leitura "meta atingida"
pode reverter quando a amostra de conferência cresce, o que reforça a
recomendação de não tratar a meta como cumprida para fins de liberação
em produção sem revisão antes da conclusão da conferência humana sobre
uma fração mais representativa da base.

A curva real de aprendizado do LSTM (Subseção 4.9, Figura 5) é
consistente com o restante do capítulo. A discrepância do *ablation*
do mesmo modelo (Figura 6), discutida em detalhe nas Limitações, não
indica arquitetura mal ajustada: com a causa principal corrigida, a
ordenação relativa das quatro variantes testadas mostra baixa
sensibilidade do LSTM a unidades e *dropout* nesta base (diferença
entre melhor e pior variante inferior a 4 pontos percentuais).

Os próximos passos deste protocolo incluem a conclusão da conferência
humana pendente (31,7% da base ainda sem decisão travada), a
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

**Apêndice A — Dicionário de colunas da planilha experimental (A:P)**

A aba experimental segue o esquema fixo de colunas A:P:

| Coluna | Campo |
|---|---|
| A | ID Chamado |
| B | TÍTULO |
| C | CATEGORIA COMPLETA (rótulo histórico) |
| D | DESCRIÇÃO GLPI |
| E | TÍTULO O.S.M. |
| F | DESCRIÇÃO O.S.M. |
| G | Classificação IA |
| H | Avaliação (%) — gravada como fração 0–1, formatada como % |
| I | Executor |
| J | Criticidade Atribuída por IA |
| K | Comparação — fórmula `=SE(G="";"";G=C)` |
| L | Classificado_Confiança_IA |
| M | CONFERÊNCIA GLPI |
| N | CONFERÊNCIA IA |
| O | Classificação IA - 2 |
| P | CONFERÊNCIA IA - 2 |

**Apêndice B — Checklist de itens reportados**

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
| Verificação explícita de pressupostos (normalidade, homogeneidade, colinearidade, independência) | 4.10 | Sim — protocolo de Zuur, Ieno e Elphick (2010) adaptado; Tabelas 8-9 |
| Critério de calibração de confiança (bruta vs. calibrada) e meta de desempenho | 3.8, 4.4 | Parcial — meta declarada (>= 95%/>= 95%); calibração formal (Platt/isotônica) ainda não aplicada |
| Protocolo de validação humana | 3.6 | Sim |
| Cobertura da validação humana na data de publicação (n e % da base) | 4 (abertura) | Sim, mas desatualizada — ver nota de revalidação de dados |
| Tratamento de conflitos de conferência | 3.7 | Sim (regra de veto/trava) |
| Reprodutibilidade (scripts e dados versionados) | 3.9 | Sim (repositório público, JSONs sanitizados) |
| Limitações declaradas | 5, 6 | Sim |
| Figuras/tabelas geradas a partir de dados verificáveis | 4.8 | Sim (scripts leem os JSONs vigentes do painel) |

**Apêndice C — Matriz de decisão M/N/P**

Contagens agregadas disponíveis nos JSONs públicos do painel (23/07/2026):

| Métrica | n |
|---|---|
| Chamados com ao menos uma conferência (M, N ou P) | 9.534 |
| Decisões travadas (categoria decidida sem conflito) | 9.096 |
| Casos restritos (categoria eliminada, sem decisão travada) | 438 |
| Conflitos (M e N confirmam categorias diferentes) | 0 |
| Conferências da coluna N (CONFERÊNCIA IA) preenchidas | 9.096 |
| Conferências da coluna M (CONFERÊNCIA GLPI) preenchidas | 9.534 |
| Conferências da coluna P (CONFERÊNCIA IA - 2) preenchidas | 0 |

Fonte: elaborado pelos autores (2026), com dados de 23/07/2026. A
coluna P (reclassificação conferida) está zerada nesta
consolidação — nenhuma reclassificação foi conferida via essa coluna
especificamente até esta data.

*Pendência explícita*: o cruzamento fino de 3 vias (contagem por combinação
exata de valores de M × N × P — ex.: quantos casos têm M=Correto e N=Errado
simultaneamente) **não está disponível em nenhum JSON público atual** e exige
extração direta da planilha experimental (`Informação insuficiente para
verificar` com os dados hoje publicados). O que se aproxima disso é a matriz
2×2 IA×histórico da Tabela 4 (Subseção 4.3), que cruza acerto da IA e do
histórico contra a verdade decidida — não é o mesmo cruzamento M×N×P bruto,
mas cobre a mesma pergunta de fundo (quando IA e histórico concordam ou
divergem da decisão final).
