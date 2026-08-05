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

**CLASSIFICAÇÃO AUDITÁVEL DE CHAMADOS DE MANUTENÇÃO PREDIAL:
FLUXO HUMANO–IA, CALIBRAÇÃO E RISCO DE RECLASSIFICAÇÃO**

*Auditable classification of building maintenance work orders: human–AI
workflow, calibration, and reclassification risk*

**Adinailson Guimarães de Oliveira** - adinailson.oliveira@cja.ufsb.edu.br
**Fabrício Berton Zanchi** - fabricio.berton@ufsb.edu.br

Universidade Federal do Sul da Bahia (UFSB), Programa de Pós-Graduação
em Biossistemas

**RESUMO**

A triagem de chamados de manutenção predial em instituições públicas depende
da categoria registrada no sistema de atendimento, cujo acerto condiciona
todo uso analítico da base. A literatura sobre a classificação automática
desses registros concentra-se em corpora de outros idiomas e domínios e
avalia o classificador contra o rótulo histórico, o que impede distinguir
erro do modelo de erro do registro e deixa por medir o risco de reescrever a
base. Este artigo propõe e mede um protocolo auditável sobre 14.060 chamados
de manutenção predial universitária em português brasileiro, com métricas
nas 13.972 linhas das 41 categorias com suporte. As predições são obtidas
fora da amostra sob validação cruzada agrupada pelo texto normalizado,
unidade também adotada na inferência, de modo que registros de texto
idêntico não atravessam a fronteira entre treino e teste nem contam como
independentes. A referência de avaliação provém de auditoria administrativa
de rótulo sobre a totalidade do corpus, que alterou a categoria histórica em
4,25% dos registros. O melhor dos sete classificadores alcança acurácia de
0,8253 contra essa referência, e a calibração isotônica viabiliza automação
seletiva de cerca de dois terços do volume com acurácia de 0,95,
encaminhando o restante ao revisor. A reclassificação automática da base
produz ganho líquido negativo nos sete modelos, veredito que se mantém sob
custos assimétricos e converte a divergência em critério de priorização da
auditoria. A contribuição é o protocolo que articula governança de rótulo,
inferência sob dependência textual, calibração, automação seletiva e
avaliação explícita do risco de reclassificação.

**Palavras-chave:** manutenção predial; classificação de chamados;
auditoria de rótulo; calibração e classificação seletiva; rótulos
ruidosos.

**ABSTRACT**

*Triage of building maintenance work orders in public institutions relies on
the category recorded in the service-management system, whose accuracy
conditions every later analytical use of the database. Research on the
automatic classification of such records concentrates on corpora from other
languages and domains and evaluates the classifier against the historical
label, which prevents telling model error from record error and leaves the
risk of rewriting the database unmeasured. This paper proposes and measures
an auditable classification protocol over 14,060 university building
maintenance work orders in Brazilian Portuguese, with metrics computed on
the 13,972 records of the 41 categories with support. Predictions are
obtained out of sample under cross-validation grouped by normalised text,
the same unit adopted for inference, so that records sharing identical text
neither cross the train-test boundary nor count as independent evidence. The
evaluation reference comes from an administrative label audit over the
entire corpus, which changed the historical category in 4.25% of records.
The best of the seven classifiers compared reaches 0.8253 accuracy against
that reference, and isotonic calibration enables selective automation of
about two thirds of the volume at 0.95 accuracy, routing the remainder to
human review. Automatic reclassification of the base yields a negative net
gain across the seven models, a verdict that holds under asymmetric costs
and turns divergence into a criterion for prioritising the audit queue. The
contribution lies in the protocol that articulates label governance,
inference under textual dependence, calibration, selective automation, and
explicit assessment of reclassification risk.*

***Keywords:** building maintenance; work-order classification; label
audit; calibration and selective classification; noisy labels.*

**1. INTRODUÇÃO**

A manutenção predial responde pela preservação do patrimônio edificado e
pela continuidade das atividades finalísticas das instituições federais de
ensino superior (IFES), ainda que disponha historicamente de menos de 2% do
orçamento institucional (MARTINS; ESPEJO, 2024; PAMPANA *et al.*, 2022). Sob
essa restrição, decidir onde intervir depende de evidência sobre o parque
edificado, conforme a gestão sistematizada definida pela NBR 5674 (ABNT,
2012).

O sinal disponível para essa decisão é textual. Um campus universitário
constitui um biossistema construído, isto é, a integração dinâmica entre
infraestrutura física, atividade humana, sistemas tecnológicos e
condicionantes ambientais, cuja persistência depende de retroalimentação
contínua entre uso, falha e reparo (CAPRA, 1996; ODUM, 1971), e sua
governança repousa sobre a capacidade institucional de captar sinais
operacionais e convertê-los em decisão (GRIMM *et al.*, 2008). Nas IFES,
esse sinal assume a forma de registros de chamados de manutenção,
armazenados em linguagem não estruturada, cuja interpretação individual
impede o uso direto por mecanismos de decisão automatizada (MORAIS; PAULA;
REIS, 2023; MOHAMMED; AMOAH, 2025). Convertê-los em dado estruturado e
auditável é condição anterior a qualquer camada preditiva.

Três obstáculos condicionam essa conversão: a natureza textual curta e
heterogênea dos registros, cujas abreviações locais e jargões de equipe
dificultam a aplicação de modelos genéricos de processamento de linguagem
natural (PLN) (SUNDARAM; ZEID, 2025); o desbalanceamento entre categorias,
em que demandas recorrentes concentram grande parte da base e categorias
raras dispõem de poucos exemplos para treinamento supervisionado (LI *et
al.*, 2024); e a qualidade do próprio rótulo histórico, que pode resultar de
interpretação rápida ou de taxonomia ainda não estabilizada, de modo a
constituir evidência importante, mas não referência definitiva (ZHANG *et
al.*, 2025; KEJRIWAL *et al.*, 2024).

A literatura confirma a viabilidade técnica da tarefa, com acurácia de 0,83
sobre 15.623 ordens de serviço hospitalares (LI *et al.*, 2024) e 78% em
requisições de edificação hospitalar (BOUABDALLAOUI *et al.*, 2020). Essas
aplicações concentram-se, todavia, em bases de outros idiomas e em domínios
industriais ou hospitalares, e avaliam o classificador contra o rótulo
registrado, sem submetê-lo a auditoria. Restam duas lacunas convergentes: a
escassez de corpora em português brasileiro na manutenção predial pública
universitária e a ausência de protocolo que trate a categoria histórica como
objeto de auditoria e meça o risco de reescrevê-la.

A pergunta que orienta este artigo não é, portanto, qual classificador mais
concorda com a categoria histórica, e sim sob que condições a classificação
automática produz dado estruturado confiável sem herdar as inconsistências
do registro que lhe deu origem.

A resposta é um protocolo auditável, medido sobre 14.060 chamados reais da
Universidade Federal do Sul da Bahia (UFSB). A contribuição não está na
comparação entre algoritmos, aqui meio e não fim, mas na articulação de
cinco elementos: governança de rótulo por auditoria administrativa sobre o
corpus integral, que separa a concordância com o histórico do acerto contra
a referência revisada; inferência que respeita a dependência entre chamados
de texto repetido, com o grupo textual como unidade na partição e nos
testes; calibração dos escores de confiança; automação seletiva condicionada
a esses escores, com encaminhamento do restante ao revisor; e avaliação do
risco de reclassificação por função de utilidade explícita. Sete
classificadores percorrem o protocolo sob as mesmas partições, e o BERTimbau
fica fora por custo computacional medido.

O objetivo geral é avaliar em que medida esse protocolo produz camada de
dados estruturados apta a sustentar a governança da manutenção predial
pública, consoante à integração físico-humano-tecnológico-ambiental do
biossistema construído.

**2. REFERENCIAL CONCEITUAL**

**2.1 Classificação automática de ordens de manutenção e de chamados**

Ordens de manutenção documentam sintomas, locais, equipamentos e soluções em
forma textual semiestruturada, o que lhes confere valor informacional
elevado e uso habitualmente reduzido no planejamento (PAMPANA *et al.*,
2022; MORAIS; PAULA; REIS, 2023). Li *et al.* (2024) são a referência-âncora
desta pesquisa por tratarem da automação de ordens de manutenção predial,
ainda que em idioma e taxonomia distintos, e Sundaram e Zeid (2025)
acrescentam que chamados curtos e descrições incompletas inviabilizam
modelos genéricos sem adaptação lexical ao corpus.

