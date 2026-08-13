# Replay congelado da Fase 2B (Execução Científica 1)

> Documento de infraestrutura/proveniência/reprodutibilidade. Não altera
> corpus, R, Y, H, folds/partições, os sete modelos-base, hiperparâmetros ou
> critérios de comparação da Fase 2B. Não contém texto bruto, ID bruto de
> chamado nem conteúdo da spreadsheet privada.

## 1. Problema que este desenho resolve

O teste de determinismo da Fase 2B (comparar uma Execução Científica 2 contra
a Execução Científica 1 aprovada) dependia, até aqui, de reler a planilha
operacional **viva** a cada rodada. Isso funciona como *gate de proveniência*
(detecta se a fonte online ainda bate com o que foi aprovado), mas não serve
como *replay científico*: a fonte viva evolui legitimamente (correções
humanas contínuas), então uma nova leitura nunca é garantidamente idêntica,
byte a byte, ao que a Execução 1 recebeu.

Isso ficou concreto na tentativa de Execução Científica 2 (run `31594961988`,
commit `07bb1969`): o Gate Zero bloqueou porque 4 dos 13.972 registros
tiveram campos textuais preenchidos após a Execução 1 (`titulo_osm`/
`descricao_osm` de um registro; `descricao_glpi` de três outros) — mudança
real na fonte, não falha de leitura.

## 2. Separação de responsabilidades

| | Gate de proveniência (vivo) | Replay científico (congelado) |
|---|---|---|
| Marcador | `[FASE2B-RUN]` | `[FASE2B-REPLAY-PREFLIGHT]` / `[FASE2B-REPLAY]` |
| Função Python | `gate_zero()` — **inalterada** | `gate_zero_replay()` — nova, paralela |
| Fonte dos dados | Planilha operacional, sempre relida | Bundle privado, estático |
| Propósito | Autorizar um *novo* congelamento/baseline | Reproduzir uma execução **já aprovada** |
| Pode produzir nova baseline? | Sim | **Não, nunca** |

As duas nunca rodam na mesma execução — os quatro marcadores de commit
(`[FASE2B-RUN]`, `[FASE2B-CANARY]`, `[FASE2B-REPLAY-PREFLIGHT]`,
`[FASE2B-REPLAY]`) são mutuamente
exclusivos por construção no job `autorizacao` do workflow.

`executar_outer_fold`, `montar_registros_modelaveis`, `agregar_execucao` etc.
recebem um `gate: dict` e não sabem (nem precisam saber) se ele veio de
`gate_zero()` ou `gate_zero_replay()` — zero mudança nelas.

### 2.1 Duas etapas do modo replay: PREFLIGHT → auditoria → REPLAY completo

O modo replay é disparado em **dois marcadores separados**, nunca de uma vez:

1. **`[FASE2B-REPLAY-PREFLIGHT]`** — roda **exclusivamente** `testes` +
   `autorizacao` + `gate_zero_replay` (o job `gate_zero_replay` do workflow
   aceita os dois marcadores). **Não libera `crossfit_fold_replay` nem
   `agregar_replay`** — zero fits, zero LSTM. Serve para validar, isolado e
   barato, que o bundle privado bate com `replay_input_sha256` e com os 5
   hashes metodológicos, antes de gastar os 175 fits.
2. **Auditoria** do resultado do preflight (ChatGPT/humano), fora do
   workflow.
3. **`[FASE2B-REPLAY]`** — só depois da auditoria aprovar o preflight: roda
   `gate_zero_replay` de novo (mesma checagem, sem atalho) **e** os 5
   `crossfit_fold_replay` (175 fits, 25 LSTM) **e** `agregar_replay`.

`crossfit_fold_replay` e `agregar_replay` dependem, na condição `if` do
workflow, exclusivamente de `autorizado_replay` — nunca de
`autorizado_replay_preflight`. O preflight não tem, por construção, nenhum
caminho para liberar um fit.

