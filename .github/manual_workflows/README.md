# Workflows manuais isolados (DESATIVADOS)

Os arquivos `.yml` desta pasta **não são executados pelo GitHub Actions**. O GitHub só
reconhece workflows diretamente em `.github/workflows/` (não lê subpastas). Eles foram
movidos para cá de propósito, para ficarem isolados da operação automática e **não
poderem ser disparados** (nem por cron, nem por `Run workflow`).

São contingências/operações manuais que **não** alimentam o painel no fluxo normal — a
classificação, reclassificação, comparação, estatística, decisão e taxonomia já são
atualizadas por workflows automáticos/condicionados em `.github/workflows/`.

## Reativar um workflow

Mover o arquivo de volta para `.github/workflows/` e commitar:

```bash
git mv .github/manual_workflows/<arquivo>.yml .github/workflows/<arquivo>.yml
git commit -m "reativa <arquivo>"
```

## Conteúdo

| Arquivo | Por que está isolado |
|---|---|
| `resetar_destrutivo/resetar.yml` | **DESTRUTIVO**: zera o experimento. Isolado em subpasta própria para reforçar que não deve rodar por acidente. |
| `classificacao_ia_2_aplicar.yml` | Grava a coluna O com confirmação `APLICAR_O`; a coluna O já é atualizada no automático pelo `transformer_ft` (noturno). |
| `reclassificar_validados.yml` | Coluna O — idem (coberta pelo `transformer_ft`). |
| `reclassificacao_robusta.yml` | Reclassificação com LSTM robusto sob demanda; a automática é coberta por `multimodelo_reclassificacao`. |
| `etapa2_reclassificacao.yml` | Reclassificação single-model; a automática é coberta por `multimodelo_reclassificacao`. |
| `classificacao_incremental.yml` | Superseded por `etapa1_turnos` (cron */15). |
| `classificacao_ia_2_dryrun.yml` | Simulação (nunca grava). |
| `reclassificacao_dry_run.yml` | Simulação (nunca grava). |
| `preparar_validacao.yml` | Re-amostra a aba `VALIDACAO_HUMANA`; automatizar trocaria a amostra que o humano está conferindo. |
| `iniciar_pipeline.yml` | Orquestrador; os fluxos que ele dispara já têm cron próprio. |
| `check_final_ready.yml` | Porta/gate de verificação; não publica dados do painel. |