Na classificação de *tickets*, a evolução das representações lexicais aos
modelos pré-treinados, como o Ticket-BERT (LIU; BENGE; JIANG, 2023), não se
transfere sem cautela à manutenção predial, cujos sistemas e equipamentos
não coincidem com categorias de incidentes digitais (SUNDARAM; ZEID, 2025).
Em texto curto de vocabulário especializado, ademais, classificadores
lineares sobre representações TF-IDF sustentam desempenho equivalente ao de
redes neurais em múltiplos *benchmarks* (GALKE; SCHERP, 2022).

**2.2 Desbalanceamento e rótulos ruidosos**

Duas propriedades da base condicionam a leitura das métricas. O
desbalanceamento entre categorias faz a acurácia agregada ser dominada pelas
classes majoritárias e mascarar falhas nas raras, o que recomenda métricas
de média por classe com o suporte declarado (SOKOLOVA; LAPALME, 2009) e leva
a classificação hierárquica de chamados a excluir rótulos de frequência
muito baixa (MARCUZZO *et al.*, 2022). O ruído de rótulo decorre de
ambiguidade semântica, sobreposição taxonômica ou erro de registro (ZHANG
*et al.*, 2025), e *benchmarks* rotulados por humanos contêm variabilidade
relevante, o que questiona a prática de assumir referência única onde há
julgamento subjetivo (KEJRIWAL *et al.*, 2024). A categoria histórica é
tratada, por conseguinte, como registro administrativo sujeito a auditoria,
e a referência de avaliação provém de auditoria de rótulo.

**2.3 Calibração e classificação seletiva**

O escore de confiança de um classificador não é, por construção, uma
probabilidade, e associá-lo à frequência de acerto exige calibração por
ajuste sigmoidal da margem (PLATT, 1999) ou por regressão isotônica,
necessidade que persiste mesmo em arquiteturas de alto desempenho (GUO *et
al.*, 2017). É a calibração que torna operável a classificação seletiva,
regime no qual o modelo decide apenas acima de um limiar e transfere os
demais casos a outro decisor, cujo compromisso entre erro e rejeição foi
formulado por Chow (1970) e é hoje reportado como par entre cobertura e
risco (EL-YANIV; WIENER, 2010). Em fluxo humano–IA, esse par delimita quanto
do volume se decide automaticamente.

**2.4 Custo computacional e delimitação de escopo**

A eficiência computacional deve ser reportada e valorizada na avaliação de
modelos, não apenas a acurácia (SCHWARTZ *et al.*, 2020; TREVISO *et al.*,
2023). Em instituição pública o critério é decisório, pois um modelo que
treina em segundos é reexecutado e auditado sem infraestrutura dedicada. É
por ele que os modelos de linguagem de grande porte, embora dispensem ajuste
supervisionado ao inferir a tarefa do próprio enunciado (BROWN *et al.*,
2020), ficam fora desta comparação: exigem aceleradores dedicados ou
serviços tarifados por uso, deslocam as descrições dos chamados para fora do
domínio da universidade e variam entre versões do serviço, o que compromete
a reprodutibilidade exigida pelo delineamento (BENDER *et al.*, 2021). O
protocolo integral não foi executado sobre essas arquiteturas nem sobre o
BERTimbau, cujo custo medido é tratado na Subseção 4.3, de sorte que nada se
afirma sobre seu desempenho relativo.

**3. MÉTODO**

**3.1 Delineamento, corpus e referência revisada**

O estudo adota delineamento experimental aplicado sobre base observacional
retrospectiva de chamados de manutenção predial do sistema GLPI institucional
da UFSB, universidade pública multicampi do sul da Bahia (MORAIS; PAULA;
REIS, 2023). A unidade de análise é o chamado individual, representado pelo
título e pela descrição do chamado e pelo título e pela descrição da ordem de
serviço, aos quais se associa a categoria histórica registrada no sistema. O
corpus congelado reúne 14.060 chamados de texto não vazio em 50 categorias
históricas, cuja distribuição consta do Apêndice A, e corresponde a um corte
único de extração sobre o qual os artefatos foram materializados e
versionados. O idioma é o português brasileiro, com jargão técnico,
abreviações locais e descrições incompletas (SUNDARAM; ZEID, 2025). O corte
não preserva a data de abertura do chamado, restrição tratada na Subseção
5.3. A Figura 1 apresenta o fluxo metodológico como *pipeline* de governança
preditiva, no qual a revisão humana precede o treinamento, pois dela sai o
rótulo com que os modelos são treinados e contra o qual são avaliados.

![Pipeline de governança preditiva, do fluxo de extração da base à retroalimentação por auditoria de rótulo.](04_artigo/figuras/fig_pipeline_governanca.pdf){width=95%}

A revisão humana é auditoria administrativa de rótulo, e não anotação
independente: a pergunta submetida ao especialista é se a categoria já
registrada é adequada ao chamado. Para cada registro, o
avaliador examinou os quatro campos textuais e a categoria histórica, sem
acesso a previsões ou níveis de confiança dos modelos; confirmada a
categoria, ela permanece como referência, e rejeitada, o avaliador registra
outra da mesma taxonomia. A revisão cobriu todo o corpus, com 13.462 manutenções da categoria histórica
e 598 substituições, taxa de alteração de 4,25%. Manter a categoria é confirmação administrativa, e não concordância
entre avaliadores nem correção factual. Havendo uma única decisão por
registro, não há segunda avaliação, cegamento nem adjudicação, e nenhuma
medida de confiabilidade entre avaliadores é reportada; a ancoragem e as
demais restrições constam da Subseção 5.3.

Uma análise de consistência interna pode ser realizada sem segundo avaliador,
mas não substitui avaliação independente nem permite estimar concordância
interavaliadores. O procedimento localiza os grupos de texto normalizado
idêntico que receberam mais de uma categoria de referência e classifica cada
um conforme as categorias em disputa pertençam ou não ao mesmo tipo de
manutenção; os grupos assim identificados sinalizam ambiguidade de contexto
não textual ou inconsistência interna, origens que só o reexame caso a caso
separaria. A contagem consta da Subseção 4.6.

**3.2 Pré-processamento e representação**

A normalização altera a matriz de atributos e, com ela, o desempenho dos
modelos (SALTON; BUCKLEY, 1988), e por isso é descrita de modo verificável.
Os quatro campos são localizados por cabeçalho, despojados de espaços nas
extremidades e concatenados por quebra de linha na ordem título do chamado,
descrição do chamado, título da ordem de serviço e descrição da ordem de
serviço; campos vazios são descartados da concatenação, e não substituídos
por marcador. Para o agrupamento, cada campo é normalizado separadamente por
decomposição Unicode com remoção de diacríticos, caixa baixa e colapso de
espaços, e o identificador do grupo é o resumo SHA-256 da serialização dos
quatro campos normalizados mantidos separados, e não do texto concatenado, o
que evita colidir registros que só coincidiriam após a junção.

A representação dos classificadores clássicos é TF-IDF com remoção de
acentos, caixa baixa, *n-gramas* de uma e duas palavras, frequência
documental mínima de uma ocorrência e limite superior de 30.000 atributos. A
LSTM emprega tokenização própria, com vocabulário de 8.000 termos, marcador
explícito para termo fora do vocabulário e comprimento máximo de 120
*tokens*, com preenchimento e truncamento à direita. Vetorizador, tokenizador
e vocabulário são ajustados dentro de cada dobra, sobre a partição de treino.
A etapa não elimina termos técnicos, códigos de ambientes ou nomes de
equipamentos, pois palavras como *bomba*, *split* e *infiltração* são âncoras
semânticas de categorias específicas.

**3.3 Modelos e configuração experimental**

