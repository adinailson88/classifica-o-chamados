# Auditoria final de submissão — Rodada 10

> Relatório de auditoria editorial e de reprodutibilidade. Não reabre
> decisões científicas encerradas em `PLANO_EXECUCAO_ATUAL.md` nem
> reestrutura o artigo. Escopo: consistência numérica, metadados,
> referências cruzadas, bibliografia, declarações de submissão e
> resíduos documentais.

**Branch:** `agent/rodada-10-auditoria-final-submissao`
**Commit-base:** `7338214fe537b4ac12783e1caccc6abee47d2d4e` (`BASE_SHA_INICIAL`, `main`, pós-merge da PR #203 e pós-regeneração automática do PDF)
**Data:** 06/08/2026, fuso America/Bahia
**Hash do corpus (rodada canônica):** `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`

## 1. Estado verificado antes de iniciar

Confirmado ao vivo (`git fetch`, `gh pr list`, `gh run list`, `git log`), não apenas assumido do prompt:

| Item | Esperado | Observado |
|---|---|---|
| PR #203 mesclada | sim | sim — merge commit `69052405` |
| Commit automático do PDF pós-merge | sim | sim — `7338214f`, mensagem `pdf do artigo gerado automaticamente [skip ci]` |
| `artigo_pdf.yml` pós-merge concluído | sucesso | sucesso, run `31067238514` |
| PR aberta no início da rodada | nenhuma | nenhuma (`gh pr list --state open` vazio) |
| Árvore de trabalho | limpa | limpa |

## 2. Escopo da auditoria

Consistência científica e numérica; metadados e coerência bilíngue; tabelas, figuras e referências cruzadas; referências bibliográficas; declarações de submissão; resíduos documentais; linguagem de relatório no corpo do artigo. Nenhuma métrica, denominador, partição, hash ou conclusão foi alterada. As únicas mudanças no texto científico foram uma chamada de tabela ausente (ver Seção 4) e a correção de resíduos nos documentos de continuidade (Seção 8).

## 3. Matriz de consistência numérica

Números centrais conferidos em todas as ocorrências (Resumo, Abstract, Método, Resultados, tabelas, legendas, figuras, Discussão, Considerações Finais, apêndice), contra os artefatos canônicos listados em `docs/MATRIZ_PROVENIENCIA.md`.

| Afirmação | Localização | Valor encontrado | Artefato canônico | Situação |
|---|---|---:|---|---|
| Corpus congelado | Resumo/Abstract/Apêndice A (Tabela A1) | 14.060 / 14,060 | `docs/dados/auditoria_base_canonica.json` | conforme |
| Linhas avaliadas | Resumo/Abstract/Método/Resultados/Tabela A2 | 13.972 / 13,972 | `docs/dados/retreino_canonico.json` e demais artefatos da rodada | conforme |
| Categorias com suporte | Resumo/Abstract/Tabela A2 | 41 | `docs/dados/retreino_canonico.json` | conforme |
| Linhas/categorias fora das partições | Apêndice A (Tabela A3) | 88 linhas / 9 categorias | `docs/dados/particoes_canonicas.json` | conforme (soma das 9 linhas da Tabela A3 = 88) |
| Taxa de alteração do rótulo histórico | Resumo/Abstract | 4,25% / 4.25% | `docs/dados/comparacao_historica.json` | conforme; não tratada como prevalência de erro em nenhuma ocorrência |
| Acurácia do melhor modelo (LinearSVC) | Resumo/Abstract/Considerações Finais | 0,8253 / 0.8253 | `docs/RETREINO_CANONICO.md` | conforme |
| Automação seletiva ao alvo de 0,95 | Resumo/Abstract/Subseção 4.3 | "cerca de dois terços" (68,90% LinearSVC / 67,32% Extra Trees) | `docs/CALIBRACAO_CANONICA.md` | conforme |
| Ganho líquido de reclassificação | Subseção 4.2/Considerações Finais | negativo nos sete modelos; 475/2.321/−1.846 (LinearSVC) | `docs/REGRAS_VERSUS_MODELOS.md` / `docs/dados/comparacao_historica.json` | conforme |
| Referências bibliográficas | Lista de referências | 45 entradas | contagem por blocos entre `**REFERÊNCIAS**` e `Apêndice A` | conforme |
| Corpo científico | fonte Markdown | 8.915 palavras | contagem entre `**1. INTRODUÇÃO**` e `**REFERÊNCIAS**`, exclusive | conforme à meta de 8.850–9.000; ver reconciliação na Seção 8 |
| Hash do corpus | `docs/MATRIZ_PROVENIENCIA.md` | `1e4762438a7e...` em todos os 8 artefatos derivados e 3 do congelamento | `src/matriz_proveniencia.py` | conforme — 0 divergências |

Nenhum número da execução legada (protocolo anterior, denominadores 14.058/14.082/8.895) foi localizado no corpo do artigo, confirmado por `python src/matriz_proveniencia.py`.

## 4. Metadados e coerência bilíngue

- Título em português e em inglês descrevem a mesma contribuição (protocolo auditável, fluxo humano–IA, calibração, risco de reclassificação); nenhuma promessa de previsão de demanda/custo ou validação temporal em nenhum dos dois.
- Resumo (249 palavras) e Abstract (247 palavras) seguem estrutura paralela de nove movimentos, com os mesmos números nas duas línguas (14.060/14,060; 13.972/13,972; 41; 4,25%/4.25%; 0,8253/0.8253).
- Palavras-chave e keywords correspondem termo a termo.
- Siglas (ECE, LSTM, GLPI, LGPD) definidas ou evidentes por contexto na primeira ocorrência.
- Nomenclatura de modelos uniforme (LinearSVC, SGD, Extra Trees, Regressão Logística, Random Forest, LSTM, Naive Bayes) em todas as ocorrências verificadas.
- Separador decimal: vírgula em português, ponto em inglês, sem mistura localizada.
- Situação: **conforme**, nenhuma correção aplicada.

## 5. Tabelas, figuras e referências cruzadas

- **Seis figuras** confirmadas: arquivos presentes em `04_artigo/figuras/` (`fig_pipeline_governanca.pdf`, `fig_tradeoff_custo.pdf`, `fig_confianca_desfecho.pdf`, `fig_calor_categorias.pdf`, `fig_matriz_confusao.pdf`, `fig_curva_aprendizado_lstm.pdf`) e citadas no corpo como Figura 1 a 6, na ordem de aparição. Figura 2 com eixo Y em duas casas decimais, confirmado (microcorreção da Rodada 9 preservada; nenhuma execução do gerador legado `src/gerar_figura3_tradeoff_custo.py` nesta rodada).
- **Quatro tabelas principais** confirmadas: `\label{tab:modelos}`, `tab:desempenho`, `tab:reclassificacao`, `tab:calibracao`, todas como floats `\begin{table}[!tbp]` com `tabularx`. Tabelas 1 a 3 são chamadas por número no corpo ("Tabela 1", "Tabela 2", "Tabela 3"); a Tabela 4 (calibração) era descrita em prosa na Subseção 4.3 sem a chamada "(Tabela 4)" — **corrigido nesta rodada** (Seção 8).
- **Tabelas A1 a A3** confirmadas como floats não divisíveis em `\footnotesize`, com contador próprio (`\renewcommand{\thetable}{A\arabic{table}}` + `\setcounter{table}{0}`), numeradas A1/A2/A3. Somas conferem: A1 = 14.060 (total geral da distribuição por categoria histórica); A2 = 4.902 + 8.485 + 585 = 13.972 (preventiva + corretiva + não manutenção); A3 = 88 (soma das 9 categorias excluídas).
- **Material suplementar**: a Subseção 4.3 cita explicitamente "Tabela S16"; as demais remissões ao longo do corpo usam a expressão genérica "material suplementar", sem numeração — consistente com o uso já estabelecido nas rodadas anteriores. Os CSVs numerados presentes em `04_artigo/figuras/` vão de S1 a S16, **com uma lacuna em S4**: não existe `tabela_S4_holdout_vs_kfold.csv`. O gerador que produziria esse nome de arquivo, `src/comparacao_holdout_kfold.py`, pertence ao protocolo legado — usa a categoria histórica como alvo (não a referência humana revisada), lê `docs/dados/estatistica.json` (fonte da execução legada, não da rodada canônica) e compara holdout fixo contra k-fold sob esse protocolo anterior, sem carregar `hash_corpus` da rodada `1e476243`. A antiga Tabela S4 foi retirada porque seu gerador pertence ao protocolo legado e não pode alimentar o suplemento canônico; a lacuna de numeração não deve ser preenchida pela regeneração desse artefato. `src/comparacao_holdout_kfold.py` não foi executado nem alterado nesta auditoria. S4 não é citado por número em nenhum ponto do corpo do artigo, de modo que a lacuna não quebra nenhuma remissão. Decisão editorial restante (Seção 9): antes do empacotamento para submissão, renumerar S5–S16 para S4–S15 ou incluir no índice do suplemento uma nota explícita de retirada; a alternativa recomendada é a renumeração contínua, a ser realizada junto à adaptação ao periódico escolhido. Nenhuma renumeração foi aplicada nesta rodada.
- Nenhuma figura, tabela, apêndice ou item suplementar órfão encontrado; nenhuma remissão a numeração inexistente (após a correção da Seção 8).

## 6. Auditoria bibliográfica

- Contagem por blocos entre `**REFERÊNCIAS**` e `Apêndice A`: **45 entradas**, confirmando o valor já registrado em `PLANO_ARTIGO_CAPITULO.md`.
- Checagem cruzada automatizada (sobrenome do primeiro autor de cada entrada contra o corpo, sem diferenciar maiúsculas/minúsculas): as 45 entradas têm ao menos uma citação no corpo. As duas entradas institucionais (ABNT; BRASIL) são citadas pela sigla/nome da instituição (`ABNT, 2012`; `BRASIL, 2018`), não pelo primeiro token do bloco de referência — verificado manualmente, sem divergência real.
- Nenhuma duplicata identificada.
- Nenhum DOI ou URL foi adicionado, alterado ou inventado nesta rodada.
- Situação: **conforme**, nenhuma correção necessária.

## 7. Declarações de submissão

| Item | Situação encontrada |
|---|---|
| Disponibilidade de dados | Declarada na Subseção 3.6: base de trabalho não pública, por restrição de privacidade institucional; artefatos publicados sanitizados (sem identificador pessoal, título ou descrição livre; mapas por registro usam SHA-256 do identificador). |
| Disponibilidade de código | Declarada na Subseção 3.6: código público em `https://github.com/adinailson88/classificacao-chamados`. |
| Aspectos institucionais / ética | Declarada na Subseção 3.6 e reiterada na Subseção 5.3: o repositório **não guarda** documento de autorização institucional formal, aprovação por comitê de ética ou dispensa de apreciação ética; nada é afirmado sobre esse ponto. |
| Financiamento | **Não localizada** nenhuma declaração de financiamento em nenhuma seção do artigo. |
| Conflito de interesses | **Não localizada** nenhuma declaração de conflito de interesses. |
| Contribuição dos autores | **Não localizada** nenhuma declaração formal de contribuição por autor (CRediT ou equivalente). |
| Uso de inteligência artificial | **Não localizada** nenhuma declaração sobre uso de ferramentas de IA generativa/assistida na pesquisa, análise ou redação. |

**Bloqueador externo à submissão:** não foi localizado documento de autorização institucional, aprovação ética ou dispensa formal. Informação insuficiente para verificar. Esta ausência já estava declarada no próprio artigo (Subseções 3.6 e 5.3) e em `PLANO_EXECUCAO_ATUAL.md`; a Rodada 10 apenas confirma que a lacuna documental persiste e corrige uma remissão interna que apontava para a subseção errada (ver Seção 8).

As ausências de financiamento, conflito de interesses, contribuição dos autores e uso de IA **não foram preenchidas nesta rodada**: nenhum documento comprobatório dessas informações existe no repositório, e nenhuma delas pode ser inferida ou presumida sem risco de fabricar declaração em nome dos autores. Ficam registradas como itens que dependem de decisão do autor (Seção 9).

## 8. Correções aplicadas

1. **Artigo** (`04_artigo/artigo_classificacao_chamados_v3.md`): acrescentada a chamada "(Tabela 4)" à frase que descreve a melhora do ECE após calibração isotônica (Subseção 4.3), alinhando-a às Tabelas 1 a 3, já citadas por número. Nenhum valor, dado ou conclusão alterado. Corpo científico: 8.913 → 8.915 palavras (ainda dentro da faixa-meta de 8.850–9.000).
2. **`PLANO_EXECUCAO_ATUAL.md`**: substituída a "Regra principal" obsoleta, que classificava os resultados publicados como "legados" apesar de a execução canônica `1e476243` já estar publicada em `main` desde a PR #203; corrigida a remissão a "Subseção 3.8" (inexistente — o Método vigente tem seis subseções) para "Subseção 3.6"; reconciliada a contagem de palavras (8.917 → 8.915, com nota explicando as duas alterações que produziram a diferença); registrado o merge da PR #203, o commit automático do PDF e a abertura da Rodada 10.
3. **`PLANO_ARTIGO_CAPITULO.md`**: a seção "Estado desta rodada", que acumulava a narrativa detalhada das Rodadas 6 a 9 (~260 linhas, violando a própria "Regra de uso" nº 4 do documento, que pede substituição sem acúmulo), foi condensada a um estado atual único, com o detalhamento remetido aos commits e às Pull Requests #202/#203; contagem de palavras reconciliada para 8.915.
4. **`04_artigo/README.md`**: seção "Estado atual" atualizada (contagem de palavras para 8.915, remoção de linguagem de commit-a-commit da Rodada 9 já coberta no histórico do Git, registro de que a próxima fase é a auditoria final de submissão).

Nenhum artefato científico canônico foi alterado. `docs/dados/matriz_proveniencia.json` foi regenerado, com alteração exclusiva do campo `gerado_em`; hashes, resultados, denominadores e conteúdo científico permaneceram inalterados. Nenhuma alteração tocou partições, categorias ou conclusões científicas.

## 9. Itens que dependem de decisão do autor

- **Financiamento, conflito de interesses, contribuição dos autores e uso de inteligência artificial**: nenhuma declaração existe hoje no artigo. Antes da submissão, o autor precisa decidir o texto de cada declaração (inclusive se há financiamento a declarar) e onde inseri-las — tipicamente uma seção "Declarações" entre as Considerações Finais e a lista de Referências, padrão já usado por muitos periódicos.
- **Autorização institucional / aprovação ética / dispensa formal**: bloqueador já declarado no artigo; requer providência do autor junto à instituição antes da submissão, não uma edição de texto.
- **Lacuna de numeração no material suplementar (S4)**: a antiga Tabela S4 (`tabela_S4_holdout_vs_kfold.csv`) foi retirada porque seu gerador, `src/comparacao_holdout_kfold.py`, pertence ao protocolo legado (alvo histórico, fonte `estatistica.json`, sem `hash_corpus` canônico) e não pode alimentar o suplemento canônico; regenerar esse artefato está fora de cogitação. A numeração salta de S3 para S5, sem quebrar nenhuma remissão do corpo (S4 não é citado por número em ponto algum). Decisão editorial restante: antes do empacotamento para submissão, renumerar S5–S16 para S4–S15 ou incluir no índice do suplemento uma nota explícita de retirada; a alternativa recomendada é a renumeração contínua, a ser realizada junto à adaptação ao periódico escolhido.
- **Escolha do periódico**: fora do escopo desta rodada, por instrução explícita.

## 10. Veredito

**Apto com pendência documental.**

O artigo está numericamente consistente com os artefatos canônicos, bilíngue e com referências cruzadas corretas (após a correção da Seção 8), com bibliografia íntegra e sem número legado. O veredito não pode ser "pronto para submissão" porque subsiste o bloqueador de autorização institucional/aprovação ética (Seção 7), e porque as declarações de financiamento, conflito de interesses, contribuição dos autores e uso de IA ainda não foram redigidas — itens que dependem de decisão do autor, não de correção editorial.

## 11. Testes

Executados antes e depois das alterações desta rodada, sem diferença de resultado:

```text
python -m unittest discover -s tests   # 507 testes, OK
python -m py_compile src/*.py          # sem erro
python src/matriz_proveniencia.py      # 0 divergências, hash 1e4762438a7e confirmado
python src/tabelas_suplementares_canonicas.py  # hash confirmado, 10 tabelas (S7–S16) regeneradas sem mudança de conteúdo
```

## 12. PDF

O artigo foi alterado nesta rodada (chamada "(Tabela 4)" acrescentada). O PDF foi regenerado pelo procedimento oficial (`artigo_pdf.yml` via `workflow_dispatch` na própria branch `agent/rodada-10-auditoria-final-submissao`, run `31068296264`, mesmo mecanismo usado na Rodada 9 por ausência de xelatex/Docker locais) e commitado automaticamente (`e8610cd9`).

**22 páginas**, dentro da faixa 21–23. Inspeção visual real das 22 páginas (renderização em PNG a 150 dpi via PyMuPDF/`fitz`), não apenas do LaTeX intermediário:

- Título, Resumo e Abstract íntegros e sem quebra de layout (página 1).
- As seis figuras renderizam corretamente, com a Figura 2 mantendo o eixo Y em duas casas decimais (0,72 a 0,82, sem marcas repetidas — microcorreção da Rodada 9 preservada).
- As quatro tabelas principais e as Tabelas A1 a A3 renderizam íntegras, com legenda e conteúdo na mesma página, incluindo a chamada "(Tabela 4)" acrescentada nesta rodada, sem quebra de linha nem estouro de margem.
- A lista de referências (páginas 17 a 19) está bem formatada, sem entrada cortada.
- As duas páginas com espaço em branco já documentadas em `PLANO_ARTIGO_CAPITULO.md` (antes da Figura 3, página 10/11; acima da Tabela A3, página 22) persistem, comportamento esperado de floats LaTeX não divisíveis, sem regressão nem piora frente à Rodada 9.
- Nenhum caractere ausente, nenhuma página quase vazia fora das duas já conhecidas, nenhuma referência cruzada quebrada.

## Proveniência

- Script auxiliar de contagem: rotina Python ad hoc, mesma definição de fronteira (`**1. INTRODUÇÃO**` a `**REFERÊNCIAS**`, exclusive) usada desde a Rodada 7.
- Nenhuma escrita foi realizada na planilha viva.
- Nenhum artefato de dados (`docs/dados/*.json`) foi alterado.
