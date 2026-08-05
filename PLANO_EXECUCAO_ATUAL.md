# PLANO ATUAL — REFORMULAÇÃO CIENTÍFICA E EXECUÇÃO CANÔNICA

> **LEITURA OBRIGATÓRIA ANTES DE ALTERAR CÓDIGO, RESULTADOS OU ARTIGO.**
>
> **Estado geral:** execução canônica `1e476243` concluída; artigo auditado número a número contra os artefatos e sem resíduo de rodadas incompatíveis; o corpus congelado não tem data de abertura, de modo que a avaliação temporal é inexecutável e o alcance prospectivo está declarado como condicional; título, resumos, Introdução, Referencial e Método reposicionados em torno do protocolo auditável; a Seção 4 foi reestruturada em cinco subseções hierarquizadas, sem vencedor absoluto declarado e com o corpo científico em cerca de 9.500 palavras, ainda cerca de 500 acima do limite superior da meta de 8 a 9 mil; resta revisar a Discussão por redundância remanescente, concluir o ajuste fino até a meta e revisar o PDF.
>
> **Regra principal:** os resultados atualmente publicados são resultados legados. Não atualizar o artigo com novos números até concluir uma única execução canônica, reproduzível e comum a todos os modelos.

Atualizado em 05/08/2026, no fuso America/Bahia.

**Pendência documental registrada em 05/08/2026:** não existe no repositório
documento de autorização institucional formal, de aprovação por comitê de ética
ou de dispensa de apreciação ética para uso científico dos registros do GLPI.
`Informação insuficiente para verificar.` O artigo declara essa ausência na
Subseção 3.8 e nada afirma sobre aprovação. Providenciar a formalização antes
da submissão.

## 1. Por que este plano existe

A auditoria do artigo e do repositório identificou que os resultados atuais não respondem integralmente ao desenho metodológico definitivo escolhido pelo autor. Há quatro causas centrais:

1. os modelos principais foram treinados com as categorias históricas do GLPI, enquanto a avaliação posterior utilizou a referência humana revisada;
2. a validação principal foi dividida por chamado, permitindo que textos idênticos ou muito semelhantes aparecessem em partições diferentes;
3. o BERTimbau não foi avaliado no mesmo protocolo *out-of-fold* integral dos sete modelos principais;
4. documentos e artefatos ainda misturam estados incompatíveis, incluindo 14.058 e 8.895 decisões, além de 50 categorias declaradas pelo autor e 56 categorias com suporte registradas nos resultados vigentes.

Essas diferenças não devem ser corrigidas apenas por edição textual. Elas exigem reconstrução do protocolo experimental, retreinamento, recomputação das métricas e somente depois reescrita do artigo.

## 2. Posicionamento científico aprovado

A contribuição central será apresentada como:

> **Fluxo híbrido, auditável e sensível à confiança para classificação e revisão de chamados de manutenção predial, com comparação entre modelos estatísticos, regras de domínio e modelo contextual, considerando desempenho e viabilidade computacional.**

Título vigente:

> **Classificação auditável de chamados de manutenção predial: fluxo humano–IA, calibração e risco de reclassificação**

O estudo atenderá a dois usos:

- classificação de chamados futuros;
- revisão e correção da base histórica.

O artigo não deve afirmar que já realiza previsão de demanda, previsão de custos ou classificação de criticidade. Sua contribuição para a tese é a camada auditável de governança e estruturação de dados que antecede essas aplicações preditivas.

## 3. Decisões autorais já encerradas

Estas decisões não precisam ser perguntadas novamente:

- o corpus informado contém 14.058 chamados revisados;
- a referência humana final foi definida para todos os registros;
- o autor informou taxonomia final de 50 categorias;
- a categoria da coluna C é a saída do GLPI, produto do registro pelo demandante e da verificação pela equipe de triagem, e não atribuição isolada;
- a revisão final foi feita por um único especialista, em desenho de auditoria sobre rótulo já verificado, e não de anotação do zero;
- o especialista analisou título, descrição do chamado, título e descrição de OSM, quando existentes, e a categoria histórica;
- previsões e níveis de confiança dos modelos não estavam visíveis durante a revisão;
- ver a categoria histórica é constitutivo da tarefa de auditoria, e não contaminação: julgar um rótulo inadequado pressupõe conhecê-lo;
- o artigo não deve descrever colunas da planilha no corpo científico;
- deve-se usar “referência humana final” ou “categoria de referência revisada”, não “verdade validada”;
- todos os modelos devem ser retreinados com a referência humana revisada, em partições que preservem a separação entre treino e teste;
- a validação cruzada agrupada será o protocolo principal;
- a divisão aleatória por chamado poderá permanecer apenas como análise de sensibilidade;
- o BERTimbau só participará da comparação principal se cumprir o mesmo protocolo;
- regras de periodicidade preventiva serão avaliadas como camada híbrida separada;
- a operação pretendida comparará sugestão humana e automação seletiva por confiança;
- os erros terão custo uniforme nesta versão;
- não haverá segunda avaliação humana; ver o Passo 9 para a justificativa;
- os detalhes de reprodutibilidade serão divididos entre corpo, suplemento e repositório;
- o periódico será escolhido depois da revisão;
- a meta editorial provisória é de 8 a 9 mil palavras.

