# Relatório de Migração da Categoria de Equipamentos e Acessórios

- Data/hora: 2026-07-03T18:22:15-03:00
- Repositório: `https://github.com/adinailson88/classificacao-chamados.git`
- Branch: `main`
- Commit inicial: `dfb3def8a81ca053f3c523057c3fdbd698cfb64a`
- Nome antigo: `Instalação de Acessórios e Mobiliário > Instalação/Reparo de Equipamentos, Acessórios e Mobiliários`
- Nome novo: `Instalação de Acessórios e Mobiliário > Instalação/reparo de equipamentos (Suportes de TV, acessórios de banheiro e quadro branco)`
- Cenário aplicado: `B`
- Decisão tomada: validação textual média; migração de artefatos textuais/JSONs permitida
- Modo de aplicação: dry-run ou bloqueado

## Validação por ID

- Campos de ID de categoria encontrados: `nenhum`
- Houve validação por ID: `não`
- ID antigo da categoria: `Informação insuficiente para verificar.`
- ID novo da categoria: `Informação insuficiente para verificar.`
- IDs são iguais: `não`
- Validação apenas textual: `sim`

## Arquivos escaneados

- Total: `154`
- Ignorados/binários: `4`

## Ocorrências por grupo

- JSON do dashboard: `197`
- dados brutos ou intermediarios: `2458`

## Arquivos alterados

- nenhum

## Arquivos não alterados

