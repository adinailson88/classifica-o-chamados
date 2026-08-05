# Plano — Artigo/Capítulo “Classificação Automática de Chamados”

Este documento registra somente a estrutura, os critérios editoriais e o estado atual do artigo/capítulo. O plano operacional vigente, os critérios de aceite e o ponto de continuidade estão em [`PLANO_EXECUCAO_ATUAL.md`](PLANO_EXECUCAO_ATUAL.md). Os dois documentos têm finalidades distintas e não devem acumular versões concorrentes do mesmo estado.

Atualizado em 05/08/2026, no fuso America/Bahia (rodada de resultados hierarquizados).

## Regra de uso

Antes de alterar o artigo:

1. ler `CONTEXTO.md`, `PLANO_EXECUCAO_ATUAL.md`, este plano e `04_artigo/README.md`;
2. conferir os timestamps e denominadores dos JSONs utilizados;
3. não reaproveitar números de rodadas antigas sem revalidação;
4. ao concluir uma rodada, substituir a seção “Estado desta rodada”, sem acumular histórico;
5. não reescrever resultados ou conclusões antes do fechamento da nova execução canônica.

## Escopo científico

O artigo avalia a classificação automática de chamados de manutenção predial em português brasileiro como camada auditável de governança e estruturação de dados para modelagem preditiva da infraestrutura pública.

A análise distingue três objetos:

- concordância entre a classificação automática e a categoria administrativa histórica;
- acerto contra a referência humana revisada;
- reclassificação e identificação de problemas na taxonomia histórica.

O texto deve tratar a categoria histórica como registro administrativo sujeito a auditoria, não como referência definitiva. Também não deve afirmar que o estudo já realiza previsão de demanda, previsão de custos ou classificação de criticidade.

## Posicionamento vigente

A contribuição central é um protocolo auditável de classificação de chamados de manutenção predial, articulando governança de rótulo, inferência que respeita a dependência textual, calibração, automação seletiva por confiança e avaliação do risco de reclassificação. A comparação entre sete modelos é meio de prova do protocolo, e não a contribuição em si.

Título vigente:

> **Classificação auditável de chamados de manutenção predial: fluxo humano–IA, calibração e risco de reclassificação**

O título não deve sugerir previsão de demanda ou de custos, classificação de criticidade, anotação independente ou cega, validação temporal inexistente, nem enfatizar a comparação multimodelo a ponto de obscurecer a contribuição.

## Estrutura do artigo

1. Introdução.
2. Referencial conceitual.
3. Método.
4. Resultados.
5. Discussão e limitações.
6. Considerações finais.
7. Declarações e referências.

A fonte editável é `04_artigo/artigo_classificacao_chamados_v3.md`. O PDF publicado fica em `docs/artigo_classificacao_chamados.pdf`.

## Fontes canônicas

Todo artefato da rodada canônica carrega `hash_corpus = 1e476243…`. Quem não
carrega pertence ao painel ou ao snapshot legado e **não** deve alimentar o
artigo.

| Assunto | Fonte canônica |
|---|---|
| Plano operacional e ponto de continuidade | `PLANO_EXECUCAO_ATUAL.md` |
| Manifesto da rodada | `docs/dados/rodada_canonica.json` |
| Acurácia, macro-F1 e custo por modelo | `docs/dados/retreino_canonico.json` |
| Concordância histórica, Kappa, ganho líquido e dispersão | `docs/dados/comparacao_historica.json` |
| Calibração, ECE, Brier e automação seletiva | `docs/dados/calibracao_canonica.json` |
| Intervalos por modelo, consenso e pressupostos secundários | `docs/dados/inferencia_canonica.json` |
| Inferência pareada no nível do grupo textual, efeito de desenho, teste global e Holm | `docs/dados/inferencia_agrupada.json` |
| Cobertura e macro-F1 sob as três convenções de denominador | `docs/dados/sensibilidade_classes_raras.json` |
| Utilidade da reclassificação sob custos assimétricos | `docs/dados/utilidade_reclassificacao.json` |
| Recortes por tipo e curva ABC | `docs/dados/recortes_canonicos.json` |
| Camada de regras de periodicidade | `docs/dados/regras_versus_modelos.json` |
| Custo computacional | `docs/dados/custo_computacional_canonico.json` e `docs/dados/custo_bertimbau.json` |
| Corpus, taxonomia, grupos e partições | `auditoria_base_canonica.json`, `grupos_textuais.json` e `particoes_canonicas.json` |
| Tabelas do apêndice | `docs/dados/tabelas_apendice_canonicas.json` |
| Grupos com referência divergente e sua natureza | `docs/dados/grupos_divergentes_canonicos.json` |
| Disponibilidade de data de abertura no corpus | `docs/dados/disponibilidade_temporal.json` |
| Rastreabilidade e ressalvas | `docs/MATRIZ_PROVENIENCIA.md` e `docs/RASTREABILIDADE_LSTM.md` |

