# Congelamento do alvo do ensemble

> Relatorio sanitizado e read-only. Nao contem IDs brutos, titulos, descricoes ou texto de chamados.

- hash_corpus: `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`
- hash_historico_ensemble: `a30b353e031a27812df12217242b8181cee1e58806ae2d243113fcddb6f61916`
- hash_alvo_ensemble: `76d903c9e89039fd507524c9c836394bf005c7c757830677a3ed3d068818d569`
- SHA-256 fisico de alvo_ensemble.json: `76d903c9e89039fd507524c9c836394bf005c7c757830677a3ed3d068818d569`
- classes_sha256: `9e6c742bd7f6410de10f857d4103a959316f588ae4f19afdb06d84a3dcea947a`
- partition_manifest_sha256: `6d7d7384276644d057acc6d8d42ec5da8d14e6b0745a5abdb97a3f52be812f1d`
- commit produtor: `a141facf3e2989d39181c3f9be565d7fc98c9266`
- registros: 13972
- grupos: 9734
- grupos atuais distintos (diagnostico): 9735
- grupos do Passo 2 distintos (A): 9735
- grupos da particao distintos (B): 9734
- Passo 2 x particao (A != B): 2
- IDs Passo 2 x particao: `["1724bbac018e0dfe8158b813ddf17117be537d626e2b22d00ae17b692b07ea27", "976f99c38d8e76b1db212d3f6b32668936fde330d22ed75fa21b8b4ef4cf81b5"]`
- particao x texto atual (B != C): 7
- Passo 2 x texto atual (A != C): 9
- grupos divididos entre dobras: 0
- referencias OOF consistentes entre sete modelos: True
- referencias OOF x planilha divergentes: 0
- origem do hash_corpus: `docs/dados/rodada_canonica.json`
- dobras: 5
- Y=1: 595
- Y=0: 13377
- H dentro de C: 13970
- H fora de C: 2

## Baseline LinearSVC

- alertas_naturais: 2849
- prejudicados: 2321
- inadequacoes_na_fila: 528
- correcoes_top1: 475
- neutros: 53
- precisao_fila_natural: 0.1853

## K, D e R por dobra

| Dobra | K_f | D_f | R_f | Inadequacoes na fila | Precisao |
|---:|---:|---:|---:|---:|---:|
| 1 | 567 | 0 | 567 | 104 | 0.1834 |
| 2 | 563 | 2 | 561 | 87 | 0.1545 |
| 3 | 621 | 0 | 621 | 120 | 0.1932 |
| 4 | 508 | 0 | 508 | 102 | 0.2008 |
| 5 | 590 | 0 | 590 | 115 | 0.1949 |

## Categorias historicas fora de C

- Hidrossanitária > ETA / ETE
- Manutenção Preventiva > Nobreak

## Garantias

- Nenhum modelo foi treinado ou executado.
- A planilha foi lida em modo read-only.
- O arquivo bruto de cache e credenciais nao sao artefatos deste relatorio.
