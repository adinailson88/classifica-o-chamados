---
header-includes:
  - |
    ```{=latex}
    \usepackage[font=small,labelfont=bf,justification=centering,skip=6pt]{caption}
    % POSICIONAMENTO DE FLOATS
    % A posicao 'h' foi acrescentada a 'tp' para que a figura possa assentar
    % onde e citada. So com 'tp' ela era empurrada ao topo da pagina seguinte, e
    % o trecho de texto que sobrava no pe da pagina anterior nao bastava para
    % fechar a coluna, o que abria vao. A posicao 'b' continua fora: figura no
    % rodape estourava a margem inferior.
    \makeatletter
    \def\fps@figure{htp}
    \makeatother
    % Fracoes folgadas reduzem a chance de o LaTeX desistir de encaixar o float
    % na pagina corrente e cria-la exclusiva para ele. O floatpagefraction alto
    % exige que uma pagina de float esteja quase cheia para existir.
    \renewcommand{\topfraction}{0.9}
    \renewcommand{\textfraction}{0.07}
    \renewcommand{\floatpagefraction}{0.9}
    \setcounter{topnumber}{3}
    \setcounter{totalnumber}{4}
    % Espacos ao redor dos floats: os padroes do article sao generosos e, com
    % sete figuras e oito tabelas, somam varias linhas perdidas.
    \setlength{\floatsep}{8pt plus 2pt minus 2pt}
    \setlength{\textfloatsep}{10pt plus 2pt minus 3pt}
    \setlength{\intextsep}{8pt plus 2pt minus 2pt}
    % \flushbottom no lugar de \raggedbottom: distribui a folga residual entre
    % os elementos da pagina em vez de acumula-la toda no rodape.
    \flushbottom
    % O texto usa titulos em negrito, nao comandos de secao, entao o LaTeX nao
    % tem ancora para esvaziar a fila de floats e acaba despejando figuras em
    % paginas onde nao cabem. As barreiras resolvem isso, mas cada uma que
    % encontra float pendente dispara \clearpage e abandona o resto da pagina,
    % entao sobraram apenas as que cercam tabelas: o pandoc emite longtable, que
    % nao e float e estoura a margem inferior quando divide pagina com figura.
    % O placeins vive em 04_artigo/latex porque nao existe na imagem
    % pandoc/extra do workflow; o ramo alternativo evita falha de build caso o
    % TEXINPUTS nao o alcance.
    \IfFileExists{placeins.sty}{%
      \usepackage{placeins}%
    }{%
      \makeatletter
      \newcommand\FloatBarrier{%
        \par
        \begingroup
          \let\@elt\relax
          \xdef\fb@pendentes{\@deferlist}%
        \endgroup
        \ifx\fb@pendentes\@empty\else\clearpage\fi
      }
      \makeatother
    }
    ```
---

**CLASSIFICAÇÃO AUTOMÁTICA MULTIMODELO DE CHAMADOS DE MANUTENÇÃO PREDIAL
UNIVERSITÁRIA EM PORTUGUÊS BRASILEIRO COM VALIDAÇÃO HUMANA**

*Multi-model automatic classification of university building maintenance work
orders in Brazilian Portuguese with human validation*

**Adinailson Guimarães de Oliveira** - adinailson.oliveira@cja.ufsb.edu.br
**Fabrício Berton Zanchi** - fabricio.berton@ufsb.edu.br

Universidade Federal do Sul da Bahia (UFSB), Programa de Pós-Graduação
em Biossistemas

**RESUMO**

A classificação automática de chamados de manutenção predial constitui
recurso estratégico para qualificar a triagem operacional e ampliar a
governança baseada em evidências em instituições públicas. Em bases
históricas de sistemas informatizados de gestão de chamados, contudo, a
categoria originalmente registrada não deve ser tratada como referência
definitiva, pois pode refletir decisões operacionais ruidosas, taxonomias
sobrepostas, registros incompletos e interpretações heterogêneas entre
equipes. Este artigo propõe um protocolo multimodelo para classificação
de chamados reais de manutenção predial universitária em português
brasileiro, extraídos do sistema institucional da Universidade Federal do
Sul da Bahia. O experimento utiliza 14.060 chamados não vazios,
organizados em 50 categorias históricas. A comparação principal avalia
seis classificadores clássicos baseados em TF-IDF e uma rede neural LSTM
bidirecional por predições *out-of-fold* sob validação cruzada agrupada
por texto, o que impede que chamados de texto idêntico atravessem treino
e teste. O BERTimbau, transformador pré-treinado em português, fica fora
da comparação por custo medido, uma vez que o ajuste fino projeta 6,44
horas por dobra em processador sem acelerador gráfico. O diferencial
metodológico reside na distinção entre concordância com o histórico
administrativo e acerto contra a referência humana revisada, obtida por
auditoria de rótulo conduzida por especialista único sobre a totalidade
do corpus e apurada sobre as 13.972 linhas de 41 categorias com suporte
nas cinco dobras. O LinearSVC lidera as duas leituras, com acordo bruto
de 79,61% frente ao histórico e acurácia de 82,53% frente à referência
humana. O achado central contraria a expectativa que motivou o estudo: o
ganho líquido de reclassificação da base histórica é negativo em todos os
sete modelos, de −1.846 no melhor deles a −3.474 no pior, porque o
especialista manteve a categoria histórica em 95,75% dos registros e
divergir do histórico significa, quase sempre, divergir também da
referência. Uma camada explícita de regras de periodicidade,
avaliada nas mesmas partições, mostra-se redundante e melhora o F1 macro
de apenas três dos sete modelos. O custo computacional permanece dimensão
relevante da decisão e favorece modelos lineares em cenários de texto
curto, ruidoso e desbalanceado: o LinearSVC treina em 2,44 s, contra
83,44 s da rede recorrente no mesmo ambiente. O F1 macro de 0,6684
resulta da composição da métrica, pois o mesmo modelo alcança 0,8207 nas
12 categorias que concentram 81,83% do volume e distingue manutenção
preventiva de corretiva com F1 de 0,9742 e 0,9547.

**Palavras-chave:** manutenção predial; classificação de chamados;
processamento de linguagem natural; rótulos ruidosos; validação humana.

**ABSTRACT**

*Automatic classification of building maintenance work orders is a
strategic resource for improving operational triage and evidence-based
governance in public institutions. However, the originally assigned
category in historical service-management databases should not be treated
as a definitive reference because it may reflect noisy operational
decisions, overlapping taxonomies, incomplete records, and heterogeneous
interpretations. This paper proposes a multi-model protocol for
classifying real university building maintenance requests in Brazilian
Portuguese from the Federal University of Southern Bahia. The experiment
uses 14,060 non-empty records organized into 50 historical categories.
The main comparison evaluates six TF-IDF-based classical classifiers and
a bidirectional LSTM through out-of-fold predictions under text-grouped
cross-validation, which prevents work orders sharing identical text from
crossing the train-test boundary. BERTimbau, a Portuguese pre-trained
transformer, is excluded from the main comparison on measured cost
grounds, as fine-tuning projects 6.44 hours per fold on a processor
without graphics acceleration. The methodological contribution is the
distinction between agreement with the administrative history and
accuracy against the revised human reference, obtained through a
label-audit review carried out by a single specialist over the entire
corpus and computed over 13,972 records in the 41 categories with support
across all five folds. LinearSVC leads both readings, with 79.61% raw
agreement against the history and 82.53% accuracy against the human
reference. The central finding contradicts the expectation that motivated
the study: the net gain from reclassifying the historical base is
negative for all seven models, from −1,846 in the best to −3,474 in the
worst, because the specialist retained the historical category in 95.75%
of records, so departing from the history almost always means departing
from the reference as well. An explicit periodicity rule layer,
evaluated on the same partitions, proves redundant and improves macro F1
for only three of the seven models. Computational cost remains a relevant
decision dimension and favors linear models in short, noisy, and
imbalanced text settings: LinearSVC trains in 2.44 s, against 83.44 s for
the recurrent network in the same environment. The macro F1 of 0.6684
stems from how the metric is composed, since the same model reaches
0.8207 on the 12 categories that concentrate 81.83% of the volume and
tells preventive from corrective maintenance with F1 of 0.9742 and
0.9547.*

***Keywords:** building maintenance; work-order classification; natural
language processing; noisy labels; human validation.*

**1. INTRODUÇÃO**

Um campus universitário pode ser descrito como um biossistema
construído, isto é, a integração dinâmica entre infraestrutura física,
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

A exploração analítica dessas bases enfrenta três obstáculos estruturais,
agravados pela restrição orçamentária que historicamente limita o custeio
da manutenção predial em IFES a patamares inferiores a 2% do orçamento
institucional (MARTINS; ESPEJO, 2024; PAMPANA *et al.*, 2022). O primeiro
é a natureza textual curta e heterogênea dos registros, redigidos em
linguagem técnica fragmentária, com abreviações locais e jargões de
equipe que dificultam a aplicação direta de modelos genéricos de
processamento de linguagem natural (PLN) (SUNDARAM; ZEID, 2025). O
segundo é o desbalanceamento entre categorias, dado que demandas
recorrentes de climatização, elétrica e hidrossanitária concentram grande
parte da base, ao passo que categorias raras dispõem de poucos exemplos
para treinamento supervisionado (LI *et al.*, 2024). O terceiro, e o mais
consequente do ponto de vista metodológico, é a qualidade do próprio
rótulo histórico, que pode resultar de interpretação rápida, conveniência
operacional ou taxonomia ainda não estabilizada, de modo a constituir
evidência importante, mas não referência definitiva (ZHANG *et al.*,
2025; KEJRIWAL *et al.*, 2024).

A literatura recente confirma a relevância do PLN para converter esses
registros em insumo de gestão. Li *et al.* (2024) demonstraram, em base
hospitalar com 15.623 ordens de serviço, que a atribuição automática de
equipes alcança acurácia de 0,83; Bouabdallaoui *et al.* (2020)
reportaram acurácia média de 78% na classificação de requisições em
edificação hospitalar; e Sundaram e Zeid (2025), sob a abordagem de
*Technical Language Processing*, argumentam que textos técnicos de
manutenção funcionam como *black holes* informacionais quando armazenam
dados relevantes sem serem utilizados na decisão. A maior parte dessas
aplicações concentra-se, contudo, em bases em inglês ou chinês e em
domínios industriais ou hospitalares, o que configura lacuna para corpora
em português brasileiro no contexto da manutenção predial pública
universitária.

Diante desse quadro, a pergunta que orienta este artigo não é qual
classificador mais concorda com a categoria histórica, e sim como extrair
de texto ruidoso, de forma confiável e auditável, o dado estruturado
capaz de alimentar um sistema de governança preditiva sem herdar
acriticamente as inconsistências do histórico que lhe deu origem, de modo
que divergências entre modelo e histórico sejam tratadas como evidência
de revisão taxonômica, e não como ruído a descartar.

Com base em chamados reais da Universidade Federal do Sul da Bahia
(UFSB), este artigo propõe uma comparação multimodelo de classificadores
de texto aplicada a chamados de manutenção predial em português
brasileiro. A base experimental contém 14.060 chamados não vazios em 50
categorias históricas, e os campos textuais agregam título e descrição do
chamado, além de informações da ordem de serviço. O estudo compara
modelos clássicos baseados em TF-IDF com uma rede neural LSTM
bidirecional; o BERTimbau é ajustado, mas fica fora da comparação
principal por custo medido. O objeto de avaliação não é o classificador
isolado, mas o protocolo de governança que articula aprendizado de
máquina, auditoria estatística, custo computacional e revisão humana,
formulação consoante à manutenção baseada em evidências preconizada pela
NBR 5674 (ABNT, 2012) e à integração físico-humano-tecnológico-ambiental
que caracteriza um biossistema construído.

Quatro objetivos específicos orientam o trabalho: apresentar um protocolo
de classificação que produza dado estruturado auditável a partir de texto
livre; distinguir a concordância com o rótulo histórico do acerto contra
a referência humana revisada; avaliar o desempenho por métricas balanceadas,
intervalos de confiança e testes pareados adequados a dados não normais,
incorporando o custo computacional como dimensão de decisão; e
determinar, por medição e não por presunção, se a classificação
automática é capaz de corrigir retroativamente a base histórica.

**2. REFERENCIAL CONCEITUAL**

**2.1 Processamento de linguagem natural em ordens de manutenção**

Ordens de manutenção constituem registros operacionais de valor
informacional elevado e uso habitualmente reduzido. Documentam sintomas,
locais, equipamentos, procedimentos e soluções executadas, acumulando-se
por anos em sistemas cuja forma textual e semiestruturada dificulta o
emprego direto em planejamento e alocação de recursos (PAMPANA *et al.*,
2022; MORAIS; PAULA; REIS, 2023). Li *et al.* (2024) constituem a
referência-âncora desta pesquisa por tratarem diretamente da automação de
ordens de manutenção predial, ainda que em idioma, tipologia
institucional e estrutura taxonômica distintos. Sundaram e Zeid (2025)
acrescentam perspectiva pertinente à manutenção predial universitária, na
qual chamados curtos, abreviações locais e descrições incompletas
inviabilizam o uso de modelos genéricos sem adaptação ao domínio, tese
que os 78% de acurácia média reportados por Bouabdallaoui *et al.* (2020)
sustentam ao mesmo tempo em que evidenciam a necessidade dessa adaptação
lexical e semântica ao corpus específico.

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

