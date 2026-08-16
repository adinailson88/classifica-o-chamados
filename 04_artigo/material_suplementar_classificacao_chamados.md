---
title: "Material suplementar"
header-includes:
  - |
    ```{=latex}
    % O placeins vive em 04_artigo/latex porque nao existe na imagem
    % pandoc/extra do workflow (TEXINPUTS aponta para la); o ramo
    % alternativo evita falha de build caso o TEXINPUTS nao o alcance.
    % Mesmo mecanismo usado em artigo_classificacao_chamados_v3.md.
    \IfFileExists{placeins.sty}{%
      \usepackage{placeins}%
    }{%
      \makeatletter
      \newcommand\FloatBarrier{%
        \par
        \begingroup
          \let\@elt\relax
          \xdef\fb@pendentes{\@deferlist}%
        \endgroup
        \ifx\fb@pendentes\@empty\else\clearpage\fi
      }
      \makeatother
    }
    ```
---

```{=latex}
\small
```

# Material suplementar

**Classificação de chamados de manutenção predial com aprendizado de máquina: desempenho e limites da automação**

Este documento reúne as Tabelas S1 a S16 citadas ao longo do artigo e do
Apêndice A. Ele não substitui o artigo principal
(`04_artigo/artigo_classificacao_chamados_v3.md`, PDF em
`docs/artigo_classificacao_chamados.pdf`) nem introduz resultado, conclusão
ou dado novo: cada tabela reproduz, sem recálculo, um artefato já gerado no
repositório. Os arquivos-fonte, em CSV, ficam versionados em
`04_artigo/figuras/tabela_S1_*.csv` a `tabela_S16_*.csv`; este documento é a
sua leitura consolidada.

**Convenção de exibição.** Os CSVs-fonte usam ponto como separador decimal
(formato de máquina); as tabelas abaixo convertem para vírgula, para manter
a mesma convenção do corpo do artigo em português, preservando a
quantidade de casas decimais do CSV-fonte (capada em quatro, para os
poucos valores com mais precisão, como as diferenças de precisão/recall da
Tabela S16). Os nomes de coluna mostram espaço no lugar do sublinhado do
CSV-fonte, para permitir quebra de linha. Ambas as conversões são apenas de
apresentação: nenhum valor foi recalculado, e o CSV correspondente
permanece a fonte de registro. Tabelas com muitas colunas foram divididas
em partes por largura de página; a chave (`modelo`, ou `escopo`/`outer
fold`/`metodo`, conforme o caso) repete-se em cada parte para permitir o
cruzamento.

**Hash canônico.** As Tabelas S6 a S15 derivam de artefatos da rodada
canônica identificada por `hash_corpus`
`1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`, a mesma
que sustenta o corpo do artigo (conferível por
`python src/matriz_proveniencia.py`). As Tabelas S1 a S4 vêm de execuções
anteriores ao congelamento do corpus e não carregam esse hash; a Tabela S5
é o experimento exploratório do BERTimbau citado na Subseção 4.5; a Tabela
S16 vem do manifesto confirmatório da Fase 2C, trilha experimental própria,
também sem `hash_corpus`. A distinção de trilha é registrada na nota de
cada tabela.

## Sumário

| Tabela | Título | Trilha |
|---|---|---|
| S1 | Métricas por categoria (suporte, precisão, recall, F1) | legado, pré-congelamento |
| S2 | Códigos de categoria usados na Figura 3 | legado, pré-congelamento |
| S3 | *Ablation* do LSTM: unidades × *dropout* | legado, pré-congelamento |
| S4 | KFold por linha *versus* GroupKFold por grupo textual | legado, pré-congelamento |
| S5 | Holdout exploratório do BERTimbau | exploratório (BERTimbau) |
| S6 | Dispersão das predições (entropia e Jensen-Shannon) | rodada canônica |
| S7 | Curva ABC global, acurácia e macro-F1 por modelo | rodada canônica |
| S8 | Tarefa de tipo de manutenção | rodada canônica |
| S9 | Curva ABC interna a cada tipo (LinearSVC) | rodada canônica |
| S10 | Camada de regras de periodicidade *versus* modelo puro | rodada canônica |
| S11 | Inferência pareada agrupada (21 pares) | rodada canônica |
| S12 | Macro-F1 sob três convenções de denominador | rodada canônica |
| S13 | Utilidade da reclassificação sob custos assimétricos | rodada canônica |
| S14 | Pressupostos estatísticos secundários | rodada canônica |
| S15 | Calibração completa dos sete modelos | rodada canônica |
| S16 | Fase 2C: LinearSVC *versus* combinações de *ensemble* | confirmatório (Fase 2C) |

```{=latex}
\FloatBarrier
```

## Tabela S1 — Métricas por categoria

**Fonte:** aba viva da planilha experimental (`TABELA_S1_METRICAS`,
`gid=1862157493`), com *fallback* documentado para
`docs/dados/metricas_por_categoria.json` quando a credencial de acesso não
está disponível na sessão (`src/exportar_tabela_por_categoria.py`). Trilha
legada, anterior ao congelamento do corpus em 14.060 chamados; não carrega
`hash_corpus`. **Denominador:** suporte por categoria varia conforme a
coluna `support`; a base desta tabela não é a rodada canônica de 13.972
linhas avaliadas. A coluna `concordancia`, sempre vazia nesta execução, e a
coluna `fonte`, constante em todas as linhas (o texto acima), foram
omitidas da tabela impressa por não variarem entre categorias.

