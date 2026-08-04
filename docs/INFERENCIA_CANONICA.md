# Inferência estatística da rodada canônica

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Gerado em:** 04/08/2026 19:03  
**Hash do corpus:** `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`

## Protocolo

- Bootstrap: reamostragem de grupos textuais com reposicao, bootstrap de conglomerados; a linha nao e a unidade de reamostragem porque registros do mesmo grupo nao sao independentes.
- Repetições: 1000; semente: 42; nível de significância 0.05.
- Ordem dos testes: Cochran Q global primeiro; McNemar pareado apenas se o Q rejeitar, com Holm sobre os 21 pares.
- Observações: 13972 registros em 9735 grupos textuais, 41 categorias e 7 modelos pareados.

## Intervalos de confiança por bootstrap de grupo

| Modelo | Acurácia | IC 95% | Macro-F1 | IC 95% |
|---|---:|---|---:|---|
| linear_svc | 0.8253 | [0.8115; 0.8378] | 0.6664 | [0.6526; 0.6804] |
| sgd | 0.8093 | [0.795; 0.8227] | 0.665 | [0.651; 0.6788] |
| extra_trees | 0.8073 | [0.7923; 0.8211] | 0.6334 | [0.6177; 0.6498] |
| regressao_logistica | 0.805 | [0.7907; 0.8189] | 0.6671 | [0.6534; 0.6812] |
| random_forest | 0.797 | [0.7812; 0.8111] | 0.6122 | [0.5971; 0.6288] |
| lstm | 0.7287 | [0.708; 0.748] | 0.5223 | [0.5107; 0.5343] |
| naive_bayes | 0.7088 | [0.686; 0.7311] | 0.2961 | [0.2887; 0.3099] |

## Teste global

Cochran Q = 2661.0353, 6 graus de liberdade, p = 0. Hipótese nula: todos os modelos tem a mesma taxa de acerto. Rejeitada, o que autoriza as comparações pareadas.

## McNemar pareado, com correção de Holm

| Par | Discordantes | Só o 1º acerta | Só o 2º acerta | p bruto | p ajustado | Significativo |
|---|---:|---:|---:|---:|---:|---|
| extra_trees × linear_svc | 1287 | 518 | 769 | 3.2e-12 | 0 | sim |
| extra_trees × lstm | 2178 | 1638 | 540 | 3.55e-122 | 0 | sim |
| extra_trees × naive_bayes | 2333 | 1855 | 478 | 1.65e-178 | 0 | sim |
| extra_trees × random_forest | 459 | 302 | 157 | 1.8e-11 | 0 | sim |
| linear_svc × lstm | 2047 | 1698 | 349 | 4.65e-195 | 0 | sim |
| linear_svc × naive_bayes | 2732 | 2180 | 552 | 1.02e-212 | 0 | sim |
| linear_svc × random_forest | 1410 | 903 | 507 | 7.04e-26 | 0 | sim |
| linear_svc × regressao_logistica | 919 | 601 | 318 | 1.37e-20 | 0 | sim |
| linear_svc × sgd | 848 | 536 | 312 | 1.89e-14 | 0 | sim |
| lstm × random_forest | 2191 | 619 | 1572 | 5.89e-92 | 0 | sim |
| lstm × regressao_logistica | 1980 | 457 | 1523 | 1.35e-126 | 0 | sim |
| lstm × sgd | 1985 | 430 | 1555 | 1.97e-140 | 0 | sim |
| naive_bayes × random_forest | 2324 | 546 | 1778 | 8.01e-144 | 0 | sim |
| naive_bayes × regressao_logistica | 3037 | 846 | 2191 | 2.29e-131 | 0 | sim |
| naive_bayes × sgd | 2886 | 741 | 2145 | 2.39e-150 | 0 | sim |
| lstm × naive_bayes | 3129 | 1704 | 1425 | 6.7e-07 | 4e-06 | sim |
| random_forest × sgd | 1382 | 605 | 777 | 4.23e-06 | 2.1e-05 | sim |
| regressao_logistica × sgd | 263 | 102 | 161 | 0.000348 | 0.00139 | sim |
| random_forest × regressao_logistica | 1513 | 700 | 813 | 0.00398 | 0.012 | sim |
| extra_trees × regressao_logistica | 1414 | 723 | 691 | 0.41 | 0.819 | não |
| extra_trees × sgd | 1285 | 629 | 656 | 0.468 | 0.819 | não |

Dos 21 pares, 19 são significativos após Holm e 2 não são. Pares não significativos indicam modelos empatados dentro do poder do teste, e o artigo não deve apresentá-los como ordenados.

## Proveniência

- Predições: `docs/dados/retreino_canonico_predicoes.csv`.
- Grupos textuais: `docs/dados/grupos_textuais_mapa.csv`, Passo 2.
- Script: `src/inferencia_canonica.py`.
- Nenhum modelo foi retreinado e nenhuma escrita foi feita na planilha.
