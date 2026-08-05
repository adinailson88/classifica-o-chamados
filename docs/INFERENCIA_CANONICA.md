# Inferência estatística da rodada canônica

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Gerado em:** 04/08/2026 21:09  
**Hash do corpus:** `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`

## Protocolo

- Bootstrap: reamostragem de grupos textuais com reposicao, bootstrap de conglomerados; a linha nao e a unidade de reamostragem porque registros do mesmo grupo nao sao independentes.
- Repetições: 1000; semente: 42; nível de significância 0.05.
- Ordem dos testes: Cochran Q global primeiro; McNemar pareado apenas se o Q rejeitar, com Holm sobre os 21 pares.
- Observações: 13972 registros em 9735 grupos textuais, 41 categorias e 7 modelos pareados.

## Intervalos de confiança por bootstrap de grupo

Três grandezas distintas, e a coluna de cada uma é declarada: a estimativa **observada** na amostra inteira, a **média** das mil reamostragens e o **intervalo** de percentil. O artigo reporta a estimativa observada ao lado do intervalo; a média das reamostragens não deve substituí-la.

| Modelo | Acurácia obs. | Média boot. | IC 95% | Macro-F1 obs. | Média boot. | IC 95% |
|---|---:|---:|---|---:|---:|---|
| linear_svc | 0.8253 | 0.8248 | [0.8115; 0.8378] | 0.6684 | 0.6664 | [0.6526; 0.6804] |
| sgd | 0.8093 | 0.8088 | [0.795; 0.8227] | 0.6669 | 0.665 | [0.651; 0.6788] |
| extra_trees | 0.8073 | 0.8069 | [0.7923; 0.8211] | 0.6362 | 0.6334 | [0.6177; 0.6498] |
| regressao_logistica | 0.805 | 0.8046 | [0.7907; 0.8189] | 0.6689 | 0.6671 | [0.6534; 0.6812] |
| random_forest | 0.797 | 0.7965 | [0.7812; 0.8111] | 0.6152 | 0.6122 | [0.5971; 0.6288] |
| lstm | 0.7287 | 0.7281 | [0.708; 0.748] | 0.524 | 0.5223 | [0.5107; 0.5343] |
| naive_bayes | 0.7088 | 0.7084 | [0.686; 0.7311] | 0.2951 | 0.2961 | [0.2887; 0.3099] |

## Contagem de grupos textuais

| Contagem | Valor |
|---|---:|
| Grupos congelados no recorte avaliado (unidade do bootstrap) | 9735 |
| Grupos no mapa de partições, recalculados sobre o texto vivo | 9734 |
| Registros cujo grupo vivo diverge do congelado | 2 |

as contagens divergem quando o texto de um chamado e editado na aba viva depois do congelamento; a contagem congelada e a reproduzivel e e a usada como unidade de reamostragem

## Consenso entre os modelos

- Unanimidade (os sete modelos preveem a mesma categoria): 8444 registros, 0.6044.
- Desacordo estrutural (tres ou mais categorias distintas entre as sete predicoes): 2285 registros, 0.1635.
- Entropia média normalizada dos votos: 0.1422.

## Confiança bruta contra acerto

| Modelo | n | Spearman | Ponto-bisserial |
|---|---:|---:|---:|
| extra_trees | 13972 | 0.5272 | 0.5569 |
| linear_svc | 13972 | 0.485 | 0.45 |
| lstm | 13972 | 0.616 | 0.656 |
| naive_bayes | 13972 | 0.6077 | 0.6277 |
| random_forest | 13972 | 0.5391 | 0.5644 |
| regressao_logistica | 13972 | 0.4809 | 0.4819 |
| sgd | 13972 | 0.4941 | 0.4847 |

Spearman entre 0.4809 e 0.616; ponto-bisserial entre 0.45 e 0.656. Todos positivos e significativos: sim.

## Pressupostos

Shapiro-Wilk sobre subamostra de 5000 observações, semente 42. Fator de Inflação de Variância entre as confianças dos modelos, limiar convencional de 10.0.

| Modelo | Shapiro W | Rejeita normalidade | Variância | VIF |
|---|---:|---|---:|---:|
| extra_trees | 0.8606 | sim | 0.07235 | 20.784 |
| linear_svc | 0.9209 | sim | 0.00456 | 4.208 |
| lstm | 0.8211 | sim | 0.08336 | 3.109 |
| naive_bayes | 0.8335 | sim | 0.08463 | 4.016 |
| random_forest | 0.8633 | sim | 0.0764 | 22.322 |
| regressao_logistica | 0.87 | sim | 0.10777 | 26.91 |
| sgd | 0.9057 | sim | 0.09031 | 29.984 |

Normalidade rejeitada em 7 dos 7 modelos. Levene = 4216.75, p = 0: homogeneidade de variância rejeitada. VIF acima do limiar em 4 modelos: extra_trees, random_forest, regressao_logistica, sgd.

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
