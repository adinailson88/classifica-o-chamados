# Inferência estatística da rodada canônica

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Gerado em:** 03/08/2026 23:49  
**Hash do corpus:** `3aa42e314459787ef12ccc778dfa1368e89d81c4863108042d59a1a9343ec3ff`

## Protocolo

- Bootstrap: reamostragem de grupos textuais com reposicao, bootstrap de conglomerados; a linha nao e a unidade de reamostragem porque registros do mesmo grupo nao sao independentes.
- Repetições: 1000; semente: 42; nível de significância 0.05.
- Ordem dos testes: Cochran Q global primeiro; McNemar pareado apenas se o Q rejeitar, com Holm sobre os 21 pares.
- Observações: 13972 registros em 9735 grupos textuais, 41 categorias e 7 modelos pareados.

## Intervalos de confiança por bootstrap de grupo

| Modelo | Acurácia | IC 95% | Macro-F1 | IC 95% |
|---|---:|---|---:|---|
| linear_svc | 0.8255 | [0.8119; 0.8384] | 0.6677 | [0.6535; 0.6821] |
| sgd | 0.8092 | [0.7944; 0.8226] | 0.6662 | [0.6522; 0.6802] |
| extra_trees | 0.8052 | [0.7902; 0.819] | 0.635 | [0.6192; 0.6509] |
| regressao_logistica | 0.8042 | [0.7899; 0.8181] | 0.6666 | [0.6536; 0.6804] |
| random_forest | 0.7974 | [0.7816; 0.8115] | 0.6137 | [0.5982; 0.63] |
| lstm | 0.7261 | [0.7061; 0.7464] | 0.5253 | [0.5084; 0.5423] |
| naive_bayes | 0.7084 | [0.6856; 0.7306] | 0.2962 | [0.2889; 0.31] |

## Teste global

Cochran Q = 2669.6664, 6 graus de liberdade, p = 0. Hipótese nula: todos os modelos tem a mesma taxa de acerto. Rejeitada, o que autoriza as comparações pareadas.

## McNemar pareado, com correção de Holm

| Par | Discordantes | Só o 1º acerta | Só o 2º acerta | p bruto | p ajustado | Significativo |
|---|---:|---:|---:|---:|---:|---|
| extra_trees × linear_svc | 1306 | 511 | 795 | 4.84e-15 | 0 | sim |
| extra_trees × lstm | 2333 | 1719 | 614 | 1.26e-115 | 0 | sim |
| extra_trees × naive_bayes | 2326 | 1839 | 487 | 1.15e-172 | 0 | sim |
| linear_svc × lstm | 2131 | 1760 | 371 | 1.29e-198 | 0 | sim |
| linear_svc × naive_bayes | 2718 | 2177 | 541 | 6.84e-216 | 0 | sim |
| linear_svc × random_forest | 1403 | 898 | 505 | 1.25e-25 | 0 | sim |
| linear_svc × regressao_logistica | 924 | 611 | 313 | 1.51e-22 | 0 | sim |
| linear_svc × sgd | 852 | 540 | 312 | 7.43e-15 | 0 | sim |
| lstm × random_forest | 2332 | 668 | 1664 | 2.51e-94 | 0 | sim |
| lstm × regressao_logistica | 2023 | 466 | 1557 | 9.71e-130 | 0 | sim |
| lstm × sgd | 2033 | 436 | 1597 | 5.83e-146 | 0 | sim |
| naive_bayes × random_forest | 2321 | 539 | 1782 | 1.48e-146 | 0 | sim |
| naive_bayes × regressao_logistica | 3036 | 849 | 2187 | 4.59e-130 | 0 | sim |
| naive_bayes × sgd | 2894 | 743 | 2151 | 8.78e-151 | 0 | sim |
| extra_trees × random_forest | 445 | 277 | 168 | 3.06e-07 | 2e-06 | sim |
| lstm × naive_bayes | 3109 | 1678 | 1431 | 1.02e-05 | 6.1e-05 | sim |
| random_forest × sgd | 1417 | 626 | 791 | 1.32e-05 | 6.6e-05 | sim |
| regressao_logistica × sgd | 262 | 96 | 166 | 2.02e-05 | 8.1e-05 | sim |
| random_forest × regressao_logistica | 1543 | 724 | 819 | 0.0167 | 0.0501 | não |
| extra_trees × sgd | 1330 | 637 | 693 | 0.132 | 0.263 | não |
| extra_trees × regressao_logistica | 1460 | 737 | 723 | 0.734 | 0.734 | não |

Dos 21 pares, 18 são significativos após Holm e 3 não são. Pares não significativos indicam modelos empatados dentro do poder do teste, e o artigo não deve apresentá-los como ordenados.

## Proveniência

- Predições: `docs/dados/retreino_canonico_predicoes.csv`.
- Grupos textuais: `docs/dados/grupos_textuais_mapa.csv`, Passo 2.
- Script: `src/inferencia_canonica.py`.
- Nenhum modelo foi retreinado e nenhuma escrita foi feita na planilha.
