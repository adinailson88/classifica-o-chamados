# Classificacao de Chamados

Repositorio experimental para avaliacao da classificacao e reclassificacao automatica de chamados, separado do repositorio operacional Malha IA.

O objetivo e manter um experimento rastreavel, com processamento por turnos, logs, metricas, painel publico e preparacao para validacao humana.

## Prompt pronto — continuar o artigo/capitulo da tese

Copie o bloco abaixo e cole numa conversa nova (pode ser com esforco/raciocinio menor)
para comecar ou continuar a construcao do artigo/capitulo de classificacao de chamados.
O prompt aponta o repositorio, o arquivo de plano, o bloco de continuidade e as fontes
de dado reais — a sessao nao precisa de mais contexto alem disso.

```text
Repositorio: adinailson88/classificacao-chamados (clone local em
C:\Users\adina\repos\classificacao-chamados). Este e o experimento de classificacao/
reclassificacao automatica de chamados de manutencao predial com IA local (LSTM
primario, RF fallback, baseline TF-IDF+LogReg, mais 6 IAs multimodelo — linear_svc,
extra_trees, sgd, random_forest, regressao_logistica, naive_bayes — e um 8o modelo
BERTimbau com fine-tuning), separado do repositorio operacional malha-ia. O objetivo
final e virar um capitulo/artigo da tese de Biossistemas Construidos (PPG UFSB), com
ponte para o outro capitulo de revisao (adinailson88/revisao-bibliografica, MCDM/
TOPSIS/ODS/ESG).

Antes de qualquer coisa:
1. `cd` no clone local, `git pull` e `git log --oneline -5` para confirmar o estado
   do branch main (o historico deste repo pode ser reescrito por limpeza de
   filter-repo — se o pull falhar por divergencia, comparar a arvore/tree do commit
   antigo com a do novo antes de decidir qualquer coisa; nao forcar push sem
   confirmar que o conteudo e equivalente).
2. Ler o arquivo `PLANO_ARTIGO_CAPITULO.md` na raiz do repo INTEIRO, especialmente a
   secao "Estado desta rodada" (onde a redacao parou, o que foi feito por ultimo, e
   qual e o proximo passo). Esse arquivo tem a estrutura fixa do artigo (Resumo,
   Introducao, Referencial conceitual, Metodo 3.1-3.9, Resultados 4.1-4.8, Discussao,
   Consideracoes finais, Referencias, Apendices) mapeada as fontes reais de dado do
   repositorio (`docs/dados/*.json`, `src/*.py`).
3. Ler tambem `AGENTS.md` (regras gerais do repo) e, se existir, `docs/CODEX_PROXIMA_
   SESSAO.md` (pendencia tecnica separada, nao relacionada ao artigo).
4. Nao reaproveitar numeros de auditorias antigas sem reconferir a fonte viva —
   `docs/dados/avaliacao_final.json` (ranking validado por conferencia humana),
   `docs/dados/calibracao.json`, `docs/dados/reclass_resumo.json`,
   `docs/dados/shannon_resumo.json` e correlatos mudam a cada execucao de workflow.
   A conferencia humana (colunas M/N/P da planilha) pode ter avancado desde a ultima
   sessao; conferir antes de citar qualquer percentual de validacao.
5. O rascunho vive em `04_artigo/artigo_classificacao_chamados_v3.md` (versionado
   desde 23/07/2026), com estrutura de titulos ja alinhada ao plano. O `.docx`
   original fica em `04_artigo/` so como registro de proveniencia — nao editar o
   `.docx`, editar o `.md`.
6. Ha um PDF gerado automaticamente a partir desse `.md` e publicado no GitHub
   Pages junto do painel (ver `docs/PLANO_PDF_ARTIGO_PAGES.md` e a secao
   "Publicacao em PDF" de `PLANO_ARTIGO_CAPITULO.md`) — o PDF se regenera quando
   `04_artigo/*.md` muda, mas NAO reescreve numeros no texto sozinho; a
   correspondencia entre resultado e JSON vigente ainda depende de revisao humana.
7. A anomalia de `calibracao.json` (`acerto_validado` = 1.0 em toda faixa de
   confianca) foi diagnosticada e corrigida em 23/07/2026 (viés de selecao em
   `src/calibracao.py`, commits `21258deb` e `617d3ac2`; testes em
   `tests/test_calibracao.py`). Nao e mais pendencia.
8. Duas pendencias tecnicas NOVAS, encontradas em 23/07/2026, ainda sem
   correcao (exigem leitura/escrita direta na planilha, fora do alcance de
   uma sessao sem credenciais): (a) corrupcao de acentuacao (mojibake) nos
   nomes de categoria lidos das abas `CLASSIF__<modelo>` por
   `src/analise_estatistica.py`, contaminando `top_confusoes` em
   `estatistica.json`, `cruzamento_taxonomia.json` e
   `confusao_historico_ia.json`; (b) `total_reclassificado` do Random Forest
   em `reclass_resumo.json` excede o tamanho da base (18.049 > 13.965),
   indicando linhas duplicadas na aba `RECLASS__random_forest` — suspeita de
   falha silenciosa em `linhas_ja_reclass()` (`src/reclassificacao_multimodelo.py`).
   Ver "Estado desta rodada" em `PLANO_ARTIGO_CAPITULO.md`.

Depois de executar o que for pedido nesta rodada, atualizar a secao "Estado desta
rodada" de `PLANO_ARTIGO_CAPITULO.md` (substituir, nao acumular) com: onde parou, o
que foi feito, e o proximo passo — para que a proxima sessao continue sem precisar
de mais contexto do que este prompt e esse arquivo.

Agora: [descreva aqui o que voce quer que a sessao faca nesta rodada — ex.: "revalide
os numeros da secao 4.2 e escreva um rascunho da Discussao (secao 5)", ou "traga o
v3.docx para dentro do repo em 04_artigo/ e converta para Markdown"].
```

## Checklist do artigo (submissão) — verificar aqui antes de qualquer rodada

> Resumo vivo, gerado por auditoria cruzada entre um plano de revisão externo
> de 20 passos (DeepSeek, rodadas de 24/07/2026) e o estado real do
> repositório/artigo, item por item, com evidência (não suposição). O
> detalhe narrativo completo (o quê, quando, por quê) mora em
> `PLANO_ARTIGO_CAPITULO.md`, seção "Estado desta rodada" — **não duplicar
> aqui**, só apontar. Atualizar este bloco (substituir, não acumular) sempre
> que um item mudar de estado.

### Confirmado feito — não repetir em nova rodada
- [x] Aviso de viés de amostra não aleatória no Resumo/Abstract (COCHRAN, 1977)
- [x] Discussão da inferioridade do LSTM frente aos modelos lineares
      (GALKE; SCHERP, 2022)
- [x] Referências completas de *Green AI*/eficiência computacional
      (SCHWARTZ *et al.*, 2020; TREVISO *et al.*, 2023), com entradas
      completas na lista de referências