**Fontes que NÃO são do artigo.** `avaliacao_final.json`, `estatistica.json`,
`calibracao.json`, `calibracao_ajustada_modelos.json` e a família
`shannon_*.json` alimentam o painel e vêm da execução legada, com 14.058 a
14.082 linhas, oito modelos e verdade derivada de outro modo. Não carregam
`hash_corpus` e não podem ser citados no artigo.

## Critérios editoriais

- Toda afirmação teórica deve ter referência bibliográfica adequada.
- Datas de execução, IDs de workflow, caminhos internos e linguagem de relatório técnico não devem aparecer no corpo científico, salvo quando metodologicamente indispensáveis.
- O corpo científico deve descrever o procedimento de revisão humana, não as letras das colunas da planilha.
- Utilizar “referência humana revisada” ou “categoria de referência revisada”, evitando “verdade validada”, “verdade final” e “acerto validado”.
- Descrever a revisão humana como auditoria administrativa de rótulo por avaliador único; os 4,25% são taxa de alteração do rótulo histórico, nunca prevalência de erro.
- Resultados estatísticos detalhados devem permanecer em material suplementar quando não forem necessários à interpretação principal.
- Números repetidos no Resumo, Abstract, tabelas, figuras, resultados, discussão e conclusão devem ser atualizados em conjunto.
- O BERTimbau só integrará a comparação principal se utilizar o mesmo protocolo dos demais modelos; caso contrário, ficará como experimento exploratório no suplemento.
- O PDF deve ser regenerado e revisado visualmente após qualquer alteração estrutural ou numérica.
- A meta provisória é de 8 a 9 mil palavras, aproximadamente quatro figuras e quatro ou cinco tabelas principais, ajustável após a escolha do periódico.

## Estado desta rodada

**Rodada canônica:** `1e476243`. Os oito artefatos derivados e os três do
congelamento conferem esse hash, verificável por `python src/matriz_proveniencia.py`.

**Onde está:** os Passos 0 a 10 estão concluídos, o 9 encerrado como não
aplicável. O Passo 11 segue em execução, agora concentrado na Discussão.

**Resultados reestruturados em cinco subseções.** A Seção 4 passou de doze
para cinco subseções: 4.1 desempenho, incerteza e custo; 4.2 auditoria do
histórico e risco de reclassificação; 4.3 calibração e automação seletiva;
4.4 erros por categoria e implicações taxonômicas; 4.5 análises
complementares. A concordância histórica, a acurácia contra a referência
revisada, o macro-F1, o custo de treino e a inferência sob dependência
textual, antes em quatro subseções e três tabelas, fundiram-se na 4.1 com
uma única tabela de desempenho. A duplicação taxonômica, o diagnóstico de
Shannon, a matriz de confusão e os grupos divergentes, antes repetidos em
duas subseções, unificaram-se na 4.4. O BERTimbau, o comportamento do
LSTM, a curva ABC, a tarefa de tipo e a camada de regras de periodicidade,
antes com subseção própria cada um, tornaram-se sínteses curtas na 4.5.

**Nenhum vencedor absoluto.** O parágrafo de abertura e a Subseção 4.1
deixaram de apresentar o LinearSVC como líder isolado: ele lidera a
acurácia, mas a Regressão Logística tem o macro-F1 pontual ligeiramente
superior e o SGD permanece próximo dos dois em ambas as métricas a custo
de treino semelhante, de modo que a escolha operacional é declarada
multicritério.

