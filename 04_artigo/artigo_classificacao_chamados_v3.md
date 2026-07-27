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

A classificação automática de chamados de manutenção predial constitui um recurso estratégico para qualificar a triagem operacional e ampliar a governança baseada em evidências em instituições públicas. Entretanto, as categorias registradas em sistemas administrativos podem refletir taxonomias sobrepostas, informações incompletas e interpretações heterogêneas das equipes de atendimento.

Este artigo propõe um protocolo multimodelo para a classificação de chamados reais de manutenção predial universitária em português brasileiro, extraídos do sistema GLPI da Universidade Federal do Sul da Bahia. O corpus reúne 13.965 chamados não vazios, distribuídos em 55 categorias históricas, e compara classificadores baseados em TF-IDF — Naive Bayes, Regressão Logística, LinearSVC, SGD, Random Forest e Extra Trees — com uma rede neural LSTM bidirecional. O BERTimbau é apresentado como extensão planejada.

O protocolo distingue a concordância com o histórico administrativo do acerto avaliado por revisão humana, tratando a categoria original como referência preliminar. A conferência abrange 9.534 chamados, dos quais 9.044 possuem decisão travada e 52 apresentam conflito entre as fontes avaliadas. O LinearSVC alcança a maior concordância com o histórico, com 80,31% (IC95%: 79,63%–80,97%), e o maior acerto validado, com 95,02% (IC95%: 94,58%–95,46%). A LSTM obtém, respectivamente, 67,18% e 88,11%.

Na faixa de confiança igual ou superior a 95%, o classificador operacional alcança 99,94% de acerto em 4.675 decisões validadas. Os resultados referem-se à amostra conferida, cuja composição é discutida na Seção 5. A rejeição da normalidade sustenta o emprego de testes não paramétricos. Em conjunto, os achados mostram que classificadores lineares oferecem equilíbrio favorável entre desempenho, custo computacional e auditabilidade para textos técnicos curtos, ruidosos e desbalanceados.

**Palavras-chave:** manutenção predial; classificação de chamados; processamento de linguagem natural; rótulos ruidosos; validação humana; governança preditiva.

**ABSTRACT**

*Automatic classification of building-maintenance work orders is a strategic resource for improving operational triage and evidence-based governance in public institutions. Administrative categories, however, may reflect overlapping taxonomies, incomplete information and heterogeneous interpretations by maintenance teams.

This study proposes a multi-model protocol for 13,965 real university building-maintenance work orders in Brazilian Portuguese, organized into 55 historical categories. The comparison includes TF-IDF-based classifiers — Naive Bayes, Logistic Regression, LinearSVC, SGD, Random Forest and Extra Trees — and a bidirectional LSTM. BERTimbau is presented as a planned extension.

The protocol distinguishes agreement with the administrative history from accuracy against human-reviewed decisions. Human review covers 9,534 records, including 9,044 locked decisions and 52 conflicts. LinearSVC achieves the highest historical agreement, 80.31% (95% CI: 79.63%–80.97%), and the highest validated accuracy, 95.02% (95% CI: 94.58%–95.46%). LSTM reaches 67.18% and 88.11%, respectively.

For predictions with confidence equal to or greater than 95%, the operational classifier reaches 99.94% validated accuracy across 4,675 decisions. The results refer to the reviewed sample, whose composition is discussed in Section 5. Rejection of normality supports non-parametric testing. Overall, linear classifiers provide a favorable balance between performance, computational cost and auditability for short, noisy and imbalanced technical text.*

***Keywords:** building maintenance; work-order classification; natural language processing; noisy labels; human validation; predictive governance.*

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

O corpus experimental é composto por 13.965 chamados de manutenção predial não vazios, distribuídos em 55 categorias históricas e extraídos do ambiente institucional da UFSB. Os campos considerados incluem o título e a descrição do chamado, além do título e da descrição da ordem de serviço. Esses campos foram concatenados em uma única representação textual para a classificação.

A categoria histórica foi utilizada como referência administrativa preliminar. A avaliação principal empregou a categoria definida pela memória de decisão resultante da conferência humana. Os textos estão redigidos em português brasileiro e contêm jargões técnicos, abreviações locais, nomes de equipamentos e descrições incompletas, características típicas de registros operacionais de manutenção (SUNDARAM; ZEID, 2025).

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

