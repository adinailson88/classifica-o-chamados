# Plano — Artigo/Capítulo “Classificação Automática de Chamados”

Este documento registra somente a estrutura, os critérios editoriais e o estado atual do artigo/capítulo. O plano operacional vigente, os critérios de aceite e o ponto de continuidade estão em [`PLANO_EXECUCAO_ATUAL.md`](PLANO_EXECUCAO_ATUAL.md). Os dois documentos têm finalidades distintas e não devem acumular versões concorrentes do mesmo estado.

Atualizado em 02/08/2026, no fuso America/Bahia.

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
- acerto contra a referência humana final;
- reclassificação e identificação de problemas na taxonomia histórica.

O texto deve tratar a categoria histórica como referência administrativa, não como verdade absoluta. Também não deve afirmar que o estudo já realiza previsão de demanda, previsão de custos ou classificação de criticidade.

## Posicionamento vigente

A contribuição central será um fluxo híbrido, auditável e sensível à confiança para classificação e revisão de chamados de manutenção predial, com comparação entre modelos estatísticos, regras de domínio e modelo contextual, considerando desempenho e viabilidade computacional.

Título provisório:

> **Classificação auditável de chamados de manutenção predial: um fluxo híbrido humano–IA com automação seletiva por confiança**

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

| Assunto | Fonte |
|---|---|
| Plano operacional e ponto de continuidade | `PLANO_EXECUCAO_ATUAL.md` |
| Resultado validado por modelo | `docs/dados/avaliacao_final.json` |
| Comparação estatística | `docs/dados/estatistica.json` |
| Calibração e faixas de confiança | `docs/dados/calibracao.json` e `docs/dados/calibracao_ajustada_modelos.json` |
| Estado do BERTimbau | `docs/dados/bertimbau_training_state.json` e `docs/dados/bertimbau_metr_full.json` |
| Figuras e tabelas derivadas | scripts em `src/` e JSONs em `docs/dados/` |
| Regras operacionais | `AGENTS.md`, `README.md` e `CONTEXTO.md` |

**Estado transitório:** os JSONs atuais são canônicos apenas para reproduzir o snapshot legado. Eles não são os resultados definitivos do novo protocolo até a conclusão da execução prevista em `PLANO_EXECUCAO_ATUAL.md`.

## Critérios editoriais

- Toda afirmação teórica deve ter referência bibliográfica adequada.
- Datas de execução, IDs de workflow, caminhos internos e linguagem de relatório técnico não devem aparecer no corpo científico, salvo quando metodologicamente indispensáveis.
- O corpo científico deve descrever o procedimento de revisão humana, não as letras das colunas da planilha.
- Utilizar “referência humana final” ou “categoria de referência revisada”, evitando “verdade validada”.
- Resultados estatísticos detalhados devem permanecer em material suplementar quando não forem necessários à interpretação principal.
- Números repetidos no Resumo, Abstract, tabelas, figuras, resultados, discussão e conclusão devem ser atualizados em conjunto.
- O BERTimbau só integrará a comparação principal se utilizar o mesmo protocolo dos demais modelos; caso contrário, ficará como experimento exploratório no suplemento.
- O PDF deve ser regenerado e revisado visualmente após qualquer alteração estrutural ou numérica.
- A meta provisória é de 8 a 9 mil palavras, aproximadamente quatro figuras e quatro ou cinco tabelas principais, ajustável após a escolha do periódico.

## Estado desta rodada

**Onde está:** o Passo 1 foi concluído. A auditoria canônica somente leitura declarou a base `apto_para_congelar`, com 14.060 IDs únicos, 14.060 referências humanas válidas e 50 categorias tanto na taxonomia histórica quanto na referência revisada. O artigo e os resultados experimentais publicados ainda representam a execução anterior e permanecem legados.

**Por que a execução será refeita:** os modelos vigentes foram treinados com categorias históricas do GLPI; a divisão principal ocorreu por registro; textos repetidos podem atravessar treino e teste; e o BERTimbau utiliza protocolo diferente. As divergências de corpus e taxonomia que bloqueavam o redesenho foram resolvidas pela auditoria canônica, mas os modelos ainda precisam ser avaliados sob a nova referência e partições agrupadas comuns.

