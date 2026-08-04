# Recortes por tipo de manutenção e por volume

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Gerado em:** 03/08/2026 23:20  
**Hash do corpus:** `3aa42e314459787ef12ccc778dfa1368e89d81c4863108042d59a1a9343ec3ff`

## Critérios

- Tipo: familia da categoria, conforme src/tipo_manutencao.py; Preventiva, Corretiva e Nao manutencao.
- ABC: percentual acumulado de volume, corte A em 0.8 e B em 0.95; a categoria que cruza o corte pertence a classe que ela fecha.
- F1 de recorte: o F1 de um recorte usa apenas os rotulos daquele recorte, mas todos os pares, para que falsos positivos vindos de fora continuem contando.

## Tarefa de tipo

Verdade e predição projetadas para os três tipos. Responde se o modelo distingue a natureza do serviço, independentemente de acertar a folha.

| Modelo | Acurácia | Macro-F1 | Preventiva | Corretiva | Não manutenção |
|---|---:|---:|---:|---:|---:|
| extra_trees | 0.9499 | 0.7996 | 0.9762 | 0.9598 | 0.4629 |
| random_forest | 0.9494 | 0.7941 | 0.9756 | 0.9594 | 0.4473 |
| linear_svc | 0.9436 | 0.8156 | 0.9739 | 0.9542 | 0.5187 |
| naive_bayes | 0.942 | 0.7297 | 0.9661 | 0.9547 | 0.2684 |
| sgd | 0.9349 | 0.8166 | 0.9713 | 0.9465 | 0.5319 |
| regressao_logistica | 0.9311 | 0.8104 | 0.9709 | 0.9431 | 0.5172 |
| lstm | 0.9012 | 0.7457 | 0.9551 | 0.9183 | 0.3638 |

## Recorte por tipo, na tarefa de categoria

| Modelo | Tipo | Categorias | Chamados | Acurácia | Macro-F1 |
|---|---|---:|---:|---:|---:|
| extra_trees | Preventiva | 13 | 4904 | 0.9621 | 0.795 |
| extra_trees | Corretiva | 21 | 8483 | 0.7468 | 0.6545 |
| extra_trees | Não manutenção | 7 | 585 | 0.3368 | 0.2971 |
| linear_svc | Preventiva | 13 | 4904 | 0.9684 | 0.794 |
| linear_svc | Corretiva | 21 | 8483 | 0.7687 | 0.698 |
| linear_svc | Não manutenção | 7 | 585 | 0.4513 | 0.3534 |
| lstm | Preventiva | 13 | 4904 | 0.9417 | 0.7185 |
| lstm | Corretiva | 21 | 8483 | 0.6274 | 0.5083 |
| lstm | Não manutenção | 7 | 585 | 0.3504 | 0.2249 |
| naive_bayes | Preventiva | 13 | 4904 | 0.9058 | 0.5108 |
| naive_bayes | Corretiva | 21 | 8483 | 0.6324 | 0.2144 |
| naive_bayes | Não manutenção | 7 | 585 | 0.1556 | 0.1372 |
| random_forest | Preventiva | 13 | 4904 | 0.9611 | 0.7917 |
| random_forest | Corretiva | 21 | 8483 | 0.7359 | 0.6256 |
| random_forest | Não manutenção | 7 | 585 | 0.3162 | 0.2642 |
| regressao_logistica | Preventiva | 13 | 4904 | 0.9647 | 0.8037 |
| regressao_logistica | Corretiva | 21 | 8483 | 0.7277 | 0.6888 |
| regressao_logistica | Não manutenção | 7 | 585 | 0.5675 | 0.3558 |
| sgd | Preventiva | 13 | 4904 | 0.9664 | 0.8055 |
| sgd | Corretiva | 21 | 8483 | 0.7358 | 0.6857 |
| sgd | Não manutenção | 7 | 585 | 0.5556 | 0.3602 |

## Curva ABC global

| Modelo | Classe | Categorias | Chamados | % do volume | Acurácia | Macro-F1 |
|---|---|---:|---:|---:|---:|---:|
| extra_trees | A | 12 | 11432 | 0.8182 | 0.8455 | 0.7935 |
| extra_trees | B | 12 | 1911 | 0.1368 | 0.6771 | 0.7434 |
| extra_trees | C | 17 | 629 | 0.045 | 0.461 | 0.4539 |
| linear_svc | A | 12 | 11432 | 0.8182 | 0.8544 | 0.821 |
| linear_svc | B | 12 | 1911 | 0.1368 | 0.7405 | 0.7526 |
| linear_svc | C | 17 | 629 | 0.045 | 0.558 | 0.5041 |
| lstm | A | 12 | 11432 | 0.8182 | 0.761 | 0.7431 |
| lstm | B | 12 | 1911 | 0.1368 | 0.6044 | 0.6153 |
| lstm | C | 17 | 629 | 0.045 | 0.461 | 0.311 |
| naive_bayes | A | 12 | 11432 | 0.8182 | 0.8236 | 0.6884 |
| naive_bayes | B | 12 | 1911 | 0.1368 | 0.2292 | 0.2527 |
| naive_bayes | C | 17 | 629 | 0.045 | 0.0715 | 0.0477 |
| random_forest | A | 12 | 11432 | 0.8182 | 0.8396 | 0.7849 |
| random_forest | B | 12 | 1911 | 0.1368 | 0.6667 | 0.7344 |
| random_forest | C | 17 | 629 | 0.045 | 0.4277 | 0.4145 |
| regressao_logistica | A | 12 | 11432 | 0.8182 | 0.8195 | 0.7992 |
| regressao_logistica | B | 12 | 1911 | 0.1368 | 0.7802 | 0.7549 |
| regressao_logistica | C | 17 | 629 | 0.045 | 0.5978 | 0.5149 |
| sgd | A | 12 | 11432 | 0.8182 | 0.8264 | 0.8027 |
| sgd | B | 12 | 1911 | 0.1368 | 0.7739 | 0.7546 |
| sgd | C | 17 | 629 | 0.045 | 0.6041 | 0.512 |

## Proveniência

- Origem: `docs/dados/retreino_canonico_predicoes.csv`.
- Script: `src/recortes_canonicos.py`.
- Nenhum modelo foi retreinado e nenhuma escrita foi feita na planilha.
