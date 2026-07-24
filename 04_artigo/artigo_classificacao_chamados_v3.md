**CLASSIFICAÇÃO AUTOMÁTICA MULTIMODELO DE CHAMADOS DE MANUTENÇÃO PREDIAL
UNIVERSITÁRIA EM PORTUGUÊS BRASILEIRO: PROTOCOLO DE GOVERNANÇA PREDITIVA
COM VALIDAÇÃO HUMANA SOB RÓTULOS HISTÓRICOS RUIDOSOS**

*Multi-model automatic classification of university building maintenance
work orders in Brazilian Portuguese: a predictive governance protocol
with human validation under noisy historical labels*

**Adinailson Guimarães de Oliveira**

Universidade Federal do Sul da Bahia (UFSB), Programa de Pós-Graduação
em Biossistemas

E-mail: adinailson.oliveira@cja.ufsb.edu.br

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
Logística, LinearSVC calibrado, SGD, Random Forest e Extra Trees), rede
neural LSTM bidirecional e um transformador pré-treinado em português
(BERTimbau, com ajuste fino), já com resultado comparativo disponível
nesta consolidação. O diferencial metodológico reside na distinção entre
concordância com o histórico administrativo e acerto validado por
revisão humana, tratando a categoria histórica como referência
preliminar imperfeita — distinção que se mostrou decisiva: o acerto
validado por conferência humana (9.096 decisões travadas) revelou-se
mais conservador do que a concordância com o histórico sugeria, à medida
que a amostra de conferência cresceu e deixou de se concentrar apenas em
casos de fácil confirmação. Resultados indicam superioridade do LinearSVC
calibrado tanto na concordância com o histórico (acurácia de 80,34%,
IC95%: 79,69%--80,97%) quanto no acerto validado (79,89%, IC95%:
78,99%--80,73%), enquanto o LSTM apresentou concordância de 68,47% e
acerto validado de 74,71%. A normalidade da concordância por turno foi
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
classifiers (Naive Bayes, Logistic Regression, calibrated LinearSVC,
SGD, Random Forest, and Extra Trees), a bidirectional LSTM neural
network, and a Portuguese pre-trained transformer (BERTimbau,
fine-tuned), already with comparative results in this consolidation. The
methodological contribution lies in distinguishing agreement with
administrative history from human-validated accuracy — a distinction
that proved decisive: human-validated accuracy (9,096 locked decisions)
turned out more conservative than agreement with history suggested, as
the validation sample grew and stopped concentrating on easily
confirmed cases. Results indicate calibrated LinearSVC superiority both
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
abordagem neural LSTM bidirecional e um transformador pré-treinado em
português (BERTimbau, com ajuste fino), já com resultado comparativo
disponível nesta consolidação. O
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

O corpus experimental é composto por 13.825 chamados de manutenção
predial não vazios, organizados em 54 categorias históricas, extraídos
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
ampliação da conferência humana, não uma mudança metodológica dos
scripts de análise (confirmado por conferência do histórico de commits
dos scripts que produzem `avaliacao_final.json` e `estatistica.json`).

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

O desenho experimental considera oito modelos, todos já materializados
nesta consolidação. Os classificadores clássicos adotam representação
TF-IDF e algoritmos de aprendizado supervisionado amplamente
consolidados na literatura de classificação textual (JOACHIMS, 1998;
PEDREGOSA *et al.*, 2011): Naive Bayes Multinomial, como *baseline*
probabilístico; Regressão Logística, com calibração natural e boa
interpretabilidade; LinearSVC calibrado, combinando margem linear e
calibração de confiança via Platt (PLATT, 1999); SGD, como alternativa
eficiente para matrizes esparsas de grande dimensão; Random Forest e
Extra Trees, como representantes de métodos não lineares baseados em
*ensemble* de árvores. A LSTM Bidirecional foi construída com camada de
*embedding* de 8.000 termos e 128 dimensões, camada recorrente
bidirecional de 64 unidades (GRAVES; SCHMIDHUBER, 2005), *dropout* de
0,5 e camada densa com ativação *softmax*, treinada com parada
antecipada, avaliada tanto na comparação *out-of-fold* (Subseção 4.1)
quanto na Etapa 1 oficial de produção, com *fallback* de Random Forest.

O oitavo modelo, um transformador pré-treinado em português com ajuste
fino (BERTimbau, `neuralmind/bert-base-portuguese-cased`), foi
incorporado como extensão contextual, com *fallback* automático para
LSTM/RF quando as dependências de treinamento (torch/transformers) não
estão disponíveis no ambiente de execução. Pelo custo computacional em
CPU, o ajuste fino roda em fluxo de trabalho próprio, de baixa
frequência, fora do ciclo padrão de 15 minutos, e é condicionado a um
limiar mínimo de avanço da base validada (100 novos casos conferidos)
antes de cada novo treinamento. Nesta consolidação (23/07/2026), esse
limiar já foi atingido e o modelo tem resultado comparativo disponível e
reportado na Seção 4 (68,06% de concordância com o histórico, 73,79% de
acerto validado) — diferentemente de versões anteriores deste protocolo,
em que o treinamento permanecia adiado e o modelo era tratado como
trabalho em andamento.

**3.5 Desenho de avaliação**