Sete modelos em três famílias compõem a comparação principal, escolhidas
pelas características do domínio: texto curto, vocabulário técnico e forte
desbalanceamento. Fronteiras lineares separam bem as classes
sobre representação esparsa quando o vocabulário carrega poder discriminativo
(JOACHIMS, 1998; SALTON; BUCKLEY, 1988); os *ensembles* de árvores capturam
interações não lineares a custo maior; o Naive Bayes assume independência
condicional entre atributos dada a classe, suposição violada quando termos
técnicos co-ocorrem dentro de uma mesma categoria (PEDREGOSA *et al.*, 2011);
e a LSTM treina seus *embeddings* do zero (GRAVES; SCHMIDHUBER, 2005),
concentrando nessa camada cerca de 1,02 milhão de parâmetros, ordem de
grandeza próxima dos 11.178 exemplos de cada partição de treino. A Tabela 1 resume representação, configuração e papel de cada modelo;
os hiperparâmetros não declarados permanecem nos padrões da biblioteca e
estão versionados no repositório, com o ambiente de execução.

**Tabela 1** Configuração experimental dos sete modelos, que compartilham
partições, rótulo de treino e denominador (n = 13.972; 41 categorias).

| Modelo | Representação | Hiperparâmetros essenciais | Balanceamento | Saída de confiança | Papel |
|---|---|---|---|---|---|
| Naive Bayes | TF-IDF | suavização $\alpha$ = 1 | nenhum | probabilidade máxima | *baseline* probabilístico |
| Regressão Logística | TF-IDF | até 1.000 iterações | pesos balanceados | probabilidade máxima | linear probabilístico |
| LinearSVC | TF-IDF | margem máxima, *C* = 1 | pesos balanceados | *softmax* da margem | linear de margem máxima |
| SGD | TF-IDF | perda logarítmica | pesos balanceados | probabilidade máxima | linear incremental |
| Random Forest | TF-IDF | 200 árvores | pesos balanceados | probabilidade máxima | *ensemble* agregado |
| Extra Trees | TF-IDF | 200 árvores, cortes aleatórios | pesos balanceados | probabilidade máxima | *ensemble* aleatorizado |
| LSTM Bidirecional | tokenização própria | *embedding* de 128, 64 unidades, *dropout* 0,5, densa de 64, lote de 128 | pesos balanceados | *softmax* | rede neural sequencial |

Um oitavo modelo, o BERTimbau-Base (DEVLIN *et al.*, 2019; SOUZA; NOGUEIRA;
LOTUFO, 2020), é experimento exploratório fora da comparação principal: foi
ajustado sob protocolo distinto, com subamostragem estratificada e parada
antecipada, sem predições *out-of-fold* sobre todo o corpus. A medição de
custo que fundamenta a separação consta da Subseção 4.3; nada se afirma sobre
seu desempenho relativo.

**3.4 Validação, calibração e inferência**

A avaliação usa predições *out-of-fold* com `StratifiedGroupKFold`, cinco
dobras, embaralhamento e semente fixa, estratificação pela referência
revisada e agrupamento pelo hash do texto normalizado da Subseção 3.2, de
modo que nenhum grupo atravessa a fronteira entre treino e teste. As
partições são geradas uma única vez, versionadas e reutilizadas por todos os
modelos e pela camada de regras, o que legitima os testes pareados (SOKOLOVA;
LAPALME, 2009), e foram preferidas a conjunto de teste fixo pela menor
variância das estimativas em bases desbalanceadas (KOHAVI, 1995). A
separação é textual, e não cronológica: as métricas medem generalização para
grupos de texto não vistos dentro do mesmo corte de extração, e não
desempenho sobre chamados posteriores.

O agrupamento impõe custo de cobertura: uma categoria só entra na avaliação
se tiver grupos textuais distintos em número suficiente para as cinco dobras. Nove das 50 categorias não satisfazem essa
condição, quatro por aritmética e cinco por ausência efetiva em alguma dobra
após a estratificação; somam 88 linhas, ou 0,63% da base congelada, e sua exclusão reduz o
denominador das métricas de 14.060 para 13.972 registros em 41 categorias;
as nove excluídas, de menor frequência, constam da Tabela A3. As
alternativas examinadas, com o efeito de cada convenção de denominador,
constam da Subseção 4.9 e do material suplementar.

A unidade da inferência é o grupo textual, e não o chamado. Das 14.060
linhas, 4.586, ou 32,62%, compartilham texto normalizado com outra; a base
congelada resolve-se em 9.786 grupos, 9.474 deles unitários, e 9.735
sobrevivem ao recorte das 13.972 linhas avaliadas, ao passo que o mapa
recalculado sobre o texto vivo registra 9.734, por edição posterior ao
congelamento. Registros de texto idêntico recebem a mesma
predição de qualquer classificador e não são evidências independentes;
tratá-los como tal estreita artificialmente intervalos e valores de *p*
(COCHRAN, 1977).

As métricas são assim definidas. A acurácia é a proporção de registros cuja
predição coincide com a referência revisada, e o *macro*-F1, a média
aritmética simples do F1 por categoria, que pondera igualmente classes de
qualquer suporte (SOKOLOVA; LAPALME, 2009). O erro de calibração esperado
(ECE) é a média, ponderada pelo número de registros, do módulo da diferença
entre acurácia e confiança média em dez faixas de largura igual, e o escore de
Brier, na formulação binária de acerto ou erro, pune má calibração e baixa
resolução. A cobertura é a fração de registros cuja confiança calibrada
atinge o limiar, a acurácia seletiva restringe a acurácia a eles, e o
complemento da cobertura é a taxa de encaminhamento humano. O ganho líquido é
a diferença entre corrigidos e prejudicados onde a predição diverge do
histórico, qualificado pela utilidade da Subseção 4.5.

A calibração e a escolha do limiar seguem desenho de dobra interna. Para cada
dobra externa, uma dobra interna é escolhida deterministicamente entre as
demais; o modelo é treinado nas três restantes e prediz a interna, e os pares
de escore e acerto assim obtidos ajustam a regressão isotônica e fixam o
limiar como o menor escore que atinge o alvo de acurácia. Calibrador e limiar
são então aplicados aos escores *out-of-fold* da dobra externa, sobre a qual
recai a avaliação. Transformações, tokenizadores, vocabulários, calibradores
e limiares são, sem exceção, ajustados sem acesso à dobra externa.

A hipótese global de igualdade das taxas de acerto é apurada pela estatística
Q de Cochran (COCHRAN, 1950), com a distribuição qui-quadrado tabelada
substituída por referência empírica obtida por permutação do rótulo de modelo
dentro de cada grupo, o que preserva a dependência interna (GOOD, 2005;
ANDERSON; TER BRAAK, 2003). Rejeitada a igualdade, os 21 pares são comparados
por permutação pareada com troca de sinal da diferença de acertos por grupo,
com correção sequencial de Holm-Bonferroni (HOLM, 1979), e os intervalos das
métricas e das diferenças vêm de *bootstrap* de conglomerados, que sorteia
grupos com reposição e reconstrói a amostra com todos os registros de cada
grupo sorteado (EFRON, 1979; EFRON; TIBSHIRANI, 1993; DICICCIO; EFRON, 1996;
FIELD; WELSH, 2007; CAMERON; GELBACH; MILLER, 2008). A divisão aleatória por
linha permanece apenas como análise de sensibilidade, no material
suplementar.

**3.5 Reclassificação, utilidade e análises complementares**

Quatro análises complementam a comparação principal, sobre as mesmas
partições e os mesmos registros, sem alterar a referência revisada. A
reclassificação da base histórica conta apenas os registros em que a predição
diverge da categoria histórica, com a referência arbitrando cada divergência,
e é qualificada pela utilidade sob custos assimétricos da Subseção 4.5. A camada explícita de regras de periodicidade, em módulo próprio e auditável,
tem desenho e termos na Subseção 4.12. A camada informacional de
entropia de Shannon e divergência de Jensen-Shannon (SHANNON, 1948; LIN,
1991) é calculada sobre agregados sanitizados e mede dispersão das predições,
distância frente à distribuição histórica e desacordo entre modelos, este
último usado para ordenar fila de auditoria; nada se afirma, a partir dela,
sobre desordem do sistema físico. O teste de sensibilidade da cobertura sob
três convenções de denominador consta da Subseção 4.9.

**3.6 Reprodutibilidade, dados e aspectos institucionais**

