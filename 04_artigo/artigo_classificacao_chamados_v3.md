---
header-includes:
  - |
    ```{=latex}
    \usepackage[font=small,labelfont=bf,justification=centering,skip=6pt]{caption}
    % Sem a posicao 'b': figura colocada no rodape estourava a margem inferior.
    \makeatletter
    \def\fps@figure{tp}
    \makeatother
    \renewcommand{\topfraction}{0.85}
    \renewcommand{\textfraction}{0.10}
    \renewcommand{\floatpagefraction}{0.90}
    \setcounter{topnumber}{2}
    \setcounter{totalnumber}{3}
    \raggedbottom
    % O texto usa titulos em negrito, nao comandos de secao, entao o LaTeX nao
    % tem ancora para esvaziar a fila de floats e acaba despejando figuras em
    % paginas onde nao cabem. As barreiras resolvem isso, mas cobram vao no
    % rodape a cada \clearpage, entao ficaram so onde sao estruturais. As que
    % cercam tabelas sao obrigatorias: o pandoc emite longtable, que nao e
    % float e estoura a margem inferior quando divide pagina com figura.
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
categoria originalmente registrada não deve ser tratada como verdade
absoluta, pois pode refletir decisões operacionais ruidosas, taxonomias
sobrepostas, registros incompletos e interpretações heterogêneas entre
equipes. Este artigo propõe um protocolo multimodelo para classificação
de chamados reais de manutenção predial universitária em português
brasileiro, extraídos do sistema institucional da Universidade Federal do
Sul da Bahia. O experimento utiliza 13.965 chamados não vazios,
organizados em 55 categorias históricas. A comparação principal avalia
seis classificadores clássicos baseados em TF-IDF e uma rede neural LSTM
bidirecional por predições *out-of-fold* sobre toda a base. O BERTimbau,
transformador pré-treinado em português, é ajustado e avaliado
separadamente em um *holdout* comum de 1.000 chamados, pois não dispõe de
predições *out-of-fold* materializadas para o corpus integral. O
diferencial metodológico reside na distinção entre concordância com o
histórico administrativo e acerto validado por revisão humana. O acerto
validado, apurado sobre 8.895 decisões, descreve apenas a amostra
conferida e constitui limite superior por construção amostral, dado que
639 casos sem categoria decidida permanecem fora do denominador. Na
comparação integral, o LinearSVC lidera a concordância com o histórico
(80,31%) e o acerto validado (95,27%). No *holdout* comum, o LinearSVC
alcança 78,56% e o BERTimbau 77,46%, sem diferença estatisticamente
significativa pelo teste de McNemar (*p* = 0,510). Os resultados indicam
que o modelo contextual é competitivo no recorte avaliado, mas não há
evidência de superioridade sobre o classificador linear. O custo
computacional permanece dimensão relevante da decisão e favorece modelos
lineares em cenários de texto curto, ruidoso e desbalanceado.

**Palavras-chave:** manutenção predial; classificação de chamados;
processamento de linguagem natural; rótulos ruidosos; validação humana.

**ABSTRACT**

*Automatic classification of building maintenance work orders is a
strategic resource for improving operational triage and evidence-based
governance in public institutions. However, the originally assigned
category in historical service-management databases should not be treated
as unquestionable ground truth because it may reflect noisy operational
decisions, overlapping taxonomies, incomplete records, and heterogeneous
interpretations. This paper proposes a multi-model protocol for
classifying real university building maintenance requests in Brazilian
Portuguese from the Federal University of Southern Bahia. The experiment
uses 13,965 non-empty records organized into 55 historical categories.
The main comparison evaluates six TF-IDF-based classical classifiers and
a bidirectional LSTM through out-of-fold predictions over the complete
corpus. BERTimbau, a Portuguese pre-trained transformer, is fine-tuned and
evaluated separately on a common holdout of 1,000 work orders because
full-corpus out-of-fold predictions are not available for this model. The
methodological contribution is the distinction between agreement with the
administrative history and human-validated accuracy. Human-validated
accuracy is calculated over 8,895 decisions and describes only the
reviewed sample; it is an upper bound by sampling construction because
639 cases without a decided category remain outside the denominator. In
the full-corpus comparison, LinearSVC leads both agreement with history
(80.31%) and human-validated accuracy (95.27%). In the common holdout,
LinearSVC reaches 78.56% and BERTimbau 77.46%, with no statistically
significant difference under McNemar's test (p = 0.510). The contextual
model is therefore competitive in the evaluated subset, but there is no
evidence that it outperforms the linear classifier. Computational cost
remains a relevant decision dimension and favors linear models in short,
noisy, and imbalanced text settings.*

***Keywords:** building maintenance; work-order classification; natural
language processing; noisy labels; human validation.*

```{=latex}
\FloatBarrier
```

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

A exploração analítica dessas bases enfrenta ao menos três obstáculos
estruturais, agravados pela restrição orçamentária que historicamente
limita o custeio da manutenção predial em IFES a patamares inferiores a
2% do orçamento institucional (MARTINS; ESPEJO, 2024; PAMPANA *et al.*,
2022). O primeiro é a natureza textual curta, heterogênea e
frequentemente incompleta dos registros. Chamados de manutenção
predial são redigidos em linguagem técnica fragmentária, com
abreviações locais e jargões de equipe que dificultam a aplicação
direta de modelos genéricos de processamento de linguagem natural (PLN)
(SUNDARAM; ZEID, 2025). O segundo é o desbalanceamento entre
categorias. Demandas recorrentes de climatização, elétrica e
hidrossanitária concentram grande parte da base, enquanto categorias
raras dispõem de poucos exemplos para treinamento supervisionado (LI
*et al.*, 2024). O terceiro, e o mais consequente do ponto de vista
metodológico, é a qualidade do próprio rótulo histórico. A categoria
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
BERTimbau também é ajustado, mas sua avaliação permanece em protocolo
*holdout* separado, com métricas próprias rastreáveis, porque não há
predições *out-of-fold* desse modelo sobre toda a base. O
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

```{=latex}
\FloatBarrier
```

**2. REFERENCIAL CONCEITUAL**

```{=latex}
\FloatBarrier
```

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

```{=latex}
\FloatBarrier
```

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

```{=latex}
\FloatBarrier
```

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

```{=latex}
\FloatBarrier
```

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
Em uma instituição pública, essa dimensão é operacionalmente decisiva.
Um modelo que treina em segundos pode ser reexecutado frequentemente,
auditado com facilidade e mantido sem infraestrutura dedicada, ao passo
que um modelo que demanda dezenas de minutos exige *checkpoint*,
controle de versão de pesos e justificativa robusta de ganho marginal
(TREVISO *et al.*, 2023).

```{=latex}
\FloatBarrier
```

**3. MÉTODO**

```{=latex}
\FloatBarrier
```

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

![Pipeline de governança preditiva, do fluxo de extração da base à retroalimentação por validação humana.](04_artigo/figuras/fig_pipeline_governanca.pdf){width=95%}

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
resultados da Seção 4 referem-se ao corpus descrito acima.

**3.3 Pré-processamento textual**

O pré-processamento textual é documentado de modo reprodutível, uma
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

```{=latex}
\FloatBarrier
```

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
pré-treinadas em português brasileiro e é ajustado para as 55 categorias
do corpus (DEVLIN *et al.*, 2019; SOUZA; NOGUEIRA; LOTUFO, 2020). O
treino foi concluído em modo automático, com subamostragem estratificada
e parada antecipada por restrição computacional. Como o modelo não possui
predições *out-of-fold* materializadas sobre toda a base, ele não é
inserido artificialmente no ranking integral dos sete modelos. Sua
comparação é apresentada em protocolo *holdout* comum na Subseção 4.3.

```{=latex}
\FloatBarrier
```

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
histórico (0,8031; Tabela 1) quanto o acerto validado (0,9527; Tabela 2).

O Naive Bayes assume independência condicional entre atributos dada
a classe, suposição estrutural violada em texto de manutenção predial,
onde termos técnicos co-ocorrem de forma sistemática dentro de uma mesma
categoria. Essa divergência entre a suposição do modelo e a estrutura
real dos dados explica de forma plausível a última posição do Naive
Bayes, tanto na concordância com o histórico (0,6997; Tabela 1) quanto
no acerto validado (0,8659; Tabela 2). Trata-se do comportamento
esperado do modelo mais simples da comparação, e não de problema de
implementação.

Random Forest e Extra Trees capturam interações não lineares
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

A LSTM Bidirecional é projetada para modelar dependências
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

```{=latex}
\FloatBarrier
```

**3.5 Desenho de avaliação**

A avaliação se dá por predições fora da amostra em protocolo
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
apresentando suporte de dígito único.

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

A partição por linha, contudo, carrega uma limitação própria neste
corpus. Chamados de manutenção repetem-se, e 32,67% das 13.965 linhas
compartilham texto normalizado com outra linha, de modo que a base
contém 9.714 grupos textuais distintos. Sob particionamento por linha, o
mesmo texto pode cair em treino e em teste, o que superestima o
desempenho. Para dimensionar esse efeito, os sete modelos foram
reexecutados sob *GroupKFold* por hash de texto normalizado, protocolo
que mantém todo grupo textual em uma única partição, e comparados com o
*KFold* por linha sobre a mesma base e o mesmo alvo. O vazamento existe,
mas é pequeno: a queda média de acurácia é de 0,58 ponto percentual e a
máxima de 1,10, no Random Forest. O LinearSVC passa de 0,8031 para
0,7967. A ordenação dos modelos permanece a mesma sob os dois
protocolos, com uma única exceção, a troca de posição entre SGD e Random
Forest, justamente o par que o teste de McNemar corrigido por
Holm-Bonferroni já apontava como estatisticamente indistinguível
(Subseção 4.9). As Tabelas 1 e 2 reportam o protocolo por linha, por
coerência com a materialização em produção, e o material suplementar
traz a comparação completa entre os dois.

A avaliação do BERTimbau segue protocolo adicional e não substitui a
comparação *out-of-fold*. A execução completa mais recente do transformador
define um lote de 1.000 chamados. Os outros sete modelos são retreinados
fora exatamente dessas linhas e avaliados no mesmo conjunto, evitando
sobreposição entre treino e teste. O lote contém 639 chamados com decisão
humana M/N/P/Q. Reportam-se concordância com o histórico, acerto validado,
intervalos por *bootstrap* e McNemar entre o BERTimbau e o melhor modelo
alternativo. Como o lote corresponde aos primeiros registros elegíveis e
não a uma amostra probabilística, os resultados descrevem esse recorte e
não substituem a avaliação integral da base.

```{=latex}
\FloatBarrier
```

**3.6 Validação humana**

A validação humana constitui a etapa que diferencia o presente estudo de
uma simples comparação de classificadores contra histórico. O
processamento da base é organizado em **turnos**, blocos sequenciais de
mil chamados na ordem de registro, unidade em que a concordância é medida
ao longo do corpus e que serve de bloco nos testes por postos da Subseção
4.9. O delineamento por blocos segue a recomendação de Demšar (2006) de
comparar classificadores sobre partições múltiplas, e não sobre uma única
medida agregada. A revisão
registra, para cada caso auditado, a categoria histórica, a categoria
sugerida por cada modelo, a confiança associada, a decisão humana e a
categoria travada.

Duas unidades de análise convivem no protocolo e não devem ser
confundidas. O **chamado** é o registro individual de manutenção, unidade
das Tabelas 1, 2 e 3. A **conferência** é cada julgamento humano emitido
sobre uma fonte de classificação. A decisão M/N/P/Q pode manter o
histórico, aceitar uma classificação automática, aceitar a
reclassificação ou registrar manualmente uma categoria distinta. Dos
13.965 chamados, 9.534 receberam ao menos uma conferência; 8.895 chegaram
a uma categoria decidida e 639 permaneceram restritos, incluindo 201
conflitos entre fontes marcadas como corretas. A priorização recai sobre
chamados em que há divergência entre modelos, alta confiança da IA contra
o histórico, baixa confiança generalizada, classes raras e pares de
categorias com alta confusão recíproca. Essa estrutura permite separar
uma decisão validada de casos ainda sem referência suficiente, em
consonância com a perspectiva de que a verdade operacional deve ser
construída progressivamente (ZHANG *et al.*, 2025).

```{=latex}
\FloatBarrier
```

**3.7 Memória de decisão: veto e trava por chamado**

À medida que a conferência humana avança, o protocolo incorpora uma
memória de decisão por chamado, que evita o reprocessamento de casos já
resolvidos e impede a repetição de erros já identificados. Quando a
conferência confirma que uma categoria está correta, essa decisão é
travada e reaproveitada diretamente nas rodadas seguintes de
reclassificação, sem novo treinamento ou nova predição para aquele
chamado. Quando a conferência identifica que uma categoria está
incorreta, essa categoria passa a ser vetada especificamente para aquele
chamado, e os modelos do repositório passam a escolher
a melhor categoria alternativa fora do conjunto vetado, com a confiança
renormalizada sobre as categorias remanescentes. Essa regra é aplicada
de forma consistente na seleção de candidatos à reclassificação e no
cálculo do ganho líquido, que passa a comparar o resultado da
reclassificação contra a verdade validada quando ela está travada, e
contra o histórico apenas quando ainda não há decisão humana. Essa memória é o mecanismo concreto de
retroalimentação anunciado na Introdução: no biossistema construído, a
conferência humana funciona como o sinal que corrige o próprio sistema de
registro, e não apenas como aferição externa dele. O objetivo
metodológico da memória de decisão é impedir que o sistema corrija um
erro apenas para reincidir nele em ciclos futuros, convertendo cada
conferência manual em conhecimento persistente sobre o experimento, não
em um evento isolado.

```{=latex}
\FloatBarrier
```

**3.8 Camada de entropia de Shannon e divergência de Jensen-Shannon**

Como dimensão complementar às métricas supervisionadas, o protocolo
incorporou uma camada de análise informacional baseada em entropia de
Shannon e divergência de Jensen-Shannon (SHANNON, 1948; LIN, 1991),
calculada exclusivamente sobre agregados públicos e sanitizados, sem
identificador, título ou texto livre do chamado. Essa camada não substitui acurácia,
calibração ou validação humana, pois responde a uma pergunta distinta,
sobre onde modelos, categorias e chamados individuais concentram maior
incerteza estrutural. A entropia opera aqui como medida da desordem
informacional do biossistema construído, no sentido de Shannon (1948),
e o que ela localiza não é erro de modelo, mas a região da taxonomia em
que o próprio sistema de registro perdeu capacidade de discriminar. No nível dos modelos, a entropia de Shannon sobre
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

```{=latex}
\FloatBarrier
```

**3.9 Disponibilidade de dados**

Os artefatos que sustentam os resultados relatados neste artigo são
gerados por um processo automatizado e reproduzível, reexecutado a cada
atualização do experimento. Os chamados analisados têm origem no sistema
institucional GLPI da UFSB e não estão publicamente disponíveis, por
restrição de privacidade institucional. As métricas derivadas e o código
que produz cada figura, tabela e estatística deste artigo são de acesso
público no repositório
https://github.com/adinailson88/classificacao-chamados, que também
descreve a estrutura completa dos dados e o material suplementar citado
neste artigo. Nenhum identificador pessoal, título ou texto livre de chamado
é armazenado nos agregados publicados, e a camada de entropia (Subseção
3.8) opera exclusivamente sobre esses agregados.

```{=latex}
\FloatBarrier
```

**4. RESULTADOS**

Esta seção apresenta três conjuntos de resultados deliberadamente
segregados. O primeiro é a concordância dos sete modelos com a categoria
histórica na base completa (Subseção 4.1), em que o registro do GLPI é
referência preliminar, não verdade absoluta. O segundo é o desempenho
desses mesmos modelos contra a decisão humana M/N/P/Q (Subseção 4.2). O
terceiro é a comparação dos oito modelos no *holdout* comum que inclui o
BERTimbau (Subseção 4.3). A base elegível contém 13.965 chamados. A
conferência humana cobre 9.534 chamados (68,3% da base), dos quais 8.895
têm decisão validada (63,7% da base) e 639 permanecem restritos. Entre os
restritos, 201 apresentam conflito entre fontes marcadas como corretas.

Três achados resumem a seção. Primeiro, o LinearSVC lidera a comparação
integral, tanto em concordância histórica quanto em acerto validado, e
mantém vantagem operacional de custo. Segundo, no *holdout* comum, o
BERTimbau ocupa a segunda posição e não difere significativamente do
LinearSVC, o que caracteriza competitividade sem demonstrar
superioridade. Terceiro, a faixa de confiança igual ou superior a 95%
alcança acerto validado superior a 95%, com as ressalvas de calibração e
seleção amostral discutidas na Subseção 4.4.

```{=latex}
\FloatBarrier
```

**4.1 Concordância com o histórico (base completa)**

A comparação contra a categoria histórica, sobre a base completa (n =
13.965, com intervalo de confiança por bootstrap a 95%), mantém o
LinearSVC na liderança, com acurácia de 0,8031 (IC95%:
0,7963--0,8097), seguido por Extra Trees (0,7894), Random Forest
(0,7816), SGD (0,7767), Regressão Logística (0,7682), Naive Bayes
(0,6997) e LSTM (0,6718). O teste de Cochran Q confirma diferença global
entre os sete modelos avaliados (Q = 2984,07; p < 0,001). A comparação integral exclui o BERTimbau porque o modelo não possui
predições *out-of-fold* sobre as 13.965 linhas; o treino concluído é
avaliado separadamente na Subseção 4.3. O Kappa de Cohen (COHEN, 1960) entre cada
modelo e o histórico reproduz a mesma ordenação, variando de
0,7881 (LinearSVC) a 0,6496 (LSTM), faixa que Landis e Koch (1977)
classificam como concordância substancial. Cabe a ressalva de que o
coeficiente é sensível à prevalência das categorias, o que recomenda
lê-lo ao lado do acordo bruto (WONGPAKARAN *et al.*, 2013). A oitava fonte de classificação, a
classificação automática em produção, mantém concordância de 78,61% e
confiança média de 73,49%, posicionando-se entre Regressão Logística e
SGD nesta métrica. A comparação direta com o LSTM *out-of-fold* da
Tabela 1 não é apropriada porque essa fonte combina a rede neural com a
regra de contingência do Random Forest (Subseção 3.4), em vez de um
único modelo isolado.

**Tabela 1** Concordância com a categoria histórica por modelo (n = 13.965).

| Modelo | Acurácia | IC95% |
|---|---|---|
| LinearSVC | 0,8031 | 0,7963 -- 0,8097 |
| Extra Trees | 0,7894 | 0,7825 -- 0,7961 |
| Random Forest | 0,7816 | 0,7749 -- 0,7881 |
| SGD | 0,7767 | 0,7700 -- 0,7835 |
| Regressão Logística | 0,7682 | 0,7613 -- 0,7751 |
| Naive Bayes | 0,6997 | 0,6923 -- 0,7071 |
| LSTM (out-of-fold) | 0,6718 | 0,6637 -- 0,6796 |

A concordância com o histórico não é uniforme entre as 55 categorias. O
desempenho por categoria, incluindo suporte, precisão, revocação e F1,
está disponível no material suplementar. O desempenho concentra-se nas classes de maior volume. As
cinco categorias com maior F1 pertencem todas à Manutenção Preventiva,
com destaque para Gerador (F1 = 0,9908; suporte = 1.211) e Quadros
Elétricos (F1 = 0,9869; suporte = 576). No extremo oposto, as cinco
categorias de menor F1 reúnem Sistema Fotovoltaico, Manutenção Preventiva
sem subcategoria, Instalações Especiais, Transporte e Drenagem, todas com
F1 inferior a 0,14. Essa leitura pede cautela, pois quatro dessas cinco
categorias têm suporte igual ou inferior a sete registros, condição em
que pequena variação absoluta altera fortemente a métrica.

```{=latex}
\FloatBarrier
```

**4.2 Ranking validado por conferência humana**

A avaliação contra a decisão humana M/N/P/Q utiliza 8.895 chamados com
categoria decidida. O LinearSVC permanece o melhor modelo isolado, com
acerto validado de 0,9527 (IC95%: 0,9482--0,9569), seguido por SGD
(0,9442), Regressão Logística (0,9404), Extra Trees (0,9314), Random
Forest (0,9268), LSTM (0,8872) e Naive Bayes (0,8659). A diferença entre
o primeiro e o segundo colocado é de 0,85 ponto percentual e é
estatisticamente significativa (McNemar, *p* < 0,001). Foram avaliados
também três *ensembles*: maioria ponderada (0,9493), confiança calibrada
máxima (0,9484) e maioria simples (0,9467). Todos ficam abaixo do
LinearSVC, com McNemar *p* < 0,05 em favor do modelo isolado. A
recomendação é, portanto, usar o LinearSVC isolado, com calibração.

O número pontual constitui limite superior condicionado ao desenho da
validação. Dos 9.534 chamados conferidos, 639 (6,7%) permanecem sem
categoria decidida. Esse conjunto reúne 340 casos em que apenas o
histórico foi marcado como errado, 98 em que histórico e classificação
automática foram marcados como errados e 201 conflitos entre fontes
marcadas como corretas. Sem categoria manual adicional, esses registros
não oferecem referência contra a qual medir o acerto e ficam fora do
denominador de 8.895 decisões.

A análise de sensibilidade incorpora os 639 restritos ao denominador como
erro de todos os modelos, cenário conservador que produz um limite
inferior. O LinearSVC varia de 0,8888 a 0,9527, o SGD de 0,8810 a 0,9442,
a Regressão Logística de 0,8774 a 0,9404, o Extra Trees de 0,8690 a
0,9314, o Random Forest de 0,8647 a 0,9268, o LSTM de 0,8278 a 0,8872 e
o Naive Bayes de 0,8078 a 0,8659. A amplitude varia de 5,80 a 6,39
pontos percentuais, mas o ranking relativo permanece inalterado. A
conclusão sobre qual modelo priorizar é robusta ao cenário conservador;
os valores absolutos exigem a ressalva amostral.

**Tabela 2** Acerto validado por modelo e limite inferior de
sensibilidade ao viés de seleção (n = 8.895). O limite inferior inclui os
639 casos restritos como erro de todos os modelos.

| Modelo | Acerto validado | IC95% | Limite inferior |
|---|---|---|---|
| LinearSVC | 0,9527 | 0,9482 -- 0,9569 | 0,8888 |
| SGD | 0,9442 | 0,9394 -- 0,9490 | 0,8810 |
| Regressão Logística | 0,9404 | 0,9355 -- 0,9453 | 0,8774 |
| Extra Trees | 0,9314 | 0,9261 -- 0,9365 | 0,8690 |
| Random Forest | 0,9268 | 0,9213 -- 0,9320 | 0,8647 |
| LSTM | 0,8872 | 0,8805 -- 0,8940 | 0,8278 |
| Naive Bayes | 0,8659 | 0,8588 -- 0,8731 | 0,8078 |

**4.3 BERTimbau no holdout comum de oito modelos**

O BERTimbau foi comparado aos sete modelos no mesmo lote de 1.000
chamados, com treino realizado fora dessas linhas. Entre os registros do
lote, 639 possuem decisão humana M/N/P/Q e formam o denominador do acerto
validado. O LinearSVC ocupa a primeira posição, com 0,7856 (IC95%:
0,7527--0,8185), e o BERTimbau a segunda, com 0,7746 (IC95%:
0,7402--0,8075). A diferença é de 1,10 ponto percentual em favor do
LinearSVC e não é estatisticamente significativa (McNemar, *p* = 0,510;
38 discordâncias em que somente o BERTimbau acerta e 45 em que somente o
LinearSVC acerta).

O resultado indica que o pré-treinamento contextual em português torna o
BERTimbau competitivo neste corpus, mas não sustenta superioridade sobre
o classificador linear. A leitura deve permanecer separada do ranking da
Subseção 4.2: o lote corresponde aos primeiros registros elegíveis, não é
probabilístico e não cobre o corpus integral. Além disso, o modo
automático do BERTimbau usa subamostragem estratificada e parada
antecipada por limite computacional. A comparação responde se o modelo é
competitivo em um recorte comum, mas não substitui uma execução
*out-of-fold* integral.

**Tabela 3** Comparação dos oito modelos no mesmo holdout (n = 1.000;
n = 639 com decisão validada).

| Modelo | Concordância histórica | Acerto validado | IC95% validado |
|---|---|---|---|
| LinearSVC | 0,6560 | 0,7856 | 0,7527 -- 0,8185 |
| BERTimbau | 0,6520 | 0,7746 | 0,7402 -- 0,8075 |
| Regressão Logística | 0,6280 | 0,7653 | 0,7324 -- 0,7981 |
| SGD | 0,6250 | 0,7621 | 0,7293 -- 0,7950 |
| Extra Trees | 0,6120 | 0,7167 | 0,6808 -- 0,7527 |
| Random Forest | 0,5950 | 0,6948 | 0,6604 -- 0,7308 |
| LSTM | 0,5190 | 0,6526 | 0,6166 -- 0,6886 |
| Naive Bayes | 0,5390 | 0,6354 | 0,5978 -- 0,6714 |

```{=latex}
\FloatBarrier
```

**4.4 Confiança, calibração e faixas de decisão**

A classificação automática em produção mantém erro de calibração
esperado (ECE) de 0,0549 sobre a confiança bruta. A unidade desta
subseção é o chamado. O registro da classificação em produção é
acumulativo, pois cada execução acrescenta uma linha por chamado sem
substituir a anterior, e a leitura considera apenas a última
classificação de cada chamado, de modo que os 13.965 chamados do corpus
entram uma única vez e 8.895 deles têm conferência humana. Segmentada
por faixa de confiança e cruzada com a decisão validada, a faixa igual
ou superior a 95% concentra 5.061 chamados, 36,2% do corpus, com
concordância de 98,70% frente ao histórico e acerto validado de 99,84%
sobre os 4.894 chamados já decididos nessa faixa.
O resultado cumpre a meta de referência do experimento, que associa
confiança igual ou superior a 95% a acerto real igual ou superior a 95%.
Cabe a ressalva de que a confiança empregada é bruta, sem calibração
formal, de modo que a meta é atingida na métrica disponível, não em
confiança calibrada em sentido estrito.

Nas faixas inferiores (Tabela 4), a degradação de desempenho acompanha a
queda de confiança, do patamar de 99,17% na faixa de 90 a 95% até 55,05%
abaixo de 50%. A progressão é monótona nas seis faixas, sem inversão
entre faixas vizinhas, e corrobora a correlação positiva entre
confiança bruta e acerto, quantificada por Spearman entre 0,46 e 0,64
conforme o modelo (Subseção 4.9), mesmo sem calibração formal aplicada a
essa camada.

**Tabela 4** Acerto validado por faixa de confiança. A unidade é o
chamado, 13.965 no total, 8.895 com conferência humana.

| Faixa | n total | Concord. histórico | n validados | Acerto validado |
|---|---|---|---|---|
| < 50% | 3.673 | 43,42% | 634 | 55,05% |
| 50–70% | 1.492 | 74,06% | 632 | 91,77% |
| 70–80% | 912 | 83,99% | 522 | 96,93% |
| 80–90% | 1.593 | 84,43% | 1.126 | 98,67% |
| 90–95% | 1.234 | 94,98% | 1.087 | 99,17% |
| >= 95% | 5.061 | 98,70% | 4.894 | 99,84% |

A Figura 2 apresenta esses mesmos valores em forma gráfica, tornando
visível o descolamento entre concordância com o histórico e acerto
validado nas faixas inferiores de confiança.

![Concordância com o histórico e acerto validado por faixa de confiança bruta da classificação automática.](04_artigo/figuras/fig_confianca_desfecho.pdf){width=95%}

```{=latex}
\FloatBarrier
```

**4.5 Reclassificação e ganho líquido**

A reclassificação dos chamados já conferidos produz resultados
heterogêneos entre modelos, medidos contra a decisão validada quando ela
existe e contra o histórico nos demais casos. O LSTM apresenta o maior
ganho líquido absoluto (+100; 674 corrigidos e 574 prejudicados), seguido
por Regressão Logística (+92) e LinearSVC (+73), e todos os sete modelos
apresentam ganho líquido positivo (Tabela 5), embora o Extra Trees fique
no limiar da neutralidade (+9). Esse resultado não autoriza aplicação
indiscriminada, porque o ganho combina parcelas comparadas contra a
decisão validada e contra o histórico, duas referências de naturezas
distintas. Isso desaconselha a reclassificação em massa por modelo. O
ganho líquido, e não apenas a acurácia agregada, é o critério
operacional adequado para essa decisão, e deve ser recalculado a cada
atualização da base.

**Tabela 5** Ganho líquido de reclassificação por modelo.

| Modelo | Corrigidos | Prejudicados | Ganho líquido |
|---|---|---|---|
| LSTM | 674 | 574 | +100 |
| Regressão Logística | 245 | 153 | +92 |
| LinearSVC | 291 | 218 | +73 |
| Random Forest | 234 | 186 | +48 |
| SGD | 201 | 163 | +38 |
| Naive Bayes | 158 | 132 | +26 |
| Extra Trees | 237 | 228 | +9 |

**4.6 Diagnóstico de taxonomia e ambiguidade estrutural
(Shannon/Jensen-Shannon)**

O diagnóstico de Shannon abrange oito fontes comparáveis, a
classificação automática em produção e os sete modelos com predições
sobre toda a base. O BERTimbau foi excluído dessa análise porque não
possui predições integrais materializadas. Duas leituras
distintas emergem da Tabela 6. O LSTM apresenta a maior diversidade de
categorias previstas, com entropia normalizada de 0,8213, ao passo que o
LinearSVC exibe a menor divergência de Jensen-Shannon frente à
distribuição histórica (0,0043). Dispersão de predições e aderência
distributiva ao histórico, portanto, não caminham juntas, e o modelo de
melhor acerto validado é justamente o de distribuição mais próxima da
base. No nível de chamado individual, 3.268 dos 13.965 registros (23,4%)
apresentam alta entropia de votos entre as oito fontes, ou seja,
desacordo estrutural relevante entre arquiteturas distintas. Constitui
critério de priorização de auditoria distinto e complementar à baixa
confiança de um único modelo.

No nível de categoria, a análise aponta 77 ocorrências de alta
ambiguidade nas predições, com suporte mínimo de 30 registros por
categoria. A Figura 3 traduz esse diagnóstico em leitura direta, ao
contrastar as dez categorias de maior e de menor concordância entre as 39
com suporte suficiente. O contraste é acentuado. Nas dez melhores, a
concordância varia de 96,23% a 98,34%, com confiança média de 0,915 e
65,6% das predições emitidas acima do limiar de 95%. Nas dez piores, a
concordância cai para a faixa de 14,47% a 67,83%, a confiança média
recua para 0,463 e apenas 3,9% das predições atingem o limiar alto. Os
dois grupos têm porte semelhante, 5.213 e 6.247 chamados, de modo que a
diferença não decorre de escassez de exemplos.

![Concordância com o histórico, confiança média e proporção de predições em alta confiança, para as dez categorias de maior e de menor concordância entre as 39 com suporte mínimo de 30 chamados.](04_artigo/figuras/fig_calor_categorias.pdf){width=91%}

O padrão que emerge é sistemático, não aleatório. Sete das dez categorias
de maior concordância pertencem a Manutenção Preventiva, cujos chamados
nascem de rotina programada e recebem descrição padronizada. As de menor
concordância concentram rótulos de fronteira aberta, como Instalação e
reparo de equipamentos (14,47%), Outros (26,47%) e Alvenaria, Pisos e
Estrutura (34,28%), que competem por vocabulário com categorias vizinhas.
A confiança acompanha a concordância nos dois extremos, o que reforça a
correlação já reportada na Subseção 4.4 e indica que o classificador
reconhece a própria incerteza nessas fronteiras. Trata-se, portanto, de
ambiguidade estrutural da taxonomia, não apenas de erro do modelo, na
linha do que Zhang *et al.* (2025) descrevem para rótulos ruidosos em
processamento de linguagem natural.

A Figura 4 recorta a matriz de confusão sobre as oito categorias mais
envolvidas em troca recíproca e mostra que os erros não se espalham pela
taxonomia. A célula dominante registra 1.305 chamados de Climatização,
Ar condicionado split, preditos como Manutenção Preventiva, Ar
condicionado split. As duas categorias descrevem o mesmo equipamento e
se distinguem apenas pela natureza da intervenção, corretiva ou
programada, distinção que o texto do chamado raramente explicita. Outras
concentrações seguem a mesma lógica de vizinhança semântica, com 815
chamados de Instalação e reparo de equipamentos preditos como Alvenaria,
Pisos e Estrutura, e 707 no sentido inverso, entre Alvenaria e
Esquadrias. A leitura da matriz é assimétrica em vários pares, o que
sugere absorção de uma categoria por outra, e não simples permuta.

![Recorte da matriz de confusão sobre as oito categorias mais envolvidas em troca recíproca, com contagens agregadas entre modelos.](04_artigo/figuras/fig_matriz_confusao.pdf)

Esses dois recortes sustentam a mesma conclusão operacional. O
desempenho agregado das Tabelas 1 e 2 esconde heterogeneidade relevante
entre categorias, fenômeno que a *macro*-F1 e a *balanced accuracy*
foram adotadas para capturar (SOKOLOVA; LAPALME, 2009). Quando a queda
de desempenho se concentra em fronteiras taxonômicas específicas, e não
de modo difuso, a resposta adequada não é substituir o classificador,
mas revisar a taxonomia. A interpretação qualitativa de cada par
identificado, bem como a decisão de fundir ou redefinir categorias,
permanece humana. O que a camada Shannon e essas duas figuras oferecem é
a priorização estatística de onde essa inspeção deve começar. O Naive
Bayes chama atenção por
combinar a menor cobertura de categorias, apenas 17 contra 43 a 51 dos
demais modelos, com entropia normalizada relativamente alta (0,8157).
Trata-se de provável reflexo de concentração extrema em poucas
categorias com dispersão residual entre elas, e também da maior
divergência frente ao histórico observada na Tabela 6 (0,1024).

A Figura 5 mostra os quinze pares de categorias com maior confusão
recíproca, dominados pela fronteira entre climatização corretiva e
manutenção preventiva de ar condicionado, seguida pelas fronteiras
internas de estrutura predial.

![Quinze pares de categorias com maior confusão recíproca, agregados entre modelos. Os códigos do eixo vertical estão descritos no material suplementar.](04_artigo/figuras/fig_top_confusoes.pdf){width=95%}

![Trade-off entre acerto validado e tempo de treino, modelos clássicos.](04_artigo/figuras/fig_tradeoff_custo.pdf){width=95%}

```{=latex}
\FloatBarrier
```

**Tabela 6** Entropia de Shannon e divergência de Jensen-Shannon por
fonte de classificação.

| Fonte | Categorias previstas | Entropia normalizada | JS vs. histórico |
|---|---|---|---|
| LSTM | 51 | 0,8213 | 0,0427 |
| Classificação automática | 51 | 0,8089 | 0,0241 |
| Regressão Logística | 49 | 0,7906 | 0,0194 |
| SGD | 51 | 0,7806 | 0,0108 |
| LinearSVC | 50 | 0,7666 | 0,0043 |
| Extra Trees | 46 | 0,7217 | 0,0212 |
| Random Forest | 43 | 0,7279 | 0,0260 |
| Naive Bayes | 17 | 0,8157 | 0,1024 |

**4.7 Custo computacional**

Nos recortes de comparação por lote (1.000 registros cada), os seis
modelos clássicos tiveram tempos de treino entre 1,14 s e 21,30 s. Não
há medição padronizada de custo para LSTM ou BERTimbau no mesmo ambiente
e protocolo, portanto não é possível ordená-los frente aos demais. A tabela informa
exclusivamente as medições disponíveis para os modelos clássicos.

**Tabela 7** Custo computacional por lote de 1.000 registros. A acurácia
refere-se ao lote, não à base completa.

| Modelo | Tempo de treino (s) | Tempo de inferência (s) | Acurácia neste lote |
|---|---|---|---|
| Naive Bayes | 1,14 | 0,07 | 0,539 |
| LinearSVC | 2,55 | 0,06 | 0,655 |
| SGD | 2,60 | 0,09 | 0,624 |
| Regressão Logística | 9,43 | 0,09 | 0,624 |
| Random Forest | 19,45 | 0,13 | 0,597 |
| Extra Trees | 21,30 | 0,14 | 0,610 |

A Figura 6 cruza essas medições de custo com o acerto validado da Tabela
2 e mostra que o LinearSVC ocupa a posição mais favorável, com o maior
acerto validado a um custo de treino próximo do menor observado.

```{=latex}
\FloatBarrier
```

**4.8 Comportamento do LSTM: curva de aprendizado e *ablation***

A Figura 7 mostra a curva real de aprendizado do LSTM sobre os 13.965
exemplos e 53 categorias. O treino parou por interrupção antecipada após
11 épocas, com menor perda de validação na época 8 e maior acurácia de
validação na época 10 (0,6722). O padrão indica saturação precoce,
consistente com a hipótese de que *embeddings* treinados do zero são
insuficientes para um corpus deste porte (Subseção 3.4.1).

![Curva de aprendizado do LSTM por época, perda e acurácia em treino e validação.](04_artigo/figuras/fig_curva_aprendizado_lstm.pdf){width=95%}

O *ablation* de hiperparâmetros exige cuidado adicional de
particionamento neste corpus. Chamados de manutenção repetem-se com
frequência, e 46,72% das linhas validadas têm duplicata textual
normalizada em outra parte da base. Uma partição aleatória por linha
colocaria o mesmo texto em treino e teste, inflando o resultado. O
*ablation* usa, por isso, *GroupKFold* por hash de texto normalizado,
que mantém todo grupo textual em uma única partição. Sob esse protocolo,
a configuração adotada em produção (64 unidades, *dropout* de 0,5)
alcança 86,35% de acerto validado, e a partição aleatória equivalente
produziria 87,68%, diferença de 1,33 ponto percentual que dimensiona o
vazamento evitado.

As quatro variantes testadas separam-se por menos de 4 pontos
percentuais entre a melhor e a pior (Figura 8), o que indica baixa
sensibilidade do LSTM ao número de unidades recorrentes e à taxa de
*dropout* nesta base. A limitação do modelo, portanto, não está no
ajuste desses hiperparâmetros, mas na ausência de *embeddings*
pré-treinados discutida na Subseção 3.4.1.

![*Ablation* do LSTM, quatro variantes de unidades recorrentes e *dropout*, avaliadas por *GroupKFold* contra a decisão validada.](04_artigo/figuras/fig_ablation_lstm.pdf){width=95%}

**4.9 Robustez estatística: pressupostos e testes de sensibilidade**

Antes de qualquer teste inferencial, foram verificados os pressupostos de
robustez estatística usuais, a saber, outliers (TUKEY, 1977; HODGE;
AUSTIN, 2004), homogeneidade de variância, normalidade, desbalanceamento
entre categorias, colinearidade entre modelos, relação entre confiança e
acerto e independência das observações, adaptando o protocolo de
exploração de dados de Zuur, Ieno e Elphick (2010) da resposta contínua da ecologia para a resposta
categórica de classificação de chamados (n = 13.965). O teste de
Shapiro-Wilk (SHAPIRO; WILK, 1965) foi escolhido por reunir o maior
poder entre os testes de normalidade usuais nas comparações de Razali e
Wah (2011) e de Ogunleye, Oyejola e Obisesan (2018). Ele rejeita a
normalidade a 5% para os sete modelos sobre a concordância por turno, confirmando com números a
justificativa não paramétrica já adotada na Subseção 3.5; a variância de
confiança entre modelos também é fortemente heterogênea, reforçando essa
escolha. O teste de Friedman (FRIEDMAN, 1937) confirma diferença global
entre os modelos comparáveis, e o *post-hoc* de Nemenyi (NEMENYI, 1963)
reproduz a mesma ordem das Tabelas 1 e 2, com poder estatístico menor que
o McNemar par a par (MCNEMAR, 1947). Corrigido por Holm-Bonferroni
(HOLM, 1979), o McNemar é significativo em praticamente todas as 21
comparações entre os sete modelos, e confirma que o LinearSVC é
estatisticamente superior ao LSTM e ao Naive Bayes. A única exceção,
sem significância, é o par SGD contra Random Forest. A verificação de
colinearidade revela um efeito colateral relevante. Quatro dos sete
modelos têm confiança altamente correlacionada entre si, com Fator de
Inflação de Variância elevado (MARQUARDT, 1970), cujos limiares
convencionais devem ser lidos com a cautela recomendada por O'Brien
(2007), o que ajuda a explicar
por que nenhum *ensemble* supera o LinearSVC isolado (Subseção 4.2),
dado que modelos redundantes pouco acrescentam em informação
independente a um comitê (DIETTERICH, 2000). A correlação entre confiança bruta e acerto é
positiva e significativa em todos os sete modelos, com Spearman entre
0,46 e 0,64 e ponto-bisserial entre 0,43 e 0,66 (*p* < 0,001 em ambos;
KORNBROT, 2014),
pré-requisito para a calibração discutida
na Subseção 4.4 (GUO *et al.*, 2017; MINDERER *et al.*, 2021). A verificação completa dos oito
pressupostos, item a item, com as tabelas de correlação, a verificação de
autocorrelação serial (DURBIN; WATSON, 1950) e o Kappa de Fleiss (FLEISS,
1971) entre modelos, está disponível como Material
Suplementar.

```{=latex}
\FloatBarrier
```

**5. DISCUSSÃO**

```{=latex}
\FloatBarrier
```

**5.1 Concordância histórica, acerto validado e BERTimbau**

A comparação entre concordância histórica (Subseção 4.1) e desempenho
validado (Subseção 4.2) revela que as duas grandezas não são
intercambiáveis. O acerto validado do LinearSVC (95,27%) supera sua
concordância com o histórico (80,31%) em 14,96 pontos percentuais. Essa
diferença não pode ser interpretada como taxa de erro do histórico, pois
a amostra conferida é não probabilística e a própria regra de decisão
condiciona quais casos recebem categoria de referência.

O mecanismo estrutural aparece nos 639 chamados restritos, equivalentes a
6,7% dos 9.534 conferidos. Eles incluem casos em que todas as fontes
avaliadas foram rejeitadas e 201 conflitos entre fontes marcadas como
corretas. A análise de sensibilidade os trata como erro de todos os
modelos e encontra amplitudes entre 5,80 e 6,39 pontos percentuais, sem
alterar o ranking. Assim, a escolha qualitativa do LinearSVC permanece
robusta, mas o valor pontual de acerto validado deve ser sempre
acompanhado da ressalva amostral.

O desenho atual também não permite estimar uma taxa empírica de erro do
rótulo histórico. Quando o histórico é marcado como errado e nenhuma
categoria alternativa é decidida, o chamado permanece restrito; sem o
preenchimento da categoria manual Q, não há referência final para afirmar
qual fonte acertou. A hipótese de rótulos potencialmente ruidosos continua
fundamentada na literatura e justifica a conferência, mas não deve ser
apresentada como taxa confirmada por esta amostra (KEJRIWAL *et al.*,
2024; ZHANG *et al.*, 2025).

A avaliação do BERTimbau acrescenta uma terceira perspectiva. No mesmo
*holdout*, o transformador alcança 77,46% de acerto validado, contra
78,56% do LinearSVC, sem diferença significativa. O pré-treinamento
contextual reduz a distância observada entre modelos lineares e a LSTM
que aprende *embeddings* do zero, mas não produz ganho demonstrável sobre
o LinearSVC. Como os protocolos são distintos, a métrica do BERTimbau não
deve ser comparada diretamente aos 95,27% da avaliação integral. O
resultado sustenta sua competitividade e justifica uma futura execução
*out-of-fold* completa, não sua adoção preferencial imediata.

```{=latex}
\FloatBarrier
```

**5.2 Reclassificação, ambiguidade taxonômica e calibração**

O resultado da reclassificação (Subseção 4.5) introduz uma nuance
operacional importante, pois o ganho líquido de corrigir chamados já
classificados não é uniforme entre modelos. A amplitude vai de +9 no
Extra Trees a +100 no LSTM, e a ordenação por ganho não reproduz a
ordenação por acerto validado, o que mostra que classificar bem e
recorrigir bem são capacidades distintas. Decisões de reclassificação em
produção devem ser tomadas por modelo e reavaliadas a cada atualização
da base, com base no ganho líquido medido naquele momento, e não
generalizadas a partir do desempenho médio de concordância ou acerto
validado. Um modelo pode ser competitivo na classificação inicial e,
ainda assim, não ser bom candidato a reclassificar decisões já tomadas.

A camada de entropia de Shannon e divergência de Jensen-Shannon
(Subseção 4.6) não substitui as métricas supervisionadas ou a validação
humana, mas amplia o repertório de governança do experimento ao separar
três fenômenos que a acurácia isolada tende a confundir: o erro de
modelo, a ambiguidade genuína da taxonomia institucional e a
heterogeneidade natural da distribuição de chamados. A identificação de
3.268 chamados (23,4% da base) com alto desacordo estrutural entre as
oito fontes comparáveis oferece um critério de priorização de auditoria
distinto do simples corte por baixa confiança de um único classificador,
e complementa a fila já construída a partir da conferência humana. A
dispersão das predições e a aderência à distribuição histórica separam-se
neste corpus, pois o LSTM lidera a diversidade de categorias previstas e
o LinearSVC apresenta a menor divergência frente ao histórico (Subseção
4.6). Esse diagnóstico descreve o corpus analisado e não substitui
acurácia ou validação humana.

A meta estabelecida como critério de sucesso do protocolo associa
confiança calibrada igual ou superior a 95% a acerto real igual ou
superior a 95% (Subseção 4.4). A faixa alta de confiança da classificação
automática atinge 99,84% de acerto validado sobre 4.894 chamados
conferidos, o que cumpre o critério na métrica disponível. Duas ressalvas
qualificam essa leitura. A confiança utilizada é bruta (*softmax* ou
*decision_function*), sem calibração formal por Platt ou isotônica
(PLATT, 1999; GUO *et al.*, 2017), de modo que o requisito de confiança
calibrada permanece pendente em sentido estrito. Além disso, a faixa
concentra 36,2% dos chamados e é justamente aquela em que a
conferência tende a confirmar o esperado.

O cumprimento da meta deve ser lido como propriedade do corpus
analisado, não como garantia de operação. A amostra validada cobre 68,3%
da base e sua composição privilegia divergências e casos de menor
confiança, de modo que a fração ainda não conferida pode deslocar o
resultado. Liberar a faixa alta para decisão automática exige concluir
essa conferência e aplicar calibração formal por modelo.

```{=latex}
\FloatBarrier
```

**5.3 Limitações**

Os dados provêm de uma única instituição federal de ensino superior, com
textos em português brasileiro e taxonomia institucional própria.
Estender o desempenho relatado a outras instituições, taxonomias ou
idiomas exige validação externa.

A amostra conferida por avaliadores humanos não é probabilística, pois
prioriza divergências entre modelo e histórico e casos de maior
criticidade. Os números de acerto validado descrevem a amostra conferida,
e não estimam por inferência o desempenho da base completa (COCHRAN,
1977). Dos 9.534 chamados conferidos, 639 permanecem sem categoria
decidida e ficam fora do denominador padrão. A análise de sensibilidade
apura amplitude de 5,80 a 6,39 pontos percentuais entre o cenário
conservador e o valor pontual, sem alterar o ranking relativo.

A regra M/N/P/Q ainda depende do preenchimento manual de uma categoria
quando todas as fontes são rejeitadas ou entram em conflito. Enquanto
essa categoria não é informada, o protocolo não permite quantificar a
taxa de erro do histórico nem atribuir acerto a um modelo nesses casos.
A validação confirma a necessidade de governança sobre os rótulos, mas
não autoriza estimar, com o desenho atual, a prevalência de categorias
históricas incorretas.

As Tabelas 1 e 2 usam particionamento por linha, e não por grupo textual.
A comparação da Subseção 3.5 mostra superestimação média de 0,58 ponto
percentual, sem alteração relevante da ordenação. Os valores absolutos
devem ser lidos com essa margem.

O BERTimbau teve o ajuste fino concluído, mas foi avaliado apenas em um
*holdout* comum de 1.000 chamados, dos quais 639 possuem decisão humana.
Não há predições *out-of-fold* integrais nem medição de custo executada no
mesmo ambiente dos demais modelos, o que impede inseri-lo no ranking
principal ou comparar eficiência computacional de forma direta. A LSTM,
por sua vez, treina *embeddings* do zero, sem vetores pré-treinados em
português, condição que limita a comparação entre arquiteturas neurais.

```{=latex}
\FloatBarrier
```

**5.4 Contribuição para a governança preditiva da manutenção**

A contribuição deste artigo não termina na categoria atribuída a cada
chamado. Ao converter texto livre em categoria, criticidade e confiança
auditáveis, o protocolo produz a camada de dados estruturados sobre a
qual a gestão pública de manutenção predial pode operar de forma
preditiva, e não apenas reativa. Previsão de demanda por categoria,
priorização de intervenções segundo critérios de sustentabilidade e
leitura territorial do parque edificado dependem, todas, de uma base
classificada de modo confiável. Este artigo entrega essa fundação e
demonstra que ela exige conferência humana para se sustentar.

```{=latex}
\FloatBarrier
```

**6. CONSIDERAÇÕES FINAIS**

A contribuição central deste artigo é metodológica. O protocolo separa a
concordância com o rótulo histórico do acerto validado por conferência
humana e registra decisões, vetos e categorias manuais como conhecimento
persistente. Essa camada evita tratar o histórico como verdade automática
e, ao mesmo tempo, impede concluir que toda divergência da IA representa
correção do registro original.

Na avaliação integral de 8.895 chamados com decisão M/N/P/Q, o LinearSVC
alcança 95,27% de acerto validado (IC95%: 94,82%--95,69%) e nenhum dos
três *ensembles* o supera. A análise conservadora que inclui 639 casos
restritos reduz o limite do LinearSVC para 88,88%, sem modificar a
ordenação dos modelos. A recomendação operacional permanece usar o
LinearSVC isolado, com calibração formal antes de automatizar decisões de
alta confiança.

O BERTimbau foi efetivamente treinado e avaliado. No *holdout* comum de
1.000 chamados, com 639 decisões validadas, alcança 77,46%, contra 78,56%
do LinearSVC, sem diferença significativa. O resultado mostra que o
transformador é competitivo, mas não demonstra superioridade e não pode
ser combinado ao ranking integral sem uma execução *out-of-fold* sobre
toda a base.

A finalização metodológica também exige reconhecer o que os dados não
respondem. Como casos sem categoria decidida permanecem restritos, o
desenho atual não estima a taxa de erro do histórico. A próxima etapa de
validação deve preencher a categoria manual Q nesses casos, com prioridade
para conflitos e rejeição de todas as fontes. Em paralelo, a validação
externa em outras instituições e a execução integral do BERTimbau poderão
testar a estabilidade dos resultados sob taxonomias e volumes distintos.
A camada classificada poderá então alimentar modelos de previsão de
demanda e de priorização multicritério de intervenções sobre uma base cuja
incerteza e origem das decisões permanecem auditáveis.

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