A avaliação foi realizada por predições fora da amostra em protocolo
*out-of-fold* com *k-fold* estratificado, *seed* fixa e mesma partição
para todos os modelos, desenho que reduz viés de comparação e permite
testes pareados (SOKOLOVA; LAPALME, 2009). As métricas principais são
acurácia, *macro*-F1, F1 ponderado, *balanced accuracy* e intervalo de
confiança por *bootstrap* com 95% de confiança. A *macro*-F1 e a
*balanced accuracy* são essenciais face ao desbalanceamento entre
categorias, dado que a acurácia isolada pode superestimar desempenho em
classes majoritárias e mascarar falhas em categorias raras (SOKOLOVA;
LAPALME, 2009). A correlação entre confiança e acerto é avaliada por
Spearman; diferenças globais entre classificadores são avaliadas por
Cochran Q e Friedman; comparações pareadas são avaliadas por McNemar
(1947); e incerteza de acurácia é estimada por *bootstrap*. Quando
múltiplas comparações são realizadas, aplica-se correção de Nemenyi no
contexto de *ranks*.

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
Shannon e divergência de Jensen-Shannon, calculada exclusivamente sobre
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

Os artefatos que sustentam os resultados relatados neste capítulo são gerados por
scripts versionados no repositório público
`github.com/adinailson88/classificacao-chamados` (branch `main`), independente do
repositório operacional Malha IA. Os números citados nas Subseções 4.1 a 4.6
correspondem aos arquivos JSON publicados em `docs/dados/` (por exemplo,
`estatistica.json`, `avaliacao_final.json`, `calibracao.json`,
`reclass_resumo.json`, `shannon_resumo.json`, `jensen_shannon_modelos.json`),
regenerados automaticamente por *workflows* do GitHub Actions a cada rodada do
experimento e publicados também via GitHub Pages. Nenhum identificador pessoal,
título ou texto livre de chamado é versionado nesses arquivos; a camada
Shannon/Jensen-Shannon (Subseção 3.8) opera exclusivamente sobre agregados
sanitizados. **Pendência explícita desta subseção**: consolidar, em rodada futura,
a correspondência exata entre cada subseção de resultado e o script que a gera
(por exemplo, `src/avaliacao_final.py`, `src/calibracao.py`,
`src/analise_shannon.py`), hoje mapeada em `PLANO_ARTIGO_CAPITULO.md` mas ainda não
transcrita para o corpo do artigo.

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

A comparação contra a categoria histórica, sobre a base completa (n =
13.965, com intervalo de confiança por bootstrap a 95%), mantém o
LinearSVC calibrado na liderança, com acurácia de 0,8034 (IC95%:
0,7969--0,8097), seguido por Extra Trees (0,7898), Random Forest
(0,7798), SGD (0,7784), Regressão Logística (0,7691), Naive Bayes
(0,6990), LSTM (0,6847) e o transformador pré-treinado BERTimbau, já com
resultado disponível nesta consolidação (0,6806). O teste de Cochran Q
confirma diferença global entre os oito modelos (Q = 3.494,146; gl = 7; p
\< 0,001). O Kappa de Cohen entre cada modelo e o histórico acompanha
ordenamento muito próximo (LinearSVC 0,7884; Extra Trees 0,7721; SGD
0,7623; Random Forest 0,7611; Regressão Logística 0,7527; Naive Bayes
0,6697; LSTM 0,6633; BERTimbau 0,6590), e o Kappa de Fleiss entre os oito
modelos (0,7538) indica concordância substancial entre arquiteturas
distintas treinadas sobre a mesma base, ainda que um pouco menor do que
a observada entre os seis classificadores clássicos isolados na
consolidação de 16/07/2026 (0,8068) — resultado esperado ao acrescentar
duas arquiteturas (LSTM, BERTimbau) cujo padrão de erro diverge mais dos
modelos lineares e de *ensemble* de árvores. A nona fonte de
classificação, a Etapa 1 oficial (executor LSTM/RF de produção, coluna G
da planilha), mantém concordância de 77,65% e confiança média de 71,67%
nesta consolidação, posicionando-se entre SGD e Regressão Logística
nesta métrica — não é diretamente comparável ao LSTM *out-of-fold* da
Tabela 1, pois combina LSTM com *fallback* de Random Forest conforme a
regra de produção (Subseção 3.4), não um único modelo isolado.

**Tabela 1** Concordância com a categoria histórica, base completa (n = 13.965)

| Modelo | Acurácia | IC95% bootstrap | Kappa vs. histórico |
|---|---|---|---|
| LinearSVC calibrado | 0,8034 | 0,7969 -- 0,8097 | 0,7884 |
| Extra Trees | 0,7898 | 0,7828 -- 0,7964 | 0,7721 |
| Random Forest | 0,7798 | 0,7729 -- 0,7864 | 0,7611 |
| SGD | 0,7784 | 0,7719 -- 0,7851 | 0,7623 |
| Regressão Logística | 0,7691 | 0,7624 -- 0,7757 | 0,7527 |
| Naive Bayes | 0,6990 | 0,6914 -- 0,7064 | 0,6697 |
| LSTM (out-of-fold) | 0,6847 | 0,6769 -- 0,6923 | 0,6633 |
| Transformer (BERTimbau) | 0,6806 | 0,6730 -- 0,6881 | 0,6590 |

Fonte: `estatistica.json`, gerado em 23/07/2026 20:45 (n = 13.965).

**4.2 Ranking validado por conferência humana**

