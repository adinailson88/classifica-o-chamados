# Fase 2C — combinação dos sete modelos-base: proveniência e contrato

> Documento de infraestrutura/proveniência/contrato. Não contém texto bruto,
> ID bruto de chamado nem conteúdo da spreadsheet privada. Não recalcula
> corpus, R, Y, H, folds/partições, os sete modelos-base, hiperparâmetros ou
> critérios de comparação da Fase 2B — consome exclusivamente os artefatos já
> aprovados da Execução Científica 1.

## 1. Por que este desenho existe

A Fase 2B produziu, para os 13.970 registros com `H` dentro do espaço de
classes `C`, previsões de sete modelos-base em dois regimes: internas
(`inner`, cross-fitted, leakage-free, usadas como meta-features) e externas
(`outer`, out-of-fold, usadas como avaliação final). A Fase 2C combina essas
previsões — nunca retreina os sete modelos-base — para produzir um escore de
prioridade por chamado: quão fortemente o ensemble sugere que a categoria
histórica `H_i` está desatualizada em relação à referência humana `R_i`.

Alvo, já congelado e nunca recalculado aqui:

```
Y_i = 1(H_i != R_i)
```

## 2. Proveniência auditada da Execução Científica 1

**Run:** `31556028058` · **commit:** `d6a5504cd9c4360b97fd90dd88c13bd430155459`
(`[FASE2B-RUN] execução científica 1 pós-controle de determinismo`).

**Artifact:** `fase2b-resultado-cientifico`, contendo:

| Arquivo | Conteúdo |
|---|---|
| `fase2b_manifesto.json` | ordem das 41 classes, lista dos 7 modelos, rotações internas por fold, contadores de fits |
| `fase2b_resumo.json` | os 5 hashes científicos + `hashes_entrada_gate_zero` (os 5 hashes metodológicos de `ensemble_fase2b_crossfit.HASHES_ESPERADOS`) + contadores estruturais |
| `fase2b_hashes.json` | os mesmos 5 hashes científicos, isolados |
| `fase2b_proveniencia_run.json` | `run_id`, `commit_sha`, mensagem do commit |
| `fase2b_inner_scores.npz` | 391.160 previsões internas (7 modelos × 4 rotações × 13.970 registros, distribuídas de forma desigual por outer fold) |
| `fase2b_outer_scores.npz` | 97.790 previsões externas (7 modelos × 13.970 registros) |

Baixado e auditado nesta rodada via `gh run download 31556028058 -R
adinailson88/classificacao-chamados -n fase2b-resultado-cientifico`.

**Hashes de saída confirmados (comparação byte a byte com o artifact
baixado):**

```
input_bundle_sha256                 = a533e245d97482f423bb9981df350ad6ec550133a2253c3a5f528f086459e83f
inner_predictions_canonical_sha256  = 98e38ea42236210ba430ed322b5872062e7ac0eba2ec3d64d06566b11802b0d1
outer_predictions_canonical_sha256  = 660d3f451040615a08bac1934f6ac157ac0052b5c98fe7890508c9e064d61e6d
crossfit_manifest_sha256            = 5e9c8cd975017867b96dcf543b90ad90c7ec989939ad934cca5dd175c32179e3
fase2b_science_sha256               = 931c8092e372d6d416b0763bc55bfd74c856aeb1cf4c321dd55081ea16d82470
```

Essas 5 constantes ficam pinadas em
`src/ensemble_fase2c_combinacao.py::HASHES_EXECUCAO_1_ESPERADOS`.
`inner_predictions_canonical_sha256`/`outer_predictions_canonical_sha256`
foram **recomputados** nesta auditoria a partir do conteúdo dos `.npz`
baixados, usando a mesma função de hash da Fase 2B
(`ensemble_fase2b_crossfit.calcular_predicoes_canonical_sha256`, sem
duplicar) — reproduziram exatamente os valores acima. `montar_contexto()`
repete essa mesma checagem em todo carregamento
(`verificar_hashes_recomputados`, ligada por padrão).

### 2.1 Fonte de H, R, Y, grupo e fold — achado não óbvio

`docs/dados/ensemble/alvo_ensemble.json` (o alvo congelado "antigo",
`hash_alvo_ensemble = 76d903c9…`) **não** é o input que a Fase 2B validou.
O Gate Zero da Execução Científica 1 valida contra
`ensemble_fase2b_crossfit.HASHES_ESPERADOS`, cujo `hash_alvo_ensemble` é
`8884d609…` — que corresponde a
`docs/dados/ensemble/recongelamento_online/alvo_ensemble_online.json`.

Auditoria desta rodada (recomputando os 5 hashes a partir do arquivo
`alvo_ensemble_online.json` com o próprio código de produção,
`congelar_alvo_ensemble`/`recongelar_ensemble_online`):

