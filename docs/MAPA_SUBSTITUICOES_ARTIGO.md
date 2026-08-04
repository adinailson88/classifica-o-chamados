# Mapa de substituições no artigo

Trabalho de apoio à revisão editorial do Passo 10. Lista, linha a linha, os números da execução legada localizados em `04_artigo/artigo_classificacao_chamados_v3.md` e o valor correspondente na rodada canônica `3aa42e31`.

**Este documento não substitui nada.** Trocar número em texto científico é decisão do autor, e várias linhas exigem julgamento que a varredura automática não faz.

## O ponto que exige atenção antes de começar

O `14.058` do artigo não tem um substituto único. Ele vira **um de dois números**, conforme o que a frase afirma:

| Se a frase fala de | Use | Por quê |
|---|---:|---|
| tamanho do corpus, base experimental, cobertura da conferência humana | **14.060** | é a base congelada, com referência humana em todos os registros |
| denominador de métrica, linhas avaliadas, `n =` de tabela | **13.972** | 88 linhas de nove categorias sem suporte ficaram fora das partições |

Confundir os dois produz denominadores que não fecham entre si, que é exatamente o defeito que a rodada canônica eliminou.

## Substituições diretas

Troca de número, sem mudar o argumento.

| Linha | Trecho atual | Substituir por | Tipo |
|---:|---|---|---|
| 79 | `utiliza 14.058 chamados não vazios` | 14.060 | corpus |
| 89 | `apurado sobre as 14.058 decisões` | 13.972 | denominador |
| 120 | `uses 14,058 non-empty records` | 14,060 | corpus, abstract |
| 129 | `14,058 decisions rather than over a sample` | 13,972 | denominador, abstract |
| 231 | `A base experimental contém 14.058 chamados` | 14.060 | corpus |
| 434 | `O corpus experimental é composto por 14.058` | 14.060 | corpus |
| 451 | `totaliza 14.058 registros elegíveis` | 14.060 | corpus |
| 722 | `cobrir a totalidade do corpus: os 14.058` | 14.060 | cobertura |
| 824 | `A base elegível contém 14.058 chamados` | 14.060 | corpus |
| 825 | `conferência humana cobre a totalidade dos 14.058` | 14.060 | cobertura |
| 845 | `14.058, com intervalo de confiança por bootstrap a 95%` | 13.972 | denominador |
| 850 | `predições *out-of-fold* sobre as 14.058 linhas` | 13.972 | denominador |
| 866 | `**Tabela 1** ... (n = 14.058)` | 13.972 | denominador |
| 896 | `utiliza os 14.058` | 13.972 | denominador |
| 928 | `**Tabela 2** ... (n = 14.058)` | 13.972 | denominador |
| 987 | `os 14.058 chamados do corpus` | 14.060 | corpus |
| 1013 | `14.058 no total, todos com conferência humana` | 14.060 | cobertura |
| 1224 | `curva real de aprendizado do LSTM sobre os 14.058` | 13.972 | denominador |
| 1400 | `**Tabela 8** ... (n = 14.058` | 13.972 | denominador |
| 1444 | `14.058). P, preventiva; C, corretiva; NM` | 13.972 | denominador |
| 1712 | `avaliação integral dos 14.058 chamados` | 13.972 | denominador |
| 2004 | `dos 14.058 chamados, ordenadas por frequência` | 13.972 | denominador, apêndice |
| 2062 | `interna ao tipo (n = 14.058)` | 13.972 | denominador, apêndice |
| 1375 | `suporte das 56 categorias` | 41 categorias | taxonomia |
| 1401 | `56 categorias com suporte na referência validada` | 41 categorias | taxonomia |
| 1463 | `obtida na tarefa de 56 categorias` | 41 categorias | taxonomia |

## Substituições que arrastam outro número junto

Aqui não basta trocar o denominador: o valor associado também mudou.

| Linha | Trecho atual | O que muda |
|---:|---|---|
| 576 | `dos 14.058 chamados cerca de 11.275 compõem cada partição` | 13.972 chamados e **11.178** por partição de treino |
| 666 | `32,58% das 14.058 linhas` | **32,62%** das 14.060 linhas; a medida do Passo 2 é sobre a base congelada |
| 1262 | `(n = 14.058). O teste de` Cochran Q | 13.972 e **Q = 2669,67**, com 6 graus de liberdade |
| 1543 | `dos 14.058 chamados, ou 4,3%, o avaliador rejeitou` | 14.060 e **4,25%**, correspondendo a 598 correções |

