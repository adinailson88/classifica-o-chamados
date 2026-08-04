# Regras preventivas contra modelos puros

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Gerado em:** 03/08/2026 22:44

## Protocolo

- regra aplicada sobre as predicoes out-of-fold do Passo 4, nos mesmos registros e nas mesmas particoes; a referencia humana nao e alterada em nenhuma configuracao.
- Registros: 13972, em 41 categorias, dos quais 4904 têm referência preventiva.
- Regra: dispara somente com termo de periodicidade e termo de equipamento no mesmo chamado; abstem-se caso contrario.
- Tabela com 19 termos de periodicidade e 31 de equipamento, em `src/regras_preventivas.py`.

## Efeito global

| Modelo | Acurácia pura | Acurácia híbrida | Δ | Macro-F1 puro | Macro-F1 híbrido | Δ |
|---|---:|---:|---:|---:|---:|---:|
| linear_svc | 0.8255 | 0.8252 | -0.0003 | 0.6696 | 0.6684 | -0.0012 |
| sgd | 0.8092 | 0.8098 | +0.0006 | 0.6681 | 0.6683 | +0.0002 |
| regressao_logistica | 0.8042 | 0.805 | +0.0008 | 0.6684 | 0.6675 | -0.0009 |
| extra_trees | 0.8052 | 0.8058 | +0.0006 | 0.638 | 0.6355 | -0.0025 |
| random_forest | 0.7974 | 0.798 | +0.0006 | 0.6165 | 0.6127 | -0.0038 |
| lstm | 0.7261 | 0.7343 | +0.0082 | 0.5266 | 0.5364 | +0.0098 |
| naive_bayes | 0.7084 | 0.7222 | +0.0138 | 0.2952 | 0.3538 | +0.0586 |

## Efeito nos chamados de referência preventiva

| Modelo | Acurácia pura | Acurácia híbrida | Δ |
|---|---:|---:|---:|
| extra_trees | 0.9621 | 0.9659 | +0.0038 |
| linear_svc | 0.9684 | 0.9698 | +0.0014 |
| lstm | 0.9417 | 0.967 | +0.0253 |
| naive_bayes | 0.9058 | 0.9466 | +0.0408 |
| random_forest | 0.9611 | 0.9651 | +0.004 |
| regressao_logistica | 0.9647 | 0.97 | +0.0053 |
| sgd | 0.9664 | 0.971 | +0.0046 |

## Conflitos entre regra e modelo

| Modelo | Disparos | Conflitos | Regra acerta | Modelo acerta | Ambos erram |
|---|---:|---:|---:|---:|---:|
| extra_trees | 4487 | 47 | 23 | 15 | 9 |
| linear_svc | 4487 | 28 | 8 | 13 | 7 |
| lstm | 4487 | 145 | 126 | 12 | 7 |
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