A avaliação contra a verdade validada pela memória de decisão M/N/P (n =
9.096 decisões travadas) confirma a mesma liderança da Subseção 4.1, mas
em patamar bem mais conservador do que o reportado na consolidação de
16/07/2026: o LinearSVC calibrado permanece o melhor modelo isolado, com
acerto validado de 0,7989 (IC95%: 0,7899--0,8073), seguido por SGD
(0,7909), Regressão Logística (0,7859), Extra Trees (0,7762), Random
Forest (0,7689), LSTM (0,7471), o transformador BERTimbau (0,7379) e
Naive Bayes (0,7114). A diferença entre o primeiro e o segundo colocado é
pequena em termos absolutos (0,8 ponto percentual), mas estatisticamente
significativa (McNemar, p ~ 0,000002), sustentando a recomendação de uso
do LinearSVC calibrado como IA de referência. Nenhum método de combinação
testado supera o LinearSVC isolado: maioria ponderada com pesos
aprendidos *out-of-fold* (0,7944), maioria simples (0,7930) e confiança
calibrada máxima (0,7930) ficam todos **abaixo** do LinearSVC (0,7989),
com a diferença estatisticamente significativa a favor do LinearSVC
isolado nos três casos (McNemar p = 0,0008; p < 0,0001; p < 0,0001,
respectivamente). Combinar modelos, portanto, não se justifica
operacionalmente diante do custo adicional de manter um comitê.

**Tabela 2** Acerto validado contra a verdade decidida M/N/P (n = 9.096)

| Modelo | Acerto validado | IC95% |
|---|---|---|
| LinearSVC calibrado | 0,7989 | 0,7899 -- 0,8073 |
| SGD | 0,7909 | 0,7819 -- 0,7994 |
| Regressão Logística | 0,7859 | 0,7768 -- 0,7947 |
| Extra Trees | 0,7762 | 0,7667 -- 0,7847 |
| Random Forest | 0,7689 | 0,7598 -- 0,7777 |
| LSTM | 0,7471 | 0,7375 -- 0,7556 |
| Transformer (BERTimbau) | 0,7379 | 0,7287 -- 0,7471 |
| Naive Bayes | 0,7114 | 0,7016 -- 0,7208 |

Fonte: `avaliacao_final.json`, gerado em 23/07/2026 04:58, contra a
categoria decidida pela memória M/N/P (`decisao_validada.verdade_validada`).

*Nota metodológica sobre a mudança de patamar (92--96% em 16/07/2026 →
71--80% nesta consolidação)*: o código de `avaliacao_final.py` que produz
esta tabela **não foi alterado** entre 16/07 e 23/07/2026 (confirmado por
`git log`) — a queda não decorre de mudança de metodologia, mas do
crescimento da amostra validada (4.681 → 9.096 decisões, quase o dobro).
A leitura mais provável, retomada na Seção 5, é que a amostra menor de
16/07 estava mais concentrada em casos já fáceis de confirmar como
corretos, e a ampliação da cobertura revelou uma taxa de acerto real mais
baixa e mais representativa da base como um todo. Isso reforça, e não
enfraquece, a premissa metodológica central deste artigo: avaliar modelos
apenas contra amostras pequenas de validação humana pode superestimar o
desempenho real.

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

Fonte: `calibracao.json`, gerado em 23/07/2026 21:53. Leitura: 8.200 casos em
que ambos (IA e histórico) coincidem com a categoria decidida; 319 em que
nenhum dos dois coincide; 577 em que o histórico acerta e a IA erra; e **zero**
casos em que a IA acerta e o histórico erra. A ausência total de casos na
célula "IA correta / histórico incorreto" chama atenção e tem explicação
estrutural, não é necessariamente evidência de que a IA nunca corrige o
histórico: quando a categoria decidida vem de confirmação da própria
categoria histórica (fonte `conferencia_glpi`), a célula "histórico
incorreto" fica automaticamente descartada para aquela linha; a memória de
decisão (Subseção 3.7) também reaproveita categorias já travadas em rodadas
anteriores, o que tende a alinhar a classificação vigente da IA (coluna G no
momento do snapshot) com decisões já confirmadas. Antes de tratar essa
célula-zero como achado substantivo (ex.: "a IA nunca corrige o histórico"),
recomenda-se auditoria dirigida da fonte de decisão (`fonte_decisao`) por
linha — não realizada nesta rodada.

**4.4 Confiança, calibração e faixas de decisão**

A calibração bruta da Etapa 1 oficial mantém ECE histórico de 0,0598
nesta consolidação. Quando segmentada por faixa de confiança e cruzada
com a verdade decidida pela memória M/N/P — não mais com a marcação
bruta de uma única coluna de conferência, correção aplicada em
`src/calibracao.py` nesta rodada (ver observação metodológica adiante) —,
a faixa igual ou superior a 95% de confiança (n = 4.808; 34,4% da base)
apresenta concordância de 99,08% com o histórico e, mais relevante,
acerto validado de 96,79% sobre os 4.698 casos já com decisão travada
nessa faixa — resultado que fica muito próximo da meta de referência do
experimento (confiança calibrada >= 95% associada a acerto real >= 95%),
embora não a atinja com folga. Nas faixas inferiores, a degradação de
desempenho acompanha a queda de confiança de forma consistente (90–95%:
acerto validado 91,48%; 80–90%: 93,92%; 70–80%: 94,95%; 50–70%: 83,94%;
inferior a 50%: 49,89%), o que corrobora a correlação positiva entre
confiança bruta e acerto — quantificada nesta consolidação por Spearman
entre 0,45 e 0,56 conforme o modelo (Subseção 4.1, `estatistica.json`) —,
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

Fonte: `calibracao.json`, gerado em 23/07/2026 21:53. A amostra de conferência
prioriza divergências e casos de menor confiança na composição original, não
é aleatória — a leitura acima deve ser tomada como piso/teto conforme o
desenho da conferência, não como taxa de acerto sobre amostra representativa.

*Nota metodológica*: até 22/07/2026, esta tabela comparava a classificação do
executor apenas contra a marcação bruta da coluna N (CONFERÊNCIA IA)
isolada, o que produzia acerto validado artificialmente igual a 100% em toda
faixa de confiança, inclusive abaixo de 50% — a coluna N, no uso real, quase
nunca recebe marcação "Errado" (o erro da IA costuma ficar registrado via M,
sem tocar N). Corrigido em `src/calibracao.py` no commit `21258deb`
(23/07/2026): a comparação passou a usar a categoria decidida pela memória
M/N/P (`decisao_validada.verdade_validada`), a mesma verdade da Subseção 4.2,
eliminando o viés de seleção. Teste de regressão em `tests/test_calibracao.py`.

