# PLANO ATUAL — REFORMULAÇÃO CIENTÍFICA E EXECUÇÃO CANÔNICA

> **LEITURA OBRIGATÓRIA ANTES DE ALTERAR CÓDIGO, RESULTADOS OU ARTIGO.**
>
> **Estado geral:** decisões científicas aprovadas; nova execução experimental ainda não iniciada.
>
> **Regra principal:** os resultados atualmente publicados são resultados legados. Não atualizar o artigo com novos números até concluir uma única execução canônica, reproduzível e comum a todos os modelos.

Atualizado em 02/08/2026, no fuso America/Bahia.

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

Título provisório:

> **Classificação auditável de chamados de manutenção predial: um fluxo híbrido humano–IA com automação seletiva por confiança**

O estudo atenderá a dois usos:

- classificação de chamados futuros;
- revisão e correção da base histórica.

O artigo não deve afirmar que já realiza previsão de demanda, previsão de custos ou classificação de criticidade. Sua contribuição para a tese é a camada auditável de governança e estruturação de dados que antecede essas aplicações preditivas.

## 3. Decisões autorais já encerradas

Estas decisões não precisam ser perguntadas novamente:

- o corpus informado contém 14.058 chamados revisados;
- a referência humana final foi definida para todos os registros;
- o autor informou taxonomia final de 50 categorias;
- a revisão final foi feita por um único especialista;
- o especialista analisou título, descrição do chamado, título e descrição de OSM, quando existentes, e a categoria histórica;
- previsões e níveis de confiança dos modelos não estavam visíveis durante a revisão;
- a categoria histórica pode ter produzido viés de ancoragem e isso deve constar nas limitações;
- o artigo não deve descrever colunas da planilha no corpo científico;
- deve-se usar “referência humana final” ou “categoria de referência revisada”, não “verdade validada”;
- todos os modelos devem ser retreinados com a referência humana revisada, em partições que preservem a separação entre treino e teste;
- a validação cruzada agrupada será o protocolo principal;
- a divisão aleatória por chamado poderá permanecer apenas como análise de sensibilidade;
- o BERTimbau só participará da comparação principal se cumprir o mesmo protocolo;
- regras de periodicidade preventiva serão avaliadas como camada híbrida separada;
- a operação pretendida comparará sugestão humana e automação seletiva por confiança;
- os erros terão custo uniforme nesta versão;
- haverá segunda avaliação humana independente e cega em amostra estratificada;
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
| Segunda revisão cega | amostra estratificada | não executada | dependência humana |

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

- bootstrap por grupo textual, não por linha;
- intervalos de confiança das métricas principais;
- Cochran Q para comparação global aplicável;
- McNemar pareado;
- correção de Holm;
- limitar testes ao necessário para as hipóteses do artigo.

**Aceite:** todos os testes usam as mesmas observações pareadas e a mesma execução canônica.

### Passo 9 — segunda validação humana cega

**Dependência externa ao código.**

**Desenho:**

- segundo avaliador sem acesso à categoria histórica e às previsões;
- amostra estratificada pelas categorias;
- representação de casos confirmados e dos casos corrigidos;
- tamanho amostral justificado antes da seleção;
- concordância bruta e coeficiente de Cohen;
- divergências resolvidas por consenso ou terceiro avaliador.

**Aceite:** protocolo, amostra, decisões e resolução de divergências ficam rastreáveis.

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
| PR-0 | registrar plano, README e estado da rodada | nenhuma | em execução |
| PR-1 | Passo 1: base e taxonomia canônicas | PR-0 | pendente |
| PR-2 | Passos 2 e 3: grupos e partições | PR-1 | pendente |
| PR-3 | Passos 4 e 5: sete modelos e regras | PR-2 | pendente |
| PR-4 | Passo 6: BERTimbau | PR-2 | pendente |
| PR-5 | Passos 7 e 8: calibração e estatística | PR-3 e PR-4 | pendente |
| PR-6 | Passo 9: validação humana | protocolo aprovado | pendente externo |
| PR-7 | Passo 10: proveniência e artefatos | PR-5 e PR-6 | pendente |
| PR-8 | Passo 11: reescrita editorial | PR-7 | pendente |

## 9. Registro de andamento

| Data | Passo | Estado | Evidência | Próxima ação |
|---|---|---|---|---|
| 02/08/2026 | 0 | em execução | branch `agent/plano-reformulacao-cientifica` | publicar PR-0 e iniciar auditoria canônica |

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
