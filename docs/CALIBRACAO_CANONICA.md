# Calibração e automação seletiva por confiança

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Gerado em:** 04/08/2026 18:32

## Protocolo

- dobra interna de calibracao: para cada dobra externa f, o modelo e treinado nas dobras que nao sao f nem a interna c, o calibrador e o limiar sao ajustados em c, e so entao f e avaliada.
- Garantia: nenhum registro da dobra externa participa do ajuste do calibrador nem da escolha do limiar.
- Ressalva: o calibrador e ajustado sobre escores de um modelo treinado em tres dobras e aplicado a escores de um modelo treinado em quatro; e a troca entre ausencia de vazamento e casamento exato de distribuicao.
- Registros: 13972, em 5 dobras e 41 categorias.

## Definições

- ECE: Expected Calibration Error com faixas de largura igual: media ponderada, sobre 10 faixas, do modulo da diferenca entre acuracia e confianca media da faixa.
- Brier: escore de Brier binario acerto/erro; pune ma calibracao e baixa resolucao ao mesmo tempo.
- Limiar: menor escore que atinge o alvo de acuracia na dobra interna de calibracao.

## Calibração

| Modelo | Acurácia | ECE bruto | ECE calibrado | Brier bruto | Brier calibrado |
|---|---:|---:|---:|---:|---:|
| extra_trees | 0.8073 | 0.0859 | 0.0108 | 0.1171 | 0.1057 |
| sgd | 0.8093 | 0.3046 | 0.0109 | 0.223 | 0.1124 |
| random_forest | 0.797 | 0.0913 | 0.0145 | 0.1211 | 0.1082 |
| linear_svc | 0.8253 | 0.6925 | 0.0178 | 0.6052 | 0.1034 |
| regressao_logistica | 0.805 | 0.2351 | 0.0189 | 0.1946 | 0.1173 |
| naive_bayes | 0.7088 | 0.0144 | 0.0206 | 0.1252 | 0.128 |
| lstm | 0.7287 | 0.0158 | 0.0479 | 0.1126 | 0.1221 |

## Automação seletiva

### Alvo de acurácia 0.9

| Modelo | Dobras com limiar | Cobertura | Acurácia seletiva | Encaminhamento humano |
|---|---:|---:|---:|---:|
| extra_trees | 5/5 | 0.7912 | 0.9055 | 0.2088 |
| linear_svc | 5/5 | 0.8355 | 0.8992 | 0.1645 |
| lstm | 5/5 | 0.7655 | 0.8598 | 0.2345 |
| naive_bayes | 5/5 | 0.6691 | 0.8822 | 0.3309 |
| random_forest | 5/5 | 0.7831 | 0.9026 | 0.2169 |
| regressao_logistica | 5/5 | 0.7759 | 0.8959 | 0.2241 |
| sgd | 5/5 | 0.7644 | 0.9068 | 0.2356 |

### Alvo de acurácia 0.95

| Modelo | Dobras com limiar | Cobertura | Acurácia seletiva | Encaminhamento humano |
|---|---:|---:|---:|---:|
| extra_trees | 5/5 | 0.6732 | 0.9502 | 0.3268 |
| linear_svc | 5/5 | 0.689 | 0.9464 | 0.311 |
| lstm | 5/5 | 0.6545 | 0.921 | 0.3455 |
| naive_bayes | 5/5 | 0.5518 | 0.9306 | 0.4482 |
| random_forest | 5/5 | 0.658 | 0.9495 | 0.342 |
| regressao_logistica | 5/5 | 0.6237 | 0.9415 | 0.3763 |
| sgd | 5/5 | 0.6162 | 0.9531 | 0.3838 |

### Alvo de acurácia 0.99

| Modelo | Dobras com limiar | Cobertura | Acurácia seletiva | Encaminhamento humano |
|---|---:|---:|---:|---:|
| extra_trees | 5/5 | 0.4541 | 0.9877 | 0.5459 |
| linear_svc | 5/5 | 0.3194 | 0.9823 | 0.6806 |
| lstm | 5/5 | 0.4704 | 0.9735 | 0.5296 |
| naive_bayes | 2/5 | 0.1983 | 0.9747 | 0.8017 |
| random_forest | 5/5 | 0.4463 | 0.9876 | 0.5537 |
| regressao_logistica | 5/5 | 0.3604 | 0.9847 | 0.6396 |
| sgd | 5/5 | 0.3546 | 0.9907 | 0.6454 |

## Curva de confiabilidade do melhor modelo calibrado

Modelo `extra_trees`, após calibração.

| Faixa | Registros | Confiança média | Acurácia |
|---|---:|---:|---:|
| [0.0, 0.1) | 57 | 0.0478 | 0.3333 |
| [0.1, 0.2) | 34 | 0.1505 | 0.0588 |
| [0.2, 0.3) | 199 | 0.2491 | 0.2663 |
| [0.3, 0.4) | 724 | 0.363 | 0.3702 |
| [0.4, 0.5) | 1273 | 0.449 | 0.4643 |
| [0.5, 0.6) | 1223 | 0.5489 | 0.5626 |
| [0.6, 0.7) | 678 | 0.6578 | 0.6534 |
| [0.7, 0.8) | 980 | 0.7473 | 0.748 |
| [0.8, 0.9) | 1047 | 0.8575 | 0.8873 |
| [0.9, 1.0) | 7757 | 0.9805 | 0.9738 |

## Proveniência

- Escores externos: `docs/dados/retreino_canonico_predicoes.csv`, Passo 4.
- Partições: `docs/dados/particoes_canonicas_mapa.csv`, Passo 3.
- Script: `src/calibrar_confianca.py`.
- Nenhuma escrita foi realizada na planilha.