| Hash | Recomputado a partir de `alvo_ensemble_online.json` | Confere com `HASHES_ESPERADOS` |
|---|---|---|
| `hash_corpus` | `fe9bfa4a…` | sim |
| `classes_sha256` | `9e6c742b…` | sim |
| `partition_manifest_online_sha256` | `d38c0416…` | sim |
| `fold_assignment_sha256` | `dc17cfb2…` | sim |
| `hash_alvo_ensemble` | `8884d609…` | sim |

Os campos `H`/`R`/`Y` em si são idênticos entre o alvo antigo e o
recongelado (`h_divergentes`/`r_divergentes`/`y_divergentes` = 0 em
`resumo_recongelamento_online.json`) — a diferença de hash vem de 7
registros cujo `grupo_sha256` mudou (texto alterado após o primeiro
congelamento). Ainda assim, **a Fase 2C usa `alvo_ensemble_online.json`**
(`recongelar_ensemble_online.ALVO_ONLINE_PADRAO`), por ser o único que
reproduz criptograficamente o input real validado pelo Gate Zero da
Execução Científica 1.

Confirmado também, por junção direta com os 97.790 `outer_rows` do artifact:
o conjunto de `id_sha256` de `outer_scores.npz` é **exatamente**
`{id : historico_no_espaco_de_classes = true}` em `alvo_ensemble_online.json`
(13.970 IDs, diferença simétrica = 0), com `outer_fold` idêntico nas duas
fontes em 100% dos casos.

**Nota de ambiente (não é problema de dados):** neste checkout Windows,
`particoes_canonicas_mapa.csv` é lido em disco com `CRLF`
(`core.autocrlf=true`, sem `.gitattributes` fixando `eol=lf`), o que muda o
hash bruto do arquivo (`c58a3865…`) em relação ao que o runner Linux da CI
computou (`6d7d7384…`, o valor armazenado como
`partition_manifest_origem_sha256`). Normalizado para `LF`, os bytes batem
exatamente. Isso não afeta nenhum dos 5 hashes metodológicos nem qualquer
conteúdo de registro — o CSV é sempre lido via `csv.DictReader`, que trata
`CRLF`/`LF` de forma transparente. Fica registrado para não ser confundido
com divergência de dados numa auditoria futura.

### 2.2 Como carregar sem consultar a planilha viva

```
src/ensemble_fase2c_combinacao.py
  carregar_alvo()                    -> H, R, Y, grupo, fold  (alvo_ensemble_online.json)
  carregar_classes()                 -> ordem das 41 classes  (classes_ensemble.json)
  carregar_predicoes_agregadas()     -> inner_rows, outer_rows (os dois .npz)
  validar_proveniencia()             -> compara os 10 hashes (5 entrada + 5 saída) com as constantes pinadas
  verificar_hashes_recomputados()    -> recalcula os hashes das previsões carregadas
  montar_contexto()                  -> orquestra tudo acima + junção por id_sha256/outer_fold/grupo_sha256
```

Nenhuma dessas funções abre a planilha operacional. `montar_contexto()`
bloqueia (`ProveninciaDivergente`/`JuncaoInvalida`) em qualquer divergência,
antes de combinar qualquer previsão.

### 2.3 Onde ficam os `.npz` (risco de retenção)

O workflow publica `fase2b-resultado-cientifico` com `retention-days: 30`.
O run é de 11/08/2026 — o artifact expira por volta de 10/09/2026. Os quatro
JSONs pequenos (`fase2b_manifesto/_resumo/_hashes/_proveniencia_run.json`,
poucos KB, só hashes/contagens/ordem de classes, sem texto/ID) foram
**commitados nesta rodada** em `docs/dados/ensemble/fase2b/` como evidência
permanente. Os dois `.npz` (≈ 72 MB + 18 MB, matrizes de escore de 41
colunas) **não foram commitados** — permanecem `gitignored`
(`docs/dados/ensemble/fase2b/*.npz`), consistente com o padrão já existente
no repositório. Para reobter, antes de 10/09/2026:

```bash
gh run download 31556028058 -R adinailson88/classificacao-chamados \
  -n fase2b-resultado-cientifico -D docs/dados/ensemble/fase2b
```

**Decisão pendente do autor:** commitar os dois `.npz` (bloat permanente de
~90 MB no histórico do Git) ou reexecutar a agregação da Fase 2B a partir
dos artifacts por fold (também sujeitos à mesma retenção) antes da janela
expirar. Nenhuma das duas ações foi tomada nesta rodada.

## 3. Relação entre inner predictions, outer predictions, folds, H, R e Y