**4.5 Reclassificação e ganho líquido**

A reclassificação dos chamados já conferidos (execução de 30/06/2026,
coluna O) produz resultados heterogêneos entre modelos, medidos contra a
verdade validada quando travada e contra o histórico nos demais casos. O
LinearSVC apresenta o maior ganho líquido absoluto (+30; 479 corrigidos
e 449 prejudicados, sobre 29.794 reclassificações acumuladas, das quais
18.719 são reaproveitamento direto de decisão humana travada), seguido
por Naive Bayes (+9) e Regressão Logística (+8). Em contraste, SGD
(−92), Random Forest (−80) e Extra Trees (−40) apresentam ganho líquido
negativo nesta rodada --- a reclassificação piora mais casos do que
corrige para esses três modelos. Esse resultado reforça a decisão
metodológica de não aplicar reclassificação em massa de forma
indiscriminada por modelo, tratando o ganho líquido, e não apenas a
acurácia agregada, como critério de decisão operacional por
classificador.

*Atualização de dados (23/07/2026)*: o parágrafo acima preserva os números
da execução de 30/06/2026. A Tabela 5 mostra o recorte mais recente
(`reclass_resumo.json`, execução de 23/07/2026), já incluindo o LSTM (ausente
da comparação anterior):

**Tabela 5** Ganho líquido de reclassificação por modelo (execução de 23/07/2026)

| Modelo | Total reclassificado | Corrigidos | Prejudicados | Ganho líquido | Reuso de decisão humana |
|---|---|---|---|---|---|
| LSTM | 13.418 | 628 | 539 | +89 | 8.805 |
| LinearSVC | 13.451 | 278 | 209 | +69 | 8.856 |
| Regressão Logística | 13.332 | 235 | 144 | +91 | 8.727 |
| SGD | 13.379 | 186 | 157 | +29 | 8.771 |
| Random Forest | 18.049 | 209 | 184 | +25 | 13.387 |
| Naive Bayes | 13.226 | 125 | 132 | −7 | 8.623 |
| Extra Trees | 13.310 | 202 | 204 | −2 | 8.713 |

Fonte: `reclass_resumo.json`, gerado em 23/07/2026 21:31 (modelos executados em
23/07/2026 07:55–07:56). Nesta consolidação, apenas Extra Trees e Naive Bayes
mantêm ganho líquido negativo (a versão de 30/06 também apontava SGD e Random
Forest como negativos; ambos passaram a positivo). **Observação de qualidade
de dado, não corrigida nesta rodada**: o total reclassificado do Random Forest
(18.049) destoa dos demais modelos (~13.200–13.450), apesar de a execução ter
ocorrido no mesmo dia e com poucos minutos de diferença dos demais — não foi
investigada a causa; não interpretar o ganho líquido do Random Forest como
diretamente comparável aos demais até essa discrepância ser explicada.

**4.6 Diagnóstico de taxonomia e ambiguidade estrutural
(Shannon/Jensen-Shannon)**

A camada de entropia de Shannon, calculada sobre as oito fontes de
classificação (Etapa 1 oficial e as sete IAs materializadas, incluindo o
LSTM out-of-fold), aponta o LSTM como o modelo de maior diversidade nas
categorias previstas, e o LinearSVC como o modelo cuja distribuição de
predições mais se aproxima da distribuição histórica (menor divergência
de Jensen-Shannon). No nível de chamado individual, 3.451 dos 13.954
registros (24,7%) apresentam alta entropia de votos entre os oito
modelos, ou seja, desacordo estrutural relevante entre arquiteturas
distintas --- um critério de priorização de auditoria diferente e
complementar à simples baixa confiança de um único modelo. No nível de
categoria, a análise aponta um número relevante de ocorrências de alta
ambiguidade nas predições (79, com suporte mínimo de 30 registros por
categoria); a interpretação detalhada de quais categorias específicas
concentram essa ambiguidade, e sua sobreposição com os pares de maior
confusão recíproca já identificados na etapa de cruzamento de taxonomia
(por exemplo, entre climatização e manutenção preventiva de
ar-condicionado, ou entre estrutura predial, esquadrias e
hidrossanitária), permanece como candidata a inspeção qualitativa
dirigida. O que a camada Shannon oferece é a priorização estatística de
onde essa inspeção deve começar, não a decisão de fusão ou desambiguação
de categorias, que continua sendo humana.

*Atualização de dados (23/07/2026)*: o parágrafo acima preserva a leitura da
versão anterior deste rascunho, que atribuía ao LSTM a maior diversidade e ao
LinearSVC a menor divergência frente ao histórico. Na consolidação mais
recente (`shannon_modelos.json`, `shannon_resumo.json`), **a Etapa 1 oficial
assume as duas posições** — maior entropia de previsões e menor divergência
de Jensen-Shannon —, com LSTM e o transformador (BERTimbau) muito próximos
em terceiro e segundo lugar de diversidade:

**Tabela 6** Entropia de Shannon e divergência de Jensen-Shannon por fonte de classificação (23/07/2026)

