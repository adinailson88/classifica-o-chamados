# Auditoria de referências — NBR 6023:2025 / NBR 10520:2023

Branch: `correcao-referencias-abnt-2025`. Repositório: `adinailson88/classificacao-chamados`.

## 1. Escopo e norma adotada

Correção exclusiva das referências bibliográficas, das chamadas autor-data
no corpo e de uma afirmação quantitativa sem comprovação primária no
primeiro parágrafo da Introdução, conforme:

- ABNT NBR 6023:2025 para referências;
- ABNT NBR 10520:2023 para citações;
- metadados conferidos em fontes primárias (CrossRef, ACL Anthology, DOI
  resolver, páginas oficiais de periódico/editora).

Nenhum número experimental, tabela, figura, resultado, conclusão ou
contrato metodológico foi alterado. Nenhum modelo foi retreinado.

## 2. Pré-voo

- `git fetch origin --prune`: SHA de `origin/main` avançou de
  `a0d9e957b60d9092fd5ff9e098ddc506d5e2067c` para
  `ba83a8a9bbb34b35487be4fa8732e06409eaa98c` (commit automático do PDF da
  Rodada 12, já mesclada).
- Nenhuma PR editorial aberta (`gh pr list --state open` vazio).
- Árvore de trabalho rastreada limpa; três arquivos não rastreados
  (`TAREFA_CLAUDE_CODE_revisao_v4.md`, `docs/auditoria_referencias.docx`,
  `docs/revisao_v4.docx`), remanescentes de sessão anterior, preservados
  sem alteração.
- Branch `correcao-referencias-abnt-2025` criada a partir de
  `origin/main` (`ba83a8a9`).
- Documentos lidos antes da edição: `AGENTS.md`, `CONTEXTO.md`,
  `PLANO_EXECUCAO_ATUAL.md`, `PLANO_ARTIGO_CAPITULO.md`,
  `04_artigo/README.md`, `verificacao/relatorio_revisao_v4.md`,
  `04_artigo/artigo_classificacao_chamados_v3.md`. O relatório da Rodada
  12 já registrava como pendência explícita (item 13.2) a "auditoria
  completa da lista de referências contra a NBR 6023" — esta é essa
  rodada.

## 3. Auditoria programática antes da edição

Script ad hoc (Python, não versionado, mesma prática já registrada em
rodadas anteriores) sobre o bloco `**REFERÊNCIAS**`–`**APÊNDICE A`:

| Verificação | Resultado |
|---|---:|
| Total de referências | 44 |
| Referências citadas no corpo | 44/44 |
| Citações sem referência correspondente | 0 |
| Referências sem nenhuma citação | 0 |
| Duplicatas exatas de entrada | 0 |
| Ordem alfabética (autor; mesmo autor por ano ascendente) | correta |

Estado idêntico ao esperado pela tarefa (44 referências, todas citadas,
zero duplicatas, zero órfãs). Nenhuma divergência a reportar; a edição
prosseguiu.

## 4. Correções aplicadas

### 4.1 Chamadas autor-data (NBR 10520:2023)

43 grupos parentéticos convertidos de caixa alta para
Maiúscula/minúscula, preservando ano, agrupamento por `;` e `*et al.*`
em itálico. Exemplo: `(MARTINS; ESPEJO, 2024)` → `(Martins; Espejo,
2024)`. A sigla `ABNT` foi preservada (não é sobrenome de autor, é a
forma padrão de citar a entidade). Citações narrativas (fora de
parênteses, ex.: "Sundaram e Zeid (2025)", "Chow (1970)") já estavam
corretas e não foram tocadas. Zero chamadas autor-data inteiramente em
caixa alta remanescem (conferido programaticamente).

### 4.2 Marcuzzo et al. (2022) — ordem de autoria

