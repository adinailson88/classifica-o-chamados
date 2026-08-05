# Inferência pareada no nível do grupo textual

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Gerado em:** 05/08/2026 00:55  
**Hash do corpus:** `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`

## 1. Auditoria da unidade estatística

- Unidade anterior: linha (chamado individual).
- Unidade adotada: grupo de texto normalizado idêntico.
- 13972 linhas em 9735 grupos; tamanho médio 1.4352, maior grupo 219.
- 4546 linhas (32.54%) pertencem a grupos com mais de um membro e não são independentes entre si.

| Modelo | Acurácia | EP por linha | EP por grupo | Efeito de desenho |
|---|---:|---:|---:|---:|
| Extra Trees | 0.8073 | 0.003337 | 0.00741 | 4.932 |
| LinearSVC | 0.8253 | 0.003212 | 0.006794 | 4.473 |
| LSTM | 0.7287 | 0.003761 | 0.010175 | 7.317 |
| Naive Bayes | 0.7088 | 0.003844 | 0.011419 | 8.827 |
| Random Forest | 0.797 | 0.003403 | 0.007751 | 5.188 |
| Regressão Logística | 0.805 | 0.003352 | 0.0075 | 5.007 |
| SGD | 0.8093 | 0.003324 | 0.007319 | 4.849 |

Efeito de desenho entre 4.473 e 8.827. efeito de desenho acima de 1 indica que a suposição de independência entre linhas estreita artificialmente a precisão; os valores de p do McNemar por linha herdam esse estreitamento.

## 2. Teste global

Q de Cochran = 2661.0353, 6 graus de liberdade. Referência empírica com 2000 permutações do rótulo de modelo por grupo textual: p < 0.0005. O p da distribuição qui-quadrado por linha seria 0.

a estatística Q permanece adequada por ser pareada e binária, mas a distribuição qui-quadrado tabelada pressupõe independência entre registros, violada aqui; a referência passa a ser empírica, obtida por permutação do rótulo de modelo dentro de cada grupo textual.

## 3. Comparações pareadas

Cada par é orientado pelo modelo de maior acurácia, de modo que a diferença relatada é sempre positiva. O valor de p vem da permutação por troca de sinal da diferença por grupo e é corrigido por Holm sobre os 21 pares. A última coluna traz o p do McNemar por linha, corrigido pela mesma família, apenas para dimensionar o estreitamento que a suposição de independência produzia.

| Par | Δ acurácia (p.p.) | IC95% da diferença | Grupos a favor do 1º | a favor do 2º | Empates | d pareado | p ajustado (grupo) | p ajustado (linha) |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| LinearSVC × Naive Bayes | 11.65 | [+0.1028; +0.1329] | 1961 | 549 | 7225 | 0.1644 | 0.0021 | 0 |
| SGD × Naive Bayes | 10.05 | [+0.0871; +0.1163] | 1924 | 737 | 7074 | 0.1402 | 0.0021 | 0 |
| Extra Trees × Naive Bayes | 9.86 | [+0.0856; +0.1141] | 1636 | 468 | 7631 | 0.1413 | 0.0021 | 0 |
| LinearSVC × LSTM | 9.66 | [+0.0875; +0.1061] | 1682 | 349 | 7704 | 0.3133 | 0.0021 | 0 |
| Regressão Logística × Naive Bayes | 9.63 | [+0.0826; +0.1121] | 1970 | 842 | 6923 | 0.1332 | 0.0021 | 0 |
| Random Forest × Naive Bayes | 8.82 | [+0.0753; +0.1035] | 1559 | 540 | 7636 | 0.1263 | 0.0021 | 0 |
| SGD × LSTM | 8.05 | [+0.0724; +0.0891] | 1537 | 429 | 7769 | 0.261 | 0.0021 | 0 |
| Extra Trees × LSTM | 7.86 | [+0.0704; +0.0873] | 1622 | 533 | 7580 | 0.2428 | 0.0021 | 0 |
| Regressão Logística × LSTM | 7.63 | [+0.0684; +0.0846] | 1505 | 456 | 7774 | 0.2467 | 0.0021 | 0 |
| Random Forest × LSTM | 6.82 | [+0.0604; +0.0763] | 1555 | 615 | 7565 | 0.2094 | 0.0021 | 0 |
| LinearSVC × Random Forest | 2.83 | [+0.0229; +0.0341] | 896 | 503 | 8336 | 0.1076 | 0.0021 | 0 |
| LinearSVC × Regressão Logística | 2.03 | [+0.0156; +0.0248] | 598 | 314 | 8823 | 0.0941 | 0.0021 | 0 |
| LinearSVC × Extra Trees | 1.8 | [+0.0130; +0.0232] | 759 | 515 | 8461 | 0.0707 | 0.0021 | 0 |
| LinearSVC × SGD | 1.6 | [+0.0118; +0.0204] | 533 | 308 | 8894 | 0.0774 | 0.0021 | 0 |
| SGD × Random Forest | 1.23 | [+0.0071; +0.0176] | 767 | 599 | 8369 | 0.0467 | 0.0021 | 2.1e-05 |
| Extra Trees × Random Forest | 1.04 | [+0.0073; +0.0134] | 301 | 152 | 9282 | 0.0679 | 0.0021 | 0 |
| SGD × Regressão Logística | 0.42 | [+0.0019; +0.0067] | 161 | 102 | 9472 | 0.0369 | 0.0035 | 0.00139 |
| LSTM × Naive Bayes | 2.0 | [+0.0068; +0.0352] | 1487 | 1408 | 6840 | 0.0272 | 0.0164 | 4e-06 |
| Regressão Logística × Random Forest | 0.81 | [+0.0025; +0.0135] | 803 | 694 | 8238 | 0.0293 | 0.0164 | 0.012 |
| Extra Trees × Regressão Logística | 0.23 | [-0.0031; +0.0079] | 718 | 678 | 8339 | 0.0085 | 0.842 | 0.819 |
| SGD × Extra Trees | 0.19 | [-0.0031; +0.0072] | 643 | 624 | 8468 | 0.0076 | 0.842 | 0.819 |

Pares cujo veredito muda ao corrigir a unidade: 0. a inferência por linha e a por grupo concordam no veredito de cada par nesta rodada; o que muda é a magnitude do valor de p, que por linha é anticonservador.

## 4. Proveniência

- Predições: `docs/dados/retreino_canonico_predicoes.csv`.
- Grupos textuais: `docs/dados/grupos_textuais_mapa.csv`, Passo 2.
- Script: `src/inferencia_agrupada.py`.
- Permutações pareadas: 10000; globais: 2000; reamostragens: 2000; semente: 42.
- Nenhum modelo foi retreinado e nenhuma escrita foi feita na planilha.
