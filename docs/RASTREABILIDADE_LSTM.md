# Rastreabilidade dos experimentos com LSTM

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs
> de chamados.

Este documento existe para resolver, com evidência, por que a mesma
arquitetura recorrente aparece no repositório com três acertos diferentes:
**0,7287** na avaliação principal, **0,8635** no experimento agrupado do
*ablation* e **0,8768** na partição aleatória equivalente. A conclusão
antecipada é que os três números são válidos, medem coisas diferentes e não
podem ser comparados entre si; a Seção 3 mostra qual diferença de protocolo
responde pela maior parte da distância.

## 1. Tabela de rastreabilidade

| Item | E1 — rodada canônica | E2 — *ablation* agrupado | E3 — *ablation* aleatório |
|---|---|---|---|
| Resultado | 0,7287 de acurácia | 0,8635 de acerto | 0,8768 de acerto |
| Artefato | `docs/dados/retreino_canonico.json` | `04_artigo/figuras/ablation_lstm_resultados.json` | histórico do Git, commit `e10051d2` |
| Script | `src/retreinar_modelos_canonicos.py` | `src/ablation_lstm.py` | `src/ablation_lstm.py`, versão anterior |
| Data | 04/08/2026 | 24/07/2026 às 23:53 | 24/07/2026 às 22:33 |
| Hash do corpus | `1e4762438a7e` | não carimbado | não carimbado |
| Base | aba viva fixada pelo mapa de partições congelado | aba viva de 24/07/2026, 13.965 linhas elegíveis | idem E2 |
| Denominador | 13.972 linhas | 9.096 linhas | 9.096 linhas |
| Referência de avaliação | referência humana revisada, cobertura integral | verdade derivada de M/N/P/Q, cobertura parcial | idem E2 |
| **Rótulo de treino** | **a própria referência humana** | **a categoria histórica da coluna C** | **a categoria histórica da coluna C** |
| Categorias | 41, após o corte de suporte por dobra | taxonomia histórica inteira, sem corte | idem E2 |
| Estratégia de partição | `StratifiedGroupKFold`, k = 5, semente 42 | `GroupKFold`, k = 3, sem semente | `KFold` embaralhado por linha, k = 3, semente 42 |
| Agrupamento | sim, SHA-256 dos quatro campos normalizados | sim, SHA-256 do texto concatenado normalizado | **não** |
| Conjunto de treino | as quatro dobras restantes, ≈ 11.178 linhas | todas as linhas elegíveis fora dos grupos de teste, com ou sem referência | idem E2 |
| Tokenização | `keras.preprocessing.text.Tokenizer`, `oov_token="<OOV>"`, ajustada só no treino da dobra | idêntica | idêntica |
| Vocabulário | 8.000 termos | 8.000 termos | 8.000 termos |
| Comprimento máximo | 120 tokens, *padding* e truncamento à direita | 120 | 120 |
| Arquitetura | `Embedding(8000, 128)` → `BiLSTM(64)` → `Dropout(0,5)` → `Dense(64, ReLU)` → `Dense(K, softmax)` | idêntica na variante de referência; o estudo varia unidades (64/128) e *dropout* (0,5/0,3) | idem E2 |
| Hiperparâmetros | Adam, `sparse_categorical_crossentropy`, 15 épocas, lote 128, `class_weight` balanceado | idênticos | idênticos |
| Critério de parada antecipada | `val_loss`, paciência 3, `restore_best_weights` | idêntico | idêntico |
| Seleção de época | melhor `val_loss` na fatia interna de 10% do treino da dobra | idêntica | idêntica |
| Conjunto em que a métrica foi calculada | união das predições *out-of-fold* das cinco dobras | as 9.096 linhas com referência disponível | as mesmas 9.096 linhas |
| Sementes | 42 nas partições; TensorFlow sem semente fixa | `GroupKFold` é determinístico; TensorFlow sem semente fixa | 42 no `KFold`; TensorFlow sem semente fixa |
| **Vazamento** | **nenhum**: `grupos_vazados_para_o_treino = 0`, verificado dobra a dobra | **nenhum de grupo**, mas há assimetria de referência (Seção 3) | **sim**: 46,72% das linhas de teste têm duplicata textual no treino |