## 4. Estado verificável no início desta execução

| Item | Decisão/valor pretendido | Estado atual observado | Situação |
|---|---:|---|---|
| Corpus revisado | 14.058 | o plano antigo também conserva referência a 8.895 | reconciliar |
| Taxonomia final | 50 categorias, conforme informação do autor | resultados e plano vigentes registram 56 categorias com suporte | reconciliar por código |
| Rótulo de treino | referência humana revisada | execução vigente usou histórico do GLPI | substituir |
| Partição principal | grupos textuais | execução vigente foi principalmente por registro | substituir |
| BERTimbau | mesmo protocolo ou suplemento | protocolo diferente dos sete modelos | decidir após teste de viabilidade |
| Resultados atuais | apenas histórico | ainda sustentam artigo, painel e JSONs | arquivar e substituir |
| Segunda revisão cega | descartada | inaplicável ao desenho de auditoria | encerrada, ver Passo 9 |

Nenhum número divergente deve ser escolhido por preferência editorial. O total correto precisa ser produzido por uma auditoria reproduzível da base e da taxonomia.

## 5. Regras inegociáveis

1. Trabalhar sempre em branch e Pull Request; nunca enviar diretamente para `main`.
2. Antes de qualquer escrita na planilha viva, executar e reportar *dry-run*.
3. Nunca apagar, limpar ou sobrescrever as conferências humanas M, N e P nem a categoria manual Q.
4. Localizar colunas por cabeçalho, não por posição fixa.
5. Preservar snapshots dos resultados legados; substituir referências canônicas somente após validação completa.
6. Executar, antes de cada commit de código:
   - `python -m unittest discover -s tests`;
   - `python -m py_compile src/*.py`.
7. Não declarar acesso à planilha, retreinamento, métrica, custo computacional ou validação como concluídos sem evidência real.
8. Toda afirmação teórica incluída no artigo deve ter referência bibliográfica verificável.
9. Não iniciar a redução editorial antes de congelar os novos resultados.
10. Atualizar este arquivo ao fim de cada passo, registrando evidências, arquivos e próxima ação.

## 6. Plano de execução e critérios de aceite

### Passo 0 — registrar o plano e o ponto de continuidade

**Objetivo:** impedir perda de contexto entre agentes e sessões.

**Entregas:**

- este documento;
- link destacado no início do `README.md`;
- atualização do “Estado desta rodada” em `PLANO_ARTIGO_CAPITULO.md`;
- Pull Request próprio.

**Aceite:** qualquer novo agente encontra, pelo topo do README, o motivo da reformulação, o estado real e o próximo passo.

### Passo 1 — congelar e auditar a base canônica

**Objetivo:** produzir uma referência única antes de qualquer treinamento.

**Ações:**

- materializar a referência humana final por registro;
- validar ausência de referência vazia ou inválida;
- reconciliar 14.058 versus 8.895;
- reconciliar 50 categorias declaradas versus 56 categorias com suporte;
- listar categorias, frequências e mapeamentos de normalização;
- registrar hash, data, fonte, denominadores e script;
- produzir relatório sem escrever na planilha.

**Aceite:**

- 100% dos registros elegíveis possuem referência válida;
- nenhuma categoria fica fora da taxonomia congelada;
- corpus e taxonomia têm os mesmos valores em relatório, testes e metadados;
- qualquer exclusão é nominal, justificada e reproduzível.

### Passo 2 — construir grupos textuais

**Objetivo:** impedir vazamento entre chamados duplicados.

**Ações:**

- normalizar os quatro campos textuais usados pelos modelos;
- gerar grupos de textos idênticos;
- diagnosticar quase duplicados em análise separada;
- definir limiar de similaridade somente com justificativa e teste de sensibilidade;
- salvar identificador ou hash do grupo por registro.

**Aceite:** nenhum grupo idêntico atravessa treino e teste.