Modelos lineares com TF-IDF permanecem competitivos em tarefas de texto
curto, sobretudo quando o corpus é de porte médio, o vocabulário possui
alta especificidade técnica e as classes são desbalanceadas. Galke e
Scherp (2022), em revisão comparativa de métodos para classificação
textual, demonstraram que classificadores baseados em *bag-of-words* com
TF-IDF e SVM sustentam desempenho equivalente ao de redes neurais em
múltiplos *benchmarks* quando o corpus é reduzido ou o vocabulário é
especializado. O achado é particularmente pertinente à manutenção predial
institucional, cuja base operacional raramente atinge escala compatível
com as exigências de modelos de linguagem de grande porte.

**2.3 Rótulos ruidosos e referência operacional**

O ruído de rótulo é problema central do aprendizado supervisionado sobre
bases administrativas e, em classificação textual, decorre de ambiguidade
semântica, polissemia, insuficiência de contexto, sobreposição taxonômica
ou erro de registro (ZHANG *et al.*, 2025). Kejriwal *et al.* (2024)
acrescentam que *benchmarks* rotulados por humanos contêm variabilidade
relevante, o que questiona a prática de assumir referência única onde há
julgamento subjetivo. Neste artigo, por conseguinte, a categoria
histórica é tratada como registro administrativo sujeito a auditoria, e a
referência de avaliação é construída por revisão humana com registro
explícito da decisão.

**2.4 Custo computacional e eficiência em PLN**

A avaliação de modelos de PLN tem sido tradicionalmente orientada por
métricas de desempenho, mas a literatura recente enfatiza que custo
computacional, tempo de treino, consumo energético e reprodutibilidade
também devem compor a decisão de adoção (TREVISO *et al.*, 2023;
SCHWARTZ *et al.*, 2020). Treviso *et al.* (2023) argumentam que a
ampliação de escala em PLN aumenta o consumo de dados, tempo,
armazenamento e energia, motivando métodos eficientes em contextos de
recursos limitados, e Schwartz *et al.* (2020) cunharam o conceito de
*Green AI*, pelo qual a eficiência computacional deve ser reportada e
valorizada na avaliação de modelos, não apenas a acurácia. Em uma
instituição pública, essa dimensão é operacionalmente decisiva. Um modelo
que treina em segundos pode ser reexecutado frequentemente,
auditado com facilidade e mantido sem infraestrutura dedicada, ao passo
que um modelo que demanda dezenas de minutos exige *checkpoint*,
controle de versão de pesos e justificativa robusta de ganho marginal
(TREVISO *et al.*, 2023).

Os modelos de linguagem de grande porte não integram esta comparação.
Operam sobre representações contextuais em arquitetura de transformador
(VASWANI *et al.*, 2017), dispõem de bilhões de parâmetros contra os
aproximadamente 110 milhões do BERTimbau (SOUZA; NOGUEIRA; LOTUFO, 2020)
e dispensam ajuste supervisionado, pois inferem a tarefa de instruções e
de poucos exemplos no próprio enunciado (BROWN *et al.*, 2020), do que
decorre a expectativa de maior acurácia em chamados de redação atípica.
Sua adoção esbarra, contudo, em três restrições diante do critério de
eficiência aqui adotado: a execução exige aceleradores dedicados ou
serviços tarifados por uso, incompatíveis com a reexecução frequente que
o fluxo institucional pressupõe; o processamento por terceiros desloca as
descrições dos chamados para fora do domínio da universidade; e a
variabilidade das respostas entre versões do serviço compromete a
reprodutibilidade exigida pelo delineamento (BENDER *et al.*, 2021).
Tendo em vista que a tarefa é fechada e institucionalmente delimitada,
condição na qual classificadores baseados em *bag-of-words* permanecem
competitivos (GALKE; SCHERP, 2022), a avaliação desses modelos fica
indicada como desdobramento futuro.

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
consolidação da base; (ii) revisão humana do corpus integral, da qual
resulta a categoria de referência; (iii) higienização textual; (iv)
construção da matriz de atributos; (v) partições agrupadas por texto e
treinamento com predições *out-of-fold*; (vi) comparação com a categoria
histórica e com a referência revisada; (vii) inferência estatística não
paramétrica; e (viii) calibração e automação seletiva por confiança. A
Figura 1 apresenta esse fluxo como *pipeline* de governança preditiva. A
posição da revisão humana não é acessória: ela precede o treinamento,
porque é dela que sai o rótulo com que os modelos são treinados e contra
o qual são avaliados.

![Pipeline de governança preditiva, do fluxo de extração da base à retroalimentação por validação humana.](04_artigo/figuras/fig_pipeline_governanca.pdf){width=95%}

**3.2 Corpus e variáveis**

O corpus experimental é composto por 14.060 chamados de manutenção
predial não vazios, organizados em 50 categorias históricas, extraídos
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

A base é dinâmica, pois a planilha de trabalho é alimentada continuamente
pelo sistema de atendimento. Por essa razão, todos os resultados da Seção
4 referem-se a um corte por data de abertura, que compreende os chamados
registrados até 1º de agosto de 2026 e totaliza 14.060 registros
elegíveis. Os artefatos que sustentam cada número foram materializados
sobre esse mesmo corte e estão versionados, de modo que a reprodução não
depende do estado corrente do sistema institucional. A distribuição
completa dos chamados entre as 50 categorias históricas é apresentada no
Apêndice A.

**3.3 Pré-processamento textual**

O pré-processamento textual é documentado de modo reprodutível, uma
vez que pequenas decisões sobre normalização podem alterar a matriz de
atributos e, consequentemente, o desempenho dos modelos (SALTON;
BUCKLEY, 1988). Para os classificadores clássicos, a representação
principal é TF-IDF com *n-gramas* de uma e duas palavras e limite
superior de 30.000 atributos para controle de dimensionalidade. Para o
modelo neural LSTM, são utilizadas tokenizações específicas com
vocabulário de 8.000 termos e comprimento máximo de 120 tokens por
sequência. O vetorizador, o tokenizador e o vocabulário são ajustados
dentro de cada dobra, sobre a partição de treino, de modo que nenhuma
estatística do conjunto de teste participa da representação. Cabe
ressaltar que a etapa de
pré-processamento não elimina indiscriminadamente termos técnicos,
códigos de ambientes, nomes de equipamentos ou expressões recorrentes da
equipe, pois esses elementos possuem alto valor discriminativo em
manutenção predial, onde palavras como *bomba*, *split*, *disjuntor*,
*vazamento*, *infiltração* e *ar-condicionado* podem funcionar como
âncoras semânticas relevantes para categorias específicas.

**3.4 Modelos avaliados**

O desenho experimental compara sete modelos, organizados
em três famílias conceituais, cada uma escolhida por um motivo
específico ligado às características do domínio, ou seja, texto curto,
vocabulário técnico e forte desbalanceamento entre categorias (Subseção
3.2).

A família linear (LinearSVC, Regressão Logística e SGD) opera
diretamente sobre a representação TF-IDF esparsa (Subseção 3.3). Em
espaços de alta dimensionalidade, fronteiras lineares tendem a separar
bem as classes quando o vocabulário carrega forte poder discriminativo
(JOACHIMS, 1998; SALTON; BUCKLEY, 1988), como é o caso dos termos
técnicos de manutenção predial, que funcionam como âncoras semânticas de
categoria. A família de *ensembles* de árvores (Random Forest e Extra
Trees) captura interações não lineares entre atributos, a um custo
computacional maior. O **Naive Bayes Multinomial** entra como *baseline*
probabilístico mais simples, útil para calibrar a expectativa de
desempenho mínimo (JOACHIMS, 1998; PEDREGOSA *et al.*, 2011). A rede
neural (LSTM Bidirecional) modela dependências sequenciais no texto,
mas treina seus *embeddings* do zero, sem incorporar vetores
pré-treinados em português (GRAVES; SCHMIDHUBER, 2005). A Subseção 3.4.1
discute por que essa escolha tende a penalizar o desempenho em corpora
de porte médio como o deste estudo. Os sete modelos são avaliados na
comparação *out-of-fold* (Subseção 4.1). Em paralelo, a classificação
automática em produção opera com uma regra de contingência que aciona o
Random Forest quando a base rotulada disponível é insuficiente para
treinar a rede neural.

Um oitavo modelo, o BERTimbau-Base, incorpora representações contextuais
pré-treinadas em português brasileiro e é ajustado para as 50 categorias
do corpus (DEVLIN *et al.*, 2019; SOUZA; NOGUEIRA; LOTUFO, 2020). O
treino foi concluído em modo automático, com subamostragem estratificada
e parada antecipada por restrição computacional. Como o modelo não possui
predições *out-of-fold* materializadas sobre toda a base, ele não é
inserido artificialmente no ranking integral dos sete modelos. Sua
viabilidade computacional é examinada na Subseção 4.3.

**3.4.1 Diferenças conceituais e operacionais entre os classificadores**

Os sete modelos comparáveis cobrem quatro famílias
com suposições distintas sobre os dados: um gerador probabilístico
(Naive Bayes), discriminadores lineares (LinearSVC, Regressão Logística,
SGD), *ensembles* não lineares baseados em árvores (Random Forest, Extra
Trees) e uma rede neural sequencial (LSTM). Cada família responde de
forma diferente a um corpus de texto curto, ruidoso e com forte
desbalanceamento entre categorias (Subseção 3.2; Tabela A2), o que ajuda
a explicar por que o desempenho não é uniforme entre elas nas Tabelas 1
e 2.

Os discriminadores lineares otimizam fronteiras de decisão sobre a
representação TF-IDF esparsa de até 30.000 atributos (Subseção 3.3), e é
essa a família favorecida pelo corpus, pois em espaços esparsos de alta
dimensionalidade eles separam bem as classes quando o vocabulário carrega
forte poder discriminativo (JOACHIMS, 1998; SALTON; BUCKLEY, 1988),
condição satisfeita aqui, em que termos técnicos do domínio funcionam
como âncoras semânticas de categoria. O Naive Bayes, na outra
extremidade, assume independência condicional entre atributos dada a
classe, suposição violada em texto de manutenção predial, no qual termos
técnicos co-ocorrem sistematicamente dentro de uma mesma categoria; daí
sua última posição nas duas leituras e o colapso do F1 macro em 0,2951,
com predições restritas a 22 das 41 categorias.

Random Forest e Extra Trees capturam interações não lineares por meio da
estrutura de árvores, mas em espaços esparsos tendem a ajustar-se demais
às co-ocorrências frequentes, o que se reflete no desempenho intermediário
de ambos. O custo computacional dessa família é também o mais alto entre
os modelos clássicos medidos, entre 9,3 e 10,9 vezes o tempo de treino do
LinearSVC (Tabela 5), e só se justificaria se revertido em ganho de
acurácia, o que não se confirma nos dados analisados (SCHWARTZ *et al.*,
2020; TREVISO *et al.*, 2023).

A LSTM bidirecional é projetada para modelar dependências sequenciais no
texto, mas seus *embeddings* são inicializados aleatoriamente e treinados
do zero, sem incorporação de vetores pré-treinados em português. A camada
de *embedding* concentra sozinha cerca de 1,02 milhão de parâmetros,
ordem de grandeza próxima do número de exemplos disponíveis por partição
de treino, já que dos 13.972 chamados cerca de 11.178 compõem cada
partição em cinco dobras. Esse cenário é consoante à hipótese de que
modelos lineares igualam ou superam redes neurais em corpora de porte
médio e ruidosos, quando não há *embeddings* pré-treinados disponíveis no
idioma (GALKE; SCHERP, 2022), e a curva de aprendizado da Subseção 4.8
mostra saturação precoce, e não instabilidade de treino.

**3.5 Desenho de avaliação**

A avaliação se dá por predições fora da amostra em protocolo
*out-of-fold* com `StratifiedGroupKFold`, cinco dobras e semente fixa,
estratificado pela referência humana e agrupado pelo hash do texto
normalizado. As partições são geradas uma única vez, versionadas e
reutilizadas por todos os modelos e pela camada de regras, o que reduz o
viés de comparação e legitima os testes pareados (SOKOLOVA; LAPALME,
2009). A validação cruzada foi preferida a um conjunto de teste fixo
porque produz estimativas de menor variância em bases desbalanceadas, ao
avaliar cada exemplo em alguma dobra em vez de descartar uma fração
constante do treino (KOHAVI, 1995), condição pertinente a um corpus em
que várias categorias apresentam suporte de dígito único.

São reportadas acurácia, *macro*-F1, *balanced accuracy* e intervalo de
confiança a 95% por *bootstrap*, reamostragem com reposição que estima a
distribuição de uma estatística sem pressupor sua forma paramétrica
(EFRON, 1979; EFRON; TIBSHIRANI, 1993; DICICCIO; EFRON, 1996). A
*macro*-F1 e a *balanced accuracy* respondem ao desbalanceamento entre
categorias, dado que a acurácia isolada superestima o desempenho nas
classes majoritárias e mascara falhas nas raras (SOKOLOVA; LAPALME,
2009). A correlação entre confiança e acerto é avaliada por Spearman
(SPEARMAN, 1904) e por correlação ponto-bisserial, apropriada quando uma
das variáveis é binária (TATE, 1954).