O desenho experimental compara sete modelos organizados em três famílias conceituais, selecionadas em função das características do corpus, composto por textos curtos, vocabulário técnico e forte desbalanceamento entre categorias.

A família linear reúne LinearSVC, Regressão Logística e SGD, aplicados à representação TF-IDF esparsa. Em espaços de alta dimensionalidade, fronteiras lineares apresentam desempenho competitivo quando o vocabulário possui elevado poder discriminativo, como ocorre com termos técnicos associados a equipamentos, sistemas prediais e manifestações de falha (JOACHIMS, 1998; SALTON; BUCKLEY, 1988).

Random Forest e Extra Trees representam a família de *ensembles* de árvores e permitem modelar interações não lineares entre atributos. O Naive Bayes Multinomial funciona como referência probabilística de menor complexidade. A LSTM bidirecional representa a família neural e modela dependências sequenciais, com *embeddings* treinados diretamente no corpus (GRAVES; SCHMIDHUBER, 2005).

O BERTimbau é previsto como extensão contextual pré-treinada em português. Como seu ajuste fino ainda não dispõe de métricas rastreáveis, o modelo permanece fora dos rankings e dos testes comparativos.

**3.4.1 Diferenças conceituais e operacionais entre os classificadores**

Os classificadores avaliados adotam hipóteses distintas sobre a estrutura dos dados. O Naive Bayes representa uma abordagem probabilística; LinearSVC, Regressão Logística e SGD empregam fronteiras discriminativas lineares; Random Forest e Extra Trees modelam relações não lineares; e a LSTM explora a sequência dos termos. Essas diferenças explicam parte da variação observada nas Tabelas 1 e 2.

O LinearSVC maximiza a margem de separação entre classes sobre uma matriz TF-IDF esparsa com até 5.000 atributos. Termos como *bomba*, *split*, *disjuntor*, *vazamento*, *infiltração* e *ar-condicionado* atuam como âncoras semânticas. Essa estrutura favorece fronteiras lineares e é compatível com a liderança do modelo na concordância histórica e no acerto validado (JOACHIMS, 1998; SALTON; BUCKLEY, 1988).

O Naive Bayes assume independência condicional entre os atributos. Essa hipótese se ajusta de maneira limitada aos chamados de manutenção, nos quais termos técnicos aparecem em combinações recorrentes. Seu desempenho inferior caracteriza a referência de menor complexidade da comparação.

Random Forest e Extra Trees capturam interações entre atributos, mas apresentam custo computacional superior ao dos classificadores lineares. Na base analisada, essa complexidade produz desempenho intermediário, sem ganho de acerto validado que compense o aumento do tempo de treino. Os tempos medidos são apresentados na Tabela 6 (SCHWARTZ *et al.*, 2020; TREVISO *et al.*, 2023).

A LSTM bidirecional utiliza *embeddings* inicializados aleatoriamente e treinados sem vetores pré-treinados em português. Sua camada de *embedding*, com 8.000 termos e 128 dimensões, reúne aproximadamente 1,02 milhão de parâmetros. Cada partição de treino contém cerca de 11.172 exemplos, relação que favorece os modelos lineares em um corpus de porte médio e com ruído de rótulo (GALKE; SCHERP, 2022).

No classificador operacional, a LSTM é empregada quando a base rotulada atinge o número mínimo de exemplos previsto pelo protocolo. Abaixo desse limiar, utiliza-se Random Forest sobre TF-IDF. A confiança das predições é organizada em faixas que orientam a conferência humana e a análise de calibração.

**3.5 Desenho de avaliação**

A avaliação utiliza predições fora da amostra em protocolo *out-of-fold*, com *KFold* embaralhado em cinco partições, semente fixa e divisão idêntica para todos os modelos. A partição não é estratificada devido à presença de categorias com suporte unitário. O uso das mesmas partições permite comparações pareadas entre classificadores (SOKOLOVA; LAPALME, 2009).

As métricas principais são acurácia, *macro*-F1, F1 ponderado, *balanced accuracy* e intervalos de confiança de 95% por *bootstrap*. A *macro*-F1 e a *balanced accuracy* conferem peso às categorias raras e complementam a acurácia global em uma base desbalanceada (EFRON, 1979; EFRON; TIBSHIRANI, 1993; SOKOLOVA; LAPALME, 2009).