A rodada canônica foi executada em ambiente Linux de 64 bits, sobre executor hospedado
de quatro processadores sem acelerador gráfico, com Python 3.11.15,
NumPy 1.26.4, scikit-learn 1.5.2 e TensorFlow 2.17.0. A semente 42 foi
aplicada ao embaralhamento das partições e aos componentes do scikit-learn
que recebem `random_state`. A execução canônica da LSTM não fixou
explicitamente a semente global do TensorFlow, de sorte que a reprodução
exata dos pesos e da trajetória de treinamento não é garantida, embora
partições, rótulos e protocolo o sejam. O treino percorre no máximo quinze
épocas, com separação interna de 10% para validação, e é interrompido pelo
monitoramento da perda de validação, com paciência de três épocas e
restauração dos pesos da melhor época, registrada no artefato de cada
execução. Os tempos da Subseção 4.7 são expressos em segundos, como mediana
de três repetições de treino único sobre a base completa, e não como soma das
cinco dobras. Matriz de proveniência versionada associa cada número, tabela e
figura a script, entrada, denominador, taxonomia, partições e resumo
criptográfico do corpus.

Os chamados analisados são registros administrativos da rotina de atendimento
da instituição. A base de trabalho não é publicamente disponível, por
restrição de privacidade institucional, e os campos textuais permanecem
restritos ao ambiente do pesquisador. Os artefatos publicados são sanitizados
na origem, pois nenhum identificador pessoal, identificador de chamado em
texto claro, título ou descrição livre é gravado nos agregados versionados, e
os mapas por registro usam o resumo SHA-256 do identificador, o que preserva
a junção entre etapas sem expor o dado, em atenção ao princípio da
necessidade previsto na Lei Geral de Proteção de Dados Pessoais (BRASIL,
2018).

O repositório não guarda documento de autorização institucional formal, de
aprovação por comitê de ética ou de dispensa de apreciação ética, e nada é
aqui afirmado a esse respeito; o acesso à base decorre da atuação do primeiro
autor na gestão da manutenção predial da instituição, e a formalização
documental é providência recomendada antes da submissão. As métricas
derivadas e o código que produz cada figura, tabela e estatística são
públicos em https://github.com/adinailson88/classificacao-chamados, que
também descreve a estrutura dos dados e o material suplementar aqui citado.

**4. RESULTADOS**

Esta seção segrega deliberadamente dois conjuntos de resultados: a
concordância dos sete modelos com a categoria histórica, em que o registro
administrativo opera como referência preliminar (Subseção 4.1), e o
desempenho desses mesmos modelos contra a referência humana revisada
(Subseção 4.2). Dois denominadores convivem no texto e não devem ser
confundidos: a base congelada contém 14.060 chamados, todos com referência
humana, e é o número pertinente sempre que a frase trata do corpus ou da
cobertura da revisão, ao passo que as métricas são apuradas sobre as
13.972 linhas em 41 categorias que compõem as partições (Subseção 3.4;
Tabela A3).

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
*et al.*, 2013). O coeficiente é aplicável aqui porque modelo e categoria
histórica são fontes independentes de classificação, o que não vale entre
a referência revisada e o histórico (Subseção 3.1).

**Tabela 2** Concordância com a categoria histórica por modelo (n = 13.972).

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
concentra-se nas classes de maior volume: as de maior F1 pertencem todas
à Manutenção Preventiva, com Ar condicionado split em 0,9972 sobre
suporte de 1.987, ao passo que Projeto e Manutenção Preventiva sem
subcategoria hidráulica não alcançam acerto algum, sobre suporte entre 13
e 65 registros, condição em que pequena variação absoluta altera
fortemente a métrica. O desempenho por categoria, com suporte, tipo e
classe de volume, consta da Tabela A2.

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
sobre o SGD, segundo colocado, é de 1,60 ponto percentual, com 536 linhas
de acerto exclusivo do LinearSVC contra 312 do SGD; a inferência que a
sustenta, conduzida no nível do grupo textual, consta da Subseção 4.9.

A cobertura integral da revisão elimina o viés de seleção: a acurácia
relatada não constitui limite superior de amostra conferida, e as ressalvas
remanescentes, de outra natureza, estão declaradas na Subseção 5.3.

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

**Tabela 3** Acurácia e F1 macro por modelo contra a referência humana
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
avaliado sob o protocolo agrupado desta rodada e nada se afirma aqui sobre
seu desempenho relativo; uma comparação integral exigiria aceleração por
unidade de processamento gráfico e permanece como trabalho futuro. Um
experimento exploratório avaliou o transformador em lote de mil chamados,
dos quais 983 com referência humana, e seus valores constam do material
suplementar. Eles não são comparáveis aos das Tabelas 2 e 3, pois o lote
corresponde aos primeiros registros elegíveis, não é probabilístico, não
cobre o corpus, e o ajuste empregou subamostragem estratificada com parada
antecipada.

```{=latex}
\FloatBarrier
```

**4.4 Calibração e automação seletiva por confiança**

A confiança bruta dos classificadores não é probabilidade e não pode
sustentar decisão operacional sem tratamento. O erro de calibração
esperado (ECE) do LinearSVC alcança 0,6925 sobre o escore bruto, porque a
transformação da margem por função *softmax* produz valores que não
correspondem a frequências de acerto; a calibração isotônica, ajustada em
dobra interna, reduz esse valor a 0,0178 e o escore de Brier de 0,6052
para 0,1034. O procedimento reduz o ECE de cinco dos sete modelos, com
melhor resultado no Extra Trees, em 0,0108. O Naive Bayes e o LSTM são
exceção e pioram levemente, consequência esperada de ajustar um calibrador
sobre amostra menor quando a confiança original já era adequada.

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

**Tabela 4** Calibração e automação seletiva por modelo (n = 13.972). O
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
(Tabela 5). O procedimento é direto: conta-se apenas onde a predição
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
base.

O ganho líquido, contudo, pressupõe que corrigir um registro e estragar
outro valham o mesmo, e que revisar não custe nada. Nenhuma das duas
hipóteses é neutra em gestão pública, e ambas estavam implícitas na
subtração. A qualificação decisória adota, por isso, a função de utilidade
*U* = *b* × corrigidos − *c* × prejudicados − *r* × revisados, normalizada
pelo benefício da correção, o que dispensa atribuir valor monetário e
reduz o problema a duas razões adimensionais: $\rho$ = *c*/*b*, o custo do
prejuízo em unidades de benefício da correção, e $\lambda$ = *r*/*b*, o custo da
revisão humana na mesma unidade. O ganho líquido simples é o caso
particular $\rho$ = 1 e $\lambda$ = 0, e permanece o resultado principal por ser
transparente.

Sob aplicação direta, em que o modelo reescreve a categoria sempre que
diverge, a utilidade só é positiva se $\rho$ ficar abaixo da razão de
equilíbrio corrigidos/prejudicados, que vale 0,2047 no LinearSVC e cai a
0,0817 no Naive Bayes. A reclassificação exigiria, portanto, que estragar
um registro custasse menos de um quinto do que vale corrigir outro,
condição que a natureza do dano não sustenta: o registro corrompido
propaga para a série temporal da categoria e para a alocação de recurso
que dela deriva (Subseção 5.4), ao passo que a correção apenas recupera o
valor que o registro já deveria ter. Em toda a faixa examinada, de $\rho$ = 0,25
a $\rho$ = 4, a utilidade é negativa nos sete modelos, de modo que o veredito
não depende da hipótese de custos iguais.

A mesma predição sustenta, entretanto, uma política diferente. Se a
divergência não reescreve o rótulo e apenas enfileira o chamado para
revisão humana, não há prejudicados por construção, e o benefício é o
número de registros da fila cujo histórico de fato estava errado: 18,53%
no LinearSVC, contra a taxa de alteração de 4,25% na base congelada, o que
faz da divergência um critério de priorização com enriquecimento de cerca
de quatro vezes sobre a revisão aleatória. Os dois denominadores diferem
em 88 linhas e não devem ser fundidos, mas a ordem de grandeza não depende
disso. O limite de equilíbrio de $\lambda$ coincide com essa precisão: a triagem
paga enquanto revisar um chamado custar menos de 18,5% do que vale
corrigir um registro, valor que supõe a revisão devolvendo a referência,
verdadeiro por construção, e é portanto teto da política. A consequência
operacional é discutida na Subseção 5.2, e os valores por modelo constam
do material suplementar.

**Tabela 5** Ganho líquido de reclassificação por modelo, contado apenas
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
de fora pelo motivo exposto na Subseção 4.3. Dispersão de predições e
aderência distributiva ao histórico não caminham juntas neste corpus: o
LSTM apresenta a maior diversidade de categorias previstas, com entropia
normalizada de 0,8362, ao passo que o LinearSVC, de melhor acurácia, é o
de distribuição mais próxima da base, com divergência de Jensen-Shannon de
0,0055.

