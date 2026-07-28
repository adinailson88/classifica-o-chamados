# Workflows manuais isolados (DESATIVADOS)

Os arquivos `.yml` desta pasta não são executados pelo GitHub Actions. O GitHub reconhece workflows apenas quando estão diretamente em `.github/workflows/`.

Esta pasta mantém somente contingências ou operações de recuperação que ainda possuem função exclusiva. Fluxos substituídos, diagnósticos duplicados ou orquestradores de workflows ativos devem ser apagados, não arquivados indefinidamente.

## Reativar um workflow

Mover o arquivo para `.github/workflows/`, revisar seu escopo e criar uma alteração específica em branch + Pull Request.

```bash
git mv .github/manual_workflows/<arquivo>.yml .github/workflows/<arquivo>.yml
git commit -m "reativa <arquivo>"
```

## Conteúdo

| Arquivo | Por que está isolado |
|---|---|
| `resetar_destrutivo/resetar.yml` | **Destrutivo:** zera o experimento. Mantido em subpasta própria para impedir execução acidental. |
| `reclassificar_validados.yml` | Contingência para a coluna O; o fluxo normal é coberto pelo `transformer_ft`. |
| `reclassificacao_robusta.yml` | Reclassificação pesada sob demanda; o fluxo normal é coberto por `multimodelo_reclassificacao.yml`. |
| `etapa2_reclassificacao.yml` | Reclassificação single-model legada, mantida apenas como contingência controlada. |
| `preparar_validacao.yml` | Reamostra a aba de validação humana; não deve ser automatizado. |

Antes de reativar qualquer arquivo, confirmar que ele não duplica um workflow vigente e que preserva as colunas M, N, P e Q.
