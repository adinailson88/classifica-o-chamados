# Auditoria — consolidação e renumeração do material suplementar (item 13)

> Relatório de auditoria editorial e de reprodutibilidade. Não reabre
> decisões científicas encerradas em `PLANO_EXECUCAO_ATUAL.md` nem
> retreina, ajusta ou reavalia modelo algum. Escopo: exclusivamente o
> item 13 do parecer científico — consolidação, renumeração contínua e
> publicação do material suplementar, tratado em PR própria, sem
> empilhamento sobre a PR #215.

**Branch:** `docs/consolidacao-material-suplementar`
**SHA inicial** (`main`, ponto em que a branch foi criada): `aca9691116f8f73b1405ff3fa44c4d1ae5e1f30e`
**SHA final** (topo desta branch ao fim da rodada): `c0ca9b2d5c1abf3ae3c57c8646b34527ad3fa11b`
**Confirmado:** o commit `52589c0c19dfd8b5b453b5844e0c13a1a87a45e3` (final da PR #215) é ancestral de `aca96911` — a PR #215 estava mesclada em `main` antes do início desta rodada, condição obrigatória verificada com `git fetch`/`gh pr view 215` no início da sessão.
**Hash do corpus (rodada canônica):** `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`
**Data:** 15–16/08/2026, fuso America/Bahia

## 1. Estado verificado antes de iniciar

| Item | Esperado | Observado |
|---|---|---|
| PR #215 mesclada | sim | sim — `state: MERGED` |
| Commit `52589c0c` incorporado a `main` | sim | sim (`git merge-base --is-ancestor` confirma) |
| PR aberta tratando do material suplementar | nenhuma | nenhuma (`gh pr list --state open` vazio para os termos "material suplementar", "suplemento", "consolidacao") |
| Árvore de trabalho | limpa | limpa |

## 2. Problema resolvido

Existiam 16 tabelas suplementares numeradas de S1 a S17, com lacuna em
S4: a antiga `tabela_S4_holdout_vs_kfold.csv` fora retirada em rodada
anterior porque seu gerador (`src/comparacao_holdout_kfold.py`)
pertence ao protocolo legado — alvo histórico, fonte
`docs/dados/estatistica.json`, sem `hash_corpus` da rodada canônica —
e não pode alimentar o suplemento canônico. A antiga S17 (Fase 2C) era
numeração provisória, mantida em sequência após S16 apesar da lacuna
já existente em S4 (ver `docs/AUDITORIA_FINAL_SUBMISSAO.md`, seção 9,
Rodada 10).

**Decisão desta rodada:** renumeração contínua de S5–S17 para S4–S16,
sem recriar a tabela legada S4. `src/comparacao_holdout_kfold.py` e o
CSV que ele geraria permanecem fora do fluxo vigente, intocados.

## 3. Mapeamento completo da renumeração

| Atual (antes) | Nova (depois) | Arquivo antes | Arquivo depois |
|---|---|---|---|
| S1 | S1 | `tabela_S1_metricas_por_categoria.csv` | inalterado |
| S2 | S2 | `tabela_S2_codigos_categorias.csv` | inalterado |
| S3 | S3 | `tabela_S3_ablation_lstm.csv` | inalterado |
| S5 | S4 | `tabela_S5_kfold_vs_groupkfold.csv` | `tabela_S4_kfold_vs_groupkfold.csv` |
| S6 | S5 | `tabela_S6_holdout_bertimbau.csv` | `tabela_S5_holdout_bertimbau.csv` |
| S7 | S6 | `tabela_S7_dispersao_predicoes.csv` | `tabela_S6_dispersao_predicoes.csv` |
| S8 | S7 | `tabela_S8_curva_abc_global.csv` | `tabela_S7_curva_abc_global.csv` |
| S9 | S8 | `tabela_S9_tarefa_tipo.csv` | `tabela_S8_tarefa_tipo.csv` |
| S10 | S9 | `tabela_S10_curva_abc_por_tipo.csv` | `tabela_S9_curva_abc_por_tipo.csv` |
| S11 | S10 | `tabela_S11_regras_versus_modelos.csv` | `tabela_S10_regras_versus_modelos.csv` |
| S12 | S11 | `tabela_S12_inferencia_agrupada.csv` | `tabela_S11_inferencia_agrupada.csv` |
| S13 | S12 | `tabela_S13_classes_raras.csv` | `tabela_S12_classes_raras.csv` |
| S14 | S13 | `tabela_S14_utilidade_reclassificacao.csv` | `tabela_S13_utilidade_reclassificacao.csv` |
| S15 | S14 | `tabela_S15_pressupostos.csv` | `tabela_S14_pressupostos.csv` |
| S16 | S15 | `tabela_S16_calibracao_completa.csv` | `tabela_S15_calibracao_completa.csv` |
| S17 | S16 | `tabela_S17_ensemble_confirmatorio.csv` | `tabela_S16_ensemble_confirmatorio.csv` |

Ao final existem exatamente as tabelas S1 a S16, sem lacuna e sem S17.
S4 não foi recriada. Renomeações feitas com `git mv`, em ordem
decrescente de número (S17 primeiro, S5 por último) para não colidir
com um nome já ocupado durante o processo.

## 4. Hashes SHA-256 antes e depois

Calculados com `sha256sum` sobre cada CSV, antes de qualquer `git mv`
e novamente depois. Todos idênticos — conteúdo preservado byte a
byte; apenas o nome do arquivo mudou.

| Tabela nova | SHA-256 (antes = depois) |
|---|---|
| S1 (inalterada) | `23cddbb1514109288a1c57653121dac04b0cf45ad4880d2b7d1e3d4fd7c026ed` |
| S2 (inalterada) | `fbc521500c08516cbea50cab93e46aacaa1009289a99172990d7474b355f7abe` |
| S3 (inalterada) | `9bdfe6b7ba1a2d8c0b70cdd9e9cf8992a7274ad576530c58a78eeca77e785943` |
| S4 (era S5) | `20239fe5069fba56d3e8ca170f8eef97ba129cbd63ab00c96169c5bf25f5e974` |
| S5 (era S6) | `8616d4e118b57b8cd4e30aa0ddfcbee6ff6a5bf06937404c35f068fbb9383822` |
| S6 (era S7) | `f1a9d8d4ab3d54d93bd4358a4d96a1a0f5638926e9da40da194f7344aed5b455` |
| S7 (era S8) | `487801ece457c91d32af7e3bcc22e0de1b1788618f14d1939ef11fa4aeb4da0a` |
| S8 (era S9) | `f74a4cc0f2ab240d538811d8a7b007bd2e818fe382d97628a84274398c84f8f5` |
| S9 (era S10) | `6a7f577ded8e3d440588a4539add07fc18a9af046f97f129931a030d5c3acbea` |
| S10 (era S11) | `211b9952f07d3d5f6ff3f3ec1ef2d84df3a3f7535dee640baab2c17934d60d4e` |
| S11 (era S12) | `10e5ff5728f64cc2fef1ff2a9e8f9330e1c3133451ab8b276ac41cb22d0d856e` |
| S12 (era S13) | `fb95ebfc1d0ad5ef85b6b0289f107ee9c5e6b89fe0e716e8c7967bee3f284b3c` |
| S13 (era S14) | `07d7cd7f17d97d423fbd093573159530861ae303fadc0758c8ed774b84dbacfc` |
| S14 (era S15) | `a58d3393bf23ea8c8e53b35d3ce49238e5b85f1351bcde2e43530bfc74587325` |
| S15 (era S16) | `f44ed6941c3d9b487d335b58d4e84c7cfbbcfacd632c69061ede34169bafc8a3` |
| S16 (era S17) | `55550b677552942b24c538963e5a4286ecefa4b1de87d55466d11ff065ea09c4` |

**Confirmação:** `git status` após os `git mv` mostrou 13 entradas
`R` (renamed, sem modificação de conteúdo) e 3 arquivos ausentes da
lista (S1–S3, inalterados), somando as 16 tabelas.

## 5. Título, fonte e artefato científico de cada tabela

| Tabela | Título técnico | Fonte / gerador | Artefato científico | Trilha |
|---|---|---|---|---|
| S1 | Métricas por categoria (suporte, precisão, recall, F1) | aba viva da planilha (`TABELA_S1_METRICAS`, gid=1862157493) ou `docs/dados/metricas_por_categoria.json`; `src/exportar_tabela_por_categoria.py` | execução legada, anterior ao congelamento | legado, pré-congelamento |
| S2 | Códigos de categoria da Figura 3 | `docs/dados/estatistica.json`; `src/gerar_figura4_confusoes.py` | execução legada | legado, pré-congelamento |
| S3 | *Ablation* do LSTM (unidades × *dropout*) | `04_artigo/figuras/ablation_lstm_resultados.json`; `src/ablation_lstm.py` (inoperante desde 02/08/2026) | *snapshot* de 24/07/2026, 9.096 linhas | legado, pré-congelamento |
| S4 | KFold por linha *vs.* GroupKFold por grupo textual | `04_artigo/figuras/comparacao_kfold_groupkfold.json`; `src/comparacao_kfold_groupkfold.py` | base de 01/08/2026, 14.094 chamados | legado, pré-congelamento |
| S5 | Holdout exploratório do BERTimbau | avaliação held-out complementar citada na Subseção 4.5; gerador não localizado no repositório | lote de 1.000 chamados (983 com referência humana) | exploratório (BERTimbau) |
| S6 | Dispersão das predições | `docs/dados/comparacao_historica.json` | rodada canônica | rodada canônica |
| S7 | Curva ABC global, acurácia e macro-F1 | `docs/dados/recortes_canonicos.json` | rodada canônica | rodada canônica |
| S8 | Tarefa de tipo de manutenção | `docs/dados/recortes_canonicos.json` | rodada canônica | rodada canônica |
| S9 | Curva ABC interna a cada tipo (LinearSVC) | `docs/dados/recortes_canonicos.json` | rodada canônica | rodada canônica |
| S10 | Regras de periodicidade *vs.* modelo puro | `docs/dados/regras_versus_modelos.json` | rodada canônica | rodada canônica |
| S11 | Inferência pareada agrupada (21 pares) | `docs/dados/inferencia_agrupada.json` | rodada canônica | rodada canônica |
| S12 | Macro-F1 sob três convenções de denominador | `docs/dados/sensibilidade_classes_raras.json` | rodada canônica | rodada canônica |
| S13 | Utilidade da reclassificação sob custos assimétricos | `docs/dados/utilidade_reclassificacao.json` | rodada canônica | rodada canônica |
| S14 | Pressupostos estatísticos secundários | `docs/dados/inferencia_canonica.json` | rodada canônica | rodada canônica |
| S15 | Calibração completa dos sete modelos | `docs/dados/calibracao_canonica.json` | rodada canônica | rodada canônica |
| S16 | Fase 2C: LinearSVC *vs.* combinações de *ensemble* | manifesto confirmatório da Execução Científica 1 da Fase 2C | trilha experimental própria, validada por proveniência (não por `hash_corpus`) | confirmatório (Fase 2C) |

## 6. Referências cruzadas atualizadas

Busca global por `Tabela S`, `tabela_S`, `S16`, `S17`, `material
suplementar`, `suplemento` no início da rodada, para listar todos os
arquivos que dependem da numeração:

- `04_artigo/artigo_classificacao_chamados_v3.md`
- `04_artigo/README.md`
- `docs/AUDITORIA_FINAL_SUBMISSAO.md`
- `docs/AUDITORIA_PARECER_ARTIGO_PROJETO.md`
- `docs/dados/ensemble/fase2c/EXECUCAO_CIENTIFICA_1.md`
- `docs/RASTREABILIDADE_LSTM.md`
- `PLANO_ARTIGO_CAPITULO.md`
- `PLANO_EXECUCAO_ATUAL.md`
- `src/ablation_lstm.py`
- `src/comparacao_holdout_kfold.py`
- `src/comparacao_kfold_groupkfold.py`
- `src/exportar_tabela_por_categoria.py`
- `src/gerar_figura4_confusoes.py`
- `src/tabelas_suplementares_canonicas.py`
- `tests/test_comparacao_holdout_kfold.py`
- `tests/test_tabelas_suplementares_s17.py`
- `verificacao/relatorio_revisao_v4.md`

**Chamadas por número no corpo do artigo:** apenas duas ocorrências
existiam (`Tabela S16` na Subseção 4.3, sobre calibração completa;
`Tabela S17` na Subseção 4.5, sobre a Fase 2C). Atualizadas para
`Tabela S15` e `Tabela S16`, respectivamente. As demais menções ao
suplemento no corpo usam a expressão genérica "material suplementar",
sem número, e não precisaram de alteração.

**`src/tabelas_suplementares_canonicas.py`:** as dez funções que geram
S7–S17 foram renomeadas para `s6_` a `s16_` (acompanhando a nova
numeração), preservando integralmente a lógica de cada uma — nenhuma
fórmula, filtro ou fonte de dado foi alterado, apenas o nome da função
e o nome do arquivo CSV de saída. O docstring do módulo foi atualizado
para descrever S6–S16 em vez de S7–S17, removendo a nota sobre
numeração provisória (já resolvida).

**`src/comparacao_kfold_groupkfold.py`:** a constante `SAIDA_CSV` foi
atualizada de `tabela_S5_kfold_vs_groupkfold.csv` para
`tabela_S4_kfold_vs_groupkfold.csv`. O script não foi executado nesta
rodada (requer credencial de planilha).

**`tests/test_tabelas_suplementares_s17.py`:** renomeado para
`tests/test_tabelas_suplementares_s16.py`, com a classe de teste e a
chamada de função atualizadas de `s17_ensemble_confirmatorio` para
`s16_ensemble_confirmatorio`. As asserções (valores de fixture,
mensagens de bloqueio) permanecem idênticas — o teste continua
validando a mesma lógica de proveniência da Fase 2C.

**`src/comparacao_holdout_kfold.py`:** intencionalmente **não**
alterado. Pertence ao protocolo legado, sua saída
(`tabela_S4_holdout_vs_kfold.csv`) é a tabela retirada que não deve
ser recriada, e o script não foi e não deve ser executado.
`tests/test_comparacao_holdout_kfold.py` testa esse script legado
isoladamente e também não foi tocado.

**`docs/dados/ensemble/fase2c/EXECUCAO_CIENTIFICA_1.md`,
`verificacao/relatorio_revisao_v4.md`:** documentos de auditoria
histórica de rodadas anteriores (Rodada 11 e Rodada 12,
respectivamente); registram o estado de S16/S17 *como existia
naquele momento*. Não foram alterados, por registrarem histórico, não
estado vigente — consistente com a regra de uso de
`PLANO_ARTIGO_CAPITULO.md` ("Registro histórico").

## 7. Consolidação e publicação do material suplementar

Não havia, no repositório, fonte consolidada nem pipeline de geração
de um documento único do suplemento — apenas os 16 CSVs individuais e
citações genéricas em prosa no artigo. Foram criados:

- `04_artigo/material_suplementar_classificacao_chamados.md`: fonte
  editável, com sumário (S1–S16, título e trilha), e para cada tabela
  um título técnico, nota de fonte/proveniência (incluindo trilha —
  rodada canônica, legado pré-congelamento, exploratório do BERTimbau
  ou confirmatório da Fase 2C — e denominador), e o conteúdo completo
  reproduzido do CSV correspondente, sem recálculo. Tabelas largas
  demais para a página (S10, S11, S13, S14, S15, S16) foram divididas
  em duas ou três partes, com a chave repetida em cada parte.
- `docs/material_suplementar_classificacao_chamados.pdf`: PDF gerado
  a partir do `.md` acima, 13 páginas, inspecionado visualmente
  página a página (Seção 9).
- `.github/workflows/material_suplementar_pdf.yml`: workflow próprio
  (decisão da Seção 8) que converte o `.md` em PDF via pandoc/xelatex
  e publica em `docs/`, disparado por push no `.md`/no próprio
  workflow (restrito a `main`) ou por `workflow_dispatch` manual.

Nenhuma promessa de disponibilização futura, justificativa defensiva,
ID/título/descrição livre de chamado, resultado recalculado, tabela
legada retirada ou declaração institucional não confirmada foi
incluída.

## 8. Decisão sobre o workflow de geração do PDF

**Workflow próprio, não integrado a `artigo_pdf.yml`.** Motivo: o
pipeline do artigo principal já está em produção (dispara em push nas
mudanças do `.md` do artigo e publica automaticamente); acoplar a
geração do suplemento ao mesmo job aumentaria o escopo de falha de um
processo já estável e exigiria condicionais para decidir qual PDF
regenerar a cada push. Um workflow próprio, espelhando a mesma
estrutura (`pandoc/extra` + `xelatex`, mesmo mecanismo de *fallback*
de `placeins.sty`), isola o risco e mantém `artigo_pdf.yml` com
comportamento idêntico ao anterior — confirmado nesta rodada: o
artigo foi regenerado (Seção 10) usando exatamente o job já existente,
sem qualquer edição a `artigo_pdf.yml`.

## 9. Testes de renderização e inspeção visual do suplemento

**Ausência de xelatex/Docker locais** (mesma situação já registrada
nas Rodadas 9 e 10 do artigo principal): PDFs gerados via
`workflow_dispatch`/push na própria branch, mecanismo já usado em
rodadas anteriores.

Três problemas visuais foram encontrados e corrigidos ao longo de
quatro ciclos de geração, todos de apresentação, sem alterar dado
algum:

1. **Build falhou** na primeira tentativa (`\FloatBarrier`
   indefinido): o suplemento não tinha o mesmo *fallback* de
   `placeins.sty` já usado no artigo principal. Corrigido copiando o
   mesmo mecanismo condicional (`\IfFileExists`) para o
   `header-includes` do suplemento.
2. **Cabeçalhos de coluna sobrepostos** (S7, S9, S10, S11, S12, S13,
   S14, S15) e **corte horizontal** (S16, 11 colunas): nomes de coluna
   com `_` são um único token que o LaTeX não hifeniza; colunas
   estreitas empurravam o cabeçalho para a célula vizinha. Corrigido
   trocando `_` por espaço nos cabeçalhos exibidos (permite quebra de
   linha) e dividindo as tabelas mais largas (S10, S13, S14, S15, S16)
   em duas ou três partes por largura de página — mesmo padrão já
   usado em S11 desde a primeira versão. A formatação numérica também
   passou a preservar a precisão original do CSV-fonte em vez de
   forçar sempre quatro casas decimais, encurtando colunas que na
   fonte já tinham menos dígitos (ex.: utilidade em ρ, antes exibida
   como `-1846,0000`, agora `-1846,0`, igual ao CSV).
3. **Caracteres ρ/λ ausentes** na nota da Tabela S13: os glifos gregos
   em Unicode bruto não renderizam na fonte do ambiente xelatex do
   workflow (nenhum erro de build, apenas espaço em branco no lugar
   do glifo). Corrigido usando `$\rho$`/`$\lambda$` em modo
   matemático, o mesmo padrão já usado no artigo principal.
4. **Corte horizontal do último item da lista de proveniência**: o
   nome de arquivo `AUDITORIA_MATERIAL_SUPLEMENTAR.md`, mesmo sem
   crase, continuou sendo um único token sem ponto de quebra na mesma
   linha do texto anterior. Corrigido reescrevendo o item em dois
   tokens curtos separados por espaço quebrável ("pasta `docs`,
   arquivo `AUDITORIA_MATERIAL_SUPLEMENTAR.md`").

Cada correção foi verificada com uma rodada completa de geração e
inspeção antes da seguinte. Para permitir a geração do PDF antes do
merge (`workflow_dispatch` não alcança um workflow novo que ainda não
existe na branch padrão), a branch de trabalho foi incluída
temporariamente no `push` trigger a cada ciclo de teste e revertida
logo em seguida, em commits separados — cinco inclusões e cinco
reversões ao todo, registradas no histórico de commits desta branch.
O comportamento final do workflow (Seção 8) é idêntico ao de
`artigo_pdf.yml`: dispara só em `main` ou por `workflow_dispatch`
manual.

**Inspeção final, página por página (13/13):**

- Página 1: título, identificação do artigo-fonte, convenções de
  exibição e nota de hash canônico, íntegros.
- Páginas 1–2: sumário (S1–S16, título, trilha), sem lacuna, sem S17.
- Páginas 2–13: as 16 tabelas, cada uma com título, nota de fonte
  completa e legível, e conteúdo tabular sem sobreposição, sem corte
  horizontal, com cabeçalhos repetidos ao quebrar página (S1, longa o
  bastante para isso) e sem página em branco.
- Símbolos ρ e λ renderizam corretamente na nota e no subtítulo da
  Tabela S13.
- Última página (13): lista de proveniência completa, sem corte,
  terminando no item que remete a esta auditoria.
- Nenhum conteúdo identificável de chamado individual (ID, título ou
  descrição livre) em nenhuma página — as únicas colunas de texto
  livre são nomes de categoria da taxonomia, não de chamados.

## 10. Regeneração do PDF principal

O artigo (`04_artigo/artigo_classificacao_chamados_v3.md`) foi
alterado nesta rodada (duas chamadas de tabela renumeradas). O PDF foi
regenerado pelo procedimento oficial já existente
(`artigo_pdf.yml`, `workflow_dispatch` na própria branch, run
[`31922342255`](https://github.com/adinailson88/classificacao-chamados/actions/runs/31922342255)),
sem qualquer edição ao workflow.

**21 páginas**, dentro da faixa 21–23 exigida. Inspeção visual real
(renderização em PNG a 150 dpi via PyMuPDF/`fitz`) confirmou:

- As duas chamadas alteradas renderizam corretamente: "Tabela S15" na
  página 10 (Subseção 4.3, calibração) e "Tabela S16" na página 13
  (Subseção 4.5, Fase 2C).
- Título, Resumo, Abstract, Introdução, Figura 1 e Tabela 1 (páginas
  1–5) íntegros, sem quebra de layout.
- Lista de Considerações Finais e transição para Referências (página
  16) e Apêndice A / Tabelas A2–A3 (página 21) preservados, sem título
  órfão nem página vazia.
- Nenhuma alteração indevida no restante do artigo — apenas os dois
  números de tabela mudaram.

## 11. Validações obrigatórias

```text
python -m unittest discover -s tests   # 767 testes, OK
python -m py_compile src/*.py tests/*.py   # sem erro
python src/matriz_proveniencia.py      # 0 divergências, hash 1e4762438a7e confirmado
```

- **hash_corpus preservado:** `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`, confirmado em todos os artefatos derivados (20 ocorrências na saída da matriz de proveniência), 0 divergências.
- **Nenhum número legado** localizado no artigo (0 ocorrências).
- **`docs/dados/matriz_proveniencia.json` e `docs/MATRIZ_PROVENIENCIA.md`:** único campo alterado é `gerado_em` (executado duas vezes nesta rodada, uma após a renumeração do código e outra ao final; ambas as vezes apenas o carimbo de data/hora mudou).
- **Exatamente 16 CSVs suplementares** em `04_artigo/figuras/`, sequência contínua `tabela_S1_*.csv` a `tabela_S16_*.csv`.
- **Ausência de `tabela_S17_*`:** confirmado (`ls 04_artigo/figuras/tabela_S17*` vazio).
- **Ausência de referência textual a "Tabela S17"** no artigo: confirmado por busca direta (só restam "Tabela S15" e "Tabela S16").
- **Ausência da antiga tabela legada S4** (`tabela_S4_holdout_vs_kfold.csv`): confirmado, não recriada.
- **Corpo científico do artigo:** 8.961 palavras pela rotina histórica (`str.split()` entre `**1. INTRODUÇÃO**`, inclusive, e `**REFERÊNCIAS**`, exclusive) — inalterado frente ao início da rodada, dentro da faixa-meta de 8.850–9.000.
- **44 referências bibliográficas:** preservadas — nenhuma edição foi feita à lista de referências ou a qualquer citação no corpo além das duas chamadas de tabela.

## 12. Confirmação expressa

```text
Zero retreinamentos.
Zero fits de modelos-base.
Zero fits de stacking.
Zero execuções de LSTM ou BERTimbau.
Zero alterações em planilha, corpus, rótulos, grupos, partições ou resultados canônicos.
Nenhum merge realizado.
PR aberta como draft, não marcada como pronta para revisão.
```

Todas as 16 tabelas do suplemento reproduzem, sem recálculo, artefatos
já existentes no repositório antes desta rodada (rodada canônica,
execuções legadas pré-congelamento, experimento exploratório do
BERTimbau ou manifesto confirmatório da Fase 2C, conforme a trilha de
cada uma — Seção 5). A única execução de código nesta rodada foi
`python src/matriz_proveniencia.py`, que é somente leitura e não
recalcula nenhum resultado do experimento.

## Proveniência

- Script de renumeração: `git mv`, manual, um comando por arquivo, em
  ordem decrescente de número.
- Hashes: `sha256sum`, antes e depois de cada `git mv`.
- Nenhuma escrita foi realizada na planilha viva.
- Nenhum artefato de dados canônico (`docs/dados/*.json` da rodada
  `1e476243`) foi alterado; os únicos JSONs tocados foram
  `docs/dados/matriz_proveniencia.json` (campo `gerado_em`, duas
  vezes) e os PDFs gerados pelos workflows oficiais.