As diferenças globais e pareadas foram examinadas por testes não paramétricos. O McNemar foi aplicado às comparações entre modelos, com correção de Holm-Bonferroni para o conjunto de testes. A verificação detalhada dos pressupostos, as matrizes de comparação e os resultados dos testes complementares são apresentados no Material Suplementar.

A escolha do protocolo *k-fold* foi confrontada com um *holdout* aleatório de 15%. A estratificação do *holdout* mostrou-se inviável devido às categorias com um único exemplo, e a divisão aleatória deixou classes raras sem observações de teste. Embora a acurácia global tenha variado pouco, o *holdout* reduziu a *macro*-F1 da maioria dos modelos. O protocolo *k-fold* foi, portanto, mantido por avaliar todos os registros e oferecer estimativas mais estáveis para as categorias de menor suporte (KOHAVI, 1995).

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
travada e reaproveitada diretamente nas ciclos posteriores de
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

Os resultados são produzidos por um pipeline automatizado e reprodutível. Os agregados publicados não contêm identificadores pessoais, títulos ou descrições livres dos chamados. Os códigos, métricas derivadas e arquivos sanitizados necessários à reprodução das figuras e tabelas estão disponíveis no repositório público do estudo.

**4. RESULTADOS**

A análise separa a concordância com a categoria histórica do desempenho contra a decisão validada por conferência humana. A base contém 13.965 chamados, dos quais 9.534 foram conferidos. Entre eles, 9.044 possuem categoria decidida e 490 permanecem sem verdade validada, incluindo 52 conflitos.

Os resultados evidenciam três padrões. Os classificadores lineares, liderados pelo LinearSVC, apresentam o melhor desempenho global. A conferência humana demonstra que concordância administrativa e acerto validado são dimensões distintas. Por fim, as faixas superiores de confiança concentram maior proporção de decisões corretas.

**4.1 Concordância com o histórico (base completa)**

Na base completa, o LinearSVC alcança acurácia de 0,8031 (IC95%: 0,7963–0,8097), seguido por Extra Trees (0,7894), Random Forest (0,7816), SGD (0,7767), Regressão Logística (0,7682), Naive Bayes (0,6997) e LSTM (0,6718). O teste de Cochran Q identifica diferença global entre os sete modelos (*p* < 0,001).

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

Fonte: elaborado pelos autores (2026), com base nos agregados da comparação multimodelo.

O desempenho varia entre as 55 categorias. As classes com menor F1 possuem, em sua maioria, suporte inferior a sete registros, o que amplia a influência de pequenas variações absolutas. As métricas completas por categoria são apresentadas na Tabela Suplementar S1.

**4.2 Ranking validado por conferência humana**

A comparação contra as 9.044 decisões travadas mantém o LinearSVC na primeira posição, com acerto validado de 0,9502 (IC95%: 0,9458–0,9546). Em seguida aparecem SGD (0,9411), Regressão Logística (0,9371), Extra Trees (0,9286), Random Forest (0,9241), LSTM (0,8811) e Naive Bayes (0,8627).

A diferença entre LinearSVC e SGD é de 0,91 ponto percentual, com McNemar *p* ≈ 5,70 × 10⁻⁸. Os *ensembles* por maioria ponderada, confiança máxima e maioria simples alcançam, respectivamente, 0,9467, 0,9458 e 0,9445. O LinearSVC isolado permanece como a opção de maior desempenho. A composição da amostra validada e seus efeitos sobre a interpretação dos resultados são discutidos na Seção 5.

A análise de sensibilidade inclui os 490 casos sem verdade validada como erros no cenário conservador. A amplitude entre os limites varia de 4,43 a 4,88 pontos percentuais e preserva a ordenação dos sete modelos.

**Tabela 2** Acerto validado contra a verdade decidida M/N/P (n = 9.044) e intervalo de sensibilidade

| Modelo | Acerto validado (limite superior) | IC95% | Limite inferior (pior caso) |
|---|---|---|---|
| LinearSVC | 0,9502 | 0,9458 -- 0,9546 | 0,9014 |
| SGD | 0,9411 | 0,9363 -- 0,9459 | 0,8927 |
| Regressão Logística | 0,9371 | 0,9321 -- 0,9421 | 0,8889 |
| Extra Trees | 0,9286 | 0,9234 -- 0,9335 | 0,8808 |
| Random Forest | 0,9241 | 0,9186 -- 0,9295 | 0,8767 |
| LSTM | 0,8811 | 0,8743 -- 0,8880 | 0,8359 |
| Naive Bayes | 0,8627 | 0,8558 -- 0,8696 | 0,8183 |

