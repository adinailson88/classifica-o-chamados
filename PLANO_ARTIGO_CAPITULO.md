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
| Intervalos, testes pareados, consenso e pressupostos | `docs/dados/inferencia_canonica.json` |
| Recortes por tipo e curva ABC | `docs/dados/recortes_canonicos.json` |
| Camada de regras de periodicidade | `docs/dados/regras_versus_modelos.json` |
| Custo computacional | `docs/dados/custo_computacional_canonico.json` e `docs/dados/custo_bertimbau.json` |
| Corpus, taxonomia, grupos e partições | `auditoria_base_canonica.json`, `grupos_textuais.json` e `particoes_canonicas.json` |
| Tabelas do apêndice | `docs/dados/tabelas_apendice_canonicas.json` |
| Grupos com referência divergente e sua natureza | `docs/dados/grupos_divergentes_canonicos.json` |
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

**Rodada canônica:** `1e476243`. Os cinco artefatos derivados e os três do
congelamento conferem esse hash, verificável por `python src/matriz_proveniencia.py`.
Números de rodadas anteriores não podem aparecer na mesma tabela.

**Onde está:** os Passos 0 a 8 estão concluídos, o 9 encerrado como não
aplicável e o 10 concluído. O Passo 11 segue em execução.

**Dois denominadores, e não um:** a base congelada tem 14.060 chamados, todos
com referência humana, e é o número de toda frase sobre corpus ou cobertura da
revisão. As métricas valem para 13.972 linhas em 41 categorias, porque nove
categorias, somando 88 linhas, não sustentam suporte nas cinco dobras.

**O que esta rodada mudou: a descrição da revisão humana.** O artigo passou a
declarar o desenho pelo nome. É auditoria administrativa de rótulo, com
avaliador único que decide vendo a categoria histórica, e não anotação
independente. Daí decorrem quatro ajustes que não são de redação:

Os 4,25% deixaram de ser apresentados como prevalência de erro histórico e
passaram a ser a taxa de alteração da categoria pelo especialista. Com isso
desaparece a contradição entre chamá-los de erro no Resultado e negar, nas
Limitações, que a prevalência possa ser estimada. A Subseção 3.6 separa
explicitamente três desfechos que vinham confundidos: confirmação
administrativa, concordância entre avaliadores e correção factual.

A ancoragem entrou como ressalva medida, não como nota de rodapé. O revisor viu
o rótulo que auditava, o que eleva a probabilidade de mantê-lo, de modo que os
95,75% de confirmação refletem em proporção não separável tanto a estabilidade
do registro quanto o próprio procedimento.

A ausência de segunda avaliação está declarada, e não subentendida. Não há
segunda avaliação humana, independente ou cega, nem adjudicação de
divergências; nenhuma medida de confiabilidade entre avaliadores é reportada; e
a segunda avaliação figura como validação futura, com amostra estratificada e
adjudicação por terceiro revisor, sobretudo nos pares ambíguos.

Os 17 grupos de texto idêntico com referência divergente deixaram de ser
chamados de piso de erro irredutível. `src/auditar_grupos_divergentes.py`
caracterizou os 85 registros afetados, ou 0,61% das linhas avaliadas: em 14
grupos, somando 74 linhas, as categorias em disputa pertencem a tipos distintos
de manutenção, e o par dominante opõe Hidrossanitária > Hidráulica a Manutenção
Preventiva > Reservatório, com 11 grupos e 65 linhas. É ambiguidade de contexto
não textual, não taxa de erro de anotação. Separar as três origens possíveis
exigiria reexame caso a caso, não realizado.

**Figura 1 corrigida.** A etapa 8 dizia "validação humana (divergências e
críticos)", o que descrevia triagem amostral que o experimento não executou. A
revisão humana passou a ser a etapa 2, antes do treino, porque é dela que sai o
rótulo, e a Subseção 3.1 foi reescrita na mesma ordem.

**Governança de dados registrada.** A Subseção 3.8 declara origem
institucional, sanitização na origem, ausência de identificador pessoal nos
agregados públicos, restrição de compartilhamento e aderência ao princípio da
necessidade da LGPD (BRASIL, 2018). Registra também, sem inventar aprovação,
que o repositório não guarda documento de autorização institucional, aprovação
ética ou dispensa.

**Correção numérica encontrada de passagem:** a Subseção 5.3 dizia "três
registros" com texto editado após o congelamento;
`inferencia_canonica.json#contagem_de_grupos` registra dois.

**Tamanho:** a fonte caiu de 17.244 para 17.209 palavras, apesar do conteúdo
novo, por remoção de repetições sobre rótulos ruidosos entre Introdução,
Método, Resultados, Discussão e Conclusão, mantida uma explicação principal na
Subseção 3.6 e uma interpretação na 5.1.

**O que falta:** concluir a redução editorial até 8 a 9 mil palavras e cerca de
22 páginas, e revisar o PDF, que é gerado pelo workflow ao entrar em `main`.

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
10. o PDF final tiver sido gerado e revisado visualmente.

## Registro histórico

Planos concluídos, auditorias antigas, números substituídos e decisões de implementação devem ser consultados no histórico do Git e nos Pull Requests. Eles não devem voltar a ser acumulados neste arquivo.
