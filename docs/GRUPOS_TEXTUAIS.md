# Grupos textuais do experimento

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Estado:** `apto_para_particionar`  
**Gerado em:** 03/08/2026 01:30  
**Hash do mapa por registro:** `ab352b9424e31d2644ed6d075643adf562acc38767e0098eed77595e2dea0bb6`

## Totais

| Item | Total |
|---|---:|
| Linhas não vazias | 14060 |
| Grupos textuais | 9786 |
| Grupos unitários | 9474 |
| Linhas com duplicata | 4586 |
| Proporção de linhas com duplicata | 0.3262 |
| Maior grupo | 219 |
| Linhas sem texto em todos os campos | 0 |

## Viabilidade do particionamento

- Limite por dobra com k=5: 2812 linhas.
- Grupos maiores que uma dobra: 0.
- Grupos com referência humana divergente: 17 (85 linhas).

## Quase duplicados

Diagnóstico sobre 9786 grupos, TF-IDF char_wb 3-4 gramas, similaridade de cosseno. Busca dos 5 vizinhos mais proximos por grupo; pares alem desse teto nao sao contados.

| Limiar | Grupos acima | Proporção |
|---:|---:|---:|
| 0.8 | 1450 | 0.1482 |
| 0.85 | 1082 | 0.1106 |
| 0.9 | 806 | 0.0824 |
| 0.95 | 515 | 0.0526 |

Nenhum limiar adotado; o agrupamento permanece restrito a identidade exata ate que um limiar seja justificado.

## Validações

| Verificação | Ocorrências |
|---|---:|
| linhas sem id | 0 |
| linhas sem texto em todos os campos | 0 |
| grupos maiores que uma dobra | 0 |
| grupos com referencia divergente | 17 |

## Proveniência

- Critério de agrupamento: identidade exata do SHA-256 dos quatro campos normalizados (titulo, descricao GLPI, titulo O.S.M., descricao O.S.M.), separados e nao concatenados.
- Normalização: NFKD, remocao de diacriticos, casefold e colapso de espacos; identica a ablation_lstm.py e comparacao_kfold_groupkfold.py.
- Hash da lista de grupos: `ad8557c109af55fd6f4a6cdd69d0eeb426c1602b66bade9473b6b8f0dc7dc32f`.
- Mapa por registro: `docs/dados/grupos_textuais_mapa.csv`, com SHA-256 do ID.
- Script: `src/construir_grupos_textuais.py`.
- Nenhuma escrita foi realizada na planilha.