## 3. Os seis fingerprints

Os **cinco hashes metodológicos** já congelados continuam intocados,
calculados pelas mesmas funções de sempre:

- `hash_corpus`
- `hash_alvo_ensemble`
- `classes_sha256`
- `partition_manifest_online_sha256`
- `fold_assignment_sha256`

Eles são hashes de `id_sha256` + `grupo_sha256` (já normalizado) +
`referencia_humana` — **não** cobrem o texto bruto entregue ao TF-IDF/LSTM.
Uma alteração de texto que a normalização (NFKD + casefold + colapso de
espaços) apague preservaria `grupo_sha256` e, portanto, esses 5 hashes, sem
que o `X` bruto realmente treinado fosse o mesmo.

Por isso existe um **sexto fingerprint, exclusivamente operacional**:

```
replay_input_sha256
```

Calculado por `calcular_replay_input_sha256()`
(`src/ensemble_fase2b_crossfit.py`), cobre o texto **bruto** (não
normalizado) dos 4 campos textuais + os demais campos efetivamente
consumidos pelo treino/particionamento. **Não substitui, não altera e não
entra no cálculo de nenhum dos 5 hashes metodológicos** — é uma checagem
somada a eles, nunca no lugar deles.

## 4. Schema do bundle privado

Uma spreadsheet **privada e estática** (nunca a operacional), sem fórmula,
sem IMPORTRANGE — só valores já resolvidos, escritos uma vez via
`planilha.escrever_aba()`. Aba `REPLAY_EXECUCAO_1_INPUT_CONGELADO`, 9 colunas:

| Coluna | Conteúdo |
|---|---|
| `id_sha256` | chave de junção (nunca o ID bruto do chamado) |
| `titulo` | bruto |
| `descricao_glpi` | bruto |
| `titulo_osm` | bruto |
| `descricao_osm` | bruto |
| `categoria_historica` | H, já passado por `planilha.normalizar_categoria()` |
| `referencia_humana` | R — rótulo `y` efetivo de treino |
| `grupo_sha256` | recomputado e conferido a cada leitura (ver §5) |
| `outer_fold` | necessário operacionalmente; a fonte de verdade para o treino continua sendo `docs/dados/particoes_canonicas_mapa.csv` |

Acesso: conta de serviço de CI em **Leitor**; o proprietário humano mantém
acesso administrativo. A escrita inicial do bundle é sempre manual/humana —
nenhum job de CI grava nesta spreadsheet.

## 5. Sequência de validação em cada job `[FASE2B-REPLAY-PREFLIGHT]` / `[FASE2B-REPLAY]`

Todo job (Gate Zero replay — que roda nos dois marcadores — e, só no
`[FASE2B-REPLAY]` completo, os 5 outer folds e a agregação) roda,
independentemente, **antes de qualquer fit**:

1. Carregar o bundle (`replay_bundle.ler_bundle_congelado`).
2. Recalcular `replay_input_sha256` e exigir igualdade exata com
   `REPLAY_INPUT_SHA256_ESPERADO` (constante pinada em
   `ensemble_fase2b_crossfit.py`) → diverge: `ReplayBloqueado`.
3. Recomputar `grupo_sha256` dos 4 campos brutos de cada registro
   (`replay_bundle.validar_grupos_por_registro`, reusando
   `construir_grupos_textuais.normalizar_texto`/`hash_grupo` sem duplicar) e
   exigir igualdade com o `grupo_sha256` armazenado → diverge:
   `ReplayBloqueado`.
4. Recalcular os 5 hashes metodológicos e exigir igualdade exata com
   `HASHES_ESPERADOS` → diverge: `GateZeroBloqueado`.
5. Só então: executar o trabalho do job.

Como cada um dos 7 jobs valida de forma independente, uma edição na
spreadsheet privada entre dois jobs de uma mesma rodada é detectada no
próximo job que ler — ele bloqueia em vez de treinar sobre um input
diferente dos irmãos.

