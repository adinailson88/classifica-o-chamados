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
numeração, notas e ordem das linhas preservados; verificado no
LaTeX intermediário (`pandoc ... -t latex --standalone`), com as quatro
tabelas fechadas corretamente (4 `\begin{table}`/`\end{table}`, 4 `\caption`,
4 `\label`, 4 `\begin{tabularx}`/`\end{tabularx}`, ao menos uma coluna
flexível `Y`/`Z` por tabela) e nenhuma delas em `longtable`; conteúdo
numérico, significado, numeração e ordem das linhas foram preservados. Os
antigos títulos "**Tabela N**" em parágrafo Markdown externo à tabela
foram removidos e o texto passou para `\caption` dentro do float, o que
impede que o título fique em uma página e a tabela flutue para outra. As
Tabelas A1 a A3 do apêndice permanecem como pipe-table/`longtable` nesta
rodada, por decisão explícita de escopo (tratamento definitivo na
Rodada 9).

**Contagem, antes e depois (Rodada 8, após a auditoria independente da
PR #202):** Discussão de 1.955 para 1.450 palavras; Considerações Finais
de 525 para 393 palavras; corpo científico de 9.539 para 8.917 palavras
(rotina de contagem idêntica à da Rodada 7), redução de 622 palavras
(6,52%). A Seção 4 (Resultados) foi de 3.712 para 3.724 palavras, sem
alteração de prosa: a variação vem da legenda da Tabela 2, que passou de
parágrafo Markdown externo para `\caption{...}` dentro do float. O corpo
cresceu porque a rotina de contagem por palavras do código-fonte markdown
também soma comandos LaTeX brutos das novas tabelas (`\toprule`,
`\begin{tabularx}`, `\label{tab:...}` etc.), que não são prosa; o valor
continua dentro da faixa-meta de 8.850 a 9.000.

**Correções da primeira auditoria independente (PR #202), 05/08/2026:** as
legendas "Tabela 1" a "Tabela 4" saíram do parágrafo Markdown externo e
entraram em `\caption{...}` dentro de cada `\begin{table}[!tbp]`, com
`\label{tab:modelos}`, `tab:desempenho`, `tab:reclassificacao` e
`tab:calibracao`, cada uma acima do `tabular`; as quatro tabelas passaram
a usar ao menos uma coluna flexível do tipo X (`Y`/`Z`, ponderadas por
`\hsize`); a Subseção 5.2 deixou de atribuir os 2,92 pontos percentuais de
diferença diretamente às 598 alterações do rótulo histórico, já que a
quantidade de alterações dentro das 13.972 linhas avaliadas não foi
contabilizada separadamente; a recomendação do LinearSVC nas Considerações
Finais e a frase sobre LinearSVC/SGD na Subseção 5.1 passaram a descrever
candidatos e piloto controlado condicionados a validação temporal,
monitoramento de deriva e auditoria humana, não implantação já validada.

**Correções da segunda auditoria independente (PR #202), 05/08/2026:** as
colunas `Y`/`Z` passaram a sincronizar `\linewidth=\hsize` dentro de cada
coluna X, exigência do mecanismo interno do `tabularx` para colunas
ponderadas (a versão anterior alterava `\hsize` sem repassar o valor a
`\linewidth`); a afirmação de que o transbordo ficou "estruturalmente
impossível" foi retirada dos planos, substituída por: a conversão elimina
o excesso decorrente da soma manual de colunas fixas e limita a tabela à
largura declarada do `tabularx`, permanecendo necessária a inspeção do PDF
quanto a conteúdo não separável e legibilidade. As quatro referências já
órfãs identificadas na primeira auditoria (COHEN, 1960; LANDIS; KOCH,
1977; MCNEMAR, 1947; WONGPAKARAN *et al.*, 2013, ligadas ao antigo
Passo 9 de segunda avaliação humana, encerrado como não aplicável) foram
removidas da lista de referências. A contagem precisa de entradas
bibliográficas, obtida por separação em blocos delimitados por linha em
branco entre "**REFERÊNCIAS**" e o Apêndice A, é de 49 antes da remoção e
45 depois — não 46/42, número aproximado usado na primeira auditoria por
método de extração menos preciso. As 45 referências restantes têm ao
menos uma citação no corpo, e toda citação do corpo tem entrada
correspondente na lista.

**Rodada 9 (agent/rodada-09-figuras-paginacao), auditoria visual e
paginação:** inspeção página a página do PDF publicado após o merge da
PR #202 (66ef86b6, 21 páginas), renderizado em PNG a 180 dpi via
PyMuPDF, sem xelatex/Docker locais disponíveis. Achados do PDF de
partida: as Figuras 2, 4 e 5 (76%/73%/80%) permanecem legíveis nas
dimensões da Rodada 8, mantidas sem alteração; as Tabelas 1 a 4
permanecem íntegras, com legenda e conteúdo na mesma página; as
Tabelas A1 a A3 do apêndice, embora em `longtable`, já cabiam cada uma
inteira em uma única página, mas usavam fonte `\scriptsize`, abaixo do
piso de legibilidade desta rodada. Pendência registrada, fora do
escopo desta rodada: o eixo Y da Figura 2 (trade-off de custo) arredonda
os rótulos para uma casa decimal, fazendo marcas distintas (~0,80/0,82/
0,85) aparecerem como "0,8" repetido; a correção exige editar
`src/gerar_figura3_tradeoff_custo.py` e regenerar o artefato da figura,
não apenas o LaTeX.

**Tabelas A1 a A3 convertidas para floats não divisíveis.** Passaram de
`longtable` para `\begin{table}[!tbp]`/`[!tp]` com `tabularx`, no mesmo
padrão das Tabelas 1 a 4: `\caption`/`\label` dentro do float, colunas
`Y`/`Z` (já existentes) e uma nova coluna `W` (tipo X alinhado à
direita, adicionada ao preâmbulo) para as colunas numéricas. Fonte
subida de `\scriptsize` para `\footnotesize`. O contador de tabelas foi
resetado e renomeado no início do Apêndice A
(`\renewcommand{\thetable}{A\arabic{table}}` + `\setcounter{table}{0}`)
para que as legendas saiam como "Tabela A1", "A2" e "A3", e não
continuem a numeração 1–4 do corpo. Nenhum valor, ordem de linha ou
conteúdo foi alterado.

**Duas rodadas de correção após renderização real via
`workflow_dispatch` na própria branch** (sem tocar `main`): a 1ª
geração revelou dois problemas que só aparecem no PDF renderizado, não
no LaTeX intermediário do pandoc — legenda duplicada e mal numerada
("Tabela 5"/"Tabela 6" em vez de "Tabela A1"/"A2", por herdar o
contador de tabela do corpo) e a posição `[!p]` forçando cada tabela
para página exclusiva mesmo cabendo com folga junto do texto ao redor,
o que subiu a paginação de 21 para 24 páginas com duas páginas quase
vazias. Corrigido com o reset de contador acima e troca de `[!p]` para
`[!tbp]` em A1 e A2 (A3 já não usava `[!p]`). A Tabela A3, por ser o
último float do documento sem texto depois para preencher a página,
ficou centralizada verticalmente na página final em vez de alinhada ao
topo — LaTeX centraliza floats em página exclusiva de floats
(`@fptop`/`@fpbot` com `\vfil` simétrico), mecanismo que `\raggedbottom`
local não afeta; tentativa registrada e revertida, sem página vazia
adicional. **Paginação final: 22 páginas**, dentro da faixa preferencial
de 21 a 23.

**Página com grande espaço vazio observada e não alterada nesta
rodada:** a página com a Tabela 4 e a Figura 3 (curva de confiabilidade,
duas subplots) deixa cerca de 40% da página anterior em branco porque a
Figura 3, não divisível, não cabe no restante daquela página e migra
inteira para a seguinte — comportamento esperado de floats não
divisíveis, não um erro de posicionamento; nenhum ajuste foi aplicado
por não haver medida permitida (sem reduzir fonte, margem ou
`floatsep`) que resolvesse sem risco de destabilizar outras páginas
sem capacidade de recompilação iterativa rápida.

**O que falta:** nenhuma pendência de escopo desta rodada. A correção
do arredondamento do eixo da Figura 2 fica registrada para rodada
futura que edite scripts geradores de figura.

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
