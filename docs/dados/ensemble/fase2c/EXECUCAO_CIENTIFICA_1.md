# Fase 2C — Execução Científica 1 — resultados congelados

> Registro factual e curto. Não contém texto bruto, ID bruto de chamado
> nem conteúdo da spreadsheet privada. Números completos, hash a hash e
> fold a fold, em `fase2c_execucao_cientifica_1_manifest.json` neste
> diretório e no Release de preservação.

## Proveniência

- **Input:** Release `ensemble-fase2b-execucao-cientifica-1`, asset
  `fase2b-resultado-cientifico-run31556028058.zip`
  (SHA-256 `8cd0c2df97257bdc003beb6a2912de3350a4ff7a0689b480bd4c4be946c2f6d1`).
- **Fonte primária:** run `31556028058`, artifact `fase2b-resultado-cientifico`,
  commit produtor `d6a5504cd9c4360b97fd90dd88c13bd430155459` (Execução
  Científica 1 da Fase 2B).
- **Código executado:** commit `b3e14af869f76484df9f61911a5a8e1017e74633`,
  branch `feat/ensemble-fase2c-combinacao`.
- **Proveniência confirmada** (`--somente-validar-proveniencia`, 5 hashes
  científicos batendo exatamente): `input_bundle_sha256`,
  `inner_predictions_canonical_sha256`, `outer_predictions_canonical_sha256`,
  `crossfit_manifest_sha256`, `fase2b_science_sha256` — ver manifesto para
  os valores.

## Universo e alvo

- **Universo modelável:** 13.970 registros (`H` dentro do espaço de classes `C`).
- **`Y=1` modelável:** 593.
- **`K_f` (fila natural do LinearSVC cross-fitted por dobra):** fold 1 = 564,
  fold 2 = 560, fold 3 = 616, fold 4 = 507, fold 5 = 593 — **total 2.840**.
- **`Y=1` por dobra:** fold 1 = 124, fold 2 = 95, fold 3 = 135, fold 4 = 113,
  fold 5 = 126 — soma 593.

**Nota sobre 2.849/595:** um diagnóstico anterior havia informado
`K_f` = 567/563/621/508/590 (total 2.849) e `Y=1` = 595 como valores
"esperados". Esses números vêm de um LinearSVC **standalone** de outra
trilha (`docs/dados/retreino_canonico_predicoes.csv`, execução canônica do
artigo principal, hash `1e476243…`), sobre o universo de 13.972 registros
— incluindo 2 registros com `H` fora de `C` que nunca passam por nenhum
dos sete modelos-base e nunca podem aparecer em nenhuma fila da Fase 2C.
Não são os valores confirmatórios desta execução. Resolução completa,
registrada **antes** da leitura de qualquer resultado comparativo, em
[`../../../FASE2C_RESOLUCAO_KF_DENOMINADOR.md`](../../../FASE2C_RESOLUCAO_KF_DENOMINADOR.md).

## Alpha da votação suave por fold

| Fold | α |
|---:|---:|
| 1 | 5 |
| 2 | 20 |
| 3 | 20 |
| 4 | 20 |
| 5 | 20 |

Selecionado exclusivamente por validação interna (pool `inner` do próprio
outer fold), critério congelado: maior precisão da carga de referência →
maior recall → menor log-loss multiclasse → maior α no empate.

## Resultado agregado (capacidade `K_f` = 2.840, denominador `Y=1` = 593)

| Método | Total na fila | `Y=1` capturados | Precisão | Recall |
|---|---:|---:|---:|---:|
| LinearSVC (baseline) | 2.840 | 523 | 0,1842 | 0,8820 |
| Votação majoritária | 2.840 | 516 | 0,1817 | 0,8702 |
| Votação suave ponderada | 2.840 | 503 | 0,1771 | 0,8482 |
| Stacking | 2.840 | 512 | 0,1803 | 0,8634 |

### Diferença versus LinearSVC

| Método | Δ capturados (abs.) | Ganho relativo | Δ precisão | Δ recall |
|---|---:|---:|---:|---:|
| Votação majoritária | −7 | −1,34% | −0,0025 | −0,0118 |
| Votação suave ponderada | −20 | −3,82% | −0,0070 | −0,0337 |
| Stacking | −11 | −2,10% | −0,0039 | −0,0186 |

