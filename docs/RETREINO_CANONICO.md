# Retreino canônico dos sete modelos

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Estado:** `apto_para_regras`  
**Gerado em:** 03/08/2026 22:44  
**Melhor macro-F1:** linear_svc

## Protocolo

- predicoes out-of-fold sobre as particoes canonicas do Passo 3; rotulo e a referencia humana revisada; nenhum modelo treina no grupo textual que preve.
- Semente: 42.
- Linhas avaliadas: 13972, em 9734 grupos textuais e 5 dobras.
- Categorias: 41.
- Linhas da aba fora das partições canônicas: 101.
- Linhas com texto editado na aba após o congelamento: 2.

## Desempenho por modelo

| Modelo | Acurácia | Macro-F1 | Acurácia balanceada | Treino (s) | Inferência (s) | Pico de memória (MB) |
|---|---:|---:|---:|---:|---:|---:|
| linear_svc | 0.8255 | 0.6696 | 0.6819 | 22.35 | 6.12 | 43.6 |
| regressao_logistica | 0.8042 | 0.6684 | 0.6997 | 49.04 | 6.25 | 406.1 |
| sgd | 0.8092 | 0.6681 | 0.6998 | 22.5 | 6.12 | 43.6 |
| extra_trees | 0.8052 | 0.638 | 0.616 | 91.8 | 6.8 | 51.3 |
| random_forest | 0.7974 | 0.6165 | 0.5962 | 76.61 | 6.59 | 51.2 |
| lstm | 0.7261 | 0.5266 | 0.5713 | 586.38 | 11.54 | 152.0 |
| naive_bayes | 0.7084 | 0.2952 | 0.2997 | 17.58 | 6.13 | 71.4 |

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