A medição do vazamento de E3 está em
`04_artigo/figuras/diagnostico_ablation_lstm_duplicatas.json`: 4.250 das 9.096
linhas de teste compartilham texto normalizado com alguma linha de treino, com
taxa entre 46,27% e 47,53% nas três dobras.

## 2. O que E1 verifica e os demais não

O critério de aceite do Passo 4 é verificado a cada dobra em
`src/retreinar_modelos_canonicos.py`: a interseção entre os grupos textuais do
treino e os do teste precisa ser vazia. O artefato registra o resultado dessa
verificação, e não a intenção do desenho. Para os sete modelos, incluindo o
LSTM, `grupos_vazados_para_o_treino` é zero.

A tokenização, o vocabulário e a matriz TF-IDF dos demais modelos são ajustados
dentro de `fit`, isto é, exclusivamente sobre a partição de treino de cada
dobra. A época é escolhida por parada antecipada sobre uma fatia interna do
próprio treino. O calibrador e o limiar de automação são ajustados numa dobra
interna, distinta da dobra externa avaliada, conforme
`docs/dados/calibracao_canonica.json`. Nenhuma dessas etapas vê a dobra de
teste.

## 3. Origem técnica da discrepância entre E1 e E2

Dizer que “os protocolos são diferentes” não explica nada. O número que explica
está em `04_artigo/figuras/diagnostico_ablation_lstm_protocolo.json`:

| Campo | Valor |
|---|---:|
| Linhas avaliadas no *ablation* | 9.096 |
| Linhas em que a referência humana **coincide** com a categoria histórica | 9.096 |
| Linhas em que a referência humana **diverge** da categoria histórica | 0 |
| Taxa de coincidência | 100,00% |

Em 24/07/2026 a conferência humana ainda era parcial, e a verdade derivada só
existia onde o revisor havia **confirmado** o rótulo administrativo; os
registros marcados como incorretos seguiam pendentes de categoria manual. O
recorte de 9.096 linhas é, portanto, exatamente o subconjunto em que
referência e histórico são o mesmo rótulo.

Disso decorre a assimetria decisiva. E2 treina o modelo contra a categoria
histórica e o avalia contra uma referência que, naquele recorte, é a categoria
histórica. A tarefa medida é reproduzir o rótulo de origem em casos já
confirmados, e o modelo é premiado por concordar com o rótulo que o experimento
se propunha a auditar. E1 treina contra a referência revisada e a avalia sobre o
corpus inteiro, no qual 598 registros, ou 4,25%, têm referência distinta do
histórico, além de incluir os casos que o revisor rejeitou — justamente os mais
difíceis, e ausentes por construção do recorte de E2.

Três diferenças secundárias operam no mesmo sentido:

1. **Cobertura da avaliação.** E2 mede 9.096 das 13.965 linhas elegíveis, e o
   subconjunto não é probabilístico: é o resultado da ordem de trabalho da
   revisão manual.
2. **Taxonomia.** E1 avalia sobre as 41 categorias com suporte nas cinco
   dobras; E2, sobre a taxonomia histórica inteira daquela data.
3. **Número de dobras.** E2 usa três dobras, e não cinco, o que reduz o treino
   de cada modelo.

Não há erro de implementação em E2 quanto ao vazamento de grupo: o agrupamento
por hash de texto está correto e o treino exclui todos os grupos de teste. O
que existe é uma pergunta de pesquisa diferente, medida sobre um denominador
diferente.

## 4. Defeito de implementação encontrado e corrigido

