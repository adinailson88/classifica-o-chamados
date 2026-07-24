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
da Universidade Federal do Sul da Bahia. O experimento utiliza 13.825
chamados não vazios, organizados em 54 categorias históricas, e compara
classificadores clássicos baseados em TF-IDF (Naive Bayes, Regressão
Logística, LinearSVC calibrado, SGD, Random Forest e Extra Trees), rede
neural LSTM bidirecional e, como extensão planejada, transformador
pré-treinado em português. O diferencial metodológico reside na
distinção entre concordância com o histórico administrativo e acerto
validado por revisão humana, tratando a categoria histórica como
referência preliminar imperfeita. Resultados preliminares indicam
superioridade do LinearSVC calibrado, com acurácia de 80,26% (IC95%:
79,59%--80,92%), enquanto a LSTM apresentou concordância de 67,57%. A
normalidade da concordância por turno foi rejeitada para todos os
modelos, justificando testes não paramétricos (Friedman, Cochran Q,
McNemar, bootstrap). O custo computacional é incorporado como dimensão
de avaliação, evidenciando que modelos lineares podem oferecer melhor
relação entre desempenho e viabilidade operacional em cenários de texto
curto, ruidoso e desbalanceado.

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
Southern Bahia. The experiment uses 13,825 non-empty records organized
into 54 historical categories and compares TF-IDF-based classical
classifiers (Naive Bayes, Logistic Regression, calibrated LinearSVC,
SGD, Random Forest, and Extra Trees), a bidirectional LSTM neural
network, and, as a planned extension, a Portuguese pre-trained
transformer. The methodological contribution lies in distinguishing
agreement with administrative history from human-validated accuracy.
Preliminary results indicate calibrated LinearSVC superiority, with
80.26% accuracy (95%CI: 79.59%--80.92%), while LSTM achieved 67.57%.
Normality was rejected for all models, supporting non-parametric tests
(Friedman, Cochran Q, McNemar, bootstrap). Computational cost is
incorporated as an evaluation dimension.*

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
base experimental contém 13.825 chamados não vazios, distribuídos em 54
categorias históricas, e os campos textuais considerados agregam
informações do título e da descrição do chamado, além de informações
associadas à ordem de serviço. O estudo compara modelos clássicos
baseados em TF-IDF (Naive Bayes, Regressão Logística, LinearSVC, SGD,
Random Forest e Extra Trees) com abordagem neural LSTM bidirecional e
extensão planejada para transformadores pré-treinados em português. O
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

**\[INSERIR AQUI: fig1_pipeline_governanca.png\]**

*Figura do pipeline metodológico --- gerar a partir do fluxo descrito ou
utilizar diagrama existente no repositório.*

**Figura 1** Pipeline de governança preditiva: fluxo metodológico
completo, da extração da base à retroalimentação por validação humana.

Fonte: Elaborado pelos autores (2026).

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
classificados em turnos. Na consolidação desta auditoria (16/07/2026), o
número de chamados elegíveis já havia crescido para 13.954, nas mesmas
54 categorias históricas. Os resultados da Seção 4 utilizam esse recorte
mais recente; eventuais diferenças frente a valores publicados em
versões preliminares deste texto refletem o crescimento da base, não uma
mudança metodológica.

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

O desenho experimental considera sete modelos materializados e uma
extensão planejada. Os classificadores clássicos adotam representação
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
antecipada. A extensão com BERTimbau ou MiniLM *fine-tuned* deve ser
tratada como etapa complementar, dependente de execução controlada,
persistência de modelo e comparação estatística contra os
classificadores já consolidados.