**O que foi feito nesta rodada:** o workflow `Auditar base canonica (read-only)` foi executado novamente em `main`, sem escrita na planilha. Todos os bloqueadores ficaram zerados. O relatório e o JSON sanitizados foram preservados em `docs/`, com hash da base `e10c78e4db0026cfcbfa5267ddac034a3c8d3a7a0a1d63fa0cf2ce52f165b174` e hashes idênticos das duas taxonomias (`ec6f75ca0427d7a0bd224e019a0052ee4e50734bbda66a7fd45890f7c8b488cb`).

**Passo 2, concluído:** a base congelada de 14.060 linhas resolve-se em 9.786 grupos textuais, dos quais 9.474 são unitários. Há 4.586 linhas com duplicata, ou 32,62% da base, e o maior grupo reúne 219 linhas idênticas. Nenhum grupo excede o limite de 2.812 linhas por dobra com k=5, de modo que o particionamento agrupado do Passo 3 é viável sem tratamento especial. Dezessete grupos carregam referência humana divergente sobre texto idêntico, afetando 85 linhas, o que estabelece um piso de erro irredutível de aproximadamente 0,6% para qualquer modelo.

**Cuidado ao redigir os números:** os 32,62% deste passo não substituem nem contradizem os 46,72% citados na Subseção 4.8. Aquele valor é a taxa de vazamento sob KFold aleatório de três dobras no subconjunto validado, isto é, a fração de linhas de teste cujo texto reaparece no treino; este é a fração de linhas da base completa que pertencem a um grupo com mais de um membro. A convergência entre os 9.714 grupos do ablation e os 9.786 deste passo, sobre bases quase idênticas, confirma que as duas medidas partem do mesmo agrupamento.

**Passo 3, concluído:** as partições canônicas usam `StratifiedGroupKFold` com cinco dobras e semente 42, sobre os grupos textuais do Passo 2 e estratificadas pela referência humana. São 13.972 linhas em 9.734 grupos, distribuídas em dobras de 2.556 a 3.045 linhas, sem nenhum grupo textual dividido entre dobras.

**Denominador das métricas:** 41 das 50 categorias entraram nas partições. Quatro saíram por aritmética, tendo menos grupos textuais distintos que dobras, e cinco por ausência efetiva em alguma dobra após o sorteio; as nove somam 88 linhas. A prática de excluir rótulos de baixa frequência em classificação hierárquica de chamados tem precedente em Marcuzzo et al. (2022), fichado no acervo, com a ressalva de que o limiar deles é de cem ocorrências e o critério aqui é outro. Toda métrica da nova execução vale para essas 41 categorias, e o texto precisa declarar esse denominador sempre que reportar resultados, sem deixá-lo implícito.

**Base congelada de fato:** a auditoria do Passo 1 documentou o corpus, mas a aba principal continua viva e recebeu treze chamados entre a auditoria e o particionamento. As partições passaram a ser fixadas pelo mapa de grupos textuais versionado, de modo que o crescimento operacional da planilha não altera o experimento. Essa distinção entre corpus documentado e corpus fixado merece uma frase no método.

**Passos 4, 5 e 7, concluídos numa única rodada canônica:** os artefatos trazem todos o mesmo `hash_corpus` `3aa42e31`, o que garante que descrevem exatamente o mesmo corpus. Isso deixou de ser promessa e passou a ser verificável: antes, cada passo relia a planilha por conta própria, e uma edição de texto entre execuções bastava para dessincronizar números do mesmo experimento.

**Passo 4:** os sete modelos foram retreinados sobre as partições canônicas, com a referência humana revisada como rótulo e predição *out-of-fold* para todos os 13.972 registros. Nenhum modelo treinou no grupo textual que previu. O LinearSVC lidera nas duas métricas, com 0,8255 de acurácia e 0,6696 de macro-F1, seguido de perto pela regressão logística e pelo SGD. O Naive Bayes tem acurácia de 0,7084 mas macro-F1 de 0,2952, o que confirma que acerta a cauda pesada e falha nas categorias menores.

**Os novos números não são comparáveis aos legados:** a acurácia subiu para todos os sete modelos em relação ao snapshot anterior, mas isso não significa que o protocolo mais rigoroso melhorou o desempenho. Três coisas mudaram ao mesmo tempo. O rótulo deixou de ser a categoria histórica do GLPI e passou a ser a referência humana revisada, que é mais consistente e portanto mais previsível. O particionamento passou de aleatório por registro para agrupado por texto, o que deveria reduzir os números. E o denominador caiu de 56 categorias com suporte para 41. A discussão precisa apresentar os efeitos separadamente, ou o texto sugerirá um ganho que o desenho não sustenta; o par de valores por protocolo já disponível na Subseção 4.8 é o instrumento adequado para isolar o efeito do agrupamento.