- `.github/manual_workflows/README.md`
- `.github/manual_workflows/check_final_ready.yml`
- `.github/manual_workflows/classificacao_ia_2_aplicar.yml`
- `.github/manual_workflows/classificacao_ia_2_dryrun.yml`
- `.github/manual_workflows/classificacao_incremental.yml`
- `.github/manual_workflows/etapa2_reclassificacao.yml`
- `.github/manual_workflows/iniciar_pipeline.yml`
- `.github/manual_workflows/preparar_validacao.yml`
- `.github/manual_workflows/reclassificacao_dry_run.yml`
- `.github/manual_workflows/reclassificacao_robusta.yml`
- `.github/manual_workflows/reclassificar_validados.yml`
- `.github/manual_workflows/resetar_destrutivo/resetar.yml`
- `.github/workflows/auditar_conferencias.yml`
- `.github/workflows/avaliacao_final.yml`
- `.github/workflows/comparar_modelos.yml`
- `.github/workflows/consolidar_validacao_classificacao_2.yml`
- `.github/workflows/dashboard.yml`
- `.github/workflows/estatistica.yml`
- `.github/workflows/etapa1_turnos.yml`
- `.github/workflows/lote_noturno_cache.yml`
- `.github/workflows/multimodelo_classificacao.yml`
- `.github/workflows/multimodelo_reclassificacao.yml`
- `.github/workflows/relevancia_termos.yml`
- `.github/workflows/transformer_ft.yml`
- `.github/workflows/validacao_nao_supervisionada.yml`
- `AGENTS.md`
- `CONTEXTO.md`
- `CONTEXTO_ESTATISTICA_CLASSIFICACAO.md`
- `DOCUMENTACAO_MODELOS_E_ESTATISTICA.md`
- `ESTADO_DO_ROTEIRO.md`
- `FALTA_FAZER.md`
- `OBJETIVO_FINAL_MODELO_IA.txt`
- `PLANO_CALIBRACAO.md`
- `README.md`
- `analise_R/README.md`
- `analise_R/dados_modelos.txt`
- `config_experimento.json`
- `dados/README.md`
- `dados/bertimbau_coreset_ids.json`
- `dados/estado_automacao.json`
- `docs/CACHE_PLANILHA_WORKFLOWS.md`
- `docs/CLASSIFICACAO_IA_2_5_ETAPAS.md`
- `docs/CONTRIBUICAO_SHANNON_ARTIGO.md`
- `docs/GUIA_TECNICO.md`
- `docs/GUIA_TECNICO_VALIDACAO_NAO_SUPERVISIONADA.md`
- `docs/METODOLOGIA_SHANNON.md`
- `docs/RELATORIO_ESTADO_ATUAL.md`
- `docs/RELEVANCIA_TERMOS.md`
- `docs/VALIDACAO_NAO_SUPERVISIONADA.md`
- `docs/dados/analise_erros.json`
- `docs/dados/auditoria_conferencias.json`
- `docs/dados/avaliacao_final.json`
- `docs/dados/bertimbau_cluster_report.json`
- `docs/dados/bertimbau_coreset_resumo.json`
- `docs/dados/bertimbau_review_queue.json`
- `docs/dados/bertimbau_token_stats.json`
- `docs/dados/bertimbau_training_state.json`
- `docs/dados/cache_planilha_manifest.json`
- `docs/dados/calibracao.json`
- `docs/dados/calibracao_ajustada_modelos.json`
- `docs/dados/calibracao_modelos.json`
- `docs/dados/comparacao_categoria.json`
- `docs/dados/comparacao_modelos.json`
- `docs/dados/comparacao_previsoes.json`
- `docs/dados/confusao_historico_ia.json`
- `docs/dados/correlacao_categorias.json`
- `docs/dados/cruzamento_taxonomia.json`
- `docs/dados/estatistica.json`
- `docs/dados/jensen_shannon_modelos.json`
- `docs/dados/log_turnos_classificacao.json`
- `docs/dados/log_turnos_reclassificacao.json`
- `docs/dados/metricas_experimento.json`
- `docs/dados/metricas_por_categoria.json`
- `docs/dados/multimodelo_metricas.json`
- `docs/dados/multimodelo_reclass_turnos.json`
- `docs/dados/multimodelo_turnos.json`
- `docs/dados/reclass_resumo.json`
- `docs/dados/registros.json`
- `docs/dados/registros_extra_trees.json`
- `docs/dados/registros_linear_svc.json`
- `docs/dados/registros_lstm.json`
- `docs/dados/registros_naive_bayes.json`
- `docs/dados/registros_random_forest.json`
- `docs/dados/registros_regressao_logistica.json`
- `docs/dados/registros_sgd.json`
- `docs/dados/resumo.json`
- `docs/dados/shannon_categorias.json`
- `docs/dados/shannon_modelos.json`
- `docs/dados/shannon_resumo.json`
- `docs/dados/shannon_votos.json`
- `docs/dados/termos_relevantes.json`
- `docs/dados/workflows_index.json`
- `docs/exportar_analises.py`
- `docs/index.html`
- `docs/mapa_correlacao.html`
- `requirements-estatistica.txt`
- `requirements-leves.txt`
- `requirements-robusto.txt`
- `requirements-transformer.txt`
- `requirements.txt`
- `src/analise_erros.py`
- `src/analise_estatistica.py`
- `src/analise_shannon.py`
- `src/aplicar_formula_status_executor.py`
- `src/atualizar_cache_planilha.py`
- `src/auditar_conferencias.py`
- `src/avaliacao_final.py`
- `src/bertimbau_coreset.py`
- `src/calibracao.py`
- `src/calibracao_confianca.py`
- `src/calibracao_modelos.py`
- `src/check_final_ready.py`
- `src/classificacao_ia_2_comite.py`
- `src/classificacao_multimodelo.py`
- `src/classificador_producao.py`
- `src/classificador_robusto.py`
- `src/classificar_etapa.py`
- `src/classificar_lote_baseline.py`
- `src/classificar_lote_inicial.py`
- `src/comparar_coreset.py`
- `src/comparar_modelos.py`
- `src/comparar_modelos_lote.py`
- `src/consolidar_memoria_validada_classificacao.py`
- `src/cruzamento_taxonomia.py`
- `src/decisao_validada.py`
- `src/escrever_estado_bertimbau.py`
- `src/executar_etapa1.py`
- `src/executar_etapa2.py`
- `src/exportar_dashboard.py`
- `src/exportar_etapa.py`
- `src/gerar_pdfs_documentacao.py`
- `src/guard_automacao.py`
- `src/memoria_validada.py`
- `src/modelo_lstm.py`
- `src/modelos_zoo.py`
- `src/padronizar_datas_planilha.py`
- `src/planilha.py`
- `src/preparar_abas_experimento.py`
- `src/preparar_abas_multimodelo.py`
- `src/preparar_validacao_humana.py`
- `src/reclassificacao_multimodelo.py`
- `src/reclassificar_validados.py`
- `src/registrar_config_experimento.py`
- `src/registrar_snapshot_inicial.py`
- `src/relevancia_termos.py`
- `src/resetar_experimento.py`
- `src/smoke_transformer.py`
- `src/tempo.py`
- `src/validacao_nao_supervisionada.py`
- `src/validar_planilha_experimento.py`
- `tests/amostra_valores.json`
- `tests/test_decisao_memoria.py`
- `tests/test_github_first.py`
- `tests/test_tipo_manutencao.py`

## Arquivos com ocorrência antiga remanescente

- nenhum

## Arquivos com ocorrência nova

