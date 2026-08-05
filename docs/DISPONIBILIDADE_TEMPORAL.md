# Disponibilidade de data de abertura no corpus congelado

> Relatório sanitizado e somente leitura. Não contém títulos,
> descrições ou IDs de chamados.

**Gerado em:** 05/08/2026 10:22

**Pergunta:** o corpus congelado carrega data de abertura do chamado, que permita separar treino, calibracao e teste no tempo?

**Veredito:** `sem_variavel_temporal`

## Fontes inspecionadas

| Fonte | Natureza | Presente | Campos | Candidatos a data do chamado | Carimbos de execução |
|---|---|---|---:|---|---|
| AGENTS.md :: Colunas esperadas | contrato da aba principal | sim | 17 | — | — |
| docs/dados/auditoria_base_canonica.json | artefato canonico | sim | 41 | — | gerado_em |
| docs/dados/rodada_canonica.json | artefato canonico | sim | 33 | — | gerado_em |
| docs/dados/grupos_textuais.json | artefato canonico | sim | 46 | — | gerado_em |
| docs/dados/particoes_canonicas.json | artefato canonico | sim | 47 | — | gerado_em |
| docs/dados/grupos_textuais_mapa.csv | artefato canonico | sim | 2 | — | — |
| docs/dados/particoes_canonicas_mapa.csv | artefato canonico | sim | 3 | — | — |
| docs/dados/retreino_canonico_predicoes.csv | artefato canonico | sim | 6 | — | — |

## Leitura

a avaliacao temporal nao pode ser executada sobre os artefatos congelados; a validacao cruzada agrupada estima generalizacao entre grupos textuais, e nao desempenho futuro sob deriva temporal, de modo que toda afirmacao de uso prospectivo precisa ser condicional.

campos como gerado_em registram quando o artefato foi produzido e nao quando o chamado foi aberto; nao servem a divisao temporal.