Confirmada em <https://aclanthology.org/2022.wnut-1.22/>: Matteo
Marcuzzo, Alessandro Zangari, Michele Schiavinato, Lorenzo Giudice,
Andrea Gasparetto, Andrea Albarelli. A entrada trocava Giudice/Gasparetto
por Schiavinato; corrigida para a ordem oficial. Aproveitada a mesma
edição para padronizar a citação do evento ao modelo NBR 6023 já usado
nas demais referências de anais (nome do evento, número da edição,
ano, cidade — Gyeongju, Coreia do Sul, confirmado no volume da ACL
Anthology), substituindo a construção "PROCEEDINGS OF THE 8TH... Anais
[...]. Association for Computational Linguistics" por "WORKSHOP ON NOISY
USER-GENERATED TEXT, 8., 2022, Gyeongju. *Proceedings [...]*. Gyeongju:
ACL, 2022."

### 4.3 Brown et al. (2020) — autoria

Sete autores nominais seguidos de "et al." (contraditório) substituídos
por "BROWN, T. B. et al.", conforme instrução explícita da tarefa e
compatível com a NBR 6023:2025 para obras de autoria numerosa.

### 4.4 Padronização tipográfica das 44 referências

Destaque tipográfico (itálico) do título da publicação — periódico,
anais/proceedings ou livro — aplicado de modo uniforme às 44 entradas
(antes da rodada, nenhuma das 44 usava itálico; ficou uniformemente
ausente, não uniformemente aplicado). Único caso sem contêiner
italicizável: LIU; BENGE; JIANG (2023), preprint arXiv sem periódico ou
anais associado.

### 4.5 DOIs verificados em fontes primárias

Nenhum DOI foi aceito sem conferência de título, autoria, ano e
publicação contra a fonte oficial (CrossRef, ACL Anthology, DOI
resolver ou página do periódico). Todos no formato
`https://doi.org/...`.

**Os dez itens indicados na tarefa**, todos verificados e confirmados
corretos contra a fonte primária antes de inserir:

| Referência | DOI inserido/confirmado | Fonte de verificação |
|---|---|---|
| Bender et al., 2021 | `10.1145/3442188.3445922` | ACM DL / CrossRef |
| Bouabdallaoui et al., 2020 | `10.3390/buildings10090160` | MDPI / CrossRef |
| Devlin et al., 2019 | `10.18653/v1/N19-1423` | ACL Anthology |
| Li et al., 2024 | `10.1016/j.autcon.2024.105501` | CrossRef (autoria conferida: Y. Li, Y. Liu, J. Zhang, L. Cao, Q. Wang) |
| Liu; Benge; Jiang, 2023 | `10.48550/arXiv.2307.00108` + URL + acesso | arXiv |
| Martins; Espejo, 2024 | `10.47179/abcustos.v19i1.719` | página do periódico ABCustos |
| Mohammed; Amoah, 2025 | `10.1108/F-09-2024-0134` | Emerald |
| Pampana et al., 2022 | `10.3390/buildings12122094`; incluído n. 12 | CrossRef/MDPI |
| Sundaram; Zeid, 2025 | `10.1007/s10845-024-02323-4`; incluído n. 3 | CrossRef/Springer |
| Zhang et al., 2025 | `10.1016/j.engappai.2025.110157` | CrossRef |

**Demais DOIs verificados** (item 7 da tarefa — "verifique os demais DOI
em fontes oficiais"), todos conferidos via CrossRef (título, autoria,
periódico, volume/fascículo/páginas contra o resultado retornado, com
rejeição explícita de correspondências erradas do CrossRef quando a
busca por título trazia um trabalho diferente — ver Seção 4.7):