`src/ablation_lstm.py` ficou inoperante depois da varredura de 02/08/2026 (PR
#159), que trocou a chave de `dv.carregar_decisoes` de número de linha para
`id_chamado`. As funções `avaliar_variante` e `diagnosticar_duplicatas_folds`
continuaram procurando `item["linha"]` num mapa indexado por `id`. As duas
chaves não têm sequer o mesmo tipo, de modo que nenhum registro era encontrado
e o script abortava com `Informação insuficiente para verificar.` — sem erro
visível, que é o mesmo modo de falha que já havia derrubado quatro ferramentas
naquele dia.

Correções aplicadas nesta rodada:

- `chave_verdade` passa a resolver a chave por `id_chamado`, com recurso ao
  número da linha para chamadores que ainda passem um mapa antigo;
- o rótulo de treino passa a ser a **referência humana**, e a categoria
  histórica só é usada onde não há referência, o que elimina a assimetria da
  Seção 3 em execuções futuras;
- regressão fixada em `tests/test_ablation_lstm_chave.py`.

Os números de E2 e E3 **não foram regerados**: a execução depende de acesso à
planilha viva com credenciais de serviço e de treino real do LSTM, indisponíveis
nesta rodada. Eles permanecem no repositório como registro do experimento
legado, com a proveniência carimbada em
`04_artigo/figuras/ablation_lstm_resultados.json`, e o artigo passa a
apresentá-los no material suplementar, com o protocolo declarado e sem
compará-los às tabelas do corpo.

## 5. O que sustenta a escolha do protocolo agrupado

A justificativa do agrupamento não depende de E2 nem de E3. Ela está no
congelamento, em `docs/dados/grupos_textuais.json`: 4.586 das 14.060 linhas, ou
32,62%, compartilham texto normalizado com outra linha, e a base resolve-se em
9.786 grupos. Sob partição por linha, essas 4.586 linhas podem cair
simultaneamente em treino e teste.

As duas estimativas disponíveis da magnitude do efeito são ambas anteriores ao
congelamento e estão declaradas como tais:

| Estimativa | Diferença medida | Protocolo |
|---|---:|---|
| E3 − E2, só no LSTM | 1,33 ponto percentual | 9.096 linhas, rótulo histórico, k = 3 |
| `comparacao_kfold_groupkfold.json`, sete modelos | 0,89 a 1,84 ponto percentual | 14.094 linhas, alvo é a categoria histórica, k = 5 |

Nenhuma das duas foi reproduzida sob a rodada canônica, e por isso o artigo não
as apresenta como quantificação do vazamento evitado nas Tabelas 1 e 2.

## 6. Contagem de grupos textuais

Três contagens circulam no projeto e não são intercambiáveis. A conciliação é
calculada por `src/inferencia_canonica.py` e publicada em
`docs/dados/inferencia_canonica.json`, no bloco `contagem_de_grupos`.

| Contagem | Valor | O que é |
|---|---:|---|
| Grupos da base congelada | 9.786 | todas as 14.060 linhas do Passo 2 |
| Grupos congelados no recorte avaliado | 9.735 | unidade de reamostragem do *bootstrap*, restrita às 13.972 linhas |
| Grupos no mapa de partições | 9.734 | recalculados sobre o texto vivo no Passo 3 |

A diferença de 51 entre a primeira e a segunda são os grupos que desapareceram
com as 88 linhas fora das partições. A diferença de 1 entre a segunda e a
terceira tem causa nominal: **dois** registros tiveram o texto editado na aba
viva depois do congelamento, e num deles o texto novo passou a coincidir com um
grupo de 47 linhas já existente, que virou 48. O outro apenas trocou de hash
sem mudar a contagem. A unidade reprodutível é a congelada, 9.735, e é ela que
o artigo reporta ao descrever o *bootstrap*.

Os dois registros aqui contados e os três registrados em
`docs/dados/retreino_canonico.json` medem a mesma deriva em momentos
diferentes: o mapa de partições foi gerado em 03/08/2026 e o retreino leu a aba
em 04/08/2026, quando um terceiro texto já havia sido editado. Nenhum dos dois
números está errado; ambos precisam do carimbo de data para significar algo.
