# Plano — Artigo/Capítulo "Classificação de Chamados com IA" (tese Biossistemas)

> Documento único desta finalidade. Não criar `PLANO_ARTIGO_v2.md`, `RASCUNHO_*.md` ou
> similares — **atualizar este arquivo** a cada rodada, na seção "Estado desta rodada"
> logo abaixo. Segue a mesma convenção de `PLANO_CALIBRACAO.md`, `FALTA_FAZER.md` e
> `CONTEXTO.md` já usada neste repositório (ver [[memoria-transferencia-codex]]).
>
> Escopo: o capítulo/artigo empírico sobre o **experimento de classificação/
> reclassificação de chamados com IA local** (LSTM/RF/multimodelo/BERTimbau), que se
> torna capítulo da tese e pode também virar submissão própria. É a contraparte
> empírica do artigo de revisão (`adinailson88/revisao-bibliografica`, MCDM/TOPSIS/
> ODS/ESG) — ver Seção 5 sobre a ponte entre os dois.

## Regra de execução (ler antes de mexer no artigo)

Toda vez que o Adinailson pedir para avançar neste capítulo/artigo, a sessão deve, na
ordem:

1. **Ler a seção "Estado desta rodada"** abaixo antes de escrever qualquer texto novo.
2. Revalidar contra a fonte viva do repositório os números que pretende citar (dados
   de `docs/dados/*.json` mudam a cada execução de workflow — ver regra de
   revalidação em [[artigo-metodologia-biossistemas]]). Não reaproveitar números de
   auditorias antigas sem conferir a data.