**Os três métodos de combinação tiveram desempenho pior que o baseline
LinearSVC isolado nesta capacidade, nesta execução.** Nenhum método foi
alterado, nem pesos/alpha/tau foram reabertos, depois de ver este
resultado — a extração seguiu diretamente da execução já concluída e da
resolução de proveniência registrada antes da leitura.

## Resultado por outer fold

| Fold | `K_f` | LinearSVC (Y1 / precisão / recall) | Majoritária | Suave | Stacking |
|---:|---:|---|---|---|---|
| 1 | 564 | 104 / 0,1844 / 0,8387 | 102 / 0,1809 / 0,8226 | 97 / 0,1720 / 0,7823 | 101 / 0,1791 / 0,8145 |
| 2 | 560 | 85 / 0,1518 / 0,8947 | 85 / 0,1518 / 0,8947 | 82 / 0,1464 / 0,8632 | 82 / 0,1464 / 0,8632 |
| 3 | 616 | 119 / 0,1932 / 0,8815 | 117 / 0,1899 / 0,8667 | 118 / 0,1916 / 0,8741 | 123 / 0,1997 / 0,9111 |
| 4 | 507 | 102 / 0,2012 / 0,9027 | 100 / 0,1972 / 0,8850 | 98 / 0,1933 / 0,8673 | 98 / 0,1933 / 0,8673 |
| 5 | 593 | 113 / 0,1906 / 0,8968 | 112 / 0,1889 / 0,8889 | 108 / 0,1821 / 0,8571 | 108 / 0,1821 / 0,8571 |

`recall` por dobra usa como denominador o `Y=1` real daquela dobra (coluna
"Y=1 por dobra" acima). Único ponto de melhora local: stacking supera o
LinearSVC no fold 3 (123 vs. 119 capturados); em todos os outros folds e
métodos, o LinearSVC iguala ou supera as combinações.

## Verificação e reprodutibilidade

- Resultado agregado e por fold extraídos por **duas vias independentes**:
  o `fase2c_resumo_confirmatorio.json` gravado pelo próprio CLI durante a
  execução, e um script isolado que recomputa tudo a partir das filas JSON
  completas — concordância exata entre as duas.
- `K_f`/`Y=1` também confirmados por duas vias independentes (função do
  módulo + script direto sobre `outer_scores.npz`), concordância exata.
- Hashes físicos SHA-256 dos 13 arquivos de saída + o manifesto:
  ver `fase2c_execucao_cientifica_1_manifest.json`.

## Preservação

- **Release:** [`ensemble-fase2c-execucao-cientifica-1`](https://github.com/adinailson88/classificacao-chamados/releases/tag/ensemble-fase2c-execucao-cientifica-1)
  (pre-release, não marcado como latest), target no commit de resolução
  metodológica `e8fb4373ef496c1aa3a3e26b6a5b4b7618dffd0d`.
- **Assets:** `fase2c-resultado-cientifico-1.zip` (14 arquivos: os 13
  outputs científicos + o manifesto; SHA-256
  `a38a0e78d6de20b1b6e0ad826f0734137b5d3dfb6f17ddd30b6714ecd20d4e03`,
  verificado por novo download e recálculo após a publicação) e
  `fase2c_execucao_cientifica_1_manifest.json` isolado.
- Filas completas e curvas de ganho completas **não** entram no histórico
  Git — só o resumo agregado e o manifesto de hashes (este diretório) mais
  o Release acima.

## Declaração explícita

- **Fits de modelos-base executados: 0.** Nenhum dos sete modelos-base foi
  retreinado; a Fase 2C consumiu exclusivamente as previsões `inner`/`outer`
  já publicadas pela Execução Científica 1 da Fase 2B.
- **Fits de meta-modelo de stacking: 5.** Um `LogisticRegression` por outer
  fold, treinado somente no pool `inner` daquele fold.
- **LSTM executada: não.**
- **`tau` confirmatório: nenhum.** A comparação usa capacidade `K_f`
  (mesma fila natural do LinearSVC, idêntica para os quatro métodos), nunca
  um limiar otimizado na avaliação externa.

Esta rodada não altera o artigo/capítulo e não decide se o ensemble entra
no corpo principal, no suplemento, ou é descartado — essa decisão é da
auditoria independente (ChatGPT) sobre estes resultados.
