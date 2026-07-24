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

**Data**: 2026-07-23 (America/Bahia, UTC-03:00) — rodada 6, mesma data das
rodadas 0–5.

**Onde está**: todas as subseções de Resultados (3.2, 4.1–4.7), o Resumo,
o Abstract, a Discussão e as Considerações finais foram **reescritas** com
os números de 23/07/2026 — nenhuma subseção do corpo principal do artigo
mantém mais o padrão "atualização anexada". Apêndices A e B preenchidos;
Apêndice C parcial (cruzamento fino M×N×P segue "Informação insuficiente
para verificar"). 3 das 4 figuras publicadas; Figura 4 segue bloqueada, mas
agora por causa **não confirmada** (a hipótese inicial foi testada e
descartada — ver item 3). Um dos dois achados técnicos novos desta rodada
(duplicação de linhas no Random Forest) foi **investigado, confirmado e
corrigido** com dados reais da planilha, via workflow de diagnóstico
read-only de uso único (já removido do repositório após o uso).

**Correção de rota importante, herdada da rodada 5**: a rodada 4 havia
registrado a queda de acerto validado de 92–96% para 71–80% como "avanço
metodológico, não regressão" — isso estava errado. Confirmado via `git log`
que nem `avaliacao_final.py` nem `decisao_validada.py` mudaram no período; a
queda é efeito do crescimento da amostra validada (4.681 → 9.096) revelando
uma taxa de acerto real mais baixa. Corrigido na prosa do artigo (Seção 5).

**O que foi feito nesta rodada**:
1. **Diagnóstico read-only contra a planilha real**, via workflow de uso
   único (`.github/workflows/diagnostico_sessao_20260723.yml` +
   `src/diagnostico_sessao_20260723.py`, ambos removidos do repositório após
   a execução, commit `88a2ff3a` → removidos em `a244b59b`). Resultado:
   - **Mojibake em `CLASSIF__<modelo>`: hipótese testada e NÃO confirmada.**
     Amostra de 200 linhas de `CLASSIF__linear_svc` não teve nenhuma
     ocorrência de caractere corrompido. A causa da corrupção em
     `estatistica.json`/`top_confusoes`, `cruzamento_taxonomia.json` e
     `confusao_historico_ia.json` **permanece desconhecida** — pode estar
     fora da amostra testada, em outra aba, ou na etapa de
     agregação/serialização. Corrigido o texto do artigo, que antes
     apontava essas abas como suspeita principal sem tê-las testado.
   - **Duplicação em `RECLASS__random_forest`: CONFIRMADA.** 18.049 linhas
     brutas para apenas 13.312 identificadores de linha distintos (4.737
     duplicados). `RECLASS__linear_svc`, usado como referência, não teve
     nenhuma duplicata (13.451 = 13.451) — descarta erro de leitura
     genérico, localiza o problema especificamente na aba do Random Forest.
2. **Corrigido**: `src/exportar_dashboard.py::exportar_reclass_resumo` agora
   deduplica por `linha_planilha` antes de agregar (commit `a244b59b`,
   mantém a última ocorrência). Teste de regressão em
   `tests/test_exportar_reclass_resumo.py` (32/32 testes do repo passam).
   Disparado `dashboard.yml` manualmente para regenerar `reclass_resumo.json`
   — Random Forest agora em 13.312 registros, no mesmo patamar dos demais
   modelos (13.226–13.451). A causa raiz da duplicação em si (por que a aba
   acumulou linhas repetidas) não foi investigada — suspeita não confirmada
   de falha silenciosa em `linhas_ja_reclass()` — e permanece pendência.
3. **Reescrita completa de 3.2, 4.1–4.7, Resumo, Abstract, Discussão e
   Considerações finais** com os números de 23/07/2026 (base 13.965/55
   categorias; 9.534 conferências, 9.096 decisões travadas, 68,3% da base; 8
   modelos incluindo LSTM *out-of-fold* e BERTimbau; Tabela 5 com os números
   corrigidos do item 2). Corrigida também a Subseção 3.4 (Método), que
   ainda descrevia o BERTimbau como "treinamento adiado" — já tem resultado
   comparativo nesta consolidação.
4. **3 figuras geradas e publicadas** (`04_artigo/figuras/`, script
   `matplotlib`, rodada 5): Figura 1 (pipeline metodológico), Figura 2
   (confiança×desfecho), Figura 3 (trade-off acurácia×custo).
5. Dois bugs de renderização de PDF (caracteres Unicode sem suporte na fonte
   padrão do LaTeX, reintroduzidos durante a reescrita) corrigidos antes de
   cada push. PDF final sem nenhum warning de caractere ausente.
6. PDF republicado automaticamente pelo workflow a cada push. Link:
   `https://adinailson88.github.io/classificacao-chamados/artigo_classificacao_chamados.pdf`.

**Próximo passo**: (1) nova rodada de diagnóstico read-only para o mojibake,
com amostragem mais ampla (todas as linhas, não só 200) e testando outras
abas de trabalho além de `CLASSIF__linear_svc`, antes de tentar qualquer
correção; (2) investigar a causa raiz da duplicação em
`RECLASS__random_forest` (por que a aba acumulou linhas repetidas —
`linhas_ja_reclass()` é a suspeita, não confirmada); (3) gerar a Figura 4
assim que o mojibake for corrigido na fonte; (4) revisar a lista de
referências bibliográficas contra o acervo curado (pendência antiga, ainda
não tratada em nenhuma rodada); (5) preencher o Apêndice C por completo
(cruzamento fino M×N×P), quando houver rotina de extração direta da
planilha para isso.

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
