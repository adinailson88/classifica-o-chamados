# CONTEXTO — classificação de chamados

Este arquivo registra somente o estado vigente e a próxima ação do projeto. O histórico completo permanece nos commits, Pull Requests e execuções do GitHub Actions.

Atualizado em 28/07/2026, no fuso America/Bahia.

## Acesso público

- Artigo em PDF: <https://adinailson88.github.io/classificacao-chamados/artigo_classificacao_chamados.pdf>
- Painel: <https://adinailson88.github.io/classificacao-chamados/>
- Texto-fonte: [`04_artigo/artigo_classificacao_chamados_v3.md`](04_artigo/artigo_classificacao_chamados_v3.md)

## Objetivo

Avaliar modelos de aprendizagem de máquina para classificar chamados de manutenção predial em português brasileiro, distinguindo:

- concordância com a categoria administrativa histórica;
- acerto contra a decisão validada pela conferência humana;
- reclassificação e possíveis problemas da taxonomia histórica.

Os resultados alimentam o painel público e o artigo/capítulo da tese em Biossistemas Construídos.

## Estado dos resultados publicados

Os JSONs são dinâmicos e devem ser conferidos por data de geração antes de qualquer atualização do artigo.

- `docs/dados/avaliacao_final.json`, gerado em 27/07/2026 às 16:41, registra 8.928 decisões validadas, 606 casos restritos e 168 conflitos. Nesse recorte, o `linear_svc` lidera com acerto validado de 95,24%; os ensembles avaliados não superam o melhor modelo isolado.
- `docs/dados/calibracao.json`, gerado em 28/07/2026 às 00:25, registra 13.965 chamados e 8.895 casos validados. A diferença de denominador em relação a `avaliacao_final.json` indica que os arquivos foram produzidos em momentos distintos e precisam ser regenerados na mesma cadeia antes de serem tratados como uma fotografia única.
- `docs/dados/bertimbau_training_state.json` está com `status=sem_dados`. O BERTimbau permanece excluído da avaliação final enquanto não houver execução concluída e artefatos verificáveis.

## Arquitetura vigente

- A aba principal é lida em `A:Q`.
- A verdade validada é derivada por `src/decisao_validada.py` a partir de M, N, P e, quando necessário, Q.
- A memória de treino validada é lida diretamente da aba principal por `src/memoria_validada.py`; a antiga aba separada `VALIDACAO_HUMANA` não é mais fonte operacional.
- Modelos compartilhados de reclassificação ficam em `src/modelos_reclassificacao.py`.
- Rotinas destrutivas de reset e executores legados da Etapa 2 não integram mais o fluxo vigente.

## Fontes canônicas

| Assunto | Fonte |
|---|---|
| Resultado validado por modelo | `docs/dados/avaliacao_final.json` |
| Estatística comparativa | `docs/dados/estatistica.json` |
| Calibração e faixas de confiança | `docs/dados/calibracao.json` e `docs/dados/calibracao_ajustada_modelos.json` |
| Verdade e memória validadas | `src/decisao_validada.py` e `src/memoria_validada.py` |
| Estado do BERTimbau | `docs/dados/bertimbau_training_state.json` e `docs/dados/bertimbau_metr_full.json` |
| Texto científico | `04_artigo/artigo_classificacao_chamados_v3.md` |
| Regras operacionais | `AGENTS.md` e `README.md` |

## Regras operacionais

1. Trabalhar em branch e Pull Request; não fazer push direto em `main`.
2. Qualquer escrita na planilha viva exige opção explícita de aplicação e dry-run prévio quando cabível.
3. Preservar as colunas de conferência humana M, N, P e Q.
4. Não confundir concordância com o histórico e acerto validado.
5. Não publicar texto livre de chamados nos arquivos do GitHub Pages.
6. Não copiar números antigos para o artigo sem conferir os JSONs vigentes e seus timestamps.
7. Novas execuções do BERTimbau devem usar diretamente `transformer_ft.yml`. Avaliação, estatística e consolidação devem ser verificadas e disparadas separadamente.

## Próxima ação

1. Decidir entre executar um treino controlado do BERTimbau ou documentar sua exclusão definitiva da comparação final.
2. Em caso de treino, validar `bertimbau_training_state.json` e `bertimbau_metr_full.json` antes de qualquer etapa posterior.
3. Regenerar separadamente `avaliacao_final.json`, `estatistica.json` e `calibracao.json`, iniciando por dry-run quando houver possibilidade de escrita, para eliminar a divergência de denominadores.
4. Atualizar o artigo integralmente somente depois dessa reconciliação.

## Registro histórico

Decisões anteriores, auditorias, planos concluídos e números substituídos devem ser consultados no histórico do Git e nos Pull Requests. Não devem voltar a ser acumulados neste arquivo.