A inferência segue ordem declarada. Diferenças globais entre os sete
classificadores são apuradas por Cochran Q, teste não paramétrico para
proporções pareadas em três ou mais condições (COCHRAN, 1950), e somente
se o teste global rejeitar a igualdade procede-se às comparações pareadas
por McNemar (MCNEMAR, 1947), corrigidas pelo método sequencial de
Holm-Bonferroni, que controla a taxa de erro familiar sem o
conservadorismo da correção de Bonferroni simples (HOLM, 1979). O
protocolo de Demšar (2006) para comparação de classificadores recomenda o
*post-hoc* de Nemenyi sobre postos médios (NEMENYI, 1963), mas Benavoli,
Corani e Mangili (2016) demonstram que o teste de postos médios pode ser
inconsistente e recomendam testes pareados diretos, razão pela qual a
inferência principal repousa no McNemar. A estimação da incerteza por
*bootstrap* em métricas de modelos preditivos permanece em refinamento
(NOMA *et al.*, 2021), o que recomenda ler os intervalos ao lado dos
testes pareados, e não em substituição a eles.

A partição por linha, contudo, carrega uma limitação própria neste
corpus, e é ela que determina o protocolo adotado. Chamados de manutenção
repetem-se: 4.586 das 14.060 linhas, ou 32,62%, compartilham texto
normalizado com outra linha, e a base congelada resolve-se em 9.786
grupos textuais, dos quais 9.474 são unitários. Desses grupos, 9.735
sobrevivem ao recorte das 13.972 linhas avaliadas, e é essa a contagem
empregada como unidade de reamostragem na Subseção 4.9. Sob
particionamento por linha, o
mesmo texto pode cair em treino e em teste, o que superestima o
desempenho. Toda a avaliação principal usa, por isso, `StratifiedGroupKFold`
com cinco dobras e semente fixa, estratificado pela referência humana e
agrupado pelo hash do texto normalizado, de modo que nenhum grupo textual
atravessa a fronteira entre treino e teste. As partições são geradas uma
única vez, versionadas e reutilizadas por todos os modelos e pela camada
de regras, o que torna as comparações pareadas legítimas. A divisão
aleatória por linha permanece apenas como análise de sensibilidade, cujo
protocolo próprio e cujos resultados constam do material suplementar
(Subseção 4.8).

O agrupamento impõe um custo de cobertura que precisa ser declarado. Uma
categoria só entra na avaliação se dispuser de grupos textuais distintos
em número suficiente para figurar nas cinco dobras. Nove das 50
categorias não satisfazem essa condição, quatro por aritmética, tendo
menos grupos distintos que dobras, e cinco por ausência efetiva em alguma
dobra após a estratificação. Elas somam 88 linhas, e sua exclusão reduz o
denominador das métricas de 14.060 para 13.972 registros em 41
categorias. Excluir rótulos de baixa frequência é prática corrente na
classificação hierárquica de chamados (MARCUZZO *et al.*, 2022), ainda
que o limiar daqueles autores seja de cem ocorrências e o critério aqui
adotado seja o suporte por dobra. A Tabela A3 discrimina as categorias
excluídas, de modo que a diferença entre os dois denominadores permaneça
auditável.

O BERTimbau seria submetido ao mesmo protocolo, e a decisão de mantê-lo
fora da comparação principal apoia-se em medição de custo, não em
preferência editorial. O procedimento e o resultado dessa medição constam
da Subseção 4.3.

**3.6 Revisão humana e referência revisada**

A revisão humana é a etapa que diferencia este estudo de uma comparação
de classificadores contra histórico, e seu desenho delimita o que a
referência autoriza afirmar. Trata-se de auditoria administrativa de
rótulo, e não de anotação independente: a pergunta submetida ao
especialista é se a categoria já registrada é adequada ao chamado. Para
cada registro, o avaliador examinou o título e a descrição do chamado, o
título e a descrição da ordem de serviço, quando existentes, e a
categoria histórica; previsões e níveis de confiança dos modelos não
estavam visíveis. Confirmada a categoria, ela permanece como referência;
rejeitada, o avaliador registra outra categoria da mesma taxonomia. O
resultado é a categoria de referência revisada, usada no treinamento e na
avaliação dos modelos.

A revisão cobriu a totalidade do corpus: os 14.060 chamados receberam
decisão do especialista, sendo 13.462 de manutenção da categoria
histórica e 598 de substituição, o que corresponde a uma taxa de
alteração do rótulo histórico de 4,25%. Não restaram chamados sem
referência, o que elimina o viés de seleção de uma amostra parcialmente
conferida. Três desfechos não devem ser confundidos entre si: manter a
categoria é confirmação administrativa, isto é, o revisor não encontrou
motivo para alterar o registro; concordância entre avaliadores exigiria
segundo julgamento independente; e correção factual, no sentido de
comprovar qual intervenção foi executada, exigiria evidência externa ao
texto, como inspeção em campo, que este desenho não mobiliza.

A revisão foi conduzida por um único especialista. Não houve segunda
avaliação humana, independente ou cega, nem adjudicação de divergências,
pela razão elementar de que existe uma única decisão por registro.
Nenhuma medida de confiabilidade entre avaliadores é, portanto, reportada
neste artigo, e essa segunda avaliação fica registrada como validação
futura na Subseção 5.3. Pelo mesmo motivo não se reporta Kappa entre a
referência revisada e a categoria histórica, pois o pressuposto de
independência não se sustenta quando o revisor decide vendo o rótulo que
audita.

Ver a categoria histórica é constitutivo da auditoria, já que julgar um
rótulo inadequado pressupõe conhecê-lo, mas o efeito de ancoragem daí
decorrente precisa ser explicitado: a exposição prévia ao rótulo eleva a
probabilidade de mantê-lo, de modo que a taxa de confirmação de 95,75%
reflete, em proporção não separável neste desenho, tanto a estabilidade
do registro quanto o próprio procedimento. Dois elementos contextualizam
a leitura sem resolvê-la. A categoria histórica não é atribuição isolada
do demandante, pois resulta de registro seguido de verificação por equipe
técnica de triagem, e a auditoria de rótulo é o procedimento pertinente
ao uso pretendido, que é a governança de uma base administrativa
existente, não a construção de um corpus anotado do zero.

Uma medida da consistência interna da referência está disponível sem
segundo avaliador. Entre os grupos de texto idêntico, 17 receberam mais
de uma categoria de referência, afetando 85 linhas, ou 0,61% das linhas
avaliadas. A caracterização desses grupos desaconselha lê-los como taxa
de erro de anotação: em 14 deles, somando 74 linhas, as categorias em
disputa pertencem a tipos distintos de manutenção, e o par mais frequente
opõe Hidrossanitária > Hidráulica a Manutenção Preventiva > Reservatório,
com 11 grupos e 65 linhas. Chamados de texto idêntico podem, portanto,
corresponder a intervenções de naturezas diferentes, distinção ausente do
texto e irrecuperável por qualquer classificador textual. Separar as três
origens possíveis, a saber, contexto não textual, erro de registro e
inconsistência de anotação, exigiria reexame caso a caso, não realizado.
O valor delimita um teto de desempenho atribuível à ambiguidade
documentada, e não um piso de erro irredutível de anotação.

**3.7 Camada de entropia de Shannon e divergência de Jensen-Shannon**

Como dimensão complementar às métricas supervisionadas, o protocolo
incorporou uma camada de análise informacional baseada em entropia de
Shannon e divergência de Jensen-Shannon (SHANNON, 1948; LIN, 1991),
calculada exclusivamente sobre agregados sanitizados, sem identificador,
título ou texto livre do chamado. Ela responde a pergunta distinta da
acurácia, a saber, onde se concentra a incerteza estrutural, e o que
localiza não é erro de modelo, mas a região da taxonomia em que o próprio
sistema de registro perdeu capacidade de discriminar. A camada opera em
três níveis. No dos modelos, a entropia sobre a distribuição de
categorias previstas indica se um classificador dispersa ou concentra
suas predições, e a divergência de Jensen-Shannon mede a distância entre
essa distribuição e a histórica, funcionando como indicador de
deslocamento distributivo. No das categorias, evidencia classes cujas
predições se espalham entre múltiplas alternativas, candidatas
prioritárias a revisão taxonômica. No do chamado individual, a entropia
de votos entre modelos forma uma fila de auditoria orientada por
ambiguidade, e não por baixa confiança isolada de um único
classificador.

**3.8 Governança e disponibilidade dos dados**

Os chamados analisados têm origem no sistema institucional GLPI da UFSB e
constituem registros administrativos de manutenção predial, produzidos na
rotina de atendimento da instituição. A base de trabalho não é
publicamente disponível, por restrição de privacidade institucional, e os
campos textuais permanecem restritos ao ambiente do pesquisador. Os
artefatos publicados são sanitizados na origem: nenhum identificador
pessoal, identificador de chamado em texto claro, título ou descrição
livre é gravado nos agregados versionados, e os mapas por registro usam o
resumo criptográfico SHA-256 do identificador, o que preserva a junção
entre etapas sem expor o dado. A camada de entropia da Subseção 3.7 opera
exclusivamente sobre esses agregados. Essas medidas atendem ao princípio
da necessidade previsto na Lei Geral de Proteção de Dados Pessoais
(BRASIL, 2018), uma vez que a análise não requer dado pessoal e nenhum é
retido nos produtos públicos da pesquisa.

Cabe registrar, para transparência, que o repositório não guarda
documento de autorização institucional formal, de aprovação por comitê de
ética ou de dispensa de apreciação ética, de modo que nada é aqui
afirmado a esse respeito. O acesso à base decorre da atuação do primeiro
autor na gestão da manutenção predial da própria instituição, e a
formalização documental do consentimento institucional para uso
científico dos registros é providência recomendada antes da submissão.

As métricas derivadas e o código que produz cada figura, tabela e
estatística deste artigo são de acesso público no repositório
https://github.com/adinailson88/classificacao-chamados, que também
descreve a estrutura completa dos dados e o material suplementar citado
neste artigo. Os artefatos são gerados por processo automatizado e
reproduzível, reexecutado a cada atualização do experimento.

**4. RESULTADOS**

Esta seção apresenta dois conjuntos de resultados deliberadamente
segregados. O primeiro é a concordância dos sete modelos com a categoria
histórica (Subseção 4.1), em que o registro administrativo opera como
referência preliminar. O segundo é o desempenho desses mesmos modelos
contra a referência humana revisada (Subseção 4.2).

Dois denominadores convivem no texto e não devem ser confundidos. A base
congelada contém 14.060 chamados, todos com referência humana, e é o
número pertinente sempre que a frase trata do corpus ou da cobertura da
revisão. As métricas, contudo, são apuradas sobre 13.972 linhas em 41
categorias: nove categorias, somando 88 linhas, não sustentam suporte nas
cinco dobras e ficaram fora das partições, conforme o critério da
Subseção 3.5 e o detalhamento da Tabela A3.

Quatro achados resumem a seção: o LinearSVC lidera tanto a concordância
histórica quanto a acurácia contra a referência humana, e mantém vantagem
de custo; o ganho líquido de reclassificação é negativo em todos os
modelos, o que desautoriza a correção automática da base histórica em
massa; a camada explícita de regras de periodicidade é redundante diante
de um classificador competente; e a calibração viabiliza automação
seletiva de cerca de dois terços do volume com acurácia próxima de 0,95.

```{=latex}
\FloatBarrier
```

**4.1 Concordância com a categoria histórica**

A comparação contra a categoria histórica, sobre as predições
*out-of-fold* da rodada canônica (n = 13.972), mantém o LinearSVC na
liderança, com acordo bruto de 0,7961, seguido por Extra Trees (0,7844),
SGD (0,7781), Random Forest (0,7747), Regressão Logística (0,7738), LSTM
(0,7017) e Naive Bayes (0,6954). A comparação exclui o BERTimbau, que não
possui predições *out-of-fold* sobre as 13.972 linhas pelo motivo
computacional exposto na Subseção 4.3. O Kappa de Cohen (COHEN, 1960)
entre cada modelo e o histórico reproduz ordenação semelhante, variando
de 0,7807 (LinearSVC) a 0,6653 (Naive Bayes), faixa que Landis e Koch
(1977) classificam como concordância substancial. As duas medidas
divergem em uma única troca de posição, entre Random Forest e Regressão
Logística, decorrente da sensibilidade do coeficiente à prevalência das
categorias, o que recomenda lê-lo ao lado do acordo bruto (WONGPAKARAN
*et al.*, 2013).

O coeficiente é aplicável aqui porque modelo e categoria histórica
constituem fontes independentes de classificação, o que não vale entre a
referência revisada e o histórico, pelo motivo exposto na Subseção 3.6.

**Tabela 1** Concordância com a categoria histórica por modelo (n = 13.972).