Fonte: elaborado pelos autores (2026). O limite inferior considera os conflitos e os demais registros sem verdade validada como erros para todos os modelos.

**4.3 Interpretação conjunta da classificação operacional e do histórico**

A classificação operacional e a categoria histórica foram comparadas com a mesma decisão validada em 9.044 chamados. Ambas coincidem com a decisão em 8.476 casos. Em 559 registros, o histórico coincide com a decisão e a classificação operacional diverge; em outros nove, ambas divergem.

A ausência de ocorrências na combinação “classificação operacional correta e histórico incorreto” decorre da regra empregada para construir a verdade validada. A decisão é formada a partir das próprias fontes submetidas à conferência e somente é travada quando ao menos uma delas é confirmada. Essa dependência estrutural restringe a combinação correspondente e impede que seu valor seja interpretado como estimativa da capacidade da IA de corrigir o histórico.

O valor zero representa, portanto, uma propriedade do protocolo de decisão, e não evidência de que classificadores automáticos sejam incapazes de identificar categorias históricas inadequadas. A avaliação dessa capacidade exige uma amostra independente, anotada sem utilizar como ponto de partida as classificações comparadas.

**4.4 Confiança, calibração e faixas de decisão**

O classificador operacional apresenta erro esperado de calibração histórico de 0,0656. Na faixa de confiança igual ou superior a 95%, que reúne 4.810 chamados, a concordância com o histórico é de 98,75%. Entre as 4.675 decisões humanas disponíveis nessa faixa, o acerto validado alcança 99,94%.

A confiança utilizada é bruta, derivada da função de decisão ou da saída probabilística dos modelos. Esses valores sustentam uma política de priorização por faixas e fornecem a base empírica para a calibração formal por Platt, regressão isotônica ou escalonamento de temperatura.

**Tabela 3** Acerto validado por faixa de confiança bruta, classificador operacional

| Faixa | n total | Concord. histórico | n validados | Acerto validado |
|---|---|---|---|---|
| <50% | 4.058 | 43,05% | 880 | 51,93% |
| 50-70% | 1.443 | 75,12% | 712 | 87,50% |
| 70-80% | 946 | 87,10% | 653 | 96,78% |
| 80-90% | 1.484 | 82,82% | 1.065 | 97,84% |
| 90-95% | 1.224 | 95,59% | 1.059 | 99,15% |
| >= 95% | 4.810 | 98,75% | 4.675 | 99,94% |

Fonte: elaborado pelos autores (2026), após deduplicação por `linha_planilha`.

**4.5 Reclassificação e ganho líquido**

Todos os modelos apresentam ganho líquido positivo na reclassificação. A LSTM registra o maior ganho absoluto, com 670 correções e 571 prejuízos, resultando em saldo de +99. A Regressão Logística alcança +92, e o LinearSVC, +73.

O ganho líquido combina comparações contra a decisão validada e, nos casos sem decisão travada, contra a categoria histórica. Sua principal função é orientar a seleção de chamados e modelos para revisão. A aplicação seletiva, vinculada à memória de decisão humana, concentra o benefício da reclassificação nos casos em que há evidência suficiente para alterar a categoria.

**Tabela 4** Ganho líquido de reclassificação por modelo

| Modelo | Total reclassificado | Corrigidos | Prejudicados | Ganho líquido | Reuso de decisão humana |
|---|---|---|---|---|---|
| LSTM | 13.905 | 670 | 571 | +99 | 8.805 |
| Regressão Logística | 13.932 | 245 | 153 | +92 | 8.727 |
| LinearSVC | 13.965 | 291 | 218 | +73 | 8.856 |
| Random Forest | 13.912 | 234 | 186 | +48 | 8.719 |
| SGD | 13.965 | 201 | 163 | +38 | 8.771 |
| Naive Bayes | 13.826 | 158 | 132 | +26 | 8.623 |
| Extra Trees | 13.899 | 237 | 226 | +11 | 8.713 |

Fonte: elaborado pelos autores (2026), após deduplicação dos registros de reclassificação por identificador.

**4.6 Diagnóstico de taxonomia e ambiguidade estrutural (Shannon/Jensen-Shannon)**

