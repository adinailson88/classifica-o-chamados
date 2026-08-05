# Matriz de proveniência da rodada canônica

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Estado:** `concluido`  
**Gerado em:** 05/08/2026 01:21  
**Hash do corpus:** `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`

## Coerência dos artefatos derivados

| Artefato | Arquivo | Script | Hash confere |
|---|---|---|---|
| Retreino dos sete modelos | `docs/dados/retreino_canonico.json` | `src/retreinar_modelos_canonicos.py` | sim |
| Regras contra modelos | `docs/dados/regras_versus_modelos.json` | `src/comparar_regras_modelos.py` | sim |
| Calibracao e automacao seletiva | `docs/dados/calibracao_canonica.json` | `src/calibrar_confianca.py` | sim |
| Recortes por tipo e volume | `docs/dados/recortes_canonicos.json` | `src/recortes_canonicos.py` | sim |
| Inferencia estatistica | `docs/dados/inferencia_canonica.json` | `src/inferencia_canonica.py` | sim |
| Inferencia pareada por grupo textual | `docs/dados/inferencia_agrupada.json` | `src/inferencia_agrupada.py` | sim |
| Sensibilidade as categorias raras | `docs/dados/sensibilidade_classes_raras.json` | `src/sensibilidade_classes_raras.py` | sim |
| Utilidade da reclassificacao | `docs/dados/utilidade_reclassificacao.json` | `src/utilidade_reclassificacao.py` | sim |

## Artefatos do congelamento

Definem o corpus e por isso não carregam `hash_corpus`: ele é derivado deles.

| Artefato | Arquivo | Script | Presente |
|---|---|---|---|
| Auditoria da base | `docs/dados/auditoria_base_canonica.json` | `src/auditar_base_canonica.py` | sim |
| Grupos textuais | `docs/dados/grupos_textuais.json` | `src/construir_grupos_textuais.py` | sim |
| Particoes canonicas | `docs/dados/particoes_canonicas.json` | `src/gerar_particoes_canonicas.py` | sim |

## Rastreabilidade das grandezas publicáveis