- **outer predictions** (97.790 linhas = 7 modelos × 13.970 registros): a
  previsão de cada modelo sobre o outer fold em que o registro caiu,
  treinado nos outros 4 folds — nunca viu o próprio registro nem seu grupo
  textual. É a fonte de avaliação final e dos escores `s_ls`/`s_maj`/
  `s_soft`.
- **inner predictions** (391.160 linhas = 7 modelos × 4 rotações × 13.970,
  distribuídas desigualmente por outer fold): dentro de cada outer fold `f`,
  os registros de `T_f` (as outras 4 partições) recebem previsão de um
  modelo treinado nas 3 partições de `T_f` que não a sua — nunca viu o
  próprio outer fold `f`. É a fonte leakage-free de meta-treino do
  stacking: o meta-modelo do outer fold `f` usa **somente**
  `inner_rows` cujo primeiro campo é `f`, nunca `outer_rows` nem inner
  rows de outro contexto de outer fold.
- **H, R, Y**: não estão nos `.npz` (que só têm `id_sha256`, `grupo_sha256`,
  `outer_fold`, `modelo`, o vetor de 41 escores e o top1) — vêm da junção
  por `id_sha256` com `alvo_ensemble_online.json` (seção 2.1). `Y` nunca é
  usado como feature de nenhum escore, somente como rótulo de avaliação
  (curva Precision-Recall, curva de ganho) e como rótulo de treino do
  meta-modelo de stacking.

## 4. Contrato da Fase 2C

Baseline: LinearSVC. Métodos: votação majoritária, votação suave ponderada,
stacking. Treino (do meta-modelo de stacking; os sete modelos-base não são
retreinados): somente `H_i ∈ C`.

### 4.1 Escores de prioridade

```
s_ls    = max_{c != H_i} p_ls(c) - p_ls(H_i)
s_soft  = max_{c != H_i} S(c) - S(H_i)
s_stack = q_i                                 (P(Y_i=1) pelo meta-modelo)
s_maj   = (v_alt - v_H) / M
```

`S(c|x) = [Σ_m w_{m,c}^(α) · p_m(c|x)] / [Σ_m w_{m,c}^(α)]`, normalizado em
seguida para somar 1 entre as 41 classes — ver 4.2 para `w_{m,c}^(α)`.

`v_H` = votos (top1) em `H_i`; `v_alt` = votos na categoria alternativa
`c_alt`. Desempate de `c_alt`, nesta ordem exata: (1) mais votos; (2) maior
média das probabilidades calibradas da categoria entre os sete modelos; (3)
menor índice na ordem canônica de `classes_ensemble.json`. A fila da
votação majoritária (`montar_fila_majoritaria`) ordena por `v_alt - v_H`
decrescente, depois pela margem de probabilidade média decrescente, depois
por `id_sha256` crescente — **nunca** a ordenação genérica escore+id usada
pelos demais métodos.

Implementado em `escore_linear_svc`, `escore_votacao_majoritaria` +
`escolher_c_alt_majoritario` + `montar_fila_majoritaria`,
`escore_votacao_suave` + `escore_combinado_suave`.

### 4.2 Peso da votação suave — contrato aprovado (auditoria independente)

```
w_{m,c}^(α) = (TP_{m,c} + α·π_c) / (N_{m,c} + α)
```

`TP_{m,c}`/`N_{m,c}` vêm **exclusivamente** das previsões OOF **internas**
(`inner_rows`) do próprio outer fold — nunca da dobra externa: `N_{m,c}`
conta quantas vezes o modelo `m` previu top1 = `c` nesse pool; `TP_{m,c}`,
quantas dessas o `R` do registro também era `c`. `π_c` é a frequência de
`R=c` entre os IDs únicos do mesmo pool interno. Implementado em
`pesos_votacao_suave_regularizados` — a assinatura só aceita
`linhas_inner`/`referencia_por_id`/`classes`/`alpha`, nunca `outer_rows`
nem `scores_outer`/`top1_outer`: impossível vazar a dobra externa para
dentro da estimativa por construção da função, não só por disciplina de
uso.

`α ∈ {5, 20, 100}`, escolhido **exclusivamente por validação interna**
(`selecionar_alpha_votacao_suave`): dentro do pool interno de um outer
fold, cada uma das (até 4) rotações internas vira validação uma vez,
treinando nas demais. Critério de seleção, nesta ordem: (1) maior precisão
da carga de referência (análogo à fila natural já congelada em
`congelar_alvo_ensemble.reproduzir_baseline`, aqui sobre o top1 do escore
combinado `S` em vez do top1 do LinearSVC); (2) maior recall da mesma
carga; (3) menor log-loss multiclasse (`sklearn.metrics.log_loss`, sem
reimplementar); (4) persistindo empate, maior `α`. Pesos e `α` são
recalculados **por outer fold** (`pesos_e_alpha_votacao_suave_por_fold`) —
cada registro usa exclusivamente os pesos do próprio outer fold.