- [x] Legendas das Figuras 1–3 já autoexplicativas (fonte citada, contexto
      metodológico no texto da legenda)
- [x] Cruzamento amostral de citações × lista de referências sem lacuna
      (COCHRAN 1977; GALKE; SCHERP 2022; GUO *et al.* 2017; PLATT 1999;
      SALTON; BUCKLEY 1988 — todos presentes no corpo E na lista)
- [x] Limitações substantivas já cobertas em prosa (amostra não aleatória,
      dependência de uma instituição, BERTimbau pendente, intermitência do
      Pages) — falta só decidir se formata como subseção numerada "5.4"
      separada (cosmético, não substantivo)
- [x] Snapshot imutável com hash SHA-256 das fontes quantitativas do artigo
      (`docs/dados/snapshots/artigo-v3-20260724/`, via
      `src/gerar_manifesto_snapshot_artigo.py`) — cobre a necessidade de
      "commit estável para reprodutibilidade" sem precisar de tag Git
- [x] **Exclusão do `transformer_ft` republicada** em
      `docs/dados/avaliacao_final.json` e `docs/dados/estatistica.json`, ambos
      gerados em 24/07/2026 às 19:37. O modelo está em `modelos_excluidos`
      porque `bertimbau_training_state.json` permanece em `status=sem_dados`;
      os rankings públicos consideram somente sete modelos comparáveis.
- [x] **Número de chamados corrigido** na linha 315 de
      `04_artigo/artigo_classificacao_chamados_v3.md` (13.825 → 13.965,
      54 → 55 categorias), reconferido contra `docs/dados/resumo.json`
      (`registros: 13965`, `gerado_em: 24/07/2026 20:51`) antes de fixar o
      número — 24/07/2026, rodada 9.
- [x] **"Mojibake" investigado e descartado como alarme falso** — 24/07/2026,
      rodada 9. Verificação byte a byte (não confiar em `print`/terminal:
      Windows renderiza UTF-8 mal por padrão) de `estatistica.json`,
      `cruzamento_taxonomia.json`, `confusao_historico_ia.json` e
      `metricas_por_categoria.json` confirmou os quatro arquivos como
      **UTF-8 válido em sua totalidade**, sem nenhuma ocorrência do
      caractere de substituição Unicode (U+FFFD). O que parecia corrupção
      em rodadas anteriores era artefato de exibição de terminal, não do
      dado publicado. Texto do artigo corrigido (Figura 4 e Limitações);
      a Figura 4 deixa de estar bloqueada por qualidade de dado.
- [x] **Tabela suplementar de métricas por categoria (55 categorias)** —
      script `src/exportar_tabela_por_categoria.py`, gera
      `04_artigo/figuras/tabela_S1_metricas_por_categoria.csv`. Citada no
      artigo, Subseção 4.1, com as 5 categorias de menor e maior
      concordância. **Reescrito em 24/07/2026 (2ª parte da rodada 9)**: o
      Adinailson informou que as métricas por categoria foram movidas para
      uma aba da planilha experimental (`gid=1862157493`, URL
      compartilhada). O script agora tenta ler essa aba viva primeiro
      (via `gspread`/`src/planilha.py`, colunas por cabeçalho normalizado,
      não por posição), e só cai para o JSON público quando não há
      credencial — registrando a fonte usada em cada linha exportada.
      **Conferido contra a aba viva em 24/07/2026 via GitHub Actions**
      (`run 30137147380`, commit `ca081648`): aba
      `TABELA_S1_METRICAS`, cabeçalhos reais `Categoria`, `Support`,
      `Precision`, `Recall`, `F1-Score`. Portanto, a S1 publicada agora
      contém precision/recall/F1 real por categoria, não apenas fallback de
      concordância vs. histórico.
- [x] **Duas direções de trabalho futuro acrescentadas** na Conclusão:
      validação externa em outras IFES e integração com um modelo
      MCDM/TOPSIS de priorização de manutenção (ponte com o capítulo de
      revisão, `PLANO_ARTIGO_CAPITULO.md` §5) — 24/07/2026, rodada 9.
- [x] **Curva real de aprendizado do LSTM gerada** — `src/modelo_lstm.py`
      treinou via workflow com credencial (`run 30137383907`, commit
      `e66b4a40`) e gerou `04_artigo/figuras/lstm_history.json` e
      `04_artigo/figuras/fig5_curva_aprendizado_lstm.png`. Treino com 13.965
      exemplos e 53 categorias; `EarlyStopping` interrompeu após 11 épocas.
      Menor `val_loss`: 1,4374 na época 8; maior `val_accuracy`: 0,6722 na
      época 10.