A análise de Shannon e Jensen-Shannon considera o classificador operacional e os sete modelos materializados. O classificador operacional apresenta a maior diversidade de categorias previstas e a menor divergência em relação à distribuição histórica.

No nível dos chamados, 3.277 registros, equivalentes a 23,5% da base, apresentam alta entropia de votos. Esses casos concentram desacordo entre arquiteturas e formam uma fila de auditoria orientada por ambiguidade estrutural.

No nível das categorias, foram identificadas 76 ocorrências de alta ambiguidade entre classes com suporte mínimo de 30 registros. A análise indica onde a inspeção taxonômica deve ser concentrada, enquanto as decisões de fusão, separação ou redefinição de categorias permanecem sob responsabilidade da equipe técnica.

**Tabela 5** Entropia de Shannon e divergência de Jensen-Shannon por fonte de classificação

| Fonte | Categorias previstas | Entropia (nats) | Entropia normalizada | JS vs. histórico |
|---|---|---|---|---|
| Classificador operacional | 53 | 4,6758 | 0,8163 | 0,0286 |
| LSTM | 52 | 4,6201 | 0,8105 | 0,0847 |
| Regressão Logística | 52 | 4,4490 | 0,7805 | 0,0716 |
| SGD | 53 | 4,4363 | 0,7745 | 0,0639 |
| LinearSVC | 53 | 4,3356 | 0,7569 | 0,0575 |
| Extra Trees | 47 | 3,9955 | 0,7193 | 0,0761 |
| Random Forest | 47 | 3,9574 | 0,7124 | 0,0804 |
| Naive Bayes | 19 | 3,3340 | 0,7848 | 0,1755 |

Fonte: elaborado pelos autores (2026). O BERTimbau permanece fora da comparação por não dispor de ajuste fino concluído.

**4.7 Custo computacional**

A comparação de custo abrange os seis modelos clássicos com medições realizadas em lotes de 1.000 registros. Os tempos de treino variam entre 1,14 segundo para o Naive Bayes e 21,30 segundos para o Extra Trees. O LinearSVC treina em 2,55 segundos e apresenta o melhor acerto validado entre os modelos avaliados.

As medições posicionam o LinearSVC na região de melhor equilíbrio entre desempenho e custo. LSTM e BERTimbau deverão ser incorporados à comparação quando dispuserem de medições produzidas sob o mesmo protocolo.

**Tabela 6** Custo computacional por lote de 1.000 registros

| Modelo | Tempo de treino (s) | Tempo de inferência (s) | Acurácia neste lote |
|---|---|---|---|
| Naive Bayes | 1,14 | 0,07 | 0,539 |
| LinearSVC | 2,55 | 0,06 | 0,655 |
| SGD | 2,60 | 0,09 | 0,624 |
| Regressão Logística | 9,43 | 0,09 | 0,624 |
| Random Forest | 19,45 | 0,13 | 0,597 |
| Extra Trees | 21,30 | 0,14 | 0,610 |

Fonte: elaborado pelos autores (2026). A acurácia desta tabela contextualiza o *trade-off* custo–desempenho no lote medido; as métricas principais permanecem nas Tabelas 1 e 2.

**4.8 Figuras**

As figuras foram geradas a partir dos dados vigentes do painel público e
dos registros de treino de cada modelo. A Figura 4 usa códigos de
categoria para preservar a legibilidade; o mapeamento completo
código-categoria está na Tabela Suplementar S2.

![Figura 2 — Confiança bruta × concordância com o histórico × acerto validado, por faixa de confiança (classificador operacional).](04_artigo/figuras/fig2_confianca_desfecho.png)

**Figura 2** Confiança bruta × concordância com o histórico × acerto validado,
por faixa de confiança (classificador operacional). Mesmos números da
Tabela 3 (Subseção 4.4), em forma gráfica.

Fonte: elaborado pelos autores (2026).

![Figura 3 — Trade-off entre acerto validado e custo computacional (tempo de treino), modelos clássicos.](04_artigo/figuras/fig3_tradeoff_custo.png)

**Figura 3** Trade-off entre acerto validado (conferência humana) e custo
computacional (tempo de treino, lote de 1.000 registros), modelos
clássicos. LSTM e BERTimbau não constam desta figura por não terem
registro de tempo de treino no mesmo arquivo (Tabela 6, Subseção 4.7).

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