| categoria | support | precision | recall | f1 |
|---|---|---|---|---|
| Elétrica > Sistema Fotovoltaico (FV) | 7 | 0,0000 | 0,0000 | 0,0000 |
| Manutenção Preventiva | 2 | 0,0000 | 0,0000 | 0,0000 |
| Estrutura Predial > Instalações Especiais (gás, ar comprimido, etc.) | 3 | 0,0380 | 1,0000 | 0,0732 |
| Suprimentos / Apoio Técnico > Transporte | 1 | 0,0556 | 1,0000 | 0,1053 |
| Área Externa e Ambiental > Drenagem | 3 | 0,0833 | 0,3333 | 0,1333 |
| Manutenção Preventiva > Sistemas de incêndio | 9 | 0,2000 | 0,1111 | 0,1429 |
| Manutenção Preventiva > Aplicação cupinicida | 3 | 0,0857 | 1,0000 | 0,1579 |
| Manutenção Preventiva > Bomba | 3 | 0,0968 | 1,0000 | 0,1765 |
| Instalação de Acessórios e Mobiliário > Instalação/reparo de equipamentos (Suportes de TV, acessórios de banheiro e quadro branco) | 262 | 0,2407 | 0,1489 | 0,1840 |
| Projetos e Reformas > Projeto | 25 | 0,1691 | 0,9200 | 0,2857 |
| Projetos e Reformas > Reforma | 83 | 0,1875 | 0,6506 | 0,2911 |
| Manutenção Preventiva > Esgoto | 33 | 0,1985 | 0,7879 | 0,3171 |
| Suprimentos / Apoio Técnico > Limpeza de equipamentos, ambiente e mobiliário | 14 | 0,2391 | 0,7857 | 0,3667 |
| Outros > Outros | 33 | 0,8000 | 0,2424 | 0,3721 |
| Área Externa e Ambiental > Poda de Árvore / Roçagem | 9 | 0,2353 | 0,8889 | 0,3721 |
| Manutenção Preventiva > Hidráulica | 32 | 0,2667 | 0,7500 | 0,3934 |
| Outros > Erro de chamado | 243 | 0,3939 | 0,4280 | 0,4103 |
| Estrutura Predial > Alvenaria / Pisos / Estrutura | 1300 | 0,6559 | 0,3269 | 0,4363 |
| Manutenção Preventiva > Telhados, calhas, rufos, etc. | 44 | 0,3551 | 0,8636 | 0,5033 |
| Hidrossanitária > ETA / ETE | 16 | 0,3488 | 0,9375 | 0,5085 |
| Estrutura Predial > Pintura | 58 | 0,3676 | 0,8621 | 0,5155 |
| Estrutura Predial > Telhados, calhas, rufos, etc. | 206 | 0,5783 | 0,4660 | 0,5161 |
| Equipamentos de Transporte > Elevador | 22 | 0,4082 | 0,9091 | 0,5634 |
| Área Externa e Ambiental > Manutenção área externa / meio ambiente | 94 | 0,7121 | 0,5000 | 0,5875 |
| Suprimentos / Apoio Técnico > Materiais | 85 | 0,4851 | 0,7647 | 0,5936 |
| Manutenção Preventiva > Nobreak | 10 | 0,4500 | 0,9000 | 0,6000 |
| Segurança contra Incêndio > Sistemas de combate a incêndio (extintores, hidrantes) | 27 | 0,5278 | 0,7037 | 0,6032 |
| Climatização > Ar condicionado central | 36 | 0,5091 | 0,7778 | 0,6154 |
| Elétrica > Subestação | 18 | 0,5417 | 0,7222 | 0,6190 |
| TI / Dados / Rede > Ponto de rede / fibra ótica / Wi-fi | 399 | 0,5524 | 0,8195 | 0,6599 |
| Elétrica > Instalações elétricas | 940 | 0,7675 | 0,5830 | 0,6626 |
| Instalação de Acessórios e Mobiliário > Placas de identificação | 54 | 0,5393 | 0,8889 | 0,6713 |
| Estrutura Predial > Infiltração | 213 | 0,6113 | 0,8122 | 0,6976 |
| Elétrica > Gerador | 38 | 0,5806 | 0,9474 | 0,7200 |
| Hidrossanitária > Bomba | 38 | 0,6346 | 0,8684 | 0,7333 |
| Climatização > Ar condicionado | 517 | 0,9873 | 0,5996 | 0,7461 |
| Estrutura Predial > Forro | 144 | 0,6760 | 0,8403 | 0,7492 |
| Elétrica > Nobreak | 127 | 0,6421 | 0,9606 | 0,7697 |
| Hidrossanitária > Hidráulica | 1276 | 0,9173 | 0,6865 | 0,7853 |
| Estrutura Predial > Esquadrias, porta, portão e janelas | 969 | 0,8407 | 0,8390 | 0,8399 |
| Elétrica > Iluminação | 747 | 0,8769 | 0,8675 | 0,8721 |
| Manutenção Preventiva > Reservatório | 279 | 0,7982 | 0,9785 | 0,8792 |
| Manutenção Preventiva > Poços artesianos | 13 | 0,8667 | 1,0000 | 0,9286 |
| Manutenção Preventiva > Ar condicionado split | 1795 | 0,9012 | 0,9811 | 0,9395 |
| Climatização > Ar condicionado split | 1117 | 0,9444 | 0,9427 | 0,9435 |
| TI / Dados / Rede > Coleta de dados | 40 | 0,9286 | 0,9750 | 0,9512 |
| Manutenção Preventiva > Vistoria em Instalações | 247 | 0,9831 | 0,9393 | 0,9607 |
| Posto de trabalho > Contratação de Posto de trabalho | 102 | 0,9612 | 0,9706 | 0,9659 |
| Manutenção Preventiva > Iluminação | 132 | 0,9844 | 0,9545 | 0,9692 |
| Manutenção Preventiva > Elevador | 86 | 0,9655 | 0,9767 | 0,9711 |
| Manutenção Preventiva > Ar condicionado central | 165 | 0,9819 | 0,9879 | 0,9849 |
| Manutenção Preventiva > Quadros Elétricos | 576 | 0,9965 | 0,9774 | 0,9869 |
| Manutenção Preventiva > Sistemas de combate a incêndio (extintores, hidrantes) | 45 | 0,9783 | 1,0000 | 0,9890 |
| Manutenção Preventiva > Gerador | 1211 | 0,9992 | 0,9827 | 0,9908 |
| Manutenção Preventiva > Extintor | 14 | 1,0000 | 1,0000 | 1,0000 |

```{=latex}
\FloatBarrier
```

## Tabela S2 — Códigos de categoria (Figura 3)

**Fonte:** `docs/dados/estatistica.json`, execução legada anterior ao
congelamento (`src/gerar_figura4_confusoes.py`); não carrega
`hash_corpus`. Mapeia os códigos `C01`–`C10` usados para manter a Figura 3
(principais confusões) legível, para a categoria histórica completa que
cada código representa.

