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

**Data**: 2026-07-24 (America/Bahia, UTC-03:00) — rodada 8 em execução.

**Onde está**: correção técnica e rastreabilidade do texto concluídas antes da
regeneração final do PDF. O artigo e o painel distinguem o BERTimbau pendente
dos sete modelos comparáveis; os JSONs de avaliação final e estatística ainda
precisam ser republicados por execução real da planilha.

**O que foi feito nesta rodada**: além do registro histórico a seguir, foram
aplicadas correções locais ainda não commitadas: (1) Tabela 5 atualizada do
`reclass_resumo.json` de 24/07; (2) causa raiz do retry não idempotente do
Random Forest atualizada para o commit `098c477e`; (3) BERTimbau removido das
alegações comparativas no artigo, com `transformer_ft` excluído também de
`src/analise_shannon.py` e dos diagnósticos Shannon regenerados; (4) método
corrigido para `KFold` embaralhado e confiança do LinearSVC descrita sem Platt;
(5) painel marcado como amostra humana parcial e não aleatória, com
`transformer_ft` ocultado enquanto `bertimbau_training_state.json` não for
`ok`; (6) `avaliacao_final.py` e `analise_estatistica.py` passam a excluir esse
modelo em novas publicações; (7) criado `src/gerar_manifesto_snapshot_artigo.py`
e executado o snapshot `docs/dados/snapshots/artigo-v3-20260724/`, com manifesto,
hashes SHA-256, scripts de origem e observação de validação. O histórico da rodada
7 permanece abaixo. Nesta continuação, a planilha experimental foi lida diretamente
por conector, sem alterações: `CHAMADOS_ESQUELETO_REDUZIDO` tem 13.965 linhas
processadas; `MEMORIA_VALIDADA_CLASSIFICACAO` e `CALIBRACAO_VALIDADA` confirmam
9.096 decisões/observações de validação. A leitura também confirmou defasagem de
metadados: `EXPERIMENTO_CONFIG` registra execução de 16--17/07, enquanto
`MULTIMODELO_METRICAS` está em 24/07. Foram corrigidos o dicionário A:P e o
checklist de particionamento no artigo, e `avaliacao_final.py` e
`analise_estatistica.py` passam a emitir metadados mínimos nas próximas execuções.
1. **Duplicação em `RECLASS__random_forest` — causa raiz corrigida e
   commitada** (commit `098c477e`, já em `origin/main`). Investigação
   read-only nos logs do GitHub Actions (`gh run view --log`) achou, em
   2026-07-18, um append de 4.737 linhas em `RECLASS__random_forest` que
   sofreu erro transitório de API e foi reenviado com sucesso no retry — o
   número bate exatamente com os 4.737 duplicados confirmados na rodada 6.
   Causa: `_append_resiliente()` em `src/reclassificacao_multimodelo.py`
   fazia retry não-idempotente (reenviava o lote inteiro mesmo quando a
   escrita já tinha sido commitada no servidor antes do erro chegar ao
   cliente). Corrigido: a função agora conta as linhas da aba-alvo antes de
   cada retry e cancela o reenvio se a aba já cresceu o suficiente para ter
   absorvido a tentativa anterior. Teste de regressão novo em
   `tests/test_append_resiliente.py` (2 casos). Suíte completa: 34/34
   passando. **Não testado em produção** (só com fakes offline) — a
   correção só será validada de fato no próximo disparo real do workflow
   `multimodelo_reclassificacao.yml`.
2. **Referências bibliográficas — revisão parcial contra o acervo curado**.
   O "acervo curado" citado nas rodadas anteriores não é uma pasta do
   Google Drive (não localizada com esse nome) — é o arquivo local
   `C:\Users\adina\OneDrive\Área de Trabalho\ARQUIVOS - CLAUDE\REFERENCIAS\Referencias Bibliográficas - Tese\Mapa_Referencias_Tese.md`
   (78 referências curadas, escopo = temas amplos da tese: manutenção
   predial, governança preditiva, biossistemas, ESG/ODS, MCDM). Desse
   acervo, **só 2 das 22 referências do artigo têm entrada correspondente**:
   `Martins_2024` e `Morais_2023` (as outras 20 são papers técnicos
   internacionais de NLP/ML/estatística, fora do escopo temático do
   acervo). Por decisão do Adinailson, revisadas só essas 2 nesta rodada.
   Resultado: **nenhum erro de autoria ou inconsistência de ano** nas duas
   (autoria, ano, volume e número batem exatamente com o acervo) — o "1
   erro de autoria e 1 inconsistência de ano" da auditoria de 16/07 **não**
   está nelas; ou já foi corrigido entre v2 e v3, ou está numa das outras
   20 (não verificadas). Achadas e corrigidas 2 lacunas de completude (ABNT
   NBR 6023 exige): faltava o intervalo de páginas em Martins (`p.
   79--98`) e o DOI em Morais (`10.18830/issn.1679-0944.n34.2023.08`) —
   ambos adicionados em `04_artigo/artigo_classificacao_chamados_v3.md`
   (confirmado como a fonte real usada pelo workflow `artigo_pdf.yml` que
   gera o PDF publicado, via `grep` no `.yml`). **Ainda não commitado nem
   enviado.**

**Próximo passo**: executar `avaliacao_final.py` e `analise_estatistica.py`
contra a planilha com credenciais no workflow, para publicar JSONs sem
`transformer_ft`; gerar um novo snapshot com esses artefatos, validar o painel
e só então regenerar o PDF e repetir a auditoria número a número.

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
