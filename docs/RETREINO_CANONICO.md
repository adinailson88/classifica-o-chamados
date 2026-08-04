# Retreino canônico dos sete modelos

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Estado:** `apto_para_regras`  
**Gerado em:** 04/08/2026 18:32  
**Melhor macro-F1:** regressao_logistica

## Protocolo

- predicoes out-of-fold sobre as particoes canonicas do Passo 3; rotulo e a referencia humana revisada; nenhum modelo treina no grupo textual que preve.
- Semente: 42.
- Linhas avaliadas: 13972, em 9734 grupos textuais e 5 dobras.
- Categorias: 41.
- Linhas da aba fora das partições canônicas: 110.
- Linhas com texto editado na aba após o congelamento: 3.

## Desempenho por modelo

| Modelo | Acurácia | Macro-F1 | Acurácia balanceada | Treino (s) | Inferência (s) | Pico de memória (MB) |
|---|---:|---:|---:|---:|---:|---:|
| regressao_logistica | 0.805 | 0.6689 | 0.6996 | 58.07 | 5.95 | 406.1 |
| linear_svc | 0.8253 | 0.6684 | 0.6805 | 22.06 | 5.72 | 43.6 |
| sgd | 0.8093 | 0.6669 | 0.6988 | 22.0 | 5.86 | 43.6 |
| extra_trees | 0.8073 | 0.6362 | 0.6133 | 118.18 | 6.48 | 51.3 |
| random_forest | 0.797 | 0.6152 | 0.5971 | 103.12 | 6.35 | 51.2 |
| lstm | 0.7287 | 0.524 | 0.5871 | 384.99 | 10.83 | 147.7 |
| naive_bayes | 0.7088 | 0.2951 | 0.2997 | 16.97 | 5.8 | 71.4 |

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