- `analise_R/dados_modelos.txt`
- `dados/bertimbau_coreset_ids.json`
- `docs/dados/analise_erros.json`
- `docs/dados/bertimbau_cluster_report.json`
- `docs/dados/bertimbau_coreset_resumo.json`
- `docs/dados/bertimbau_review_queue.json`
- `docs/dados/bertimbau_token_stats.json`
- `docs/dados/comparacao_categoria.json`
- `docs/dados/comparacao_previsoes.json`
- `docs/dados/confusao_historico_ia.json`
- `docs/dados/correlacao_categorias.json`
- `docs/dados/cruzamento_taxonomia.json`
- `docs/dados/estatistica.json`
- `docs/dados/metricas_por_categoria.json`
- `docs/dados/registros.json`
- `docs/dados/registros_extra_trees.json`
- `docs/dados/registros_linear_svc.json`
- `docs/dados/registros_lstm.json`
- `docs/dados/registros_naive_bayes.json`
- `docs/dados/registros_random_forest.json`
- `docs/dados/registros_regressao_logistica.json`
- `docs/dados/registros_sgd.json`
- `docs/dados/shannon_categorias.json`
- `docs/dados/shannon_votos.json`
- `docs/dados/termos_relevantes.json`

## Validações executadas

- `dry-run: nenhuma alteração aplicada`

## Riscos

- `Informação insuficiente para verificar por ID da categoria`

## Pendências

- nenhum

## Recomendação para os próximos repositórios

Repetir a mesma lógica por repositório, começando por diagnóstico de ID de categoria GLPI. Não consolidar categorias sem ID igual ou sem cenário textual seguro explicitamente registrado.

## Verificação final (2026-07-23)

Pendência de `docs/CODEX_PROXIMA_SESSAO.md` tratada nesta rodada. Resultado:

- **Dados locais (`docs/dados/*.json`)**: 23 arquivos com a string nova (`Suportes de TV, acessórios de banheiro e quadro branco`), 0 arquivos com a string antiga remanescente — confirmado por `grep` direto, coerente com a contagem original deste relatório.
- **`raw.githubusercontent.com/.../main/docs/dados/analise_erros.json`**: contém apenas a categoria nova. Sem ocorrência da string antiga.
- **GitHub Pages (`adinailson88.github.io/classificacao-chamados/dados/analise_erros.json`)**: HTTP 200, `Last-Modified: 2026-07-23`, `Age: 0`, `Cache-Control: max-age=600` — conteúdo servido é o atual, não há cache antigo represado. Contém apenas a categoria nova.
- **Local × raw/main × Pages**: as três fontes são coerentes entre si (categoria nova em todas, categoria antiga em nenhuma).
- A frase "Modo de aplicação: dry-run ou bloqueado" / "Arquivos alterados: nenhum" registrada acima **permanece correta e não é uma inconsistência**: o texto novo já chegou pronto nos dados de origem (upstream/GLPI) antes de qualquer commit deste repositório; este script de migração nunca precisou reescrever arquivo nenhum, apenas confirmar por texto que a categoria antiga havia desaparecido dos dados operacionais.
- Continua valendo o limite já registrado: a validação é **apenas textual**, pois `classificacao-chamados` não preserva `itilcategories_id` (nem outro ID próprio de categoria do GLPI). Não há verificação por ID nesta migração.

Único resíduo da string antiga no repositório: `docs/CODEX_PROXIMA_SESSAO.md` (texto descritivo da pendência) e `scripts/migracoes/migrar_categoria_equipamentos_acessorios.py` (constante de busca do próprio script) — ambos esperados, não são dados operacionais.

**Conclusão**: pendência fechada. Nada a aplicar; nenhuma ação de escrita necessária nos dados.


## Verificação final complementar (2026-07-24)

Validação repetida sobre o `main` remoto e a publicação do GitHub Pages:

- **`docs/dados/`**: 0 ocorrências do nome antigo e 4.518 ocorrências do nome novo, distribuídas em 24 arquivos.
- **`dados/bertimbau_coreset_ids.json`**: 0 ocorrências do nome antigo e 253 do nome novo.
- **`metricas_por_categoria.json` no raw GitHub e no GitHub Pages**: ambas as fontes responderam HTTP 200 e apresentam a categoria nova, sem ocorrência do nome antigo.
- **Dados operacionais e publicação**: coerentes quanto à substituição textual da categoria.

A limitação metodológica permanece: não há `itilcategories_id` nem outro identificador próprio da categoria GLPI nos artefatos deste repositório. Portanto, a conclusão é de migração textual consistente, não de equivalência confirmada por ID.

**Conclusão atualizada**: verificação final concluída; não há alteração a aplicar nos dados ou nos workflows.