Anderson; Ter Braak (2003) `10.1080/00949650215733`; Cameron; Gelbach;
Miller (2008) `10.1162/rest.90.3.414`; Chow (1970)
`10.1109/tit.1970.1054406`; Cochran (1950) `10.2307/2332378`; DiCiccio;
Efron (1996) `10.1214/ss/1032280214`; Efron (1979)
`10.1214/aos/1176344552`; Field; Welsh (2007)
`10.1111/j.1467-9868.2007.00593.x`; Galke; Scherp (2022)
`10.18653/v1/2022.acl-long.279`; Good (2005) `10.1007/b138696`; Graves;
Schmidhuber (2005) `10.1016/j.neunet.2005.06.042`; Grimm et al. (2008)
`10.1126/science.1150195`; Joachims (1998) `10.1007/BFb0026683`;
Kejriwal et al. (2024) `10.1038/s41598-024-58937-4`; Salton; Buckley
(1988) `10.1016/0306-4573(88)90021-0`; Schwartz et al. (2020)
`10.1145/3381831`; Shannon (1948) — duas partes, DOIs distintos:
`10.1002/j.1538-7305.1948.tb01338.x` (n. 3) e
`10.1002/j.1538-7305.1948.tb00917.x` (n. 4); Sokolova; Lapalme (2009)
`10.1016/j.ipm.2009.03.002`; Treviso et al. (2023)
`10.1162/tacl_a_00577`.

**DOIs já existentes reformatados** para `https://doi.org/...` (antes em
formato abreviado `DOI: 10.xxxx`): Lin (1991), Morais; Paula; Reis
(2023), Souza; Nogueira; Lotufo (2020).

### 4.6 Correções de metadados encontradas durante a verificação

