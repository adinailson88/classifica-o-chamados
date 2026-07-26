# Plano — Artigo/Capítulo "Classificação de Chamados com IA" (tese Biossistemas)

> Documento único desta finalidade. Não criar `PLANO_ARTIGO_v2.md`, `RASCUNHO_*.md` ou
> similares — **atualizar este arquivo** a cada rodada, na seção "Estado desta rodada"
> logo abaixo. Segue a mesma convenção de `PLANO_CALIBRACAO.md`, `FALTA_FAZER.md` e
> `CONTEXTO.md` já usada neste repositório (ver [[memoria-transferencia-codex]]).
>
> Escopo: o capítulo/artigo empírico sobre o **experimento de classificação/
> reclassificação de chamados com IA local** (LSTM/RF/multimodelo/BERTimbau), que se
> torna capítulo da tese e pode também virar submissão própria. É a contraparte
> empírica do artigo de revisão (`adinailson88/revisao-bibliografica`, MCDM/TOPSIS/
> ODS/ESG) — ver Seção 5 sobre a ponte entre os dois.

## Regra de execução (ler antes de mexer no artigo)

Toda vez que o Adinailson pedir para avançar neste capítulo/artigo, a sessão deve, na
ordem:

1. **Ler a seção "Estado desta rodada"** abaixo antes de escrever qualquer texto novo.
2. Revalidar contra a fonte viva do repositório os números que pretende citar (dados
   de `docs/dados/*.json` mudam a cada execução de workflow — ver regra de
   revalidação em [[artigo-metodologia-biossistemas]]). Não reaproveitar números de
   auditorias antigas sem conferir a data.
3. Ao terminar o que foi pedido nesta rodada, **substituir** (não acrescentar sem
   critério) a seção "Estado desta rodada" com três blocos obrigatórios:
   - **Onde está**: em qual seção/etapa do plano abaixo (ex.: "Seção 4.2 do artigo,
     aguardando fechar 4.6").
   - **O que foi feito nesta rodada**: resumo verificável (arquivos alterados,
     números conferidos, o que foi descartado e por quê).
   - **Próximo passo**: uma ação concreta e priorizada, não uma lista genérica.

Isso substitui a necessidade de o usuário reexplicar contexto a cada nova conversa.

---

## Plano de reformulação editorial (rodada 23, substitui a abordagem anterior)

O Adinailson trouxe um plano editorial externo (avaliado como melhor que a
abordagem de polimento incremental das rodadas 20-22) e pediu para ele
**substituir** a orientação anterior de "revisar formatação/prolixidade" por
uma reformulação de conteúdo: transformar o texto de relatório técnico
detalhado em capítulo de tese/artigo de alto impacto, integrado
explicitamente ao projeto de doutorado "Modelo Preditivo de Governança
Sustentável" (o artigo é o **Eixo 1**: transformar texto livre de chamados em
dado estruturado para alimentar os Eixos 2 previsão de custos/séries
temporais, 3 MCDM/ESG/ODS e 4 geoprocessamento).

Seis tarefas do plano (ordem de execução, não a ordem em que foram dadas):

1. Remover o Apêndice A (dicionário de colunas) — documentação de sistema,
   não conteúdo científico.
2. Condensar as Limitações (estavam em 6 parágrafos com datas/rodadas) em 3
   parágrafos: cobertura, validação, modelo.
3. Adicionar subseção na Discussão amarrando o artigo ao papel de "fundação
   de dados" da tese (Eixos 2-4).
4. Reformular a Introdução: abrir pela tensão de governança em biossistemas
   construídos (Capra, Odum, Grimm), pergunta central não é "qual
   classificador é melhor" e sim "como extrair dado estruturado auditável de
   texto ruidoso para alimentar governança preditiva"; remover datas,
   caminhos de script e nomes de arquivo do corpo.
5. Condensar Método (3.4, organizar por família — linear/ensemble/neural —
   com justificativa conceitual, não hiperparâmetro por hiperparâmetro) e
   Resultados (resumir aos 3 achados principais; consolidar Shapiro/
   Friedman/McNemar num parágrafo; mover detalhe estatístico para Material
   Suplementar; remover "Nota de rastreabilidade (data)").
6. Passe de estilo geral: parágrafos > 10 linhas quebrados, remover
   "na interpretação do autor" e hedging repetitivo, checar duplicidade de
   citação (ex.: Deng et al.), manter ABNT (não mexe no formato de citação).

**Onde está**: Etapas 1-4 concluídas (branch
`docs/reformulacao-editorial-governanca-preditiva`, PR #73, ainda sem
merge — mudança de conteúdo grande, revisão em fatias). Etapas 5-6
pendentes.

**O que foi feito até agora**:
1. Apêndice A (dicionário de colunas A:P) removido; substituído por uma
   frase apontando para o repositório público. Apêndice B (checklist) e C
   (matriz M/N/P) renumerados para A e B.
2. Limitações (dentro da Seção 5, Discussão) condensadas de 6 parágrafos
   com datas de rodada para 3 parágrafos — cobertura, validação, modelo.
3. Nova subseção **"Papel no modelo de governança preditiva"** ao final
   da Seção 5 (Discussão) — liga os dados de saída (categoria,
   criticidade, confiança) aos três eixos seguintes da tese (séries
   temporais ARIMA/SES, matriz MCDM/ESG/ODS, geoprocessamento via Google
   Earth Engine); afirma que este capítulo entrega a "fundação de dados"
   do modelo de governança.
4. **Introdução reformulada**: abre pela tensão de governança em
   biossistemas construídos (CAPRA, 1996; ODUM, 1971; GRIMM *et al.*,
   2008 — três referências novas, inseridas em ordem alfabética na lista
   ABNT) em vez de partir direto da lacuna técnica de PLN. Pergunta
   central reformulada: não "qual classificador é melhor", mas como
   extrair dado estruturado auditável de texto ruidoso para alimentar
   governança preditiva. Classificação automática agora é explicitamente
   apresentada como primeira camada de um protocolo maior, não produto
   final. Removida a única data solta da seção (23/07/2026). Revisão de
   literatura já citada (Li *et al.* 2024, Sundaram e Zeid 2025,
   Bouabdallaoui *et al.* 2020, Zhang *et al.* 2025, Kejriwal *et al.*
   2024) mantida intacta.