No nível de chamado individual, os sete modelos são unânimes em 8.444 dos
13.972 registros, ou 60,44%, e 2.285 registros, ou 16,35%, distribuem os
votos por três ou mais categorias distintas. Esse segundo conjunto
caracteriza desacordo estrutural entre arquiteturas, em que a divergência
deixa de ser escolha entre duas alternativas e passa a indicar ausência de
sinal textual suficiente, e constitui critério de priorização de auditoria
complementar à baixa confiança de um único modelo.

A auditoria dos grupos de texto idêntico descrita na Subseção 3.1 localiza
a ambiguidade no próprio dado, e não na predição. Entre esses grupos, 17
receberam mais de uma categoria de referência, afetando 85 linhas, ou 0,61%
das linhas avaliadas; em 14 deles, somando 74 linhas, as categorias em
disputa pertencem a tipos distintos de manutenção, e o par mais frequente
opõe Hidrossanitária > Hidráulica a Manutenção Preventiva > Reservatório,
com 11 grupos e 65 linhas. Textos idênticos podem, portanto, corresponder a
intervenções de naturezas diferentes, distinção irrecuperável por qualquer
classificador textual. A contagem sinaliza ambiguidade ou inconsistência
interna, mas não fixa teto quantitativo de desempenho: esse teto exigiria
calcular a distribuição dos rótulos dentro de cada grupo, o que não foi
feito, e tampouco se trata de piso de erro de anotação.

No nível de categoria, o contraste é acentuado entre as 33 categorias com
suporte mínimo de trinta registros. A Figura 3 contrasta as dez de maior e
as dez de menor F1 do LinearSVC: nas dez melhores, o F1 varia de 0,9139 a
0,9972 sobre 6.271 chamados; nas dez piores, cai à faixa de 0,2162 a
0,6288 sobre 2.403 chamados, porte comparável em ordem de grandeza, de
modo que a diferença não decorre de escassez de exemplos.

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

A fronteira entre climatização corretiva e preventiva, que descreve o
mesmo equipamento sob naturezas distintas de intervenção, não figura entre
as maiores confusões: a ambiguidade que resta é a de escopo entre sistemas
prediais, não a de natureza do serviço, resultado coerente com a
facilidade da tarefa de tipo reportada na Subseção 4.11.

![Recorte da matriz de confusão sobre as oito categorias mais envolvidas em troca recíproca, com contagens agregadas entre modelos.](04_artigo/figuras/fig_matriz_confusao.pdf)

Esses recortes sustentam a mesma conclusão operacional. Quando a queda de
desempenho se concentra em fronteiras taxonômicas específicas, e não de
modo difuso, a resposta adequada não é substituir o classificador, mas
revisar a taxonomia, decisão que permanece humana e para a qual a camada
de Shannon oferece apenas a priorização estatística. O Naive Bayes
sintetiza o diagnóstico ao combinar a menor cobertura de categorias,
apenas 22 contra 39 a 41 dos demais modelos, com a menor entropia
normalizada e a maior divergência frente ao histórico, o que explica seu
F1 macro de 0,2951 apesar de acurácia próxima de 0,71. O ordenamento
completo dos quinze pares de maior confusão recíproca consta do material
suplementar.

```{=latex}
\FloatBarrier
```

**4.7 Custo computacional**

O custo de treino e de inferência foi medido para os sete modelos sobre a
base completa, no mesmo ambiente computacional, um processador de quatro
núcleos sem acelerador gráfico, com mediana de três execuções por modelo.
O desenho é o de treino único sobre a base inteira, e não a soma das cinco
dobras, de modo que os valores medem o custo de colocar cada modelo em
operação; os tempos absolutos variam conforme a máquina, mas as razões
entre modelos permanecem estáveis e constituem o dado relevante para a
decisão de adoção.

Os modelos lineares treinam em poucos segundos, de 1,12 s no Naive Bayes a
8,43 s na Regressão Logística, os *ensembles* de árvores exigem entre
vinte e trinta segundos, e a rede neural LSTM consome 83,44 s, cerca de 34
vezes o tempo do LinearSVC. A faixa entre a execução mais rápida e a mais
lenta é estreita em todos os modelos, com exceção do LSTM, o que permite
distinguir diferença real de ruído do executor. O BERTimbau não figura na
tabela por estar em outra ordem de grandeza, com 6,44 horas por dobra
(Subseção 4.3), e por não corresponder a treino único sobre a base
inteira.

**Tabela 6** Custo computacional por modelo sobre a base completa
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

A Figura 5 cruza essas medições de custo com a acurácia da Tabela 3 e
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

A Figura 6 mostra a curva de aprendizado do LSTM. O treino parou por
interrupção antecipada após 11 épocas, com menor perda de validação na
época 8 e maior acurácia de validação na época 10 (0,6722). O padrão
indica saturação precoce, consistente com a hipótese de que *embeddings*
treinados do zero são insuficientes para um corpus deste porte (Subseção
3.3). A curva provém de um treino único sobre a base inteira, com
validação interna de 10%, e descreve a dinâmica de convergência da
arquitetura, não o desempenho reportado na Tabela 3, que é a união das
predições *out-of-fold* das cinco dobras.

![Curva de aprendizado do LSTM por época, perda e acurácia em treino e validação.](04_artigo/figuras/fig_curva_aprendizado_lstm.pdf){width=95%}

A justificativa do particionamento agrupado é anterior a qualquer medição
de desempenho e repousa na estrutura do corpus (Subseção 3.4): a partição
por linha permitiria ao mesmo texto ocupar treino e teste, e duas
estimativas da magnitude do efeito indicam ganho espúrio entre 0,89 e 1,84
ponto percentual de acurácia. Elas constam do material suplementar com o
protocolo declarado e não são comparáveis às Tabelas 2 e 3, por terem
outra base, outro denominador e outro rótulo de treino, assim como o
estudo de sensibilidade a unidades recorrentes e *dropout*, que separa as
quatro variantes por menos de quatro pontos percentuais.

**4.9 Inferência sob dependência textual**

A dependência entre registros de texto idêntico não é detalhe de
implementação: ela determina quanta informação a amostra de fato contém.
As 13.972 linhas avaliadas distribuem-se por 9.735 grupos textuais
congelados, e 4.546 delas, ou 32,54%, pertencem a grupos com mais de um
membro. O efeito de desenho, razão entre a variância da acurácia sob
reamostragem de conglomerados e a variância binomial que a suposição de
independência produziria (COCHRAN, 1977), fica entre 4,47 no LinearSVC e
8,83 no Naive Bayes. Em erro padrão, isso significa que a precisão
declarada por linha era de 2,1 a 3,0 vezes maior do que a amostra
sustenta: para o LinearSVC, 0,0032 contra 0,0068. Toda inferência desta
subseção adota, por isso, o grupo como unidade.

O teste global rejeita a igualdade entre os sete modelos. A estatística Q
de Cochran vale 2.661,04 sobre seis graus de liberdade, e sua
significância é apurada contra distribuição empírica de duas mil
permutações do rótulo de modelo dentro de cada grupo, o que preserva a
dependência interna: nenhuma permutação alcançou o valor observado, de
modo que *p* < 0,0005. Só então os 21 pares foram comparados, por
permutação pareada com troca de sinal da diferença de acertos por grupo,
com dez mil permutações e correção de Holm sobre a família. Sem o teste
global, 21 comparações constituiriam pesca de significância.

A Tabela 7 apresenta as seis comparações do LinearSVC, que é o modelo
líder, contra cada um dos demais. O LinearSVC supera os seis com
significância, e a leitura por grupos qualifica a magnitude: contra o
SGD, a vantagem de 1,60 ponto percentual corresponde a 533 grupos
favoráveis ao LinearSVC contra 308 ao SGD, com 8.894 grupos empatados.
Vantagem estatisticamente estabelecida e vantagem prática são, portanto,
coisas distintas, e nove de cada dez grupos não distinguem os dois
modelos. O *d* pareado por grupo, que padroniza a diferença média pelo
desvio das diferenças, fica entre 0,07 e 0,31, faixa de efeito pequeno.