| Fonte | Categorias previstas | Entropia (nats) | Entropia normalizada | JS vs. histórico |
|---|---|---|---|---|
| Etapa 1 oficial | 53 | 4,6758 | 0,8163 | 0,0286 |
| Transformer (BERTimbau) | 51 | 4,6288 | 0,8160 | 0,0872 |
| LSTM | 52 | 4,6201 | 0,8105 | 0,0847 |
| Regressão Logística | 52 | 4,4490 | 0,7805 | 0,0716 |
| SGD | 53 | 4,4363 | 0,7745 | 0,0639 |
| LinearSVC | 53 | 4,3356 | 0,7569 | 0,0575 |
| Extra Trees | 47 | 3,9955 | 0,7193 | 0,0761 |
| Random Forest | 47 | 3,9574 | 0,7124 | 0,0804 |
| Naive Bayes | 19 | 3,3340 | 0,7848 | 0,1755 |

Fonte: `shannon_modelos.json` e `jensen_shannon_modelos.json`, gerados em
23/07/2026 (workflow `dashboard.yml`, via `src/analise_shannon.py`). No nível
de categoria, a mais recente `shannon_resumo.json` aponta 91 ocorrências de
alta ambiguidade nas predições (ante 79 na versão anterior) e 3.378 chamados
(ante 3.451) com alta entropia de votos entre modelos — números próximos, sem
mudança de leitura qualitativa. Naive Bayes chama atenção por combinar a
menor cobertura de categorias (19, ante 47–53 dos demais) com entropia
normalizada relativamente alta (0,7848) — provável reflexo de concentração
extrema em poucas categorias com alguma dispersão residual, não investigado
em detalhe nesta rodada.

**4.7 Custo computacional**

Nos recortes de comparação por lote (1.000 registros cada), o tempo de
treino mantém-se na casa de segundos para os modelos lineares e
probabilísticos mais simples (por exemplo, Naive Bayes ~ 1,1 s) e sobe
para modelos com mais hiperparâmetros (Regressão Logística ~ 8,7 s neste
recorte), enquanto o LSTM, por depender de épocas de treinamento em rede
neural, permanece a opção de maior custo computacional entre as fontes
de classificação avaliadas, exigindo minutos e infraestrutura de
checkpoint; o oitavo modelo (transformador com ajuste fino) tende a
ampliar ainda mais esse custo, o que motivou seu isolamento em fluxo de
trabalho próprio, de baixa frequência (Subseção 3.4). Essa hierarquia de
custo é consistente com a observada em versões anteriores deste
protocolo e reforça o argumento operacional de que modelos lineares
combinam o melhor desempenho validado (Subseção 4.2) com o menor custo
de reexecução e auditoria.

**Tabela 7** Custo computacional por lote de 1.000 registros

| Modelo | Tempo de treino (s) | Tempo de inferência (s) | Acurácia neste lote |
|---|---|---|---|
| Naive Bayes | 1,14 | 0,07 | 0,539 |
| LinearSVC | 2,55 | 0,06 | 0,655 |
| SGD | 2,60 | 0,09 | 0,624 |
| Regressão Logística | 9,43 | 0,09 | 0,624 |
| Random Forest | 19,45 | 0,13 | 0,597 |
| Extra Trees | 21,30 | 0,14 | 0,610 |

Fonte: `comparacao_modelos.json`, execução mais recente por modelo em
18/07/2026 03:30 — não reexecutado em 23/07/2026; único registro de custo
computacional disponível no painel para os modelos clássicos. LSTM e o
transformador (BERTimbau) não constam deste arquivo; seu custo mais alto é
descrito qualitativamente no parágrafo acima (dependência de épocas de
treinamento em rede neural), não medido nesta mesma tabela. A acurácia
reportada aqui é sobre um lote de 1.000 registros (não a base completa) e
serve só para contextualizar o trade-off custo×desempenho desta subseção —
não usar como substituto das Tabelas 1 e 2.

**4.8 Figuras**

*Atualização de dados (23/07/2026)*: das quatro figuras originalmente
planejadas para este capítulo, três foram geradas nesta rodada a partir dos
JSONs vigentes do painel (script `matplotlib`, ver
`04_artigo/figuras/`). A quarta permanece pendente por um motivo de
qualidade de dado, não de esforço de geração.

![Figura 2 — Confiança bruta × concordância com o histórico × acerto validado, por faixa de confiança (executor oficial, Etapa 1, 23/07/2026).](04_artigo/figuras/fig2_confianca_desfecho.png)

**Figura 2** Confiança bruta × concordância com o histórico × acerto validado,
por faixa de confiança (executor oficial, Etapa 1). Mesmos números da
Tabela 3 (Subseção 4.4), em forma gráfica.

Fonte: `calibracao.json`, gerado em 23/07/2026 21:53.

![Figura 3 — Trade-off entre acerto validado e custo computacional (tempo de treino), modelos clássicos.](04_artigo/figuras/fig3_tradeoff_custo.png)

**Figura 3** Trade-off entre acerto validado (conferência humana, 23/07/2026)
e custo computacional (tempo de treino, lote de 1.000 registros, 18/07/2026),
modelos clássicos. LSTM e o transformador (BERTimbau) não constam desta
figura por não terem registro de tempo de treino no mesmo arquivo (Tabela 7,
Subseção 4.7); seu custo mais alto é descrito qualitativamente no texto.

Fonte: `comparacao_modelos.json` (custo) e `avaliacao_final.json` (acerto
validado).