- [x] **Figura 4 gerada de fato** — `src/gerar_figura4_confusoes.py` lê
      `docs/dados/estatistica.json.top_confusoes` e gera
      `04_artigo/figuras/fig4_top_confusoes.png`. O gráfico usa códigos
      C01-C10 por legibilidade; os nomes reais permanecem em UTF-8 na
      Tabela Suplementar S2.
- [x] **Tabela Suplementar S2 gerada** —
      `04_artigo/figuras/tabela_S2_codigos_categorias_fig4.csv`, mapeando
      código → categoria para a Figura 4.
- [x] **Ablation study real do LSTM executado** — `src/ablation_lstm.py`
      avaliou unidades 64/128 × dropout 0,5/0,3 por 3-fold KFold sobre 9.096
      linhas validadas (`run 30137529732`, commit `fcf39887`). Arquivos
      publicados: `04_artigo/figuras/ablation_lstm_resultados.json`,
      `04_artigo/figuras/tabela_S3_ablation_lstm.csv` e
      `04_artigo/figuras/fig6_ablation_lstm.png`. Resultado: configuração
      atual 64/0,5 = 87,68%; melhor variação 128/0,3 = 88,18% (+0,50 p.p.,
      46 acertos a mais).

### Pendente confirmado — com o arquivo exato a mexer
- [ ] Seções de metadados estilo MDPI (Author Contributions, Funding, Data
      Availability Statement, Conflicts of Interest) — ainda não existem em
      `04_artigo/artigo_classificacao_chamados_v3.md`; só fazem sentido ao
      preparar a versão de submissão a um periódico (hoje o texto é
      capítulo de tese).
- [ ] `analise_R/analise_estatistica.R` está **desconectado do pipeline
      automático** — seu `dados_modelos.txt` precisa ser regerado
      manualmente a partir da planilha atual (9.096 validados) antes de
      usá-lo para conferência cruzada dos números citados no artigo.

### Decisão do pesquisador antes de virar tarefa (não são prompts soltos)
- [ ] **Holdout fixo de treino/teste** — o pipeline usa out-of-fold KFold
      (sem vazamento) avaliado contra a verdade validada humana (9.096
      decisões), o que é metodologicamente mais forte que um holdout clássico
      avaliado só contra rótulo histórico. Implementar um holdout de
      verdade exigiria retreinar os 7 modelos fora do desenho atual e
      redesenhar `etapa1_turnos.yml`/`classificacao_multimodelo.yml`/
      `reclassificacao_multimodelo.yml` — não é uma tarefa de um prompt.
      Escolher entre: (a) documentar a justificativa metodológica atual no
      Método, ou (b) encomendar o redesenho como projeto à parte.
- [ ] **Referências em formato MDPI numérico** — hoje o artigo usa ABNT
      (autor-data), porque é primariamente capítulo de tese. Reformatar
      ~25 referências só faz sentido se decidir formalmente submeter à
      MDPI Computation (ou periódico equivalente) agora.

### Dashboard (`docs/index.html` + `docs/dados/*.json`)
- [ ] Aba **Taxonomia** herda o mesmo mojibake de
      `cruzamento_taxonomia.json`/`confusao_historico_ia.json` — corrigir na
      fonte beneficia painel e artigo ao mesmo tempo.
- [ ] Quando a tabela por categoria existir (item acima), avaliar se também
      entra nas abas `Categorias`/`Métricas`, não só no artigo.
- [x] `avaliacao_final.json`/`estatistica.json` já republicados sem
      `transformer_ft` em rankings — conferir visualmente que as abas
      `Decisão`/`Modelos` não voltaram a referenciá-lo (verificação visual
      ainda não feita nesta auditoria).

## Estado atual

1. A planilha experimental e lida por conta de servico Google Cloud via `gspread`.
2. O ID da planilha nao e versionado; use `SPREADSHEET_ID` ou `spreadsheet_id.local`.
3. A chave da conta de servico nao e versionada; use `credenciais_sa.json` local ou o secret `GCP_SA_KEY` no GitHub Actions.
4. A aba principal e `CHAMADOS_ESQUELETO_REDUZIDO`, com leitura em `A:M`.
5. Os dados reais gerados em `dados/*.json` e `dados/*.jsonl` ficam ignorados no Git.
6. Os dados publicos do dashboard ficam em `docs/dados`.
7. Nenhum script escreve na planilha sem flag explicita `--aplicar`; workflows de reclassificacao rodam em dry-run por padrao.
8. A validacao humana ja pode ser preparada, mas a revisao manual fica **pausada** ate o fortalecimento dos scripts/modelos.

### 7 IAs materializadas (multimodelo)

> Tabela atualizada em 24/07/2026 (rodada 9), a partir de
> `docs/dados/estatistica.json` (gerado 24/07/2026 15:55) e
> `docs/dados/avaliacao_final.json` (gerado 24/07/2026 19:37, 9.096
> validados). Nao copiar estes numeros sem reconferir a fonte viva —
> ambos os JSONs mudam a cada execucao de workflow.

As **7 IAs estao completas** (transformer_ft/BERTimbau excluido por
`status=sem_dados`), com 13.965 chamados por modelo, 0 pendentes e predicao
**out-of-fold** (`kfold_5`, sem vazamento).

| Modelo | Concordancia vs historico | Acerto validado (n=9.096) |
|---|---|---|
| `linear_svc` | 80,34% | 79,89% |
| `extra_trees` | 78,98% | 77,62% |
| `random_forest` | 77,98% | 76,89% |
| `sgd` | 77,84% | 79,09% |
| `regressao_logistica` | 76,91% | 78,59% |
| `naive_bayes` | 69,90% | 71,14% |
| `lstm` | 68,47% | 74,71% |

Onde cada coisa aparece no painel:

- **`Classificacao`** usa apenas a **Etapa 1 / LSTM single-model** (fonte `registros.json`).
- **`Modelos`**, **`Multimodelo`** e **`Estatistica`** trazem a **comparacao das 7 IAs**.
- `multimodelo_registros.json` foi **removido** porque multiplicava chamados por 7 (exibia
  ~96.775 predicoes como se fossem chamados). **Nao recriar.**

A analise estatistica assume **pressupostos nao parametricos**: Shapiro rejeitou
normalidade nos 7 modelos. Por isso o foco e Spearman, Friedman/Nemenyi, Cochran Q,
McNemar e bootstrap. Esta tabela e a secao "Colunas da aba principal" abaixo mostram
numeros **contra o historico**; o acerto **validado por conferencia humana** (M/N/P)
ja existe e cobre 9.096 decisoes travadas sem conflito (68,3% da base) — ver
`docs/dados/avaliacao_final.json` e a tabela do checklist acima.

## Colunas da aba principal

```text
A  ID Chamado
B  TITULO
C  CATEGORIA COMPLETA
D  DESCRICAO GLPI
E  TITULO O.S.M.
F  DESCRICAO O.S.M.
G  Classificacao IA
H  Avaliacao (%)
I  Executor
J  Criticidade Atribuida por IA
K  Comparacao
L  Classificado_Confianca_IA
M  CONFERENCIA GLPI
N  CONFERENCIA IA
O  Classificacao IA - 2
P  CONFERENCIA IA - 2
```

Saida da IA: `G:J`.

`K` compara a classificacao da IA com a categoria historica: `=SE(G="";"";G=C)`.

### Validacao humana (modo de conferencia dupla)

A validacao humana e registrada em DUAS colunas independentes, o que permite avaliar
nao so o acerto da IA, mas tambem a qualidade da propria classificacao historica e,
por consequencia, falsos positivos e falsos negativos:

- `M` (**CONFERENCIA GLPI**): o avaliador marca se a classificacao historica do GLPI
  (coluna `C`) esta `Correto` ou `Errado`. Celula vazia = ainda nao validada.
- `N` (**CONFERENCIA IA**): o avaliador marca se a classificacao da IA (coluna `G`) esta
  `Correto` ou `Errado`. Celula vazia = ainda nao validada.

A combinacao das duas colunas forma uma matriz 2x2 (IA `Correto`/`Errado` x GLPI
`Correto`/`Errado`), que distingue, por exemplo, os casos em que a IA acerta e o
historico erra (a IA corrige o GLPI) dos casos opostos. Convencao de leitura no codigo:
o valor `Correto` (sem distincao de caixa) indica acerto; qualquer outro valor nao vazio
e tratado como `Errado`. A leitura dessas colunas e read-only e nao sobrescreve a planilha.

### Coluna O (`Classificacao IA - 2`): resultado da reclassificacao

A `CONFERENCIA IA` (coluna `N`) refere-se a classificacao ORIGINAL da IA (coluna `G`,
Etapa 1). Quando um chamado e reclassificado (Etapa 2), gravar o novo resultado de volta
em `G` apagaria o registro original e tornaria a conferencia `N` ambigua (o avaliador
disse "Errado" sobre `G`, nao sobre a reclassificacao). Por isso a reclassificacao e
gravada numa coluna propria, `O` (**Classificacao IA - 2**), preservando `G`, `M` e `N`.
Assim e possivel comparar, lado a lado, a classificacao original, o veredito humano e a
reclassificacao. A escrita em `O` e opcional (flag `--gravar-coluna-2` /
input `gravar_coluna_2`), usada com um unico modelo no escopo, e nao toca em nenhuma
outra coluna.

A reclassificacao (coluna `O`) tem sua propria conferencia humana na coluna `P`
(**CONFERENCIA IA - 2**), que funciona como `M` e `N`: o avaliador marca se a
reclassificacao esta `Correto`/`Errado`. Com isso, o painel mede tambem o acerto validado
da reclassificacao (`acerto_reclass_validado` em `calibracao.json`). O ciclo fica:
a IA reclassifica (`O`) e ENTAO aguarda a conferencia humana (`P`) — nenhum passo
automatico consome `O` antes de `P` ser preenchida.

## Fluxo principal

1. Etapa 1: classificacao progressiva em turnos de 15.
2. Etapa 2: reclassificacao de casos de baixa confianca.
3. Fortalecimento antes da etapa manual: LSTM configuravel, memoria validada, reclassificacao priorizando menor confianca e modelo robusto local.
4. Etapa 3: validacao humana.
5. Etapas finais: matriz de confusao, metricas por categoria, confianca calibrada e indicadores consolidados.

## Objetivo final do modelo

Arquivo de referencia: `OBJETIVO_FINAL_MODELO_IA.txt`.

A meta e chegar a um modelo treinado e calibrado que indique, para a maioria das categorias, se a categoria historica do chamado esta correta ou nao. A confianca minima alvo e `>=95%`, mas essa confianca precisa ser validada/calibrada: softmax alto sozinho nao comprova acerto.

Calibracao preliminar publicada:

- `docs/dados/calibracao_modelos.json`: diagnostico bruto por IA (ECE, Brier, faixa >=95%).
- `docs/dados/calibracao_ajustada_modelos.json`: calibracao escalar out-of-fold de
  `P(previsao correta | confianca_bruta)`, ainda contra historico.
- Resultado atual relevante: `linear_svc` continua melhor em concordancia global (`80,26%`)
  e, apos calibracao escalar, sua faixa ajustada `>=95%` tem `n=5.125` e acerto historico
  `98,36%`. Isso ainda nao substitui validacao humana.

O reforco automatico antes da revisao manual esta em:

1. `config_experimento.json`: define `objetivo_final`, `modelo_ia` e `memoria_validada`.
2. `src/modelo_lstm.py`: aceita perfil LSTM `robusto`.
3. `src/memoria_validada.py`: le apenas exemplos humanos com `categoria_validada` e `usar_para_treino=SIM`.
4. `src/executar_etapa1.py` e `src/executar_etapa2.py`: usam a memoria validada quando ela existir.
5. `src/executar_etapa2.py`: prioriza menor confianca antes de reclassificar.
6. `src/classificacao_multimodelo.py` e `src/reclassificacao_multimodelo.py`: executam o ciclo completo por modelo em abas separadas, com predicao out-of-fold.

## Comandos locais

Validacao de sintaxe:

```bash
python -m py_compile src/classificar_etapa.py src/exportar_etapa.py src/registrar_snapshot_inicial.py
```

Testes sem rede:

```bash
python tests/test_github_first.py
```

Fluxo GitHub-first com conta de servico:

```bash
python src/registrar_snapshot_inicial.py
python src/classificar_etapa.py --modo incremental --modelo producao
python src/exportar_etapa.py
python src/exportar_etapa.py --aplicar
```

Etapa 1 progressiva:

```bash
python src/executar_etapa1.py --modelo producao --max-turnos 60
python src/executar_etapa1.py --modelo producao --max-turnos 60 --aplicar
```

Etapa 2, reclassificacao:

```bash
python src/executar_etapa2.py --modelo producao --max-turnos 40
python src/executar_etapa2.py --modelo producao --max-turnos 40 --aplicar
```

Multimodelo completo:

```bash
python src/classificacao_multimodelo.py --modelos leves --max-turnos 1
python src/reclassificacao_multimodelo.py --modelos leves --max-turnos 1
```

Para gravar resultados na planilha, acrescente `--aplicar` somente depois de revisar o dry-run.

Preparacao da validacao humana:

```bash
python src/preparar_validacao_humana.py --modo divergentes --limite 0
python src/preparar_validacao_humana.py --modo divergentes --limite 0 --aplicar
```

Reset controlado do experimento:

```bash
python src/resetar_experimento.py
python src/resetar_experimento.py --aplicar --confirmar RESETAR
```

## Workflows

1. `etapa1_turnos.yml`: classificacao progressiva, agendada a cada 15 minutos.
2. `dashboard.yml`: exporta os JSONs publicos do painel para `docs/dados`, agendado a cada 30 minutos.
3. `etapa2_reclassificacao.yml`: reclassificacao, disparo manual.
4. `reclassificacao_robusta.yml`: modelo pesado local, disparo manual.
5. `preparar_validacao.yml`: monta a aba `VALIDACAO_HUMANA`, disparo manual.
6. `resetar.yml`: reset seguro, disparo manual com confirmacao.
7. `classificacao_incremental.yml`: fluxo incremental antigo, mantido manual.
8. `multimodelo_classificacao.yml`: classificacao por modelo em `CLASSIF__<modelo>`, manual, dry-run por padrao.
9. `multimodelo_reclassificacao.yml`: reclassificacao por modelo em `RECLASS__<modelo>`, manual, dry-run por padrao.
10. `reclassificar_validados.yml`: reclassifica os chamados ja validados (colunas `M` e `N` preenchidas) com o modelo robusto, gravando o resultado na coluna `O` (Classificacao IA - 2). **Manual** (`workflow_dispatch`): o cron de 15 min esta comentado/pausado no YAML para evitar disputa pela coluna `O`. No maximo 15 chamados por execucao; so treina quando ha validados pendentes.
11. `transformer_ft.yml`: 8o modelo, **BERTimbau com fine-tuning** (contextual, self-attention). PESADO (torch + transformers, fine-tuning em CPU). **Noturno condicionado** (cron `17 5 * * *` ≈ 02:17 BRT) + manual; ver secao "BERTimbau" abaixo. Acoes: `reclassificar_validados` (refaz a coluna `O`) ou `comparar` (janela held-out -> `COMPARACAO_MODELOS`).
12. `iniciar_pipeline.yml`: orquestrador manual que dispara Etapa 1 + reclassificar_validados + dashboard de uma vez.
13. `relevancia_termos.yml`: termos caracteristicos por categoria + mapa de correlacao, manual, dry-run por padrao; commita os JSON agregados.

O indice completo dos workflows (todos os 24, com gatilho, entrada, saida e a aba do
painel que cada um alimenta) esta versionado em `docs/dados/workflows_index.json` e e
exibido na aba **Fluxo de atualizacao** do dashboard. Mantenha esse JSON atualizado ao
criar ou alterar um workflow.

### Automacao condicionada (geracao de dados sem depender de disparo manual)

Os fluxos que geram dados deixaram de depender so de disparo manual. Cada um tem
`workflow_dispatch` (manual, que **ignora a guarda** e sempre roda) **e** um gatilho
automatico:

- **Automatico** (leves, so leitura): `auditar_conferencias.yml` (a cada 6 h),
  `relevancia_termos.yml` (diario, `aplicar=false`), alem dos ja existentes
  `etapa1_turnos`, `estatistica`, `multimodelo_reclassificacao`, `transformer_ft`,
  `lote_noturno_cache`.
- **Automatico condicionado** (pesados, com guarda de avanco):
  - `avaliacao_final.yml` — a cada 6 h, mas a parte pesada (bootstrap/ensembles) so
    roda com **+100 conferencias humanas** novas (`validados`).
  - `comparar_modelos.yml` — diario, so roda com **base +1000 chamados** ou comparacao
    ainda vazia.
  - `multimodelo_classificacao.yml` — semanal, so materializa (modelos **leves**) com
    **base +1000 chamados** ou multimodelo ainda vazio.

