# Comparações contra a categoria histórica

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Gerado em:** 04/08/2026 18:32  
**Hash do corpus:** `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`

## Protocolo

- comparacoes contra a categoria historica da coluna C, sobre as predicoes out-of-fold da rodada canonica; a referencia humana arbitra quem acerta em cada divergencia.
- Sobre o Kappa: aqui o Kappa e legitimo porque modelo e categoria historica sao fontes independentes; o mesmo nao valeria entre a referencia humana e a categoria historica, que o revisor viu ao decidir.
- Registros: 13972, com 41 categorias na referência e 43 no histórico.

## Concordância com a categoria histórica

| Modelo | Acordo bruto | Kappa de Cohen |
|---|---:|---:|
| linear_svc | 0.7961 | 0.7807 |
| extra_trees | 0.7844 | 0.7665 |
| sgd | 0.7781 | 0.7618 |
| random_forest | 0.7747 | 0.7559 |
| regressao_logistica | 0.7738 | 0.7574 |
| lstm | 0.7017 | 0.6809 |
| naive_bayes | 0.6954 | 0.6653 |

## Ganho líquido de reclassificação

Contado apenas onde a predição diverge do histórico. A referência humana arbitra: corrigido é o caso em que o modelo acerta e o histórico erra.

| Modelo | Divergências | Corrigidos | Prejudicados | Neutros | Ganho líquido |
|---|---:|---:|---:|---:|---:|
| linear_svc | 2849 | 475 | 2321 | 53 | -1846 |
| sgd | 3100 | 489 | 2559 | 52 | -2070 |
| extra_trees | 3012 | 422 | 2519 | 71 | -2097 |
| regressao_logistica | 3161 | 492 | 2621 | 48 | -2129 |
| random_forest | 3148 | 416 | 2658 | 74 | -2242 |
| lstm | 4168 | 426 | 3621 | 121 | -3195 |
| naive_bayes | 4256 | 309 | 3783 | 164 | -3474 |

## Dispersão das predições

| Modelo | Categorias previstas | Entropia normalizada | JS contra o histórico |
|---|---:|---:|---:|
| lstm | 41 | 0.8362 | 0.0167 |
| regressao_logistica | 41 | 0.8045 | 0.0127 |
| sgd | 41 | 0.8023 | 0.0092 |
| linear_svc | 41 | 0.79 | 0.0055 |
| extra_trees | 39 | 0.7466 | 0.0087 |
| random_forest | 39 | 0.7403 | 0.0117 |
| naive_bayes | 22 | 0.6131 | 0.0652 |

## Proveniência

- Predições e categoria histórica: rodada canônica.
- Script: `src/comparacao_historica.py`.
- Nenhuma escrita foi realizada na planilha.