Um oitavo modelo, baseado em transformador pré-treinado em português com
ajuste fino (BERTimbau, neuralmind/bert-base-portuguese-cased), foi
incorporado como extensão contextual, com fallback automático para
LSTM/RF quando as dependências de treinamento (torch/transformers) não
estão disponíveis no ambiente de execução. Pelo custo computacional em
CPU, o ajuste fino roda em fluxo de trabalho próprio, de baixa
frequência, fora do ciclo padrão de 15 minutos. Até a data desta
auditoria, o treinamento havia sido adiado automaticamente por avanço
insuficiente da base validada (limiar de 100 novos casos conferidos
ainda não atingido); seus resultados comparativos ainda não estão
disponíveis e permanecem como trabalho em andamento, não como resultado
reportado na Seção 4.

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
e 4.3), calculado exclusivamente sobre os chamados em que houve
conferência dupla das colunas M (histórico) e N (IA). Na data de
consolidação desta auditoria (16/07/2026), a base elegível continha
13.954 chamados e a conferência humana já cobria 4.737 chamados (33,9%
da base), dos quais 4.681 com decisão travada e sem conflito. Ainda que
essa cobertura não configure amostra aleatória --- a priorização recaiu
sobre divergências e casos de menor confiança ---, seu tamanho já
permite leitura estatística mais robusta do que a amostra parcial de 305
casos (2,2% da base) reportada em versões anteriores deste protocolo.

**4.1 Concordância com o histórico (base completa)**

A comparação contra a categoria histórica, sobre a base completa (n =
13.954, com intervalo de confiança por bootstrap a 95%), mantém o
LinearSVC calibrado na liderança, com acurácia de 0,7996 (IC95%:
0,7927--0,8063), seguido por Extra Trees (0,7859), Random Forest
(0,7792), SGD (0,7745), Regressão Logística (0,7640) e Naive Bayes
(0,6984). O teste de Cochran Q confirma diferença global entre os seis
modelos (Q = 1.448,755; gl = 5; p \< 0,001). O Kappa de Cohen entre cada
modelo e o histórico acompanha o mesmo ordenamento (LinearSVC 0,7843;
Extra Trees 0,7679; Random Forest 0,7604; SGD 0,7581; Regressão
Logística 0,7473; Naive Bayes 0,6689), e o Kappa de Fleiss entre os
próprios modelos (0,8068) indica concordância substancial entre
arquiteturas distintas treinadas sobre a mesma base --- evidência de que
a hierarquia de desempenho não é artefato de uma única execução. A
sétima fonte de classificação, a Etapa 1 oficial (executor LSTM/RF de
produção), mantém concordância de 76,7% e confiança média de 71,7% no
recorte publicado no painel, posicionando-se entre Random Forest e SGD
nesta métrica.

**Tabela 1** Concordância com a categoria histórica, base completa (n =
13.954)

| Modelo | Acurácia | IC95% bootstrap | Kappa vs. histórico |
|---|---|---|---|
| LinearSVC calibrado | 0,7996 | 0,7927 -- 0,8063 | 0,7843 |
| Extra Trees | 0,7859 | 0,7789 -- 0,7929 | 0,7679 |
| Random Forest | 0,7792 | 0,7722 -- 0,7862 | 0,7604 |
| SGD | 0,7745 | 0,7678 -- 0,7812 | 0,7581 |
| Regressão Logística | 0,7640 | 0,7570 -- 0,7709 | 0,7473 |
| Naive Bayes | 0,6984 | 0,6909 -- 0,7058 | 0,6689 |

Fonte: estatistica.json, gerado em 16/07/2026 (n = 13.954).

**4.2 Ranking validado por conferência humana**

A avaliação contra a verdade validada por conferência humana (n = 4.681;
coluna M = conferência do histórico, coluna N = conferência da IA) muda
a magnitude, mas não a ordem, da liderança observada em 4.1: todos os
seis modelos atingem acerto validado entre 92% e 96%, patamar muito
superior à concordância com o histórico. O LinearSVC calibrado permanece
o melhor modelo isolado, com acerto validado de 0,9549 (IC95%:
0,9489--0,9603), seguido por SGD (0,9500), Random Forest (0,9477), Extra
Trees (0,9470), Regressão Logística (0,9442) e Naive Bayes (0,9203). A
diferença entre o primeiro e o segundo colocado é pequena em termos
absolutos (0,49 ponto percentual), mas estatisticamente significativa
(McNemar, p = 0,0044), sustentando a recomendação de uso do LinearSVC
com calibração como IA de referência. Nenhum método de combinação
testado --- confiança calibrada máxima (0,9562), maioria ponderada com
pesos aprendidos out-of-fold (0,9554) ou maioria simples (0,9547) ---
supera o LinearSVC isolado com significância estatística (McNemar p ≥
0,05 nos três casos), de modo que combinar modelos não se justifica
operacionalmente diante do custo adicional de manter um comitê.

