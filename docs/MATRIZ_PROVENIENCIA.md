# Matriz de proveniência da rodada canônica

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Estado:** `concluido`  
**Gerado em:** 04/08/2026 14:12  
**Hash do corpus:** `3aa42e314459787ef12ccc778dfa1368e89d81c4863108042d59a1a9343ec3ff`

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
| Acuracia e macro-F1 por modelo | `docs/RETREINO_CANONICO.md` | `src/retreinar_modelos_canonicos.py` | 13972 | 41 | 5 | `3aa42e314459` |
| Ganho ou perda da camada de regras | `docs/REGRAS_VERSUS_MODELOS.md` | `src/comparar_regras_modelos.py` | 13972 | 41 | 5 | `3aa42e314459` |
| ECE, Brier e curva de confiabilidade | `docs/CALIBRACAO_CANONICA.md` | `src/calibrar_confianca.py` | 13972 | 41 | 5 | `3aa42e314459` |
| Cobertura e acuracia seletiva por limiar | `docs/CALIBRACAO_CANONICA.md` | `src/calibrar_confianca.py` | 13972 | 41 | 5 | `3aa42e314459` |
| Recorte por tipo e tarefa de tipo | `docs/RECORTES_CANONICOS.md` | `src/recortes_canonicos.py` | 13972 | 41 | 5 | `3aa42e314459` |
| Curva ABC por volume | `docs/RECORTES_CANONICOS.md` | `src/recortes_canonicos.py` | 13972 | 41 | 5 | `3aa42e314459` |
| Intervalos de confianca | `docs/INFERENCIA_CANONICA.md` | `src/inferencia_canonica.py` | 13972 | 41 | 5 | `3aa42e314459` |
| Cochran Q e McNemar com Holm | `docs/INFERENCIA_CANONICA.md` | `src/inferencia_canonica.py` | 13972 | 41 | 5 | `3aa42e314459` |
| Custo computacional do BERTimbau | `docs/CUSTO_BERTIMBAU.md` | `src/medir_custo_bertimbau.py` | 13972 | 41 | 5 | `3aa42e314459` |

## Números legados ainda presentes no artigo

Encontradas 35 ocorrências em `04_artigo/artigo_classificacao_chamados_v3.md`. a varredura do artigo aponta, nunca corrige: substituir numero em texto cientifico e decisao editorial do autor.

| Linha | Forma no texto | Valor legado |
|---:|---|---|
| 79 | `14.058` | corpus legado |
| 89 | `14.058` | corpus legado |
| 120 | `14,058` | corpus legado |
| 129 | `14,058` | corpus legado |
| 231 | `14.058` | corpus legado |
| 434 | `14.058` | corpus legado |
| 451 | `14.058` | corpus legado |
| 576 | `14.058` | corpus legado |
| 666 | `14.058` | corpus legado |
| 722 | `14.058` | corpus legado |
| 824 | `14.058` | corpus legado |
| 825 | `14.058` | corpus legado |
| 845 | `14.058` | corpus legado |
| 850 | `14.058` | corpus legado |
| 866 | `14.058` | corpus legado |
| 896 | `14.058` | corpus legado |
| 928 | `14.058` | corpus legado |
| 987 | `14.058` | corpus legado |
| 1013 | `14.058` | corpus legado |
| 1082 | `14.058` | corpus legado |
| 1195 | `14.058` | corpus legado |
| 1224 | `14.058` | corpus legado |
| 1262 | `14.058` | corpus legado |
| 1304 | `14.058` | corpus legado |
| 1375 | `56 categorias` | categorias legadas |
| 1400 | `14.058` | corpus legado |
| 1401 | `56 categorias` | categorias legadas |
| 1444 | `14.058` | corpus legado |
| 1463 | `56 categorias` | categorias legadas |
| 1543 | `14.058` | corpus legado |
| 1712 | `14.058` | corpus legado |
| 2004 | `14.058` | corpus legado |
| 2043 | `14.058` | corpus legado |
| 2062 | `14.058` | corpus legado |
| 2105 | `0,69` | acuracia legada de lstm |

## Validações

| Verificação | Ocorrências |
|---|---:|
| artefatos com hash divergente | 0 |
| artefatos do congelamento ausentes | 0 |
| numeros legados ainda no artigo | 35 |

**Cobertura da varredura:** sao procuradas as acuracias registradas em estatistica.json, o total de chamados e a contagem de categorias da execucao legada. O artigo pode conter numeros de rodadas intermediarias que nao estao em nenhum JSON versionado, e esses a varredura nao alcanca; a contagem e piso, nao teto.

## Proveniência

- Script: `src/matriz_proveniencia.py`.
- Nenhuma escrita foi realizada na planilha nem no artigo.