A guarda e `src/guard_automacao.py`: compara uma metrica de `docs/dados/resumo.json`
(`registros` ou `calibracao.validados`) com o marcador em `dados/estado_automacao.json`.
Sem avanco suficiente, encerra **com sucesso** e log claro (nao falha o workflow); com
avanco, gera os JSON reais e so entao avanca o marcador. O `dashboard.yml` permanece
intacto como publicador (cron 30 min + `workflow_run`) e republica o painel apos esses
fluxos. As escritas continuam serializadas por `concurrency: escrita-planilha`, sem loop
de publicacao. Fluxos destrutivos ou que gravam a coluna `O`
(`reclassificar_validados`, `classificacao_ia_2_aplicar`, `resetar`) seguem **manuais**.

### BERTimbau (fine-tuning) — limite do runner e modos

O fine-tuning do BERTimbau (`transformer_ft.yml`) treina sobre a base historica
(`reclassificar_validados.py` usa "base menos o lote", ~13,8 mil chamados) em **CPU**.
Runners **GitHub-hosted tem teto rigido de 6 h por job** — `timeout-minutes` acima de
360 nao tem efeito. O treino de base inteira em CPU NAO cabe em 6 h; por isso o job
ficava ~6 h e era morto antes de gerar a coluna `O`, deixando a aba Reclassificacao/
Decisao sem dados.

Correcoes:
- **`timeout-minutes: 330`** (abaixo do teto) + **orcamento de tempo interno**
  (`TRANSFORMER_TIME_BUDGET_S=18000`): o treino para sozinho, **salva o melhor modelo**
  e encerra com sucesso antes de ser morto — nunca mais fica indefinidamente preso.
- **`concurrency: bertimbau-finetune`** (grupo proprio): um treino de horas **nao
  bloqueia** `etapa1_turnos`/`dashboard` (que usam `escrita-planilha`).
- **Guarda** (`src/guard_automacao.py`, `chave=transformer_ft`): no modo `auto` so
  treina com **+100 conferencias humanas** novas; senao encerra com sucesso e registra
  o motivo. Estado em `docs/dados/bertimbau_training_state.json` (mostrado na aba
  **Fluxo de atualizacao**).
- **Otimizacoes** (em `src/modelos_zoo.py`, todas opt-in por env; default preserva o
  comportamento atual): **padding dinamico** (por lote), **early stopping** por
  macro-F1 de validacao com `load_best_model_at_end`, **subamostragem estratificada**
  (`TRANSFORMER_MAX_TRAIN`), `fp16` quando ha GPU, e logs de tempo por epoca.

Modos (input `modo` do `workflow_dispatch`; cron usa `auto`):
- **`smoke`**: teste rapido com dados sinteticos, **sem secrets** e sem planilha
  (`src/smoke_transformer.py`) — valida o pipeline barato.
- **`auto`**: noturno condicionado. Subamostra estratificada (`TRANSFORMER_MAX_TRAIN=4000`)
  + early stopping para **caber no runner**.
- **`manual`**: treino completo (base inteira, metodologia original).
- **`force`**: manual ignorando a regra das 100 conferencias (mantem as validacoes de
  secret/dados).
- **`full`**: alias explicito para base completa; mantem o caminho de validacao futura
  sem subamostra.
- **`cluster_coreset`**: diagnostico e selecao representativa experimental, sem
  fine-tuning. Gera TF-IDF + KMeans por categoria, preserva categorias raras,
  baixa confianca, divergencias IA/historico, divergencias humanas e alta
  divergencia entre modelos quando publicada em `shannon_votos.json`.

> **Qualidade vs. custo:** o modo `auto` usa subamostra para caber em CPU/6 h — e uma
> variante operacional para manter a coluna `O` fresca, **nao** substitui a avaliacao
> rigorosa. As metricas autoritativas por categoria (acuracia, precision, recall, F1
> macro, matriz de confusao) vem da acao `comparar` -> `COMPARACAO_MODELOS` ->
> `estatistica.json`, com a **base inteira**. Para fine-tuning de fidelidade total
> (base inteira, varias epocas) sem o teto de 6 h, use **self-hosted runner** ou divida
> o treino; os hiperparametros nao foram alterados no default justamente para nao
> degradar qualidade sem comparacao medida.

#### `cluster_coreset` experimental

O modo `cluster_coreset` prepara uma alternativa de reducao de custo antes de qualquer
novo treino caro. Ele **nao treina** o BERTimbau e **nao vira padrao**. A selecao e
por categoria: categorias com ate `categoria_rara_max` exemplos ficam integrais; nas
categorias volumosas, o script agrupa os textos por TF-IDF + KMeans, preserva exemplos
proximos ao centroide, outliers, possiveis fronteiras, baixa confianca, divergencias
IA x historico, divergencias humanas e linhas com alta entropia de votos entre modelos.

Artefatos:

- `dados/bertimbau_coreset_ids.json`: lista auditavel de linhas selecionadas, com
  `id_hash` e sem texto do chamado.
- `docs/dados/bertimbau_coreset_resumo.json`: resumo agregado publicado no dashboard.
- `docs/dados/bertimbau_token_stats.json`: estimativa de tokens antes/depois.
- `docs/dados/bertimbau_cluster_report.json`: parametros, clusters e duplicatas.
- `docs/dados/bertimbau_review_queue.json`: fila sugestiva de conferencia humana.

Comando local sem planilha, apenas para validar o codigo:

```bash
python src/bertimbau_coreset.py --fixture 120 --max-total 60
```

Comando real via Actions, sem treino:

```bash
gh workflow run transformer_ft.yml -f modo=cluster_coreset -f coreset_max_total=4000
```

O criterio de seguranca permanece: nao tornar `cluster_coreset` padrao se houver queda
maior que `0,02` no F1 macro, piora em categoria rara ou instabilidade. A comparacao
futura deve confrontar `full`, `auto_subamostra` e `cluster_coreset` em acuracia,
precisao/recall/F1 por categoria, F1 macro, matriz de confusao, tempo, total de
exemplos e tokens estimados.

#### Treinar sobre o coreset e decidir (porta de aprovacao)

