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

**A validação temporal não é executável, e isso passou a estar declarado.**
`src/auditar_disponibilidade_temporal.py` percorre o contrato de colunas de
`AGENTS.md` e os sete artefatos do congelamento e da rodada canônica,
classificando cada nome de campo em candidato a data do chamado, carimbo de
execução ou irrelevante. O veredito registrado em
`docs/dados/disponibilidade_temporal.json` é `sem_variavel_temporal`: zero
candidatos entre os 17 campos do contrato e os artefatos, e os únicos campos
temporais são `gerado_em`, que datam o arquivo e não o chamado. Sem data de
abertura não há como separar treino, calibração e teste em períodos
sucessivos, de modo que nenhuma métrica temporal foi produzida e nenhuma foi
inventada. A consequência entrou no artigo: a Subseção 3.2 declara que o corte
é de extração e não admite ordenação cronológica, a 3.5 delimita que o
protocolo estima generalização entre grupos textuais do mesmo corte e não
desempenho futuro, a 5.3 ganhou a limitação e os riscos de implantação
(deriva de vocabulário, mudança de taxonomia, categoria nova sem exemplo,
alteração de formulário e de equipe, monitoramento e recalibração), e as
afirmações prospectivas da 5.2, da 5.4 e da Seção 6 passaram a condicionais.

**Custo editorial:** o corpo científico foi de 13.323 para 13.719 palavras,
396 a mais. A compensação parcial veio de três passagens da Discussão que
repetiam os Resultados sem acrescentar: o veredito da reclassificação na 5.2,
o parágrafo de Shannon e o de calibração, além da fusão dos dois parágrafos
finais da 5.1.

**Dois denominadores, e não um:** a base congelada tem 14.060 chamados, todos
com referência humana, e é o número de toda frase sobre corpus ou cobertura da
revisão. As métricas valem para 13.972 linhas em 41 categorias, porque nove
categorias, somando 88 linhas, não sustentam suporte nas cinco dobras.

**O que esta rodada mudou: a unidade da inferência.** O bootstrap já
reamostrava grupos, mas o Cochran Q e os 21 McNemar somavam discordantes linha
a linha, tratando como independentes 4.546 registros que dividem texto
normalizado com outro. O efeito de desenho medido em `inferencia_agrupada.json`
fica entre 4,47 e 8,83, isto é, o erro padrão declarado por linha era de 2,1 a
3,0 vezes menor do que a amostra sustenta. A inferência foi refeita com o grupo
textual como unidade: teste global com a estatística Q contra distribuição de
permutação por grupo, 21 comparações por permutação pareada com troca de sinal
da diferença por grupo, intervalos por bootstrap de conglomerados e Holm sobre
a família. **Nenhum dos 21 vereditos muda**, com os mesmos 19 pares
significativos e os mesmos 2 empatados, o que é resultado da análise e não sua
premissa. A Tabela 6 do corpo traz as seis comparações do LinearSVC com
diferença, intervalo, grupos a favor de cada modelo, efeito e *p* ajustado; os
15 pares restantes estão na Tabela S12.

**Pressupostos periféricos saíram do corpo.** Shapiro-Wilk, Levene, VIF entre
confianças, outliers e a correlação entre confiança e acerto não decidem nada
sobre comparação pareada de classificadores binários e ocupavam uma subseção
inteira. Foram para a Tabela S15, com quinze referências que só sustentavam
esses testes retiradas da lista. A antiga Subseção 4.9 virou "Inferência sob
dependência textual" e contém apenas o que a hipótese exige.

**Categorias raras: alternativas medidas, protocolo mantido.**
`sensibilidade_classes_raras.json` mede a cobertura, de 99,37% das linhas e 82%
das categorias, e o macro-F1 sob três convenções de denominador: 0,6684 nas 41
avaliadas, 0,5481 projetado sobre as 50 da taxonomia com F1 zero nas ausentes,
e 0,6816 agregado às 14 famílias do primeiro nível. Reduzir k recuperaria três
categorias e dez linhas a k = 3, e foi recusado por ser decisão de protocolo
tomada depois de ver o resultado. A declaração de que o desempenho não cobre as
50 categorias está em negrito na Subseção 3.5.

**O ganho líquido deixou de pressupor custos iguais em silêncio.**
`utilidade_reclassificacao.json` explicita *U* = *b*×corrigidos −
*c*×prejudicados − *r*×revisados, normalizada por *b*, com as razões
adimensionais ρ = *c*/*b* e λ = *r*/*b* e sem qualquer valor monetário. O ganho
líquido simples é o caso ρ = 1 e λ = 0 e continua sendo o resultado principal.
A reescrita direta só compensaria com ρ abaixo de 0,2047 no melhor modelo, e a
utilidade é negativa em toda a faixa de 0,25 a 4. A mesma divergência, usada
para enfileirar auditoria em vez de reescrever, tem precisão de 18,53% contra
taxa de alteração de 4,25% na base congelada, enriquecimento de cerca de quatro
vezes, e paga enquanto λ ficar abaixo dessa precisão.

**Tamanho:** corpo científico em 13.719 palavras e fonte em 17.246, contra
13.323 e 16.851 ao fim da rodada anterior. Seis figuras e seis tabelas no
corpo, suplemento de S1 a S15.

**O que falta:** concluir a redução editorial até 8 a 9 mil palavras e cerca de
22 páginas, e revisar o PDF, que é gerado pelo workflow ao entrar em `main`. O
PDF publicado tem 28 páginas e não pôde ser regerado nesta rodada: o ambiente
local não dispõe de xelatex nem de Docker.

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