### Passo 3 — gerar partições canônicas

**Objetivo:** garantir comparação justa entre os modelos.

**Ações:**

- usar `StratifiedGroupKFold`, preferencialmente com cinco partições e semente fixa;
- verificar suporte das 50 categorias em cada dobra;
- tratar explicitamente classes raras que impeçam estratificação;
- salvar IDs ou hashes das partições;
- usar as mesmas partições para todos os modelos e para a camada de regras;
- manter separação aleatória por chamado somente como sensibilidade.

**Aceite:** partições reproduzíveis, sem sobreposição de grupos e com relatório de distribuição por categoria.

### Passo 4 — retreinar os sete modelos principais

Modelos:

- Naive Bayes;
- regressão logística;
- Random Forest;
- Extra Trees;
- SGD;
- LinearSVC;
- LSTM.

**Regras:**

- referência humana final como rótulo;
- predições *out-of-fold* para todo o corpus elegível;
- busca de hiperparâmetros restrita aos dados de treinamento;
- mesma representação de entrada e mesmas partições comparáveis;
- registrar tempo, memória, versão de dependências e semente.

**Aceite:** cada registro recebe previsão de modelo que não treinou no próprio registro nem no seu grupo textual.

### Passo 5 — comparar modelo puro e regras preventivas

**Objetivo:** medir, e não presumir, o valor das regras de domínio.

**Ações:**

- implementar regras em módulo separado e auditável;
- comparar cada configuração nas mesmas partições;
- incluir termos de periodicidade, como mensal, semanal, trimestral e semestral, apenas na camada explícita;
- medir desempenho global e desempenho nos chamados preventivos;
- registrar conflitos entre regra e modelo.

**Aceite:** relatório mostra ganho ou perda com denominadores idênticos e sem alterar silenciosamente o rótulo de referência.

### Passo 6 — decidir o BERTimbau

**Condição para o corpo principal:** mesma referência, mesmos grupos, mesmas partições, mesmos registros e seleção de hiperparâmetros sem acesso ao teste.

Se a execução integral não for viável:

- preservar os resultados como experimento exploratório;
- mover a análise detalhada para o suplemento;
- registrar hardware, memória, duração e motivo objetivo da interrupção;
- não comparar diretamente rankings produzidos por protocolos distintos.

**Aceite:** decisão documentada por evidência computacional, sem alegação vaga de custo.

**Decisão tomada em 03/08/2026:** o BERTimbau **não** integra a comparação principal e fica como experimento exploratório no suplemento. A medição em `docs/CUSTO_BERTIMBAU.md` cronometrou 10,774 segundos por passo de fine-tuning, com variação entre 10,706 e 10,824, sobre executor hospedado de quatro processadores e sem GPU. São 701 passos por época e 2.103 por dobra, o que projeta 6,44 horas por dobra e 32,2 horas nas cinco. Uma única dobra já excede o teto de seis horas de um job, de modo que nenhuma dobra completa cabe na infraestrutura disponível. A interrupção é, portanto, por limite de infraestrutura verificado, e não por escolha editorial. Rankings produzidos sob protocolos distintos não devem ser comparados diretamente.

### Passo 7 — calibração e automação seletiva

**Ações:**

- calibrar somente com dados internos de treinamento;
- definir ECE e método de cálculo;
- produzir curva de confiabilidade;
- incluir métrica complementar adequada;
- selecionar limiares sem usar a dobra de teste;
- reportar cobertura, acurácia seletiva e taxa de encaminhamento humano;
- comparar sugestão humana e automação condicionada à confiança.

**Aceite:** nenhum dado de teste influencia calibração ou escolha do limiar.

### Passo 8 — inferência estatística

**Ações:**

- bootstrap por grupo textual, não por linha, tanto para as métricas quanto
  para as diferenças entre modelos;
- unidade estatística no grupo textual também nos testes de hipótese, e não
  apenas nos intervalos;
- teste global pela estatística Q de Cochran com distribuição de referência
  obtida por permutação do rótulo de modelo dentro de cada grupo;
- comparações pareadas por permutação com troca de sinal da diferença de
  acertos por grupo;
- correção de Holm sobre a família dos 21 pares;
- por comparação: diferença observada, intervalo da diferença, grupos que
  favorecem cada modelo, tamanho de efeito e *p* ajustado;
- limitar testes ao necessário para as hipóteses do artigo, mantendo
  pressupostos periféricos fora do corpo.

**Aceite:** todos os testes usam as mesmas observações pareadas, a mesma
execução canônica e a mesma unidade de dependência que o Passo 3 usou para
particionar.