O coreset deixa de ser so diagnostico quando voce TREINA sobre ele e compara com o
treino completo:

1. **Treino full** (referencia): `modo=full` (ou `manual`), `acao=comparar` — avalia
   held-out e grava metricas em `COMPARACAO_MODELOS` -> `estatistica.json`.
2. **Treino coreset**: `modo=full`, `acao=comparar`, `selecao_treino=cluster_coreset`
   — o fine-tuning usa a MESMA selecao por clustering (`TRANSFORMER_SELECT=cluster_coreset`
   em `src/modelos_zoo.py`, reutilizando `src/bertimbau_coreset.py`), sobre a mesma
   janela held-out.
3. **Decisao**: com as duas metricas (JSON `{f1_macro, acuracia, por_categoria:{cat:{f1,
   suporte}}}`), rode:
   ```bash
   python src/comparar_coreset.py --full metr_full.json --coreset metr_coreset.json \
       --tempo-full-s <s> --tempo-coreset-s <s>
   ```
   Ele grava `decisao` em `docs/dados/bertimbau_coreset_resumo.json`:
   - **`rejeitado`**: queda de F1 macro > `0,02` **ou** piora numa categoria rara
     (suporte <= 30) maior que `0,05`.
   - **`aprovado`**: F1 macro equivalente ou melhor (queda <= `0,005`) e sem piora em
     raras/criticas.
   - **`experimental`**: intermediario — precisa de mais evidencia.

So apos `decisao = aprovado` faz sentido considerar `cluster_coreset` no automatico
noturno; ate la, o automatico segue na subamostra estratificada (`auto`) e o treino
**`full` permanece sempre disponivel**. A decisao e mostrada no card do BERTimbau no
dashboard (aba **Fluxo de atualizacao**) e e reversivel: basta nao promover o modo.

Todos os workflows que escrevem dados compartilham `concurrency: group: escrita-planilha`
com `cancel-in-progress: false`, ou seja, sao **serializados** — nao ha escrita
simultanea nos mesmos arquivos. O `dashboard.yml` republica o painel automaticamente
(via `workflow_run`) quando os fluxos de dados concluem com sucesso.

Nos workflows manuais com input `aplicar`, mantenha `false` ate revisar logs, ganho liquido e impacto esperado.

Dependencias em CI:

- `requirements-leves.txt`: base comum sem TensorFlow (`gspread`, `google-auth`, `numpy`, `scikit-learn`).
- `requirements.txt`: ambiente completo com TensorFlow, usado quando o fluxo realmente precisa de LSTM/producao.
- `requirements-robusto.txt`: transformer local pesado, usado apenas nos fluxos de reclassificacao robusta.

## Dashboard publico

O painel esta em:

```text
docs/index.html
```

Ele consome:

```text
docs/dados/resumo.json
docs/dados/registros.json                 # Etapa 1 / LSTM (aba Classificacao)
docs/dados/log_turnos_classificacao.json
docs/dados/metricas_por_categoria.json
docs/dados/log_turnos_reclassificacao.json
docs/dados/metricas_experimento.json
docs/dados/comparacao_modelos.json
docs/dados/comparacao_categoria.json
docs/dados/comparacao_previsoes.json    # versao sanitizada, sem ID/titulo/observacao
docs/dados/multimodelo_turnos.json        # 7 IAs (abas Modelos / Multimodelo)
docs/dados/multimodelo_metricas.json      # 7 IAs
docs/dados/multimodelo_reclass_turnos.json
docs/dados/estatistica.json               # analise nao parametrica (aba Estatistica)
docs/dados/calibracao.json
docs/dados/calibracao_modelos.json        # diagnostico bruto por IA
docs/dados/calibracao_ajustada_modelos.json # calibracao escalar preliminar por IA
docs/dados/shannon_resumo.json            # criterios e destaques da camada Shannon
docs/dados/shannon_modelos.json           # entropia por IA
docs/dados/jensen_shannon_modelos.json    # distancia distributiva IA x historico
docs/dados/shannon_categorias.json        # ambiguidade por categoria historica
docs/dados/shannon_votos.json             # linhas sanitizadas com maior desacordo entre IAs
docs/dados/workflows_index.json           # indice tecnico dos workflows (aba Fluxo de atualizacao)
```

O site publicado pelo GitHub Pages deve identificar o projeto como `Classificacao de Chamados - Painel Experimental`. A referencia a Malha IA deve aparecer apenas como contexto de origem, nao como nome principal do site.

### Dados parciais e tolerancia a JSON ausente

O painel **nao depende de o experimento estar 100% concluido** para renderizar. Cada
renderizador degrada com seguranca:

- `getJSON()` devolve `[]` quando o arquivo nao existe ou falha; o boot normaliza
  com `Array.isArray(...)` / `|| {}`, entao nenhuma aba quebra por um JSON faltante.
- Quando um JSON ainda esta vazio (`[]` / `{}`), a aba mostra uma **mensagem
  controlada** ("Sem ... publicado", "aguardando conferencia humana") com o link do
  workflow que precisa rodar, em vez de um grafico ou tabela vazia sem explicacao.
- A aba **Modelos** usa `estatistica.json` como fallback quando os JSON multimodelo
  ainda estao vazios, identificando o resultado como concordancia vs. historico.
- Metricas dependentes de validacao humana (M/N/P) so aparecem como **definitivas**
  quando ha conferencia suficiente; antes disso sao rotuladas como parciais.

### Aba "Fluxo de atualizacao" (indice tecnico dos workflows)

A aba **Fluxo de atualizacao** lista todos os workflows com gatilho, o que fazem,
entrada, saida, aba(s) alimentada(s), quando executar manualmente e observacoes. Ela
e gerada a partir do arquivo versionado `docs/dados/workflows_index.json` — **fonte de
verdade**: ao criar ou alterar um workflow em `.github/workflows/`, atualize tambem
esse JSON.