| codigo | categoria |
|---|---|
| C01 | Climatização > Ar condicionado split |
| C02 | Elétrica > Instalações elétricas |
| C03 | Estrutura Predial > Alvenaria / Pisos / Estrutura |
| C04 | Estrutura Predial > Esquadrias, porta, portão e janelas |
| C05 | Hidrossanitária > Hidráulica |
| C06 | Instalação de Acessórios e Mobiliário > Instalação/reparo de equipamentos (Suportes de TV, acessórios de banheiro e quadro branco) |
| C07 | Manutenção Preventiva > Ar condicionado split |
| C08 | Manutenção Preventiva > Reservatório |
| C09 | Outros > Erro de chamado |
| C10 | TI / Dados / Rede > Ponto de rede / fibra ótica / Wi-fi |

```{=latex}
\FloatBarrier
```

## Tabela S3 — *Ablation* do LSTM: unidades × *dropout*

**Fonte:** `04_artigo/figuras/ablation_lstm_resultados.json`
(`src/ablation_lstm.py`). *Snapshot* legado de 24/07/2026, com cobertura
parcial da revisão humana (9.096 linhas validadas) e rótulo de treino
histórico; não carrega `hash_corpus`. O script tornou-se inoperante após a
varredura de reindexação por `id_chamado` de 02/08/2026
(`docs/RASTREABILIDADE_LSTM.md`) e os números não foram regerados sob o
protocolo atual. **Denominador:** 9.096 linhas validadas na execução
original. `units64_dropout05_atual` é a configuração usada no LSTM
reportado no corpo do artigo.

| variante | units | dropout | n validado | acerto validado | acertos | erros |
|---|---|---|---|---|---|---|
| units64_dropout05_atual | 64 | 0,5 | 9096 | 0,8635 | 7854 | 1242 |
| units128_dropout03 | 128 | 0,3 | 9096 | 0,8603 | 7825 | 1271 |
| units128_dropout05 | 128 | 0,5 | 9096 | 0,8497 | 7729 | 1367 |
| units64_dropout03 | 64 | 0,3 | 9096 | 0,8459 | 7694 | 1402 |

```{=latex}
\FloatBarrier
```

## Tabela S4 — KFold por linha *versus* GroupKFold por grupo textual

**Fonte:** `04_artigo/figuras/comparacao_kfold_groupkfold.json`
(`src/comparacao_kfold_groupkfold.py`). Base de 01/08/2026, com 14.094
chamados, anterior ao congelamento em 14.060; alvo é a categoria histórica,
não a referência humana revisada; não carrega `hash_corpus`. Mede o efeito
de vazamento textual entre treino e teste quando o particionamento ignora
grupos de texto normalizado idêntico — a mesma sensibilidade citada em
prosa na Subseção 4.5 (ganho espúrio entre 0,89 e 1,84 ponto percentual).
**Coluna `delta`:** acurácia sob KFold menos acurácia sob GroupKFold, por
modelo.

| modelo | acuracia kfold | acuracia groupkfold | delta | macro f1 kfold | macro f1 groupkfold |
|---|---|---|---|---|---|
| naive_bayes | 0,6969 | 0,688 | 0,0089 | 0,2004 | 0,1815 |
| regressao_logistica | 0,7645 | 0,7517 | 0,0128 | 0,5415 | 0,4979 |
| linear_svc | 0,8004 | 0,7852 | 0,0152 | 0,5691 | 0,5178 |
| sgd | 0,7717 | 0,761 | 0,0107 | 0,5346 | 0,4878 |
| extra_trees | 0,7841 | 0,7686 | 0,0155 | 0,4884 | 0,4158 |
| random_forest | 0,7779 | 0,7595 | 0,0184 | 0,4591 | 0,377 |
| lstm | 0,6836 | 0,6726 | 0,011 | 0,3556 | 0,3302 |

```{=latex}
\FloatBarrier
```

## Tabela S5 — Holdout exploratório do BERTimbau

**Fonte:** avaliação held-out complementar do BERTimbau, citada em prosa na
Subseção 4.5. **Trilha:** experimento exploratório, não comparável à rodada
canônica: não cobre o corpus probabilisticamente, usa subamostragem
estratificada com parada antecipada e não carrega `hash_corpus`. Não foi
localizado neste repositório, sob controle de versão, um script gerador
correspondente a este nome de arquivo; o conteúdo do CSV foi preservado
byte a byte nesta rodada, apenas renomeado de S6 para S5 na renumeração
contínua. **Denominador:** lote de 1.000 chamados, dos quais 983 possuem
referência humana revisada (coluna `protocolo`, omitida da tabela impressa
por ser constante em todas as linhas — o texto está acima). `acerto_referencia`
é o acerto contra a referência humana revisada; `concordancia_historica`, a
concordância com a categoria histórica.

| modelo | concordancia historica | acerto referencia | ic95 min | ic95 max |
|---|---|---|---|---|
| BERTimbau | 0,6650 | 0,6785 | 0,6490 | 0,7060 |
| LinearSVC | 0,6500 | 0,6734 | 0,6450 | 0,7019 |
| Regressao Logistica | 0,6210 | 0,6511 | 0,6236 | 0,6816 |
| SGD | 0,6210 | 0,6511 | 0,6205 | 0,6806 |
| Extra Trees | 0,5950 | 0,6022 | 0,5727 | 0,6328 |
| Random Forest | 0,5880 | 0,6002 | 0,5717 | 0,6307 |
| Naive Bayes | 0,5230 | 0,5209 | 0,4903 | 0,5493 |
| LSTM | 0,4560 | 0,4802 | 0,4486 | 0,5107 |

```{=latex}
\FloatBarrier
```

## Tabela S6 — Dispersão das predições

**Fonte:** `docs/dados/comparacao_historica.json`, rodada canônica
(`hash_corpus` `1e4762438a7e...`). **Denominador:** 13.972 linhas
avaliadas, 41 categorias com suporte. `entropia_normalizada` mede a
dispersão das predições de cada modelo entre as categorias;
`js_contra_o_historico`, a divergência de Jensen-Shannon entre a
distribuição de predições do modelo e a distribuição da categoria
histórica.

