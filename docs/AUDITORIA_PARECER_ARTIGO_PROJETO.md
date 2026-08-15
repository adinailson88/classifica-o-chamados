# Auditoria das correções do parecer científico confrontado com o projeto de doutorado

> Relatório de auditoria editorial. Escopo: itens 1 a 12 do parecer científico
> recebido pelo autor, confrontados com o artigo (`04_artigo/artigo_classificacao_chamados_v3.md`)
> e com o projeto de doutorado. Não reabre decisões científicas da rodada
> canônica `1e476243`, não retreina modelo, não altera corpus, partições,
> rótulos ou resultados. O item 13 (consolidação/publicação do material
> suplementar) fica para PR separada, por instrução explícita.

**Branch:** `docs/correcoes-parecer-artigo-projeto`
**Commit-base:** `ce9211d2a3b5dcc9a802691aa82294f6b83428a1` (`origin/main` no início da rodada)
**Data:** 15/08/2026, fuso America/Bahia

**Microcorreção (mesma data):** resolvido o bloqueio do item 10 (Odum),
completada a inspeção visual às 21 páginas, e corrigidas divergências de
contagem entre este documento e `04_artigo/README.md`/`PLANO_ARTIGO_CAPITULO.md`.
Sem nova PR, sem merge — commit adicional na mesma branch, sobre o HEAD
`b5007a9c35b2b4f32007d4b2941cb92c9756209e`.

**Segunda microcorreção (mesma data, ver Seção 8):** remoção da seção
"Disponibilidade de dados e código" (promessa de disponibilização futura),
auditoria final repetida dos itens 1 a 12 diretamente sobre o texto do
artigo, confirmação do item 13 como pendência fora de escopo, recontagem
do corpo científico (8.999 → 8.972 palavras), validações completas e
regeneração/inspeção visual integral do PDF. Sem nova PR, sem merge —
commit adicional na mesma branch, sobre o HEAD
`3d86533800986ff2dc6765e8f26a59066910b1b9`, resultando no commit de texto
`9120e6d88c42ca0ef38d454a8a63a40b78db4710` e no commit automático do PDF
`601248a50827b50309ea59d0270e8acad4c2cbe6`.

## 0. Estado verificado antes de iniciar

- `git fetch origin --prune` e `gh pr list --state open`: nenhuma PR aberta.
- `docs/CODEX_PROXIMA_SESSAO.md`: não existe no repositório.
- Árvore de trabalho: limpa no início.
- Baseline: 765 testes aprovados (`python -m unittest discover -s tests`),
  `py_compile` limpo, `python src/matriz_proveniencia.py` sem divergência
  (hash `1e4762438a7e` confirmado).
- Contagem inicial do corpo científico (rotina histórica, entre
  `**1. INTRODUÇÃO**` e `**REFERÊNCIAS**`, exclusive): **8.855 palavras**,
  conforme `origin/main`, `04_artigo/README.md` e `PLANO_ARTIGO_CAPITULO.md`
  no início da rodada. Nota de reconciliação: uma recontagem independente
  desta rodada, por *split* de espaços em branco sobre o mesmo texto-fonte
  em `ce9211d2` (o commit-base), mediu 8.948 palavras — 93 a mais. Não
  existe script de contagem canônico versionado (a rotina é descrita como
  "ad hoc" desde a Rodada 7); a divergência provavelmente decorre de
  método de contagem distinto entre rodadas, e não de texto diferente.
  Mantido 8.855 como valor de referência por ser o registrado em três
  documentos independentes antes desta microcorreção.

**Achado relevante não solicitado como item, mas registrado por
transparência:** `PLANO_EXECUCAO_ATUAL.md` e `PLANO_ARTIGO_CAPITULO.md`
descreviam, no início desta rodada, um estado do artigo (título
"Classificação auditável de chamados de manutenção predial: fluxo
humano–IA, calibração e risco de reclassificação", Subseção 3.6 com
declarações institucionais completas) que **não correspondia** ao conteúdo
real de `origin/main`. Entre a Rodada 11 (registrada nos planos) e o início
desta rodada, `main` recebeu commits adicionais não documentados nos planos
— "Revisão editorial v4: título, 3.6, IFES, Tabela 5, paginação e figuras"
(`3fb2e096`), correções de referências ABNT NBR 6023:2025/NBR 10520:2023
(`ac1ce761`), correções de bloqueadores da auditoria independente da PR
#212 (`36f5a0c1`) e ajustes de paginação do Apêndice A (`06968cfa`,
`d1414b1f`) — que alteraram o título do artigo, reescreveram a Subseção 3.6
(hoje "Reprodutibilidade computacional", sem o detalhamento institucional
que os planos ainda descreviam) e adicionaram uma Tabela 5 (comparação
confirmatória do ensemble) que os planos não mencionam. Esta auditoria
trabalhou sobre o **artigo real em `origin/main`**, não sobre o estado
desatualizado descrito nos planos, conforme a instrução de não declarar
item resolvido apenas porque um documento anterior afirmava isso. A
atualização dos planos (Seção 6 abaixo) reconcilia essa divergência.

