# Resolução do bloqueio de K_f e do denominador de Y=1 (Fase 2C)

> Registrado em 14/08/2026, no fuso America/Bahia, **antes** de qualquer
> leitura de resultado comparativo dos quatro métodos da Fase 2C. Este
> documento existe para deixar temporalmente provado que a decisão abaixo
> foi tomada por proveniência/definição de universo, não por desempenho
> observado dos ensembles.

## O que ocorreu

A verificação estrutural da primeira tentativa de Execução Científica 1 da
Fase 2C encontrou uma divergência entre os `K_f` informados como
"esperados" e os `K_f` efetivamente computados a partir dos artefatos que
a Fase 2C está contratualmente autorizada a consumir. A execução foi
interrompida no Passo 4 antes de qualquer extração de resultado, e o
bloqueio foi reportado sem tentativa de reconciliação unilateral.

## Universo anterior (não usado nesta avaliação confirmatória)

- corpus congelado: 13.972 registros;
- `Y=1` total: 595;
- `K_f` por dobra: 567, 563, 621, 508, 590;
- `K_total`: 2.849.

Esses valores vêm da tabela "K, D e R por dobra" de
[`docs/CONGELAMENTO_ALVO_ENSEMBLE.md`](CONGELAMENTO_ALVO_ENSEMBLE.md),
originada em `docs/dados/ensemble/alvo_ensemble_resumo.json`, calculada por
`congelar_alvo_ensemble.reproduzir_baseline()` sobre
`docs/dados/retreino_canonico_predicoes.csv` — um treino **standalone** de
LinearSVC da trilha do artigo principal (execução canônica hash
`1e476243…`). Inclui os 2 registros com `H` fora do espaço de classes `C`,
que nunca passam por nenhum dos sete modelos-base e nunca aparecem em
nenhuma fila de nenhum método da Fase 2C.

## Universo confirmatório da Fase 2C (vigente)

- universo modelável: **13.970** registros (`H` dentro de `C`);
- `Y=1` modelável: **593**;
- `K_f` por dobra: **564, 560, 616, 507, 593**;
- `K_total`: **2.840**.

Motivo da exclusão dos 2 registros com `H` fora de `C`: eles nunca
recebem previsão de nenhum dos sete modelos-base (fora do domínio
aprendido), logo nunca aparecem em `outer_scores.npz`, nunca entram em
`contexto["registros"]` e nunca podem ser capturados por nenhuma fila —
incluí-los no denominador impõe um teto de recall inatingível por
construção, não por desempenho.

`K_f` e `Y=1` desta seção foram obtidos por duas vias independentes,
concordantes exatamente:

1. `ensemble_fase2c_combinacao.capacidade_linear_svc_por_fold()` sobre o
   contexto montado por `montar_contexto()`;
2. script isolado, lendo diretamente `fase2b_outer_scores.npz` (filtrado a
   `modelo == "linear_svc"`) e `docs/dados/ensemble/recongelamento_online/
   alvo_ensemble_online.json`, sem reusar nenhuma função do módulo.

A fonte válida para `K_f` na Fase 2C são as previsões **outer** do
LinearSVC da própria Execução Científica 1 da Fase 2B (artifact
`fase2b-resultado-cientifico`, run `31556028058`, commit
`d6a5504cd9c4360b97fd90dd88c13bd430155459`) — nunca o LinearSVC standalone
do baseline antigo, que não passou pelo cross-fitting de 5 outer folds da
Fase 2B e não é um artefato que a Fase 2C tenha autorização de consumir.

## Decisão vinculante

- `2849`/`595` (baseline antigo) **não são usados** como referência
  confirmatória da Fase 2C — permanecem apenas como evidência histórica da
  etapa anterior, citados aqui só para rastreabilidade;
- `2840`/`593` (previsões `outer` da Execução Científica 1) são os valores
  congelados e vinculantes desta avaliação;
- a decisão decorre exclusivamente de **proveniência e definição do
  universo modelável** — nenhum resultado comparativo entre os quatro
  métodos havia sido lido no momento desta decisão;
- nenhuma metodologia (pesos, alpha, capacidade, ausência de tau) foi
  reaberta ou alterada para produzir este ajuste — só a origem numérica do
  `K_f`/`Y=1` de referência foi corrigida.