**Próximo passo**: Etapa 5 — condensar Método 3.4 (reorganizar por
família de modelo: linear/ensemble/neural, com justificativa conceitual
por família, não hiperparâmetro por hiperparâmetro; manter ênfase no
protocolo de validação out-of-fold + validação humana como diferencial)
e condensar Resultados (4.1-4.10) aos 3 achados principais do plano —
(a) lineares superam neurais/ensembles em texto curto e desbalanceado,
com vantagem de custo; (b) validação humana confirmou ruído real no
rótulo histórico (~3,5%); (c) meta de calibração próxima mas não
formalmente probabilística — consolidando Shapiro/Friedman/Nemenyi/
McNemar num único parágrafo e movendo detalhe estatístico para Material
Suplementar. Depois, Etapa 6 (passe de estilo geral: parágrafos longos,
"na interpretação do autor", duplicidade de citação) sobre o texto já
reformulado. Antes de fechar, revalidar contra `docs/dados/*.json`
qualquer número citado nas seções reescritas. Ao final, gerar novo PDF
(`artigo_pdf.yml`) e revisar visualmente.

---

### Histórico da rodada 21 (rigor formal MDPI: figuras 300dpi, dois autores, declarações)

**Contexto**: seguindo o Passo 5 do prompt original de 6 passos ("rigor
formal de submissão MDPI: metadados, figuras 300dpi, subseção 5.4
dedicada"), o Adinailson confirmou: (a) escrever scripts Python/R para
gerar as Figuras 1–3 (que não tinham script gerador no repo), seguindo o
estilo de um artigo-exemplo que ele anexou (rascunho não citável,
"Random Forest e Lógica Fuzzy..."); (b) autoria: Adinailson Guimarães de
Oliveira + orientador Prof. Dr. Fabrício Berton Zanchi (UFSB); (c) sem
financiamento formal, sem IRB/consentimento informado aplicável.

**Onde está**: concluído nesta branch
(`docs/mdpi-figuras-300dpi-declaracoes`).

1. **Figuras 1–3 (sem script antes)**: criados
   `src/gerar_figura1_pipeline.py` (diagrama estático do pipeline, não
   depende de dado vivo), `src/gerar_figura2_confianca_desfecho.py` (lê
   `calibracao.json#por_faixa`, mesmos números da Tabela 3) e
   `src/gerar_figura3_tradeoff_custo.py` (cruza `comparacao_modelos.json`
   — lote de 1.000 registros — com `avaliacao_final.json#por_modelo`).
   Nenhum número foi digitado à mão; os três leem o JSON vigente do
   painel.
2. **Figuras 4–6 (já tinham script)**: `dpi=220` → `dpi=300` em
   `src/ablation_lstm.py`, `src/gerar_figura4_confusoes.py` e
   `src/modelo_lstm.py`. Regeneradas sem retreinar: Fig4 rodando o
   script normal (só plota, não depende de treino); Fig5 e Fig6
   chamando as funções de plot já existentes (`plotar_history`,
   `salvar_figura`) com os artefatos já salvos em cache
   (`lstm_history.json`, `ablation_lstm_resultados.json`) em vez de
   re-treinar o LSTM. As 6 figuras confirmadas a 300dpi (`PIL.Image.info`).
3. **Autoria e declarações MDPI**: cabeçalho do artigo passou a listar
   os dois autores (E-mail de cada um, F.B.Z. identificado como
   orientador). Acrescentado o bloco de declarações obrigatórias da
   MDPI antes da lista de REFERÊNCIAS: Author Contributions (papéis
   reais, não genéricos — F.B.Z. como supervisão/administração,
   A.G.O. como execução), Funding ("no external funding"),
   Institutional Review Board Statement e Informed Consent Statement
   ("Not applicable", com justificativa de que não há pesquisa com
   seres humanos — a conferência é atividade interna de qualidade,
   não protocolo experimental), Data Availability Statement (dados da
   planilha institucional não públicos por confidencialidade; código
   público no GitHub), Acknowledgments, Conflicts of Interest.
4. Suíte completa: 90/90.

**Ressalva importante sobre dados transitórios**: a rematerialização da
Etapa 1 oficial (rodada 20, item 3 abaixo) ainda está em andamento via
cron (`etapa1_turnos.yml`, a cada 15 min) quando esta rodada foi feita.
A Figura 2 e a Figura 3, por lerem o JSON vigente, já refletem números
ligeiramente diferentes dos publicados nas Tabelas 3 e 7 do texto (que
ficaram congeladas na última consolidação). Isso é esperado e
transitório — quando o cron terminar de reclassificar a base inteira,
recomenda-se rodar os três scripts de novo (`gerar_figura2_confianca_desfecho.py`,
`gerar_figura3_tradeoff_custo.py`) e também atualizar as Tabelas 3 e 7 do
texto para os números finais, num novo snapshot.

**Próximo passo**: (1) revisar/mergear o PR desta rodada; (2) quando o
cron de rematerialização da Etapa 1 terminar (pode levar mais de um
dia), regerar Figuras 2–3 e atualizar Tabelas 3 e 7 com os números
finais, e então gerar um snapshot de fechamento; (3) subseção dedicada
de rigor formal (se o Adinailson ainda quiser uma "5.4" textual
explícita além do bloco de declarações já inserido — confirmar com ele
o que exatamente falta, já que "subseção 5.4" no prompt original de 6
passos provavelmente já se referia a este bloco de declarações).

---

### Histórico da rodada 20 (4 referências CAPES restantes; remoção da coautoria Claude; rematerialização da Etapa 1; referências MDPI numérico)

**Contexto**: o Adinailson pediu, em uma única mensagem, 4 coisas: (1)
incluir as "10 alternativas CAPES" da rodada 19, só as já salvas no
Drive; (2) avaliar 2 PDFs anexados (outliers em bibliometria;
Durbin-Watson) para os gaps declarados na rodada 19; (3) gerar novo
snapshot, mesclar, e remover `Co-Authored-By: Claude` de **todo** o
histórico de commits (force-push confirmado, mesmo com o risco de
quebrar outros clones/sessões); (4) assumir os Passos 3–6 pendentes
(antes reservados ao Codex).

**Onde está**: os 4 pontos concluídos.

1. **CAPES + PDFs (pontos 1–2)**: PR #66 mesclado. 4 referências CAPES
   que faltavam (Hodge e Austin 2004, DiCiccio e Efron 1996, Kornbrot
   2014, Wongpakaran *et al.* 2013) inseridas na Subseção 4.10/3.5 e na
   bibliografia — as outras 6 da lista de 10 já estavam citadas.
   `Durbin-Watson.pdf` rejeitado (nota autopublicada no ResearchGate, sem
   revisão por pares); a lacuna de Durbin-Watson/ACF continua declarada,
   agora com nota de transparência. PDF de outliers bibliométricos (Lima
   *et al.*, 2017, *Em Questão*/UFRGS, revisado por pares) aceito como
   apoio ao Tukey/IQR, com analogia explícita para ML. Novo snapshot
   `artigo-v3-20260726` gerado e mesclado.
2. **Reescrita de histórico (ponto 3)**: `git filter-repo` removeu
   `Co-Authored-By: Claude` de 110 commits no `main`; árvore de arquivos
   verificada idêntica (mesmo hash) antes/depois; force-push isolado,
   feito só depois de confirmar que nenhuma outra sessão tinha tocado o
   `main` nesse meio-tempo. GitHub confirmado sem Claude nos Contributors.
3. **Rematerialização da Etapa 1 oficial (Passo 3)**: cabeçalho real da
   planilha confirmado pelo Adinailson (`L = Classificado_Confiança_IA`,
   uma fórmula nativa que recalcula sozinha — resolveu divergência entre
   `CONTEXTO.md` e o docstring de `resetar_experimento.py`). Script novo
   `src/rematerializar_etapa1_oficial.py` + workflow
   `rematerializar_etapa1_oficial.yml` (PR #67, mesclado): limpam SOMENTE
   G2:K, preservando L (fórmula), M/N/O/P/Q (conferência humana e Etapa
   2) e todas as abas de log. Dry-run confirmou 13.965 linhas afetadas;
   aplicado de verdade com backup automático (`BACKUP_ETAPA1_20260726_131413`).
   O cron de produção (`etapa1_turnos.yml`, a cada 15 min) assumiu o
   reprocessamento gradual — não precisa de acompanhamento manual.
4. **Passo 6 — referências em formato MDPI numérico**: convertido o
   artigo inteiro (`04_artigo/artigo_classificacao_chamados_v3.md`) de
   citação autor-data (ABNT) para numérica ([1], [2,3]...), ordem de
   primeira citação, como exigido pela revista alvo (*Buildings*, MDPI).
   Feito via script de conversão (não editado à mão): mapeou as 56
   referências da bibliografia por (sobrenome, ano), localizou todas as
   ~109 ocorrências de citação no corpo (formas ABNT maiúsculas,
   narrativas em minúsculas, e bundles com prosa embutida em células de
   tabela do Apêndice B), atribuiu os números por ordem de primeira
   aparição e substituiu. Verificações feitas antes de aplicar: as 56
   referências têm pelo menos uma citação encontrada; os números 1–56
   aparecem cada um pelo menos uma vez no corpo (nenhum buraco, nenhum
   número fora do intervalo); nenhum padrão autor-ano remanescente sobrou
   fora da lista de referências; cabeçalhos de seção, legendas de
   figura/tabela e conteúdo das tabelas continuam byte-a-byte idênticos
   (`diff` vazio). A lista de REFERÊNCIAS foi reordenada e renumerada,
   mas o texto bibliográfico de cada entrada foi mantido como estava
   (não reformatado campo a campo para a micro-sintaxe exata da MDPI).
5. Suíte completa: 90/90 em cada PR (mudança só em Markdown/JSON de
   snapshot).

**Próximo passo**: resolvido na rodada 21 (figuras 300dpi + declarações
MDPI) — ver acima.

---

### Histórico da rodada 19 (limite de 10 anos + acesso aos arquivos das referências estatísticas)

**Contexto**: o Adinailson perguntou se as 19 referências estatísticas da
rodada 18 existem na pasta do acervo do Drive (`Referência Bibliográfica
- Drive/README.md`) e pediu duas coisas: (1) nenhuma referência com mais
de 10 anos — mas todas as 19 são os artigos ORIGINAIS de cada teste
clássico (Shapiro-Wilk 1965, Friedman 1937, Cochran 1950 etc.), o que é
inevitável (o teste nasceu naquele ano); (2) link de acesso (Scopus, Web
of Science ou DOI) para as que não estão salvas no Drive. Perguntei antes
de agir (`AskUserQuestion`) porque forçar "só ≤10 anos" sem contexto
faria eu inventar ou descartar referências fundadoras — ele escolheu
manter os originais + adicionar um artigo recente de apoio para cada
teste, e pediu os links de acesso para as 17 que faltam no Drive.

**Onde está**: concluído, branch `docs/referencias-recentes-complementares`.
1. **Verificação no Drive**: só 2 das 19 (ZUUR 2010, RAZALI; WAH 2011) já
   estão salvas em `03_Predicao_Custos_e_Estatistica` do acervo, com
   link de acesso no README. As outras 17 não estão no Drive.
2. **5 referências recentes (≤10 anos) adicionadas**, uma para cada
   cluster de testes, todas verificadas via busca web (DOI/venue
   conferidos, não só memória): BENAVOLI; CORANI; MANGILI (2016, JMLR) —
   crítica ao Nemenyi/postos médios, cita explicitamente por que este
   artigo também reporta McNemar par a par em vez de só confiar no
   Nemenyi; CHAN *et al.* (2022, Mathematics/MDPI) — revisão de
   multicolinearidade/VIF em ML; MINDERER *et al.* (2021, NeurIPS) —
   calibração de redes neurais modernas; NOMA *et al.* (2021, Statistics
   in Medicine) — IC por bootstrap em modelos preditivos; OGUNLEYE;
   OYEJOLA; OBISESAN (2018) — comparação de testes de normalidade,
   reforçando Shapiro-Wilk.
3. **Gaps declarados, não forçados**: não encontrei um artigo recente
   (≤10 anos) suficientemente confiável para Tukey/regra 1,5×IQR nem para
   Durbin-Watson/ACF em contexto de ML — preferi avisar o Adinailson a
   inventar uma citação fraca só para preencher a lacuna.
4. Links de acesso (DOI/venue) das 19 referências originais + das 5
   novas enviados ao Adinailson na resposta desta rodada, para ele
   salvar no Drive se quiser. Suíte completa: 90/90 (mudança só em
   Markdown).

**Próximo passo**: (1) revisar/mergear o PR desta rodada; (2) o
Adinailson decide se quer salvar os PDFs das 17 referências faltantes no
Drive (links já enviados); (3) quando o Codex retomar em 29/07 (ou antes,
se decidido), continuar os Passos 3–6 do prompt original de 6 passos.

---

### Histórico da rodada 18 (referenciação exaustiva da Subseção 4.10 e do parágrafo de métodos da 3.5)

**Contexto**: após fechar a rodada 17 (PRs #61 e #62 mergeados, conteúdo
verificado íntegro em `main`), o Adinailson pediu explicitamente que a
redação estatística fosse "bastante referenciada e explicada" e que eu
"não me contivesse em quantidade de citações de referências".

**Onde está**: concluído, branch `docs/referencias-estatisticas-4-10`.
Cada teste/conceito estatístico citado nas Subseções 3.5 e 4.10 ganhou
sua referência primária (nenhuma foi inventada — todas são trabalhos
reais e amplamente citados na literatura de estatística/ML):
BOX; JENKINS (1970, ACF), COCHRAN (1950, teste Q — distinto do
COCHRAN 1977 já citado, mesmo autor/obras diferentes), DEMŠAR (2006,
protocolo de comparação de classificadores), DIETTERICH (2000,
diversidade em ensembles), DURBIN; WATSON (1950), EFRON (1979) e EFRON;
TIBSHIRANI (1993) (bootstrap), FLEISS (1971, Kappa), FRIEDMAN (1937),
HOLM (1979), LANDIS; KOCH (1977, escala de interpretação do Kappa),
MARQUARDT (1970, VIF), NEMENYI (1963), O'BRIEN (2007, crítica à regra de
bolso do VIF), RAZALI; WAH (2011, poder comparativo do Shapiro-Wilk),
SHAPIRO; WILK (1965), SPEARMAN (1904), TATE (1954, ponto-bisserial),
TUKEY (1977, regra 1,5×IQR). 19 referências novas, todas verificadas e
inseridas em ordem alfabética na lista de REFERÊNCIAS (checado com
`grep`/leitura completa, não só memória). Apêndice B atualizado. Suíte
completa: 90/90 (mudança é só em Markdown).

**Próximo passo**: (1) revisar/mergear o PR desta rodada; (2) quando o
Codex retomar em 29/07 (ou antes, se decidido), continuar os Passos 3–6
do prompt original de 6 passos.

---

### Histórico da rodada 17 (Subseção 4.10 de robustez estatística; recuperação de conteúdo perdido em merge concorrente)

**Contexto**: nesta mesma jornada de trabalho, mais de uma sessão/processo
esteve operando neste clone local em paralelo (já detectado e contornado
nas rodadas 15-16 — ver histórico). Ao retomar o trabalho nesta rodada,
detectei que o merge da rodada 16 (PR #58, justificativa k-fold vs.
holdout) **perdeu conteúdo real** no processo: a própria Subseção 3.5
("Desenho de avaliação") ficou sem cabeçalho (erro meu, de uma rodada
anterior) e, mais grave, o parágrafo inteiro de justificativa
(KOHAVI, 1995 + comparação empírica holdout vs. k-fold), a referência
bibliográfica e a linha de checklist correspondente **desapareceram do
artigo publicado em `main`**, embora o PR estivesse marcado como
mergeado. Comparação byte a byte (`comm` após normalizar CRLF/LF, não
diff ingênuo) confirmou que essa foi a ÚNICA perda real; todo o resto
(README.md, 3.4.1, etc.) estava intacto.

**Onde está**: tudo recuperado e ampliado nesta rodada, branch
`docs/robustez-estatistica-artigo`:
1. **Recuperação**: cabeçalho "**3.5 Desenho de avaliação**" restaurado;
   parágrafo "Escolha entre validação cruzada e *holdout* fixo" (com
   KOHAVI, 1995 e os números reais de `comparacao_holdout_kfold.json`)
   restaurado a partir do commit `8ddf6c67` (ainda íntegro no histórico
   git, só não presente em `main`); referência KOHAVI e linha de
   checklist reinseridas.
2. **Novo, a pedido do Adinailson** ("gostaria que tivesse uma seção que
   desse a robustez estatística mostrando os pressupostos e os resultados
   dos testes"): criada Subseção **4.10 Robustez estatística: pressupostos
   e testes de sensibilidade**, com números reais de
   `docs/dados/estatistica.json` (gerado 25/07/2026 15:45, n = 13.965) —
   protocolo de Zuur, Ieno e Elphick (2010, adaptado de resposta contínua
   ecológica para resposta categórica), cobrindo outliers, homogeneidade
   de variância, normalidade (Shapiro-Wilk, Tabela 8), excesso de
   categorias raras, colinearidade entre modelos (VIF), relação
   confiança×acerto (Tabela 9), interações e independência das
   observações (ACF/Durbin-Watson). Testes globais com números completos:
   Cochran Q, Friedman+Nemenyi (só 5 de 15 pares significativos — bem
   menos que o McNemar-Holm, por diferença de poder estatístico entre os
   dois testes, explicitado no texto), McNemar-Holm (20/21 pares
   significativos; única exceção SGD vs. Random Forest), Kappa de Fleiss
   entre as 7 IAs (0,7719). Verifiquei cada número manualmente antes de
   publicar — encontrei e corrigi uma alegação minha própria incorreta
   sobre o Nemenyi antes do commit (tinha escrito "quase todos os pares
   significativos", o cálculo real mostrou 5 de 15).
3. **Correção de referência cruzada pré-existente, achada de graça**: 9
   menções a "Subseção 4.9" no artigo apontavam para uma subseção que
   nunca existia formalmente (o conteúdo da investigação do *ablation*
   do LSTM estava só dentro da legenda da Figura 6, em 4.8). Formalizei
   como **4.9 Investigação da discrepância do *ablation* do LSTM**,
   resolvendo as 9 referências cruzadas quebradas de uma vez.
4. Referência ZUUR (2010) adicionada; Apêndice B e tabela de estrutura
   deste arquivo (Seção 3, acima) atualizados com 4.9/4.10. Suíte
   completa: 90/90 (mudança é só em Markdown).

**Próximo passo**: (1) revisar/mergear o PR desta rodada — **checar com
cuidado extra o resultado do merge**, dado o incidente de perda de
conteúdo; (2) considerar novo snapshot imutável pós-merge, já que o
`artigo-v3-20260725` (rodada anterior) não inclui 4.9/4.10; (3) quando o
Codex retomar em 29/07 (ou antes, se decidido), continuar os Passos 3–6
do prompt original de 6 passos.

---

### Histórico da rodada 15 (fechamento: limpeza total + rematerialização dos 8 modelos; verificação do parecer externo; rodada 16 recuperada acima)

**Contexto**: o Adinailson enviou a outra sessão (Codex, via conector
GitHub) um prompt com 6 passos para revisar o artigo com rigor de
submissão A1/A2. Essa sessão concluiu os Passos 1–2 e preparou o Passo 3
em modo seguro, mas ficou **bloqueada pelo limite de uso do Codex até
2026-07-29 11:49**, com 3 commits locais no sandbox dele, nunca enviados
ao GitHub. O Adinailson pediu para eu tratar os Passos 1 e 2 nesta
sessão. Na rodada 14, os Passos 1 e 2 foram concluídos e mergeados
(PR #54, #55, #56). Nesta rodada (15), o Adinailson pediu explicitamente
para "reexecutar tudo" ("corrija tudo, só não apague o que fiz
manualmente [M/N/P/Q], pode apagar e refazer todos os dados de todas as
outras abas, NÃO POSSO usar dados falsos") — fechando o ciclo iniciado
com o achado do transformer_ft.

**Onde está**: ciclo completo, **concluído nesta rodada**:
1. `src/limpar_classif_multimodelo.py --modelos "naive_bayes,regressao_logistica,linear_svc,sgd,extra_trees,random_forest,lstm,transformer_ft" --aplicar`
   (via `lstm_artigo.yml`, tarefa `limpar_multimodelo`) — dry-run
   reportado antes, depois aplicado: limpou 13.965 linhas × 8 modelos em
   `CLASSIF__<modelo>`, 7.449 linhas de `MULTIMODELO_TURNOS`, 8 linhas de
   `MULTIMODELO_METRICAS` (tudo, `linhas_mantidas: 0`). Confirmado por
   leitura pós-limpeza que a aba principal (M/N/P/Q) não foi tocada (sem
   `#REF!`, header Q intacto).
2. `multimodelo_classificacao.yml --modelos=todos --max_turnos=0 --aplicar=true`
   (run `30163521690`) rematerializou do zero. Resultado, confirmado em
   log: `transformer_ft` → `RECUSADO` (o fix da rodada 14 funcionou —
   nada publicado sob esse nome); os 7 modelos comparáveis →
   `previstos=13965` cada, `metodo=kfold_5`.
3. `avaliacao_final.yml` (run `30164458083`) e `estatistica.yml` (run
   `30164458982`) regeneraram os JSONs. Números finais (n=9.096,
   `avaliacao_final.json` gerado 25/07/2026 12:52,
   `modelos_excluidos: ["transformer_ft"]`): linear_svc 0,9493; sgd
   0,9392; regressao_logistica 0,9355; extra_trees 0,9274; random_forest
   0,9227; lstm 0,879; naive_bayes 0,8609. **Praticamente idênticos aos
   da rodada 12** (diferença de ~0,01-0,04 p.p. por modelo, atribuível à
   aleatoriedade do k-fold entre execuções distintas — não indica
   regressão). `vale_combinar=False` (nenhum ensemble supera linear_svc
   isolado), mesma conclusão da rodada 12. Ranking relativo idêntico.

**Interpretação**: os números não mudaram de forma relevante porque os 7
modelos comparáveis já estavam corretos desde a rodada 12 (a rodada 15
só limpou e reprocessou, não mudou lógica de treino deles). O que mudou
de fato é que `transformer_ft` agora **nunca mais** vai poluir
silenciosamente `CLASSIF__transformer_ft`/`MULTIMODELO_TURNOS`/
`MULTIMODELO_METRICAS` — o cron automático de 15 em 15 min vira no-op
para esse modelo até alguém rodar com `torch`/`transformers` instalados
de verdade.

**Não tratado (fora de escopo, aguardando o Codex ou nova decisão)**:
Passos 3–6 do prompt original — rematerialização da Etapa 1 oficial
(coluna G, dashboard público); bug no dashboard que esconde a tabela de
ensembles com mensagem desatualizada; snapshot imutável novo
pós-rematerialização (pendência recorrente desde a rodada 12, ainda não
feita); rigor formal de submissão MDPI (metadados, figuras 300dpi,
subseção 5.4 dedicada); holdout fixo de treino/teste; referências em
formato MDPI numérico.

**Revisão externa recebida (PARECER FINAL, 25/07/2026, mesmo dia)**: o
Adinailson trouxe um parecer de outra IA avaliando o PDF do artigo, nota
9,0/10, com plano bifásico de 12 passos (Fase A — 7 itens executáveis já;
Fase B — 5 itens só após a conferência humana terminar). Verificação
item a item contra o estado real do repositório (não presumido):

- **Já resolvido, sem necessidade de ação** (o parecer foi escrito a
  partir de um PDF gerado ANTES da resincronização final desta mesma
  rodada, por isso cita números defasados — 94,94%/88,69% em vez dos
  94,93%/87,90% atuais):
  - Passo 3 (Abstract com números corretos) — já resincronizado (ver
    RESUMO/ABSTRACT do artigo).
  - Passo 4 (Tabela S1 descrita em prosa na Subseção 4.1) — já existe,
    com mais rigor que o texto sugerido pelo parecer (nossa versão liga
    o F1 baixo ao suporte pequeno das categorias, não a uma hipótese de
    proximidade semântica não verificada).
  - Passo 5 (padronizar 13.965 em todo o texto) — já não há ocorrência de
    13.825/13.618 no artigo (`git grep` confirmou).
  - Passo 6 (legendas autoexplicativas das Figuras 2-6) — já mais
    detalhadas que a sugestão do parecer (incluem fonte, data de geração
    e números; a sugestão do parecer inclusive cita o número desatualizado
    88,69% na legenda da Figura 6).
  - Passo 7 (3 direções de trabalho futuro) — já presentes em prosa nas
    Considerações Finais (BERTimbau, validação externa noutras IFES,
    integração MCDM/TOPSIS); não estão em formato de 3 bullets separados,
    mas o conteúdo já existe — reformatação é puramente estética, baixa
    prioridade.
- **RESOLVIDO nesta mesma rodada**: Passo 1 (subseção 3.4.1 — diferenças
  conceituais entre as famílias de classificadores). Escrita e inserida
  entre 3.4 e 3.5 em `04_artigo/artigo_classificacao_chamados_v3.md`. Não
  reaproveitei os números do parecer sem verificar: o custo computacional
  citado (RF/Extra Trees entre 7,6–8,4× o LinearSVC e 17,1–18,7× o Naive
  Bayes) vem de `Tabela 7` (`comparacao_modelos.json`), não da estimativa
  solta "10-20x" do parecer. Também corrigi uma imprecisão do próprio
  parecer: o mecanismo de produção não troca de modelo por confiança
  abaixo de 70% por chamado — `src/classificador_producao.py` mostra que
  a escolha LSTM-vs-RF é feita uma vez, no nível da base de treino
  (`MIN_BASE_LSTM=200`); os limiares 0,70/0,95 só rotulam a faixa de
  confiança para métricas, não trocam de modelo. A ausência de
  *embeddings* pré-treinados em português no LSTM foi confirmada
  diretamente em `src/modelo_lstm.py` (camada `Embedding` sem `weights=`)
  antes de entrar como argumento no texto. Suíte completa (85 testes)
  seguiu passando após a edição (mudança é só de texto/markdown).
- **Bloqueado por decisão já registrada do Adinailson, não uma pendência
  nova**: Passo 2 (holdout fixo de 15%). Este repositório já tem uma
  decisão explícita da rodada 9 (linha "Não mexer no holdout fixo de
  treino/teste... sem decisão explícita do Adinailson", ver Histórico da
  rodada 9 abaixo) — o desenho atual usa out-of-fold KFold
  deliberadamente, e mudar para holdout fixo implicaria reprocessar os 8
  modelos de novo. Não vou implementar isso sem confirmação explícita
  dele nesta rodada, mesmo com o parecer recomendando.
- **Fase B (Passos 8-12, pós-conferência humana)**: não traz nada novo —
  já é exatamente o que este arquivo e o `README.md` já rastreiam como
  pendente (Tabela 2/4/calibração recalculadas quando a conferência M/N/P
  terminar). Nenhuma ação necessária agora.

**Próximo passo**: (1) se o Adinailson quiser avançar no holdout fixo
(Passo 2 do parecer), tratar como mudança metodológica nova, com dry-run
e discussão antes de reprocessar os 8 modelos; (2) gerar novo snapshot
imutável (`gerar_manifesto_snapshot_artigo.py`), pendência recorrente
desde a rodada 12; (3) verificar se o dashboard
público (`docs/index.html`) precisa de refresh dos JSONs novos; (4)
quando o Codex retomar em 29/07 (ou antes, se decidido), continuar os
Passos 3–6 do prompt original de 6 passos — cuidado para não
duplicar/conflitar com o que ele já tinha preparado.

---

### Histórico da rodada 14 (Passos 1 e 2 do prompt de 6 passos, mergeados)
Passos 1 e 2 (ambos críticos) concluídos e mergeados em `main`, em 3
PRs: **#54** (`fix/vies-amostra-validada`) quantificou o viés estrutural
da amostra validada — 438 dos 9.534 conferidos (4,6%) são "restritos"
(avaliador julgou todas as fontes erradas, sem verdade conhecida) e
ficam fora do denominador de `acerto_validado`; publicado intervalo
`[limite_inferior, limite_superior]` por modelo em
`04_artigo/figuras/sensibilidade_vies_validacao.json` (amplitude
3,95-4,36 p.p.; ranking relativo estável em todo o intervalo). **#55**
(`feat/categoria-correta-manual`) elimina esse viés na raiz: nova coluna
Q "CATEGORIA CORRETA MANUAL" na aba principal; `decisao_validada.py::decidir()`
ganhou o parâmetro `categoria_manual`. **#56**
(`fix/transformer-ft-fallback-explicito`) — Passo 2: confirmado em log
real (run `29550863840`, 17/07/2026) que a materialização inteira
publicada como `transformer_ft` (13.954/13.965 linhas) era fallback
silencioso para LSTM; corrigido para recusar publicar quando isso
acontece. Os 3 PRs partiram do mesmo commit e reescreviam esta seção —
conflito resolvido manualmente ao mergear #56 por último.

---

### Histórico da rodada 12 (rematerialização completa dos 7 modelos; discrepância do LSTM resolvida)
A discrepância do ablation do LSTM (sinalizada na rodada 10, investigada
nas rodadas 11–14) foi **resolvida**. Decisão do Adinailson: rematerializar
os 7 modelos comparáveis por completo (não só o LSTM). Resultado: todos
os 7 modelos subiram ~15 p.p. de acerto validado (materialização de
16-17/07 estava genericamente desatualizada); ranking relativo
inalterado. Acerto validado (n=9.096, `avaliacao_final.json` de
25/07/2026 01:52): linear_svc 0,9494; sgd 0,9391; regressao_logistica
0,9349; extra_trees 0,9265; random_forest 0,9210; lstm 0,8869 (perto dos
0,8635 do ablation corrigido por GroupKFold); naive_bayes 0,8607. Criado
`src/limpar_classif_multimodelo.py` (8 testes) para permitir a
rematerialização com segurança. Ferramental: novo script
`src/analise_sensibilidade_vies_validacao.py` (rodada 13, acima) já usa
esses mesmos dados como base do intervalo de sensibilidade.

---

### Histórico da rodada 9 (fechada em 2026-07-24, ver acima a auditoria)
1. **S1 viva confirmada e publicada**: a execução local de
   `python src/exportar_tabela_por_categoria.py` bloqueou por ausência local de
   `SPREADSHEET_ID`, mas o workflow manual foi disparado com secrets do GitHub
   (`run 30137147380`) e leu a aba `TABELA_S1_METRICAS` (`gid=1862157493`).
   Cabeçalhos reais impressos no log: `Categoria`, `Support`, `Precision`,
   `Recall`, `F1-Score`. O CSV real foi publicado em
   `04_artigo/figuras/tabela_S1_metricas_por_categoria.csv` pelo commit
   `ca081648`, e a Subseção 4.1 foi atualizada para usar F1 por categoria.
2. **Figura 4 gerada de fato**: novo script
   `src/gerar_figura4_confusoes.py` lê `docs/dados/estatistica.json`, campo
   `top_confusoes` (gerado em 24/07/2026 20:52), agrega os pares direcionais
   mais frequentes entre os top pares dos modelos e grava
   `04_artigo/figuras/fig4_top_confusoes.png`. O artigo foi atualizado na
   Subseção 4.8. O maior par agregado foi `Climatização > Ar condicionado` para
   `Manutenção Preventiva > Ar condicionado split` (1.310 ocorrências).
3. **Tabela Suplementar S2 gerada**: como a Figura 4 usa códigos C01-C10 por
   legibilidade, foi gerado
   `04_artigo/figuras/tabela_S2_codigos_categorias_fig4.csv` com o mapeamento
   código-categoria, preservando os nomes reais em UTF-8.
4. **CLI de treino real do LSTM preparada**: `src/modelo_lstm.py` agora pode ser
   executado diretamente para treinar o LSTM, chamar `salvar_history()` e gerar
   `04_artigo/figuras/lstm_history.json` e
   `04_artigo/figuras/fig5_curva_aprendizado_lstm.png`. O workflow
   `30137383907` executou o treino real com 13.965 exemplos e 53 categorias;
   `EarlyStopping` interrompeu após 11 épocas. Menor `val_loss`: 1,4374 na
   época 8; maior `val_accuracy`: 0,6722 na época 10. Arquivos publicados pelo
   commit `e66b4a40`.
5. **Ablation study executado com dados vivos**: `src/ablation_lstm.py`
   comparou 64/128 unidades × dropout 0,5/0,3 por 3-fold KFold sobre 9.096
   linhas validadas, medindo acerto contra verdade validada humana. O workflow
   `30137529732` publicou `04_artigo/figuras/ablation_lstm_resultados.json`,
   `04_artigo/figuras/tabela_S3_ablation_lstm.csv` e
   `04_artigo/figuras/fig6_ablation_lstm.png` pelo commit `fcf39887`.
   Resultado: configuração atual 64/0,5 = 87,68%; melhor variação 128/0,3 =
   88,18% (+0,50 ponto percentual; 46 acertos a mais).
6. **Workflow manual criado**:
   `.github/workflows/lstm_artigo.yml` permite rodar com secrets do GitHub as
   tarefas `tabela_s1`, `history` e `ablation`.

Commits desta continuação: `52eb3612` (Figura 4/S2), `667189d4` (CLI da curva
LSTM), `9ff80ce2` (ablation + workflow manual), `7ffe9af8` (correção de push
do workflow), `ca081648` (S1 real publicada pelo workflow), `07383e21`
(correção dos parâmetros do treino LSTM), `e66b4a40` (curva real do LSTM) e
`fcf39887` (ablation real do LSTM).

**Próximo passo**: gerar novo snapshot imutável do artigo, regenerar o PDF e
revisar visualmente as figuras no artefato final. Não mexer no holdout fixo de
treino/teste nem na reformatação numérica MDPI sem decisão explícita do
Adinailson.

---

## 1. Por que este documento existe

O Adinailson pediu um modelo reaproveitável: sempre que solicitar avanço no
artigo/capítulo de classificação de chamados, a sessão deve seguir esta estrutura e
deixar registrado onde parou. Este arquivo é esse modelo — parte fixa (estrutura do
artigo, mapeamento de fontes) e parte viva (bloco "Estado desta rodada" acima).

## 2. Diferença em relação ao `revisao-bibliografica`

`revisao-bibliografica` é uma **revisão de literatura** (corpus bibliográfico externo,
pipeline `00_protocolo → 01_dados_brutos → 02_triagem → 03_analise → 04_artigo →
05_bibliografia`, LaTeX compilado via CI). `classificacao-chamados` é um
**experimento empírico aplicado** (dados operacionais reais da planilha, modelos
treinados, validação humana) — não existe "corpus bibliográfico" a triar aqui, e por
isso replicar a pipeline `00_..05_` inteira não faz sentido 1:1.

O que **é** análogo e vale replicar:
- Um arquivo único descrevendo a estrutura do texto, no padrão de
  `04_artigo/estrutura_texto.md` do outro repo — feito na Seção 3 abaixo.
- Números do artigo gerados por script a partir de dados versionados/rastreáveis
  (lá é `generated_numbers.tex`; aqui já existe o equivalente natural:
  `docs/dados/*.json`, todos gerados por `src/*.py`) — **não digitar números à mão no
  texto do artigo**, sempre citar a partir do JSON vigente.
- Um handoff de continuidade por rodada (lá é `HANDOFF_ARTIGO_CODEX.md`; aqui é o
  bloco "Estado desta rodada" deste próprio arquivo, sem criar arquivo novo).
- Disponibilidade de dados/scripts documentada no próprio artigo, apontando para os
  arquivos reais do repositório (Seção 3.9 abaixo).

O que falta hoje e é a lacuna mais importante encontrada nesta auditoria: **o
rascunho do artigo não mora no repositório**. Recomendação (a confirmar com o
usuário antes de executar, é decisão dele): criar `04_artigo/` neste repo (mesmo nome
do outro, por consistência) com o texto em Markdown ou LaTeX e um script
`gerar_numeros_artigo.py` que leia `docs/dados/*.json` e produza um bloco de
constantes citável, do mesmo jeito que `generated_numbers.tex` faz lá.

## 3. Estrutura do artigo/capítulo (modelo fixo, mapeado às fontes reais)

Baseada na estrutura do artigo-modelo (`artigo_revisao_preliminar (2).pdf`, revisão
MCDM/TOPSIS) e no rascunho já iniciado (`artigo_classificacao_chamados_v3.docx`).

### Resumo estruturado
Contexto / Objetivo / Método / Resultados / Conclusão + palavras-chave. Escrever por
último, depois que 3–4 estiverem fechados com números revalidados.

### 1. Introdução
Governança preditiva da manutenção predial como problema; chamados/ordens de serviço
como matéria-prima negligenciada pela literatura (**ponte direta com o achado do
capítulo de revisão**: "uso de dados operacionais de chamados... é raro (3 estudos)"
— este capítulo empírico preenche exatamente essa lacuna identificada na revisão).

### 2. Referencial conceitual
Classificação automática de texto/NLP; modelos clássicos (TF-IDF+LogReg) vs. LSTM vs.
ensembles (RF, ExtraTrees, SGD, Naive Bayes) vs. transformer (BERTimbau); calibração
de confiança (Platt/isotônica) vs. softmax bruto; entropia de Shannon e divergência
Jensen-Shannon como camada de diagnóstico de ambiguidade; validação humana como
padrão-ouro; "rótulos ruidosos" no histórico administrativo como problema de pesquisa.

### 3. Método
| Subseção | Conteúdo | Fonte no repo |
|---|---|---|
| 3.1 | Desenho do experimento, fonte de verdade (roteiro 50 etapas) | `CONTEXTO.md`, roteiro PDF do usuário |
| 3.2 | Base de dados/planilha experimental (aba, colunas A:P, tamanho, período) | `AGENTS.md`, `README.md` |
| 3.3 | Modelos (LSTM primário, RF fallback, baseline, 7 IAs multimodelo, 8º BERTimbau) | `src/modelo_lstm.py`, `src/modelos_zoo.py`, `src/bertimbau_coreset.py` |
| 3.4 | Pipeline por turnos (Etapa 1 progressiva, Etapa 2 reclassificação) | `src/executar_etapa1.py`, `src/executar_etapa2.py`, `.github/workflows/etapa1_turnos.yml` |
| 3.5 | Métricas (concordância vs. histórico, acerto validado, calibração ECE, Kappa) | `src/calibracao.py`, `src/analise_estatistica.py` |
| 3.6 | Validação humana (colunas M/N/P, conflitos) | `src/auditar_conferencias.py` |
| 3.7 | Memória de decisão (veto/trava) | `src/decisao_validada.py`, `src/memoria_validada.py` |
| 3.8 | Camada Shannon/Jensen-Shannon | `src/analise_shannon.py`, `docs/METODOLOGIA_SHANNON.md` |
| 3.9 | Disponibilidade de dados e scripts (mover para o fim do artigo, como no modelo) | `docs/dados/*.json`, este repositório público |

### 4. Resultados
| Subseção | Conteúdo | Fonte no repo |
|---|---|---|
| 4.1 | Concordância com histórico, por modelo | `docs/dados/registros_<modelo>.json` |
| 4.2 | **Ranking validado por conferência humana** (o resultado mais importante) | `docs/dados/avaliacao_final.json` |
| 4.3 | Matriz de confusão IA × histórico na amostra conferida | `src/avaliacao_final.py` |
| 4.4 | Calibração por faixa de confiança | `docs/dados/calibracao.json` |
| 4.5 | Reclassificação e ganho líquido por modelo | `docs/dados/reclass_resumo.json` |
| 4.6 | Diagnóstico Shannon/Jensen-Shannon | `docs/dados/shannon_resumo.json`, `shannon_modelos.json`, `jensen_shannon_modelos.json` |
| 4.7 | Custo computacional | a confirmar se já medido — se não, marcar "Informação insuficiente para verificar" |
| 4.8 | Figuras | pendência conhecida: regenerar a partir dos JSONs atuais |
| 4.9 | Investigação da discrepância do ablation do LSTM (rodadas 10-11) | `04_artigo/figuras/ablation_lstm_resultados.json`, `diagnostico_*_lstm*.json` |
| 4.10 | Robustez estatística: pressupostos (Zuur et al. 2010, adaptado) e testes de sensibilidade completos (Shapiro-Wilk, Friedman/Nemenyi, McNemar-Holm, Fleiss Kappa, correlação confiança×acerto) | `docs/dados/estatistica.json` (campos `pressupostos`, `protocolo_zuur`, `cochran_q`, `friedman`, `mcnemar_holm`, `fleiss_kappa_entre_ias`, `residuos_tendencia`) |

### 5. Discussão
Rótulos ruidosos no histórico vs. erro da IA; quando confiar na IA e quando confiar
no histórico; implicações para a governança preditiva da manutenção (**ponte
explícita com o capítulo de revisão MCDM/TOPSIS**: a revisão apontou a lacuna de
integrar dados operacionais de chamados a modelos formais de decisão — este capítulo
fornece exatamente esses dados operacionais tratados e validados, e pode alimentar
como entrada um modelo multicritério futuro).

### 6. Considerações finais
Limitações (amostra validada prioriza divergências, não é aleatória; 8º modelo
pendente; reclassificação tem resultado dependente da rodada e mistura bases de
comparação). Não afirmar validação empírica
completa enquanto a conferência humana não terminar.

### Referências
Conferir contra o acervo curado (`Referência Bibliográfica - Drive/README.md`,
mencionado na auditoria de 16/07) antes de aceitar qualquer referência do v2/v3.docx
como correta — a auditoria anterior já achou 1 erro de autoria e 1 inconsistência de
ano nesse rascunho.

### Apêndices
Dicionário de colunas da planilha (A:P); checklist de itens reportados (inspirar-se
no Apêndice D/checklist PRISMA-ScR do artigo-modelo, adaptado para relato de
experimento de ML, não de revisão bibliográfica); matriz de decisão M/N/P.

## 4. Checklist de auditoria de dados (pendência do próprio usuário)

Isto é o que o Adinailson referiu como "ainda não acabei" — não é tarefa da IA
completar, é o próprio critério de corte para poder escrever a Seção 4 com
confiança:

- [ ] Conferência humana M/N/P avançando além dos 33,9% (4.737/13.954) registrados
      em 16/07/2026 — reconferir valor atual antes de qualquer nova rodada de escrita.
- [ ] 2 conflitos antigos ficaram resolvidos (registrado como 0 pendentes em
      16/07) — reconfirmar que nenhum conflito novo apareceu com o crescimento da base.
- [ ] Decisão sobre a mudança não commitada mencionada na auditoria de 16/07 em
      `src/reclassificar_validados.py` (trava de segurança) — verificar se ainda existe
      ou já foi resolvida (o `git status` desta auditoria de 23/07 mostrou working tree
      limpo, então **parece já resolvida**; confirmar mesmo assim antes de citar).
- [ ] Resultado comparativo do 8º modelo (BERTimbau) — ainda não existe.

## 5. Ligação com a tese (capítulos)

Capítulo A — revisão integrativa (`revisao-bibliografica`): panorama MCDM/TOPSIS/
ODS/ESG na manutenção predial; achado central: dados operacionais de chamados são
raríssimos na literatura (3 estudos).

Capítulo B — este capítulo (`classificacao-chamados`): trata exatamente esses dados
operacionais de chamados, com classificação/reclassificação por IA local, validação
humana e calibração.

A tese de biossistemas construídos se fortalece ao explicitar essa ponte na
Introdução e na Discussão de ambos os capítulos: a revisão identifica a lacuna, o
capítulo empírico a preenche parcialmente e aponta o próximo elo (dados de chamados
tratados → entrada para um modelo multicritério de priorização de manutenção).

Relaciona-se com [[classificacao-chamados-ia]], [[artigo-metodologia-biossistemas]] e
[[memoria-transferencia-codex]].
