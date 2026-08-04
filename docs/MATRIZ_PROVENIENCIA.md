# Matriz de proveniência da rodada canônica

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Estado:** `concluido`  
**Gerado em:** 04/08/2026 19:06  
**Hash do corpus:** `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`

## Coerência dos artefatos derivados

| Artefato | Arquivo | Script | Hash confere |
|---|---|---|---|
| Retreino dos sete modelos | `docs/dados/retreino_canonico.json` | `src/retreinar_modelos_canonicos.py` | sim |
| Regras contra modelos | `docs/dados/regras_versus_modelos.json` | `src/comparar_regras_modelos.py` | sim |
| Calibracao e automacao seletiva | `docs/dados/calibracao_canonica.json` | `src/calibrar_confianca.py` | sim |
| Recortes por tipo e volume | `docs/dados/recortes_canonicos.json` | `src/recortes_canonicos.py` | sim |
| Inferencia estatistica | `docs/dados/inferencia_canonica.json` | `src/inferencia_canonica.py` | sim |

## Artefatos do congelamento

Definem o corpus e por isso não carregam `hash_corpus`: ele é derivado deles.

| Artefato | Arquivo | Script | Presente |
|---|---|---|---|
| Auditoria da base | `docs/dados/auditoria_base_canonica.json` | `src/auditar_base_canonica.py` | sim |
| Grupos textuais | `docs/dados/grupos_textuais.json` | `src/construir_grupos_textuais.py` | sim |
| Particoes canonicas | `docs/dados/particoes_canonicas.json` | `src/gerar_particoes_canonicas.py` | sim |

## Rastreabilidade das grandezas publicáveis

| Grandeza | Artefato | Script | Denominador | Categorias | Partições | Hash |
|---|---|---|---:|---:|---:|---|
| Acuracia e macro-F1 por modelo | `docs/RETREINO_CANONICO.md` | `src/retreinar_modelos_canonicos.py` | 13972 | 41 | 5 | `1e4762438a7e` |
| Ganho ou perda da camada de regras | `docs/REGRAS_VERSUS_MODELOS.md` | `src/comparar_regras_modelos.py` | 13972 | 41 | 5 | `1e4762438a7e` |
| ECE, Brier e curva de confiabilidade | `docs/CALIBRACAO_CANONICA.md` | `src/calibrar_confianca.py` | 13972 | 41 | 5 | `1e4762438a7e` |
| Cobertura e acuracia seletiva por limiar | `docs/CALIBRACAO_CANONICA.md` | `src/calibrar_confianca.py` | 13972 | 41 | 5 | `1e4762438a7e` |
| Recorte por tipo e tarefa de tipo | `docs/RECORTES_CANONICOS.md` | `src/recortes_canonicos.py` | 13972 | 41 | 5 | `1e4762438a7e` |
| Curva ABC por volume | `docs/RECORTES_CANONICOS.md` | `src/recortes_canonicos.py` | 13972 | 41 | 5 | `1e4762438a7e` |
| Intervalos de confianca | `docs/INFERENCIA_CANONICA.md` | `src/inferencia_canonica.py` | 13972 | 41 | 5 | `1e4762438a7e` |
| Cochran Q e McNemar com Holm | `docs/INFERENCIA_CANONICA.md` | `src/inferencia_canonica.py` | 13972 | 41 | 5 | `1e4762438a7e` |
| Custo computacional do BERTimbau | `docs/CUSTO_BERTIMBAU.md` | `src/medir_custo_bertimbau.py` | 13972 | 41 | 5 | `1e4762438a7e` |

## Números legados ainda presentes no artigo

Encontradas 5 ocorrências em `04_artigo/artigo_classificacao_chamados_v3.md`. a varredura do artigo aponta, nunca corrige: substituir numero em texto cientifico e decisao editorial do autor.

| Linha | Forma no texto | Valor legado |
|---:|---|---|
| 872 | `0,7714` | acuracia legada de regressao_logistica |
| 1082 | `14.058` | corpus legado |
| 1195 | `14.058` | corpus legado |
| 1304 | `14.058` | corpus legado |
| 2043 | `14.058` | corpus legado |

## Validações

| Verificação | Ocorrências |
|---|---:|
| artefatos com hash divergente | 0 |
| artefatos do congelamento ausentes | 0 |
| numeros legados ainda no artigo | 5 |

**Cobertura da varredura:** sao procuradas as acuracias registradas em estatistica.json, o total de chamados e a contagem de categorias da execucao legada. O artigo pode conter numeros de rodadas intermediarias que nao estao em nenhum JSON versionado, e esses a varredura nao alcanca; a contagem e piso, nao teto.

## Proveniência

- Script: `src/matriz_proveniencia.py`.
- Nenhuma escrita foi realizada na planilha nem no artigo.
