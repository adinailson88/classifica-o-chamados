# Partições canônicas do experimento

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Estado:** `apto_para_treinar`  
**Gerado em:** 03/08/2026 20:09  
**Hash do mapa por registro:** `9465857d83ba76ec193974982835d91e03e783587153e26597051d4dfd9abcf2`

## Protocolo

- Algoritmo: sklearn.model_selection.StratifiedGroupKFold, shuffle=True.
- Dobras: 5; semente: 42.
- Linhas particionadas: 13972.
- Grupos textuais particionados: 9734.
- Grupos divididos entre dobras: 0.
- Categorias particionadas: 41 de 50 na referência.
- Corpus fixado na base congelada do Passo 2, com 14060 registros; 13 linhas vivas da aba ficaram fora por serem posteriores ao congelamento.

## Distribuição por dobra

| Dobra | Linhas | Grupos | Categorias com suporte |
|---:|---:|---:|---:|
| 1 | 2758 | 1951 | 41 |
| 2 | 2556 | 1950 | 41 |
| 3 | 3045 | 1949 | 41 |
| 4 | 2884 | 1944 | 41 |
| 5 | 2729 | 1940 | 41 |

## Categorias excluídas por suporte insuficiente

Das 50 categorias da referência humana, 4 aparecem em menos de 5 grupos textuais distintos. Como um grupo inteiro ocupa uma única dobra, o suporte em todas as 5 dobras é aritmeticamente impossível, e por isso ficam fora do particionamento, somando 12 linhas. A exclusão é nominal: a taxonomia congelada no Passo 1 não é alterada e nenhuma categoria é fundida com outra.

| Categoria | Grupos distintos | Linhas | Dobras possíveis |
|---|---:|---:|---:|
| Suprimentos / Apoio Técnico > Transporte | 2 | 2 | 2 |
| Manutenção Preventiva > Aplicação cupinicida | 3 | 3 | 3 |
| Manutenção Preventiva > Bomba | 3 | 3 | 3 |
| Área Externa e Ambiental > Drenagem | 4 | 4 | 4 |

## Categorias excluídas por ausência efetiva em alguma dobra

Ter ao menos 5 grupos é condição necessária, não suficiente: o sorteio ainda pode reunir numa única dobra todos os grupos de uma categoria. Estas saíram em 2 rodada(s) de reparticionamento, até que todas as categorias remanescentes tivessem suporte verificado em todas as dobras.

| Categoria | Linhas | Rodada |
|---|---:|---:|
| Elétrica > Sistema Fotovoltaico (FV) | 7 | 1 |
| Estrutura Predial > Instalações Especiais (gás, ar comprimido, etc.) | 5 | 1 |
| Hidrossanitária > ETA / ETE | 15 | 2 |
| Manutenção Preventiva > Nobreak | 9 | 2 |
| TI / Dados / Rede > Coleta de dados | 40 | 2 |

No total, 88 linhas ficaram fora das partições. Qualquer métrica derivada delas vale para as 41 categorias particionadas, e não para as 50 da taxonomia. O artigo precisa declarar esse denominador sempre que reportar resultados.

## Validações

| Verificação | Ocorrências |
|---|---:|
| linhas sem dobra | 0 |
| grupos divididos entre dobras | 0 |
| registros descartados | 0 |
| categorias sem suporte em alguma dobra | 0 |

## Proveniência

- Grupos textuais: `src/construir_grupos_textuais.py`, Passo 2.
- Referência humana: regra congelada no Passo 1.
- Mapa por registro: `docs/dados/particoes_canonicas_mapa.csv`, com SHA-256 do ID.
- Script: `src/gerar_particoes_canonicas.py`.
- Nenhuma escrita foi realizada na planilha.
