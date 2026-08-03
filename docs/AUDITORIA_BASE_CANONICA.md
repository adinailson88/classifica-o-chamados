# Auditoria da base canônica

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Estado:** `apto_para_congelar`

**Gerado em:** 03/08/2026 00:54

**Hash da base:** `e10c78e4db0026cfcbfa5267ddac034a3c8d3a7a0a1d63fa0cf2ce52f165b174`

## Totais

| Item | Total |
|---|---:|
| Linhas não vazias | 14060 |
| IDs válidos | 14060 |
| IDs únicos | 14060 |
| Referências humanas válidas | 14060 |
| Categorias históricas | 50 |
| Categorias com suporte na referência | 50 |

## Reconciliação da taxonomia

Todas as categorias da referência pertencem à taxonomia histórica.

## Validações

| Verificação | Ocorrências |
|---|---:|
| linhas sem id | 0 |
| ids duplicados | 0 |
| linhas sem categoria historica | 0 |
| vereditos invalidos | 0 |
| conflitos referencia | 0 |
| linhas sem referencia | 0 |
| categorias referencia fora taxonomia historica | 0 |

## Proveniência

- Regra: M='Correto' -> categoria historica; M='Errado' + Q preenchida -> categoria manual; demais casos sem referencia.
- Hash da taxonomia histórica: `ec6f75ca0427d7a0bd224e019a0052ee4e50734bbda66a7fd45890f7c8b488cb`.
- Hash da taxonomia da referência: `ec6f75ca0427d7a0bd224e019a0052ee4e50734bbda66a7fd45890f7c8b488cb`.
- Escopo do hash da base: id, categoria historica, referencia humana e fonte; ordenados por id.
- Script: `src/auditar_base_canonica.py`.
- Nenhuma escrita foi realizada na planilha.