| modelo | categorias previstas | entropia normalizada | js contra o historico |
|---|---|---|---|
| LSTM | 41 | 0,8362 | 0,0167 |
| Regressao Logistica | 41 | 0,8045 | 0,0127 |
| SGD | 41 | 0,8023 | 0,0092 |
| LinearSVC | 41 | 0,79 | 0,0055 |
| Extra Trees | 39 | 0,7466 | 0,0087 |
| Random Forest | 39 | 0,7403 | 0,0117 |
| Naive Bayes | 22 | 0,6131 | 0,0652 |

```{=latex}
\FloatBarrier
```

## Tabela S7 — Curva ABC global, acurácia e macro-F1 por modelo

**Fonte:** `docs/dados/recortes_canonicos.json`, rodada canônica. As linhas
com `modelo = LinearSVC` correspondem aos números citados em prosa na
Subseção 4.5 (classe A com 81,83% do volume; macro-F1 de 0,8207 em A contra
0,5018 em C). **Denominador:** 13.972 linhas avaliadas.

| modelo | classe | categorias | chamados | proporcao do volume | acuracia | macro f1 |
|---|---|---|---|---|---|---|
| Extra Trees | A | 12 | 11433 | 0,8183 | 0,8488 | 0,7978 |
| Extra Trees | B | 12 | 1912 | 0,1368 | 0,6778 | 0,7447 |
| Extra Trees | C | 17 | 627 | 0,0449 | 0,4466 | 0,4455 |
| LinearSVC | A | 12 | 11433 | 0,8183 | 0,8539 | 0,8207 |
| LinearSVC | B | 12 | 1912 | 0,1368 | 0,7416 | 0,7521 |
| LinearSVC | C | 17 | 627 | 0,0449 | 0,5582 | 0,5018 |
| LSTM | A | 12 | 11433 | 0,8183 | 0,7586 | 0,7435 |
| LSTM | B | 12 | 1912 | 0,1368 | 0,636 | 0,6356 |
| LSTM | C | 17 | 627 | 0,0449 | 0,4673 | 0,2903 |
| Naive Bayes | A | 12 | 11433 | 0,8183 | 0,8239 | 0,688 |
| Naive Bayes | B | 12 | 1912 | 0,1368 | 0,2291 | 0,2527 |
| Naive Bayes | C | 17 | 627 | 0,0449 | 0,0718 | 0,0477 |
| Random Forest | A | 12 | 11433 | 0,8183 | 0,8388 | 0,7839 |
| Random Forest | B | 12 | 1912 | 0,1368 | 0,6658 | 0,7312 |
| Random Forest | C | 17 | 627 | 0,0449 | 0,4338 | 0,4141 |
| Regressao Logistica | A | 12 | 11433 | 0,8183 | 0,8203 | 0,8003 |
| Regressao Logistica | B | 12 | 1912 | 0,1368 | 0,7814 | 0,7545 |
| Regressao Logistica | C | 17 | 627 | 0,0449 | 0,5981 | 0,5158 |
| SGD | A | 12 | 11433 | 0,8183 | 0,8263 | 0,8025 |
| SGD | B | 12 | 1912 | 0,1368 | 0,7746 | 0,7549 |
| SGD | C | 17 | 627 | 0,0449 | 0,6045 | 0,5091 |

```{=latex}
\FloatBarrier
```

## Tabela S8 — Tarefa de tipo de manutenção

**Fonte:** `docs/dados/recortes_canonicos.json`, rodada canônica.
Desempenho de cada modelo na tarefa projetada de distinguir preventiva,
corretiva e não manutenção. **Denominador:** 13.972 linhas avaliadas.

| modelo | acuracia | macro f1 | f1 preventiva | f1 corretiva | f1 nao manutencao |
|---|---|---|---|---|---|
| Extra Trees | 0,9497 | 0,7999 | 0,9762 | 0,9596 | 0,4638 |
| Random Forest | 0,949 | 0,7907 | 0,9762 | 0,9592 | 0,4367 |
| LinearSVC | 0,9443 | 0,818 | 0,9742 | 0,9547 | 0,525 |
| Naive Bayes | 0,9421 | 0,7298 | 0,9662 | 0,9548 | 0,2684 |
| SGD | 0,9355 | 0,8173 | 0,9718 | 0,947 | 0,533 |
| Regressao Logistica | 0,9317 | 0,8116 | 0,9715 | 0,9437 | 0,5196 |
| LSTM | 0,8999 | 0,7403 | 0,9559 | 0,9172 | 0,3478 |

```{=latex}
\FloatBarrier
```

## Tabela S9 — Curva ABC interna a cada tipo (LinearSVC)

**Fonte:** `docs/dados/recortes_canonicos.json`, rodada canônica, recorte
do modelo de referência (LinearSVC). Diferente da Tabela S7: aqui a classe
ABC é calculada dentro de cada tipo de manutenção (`proporcao_do_volume_do_tipo`),
não sobre o volume global — a mesma distinção declarada na Subseção 4.5 do
artigo entre curva ABC global e curva ABC interna ao tipo. **Denominador:**
13.972 linhas avaliadas, particionadas pelos três tipos de manutenção.

| tipo | classe | categorias | chamados | proporcao do volume do tipo | acuracia | macro f1 |
|---|---|---|---|---|---|---|
| Preventiva | A | 4 | 4091 | 0,8346 | 0,9897 | 0,9727 |
| Preventiva | B | 4 | 630 | 0,1285 | 0,9556 | 0,9645 |
| Preventiva | C | 5 | 181 | 0,0369 | 0,5193 | 0,5071 |
| Corretiva | A | 7 | 6937 | 0,8176 | 0,7921 | 0,7835 |
| Corretiva | B | 5 | 1128 | 0,1329 | 0,6365 | 0,6357 |
| Corretiva | C | 9 | 420 | 0,0495 | 0,7286 | 0,6614 |
| Não manutenção | A | 4 | 521 | 0,8906 | 0,4952 | 0,5184 |
| Não manutenção | B | 2 | 51 | 0,0872 | 0,1569 | 0,1702 |
| Não manutenção | C | 1 | 13 | 0,0222 | 0,0769 | 0,0909 |

```{=latex}
\FloatBarrier
```

## Tabela S10 — Camada de regras de periodicidade *versus* modelo puro

