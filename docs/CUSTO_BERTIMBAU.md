# Custo computacional do BERTimbau sob o protocolo canônico

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Veredito:** `protocolo_integral_inviavel_no_executor_atual`  
**Gerado em:** 03/08/2026 21:55

## O que é medido e o que é extrapolado

- Medido: segundos por passo, taxa de tokenizacao, taxa de inferencia e tempos de carga.
- Extrapolado: tempo por dobra e tempo das cinco dobras, obtidos multiplicando a taxa medida pelo numero de passos.

## Configuração

- Modelo base: `neuralmind/bert-base-portuguese-cased`.
- Épocas 3, comprimento máximo 192, lote 16, taxa 2e-05.
- Dobra medida: 1, com 11214 linhas de treino e 2758 de teste, em 41 categorias.

## Taxas medidas

| Grandeza | Valor |
|---|---:|
| Passos cronometrados | 30 |
| Segundos por passo | 10.774 |
| Faixa por passo (mín–máx) | 10.706–10.824 |
| Amostras/s no treino | 1.49 |
| Amostras/s na inferência | 5.24 |
| Amostras/s na tokenização | 5005.0 |
| Carga do modelo (s) | 4.07 |

## Projeção do protocolo integral

| Grandeza | Valor |
|---|---:|
| Passos por época | 701 |
| Passos por dobra | 2103 |
| Horas por dobra | 6.44 |
| Horas nas cinco dobras | 32.2 |
| Limite de um job do executor (h) | 6.0 |
| Dobras que cabem em um job | 0 |

## Ambiente

- 3.11.15 em Linux-6.17.0-1020-azure-x86_64-with-glibc2.39, 4 processadores.
- torch 2.13.0+cu130, transformers 4.57.6.
- Dispositivo: cpu; CUDA disponível: False.

## Proveniência

- Partições: `docs/dados/particoes_canonicas_mapa.csv`, Passo 3.
- Hiperparâmetros espelhados de `_ModeloTransformerFT`, em `src/modelos_zoo.py`.
- Script: `src/medir_custo_bertimbau.py`.
- Nenhum modelo foi treinado até o fim e nenhuma predição foi publicada.
- Nenhuma escrita foi realizada na planilha.
