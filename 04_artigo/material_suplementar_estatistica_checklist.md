# Material Suplementar — classificação automática de chamados

## S5. Robustez estatística: diagnósticos e testes complementares

Antes de qualquer teste inferencial, verificamos os pressupostos de
robustez estatística usuais — outliers, homogeneidade de variância,
normalidade, desbalanceamento entre categorias, colinearidade entre
modelos, relação entre confiança e acerto, e independência das
observações —, adaptando o protocolo de exploração de dados de Zuur,
Ieno e Elphick (2010) da resposta contínua da ecologia para a resposta
categórica de classificação de chamados (n = 13.965). O teste de
Shapiro-Wilk (SHAPIRO; WILK, 1965) rejeita a normalidade a 5% para os
sete modelos sobre a concordância por turno, confirmando com números a
justificativa não paramétrica já adotada na Subseção 3.5; a variância de
confiança entre modelos também é fortemente heterogênea, reforçando essa
escolha. O teste de Friedman (FRIEDMAN, 1937) confirma diferença global
entre os modelos comparáveis, e o *post-hoc* de Nemenyi (NEMENYI, 1963)
reproduz a mesma ordem das Tabelas 1 e 2, com poder estatístico menor que
o McNemar par a par (MCNEMAR, 1947) — que, corrigido por
Holm-Bonferroni (HOLM, 1979), é significativo em praticamente todas as
21 comparações entre os sete modelos, confirmando que o **LinearSVC é
estatisticamente superior ao LSTM e ao Naive Bayes** (a única exceção,
sem significância, é o par SGD vs. Random Forest). A verificação de
colinearidade mostra um efeito colateral relevante: quatro dos sete
modelos têm confiança altamente correlacionada entre si (Fator de
Inflação de Variância elevado; MARQUARDT, 1970), o que ajuda a explicar
por que nenhum *ensemble* supera o LinearSVC isolado (Subseção 4.2) —
modelos redundantes contribuem pouco em informação independente a um
comitê (DIETTERICH, 2000). A correlação entre confiança bruta e acerto é
positiva e significativa em todos os sete modelos (Spearman e
ponto-bisserial, *p* < 0,001), pré-requisito para a calibração discutida
na Subseção 4.4 (GUO *et al.*, 2017). A verificação completa dos oito
pressupostos, item a item, com as tabelas de correlação, autocorrelação
e o Kappa de Fleiss entre modelos, está disponível como Material
Suplementar.

## Checklist de itens reportados

Adaptado do espírito do checklist tipo PRISMA-ScR do artigo-modelo de revisão
(MCDM/TOPSIS/ODS/ESG) para relato de experimento de classificação supervisionada
com validação humana. Cada item indica a subseção onde é reportado e o status desta consolidação.
Os números foram sincronizados com os JSONs vigentes, mas devem ser
revalidados antes da submissão caso ocorra nova materialização dos dados.

| Item | Subseção | Reportado? |
|---|---|---|
| Fonte de dados e sistema de origem declarados | 3.1, 3.2 | Sim (GLPI/UFSB) |
| Tamanho da amostra e corte de consolidação | 3.2 | Sim (n = 13.965; agregados vigentes) |
| Critério de inclusão/exclusão de registros | 3.2 | Parcial — "chamados não vazios" declarado; demais critérios não detalhados |
| Pré-processamento textual | 3.3 | Sim |
| Modelos avaliados e hiperparâmetros principais | 3.4 | Sim (7 materializados + 1 em extensão) |
| Justificativa conceitual das diferenças de desempenho entre modelos | 3.4.1 | Sim |
| Método de particionamento (out-of-fold, k-fold, seed) | 3.5 | Sim (out-of-fold, KFold embaralhado, `random_state=42`; sem estratificação) |
| Justificativa da escolha k-fold vs. holdout fixo, com comparação empírica | 3.5 | Sim (KOHAVI, 1995; Tabela Suplementar S4) |
| Métricas reportadas e justificativa | 3.5 | Sim (acurácia, macro-F1, balanced accuracy, IC95% bootstrap) |
| Testes estatísticos e correção para múltiplas comparações | 3.5, 4.10 | Sim — resultados numéricos completos em 4.10 |
| Verificação explícita de pressupostos (normalidade, homogeneidade, colinearidade, independência) | 4.10 | Sim — protocolo de Zuur, Ieno e Elphick (2010) adaptado; detalhamento completo em Material Suplementar |
| Critério de calibração de confiança (bruta vs. calibrada) e meta de desempenho | 3.8, 4.4 | Parcial — meta declarada (>= 95%/>= 95%); calibração formal (Platt/isotônica) ainda não aplicada |
| Protocolo de validação humana | 3.6 | Sim |
| Cobertura da validação humana (n e % da base) | 4 (abertura) | Sim (9.534 conferidos; 9.044 decisões; 52 conflitos) |
| Tratamento de conflitos de conferência | 3.7 | Sim (regra de veto/trava) |
| Reprodutibilidade (scripts e dados versionados) | 3.9 | Sim (repositório público, JSONs sanitizados) |
| Limitações declaradas | 5, 6 | Sim |
| Figuras/tabelas geradas a partir de dados verificáveis | 4.8 | Sim (scripts leem os JSONs vigentes do painel) |

\newpage