## 6. Nível de evidência da reconstrução da Execução 1

**O que está provado:**
- Os 13.968 registros não flagados preservam `grupo_sha256` idêntico ao
  aprovado (confirmado por diagnóstico read-only anterior).
- Os 4 registros divergentes têm seu estado histórico (na revisão de Drive
  `11302`, a mais recente ainda acessível — as revisões `11230` e `11291`
  retornaram `Revision not found`) já auditado e usado para reconstruir o
  bundle candidato.
- O bundle candidato, reconstruído a partir da base online atual + os 4
  estados históricos da revisão `11302`, reproduz **exatamente** os 5 hashes
  metodológicos aprovados (`HASHES_ESPERADOS`).

**O que NÃO está provado:** que o texto bruto dos 13.968 registros não
flagados é bit-a-bit idêntico ao que a Execução 1 realmente recebeu. A
igualdade dos 5 hashes metodológicos é necessária, mas não suficiente para
essa afirmação — ela só vê o texto através de `grupo_sha256`, que é hash de
texto **normalizado**; uma alteração absorvida pela normalização (espaço
duplo, acentuação, maiúscula/minúscula) mudaria o `X` bruto sem mudar nenhum
dos 5 hashes. Não há, até o momento, confirmação direta e independente
(ex.: exportação de uma revisão de Drive cobrindo a janela completa da
Execução 1, `02:10:28Z`–`02:36:35Z` em 2026-08-12) do texto bruto desses
13.968 registros.

**Portanto:** `replay_input_sha256`, uma vez pinado a partir deste bundle,
prova a **imutabilidade do bundle reconstruído daqui para frente** — não uma
prova retroativa, bit-a-bit, do `X` bruto exato da Execução 1. Esta é uma
limitação explícita e vinculante, não uma omissão.

## 7. Arquivos deste desenho

- `src/replay_bundle.py` — leitura do bundle privado, checagem por registro.
- `src/ensemble_fase2b_crossfit.py` — `calcular_replay_input_sha256`,
  `gate_zero_replay`, `ReplayBloqueado`, `REPLAY_INPUT_SHA256_ESPERADO`,
  `gravar_gate_zero_replay`, flag `--modo-replay` na CLI. `gate_zero()`
  permanece inalterada.
- `.github/workflows/ensemble_fase2b_crossfit.yml` — marcadores
  `[FASE2B-REPLAY-PREFLIGHT]` e `[FASE2B-REPLAY]`, jobs `gate_zero_replay`
  (compartilhado pelos dois marcadores), `crossfit_fold_replay` (matriz
  1–5, só `[FASE2B-REPLAY]`), `agregar_replay` (idem).
- `docs/dados/ensemble/replay/bundle_manifesto.json` — só fingerprints e
  contagens, nunca texto/ID.
- `tests/test_replay_bundle.py`, `tests/test_ensemble_fase2b_crossfit.py`.

## 8. Pendências antes de qualquer Execução Científica de replay

1. Criar a spreadsheet privada e escrever o bundle (ação manual/humana).
2. Auditar o conteúdo do bundle escrito contra o candidato validado neste
   documento.
3. Pinar `REPLAY_INPUT_SHA256_ESPERADO` em
   `src/ensemble_fase2b_crossfit.py` com o valor aprovado.
4. Disparar `[FASE2B-REPLAY-PREFLIGHT]` — só `gate_zero_replay`, zero fits —
   e auditar o resultado (ChatGPT).
5. Só depois da auditoria do preflight aprovar, disparar `[FASE2B-REPLAY]`
   (execução completa: 175 fits, 25 LSTM, agregação).

Enquanto `REPLAY_INPUT_SHA256_ESPERADO` for `None`, `gate_zero_replay()`
bloqueia sempre, por construção — nenhuma rodada de replay roda sem um valor
pinado e aprovado.

