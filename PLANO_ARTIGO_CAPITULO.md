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

**Data**: 2026-07-23 (America/Bahia, UTC-03:00) — rodada 3, mesma data das
rodadas 0–2.

**Onde está**: `04_artigo/artigo_classificacao_chamados_v3.md` tem a estrutura
alinhada ao plano (rodada 2) e agora também uma primeira tabela com dados
**revalidados e corrigidos** (Tabela 3, calibração por faixa, Subseção 4.4).
Publicação em PDF no GitHub Pages está no ar. Apêndice B preenchido. Restam
pendentes: Tabelas 4–7 (matriz de confusão, reclassificação, Shannon/JS, custo)
e Apêndice C.

**O que foi feito nesta rodada**:
1. **Bug de dados corrigido**: ao tentar revalidar números para tabelar,
   `docs/dados/calibracao.json` mostrava `acerto_validado = 1,0` em TODAS as
   faixas de confiança (implausível). Causa: `src/calibracao.py` media acerto
   comparando só contra a marcação bruta da coluna N (CONFERÊNCIA IA) isolada,
   que na prática quase nunca é marcada "Errado" (o erro da IA costuma ficar
   registrado só via M) — viés de seleção. Corrigido no commit `21258deb`
   (comparar contra a categoria DECIDIDA pela memória M/N/P, mesma verdade de
   `avaliacao_final.py`); teste de regressão adicionado em
   `tests/test_calibracao.py` (29/29 testes passam). Não foi possível
   reexecutar contra a planilha real localmente (sem credenciais) — disparado
   manualmente o workflow `dashboard.yml` (run
   `30056361490`, concluído com sucesso), que regenerou
   `docs/dados/calibracao.json` já corrigido. Números pós-correção são
   plausíveis: acerto validado por faixa cresce de 49,89% (<50% confiança) a
   96,79% (≥95% confiança), sobre 9.096 decisões travadas.
   **Achado colateral ainda em aberto**: `validacao_humana.matriz_ia_x_glpi`
   dentro do mesmo JSON tem o MESMO viés estrutural (ainda compara marcação
   bruta de M e N) e continua com variância zero — não corrigido nesta rodada;
   não usar esse campo para a Tabela 4.3 (matriz de confusão IA×GLPI) até nova
   correção. Detalhe completo em `docs/PLANO_PDF_ARTIGO_PAGES.md`.
2. **Tabela 3 acrescentada** à Subseção 4.4 do artigo, com os números
   corrigidos de hoje (fonte: `calibracao.json`, gerado 23/07/2026 21:31),
   sem apagar o parágrafo de prosa com os números de 16/07/2026 — inserida
   como "Atualização de dados (23/07/2026)" logo abaixo, para preservar
   rastreabilidade. Prosa antiga ainda não foi reescrita/substituída (fica
   para quando o restante da Seção 4 for revalidado, para não deixar o texto
   com números de datas misturadas sem aviso).
3. **Nota metodológica acrescentada à Subseção 4.3** avisando que a matriz de
   confusão IA×GLPI de 16/07/2026 (4.454/45/186/13) não pôde ser reconfirmada
   nesta rodada pelo motivo do item 1.
4. **Apêndice B preenchido**: checklist de itens reportados (adaptado do
   espírito PRISMA-ScR) mapeando cada item à subseção e ao status de
   reconferência — commit `0e8dda56`.
5. **Publicação em PDF no GitHub Pages**: novo workflow
   `.github/workflows/artigo_pdf.yml` (pandoc + xelatex via imagem Docker
   `pandoc/extra`) converte `04_artigo/artigo_classificacao_chamados_v3.md`
   para `docs/artigo_classificacao_chamados.pdf` a cada push que altere esse
   `.md`, ou por disparo manual; `docs/index.html` agora linka o PDF no
   cabeçalho do painel. Testado localmente (xelatex via MiKTeX) antes de
   commitar — renderiza corretamente (acentuação, tabelas, sumário). Registro
   completo do desenho e das limitações em `docs/PLANO_PDF_ARTIGO_PAGES.md` —
   em particular: o PDF acompanha o `.md` automaticamente, mas **não reescreve
   números sozinho** quando só os JSONs de `docs/dados/` mudam; isso continua
   exigindo edição manual do `.md` após revalidação.
6. `README.md` (bloco "prompt pronto") e este arquivo atualizados para refletir
   tudo isso.

**Próximo passo**: (1) construir as Tabelas 4–7 restantes (reclassificação —
`reclass_resumo.json`; Shannon/JS — `shannon_modelos.json` e
`jensen_shannon_modelos.json`; custo computacional — verificar se há JSON
dedicado ou declarar "Informação insuficiente para verificar") com os dados
vivos de hoje, seguindo o mesmo padrão desta rodada (tabela nova + nota de
atualização, sem apagar a prosa antiga sem revisão); (2) decidir se e quando
reescrever a prosa de toda a Seção 4/Resumo para os números de 23/07/2026 —
a base de conferência humana cresceu muito desde 16/07 (4.737 → 9.534
conferências) e o ranking de `avaliacao_final.json` mudou de faixa (92–96% →
71–80% de acerto validado, porque agora compara CADA modelo contra a verdade
decidida, não só o executor oficial contra sua própria conferência — é
avanço metodológico, não regressão, mas precisa de parágrafo explicando a
mudança de metodologia para o leitor não estranhar a queda aparente); (3)
aplicar correção equivalente à de `calibracao.py` no campo
`matriz_ia_x_glpi` antes de reconstruir a Tabela 4.3; (4) preencher o
Apêndice C (matriz M/N/P) quando houver extração direta da planilha.

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
| 3.2 | Base de dados/planilha experimental (aba, colunas A:M, tamanho, período) | `AGENTS.md`, `README.md` |
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
pendente; reclassificação só ganha em 3 dos modelos). Não afirmar validação empírica
completa enquanto a conferência humana não terminar.

### Referências
Conferir contra o acervo curado (`Referência Bibliográfica - Drive/README.md`,
mencionado na auditoria de 16/07) antes de aceitar qualquer referência do v2/v3.docx
como correta — a auditoria anterior já achou 1 erro de autoria e 1 inconsistência de
ano nesse rascunho.

### Apêndices
Dicionário de colunas da planilha (A:M); checklist de itens reportados (inspirar-se
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
