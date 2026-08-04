# Recortes por tipo de manutenção e por volume

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Gerado em:** 04/08/2026 18:32  
**Hash do corpus:** `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`

## Critérios

- Tipo: familia da categoria, conforme src/tipo_manutencao.py; Preventiva, Corretiva e Nao manutencao.
- ABC: percentual acumulado de volume, corte A em 0.8 e B em 0.95; a categoria que cruza o corte pertence a classe que ela fecha.
- F1 de recorte: o F1 de um recorte usa apenas os rotulos daquele recorte, mas todos os pares, para que falsos positivos vindos de fora continuem contando.

## Tarefa de tipo

Verdade e predição projetadas para os três tipos. Responde se o modelo distingue a natureza do serviço, independentemente de acertar a folha.

| Modelo | Acurácia | Macro-F1 | Preventiva | Corretiva | Não manutenção |
|---|---:|---:|---:|---:|---:|
| extra_trees | 0.9497 | 0.7999 | 0.9762 | 0.9596 | 0.4638 |
| random_forest | 0.949 | 0.7907 | 0.9762 | 0.9592 | 0.4367 |
| linear_svc | 0.9443 | 0.818 | 0.9742 | 0.9547 | 0.525 |
| naive_bayes | 0.9421 | 0.7298 | 0.9662 | 0.9548 | 0.2684 |
| sgd | 0.9355 | 0.8173 | 0.9718 | 0.947 | 0.533 |
| regressao_logistica | 0.9317 | 0.8116 | 0.9715 | 0.9437 | 0.5196 |
| lstm | 0.8999 | 0.7403 | 0.9559 | 0.9172 | 0.3478 |

## Recorte por tipo, na tarefa de categoria

| Modelo | Tipo | Categorias | Chamados | Acurácia | Macro-F1 |
|---|---|---:|---:|---:|---:|
| extra_trees | Preventiva | 13 | 4902 | 0.9625 | 0.7979 |
| extra_trees | Corretiva | 21 | 8485 | 0.7498 | 0.6483 |
| extra_trees | Não manutenção | 7 | 585 | 0.3419 | 0.2996 |
| linear_svc | Preventiva | 13 | 4902 | 0.968 | 0.7911 |
| linear_svc | Corretiva | 21 | 8485 | 0.7683 | 0.696 |
| linear_svc | Não manutenção | 7 | 585 | 0.4564 | 0.3579 |
| lstm | Preventiva | 13 | 4902 | 0.961 | 0.7403 |
| lstm | Corretiva | 21 | 8485 | 0.6218 | 0.4899 |
| lstm | Não manutenção | 7 | 585 | 0.3333 | 0.2248 |
| naive_bayes | Preventiva | 13 | 4902 | 0.9062 | 0.5108 |
| naive_bayes | Corretiva | 21 | 8485 | 0.6329 | 0.2142 |
| naive_bayes | Não manutenção | 7 | 585 | 0.1556 | 0.1372 |
| random_forest | Preventiva | 13 | 4902 | 0.9614 | 0.7857 |
| random_forest | Corretiva | 21 | 8485 | 0.7354 | 0.6286 |
| random_forest | Não manutenção | 7 | 585 | 0.3111 | 0.2583 |
| regressao_logistica | Preventiva | 13 | 4902 | 0.9647 | 0.8007 |
| regressao_logistica | Corretiva | 21 | 8485 | 0.7289 | 0.6912 |
| regressao_logistica | Não manutenção | 7 | 585 | 0.5709 | 0.3572 |
| sgd | Preventiva | 13 | 4902 | 0.9665 | 0.8037 |
| sgd | Corretiva | 21 | 8485 | 0.7358 | 0.6839 |
| sgd | Não manutenção | 7 | 585 | 0.5573 | 0.3622 |

## Curva ABC global

| Modelo | Classe | Categorias | Chamados | % do volume | Acurácia | Macro-F1 |
|---|---|---:|---:|---:|---:|---:|
| extra_trees | A | 12 | 11433 | 0.8183 | 0.8488 | 0.7978 |
| extra_trees | B | 12 | 1912 | 0.1368 | 0.6778 | 0.7447 |
| extra_trees | C | 17 | 627 | 0.0449 | 0.4466 | 0.4455 |
| linear_svc | A | 12 | 11433 | 0.8183 | 0.8539 | 0.8207 |
| linear_svc | B | 12 | 1912 | 0.1368 | 0.7416 | 0.7521 |
| linear_svc | C | 17 | 627 | 0.0449 | 0.5582 | 0.5018 |
| lstm | A | 12 | 11433 | 0.8183 | 0.7586 | 0.7435 |
| lstm | B | 12 | 1912 | 0.1368 | 0.636 | 0.6356 |
| lstm | C | 17 | 627 | 0.0449 | 0.4673 | 0.2903 |
| naive_bayes | A | 12 | 11433 | 0.8183 | 0.8239 | 0.688 |
| naive_bayes | B | 12 | 1912 | 0.1368 | 0.2291 | 0.2527 |
| naive_bayes | C | 17 | 627 | 0.0449 | 0.0718 | 0.0477 |
| random_forest | A | 12 | 11433 | 0.8183 | 0.8388 | 0.7839 |
| random_forest | B | 12 | 1912 | 0.1368 | 0.6658 | 0.7312 |
| random_forest | C | 17 | 627 | 0.0449 | 0.4338 | 0.4141 |
| regressao_logistica | A | 12 | 11433 | 0.8183 | 0.8203 | 0.8003 |
| regressao_logistica | B | 12 | 1912 | 0.1368 | 0.7814 | 0.7545 |
| regressao_logistica | C | 17 | 627 | 0.0449 | 0.5981 | 0.5158 |
| sgd | A | 12 | 11433 | 0.8183 | 0.8263 | 0.8025 |
| sgd | B | 12 | 1912 | 0.1368 | 0.7746 | 0.7549 |
| sgd | C | 17 | 627 | 0.0449 | 0.6045 | 0.5091 |

## Proveniência

- Origem: `docs/dados/retreino_canonico_predicoes.csv`.
- Script: `src/recortes_canonicos.py`.
- Nenhum modelo foi retreinado e nenhuma escrita foi feita na planilha.
