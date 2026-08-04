# Calibração e automação seletiva por confiança

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Gerado em:** 03/08/2026 22:44

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
| extra_trees | 0.8052 | 0.0834 | 0.0108 | 0.1164 | 0.1053 |
| sgd | 0.8092 | 0.3046 | 0.0116 | 0.223 | 0.1127 |
| random_forest | 0.7974 | 0.0905 | 0.0163 | 0.1207 | 0.1087 |
| linear_svc | 0.8255 | 0.6926 | 0.0173 | 0.6052 | 0.1028 |
| regressao_logistica | 0.8042 | 0.2336 | 0.0191 | 0.1935 | 0.117 |
| naive_bayes | 0.7084 | 0.0143 | 0.0194 | 0.1252 | 0.128 |
| lstm | 0.7261 | 0.0232 | 0.027 | 0.1171 | 0.1201 |

## Automação seletiva

### Alvo de acurácia 0.9

| Modelo | Dobras com limiar | Cobertura | Acurácia seletiva | Encaminhamento humano |
|---|---:|---:|---:|---:|
| extra_trees | 5/5 | 0.7884 | 0.9054 | 0.2116 |
| linear_svc | 5/5 | 0.8344 | 0.9001 | 0.1656 |
| lstm | 5/5 | 0.6817 | 0.9055 | 0.3183 |
| naive_bayes | 5/5 | 0.669 | 0.8817 | 0.331 |
| random_forest | 5/5 | 0.784 | 0.9031 | 0.216 |
| regressao_logistica | 5/5 | 0.7749 | 0.8957 | 0.2251 |
| sgd | 5/5 | 0.7655 | 0.9052 | 0.2345 |

### Alvo de acurácia 0.95

| Modelo | Dobras com limiar | Cobertura | Acurácia seletiva | Encaminhamento humano |
|---|---:|---:|---:|---:|
| extra_trees | 5/5 | 0.679 | 0.9507 | 0.321 |
| linear_svc | 5/5 | 0.6897 | 0.9461 | 0.3103 |
| lstm | 5/5 | 0.5561 | 0.9427 | 0.4439 |
| naive_bayes | 5/5 | 0.5516 | 0.9305 | 0.4484 |
| random_forest | 5/5 | 0.6653 | 0.9464 | 0.3347 |
| regressao_logistica | 5/5 | 0.6239 | 0.9413 | 0.3761 |
| sgd | 5/5 | 0.6154 | 0.9537 | 0.3846 |

### Alvo de acurácia 0.99

| Modelo | Dobras com limiar | Cobertura | Acurácia seletiva | Encaminhamento humano |
|---|---:|---:|---:|---:|
| extra_trees | 5/5 | 0.4621 | 0.9875 | 0.5379 |
| linear_svc | 5/5 | 0.3182 | 0.9825 | 0.6818 |
| lstm | 5/5 | 0.3992 | 0.9729 | 0.6008 |
| naive_bayes | 2/5 | 0.1971 | 0.9749 | 0.8029 |
| random_forest | 5/5 | 0.4639 | 0.9861 | 0.5361 |
| regressao_logistica | 5/5 | 0.364 | 0.9856 | 0.636 |
| sgd | 5/5 | 0.3547 | 0.9905 | 0.6453 |

## Curva de confiabilidade do melhor modelo calibrado

Modelo `extra_trees`, após calibração.

| Faixa | Registros | Confiança média | Acurácia |
|---|---:|---:|---:|
| [0.0, 0.1) | 11 | 0.0175 | 0.0909 |
| [0.1, 0.2) | 60 | 0.1532 | 0.25 |
| [0.2, 0.3) | 513 | 0.245 | 0.2904 |
| [0.3, 0.4) | 298 | 0.334 | 0.3859 |
| [0.4, 0.5) | 1359 | 0.4558 | 0.4511 |
| [0.5, 0.6) | 1568 | 0.552 | 0.5631 |
| [0.6, 0.7) | 375 | 0.6433 | 0.6533 |
| [0.7, 0.8) | 790 | 0.7678 | 0.762 |
| [0.8, 0.9) | 1130 | 0.8369 | 0.8558 |
| [0.9, 1.0) | 7868 | 0.9802 | 0.9736 |

## Proveniência

- Escores externos: `docs/dados/retreino_canonico_predicoes.csv`, Passo 4.
- Partições: `docs/dados/particoes_canonicas_mapa.csv`, Passo 3.
- Script: `src/calibrar_confianca.py`.
- Nenhuma escrita foi realizada na planilha.