**Tabela 7** Comparações pareadas do LinearSVC contra os demais modelos,
com o grupo textual como unidade (13.972 linhas em 9.735 grupos). A
diferença de acurácia é a estimativa observada; o intervalo vem de
*bootstrap* de conglomerados com duas mil reamostragens; o valor de *p*
vem de permutação pareada com dez mil repetições e correção de Holm sobre
os 21 pares. Nenhuma permutação alcançou a diferença observada nestes seis
pares, de modo que os valores de *p* são limites superiores impostos pelo
número de repetições, e não estimativas pontuais. Os 15 pares restantes
constam do material suplementar.

| Comparação | Δ acurácia (p.p.) | IC95% da diferença | Grupos a favor | Grupos contra | Empates | *d* pareado | *p* ajustado |
|---|---:|---|---:|---:|---:|---:|---:|
| × SGD | 1,60 | 0,0118 -- 0,0204 | 533 | 308 | 8.894 | 0,077 | $\leq$ 0,0021 |
| × Extra Trees | 1,80 | 0,0130 -- 0,0232 | 759 | 515 | 8.461 | 0,071 | $\leq$ 0,0021 |
| × Regressão Logística | 2,03 | 0,0156 -- 0,0248 | 598 | 314 | 8.823 | 0,094 | $\leq$ 0,0021 |
| × Random Forest | 2,83 | 0,0229 -- 0,0341 | 896 | 503 | 8.336 | 0,108 | $\leq$ 0,0021 |
| × LSTM | 9,66 | 0,0875 -- 0,1061 | 1.682 | 349 | 7.704 | 0,313 | $\leq$ 0,0021 |
| × Naive Bayes | 11,65 | 0,1028 -- 0,1329 | 1.961 | 549 | 7.225 | 0,164 | $\leq$ 0,0021 |

Dos 21 pares, 19 são significativos após a correção e 2 não são: Extra
Trees contra Regressão Logística e Extra Trees contra SGD, ambos com *p*
ajustado de 0,842 e intervalo da diferença contendo o zero. Esses dois
pares devem ser lidos como empate dentro do poder do teste, e não como
ordenação, o que é coerente com a sobreposição dos intervalos de F1 macro
apontada na Subseção 4.2.

Cabe registrar o alcance da correção de unidade. Nenhum dos 21 vereditos
muda ao passar da linha para o grupo: repetida a família de comparações
por McNemar sobre linhas (MCNEMAR, 1947), os mesmos 19 pares permanecem
significativos e os mesmos 2 permanecem empatados. O que muda é a
magnitude do valor de *p*, e a diferença é de ordens de grandeza em
vários pares. A conclusão substantiva do artigo, portanto, não dependia
da suposição incorreta, mas a precisão anteriormente declarada dependia,
e a permanência do veredito é resultado da análise, não sua premissa.

A cauda de categorias raras impõe uma segunda qualificação, agora sobre a
composição da métrica e não sobre a incerteza. O *macro*-F1 de 0,6684 do
LinearSVC é média sobre as 41 categorias avaliadas. Projetado sobre as 50
categorias da taxonomia, com F1 igual a zero nas nove ausentes das
partições, ele cai a 0,5481, valor que é o limite inferior honesto, pois
nenhum modelo prevê categoria que não esteve no treino. Agregado às 14
famílias do primeiro nível da taxonomia, sobe a 0,6816, e nessa
granularidade o LinearSVC assume também a liderança do *macro*-F1, que na
leitura por categoria pertencia à Regressão Logística por três milésimos.
A ordenação dos modelos é estável nas três convenções, à exceção dessa
troca de posição no topo. Os valores por modelo constam do material
suplementar.

**4.10 Duplicação taxonômica e recomendação de governança**

A acurácia dos sete modelos varia entre 0,7088 e 0,8253, faixa de 12
pontos percentuais, ao passo que o F1 macro varia de 0,2951 a 0,6689,
faixa de 37 pontos: os modelos se diferenciam sobretudo no tratamento das
categorias de baixa frequência, e o padrão de fronteira da Subseção 4.6
reaparece no LinearSVC isoladamente, o que caracteriza o desequilíbrio
como propriedade da taxonomia e não de um indutor particular.

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

Depreende-se daí uma recomendação de governança anterior à escolha do
modelo. Antes de perseguir ganho de acurácia por meio de arquiteturas mais
custosas, convém revisar a taxonomia institucional, unificando os pares
que nomeiam o mesmo objeto e explicitando o critério de natureza da
manutenção no formulário de abertura do chamado. Essa intervenção atua
sobre a origem do erro, enquanto a substituição do classificador atua
apenas sobre seu efeito.

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
entre acurácia e F1 macro decorre da composição da métrica, e não de falha
generalizada do classificador: o LinearSVC alcança 0,8207 na classe A e
0,5018 na classe C, de modo que o valor agregado de 0,6684 é média entre
dois regimes distintos. A ordenação dos modelos permanece estável nas três
classes, e o Naive Bayes é o único cujo colapso alcança a classe B, com
0,2527, ao passo que os demais preservam desempenho superior a 0,63 nas
duas primeiras. Os valores por modelo e classe constam do material
suplementar.

O segundo recorte separa os chamados pela natureza da intervenção, em três
tipos e não na dicotomia usual entre preventivo e corretivo, porque a
taxonomia institucional abriga famílias que não descrevem serviço de
manutenção: o registro indevido de chamado, a contratação de posto de
trabalho, o fornecimento de materiais e a execução de reformas. Elas somam
585 chamados, ou 4,19% das linhas avaliadas, e sua atribuição
indiscriminada à manutenção corretiva elevaria o denominador desta em
cerca de 7% relativos, com efeito direto sobre qualquer razão calculada
entre as duas naturezas. Sob o critério adotado, a preventiva responde por
4.902 chamados (35,09%) e a corretiva por 8.485 (60,73%).

A projeção da referência revisada e das predições para o nível de tipo
eleva o desempenho a outro patamar. O LinearSVC alcança 0,9443 de acurácia
nessa granularidade, contra 0,8253 na tarefa de 41 categorias, com F1 de
0,9742 na preventiva e de 0,9547 na corretiva, de modo que a distinção
apontada na Subseção 4.10 como origem taxonômica de parte do erro
resolve-se com folga no nível em que a decisão de gestão ocorre. Toda a
perda concentra-se no terceiro tipo, cujo F1 não ultrapassa 0,5330 em
nenhum modelo e recua a 0,2684 no Naive Bayes, coerente com categorias
cuja atribuição depende de juízo administrativo sobre a pertinência do
chamado, e não de sua descrição técnica. Cabe registrar a inversão de
ordenação nessa granularidade: o Extra Trees lidera a acurácia, com
0,9497, e o LinearSVC lidera o F1 macro, com 0,8180, precisamente por ir
melhor na classe difícil, o que faz a escolha do classificador depender
tanto do nível de agregação da decisão quanto da métrica que ela
privilegia.

A curva ABC recalculada dentro de cada tipo delimita o conjunto mínimo de
categorias que sustenta cada leitura: quatro categorias preventivas cobrem
83,46% do tipo com F1 macro de 0,9727, sete corretivas cobrem 81,76% com
0,7835, e as quatro de não manutenção que cobrem 89,06% alcançam apenas
0,5184, o que confirma a dificuldade como propriedade do tipo, e não da
cauda de baixa frequência. O detalhamento consta do material suplementar.

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

O número que explica o padrão é o de conflitos: como a regra depende
apenas do texto, ela dispara no mesmo conjunto de registros para os sete
modelos, e o que varia é a predição que ela substitui. No LinearSVC, os
4.487 disparos produzem apenas 31 divergências; no Naive Bayes, produzem
219, com a regra acertando 201 contra 9 do modelo.

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
exige nova revisão. A taxa é baixa por duas causas que a Subseção 3.1
discrimina sem que o desenho permita separá-las, o rótulo produzido sob
verificação de equipe técnica e a ancoragem do procedimento de auditoria;
seja qual for a proporção entre elas, o que os modelos acompanham não é um
rótulo ingênuo, e é essa estabilidade da linha de base que torna negativo
o ganho de reclassificação discutido na Subseção 5.2.

O BERTimbau não integra essa comparação por motivo computacional medido
(Subseção 4.3), e nada se afirma aqui sobre sua qualidade relativa, pois
rankings produzidos sob protocolos distintos não sustentam comparação
direta.

**5.2 Reclassificação, ambiguidade taxonômica e calibração**