## Linhas que exigem recomputação, não substituição

Nestas, o número legado depende de um cálculo que precisa ser refeito sobre a rodada canônica. Trocar só o denominador produziria valor errado.

| Linha | Trecho atual | O que fazer |
|---:|---|---|
| 1082 | `3.268 dos 14.058 registros (23,4%)` | recalcular a contagem sobre as 13.972 linhas; o numerador não foi reproduzido nesta rodada |
| 1195 | `(n = 14.058), mediana de três execuções em processador de quatro núcleos` | os tempos vêm de `docs/RETREINO_CANONICO.md`, que mede uma execução e não a mediana de três; decidir se mantém o desenho antigo ou adota o novo |
| 1304 | `sobre os 14.058 chamados e envolvendo 59 categorias distintas` | as 59 categorias distintas somam verdade e predição; recontar sobre a rodada canônica |
| 2043 | `**Total geral** \| **14.058**` | tabela de apêndice construída sobre 56 categorias; precisa ser regerada a partir de `docs/dados/recortes_canonicos.json`, não corrigida célula a célula |

## Números novos disponíveis para a redação

Todos com `hash_corpus` `3aa42e31`.

| Grandeza | Valor | Origem |
|---|---|---|
| Corpus congelado | 14.060 | `docs/AUDITORIA_BASE_CANONICA.md` |
| Linhas avaliadas | 13.972 | `docs/PARTICOES_CANONICAS.md` |
| Categorias avaliadas | 41, de 50 | `docs/PARTICOES_CANONICAS.md` |
| Grupos textuais | 9.786 na base, 9.734 nas partições | `docs/GRUPOS_TEXTUAIS.md` |
| Linhas com duplicata | 4.586, ou 32,62% | `docs/GRUPOS_TEXTUAIS.md` |
| Inconsistência interna da referência | 85 linhas em 17 grupos, ou 0,60% | `docs/GRUPOS_TEXTUAIS.md` |
| Melhor acurácia | LinearSVC, 0,8255 [0,8119; 0,8384] | `docs/INFERENCIA_CANONICA.md` |
| Melhor macro-F1 | LinearSVC, 0,6696 [0,6535; 0,6821] | `docs/INFERENCIA_CANONICA.md` |
| Cochran Q | 2669,67, 6 g.l., p ≈ 0 | `docs/INFERENCIA_CANONICA.md` |
| Pares sem diferença após Holm | 3 de 21 | `docs/INFERENCIA_CANONICA.md` |
| Curva ABC, classe A | 12 categorias, 81,82% do volume, macro-F1 0,8210 | `docs/RECORTES_CANONICOS.md` |
| Curva ABC, classe C | 17 categorias, 4,50% do volume, macro-F1 0,5041 | `docs/RECORTES_CANONICOS.md` |
| Tarefa de tipo | Extra Trees, acurácia 0,9499 | `docs/RECORTES_CANONICOS.md` |
| Menor ECE após calibração | Extra Trees, 0,0108 | `docs/CALIBRACAO_CANONICA.md` |
| Automação ao alvo de 0,95 | Extra Trees, cobertura 67,9%, acurácia seletiva 0,9507 | `docs/CALIBRACAO_CANONICA.md` |
| Custo do BERTimbau | 6,44 h por dobra, 32,2 h nas cinco | `docs/CUSTO_BERTIMBAU.md` |

## Limite deste mapa

A varredura encontra o que está registrado em `docs/dados/estatistica.json` mais os totais de corpus e categorias. Números de rodadas intermediárias sem JSON versionado não são alcançados — o `0,8197` e o `0,5523` da consolidação de agosto, por exemplo, estão no texto e não aparecem aqui. As `59 categorias distintas` da linha 1304 só entraram nesta lista porque a linha também citava o total legado.

**A contagem é piso, não teto.** A revisão manual continua necessária, sobretudo nas seções de resultados e discussão.

Os números de linha valem para a versão atual do arquivo. Depois da primeira substituição eles se deslocam; reexecutar `python src/matriz_proveniencia.py` regenera a varredura sobre o texto corrente.