## 1. Matriz dos itens 1 a 12

| # | Apontamento do parecer | Estado antes da edição | Evidência verificada | Correção aplicada | Arquivos alterados | Estado final |
|---|---|---|---|---|---|---|
| 1 | Reconciliar 598 (corpus) e 593 (recorte do ensemble); não atribuir automaticamente os 2,92 p.p. às 593 alterações | Subseção 5.2 dizia "não se contabilizou separadamente quantas dessas alterações pertencem às 13.972 linhas avaliadas" | `docs/dados/auditoria_base_canonica.json` (`fontes.manual = 598` sobre 14.060); `docs/FASE2C_RESOLUCAO_KF_DENOMINADOR.md` (universo modelável 13.970, `Y=1` = 593); aritmética 598 − 593 = 5, consistente com o encaixe 13.970 ⊂ 13.972 ⊂ 14.060 | Subseção 5.2 reescrita: "Das 598 alterações do corpus congelado, 593 ocorrem nos 13.970 registros modeláveis do experimento de ensemble e cinco ficam fora; esse recorte não coincide com as 13.972 linhas da comparação principal (Subseção 3.4), de modo que os 2,92 pontos percentuais não são atribuídos diretamente às 593 alterações" | `04_artigo/artigo_classificacao_chamados_v3.md` | **resolvido** |
| 2 | Não substituir 6,44h por 6,29h; decompor treino/inferência/tokenização | Subseção 4.5 atribuía as 6,44h aos "2.103 passos", sem separar o componente de treino | `docs/dados/custo_bertimbau.json` (`medicao`/`projecao`: 10,774 s/passo × 2.103 passos = 22.657,722 s ≈ 6,29h; inferência 2.758/5,24 ≈ 526,34 s ≈ 0,15h; tokenização 13.972/5.005 ≈ 2,79 s; total 6,44h) | Subseção 4.5 explicita que 6,29h são só o treino e 6,44h é o total (treino + inferência + tokenização), com ressalva de extrapolação e ausência de dobra completa; `docs/CUSTO_BERTIMBAU.md` ganhou parágrafo de decomposição | `04_artigo/artigo_classificacao_chamados_v3.md`, `docs/CUSTO_BERTIMBAU.md` | **resolvido** (JSON canônico não tocado, conforme exigido) |
| 3 | Definir "neutros" e os 18,53%; distinguir precisão da fila de precisão estatística | Tabela 3 não definia "neutros"; 4,2 citava 18,53% sem fórmula | `docs/dados/comparacao_historica.json`/artigo: LinearSVC corrigidos 475, neutros 53, divergências 2.849; (475+53)/2.849 = 0,18533 | Legenda da Tabela 3 define neutros; Subseção 4.2 explicita a soma corrigidos+neutros e a fórmula (475+53)/2.849 = 18,53%, com ressalva de não confundir com precisão estatística do classificador | `04_artigo/artigo_classificacao_chamados_v3.md` | **resolvido** |
| 4 | Distinguir curva ABC global (12 categorias classe A, 81,83%) da classe ABC interna ao tipo (Tabela A2) | Subseção 4.5 dizia apenas "curva ABC"; legenda da Tabela A2 já dizia "classe da curva ABC interna ao tipo" | `docs/dados/recortes_canonicos.json` e o próprio texto da Tabela A2 | Subseção 4.5 renomeada para "curva ABC global"; texto explicita que o macro-F1 0,8207 refere-se à classe A da curva global e que a Tabela A2 usa classificação distinta (interna ao tipo) | `04_artigo/artigo_classificacao_chamados_v3.md` | **resolvido** (legenda da Tabela A2 já estava conforme; nenhuma alteração necessária nela) |
| 5 | Declarar otimismo da seleção do LinearSVC (mesmas predições OOF usadas para seleção e estimativa) | Subseção 5.3 não mencionava o ponto | Desenho do protocolo (Subseção 3.4): seleção e estimativa usam as mesmas predições *out-of-fold* | Frase curta acrescentada à Subseção 5.3, sem afirmar que o viés foi medido, remetendo à validação temporal futura | `04_artigo/artigo_classificacao_chamados_v3.md` | **resolvido** |
| 6 | Resumo/Abstract: "alvo de 0,95" em vez de "acurácia de 0,95" | Resumo/Abstract afirmavam acurácia de 0,95 atingida | Tabela 4: acurácias seletivas observadas 0,9415–0,9531, nenhuma exatamente 0,95 | Resumo: "no alvo de 0,95 de acurácia"; Abstract: "under a target accuracy of 0.95" | `04_artigo/artigo_classificacao_chamados_v3.md` | **resolvido** |
| 7 | Declarar ausência de busca de hiperparâmetros | Subseção 3.3 não mencionava o ponto | `src/modelos_zoo.py`/Tabela 1: hiperparâmetros fixos, sem `GridSearchCV`/`RandomizedSearchCV` no protocolo canônico | Frase acrescentada à Subseção 3.3: nenhum dos sete modelos passou por busca de hiperparâmetros; valores não representam o máximo desempenho alcançável | `04_artigo/artigo_classificacao_chamados_v3.md` | **resolvido** |
| 8 | `p ≤ 0,0005` em vez de `p < 0,0005` (o valor é limite superior da permutação) | Artigo, `docs/INFERENCIA_AGRUPADA.md` e `src/inferencia_agrupada.py` usavam `p <` | `docs/dados/inferencia_agrupada.json`: `p_permutacional = 0.0005`, `p_permutacional_e_limite_superior = true` | Artigo, `docs/INFERENCIA_AGRUPADA.md` e a função `renderizar_markdown` de `src/inferencia_agrupada.py` passaram a usar `p ≤`; teste unitário dedicado criado | `04_artigo/artigo_classificacao_chamados_v3.md`, `docs/INFERENCIA_AGRUPADA.md`, `src/inferencia_agrupada.py`, `tests/test_inferencia_agrupada.py` | **resolvido** (JSON canônico não tocado; permutações não recalculadas) |
| 9 | "Biossistema construído" como definição operacional do autor, não terminologia de Capra/Odum/Grimm | Introdução citava Capra/Odum/Grimm logo após a definição, sem distinguir autoria do termo | Nenhum dos três textos-fonte emprega literalmente "biossistema construído" (ver item 10) | Parágrafo da Introdução reescrito: a expressão é apresentada como definição operacional proposta neste estudo; Capra/Odum/Grimm citados como fundamentação sistêmica/ecológica; texto declara explicitamente que o artigo não mede diretamente a retroalimentação ecológica | `04_artigo/artigo_classificacao_chamados_v3.md` | **resolvido** |
| 10 | Harmonizar Capra, Odum e Grimm com o projeto de doutorado | Artigo citava Capra (1996), Odum (1971, *Environment, Power, and Society*, H. T. Odum), Grimm *et al.* (2008, *Science*) | Ver Seção 2 abaixo (verificação externa); acervo do projeto (Google Drive) confirma autoria e edição de Odum | Capra: ano corrigido para 1997 (edição harmonizada); Grimm: substituído por Grimm *et al.* (2000), *BioScience*, DOI conferido via redirecionamento para Oxford Academic; Odum: substituído por E. P. Odum, *Fundamentos de ecologia*, 6. ed., Fundação Calouste Gulbenkian, 1996, conforme exemplar e ficha de leitura do acervo do projeto | `04_artigo/artigo_classificacao_chamados_v3.md` | **resolvido, com ressalva bibliográfica** — autoria e edição de Odum confirmadas pelo exemplar; o ano de 1996 é o do projeto e do nome do arquivo do acervo, não confirmado na página de créditos (ver Seção 2) |
| 11 | Meia frase sobre Naive Bayes sem reponderação; introdução do Apêndice A explicando A1 vs A2/A3 | Subseção 4.4 não mencionava o desbalanceamento de classes do Naive Bayes; introdução do Apêndice A não distinguia a base das duas fontes de rótulo | Tabela 1: Naive Bayes é o único com "Balanceamento: nenhum"; Tabela A1 usa categoria histórica, Tabelas A2/A3 usam referência revisada | Frase acrescentada à Subseção 4.4 (sem atribuir todo o desempenho inferior a esse fator); parágrafo acrescentado à introdução do Apêndice A distinguindo A1 (histórica) de A2/A3 (referência revisada) e atribuindo diferenças à auditoria de rótulo, não a erro de transcrição | `04_artigo/artigo_classificacao_chamados_v3.md` | **resolvido** |
| 12 | Inspeção visual do PDF (não refazer correções já feitas em PRs anteriores); Ticket-BERT como preprint arXiv; conferir Li 2024 e Bouabdallaoui 2020 | Referência do Ticket-BERT já citava `arXiv:2307.00108` e DOI, mas sem a palavra "preprint"; Li e Bouabdallaoui já citados corretamente com DOI e valores (15.623/0,83; 78%) | Verificação externa: `arxiv.org/abs/2307.00108`, `doi.org/10.1016/j.autcon.2024.105501`, `doi.org/10.3390/buildings10090160`; busca por publicação revisada por pares do Ticket-BERT não encontrou evidência (apenas `CoRR abs/2307.00108`) | Referência do Ticket-BERT marcada explicitamente como `*Preprint*`, com nota de que não foi localizada publicação revisada por pares; citação no corpo (Subseção 2.1) passou a dizer "Ticket-BERT, preprint no arXiv"; Li e Bouabdallaoui conferidos e mantidos sem alteração (já corretos); inspeção visual do PDF registrada na Seção 3 abaixo | `04_artigo/artigo_classificacao_chamados_v3.md` | **resolvido** (textual); inspeção visual do PDF na Seção 3 |

