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
aplicável. O Passo 11 foi concluído nesta rodada (Rodada 8): a Discussão e
as Considerações Finais foram reescritas para eliminar redundância com a
Seção 4 e o corpo científico entrou na faixa-meta de 8.850 a 9.000
palavras.

**Discussão reestruturada em quatro subseções.** 5.1 adequação dos
modelos e decisão multicritério; 5.2 auditoria do histórico,
reclassificação e fluxo humano–IA; 5.3 limitações e alcance da evidência;
5.4 implicações para governança e continuidade da tese. A concordância
histórica, a auditoria de rótulo, o ganho líquido, a ambiguidade
taxonômica e a calibração, antes espalhados por duas subseções com
repetição de números já apresentados na Seção 4, foram consolidados em
argumentos únicos, cada um remetendo à tabela ou subseção de Resultados em
vez de repetir a série de valores. As catorze limitações antes dispersas
entre Discussão, Conclusão e Declarações foram reunidas na única
Subseção 5.3. Nenhum número de Método ou Resultados foi alterado; apenas
remissões cruzadas e a largura de três figuras foram tocadas.

**Considerações Finais em cinco parágrafos curtos**, na ordem
contribuição, achados centrais, implicação operacional, limitações e
continuidade da tese, mantendo somente os números indispensáveis
(0,8253 de acurácia do LinearSVC, IC95% e as contagens de 13.972
chamados e 41 categorias).

**Figuras 2, 4 e 5 reduzidas em 20%.** Figura 2 (trade-off de custo) de
`width=95%` para `width=76%`; Figura 4 (mapa de categorias) de
`width=91%` para `width=73%`; Figura 5 (matriz de confusão), sem largura
explícita, ganhou `width=80%`. Figuras 1, 3 e 6 não foram tocadas. A
inspeção visual do PDF gerado pelo workflow fica pendente para a Rodada 9;
localmente não há xelatex nem Docker para renderizar.

**Tabelas 1 a 4 convertidas para floats não divisíveis.** Deixaram de sair
como `longtable` (herança do pandoc para tabelas em pipe-markdown) e
passaram a `\begin{table}[!tbp]` com `tabularx`, fonte `\small`, sem
`[H]` e sem `\FloatBarrier`/`\clearpage` colado à tabela — apenas as
barreiras de subseção já existentes no documento permanecem. Conteúdo,
numeração, notas e ordem das linhas preservados byte a byte; verificado no
LaTeX intermediário (`pandoc ... -t latex --standalone`), com as quatro
tabelas fechadas corretamente (4 `\begin{table}`/`\end{table}`, 4
`\begin{tabularx}`/`\end{tabularx}`) e nenhuma delas em `longtable`. As
Tabelas A1 a A3 do apêndice permanecem como pipe-table/`longtable` nesta
rodada, por decisão explícita de escopo (tratamento definitivo na
Rodada 9).

**Contagem, antes e depois (Rodada 8):** Discussão de 1.955 para 1.421
palavras; Considerações Finais de 525 para 372 palavras; corpo científico
de 9.539 para 8.871 palavras (rotina de contagem idêntica à da Rodada 7),
redução de 668 palavras (7,00%). A Seção 4 (Resultados) permanece em
3.712 palavras, sem alteração de prosa; o corpo cresceu cerca de 19
palavras entre a conclusão da reescrita editorial (8.852) e a conversão
técnica das Tabelas 1 a 4 porque a rotina de contagem por palavras do
código-fonte markdown também soma comandos LaTeX brutos das novas tabelas
(`\toprule`, `\begin{tabularx}` etc.), que não são prosa; o valor
continua dentro da faixa-meta de 8.850 a 9.000.

**O que falta:** inspeção visual do PDF gerado pelo workflow após o merge
(figuras redimensionadas e tabelas não divisíveis), o que pode gerar
ajuste na Rodada 9; tratamento definitivo das Tabelas A1 a A3 do apêndice,
também na Rodada 9.

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