**Tabela 2** Acerto validado por conferência humana dupla (n = 4.681)

| Modelo | Acerto validado | IC95% |
|---|---|---|
| LinearSVC calibrado | 0,9549 | 0,9489 -- 0,9603 |
| SGD | 0,9500 | 0,9436 -- 0,9562 |
| Random Forest | 0,9477 | 0,9413 -- 0,9539 |
| Extra Trees | 0,9470 | 0,9406 -- 0,9530 |
| Regressão Logística | 0,9442 | 0,9374 -- 0,9509 |
| Naive Bayes | 0,9203 | 0,9122 -- 0,9280 |

Fonte: avaliacao_final.json, gerado em 16/07/2026, conferência dupla
M/N/P.

**4.3 A classificação oficial frente ao histórico: matriz de confusão
validada**

Um resultado adicional, obtido diretamente da conferência dupla sobre a
classificação oficial da Etapa 1 (coluna G, executor LSTM/RF), qualifica
a tese de rótulos ruidosos apresentada na Introdução. Sobre 4.737
conferências, a categoria histórica (GLPI) validada atinge acerto de
0,9854, superior ao acerto validado da IA oficial (0,9508). A matriz de
confusão IA×GLPI mostra 4.454 casos em que ambos estão corretos, 45 em
que ambos estão incorretos, 186 em que a IA erra e o histórico está
certo, e apenas 13 em que a IA corrige um histórico incorreto. Essa
proporção --- aproximadamente quatorze casos de erro da IA para cada
caso de correção de histórico --- indica que, nesta base e nesta amostra
de conferência, o rótulo histórico do GLPI é, em geral, mais confiável
do que a predição automática isolada. O resultado nuança, sem invalidar,
a premissa metodológica do artigo: existe ruído real no histórico (58
dos 4.737 casos conferidos, 1,2%, têm categoria histórica incorreta),
mas ele é proporcionalmente menor do que o risco de erro da própria IA
nesta amostra. A implicação prática é que a IA deve ser tratada como
instrumento de triagem e auditoria complementar ao histórico, não como
substituto ou árbitro superior a ele.

*Nota metodológica (23/07/2026)*: o campo do painel que sustentaria uma nova
versão desta matriz (`calibracao.json`, `validacao_humana.matriz_ia_x_glpi`)
apresenta, na consolidação mais recente, variância nula entre as quatro
células — resultado do mesmo viés de seleção identificado e corrigido na
Subseção 4.4 (a coluna N de conferência bruta raramente registra "Errado" na
prática). Diferentemente da Subseção 4.4, este campo específico **ainda não
foi corrigido**; os números de 16/07/2026 citados acima permanecem como
único registro disponível desta matriz e **não devem ser tratados como
reconfirmados** até uma nova rotina de cálculo (comparando a decisão
travada M/N/P, não a marcação bruta de uma única coluna) ser implementada e
reexecutada. Ver `docs/PLANO_PDF_ARTIGO_PAGES.md` para o registro técnico
completo.

**4.4 Confiança, calibração e faixas de decisão**

A calibração bruta da Etapa 1 oficial mantém ECE histórico de 0,0536.
Quando segmentada por faixa de confiança e cruzada com a validação
humana, a faixa igual ou superior a 95% de confiança (n = 4.739; cerca
de 34% da base) apresenta concordância de 99,35% com o histórico e, mais
relevante, acerto validado de 99,73% sobre os 3.284 casos já conferidos
nessa faixa --- resultado que atinge e supera, nessa faixa específica, a
meta de referência do experimento (confiança calibrada ≥95% associada a
acerto real ≥95%). Nas faixas inferiores, a degradação de desempenho
acompanha a queda de confiança de forma consistente (90--95%: acerto
validado 96,83%; 80--90%: 94,32%; 70--80%: 87,59%; 50--70%: 61,40%;
inferior a 50%: 38,10%), o que corrobora a correlação positiva entre
confiança bruta e acerto já observada na versão preliminar deste
protocolo, mesmo sem calibração formal (Platt/isotônica) aplicada a essa
camada. A leitura por executor confirma o desenho de triagem automática:
o executor LSTM de alta confiança (n = 4.739) atinge 99,73% de acerto
validado, enquanto o executor de baixa confiança (n = 9.215) atinge
84,30% (n = 1.414 validados) --- diferença que justifica represar apenas
os casos de baixa confiança para revisão manual.