**Figura 4 (pares de maior confusão entre categorias) — pendência explícita,
motivo novo**: ao preparar esta figura, foi descoberta corrupção de
acentuação (mojibake — caracteres substitutos no lugar de vogais acentuadas,
por exemplo em "Instalação" e "Climatização") nos
nomes de categoria de três arquivos-fonte (`estatistica.json`, campo
`top_confusoes`; `cruzamento_taxonomia.json`; `confusao_historico_ia.json`).
Rastreamento parcial (não confirmado por leitura direta da planilha):
`src/analise_estatistica.py` lê os nomes de categoria das abas
`CLASSIF__<modelo>` (não da aba principal nem de `registros.json`, que estão
limpos), o que restringe a suspeita a essas abas de trabalho específicas ou a
como esse script as lê. Publicar essa figura com texto corrompido seria pior
do que não publicá-la — fica como `Informação insuficiente para verificar`
até investigação com acesso à planilha real, registrada como novo achado em
`PLANO_ARTIGO_CAPITULO.md`, separado do bug de calibração corrigido nesta
mesma rodada (Subseções 4.3 e 4.4).

**5. DISCUSSÃO**

A comparação entre concordância histórica (Subseção 4.1) e desempenho
validado (Subseção 4.2) revela um padrão que mudou de magnitude ao longo
da elaboração deste capítulo e que, por isso, merece registro explícito
antes de qualquer outra leitura: na consolidação de 16/07/2026, sobre
4.681 decisões travadas, o acerto validado (92–96%) superava com folga a
concordância com o histórico (70–80%); na consolidação vigente
(23/07/2026), sobre 9.096 decisões — quase o dobro —, os dois patamares
se aproximaram (concordância 68–80%, acerto validado 71–80%), com o
LinearSVC calibrado praticamente empatado entre as duas métricas (80,34%
concordância, 79,89% acerto validado). Como já registrado na Subseção
4.2, essa aproximação não decorre de mudança nos scripts de avaliação
(confirmado por conferência do histórico de commits), e sim do
crescimento da amostra de conferência: a leitura mais provável é que a
amostra menor de 16/07 concentrava casos mais fáceis de confirmar como
corretos, e a ampliação revelou uma taxa de acerto real mais baixa e mais
representativa da base como um todo. Esse é, em si, um achado
metodológico relevante para a literatura de validação humana em PLN
aplicado: amostras de conferência pequenas, mesmo quando maiores do que
o convencional na área (a versão original deste protocolo já superava a
amostra piloto de 305 casos), podem superestimar sistematicamente o
desempenho real de um classificador se a priorização de casos a conferir
não for depois compensada por uma amostra final ampla o bastante para
diluir esse viés inicial.

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

A manutenção da liderança do LinearSVC calibrado tanto na concordância
histórica quanto no acerto validado (Subseções 4.1 e 4.2) reforça, com
evidência agora validada e não apenas preliminar, a leitura já delineada
na primeira versão deste protocolo: em textos curtos, técnicos e
ruidosos como os chamados de manutenção predial, um classificador linear
sobre representação TF-IDF pode superar arquiteturas neurais mais
complexas, inclusive quando avaliado contra verdade humana, e ainda
manter vantagem de custo computacional (Subseção 4.7). A ausência de
ganho estatisticamente significativo de qualquer estratégia de
combinação de modelos (Subseção 4.2) reforça a mesma leitura: neste
domínio e neste estágio do experimento, investir engenharia em um único
classificador linear bem calibrado tem retorno mais claro do que
orquestrar um comitê de modelos heterogêneos.

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
da distribuição de chamados. A identificação de 3.378 chamados (24,2% da
base) com alto desacordo estrutural entre as nove fontes de classificação
(Etapa 1 oficial e as oito IAs materializadas) oferece um critério de
priorização de auditoria distinto do simples corte por baixa confiança
de um único classificador, e complementa a fila já construída a partir
da conferência M/N/P. O achado de que a Etapa 1 oficial, não o LSTM
isolado, lidera tanto a diversidade de predições quanto a menor
divergência frente ao histórico (Subseção 4.6) é consistente com sua
natureza híbrida (LSTM com *fallback* de Random Forest): a combinação
tende a produzir uma distribuição de categorias mais rica do que
qualquer modelo isolado, sem se afastar tanto do padrão histórico quanto
arquiteturas mais recentes (LSTM *out-of-fold*, BERTimbau).

A meta de confiança calibrada igual ou superior a 95% associada a acerto
real igual ou superior a 95% (Subseção 4.4), estabelecida como critério
de sucesso deste protocolo, fica próxima de ser atingida, mas não é mais
alcançada com folga como sugeria a consolidação anterior: a faixa alta
de confiança da Etapa 1 oficial chega a 96,79% de acerto validado sobre
4.698 casos conferidos (ante 99,73% sobre 3.284 casos em 16/07/2026),
ainda que a confiança utilizada seja bruta (softmax/decision_function),
não formalmente calibrada por Platt ou isotônica. Essa queda de 99,73%
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
com quatro ajustes relevantes. Primeiro, a amostra validada deixou de
ser uma amostra piloto de 305 casos (2,2% da base) e passou a cobrir
9.534 conferências (68,3% da base, 9.096 decisões travadas sem
conflito), o que aumenta substancialmente a robustez estatística das
Subseções 4.2 a 4.4 — mas, como discutido acima, essa mesma ampliação já
revelou que a robustez estatística de uma amostra intermediária não
garante estabilidade da magnitude do resultado, apenas de sua direção
geral (a ordem entre modelos manteve-se; o patamar de acerto, não).
Segundo, os conflitos de conferência identificados em versões anteriores
do protocolo (casos em que duas colunas de conferência confirmam
categorias diferentes) permanecem em zero nos dados publicados
(`conflitos = 0` em `avaliacao_final.json`), o que não elimina a
possibilidade de novos conflitos surgirem à medida que a conferência
avança sobre os 31,7% da base ainda sem decisão travada. Terceiro, o
oitavo modelo (transformador BERTimbau com ajuste fino), que na versão
anterior deste protocolo ainda não tinha resultado comparativo, passou a
ter: seu desempenho (68,06% de concordância, 73,79% de acerto validado)
o posiciona entre os últimos colocados do ranking, próximo ao LSTM, não
superando os classificadores lineares clássicos nesta base — resultado
que, mesmo preliminar, já qualifica a expectativa inicial de que um
transformador pré-treinado traria ganho automático de desempenho neste
domínio de texto curto e técnico. Quarto, foi identificada nesta rodada
uma corrupção de acentuação (mojibake) nos nomes de categoria de três
arquivos-fonte usados para análises de confusão entre categorias
(Subseção 4.8), que impediu a geração da quarta figura planejada e
permanece sem causa-raiz confirmada — registrada como pendência técnica
em `PLANO_ARTIGO_CAPITULO.md`, não como resultado do experimento em si.
Persistem como limitações a dependência de uma única instituição como
caso empírico e a intermitência observada na publicação automática do
painel no GitHub Pages, discutida na auditoria técnica que acompanha
este capítulo.

