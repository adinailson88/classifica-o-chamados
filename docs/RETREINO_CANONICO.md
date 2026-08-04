# Retreino canônico dos sete modelos

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Estado:** `apto_para_regras`  
**Gerado em:** 03/08/2026 20:33  
**Melhor macro-F1:** regressao_logistica

## Protocolo

- predicoes out-of-fold sobre as particoes canonicas do Passo 3; rotulo e a referencia humana revisada; nenhum modelo treina no grupo textual que preve.
- Semente: 42.
- Linhas avaliadas: 13972, em 9734 grupos textuais e 5 dobras.
- Categorias: 41.
- Linhas da aba fora das partições canônicas: 101.

## Desempenho por modelo

| Modelo | Acurácia | Macro-F1 | Acurácia balanceada | Treino (s) | Inferência (s) | Pico de memória (MB) |
|---|---:|---:|---:|---:|---:|---:|
| regressao_logistica | 0.8048 | 0.6697 | 0.7005 | 61.74 | 6.49 | 405.8 |
| linear_svc | 0.8252 | 0.6683 | 0.6804 | 23.5 | 6.46 | 43.4 |
| sgd | 0.809 | 0.6677 | 0.6997 | 24.3 | 6.5 | 43.4 |
| extra_trees | 0.8083 | 0.6368 | 0.6156 | 115.84 | 7.07 | 51.0 |
| random_forest | 0.7992 | 0.6183 | 0.5985 | 99.29 | 6.82 | 51.0 |
| lstm | 0.729 | 0.5363 | 0.5878 | 414.64 | 11.66 | 147.0 |
| naive_bayes | 0.7086 | 0.2951 | 0.2996 | 17.81 | 6.27 | 71.1 |

Os tempos somam as cinco dobras e refletem a máquina do executor; servem para comparar modelos entre si, não como medida absoluta de custo.

## Validações

| Verificação | Ocorrências |
|---|---:|
| modelos com vazamento de grupo | 0 |
| modelos com registro sem predicao | 0 |
| linhas do corpus sem rotulo | 0 |

## Proveniência

- Python 3.11.15 em Linux-6.17.0-1020-azure-x86_64-with-glibc2.39.
- Dependências: numpy 1.26.4, sklearn 1.5.2, tensorflow 2.17.0.
- Partições: `docs/dados/particoes_canonicas_mapa.csv`, Passo 3.
- Predições por registro: `docs/dados/retreino_canonico_predicoes.csv`, com SHA-256 do ID.
- Script: `src/retreinar_modelos_canonicos.py`.
- Nenhuma escrita foi realizada na planilha.