| Modelo | Acordo bruto | Kappa de Cohen |
|---|---|---|
| LinearSVC | 0,7961 | 0,7807 |
| Extra Trees | 0,7844 | 0,7665 |
| SGD | 0,7781 | 0,7618 |
| Random Forest | 0,7747 | 0,7559 |
| Regressão Logística | 0,7738 | 0,7574 |
| LSTM | 0,7017 | 0,6809 |
| Naive Bayes | 0,6954 | 0,6653 |

O desempenho não é uniforme entre as 41 categorias avaliadas e
concentra-se nas classes de maior volume. As categorias de maior F1
pertencem todas à Manutenção Preventiva, com destaque para Ar
condicionado split (F1 = 0,9972; suporte = 1.987), Gerador (0,9954;
1.208) e Quadros Elétricos (0,9843; 578). No extremo oposto, Manutenção
Preventiva sem subcategoria hidráulica e Projeto não alcançam acerto
algum, e Limpeza de equipamentos, Telhados preventivos e Reforma ficam
abaixo de 0,25. Essa leitura pede cautela, pois essas categorias têm
suporte entre 13 e 65 registros, condição em que pequena variação
absoluta altera fortemente a métrica. O desempenho por categoria, com
suporte, tipo e classe de volume, consta da Tabela A2.

```{=latex}
\FloatBarrier
```

**4.2 Acerto contra a referência humana revisada**

A revisão humana estabeleceu categoria de referência para a totalidade
dos 14.060 chamados da base congelada, e a avaliação incide sobre os
13.972 que compõem as partições canônicas. O LinearSVC é o
melhor modelo em acurácia, com 0,8253 (IC95%: 0,8115--0,8378), seguido
por SGD (0,8093), Extra Trees (0,8073), Regressão Logística (0,8050),
Random Forest (0,7970), LSTM (0,7287) e Naive Bayes (0,7088). A vantagem
sobre o SGD, segundo colocado, é de 1,60 ponto percentual e permanece
significativa após correção de Holm, com 536 acertos exclusivos do
LinearSVC contra 312 do SGD.

A cobertura integral da revisão elimina o viés de seleção: não há chamado
sem categoria de referência, de modo que a acurácia relatada não
constitui limite superior de amostra conferida. As ressalvas
remanescentes são de outra natureza e estão declaradas na Subseção 5.3,
pois a referência é decisão de especialista único sobre uma taxonomia
que apresenta pares sobrepostos, discutidos na Subseção 4.6.

A leitura por acurácia deve ser acompanhada do F1 macro, que pondera
igualmente todas as categorias e revela comportamento distinto entre os
modelos. As três melhores marcas de F1 macro ficam a menos de três
milésimos umas das outras, com Regressão Logística em 0,6689, LinearSVC
em 0,6684 e SGD em 0,6669, e seus intervalos de confiança se sobrepõem
integralmente. Os três modelos não devem ser ordenados por essa métrica.
A leitura pertinente é outra: o LinearSVC lidera a acurácia sem pagar
por isso em desempenho na cauda, ao contrário dos *ensembles* de árvores,
que perdem cerca de três centésimos de F1 macro na mesma faixa de
acurácia.

**Tabela 2** Acurácia e F1 macro por modelo contra a referência humana
final (n = 13.972; 41 categorias). As duas métricas são a estimativa
observada na amostra inteira; os intervalos vêm de *bootstrap* de grupo
textual, com mil repetições sobre os 9.735 grupos congelados. A média das
reamostragens é grandeza distinta da estimativa observada e não ocupa
estas colunas: para o LinearSVC, por exemplo, a média do F1 macro é
0,6664, contra os 0,6684 observados. O F1 macro pondera igualmente todas
as categorias, independentemente do suporte.

| Modelo | Acurácia | IC95% | F1 macro | IC95% |
|---|---|---|---|---|
| LinearSVC | 0,8253 | 0,8115 -- 0,8378 | 0,6684 | 0,6526 -- 0,6804 |
| SGD | 0,8093 | 0,7950 -- 0,8227 | 0,6669 | 0,6510 -- 0,6788 |
| Extra Trees | 0,8073 | 0,7923 -- 0,8211 | 0,6362 | 0,6177 -- 0,6498 |
| Regressão Logística | 0,8050 | 0,7907 -- 0,8189 | 0,6689 | 0,6534 -- 0,6812 |
| Random Forest | 0,7970 | 0,7812 -- 0,8111 | 0,6152 | 0,5971 -- 0,6288 |
| LSTM | 0,7287 | 0,7080 -- 0,7480 | 0,5240 | 0,5107 -- 0,5343 |
| Naive Bayes | 0,7088 | 0,6860 -- 0,7311 | 0,2951 | 0,2887 -- 0,3099 |

**4.3 Viabilidade computacional do BERTimbau**

O BERTimbau não integra a comparação principal, e o motivo é
computacional. O ajuste fino foi cronometrado no mesmo ambiente dos
demais modelos, um executor de quatro processadores sem acelerador
gráfico, e custou 10,774 segundos por passo, com variação de 0,12
segundo entre o passo mais rápido e o mais lento. São 2.103 passos por
dobra, o que projeta 6,44 horas para uma única dobra e 32,2 horas para as
cinco. O teto de execução disponível é de seis horas, de modo que nem uma
dobra completa cabe na infraestrutura do estudo.

A limitação é de infraestrutura, não do modelo. O BERTimbau não foi
avaliado sob o protocolo agrupado desta rodada e, por conseguinte, nada
se afirma aqui sobre seu desempenho relativo; uma comparação integral
exigiria aceleração por unidade de processamento gráfico, indisponível no
ambiente do estudo, e permanece como trabalho futuro. Um experimento
exploratório avaliou o transformador em lote de mil chamados, dos quais
983 com referência humana, e seus valores constam do material suplementar
(Tabela S6). Eles não são comparáveis aos das Tabelas 1 e 2, pois o lote
corresponde aos primeiros registros elegíveis, não é probabilístico, não
cobre o corpus, e o ajuste empregou subamostragem estratificada com
parada antecipada.

```{=latex}
\FloatBarrier
```

**4.4 Calibração e automação seletiva por confiança**

A confiança bruta dos classificadores não é probabilidade e não pode
sustentar decisão operacional sem tratamento. O erro de calibração
esperado (ECE) do LinearSVC alcança 0,6925 sobre o escore bruto, porque a
transformação da margem por função *softmax* produz valores que não
correspondem a frequências de acerto. A calibração isotônica, ajustada em
dobra interna de calibração, reduz esse valor a 0,0178, e o escore de
Brier cai de 0,6052 para 0,1034. O SGD segue o mesmo padrão, de 0,3046
para 0,0109.

O procedimento reduz o ECE de cinco dos sete modelos. O Naive Bayes e o
LSTM constituem exceção e pioram levemente, de 0,0144 para 0,0206 e de
0,0158 para 0,0479, o que é consequência esperada de ajustar um
calibrador sobre amostra menor quando a confiança original já era
adequada. O melhor resultado calibrado pertence ao Extra Trees, com ECE
de 0,0108.

A calibração viabiliza a automação seletiva, em que o classificador
decide sozinho acima de um limiar de confiança e encaminha o restante à
revisão humana. Ao alvo de 0,95 de acurácia, o Extra Trees automatiza
67,32% dos chamados com acurácia seletiva de 0,9502 e encaminha 32,68% ao
revisor; o LinearSVC automatiza 68,90% com 0,9464. Elevar o alvo a 0,99
reduz a cobertura à faixa de 31,94% a 47,04%, e o Naive Bayes só alcança
o limiar em duas das cinco dobras, o que o desqualifica para esse regime.

Parte das acurácias seletivas fica pouco abaixo do alvo, como os 0,9464
do LinearSVC contra a meta de 0,95, e a cobertura é média entre as cinco
dobras. Ambos são consequência esperada de escolher o limiar em dobra
interna: um procedimento que atingisse o alvo exatamente em todas as
dobras indicaria que o limiar teve acesso ao conjunto de teste.

**Tabela 3** Calibração e automação seletiva por modelo (n = 13.972). O
ECE e o Brier referem-se ao escore antes e depois da calibração
isotônica; a cobertura e a acurácia seletiva correspondem ao alvo de 0,95.

| Modelo | ECE bruto | ECE calibrado | Brier calibrado | Cobertura | Acurácia seletiva |
|---|---|---|---|---|---|
| Extra Trees | 0,0859 | 0,0108 | 0,1057 | 0,6732 | 0,9502 |
| SGD | 0,3046 | 0,0109 | 0,1124 | 0,6162 | 0,9531 |
| Random Forest | 0,0913 | 0,0145 | 0,1082 | 0,6580 | 0,9495 |
| LinearSVC | 0,6925 | 0,0178 | 0,1034 | 0,6890 | 0,9464 |
| Regressão Logística | 0,2351 | 0,0189 | 0,1173 | 0,6237 | 0,9415 |
| Naive Bayes | 0,0144 | 0,0206 | 0,1280 | 0,5518 | 0,9306 |
| LSTM | 0,0158 | 0,0479 | 0,1221 | 0,6545 | 0,9210 |

A Figura 2 apresenta a curva de confiabilidade do Extra Trees calibrado,
tornando visível a aderência entre confiança declarada e acerto observado
ao longo das dez faixas.

![Curva de confiabilidade do Extra Trees após calibração isotônica, com confiança média e acurácia observada por faixa.](04_artigo/figuras/fig_confianca_desfecho.pdf){width=95%}

```{=latex}
\FloatBarrier
```

**4.5 Reclassificação e ganho líquido**

A hipótese operacional que motiva esta subseção é a de que um
classificador competente possa corrigir a base histórica em massa. A
medição a refuta. O ganho líquido de reclassificação é negativo em todos
os sete modelos, variando de −1.846 no LinearSVC a −3.474 no Naive Bayes
(Tabela 4). O procedimento é direto: conta-se apenas onde a predição
diverge da categoria histórica, e a referência revisada arbitra cada
divergência, de modo que corrigido é o caso em que o modelo coincide com
a referência e o histórico dela se afasta, e prejudicado o caso inverso.
O melhor modelo produz 2.849 divergências, das quais apenas 475
representam correção contra 2.321 que degradariam o registro, razão que
piora monotonicamente à medida que cai o desempenho do modelo, até o
Naive Bayes, que diverge 4.256 vezes para acertar 309.

A explicação não está em falha de cálculo, e sim na estabilidade da
referência. O especialista manteve a categoria histórica em 13.462 dos
14.060 chamados, ou 95,75% do corpus, e a substituiu em 598 registros. Um
histórico que a revisão preserva em mais de nove décimos dos casos
oferece pouca margem de correção e muita margem de dano: divergir do
histórico significa, na maior parte das vezes, divergir também da
referência. O teto de correção mensurável neste desenho corresponde aos
4,25% de registros cuja categoria foi alterada, e nenhum modelo se
aproxima dele sem produzir um volume de alterações indevidas várias vezes
maior.

A reclassificação automática em massa não é, portanto, desaconselhada por
cautela metodológica, mas por evidência de que degradaria a base em que
fosse aplicada. O ganho líquido, e não a acurácia agregada, é o critério
adequado para essa decisão, e deve ser recalculado a cada atualização da
base. A consequência operacional é discutida na Subseção 5.2.

**Tabela 4** Ganho líquido de reclassificação por modelo, contado apenas
onde a predição diverge da categoria histórica e arbitrado pela
referência humana revisada (n = 13.972).

| Modelo | Divergências | Corrigidos | Prejudicados | Neutros | Ganho líquido |
|---|---|---|---|---|---|
| LinearSVC | 2.849 | 475 | 2.321 | 53 | −1.846 |
| SGD | 3.100 | 489 | 2.559 | 52 | −2.070 |
| Extra Trees | 3.012 | 422 | 2.519 | 71 | −2.097 |
| Regressão Logística | 3.161 | 492 | 2.621 | 48 | −2.129 |
| Random Forest | 3.148 | 416 | 2.658 | 74 | −2.242 |
| LSTM | 4.168 | 426 | 3.621 | 121 | −3.195 |
| Naive Bayes | 4.256 | 309 | 3.783 | 164 | −3.474 |

**4.6 Diagnóstico de taxonomia e ambiguidade estrutural
(Shannon/Jensen-Shannon)**

O diagnóstico de Shannon abrange os sete modelos com predições
*out-of-fold* sobre a totalidade das linhas avaliadas. O BERTimbau fica
de fora pelo motivo exposto na Subseção 4.3. Duas leituras distintas
emergem da dispersão das predições. O LSTM apresenta a maior diversidade
previstas, com entropia normalizada de 0,8362, ao passo que o LinearSVC
exibe a menor divergência de Jensen-Shannon frente à distribuição
histórica (0,0055). Dispersão de predições e aderência distributiva ao
histórico, portanto, não caminham juntas, e o modelo de melhor acurácia é
justamente o de distribuição mais próxima da base.