| Grandeza | Artefato | Script | Denominador | Categorias | Partições | Hash | Ressalva |
|---|---|---|---:|---:|---:|---|---|
| Acuracia e macro-F1 por modelo | `docs/RETREINO_CANONICO.md` | `src/retreinar_modelos_canonicos.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Ganho ou perda da camada de regras | `docs/REGRAS_VERSUS_MODELOS.md` | `src/comparar_regras_modelos.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| ECE, Brier e curva de confiabilidade | `docs/CALIBRACAO_CANONICA.md` | `src/calibrar_confianca.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Cobertura e acuracia seletiva por limiar | `docs/CALIBRACAO_CANONICA.md` | `src/calibrar_confianca.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Recorte por tipo e tarefa de tipo | `docs/RECORTES_CANONICOS.md` | `src/recortes_canonicos.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Curva ABC por volume | `docs/RECORTES_CANONICOS.md` | `src/recortes_canonicos.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Intervalos de confianca | `docs/INFERENCIA_CANONICA.md` | `src/inferencia_canonica.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Efeito de desenho da dependencia intragrupo | `docs/INFERENCIA_AGRUPADA.md` | `src/inferencia_agrupada.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Cochran Q com referencia por permutacao de grupo | `docs/INFERENCIA_AGRUPADA.md` | `src/inferencia_agrupada.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Diferenca de acuracia, IC, grupos a favor e p ajustado por par | `docs/INFERENCIA_AGRUPADA.md` | `src/inferencia_agrupada.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Cobertura e macro-F1 sob tres convencoes de denominador | `docs/SENSIBILIDADE_CLASSES_RARAS.md` | `src/sensibilidade_classes_raras.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Razao de equilibrio e utilidade da reclassificacao | `docs/UTILIDADE_RECLASSIFICACAO.md` | `src/utilidade_reclassificacao.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Cochran Q e McNemar por linha, mantidos so para contraste | `docs/INFERENCIA_CANONICA.md` | `src/inferencia_canonica.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Custo computacional do BERTimbau | `docs/CUSTO_BERTIMBAU.md` | `src/medir_custo_bertimbau.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Concordancia historica, Kappa e ganho liquido | `docs/dados/comparacao_historica.json` | `src/executar_rodada_canonica.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Dispersao das predicoes e Jensen-Shannon | `docs/dados/comparacao_historica.json` | `src/executar_rodada_canonica.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Unanimidade e desacordo estrutural entre modelos | `docs/INFERENCIA_CANONICA.md` | `src/inferencia_canonica.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Conciliacao das contagens de grupos textuais | `docs/INFERENCIA_CANONICA.md` | `src/inferencia_canonica.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Tabelas A1 a A3 do apendice | `docs/dados/tabelas_apendice_canonicas.json` | `src/tabelas_apendice_canonicas.py` | 13972 | 41 | 5 | `1e4762438a7e` | — |
| Corpus congelado, referencia humana e taxonomia | `docs/dados/auditoria_base_canonica.json` | `src/auditar_base_canonica.py` | 14060 | 50 | — | `congelamento` | denominador do corpus e da cobertura da revisao, nunca das metricas, que valem para 13.972 linhas |
| Grupos textuais da base congelada | `docs/dados/grupos_textuais.json` | `src/construir_grupos_textuais.py` | 14060 | 50 | — | `congelamento` | 9.786 grupos na base inteira; 9.735 no recorte de 13.972 linhas; 9.734 no mapa de particoes, recalculado sobre o texto vivo |
| Grupos com referencia humana divergente e sua natureza | `docs/dados/grupos_divergentes_canonicos.json` | `src/auditar_grupos_divergentes.py` | 13972 | 41 | — | `congelamento` | 17 grupos e 85 linhas medidos sobre as linhas com referencia avaliada; 14 grupos e 74 linhas opoem categorias de TIPOS de manutencao distintos, de modo que a contagem nao pode ser lida como piso de erro de anotacao |
| Curva de aprendizado do LSTM (Figura 7) | `04_artigo/figuras/lstm_history.json` | `src/modelo_lstm.py` | — | — | — | `fora da rodada canonica` | treino unico sobre a aba viva de 25/07/2026, com rotulo historico e validacao interna de 10%; nao comparavel com as Tabelas 1 e 2 |
| Ablation de unidades e dropout do LSTM | `04_artigo/figuras/ablation_lstm_resultados.json` | `src/ablation_lstm.py` | 9096 | — | 3 | `fora da rodada canonica` | snapshot legado de 24/07/2026, cobertura parcial da revisao humana e rotulo de treino historico; o script foi corrigido depois e os numeros nao foram regerados |
| KFold por linha contra GroupKFold por texto | `04_artigo/figuras/comparacao_kfold_groupkfold.json` | `src/comparacao_kfold_groupkfold.py` | 14094 | — | 5 | `fora da rodada canonica` | base de 01/08/2026, anterior ao congelamento em 14.060, e alvo e a categoria historica |

## Números legados ainda presentes no artigo

Encontradas 2 ocorrências em `04_artigo/artigo_classificacao_chamados_v3.md`. a varredura do artigo aponta, nunca corrige: substituir numero em texto cientifico e decisao editorial do autor.

| Linha | Forma no texto | Valor legado |
|---:|---|---|
| 693 | `0,7781` | acuracia legada de random_forest |
| 713 | `0,7781` | acuracia legada de random_forest |

## Validações

| Verificação | Ocorrências |
|---|---:|
| artefatos com hash divergente | 0 |
| artefatos do congelamento ausentes | 0 |
| numeros legados ainda no artigo | 2 |

**Cobertura da varredura:** sao procuradas as acuracias registradas em estatistica.json, o total de chamados e a contagem de categorias da execucao legada. O artigo pode conter numeros de rodadas intermediarias que nao estao em nenhum JSON versionado, e esses a varredura nao alcanca; a contagem e piso, nao teto.

## Proveniência

- Script: `src/matriz_proveniencia.py`.
- Nenhuma escrita foi realizada na planilha nem no artigo.