**Passo 5, com resultado negativo:** a camada explícita de regras de periodicidade dispara em 4.487 dos 13.972 registros, quase um terço do corpus, mas melhora o macro-F1 de apenas três dos sete modelos. O ganho concentra-se onde o modelo é fraco, e nos modelos fortes o efeito desaparece ou inverte.

**Como redigir esse achado:** a leitura correta não é que as regras de domínio funcionam, e sim que elas são redundantes diante de um classificador estatístico competente. Os modelos já capturam os sinais de periodicidade implicitamente a partir do texto; a camada explícita apenas repete o que eles fazem, com 4.487 disparos gerando entre 31 e 60 divergências nos modelos lineares. Isso é resultado publicável e contraria a expectativa inicial do desenho, que era medir um ganho. Sustenta também a decisão de manter o fluxo híbrido no eixo humano-IA, e não no eixo regra-modelo.

**Passo 6, concluído:** o BERTimbau fica fora da comparação principal, como experimento exploratório no suplemento. A decisão tem número, não impressão. O fine-tuning custou 10,774 segundos por passo em executor de quatro processadores sem GPU, com variação de apenas 0,12 segundo entre o passo mais rápido e o mais lento, o que torna a projeção confiável. São 2.103 passos por dobra, ou 6,44 horas, e 32,2 horas nas cinco dobras, contra um teto de seis horas por job. Nem uma dobra completa cabe na infraestrutura disponível.

**Como redigir a exclusão:** a limitação é de infraestrutura, não do modelo, e o texto precisa dizer isso nesses termos. Não afirmar que o BERTimbau tem desempenho inferior, porque ele não foi avaliado sob este protocolo; não comparar o número exploratório antigo com os valores da Tabela 1, porque vieram de protocolos distintos. A formulação defensável é que a comparação integral exigiria aceleração por GPU, e que o custo medido em CPU inviabiliza a validação cruzada agrupada de cinco dobras no ambiente do estudo. Esse número também reforça o argumento de viabilidade computacional, ao lado do LSTM, que já custava dezoito vezes o treino do LinearSVC para perder dele.

**Passo 7, concluído:** a calibração isotônica ajustada em dobra interna reduz o ECE de cinco dos sete modelos, e o efeito é maior justamente onde a confiança bruta não significava nada. O LinearSVC cai de 0,6926 para 0,0173, porque o *softmax* da margem não é probabilidade; o SGD cai de 0,3046 para 0,0116. O Naive Bayes e o LSTM já eram bem calibrados e pioram levemente, o que é consequência esperada de ajustar um calibrador sobre uma amostra menor.

**Automação seletiva:** ao alvo de 0,95, o Extra Trees automatiza 67,9% dos chamados com acurácia seletiva de 0,9507 e encaminha 32,1% ao revisor humano; o LinearSVC automatiza 68,97% com 0,9461. Ao alvo de 0,99 a cobertura cai para a faixa de 32% a 46%, e o Naive Bayes só alcança o limiar em duas das cinco dobras.

**Detalhe metodológico que sustenta o resultado:** parte das acurácias seletivas fica pouco abaixo do alvo, como os 0,9461 do LinearSVC contra a meta de 0,95. Isso não é defeito, é a consequência esperada de escolher o limiar numa dobra interna e aplicá-lo a dados nunca vistos. Um procedimento que atingisse o alvo exatamente em todas as dobras seria indício de que o limiar viu o teste. Convém dizer isso na redação, porque um parecerista atento vai reparar na diferença.

**Recortes por tipo e por volume, refeitos sob o protocolo canônico:** os recortes consolidados no item 0.31 do `CONTEXTO.md` existiam apenas para a execução legada e agora saem da mesma rodada, com o mesmo `hash_corpus`. Os três tipos preservam a proporção medida em agosto: Corretiva com 8.483 chamados em 21 categorias, Preventiva com 4.904 em 13 e Não manutenção com 585 em 7, ou 4,2%.