No nível de chamado individual, os sete modelos são unânimes em 8.444 dos
13.972 registros, ou 60,44%. No extremo oposto, 2.285 registros, ou
16,35%, distribuem os votos por três ou mais categorias distintas, o que
caracteriza desacordo estrutural entre arquiteturas: a divergência deixa
de ser a escolha entre duas alternativas e passa a indicar ausência de
sinal textual suficiente para delimitar a categoria. Esse subconjunto
constitui critério de priorização de auditoria distinto e complementar à
baixa confiança de um único modelo, já que decorre de discordância entre
indutores e não da incerteza declarada por um deles.

No nível de categoria, o contraste é acentuado entre as 33 categorias com
suporte mínimo de trinta registros. A Figura 3 contrasta as dez de maior
e as dez de menor F1 do LinearSVC. Nas dez melhores, o F1 varia de 0,9139
a 0,9972 e o conjunto reúne 6.271 chamados; nas dez piores, cai para a
faixa de 0,2162 a 0,6288 sobre 2.403 chamados. Os dois grupos têm porte
comparável em ordem de grandeza, de modo que a diferença não decorre de
escassez de exemplos.

![F1 do LinearSVC e suporte, para as dez categorias de maior e de menor desempenho entre as 33 com suporte mínimo de 30 chamados.](04_artigo/figuras/fig_calor_categorias.pdf){width=91%}

O padrão que emerge é sistemático, não aleatório. Oito das dez categorias
de maior desempenho pertencem a Manutenção Preventiva, cujos chamados
nascem de rotina programada e recebem descrição padronizada. As de menor
desempenho concentram rótulos de fronteira aberta, como Telhados
preventivos (0,2162), Reforma (0,2407), Erro de chamado (0,3978) e
Alvenaria, Pisos e Estrutura (0,4610), que competem por vocabulário com
categorias vizinhas. Trata-se, portanto, de ambiguidade estrutural da
taxonomia, não apenas de erro do modelo, na linha do que Zhang *et al.*
(2025) descrevem para rótulos ruidosos em processamento de linguagem
natural.

A Figura 4 recorta a matriz de confusão sobre as oito categorias mais
envolvidas em troca recíproca e mostra que os erros não se espalham pela
taxonomia. A célula dominante registra 1.066 chamados de Instalação e
reparo de equipamentos preditos como Alvenaria, Pisos e Estrutura, com
937 no sentido inverso, o que faz desse par a maior fronteira do corpus,
com 2.003 trocas somadas. Seguem-se Alvenaria contra Esquadrias, com
1.097 trocas, e Alvenaria contra Hidráulica, com 940. Alvenaria, Pisos e
Estrutura comparece nos cinco maiores pares e se comporta como categoria
absorvente, para a qual convergem chamados cuja descrição não delimita o
sistema predial afetado. A leitura da matriz é assimétrica em vários
pares, o que sugere absorção de uma categoria por outra, e não simples
permuta.

Convém registrar que a fronteira entre climatização corretiva e
preventiva, dominante sob o protocolo anterior, deixa de figurar entre as
maiores confusões. Os dois rótulos descrevem o mesmo equipamento e se
distinguem pela natureza da intervenção; treinados contra a referência
humana revisada, os modelos passam a separá-los de modo consistente. A
ambiguidade que resta é a de escopo entre sistemas prediais, não a de
natureza do serviço, resultado coerente com a facilidade da tarefa de
tipo reportada na Subseção 4.11.

![Recorte da matriz de confusão sobre as oito categorias mais envolvidas em troca recíproca, com contagens agregadas entre modelos.](04_artigo/figuras/fig_matriz_confusao.pdf)

Esses recortes sustentam a mesma conclusão operacional. O desempenho
agregado das Tabelas 1 e 2 esconde heterogeneidade relevante entre
categorias, fenômeno que a *macro*-F1 e a *balanced accuracy* foram
adotadas para capturar (SOKOLOVA; LAPALME, 2009). Quando a queda de
desempenho se concentra em fronteiras taxonômicas específicas, e não de
modo difuso, a resposta adequada não é substituir o classificador, mas
revisar a taxonomia, decisão que permanece humana e para a qual a camada
de Shannon oferece apenas a priorização estatística. O Naive Bayes
sintetiza o diagnóstico ao combinar a menor cobertura de categorias,
apenas 22 contra 39 a 41 dos demais modelos, com a menor entropia
normalizada e a maior divergência frente ao histórico: concentra o corpus
em pouco mais de metade da taxonomia e reproduz mal a distribuição real,
o que explica seu F1 macro de 0,2951 apesar de acurácia próxima de 0,71.
A Figura 5 mostra os quinze pares de maior confusão recíproca, dominados
pelas fronteiras internas de estrutura predial.

![Quinze pares de categorias com maior confusão recíproca, agregados entre modelos. Os códigos do eixo vertical estão descritos no material suplementar.](04_artigo/figuras/fig_top_confusoes.pdf){width=95%}

```{=latex}
\FloatBarrier
```

**4.7 Custo computacional**

O custo de treino e de inferência foi medido para os sete modelos sobre a
base completa, no mesmo ambiente computacional (processador de quatro
núcleos, sem acelerador gráfico), com mediana de três execuções por
modelo. O desenho é o de treino único sobre a base inteira, e não a soma
das cinco dobras da validação cruzada, de modo que os valores medem o
custo de colocar cada modelo em operação. Os tempos absolutos variam
conforme a máquina, mas as razões entre modelos permanecem estáveis e
constituem o dado relevante para a decisão de adoção.

Os modelos lineares treinam em poucos segundos, de 1,12 s no Naive Bayes
a 8,43 s na Regressão Logística. Os *ensembles* de árvores exigem entre
vinte e trinta segundos, e a rede neural LSTM consome 83,44 s, cerca de
34 vezes o tempo do LinearSVC e 74,6 vezes o do Naive Bayes, que é o
extremo mais rápido. A faixa entre a execução mais rápida e a mais lenta
é estreita em todos os modelos, com exceção do LSTM, o que permite
distinguir diferença real de ruído do executor.

O BERTimbau não figura na tabela por estar em outra ordem de grandeza,
com 6,44 horas por dobra (Subseção 4.3), e porque os tempos aqui
reportados referem-se a treino único sobre a base inteira, e não a uma
dobra da validação cruzada.

**Tabela 5** Custo computacional por modelo sobre a base completa
(n = 13.972), mediana de três execuções em processador de quatro núcleos.

| Modelo | Tempo de treino (s) | Faixa | Tempo de inferência (s) |
|---|---|---|---|
| Naive Bayes | 1,12 | 1,12 -- 1,12 | 0,89 |
| SGD | 2,28 | 2,27 -- 2,28 | 0,93 |
| LinearSVC | 2,44 | 2,41 -- 2,46 | 0,89 |
| Regressão Logística | 8,43 | 8,43 -- 8,46 | 0,92 |
| Random Forest | 22,62 | 22,62 -- 22,66 | 1,34 |
| Extra Trees | 26,69 | 26,63 -- 26,72 | 1,46 |
| LSTM | 83,44 | 70,38 -- 83,63 | 4,89 |

A Figura 6 cruza essas medições de custo com a acurácia da Tabela 2 e
mostra que o LinearSVC ocupa a posição mais favorável, com a maior
acurácia a um custo de treino próximo do menor observado. O argumento de
eficiência da Subseção 2.4 se sustenta em duas frentes. Contra o LSTM, a
comparação é direta e desfavorável ao modelo neural, que custa 34 vezes
mais para perder 9,7 pontos percentuais de acurácia. Contra o BERTimbau,
o que se afirma é mais restrito: o custo medido inviabiliza a validação
cruzada agrupada no ambiente do estudo, sem que disso decorra juízo sobre
seu desempenho.

![Trade-off entre acurácia e tempo de treino, modelos clássicos.](04_artigo/figuras/fig_tradeoff_custo.pdf){width=95%}

**4.8 Comportamento do LSTM e justificativa do protocolo agrupado**

A Figura 7 mostra a curva de aprendizado do LSTM. O treino parou por
interrupção antecipada após 11 épocas, com menor perda de validação na
época 8 e maior acurácia de validação na época 10 (0,6722). O padrão
indica saturação precoce, consistente com a hipótese de que *embeddings*
treinados do zero são insuficientes para um corpus deste porte (Subseção
3.4.1). A curva provém de um treino único sobre a base inteira, com
validação interna de 10%, e descreve a dinâmica de convergência da
arquitetura, não o desempenho reportado na Tabela 2, que é a união das
predições *out-of-fold* das cinco dobras.

![Curva de aprendizado do LSTM por época, perda e acurácia em treino e validação.](04_artigo/figuras/fig_curva_aprendizado_lstm.pdf){width=95%}

A justificativa do particionamento agrupado é anterior a qualquer
medição de desempenho e repousa na estrutura do corpus: 32,62% das linhas
compartilham texto normalizado com outra linha (Subseção 3.5), de modo
que a partição por linha permitiria ao mesmo texto ocupar treino e teste.
Duas estimativas da magnitude do efeito indicam ganho espúrio entre 0,89
e 1,84 ponto percentual de acurácia; elas constam do material suplementar
com o protocolo declarado e não são comparáveis às Tabelas 1 e 2, por
terem outra base, outro denominador e outro rótulo de treino. O estudo de
sensibilidade a unidades recorrentes e *dropout* também consta do
suplemento e separa as quatro variantes por menos de quatro pontos
percentuais, o que indica baixa sensibilidade do LSTM a esses
hiperparâmetros nesta base.

**4.9 Robustez estatística: pressupostos e testes de sensibilidade**

Antes de qualquer teste inferencial, foram verificados os pressupostos de
robustez estatística usuais, a saber, outliers (TUKEY, 1977; HODGE;
AUSTIN, 2004), homogeneidade de variância, normalidade, desbalanceamento
entre categorias, colinearidade entre modelos, relação entre confiança e
acerto e independência das observações, adaptando o protocolo de
exploração de dados de Zuur, Ieno e Elphick (2010) da resposta contínua da ecologia para a resposta
categórica de classificação de chamados (n = 13.972). O teste de
Shapiro-Wilk (SHAPIRO; WILK, 1965), escolhido por reunir o maior poder
entre os testes de normalidade usuais (RAZALI; WAH, 2011; OGUNLEYE;
OYEJOLA; OBISESAN, 2018), rejeita a normalidade a 5% para os sete modelos
quando aplicado à distribuição de confiança de cada um, sobre subamostra
de cinco mil observações com semente fixa. A variância de confiança entre
modelos é fortemente heterogênea, com Levene de 4.216,75 e *p*
praticamente nulo. Ambos confirmam com números a justificativa não
paramétrica adotada na Subseção 3.5.

A independência das observações merece tratamento próprio, porque é o
pressuposto que este corpus viola de modo mais evidente. Registros que
compartilham texto idêntico não são independentes, e tratá-los como tal
estreitaria artificialmente qualquer intervalo. Os intervalos da Tabela 2
vêm, por isso, de *bootstrap* de conglomerados, com mil reamostragens dos
9.735 grupos textuais congelados que compõem as 13.972 linhas avaliadas,
com semente fixa, e não de reamostragem por linha.

O texto reporta duas contagens de grupos, 9.786 na base congelada de
14.060 chamados e 9.735 no recorte de 13.972 linhas, que são a mesma
partição textual sob denominadores distintos: a diferença de 51
corresponde aos grupos que saem junto com as 88 linhas fora das
partições. A unidade reprodutível é a congelada, e é ela que sustenta os
intervalos aqui reportados.

A ordem dos testes é declarada porque importa. O Cochran Q (COCHRAN,
1950) foi aplicado primeiro à hipótese global de que os sete modelos têm
a mesma taxa de acerto, e a rejeita com Q = 2661,04 sobre seis graus de
liberdade e *p* praticamente nulo. Só então as comparações pareadas foram
conduzidas por McNemar (MCNEMAR, 1947) sobre os 21 pares, com correção de
Holm-Bonferroni (HOLM, 1979) aplicada a essa família. Sem o teste global,
21 comparações constituiriam pesca de significância.

Dos 21 pares, 19 são significativos após a correção e 2 não são: Extra
Trees contra Regressão Logística e Extra Trees contra SGD, ambos com *p*
ajustado de 0,819. Esses dois pares devem ser lidos como empate dentro do
poder do teste, e não como ordenação, o que é coerente com a sobreposição
dos intervalos de F1 macro apontada na Subseção 4.2. O LinearSVC supera
todos os demais com significância.

A verificação de colinearidade revela um efeito colateral pertinente à
decisão de arquitetura. Quatro dos sete modelos apresentam confiança
altamente correlacionada entre si, com Fator de Inflação de Variância
entre 20,78 e 29,98 (MARQUARDT, 1970), muito acima do limiar convencional
de dez, que deve ainda assim ser lido com a cautela recomendada por
O'Brien (2007). São o Extra Trees, o Random Forest, a Regressão Logística
e o SGD; os três restantes ficam abaixo de 4,3. Modelos redundantes pouco
acrescentam em informação independente a um comitê (DIETTERICH, 2000), o
que desaconselha combiná-los em *ensemble*. A correlação entre confiança
bruta e acerto, por sua vez, é positiva e significativa nos sete modelos,
com Spearman entre 0,4809 e 0,6160 e ponto-bisserial entre 0,4500 e
0,6560 (*p* < 0,001 em ambos; KORNBROT, 2014), pré-requisito para a calibração
discutida na Subseção 4.4 (GUO *et al.*, 2017; MINDERER *et al.*, 2021).
A verificação completa dos pressupostos, item a item, com as estatísticas
de normalidade, variância, colinearidade e correlação por modelo, consta
do material suplementar e é apurada sobre as mesmas predições que
sustentam as Tabelas 1 a 5.

