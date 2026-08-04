# Regras preventivas contra modelos puros

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Gerado em:** 04/08/2026 18:32

## Protocolo

- regra aplicada sobre as predicoes out-of-fold do Passo 4, nos mesmos registros e nas mesmas particoes; a referencia humana nao e alterada em nenhuma configuracao.
- Registros: 13972, em 41 categorias, dos quais 4902 têm referência preventiva.
- Regra: dispara somente com termo de periodicidade e termo de equipamento no mesmo chamado; abstem-se caso contrario.
- Tabela com 19 termos de periodicidade e 31 de equipamento, em `src/regras_preventivas.py`.

## Efeito global

| Modelo | Acurácia pura | Acurácia híbrida | Δ | Macro-F1 puro | Macro-F1 híbrido | Δ |
|---|---:|---:|---:|---:|---:|---:|
| regressao_logistica | 0.805 | 0.806 | +0.001 | 0.6689 | 0.6686 | -0.0003 |
| sgd | 0.8093 | 0.81 | +0.0007 | 0.6669 | 0.6676 | +0.0007 |
| linear_svc | 0.8253 | 0.8252 | -0.0001 | 0.6684 | 0.6667 | -0.0017 |
| extra_trees | 0.8073 | 0.8077 | +0.0004 | 0.6362 | 0.6324 | -0.0038 |
| random_forest | 0.797 | 0.7975 | +0.0005 | 0.6152 | 0.6114 | -0.0038 |
| lstm | 0.7287 | 0.7305 | +0.0018 | 0.524 | 0.5267 | +0.0027 |
| naive_bayes | 0.7088 | 0.7225 | +0.0137 | 0.2951 | 0.3537 | +0.0586 |

## Efeito nos chamados de referência preventiva

| Modelo | Acurácia pura | Acurácia híbrida | Δ |
|---|---:|---:|---:|
| extra_trees | 0.9625 | 0.9657 | +0.0032 |
| linear_svc | 0.968 | 0.97 | +0.002 |
| lstm | 0.961 | 0.967 | +0.006 |
| naive_bayes | 0.9062 | 0.947 | +0.0408 |
| random_forest | 0.9614 | 0.9651 | +0.0037 |
| regressao_logistica | 0.9647 | 0.9702 | +0.0055 |
| sgd | 0.9665 | 0.9714 | +0.0049 |

## Conflitos entre regra e modelo

| Modelo | Disparos | Conflitos | Regra acerta | Modelo acerta | Ambos erram |
|---|---:|---:|---:|---:|---:|
| extra_trees | 4487 | 47 | 22 | 17 | 8 |
| linear_svc | 4487 | 31 | 11 | 13 | 7 |
| lstm | 4487 | 53 | 31 | 7 | 15 |
| naive_bayes | 4487 | 219 | 201 | 9 | 9 |
| random_forest | 4487 | 48 | 23 | 16 | 9 |
| regressao_logistica | 4487 | 47 | 27 | 14 | 6 |
| sgd | 4487 | 45 | 25 | 15 | 5 |

## Leitura

A camada híbrida melhora o macro-F1 de 3 dos 7 modelos: lstm, naive_bayes, sgd.

A regra dispara no mesmo conjunto de registros para todos os modelos, porque depende apenas do texto. O que varia entre as linhas é a predição que ela substitui, e por isso o mesmo conjunto de regras ajuda um modelo e pode prejudicar outro.

## Proveniência

- Predições: `docs/dados/retreino_canonico_predicoes.csv`, Passo 4.
- Regras: `src/regras_preventivas.py`.
- Script: `src/comparar_regras_modelos.py`.
- Nenhuma escrita foi realizada na planilha.