**4.9 Estudo de ablação da LSTM**

A comparação entre o estudo de ablação e a avaliação principal da LSTM revelou duas fontes de diferença. A primeira foi a presença de grupos textuais repetidos entre treino e teste no *KFold* originalmente utilizado. Entre as 9.096 observações da coorte de ablação, 4.250 possuíam duplicata textual normalizada em outra partição.

O estudo foi refeito com *GroupKFold* definido pelo *hash* do texto normalizado. A alteração reduziu o acerto da configuração com 64 unidades e *dropout* de 0,5 de 87,68% para 86,35%, diferença de 1,33 ponto percentual. O resultado indica que a repetição textual produzia efeito mensurável, porém limitado.

A segunda fonte de diferença foi o desalinhamento entre a base utilizada no estudo de ablação e a referência empregada na comparação inicial. Na avaliação principal, a LSTM alcança 88,11%, enquanto o estudo corrigido alcança 86,35%. A diferença residual de 1,76 ponto percentual é compatível com as distinções entre os protocolos de particionamento e treinamento.

As quatro variantes avaliadas apresentam diferença inferior a quatro pontos percentuais. O resultado mostra baixa sensibilidade da LSTM às combinações testadas de número de unidades e *dropout*, ao mesmo tempo que confirma a importância do agrupamento de textos repetidos na construção das partições.

Fonte: elaborado pelos autores (2026).

**4.10 Robustez estatística**

Os pressupostos da análise foram verificados segundo protocolo adaptado de Zuur, Ieno e Elphick (2010). A normalidade foi rejeitada para os sete modelos, sustentando o emprego de testes não paramétricos. As comparações por McNemar com correção de Holm-Bonferroni confirmam a superioridade estatística do LinearSVC; os diagnósticos, testes complementares e tabelas completas são apresentados no Material Suplementar.

**5. DISCUSSÃO**

O LinearSVC apresenta o melhor resultado tanto na concordância com o histórico quanto no acerto validado. Seu desempenho de 95,02%, associado ao tempo de treino de 2,55 segundos por lote de 1.000 registros, demonstra que uma representação TF-IDF combinada com um classificador linear constitui solução eficiente para chamados técnicos curtos e com vocabulário especializado.

O resultado também confirma a relevância de distinguir concordância administrativa de acerto validado. A diferença entre as duas métricas mostra que a avaliação de classificadores em bases institucionais depende da qualidade do rótulo de referência. A conferência humana acrescenta uma camada de governança ao separar erro de modelo, inconsistência histórica e ambiguidade taxonômica.

A combinação “IA correta e histórico incorreto” não foi observada na análise conjunta porque a regra de decisão utiliza as próprias fontes comparadas para formar a categoria validada. Essa dependência restringe estruturalmente a matriz e explica o valor zero. O resultado caracteriza o funcionamento da memória de decisão e aponta para a necessidade de uma amostra independente quando o objetivo for estimar diretamente a capacidade da IA de corrigir o histórico.

Os ganhos positivos de reclassificação indicam que os modelos contêm informação útil mesmo quando não ocupam a primeira posição no ranking global. A LSTM, por exemplo, apresenta o maior ganho líquido absoluto. A estratégia mais produtiva consiste em combinar a liderança global do LinearSVC com o uso complementar dos demais modelos para localizar divergências, identificar casos ambíguos e selecionar chamados para auditoria.

A entropia de votos acrescenta uma dimensão distinta da confiança individual. Os 3.277 chamados com alto desacordo entre modelos representam regiões da base em que diferentes hipóteses de classificação produzem respostas incompatíveis. Esse indicador direciona a revisão taxonômica e fortalece a gestão da incerteza no protocolo.

A faixa de confiança igual ou superior a 95% alcança 99,94% de acerto validado. O resultado fornece base empírica para uma política gradual de automação, com tratamento diferenciado por faixa de confiança e integração da calibração formal antes da adoção operacional em maior escala.

**Limitações**

A principal limitação de cobertura decorre do uso de dados de uma única instituição federal de ensino superior, com taxonomia própria e textos em português brasileiro. A transferência dos resultados para outras organizações requer avaliação externa sob diferentes distribuições de chamados, estruturas de categorias e práticas de registro.

