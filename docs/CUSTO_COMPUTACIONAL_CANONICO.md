# Custo computacional sobre a base canônica

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Gerado em:** 04/08/2026 18:32  
**Hash do corpus:** `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`

## Desenho

- treino unico sobre a base completa, repetido 3 vezes, com a mediana reportada; nao e a soma das dobras da validacao cruzada.
- Corpus: 13972 linhas em 41 categorias.
- 3.11.15 em Linux-6.17.0-1020-azure-x86_64-with-glibc2.39.
- Dependências: numpy 1.26.4, sklearn 1.5.2, tensorflow 2.17.0.

## Tempos por modelo

| Modelo | Treino (s) | Faixa | Inferência (s) | Faixa | Razão para o mais rápido |
|---|---:|---|---:|---|---:|
| naive_bayes | 1.12 | 1.12–1.12 | 0.89 | 0.89–0.9 | 1.0× |
| sgd | 2.28 | 2.27–2.28 | 0.93 | 0.93–0.95 | 2.0× |
| linear_svc | 2.44 | 2.41–2.46 | 0.89 | 0.88–0.89 | 2.2× |
| regressao_logistica | 8.43 | 8.43–8.46 | 0.92 | 0.91–0.92 | 7.5× |
| random_forest | 22.62 | 22.62–22.66 | 1.34 | 1.31–1.34 | 20.2× |
| extra_trees | 26.69 | 26.63–26.72 | 1.46 | 1.46–1.51 | 23.9× |
| lstm | 83.44 | 70.38–83.63 | 4.89 | 4.89–4.98 | 74.6× |

Medianas de três execuções. A faixa entre mínimo e máximo indica a variação do executor e ajuda a julgar quanto de uma diferença pequena é ruído de máquina.

## Proveniência

- Corpus: mesmo das partições canônicas, fixado por identificador.
- Script: `src/custo_computacional_canonico.py`.
- Nenhuma escrita foi realizada na planilha.