**4.10 Análise de erro por categoria e matriz de confusão**

A avaliação por acurácia global descreve o desempenho médio, mas oculta a
distribuição do acerto entre categorias. Esta subseção examina a matriz de
confusão de cada modelo contra a categoria de referência revisada,
apurada sobre os 13.972 chamados avaliados. As predições não extrapolam a
taxonomia de treino, de modo que referência e predições percorrem o mesmo
conjunto de 41 categorias.

O contraste entre acurácia e F1 macro é o primeiro achado. A acurácia dos
sete modelos varia entre 0,7088 e 0,8253, faixa de 12 pontos percentuais,
ao passo que o F1 macro varia de 0,2951 a 0,6689, faixa de 37 pontos, o
que indica que os modelos se diferenciam sobretudo no tratamento das
categorias de baixa frequência. O SGD e a Regressão Logística, embora
percam em acurácia para o LinearSVC, alcançam F1 macro equivalente, o que
sugere fronteira de decisão mais distribuída entre classes.

O mesmo padrão de fronteira descrito na Subseção 4.6 para o conjunto dos
modelos reaparece no LinearSVC isoladamente, com 174 casos de `Alvenaria
/ Pisos / Estrutura` recebidos de `Instalação/reparo de equipamentos` e
107 no sentido inverso, seguidos de `Esquadrias` (106 e 31) e
`Hidráulica` (68 e 34), o que confirma o desequilíbrio como propriedade
da taxonomia e não de um indutor particular.

Observa-se ainda a categoria `Outros > Erro de chamado` entre os pares de
maior volume, com 56 casos recebidos de `TI / Dados / Rede > Ponto de
rede / fibra ótica / Wi-fi` e 45 no sentido inverso. Trata-se de
categoria residual, cuja atribuição depende de juízo sobre a pertinência
do próprio chamado, e não de sua natureza técnica, o que a torna
estruturalmente difícil para qualquer modelo baseado em texto.

Soma-se a esse quadro a duplicação taxonômica. A categoria `Ar
condicionado split` existe simultaneamente sob `Manutenção Preventiva`,
com 1.798 chamados, e sob `Climatização`, com 1.640, e o mesmo
desdobramento ocorre com `Ar condicionado central`, `Gerador`, `Nobreak`,
`Elevador`, `Telhados, calhas, rufos` e `Sistemas de combate a incêndio`.
O critério que separa esses pares é a natureza preventiva ou corretiva da
intervenção, informação que o texto do chamado frequentemente não
explicita, de modo que uma fração do erro medido não decorre de limitação
do classificador, mas da exigência de inferir do texto uma distinção que
nele não está registrada. A cauda de categorias raras impõe restrição
análoga: das 50 categorias históricas, 14 reúnem menos de trinta chamados
e 6 reúnem menos de dez, suporte em que um único acerto desloca o F1 em
dezenas de pontos percentuais.

Depreende-se do conjunto dessas observações uma recomendação de
governança anterior à escolha do modelo. Antes de perseguir ganho de
acurácia por meio de arquiteturas mais custosas, convém revisar a
taxonomia institucional, unificando os pares que nomeiam o mesmo objeto e
explicitando o critério de natureza da manutenção no formulário de
abertura do chamado. Essa intervenção atua sobre a origem do erro,
enquanto a substituição do classificador atua apenas sobre seu efeito.

**4.11 Desempenho por volume de categoria e por natureza da manutenção**

O F1 macro atribui o mesmo peso a uma categoria de dois chamados e a
outra de dois mil, o que torna a métrica agregada pouco informativa
quando a distribuição de volume é acentuadamente desigual. Aplicou-se,
por conseguinte, uma curva ABC sobre o suporte das 41 categorias
avaliadas. A classe A reúne o menor conjunto de categorias que acumula ao
menos 80% do volume, a classe B corresponde ao intervalo entre 80% e 95%,
e a classe C abrange o restante. A partição resultante concentra 11.433
chamados, equivalentes a 81,83% do total, em apenas 12 categorias; a
classe B reúne outras 12 categorias e 1.912 chamados; a classe C reúne 17
categorias e 627 chamados, ou 4,49% do total.

O F1 macro recalculado dentro de cada classe demonstra que a distância
entre acurácia e F1 macro decorre da composição da métrica, e não de
falha generalizada do classificador. O LinearSVC alcança 0,8207 na classe
A e 0,5018 na classe C, de modo que o valor agregado de 0,6684 constitui
média entre dois regimes distintos de desempenho. A ordenação dos modelos
permanece estável nas três classes, o que indica que o recorte não altera
a comparação entre arquiteturas, apenas a interpretação de sua magnitude.
Constata-se ainda que o Naive Bayes é o único modelo cujo colapso alcança
a classe B, com 0,2527, ao passo que os demais preservam desempenho
superior a 0,63 nas duas primeiras classes. Os valores por modelo e
classe constam do material suplementar.

O segundo recorte separa os chamados pela natureza da intervenção.
Adotou-se classificação em três tipos, e não a dicotomia usual entre
preventivo e corretivo, porque a taxonomia institucional abriga
famílias que não descrevem serviço de manutenção. Encontram-se nessa
condição o registro indevido de chamado, a contratação de posto de
trabalho, o fornecimento de materiais e a execução de reformas. Essas
famílias somam 585 chamados, correspondentes a 4,19% das linhas
avaliadas, e sua atribuição indiscriminada à manutenção corretiva
elevaria o denominador desta em cerca de 7% relativos, com efeito direto
sobre qualquer razão calculada entre as duas naturezas. Sob o critério
adotado, a manutenção preventiva responde por 4.902 chamados (35,09%) e a
corretiva por 8.485 (60,73%).

A projeção da referência revisada e das predições para o nível de tipo
eleva o desempenho a outro patamar. O LinearSVC alcança 0,9443 de
acurácia nessa granularidade, contra 0,8253 na tarefa de 41 categorias,
com F1 de 0,9742 na manutenção preventiva e de 0,9547 na corretiva. A
distinção entre preventivo e corretivo, apontada na Subseção 4.10 como
origem taxonômica de parte do erro por categoria, resolve-se com folga
quando lida no nível em que a decisão de gestão efetivamente ocorre.

Toda a perda de desempenho observada nessa projeção concentra-se no
terceiro tipo, cujo F1 não ultrapassa 0,5330 em nenhum dos sete modelos e
recua a 0,2684 no Naive Bayes, resultado coerente com a natureza dessas
categorias, cuja atribuição depende de juízo administrativo sobre a
pertinência do próprio chamado e não de sua descrição técnica. Cabe
registrar a inversão de ordenação entre as duas métricas nessa
granularidade: o Extra Trees lidera a acurácia, com 0,9497, ao passo que
o LinearSVC lidera o F1 macro, com 0,8180, precisamente por ir melhor na
classe difícil. Reportar apenas a acurácia ocultaria a diferença, e
depreende-se que a escolha do classificador depende tanto do nível de
agregação em que a decisão será tomada quanto da métrica que ela
privilegia.

A curva ABC recalculada dentro de cada tipo delimita o conjunto mínimo de
categorias que sustenta cada leitura. Na manutenção preventiva, quatro
categorias concentram 83,46% do volume do tipo, e nelas o LinearSVC
alcança F1 macro de 0,9727. Na corretiva são necessárias sete categorias
para cobrir 81,76% do tipo, com 0,7835, valor sensivelmente inferior e
compatível com a ambiguidade de fronteira descrita na subseção anterior.
No conjunto de não manutenção, as quatro categorias que cobrem 89,06% do
tipo alcançam apenas 0,5184, o que confirma a dificuldade como
propriedade do tipo, e não da cauda de baixa frequência. O detalhamento
por classe e por tipo consta do material suplementar.

Depreende-se do conjunto dessas medições uma hierarquia de
confiabilidade: a contagem por tipo de manutenção é a leitura mais
segura, com erro agregado inferior a 2% na classe preventiva; a leitura
por categoria só se sustenta nas categorias de classe A do respectivo
tipo, condição satisfeita por quatro categorias preventivas e sete
corretivas, que reúnem 11.028 chamados e estão discriminadas na Tabela
A2. Nas classes B e C, e em toda a família de não manutenção, o
desempenho medido não autoriza uso automático. A consequência para
indicadores institucionais é tratada na Subseção 5.4.

**4.12 Camada explícita de regras de periodicidade**

O desenho do estudo previa medir, e não presumir, o valor de uma camada
de regras de domínio sobre a predição estatística. A regra implementada
atribui categoria preventiva quando o chamado reúne, no mesmo texto, um
termo de periodicidade e um termo de equipamento, e abstém-se nos demais
casos. São 19 termos de periodicidade e 31 de equipamento. A avaliação
usa as mesmas partições e os mesmos registros da comparação principal, e
em nenhuma configuração a referência humana é alterada.

A regra dispara em 4.487 dos 13.972 registros, quase um terço do corpus,
e ainda assim melhora o F1 macro de apenas três dos sete modelos. O ganho
concentra-se onde o classificador é fraco: o Naive Bayes sobe 0,0586 no
F1 macro, ao passo que Extra Trees e Random Forest perdem 0,0038 cada, e
o LinearSVC perde 0,0017. Nos chamados de referência preventiva a
acurácia sobe em todos os modelos, mas o efeito é de segunda ordem fora
do Naive Bayes, entre 0,0020 e 0,0060.

O número que explica o padrão é o de conflitos. Como a regra depende
apenas do texto, ela dispara no mesmo conjunto de registros para os sete
modelos; o que varia é a predição que ela substitui. No LinearSVC, os
4.487 disparos produzem apenas 31 divergências, nas quais a regra acerta
11 vezes e o modelo, 13. No Naive Bayes, os mesmos disparos produzem 219
divergências, com a regra acertando 201 contra 9 do modelo.

A leitura correta, portanto, não é que regras de domínio funcionam, e sim
que elas são redundantes diante de um classificador estatístico
competente. Os modelos já capturam implicitamente os sinais de
periodicidade presentes no texto, e a camada explícita apenas repete o
que eles fazem, com o custo adicional de manter uma tabela de termos.
Trata-se de resultado negativo, contrário à expectativa que motivou o
teste, e com implicação de desenho: o ganho do fluxo híbrido está no eixo
humano–IA, tratado na Subseção 4.4, e não no eixo regra–modelo.

**5. DISCUSSÃO**

**5.1 Concordância histórica, acerto contra a referência e custo do
BERTimbau**

A comparação entre concordância histórica (Subseção 4.1) e desempenho
contra a referência humana (Subseção 4.2) revela que as duas grandezas
não são intercambiáveis. A acurácia do LinearSVC (82,53%) supera sua
concordância com o histórico (79,61%) em 2,92 pontos percentuais. A
diferença mede o efeito das 598 correções sobre a avaliação: ao
substituir a categoria histórica pela categoria revisada, parte das
divergências que seriam contabilizadas como erro do modelo passa a ser
reconhecida como erro do registro administrativo.

Com a revisão estendida ao corpus integral, a diferença deixa de depender
de qualquer recorte amostral e passa a ser propriedade medida da base. Em
598 dos 14.060 chamados, ou 4,25%, o avaliador rejeitou a categoria
registrada e definiu outra. A grandeza é uma taxa de alteração do rótulo
histórico sob auditoria administrativa, e não uma estimativa da
prevalência de erro do registro: ela mede quantas categorias um
especialista único decidiu trocar tendo o rótulo à vista, o que é
compatível com a hipótese de rótulos ruidosos da literatura (KEJRIWAL *et
al.*, 2024; ZHANG *et al.*, 2025) sem quantificá-la. O valor é específico
deste corpus e desta taxonomia, e sua transposição a outras instituições
exige nova revisão.

Convém observar que 4,25% é uma taxa de alteração baixa, e duas causas
concorrem para isso sem que o desenho permita separá-las. A primeira é o
modo de produção do rótulo, que não é atribuição isolada do demandante,
mas registro seguido de verificação por equipe técnica de triagem. A
segunda é o próprio procedimento de auditoria, no qual o revisor decide
vendo a categoria registrada, condição que favorece a manutenção do
rótulo. Seja qual for a proporção entre as duas, o que os modelos
acompanham não é um rótulo ingênuo, e é essa estabilidade da linha de
base que torna negativo o ganho de reclassificação discutido na Subseção
5.2.

O BERTimbau não integra essa comparação por motivo computacional medido
(Subseção 4.3), e nada se afirma aqui sobre sua qualidade relativa, pois
rankings produzidos sob protocolos distintos não sustentam comparação
direta.

**5.2 Reclassificação, ambiguidade taxonômica e calibração**

O resultado da reclassificação (Subseção 4.5) contraria a expectativa que
motivou o estudo e tem consequência operacional direta. O ganho líquido
de corrigir chamados já classificados é negativo em todos os sete
modelos, e a magnitude do prejuízo acompanha, na ordem inversa, o
desempenho de cada um. Não se trata de nuance entre modelos, e sim de
veredito sobre a tarefa: nenhum classificador aqui avaliado é candidato a
reclassificar a base histórica em massa.