### 4.3 Capacidade `K_f`, não limiar — contrato aprovado

A comparação confirmatória entre métodos usa capacidade, nunca um `τ`
otimizado na avaliação externa:

```
K_f = |B_f^{LSVC}|
```

`B_f^{LSVC}` = fila natural de divergências Top-1 do LinearSVC na dobra
`f` (`previsto_linear_svc != H_i`, o mesmo conceito já congelado no
baseline). Cada método é truncado na **mesma** `K_f` daquela dobra
(`capacidade_linear_svc_por_fold`, `aplicar_capacidade_por_fold`,
`comparar_metodos_por_capacidade`) antes de comparar quantas inadequações
reais (`Y=1`) cada método capturou.

`curva_precisao_recall()` continua disponível como **saída analítica**
(nunca suprimida) e `selecionar_tau()` como **utilitário exploratório**:
nenhum dos dois é chamado por nenhum orquestrador confirmatório
(`combinar_linear_svc`, `combinar_votacao_majoritaria`,
`combinar_votacao_suave`, `combinar_stacking`,
`comparar_metodos_por_capacidade`) — confirmado por teste que substitui
`selecionar_tau` por um espião que levanta exceção se chamado. `max_f1`
**não** é regra vinculante de seleção de limiar; `selecionar_tau` não tem
mais valor padrão de `criterio`, exatamente para que nenhuma chamada seja
implícita.

Terceira escolha, de menor impacto, mantida: o **`c_alt` do stacking**
reaproveita o `c_alt` da votação suave (`combinar_stacking`), porque o
stacking em si só produz `q_i` (um escore escalar), nunca uma categoria
alternativa própria.

### 4.4 Filas de saída

`montar_fila()` (LinearSVC, votação suave, stacking) e
`montar_fila_majoritaria()` (votação majoritária, ordenação dedicada de
4.1) produzem, por método, uma lista com os campos de auditoria do
contrato — `id_sha256`, `H`, `R`, `c_alt`, `score`, `fold` — mais `Y`
(rótulo de avaliação, nunca feature).

### 4.5 Curva de ganho

`curva_ganho()`: para cada tamanho de fila `K` (ordenada por escore
decrescente), quantas inadequações reais (`Y=1`) foram capturadas, com
precisão e recall acumulados — gains chart padrão, não uma métrica nova.

## 5. O que esta rodada implementou e o que não executou

**Implementado e testado** (`src/ensemble_fase2c_combinacao.py`,
`tests/test_ensemble_fase2c_combinacao.py`, 52 testes, dados sintéticos
minúsculos, nenhum fit real, nenhuma leitura de planilha):

- carregamento + validação de proveniência (10 hashes) com bloqueio
  comprovado em dados não oficiais;
- junção H/R/Y/grupo/fold × previsões externas, com bloqueio em
  inconsistência de fold/grupo/modelo faltante;
- os quatro escores de prioridade e seus `c_alt`, incluindo o desempate
  majoritário em três níveis e a ordenação dedicada da fila majoritária;
- pesos regularizados da votação suave por modelo/classe, estimados
  exclusivamente do pool interno por outer fold, com seleção de `α`
  também restrita à validação interna — ambos comprovados por teste
  diferencial (mudar dados que só existem na dobra externa de um fold não
  muda nem os pesos nem o `α` escolhido daquele fold);
- capacidade `K_f` do LinearSVC por dobra, aplicada igualmente a todos os
  métodos, e confirmação de que nenhum orquestrador confirmatório chama
  `selecionar_tau`;
- stacking com meta-modelo por outer fold, leakage-free por construção
  (treino de cada fold usa exclusivamente o pool `inner` daquele fold —
  comprovado por reconstrução independente das features/rótulos esperados
  no teste, não apenas por inspeção do código), bloqueio se um fold não tem
  as duas classes de `Y` no meta-treino;
- fila ordenada, curva Precision-Recall (saída analítica), curva de ganho.

**Não executado nesta rodada, deliberadamente:**

- nenhum dos 175 fits dos sete modelos-base;
- nenhuma execução de LSTM;
- nenhuma combinação real sobre os 13.970 registros da Execução Científica
  1 (a infraestrutura roda contra o `.npz` real via CLI —
  `python src/ensemble_fase2c_combinacao.py --metodo todos` — mas isso não
  foi disparado nesta rodada);
- nenhuma comparação declarada como resultado científico da Fase 2C.

Motivo: item 9 do prompt operacional da rodada anterior — não produzir
análise científica final da Fase 2C nesta etapa de infraestrutura. As duas
escolhas que antes ficavam abertas (peso da votação suave, seleção de
limiar) foram corrigidas nesta rodada pela auditoria independente e agora
são contrato — ver seções 4.2 e 4.3.