**Fonte:** `docs/dados/regras_versus_modelos.json`, rodada canônica.
Compara cada modelo puro ao híbrido com a camada de regras de
periodicidade preventiva, nos disparos em que a regra se aplica. Dividida
em duas partes por largura de página: (a) acurácia e macro-F1, puros e
híbridos; (b) disparos, conflitos e a quem cada conflito favorece.
**Denominador:** 4.487 disparos da regra sobre as 13.972 linhas avaliadas.

**(a) Acurácia e macro-F1**

| modelo | acuracia pura | acuracia hibrida | macro f1 puro | macro f1 hibrido | delta macro f1 |
|---|---|---|---|---|---|
| Regressao Logistica | 0,805 | 0,806 | 0,6689 | 0,6686 | -0,0003 |
| LinearSVC | 0,8253 | 0,8252 | 0,6684 | 0,6667 | -0,0017 |
| SGD | 0,8093 | 0,81 | 0,6669 | 0,6676 | 0,0007 |
| Extra Trees | 0,8073 | 0,8077 | 0,6362 | 0,6324 | -0,0038 |
| Random Forest | 0,797 | 0,7975 | 0,6152 | 0,6114 | -0,0038 |
| LSTM | 0,7287 | 0,7305 | 0,524 | 0,5267 | 0,0027 |
| Naive Bayes | 0,7088 | 0,7225 | 0,2951 | 0,3537 | 0,0586 |

**(b) Disparos e conflitos**

| modelo | disparos | conflitos | regra acerta | modelo acerta |
|---|---|---|---|---|
| Regressao Logistica | 4487 | 47 | 27 | 14 |
| LinearSVC | 4487 | 31 | 11 | 13 |
| SGD | 4487 | 45 | 25 | 15 |
| Extra Trees | 4487 | 47 | 22 | 17 |
| Random Forest | 4487 | 48 | 23 | 16 |
| LSTM | 4487 | 53 | 31 | 7 |
| Naive Bayes | 4487 | 219 | 201 | 9 |

```{=latex}
\FloatBarrier
```

## Tabela S11 — Inferência pareada agrupada