3. Ao terminar o que foi pedido nesta rodada, **substituir** (não acrescentar sem
   critério) a seção "Estado desta rodada" com três blocos obrigatórios:
   - **Onde está**: em qual seção/etapa do plano abaixo (ex.: "Seção 4.2 do artigo,
     aguardando fechar 4.6").
   - **O que foi feito nesta rodada**: resumo verificável (arquivos alterados,
     números conferidos, o que foi descartado e por quê).
   - **Próximo passo**: uma ação concreta e priorizada, não uma lista genérica.

Isso substitui a necessidade de o usuário reexplicar contexto a cada nova conversa.

---

## Estado desta rodada

> **AVISO PARA QUEM FOR MERGEAR**: esta rodada (13, Passo 2) foi escrita no
> branch `fix/transformer-ft-fallback-explicito`, ramificado do mesmo commit
> de main que os branches `fix/vies-amostra-validada` (PR #54) e
> `feat/categoria-correta-manual` (PR #55) — cada um TAMBEM reescreveu esta
> secao "Estado desta rodada" com seu proprio conteudo de rodada 13. Os 3
> PRs vao conflitar aqui. Ao mergear, NAO pegar so o "ultimo que mergear
> por acaso" — ler os 3 blocos e escrever manualmente uma secao final que
> cubra os 3 (viés da amostra validada, coluna de categoria manual,
> transformer_ft com fallback explicito), com a rodada seguinte (14) em
> diante.

**Data**: 2026-07-25 (America/Bahia, UTC-03:00) - rodada 13 (Passo 2 do
prompt de 6 passos: transformer_ft com fallback silencioso para LSTM).

**Onde está**: Passo 2 (crítico) do prompt de revisão de 6 passos que a
outra sessão (Codex, bloqueada por limite de uso até 29/07) começou a
executar. Passo 1 já tratado em paralelo (PR #54 + #55, branches
diferentes). Corrigido em branch + PR, não mergeado ainda.

**O que foi feito nesta rodada**:
1. Confirmado em código (`src/modelos_zoo.py:181-186`,
   `.github/workflows/multimodelo_classificacao.yml`) e em log real de
   produção (run `29550863840`, 17/07/2026) que o cron automático de
   classificação nunca instala `torch`/`transformers`, e que a
   materialização inteira publicada como `transformer_ft`
   (13.954/13.965 linhas, `kfold_5`) foi feita via fallback silencioso
   para LSTM — sem nenhum registro desse desvio em artefato publicado.
2. `modelos_zoo._ModeloTransformerFT` ganhou a propriedade `usou_fallback`.
3. `classificacao_multimodelo.prever_out_of_fold()` agora retorna um 4º
   valor (`usou_fallback`); os 4 chamadores (`classificacao_multimodelo.py`,
   `reclassificacao_multimodelo.py`, `ablation_lstm.py`,
   `tests/test_decisao_memoria.py`) atualizados.
4. `classificar_modelo()`/`reclassificar_modelo()` recusam publicar
   quando `usou_fallback=True` — nada gravado em
   `CLASSIF__<modelo>`/`MULTIMODELO_TURNOS`/`RECLASS__<modelo>`, aviso
   explícito no log. O cron automático vira no-op para `transformer_ft`
   até rodar com as dependências reais instaladas.
5. 4 testes novos (`tests/test_transformer_fallback_explicito.py`),
   rodando no mesmo ambiente sem torch/transformers real (não mockado).
   Suíte completa: 71/71.
6. Artigo (Limitações) e README atualizados com a causa raiz e a
   confirmação de que os artefatos `transformer_ft` publicados antes
   desta correção não são confiáveis.

**Não feito nesta rodada (Passo 2, itens (c)/(d) parcial — aguardando
decisão do Adinailson)**: os artefatos JÁ publicados sob `transformer_ft`
(aba `CLASSIF__transformer_ft`, 13.954 linhas contaminadas;
`docs/dados/registros_transformer_ft.json`; linha `transformer_ft` em
`multimodelo_metricas.json`) ainda não foram limpos/marcados — decidir se
apaga a aba ou só documenta como contaminada.

**Próximo passo**: (1) decidir com o Adinailson se limpa os artefatos
`transformer_ft` já publicados (item acima); (2) revisar/mergear os PRs
#54, #55 e este; reconciliar manualmente a seção "Estado desta rodada"
(ver aviso no topo); (3) Passos 3–6 do prompt de 6 passos seguem
pendentes, aguardando o Codex (29/07) ou nova decisão de prosseguir sem
ele.

---

### Histórico da rodada 12 (rematerialização completa dos 7 modelos; discrepância do LSTM resolvida)

**Onde esta**: a discrepancia do ablation do LSTM (sinalizada na rodada 10,
investigada nas rodadas 11-14) esta **resolvida**. O Adinailson confirmou
explicitamente a decisao de rematerializar os 7 modelos comparaveis por
completo (nao so o LSTM), em vez de preservar o valor oficial historico como
as rodadas anteriores haviam decidido conservadoramente. Executado e
verificado nesta rodada, com credencial, via GitHub Actions (nao localmente
-- esta sessao segue sem `credenciais_sa.json`/`SPREADSHEET_ID` local).

**O que foi feito nesta rodada**:
1. Investiguei `src/classificacao_multimodelo.py`: o fluxo e incremental
   (so processa linhas pendentes) e nunca abre a aba principal para
   escrita -- so le `CHAMADOS_ESQUELETO_REDUZIDO` e escreve em
   `CLASSIF__<modelo>`/`MULTIMODELO_TURNOS`/`MULTIMODELO_METRICAS`.
2. Criei `src/limpar_classif_multimodelo.py` (novo): limpa SOMENTE essas
   tres abas, restrito aos modelos passados (`comparaveis` = 7, nunca
   `transformer_ft` por padrao). Confirmado por teste que o codigo-fonte
   nao contem a string `aba_principal`. Dry-run por padrao. 8 testes
   offline novos (fake worksheet/spreadsheet) em
   `tests/test_limpar_classif_multimodelo.py`. Suite completa: 50/50.
3. Adicionei a tarefa `limpar_multimodelo` ao workflow "Pendencias artigo
   com credencial" (`.github/workflows/lstm_artigo.yml`), com
   `aplicar_limpeza` boolean (default false).
4. Rodei o dry-run via `gh workflow run` (run `30144116442`): confirmou
   13.965 linhas por modelo em `CLASSIF__<modelo>` x7, 6.524 linhas de
   `MULTIMODELO_TURNOS` (932 do `transformer_ft` preservadas), 7 linhas de
   `MULTIMODELO_METRICAS` (1 do `transformer_ft` preservada). Reportei ao
   Adinailson antes de aplicar; ele confirmou explicitamente.
5. Apliquei de verdade (run `30144225377`): numeros identicos ao dry-run,
   sucesso.
6. Disparei `classificacao_multimodelo.yml` com os 7 modelos, `max_turnos=0`,
   `aplicar=true` (run `30144280472`): rematerializou 13.965/13.965 por
   modelo, 0 pendentes, `kfold_5`. Concordancia vs. historico ficou
   praticamente igual a antes (ex.: LSTM 68,13% vs. ~68% anterior) -- essa
   metrica nunca foi onde a anomalia aparecia.
7. Disparei `avaliacao_final.yml` (run `30144740084`, sucesso) e
   `estatistica.yml` (primeira tentativa `30144742053` cancelada por
   concorrencia; redisparada com sucesso, run `30144847227`).
8. **Resultado**: todos os 7 modelos subiram ~15 pontos percentuais de
   acerto validado -- a materializacao de 16-17/07 estava genericamente
   desatualizada, nao so para o LSTM. Ranking relativo **inalterado**.
   Acerto validado novo (n=9.096, `avaliacao_final.json` gerado
   25/07/2026 01:52): linear_svc 0,9494; sgd 0,9391; regressao_logistica
   0,9349; extra_trees 0,9265; random_forest 0,9210; **lstm 0,8869** (perto
   dos 0,8635 do ablation corrigido por GroupKFold -- diferenca residual de
   2,34 p.p., atribuivel a `k_folds` diferente entre os dois protocolos:
   3 no ablation, 5 na materializacao oficial); naive_bayes 0,8607. Nenhum
   ensemble supera linear_svc isolado com significancia (McNemar p<0,05
   em favor do linear_svc nos tres).
9. Atualizei `04_artigo/artigo_classificacao_chamados_v3.md`: Tabela 1
   (Subsecao 4.1, concordancia vs. historico), Tabela 2 (Subsecao 4.2,
   acerto validado + ensembles), a ressalva da Figura 6 (Subsecao 4.9,
   de "suspeito" para "investigado e resolvido"), o paragrafo da
   Discussao com a serie historica de 3 consolidacoes (16/07 -> 24/07 ->
   25/07), a quinta limitacao (ablation), e os numeros do Resumo/Abstract
   e das Considerações Finais que citavam os valores antigos do LSTM
   (0,7471) e do LinearSVC (0,7989). Varredura final confirmou zero
   ocorrencia residual dos numeros antigos fora de contexto historico
   intencional.
10. Atualizei o bloco do `README.md` de "BLOQUEADOR" para "RESOLVIDO", com
    o historico completo da investigacao e o resultado final, e a tabela
    "7 IAs materializadas" com os numeros de 25/07/2026.

**Nao rematerializado nesta rodada (fora de escopo, decisao futura)**: a
Etapa 1 oficial de producao (executor LSTM/RF, coluna G da planilha, usada
no dashboard publico `Classificacao`) pode estar sujeita a defasagem
semelhante -- nao foi tocada.

**Proximo passo**: gerar novo snapshot imutavel (`gerar_manifesto_
snapshot_artigo.py`) refletindo os numeros de 25/07/2026, regenerar o PDF,
e revisar visualmente as abas `Decisao`/`Modelos` do painel publico contra
os novos JSONs. Continuam fora de escopo, aguardando decisao do
Adinailson: holdout fixo de treino/teste e reformatacao das referencias
para o padrao MDPI numerico.

---

### Histórico da rodada 9 (fechada em 2026-07-24, ver acima a auditoria)
1. **S1 viva confirmada e publicada**: a execução local de
   `python src/exportar_tabela_por_categoria.py` bloqueou por ausência local de
   `SPREADSHEET_ID`, mas o workflow manual foi disparado com secrets do GitHub
   (`run 30137147380`) e leu a aba `TABELA_S1_METRICAS` (`gid=1862157493`).
   Cabeçalhos reais impressos no log: `Categoria`, `Support`, `Precision`,
   `Recall`, `F1-Score`. O CSV real foi publicado em
   `04_artigo/figuras/tabela_S1_metricas_por_categoria.csv` pelo commit
   `ca081648`, e a Subseção 4.1 foi atualizada para usar F1 por categoria.
2. **Figura 4 gerada de fato**: novo script
   `src/gerar_figura4_confusoes.py` lê `docs/dados/estatistica.json`, campo
   `top_confusoes` (gerado em 24/07/2026 20:52), agrega os pares direcionais
   mais frequentes entre os top pares dos modelos e grava
   `04_artigo/figuras/fig4_top_confusoes.png`. O artigo foi atualizado na
   Subseção 4.8. O maior par agregado foi `Climatização > Ar condicionado` para
   `Manutenção Preventiva > Ar condicionado split` (1.310 ocorrências).
3. **Tabela Suplementar S2 gerada**: como a Figura 4 usa códigos C01-C10 por
   legibilidade, foi gerado
   `04_artigo/figuras/tabela_S2_codigos_categorias_fig4.csv` com o mapeamento
   código-categoria, preservando os nomes reais em UTF-8.
4. **CLI de treino real do LSTM preparada**: `src/modelo_lstm.py` agora pode ser
   executado diretamente para treinar o LSTM, chamar `salvar_history()` e gerar
   `04_artigo/figuras/lstm_history.json` e
   `04_artigo/figuras/fig5_curva_aprendizado_lstm.png`. O workflow
   `30137383907` executou o treino real com 13.965 exemplos e 53 categorias;
   `EarlyStopping` interrompeu após 11 épocas. Menor `val_loss`: 1,4374 na
   época 8; maior `val_accuracy`: 0,6722 na época 10. Arquivos publicados pelo
   commit `e66b4a40`.
5. **Ablation study executado com dados vivos**: `src/ablation_lstm.py`
   comparou 64/128 unidades × dropout 0,5/0,3 por 3-fold KFold sobre 9.096
   linhas validadas, medindo acerto contra verdade validada humana. O workflow
   `30137529732` publicou `04_artigo/figuras/ablation_lstm_resultados.json`,
   `04_artigo/figuras/tabela_S3_ablation_lstm.csv` e
   `04_artigo/figuras/fig6_ablation_lstm.png` pelo commit `fcf39887`.
   Resultado: configuração atual 64/0,5 = 87,68%; melhor variação 128/0,3 =
   88,18% (+0,50 ponto percentual; 46 acertos a mais).
6. **Workflow manual criado**:
   `.github/workflows/lstm_artigo.yml` permite rodar com secrets do GitHub as
   tarefas `tabela_s1`, `history` e `ablation`.

Commits desta continuação: `52eb3612` (Figura 4/S2), `667189d4` (CLI da curva
LSTM), `9ff80ce2` (ablation + workflow manual), `7ffe9af8` (correção de push
do workflow), `ca081648` (S1 real publicada pelo workflow), `07383e21`
(correção dos parâmetros do treino LSTM), `e66b4a40` (curva real do LSTM) e
`fcf39887` (ablation real do LSTM).

**Próximo passo**: gerar novo snapshot imutável do artigo, regenerar o PDF e
revisar visualmente as figuras no artefato final. Não mexer no holdout fixo de
treino/teste nem na reformatação numérica MDPI sem decisão explícita do
Adinailson.

---

## 1. Por que este documento existe

O Adinailson pediu um modelo reaproveitável: sempre que solicitar avanço no
artigo/capítulo de classificação de chamados, a sessão deve seguir esta estrutura e
deixar registrado onde parou. Este arquivo é esse modelo — parte fixa (estrutura do
artigo, mapeamento de fontes) e parte viva (bloco "Estado desta rodada" acima).

## 2. Diferença em relação ao `revisao-bibliografica`

`revisao-bibliografica` é uma **revisão de literatura** (corpus bibliográfico externo,
pipeline `00_protocolo → 01_dados_brutos → 02_triagem → 03_analise → 04_artigo →
05_bibliografia`, LaTeX compilado via CI). `classificacao-chamados` é um
**experimento empírico aplicado** (dados operacionais reais da planilha, modelos
treinados, validação humana) — não existe "corpus bibliográfico" a triar aqui, e por
isso replicar a pipeline `00_..05_` inteira não faz sentido 1:1.

O que **é** análogo e vale replicar:
- Um arquivo único descrevendo a estrutura do texto, no padrão de
  `04_artigo/estrutura_texto.md` do outro repo — feito na Seção 3 abaixo.
- Números do artigo gerados por script a partir de dados versionados/rastreáveis
  (lá é `generated_numbers.tex`; aqui já existe o equivalente natural:
  `docs/dados/*.json`, todos gerados por `src/*.py`) — **não digitar números à mão no
  texto do artigo**, sempre citar a partir do JSON vigente.
- Um handoff de continuidade por rodada (lá é `HANDOFF_ARTIGO_CODEX.md`; aqui é o
  bloco "Estado desta rodada" deste próprio arquivo, sem criar arquivo novo).
- Disponibilidade de dados/scripts documentada no próprio artigo, apontando para os
  arquivos reais do repositório (Seção 3.9 abaixo).

O que falta hoje e é a lacuna mais importante encontrada nesta auditoria: **o
rascunho do artigo não mora no repositório**. Recomendação (a confirmar com o
usuário antes de executar, é decisão dele): criar `04_artigo/` neste repo (mesmo nome
do outro, por consistência) com o texto em Markdown ou LaTeX e um script
`gerar_numeros_artigo.py` que leia `docs/dados/*.json` e produza um bloco de
constantes citável, do mesmo jeito que `generated_numbers.tex` faz lá.

## 3. Estrutura do artigo/capítulo (modelo fixo, mapeado às fontes reais)

Baseada na estrutura do artigo-modelo (`artigo_revisao_preliminar (2).pdf`, revisão
MCDM/TOPSIS) e no rascunho já iniciado (`artigo_classificacao_chamados_v3.docx`).

### Resumo estruturado
Contexto / Objetivo / Método / Resultados / Conclusão + palavras-chave. Escrever por
último, depois que 3–4 estiverem fechados com números revalidados.

### 1. Introdução
Governança preditiva da manutenção predial como problema; chamados/ordens de serviço
como matéria-prima negligenciada pela literatura (**ponte direta com o achado do
capítulo de revisão**: "uso de dados operacionais de chamados... é raro (3 estudos)"
— este capítulo empírico preenche exatamente essa lacuna identificada na revisão).

### 2. Referencial conceitual
Classificação automática de texto/NLP; modelos clássicos (TF-IDF+LogReg) vs. LSTM vs.
ensembles (RF, ExtraTrees, SGD, Naive Bayes) vs. transformer (BERTimbau); calibração
de confiança (Platt/isotônica) vs. softmax bruto; entropia de Shannon e divergência
Jensen-Shannon como camada de diagnóstico de ambiguidade; validação humana como
padrão-ouro; "rótulos ruidosos" no histórico administrativo como problema de pesquisa.

### 3. Método
| Subseção | Conteúdo | Fonte no repo |
|---|---|---|
| 3.1 | Desenho do experimento, fonte de verdade (roteiro 50 etapas) | `CONTEXTO.md`, roteiro PDF do usuário |
| 3.2 | Base de dados/planilha experimental (aba, colunas A:P, tamanho, período) | `AGENTS.md`, `README.md` |
| 3.3 | Modelos (LSTM primário, RF fallback, baseline, 7 IAs multimodelo, 8º BERTimbau) | `src/modelo_lstm.py`, `src/modelos_zoo.py`, `src/bertimbau_coreset.py` |
| 3.4 | Pipeline por turnos (Etapa 1 progressiva, Etapa 2 reclassificação) | `src/executar_etapa1.py`, `src/executar_etapa2.py`, `.github/workflows/etapa1_turnos.yml` |
| 3.5 | Métricas (concordância vs. histórico, acerto validado, calibração ECE, Kappa) | `src/calibracao.py`, `src/analise_estatistica.py` |
| 3.6 | Validação humana (colunas M/N/P, conflitos) | `src/auditar_conferencias.py` |
| 3.7 | Memória de decisão (veto/trava) | `src/decisao_validada.py`, `src/memoria_validada.py` |
| 3.8 | Camada Shannon/Jensen-Shannon | `src/analise_shannon.py`, `docs/METODOLOGIA_SHANNON.md` |
| 3.9 | Disponibilidade de dados e scripts (mover para o fim do artigo, como no modelo) | `docs/dados/*.json`, este repositório público |

### 4. Resultados
| Subseção | Conteúdo | Fonte no repo |
|---|---|---|
| 4.1 | Concordância com histórico, por modelo | `docs/dados/registros_<modelo>.json` |
| 4.2 | **Ranking validado por conferência humana** (o resultado mais importante) | `docs/dados/avaliacao_final.json` |
| 4.3 | Matriz de confusão IA × histórico na amostra conferida | `src/avaliacao_final.py` |
| 4.4 | Calibração por faixa de confiança | `docs/dados/calibracao.json` |
| 4.5 | Reclassificação e ganho líquido por modelo | `docs/dados/reclass_resumo.json` |
| 4.6 | Diagnóstico Shannon/Jensen-Shannon | `docs/dados/shannon_resumo.json`, `shannon_modelos.json`, `jensen_shannon_modelos.json` |
| 4.7 | Custo computacional | a confirmar se já medido — se não, marcar "Informação insuficiente para verificar" |
| 4.8 | Figuras | pendência conhecida: regenerar a partir dos JSONs atuais |

### 5. Discussão
Rótulos ruidosos no histórico vs. erro da IA; quando confiar na IA e quando confiar
no histórico; implicações para a governança preditiva da manutenção (**ponte
explícita com o capítulo de revisão MCDM/TOPSIS**: a revisão apontou a lacuna de
integrar dados operacionais de chamados a modelos formais de decisão — este capítulo
fornece exatamente esses dados operacionais tratados e validados, e pode alimentar
como entrada um modelo multicritério futuro).

### 6. Considerações finais
Limitações (amostra validada prioriza divergências, não é aleatória; 8º modelo
pendente; reclassificação tem resultado dependente da rodada e mistura bases de
comparação). Não afirmar validação empírica
completa enquanto a conferência humana não terminar.

### Referências
Conferir contra o acervo curado (`Referência Bibliográfica - Drive/README.md`,
mencionado na auditoria de 16/07) antes de aceitar qualquer referência do v2/v3.docx
como correta — a auditoria anterior já achou 1 erro de autoria e 1 inconsistência de
ano nesse rascunho.

### Apêndices
Dicionário de colunas da planilha (A:P); checklist de itens reportados (inspirar-se
no Apêndice D/checklist PRISMA-ScR do artigo-modelo, adaptado para relato de
experimento de ML, não de revisão bibliográfica); matriz de decisão M/N/P.

## 4. Checklist de auditoria de dados (pendência do próprio usuário)

Isto é o que o Adinailson referiu como "ainda não acabei" — não é tarefa da IA
completar, é o próprio critério de corte para poder escrever a Seção 4 com
confiança:

- [ ] Conferência humana M/N/P avançando além dos 33,9% (4.737/13.954) registrados
      em 16/07/2026 — reconferir valor atual antes de qualquer nova rodada de escrita.
- [ ] 2 conflitos antigos ficaram resolvidos (registrado como 0 pendentes em
      16/07) — reconfirmar que nenhum conflito novo apareceu com o crescimento da base.
- [ ] Decisão sobre a mudança não commitada mencionada na auditoria de 16/07 em
      `src/reclassificar_validados.py` (trava de segurança) — verificar se ainda existe
      ou já foi resolvida (o `git status` desta auditoria de 23/07 mostrou working tree
      limpo, então **parece já resolvida**; confirmar mesmo assim antes de citar).
- [ ] Resultado comparativo do 8º modelo (BERTimbau) — ainda não existe.

## 5. Ligação com a tese (capítulos)

Capítulo A — revisão integrativa (`revisao-bibliografica`): panorama MCDM/TOPSIS/
ODS/ESG na manutenção predial; achado central: dados operacionais de chamados são
raríssimos na literatura (3 estudos).

Capítulo B — este capítulo (`classificacao-chamados`): trata exatamente esses dados
operacionais de chamados, com classificação/reclassificação por IA local, validação
humana e calibração.

A tese de biossistemas construídos se fortalece ao explicitar essa ponte na
Introdução e na Discussão de ambos os capítulos: a revisão identifica a lacuna, o
capítulo empírico a preenche parcialmente e aponta o próximo elo (dados de chamados
tratados → entrada para um modelo multicritério de priorização de manutenção).

Relaciona-se com [[classificacao-chamados-ia]], [[artigo-metodologia-biossistemas]] e
[[memoria-transferencia-codex]].