### Validar o painel localmente

```bash
cd docs
python -m http.server 8765
# abra http://localhost:8765/index.html
```

Servir por HTTP (e nao abrir o arquivo por `file://`) e necessario porque o painel
busca os JSON via `fetch("./dados/...")`. Checagem rapida de que tudo renderiza:

1. Abra o console do navegador — nao deve haver erro de JavaScript.
2. Percorra as abas Classificacao, Categorias, Metricas, Modelos, Reclassificacao,
   Decisao e Fluxo de atualizacao: cada uma deve mostrar dados reais **ou** uma
   mensagem controlada de "dados ainda nao gerados".
3. Valide os JSON antes de publicar:
   ```bash
   python -c "import json,glob; [json.load(open(p,encoding='utf-8')) for p in glob.glob('docs/dados/*.json')]" && echo OK
   ```

## PDF do artigo/capitulo no GitHub Pages

O rascunho do artigo/capitulo da tese (`04_artigo/artigo_classificacao_chamados_v3.md`)
e publicado automaticamente em PDF, ao lado do painel:

```text
https://adinailson88.github.io/classificacao-chamados/artigo_classificacao_chamados.pdf
```

Tambem ha um link direto no cabecalho do painel (`docs/index.html`). Gerado pelo
workflow `.github/workflows/artigo_pdf.yml` (pandoc + xelatex) a cada push que
altere esse `.md`, ou por disparo manual. **Limitacao deliberada**: o PDF sempre
acompanha o texto do `.md` fielmente, mas nao reescreve numeros sozinho quando so
os JSONs de `docs/dados/` mudam — a revalidacao de numeros continua manual. Ver
`docs/PLANO_PDF_ARTIGO_PAGES.md` para o desenho completo e o historico de achados
tecnicos (ex.: correcao de vies em `calibracao.py`, 2026-07-23).

## Relevancia de termos + mapa de correlacao (exploratorio)

`src/relevancia_termos.py` calcula, por categoria, os **termos caracteristicos**
(log-odds com prior de Dirichlet + peso TF-IDF — ex.: `agua`, `torneira`, `sanitario`
para hidraulica) e o **mapa de correlacao** entre categorias (cosseno entre centroides
TF-IDF). E uma triagem de **taxonomia**, nao uma metrica de acuracia: nao decide categoria
e nao altera o historico. Saidas agregadas e sanitizadas em `docs/dados/termos_relevantes.json`
e `docs/dados/correlacao_categorias.json`; visualizador (mapa de calor estilo
geoprocessamento) em `docs/mapa_correlacao.html`. Workflow manual `relevancia_termos.yml`,
dry-run por padrao. Detalhes em `docs/RELEVANCIA_TERMOS.md`.

```bash
python src/relevancia_termos.py --top-n 25 --min-df 5 --min-chamados-categoria 10
```

`src/cruzamento_taxonomia.py` cruza a **matriz de confusao IA×historico** com a correlacao
vocabular e ranqueia os **candidatos a revisao de taxonomia** (pares confundidos pela IA E
com vocabulario sobreposto -> fusao/desambiguacao, etapa 46). Gera
`docs/dados/confusao_historico_ia.json` e `docs/dados/cruzamento_taxonomia.json`, exibidos no
mesmo visualizador. Roda junto no workflow `relevancia_termos.yml`.

```bash
python src/cruzamento_taxonomia.py --top 40 --min-df 5 --min-chamados-categoria 10
```

## Shannon / Jensen-Shannon (ambiguidade e governanca)

`src/analise_shannon.py` calcula uma camada informacional sobre os JSONs publicos do
dashboard. Ela mede dispersao das previsoes por IA, ambiguidade por categoria historica,
desacordo de votos entre IAs e divergencia Jensen-Shannon entre a distribuicao prevista
por cada IA e a distribuicao historica. Nao e acuracia, nao substitui validacao humana e
nao grava nada na planilha.

Saidas sanitizadas em `docs/dados`: `shannon_resumo.json`, `shannon_modelos.json`,
`jensen_shannon_modelos.json`, `shannon_categorias.json` e `shannon_votos.json`.
O dashboard exibe esses dados na aba **Shannon**. O workflow `dashboard.yml` roda essa
analise automaticamente apos `src/exportar_dashboard.py`.

```bash
python src/analise_shannon.py
```

## Documentacao

1. `CONTEXTO.md`: panorama vivo do repositorio, decisoes e proximos passos.
2. `docs/GUIA_TECNICO.md`: explicacao dos scripts, colunas, executores e fluxos.
3. `dados/README.md`: schemas dos artefatos JSON internos.
4. `docs/index.html`: painel publico com graficos, tabelas, metricas e aba de documentacao.
5. `docs/RELEVANCIA_TERMOS.md`: termos caracteristicos por categoria + mapa de correlacao.
6. `docs/RELATORIO_ESTADO_ATUAL.md`: diagnostico tecnico/metodologico desta revisao.
7. `docs/METODOLOGIA_SHANNON.md`: calculos, fontes, interpretacao e limitacoes da camada Shannon.
8. `docs/CONTRIBUICAO_SHANNON_ARTIGO.md`: texto tecnico para artigo e conclusao.
9. `PLANO_ARTIGO_CAPITULO.md`: estrutura do artigo/capitulo da tese mapeada as fontes de dado do repo, com o bloco de continuidade "Estado desta rodada" (ver tambem o prompt pronto no topo deste README).

## Apps Script

`apps_script/Code.gs` e legado. O fluxo principal atual usa conta de servico com `gspread`.

Manter Apps Script apenas como referencia historica ou alternativa ate decisao de remocao definitiva.

## Privacidade

Nao versionar credenciais, IDs privados de planilha, tokens, URLs privadas de Web App ou arquivos JSON que contenham texto real de chamados.