A amostra conferida não é probabilística. A seleção prioriza divergências entre modelos e histórico, casos críticos e regiões de baixa confiança. Assim, os valores de acerto caracterizam os 9.044 chamados com decisão travada e não constituem estimativa inferencial do desempenho sobre os 13.965 registros. Os 490 casos sem verdade validada, entre eles 52 conflitos, foram incorporados à análise de sensibilidade; mesmo no cenário conservador, o ranking dos modelos permanece estável (COCHRAN, 1977).

A comparação neural inclui apenas a LSTM treinada sem *embeddings* pré-treinados de domínio. A avaliação do BERTimbau permitirá examinar o efeito de representações contextuais em português e ampliar a comparação entre modelos lineares, sequenciais e transformadores.

**Papel no modelo de governança preditiva**

Este estudo constitui o Eixo 1 de um modelo de governança preditiva para manutenção predial, no qual o campus universitário é compreendido como biossistema construído. A classificação transforma registros textuais dispersos em dados estruturados, auditáveis e associados a indicadores de confiança.

Esses dados alimentam três desenvolvimentos complementares. O primeiro compreende modelos de séries temporais para previsão de custos e demanda por categoria. O segundo utiliza métodos multicritério, como MCDM e TOPSIS, para priorizar intervenções segundo critérios técnicos, ambientais, sociais e institucionais. O terceiro espacializa os chamados e seus indicadores por meio de geoprocessamento.

A camada de classificação oferece, assim, a infraestrutura informacional necessária para integrar previsão, priorização e análise territorial. Sua contribuição central reside na transformação do chamado individual em evidência reutilizável para planejamento e decisão.

**6. CONSIDERAÇÕES FINAIS**

O protocolo multimodelo identificou o LinearSVC como o classificador de melhor desempenho para os chamados analisados. O modelo alcançou 80,31% de concordância com o histórico e 95,02% de acerto na amostra validada, superando os demais classificadores e os três *ensembles*. Na faixa de confiança igual ou superior a 95%, o classificador operacional atingiu 99,94% de acerto em 4.675 decisões. Esses resultados, combinados ao baixo custo computacional, sustentam a adoção do LinearSVC como modelo principal, acompanhado de calibração de confiança e memória de decisão humana.

A contribuição do estudo ultrapassa a seleção de um classificador. O protocolo transforma textos operacionais ruidosos em dados estruturados e auditáveis, que podem alimentar previsão de custos e demanda, priorização multicritério de intervenções e análise espacial da manutenção. A classificação constitui, portanto, a camada informacional de base do modelo de governança preditiva aplicado ao biossistema construído universitário.

Os próximos passos concentram-se na validação externa em outras instituições, na calibração formal das probabilidades e margens de decisão e no treinamento comparativo do BERTimbau. Essas etapas permitirão avaliar a transferibilidade do protocolo, estabelecer limiares operacionais mais robustos e medir o ganho proporcionado por representações contextuais pré-treinadas em português.

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

**Apêndice A — Matriz de decisão M/N/P**

Contagens agregadas disponíveis nos JSONs públicos do painel:

| Métrica | n |
|---|---|
| Chamados com ao menos uma conferência (M, N ou P) | 9.534 |
| Decisões travadas (categoria decidida sem conflito) | 9.044 |
| Casos sem verdade validada | 490 |
| Conflitos entre fontes conferidas | 52 |
| Comparações válidas da IA oficial contra a verdade decidida | 9.044 |
| Registros no diagnóstico da conferência GLPI | 9.534 |
| Registros com conferência da reclassificação | 0 |

Fonte: elaborado pelos autores (2026), com base nos agregados vigentes de
auditoria e calibração. Não há registro com conferência da reclassificação
neste estudo.

*Pendência explícita*: o cruzamento fino de 3 vias (contagem por combinação
exata de valores de M × N × P — ex.: quantos casos têm M=Correto e N=Errado
simultaneamente) **não está disponível em nenhum JSON público atual** e exige
extração direta da planilha experimental (`Informação insuficiente para
verificar` com os dados hoje publicados). O que se aproxima disso é a matriz
2×2 IA×histórico da Tabela 4 (Subseção 4.3), que cruza acerto da IA e do
histórico contra a verdade decidida — não é o mesmo cruzamento M×N×P bruto,
mas cobre a mesma pergunta de fundo (quando IA e histórico concordam ou
divergem da decisão final).
