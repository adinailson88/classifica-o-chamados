# Plano — Artigo/Capítulo “Classificação Automática de Chamados”

Este documento registra somente a estrutura, os critérios editoriais e o estado atual do artigo/capítulo. O plano operacional vigente, os critérios de aceite e o ponto de continuidade estão em [`PLANO_EXECUCAO_ATUAL.md`](PLANO_EXECUCAO_ATUAL.md). Os dois documentos têm finalidades distintas e não devem acumular versões concorrentes do mesmo estado.

Atualizado em 05/08/2026, no fuso America/Bahia.

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
aplicável. O Passo 11 segue em execução.

**Método reestruturado em seis subseções.** A Seção 3 passou de oito para
seis subseções: 3.1 delineamento, corpus e referência revisada; 3.2
pré-processamento e representação; 3.3 modelos e configuração experimental;
3.4 validação, calibração e inferência; 3.5 reclassificação, utilidade e
análises complementares; 3.6 reprodutibilidade, dados e aspectos
institucionais. As antigas 3.1 e 3.2 fundiram-se, a antiga 3.6 de revisão
humana passou a integrar a 3.1, a antiga 3.7 de Shannon foi reduzida e
absorvida pela 3.5 e a antiga 3.8 de governança virou a 3.6.

**Duplicações eliminadas.** As famílias de modelos eram descritas em prosa
e reexplicadas caso a caso; agora há uma passagem única de justificativa e
a Tabela 1, nova, com modelo, representação, hiperparâmetros essenciais,
balanceamento, saída de confiança e papel no experimento. O `StratifiedGroupKFold`
é explicado uma só vez, na 3.4. O ranking do Naive Bayes por categorias
previstas saiu do Método, por já constar da Subseção 4.6, e o desenho da
camada de regras saiu, por já constar da 4.12.

**Correspondência com o código.** Cada afirmação foi conferida contra
`src/modelos_zoo.py`, `src/modelo_lstm.py`, `src/construir_grupos_textuais.py`,
`src/gerar_particoes_canonicas.py`, `src/retreinar_modelos_canonicos.py` e
`src/calibrar_confianca.py`. Entraram no texto os itens verificáveis que
faltavam: ordem e concatenação dos quatro campos, descarte de campo vazio
sem marcador, normalização por decomposição Unicode com remoção de
diacríticos e colapso de espaços, hash do grupo como SHA-256 dos quatro
campos mantidos separados, frequência documental mínima do TF-IDF,
marcador de termo fora do vocabulário e truncamento à direita na LSTM,
protocolo de dobra interna da calibração e ambiente de execução com
versões. Saiu a regra de contingência que aciona o Random Forest, que é de
produção e não da rodada canônica.

**Numeração.** A Tabela 1 do Método deslocou as tabelas do corpo, que
passaram de 1 a 6 para 2 a 7, com as citações no texto ajustadas. As
remissões ao Método foram remapeadas: a antiga 3.2 e a antiga 3.6 apontam
para 3.1, a antiga 3.3 para 3.2, a antiga 3.4 para 3.3, a antiga 3.5 para
3.4, a antiga 3.7 para 3.5 e a antiga 3.8 para 3.6.

**Contagem, antes e depois:** o Método caiu de 2.972 para 2.496 palavras,
menos 16,0%. A meta da rodada era de 25% a 35%, e não foi alcançada porque
a mesma rodada exigia acrescentar ao Método a tabela de modelos, as
definições compactas de oito métricas, o protocolo de calibração e o
registro de ambiente, sementes e repetições. Cortar além deste ponto
exigiria remover informação necessária à reprodução. O corpo científico
caiu de 12.513 para 12.037 palavras e a fonte de 16.567 para 16.091.

**Dois denominadores, e não um:** a base congelada tem 14.060 chamados,
todos com referência humana, e é o número de toda frase sobre corpus ou
cobertura da revisão. As métricas valem para 13.972 linhas em 41
categorias, porque nove categorias, somando 88 linhas, não sustentam
suporte nas cinco dobras.

**Unidade da inferência:** o grupo de texto normalizado, e não a linha. O
efeito de desenho medido fica entre 4,47 e 8,83. Intervalos vêm de
*bootstrap* de conglomerados, testes pareados de permutação com troca de
sinal por grupo, teste global da estatística Q contra permutação por grupo
e Holm sobre os 21 pares. Os 21 vereditos não mudam em relação ao McNemar
por linha, com 19 pares significativos e 2 empatados.

**O que falta:** concluir a redução editorial até 8 a 9 mil palavras e
cerca de 22 páginas, agora concentrada nos Resultados e na Discussão, já
que o Método foi reestruturado, e revisar o PDF, que é gerado pelo workflow
ao entrar em `main`. O ambiente local não dispõe de xelatex nem de Docker,
de modo que o PDF não foi regerado nesta rodada.

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