## 9. Encerramento formal da Fase 2B — Execução 2 inconclusiva

**Status do replay da Execução Científica 2:**
`INCONCLUSIVO_POR_AUSENCIA_DE_SNAPSHOT_BRUTO_INTEGRAL`.

A tentativa de reconstrução do bundle candidato (marcador
`[FASE2B-REPLAY-RECOVER]`, ferramenta `src/recuperar_bundle_replay.py`,
GitHub Actions run `31740951432`, commit `adc50531`) confirmou:

- universo estrutural = 13.972 IDs, sem faltantes nem duplicados;
- partições e alvo congelado cobrem exatamente o mesmo universo, com o
  mesmo fold por ID nas duas fontes;
- H, R e o alvo `Y=1(H!=R)` vieram diretamente dos artefatos já congelados
  (`docs/dados/ensemble/alvo_ensemble.json` + `docs/dados/particoes_canonicas_mapa.csv`),
  nunca recalculados a partir da planilha operacional atual;
- a `ALLOWLIST_GRUPO_A` (4 registros) e a `ALLOWLIST_GRUPO_B` (3 registros)
  aplicaram os patches auditados;
- mesmo assim, **10 registros** têm texto atual cujo `grupo_sha256`
  recomputado diverge do congelado — `status = bloqueado_grupo_textual_divergente`,
  `recover_diagnostico.json` do run `31740951432` (artifact
  `fase2b-replay-bundle-recover`).
- **nenhum fit foi executado** nesta tentativa: o bloqueio ocorreu no job
  `Verificacao do bundle candidato REPLAY (allowlist explicita, ZERO fits)`,
  antes de `crossfit_fold_replay`/`agregar_replay`, que nem chegaram a
  rodar (dependem exclusivamente de `autorizado_replay`, nunca de
  `autorizado_replay_preflight`).

**Motivo:** o input bruto integral efetivamente recebido pela Execução
Científica 1 não foi preservado como snapshot independente no momento da
execução. A reconstrução via allowlist explícita (Grupos A e B, 7
registros no total) e revisões de Drive ainda acessíveis esgotou a
evidência disponível sem resolver os 10 registros restantes — as revisões
`11230`/`11291` do Drive não estão mais acessíveis pela API, e não existe,
dentro deste repositório, nenhuma fonte independente adicional a
consultar.

**Decisão científica vinculante, registrada nesta rodada:**

- não continuar tentando reconstruir esses 10 textos;
- não procurar novas revisões do Google Drive;
- não criar novas allowlists;
- não inferir textos históricos para forçar um hash desejado;
- não modificar dados para fazer o replay passar.

Essa impossibilidade é uma **limitação de preservação/proveniência do X
bruto**, não evidência de indeterminismo dos modelos, erro científico da
Execução 1 ou divergência de resultados — nenhuma dessas três leituras deve
ser atribuída a este achado. Também não se deve afirmar que os 13.972
registros foram comprovados bit a bit idênticos ao input bruto original: a
igualdade dos 5 hashes metodológicos (que só enxergam texto já normalizado
via `grupo_sha256`) é necessária, mas não suficiente para essa afirmação —
ver seção 6.

**A Execução Científica 1 (run `31556028058`, commit `d6a5504c`) permanece
válida e preservada.** Nenhuma Execução Científica 2 foi aprovada. Toda
etapa posterior — a partir da Fase 2C — usa exclusivamente os artefatos da
Execução Científica 1; ver `docs/FASE2C_ENSEMBLE_CONTRATO.md` para a
auditoria de proveniência específica desses artefatos e o desenho da fase
seguinte.

A infraestrutura de RECOVER (`src/recuperar_bundle_replay.py`,
`tests/test_recuperar_bundle_replay.py`, o job
`[FASE2B-REPLAY-RECOVER]` do workflow) é preservada como evidência
histórica do que foi tentado e por quê — nenhum gate, script ou
diagnóstico deste desenho foi removido.
