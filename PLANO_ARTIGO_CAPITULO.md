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

**Próximo passo:** executar o Passo 4, retreinando os sete modelos sobre estas partições, com a referência humana revisada como rótulo.

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
