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

- `docs/dados/avaliacao_final.json`, gerado em 28/07/2026, registra 8.895 decisões validadas, 639 casos restritos e 201 conflitos, sobre 8.895 decisões. Nesse recorte, o `linear_svc` lidera com acerto validado de 95,27% (IC95%: 94,82%–95,69%); os ensembles avaliados não superam o melhor modelo isolado.
- `docs/dados/bertimbau_training_state.json` está com `status=ok`: o treino do BERTimbau foi concluído em modo automático. `docs/dados/avaliacao_bertimbau_holdout.json` registra a avaliação held-out complementar, no mesmo lote de 1.000 chamados usado pelos outros sete modelos (639 com decisão M/N/P/Q): BERTimbau com acerto validado de 77,46% (IC95%: 74,02%–80,75%), segunda posição, contra 78,56% do LinearSVC (McNemar, *p* = 0,510, sem diferença significativa). O BERTimbau não integra o ranking integral dos sete modelos por não possuir predições *out-of-fold* sobre toda a base; é apresentado em subseção própria (4.3) do artigo.

## Arquitetura vigente

- A aba principal é lida em `A:Q`.
- A verdade validada é derivada por `src/decisao_validada.py` a partir de M, N, P e, quando necessário, Q.
- A memória de treino validada é lida diretamente da aba principal por `src/memoria_validada.py`; a antiga aba separada `VALIDACAO_HUMANA` não é mais fonte operacional.
- A consolidação das abas privadas usa `src/consolidar_validacao.py`, sem regra paralela de verdade e com exclusão de conflitos. O cron executa apenas dry-run; a gravação exige disparo manual explícito.
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

0. **Pendente (28/07/2026): reprocessamento após mesclagem de categorias no GLPI.** O usuário mesclou diretamente no GLPI os casos `Manutenção Preventiva > Extintor` → `Manutenção Preventiva > Sistemas de combate a incêndio (extintores, hidrantes)` e `Área Externa e Ambiental > Poda de árvore / Roçagem` → `Área Externa e Ambiental > Manutenção área externa / meio ambiente / Poda de árvore / Roçagem` (o usuário excluiu a categoria de Poda no GLPI e renomeou a categoria maior para esse nome novo combinado; por isso os DOIS nomes antigos apontam para ele — ver `config_categorias_canonicas.json`) (identificados via `docs/dados/cruzamento_taxonomia.json`, workflow `relevancia_termos.yml` rodado com `min_chamados_categoria=5`). Isso vai exigir atualizar o JSON de categorias de manutenção, o que propaga para o IMPORTRANGE da planilha e provavelmente exige rodar a pipeline inteira de novo (classificação, comparação de modelos, avaliação, calibração). Decisão explícita do usuário: quando isso acontecer, **não alterar a estrutura do artigo nem do dashboard** — só os dados/números devem mudar, seguindo o mesmo padrão do PR do BERTimbau (script editorial pontual, sem reescrever seções).
0.1. **Pendente (01/08/2026): a planilha esbarrou no teto de 10 milhões de células do Google Sheets.** A criação da aba `CONFERENCIA_MULTIMODELO` falhou com `This action would increase the number of cells in the workbook above the limit`. Auditoria em `scripts/migracoes/auditar_abas_planilha.py` (workflow `auditar_abas_planilha.yml`, read-only) mediu **9.008.123 células alocadas (90,1% do limite) para 7.427.340 usadas — 1.580.783 de desperdício**. Conclusões, para não refazer o diagnóstico:
    - **Não há lixo relevante.** Só 2 abas órfãs, somando 84 mil células (0,8% do limite). Apagar o que não é usado não resolve.
    - **O ganho está em redimensionar a grade**, sem apagar dado nenhum. Piores casos: `COMPARACAO_MODELOS` (260.000 alocadas para 1.313 usadas), `CLASSIF__transformer_ft` (220.000 para 11), `CONTROLE_CLASSIFICACAO_2` (180.000 para 261), `RECLASS_VALIDADOS` (260.000 para 50.115), `RECLASS__linear_svc` (476.720 para 225.520), `VALIDACAO_HUMANA` e `LOG_TURNOS_RECLASSIFICACAO` (alocadas e **totalmente vazias**). Redimensionar tudo levaria de 90,1% para ~74%.
    - **NÃO APAGAR `BACKUP_ETAPA1_20260726_131413`.** A auditoria o marca como órfão pelo prefixo, mas ele guarda **coluna A (ID) + G:K de 26/07, com 13.967 linhas** — é a fonte para restaurar a coluna G por `id_chamado`, ver item 0.2.
    - `RECLASS_HISTORICO` ocupa 2.718.336 células (30% de tudo), com zero desperdício. Compactar para a última entrada por chamado liberaria ~2,3 milhões, **mas só depois de exportar o histórico completo para arquivo** — foi essa trilha que permitiu restaurar a coluna O em 01/08.