## 2. Verificação externa: Capra, Odum e Grimm

Fontes primárias/secundárias consultadas (buscas na web e um `WebFetch` ao
DOI do artigo de Grimm), em 15/08/2026.

### Grimm et al. — resolvido

- O DOI fornecido pela tarefa, `https://doi.org/10.1641/0006-3568(2000)050[0571:IATLTO]2.0.CO;2`,
  redireciona para `academic.oup.com/bioscience/article/50/7/571-584/354328`,
  confirmando: **Grimm, N. B.; Grove, J. M.; Pickett, S. T. A.; Redman, C. L.
  Integrated Approaches to Long-Term Studies of Urban Ecological Systems.
  BioScience, v. 50, n. 7, p. 571–584, 2000.** (O nome do segundo autor foi
  confirmado como J. Morgan Grove — a extração automática do WebFetch
  retornou "J. Grove Grove", claramente um artefato de raspagem, corrigido
  para o nome correto antes de entrar na referência.)
- Trata diretamente de integração social-ecológica em sistemas urbanos,
  sustentando melhor a frase sobre "capacidade institucional de captar
  sinais operacionais e convertê-los em decisão" do que o artigo de 2008
  (*Global change and the ecology of cities*, Science), que é mais amplo e
  menos focado em governança.
- Referência e citação no corpo atualizadas de Grimm *et al.* (2008) para
  Grimm *et al.* (2000).

