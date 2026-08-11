# Recongelamento online da base do ensemble

> Relatorio sanitizado e read-only. Substitui o Gate 2A de recuperacao textual historica: usa o texto ONLINE atual da planilha (corrigido humanamente apos 04/08/2026) como fonte, preservando IDs, outer_folds, H, R e Y do congelamento anterior.

**Estado:** `apto_para_baseline`  
**Gerado em:** 10/08/2026 23:58  
**Spreadsheet ID:** `1lohPUQOgxzt_DMxnNLKMxnieZq1sVmh4uwBLbbgvfiQ`  
**Aba:** `CHAMADOS_ESQUELETO_REDUZIDO`  
**BASE_SHA (main):** `4cf0d2fa89158c753448ffa0d6f8ec75ef94d51f`  
**HEAD_SHA (branch):** `bf5b1c3b3d38950b16610231c9cad57db81a7edf`

## Diagnostico de invariantes

| Verificacao | Valor |
|---|---:|
| total ids particoes | 13972 |
| total ids alvo congelado | 13972 |
| total ids particao sem alvo | 0 |
| total ids alvo sem particao | 0 |
| folds particao | [1, 2, 3, 4, 5] |
| folds alvo congelado | [1, 2, 3, 4, 5] |
| total dobra historica divergente | 0 |
| total ids encontrados no online | 13972 |
| total faltantes no online | 0 |
| total ids duplicados no online | 0 |
| total grupos atuais distintos | 9735 |
| total grupos congelados distintos | 9734 |
| total grupos ou textos alterados em relacao ao historico | 7 |
| grupos cruzando dobras | 0 |
| h divergentes | 0 |
| r divergentes | 0 |
| y divergentes | 0 |

Bloqueios: nenhum.

## Hashes

| Hash | Anterior | Novo | Mudou |
|---|---|---|---|
| hash_corpus | `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a` | `fe9bfa4a6c521c0c73b234500e1c9d14bdeb6769470269daa38e588a7a877891` | True |
| hash_alvo_ensemble | `76d903c9e89039fd507524c9c836394bf005c7c757830677a3ed3d068818d569` | `8884d6098325734a0315e8976ffa1b8bd7da15cede3a6a959904a098fbe7d57c` | True |
| hash_historico_ensemble | `a30b353e031a27812df12217242b8181cee1e58806ae2d243113fcddb6f61916` | `a30b353e031a27812df12217242b8181cee1e58806ae2d243113fcddb6f61916` | False |
| classes_sha256 | `9e6c742bd7f6410de10f857d4103a959316f588ae4f19afdb06d84a3dcea947a` | `9e6c742bd7f6410de10f857d4103a959316f588ae4f19afdb06d84a3dcea947a` | False |
| partition_manifest_origem_sha256 | `6d7d7384276644d057acc6d8d42ec5da8d14e6b0745a5abdb97a3f52be812f1d` | `6d7d7384276644d057acc6d8d42ec5da8d14e6b0745a5abdb97a3f52be812f1d` | False |
| partition_manifest_online_sha256 | `None` | `d38c041695259e9204a7450955bed209191c829e0f99b269a28cfbf4bc53b404` | True |
| fold_assignment_sha256 | `None` | `dc17cfb2806d1c20b141c1e394b684f7c3e087a1ba922e4920497d96bcd64b7d` | True |

## Baseline LinearSVC: historico x atual

| Metrica | Historico | Atual | Diferenca |
|---|---:|---:|---:|
| alertas_naturais | 2849 | 2828 | -21 |
| inadequacoes_na_fila | 528 | 524 | -4 |
| precisao_fila_natural | 0.1853 | 0.1853 | 0.0 |
| correcoes_top1 | 475 | 474 | -1 |
| neutros | 53 | 50 | -3 |
| prejudicados | 2321 | 2304 | -17 |

## Garantias

- Nenhuma escrita foi realizada na planilha.
- As particoes canonicas (`docs/dados/particoes_canonicas_mapa.csv`) nao foram regeneradas; o StratifiedGroupKFold nao foi reexecutado.
- Nenhum texto bruto ou ID de chamado foi publicado.
