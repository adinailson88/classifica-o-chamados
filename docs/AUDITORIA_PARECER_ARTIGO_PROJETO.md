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

## 0. Estado verificado antes de iniciar

- `git fetch origin --prune` e `gh pr list --state open`: nenhuma PR aberta.
- `docs/CODEX_PROXIMA_SESSAO.md`: não existe no repositório.
- Árvore de trabalho: limpa no início.
- Baseline: 765 testes aprovados (`python -m unittest discover -s tests`),
  `py_compile` limpo, `python src/matriz_proveniencia.py` sem divergência
  (hash `1e4762438a7e` confirmado).
- Contagem inicial do corpo científico (rotina histórica, entre
  `**1. INTRODUÇÃO**` e `**REFERÊNCIAS**`, exclusive): **8.948 palavras**.

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
| 10 | Harmonizar Capra, Odum e Grimm com o projeto de doutorado | Artigo citava Capra (1996), Odum (1971, *Environment, Power, and Society*), Grimm *et al.* (2008, *Science*) | Ver Seção 2 abaixo (verificação externa) | Capra: ano corrigido para 1997 (edição harmonizada); Grimm: substituído por Grimm *et al.* (2000), *BioScience*, DOI conferido via redirecionamento para Oxford Academic; Odum: **não alterado** | `04_artigo/artigo_classificacao_chamados_v3.md` | **parcial** — Capra e Grimm resolvidos; Odum bloqueado (ver Seção 2) |
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

### Odum — bloqueado, não alterado

- **Achado crítico:** *Fundamentos de Ecologia* (a obra indicada pelo
  projeto) é de autoria de **Eugene P. Odum** (com Gary W. Barrett nas
  edições mais recentes), tradução portuguesa publicada pela Fundação
  Calouste Gulbenkian (edições confirmadas: 1ª ed. 1973, 2ª ed. 1976, 7ª
  ed. 2004) e também por editoras brasileiras (Cengage/Thomson). **Já o
  artigo cita Howard T. Odum** (*Environment, Power, and Society*, John
  Wiley & Sons/Wiley-Interscience, 1971, confirmado por catálogos de
  editora e livrarias) — irmão de Eugene P. Odum, ecólogo distinto, autor
  de obra distinta.
- Não foi localizada, nas buscas realizadas, uma edição de
  *Fundamentos de Ecologia* datada exatamente de 1996 (as edições
  Gulbenkian encontradas são 1973/1976/2004; a edição Cengage brasileira
  não teve o ano de publicação confirmado com precisão nesta auditoria).
- Como o projeto de doutorado não está acessível a partir deste
  repositório (`classificacao-chamados` é repositório separado, sem
  vínculo com os arquivos da tese), não foi possível confirmar se a
  citação "Odum" do projeto se refere a Eugene P. Odum ou a Howard T.
  Odum — a diferença de autoria é substantiva, não apenas de edição.
  `Informação insuficiente para verificar.`
- **Decisão:** a referência do artigo (Howard T. Odum, 1971) **não foi
  alterada**. Substituí-la por Eugene P. Odum sem confirmação da autoria
  pretendida pelo projeto arriscaria atribuir ao artigo uma obra e um autor
  diferentes dos que o parágrafo da Introdução efetivamente sustenta (a
  passagem trata de retroalimentação sistêmica entre uso, falha e reparo,
  tema mais próximo da ecologia de sistemas de H. T. Odum do que do
  manual geral de ecologia de E. P. Odum). Registrado como **item
  parcial/bloqueado**: o autor deve confirmar, a partir do texto do
  projeto, qual dos dois Odum e qual edição pretendia citar antes de
  qualquer harmonização adicional nesta referência.

## 3. Inspeção visual do PDF

PDF regenerado duas vezes pelo workflow oficial (`artigo_pdf.yml`,
`workflow_dispatch`) na própria branch, runs `31900772924` e
`31901095700`. **21 páginas**, dentro da faixa 21–23. Renderização real
via PyMuPDF a 150–400 dpi (não apenas o LaTeX intermediário), 18 das 21
páginas inspecionadas individualmente (1, 2, 5–21).

**Achado na primeira renderização (`31900772924`), corrigido antes da
segunda:** o caractere Unicode cru `≤` inserido no item 8 foi
silenciosamente descartado pelo pandoc/xelatex ao converter para PDF,
deixando "com *p* 0,0005" sem o operador na página 8. Substituído por
`$\leq$` em LaTeX — mesmo padrão já usado para $\rho$ e $\lambda$ em
rodada anterior (ver `PLANO_EXECUCAO_ATUAL.md`, rodada de posicionamento
editorial). Confirmado corrigido na segunda renderização
(`31901095700`): "com *p* ≤ 0,0005" renderiza corretamente.

Pontos do parecer conferidos (numeração de página pode ter deslocado
frente ao parecer original, pois a estrutura do artigo mudou nas Rodadas
12–13, já mescladas em `main` antes desta rodada): página 1 (autores e
e-mails corretos), página 5 (Tabela 1 íntegra, com a frase de ausência de
busca de hiperparâmetros), página 8 (Tabela 2, Figura 2 e o teste global
com `p ≤ 0,0005`, após a correção acima), página 9 (Tabela 3 com a
legenda de "Neutros" e a fórmula 18,53%), página 10 (Tabela 4, sem vão
antes dela), página 11 (Figura 4 e a frase sobre o Naive Bayes sem
reponderação), página 12 (Figura 5), página 13 (Figura 6, Tabela 5 e a
distinção ABC global/interna ao tipo), página 14 (Subseção 5.2 com a
reconciliação 598/593), página 15 (Subseção 5.3 com o otimismo da seleção
do LinearSVC, sem título órfão), página 16 (Considerações Finais e início
das Referências, sem título órfão), páginas 17–19 (Capra 1997, Grimm
*et al.* 2000 com DOI completo, Ticket-BERT como preprint, Li e
Bouabdallaoui inalterados e corretos), página 20 (ordem título →
introdução → Tabela A1, com o novo parágrafo distinguindo A1 de A2/A3),
página 21 (Tabela A2 com "classe da curva ABC interna ao tipo" e Tabela
A3, ambas com nota de fonte visível). Nenhuma sobreposição, corte,
título órfão ou tabela fora de ordem encontrada. Nenhuma correção visual
das PRs #211–#214 foi refeita nesta rodada — o único ajuste visual foi o
`$\leq$` acima, decorrente diretamente do item 8 desta própria rodada.

## 4. Controle de extensão

- Contagem inicial (antes das correções, `origin/main`): **8.948 palavras**.
- Após aplicar os itens 1–12: pico de **9.313 palavras**, acima do teto de
  9.000.
- Cortes compensatórios locais aplicados exclusivamente nas subseções
  tocadas pelas correções (Introdução, 3.3, 4.2, 4.4, 4.5, 5.2, 5.3,
  introdução do Apêndice A), eliminando redundância de prosa sem remover
  dado, ressalva, citação ou conclusão.
- Contagem final: **8.999 palavras**, dentro da faixa-meta 8.850–9.000.

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