0.2. **Pendente (01/08/2026): a coluna G (Classificação IA) está desalinhada.** Medição: `C == G` em **9,1%** (1.288/14.094), contra a referência histórica de 67–71% do LSTM. Controle no mesmo diagnóstico: `C == O` em 80,7%, e a coluna O foi realinhada por `id_chamado` em 01/08. Causa: as colunas A–F são fórmula (`IMPORTRANGE`) e acompanharam a reordenação da fonte em 28/07; G–J são valor literal e ficaram para trás. Efeito visível: a fórmula da coluna K (`=SE(G2="";"";G2=C2)`) passou a devolver FALSO em massa. As colunas M, N, P e Q **não** estão nesse problema — teste de isolamento em `scripts/migracoes/dump_amostra_planilha.py` mostrou que M discrimina (C==O em 83,9% sob `M='Correto'` contra 25,6% sob `M='Errado'`), o que só ocorre em coluna alinhada. Restauração possível a partir do backup citado em 0.1, indexando por `id_chamado` e **nunca por número de linha** (10.410 de 14.094 linhas divergem — ver `scripts/migracoes/verificar_alinhamento_linhas.py`).

0.3. **Pendente (01/08/2026): workflows de escrita desabilitados.** Para proteger a planilha durante o diagnóstico, foram desabilitados manualmente: `etapa1_turnos`, `multimodelo_classificacao`, `multimodelo_reclassificacao`, `comparar_modelos`, `validacao_nao_supervisionada`, `lote_noturno_cache`, `transformer_ft` e `consolidar_validacao`. **Reabilitar quando o realinhamento de G estiver concluído** — o `etapa1_turnos` escreve na coluna G a cada 15 minutos.

1. Preencher a categoria manual Q dos 639 casos restritos, priorizando os 201 conflitos entre fontes marcadas como corretas.
2. Avaliar a viabilidade de uma execução *out-of-fold* integral do BERTimbau sobre toda a base, para permitir sua entrada no ranking principal. O treino atual roda em CPU no runner do GitHub Actions (teto de 6h), o que obriga o modo `auto` a usar subamostragem estratificada (`.github/workflows/transformer_ft.yml`); a base inteira (~13,8 mil chamados) não cabe nesse limite. **Ideia registrada, ainda não decidida:** rodar o fine-tuning em notebook Google Colab (GPU T4/A100), fora do fluxo automatizado por Actions, trazendo os artefatos de volta ao repositório manualmente. Ganho esperado: viabilizar o treino sobre a base inteira. Trade-off: sai do fluxo 100% reprodutível por Action; exige atenção ao levar a credencial da conta de serviço para dentro do notebook.
3. Considerar validação externa em outras instituições para testar a estabilidade dos resultados sob taxonomias e volumes distintos.

## Registro histórico

Decisões anteriores, auditorias, planos concluídos e números substituídos devem ser consultados no histórico do Git e nos Pull Requests. Não devem voltar a ser acumulados neste arquivo.
