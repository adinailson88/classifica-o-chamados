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

**Próximo passo:** o Passo 2 está em execução em branch própria. A ferramenta `src/construir_grupos_textuais.py` normaliza os quatro campos textuais, agrupa por identidade exata do hash dos quatro campos separados, diagnostica quase duplicados por similaridade de cosseno sem fundi-los e grava o hash de grupo por registro. Falta executá-la contra a base congelada e registrar os números reais. Nenhum retreinamento deve começar antes de verificar que os grupos idênticos poderão permanecer integralmente na mesma partição.

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