**Tabelas do corpo, de seis para quatro.** A antiga Tabela 2 (concordância
histórica), a antiga Tabela 3 (acurácia e macro-F1) e a antiga Tabela 6
(custo computacional) fundiram-se na nova Tabela 2, com concordância
histórica, acurácia, macro-F1, intervalo essencial e tempo de treino por
modelo. A antiga Tabela 4 de calibração, com sete modelos, deu lugar à
nova Tabela 4, com os quatro modelos mais competitivos em acurácia; o
ECE piorado do Naive Bayes e do LSTM após a calibração permanece
declarado em texto, e a tabela completa foi para o material suplementar.
A antiga Tabela 7, com seis das 21 comparações pareadas, saiu do corpo: a
Subseção 4.1 relata o teste global, a contagem de pares significativos e
um exemplo (LinearSVC contra SGD) em prosa, e a matriz completa permanece
no material suplementar. A Tabela 5 de ganho líquido virou Tabela 3, sem
alteração de conteúdo. Restam quatro tabelas no corpo dos Resultados, mais
a Tabela 1 do Método.

**Figuras renumeradas pela nova ordem de aparição.** O trade-off de custo
(antiga Figura 5) passou a Figura 2, por entrar na 4.1; a curva de
confiabilidade (antiga Figura 2) passou a Figura 3, na 4.3; o mapa de
categorias (antiga Figura 3) e a matriz de confusão (antiga Figura 4)
passaram a Figuras 4 e 5, na 4.4; a curva de aprendizado do LSTM manteve o
número 6, na 4.5.

**Achados preservados e números conferidos.** Os quatro achados centrais
exigidos pela rodada permanecem no corpo: desempenho comparável dos sete
modelos, ganho líquido negativo da reclassificação, automação seletiva
após calibração e concentração dos erros em fronteiras taxonômicas. Os 17
grupos divergentes, as 85 linhas, os 14 grupos e 74 linhas entre tipos
distintos e o par dominante Hidrossanitária × Reservatório permanecem na
4.4, sem tratamento de teto quantitativo. O macro-F1 de 0,5481 passou a
cenário conservador de sensibilidade, com F1 zero atribuído às nove
categorias ausentes, e não desempenho observado de um modelo treinado nas
50 categorias. Cada número reaproveitado foi conferido contra
`docs/dados/comparacao_historica.json`, `docs/dados/custo_computacional_canonico.json`
e `docs/dados/calibracao_canonica.json`. A frase defensiva "não está em
falha de cálculo" saiu do texto sobre o ganho líquido.

**Remissões cruzadas remapeadas.** Todas as ocorrências de "Subseção 4.X"
no Método, na Discussão e nas Considerações Finais foram atualizadas para
a nova numeração, inclusive as duas que colapsaram em uma só referência
por terem se fundido na mesma subseção (concordância histórica e acerto
contra a referência, ambas agora na 4.1).

**Contagem, antes e depois:** a Seção 4 caiu de 6.082 para cerca de 3.680
palavras, redução de 39,5%, dentro da meta de 30% a 40%. O corpo científico
caiu de 11.903 para cerca de 9.500 palavras, dentro da meta de 8 a 9 mil.

**O que falta:** revisar a Discussão para eliminar qualquer redundância
remanescente com a Seção 4 reestruturada, concluir o ajuste fino de
palavras até a faixa de 8 a 9 mil, revisar visualmente as figuras (Rodada
9) e regerar o PDF, que é gerado pelo workflow ao entrar em `main`. O
ambiente local não dispõe de xelatex nem de Docker, de modo que o PDF não
foi regerado nesta rodada.

## Critérios para novo fechamento científico

A nova rodada científica somente poderá ser considerada fechada quando:

1. corpus, referência e taxonomia estiverem congelados e reconciliados;
2. grupos e partições canônicas estiverem salvos e reproduzíveis;
3. os sete modelos tiverem predições *out-of-fold* sob o mesmo protocolo agrupado;
4. a camada de regras preventivas tiver comparação pareada com os modelos puros;
5. o BERTimbau estiver no mesmo protocolo ou explicitamente classificado como exploratório;
6. calibração, intervalos e testes estatísticos derivarem da mesma execução;
7. a ausência de segunda avaliação humana estiver declarada no texto, com a limitação correspondente;
8. cada número, tabela e figura tiver proveniência rastreável;
9. Resumo, Abstract, tabelas, figuras, discussão e conclusões estiverem coerentes;
10. o PDF final tiver sido gerado e revisado visualmente;
11. o alcance temporal estiver declarado, com avaliação em períodos sucessivos executada ou limitação explícita, e nenhuma afirmação prospectiva excedendo a evidência disponível.

## Registro histórico

Planos concluídos, auditorias antigas, números substituídos e decisões de implementação devem ser consultados no histórico do Git e nos Pull Requests. Eles não devem voltar a ser acumulados neste arquivo.