**6. CONSIDERAÇÕES FINAIS**

O presente capítulo atualizou o protocolo de classificação automática
multimodelo de chamados de manutenção predial universitária em português
brasileiro com os resultados acumulados até 23 de julho de 2026,
incorporando uma oitava fonte de classificação já com resultado
comparativo (transformador BERTimbau com ajuste fino), uma camada de
memória de decisão por veto e trava de categorias já conferidas, e uma
camada de análise informacional baseada em entropia de Shannon e
divergência de Jensen-Shannon. A contribuição central permanece
metodológica: não apenas identificar o melhor classificador, mas
estruturar um protocolo em que aprendizado de máquina, estatística não
paramétrica, memória de decisão e auditoria humana qualificam
progressivamente a base de dados e revelam inconsistências taxonômicas
— e, como esta rodada demonstrou, também revelam e corrigem
inconsistências no próprio pipeline de avaliação (Subseções 4.3 e 4.4).

Diferentemente da versão preliminar deste texto, a conclusão atual se
apoia em validação humana substancial e, pela primeira vez, ampla o
bastante para revisar a magnitude dos resultados publicados
anteriormente. Sobre 9.096 chamados com decisão travada e sem conflito,
o LinearSVC calibrado confirma-se como a melhor IA isolada, com acerto
validado de 79,89% (IC95%: 78,99%--80,73%), à frente de SGD (79,09%),
Regressão Logística (78,59%), Extra Trees (77,62%), Random Forest
(76,89%), LSTM (74,71%), o transformador BERTimbau (73,79%) e Naive
Bayes (71,14%); nenhuma estratégia de combinação de modelos supera essa
IA isolada com significância estatística. Esse patamar é
substancialmente mais conservador do que os 92–96% reportados na
consolidação de 16/07/2026 sobre uma amostra bem menor (4.681 decisões)
— queda que, como discutido na Seção 5, reflete o crescimento da própria
amostra de validação, não uma piora do classificador nem mudança de
metodologia de cálculo. A matriz de confusão IA×histórico qualifica, sem
invalidar, a premissa de rótulos ruidosos: o histórico administrativo,
quando conferido, acerta mais do que a IA (96,49% contra 90,15%), mas
apresenta uma taxa real e crescente de erro confirmado (3,51% dos casos
conferidos, ante 1,2% em 16/07/2026), o que justifica manter a
arquitetura de validação humana como componente permanente do
protocolo, não como etapa transitória a ser eliminada quando a IA
atingir bom desempenho médio.

A meta original do experimento — confiança calibrada igual ou superior a
95% associada a acerto validado igual ou superior a 95% — fica próxima
de ser atingida na faixa de alta confiança da classificação oficial
(96,79% de acerto validado, ante 99,73% na consolidação anterior sobre
amostra menor), resultado que recomenda cautela redobrada em relação à
já registrada na versão anterior deste texto: a trajetória entre 16/07 e
23/07/2026 mostrou que mesmo a leitura "meta atingida" pode reverter
quando a amostra de conferência cresce, o que reforça — e não apenas
repete — a recomendação de não tratar a meta como cumprida para fins de
liberação em produção sem revisão antes da conclusão da conferência
humana sobre uma fração bem mais representativa da base. Os próximos
passos deste protocolo incluem a conclusão da conferência humana
pendente (31,7% da base ainda sem decisão travada), a calibração formal
por modelo (Platt/isotônica/temperatura) condicionada a essa
conferência, a análise comparativa mais aprofundada do desempenho do
transformador BERTimbau frente aos classificadores lineares (por ora
inferior, resultado que qualifica a expectativa inicial sobre ganho
automático de arquiteturas pré-treinadas neste domínio), a investigação
da discrepância de escala identificada na reclassificação do Random
Forest (Subseção 4.5) e da corrupção de acentuação identificada nos
arquivos-fonte de análise de confusão entre categorias (Subseção 4.8),
a revisão taxonômica dirigida pelos candidatos identificados na etapa de
cruzamento de taxonomia e na entropia de Shannon, e a estabilização da
publicação automática do painel, cuja intermitência técnica está
documentada na auditoria que acompanha este capítulo. Com isso, o
protocolo pretende seguir contribuindo tanto para a literatura de
*facility management* e processamento de linguagem natural aplicado
quanto para a melhoria concreta e continuamente auditável da gestão de
manutenção predial em instituições públicas — inclusive como exemplo
de que a própria prática de reconferir dados vivos antes de publicar,
defendida ao longo deste capítulo, é capaz de encontrar e corrigir
falhas no pipeline de avaliação, não apenas nos rótulos históricos que
motivaram o estudo.

**REFERÊNCIAS**

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. ABNT NBR 5674: Manutenção de
edificações: Requisitos para o sistema de gestão de manutenção. Rio de
Janeiro: ABNT, 2012.

