# Plano — Artigo/Capítulo “Classificação Automática de Chamados”

Este documento registra somente a estrutura, os critérios editoriais e o estado atual do artigo/capítulo. O plano operacional vigente, os critérios de aceite e o ponto de continuidade estão em [`PLANO_EXECUCAO_ATUAL.md`](PLANO_EXECUCAO_ATUAL.md). Os dois documentos têm finalidades distintas e não devem acumular versões concorrentes do mesmo estado.

Atualizado em 14/08/2026, no fuso America/Bahia (Rodada 12, revisão editorial v4: título, Subseção 3.6, IFES, Tabela 5, paginação e figuras).

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

**Rodada canônica:** `1e476243` (hash completo
`1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`). Os oito
artefatos derivados e os três do congelamento conferem esse hash,
verificável por `python src/matriz_proveniencia.py`; a Rodada 12 não
alterou nenhum artefato de dados, e a matriz seguiu sem divergências.

**Onde está:** os Passos 0 a 10 estão concluídos, o 9 encerrado como não
aplicável, e os Passos 11 e 12 (redução/reescrita editorial e integração
do ensemble) estão concluídos. A Rodada 12 é uma revisão editorial de
forma — título, identificação institucional, composição de tabelas,
paginação e legibilidade de figuras — sem reabrir decisões científicas,
sem retreinar modelo algum e sem alterar número, tabela de dados ou
referência além do explicitamente descrito em
`TAREFA_CLAUDE_CODE_revisao_v4.md`. Zero fits de modelo-base, zero fits de
stacking, zero execuções de LSTM.

**Estrutura vigente.** Seis figuras e **cinco** tabelas principais no
corpo (nova Tabela 5, comparação confirmatória do ensemble, Subseção 4.5);
apêndice com as Tabelas A1 a A3, floats não divisíveis em `\footnotesize`
com numeração própria (A1/A2/A3, independente da sequência 1–5 do corpo),
com o título e o parágrafo introdutório do Apêndice A agora impressos
antes da Tabela A1; material suplementar até S17. Discussão em quatro
subseções (5.1 a 5.4); Considerações Finais em cinco parágrafos curtos.
Lista de referências com 44 entradas (a entrada órfã de BRASIL, 2018,
saiu junto da prosa que a citava; duas entradas foram reordenadas
alfabeticamente), todas citadas no corpo, sem duplicatas nem citação
órfã.

**Título e identificação institucional.** Título e subtítulo
reformulados para "Classificação de chamados de manutenção predial com
aprendizado de máquina: desempenho e limites da automação". O corpus é
descrito como o de uma instituição federal de ensino superior (IFES), sem
nomear a UFSB fora do bloco de afiliação dos autores (`UFSB` ocorre uma
única vez no arquivo-fonte).

**Corpo científico: 8.855 palavras**, medidas pela mesma rotina única
(contagem de palavras do Markdown-fonte entre "**1. INTRODUÇÃO**" e
"**REFERÊNCIAS**", exclusive). Partiu de 8.999 (Rodada 11) e absorveu, na
Rodada 12, a reescrita da Subseção 3.6, a supressão do parágrafo de
"quatro achados" da Seção 4, a supressão da cauda sobre privacidade
institucional da Subseção 5.3, a nova seção "Disponibilidade de dados e
código" e a nova Tabela 5, com elaborações compensatórias em outros
trechos para permanecer dentro da faixa-meta de 8.850 a 9.000.

**PDF:** regenerado pelo workflow oficial (`artigo_pdf.yml`,
`workflow_dispatch`) na própria branch desta rodada; contagem de páginas e
inspeção visual registradas em `verificacao/relatorio_revisao_v4.md`.

**Figuras regeneradas nesta rodada (só parâmetros de apresentação, sem
alterar dado ou ordenação):** Figura 1 (texto interno e rótulo de
retroalimentação a 8 pt, rótulo em tom mais escuro), Figura 4 (fonte a
8 pt, rótulos truncados substituídos por abreviações explícitas em
`ABREVIACOES_EXPLICITAS`), Figura 5 (fonte a 8 pt, mesmo conjunto de
rótulos abreviados nos dois eixos da matriz), Figura 6 (eixos dos dois
painéis em formato decimal pt-BR). Resumo criptográfico dos dados de
entrada de cada figura conferido idêntico antes e depois em
`verificacao/relatorio_revisao_v4.md`.

**Pendência conhecida:** a contagem de construções antitéticas ", e não"
no corpo já estava em 23 antes desta rodada (acima do limite de 8 usado
como critério de aceitação da tarefa) e caiu para 20 com os cortes desta
rodada; reduzi-la a 8 exigiria reescrever dezenas de frases fora do
escopo explícito desta tarefa, o que não foi feito — ver bloqueador no
relatório da rodada.

**Material suplementar: S17.** `tabela_S17_ensemble_confirmatorio.csv`,
gerada programaticamente por `src/tabelas_suplementares_canonicas.py` a
partir exclusivamente de
`docs/dados/ensemble/fase2c/fase2c_execucao_cientifica_1_manifest.json`
(sem `hash_corpus`, por pertencer à trilha experimental da Fase 2C, não à
rodada canônica do artigo principal), com validação de proveniência
(universo 13.970, denominador `Y=1` 593, capacidade `K` 2.840, run/commit
da Fase 2B). Não modificada nesta rodada; a nova Tabela 5 do corpo apenas
formata, sem alterar, os mesmos quatro valores já usados no parágrafo
final da Subseção 4.5 desde a Rodada 11.

O detalhamento rodada a rodada de como o estado anterior a este foi
alcançado — reestruturação da Discussão, conversão das tabelas em floats,
correções das duas auditorias independentes da PR #202, auditoria visual e
paginação da Rodada 9, auditoria final de submissão da Rodada 10,
integração editorial do ensemble na Rodada 11 — está nos commits e nas
Pull Requests (#202, #203, #209, #210) e não é repetido aqui, conforme a
regra de uso deste documento. O relatório completo da Rodada 12 está em
`verificacao/relatorio_revisao_v4.md`.

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
