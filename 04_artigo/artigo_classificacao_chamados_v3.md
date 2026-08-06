---
header-includes:
  - |
    ```{=latex}
    \usepackage[font=small,labelfont=bf,justification=centering,skip=6pt]{caption}
    % TABELAS 1 A 4: floats nao divisiveis
    % As Tabelas 1 a 4 do corpo passaram de longtable (pipe-table do pandoc)
    % para o ambiente flutuante 'table' com tabularx: uma tabela que nao
    % couber inteira na pagina corrente migra inteira para a proxima, em vez
    % de dividir linhas entre paginas. As Tabelas A1 a A3 do apendice
    % permanecem como pipe-table/longtable nesta rodada.
    % Colunas Y/Z: todas as colunas sao do tipo X do tabularx (flexivel), com
    % o multiplicador de \hsize controlando a largura relativa de cada uma;
    % \linewidth e sincronizado a \hsize dentro de cada coluna, exigencia do
    % mecanismo interno do tabularx para colunas X ponderadas. A conversao
    % elimina o excesso decorrente da soma manual de colunas fixas e limita a
    % tabela a largura declarada do tabularx, permanecendo necessaria a
    % inspecao do PDF quanto a conteudo nao separavel e legibilidade.
    \usepackage{array}
    \usepackage{booktabs}
    \usepackage{tabularx}
    \newcolumntype{Y}[1]{%
      >{\hsize=#1\hsize\linewidth=\hsize\raggedright\arraybackslash}X
    }
    \newcolumntype{Z}[1]{%
      >{\hsize=#1\hsize\linewidth=\hsize\centering\arraybackslash}X
    }
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
BERTimbau, cujo custo medido é tratado na Subseção 4.5, de sorte que nada se
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
separaria. A contagem consta da Subseção 4.4.

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

```{=latex}
\begin{table}[!tbp]
\centering
\small
\caption{Configuração experimental dos sete modelos, que compartilham
partições, rótulo de treino e denominador (n = 13.972; 41 categorias).}
\label{tab:modelos}
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.15}
\begin{tabularx}{\textwidth}{@{}Y{0.75}Y{0.65}Y{2.2}Y{0.8}Y{0.8}Y{0.8}@{}}
\toprule
Modelo & Representação & Hiperparâmetros essenciais & Balanceamento & Saída de confiança & Papel \\
\midrule
Naive Bayes & TF-IDF & suavização $\alpha$ = 1 & nenhum & probabilidade máxima & \textit{baseline} probabilístico \\
Regressão Logística & TF-IDF & até 1.000 iterações & pesos balanceados & probabilidade máxima & linear probabilístico \\
LinearSVC & TF-IDF & margem máxima, \textit{C} = 1 & pesos balanceados & \textit{softmax} da margem & linear de margem máxima \\
SGD & TF-IDF & perda logarítmica & pesos balanceados & probabilidade máxima & linear incremental \\
Random Forest & TF-IDF & 200 árvores & pesos balanceados & probabilidade máxima & \textit{ensemble} agregado \\
Extra Trees & TF-IDF & 200 árvores, cortes aleatórios & pesos balanceados & probabilidade máxima & \textit{ensemble} aleatorizado \\
LSTM Bidirecional & tokenização própria & \textit{embedding} de 128, 64 unidades, \textit{dropout} 0,5, densa de 64, lote de 128 & pesos balanceados & \textit{softmax} & rede neural sequencial \\
\bottomrule
\end{tabularx}
\end{table}
```

Um oitavo modelo, o BERTimbau-Base (DEVLIN *et al.*, 2019; SOUZA; NOGUEIRA;
LOTUFO, 2020), é experimento exploratório fora da comparação principal: foi
ajustado sob protocolo distinto, com subamostragem estratificada e parada
antecipada, sem predições *out-of-fold* sobre todo o corpus. A medição de
custo que fundamenta a separação consta da Subseção 4.5; nada se afirma sobre
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
constam da Subseção 4.1 e do material suplementar.

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
histórico, qualificado pela utilidade da Subseção 4.2.

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
e é qualificada pela utilidade sob custos assimétricos da Subseção 4.2. A camada explícita de regras de periodicidade, em módulo próprio e auditável,
tem desenho e termos na Subseção 4.5. A camada informacional de
entropia de Shannon e divergência de Jensen-Shannon (SHANNON, 1948; LIN,
1991) é calculada sobre agregados sanitizados e mede dispersão das predições,
distância frente à distribuição histórica e desacordo entre modelos, este
último usado para ordenar fila de auditoria; nada se afirma, a partir dela,
sobre desordem do sistema físico. O teste de sensibilidade da cobertura sob
três convenções de denominador consta da Subseção 4.1.

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
execução. Os tempos da Subseção 4.1 são expressos em segundos, como mediana
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

Esta seção reporta o desempenho de sete modelos sob dois denominadores que
não devem ser confundidos: a base congelada contém 14.060 chamados, todos
com referência humana, número pertinente sempre que a frase tratar do
corpus ou da cobertura da revisão, ao passo que as métricas de desempenho,
calibração e inferência são apuradas sobre as 13.972 linhas em 41
categorias que compõem as partições canônicas (Subseção 3.4; Tabela A3).

Quatro achados organizam a seção. Os sete modelos foram avaliados de forma
comparável sob o mesmo protocolo, mas apresentaram desempenhos distintos,
sem vencedor absoluto ao considerar simultaneamente acurácia, macro-F1,
custo e calibração: o LinearSVC lidera
a acurácia, a Regressão Logística tem o macro-F1 pontual ligeiramente
superior e o SGD permanece próximo dos dois, de modo que a escolha
operacional depende de mais de um critério (Subseção 4.1). A
reclassificação automática da base histórica produz ganho líquido negativo
em todos os modelos, o que desautoriza a correção em massa e desloca o
valor da divergência para a priorização da auditoria humana (Subseção
4.2). A calibração isotônica viabiliza automação seletiva de cerca de dois
terços do volume com acurácia próxima de 0,95 (Subseção 4.3). E os erros
que restam concentram-se em fronteiras taxonômicas específicas, e não se
distribuem de modo difuso pela taxonomia (Subseção 4.4).

```{=latex}
\FloatBarrier
```

**4.1 Desempenho, incerteza e custo**

A comparação contra a categoria histórica, sobre as predições
*out-of-fold* da rodada canônica (n = 13.972), mantém o LinearSVC à frente
em acordo bruto, seguido por Extra Trees, SGD, Random Forest e Regressão
Logística, com LSTM e Naive Bayes na última posição; o BERTimbau fica fora
desse conjunto pelo motivo computacional detalhado na Subseção 4.5. A
revisão humana estabeleceu categoria de referência para a totalidade dos
14.060 chamados da base congelada, e a avaliação contra essa referência
incide sobre as 13.972 linhas das partições: o LinearSVC é o modelo de
maior acurácia, com 0,8253 (IC95%: 0,8115--0,8378), seguido por SGD, Extra
Trees, Regressão Logística e Random Forest, com LSTM e Naive Bayes bem
atrás. A cobertura integral da revisão evita o viés decorrente de
selecionar apenas uma subamostra para revisão, de modo que a acurácia
relatada não constitui limite superior de amostra conferida; ela não
elimina, porém, a ancoragem na categoria histórica, o avaliador único, a
ausência de cegamento e a ausência de avaliação independente, ressalvas
detalhadas na Subseção 5.3.

Não há vencedor absoluto entre os três primeiros colocados. O LinearSVC
lidera a acurácia, mas as três melhores marcas de macro-F1 ficam a menos
de três milésimos umas das outras, com Regressão Logística em 0,6689,
LinearSVC em 0,6684 e SGD em 0,6669, e seus intervalos de confiança se
sobrepõem integralmente: os três não devem ser ordenados por essa métrica
isoladamente. A leitura pertinente é que o LinearSVC lidera a acurácia sem
pagar por isso em desempenho na cauda, ao contrário dos *ensembles* de
árvores, que perdem cerca de três centésimos de macro-F1 na mesma faixa de
acurácia, e que o SGD permanece competitivo nas duas métricas a um custo
de treino semelhante ao do LinearSVC. A escolha operacional é, portanto,
multicritério, e deve pesar acurácia, macro-F1 e custo computacional
conjuntamente, e não apenas a primeira.

```{=latex}
\begin{table}[!tbp]
\centering
\small
\caption{Concordância com a categoria histórica, acurácia e macro-F1
contra a referência humana revisada, e custo de treino, por modelo
(n = 13.972; 41 categorias). O intervalo é da acurácia, obtido por
\textit{bootstrap} de grupo textual com mil repetições sobre os 9.735
grupos congelados; o custo de treino é mediana de três execuções sobre a
base completa.}
\label{tab:desempenho}
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.15}
\begin{tabularx}{\textwidth}{@{}Y{1.3}Z{1.0}Z{0.7}Z{0.7}Z{1.4}Z{0.9}@{}}
\toprule
Modelo & Concordância histórica & Acurácia & Macro-F1 & Intervalo essencial (IC95\% da acurácia) & Tempo de treino (s) \\
\midrule
LinearSVC & 0,7961 & 0,8253 & 0,6684 & 0,8115 -- 0,8378 & 2,44 \\
SGD & 0,7781 & 0,8093 & 0,6669 & 0,7950 -- 0,8227 & 2,28 \\
Extra Trees & 0,7844 & 0,8073 & 0,6362 & 0,7923 -- 0,8211 & 26,69 \\
Regressão Logística & 0,7738 & 0,8050 & 0,6689 & 0,7907 -- 0,8189 & 8,43 \\
Random Forest & 0,7747 & 0,7970 & 0,6152 & 0,7812 -- 0,8111 & 22,62 \\
LSTM & 0,7017 & 0,7287 & 0,5240 & 0,7080 -- 0,7480 & 83,44 \\
Naive Bayes & 0,6954 & 0,7088 & 0,2951 & 0,6860 -- 0,7311 & 1,12 \\
\bottomrule
\end{tabularx}
\end{table}
```

O custo de treino, medido no mesmo ambiente computacional para os sete
modelos sobre a base completa, com mediana de três execuções, reforça a
leitura multicritério: os modelos lineares treinam em poucos segundos, de
1,12 s no Naive Bayes a 8,43 s na Regressão Logística, os *ensembles* de
árvores exigem entre vinte e trinta segundos e a rede neural LSTM consome
83,44 segundos, cerca de 34 vezes o tempo do LinearSVC, para 9,7 pontos
percentuais a menos de acurácia. Os tempos absolutos e as razões entre
modelos descrevem o ambiente avaliado, um processador de quatro núcleos
sem acelerador gráfico; a estabilidade relativa desses tempos em outras
infraestruturas não foi testada. A Figura 2 cruza essas medições
de custo
com a acurácia e mostra o LinearSVC na posição mais favorável, com a
maior acurácia a um custo de treino próximo do menor observado. Contra o
BERTimbau, o que se afirma é mais restrito: o custo medido de 6,44 horas
por dobra inviabiliza a validação cruzada agrupada no ambiente do estudo
(Subseção 4.5), sem que disso decorra juízo sobre seu desempenho.

![Trade-off entre acurácia e tempo de treino, modelos clássicos.](04_artigo/figuras/fig_tradeoff_custo.pdf){width=76%}

A comparação entre modelos exige tratar a dependência entre registros de
texto idêntico como propriedade do desenho, e não como detalhe de
implementação: as 13.972 linhas avaliadas distribuem-se por 9.735 grupos
textuais, e 4.546 delas, ou 32,54%, pertencem a grupos com mais de um
membro. O efeito de desenho, razão entre a variância da acurácia sob
reamostragem de conglomerados e a variância binomial que a suposição de
independência produziria (COCHRAN, 1977), fica entre 4,47 no LinearSVC e
8,83 no Naive Bayes, de modo que toda inferência desta subseção adota o
grupo textual como unidade. O teste global rejeita a igualdade entre os
sete modelos: a estatística Q de Cochran vale 2.661,04 sobre seis graus de
liberdade, apurada contra distribuição empírica de duas mil permutações
do rótulo de modelo dentro de cada grupo, com *p* < 0,0005. Só então os 21
pares foram comparados, por permutação pareada com troca de sinal da
diferença de acertos por grupo e correção de Holm sobre a família:
dezenove são significativos após a correção e dois não são, Extra Trees
contra Regressão Logística e Extra Trees contra SGD, ambos com intervalo
da diferença contendo o zero, o que é coerente com a sobreposição de
macro-F1 relatada acima. Contra o segundo colocado, SGD, a vantagem do
LinearSVC de 1,60 ponto percentual (IC95%: 0,0118--0,0204) corresponde a
533 grupos favoráveis contra 308, com 8.894 empatados: vantagem
estatisticamente estabelecida e vantagem prática são coisas distintas, e
nove de cada dez grupos não distinguem os dois modelos. A matriz completa
dos 21 pares, com intervalos, grupos favoráveis e tamanho de efeito,
consta do material suplementar.

O macro-F1 de 0,6684 do LinearSVC é média sobre as 41 categorias com
suporte nas partições. Sob um cenário pessimista de sensibilidade,
atribuindo F1 igual a zero às nove categorias ausentes das 50 da
taxonomia, esse valor cai a 0,5481; não se trata de desempenho observado
de um modelo treinado nas 50 categorias, pois nenhum classificador prevê
categoria que não esteve em seu treino: a cobertura de linhas permanece
alta, 99,37%, mas a de categorias cai a 82%. Agregado às 14 famílias do
primeiro nível da
taxonomia, o
macro-F1 sobe a 0,6816, granularidade em que o LinearSVC assume também a
liderança dessa métrica, antes com a Regressão Logística por três
milésimos. A ordenação dos modelos é estável nas três convenções de
denominador, à exceção dessa troca de posição no topo; os valores por
modelo constam do material suplementar.

```{=latex}
\FloatBarrier
```

**4.2 Auditoria do histórico e risco de reclassificação**

A revisão humana manteve a categoria histórica em 13.462 dos 14.060
chamados da base congelada, ou 95,75% do corpus, e a substituiu em 598
registros, taxa de alteração do rótulo histórico de 4,25%, e não
estimativa de prevalência de erro (Subseção 3.1). Essa estabilidade da
referência explica o resultado da reclassificação automática: como o
histórico já concorda com a revisão na quase totalidade dos casos,
divergir dele significa, na maior parte das vezes, divergir também da
referência.

O ganho líquido de reclassificação, contado apenas onde a predição
diverge da categoria histórica e arbitrado pela referência revisada, é
negativo nos sete modelos, de −1.846 no LinearSVC a −3.474 no Naive Bayes
(Tabela 3). O melhor modelo produz 2.849 divergências, das quais apenas
475 representam correção contra 2.321 que degradariam o registro, razão
que piora monotonicamente à medida que cai o desempenho do modelo. A
reclassificação automática em massa não é, portanto, desaconselhada por
cautela metodológica, mas por evidência de que degradaria a base em que
fosse aplicada, e o ganho líquido, e não a acurácia agregada, é o critério
adequado para essa decisão, a ser recalculado a cada atualização da base.

```{=latex}
\begin{table}[!tbp]
\centering
\small
\caption{Ganho líquido de reclassificação por modelo, contado apenas
onde a predição diverge da categoria histórica e arbitrado pela
referência humana revisada (n = 13.972).}
\label{tab:reclassificacao}
\setlength{\tabcolsep}{5pt}
\renewcommand{\arraystretch}{1.15}
\begin{tabularx}{\textwidth}{@{}Y{1.6}Z{0.9}Z{0.9}Z{0.9}Z{0.7}Z{1.0}@{}}
\toprule
Modelo & Divergências & Corrigidos & Prejudicados & Neutros & Ganho líquido \\
\midrule
LinearSVC & 2.849 & 475 & 2.321 & 53 & $-$1.846 \\
SGD & 3.100 & 489 & 2.559 & 52 & $-$2.070 \\
Extra Trees & 3.012 & 422 & 2.519 & 71 & $-$2.097 \\
Regressão Logística & 3.161 & 492 & 2.621 & 48 & $-$2.129 \\
Random Forest & 3.148 & 416 & 2.658 & 74 & $-$2.242 \\
LSTM & 4.168 & 426 & 3.621 & 121 & $-$3.195 \\
Naive Bayes & 4.256 & 309 & 3.783 & 164 & $-$3.474 \\
\bottomrule
\end{tabularx}
\end{table}
```

O ganho líquido simples pressupõe que corrigir um registro e estragar
outro valham o mesmo, e que revisar não custe nada. A qualificação
decisória substitui essa hipótese pela função de utilidade
*U* = *b* × corrigidos − *c* × prejudicados − *r* × revisados, normalizada
pelo benefício da correção em duas razões adimensionais: $\rho$ = *c*/*b*,
o custo do prejuízo em unidades de benefício, e $\lambda$ = *r*/*b*, o
custo da revisão humana na mesma unidade. Sob aplicação direta, a
utilidade só seria positiva se $\rho$ ficasse abaixo da razão de
equilíbrio corrigidos/prejudicados, que vale 0,2047 no LinearSVC e cai a
0,0817 no Naive Bayes: a reclassificação exigiria que estragar um
registro custasse menos de um quinto do que vale corrigir outro, condição
que a natureza do dano não sustenta, pois o registro corrompido propaga
para a série temporal da categoria (Subseção 5.4). Em toda a faixa
examinada, de $\rho$ = 0,25 a $\rho$ = 4, a utilidade é negativa nos sete
modelos.

A mesma predição sustenta, entretanto, uma política de triagem: se a
divergência apenas enfileira o chamado para revisão humana, sem
reescrever o rótulo, não há prejudicados por construção, e o benefício é
a fração da fila cujo histórico de fato estava errado, 18,53% no
LinearSVC contra a taxa de alteração de 4,25% na base, enriquecimento de
cerca de quatro vezes sobre a revisão aleatória. O limite de equilíbrio de
$\lambda$ coincide com essa precisão: a triagem paga enquanto revisar um
chamado custar menos de 18,5% do que vale corrigir um registro. A
consequência operacional é discutida na Subseção 5.2, e os valores por
modelo constam do material suplementar.

**4.3 Calibração e automação seletiva**

A confiança bruta dos classificadores não é probabilidade e não sustenta
decisão operacional sem tratamento: o erro de calibração esperado (ECE)
do LinearSVC alcança 0,6925 sobre o escore bruto, porque a transformação
da margem por função *softmax* produz valores que não correspondem a
frequências de acerto. A calibração isotônica, ajustada em dobra interna,
reduz esse valor a 0,0178 e o escore de Brier de 0,6052 para 0,1034, e
melhora o ECE de cinco dos sete modelos. Naive Bayes e LSTM foram as
exceções, com aumento do ECE após a calibração; o desenho não permite
atribuir causalmente essa piora a um mecanismo específico.

A calibração viabiliza a automação seletiva, em que o classificador
decide sozinho acima de um limiar de confiança e encaminha o restante à
revisão humana. Ao alvo de 0,95 de acurácia, o Extra Trees automatiza
67,32% dos chamados com acurácia seletiva de 0,9502, o SGD automatiza
61,62% com 0,9531 e o LinearSVC automatiza 68,90% com 0,9464, faixa que
ilustra a mesma escolha multicritério da Subseção 4.1 entre cobertura e
acurácia seletiva. Parte das acurácias seletivas fica pouco abaixo do
alvo, consequência esperada de escolher o limiar em dobra interna sem
acesso ao conjunto de teste. Elevar o alvo a 0,99 reduz a cobertura à
faixa de 31,94% a 47,04%, e o Naive Bayes só alcança o limiar em duas das
cinco dobras, o que o desqualifica para esse regime.

```{=latex}
\begin{table}[!tbp]
\centering
\small
\caption{Calibração e automação seletiva dos quatro modelos mais
competitivos em acurácia (n = 13.972). O ECE refere-se ao escore antes e
depois da calibração isotônica; a cobertura e a acurácia seletiva
correspondem ao alvo de 0,95. Random Forest é omitido desta versão
reduzida; a tabela com os sete modelos, incluindo Naive Bayes e LSTM,
cujo ECE aumenta após a calibração, consta do material suplementar
(Tabela S16).}
\label{tab:calibracao}
\setlength{\tabcolsep}{6pt}
\renewcommand{\arraystretch}{1.15}
\begin{tabularx}{\textwidth}{@{}Y{1.6}Z{0.85}Z{0.85}Z{0.85}Z{0.85}@{}}
\toprule
Modelo & ECE bruto & ECE calibrado & Cobertura & Acurácia seletiva \\
\midrule
LinearSVC & 0,6925 & 0,0178 & 0,6890 & 0,9464 \\
SGD & 0,3046 & 0,0109 & 0,6162 & 0,9531 \\
Extra Trees & 0,0859 & 0,0108 & 0,6732 & 0,9502 \\
Regressão Logística & 0,2351 & 0,0189 & 0,6237 & 0,9415 \\
\bottomrule
\end{tabularx}
\end{table}
```

A Figura 3 apresenta a curva de confiabilidade do Extra Trees calibrado,
tornando visível a aderência entre confiança declarada e acerto observado
ao longo das dez faixas.

![Curva de confiabilidade do Extra Trees após calibração isotônica, com confiança média e acurácia observada por faixa.](04_artigo/figuras/fig_confianca_desfecho.pdf){width=95%}

```{=latex}
\FloatBarrier
```

**4.4 Erros por categoria e implicações taxonômicas**

O diagnóstico de dispersão entre as predições dos sete modelos mostra que
diversidade de categorias previstas e aderência à distribuição histórica
não caminham juntas neste corpus: o LSTM tem a maior entropia normalizada
(0,8362) e o LinearSVC a menor divergência de Jensen-Shannon frente ao
histórico (0,0055). No nível do chamado, os sete modelos são unânimes em
60,44% dos registros e discordam em três ou mais categorias em 16,35%
deles, conjunto que caracteriza desacordo estrutural entre arquiteturas e
prioriza auditoria complementar à baixa confiança de um único modelo. O
Naive Bayes sintetiza o diagnóstico ao combinar a menor cobertura de
categorias, apenas 22 contra 39 a 41 dos demais modelos, com a menor
entropia normalizada e a maior divergência frente ao histórico, o que
explica seu macro-F1 de 0,2951 apesar de acurácia próxima de 0,71.

O desempenho também não é uniforme entre as 41 categorias avaliadas. A
Figura 4 contrasta, entre as 33 categorias com suporte mínimo de trinta
registros, as dez de maior e as dez de menor F1 do LinearSVC: nas
melhores, o F1 varia de 0,9139 a 0,9972 sobre 6.271 chamados, quase todas
de Manutenção Preventiva, cujos chamados nascem de rotina programada e
recebem descrição padronizada; nas piores, cai à faixa de 0,2162 a 0,6288
sobre 2.403 chamados, porte comparável em ordem de grandeza, concentrando
rótulos de fronteira aberta como Telhados preventivos, Reforma, Erro de
chamado e Alvenaria, Pisos e Estrutura, que competem por vocabulário com
categorias vizinhas. O padrão é sistemático, na linha do que Zhang *et
al.* (2025) descrevem para rótulos ruidosos em processamento de linguagem
natural, e não aleatório. O desempenho por categoria, com suporte, tipo e
classe de volume, consta da Tabela A2.

![F1 do LinearSVC e suporte, para as dez categorias de maior e de menor desempenho entre as 33 com suporte mínimo de 30 chamados.](04_artigo/figuras/fig_calor_categorias.pdf){width=73%}

A Figura 5 recorta a matriz de confusão sobre as oito categorias mais
envolvidas em troca recíproca. A célula dominante registra 1.066 chamados
de Instalação e reparo de equipamentos preditos como Alvenaria, Pisos e
Estrutura, com 937 no sentido inverso, a maior fronteira do corpus, com
2.003 trocas somadas; seguem-se Alvenaria contra Esquadrias, com 1.097
trocas, e Alvenaria contra Hidráulica, com 940. Alvenaria, Pisos e
Estrutura comparece nos cinco maiores pares e se comporta como categoria
absorvente, para a qual convergem chamados cuja descrição não delimita o
sistema predial afetado; a leitura assimétrica de vários pares sugere
absorção, e não simples permuta. A fronteira entre climatização corretiva
e preventiva não figura entre as maiores confusões, resultado coerente
com a facilidade da tarefa de tipo reportada na Subseção 4.5. O
ordenamento completo dos quinze pares de maior confusão recíproca consta
do material suplementar.

![Recorte da matriz de confusão sobre as oito categorias mais envolvidas em troca recíproca, com contagens agregadas entre modelos.](04_artigo/figuras/fig_matriz_confusao.pdf){width=80%}

A auditoria dos grupos de texto idêntico (Subseção 3.1) localiza
ambiguidade no próprio dado, e não na predição: 17 grupos receberam mais
de uma categoria de referência, afetando 85 linhas, ou 0,61% das linhas
avaliadas, e em 14 deles, somando 74 linhas, as categorias em disputa
pertencem a tipos distintos de manutenção, com o par mais frequente
opondo Hidrossanitária > Hidráulica a Manutenção Preventiva > Reservatório,
em 11 grupos e 65 linhas. Textos idênticos podem, portanto, corresponder a
intervenções de naturezas diferentes, distinção irrecuperável por um
classificador que utilize exclusivamente os quatro campos textuais
empregados neste estudo; a contagem sinaliza ambiguidade interna,
mas não fixa teto quantitativo de desempenho, pois esse teto exigiria
calcular a distribuição dos rótulos dentro de cada grupo, o que não foi
feito.

Soma-se a esse quadro a duplicação taxonômica: a categoria Ar condicionado
split existe simultaneamente sob Manutenção Preventiva, com 1.798
chamados, e sob Climatização, com 1.640, e o mesmo desdobramento ocorre
com Ar condicionado central, Gerador, Nobreak, Elevador, Telhados, calhas,
rufos e Sistemas de combate a incêndio. O critério que separa esses pares
é a natureza preventiva ou corretiva da intervenção, informação que o
texto do chamado frequentemente não explicita, de modo que parte do erro
medido decorre da exigência de inferir do texto uma distinção que nele
não está registrada, e não de limitação do classificador. Depreende-se
daí uma recomendação de governança anterior à escolha do modelo: revisar
a taxonomia institucional, unificando os pares que nomeiam o mesmo objeto
e explicitando o critério de natureza da manutenção no formulário de
abertura do chamado, atua sobre a origem do erro, ao passo que a
substituição do classificador atua apenas sobre seu efeito.

```{=latex}
\FloatBarrier
```

**4.5 Análises complementares**

O BERTimbau não integra a comparação principal por motivo computacional
medido no mesmo ambiente dos demais modelos: o ajuste fino custou 10,774
segundos por passo, e os 2.103 passos de cada dobra projetam 6,44 horas
por dobra e 32,2 horas para as cinco, contra um teto de execução de seis
horas, de modo que nem uma dobra completa cabe na infraestrutura do
estudo. A limitação é de infraestrutura, e não do modelo; um experimento
exploratório avaliou o transformador em lote de mil chamados, dos quais
983 com referência humana, e os valores constam do material suplementar,
sem serem comparáveis às métricas desta seção, por não cobrirem o corpus
de modo probabilístico e por empregarem subamostragem estratificada com
parada antecipada.

O treino do LSTM parou por interrupção antecipada após 11 épocas, com
menor perda de validação na época 8 e maior acurácia de validação na
época 10 (0,6722), padrão de saturação precoce consistente com a hipótese
de que *embeddings* treinados do zero são insuficientes para um corpus
deste porte (Subseção 3.3; Figura 6). A justificativa do particionamento
agrupado é anterior a essa medição e repousa na estrutura do corpus: a
partição por linha permitiria ao mesmo texto ocupar treino e teste, e
duas estimativas de sensibilidade indicam ganho espúrio entre 0,89 e 1,84
ponto percentual de acurácia sob esse desenho, valores que constam do
material suplementar com o protocolo declarado.

![Curva de aprendizado do LSTM por época, perda e acurácia em treino e validação.](04_artigo/figuras/fig_curva_aprendizado_lstm.pdf){width=95%}

Dois recortes complementares qualificam a leitura agregada sem alterá-la.
A curva ABC sobre o suporte das 41 categorias concentra 81,83% do volume
em 12 categorias de classe A, com macro-F1 do LinearSVC de 0,8207 nessa
classe contra 0,5018 na classe C, o que localiza na cauda a distância
entre acurácia e macro-F1 agregados. A projeção da referência e das
predições para o nível de tipo de manutenção, em três categorias e não na
dicotomia usual entre preventivo e corretivo, eleva o desempenho a outro
patamar: o LinearSVC alcança 0,9443 de acurácia contra 0,8253 na tarefa
de 41 categorias, com F1 de 0,9742 na preventiva e 0,9547 na corretiva, e
toda a perda concentra-se no terceiro tipo, cujo F1 não ultrapassa 0,5330
em nenhum modelo. Cabe registrar a inversão de ordenação nessa
granularidade: o Extra Trees lidera a acurácia, com 0,9497, e o LinearSVC
lidera o macro-F1, com 0,8180, precisamente por ir melhor na classe
difícil, o que faz a escolha do classificador depender tanto do nível de
agregação da decisão quanto da métrica que ela privilegia. Depreende-se
do conjunto dessas medições uma hierarquia de confiabilidade: a contagem
por tipo de manutenção é a leitura mais segura, a leitura por categoria só
se sustenta nas classes de maior volume de cada tipo, e nas classes B e C
o desempenho medido não autoriza uso automático. O detalhamento por
classe e por tipo consta do material suplementar.

A camada explícita de regras de periodicidade, que atribui categoria
preventiva quando o texto reúne um termo de periodicidade e um termo de
equipamento, dispara em 4.487 dos 13.972 registros e ainda assim melhora
o macro-F1 de apenas três dos sete modelos, com ganho concentrado no
Naive Bayes (+0,0586) e perdas marginais em Extra Trees, Random Forest e
LinearSVC. Como a regra depende só do texto, ela dispara no mesmo
conjunto para os sete modelos, e o que varia é a predição que substitui:
no LinearSVC, os 4.487 disparos produzem apenas 31 divergências, contra
219 no Naive Bayes, no qual a regra acerta 201 vezes contra 9 do modelo.
A leitura é que regras de domínio são redundantes diante de um
classificador estatístico competente, que já captura implicitamente os
sinais de periodicidade presentes no texto: o ganho do fluxo híbrido está
no eixo humano–IA (Subseção 4.3), e não no eixo regra–modelo.

**5. DISCUSSÃO**

**5.1 Adequação dos modelos e decisão multicritério**

O desempenho dos sete modelos (Tabela 2) não aponta vencedor absoluto: o
LinearSVC lidera a acurácia, a Regressão Logística tem o macro-F1 pontual
ligeiramente superior, e o SGD permanece próximo de ambos, com intervalos
de confiança sobrepostos entre os três primeiros. A leitura operacional é,
portanto, multicritério, e pesa acurácia, macro-F1 e custo computacional em
conjunto: a superioridade estatística do LinearSVC sobre o segundo colocado
(Subseção 4.1) não basta, isoladamente, para declará-lo vencedor único.

O bom desempenho dos modelos lineares é compatível com a literatura sobre
texto curto de vocabulário técnico, em que representações esparsas com
fronteiras lineares sustentam desempenho competitivo (JOACHIMS, 1998;
SALTON; BUCKLEY, 1988; GALKE; SCHERP, 2022), sem que isso autorize
generalizar essa superioridade a outros domínios, corpora mais longos ou
arquiteturas neurais e transformadoras mais profundas, cuja comparação
direta este desenho não realizou.

O BERTimbau permanece fora dessa comparação por custo computacional medido
(Subseção 4.5), condição de infraestrutura, e não julgamento sobre seu
desempenho: rankings produzidos sob protocolos distintos não sustentam
comparação direta, e nada se afirma aqui sobre sua qualidade relativa aos
sete modelos avaliados sob o protocolo agrupado.

O custo de treino pesa na decisão institucional tanto quanto a métrica de
acerto: em ambiente sem acelerador gráfico, um modelo que treina em poucos
segundos pode ser reexecutado e auditado a cada atualização da base sem
infraestrutura dedicada, condição que a literatura sobre eficiência
computacional recomenda reportar junto da acurácia (SCHWARTZ *et al.*,
2020; TREVISO *et al.*, 2023). É esse critério, e não apenas o desempenho
isolado, que torna o LinearSVC e o SGD os candidatos mais favoráveis no
ambiente e no protocolo avaliados, por sustentarem acurácia e macro-F1
competitivos a custo de treino próximo do menor observado, sem exigir
aceleração gráfica nem infraestrutura fora do ambiente institucional
(Subseção 4.1).

**5.2 Auditoria do histórico, reclassificação e fluxo humano–IA**

A acurácia do LinearSVC contra a referência revisada (0,8253) supera sua
concordância com o histórico (0,7961) em 2,92 pontos percentuais (Tabela 2).
A diferença reflete a substituição da categoria histórica pela referência
revisada no recorte avaliado. No corpus integral, 598 dos 14.060 rótulos
foram alterados; como não se contabilizou separadamente quantas dessas
alterações pertencem às 13.972 linhas avaliadas, os 2,92 pontos percentuais
não são atribuídos diretamente ao total de 598 alterações. A revisão manteve
a categoria histórica em 95,75% dos casos; os 4,25% restantes são taxa de
alteração do rótulo sob auditoria administrativa de avaliador único, com a
categoria histórica à vista, sem segunda avaliação, cegamento ou
adjudicação, e nenhuma medida de concordância interavaliadores é reportada
(Subseção 3.1). É essa estabilidade da linha de base, e não uma limitação
estatística isolada, que explica por que corrigir a base a partir da
divergência fracassa.

O ganho líquido de reclassificação é negativo nos sete modelos (Tabela 3):
o melhor deles corrige menos de um quinto das vezes em que diverge do
histórico, veredito sobre a tarefa, e não nuance entre modelos, pois a
magnitude do prejuízo acompanha, na ordem inversa, o desempenho de cada
classificador. Sob a função de utilidade explícita (Subseção 4.2), a
reclassificação automática em massa só compensaria se o custo de um
registro prejudicado ficasse abaixo de um quinto do benefício de corrigir
outro, hipótese que a assimetria do dano contradiz. Automação seletiva por
confiança, entretanto, não equivale a reescrever a base: a mesma
divergência que fracassa como correção em massa funciona como critério de
priorização da fila de auditoria humana, com enriquecimento de cerca de
quatro vezes sobre a revisão aleatória, e é a calibração isotônica que
torna esse regime operável, ao permitir selecionar uma fração do volume no
alvo de acurácia desejado e encaminhar o restante ao revisor (Subseção
4.3); o desempenho desse regime sobre chamados futuros ainda não foi
validado temporalmente (Subseção 5.3).

A ambiguidade taxonômica contribui para esse quadro: pares de categorias
que nomeiam o mesmo objeto sob famílias distintas de natureza preventiva ou
corretiva, e grupos de texto idêntico com referência divergente entre tipos
de manutenção, mostram que parte do erro medido decorre da própria
taxonomia, e não apenas do classificador (Subseção 4.4). Essa distinção
fica irrecuperável para qualquer modelo que utilize somente os quatro
campos textuais empregados neste estudo, e a contagem de grupos divergentes
não define teto quantitativo de desempenho: sinaliza ambiguidade a ser
resolvida por revisão da taxonomia institucional, não limite estatístico do
classificador.

O diagnóstico de entropia de Shannon e divergência de Jensen-Shannon entre
as predições dos sete modelos (Subseção 4.4) amplia esse repertório de
governança sem substituir as métricas supervisionadas: ao separar
dispersão de predição, distância frente à distribuição histórica e
desacordo entre modelos, ele distingue o erro do classificador da
ambiguidade genuína da taxonomia e da heterogeneidade natural da demanda,
e o desacordo estrutural entre arquiteturas passa a critério adicional
para ordenar a fila de auditoria, complementar à baixa confiança de um
único modelo.

**5.3 Limitações e alcance da evidência**

A evidência tem alcance delimitado por características do desenho, que
devem ser lidas em conjunto. Os dados provêm de uma única instituição
federal de ensino superior, em português brasileiro e taxonomia
institucional própria, o que exige validação externa antes de generalizar
a outras instituições, idiomas ou taxonomias. A referência humana resulta
de auditoria administrativa por avaliador único, com a categoria histórica
à vista, sem segunda avaliação, cegamento ou adjudicação, condição que
impede estimar a prevalência de erro do rótulo histórico ou a
reprodutibilidade da referência por outro especialista, restrição agravada
pela ancoragem, condição constitutiva da auditoria de rótulo mas
incompatível com anotação independente: a literatura registra
variabilidade relevante entre anotadores em tarefas de rotulagem dessa
natureza (KEJRIWAL *et al.*, 2024). Uma segunda avaliação sobre amostra
estratificada, com adjudicação nos pares taxonômicos ambíguos, é a
validação futura pertinente. As métricas cobrem 41 das 50 categorias da
taxonomia, com as nove mais raras fora das partições por suporte
insuficiente (Subseção 4.1), e os grupos de texto idêntico com referência
divergente (Subseção 4.4) expõem inconsistência interna que não substitui
avaliação independente.

O corpus congelado não preserva data de abertura por chamado, de modo que
a validação cruzada agrupada mede generalização entre grupos textuais de
um mesmo corte de extração, e não desempenho futuro sob deriva de
vocabulário, de taxonomia ou de equipe de triagem; nenhuma métrica deste
artigo é, portanto, prospectiva. A execução canônica da LSTM não fixou a
semente global do TensorFlow, o que não compromete partições, rótulos ou
protocolo, mas impede reproduzir exatamente pesos e trajetória de
treinamento; o BERTimbau permanece exploratório, fora da comparação
principal, por custo computacional medido. Os campos textuais brutos
permanecem restritos ao ambiente do pesquisador por privacidade
institucional, e o repositório não guarda documento de autorização
institucional formal, de aprovação por comitê de ética ou de dispensa de
apreciação ética; nada se afirma aqui sobre esse ponto, e sua formalização
é providência recomendada antes da submissão (Subseção 3.6).

**5.4 Implicações para governança e continuidade da tese**

A classificação auditável não é etapa preditiva em si, mas camada de
governança e estruturação dos dados que a antecede: converte texto livre
em categoria e confiança rastreáveis, condição sem a qual previsão de
demanda por categoria, estimativa de custo de manutenção, leitura
territorial e geoprocessada do parque edificado, classificação de
criticidade e métodos de decisão multicritério (MCDM) não têm base
confiável sobre a qual operar. Nenhuma dessas etapas foi validada neste
artigo, e sua incorporação é trabalho futuro da tese, não extensão
implícita dos resultados aqui reportados. A exigência é específica quando
a camada classificada alimenta modelos de série temporal por categoria: um
chamado mal classificado subtrai uma ocorrência de uma categoria e a
acrescenta a outra, deslocando duas séries em sentidos opostos e
propagando o erro à estimativa de demanda, de custo e ao ordenamento de
prioridades que delas deriva, o que dá assimetria aos custos discutidos na
Subseção 5.2.

O enquadramento do campus como biossistema construído (Seção 1) organiza
essa continuidade como integração entre infraestrutura física, atividade
humana, sistemas tecnológicos e condicionantes ambientais, e não como
resultado empírico medido neste estudo: a contribuição empírica é o
protocolo de classificação auditável, e o enquadramento situa por que essa
camada de dados importa para a governança do biossistema, sem que o artigo
meça retroalimentação ecológica ou desempenho ambiental. É esse
enquadramento funcional, e não um achado sobre o sistema físico, que
justifica tratar a auditoria de rótulo como etapa de governança e não como
mero pré-processamento estatístico.

Toda aplicação futura sobre chamados novos permanece condicionada à
inclusão de variável temporal na extração, à validação em período
posterior ao corte avaliado, ao monitoramento de deriva de vocabulário e
de taxonomia, à recalibração periódica dos limiares de confiança, ao
retreinamento a cada mudança relevante da taxonomia e à manutenção da
auditoria humana como instância final de decisão.

**6. CONSIDERAÇÕES FINAIS**

A contribuição central deste artigo é metodológica: um protocolo que
separa a concordância com o rótulo histórico do acerto contra a referência
humana revisada, mede as duas grandezas sob a mesma execução e usa
partições agrupadas por texto que impedem a repetição de chamados entre
treino e teste. Essa separação evita tratar o histórico como referência
inquestionável e, ao mesmo tempo, impede concluir que toda divergência da
classificação automática representa correção do registro original.

O achado central é duplo. Na avaliação sobre 13.972 chamados em 41
categorias, o LinearSVC alcança 0,8253 de acurácia (IC95%: 0,8115--0,8378)
e lidera com significância estatística, mas sem vencedor absoluto quando
acurácia, macro-F1 e custo são considerados em conjunto (Subseção 4.1). E a
reclassificação automática da base histórica produz ganho líquido negativo
nos sete modelos, veredito que se sustenta mesmo sob custos assimétricos
(Subseção 4.2).

A implicação operacional é dupla. No corte avaliado, o LinearSVC constitui
o principal candidato a piloto controlado com calibração isotônica e
automação seletiva, condicionado à validação temporal, ao monitoramento de
deriva e à auditoria humana, regime em que cerca de dois terços do volume
poderiam ser decididos automaticamente com acurácia próxima de 0,95 e o
restante encaminhado à revisão humana; e usar a divergência entre modelo e
histórico não para reescrever a base, mas para priorizar a fila de
auditoria, com enriquecimento de cerca de quatro vezes sobre a revisão
aleatória. Ambas as recomendações permanecem condicionadas à ausência de
validação temporal (Subseção 5.3).

As limitações mais consequentes são o avaliador único sem segunda
avaliação independente, a ausência de validação temporal pela falta de
data de abertura no corpus congelado, e o alcance restrito a uma única
instituição, idioma e taxonomia (Subseção 5.3). Nenhuma delas invalida o
protocolo: qualifica o que ele já entrega e delimita o que ainda depende
de trabalho futuro para ser afirmado.

A continuidade da tese depende de reconstituir o corte preservando a data
de abertura, o que viabiliza avaliação em períodos sucessivos, de
incorporar segunda avaliação humana com adjudicação nos pares taxonômicos
ambíguos, de testar a validação externa em outras instituições e de
avançar, sob infraestrutura com acelerador gráfico, a execução *out-of-fold*
integral do BERTimbau, hoje limitada a experimento exploratório. Feitas
essas etapas, a camada classificada e auditável poderá sustentar modelos de
previsão de demanda, de custo e de priorização multicritério de
intervenções sobre o biossistema construído.

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