A explicação é aritmética antes de ser metodológica. Estreito o espaço de
alteração da referência (Subseção 5.1), qualquer divergência sistemática
entre modelo e histórico tende a cair fora dele, e o melhor modelo
diverge 2.849 vezes para acertar 475, cerca de um acerto para cada cinco
prejuízos. O resultado depende de a referência cobrir todo o corpus, pois
arbitrar parte das divergências pela decisão revisada e parte pelo
próprio histórico misturaria referências de naturezas distintas e
premiaria o modelo por concordar com o rótulo que se pretendia auditar.

Disso não decorre que a classificação automática seja inútil neste
domínio, e sim que seu uso defensável é prospectivo e seletivo. Sobre
chamados novos, não há rótulo prévio correto a ser degradado. Sobre a
base histórica, o encaminhamento adequado é a automação condicionada à
confiança da Subseção 4.4, que preserva o registro nas faixas em que o
modelo não tem vantagem demonstrável sobre ele.

A camada de entropia de Shannon e divergência de Jensen-Shannon (Subseção
4.6) não substitui as métricas supervisionadas ou a revisão humana, mas
amplia o repertório de governança ao separar três fenômenos que a
acurácia isolada tende a confundir: o erro de modelo, a ambiguidade
genuína da taxonomia institucional e a heterogeneidade natural da
distribuição de chamados. Os sete modelos são unânimes em 60,44% dos
registros, e os 2.285 chamados em que os votos se espalham por três ou
mais categorias, ou 16,35%, oferecem critério de priorização de auditoria
distinto do simples corte
por baixa confiança de um único classificador. A dispersão das predições
e a aderência à distribuição histórica separam-se neste corpus, pois o
LSTM lidera a diversidade de categorias previstas e o LinearSVC apresenta
a menor divergência frente ao histórico.

A calibração transforma essa leitura em procedimento operável (Subseção
4.4). A confiança bruta não é probabilidade, e o caso do LinearSVC é
extremo: seu erro de calibração esperado de 0,6925 cai a 0,0178 após
ajuste isotônico em dobra interna (PLATT, 1999; GUO *et al.*, 2017). Com
escores calibrados, o alvo de 0,95 de acurácia é atingido automatizando
cerca de dois terços do volume e encaminhando o terço restante à revisão
humana. Essa é a forma defensável de cumprir o critério de sucesso do
protocolo, que associa confiança alta a acerto alto, sem depender de
faixas de confiança bruta cuja escala não tem interpretação
probabilística.

Uma ressalva qualifica a leitura: o calibrador é ajustado sobre escores
de um modelo treinado em três dobras e aplicado a escores de um modelo
treinado em quatro, troca deliberada entre ausência de vazamento e
casamento exato de distribuição.

**5.3 Limitações**

Os dados provêm de uma única instituição federal de ensino superior, com
textos em português brasileiro e taxonomia institucional própria.
Estender o desempenho relatado a outras instituições, taxonomias ou
idiomas exige validação externa.

A revisão humana cobre o corpus integral, o que afasta o viés de seleção
que limitaria a leitura caso apenas parte dos chamados tivesse sido
revista, mas seu desenho impõe três restrições que precisam ser lidas em
conjunto. A primeira é o avaliador único: não houve segunda avaliação
independente nem cega, nenhuma medida de concordância entre avaliadores
foi apurada e a reprodutibilidade da referência por outro especialista
permanece não testada. A literatura registra variabilidade relevante
entre anotadores em tarefas dessa natureza, de modo que a referência aqui
utilizada não deve ser tratada como isenta de erro. A segunda é a
ancoragem: o revisor decidiu com a categoria histórica à vista, condição
constitutiva da auditoria de rótulo e incompatível com anotação
independente, de sorte que a taxa de confirmação de 95,75% expressa
conjuntamente a estabilidade do registro e o efeito do procedimento, sem
que este desenho permita atribuir peso a cada parcela. A terceira é
consequência das duas anteriores: a taxa de alteração de 4,25% não
autoriza estimar a prevalência de categorias históricas incorretas na
base, e nenhuma afirmação desse tipo é feita neste artigo. Uma segunda
avaliação sobre amostra estratificada, com registro de divergências e
adjudicação por terceiro revisor, é a validação futura pertinente,
sobretudo nos pares taxonômicos ambíguos.

A taxonomia institucional apresenta pares de categorias que nomeiam o
mesmo objeto sob famílias distintas, discutidos na Subseção 4.6, e a
divergência interna medida na Subseção 3.6 confirma o problema no próprio
dado: 74 das 85 linhas em grupos de texto idêntico com referência
divergente opõem categorias de tipos diferentes de manutenção. Nesses
pares, a atribuição depende de um critério de natureza da intervenção que
o texto do chamado nem sempre permite inferir, o que impõe teto ao
desempenho alcançável por qualquer classificador textual.

As métricas valem para as 41 categorias com suporte nas cinco dobras, e
não para a taxonomia inteira. As nove categorias excluídas são justamente
as mais raras, de modo que o F1 macro reportado é, em alguma medida,
otimista em relação ao que se obteria sobre a taxonomia completa. A
Tabela A3 torna a diferença auditável, mas não a elimina.

Uma restrição adicional decorre do congelamento. As partições são
fixadas por um mapa versionado de grupos textuais, e não recalculadas a
cada execução, o que garante reprodutibilidade mas dissocia o experimento
do crescimento da base operacional. Dois registros tiveram o texto
editado após o congelamento, o que basta para explicar diferenças de
última casa decimal em execuções futuras.

Quanto às arquiteturas, o BERTimbau não foi avaliado sob este protocolo,
por limitação de infraestrutura, e a execução *out-of-fold* integral com
aceleração gráfica permanece como trabalho futuro; a LSTM, por sua vez,
treina *embeddings* do zero, sem vetores pré-treinados em português,
condição que limita a comparação entre arquiteturas neurais.

**5.4 Contribuição para a governança preditiva da manutenção**

Ao converter texto livre em categoria e confiança auditáveis, o protocolo
produz a camada de dados estruturados sobre a qual a gestão pública de
manutenção predial pode operar de forma preditiva, e não apenas reativa.
Previsão de demanda por categoria, priorização de intervenções segundo
critérios de sustentabilidade e leitura territorial do parque edificado
dependem, todas, de uma base classificada de modo confiável, e a medição
aqui reportada mostra que essa confiabilidade exige revisão humana.

A exigência tem razão específica quando a camada classificada alimenta
modelos de série temporal por categoria. Um chamado
atribuído à categoria incorreta não produz apenas um erro de rótulo:
subtrai uma ocorrência da série de uma categoria e a acrescenta à série
de outra, deslocando duas séries em sentidos opostos. O efeito propaga-se
à estimativa de demanda e de custo por categoria e, em seguida, ao
ordenamento de prioridades que dela deriva, de modo que o erro de
classificação se converte em erro de alocação de recurso. Sob essa
perspectiva, o acerto contra a referência revisada deixa de ser métrica
de comparação entre modelos e passa a operar como requisito de engenharia
da camada preditiva, o que justifica o esforço de revisão integral aqui
descrito.

O recorte da Subseção 4.11 indica em que ordem essa camada pode ser
incorporada a indicadores institucionais. A razão entre manutenção
preventiva e corretiva, que expressa a maturidade da gestão do parque
edificado e alimenta metas de conservação patrimonial, é a leitura de
menor erro medido e pode ser publicada sem revisão caso a caso. Já os
indicadores desagregados por categoria exigem restrição às classes de
maior volume dentro de cada tipo, sob pena de atribuir a frações
residuais do corpus uma precisão que a medição não sustenta. A hierarquia
converte o diagnóstico de desempenho em critério de publicação de
indicador, e não apenas em ressalva metodológica.

**6. CONSIDERAÇÕES FINAIS**

A contribuição central deste artigo é metodológica. O protocolo separa a
concordância com o rótulo histórico do acerto contra a referência humana
revisada e mede as duas grandezas sobre a mesma execução, com partições
agrupadas por texto que impedem a repetição de chamados entre treino e
teste. Essa separação evita tratar o histórico como referência
inquestionável e, ao mesmo tempo, impede concluir que toda divergência da
classificação automática representa correção do registro original.

Na avaliação sobre 13.972 chamados em 41 categorias, o LinearSVC alcança
82,53% de acurácia (IC95%: 81,15%--83,78%) e supera os demais modelos com
significância estatística, ao custo de treino de 2,44 s sobre a base
inteira. A recomendação operacional é usá-lo com calibração isotônica e
automação condicionada à confiança, regime em que cerca de dois terços do
volume podem ser decididos automaticamente com acurácia próxima de 0,95 e
o terço restante encaminhado à revisão humana.

O achado que mais altera a orientação prática é negativo. A
reclassificação automática da base histórica produz prejuízo líquido em
todos os sete modelos, porque a revisão manteve a categoria registrada em
95,75% dos casos e o espaço de alteração é estreito demais para compensar
os erros introduzidos. A classificação
automática, neste corpus, serve ao chamado novo e à triagem assistida,
não à correção retroativa em massa. Também é negativo, e igualmente útil,
o resultado da camada explícita de regras de periodicidade: ela é
redundante diante de um classificador estatístico competente, que já
captura esses sinais a partir do texto.

A finalização metodológica exige reconhecer o que os dados não respondem.
A referência provém de auditoria administrativa conduzida por avaliador
único, com a categoria histórica à vista e sem segunda avaliação
independente, de modo que o estudo não estima a prevalência de erro do
rótulo histórico nem a reprodutibilidade da referência por outro
especialista. A taxonomia institucional, por sua vez, mantém pares de
categorias que nomeiam o mesmo objeto sob famílias distintas. A próxima
etapa deve incorporar segunda avaliação, com adjudicação de divergências,
nos pares ambíguos identificados na Subseção 4.6, e submeter a própria
taxonomia a revisão. Em
paralelo, a validação externa em outras instituições e a execução
*out-of-fold* integral do BERTimbau, viável em infraestrutura com
acelerador gráfico, poderão testar a estabilidade dos resultados sob
taxonomias e volumes distintos. A camada classificada poderá então
alimentar modelos de previsão de demanda e de priorização multicritério
de intervenções sobre uma base cuja incerteza e origem das decisões
permanecem auditáveis.

**REFERÊNCIAS**

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. ABNT NBR 5674: Manutenção de
edificações: Requisitos para o sistema de gestão de manutenção. Rio de
Janeiro: ABNT, 2012.

BENAVOLI, A.; CORANI, G.; MANGILI, F. Should we really use post-hoc
tests based on mean-ranks? Journal of Machine Learning Research, v. 17,
n. 5, p. 1--10, 2016.