### Passo 9 — segunda validação humana cega

**Encerrado em 03/08/2026 como NÃO APLICÁVEL ao desenho.** Não é dependência
pendente e não deve ser retomado como tarefa.

**Por que a especificação original não se sustenta.** O passo pedia um segundo
avaliador "sem acesso à categoria histórica". Isso descreve anotação do zero,
que é tarefa diferente da que foi executada e da que faz sentido executar aqui.
O que existe é auditoria de rótulo: a pergunta é se a categoria registrada é
adequada ao chamado, e a categoria é o objeto do julgamento. Ocultá-la não
remove viés, torna a tarefa impossível — para corrigir um rótulo é preciso
vê-lo, e isso vale igualmente para a triagem da etapa operacional.

**Por que a medida também não é necessária.** A pergunta de pesquisa é se os
modelos classificam corretamente contra uma referência, não se a referência
seria reproduzida por outra pessoa. Um Kappa entre humanos responderia à
segunda pergunta, e ainda assim mal: como o revisor viu a categoria antes de
decidir, o coeficiente sairia inflado pela adjudicação e violaria o pressuposto
de independência. Publicá-lo como confiabilidade entre avaliadores seria
afirmar mais do que o dado sustenta.

**O que ocupa o lugar dele.** O Passo 2 mediu 17 grupos de texto idêntico com
referência divergente, afetando 85 linhas, ou 0,61% das linhas avaliadas. É
inconsistência interna da própria referência, medida sem segundo avaliador.
`src/auditar_grupos_divergentes.py` caracterizou esses grupos em 05/08/2026: em
14 deles, somando 74 linhas, as categorias em disputa pertencem a tipos
distintos de manutenção, e o par dominante opõe `Hidrossanitária > Hidráulica`
a `Manutenção Preventiva > Reservatório`, com 11 grupos e 65 linhas. Trata-se,
portanto, de ambiguidade de contexto não textual, e **não** de piso de erro de
anotação; a expressão "piso de erro irredutível" saiu do artigo.

**O que o artigo pode e não pode afirmar.** Pode reportar a inconsistência
interna com a caracterização acima e descrever a linha de base como rótulo
administrativo verificado por equipe técnica, e não como atribuição única. Não
pode afirmar que a referência é reproduzível por outro especialista, nem
estimar a prevalência de erro do rótulo histórico, porque nada disso foi
medido; a ausência dessas medidas entra nas limitações, junto com o efeito de
ancoragem decorrente de o revisor decidir vendo o rótulo que audita.

**Aceite:** justificativa registrada e limitação declarada. Nada a executar.

### Passo 10 — proveniência e reconstrução dos artefatos

**Ações:**

- criar tabela ligando cada número, tabela e figura ao script, entrada, denominador, taxonomia, partições e hash;
- gerar JSONs, tabelas, figuras, painel e artigo a partir da mesma execução;
- verificar que resultados antigos não permanecem no Resumo, Abstract, discussão ou conclusão;
- revisar o PDF visualmente.

**Aceite:** cada afirmação quantitativa principal pode ser rastreada até um artefato canônico.

### Passo 11 — redução e reescrita editorial

**Somente após o Passo 10.**

**Corpo principal:**

- problema e contribuição;
- construção da referência humana;
- protocolo agrupado;
- modelos e camada de regras;
- métricas essenciais;
- confiança e custo computacional;
- resultados centrais e implicações operacionais.

**Suplemento:**

- hiperparâmetros completos;
- matrizes de confusão extensas;
- resultados por categoria;
- ablações;
- testes secundários;
- detalhes operacionais.

**Meta provisória:** 8 a 9 mil palavras, aproximadamente quatro figuras e quatro ou cinco tabelas principais, ajustável depois da escolha do periódico.

## 7. Resultados atuais: tratamento obrigatório

Os resultados publicados antes desta reformulação não devem ser apagados. Devem ser identificados como **snapshot legado**, porque respondem a outro protocolo.

Não reutilizar nas conclusões definitivas, sem recomputação:

- rankings dos modelos;
- acurácia e F1 atuais;
- testes estatísticos atuais;
- calibração e limiares atuais;
- comparações diretas com BERTimbau;
- tabelas e figuras derivadas desses valores.

A preservação do snapshot permite auditoria histórica e comparação metodológica, mas não autoriza misturar números antigos e novos.

## 8. Ordem prática das próximas Pull Requests