**Fonte:** `docs/dados/inferencia_agrupada.json`, rodada canônica. Os 21
pares completos entre os sete modelos, que o corpo do artigo resume em seis
linhas (Subseção 4.2). Unidade de análise: grupo de texto normalizado
idêntico, não a linha (`04_artigo/README.md`, "Regra estatística
obrigatória"). Dividida em duas partes por largura de página: (a)
diferença de acurácia, intervalo de confiança e grupos a favor de cada
modelo; (b) tamanho de efeito pareado, *p* permutacional, *p* ajustado por
Holm e significância. **Denominador:** 9.735 grupos textuais no recorte de
13.972 linhas avaliadas.

**(a) Diferença de acurácia e grupos a favor**

| modelo 1 | modelo 2 | diferenca de acuracia | ic95 min | ic95 max | grupos a favor do 1 | grupos a favor do 2 | grupos empatados |
|---|---|---|---|---|---|---|---|
| LinearSVC | Naive Bayes | 0,1165 | 0,1028 | 0,1329 | 1961 | 549 | 7225 |
| SGD | Naive Bayes | 0,1005 | 0,0871 | 0,1163 | 1924 | 737 | 7074 |
| Extra Trees | Naive Bayes | 0,0986 | 0,0856 | 0,1141 | 1636 | 468 | 7631 |
| LinearSVC | LSTM | 0,0966 | 0,0875 | 0,1061 | 1682 | 349 | 7704 |
| Regressao Logistica | Naive Bayes | 0,0963 | 0,0826 | 0,1121 | 1970 | 842 | 6923 |
| Random Forest | Naive Bayes | 0,0882 | 0,0753 | 0,1035 | 1559 | 540 | 7636 |
| SGD | LSTM | 0,0805 | 0,0724 | 0,0891 | 1537 | 429 | 7769 |
| Extra Trees | LSTM | 0,0786 | 0,0704 | 0,0873 | 1622 | 533 | 7580 |
| Regressao Logistica | LSTM | 0,0763 | 0,0684 | 0,0846 | 1505 | 456 | 7774 |
| Random Forest | LSTM | 0,0682 | 0,0604 | 0,0763 | 1555 | 615 | 7565 |
| LinearSVC | Random Forest | 0,0283 | 0,0229 | 0,0341 | 896 | 503 | 8336 |
| LinearSVC | Regressao Logistica | 0,0203 | 0,0156 | 0,0248 | 598 | 314 | 8823 |
| LinearSVC | Extra Trees | 0,018 | 0,013 | 0,0232 | 759 | 515 | 8461 |
| LinearSVC | SGD | 0,016 | 0,0118 | 0,0204 | 533 | 308 | 8894 |
| SGD | Random Forest | 0,0123 | 0,0071 | 0,0176 | 767 | 599 | 8369 |
| Extra Trees | Random Forest | 0,0104 | 0,0073 | 0,0134 | 301 | 152 | 9282 |
| SGD | Regressao Logistica | 0,0042 | 0,0019 | 0,0067 | 161 | 102 | 9472 |
| LSTM | Naive Bayes | 0,02 | 0,0068 | 0,0352 | 1487 | 1408 | 6840 |
| Regressao Logistica | Random Forest | 0,0081 | 0,0025 | 0,0135 | 803 | 694 | 8238 |
| Extra Trees | Regressao Logistica | 0,0023 | -0,0031 | 0,0079 | 718 | 678 | 8339 |
| SGD | Extra Trees | 0,0019 | -0,0031 | 0,0072 | 643 | 624 | 8468 |

**(b) Tamanho de efeito e significância**

| modelo 1 | modelo 2 | d pareado por grupo | p permutacional | p ajustado holm | significativo | p ajustado holm por linha |
|---|---|---|---|---|---|---|
| LinearSVC | Naive Bayes | 0,1644 | 0,0001 | 0,0021 | sim | 0,0 |
| SGD | Naive Bayes | 0,1402 | 0,0001 | 0,0021 | sim | 0,0 |
| Extra Trees | Naive Bayes | 0,1413 | 0,0001 | 0,0021 | sim | 0,0 |
| LinearSVC | LSTM | 0,3133 | 0,0001 | 0,0021 | sim | 0,0 |
| Regressao Logistica | Naive Bayes | 0,1332 | 0,0001 | 0,0021 | sim | 0,0 |
| Random Forest | Naive Bayes | 0,1263 | 0,0001 | 0,0021 | sim | 0,0 |
| SGD | LSTM | 0,261 | 0,0001 | 0,0021 | sim | 0,0 |
| Extra Trees | LSTM | 0,2428 | 0,0001 | 0,0021 | sim | 0,0 |
| Regressao Logistica | LSTM | 0,2467 | 0,0001 | 0,0021 | sim | 0,0 |
| Random Forest | LSTM | 0,2094 | 0,0001 | 0,0021 | sim | 0,0 |
| LinearSVC | Random Forest | 0,1076 | 0,0001 | 0,0021 | sim | 0,0 |
| LinearSVC | Regressao Logistica | 0,0941 | 0,0001 | 0,0021 | sim | 0,0 |
| LinearSVC | Extra Trees | 0,0707 | 0,0001 | 0,0021 | sim | 0,0 |
| LinearSVC | SGD | 0,0774 | 0,0001 | 0,0021 | sim | 0,0 |
| SGD | Random Forest | 0,0467 | 0,0001 | 0,0021 | sim | 2,1e-05 |
| Extra Trees | Random Forest | 0,0679 | 0,0001 | 0,0021 | sim | 0,0 |
| SGD | Regressao Logistica | 0,0369 | 0,0007 | 0,0035 | sim | 0,0014 |
| LSTM | Naive Bayes | 0,0272 | 0,0042 | 0,0164 | sim | 4e-06 |
| Regressao Logistica | Random Forest | 0,0293 | 0,0041 | 0,0164 | sim | 0,0120 |
| Extra Trees | Regressao Logistica | 0,0085 | 0,4212 | 0,8423 | nao | 0,8194 |
| SGD | Extra Trees | 0,0076 | 0,4771 | 0,8423 | nao | 0,8194 |

```{=latex}
\FloatBarrier
```

## Tabela S12 — Macro-F1 sob três convenções de denominador

**Fonte:** `docs/dados/sensibilidade_classes_raras.json`, rodada canônica.
Recalcula o macro-F1 sob três universos de categorias: `macro_f1_41_avaliadas`
(as 41 categorias com suporte na rodada canônica), `macro_f1_50_taxonomia`
(as 50 categorias declaradas pelo autor, incluindo as sem suporte
observado) e `macro_f1_14_familias` (14 famílias de categoria agregadas).
**Denominador:** 13.972 linhas avaliadas; a acurácia não varia entre
convenções, apenas o macro-F1.

| modelo | acuracia | macro f1 41 avaliadas | macro f1 50 taxonomia | macro f1 14 familias |
|---|---|---|---|---|
| Regressao Logistica | 0,805 | 0,6689 | 0,5485 | 0,6801 |
| LinearSVC | 0,8253 | 0,6684 | 0,5481 | 0,6816 |
| SGD | 0,8093 | 0,6669 | 0,5469 | 0,673 |
| Extra Trees | 0,8073 | 0,6362 | 0,5217 | 0,6548 |
| Random Forest | 0,797 | 0,6152 | 0,5044 | 0,6346 |
| LSTM | 0,7287 | 0,524 | 0,4297 | 0,524 |
| Naive Bayes | 0,7088 | 0,2951 | 0,242 | 0,3626 |

```{=latex}
\FloatBarrier
```

## Tabela S13 — Utilidade da reclassificação sob custos assimétricos

**Fonte:** `docs/dados/utilidade_reclassificacao.json`, rodada canônica.
`ganho_liquido_simples` é `corrigidos − prejudicados`, o resultado principal
citado no corpo, sob a suposição de custos iguais; as demais colunas
qualificam esse resultado sob custos assimétricos, sem substituí-lo.
Dividida em três partes por largura de página: (a) contadores e ganho
líquido simples, com `rho_de_equilibrio` (razão de custo em que o ganho
líquido zera); (b) utilidade da aplicação direta sob cinco valores de
$\rho$; (c) triagem por divergência entre modelo e categoria histórica,
com a fila resultante, sua precisão e a utilidade sob quatro valores de
$\lambda$. **Denominador:** 13.972 linhas avaliadas.

**(a) Contadores e ganho líquido**

| modelo | corrigidos | prejudicados | neutros | ganho liquido simples | rho de equilibrio |
|---|---|---|---|---|---|
| LinearSVC | 475 | 2321 | 53 | -1846 | 0,2047 |
| SGD | 489 | 2559 | 52 | -2070 | 0,1911 |
| Extra Trees | 422 | 2519 | 71 | -2097 | 0,1675 |
| Regressao Logistica | 492 | 2621 | 48 | -2129 | 0,1877 |
| Random Forest | 416 | 2658 | 74 | -2242 | 0,1565 |
| LSTM | 426 | 3621 | 121 | -3195 | 0,1176 |
| Naive Bayes | 309 | 3783 | 164 | -3474 | 0,0817 |

**(b) Utilidade da aplicação direta por $\rho$**

| modelo | U direta rho 0.25 | U direta rho 0.5 | U direta rho 1 | U direta rho 2 | U direta rho 4 |
|---|---|---|---|---|---|
| LinearSVC | -105,2 | -685,5 | -1846,0 | -4167,0 | -8809,0 |
| SGD | -150,8 | -790,5 | -2070,0 | -4629,0 | -9747,0 |
| Extra Trees | -207,8 | -837,5 | -2097,0 | -4616,0 | -9654,0 |
| Regressao Logistica | -163,2 | -818,5 | -2129,0 | -4750,0 | -9992,0 |
| Random Forest | -248,5 | -913,0 | -2242,0 | -4900,0 | -10216,0 |
| LSTM | -479,2 | -1384,5 | -3195,0 | -6816,0 | -14058,0 |
| Naive Bayes | -636,8 | -1582,5 | -3474,0 | -7257,0 | -14823,0 |

**(c) Triagem por divergência**

| modelo | fila de triagem | precisao da fila | U triagem lambda 0 | U triagem lambda 0.05 | U triagem lambda 0.1 | U triagem lambda 0.2 |
|---|---|---|---|---|---|---|
| LinearSVC | 2849 | 0,1853 | 528,0 | 385,5 | 243,1 | -41,8 |
| SGD | 3100 | 0,1745 | 541,0 | 386,0 | 231,0 | -79,0 |
| Extra Trees | 3012 | 0,1637 | 493,0 | 342,4 | 191,8 | -109,4 |
| Regressao Logistica | 3161 | 0,1708 | 540,0 | 381,9 | 223,9 | -92,2 |
| Random Forest | 3148 | 0,1557 | 490,0 | 332,6 | 175,2 | -139,6 |
| LSTM | 4168 | 0,1312 | 547,0 | 338,6 | 130,2 | -286,6 |
| Naive Bayes | 4256 | 0,1111 | 473,0 | 260,2 | 47,4 | -378,2 |

```{=latex}
\FloatBarrier
```

## Tabela S14 — Pressupostos estatísticos secundários

**Fonte:** `docs/dados/inferencia_canonica.json`, rodada canônica.
Verificações que não decidem a comparação pareada principal entre
classificadores e por isso não integram o corpo do artigo (normalidade de
Shapiro-Wilk, variância da confiança, VIF entre confianças, correlação de
Spearman e ponto-bisserial entre confiança e acerto). Publicadas aqui por
terem sido calculadas; `04_artigo/README.md` ("Regra estatística
obrigatória") registra que nenhuma delas deve ser lida como prova de
calibração ou como justificativa de escolha de modelo. Dividida em duas
partes por largura de página: (a) normalidade, variância e VIF; (b)
correlações entre confiança e acerto. **Denominador:** 13.972 linhas
avaliadas.

**(a) Normalidade, variância e VIF**

| modelo | shapiro w | shapiro p | rejeita normalidade | variancia da confianca | vif |
|---|---|---|---|---|---|
| Extra Trees | 0,8606 | 5,81e-55 | sim | 0,0723 | 20,784 |
| LinearSVC | 0,9209 | 2,41e-45 | sim | 0,0046 | 4,208 |
| LSTM | 0,8211 | 1,67e-59 | sim | 0,0834 | 3,109 |
| Naive Bayes | 0,8335 | 3,55e-58 | sim | 0,0846 | 4,016 |
| Random Forest | 0,8633 | 1,3e-54 | sim | 0,0764 | 22,322 |
| Regressao Logistica | 0,87 | 9,89e-54 | sim | 0,1078 | 26,91 |
| SGD | 0,9057 | 3,11e-48 | sim | 0,0903 | 29,984 |

**(b) Correlações confiança-acerto**

| modelo | spearman confianca acerto | pointbiserial confianca acerto |
|---|---|---|
| Extra Trees | 0,5272 | 0,5569 |
| LinearSVC | 0,485 | 0,45 |
| LSTM | 0,616 | 0,656 |
| Naive Bayes | 0,6077 | 0,6277 |
| Random Forest | 0,5391 | 0,5644 |
| Regressao Logistica | 0,4809 | 0,4819 |
| SGD | 0,4941 | 0,4847 |

```{=latex}
\FloatBarrier
```

## Tabela S15 — Calibração completa dos sete modelos

**Fonte:** `docs/dados/calibracao_canonica.json`, rodada canônica. O corpo
do artigo (Tabela 4) mostra uma versão reduzida, com os quatro modelos mais
competitivos em acurácia e sem o Random Forest; esta tabela traz os sete,
incluindo Naive Bayes e LSTM, cujo ECE aumenta após a calibração isotônica
(Subseção 4.3). Dividida em duas partes por largura de página: (a) ECE e
Brier, brutos e calibrados; (b) automação seletiva ao alvo de 0,95.
**Denominador:** 13.972 linhas avaliadas, cinco dobras com limiar de
automação seletiva calculado.

**(a) ECE e Brier**

| modelo | ece bruto | ece calibrado | brier bruto | brier calibrado |
|---|---|---|---|---|
| LinearSVC | 0,6925 | 0,0178 | 0,6052 | 0,1034 |
| SGD | 0,3046 | 0,0109 | 0,223 | 0,1124 |
| Extra Trees | 0,0859 | 0,0108 | 0,1171 | 0,1057 |
| Regressao Logistica | 0,2351 | 0,0189 | 0,1946 | 0,1173 |
| Random Forest | 0,0913 | 0,0145 | 0,1211 | 0,1082 |
| LSTM | 0,0158 | 0,0479 | 0,1126 | 0,1221 |
| Naive Bayes | 0,0144 | 0,0206 | 0,1252 | 0,128 |

**(b) Automação seletiva**

| modelo | cobertura alvo 0 95 | acuracia seletiva alvo 0 95 | dobras com limiar |
|---|---|---|---|
| LinearSVC | 0,689 | 0,9464 | 5 |
| SGD | 0,6162 | 0,9531 | 5 |
| Extra Trees | 0,6732 | 0,9502 | 5 |
| Regressao Logistica | 0,6237 | 0,9415 | 5 |
| Random Forest | 0,658 | 0,9495 | 5 |
| LSTM | 0,6545 | 0,921 | 5 |
| Naive Bayes | 0,5518 | 0,9306 | 5 |

```{=latex}
\FloatBarrier
```

## Tabela S16 — Fase 2C: LinearSVC *versus* combinações de *ensemble*

**Fonte:** manifesto confirmatório da Execução Científica 1 da Fase 2C
(`docs/dados/ensemble/fase2c/fase2c_execucao_cientifica_1_manifest.json`),
lido por `src/tabelas_suplementares_canonicas.py`, que valida universo
modelável, denominador, capacidade da fila e proveniência da Fase 2B antes
de gravar qualquer valor, e aborta em caso de divergência. **Trilha
própria:** não pertence à rodada canônica do artigo principal e não carrega
`hash_corpus`; nenhum valor desta tabela foi recalculado, todos vêm lidos
diretamente do manifesto já congelado. Compara o LinearSVC a três
combinações (votação majoritária, votação suave ponderada, *stacking*) em
fila de igual capacidade `K`, agregado e por dobra externa (`outer_fold`).
Nenhuma combinação supera o LinearSVC no agregado (Subseção 4.5, Tabela 5
do corpo); o único ganho local, do *stacking* na terceira dobra (123
capturados contra 119), não se sustenta fora dela. Dividida em duas partes
por largura de página: (a) contexto e desfecho de cada método; (b)
diferença contra o LinearSVC do mesmo escopo/dobra. **Denominador:** 13.970
registros modeláveis, 593 divergências entre categoria histórica e
referência revisada (`y1_denominador`).

**(a) Contexto e desfecho**

| escopo | outer fold | metodo | K | y1 denominador | capturados | precisao | recall |
|---|---|---|---|---|---|---|---|
| agregado |  | LinearSVC | 2840 | 593 | 523 | 0,1842 | 0,8820 |
| agregado |  | Votacao majoritaria | 2840 | 593 | 516 | 0,1817 | 0,8702 |
| agregado |  | Votacao suave ponderada | 2840 | 593 | 503 | 0,1771 | 0,8482 |
| agregado |  | Stacking | 2840 | 593 | 512 | 0,1803 | 0,8634 |
| fold | 1 | LinearSVC | 564 | 124 | 104 | 0,1844 | 0,8387 |
| fold | 1 | Votacao majoritaria | 564 | 124 | 102 | 0,1809 | 0,8226 |
| fold | 1 | Votacao suave ponderada | 564 | 124 | 97 | 0,1720 | 0,7823 |
| fold | 1 | Stacking | 564 | 124 | 101 | 0,1791 | 0,8145 |
| fold | 2 | LinearSVC | 560 | 95 | 85 | 0,1518 | 0,8947 |
| fold | 2 | Votacao majoritaria | 560 | 95 | 85 | 0,1518 | 0,8947 |
| fold | 2 | Votacao suave ponderada | 560 | 95 | 82 | 0,1464 | 0,8632 |
| fold | 2 | Stacking | 560 | 95 | 82 | 0,1464 | 0,8632 |
| fold | 3 | LinearSVC | 616 | 135 | 119 | 0,1932 | 0,8815 |
| fold | 3 | Votacao majoritaria | 616 | 135 | 117 | 0,1899 | 0,8667 |
| fold | 3 | Votacao suave ponderada | 616 | 135 | 118 | 0,1916 | 0,8741 |
| fold | 3 | Stacking | 616 | 135 | 123 | 0,1997 | 0,9111 |
| fold | 4 | LinearSVC | 507 | 113 | 102 | 0,2012 | 0,9027 |
| fold | 4 | Votacao majoritaria | 507 | 113 | 100 | 0,1972 | 0,8850 |
| fold | 4 | Votacao suave ponderada | 507 | 113 | 98 | 0,1933 | 0,8673 |
| fold | 4 | Stacking | 507 | 113 | 98 | 0,1933 | 0,8673 |
| fold | 5 | LinearSVC | 593 | 126 | 113 | 0,1906 | 0,8968 |
| fold | 5 | Votacao majoritaria | 593 | 126 | 112 | 0,1889 | 0,8889 |
| fold | 5 | Votacao suave ponderada | 593 | 126 | 108 | 0,1821 | 0,8571 |
| fold | 5 | Stacking | 593 | 126 | 108 | 0,1821 | 0,8571 |

**(b) Diferença contra o LinearSVC**

| escopo | outer fold | metodo | diff capturados vs linear svc | diff precisao vs linear svc | diff recall vs linear svc |
|---|---|---|---|---|---|
| agregado |  | LinearSVC | 0 | 0,0 | 0,0 |
| agregado |  | Votacao majoritaria | -7 | -0,0025 | -0,0118 |
| agregado |  | Votacao suave ponderada | -20 | -0,0070 | -0,0337 |
| agregado |  | Stacking | -11 | -0,0039 | -0,0185 |
| fold | 1 | LinearSVC | 0 | 0,0 | 0,0 |
| fold | 1 | Votacao majoritaria | -2 | -0,0035 | -0,0161 |
| fold | 1 | Votacao suave ponderada | -7 | -0,0124 | -0,0565 |
| fold | 1 | Stacking | -3 | -0,0053 | -0,0242 |
| fold | 2 | LinearSVC | 0 | 0,0 | 0,0 |
| fold | 2 | Votacao majoritaria | 0 | 0,0 | 0,0 |
| fold | 2 | Votacao suave ponderada | -3 | -0,0054 | -0,0316 |
| fold | 2 | Stacking | -3 | -0,0054 | -0,0316 |
| fold | 3 | LinearSVC | 0 | 0,0 | 0,0 |
| fold | 3 | Votacao majoritaria | -2 | -0,0032 | -0,0148 |
| fold | 3 | Votacao suave ponderada | -1 | -0,0016 | -0,0074 |
| fold | 3 | Stacking | 4 | 0,0065 | 0,0296 |
| fold | 4 | LinearSVC | 0 | 0,0 | 0,0 |
| fold | 4 | Votacao majoritaria | -2 | -0,0039 | -0,0177 |
| fold | 4 | Votacao suave ponderada | -4 | -0,0079 | -0,0354 |
| fold | 4 | Stacking | -4 | -0,0079 | -0,0354 |
| fold | 5 | LinearSVC | 0 | 0,0 | 0,0 |
| fold | 5 | Votacao majoritaria | -1 | -0,0017 | -0,0079 |
| fold | 5 | Votacao suave ponderada | -5 | -0,0084 | -0,0397 |
| fold | 5 | Stacking | -5 | -0,0084 | -0,0397 |

```{=latex}
\FloatBarrier
```

## Proveniência deste documento

- Nenhum modelo foi retreinado, ajustado ou reavaliado para compor este
  material; todas as tabelas reproduzem artefatos já existentes no
  repositório antes desta rodada.
- As Tabelas S1 a S4 (legado, pré-congelamento) e a Tabela S5
  (exploratório, BERTimbau) não carregam `hash_corpus` e não são
  comparáveis, linha a linha, aos números do corpo do artigo.
- As Tabelas S6 a S15 carregam `hash_corpus`
  `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`,
  conferido por `python src/matriz_proveniencia.py` sem divergência.
- A Tabela S16 vem do manifesto confirmatório da Fase 2C, trilha
  experimental própria, validada por proveniência (universo, denominador,
  capacidade e origem da Fase 2B) em vez de `hash_corpus`.
- Detalhamento completo da renumeração S5–S17 para S4–S16 e da
  consolidação deste documento: pasta `docs`, arquivo
  `AUDITORIA_MATERIAL_SUPLEMENTAR.md`.