*Atualização de dados (23/07/2026)*: o parágrafo acima preserva os números de
16/07/2026 citados na versão anterior deste rascunho. Nesta data, ao
revalidar a fonte viva (`docs/dados/calibracao.json`), foi corrigido um viés
de seleção em `src/calibracao.py` que fazia o acerto validado por faixa sair
artificialmente igual a 100% em toda faixa de confiança, inclusive abaixo de
50% (a coluna N de conferência bruta isolada raramente registra "Errado" no
uso real; a correção passou a comparar a classificação do executor contra a
categoria **decidida** pela memória M/N/P — a mesma verdade usada na Subseção
4.2 — em vez da marcação bruta de uma única coluna). A Tabela 3 mostra os
números corrigidos, já sobre uma base de conferência bem maior (9.096
decisões travadas, ante 4.681 em 16/07):

**Tabela 3** Acerto validado por faixa de confiança bruta, executor oficial
(Etapa 1), pós-correção do viés de seleção (n = 9.096 decisões travadas)

| Faixa | n total | Concord. histórico | n validados | Acerto validado |
|---|---|---|---|---|
| < 50% | 3.972 | 42,35% | 876 | 49,89% |
| 50–70% | 1.504 | 73,40% | 741 | 83,94% |
| 70–80% | 972 | 87,45% | 654 | 94,95% |
| 80–90% | 1.499 | 87,99% | 1.118 | 93,92% |
| 90–95% | 1.210 | 92,98% | 1.009 | 91,48% |
| ≥ 95% | 4.808 | 99,08% | 4.698 | 96,79% |