**O achado que o recorte por tipo isola:** distinguir a natureza do serviço é tarefa quase resolvida, enquanto escolher a folha da taxonomia não é. Na tarefa de tipo projetada, o Extra Trees alcança 0,9499 de acurácia, com F1 de 0,9762 em preventiva e 0,9598 em corretiva. Na tarefa de categoria, o mesmo recorte preventivo dá 0,9621 de acurácia contra 0,7468 em corretiva. Preventiva é sistematicamente mais fácil, porque seus chamados são padronizados e repetitivos, o que também explica a concentração de duplicatas textuais.

**Não manutenção é o problema, não a preventiva:** o F1 desse tipo fica entre 0,2684 e 0,5319 conforme o modelo, e é ele que puxa o macro-F1 da tarefa de tipo para a faixa de 0,73 a 0,82, apesar da acurácia acima de 0,93. Vale notar a inversão de ranking: o Extra Trees vence em acurácia, mas o SGD e o LinearSVC vencem em macro-F1, justamente por irem melhor na classe difícil. Reportar só a acurácia esconderia isso.

**Curva ABC:** a classe A reúne 12 categorias e 81,8% do volume, com o LinearSVC em 0,8544 de acurácia e 0,8210 de macro-F1; a classe C reúne 17 categorias e 4,5% do volume, com 0,5580 e 0,5041. É esse contraste que localiza na cauda a distância entre a acurácia de 0,83 e o macro-F1 de 0,67. Dentro da preventiva, a classe A chega a 0,9743 de macro-F1, quase saturada.

**Passo 8, concluído:** os intervalos de confiança vêm de bootstrap por grupo textual, com mil repetições e semente 42. Reamostrar linhas trataria como independentes os 4.586 registros que pertencem a grupos com mais de um membro, e estreitaria os intervalos artificialmente. A unidade de reamostragem é o grupo congelado no Passo 2, que são 9.735 entre os registros avaliados, e não o grupo recalculado sobre o texto vivo, porque só o congelado é reproduzível.

**Protocolo dos testes:** Cochran Q primeiro, com Q = 2669,67 sobre 6 graus de liberdade e p praticamente nulo, o que rejeita a igualdade das taxas de acerto e autoriza as comparações pareadas. Em seguida McNemar nos 21 pares, com correção de Holm sobre essa família. A ordem importa e deve ser declarada: sem o teste global, 21 comparações seriam pesca de significância.

**O que os testes autorizam afirmar:** o LinearSVC supera todos os demais com significância, e a diferença para o SGD, segundo colocado, tem 540 acertos exclusivos contra 312. Mas três pares ficam empatados depois de Holm — Extra Trees contra Regressão Logística, com p ajustado de 0,734, Extra Trees contra SGD, com 0,263, e Random Forest contra Regressão Logística, com 0,050. Esse trio não deve ser apresentado como ordenado; a tabela precisa mostrar o empate, e não apenas as posições.

**Cuidado com o par na fronteira:** os 0,050 de Random Forest contra Regressão Logística ficam exatamente sobre o limiar. É prudente descrevê-lo como indistinguível dentro do poder do teste, em vez de reportá-lo como diferença marginal, porque a leitura oposta depende inteiramente de uma casa decimal.

**Próximo passo:** executar o Passo 10, de proveniência e artefatos. O Passo 9, da segunda validação humana cega, é dependência externa.

## Critérios para novo fechamento científico

A nova rodada científica somente poderá ser considerada fechada quando:

1. corpus, referência e taxonomia estiverem congelados e reconciliados;
2. grupos e partições canônicas estiverem salvos e reproduzíveis;
3. os sete modelos tiverem predições *out-of-fold* sob o mesmo protocolo agrupado;
4. a camada de regras preventivas tiver comparação pareada com os modelos puros;
5. o BERTimbau estiver no mesmo protocolo ou explicitamente classificado como exploratório;
6. calibração, intervalos e testes estatísticos derivarem da mesma execução;
7. a segunda avaliação humana cega estiver documentada;
8. cada número, tabela e figura tiver proveniência rastreável;
9. Resumo, Abstract, tabelas, figuras, discussão e conclusões estiverem coerentes;
10. o PDF final tiver sido gerado e revisado visualmente.

## Registro histórico

Planos concluídos, auditorias antigas, números substituídos e decisões de implementação devem ser consultados no histórico do Git e nos Pull Requests. Eles não devem voltar a ser acumulados neste arquivo.