### Capra — parcial, harmonizado com ressalva

- *The Web of Life: A New Scientific Understanding of Living Systems*
  (original em inglês) teve primeira edição em capa dura pela Anchor Books
  em 1996 e edição em brochura em 1997 (confirmado por múltiplos catálogos
  de livrarias: AbeBooks, Biblio).
- A tradução brasileira, *A Teia da Vida*, Cultrix, é listada por
  vendedores como 1996 (Portal dos Livreiros, Estante Virtual) **e** como
  "1ª ed. 1997" (Travessa.com.br) — fontes secundárias divergem entre si; a
  editora Cultrix não mantém catálogo on-line com data de primeira edição
  verificável de forma inequívoca por esta auditoria.
- Diante da divergência e da indicação do projeto ("edição indicada como
  1997"), o ano da referência foi corrigido de 1996 para 1997, mantendo
  título, tradução e editora (Cultrix). Isso harmoniza com o projeto sem
  trocar a obra citada. `Informação insuficiente para verificar` de forma
  definitiva qual ano a editora Cultrix registra oficialmente como primeira
  edição; se o autor tiver o exemplar físico do projeto em mãos, a página
  de crédito editorial resolve a divergência de forma definitiva.

### Odum — resolvido, com ressalva bibliográfica sobre o ano

Bloqueio da rodada anterior levantado nesta microcorreção, a partir de
evidência direta do acervo do projeto de doutorado (Google Drive,
fornecida pelo autor):

- pasta do acervo: `https://drive.google.com/drive/u/0/folders/1QEOknZEip_x7rN27OvVecWK071relki9`;
- exemplar: `https://drive.google.com/file/d/11x0sHewIweIOnL2mk17lEypdSsm05Rs5/view`;
- ficha de leitura: `https://drive.google.com/file/d/1L9vrXCVJTMIEEGLBT_1TsZsV-gNmpDR0/view`;
- nome do arquivo no acervo: `1996_OUTRO_Ecologia_Odum_Fundamentos_Ecologia.pdf`.

O exemplar e a ficha de leitura do acervo confirmam, sem ambiguidade, que
o autor pretendido pelo projeto é **Eugene P. Odum**, autor de
*Fundamentos de Ecologia*, na **6ª edição**, e não Howard T. Odum (autor
de *Environment, Power, and Society*, citado erroneamente na versão
anterior do artigo — achado da rodada anterior, que identificou os dois
Odum como pessoas e obras distintas, mas não tinha, até então, acesso ao
acervo para decidir entre eles).

- **Autoria e edição:** confirmadas diretamente pelo exemplar do acervo
  (Eugene P. Odum, 6. ed.) — não são mais uma inferência bibliográfica
  externa, mas leitura direta da fonte primária do projeto.
- **Ano (1996):** consta do projeto e do nome do arquivo do acervo
  (`1996_OUTRO_...`), mas **não foi confirmado na página de créditos do
  exemplar** — a página de créditos não foi localizada nesta auditoria, ou
  não trazia o ano de publicação de forma legível. O ano de 1996 é,
  portanto, harmonizado com o projeto e com a identificação do arquivo,
  não uma confirmação editorial independente. `Informação insuficiente
  para verificar o ano diretamente na página de créditos do exemplar.`
- **Decisão:** a referência do artigo foi substituída para
  `ODUM, E. P. Fundamentos de ecologia. 6. ed. Lisboa: Fundação Calouste
  Gulbenkian, 1996.`, e a citação no corpo passou a "Odum (1996)". A
  publicadora (Fundação Calouste Gulbenkian, Lisboa) segue as edições
  1ª (1973), 2ª (1976) e 7ª (2004) já confirmadas por esta auditoria em
  fonte secundária (livrarias/catálogos); a 6ª edição citada pelo exemplar
  do acervo situa-se cronologicamente entre a 2ª (1976) e a 7ª (2004), o
  que é compatível com 1996. Item registrado como **resolvido, com
  ressalva bibliográfica sobre a confirmação do ano na página de
  créditos** — a ressalva não é mais um bloqueio de autoria, apenas uma
  pendência de verificação editorial de detalhe.

## 3. Inspeção visual do PDF

PDF regenerado três vezes pelo workflow oficial (`artigo_pdf.yml`,
`workflow_dispatch`) na própria branch, runs `31900772924`, `31901095700`
(rodada original) e `31902939975` (microcorreção do item 10). **21
páginas**, dentro da faixa 21–23, preservadas nas três renderizações.
Renderização real via PyMuPDF a 150–400 dpi (não apenas o LaTeX
intermediário).

**Achado na primeira renderização (`31900772924`), corrigido antes da
segunda:** o caractere Unicode cru `≤` inserido no item 8 foi
silenciosamente descartado pelo pandoc/xelatex ao converter para PDF,
deixando "com *p* 0,0005" sem o operador na página 8. Substituído por
`$\leq$` em LaTeX — mesmo padrão já usado para $\rho$ e $\lambda$ em
rodada anterior. Confirmado corrigido na segunda renderização
(`31901095700`) e preservado na terceira (`31902939975`).

**Inspeção completa: 21 das 21 páginas**, individualmente, na
renderização da microcorreção (`31902939975`). As páginas 3 e 4 — não
registradas individualmente na rodada anterior — foram inspecionadas
nesta microcorreção: página 3 traz o fim da Subseção 2.1 (Ticket-BERT
como preprint), as Subseções 2.2 a 2.4 e o início da Seção 3
(Subseção 3.1), toda em texto corrido sem tabela ou figura, sem
sobreposição ou corte; página 4 traz a Figura 1 (*pipeline* de
governança preditiva) íntegra e bem posicionada, seguida do restante da
Subseção 3.1 e das Subseções 3.2–3.3, sem anomalia. A página 2 confirma
"na concepção de ecossistema de Odum (1996)" renderizado corretamente,
sem quebra; a página 18 confirma a entrada `ODUM, E. P. Fundamentos de
ecologia. 6. ed. Lisboa: Fundação Calouste Gulbenkian, 1996.` na posição
alfabética correta, sem corte.

Demais páginas conferidas: página 1 (autores e e-mails corretos), página
5 (Tabela 1 íntegra, com a frase de ausência de busca de
hiperparâmetros), página 6 (Subseções 3.4 início e 3.5), página 7
(Subseção 3.6, início da Seção 4 e Subseção 4.1), página 8 (Tabela 2,
Figura 2 e o teste global com `p ≤ 0,0005`), página 9 (Tabela 3 com a
legenda de "Neutros" e a fórmula 18,53%, início da Subseção 4.3), página
10 (Tabela 4, sem vão antes dela, Figura 3), página 11 (Figura 4 e a
frase sobre o Naive Bayes sem reponderação), página 12 (Figura 5), página
13 (Figura 6, Tabela 5 e a distinção ABC global/interna ao tipo), página
14 (Subseção 5.2 com a reconciliação 598/593), página 15 (Subseção 5.3
com o otimismo da seleção do LinearSVC, sem título órfão), página 16
(Considerações Finais e início das Referências, sem título órfão), página
17 (Capra 1997 e Grimm *et al.* 2000 com DOI completo, ambos na posição
alfabética correta), página 19 (fim das referências, Ticket-BERT já
conferido na página 18, Li e Bouabdallaoui inalterados e corretos), página
20 (ordem título → introdução → Tabela A1, com o parágrafo distinguindo
A1 de A2/A3), página 21 (Tabela A2 com "classe da curva ABC interna ao
tipo" e Tabela A3, ambas com nota de fonte visível). Nenhuma
sobreposição, corte, título órfão, caractere matemático ausente ou
tabela fora de ordem encontrada em nenhuma das 21 páginas. Nenhuma
correção visual das PRs #211–#214 foi refeita nesta rodada.

## 4. Controle de extensão

- Contagem inicial (antes das correções, `origin/main`): **8.855 palavras**
  (ver nota de reconciliação na Seção 0).
- Após aplicar os itens 1–12: pico de **9.313 palavras**, acima do teto de
  9.000.
- Cortes compensatórios locais aplicados exclusivamente nas subseções
  tocadas pelas correções (Introdução, 3.3, 4.2, 4.4, 4.5, 5.2, 5.3,
  introdução do Apêndice A), eliminando redundância de prosa sem remover
  dado, ressalva, citação ou conclusão.
- Contagem após a rodada original: **8.999 palavras**.
- Microcorreção do item 10 (Odum): parágrafo da Introdução e referência
  reescritos, com corte local mínimo no mesmo parágrafo para permanecer
  dentro da faixa. Contagem final: **8.999 palavras**, dentro da
  faixa-meta 8.850–9.000.

## 5. Arquivos alterados nesta rodada

```text
04_artigo/artigo_classificacao_chamados_v3.md
docs/CUSTO_BERTIMBAU.md
src/inferencia_agrupada.py
tests/test_inferencia_agrupada.py
docs/INFERENCIA_AGRUPADA.md
docs/AUDITORIA_PARECER_ARTIGO_PROJETO.md (este arquivo)
PLANO_ARTIGO_CAPITULO.md
PLANO_EXECUCAO_ATUAL.md
04_artigo/README.md
```

Não alterados: `docs/dados/*.json`, `docs/dados/ensemble/**`,
`04_artigo/figuras/tabela_S*.csv`, `src/tabelas_suplementares_canonicas.py`,
a planilha viva, o repositório `malha-ia`, qualquer resultado, corpus,
partição ou hash canônico.

## 6. Reconciliação dos documentos de plano

`PLANO_EXECUCAO_ATUAL.md` e `PLANO_ARTIGO_CAPITULO.md` foram atualizados
nesta rodada para refletir o estado real de `origin/main` no início da
rodada (título vigente, Subseção 3.6 atual, Tabela 5, referências ABNT
atualizadas) antes de registrar as correções desta PR, corrigindo a
divergência descrita na Seção 0.

## 7. Declaração de execução

Zero retreinamentos. Zero fits de modelos-base. Zero fits de stacking.
Zero execuções de LSTM ou BERTimbau. Zero alterações em planilha, corpus,
partições ou resultados canônicos. Nenhuma escrita foi realizada na
planilha viva.

## 8. Segunda microcorreção (15/08/2026): remoção da promessa de disponibilização futura

**Branch:** `docs/correcoes-parecer-artigo-projeto` (mesma), sem nova PR.
**Commit-base:** HEAD ao final da microcorreção do item 10 (Odum),
`3d86533800986ff2dc6765e8f26a59066910b1b9`.

### 8.1 Remoção do texto

O bloco a seguir, localizado entre as Considerações Finais e a lista de
Referências, foi excluído integralmente do artigo, sem substituição por
outra declaração defensiva:

> **DISPONIBILIDADE DE DADOS E CÓDIGO**
>
> Os dados e o código necessários à reprodução das análises, tabelas e
> figuras serão disponibilizados em repositório público permanente
> associado ao artigo.

O trecho prometia uma ação administrativa futura sem conteúdo científico
correspondente, contrária à diretriz editorial de texto afirmativo,
direto e proporcional às evidências. A transição do artigo passa a ir
diretamente das Considerações Finais para as Referências.

### 8.2 Busca por promessas equivalentes

```bash
rg -n -i "será disponibiliz|serão disponibiliz|disponibilidade de dados|repositório público permanente|dados e código" 04_artigo/artigo_classificacao_chamados_v3.md
```

Nenhuma outra ocorrência encontrada no artigo após a remoção. Buscas
complementares por variações ("será/serão publicado(s)", "ficará/estará
disponível", "em versão/trabalho futuro") também não retornaram
ocorrência. Nos documentos de acompanhamento (`04_artigo/README.md`,
`PLANO_ARTIGO_CAPITULO.md`, `PLANO_EXECUCAO_ATUAL.md`, este arquivo), a
única ocorrência remanescente da frase é uma menção histórica em
`04_artigo/README.md` (linha da Rodada 12), que descreve a criação da
seção "Disponibilidade de dados e código" naquela rodada como fato já
ocorrido — registro histórico correto, não uma descrição do estado
vigente do artigo, portanto não alterada.

### 8.3 Auditoria final dos itens 1 a 12

Repetida diretamente sobre o texto do artigo (`grep`/leitura de trecho),
não apenas sobre o estado declarado na matriz da Seção 1. Todos os 12
itens permanecem presentes e coerentes com a correção registrada:

| # | Verificação repetida | Localização confirmada no artigo |
|---|---|---|
| 1 | "Das 598 alterações... 593... cinco ficam fora... não coincide com as 13.972... não são atribuídos diretamente às 593 alterações" | Subseção 5.2 |
| 2 | "6,29 horas só de treino"; "6,44 horas por dobra e 32,2 horas para as cinco" | Subseção 4.5 |
| 3 | Legenda "Neutros" na Tabela 3; fórmula "(475 + 53) / 2.849 = 18,53%" | Subseção 4.2 |
| 4 | "curva ABC global"; legenda "classe da curva ABC interna ao tipo" na Tabela A2 | Subseção 4.5 e Tabela A2 |
| 5 | Frase sobre uso das mesmas predições *out-of-fold* para seleção e estimativa | Subseção 5.3 |
| 6 | "alvo de 0,95 de acurácia" (Resumo); "a target accuracy of 0.95" (Abstract) | Resumo e Abstract |
| 7 | "busca de hiperparâmetros: a comparação avalia as configurações da Tabela..." | Subseção 3.3 |
| 8 | "*p* $\leq$ 0,0005" (LaTeX, renderiza como ≤) | Subseção 4.1 |
| 9 | "biossistema construído — definição operacional aqui..." | Introdução |
| 10 | CAPRA (1997); GRIMM *et al.* (2000); ODUM, E. P. (1996) nas Referências | Lista de Referências |
| 11 | "Naive Bayes é o único modelo sem reponderação de classes"; parágrafo A1/A2-A3 | Subseção 4.4 e introdução do Apêndice A |
| 12 | "Ticket-BERT, preprint no arXiv"; entrada com `*Preprint*` nas Referências | Subseção 2.1 e Referências |

Nenhum item ausente, contraditório ou apenas parcialmente implementado.
Nenhuma decisão científica reaberta; nenhum resultado numérico alterado.

### 8.4 Item 13

Confirmado como pendência fora do escopo desta PR, para PR separada, nos
três documentos de acompanhamento (`docs/AUDITORIA_PARECER_ARTIGO_PROJETO.md`
Seção 0, `PLANO_ARTIGO_CAPITULO.md`, `PLANO_EXECUCAO_ATUAL.md`). Não
implementado nesta rodada.

### 8.5 Controle de extensão

Rotina de contagem: divisão por espaços em branco (`str.split()`) do
texto-fonte Markdown entre `**1. INTRODUÇÃO**` e `**REFERÊNCIAS**`,
exclusive — a mesma rotina histórica usada nas rodadas anteriores.

- Contagem antes da remoção (estado ao final da microcorreção do item 10):
  **8.999 palavras**.
- Contagem após a remoção da seção "Disponibilidade de dados e código":
  **8.972 palavras**.
- Diferença: −27 palavras, correspondente exatamente ao texto removido;
  nenhum texto foi acrescentado para compensar a remoção ou para retornar
  a um valor específico.
- Permanece dentro da faixa-meta de 8.850 a 9.000 palavras.

### 8.6 Validações executadas

- `python -m unittest discover -s tests`: **767 testes aprovados**, 0 falhas.
- `python -m py_compile src/*.py tests/*.py`: limpo, sem erro.
- `python src/matriz_proveniencia.py`: 0 artefatos com hash divergente, 0
  artefatos do congelamento ausentes, 0 números legados no artigo; hash
  canônico completo `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`
  preservado em `docs/MATRIZ_PROVENIENCIA.md` e em `docs/dados/rodada_canonica.json`.
- Commit único `9120e6d88c42ca0ef38d454a8a63a40b78db4710`, mensagem
  "docs: remove promessa futura e conclui auditoria do parecer", incluindo
  a atualização de `docs/dados/matriz_proveniencia.json` (único campo
  alterado: `gerado_em`). Push para `origin/docs/correcoes-parecer-artigo-projeto`.
- Workflow oficial `artigo_pdf.yml` disparado via `gh workflow run` na
  própria branch (run `31903959626`), concluído com sucesso em 40s.
  Commit automático do PDF: `601248a50827b50309ea59d0270e8acad4c2cbe6`
  ("pdf do artigo gerado automaticamente [skip ci]").
- PDF renderizado via PyMuPDF a 170 dpi: **21 páginas**, dentro da faixa
  21–23, preservadas em relação à rodada anterior.
- Inspeção visual: **21 das 21 páginas**, individualmente. Confirmados
  sem alteração indevida: título, autores, Resumo/Abstract (página 1);
  Introdução com "biossistema construído" e Capra/Odum/Grimm (página 2);
  Figura 1 e revisão humana (página 4); Tabela 1 com ausência de busca de
  hiperparâmetros (página 5); `p ≤ 0,0005` renderizado corretamente
  (página 6, Subseção 3.4); Tabela 2 e Figura 2 (páginas 7–8); Tabela 3
  com legenda "Neutros" e fórmula 18,53% (página 9); Tabela 4 e Figura 3
  (página 10); Naive Bayes sem reponderação (página 11); Figura 5 e
  duplicação taxonômica (página 12); Figura 6, Tabela 5 e curva ABC global
  (página 13); reconciliação 598/593 (página 14, Subseção 5.2); otimismo
  da seleção do LinearSVC (página 15, Subseção 5.3); **transição de
  "6. CONSIDERAÇÕES FINAIS" diretamente para "REFERÊNCIAS", sem a seção
  removida e sem título órfão** (página 16); Capra (1997) e Grimm *et al.*
  (2000) na posição alfabética correta (página 17); Odum (1996) e
  Ticket-BERT como `*Preprint*` (página 18); fim das referências (página
  19); início do Apêndice A com Tabela A1 e parágrafo distinguindo A1 de
  A2/A3 (página 20); Tabelas A2 e A3 com "classe da curva ABC interna ao
  tipo" (página 21). Nenhuma sobreposição, corte, página vazia ou
  problema de ordem encontrado em nenhuma página.
- Contagem de referências recontada programaticamente (blocos separados
  por linha em branco entre `**REFERÊNCIAS**` e `APÊNDICE A`, descontados
  dois artefatos de LaTeX bruto — `\FloatBarrier`/`\clearpage`, não
  entradas bibliográficas): **44 referências**, inalterado.

### 8.7 Arquivos alterados nesta microcorreção

```text
04_artigo/artigo_classificacao_chamados_v3.md
04_artigo/README.md
PLANO_ARTIGO_CAPITULO.md
PLANO_EXECUCAO_ATUAL.md
docs/AUDITORIA_PARECER_ARTIGO_PROJETO.md (este arquivo)
```

Não alterados: `docs/dados/*.json`, `docs/dados/ensemble/**`, planilha
viva, repositório `malha-ia`, qualquer resultado, corpus, partição ou
hash canônico.