Fonte: `calibracao.json`, gerado em 23/07/2026 21:31 (America/Bahia), já com a
correção de `src/calibracao.py` aplicada. ECE histórico nesta consolidação:
0,0598. A meta do experimento (confiança calibrada ≥95% associada a acerto
real ≥95%) fica muito próxima de ser atingida na faixa mais alta (96,79%),
mas — como já registrado na versão anterior deste texto — a confiança
utilizada aqui ainda é bruta (softmax/*decision_function*), não formalmente
calibrada por Platt ou isotônica, e a amostra de conferência prioriza
divergências, não é aleatória. Note-se também que a faixa 80–90% (93,92%)
supera ligeiramente a faixa 90–95% (91,48%) — pequena inversão de monotonia
plausível em dados reais com amostras desse tamanho, mas que merece
acompanhamento nas próximas consolidações antes de ser tratada como padrão
estável.

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

**4.7 Custo computacional**

Nos recortes de comparação por lote (1.000 registros cada), o tempo de
treino mantém-se na casa de segundos para os modelos lineares e
probabilísticos mais simples (por exemplo, Naive Bayes ≈ 1,1 s) e sobe
para modelos com mais hiperparâmetros (Regressão Logística ≈ 8,7 s neste
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

**4.8 Figuras**

As figuras originalmente planejadas para este capítulo (Figura 1 — pipeline
metodológico, Subseção 3.1; distribuição de confiança por desfecho; trade-off
acurácia×custo; pares de maior confusão, Subseção 4.6) ainda não foram
regeneradas a partir dos dados desta auditoria; os mesmos resultados são
apresentados aqui em forma tabular e textual, com números conferidos
diretamente nos arquivos publicados do painel. A geração das figuras
finais depende da execução dos scripts de visualização (R ou Python)
contra os JSON vigentes e fica registrada como pendência explícita, não
como lacuna de conteúdo.

**5. DISCUSSÃO**

A comparação entre concordância histórica (Subseção 4.1) e desempenho
validado (Subseção 4.2) revela um padrão que a literatura sobre rótulos
ruidosos ajuda a interpretar, mas que a amostra validada desta pesquisa
qualifica com maior precisão do que hipóteses genéricas permitiriam: a
distância entre concordância com o histórico (≈70--80%) e acerto
validado (≈92--96%) não decorre apenas de erro do histórico, mas também
do fato de que boa parte das divergências entre IA e histórico
corresponde a erro da própria IA, não do registro original. A matriz
IA×GLPI (Subseção 4.3) mostra que, quando os dois discordam, o histórico
está correto com frequência muito maior (186 casos) do que a IA corrige
um erro genuíno do histórico (13 casos). Esse achado não invalida a
premissa metodológica de que a categoria histórica não deve ser tratada
como verdade absoluta --- ainda existe uma taxa real, embora pequena
(1,2% dos casos conferidos), de erro confirmado no registro original
---, mas recomenda cautela contra a leitura oposta e igualmente
equivocada, de que baixa concordância com o histórico implica
automaticamente acerto da IA. A validação humana, portanto, cumpre
função insubstituível: sem ela, seria impossível distinguir as duas
situações apenas observando a taxa de concordância.

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
classificados não é uniforme entre modelos, e para três dos seis
classificadores avaliados (SGD, Random Forest e Extra Trees) a
reclassificação nesta rodada piorou mais casos do que corrigiu. Isso
sugere que decisões de reclassificação em produção devem ser tomadas por
modelo, com base no ganho líquido medido, e não generalizadas a partir
do desempenho médio de concordância ou acerto validado --- um modelo
pode ser competitivo na classificação inicial e, ainda assim, não ser um
bom candidato a reclassificar decisões já tomadas.

A camada de entropia de Shannon e divergência de Jensen-Shannon
(Subseção 4.6) não substitui as métricas supervisionadas ou a validação
humana, mas amplia o repertório de governança do experimento ao separar
três fenômenos que a acurácia isolada tende a confundir: erro de modelo,
ambiguidade genuína da taxonomia institucional e heterogeneidade natural
da distribuição de chamados. A identificação de 3.451 chamados (24,7% da
base) com alto desacordo estrutural entre os oito modelos oferece um
critério de priorização de auditoria distinto do simples corte por baixa
confiança de um único classificador, e complementa a fila já construída
a partir da conferência dupla M/N.

A meta de confiança calibrada igual ou superior a 95% associada a acerto
real igual ou superior a 95% (Subseção 4.4), estabelecida como critério
de sucesso deste protocolo, já é atingida na faixa alta de confiança da
Etapa 1 oficial (99,73% de acerto validado sobre 3.284 casos
conferidos), ainda que a confiança utilizada seja bruta
(softmax/decision_function), não formalmente calibrada por Platt ou
isotônica. Esse resultado é encorajador, mas deve ser lido com a mesma
cautela metodológica aplicada ao restante do artigo: a amostra validada,
embora já substancial (33,9% da base), prioriza divergências e casos de
menor confiança na sua composição original, o que pode inflar
artificialmente o acerto validado nas faixas de alta confiança, onde a
conferência tende a simplesmente confirmar o que já era esperado. A
confirmação definitiva da meta depende da conclusão da conferência
humana sobre uma amostra mais representativa da faixa alta, e não apenas
dos casos originalmente priorizados.

As limitações do estudo permanecem análogas às já registradas, com dois
ajustes relevantes em relação à versão anterior. Primeiro, a amostra
validada deixou de ser uma amostra piloto de 305 casos (2,2% da base) e
passou a cobrir 4.737 conferências (33,9% da base), o que aumenta
substancialmente a robustez estatística das Subseções 4.2 a 4.4, ainda
que sem garantia de representatividade aleatória. Segundo, os dois
conflitos de conferência identificados em versões anteriores do
protocolo (casos em que tanto a coluna M quanto a N foram marcadas como
corretas, apesar de histórico e IA divergirem) foram resolvidos e não
aparecem mais nos dados publicados (conflitos = 0 em
avaliacao_final.json), embora isso não elimine a possibilidade de novos
conflitos surgirem à medida que a conferência avança sobre casos ainda
não revisados. Persistem como limitações a dependência de uma única
instituição como caso empírico, a ausência de resultados comparativos do
oitavo modelo (transformador com ajuste fino), cujo treinamento
permanece adiado por critério automático de avanço insuficiente da base
validada, e a intermitência observada na publicação automática do painel
no GitHub Pages, discutida na auditoria técnica que acompanha este
capítulo.

**6. CONSIDERAÇÕES FINAIS**

O presente capítulo atualizou o protocolo de classificação automática
multimodelo de chamados de manutenção predial universitária em português
brasileiro com os resultados acumulados até 16 de julho de 2026,
incorporando uma oitava fonte de classificação (transformador com ajuste
fino, ainda em treinamento adiado), uma camada de memória de decisão por
veto e trava de categorias já conferidas, e uma camada de análise
informacional baseada em entropia de Shannon e divergência de
Jensen-Shannon. A contribuição central permanece metodológica: não
apenas identificar o melhor classificador, mas estruturar um protocolo
em que aprendizado de máquina, estatística não paramétrica, memória de
decisão e auditoria humana qualificam progressivamente a base de dados e
revelam inconsistências taxonômicas.

Diferentemente da versão preliminar deste texto, a conclusão atual já se
apoia em validação humana substancial, e não apenas em concordância com
o histórico. Sobre 4.681 chamados com decisão travada e sem conflito, o
LinearSVC calibrado confirma-se como a melhor IA isolada, com acerto
validado de 95,49% (IC95%: 94,89%--96,03%), à frente de SGD (95,00%),
Random Forest (94,77%), Extra Trees (94,70%), Regressão Logística
(94,42%) e Naive Bayes (92,03%); nenhuma estratégia de combinação de
modelos supera essa IA isolada com significância estatística. A matriz
de confusão IA×GLPI qualifica, sem invalidar, a premissa de rótulos
ruidosos: o histórico administrativo, quando conferido, acerta mais do
que a IA (98,54% contra 95,08%), mas ainda apresenta uma taxa real e não
desprezível de erro confirmado (1,2% dos casos conferidos), o que
justifica manter a arquitetura de validação humana como componente
permanente do protocolo, não como etapa transitória a ser eliminada
quando a IA atingir bom desempenho médio.

A meta original do experimento --- confiança calibrada igual ou superior
a 95% associada a acerto validado igual ou superior a 95% --- já é
observada na faixa de alta confiança da classificação oficial (99,73% de
acerto validado), resultado que recomenda cautela otimista: é
encorajador, mas ainda depende da conclusão da conferência humana sobre
uma amostra mais representativa antes de ser tratado como meta cumprida
para fins de liberação em produção sem revisão. Os próximos passos deste
protocolo incluem a conclusão da conferência humana pendente (colunas M,
N e P), a calibração formal por modelo (Platt/isotônica/temperatura)
condicionada a essa conferência, a decisão sobre retomar ou não o
treinamento do oitavo modelo (transformador com ajuste fino), a revisão
taxonômica dirigida pelos candidatos identificados na etapa de
cruzamento de taxonomia e na entropia de Shannon, e a estabilização da
publicação automática do painel, cuja intermitência técnica está
documentada na auditoria que acompanha este capítulo. Com isso, o
protocolo pretende seguir contribuindo tanto para a literatura de
facility management e processamento de linguagem natural aplicado quanto
para a melhoria concreta e continuamente auditável da gestão de
manutenção predial em instituições públicas.

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
| Critério de calibração de confiança (bruta vs. calibrada) e meta de desempenho | 3.8, 4.4 | Parcial — meta declarada (≥95%/≥95%); calibração formal (Platt/isotônica) ainda não aplicada |
| Protocolo de validação humana | 3.6 | Sim |
| Cobertura da validação humana na data de publicação (n e % da base) | 4 (abertura) | Sim, mas desatualizada — ver nota de revalidação de dados |
| Tratamento de conflitos de conferência | 3.7 | Sim (regra de veto/trava) |
| Reprodutibilidade (scripts e dados versionados) | 3.9 | Sim (repositório público, JSONs sanitizados) |
| Limitações declaradas | 5, 6 | Sim |
| Figuras/tabelas geradas a partir de dados verificáveis | 4.8 | Não — pendência explícita registrada |

**Apêndice C — Matriz de decisão M/N/P**

*Pendência explícita*: apêndice ainda não preenchido. Deve tabular, para a
amostra de conferência humana dupla, a relação entre coluna M (conferência do
histórico), coluna N (conferência da IA) e coluna P (decisão final travada),
com contagens por combinação de valores. Depende de extração direta da
planilha experimental na data de fechamento da Seção 4 — não reaproveitar
números de auditorias anteriores sem reconferência.