| PR | Escopo | Dependência | Estado |
|---|---|---|---|
| PR-0 | registrar plano, README e estado da rodada | nenhuma | concluído — [PR #164](https://github.com/adinailson88/classificacao-chamados/pull/164) |
| PR-1 | Passo 1: base e taxonomia canônicas | PR-0 | concluído — ferramenta no [PR #166](https://github.com/adinailson88/classificacao-chamados/pull/166) e auditoria final `apto_para_congelar` |
| PR-2 | Passos 2 e 3: grupos e partições | PR-1 | concluído — 9.786 grupos textuais e partições canônicas em cinco dobras, `apto_para_treinar` |
| PR-3 | Passos 4 e 5: sete modelos e regras | PR-2 | concluído — rodada canônica `3aa42e31` |
| PR-4 | Passo 6: BERTimbau | PR-2 | concluído — exploratório, por custo medido |
| PR-5 | Passos 7 e 8: calibração e estatística | PR-3 e PR-4 | concluído — inferência refeita no nível do grupo textual em 05/08/2026 |
| PR-6 | Passo 9: validação humana | nenhuma | encerrado como não aplicável ao desenho |
| PR-7 | Passo 10: proveniência e artefatos | PR-5 e PR-6 | concluído — números, tabelas e figuras substituídos pelos da rodada `1e476243` |
| PR-8 | Passo 11: reescrita editorial | PR-7 | em execução — corpo em ~13.300 palavras, meta de 8 a 9 mil |

## 9. Registro de andamento

| Data | Passo | Estado | Evidência | Próxima ação |
|---|---|---|---|---|
| 02/08/2026 | 0 | concluído | [PR #164](https://github.com/adinailson88/classificacao-chamados/pull/164), merge `e39338c` | iniciar o Passo 1 em nova branch: auditoria canônica da base e da taxonomia |
| 03/08/2026 | 1 | concluído | [workflow final](https://github.com/adinailson88/classificacao-chamados/actions/runs/30780457229), artefato `8844276140`, 14.060/14.060 referências válidas, 50/50 categorias e hash `e10c78e4db0026cfcbfa5267ddac034a3c8d3a7a0a1d63fa0cf2ce52f165b174` | executar o Passo 2: normalizar os quatro campos textuais e construir grupos de textos idênticos |
| 03/08/2026 | 2 | concluído | [PR #168](https://github.com/adinailson88/classificacao-chamados/pull/168), merge `b990cbe4`, [workflow](https://github.com/adinailson88/classificacao-chamados/actions/runs/30784573148); 14.060 linhas em 9.786 grupos textuais, 9.474 unitários, 4.586 linhas com duplicata (32,62%), maior grupo com 219 linhas, nenhum grupo maior que uma dobra e hash do mapa `ab352b9424e31d2644ed6d075643adf562acc38767e0098eed77595e2dea0bb6` | executar o Passo 3: `StratifiedGroupKFold` com k=5 e semente fixa sobre os grupos congelados |
| 03/08/2026 | 3 | concluído | [PR #171](https://github.com/adinailson88/classificacao-chamados/pull/171) e [PR #172](https://github.com/adinailson88/classificacao-chamados/pull/172), [workflow](https://github.com/adinailson88/classificacao-chamados/actions/runs/30861272862); 13.972 linhas em 9.734 grupos, cinco dobras de 2.556 a 3.045 linhas, nenhum grupo dividido, 41 das 50 categorias com suporte em todas as dobras, 88 linhas fora por suporte insuficiente e hash do mapa `9465857d83ba76ec193974982835d91e03e783587153e26597051d4dfd9abcf2` | executar o Passo 4: retreinar os sete modelos sobre estas partições, com a referência humana como rótulo |
| 03/08/2026 | 4 | concluído | rodada canônica `3aa42e31`, [workflow](https://github.com/adinailson88/classificacao-chamados/actions/runs/30869618529); 13.972 linhas e 41 categorias, predição *out-of-fold* nos sete modelos, zero vazamento de grupo; melhor macro-F1 e melhor acurácia no `linear_svc` (0,6696 e 0,8255) | executar o Passo 8: inferência estatística com bootstrap por grupo textual |
| 03/08/2026 | 8 | concluído | rodada canônica `3aa42e31`, `docs/INFERENCIA_CANONICA.md`; bootstrap de 1.000 repetições sobre 9.735 grupos, Cochran Q = 2669,67 com p nulo, McNemar nos 21 pares com Holm; 18 pares significativos e 3 empatados | executar o Passo 10: proveniência e artefatos |
| 03/08/2026 | 10 | em execução | `docs/MATRIZ_PROVENIENCIA.md`; os 5 artefatos derivados conferem o hash `3aa42e31` e os 3 do congelamento estão presentes; a varredura achou 35 ocorrências de números legados na fonte do artigo | substituir os números legados no artigo, o que é decisão editorial |
| 03/08/2026 | 5 | concluído | rodada canônica `3aa42e31`, mesmo run; regra dispara em 4.487 dos 13.972 registros e melhora o macro-F1 de apenas 3 dos 7 modelos, com ganho concentrado no `naive_bayes` | resultado negativo registrado; nada a executar |
| 03/08/2026 | 6 | concluído | [PR #178](https://github.com/adinailson88/classificacao-chamados/pull/178), [workflow](https://github.com/adinailson88/classificacao-chamados/actions/runs/30866677706); 10,774 s por passo em CPU de quatro núcleos, 2.103 passos por dobra, 6,44 h por dobra e 32,2 h nas cinco, contra teto de 6 h por job; BERTimbau fica como exploratório no suplemento | decisão registrada; BERTimbau fora da comparação principal |
| 03/08/2026 | 7 | concluído | rodada canônica `3aa42e31`, mesmo run; calibração isotônica em dobra interna reduz o ECE de 5 dos 7 modelos, com o `linear_svc` caindo de 0,6926 para 0,0173; ao alvo de 0,95 o `extra_trees` automatiza 67,9% com acurácia seletiva de 0,9507 e encaminha 32,1% ao humano | executar o Passo 8: inferência estatística |

| 04/08/2026 | 10 | concluído | rodada canônica `1e476243`, `docs/MATRIZ_PROVENIENCIA.md`; os 5 artefatos derivados e os 3 do congelamento conferem o hash; as Tabelas 1 a 5 do corpo, as Figuras 2 a 6 e as tabelas do apêndice passaram a sair da rodada canônica; a varredura caiu de 35 para 2 ocorrências, ambas falso positivo (`0,7781` é o acordo bruto do SGD) | executar o Passo 11: redução editorial |
| 04/08/2026 | 11 | em execução | corpo do artigo de 14.782 para ~13.100 palavras; cinco tabelas no corpo e cinco movidas ao suplemento (S7 a S11); a antiga Tabela 3 virou S6; removida a Subseção 3.7, de fluxo interno de triagem; corrigido o protocolo declarado na Subseção 3.5, que ainda dizia `KFold` por linha | concluir a redução até 8 a 9 mil palavras e revisar o PDF |
| 05/08/2026 | 11 | em execução | rodada da referência humana: o artigo passou a nomear o desenho como auditoria administrativa de rótulo por avaliador único, e não anotação independente; os 4,25% viraram taxa de alteração do rótulo histórico, o que elimina a contradição com a limitação sobre prevalência; a ancoragem entrou como ressalva explícita; a ausência de segunda avaliação, de cegamento e de adjudicação está declarada, com a segunda avaliação registrada como validação futura; `src/auditar_grupos_divergentes.py` e `docs/dados/grupos_divergentes_canonicos.json` caracterizaram os 17 grupos e 85 linhas divergentes, mostrando que 14 grupos e 74 linhas opõem tipos distintos de manutenção, o que retira do valor o rótulo de piso de erro irredutível; Figura 1 e Subseção 3.1 recolocaram a revisão humana antes do treino e sobre o corpus integral; Subseção 3.8 registrou a governança de dados e a ausência de documento de ética ou autorização; corrigido "três registros" para dois com texto editado após o congelamento; fonte de 17.244 para 17.209 palavras | concluir a redução até 8 a 9 mil palavras e revisar o PDF gerado em `main` |
| 04/08/2026 | 10 | concluído | auditoria canônica dos bloqueadores numéricos, `docs/RASTREABILIDADE_LSTM.md`; matriz de proveniência ampliada com as grandezas de fora da rodada e suas ressalvas; 74 números do artigo conferidos contra os artefatos, com zero divergências, e nenhum decimal do corpo sem lastro em artefato versionado; 9.786/9.735/9.734 conciliados; discrepância do LSTM atribuída à coincidência de 100% entre referência e histórico nas 9.096 linhas do *ablation*; `src/ablation_lstm.py` corrigido, com regressão em `tests/test_ablation_lstm_chave.py` | executar o Passo 11: reduzir o corpo até 8 a 9 mil palavras e o PDF de 28 para cerca de 22 páginas |
| 05/08/2026 | 8 e 11 | concluído o 8, em execução o 11 | rodada canônica `1e476243`, `docs/INFERENCIA_AGRUPADA.md`, `docs/SENSIBILIDADE_CLASSES_RARAS.md` e `docs/UTILIDADE_RECLASSIFICACAO.md`; auditoria da unidade estatística mediu efeito de desenho entre 4,47 e 8,83, isto é, o McNemar por linha declarava erro padrão de 2,1 a 3,0 vezes menor do que a amostra sustenta; inferência refeita no nível do grupo, com Q de Cochran contra permutação por grupo (p < 0,0005), 21 permutações pareadas com Holm e bootstrap de conglomerados da diferença; os 21 vereditos não mudam, 19 significativos e 2 empatados; Subseção 4.9 reescrita e Shapiro-Wilk, Levene, VIF, outliers e correlação confiança-acerto retirados do corpo para a Tabela S15, com 15 referências órfãs removidas; sensibilidade das classes raras mediu cobertura de 99,37% das linhas e 82% das categorias e macro-F1 de 0,6684, 0,5481 e 0,6816 sob as três convenções de denominador; ganho líquido ganhou função de utilidade com ρ e λ adimensionais, ρ de equilíbrio de 0,2047 no melhor modelo e precisão de fila de triagem de 18,53%; corpo científico de 13.350 para 13.323 palavras e sete para seis figuras | concluir a redução até 8 a 9 mil palavras e revisar o PDF gerado em `main` |
| 05/08/2026 | 11 | em execução | rodada da validação temporal: `src/auditar_disponibilidade_temporal.py` e `docs/dados/disponibilidade_temporal.json` verificaram o contrato de colunas de `AGENTS.md` e os sete artefatos do congelamento e da rodada canônica, com veredito `sem_variavel_temporal` e zero campos candidatos a data do chamado, apenas carimbos `gerado_em` de geração de artefato; a avaliação em períodos sucessivos é, portanto, inexecutável sobre o corpus congelado e nenhum número temporal foi produzido; o artigo passou a declarar corte de extração na Subseção 3.2, a delimitar na 3.5 que o protocolo estima generalização entre grupos textuais e não desempenho futuro, a registrar na 5.3 a limitação e os riscos de implantação, e a condicionar as afirmações prospectivas da 5.2, da 5.4 e da Seção 6; corpo de 13.323 para 13.719 palavras, com compensação parcial na Discussão | reconstituir o corte preservando a data de abertura, o que habilita a avaliação temporal, e concluir a redução até 8 a 9 mil palavras |
| 05/08/2026 | 11 | em execução | rodada de posicionamento editorial: o título passou a nomear a contribuição real, sem multimodelo, sem validação humana e sem promessa temporal; Resumo e Abstract foram reescritos em estrutura paralela de nove movimentos, de 436 para 249 e de 413 para 247 palavras; a Introdução foi reordenada em relevância, registros textuais, rótulos históricos, lacuna, pergunta, contribuição e objetivo, com os quatro objetivos específicos substituídos por um objetivo geral e cinco contribuições, e caiu de 719 para 571 palavras; o Referencial foi reorganizado em quatro subseções, com uma nova sobre calibração e classificação seletiva, e caiu de 732 para 550 palavras; entraram CHOW (1970) e EL-YANIV; WIENER (2010) e saiu VASWANI *et al.* (2017), órfã após os cortes; os símbolos Unicode crus rô, lambda e menor ou igual viraram `$\rho$`, `$\lambda$` e `$\leq$`, com a conversão a LaTeX verificada por pandoc; 507 testes aprovados e matriz de proveniência sem divergências | concluir a redução até 8 a 9 mil palavras e revisar o PDF gerado em `main` |
| 05/08/2026 | 11 | em execução | rodada do método reprodutível: a Seção 3 foi reestruturada de oito para seis subseções, na ordem delineamento e referência revisada, pré-processamento e representação, modelos e configuração experimental, validação e calibração e inferência, reclassificação e análises complementares, e reprodutibilidade e governança; entrou a Tabela 1 com modelo, representação, hiperparâmetros, balanceamento, saída de confiança e papel, o que deslocou as tabelas do corpo de 1 a 6 para 2 a 7; as famílias de modelos deixaram de ser explicadas duas vezes e o `StratifiedGroupKFold` passou a ser descrito uma única vez; cada afirmação foi conferida contra `src/modelos_zoo.py`, `src/modelo_lstm.py`, `src/construir_grupos_textuais.py`, `src/gerar_particoes_canonicas.py` e `src/calibrar_confianca.py`, entrando os itens verificáveis que faltavam e saindo a regra de contingência do Random Forest, que é de produção; a calibração passou a declarar sem ambiguidade a dobra interna de ajuste, a dobra externa de avaliação e a ausência de acesso ao teste por transformações, tokenizadores, vocabulários, calibradores e limiares; 9.786, 9.735 e 9.734 estão distinguidos no corpo; auditoria independente incorporada: a consistência interna deixou de ser apresentada como dispensa de segundo avaliador, os 17 grupos divergentes deixaram de delimitar teto quantitativo e seus números passaram à Subseção 4.6, a declaração de sementes passou a registrar que a execução canônica da LSTM não fixou a semente global do TensorFlow e que a reprodução exata dos pesos não é garantida, e a discussão histórica de *post-hoc* saiu do corpo, com a remoção de BENAVOLI; CORANI; MANGILI (2016), DEMŠAR (2006), NEMENYI (1963) e NOMA *et al.* (2021), órfãs; Método de 2.972 para 2.228 palavras, menos 25,03%, dentro da meta; 507 testes aprovados e matriz de proveniência sem divergências | concluir a redução editorial nos Resultados e na Discussão e revisar o PDF gerado em `main` |
| 05/08/2026 | 11 | em execução | rodada dos resultados hierarquizados: a Seção 4 foi reestruturada de doze para cinco subseções, na ordem desempenho/incerteza/custo, auditoria do histórico e risco de reclassificação, calibração e automação seletiva, erros por categoria e implicações taxonômicas e análises complementares; a concordância histórica, a acurácia, o macro-F1, o custo de treino e o núcleo da inferência sob dependência textual fundiram-se em uma única tabela de desempenho (nova Tabela 2), substituindo três tabelas antigas; a tabela de calibração foi reduzida aos quatro modelos mais competitivos, com o ECE piorado do Naive Bayes e do LSTM declarado em texto e a tabela completa dos sete no suplemento; a matriz de 21 comparações pareadas saiu do corpo, restando teste global, contagem de pares significativos e um exemplo em prosa; as figuras foram renumeradas pela nova ordem de aparição (trade-off de custo passou a Figura 2, confiabilidade a Figura 3, mapa de categorias a Figura 4, matriz de confusão a Figura 5, curva do LSTM manteve o número 6); o parágrafo de abertura deixou de declarar o LinearSVC vencedor absoluto, registrando que a Regressão Logística tem macro-F1 pontual ligeiramente superior e o SGD permanece próximo; o macro-F1 de 0,5481 passou a cenário conservador de sensibilidade; os 17 grupos e 85 linhas divergentes, os 14 grupos e 74 linhas entre tipos distintos e o par dominante permanecem no corpo, sem tratamento de teto; todas as remissões a "Subseção 4.X" no Método, na Discussão e nas Considerações Finais foram remapeadas para a nova numeração; a frase "não está em falha de cálculo" saiu do texto; Seção 4 de 6.082 para cerca de 3.680 palavras, menos 39,5%, dentro da meta de 30% a 40%; corpo científico de cerca de 11.900 para cerca de 9.500 palavras, aproximando-se da meta final de 8 a 9 mil, mas ainda cerca de 500 palavras acima do limite superior; 507 testes aprovados e matriz de proveniência sem divergências | revisar a Discussão por redundância remanescente com a Seção 4, concluir o ajuste fino até 8 a 9 mil palavras e revisar o PDF gerado em `main` |
Estados permitidos: `pendente`, `em execução`, `bloqueado`, `concluído`, `substituído`.

## 10. Instruções para continuidade por outro agente

Ao retomar:

1. ler `AGENTS.md`, este arquivo, `PLANO_ARTIGO_CAPITULO.md`, `CONTEXTO.md` e `04_artigo/README.md`;
2. verificar o PR e a branch em andamento;
3. conferir a última linha da seção “Registro de andamento”;
4. não repetir perguntas autorais registradas na seção 3;
5. não iniciar pelo artigo: iniciar pelo primeiro passo técnico pendente;
6. antes de alterar código, inspecionar testes e artefatos já existentes;
7. atualizar esta tabela e o “Estado desta rodada” ao concluir cada PR;
8. informar com precisão qualquer credencial ou workflow que falte, sem inventar execução.

### Prompt curto de retomada

> No repositório `adinailson88/classificacao-chamados`, leia primeiro `AGENTS.md` e `PLANO_EXECUCAO_ATUAL.md`. Continue a partir do primeiro passo técnico pendente no “Registro de andamento”. Trabalhe em branch e Pull Request, preserve M/N/P/Q, execute os testes exigidos antes de commits de código e atualize o plano com evidências reais. Não reescreva o artigo antes da execução canônica.
