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

**Data**: 2026-07-23 (America/Bahia, UTC-03:00) — rodada 5, mesma data das
rodadas 0–4.

**Onde está**: a prosa principal do Resumo/Abstract e das Subseções 3.2,
4.1–4.4 foi **reescrita** com os números de 23/07/2026 (não mais um parágrafo
"Atualização de dados" separado — o número vigente já está no corpo do
texto). Seção 5 (Discussão) e Seção 6 (Considerações finais) também
reescritas para refletir o achado central desta rodada: o patamar de acerto
validado caiu de ~92–96% para ~71–80% porque a amostra de conferência quase
dobrou (4.681 → 9.096), não por mudança de código. Subseções 4.5–4.7 mantêm
o padrão anterior (prosa de 16/07 preservada + parágrafo "Atualização de
dados" com a Tabela 5/6/7) — não foram reintegradas nesta rodada por serem
subseções secundárias/exploratórias, não headline. Figuras 1–3 geradas e
publicadas (Subseção 4.8); Figura 4 permanece bloqueada por um novo achado
técnico (ver item 3 abaixo).

**Correção de rota importante desta rodada**: a rodada 4 registrou a queda de
92–96% para 71–80% como "avanço metodológico, não regressão" — **isso estava
errado**. Conferido via `git log --since=2026-07-16` que nem
`src/avaliacao_final.py` nem `src/decisao_validada.py` foram alterados nesse
intervalo; a queda é inteiramente efeito do crescimento da amostra validada
revelando uma taxa de acerto real mais baixa e mais representativa. Corrigido
na prosa do artigo (Seção 5) e aqui.

**O que foi feito nesta rodada**:
1. **Reescrita de 3.2, 4.1, 4.2, 4.3, 4.4** com números de 23/07/2026 (base
   13.965/55 categorias; 9.534 conferências, 9.096 decisões travadas, 68,3%
   da base; Tabela 1 e 2 agora com 8 modelos, incluindo LSTM *out-of-fold* e
   BERTimbau, que já tem resultado comparativo). Removidos os parágrafos
   "Atualização de dados" dessas quatro subseções — o número vigente é agora
   a própria prosa, não um adendo.
2. **Resumo/Abstract reescritos** com os mesmos números (LinearSVC 80,34%
   concordância / 79,89% acerto validado; LSTM 68,47% / 74,71%; BERTimbau já
   citado como modelo com resultado, não mais "extensão planejada").
3. **Novo achado técnico, não corrigido**: ao preparar a Figura 4 (pares de
   maior confusão), descoberta corrupção de acentuação (mojibake) nos nomes
   de categoria de `estatistica.json` (campo `top_confusoes`),
   `cruzamento_taxonomia.json` e `confusao_historico_ia.json`. Rastreamento
   parcial: `src/analise_estatistica.py` lê os nomes de categoria das abas
   `CLASSIF__<modelo>` (não da aba principal nem de `registros.json`, que
   estão limpos) — suspeita recai sobre essas abas de trabalho ou sobre como
   esse script as lê. **Não corrigido, não confirmado por leitura direta da
   planilha.** Figura 4 fica pendente por esse motivo, registrado no artigo
   (Subseção 4.8) e aqui.
4. **Investigação da discrepância do Random Forest (Tabela 5)**: rastreada até
   `src/exportar_dashboard.py::exportar_reclass_resumo`, que conta
   `total_reclassificado = len(rows)` — uma contagem simples de linhas da aba
   `RECLASS__random_forest`. O total (18.049) excede o tamanho da base
   (13.965), o que é matematicamente impossível sob a premissa de 1 linha por
   chamado — indica linhas duplicadas acumuladas nessa aba especificamente.
   Hipótese não confirmada: `linhas_ja_reclass()` (mecanismo de dedup por
   linha) pode estar falhando silenciosamente para esse modelo (a função tem
   um `except: return set()` que, se disparado, faria o script reprocessar e
   reanexar linhas já feitas). **Não corrigido** — requer inspeção da
   planilha real (contagem de valores duplicados na coluna C da aba) antes de
   qualquer tentativa de correção de código, para não arriscar piorar dados
   de produção sem entender a causa.
5. **3 figuras geradas e publicadas** (`04_artigo/figuras/`, script
   `matplotlib`): Figura 1 (pipeline metodológico, agora como diagrama real,
   não mais placeholder), Figura 2 (confiança×desfecho, dados da Tabela 3),
   Figura 3 (trade-off acurácia×custo). Embutidas no `.md` com caminho
   relativo à raiz do repo (`04_artigo/figuras/...`), necessário porque o
   `pandoc` do workflow roda a partir da raiz.
6. **Dois novos bugs de renderização de PDF corrigidos** durante a escrita:
   caracteres `≈`, `≥`, `⁻`, `⁶` (usados na notação científica `p ≈
   1,99×10⁻⁶` e em `≥95%`) reintroduzidos durante a reescrita — mesma causa
   do bug corrigido na rodada 4 (fonte padrão do LaTeX não cobre esses
   glifos). Substituídos por notação ASCII (`~`, `>=`, `0,000002`). PDF
   final gera sem nenhum warning de caractere ausente.
7. PDF republicado automaticamente pelo workflow a cada push. Link:
   `https://adinailson88.github.io/classificacao-chamados/artigo_classificacao_chamados.pdf`.

**Próximo passo**: (1) investigar com acesso à planilha real as duas
pendências técnicas encontradas nesta rodada (mojibake nas abas
`CLASSIF__<modelo>`; duplicação de linhas em `RECLASS__random_forest`) —
ambas fora do escopo do que pode ser corrigido sem leitura/escrita direta na
planilha; (2) decidir se reintegra 4.5–4.7 no mesmo padrão de reescrita total
usado em 4.1–4.4, ou se mantém o padrão "atualização anexada" para essas
subseções secundárias; (3) gerar a Figura 4 assim que o mojibake for
corrigido na fonte; (4) revisar a lista de referências bibliográficas contra
o acervo curado (pendência antiga, ainda não tratada nesta rodada nem nas
anteriores).

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
