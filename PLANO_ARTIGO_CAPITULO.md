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

**Rodada canônica:** `1e476243`. Os cinco artefatos derivados e os três do
congelamento conferem esse hash, verificável por `python src/matriz_proveniencia.py`.
Números de rodadas anteriores não podem aparecer na mesma tabela.

**Onde está:** os Passos 0 a 8 estão concluídos, o 9 encerrado como não
aplicável e o 10 concluído. O Passo 11 está em execução: o corpo do artigo
caiu de 14.782 para cerca de 13.100 palavras, ainda acima da meta de 8 a 9
mil.

**Dois denominadores, e não um:** a base congelada tem 14.060 chamados, todos
com referência humana, e é o número de toda frase sobre corpus ou cobertura da
revisão. As métricas valem para 13.972 linhas em 41 categorias, porque nove
categorias, somando 88 linhas, não sustentam suporte nas cinco dobras. O
artigo declara os dois na abertura da Seção 4 e os detalha nas Tabelas A2 e A3.

**Três achados que mudaram o texto, não apenas os números:**

O ganho de reclassificação inverteu de sinal. É negativo em todos os sete
modelos, de −1.846 no LinearSVC a −3.474 no Naive Bayes. A causa não é erro de
cálculo: a referência humana confirma a categoria histórica em 13.462 dos
14.060 registros, ou 95,75%, de modo que divergir do histórico quase sempre
significa divergir da referência. O ganho positivo antigo vinha de comparar
contra a decisão revisada onde ela existia e contra o próprio histórico nos
demais casos. A Subseção 4.5 foi reescrita e a conclusão passa a desaconselhar
reclassificação em massa por evidência, não por cautela.

A camada de regras de periodicidade é redundante. Dispara em 4.487 dos 13.972
registros e melhora o macro-F1 de apenas 3 dos 7 modelos, com ganho concentrado
no Naive Bayes e perda nos modelos fortes. O resultado nunca havia chegado ao
artigo e agora ocupa a Subseção 4.12.

O BERTimbau saiu da comparação por custo medido, 6,44 h por dobra contra teto
de 6 h por job. A Subseção 4.3 passou a tratar de viabilidade computacional, a
antiga Tabela 3 foi para o suplemento como S6 com o protocolo declarado, e o
texto não afirma desempenho inferior nem compara o número exploratório antigo
com as tabelas do corpo.

**Uma mudança de achado que veio junto:** a fronteira dominante da matriz de
confusão deixou de ser climatização corretiva contra preventiva. Treinados
contra a referência revisada, os modelos separam esse par de modo consistente,
e o maior par passa a ser Alvenaria contra Instalação de equipamentos, com
2.003 trocas somadas. Alvenaria comporta-se como categoria absorvente.

**Estrutura atual:** cinco tabelas no corpo, numeradas de 1 a 5, e sete
figuras. Saíram para o suplemento a dispersão de Shannon, a curva ABC global, a
tarefa de tipo, a ABC por tipo e o efeito das regras, nas tabelas S7 a S11,
todas geradas por script a partir da rodada canônica.

**Correção de protocolo no método:** a Subseção 3.5 declarava `KFold` não
estratificado por linha, o que a rodada canônica substituiu por
`StratifiedGroupKFold` agrupado por texto. Era a afirmação mais grave
remanescente, porque descrevia um protocolo que as tabelas já não usavam.

**Subseção removida:** a antiga 3.7, sobre veto e trava por chamado. Era fluxo
interno de triagem, usava o termo vedado "verdade validada" e descrevia
justamente o cálculo de ganho misto que a rodada canônica substituiu.

**Assimetria conhecida no relatório de inferência:** em
`src/inferencia_canonica.py`, a coluna de acurácia imprime o valor observado e
a de macro-F1 imprime a média das mil reamostragens, o que produz 0,6664 contra
os 0,6684 do retreino. A Tabela 2 usa o valor observado com o intervalo do
bootstrap. Convém uniformizar o relatório.

**O que falta:** concluir a redução editorial até 8 a 9 mil palavras e revisar
o PDF, que é gerado pelo workflow ao entrar em `main`.

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