BENDER, E. M.; GEBRU, T.; McMILLAN-MAJOR, A.; SHMITCHELL, S. On the
dangers of stochastic parrots: can language models be too big? In:
Proceedings of the 2021 ACM Conference on Fairness, Accountability, and
Transparency (FAccT '21). New York: ACM, 2021. p. 610--623.

BOUABDALLAOUI, Y.; LAFHAJ, Z.; YIM, P.; DUCOULOMBIER, L.; BENNADJI, B.
Natural Language Processing Model for Managing Maintenance Requests in
Buildings. Buildings, v. 10, n. 9, art. 160, 2020.

BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de
Dados Pessoais (LGPD). Brasília: Presidência da República, 2018.

BROWN, T. B.; MANN, B.; RYDER, N.; SUBBIAH, M.; KAPLAN, J.; DHARIWAL,
P.; NEELAKANTAN, A. et al. Language models are few-shot learners. In:
Advances in Neural Information Processing Systems 33 (NeurIPS 2020).
Red Hook: Curran Associates, 2020. p. 1877--1901.

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

COHEN, J. A coefficient of agreement for nominal scales. Educational and
Psychological Measurement, v. 20, n. 1, p. 37--46, 1960.

DEMŠAR, J. Statistical comparisons of classifiers over multiple data
sets. Journal of Machine Learning Research, v. 7, p. 1--30, 2006.

DEVLIN, J.; CHANG, M.-W.; LEE, K.; TOUTANOVA, K. BERT:
Pre-training of deep bidirectional transformers for language
understanding. In: CONFERENCE OF THE NORTH AMERICAN CHAPTER OF THE
ASSOCIATION FOR COMPUTATIONAL LINGUISTICS, 2019, Minneapolis.
Proceedings [...]. Minneapolis: ACL, 2019. p. 4171--4186.

DICICCIO, T. J.; EFRON, B. Bootstrap confidence intervals. Statistical
Science, v. 11, n. 3, p. 189--228, 1996.

DIETTERICH, T. G. Ensemble methods in machine learning. In:
INTERNATIONAL WORKSHOP ON MULTIPLE CLASSIFIER SYSTEMS, 1., 2000,
Cagliari. Proceedings \[\...\]. Berlin: Springer, 2000. p. 1--15.
(Lecture Notes in Computer Science, v. 1857).

EFRON, B. Bootstrap methods: another look at the jackknife. The Annals
of Statistics, v. 7, n. 1, p. 1--26, 1979.

EFRON, B.; TIBSHIRANI, R. J. An introduction to the bootstrap. New York:
Chapman & Hall/CRC, 1993.

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

MARCUZZO, M.; ZANGARI, A.; GIUDICE, L.; GASPARETTO, A.; SCHIAVINATO, M.;
ALBARELLI, A. A multi-level approach for hierarchical Ticket
Classification. In: PROCEEDINGS OF THE 8TH WORKSHOP ON NOISY
USER-GENERATED TEXT (W-NUT 2022), 2022. Anais [...]. Association for
Computational Linguistics, 2022. p. 201--214.

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

SOUZA, F.; NOGUEIRA, R.; LOTUFO, R. BERTimbau: pretrained BERT
models for Brazilian Portuguese. In: BRAZILIAN CONFERENCE ON INTELLIGENT
SYSTEMS, 9., 2020. Proceedings [...]. Cham: Springer, 2020. p. 403--417.
DOI: 10.1007/978-3-030-61377-8_28.

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

VASWANI, A.; SHAZEER, N.; PARMAR, N.; USZKOREIT, J.; JONES, L.; GOMEZ,
A. N.; KAISER, L.; POLOSUKHIN, I. Attention is all you need. In:
Advances in Neural Information Processing Systems 30 (NIPS 2017).
Red Hook: Curran Associates, 2017. p. 5998--6008.

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

```{=latex}
\FloatBarrier
\clearpage
```

**APÊNDICE A — CATEGORIAS DO CORPUS E DAS PARTIÇÕES**

A Tabela A1 apresenta as 50 categorias históricas presentes nos 14.060
chamados da base congelada, ordenadas por frequência decrescente e
distribuídas em dois blocos paralelos para reduzir a extensão do apêndice.
As Tabelas A2 e A3 decompõem o denominador das métricas: a primeira lista
as 41 categorias que sustentaram suporte nas cinco dobras e compõem as
13.972 linhas avaliadas, e a segunda, as 9 que ficaram de fora.

```{=latex}
\scriptsize
\setlength{\tabcolsep}{2.5pt}
\renewcommand{\arraystretch}{0.92}
```

**Tabela A1** Distribuição dos chamados por categoria histórica.

| Categoria histórica | Quantidade | Categoria histórica | Quantidade |
|:---|---:|:---|---:|
| Manutenção Preventiva > Ar condicionado split | 1.798 | Manutenção Preventiva > Sistemas de combate a incêndio (extintores, hidrantes) | 66 |
| Climatização > Ar condicionado split | 1.640 | Estrutura Predial > Pintura | 58 |
| Estrutura Predial > Alvenaria / Pisos / Estrutura | 1.302 | Instalação de Acessórios e Mobiliário > Placas de identificação | 54 |
| Hidrossanitária > Hidráulica | 1.282 | Manutenção Preventiva > Telhados, calhas, rufos, etc. | 44 |
| Manutenção Preventiva > Gerador | 1.215 | TI / Dados / Rede > Coleta de dados | 40 |
| Estrutura Predial > Esquadrias, porta, portão e janelas | 977 | Elétrica > Gerador | 38 |
| Elétrica > Instalações elétricas | 945 | Hidrossanitária > Bomba | 38 |
| Elétrica > Iluminação | 758 | Climatização > Ar condicionado central | 37 |
| Manutenção Preventiva > Quadros Elétricos | 578 | Manutenção Preventiva > Esgoto | 33 |
| TI / Dados / Rede > Ponto de rede / fibra ótica / Wi-fi | 404 | Manutenção Preventiva > Hidráulica | 33 |
| Instalação de Acessórios e Mobiliário > Instalação/reparo de equipamentos (Suportes de TV, acessórios de banheiro e quadro branco) | 290 | Outros > Outros | 33 |
| Manutenção Preventiva > Reservatório | 279 | Segurança contra Incêndio > Sistemas de combate a incêndio (extintores, hidrantes) | 29 |
| Manutenção Preventiva > Vistoria em Instalações | 247 | Projetos e Reformas > Projeto | 25 |
| Outros > Erro de chamado | 245 | Equipamentos de Transporte > Elevador | 22 |
| Estrutura Predial > Infiltração | 215 | Elétrica > Subestação | 18 |
| Estrutura Predial > Telhados, calhas, rufos, etc. | 207 | Hidrossanitária > ETA / ETE | 16 |
| Manutenção Preventiva > Ar condicionado central | 165 | Suprimentos / Apoio Técnico > Limpeza de equipamentos, ambiente e mobiliário | 14 |
| Estrutura Predial > Forro | 146 | Manutenção Preventiva > Poços artesianos | 13 |
| Manutenção Preventiva > Iluminação | 132 | Manutenção Preventiva > Nobreak | 10 |
| Elétrica > Nobreak | 128 | Elétrica > Sistema Fotovoltaico (FV) | 7 |
| Área Externa e Ambiental > Manutenção área externa / meio ambiente / Poda de árvore / Roçagem | 109 | Área Externa e Ambiental > Drenagem | 4 |
| Posto de trabalho > Contratação de Posto de trabalho | 102 | Estrutura Predial > Instalações Especiais (gás, ar comprimido, etc.) | 3 |
| Manutenção Preventiva > Elevador | 86 | Manutenção Preventiva > Aplicação cupinicida | 3 |
| Suprimentos / Apoio Técnico > Materiais | 85 | Manutenção Preventiva > Bomba | 3 |
| Projetos e Reformas > Reforma | 83 | Suprimentos / Apoio Técnico > Transporte | 1 |
| **Total geral** | **14.060** |  |  |

*Fonte: elaboração própria a partir do corpus analisado.*

```{=latex}
\normalsize
\setlength{\tabcolsep}{6pt}
\renewcommand{\arraystretch}{1}
```

```{=latex}
\FloatBarrier
\clearpage
\scriptsize
\setlength{\tabcolsep}{2.5pt}
\renewcommand{\arraystretch}{0.9}
```

**Tabela A2** Categorias da referência revisada avaliadas na rodada, por tipo de manutenção e
classe da curva ABC interna ao tipo (n = 13.972; 41 categorias). O percentual é
relativo ao volume do próprio tipo e o F1 corresponde ao LinearSVC. P,
preventiva; C, corretiva; NM, não manutenção. Enquadram-se em não manutenção as
famílias que não descrevem serviço de manutenção predial, a saber, `Outros`,
`Suprimentos / Apoio Técnico`, `Posto de trabalho` e `Projetos e Reformas`. A
família `TI / Dados / Rede` permanece em manutenção corretiva por consistir
predominantemente em reparo de infraestrutura predial.

| Categoria de referência | Tipo | n | % do tipo | Classe | F1 |
|:------------------------------------------------------------------------|:-:|----:|-----:|:-:|-----:|
| **Preventiva** | **P** | **4.902** | **100,00** | | |
| Manutenção Preventiva > Ar condicionado split | P | 1.987 | 40,53 | A | 0,9972 |
| Manutenção Preventiva > Gerador | P | 1.208 | 24,64 | A | 0,9954 |
| Manutenção Preventiva > Quadros Elétricos | P | 578 | 11,79 | A | 0,9843 |
| Manutenção Preventiva > Reservatório | P | 318 | 6,49 | A | 0,9139 |
| Manutenção Preventiva > Vistoria em Instalações | P | 244 | 4,98 | B | 0,9419 |
| Manutenção Preventiva > Ar condicionado central | P | 168 | 3,43 | B | 0,9970 |
| Manutenção Preventiva > Iluminação | P | 132 | 2,69 | B | 0,9535 |
| Manutenção Preventiva > Elevador | P | 86 | 1,75 | B | 0,9655 |
| Manutenção Preventiva > Sistemas de combate a incêndio (extintores, hidrantes) | P | 66 | 1,35 | C | 0,8905 |
| Manutenção Preventiva > Telhados, calhas, rufos, etc. | P | 44 | 0,90 | C | 0,2162 |
| Manutenção Preventiva > Esgoto | P | 31 | 0,63 | C | 0,4286 |
| Manutenção Preventiva > Hidráulica | P | 27 | 0,55 | C | 0,0000 |
| Manutenção Preventiva > Poços artesianos | P | 13 | 0,27 | C | 1,0000 |
| **Corretiva** | **C** | **8.485** | **100,00** | | |
| Climatização > Ar condicionado split | C | 1.448 | 17,07 | A | 0,9550 |
| Hidrossanitária > Hidráulica | C | 1.263 | 14,89 | A | 0,8651 |
| Estrutura Predial > Alvenaria / Pisos / Estrutura | C | 1.138 | 13,41 | A | 0,4610 |
| Estrutura Predial > Esquadrias, porta, portão e janelas | C | 1.003 | 11,82 | A | 0,8712 |
| Elétrica > Instalações elétricas | C | 909 | 10,71 | A | 0,7248 |
| Elétrica > Iluminação | C | 764 | 9,00 | A | 0,8901 |
| TI / Dados / Rede > Ponto de rede / fibra ótica / Wi-fi | C | 412 | 4,86 | A | 0,7173 |
| Instalação de Acessórios e Mobiliário > Instalação/reparo de equipamentos (Suportes de TV, acessórios de banheiro e quadro branco) | C | 405 | 4,77 | B | 0,4730 |
| Estrutura Predial > Telhados, calhas, rufos, etc. | C | 203 | 2,39 | B | 0,4962 |
| Estrutura Predial > Infiltração | C | 202 | 2,38 | B | 0,6493 |
| Estrutura Predial > Forro | C | 168 | 1,98 | B | 0,7746 |
| Elétrica > Nobreak | C | 150 | 1,77 | B | 0,7855 |
| Área Externa e Ambiental > Manutenção área externa / meio ambiente / Poda de árvore / Roçagem | C | 103 | 1,21 | C | 0,6288 |
| Instalação de Acessórios e Mobiliário > Placas de identificação | C | 69 | 0,81 | C | 0,6494 |
| Estrutura Predial > Pintura | C | 60 | 0,71 | C | 0,5890 |
| Elétrica > Gerador | C | 43 | 0,51 | C | 0,7723 |
| Hidrossanitária > Bomba | C | 43 | 0,51 | C | 0,7238 |
| Climatização > Ar condicionado central | C | 33 | 0,39 | C | 0,7324 |
| Segurança contra Incêndio > Sistemas de combate a incêndio (extintores, hidrantes) | C | 29 | 0,34 | C | 0,4815 |
| Equipamentos de Transporte > Elevador | C | 21 | 0,25 | C | 0,7692 |
| Elétrica > Subestação | C | 19 | 0,22 | C | 0,6061 |
| **Não manutenção** | **NM** | **585** | **100,00** | | |
| Outros > Erro de chamado | NM | 258 | 44,10 | A | 0,3978 |
| Posto de trabalho > Contratação de Posto de trabalho | NM | 102 | 17,44 | A | 0,9561 |
| Suprimentos / Apoio Técnico > Materiais | NM | 96 | 16,41 | A | 0,4790 |
| Projetos e Reformas > Reforma | NM | 65 | 11,11 | A | 0,2407 |
| Outros > Outros | NM | 28 | 4,79 | B | 0,3404 |
| Projetos e Reformas > Projeto | NM | 23 | 3,93 | B | 0,0000 |
| Suprimentos / Apoio Técnico > Limpeza de equipamentos, ambiente e mobiliário | NM | 13 | 2,22 | C | 0,0909 |
| **Total avaliado** | | **13.972** | | | |

As nove categorias restantes da taxonomia não sustentam suporte nas cinco
dobras e ficam fora das partições, conforme o critério da Subseção 3.5.
Somam 88 linhas, ou 0,63% da base congelada, e estão discriminadas na
Tabela A3 para que a diferença entre os dois denominadores permaneça
auditável.

**Tabela A3** Categorias fora das partições canônicas.

| Categoria de referência | Linhas | Motivo da exclusão |
|:---|---:|:---|
| TI / Dados / Rede > Coleta de dados | 40 | ausente de ao menos uma dobra após a estratificação |
| Hidrossanitária > ETA / ETE | 15 | ausente de ao menos uma dobra após a estratificação |
| Manutenção Preventiva > Nobreak | 9 | ausente de ao menos uma dobra após a estratificação |
| Elétrica > Sistema Fotovoltaico (FV) | 7 | ausente de ao menos uma dobra após a estratificação |
| Estrutura Predial > Instalações Especiais (gás, ar comprimido, etc.) | 5 | ausente de ao menos uma dobra após a estratificação |
| Área Externa e Ambiental > Drenagem | 4 | suporte insuficiente para as cinco dobras |
| Manutenção Preventiva > Aplicação cupinicida | 3 | suporte insuficiente para as cinco dobras |
| Manutenção Preventiva > Bomba | 3 | suporte insuficiente para as cinco dobras |
| Suprimentos / Apoio Técnico > Transporte | 2 | suporte insuficiente para as cinco dobras |
| **Total** | **88** | |

*Fonte: elaboração própria a partir do corpus analisado.*

```{=latex}
\normalsize
\setlength{\tabcolsep}{6pt}
\renewcommand{\arraystretch}{1}
```

