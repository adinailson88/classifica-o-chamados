# Material Suplementar — classificação automática de chamados

## S5. Robustez estatística: diagnósticos e testes complementares

Antes dos testes inferenciais, foram verificados *outliers*, homogeneidade de variância, normalidade, desbalanceamento entre categorias, colinearidade entre modelos, relação entre confiança e acerto e independência das observações, segundo adaptação do protocolo de exploração de dados de Zuur, Ieno e Elphick (2010) para respostas categóricas.

O teste de Shapiro-Wilk (SHAPIRO; WILK, 1965) rejeitou a normalidade a 5% para os sete modelos sobre a concordância por turno. A variância da confiança também apresentou heterogeneidade entre os classificadores. Esses resultados fundamentam o emprego de procedimentos não paramétricos.

O teste de Friedman (FRIEDMAN, 1937) identificou diferença global entre os modelos. O pós-teste de Nemenyi (NEMENYI, 1963) reproduziu a ordenação observada nas métricas principais, embora com menor poder que as comparações pareadas. O teste de McNemar (MCNEMAR, 1947), corrigido pelo método de Holm-Bonferroni (HOLM, 1979), foi significativo na maior parte das 21 comparações entre os sete modelos. Os resultados confirmam a superioridade estatística do LinearSVC sobre LSTM e Naive Bayes; o par SGD versus Random Forest não apresentou diferença significativa.

A análise de colinearidade mostrou correlação elevada da confiança entre quatro dos sete modelos, expressa por fatores de inflação de variância elevados (MARQUARDT, 1970). Essa redundância ajuda a explicar por que os comitês avaliados não superaram o LinearSVC isolado (DIETTERICH, 2000). A confiança bruta apresentou correlação positiva e significativa com o acerto em todos os modelos, tanto por Spearman quanto por correlação ponto-bisserial (*p* < 0,001), fornecendo base empírica para a calibração formal (GUO *et al.*, 2017).

As tabelas estatísticas completas, incluindo correlações, autocorrelação, Kappa de Fleiss, postos médios e comparações pareadas, permanecem nos arquivos derivados disponíveis no repositório do estudo.

## Checklist de itens reportados

O checklist foi transferido do manuscrito principal e pode ser utilizado como documento de conformidade editorial quando solicitado pelo periódico.

| Item | Localização no manuscrito | Situação |
|---|---|---|
| Fonte de dados e sistema de origem | Seções 3.1 e 3.2 | Reportado |
| Tamanho da amostra e categorias | Seção 3.2 | Reportado |
| Critérios de inclusão dos registros | Seção 3.2 | Reportado |
| Pré-processamento textual | Seção 3.3 | Reportado |
| Modelos e justificativa conceitual | Seções 3.4 e 3.4.1 | Reportado |
| Particionamento *out-of-fold* | Seção 3.5 | Reportado |
| Comparação com *holdout* | Seção 3.5 e Tabela Suplementar S4 | Reportado |
| Métricas e intervalos de confiança | Seção 3.5 | Reportado |
| Testes estatísticos e correção para comparações múltiplas | Seção 4.10 e Material Suplementar | Reportado |
| Verificação de pressupostos | Material Suplementar S5 | Reportado |
| Protocolo de validação humana | Seção 3.6 | Reportado |
| Tratamento de conflitos e memória de decisão | Seção 3.7 | Reportado |
| Confiança bruta e calibração planejada | Seções 3.8 e 4.4 | Reportado |
| Reprodutibilidade e disponibilidade | Seção 3.9 | Reportado |
| Limitações | Seção 5 | Reportado |
| Figuras e tabelas derivadas de agregados verificáveis | Seção 4 | Reportado |