BOUABDALLAOUI, Y.; LAFHAJ, Z.; YIM, P.; DUCOULOMBIER, L.; BENNADJI, B.
Natural Language Processing Model for Managing Maintenance Requests in
Buildings. Buildings, v. 10, n. 9, art. 160, 2020.

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

JOACHIMS, T. Text categorization with support vector machines: learning
with many relevant features. In: EUROPEAN CONFERENCE ON MACHINE
LEARNING, 10., 1998, Chemnitz. Proceedings \[\...\]. Berlin: Springer,
1998. p. 137--142.

KEJRIWAL, M.; SANTOS, H.; SHEN, K.; MULVEHILL, A. M.; MCGUINNESS, D. L.
A noise audit of human-labeled benchmarks for machine commonsense
reasoning. Scientific Reports, v. 14, art. 8609, 2024.

LI, Y.; LIU, Y.; ZHANG, J.; CAO, L.; WANG, Q. Automated analysis and
assignment of maintenance work orders using natural language processing.
Automation in Construction, v. 165, art. 105501, 2024.

LIU, Z.; BENGE, C.; JIANG, S. Ticket-BERT: labeling incident management
tickets with language models. arXiv:2307.00108, 2023.

MARTINS, R. F. B.; ESPEJO, M. M. S. B. Análise de custos de manutenção
predial em uma universidade federal brasileira com uso do modelo de SES.
ABCustos, São Leopoldo, v. 19, n. 1, 2024.

MCNEMAR, Q. Note on the sampling error of the difference between
correlated proportions or percentages. Psychometrika, v. 12, n. 2, p.
153--157, 1947.

MOHAMMED, A. S.; AMOAH, C. Integration of technology in decision-making
in university facilities management: a literature review. Facilities, v.
43, n. 13/14, p. 1018--1052, 2025.

MORAIS, L. S. R. de; PAULA, H. M. de; REIS, R. P. A. Promoção da
eficiência da manutenção predial em edificações públicas: abordagem
baseada em registros de ordens de serviço. Paranoá, Brasília, v. 16, n.
34, p. 1--18, 2023.

PAMPANA, A. K. et al. Data-driven analysis for facility management in
higher education institution. Buildings, v. 12, art. 2094, 2022.

PEDREGOSA, F. et al. Scikit-learn: machine learning in Python. Journal
of Machine Learning Research, v. 12, p. 2825--2830, 2011.

PLATT, J. C. Probabilistic outputs for support vector machines and
comparisons to regularized likelihood methods. In: SMOLA, A. J. et al.
(Ed.). Advances in Large Margin Classifiers. Cambridge: MIT Press, 1999.
p. 61--74.

SALTON, G.; BUCKLEY, C. Term-weighting approaches in automatic text
retrieval. Information Processing & Management, v. 24, n. 5, p.
513--523, 1988.

SCHWARTZ, R.; DODGE, J.; SMITH, N. A.; ETZIONI, O. Green AI.
Communications of the ACM, v. 63, n. 12, p. 54--63, 2020.

SOKOLOVA, M.; LAPALME, G. A systematic analysis of performance measures
for classification tasks. Information Processing & Management, v. 45, n.
4, p. 427--437, 2009.

SUNDARAM, S.; ZEID, A. Technical Language Processing for Prognostics and
Health Management: applying text similarity and topic modeling to
maintenance work orders. Journal of Intelligent Manufacturing, v. 36, p.
1637--1657, 2025.

TREVISO, M. et al. Efficient methods for Natural Language Processing: a
survey. Transactions of the Association for Computational Linguistics,
v. 11, p. 826--860, 2023.

ZHANG, H.; ZHANG, Y.; LI, J.; LIU, J.; JI, L. A survey on learning with
noisy labels in Natural Language Processing: how to train models with
label noise. Engineering Applications of Artificial Intelligence, v.
146, art. 110157, 2025.

**APÊNDICES**

**Apêndice A — Dicionário de colunas da planilha experimental (A:M)**

A aba experimental (`CHAMADOS_ESQUELETO_REDUZIDO`) segue o esquema fixo A:M,
descrito em `AGENTS.md` do repositório:

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
| M | CONFERÊNCIA (marcação humana; `TRUE` não é sobrescrito por nova classificação automática) |

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
| Método de particionamento (out-of-fold, k-fold, seed) | 3.5 | Sim (out-of-fold, k-fold estratificado, seed fixa) |
| Métricas reportadas e justificativa | 3.5 | Sim (acurácia, macro-F1, balanced accuracy, IC95% bootstrap) |
| Testes estatísticos e correção para múltiplas comparações | 3.5 | Sim (Cochran Q, Friedman, McNemar, Nemenyi) |
| Critério de calibração de confiança (bruta vs. calibrada) e meta de desempenho | 3.8, 4.4 | Parcial — meta declarada (>= 95%/>= 95%); calibração formal (Platt/isotônica) ainda não aplicada |
| Protocolo de validação humana | 3.6 | Sim |
| Cobertura da validação humana na data de publicação (n e % da base) | 4 (abertura) | Sim, mas desatualizada — ver nota de revalidação de dados |
| Tratamento de conflitos de conferência | 3.7 | Sim (regra de veto/trava) |
| Reprodutibilidade (scripts e dados versionados) | 3.9 | Sim (repositório público, JSONs sanitizados) |
| Limitações declaradas | 5, 6 | Sim |
| Figuras/tabelas geradas a partir de dados verificáveis | 4.8 | Não — pendência explícita registrada |

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

Fonte: `auditoria_conferencias.json` e `calibracao.json`, gerados em
23/07/2026. A coluna P (reclassificação conferida) está zerada nesta
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
