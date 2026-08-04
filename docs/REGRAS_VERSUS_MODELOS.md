# Regras preventivas contra modelos puros

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Gerado em:** 03/08/2026 21:40

## Protocolo

- regra aplicada sobre as predicoes out-of-fold do Passo 4, nos mesmos registros e nas mesmas particoes; a referencia humana nao e alterada em nenhuma configuracao.
- Registros: 13972, em 41 categorias, dos quais 4904 têm referência preventiva.
- Regra: dispara somente com termo de periodicidade e termo de equipamento no mesmo chamado; abstem-se caso contrario.
- Tabela com 19 termos de periodicidade e 31 de equipamento, em `src/regras_preventivas.py`.

## Efeito global

| Modelo | Acurácia pura | Acurácia híbrida | Δ | Macro-F1 puro | Macro-F1 híbrido | Δ |
|---|---:|---:|---:|---:|---:|---:|
| regressao_logistica | 0.8048 | 0.8056 | +0.0008 | 0.6697 | 0.6689 | -0.0008 |
| sgd | 0.809 | 0.8096 | +0.0006 | 0.6677 | 0.6679 | +0.0002 |
| linear_svc | 0.8252 | 0.8251 | -0.0001 | 0.6683 | 0.6666 | -0.0017 |
| extra_trees | 0.8083 | 0.8087 | +0.0004 | 0.6368 | 0.6324 | -0.0044 |
| random_forest | 0.7992 | 0.7998 | +0.0006 | 0.6183 | 0.6145 | -0.0038 |
| lstm | 0.729 | 0.7313 | +0.0023 | 0.5363 | 0.5391 | +0.0028 |
| naive_bayes | 0.7086 | 0.7224 | +0.0138 | 0.2951 | 0.3536 | +0.0585 |

## Efeito nos chamados de referência preventiva

| Modelo | Acurácia pura | Acurácia híbrida | Δ |
|---|---:|---:|---:|
| extra_trees | 0.9621 | 0.9657 | +0.0036 |
| linear_svc | 0.9676 | 0.9696 | +0.002 |
| lstm | 0.9582 | 0.9664 | +0.0082 |
| naive_bayes | 0.9058 | 0.9466 | +0.0408 |
| random_forest | 0.9608 | 0.9649 | +0.0041 |
| regressao_logistica | 0.9647 | 0.97 | +0.0053 |
| sgd | 0.9666 | 0.9712 | +0.0046 |

## Conflitos entre regra e modelo

| Modelo | Disparos | Conflitos | Regra acerta | Modelo acerta | Ambos erram |
|---|---:|---:|---:|---:|---:|
| extra_trees | 4487 | 46 | 22 | 17 | 7 |
| linear_svc | 4487 | 31 | 11 | 13 | 7 |
| lstm | 4487 | 60 | 41 | 9 | 10 |
| naive_bayes | 4487 | 219 | 201 | 9 | 9 |
| random_forest | 4487 | 50 | 25 | 16 | 9 |
| regressao_logistica | 4487 | 46 | 26 | 14 | 6 |
| sgd | 4487 | 44 | 24 | 15 | 5 |

## Leitura

A camada híbrida melhora o macro-F1 de 3 dos 7 modelos: lstm, naive_bayes, sgd.

A regra dispara no mesmo conjunto de registros para todos os modelos, porque depende apenas do texto. O que varia entre as linhas é a predição que ela substitui, e por isso o mesmo conjunto de regras ajuda um modelo e pode prejudicar outro.

## Proveniência

- Predições: `docs/dados/retreino_canonico_predicoes.csv`, Passo 4.
- Regras: `src/regras_preventivas.py`.
- Script: `src/comparar_regras_modelos.py`.
- Nenhuma escrita foi realizada na planilha.
