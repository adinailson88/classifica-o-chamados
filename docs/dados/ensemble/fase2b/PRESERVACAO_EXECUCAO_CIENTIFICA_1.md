# Preservação durável da Execução Científica 1 (Fase 2B)

> Registro curto. Não contém texto bruto, ID bruto de chamado nem conteúdo
> da spreadsheet privada.

O artifact oficial do GitHub Actions expira em ~30 dias
(`retention-days: 30`, criado em 12/08/2026, expira por volta de
11/09/2026). Os dois `.npz` que a Fase 2C consome (`fase2b_inner_scores.npz`,
`fase2b_outer_scores.npz`) foram preservados de forma durável fora dessa
janela, via GitHub Release — sem Git LFS, sem entrar no histórico normal do
Git.

## Fonte

- **run:** `31556028058`
- **artifact:** `fase2b-resultado-cientifico` (`artifact_id` `9126463959`)
- **commit produtor:** `d6a5504cd9c4360b97fd90dd88c13bd430155459`

## Release de preservação

- **tag:** `ensemble-fase2b-execucao-cientifica-1`
- **target:** `d6a5504cd9c4360b97fd90dd88c13bd430155459` (o commit produtor exato)
- **tipo:** pre-release (não representa versão de software), não marcado como latest
- **URL:** <https://github.com/adinailson88/classificacao-chamados/releases/tag/ensemble-fase2b-execucao-cientifica-1>

**Assets:**

| Asset | Conteúdo |
|---|---|
| `fase2b-resultado-cientifico-run31556028058.zip` | o artifact original do GitHub Actions, íntegro, sem recompactação |
| `fase2b_preservacao_manifest.json` | proveniência completa: hashes, contagens, declaração de zero reexecução |

## Verificação (SHA-256)

ZIP baixado diretamente do run via `gh api .../actions/artifacts/9126463959/zip`,
comparado com o digest informado pela API do GitHub, publicado no Release, e
baixado de volta do Release para conferência — os três batem exatamente:

```
sha256(zip original) = sha256(zip no Release) = digest da API do GitHub
                      = 8cd0c2df97257bdc003beb6a2912de3350a4ff7a0689b480bd4c4be946c2f6d1
```

SHA-256 físico dos dois `.npz` extraídos do ZIP:

| Arquivo | Tamanho | SHA-256 |
|---|---:|---|
| `fase2b_inner_scores.npz` | 71.863.083 bytes | `75393dabaa198895ce1b2a86a34f2085a93ace1d68338c7578cb35d22c30195a` |
| `fase2b_outer_scores.npz` | 17.982.800 bytes | `a260e1e4e2f6e37b1bf8f95a07bcbe058992fe8708947e9804b1c05ebc8b196f` |

## Hashes científicos congelados (confirmados nesta rodada)

Confirmados rodando `src/ensemble_fase2c_combinacao.py --somente-validar-proveniencia`
sobre o conteúdo extraído — verificação de proveniência já existente da
Fase 2C, **zero fits**:

```
input_bundle_sha256                = a533e245d97482f423bb9981df350ad6ec550133a2253c3a5f528f086459e83f
inner_predictions_canonical_sha256 = 98e38ea42236210ba430ed322b5872062e7ac0eba2ec3d64d06566b11802b0d1
outer_predictions_canonical_sha256 = 660d3f451040615a08bac1934f6ac157ac0052b5c98fe7890508c9e064d61e6d
crossfit_manifest_sha256           = 5e9c8cd975017867b96dcf543b90ad90c7ec989939ad934cca5dd175c32179e3
fase2b_science_sha256              = 931c8092e372d6d416b0763bc55bfd74c856aeb1cf4c321dd55081ea16d82470
```

Contagens confirmadas: 13.970 modeláveis, 391.160 previsões internas,
97.790 previsões externas, 175 fits totais, 25 fits de LSTM.

## O que isso significa

Este Release é a **preservação durável** dos artefatos da Execução
Científica 1. O artifact temporário do GitHub Actions (run `31556028058`)
pode expirar sem invalidar a Fase 2C: `src/ensemble_fase2c_combinacao.py`
continua funcionando normalmente apontando `--entrada-dir` para o conteúdo
extraído deste Release, com os mesmos hashes de proveniência bloqueantes.