O resultado da reclassificação (Subseção 4.5) contraria a expectativa que
motivou o estudo e tem consequência operacional direta. O ganho líquido de
corrigir chamados já classificados é negativo em todos os sete modelos, e
a magnitude do prejuízo acompanha, na ordem inversa, o desempenho de cada
um. Não se trata de nuance entre modelos, e sim de veredito sobre a
tarefa: nenhum classificador aqui avaliado é candidato a reclassificar a
base histórica em massa. A explicação é aritmética antes de ser
metodológica, pois, estreito o espaço de alteração da referência (Subseção
5.1), qualquer divergência sistemática entre modelo e histórico tende a
cair fora dele, e o melhor modelo diverge 2.849 vezes para acertar 475,
cerca de um acerto para cada cinco prejuízos. O resultado depende de a
referência cobrir todo o corpus, pois arbitrar parte das divergências pelo
próprio histórico premiaria o modelo por concordar com o rótulo que se
pretendia auditar. O veredito tampouco é artefato de contabilidade: sob a
função de utilidade da Subseção 4.5, a reclassificação direta só
compensaria se estragar um registro custasse menos de um quinto do que
vale corrigir outro, hipótese que a assimetria do dano contradiz, e é a
inversa, a de que o prejuízo custa tanto ou mais que a correção, que
descreve o caso da manutenção predial.

Disso não decorre que a classificação automática seja inútil neste
domínio, e sim que seu uso defensável é seletivo. Sobre chamados novos não
há rótulo prévio correto a ser degradado, o que retira o risco medido na
Subseção 4.5, mas não transporta para o futuro a acurácia aqui reportada:
ela foi estimada entre grupos textuais de um mesmo corte de extração, e
não ao longo do tempo (Subseção 5.3), de modo que o uso prospectivo é
recomendação condicional. Sobre a base histórica, dois encaminhamentos se
sustentam. O primeiro é a automação condicionada à confiança da Subseção
4.4, que preserva o registro nas faixas em que o modelo não tem vantagem
demonstrável sobre ele. O segundo inverte o papel da divergência: em vez
de autorizar a reescrita, ela prioriza a fila de auditoria humana, e nessa
função a
mesma predição que perde por larga margem sustenta enriquecimento de
cerca de quatro vezes sobre a revisão aleatória. A predição que não
substitui o revisor pode dirigi-lo, e essa é a leitura operacional que o
resultado negativo autoriza.

A camada de entropia de Shannon e divergência de Jensen-Shannon (Subseção
4.6) não substitui as métricas supervisionadas ou a revisão humana, mas
amplia o repertório de governança ao separar três fenômenos que a acurácia
isolada tende a confundir: o erro de modelo, a ambiguidade genuína da
taxonomia institucional e a heterogeneidade natural da distribuição de
chamados.

A calibração transforma essa leitura em procedimento operável (Subseção
4.4). Escores brutos não são probabilidade, e o ajuste isotônico em dobra
interna (PLATT, 1999; GUO *et al.*, 2017) é o que permite associar
confiança alta a acerto alto sem depender de faixas cuja escala não tem
interpretação probabilística, condição do regime seletivo discutido
acima.

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
mesmo objeto sob famílias distintas, e a divergência interna medida na
Subseção 4.6 confirma o problema no próprio dado. Nesses
pares, a atribuição depende de um critério de natureza da intervenção que
o texto do chamado nem sempre permite inferir, o que impõe teto ao
desempenho alcançável por qualquer classificador textual.

As métricas valem para as 41 categorias com suporte nas cinco dobras, e
não para a taxonomia inteira. As nove categorias excluídas são justamente
as mais raras, e o efeito é quantificado na Subseção 4.9: sobre as 50
categorias, o *macro*-F1 do melhor modelo cai de 0,6684 a 0,5481. A
cobertura de linhas permanece alta, 99,37%, mas a de categorias é de 82%,
e nenhuma afirmação deste artigo se estende às nove ausentes. A Tabela A3
torna a diferença auditável, e nenhuma das alternativas examinadas, cujo
efeito consta da mesma subseção e do material suplementar, elimina a
restrição.

Uma restrição adicional decorre do congelamento: as partições são fixadas
por um mapa versionado de grupos textuais, o que garante reprodutibilidade
mas dissocia o experimento do crescimento da base operacional, e dois
registros tiveram o texto editado depois, o que basta para explicar
diferenças de última casa decimal em execuções futuras.

A limitação mais consequente para o uso prospectivo é a ausência de
validação temporal. O corpus congelado não dispõe de data de abertura por
chamado, restrição verificada sobre o contrato de colunas da base e sobre
os artefatos da rodada canônica, de modo que treino, calibração e teste
não puderam ser separados em períodos sucessivos. Segue-se que a validação
cruzada agrupada estima generalização entre grupos textuais de um mesmo
corte de extração, e não desempenho futuro sob deriva temporal: nenhum
número deste artigo prevê o comportamento do classificador sobre chamados
posteriores, e toda recomendação de uso prospectivo é condicional.

Os mecanismos que essa lacuna deixa por medir operam na direção do
desempenho reportado. A deriva de vocabulário desloca a matriz de
atributos à medida que entram equipamentos, edificações e jargões ausentes
do treino; cada fusão, criação ou renomeação de categoria, providência
recomendada na Subseção 4.10, altera o próprio espaço de saída, incluído
aí o caso extremo da categoria nova, para a qual não há exemplo e não pode
haver predição; mudanças no formulário de abertura e na composição da
equipe de triagem alteram a distribuição do texto de entrada e do rótulo
administrativo que lhe corresponde. Implantação defensável pressupõe, por
conseguinte, monitoramento da acurácia sobre amostra auditada,
recalibração periódica dos escores, dado que o limiar da Subseção 4.4 é
solidário à distribuição de confiança observada, e retreinamento a cada
mudança de taxonomia. A avaliação em períodos sucessivos depende de
extração que preserve a data de abertura e constitui validação futura
prioritária, anterior a qualquer decisão de automação em regime.

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
modelos de série temporal por categoria. Um chamado atribuído à categoria
incorreta subtrai uma ocorrência da série de uma categoria e a acrescenta
à de outra, deslocando duas séries em sentidos opostos, e o efeito
propaga-se à estimativa de demanda e de custo e ao ordenamento de
prioridades que dela deriva, de sorte que o erro de classificação se
converte em erro de alocação de recurso. É essa a razão pela qual o acerto
contra a referência revisada opera como requisito de engenharia da camada
preditiva, e não apenas como métrica de comparação entre modelos, e
também a que dá assimetria aos custos da Subseção 4.5: corromper um
registro correto custa mais do que vale recuperar um incorreto.

O recorte da Subseção 4.11 indica em que ordem essa camada pode ser
incorporada a indicadores institucionais. A razão entre manutenção
preventiva e corretiva, que expressa a maturidade da gestão do parque
edificado, é a leitura de menor erro medido e dispensa revisão caso a
caso, desde que o erro seja reaferido periodicamente sobre amostra
auditada, uma vez que o valor medido vale para o corte avaliado; já os
indicadores desagregados por categoria exigem restrição às classes de
maior volume dentro de cada tipo, sob pena de
atribuir a frações residuais do corpus uma precisão que a medição não
sustenta. A hierarquia converte o diagnóstico de desempenho em critério de
publicação de indicador, e não apenas em ressalva metodológica.

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
o terço restante encaminhado à revisão humana. A recomendação é
condicional quanto a chamados futuros, pois o corpus congelado, desprovido
de data de abertura, não permitiu separar treino, calibração e teste no
tempo: estender o regime seletivo à operação corrente pressupõe
monitoramento do desempenho e recalibração periódica.

O achado que mais altera a orientação prática é negativo. A
reclassificação automática da base histórica produz prejuízo líquido em
todos os sete modelos, porque a revisão manteve a categoria registrada em
95,75% dos casos e o espaço de alteração é estreito demais para compensar
os erros introduzidos. O veredito não depende da hipótese de custos
iguais: sob função de utilidade explícita, a reescrita só compensaria se
estragar um registro valesse menos de um quinto do que vale corrigir
outro. A mesma divergência que não autoriza a reescrita presta-se, porém,
à priorização da auditoria humana, com enriquecimento de cerca de quatro
vezes sobre a revisão aleatória. Também é negativo, e igualmente útil, o
resultado da camada explícita de regras de periodicidade: ela é redundante
diante de um classificador estatístico competente, que já captura esses
sinais a partir do texto.