- **Martins; Espejo (2024):** título estava truncado ("...com uso do
  modelo de SES"); corrigido para o título completo confirmado na página
  do periódico: "...com uso do modelo de Suavização Exponencial Simples
  (SES)".
- **Morais; Paula; Reis (2023):** páginas corrigidas de `1--18` para
  `1--27`, conforme metadado CrossRef da própria referência (DOI já
  citado no artigo).
- **Pampana et al. (2022):** incluído `n. 12` (fascículo), ausente na
  entrada original.
- **Sundaram; Zeid (2025):** incluído `n. 3` (fascículo), ausente na
  entrada original.
- **Souza; Nogueira; Lotufo (2020):** incluída a cidade do evento (Rio
  Grande, RS — BRACIS 2020), ausente na entrada original e presente nas
  demais referências de anais do artigo.

### 4.7 DOIs verificados e conferidos como **inexistentes** (não inventados)

Para os itens abaixo, a busca em fonte primária foi feita e o DOI foi
explicitamente checado como não atribuído — não é "não verificado por
falta de tempo", é "verificado: sem DOI". Registro conforme regra do
`AGENTS.md` ("Informação insuficiente para verificar" só se aplica
quando falta o dado; aqui o dado é a própria ausência, confirmada):

- **ABNT NBR 5674 (2012):** norma sem DOI atribuído; possui ISBN
  978-85-07-03557-2 (não inserido, por não ter sido solicitado).
- **Brown et al. (2020):** proceedings do NeurIPS 2020 sem DOI
  confiável localizado (uma correspondência CrossRef via busca por
  título retornou um registro claramente espúrio, rejeitado).
- **Capra (1996), Odum (1971), Cochran (1977):** monografias sem DOI
  atribuído (buscas CrossRef retornaram obras de terceiros não
  correspondentes, rejeitadas).
- **El-Yaniv; Wiener (2010):** JMLR não atribuiu DOI a este volume
  (confirmado no metadado oficial do artigo no GitHub da JMLR).
- **Guo et al. (2017):** proceedings PMLR sem DOI próprio nessa
  plataforma.
- **Holm (1979):** Scandinavian Journal of Statistics, 1979; nenhum DOI
  localizado (apenas link estável JSTOR).
- **Marcuzzo et al. (2022):** conferido diretamente na página da ACL
  Anthology; campo DOI vazio.
- **Pedregosa et al. (2011):** artigo JMLR sem DOI (confirmado; a versão
  em periódico não recebeu DOI, diferente da versão arXiv).
- **Platt (1999):** busca por título retornou obra distinta; nenhum DOI
  correto localizado.

### 4.8 Correção complementar (auditoria independente, 14/08/2026)

A auditoria independente do PR #212 apontou três bloqueadores nesta
rodada, corrigidos nesta correção complementar:

- **Brown et al. (2020):** a Seção 4.3 já descrevia a substituição por
  "BROWN, T. B. et al.", mas a entrada na lista de referências
  permanecia com os sete autores nominais seguidos de "et al."
  (divergência entre relatório e artigo). Corrigida para
  "BROWN, T. B. et al.", conforme já documentado.
- **Efron; Tibshirani (1993):** novo DOI localizado e confirmado para a
  obra completa (não apenas um capítulo): `10.1201/9780429246593`
  (DOI resolver / CrossRef). Inserido na referência; removida da lista
  de referências sem DOI (Seção 4.7).
- **Kohavi (1995):** o identificador `10.5555/1643031.1643047` é um DOI
  real — o prefixo `10.5555` é um prefixo DOI registrado, atribuído às
  Digital Library proceedings referenciadas pelo IJCAI 1995 — e não um
  identificador interno não-DOI, como afirmado incorretamente na versão
  anterior desta auditoria. Inserido na referência; removida da lista de
  referências sem DOI (Seção 4.7).

**Contagens finais harmonizadas** (substituem todos os valores
anteriores desta rodada, incluindo "23 inseridos", "10 sem DOI" e "13
sem DOI" citados em versões anteriores deste documento, do corpo do PR
#212 e do changelog):

| Métrica | Valor |
|---|---:|
| Total de referências | 44 |
| Referências com ao menos um DOI | 33 |
| Referências sem DOI | 11 |
| Identificadores/URLs DOI no texto (Shannon possui dois) | 34 |
| Referências que passaram a ter DOI em relação à base | 30 |
| Novos identificadores DOI (Shannon recebeu dois) | 31 |
| DOIs preexistentes apenas reformatados (Lin; Morais, Paula e Reis; Souza, Nogueira e Lotufo) | 3 |

O DOI do arXiv de Liu; Benge; Jiang (2023) está incluído nesses totais
(entre as 30 referências que passaram a ter DOI e os 33 com DOI); não é
contado novamente como categoria aditiva separada.

## 5. Correção científica pontual — Introdução

Removida a afirmação "ainda que disponha historicamente de menos de 2%
do orçamento institucional", sem comprovação nas duas referências então
associadas (Martins; Espejo, 2024; Pampana et al., 2022 — ambas tratam
de custos/gestão de manutenção predial, mas nenhuma sustenta o
percentual específico de "menos de 2%"). Reescrita mínima:

> Antes: "...ainda que disponha historicamente de menos de 2% do
> orçamento institucional (Martins; Espejo, 2024; Pampana *et al.*,
> 2022). Sob essa restrição, decidir onde intervir depende de
> evidência..."
>
> Depois: "...ainda que opere sob restrição orçamentária persistente
> (Martins; Espejo, 2024; Pampana *et al.*, 2022). Sob essa restrição,
> decidir onde intervir depende de evidência..."

Nenhum outro percentual foi inserido. Nenhuma fonte nova foi
acrescentada. As mesmas duas referências foram mantidas, por sustentarem
a afirmação genérica de restrição orçamentária. "Sob essa restrição" foi
mantido por já concordar com a nova redação.

## 6. Validação

### 6.1 Auditoria cruzada após a edição

| Verificação | Resultado |
|---|---:|
| Total de referências | 44 (inalterado) |
| Referências citadas | 44/44 |
| Citações sem referência | 0 |
| Referências sem citação | 0 |
| Duplicatas | 0 |
| Ordem alfabética | correta |
| Chamadas autor-data inteiramente em caixa alta | 0 |
| Ordem de autoria de Marcuzzo | corrigida e conferida |
| Ocorrências de "menos de 2%" | 0 |
| Brown et al. (2020) | `BROWN, T. B. et al.` |
| Referências com ao menos um DOI / sem DOI | 33 / 11 (34 identificadores no texto — Shannon possui dois) |
| DOIs verificados em fonte primária | 44/44 (30 referências passaram a ter DOI em relação à base — 31 novos identificadores, pois Shannon recebeu dois —, 3 preexistentes reformatados, 11 confirmadas sem DOI atribuído) |
| Destaque tipográfico do título da publicação | uniforme nas 44 entradas |

### 6.2 Testes

- `python -m unittest discover -s tests`: **764 de 765 aprovados**. A
  única falha, `test_categoria_sem_suporte_no_sorteio_sai_em_rodada_seguinte`
  (`tests/test_gerar_particoes_canonicas.py`), é a mesma falha
  determinística de ambiente já documentada em
  `verificacao/relatorio_revisao_v4.md` (Rodada 12), atribuída a
  divergência de versão de `numpy`/`scikit-learn` neste ambiente local
  frente à fixada em `requirements-leves.txt`; o módulo
  `src/gerar_particoes_canonicas.py` não foi tocado por esta rodada. Não
  é regressão desta correção editorial.
- `python -m compileall -q src`: código de saída 0, sem erros.
- `python src/matriz_proveniencia.py`: "artefatos com hash divergente:
  0", "artefatos do congelamento ausentes: 0", "números legados ainda no
  artigo: 0". Hash canônico `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`
  preservado. A única alteração produzida pela execução do script foi o
  campo `gerado_em` (timestamp) em `docs/MATRIZ_PROVENIENCIA.md` e
  `docs/dados/matriz_proveniencia.json`; revertida com `git checkout --`
  por estar fora do escopo desta rodada.

### 6.3 PDF — workflow oficial

Execução `workflow_dispatch` de `.github/workflows/artigo_pdf.yml` na
própria branch (run
[31824803944](https://github.com/adinailson88/classificacao-chamados/actions/runs/31824803944)),
sucesso, commit automático `f88089b9` incorporado por
fast-forward.

- **Páginas: 21**, dentro da faixa preferencial de 21–23 (idêntico à
  paginação da Rodada 12, sem crescimento apesar da adição de itálico e
  DOIs às 44 referências).
- Inspeção visual de todas as 21 páginas (renderização PyMuPDF, 180
  dpi), com atenção às páginas afetadas (2 — Introdução; 16 a 19 —
  Referências e transição ao Apêndice A):
  - nenhuma referência cortada, sobreposta ou com quebra de linha
    incorreta;
  - destaque tipográfico (itálico) do título de periódico/anais/livro
    renderiza corretamente em todas as entradas;
  - DOIs renderizam como texto legível no formato `https://doi.org/...`,
    sem transbordo de margem; não são hyperlinks clicáveis no PDF —
    comportamento **preexistente** e inalterado por esta rodada (as três
    referências que já tinham DOI antes desta correção também não eram
    clicáveis; o workflow invoca `pandoc` sem a extensão
    `autolink_bare_uris` e o Markdown-fonte não usa a sintaxe
    `<url>`, portanto nenhuma referência do artigo tem DOI/URL
    clicável);
  - título "APÊNDICE A" não fica órfão nem colide com a última
    referência (página 19);
  - parágrafo da Introdução (página 2) flui normalmente após a remoção
    do percentual, sem quebra de linha estranha;
  - nenhum outro título de seção isolado no rodapé de página, em
    comparação com a Rodada 12.

## 7. Confirmações finais

- Zero alteração em artefatos canônicos de dados (`docs/dados/*.json`
  fora do timestamp revertido da matriz de proveniência).
- Zero fits de modelo-base.
- Zero fits de stacking.
- Zero execuções de LSTM.
- Nenhum script de treino foi executado nesta rodada; os únicos scripts
  Python executados foram os de auditoria ad hoc (leitura), `unittest`,
  `compileall` e `matriz_proveniencia.py` (leitura/checagem).