A finalização metodológica exige reconhecer o que os dados não respondem.
A referência provém de auditoria administrativa conduzida por avaliador
único, com a categoria histórica à vista e sem segunda avaliação
independente, de modo que o estudo não estima a prevalência de erro do
rótulo histórico nem a reprodutibilidade da referência por outro
especialista, e o desempenho medido não cobre as nove categorias mais
raras da taxonomia. Tampouco há validação temporal, pela ausência de data
de abertura no corpus congelado, de sorte que a estabilidade do
desempenho sob deriva de vocabulário e sob alteração da taxonomia
permanece por medir. A próxima etapa deve incorporar segunda avaliação,
com adjudicação de divergências nos pares ambíguos, submeter a própria
taxonomia a revisão e reconstituir o corte com a data de abertura
preservada, o que viabiliza avaliação em períodos sucessivos. Em paralelo,
a validação externa em outras instituições e a execução *out-of-fold*
integral do BERTimbau, viável em infraestrutura com acelerador gráfico,
poderão testar a estabilidade dos resultados sob taxonomias e volumes
distintos. A camada classificada poderá então alimentar modelos de
previsão de demanda e de priorização
multicritério de intervenções sobre uma base cuja incerteza e origem das
decisões permanecem auditáveis.

**REFERÊNCIAS**

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. ABNT NBR 5674: Manutenção de
edificações: Requisitos para o sistema de gestão de manutenção. Rio de
Janeiro: ABNT, 2012.

ANDERSON, M. J.; TER BRAAK, C. J. F. Permutation tests for
multi-factorial analysis of variance. Journal of Statistical Computation
and Simulation, v. 73, n. 2, p. 85--113, 2003.

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

CAMERON, A. C.; GELBACH, J. B.; MILLER, D. L. Bootstrap-based
improvements for inference with clustered errors. The Review of Economics
and Statistics, v. 90, n. 3, p. 414--427, 2008.

CAPRA, F. A teia da vida: uma nova compreensão científica dos sistemas
vivos. São Paulo: Cultrix, 1996.

CHOW, C. K. On optimum recognition error and reject tradeoff. IEEE
Transactions on Information Theory, v. 16, n. 1, p. 41--46, 1970.

COCHRAN, W. G. The comparison of percentages in matched samples.
Biometrika, v. 37, n. 3-4, p. 256--266, 1950.

COCHRAN, W. G. Sampling techniques. 3. ed. New York: John Wiley & Sons,
1977.

COHEN, J. A coefficient of agreement for nominal scales. Educational and
Psychological Measurement, v. 20, n. 1, p. 37--46, 1960.

DEVLIN, J.; CHANG, M.-W.; LEE, K.; TOUTANOVA, K. BERT:
Pre-training of deep bidirectional transformers for language
understanding. In: CONFERENCE OF THE NORTH AMERICAN CHAPTER OF THE
ASSOCIATION FOR COMPUTATIONAL LINGUISTICS, 2019, Minneapolis.
Proceedings [...]. Minneapolis: ACL, 2019. p. 4171--4186.

DICICCIO, T. J.; EFRON, B. Bootstrap confidence intervals. Statistical
Science, v. 11, n. 3, p. 189--228, 1996.

EFRON, B. Bootstrap methods: another look at the jackknife. The Annals
of Statistics, v. 7, n. 1, p. 1--26, 1979.

EFRON, B.; TIBSHIRANI, R. J. An introduction to the bootstrap. New York:
Chapman & Hall/CRC, 1993.

EL-YANIV, R.; WIENER, Y. On the foundations of noise-free selective
classification. Journal of Machine Learning Research, v. 11, p.
1605--1641, 2010.

FIELD, C. A.; WELSH, A. H. Bootstrapping clustered data. Journal of the
Royal Statistical Society: Series B, v. 69, n. 3, p. 369--390, 2007.

GALKE, L.; SCHERP, A. Bag-of-words vs. graph vs. sequence in text
classification: questioning the necessity of text-graphs and the
surprising strength of a wide MLP. In: ANNUAL MEETING OF THE ASSOCIATION
FOR COMPUTATIONAL LINGUISTICS, 60., 2022, Dublin. Proceedings \[\...\].
Dublin: ACL, 2022. p. 4038--4051.

GOOD, P. Permutation, parametric and bootstrap tests of hypotheses. 3.
ed. New York: Springer, 2005.

GRAVES, A.; SCHMIDHUBER, J. Framewise phoneme classification with
bidirectional LSTM and other neural network architectures. Neural
Networks, v. 18, n. 5-6, p. 602--610, 2005.

GRIMM, N. B.; FAETH, S. H.; GOLUBIEWSKI, N. E.; REDMAN, C. L.; WU, J.;
BAI, X.; BRIGGS, J. M. Global change and the ecology of cities. Science,
v. 319, n. 5864, p. 756--760, 2008.

GUO, C.; PLEISS, G.; SUN, Y.; WEINBERGER, K. Q. On calibration of modern
neural networks. In: INTERNATIONAL CONFERENCE ON MACHINE LEARNING, 34.,
2017, Sydney. Proceedings \[\...\]. Sydney: PMLR, 2017. p. 1321--1330.

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

LANDIS, J. R.; KOCH, G. G. The measurement of observer agreement for
categorical data. Biometrics, v. 33, n. 1, p. 159--174, 1977.

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

MARTINS, R. F. B.; ESPEJO, M. M. S. B. Análise de custos de manutenção
predial em uma universidade federal brasileira com uso do modelo de SES.
ABCustos, São Leopoldo, v. 19, n. 1, p. 79--98, 2024.

MCNEMAR, Q. Note on the sampling error of the difference between
correlated proportions or percentages. Psychometrika, v. 12, n. 2, p.
153--157, 1947.

MOHAMMED, A. S.; AMOAH, C. Integration of technology in decision-making
in university facilities management: a literature review. Facilities, v.
43, n. 13/14, p. 1018--1052, 2025.

MORAIS, L. S. R. de; PAULA, H. M. de; REIS, R. P. A. Promoção da
eficiência da manutenção predial em edificações públicas: abordagem
baseada em registros de ordens de serviço. Paranoá, Brasília, v. 16, n.
34, p. 1--18, 2023. DOI: 10.18830/issn.1679-0944.n34.2023.08.

ODUM, H. T. Environment, power, and society. New York:
Wiley-Interscience, 1971.

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

SHANNON, C. E. A mathematical theory of communication. Bell System
Technical Journal, v. 27, n. 3, p. 379--423, jul. 1948; v. 27, n. 4, p.
623--656, out. 1948.

SOKOLOVA, M.; LAPALME, G. A systematic analysis of performance measures
for classification tasks. Information Processing & Management, v. 45, n.
4, p. 427--437, 2009.

SOUZA, F.; NOGUEIRA, R.; LOTUFO, R. BERTimbau: pretrained BERT
models for Brazilian Portuguese. In: BRAZILIAN CONFERENCE ON INTELLIGENT
SYSTEMS, 9., 2020. Proceedings [...]. Cham: Springer, 2020. p. 403--417.
DOI: 10.1007/978-3-030-61377-8_28.

SUNDARAM, S.; ZEID, A. Technical Language Processing for Prognostics and
Health Management: applying text similarity and topic modeling to
maintenance work orders. Journal of Intelligent Manufacturing, v. 36, p.
1637--1657, 2025.

TREVISO, M. et al. Efficient methods for Natural Language Processing: a
survey. Transactions of the Association for Computational Linguistics,
v. 11, p. 826--860, 2023.

WONGPAKARAN, N.; WONGPAKARAN, T.; WEDDING, D.; GWET, K. L. A comparison
of Cohen's Kappa and Gwet's AC1 when calculating inter-rater reliability
coefficients: a study conducted with personality disorder samples. BMC
Medical Research Methodology, v. 13, art. 61, 2013.

ZHANG, H.; ZHANG, Y.; LI, J.; LIU, J.; JI, L. A survey on learning with
noisy labels in Natural Language Processing: how to train models with
label noise. Engineering Applications of Artificial Intelligence, v.
146, art. 110157, 2025.

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
dobras e ficam fora das partições, conforme o critério da Subseção 3.4.
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

