#!/usr/bin/env python3
"""Aplica a revisão editorial final do artigo da PR 75.

O script preserva as métricas validadas, remove linguagem de relatório operacional,
transfere detalhes estatísticos e o checklist para Material Suplementar e atualiza
a numeração das tabelas afetadas.
"""

from __future__ import annotations

from pathlib import Path
import re

RAIZ = Path(__file__).resolve().parents[1]
ARTIGO = RAIZ / "04_artigo" / "artigo_classificacao_chamados_v3.md"
SUPLEMENTAR = RAIZ / "04_artigo" / "material_suplementar_estatistica_checklist.md"
PLANO = RAIZ / "PLANO_ARTIGO_CAPITULO.md"


def bloco(texto: str, inicio: str, fim: str, novo: str, rotulo: str) -> str:
    padrao = re.escape(inicio) + r".*?(?=" + re.escape(fim) + r")"
    atualizado, n = re.subn(padrao, novo.strip() + "\n\n", texto, count=1, flags=re.S)
    if n != 1:
        raise RuntimeError(f"Bloco não localizado ou ambíguo: {rotulo} (ocorrências={n})")
    return atualizado


def capturar(texto: str, inicio: str, fim: str) -> str:
    m = re.search(re.escape(inicio) + r"(.*?)(?=" + re.escape(fim) + r")", texto, flags=re.S)
    if not m:
        return ""
    return m.group(1).strip()


def main() -> int:
    texto = ARTIGO.read_text(encoding="utf-8")

    estatistica_anterior = capturar(
        texto,
        "**4.10 Robustez estatística: pressupostos e testes de sensibilidade**",
        "**5. DISCUSSÃO**",
    )
    checklist_anterior = capturar(
        texto,
        "**Apêndice A — Checklist de itens reportados**",
        "**Apêndice B — Matriz de decisão M/N/P**",
    )

    resumo = r'''**RESUMO**

A classificação automática de chamados de manutenção predial constitui um recurso estratégico para qualificar a triagem operacional e ampliar a governança baseada em evidências em instituições públicas. Entretanto, as categorias registradas em sistemas administrativos podem refletir taxonomias sobrepostas, informações incompletas e interpretações heterogêneas das equipes de atendimento.

Este artigo propõe um protocolo multimodelo para a classificação de chamados reais de manutenção predial universitária em português brasileiro, extraídos do sistema GLPI da Universidade Federal do Sul da Bahia. O corpus reúne 13.965 chamados não vazios, distribuídos em 55 categorias históricas, e compara classificadores baseados em TF-IDF — Naive Bayes, Regressão Logística, LinearSVC, SGD, Random Forest e Extra Trees — com uma rede neural LSTM bidirecional. O BERTimbau é apresentado como extensão planejada.

O protocolo distingue a concordância com o histórico administrativo do acerto avaliado por revisão humana, tratando a categoria original como referência preliminar. A conferência abrange 9.534 chamados, dos quais 9.044 possuem decisão travada e 52 apresentam conflito entre as fontes avaliadas. O LinearSVC alcança a maior concordância com o histórico, com 80,31% (IC95%: 79,63%–80,97%), e o maior acerto validado, com 95,02% (IC95%: 94,58%–95,46%). A LSTM obtém, respectivamente, 67,18% e 88,11%.

Na faixa de confiança igual ou superior a 95%, o classificador operacional alcança 99,94% de acerto em 4.675 decisões validadas. Os resultados referem-se à amostra conferida, cuja composição é discutida na Seção 5. A rejeição da normalidade sustenta o emprego de testes não paramétricos. Em conjunto, os achados mostram que classificadores lineares oferecem equilíbrio favorável entre desempenho, custo computacional e auditabilidade para textos técnicos curtos, ruidosos e desbalanceados.

**Palavras-chave:** manutenção predial; classificação de chamados; processamento de linguagem natural; rótulos ruidosos; validação humana; governança preditiva.'''
    texto = bloco(texto, "**RESUMO**", "**ABSTRACT**", resumo, "Resumo")

    abstract = r'''**ABSTRACT**

*Automatic classification of building-maintenance work orders is a strategic resource for improving operational triage and evidence-based governance in public institutions. Administrative categories, however, may reflect overlapping taxonomies, incomplete information and heterogeneous interpretations by maintenance teams.

This study proposes a multi-model protocol for 13,965 real university building-maintenance work orders in Brazilian Portuguese, organized into 55 historical categories. The comparison includes TF-IDF-based classifiers — Naive Bayes, Logistic Regression, LinearSVC, SGD, Random Forest and Extra Trees — and a bidirectional LSTM. BERTimbau is presented as a planned extension.

The protocol distinguishes agreement with the administrative history from accuracy against human-reviewed decisions. Human review covers 9,534 records, including 9,044 locked decisions and 52 conflicts. LinearSVC achieves the highest historical agreement, 80.31% (95% CI: 79.63%–80.97%), and the highest validated accuracy, 95.02% (95% CI: 94.58%–95.46%). LSTM reaches 67.18% and 88.11%, respectively.

For predictions with confidence equal to or greater than 95%, the operational classifier reaches 99.94% validated accuracy across 4,675 decisions. The results refer to the reviewed sample, whose composition is discussed in Section 5. Rejection of normality supports non-parametric testing. Overall, linear classifiers provide a favorable balance between performance, computational cost and auditability for short, noisy and imbalanced technical text.*

***Keywords:** building maintenance; work-order classification; natural language processing; noisy labels; human validation; predictive governance.*'''
    texto = bloco(texto, "**ABSTRACT**", "**1. INTRODUÇÃO**", abstract, "Abstract")

    secao_32 = r'''**3.2 Corpus e variáveis**

O corpus experimental é composto por 13.965 chamados de manutenção predial não vazios, distribuídos em 55 categorias históricas e extraídos do ambiente institucional da UFSB. Os campos considerados incluem o título e a descrição do chamado, além do título e da descrição da ordem de serviço. Esses campos foram concatenados em uma única representação textual para a classificação.

A categoria histórica foi utilizada como referência administrativa preliminar. A avaliação principal empregou a categoria definida pela memória de decisão resultante da conferência humana. Os textos estão redigidos em português brasileiro e contêm jargões técnicos, abreviações locais, nomes de equipamentos e descrições incompletas, características típicas de registros operacionais de manutenção (SUNDARAM; ZEID, 2025).'''
    texto = bloco(texto, "**3.2 Corpus e variáveis**", "**3.3 Pré-processamento textual**", secao_32, "3.2")

    secao_34_35 = r'''**3.4 Modelos avaliados**

O desenho experimental compara sete modelos organizados em três famílias conceituais, selecionadas em função das características do corpus, composto por textos curtos, vocabulário técnico e forte desbalanceamento entre categorias.

A família linear reúne LinearSVC, Regressão Logística e SGD, aplicados à representação TF-IDF esparsa. Em espaços de alta dimensionalidade, fronteiras lineares apresentam desempenho competitivo quando o vocabulário possui elevado poder discriminativo, como ocorre com termos técnicos associados a equipamentos, sistemas prediais e manifestações de falha (JOACHIMS, 1998; SALTON; BUCKLEY, 1988).

Random Forest e Extra Trees representam a família de *ensembles* de árvores e permitem modelar interações não lineares entre atributos. O Naive Bayes Multinomial funciona como referência probabilística de menor complexidade. A LSTM bidirecional representa a família neural e modela dependências sequenciais, com *embeddings* treinados diretamente no corpus (GRAVES; SCHMIDHUBER, 2005).

O BERTimbau é previsto como extensão contextual pré-treinada em português. Como seu ajuste fino ainda não dispõe de métricas rastreáveis, o modelo permanece fora dos rankings e dos testes comparativos.

**3.4.1 Diferenças conceituais e operacionais entre os classificadores**

Os classificadores avaliados adotam hipóteses distintas sobre a estrutura dos dados. O Naive Bayes representa uma abordagem probabilística; LinearSVC, Regressão Logística e SGD empregam fronteiras discriminativas lineares; Random Forest e Extra Trees modelam relações não lineares; e a LSTM explora a sequência dos termos. Essas diferenças explicam parte da variação observada nas Tabelas 1 e 2.

O LinearSVC maximiza a margem de separação entre classes sobre uma matriz TF-IDF esparsa com até 5.000 atributos. Termos como *bomba*, *split*, *disjuntor*, *vazamento*, *infiltração* e *ar-condicionado* atuam como âncoras semânticas. Essa estrutura favorece fronteiras lineares e é compatível com a liderança do modelo na concordância histórica e no acerto validado (JOACHIMS, 1998; SALTON; BUCKLEY, 1988).

O Naive Bayes assume independência condicional entre os atributos. Essa hipótese se ajusta de maneira limitada aos chamados de manutenção, nos quais termos técnicos aparecem em combinações recorrentes. Seu desempenho inferior caracteriza a referência de menor complexidade da comparação.

Random Forest e Extra Trees capturam interações entre atributos, mas apresentam custo computacional superior ao dos classificadores lineares. Na base analisada, essa complexidade produz desempenho intermediário, sem ganho de acerto validado que compense o aumento do tempo de treino. Os tempos medidos são apresentados na Tabela 6 (SCHWARTZ *et al.*, 2020; TREVISO *et al.*, 2023).

A LSTM bidirecional utiliza *embeddings* inicializados aleatoriamente e treinados sem vetores pré-treinados em português. Sua camada de *embedding*, com 8.000 termos e 128 dimensões, reúne aproximadamente 1,02 milhão de parâmetros. Cada partição de treino contém cerca de 11.172 exemplos, relação que favorece os modelos lineares em um corpus de porte médio e com ruído de rótulo (GALKE; SCHERP, 2022).

No classificador operacional, a LSTM é empregada quando a base rotulada atinge o número mínimo de exemplos previsto pelo protocolo. Abaixo desse limiar, utiliza-se Random Forest sobre TF-IDF. A confiança das predições é organizada em faixas que orientam a conferência humana e a análise de calibração.

**3.5 Desenho de avaliação**

A avaliação utiliza predições fora da amostra em protocolo *out-of-fold*, com *KFold* embaralhado em cinco partições, semente fixa e divisão idêntica para todos os modelos. A partição não é estratificada devido à presença de categorias com suporte unitário. O uso das mesmas partições permite comparações pareadas entre classificadores (SOKOLOVA; LAPALME, 2009).

As métricas principais são acurácia, *macro*-F1, F1 ponderado, *balanced accuracy* e intervalos de confiança de 95% por *bootstrap*. A *macro*-F1 e a *balanced accuracy* conferem peso às categorias raras e complementam a acurácia global em uma base desbalanceada (EFRON, 1979; EFRON; TIBSHIRANI, 1993; SOKOLOVA; LAPALME, 2009).

As diferenças globais e pareadas foram examinadas por testes não paramétricos. O McNemar foi aplicado às comparações entre modelos, com correção de Holm-Bonferroni para o conjunto de testes. A verificação detalhada dos pressupostos, as matrizes de comparação e os resultados dos testes complementares são apresentados no Material Suplementar.

A escolha do protocolo *k-fold* foi confrontada com um *holdout* aleatório de 15%. A estratificação do *holdout* mostrou-se inviável devido às categorias com um único exemplo, e a divisão aleatória deixou classes raras sem observações de teste. Embora a acurácia global tenha variado pouco, o *holdout* reduziu a *macro*-F1 da maioria dos modelos. O protocolo *k-fold* foi, portanto, mantido por avaliar todos os registros e oferecer estimativas mais estáveis para as categorias de menor suporte (KOHAVI, 1995).'''
    texto = bloco(texto, "**3.4 Modelos avaliados**", "**3.6 Validação humana**", secao_34_35, "3.4-3.5")

    secao_39 = r'''**3.9 Disponibilidade de dados e scripts**

Os resultados são produzidos por um pipeline automatizado e reprodutível. Os agregados publicados não contêm identificadores pessoais, títulos ou descrições livres dos chamados. Os códigos, métricas derivadas e arquivos sanitizados necessários à reprodução das figuras e tabelas estão disponíveis no repositório público do estudo.'''
    texto = bloco(texto, "**3.9 Disponibilidade de dados e scripts**", "**4. RESULTADOS**", secao_39, "3.9")

    abertura_resultados = r'''**4. RESULTADOS**

A análise separa a concordância com a categoria histórica do desempenho contra a decisão validada por conferência humana. A base contém 13.965 chamados, dos quais 9.534 foram conferidos. Entre eles, 9.044 possuem categoria decidida e 490 permanecem sem verdade validada, incluindo 52 conflitos.

Os resultados evidenciam três padrões. Os classificadores lineares, liderados pelo LinearSVC, apresentam o melhor desempenho global. A conferência humana demonstra que concordância administrativa e acerto validado são dimensões distintas. Por fim, as faixas superiores de confiança concentram maior proporção de decisões corretas.'''
    texto = bloco(texto, "**4. RESULTADOS**", "**4.1 Concordância com o histórico (base completa)**", abertura_resultados, "abertura 4")

    secao_41 = r'''**4.1 Concordância com o histórico (base completa)**

Na base completa, o LinearSVC alcança acurácia de 0,8031 (IC95%: 0,7963–0,8097), seguido por Extra Trees (0,7894), Random Forest (0,7816), SGD (0,7767), Regressão Logística (0,7682), Naive Bayes (0,6997) e LSTM (0,6718). O teste de Cochran Q identifica diferença global entre os sete modelos (*p* < 0,001).

**Tabela 1** Concordância com a categoria histórica, base completa (n = 13.965)

| Modelo | Acurácia | IC95% bootstrap | Kappa vs. histórico |
|---|---|---|---|
| LinearSVC | 0,8031 | 0,7963 -- 0,8097 | 0,7881 |
| Extra Trees | 0,7894 | 0,7825 -- 0,7961 | 0,7716 |
| Random Forest | 0,7816 | 0,7749 -- 0,7881 | 0,7630 |
| SGD | 0,7767 | 0,7700 -- 0,7835 | 0,7604 |
| Regressão Logística | 0,7682 | 0,7613 -- 0,7751 | 0,7518 |
| Naive Bayes | 0,6997 | 0,6923 -- 0,7071 | 0,6705 |
| LSTM (out-of-fold) | 0,6718 | 0,6637 -- 0,6796 | 0,6496 |

Fonte: elaborado pelos autores (2026), com base nos agregados da comparação multimodelo.

O desempenho varia entre as 55 categorias. As classes com menor F1 possuem, em sua maioria, suporte inferior a sete registros, o que amplia a influência de pequenas variações absolutas. As métricas completas por categoria são apresentadas na Tabela Suplementar S1.'''
    texto = bloco(texto, "**4.1 Concordância com o histórico (base completa)**", "**4.2 Ranking validado por conferência humana**", secao_41, "4.1")

    secao_42 = r'''**4.2 Ranking validado por conferência humana**

A comparação contra as 9.044 decisões travadas mantém o LinearSVC na primeira posição, com acerto validado de 0,9502 (IC95%: 0,9458–0,9546). Em seguida aparecem SGD (0,9411), Regressão Logística (0,9371), Extra Trees (0,9286), Random Forest (0,9241), LSTM (0,8811) e Naive Bayes (0,8627).

A diferença entre LinearSVC e SGD é de 0,91 ponto percentual, com McNemar *p* ≈ 5,70 × 10⁻⁸. Os *ensembles* por maioria ponderada, confiança máxima e maioria simples alcançam, respectivamente, 0,9467, 0,9458 e 0,9445. O LinearSVC isolado permanece como a opção de maior desempenho. A composição da amostra validada e seus efeitos sobre a interpretação dos resultados são discutidos na Seção 5.

A análise de sensibilidade inclui os 490 casos sem verdade validada como erros no cenário conservador. A amplitude entre os limites varia de 4,43 a 4,88 pontos percentuais e preserva a ordenação dos sete modelos.

**Tabela 2** Acerto validado contra a verdade decidida M/N/P (n = 9.044) e intervalo de sensibilidade

| Modelo | Acerto validado (limite superior) | IC95% | Limite inferior (pior caso) |
|---|---|---|---|
| LinearSVC | 0,9502 | 0,9458 -- 0,9546 | 0,9014 |
| SGD | 0,9411 | 0,9363 -- 0,9459 | 0,8927 |
| Regressão Logística | 0,9371 | 0,9321 -- 0,9421 | 0,8889 |
| Extra Trees | 0,9286 | 0,9234 -- 0,9335 | 0,8808 |
| Random Forest | 0,9241 | 0,9186 -- 0,9295 | 0,8767 |
| LSTM | 0,8811 | 0,8743 -- 0,8880 | 0,8359 |
| Naive Bayes | 0,8627 | 0,8558 -- 0,8696 | 0,8183 |

Fonte: elaborado pelos autores (2026). O limite inferior considera os conflitos e os demais registros sem verdade validada como erros para todos os modelos.'''
    texto = bloco(texto, "**4.2 Ranking validado por conferência humana**", "**4.3 A classificação oficial frente ao histórico: matriz de confusão\nvalidada**", secao_42, "4.2")

    secao_43 = r'''**4.3 Interpretação conjunta da classificação operacional e do histórico**

A classificação operacional e a categoria histórica foram comparadas com a mesma decisão validada em 9.044 chamados. Ambas coincidem com a decisão em 8.476 casos. Em 559 registros, o histórico coincide com a decisão e a classificação operacional diverge; em outros nove, ambas divergem.

A ausência de ocorrências na combinação “classificação operacional correta e histórico incorreto” decorre da regra empregada para construir a verdade validada. A decisão é formada a partir das próprias fontes submetidas à conferência e somente é travada quando ao menos uma delas é confirmada. Essa dependência estrutural restringe a combinação correspondente e impede que seu valor seja interpretado como estimativa da capacidade da IA de corrigir o histórico.

O valor zero representa, portanto, uma propriedade do protocolo de decisão, e não evidência de que classificadores automáticos sejam incapazes de identificar categorias históricas inadequadas. A avaliação dessa capacidade exige uma amostra independente, anotada sem utilizar como ponto de partida as classificações comparadas.'''
    texto = bloco(texto, "**4.3 A classificação oficial frente ao histórico: matriz de confusão\nvalidada**", "**4.4 Confiança, calibração e faixas de decisão**", secao_43, "4.3")

    secao_44 = r'''**4.4 Confiança, calibração e faixas de decisão**

O classificador operacional apresenta erro esperado de calibração histórico de 0,0656. Na faixa de confiança igual ou superior a 95%, que reúne 4.810 chamados, a concordância com o histórico é de 98,75%. Entre as 4.675 decisões humanas disponíveis nessa faixa, o acerto validado alcança 99,94%.

A confiança utilizada é bruta, derivada da função de decisão ou da saída probabilística dos modelos. Esses valores sustentam uma política de priorização por faixas e fornecem a base empírica para a calibração formal por Platt, regressão isotônica ou escalonamento de temperatura.

**Tabela 3** Acerto validado por faixa de confiança bruta, classificador operacional

| Faixa | n total | Concord. histórico | n validados | Acerto validado |
|---|---|---|---|---|
| <50% | 4.058 | 43,05% | 880 | 51,93% |
| 50-70% | 1.443 | 75,12% | 712 | 87,50% |
| 70-80% | 946 | 87,10% | 653 | 96,78% |
| 80-90% | 1.484 | 82,82% | 1.065 | 97,84% |
| 90-95% | 1.224 | 95,59% | 1.059 | 99,15% |
| >= 95% | 4.810 | 98,75% | 4.675 | 99,94% |

Fonte: elaborado pelos autores (2026), após deduplicação por `linha_planilha`.'''
    texto = bloco(texto, "**4.4 Confiança, calibração e faixas de decisão**", "**4.5 Reclassificação e ganho líquido**", secao_44, "4.4")

    secao_45 = r'''**4.5 Reclassificação e ganho líquido**

Todos os modelos apresentam ganho líquido positivo na reclassificação. A LSTM registra o maior ganho absoluto, com 670 correções e 571 prejuízos, resultando em saldo de +99. A Regressão Logística alcança +92, e o LinearSVC, +73.

O ganho líquido combina comparações contra a decisão validada e, nos casos sem decisão travada, contra a categoria histórica. Sua principal função é orientar a seleção de chamados e modelos para revisão. A aplicação seletiva, vinculada à memória de decisão humana, concentra o benefício da reclassificação nos casos em que há evidência suficiente para alterar a categoria.

**Tabela 4** Ganho líquido de reclassificação por modelo

| Modelo | Total reclassificado | Corrigidos | Prejudicados | Ganho líquido | Reuso de decisão humana |
|---|---|---|---|---|---|
| LSTM | 13.905 | 670 | 571 | +99 | 8.805 |
| Regressão Logística | 13.932 | 245 | 153 | +92 | 8.727 |
| LinearSVC | 13.965 | 291 | 218 | +73 | 8.856 |
| Random Forest | 13.912 | 234 | 186 | +48 | 8.719 |
| SGD | 13.965 | 201 | 163 | +38 | 8.771 |
| Naive Bayes | 13.826 | 158 | 132 | +26 | 8.623 |
| Extra Trees | 13.899 | 237 | 226 | +11 | 8.713 |

Fonte: elaborado pelos autores (2026), após deduplicação dos registros de reclassificação por identificador.'''
    texto = bloco(texto, "**4.5 Reclassificação e ganho líquido**", "**4.6 Diagnóstico de taxonomia e ambiguidade estrutural\n(Shannon/Jensen-Shannon)**", secao_45, "4.5")

    secao_46 = r'''**4.6 Diagnóstico de taxonomia e ambiguidade estrutural (Shannon/Jensen-Shannon)**

A análise de Shannon e Jensen-Shannon considera o classificador operacional e os sete modelos materializados. O classificador operacional apresenta a maior diversidade de categorias previstas e a menor divergência em relação à distribuição histórica.

No nível dos chamados, 3.277 registros, equivalentes a 23,5% da base, apresentam alta entropia de votos. Esses casos concentram desacordo entre arquiteturas e formam uma fila de auditoria orientada por ambiguidade estrutural.

No nível das categorias, foram identificadas 76 ocorrências de alta ambiguidade entre classes com suporte mínimo de 30 registros. A análise indica onde a inspeção taxonômica deve ser concentrada, enquanto as decisões de fusão, separação ou redefinição de categorias permanecem sob responsabilidade da equipe técnica.

**Tabela 5** Entropia de Shannon e divergência de Jensen-Shannon por fonte de classificação

| Fonte | Categorias previstas | Entropia (nats) | Entropia normalizada | JS vs. histórico |
|---|---|---|---|---|
| Classificador operacional | 53 | 4,6758 | 0,8163 | 0,0286 |
| LSTM | 52 | 4,6201 | 0,8105 | 0,0847 |
| Regressão Logística | 52 | 4,4490 | 0,7805 | 0,0716 |
| SGD | 53 | 4,4363 | 0,7745 | 0,0639 |
| LinearSVC | 53 | 4,3356 | 0,7569 | 0,0575 |
| Extra Trees | 47 | 3,9955 | 0,7193 | 0,0761 |
| Random Forest | 47 | 3,9574 | 0,7124 | 0,0804 |
| Naive Bayes | 19 | 3,3340 | 0,7848 | 0,1755 |

Fonte: elaborado pelos autores (2026). O BERTimbau permanece fora da comparação por não dispor de ajuste fino concluído.'''
    texto = bloco(texto, "**4.6 Diagnóstico de taxonomia e ambiguidade estrutural\n(Shannon/Jensen-Shannon)**", "**4.7 Custo computacional**", secao_46, "4.6")

    secao_47 = r'''**4.7 Custo computacional**

A comparação de custo abrange os seis modelos clássicos com medições realizadas em lotes de 1.000 registros. Os tempos de treino variam entre 1,14 segundo para o Naive Bayes e 21,30 segundos para o Extra Trees. O LinearSVC treina em 2,55 segundos e apresenta o melhor acerto validado entre os modelos avaliados.

As medições posicionam o LinearSVC na região de melhor equilíbrio entre desempenho e custo. LSTM e BERTimbau deverão ser incorporados à comparação quando dispuserem de medições produzidas sob o mesmo protocolo.

**Tabela 6** Custo computacional por lote de 1.000 registros

| Modelo | Tempo de treino (s) | Tempo de inferência (s) | Acurácia neste lote |
|---|---|---|---|
| Naive Bayes | 1,14 | 0,07 | 0,539 |
| LinearSVC | 2,55 | 0,06 | 0,655 |
| SGD | 2,60 | 0,09 | 0,624 |
| Regressão Logística | 9,43 | 0,09 | 0,624 |
| Random Forest | 19,45 | 0,13 | 0,597 |
| Extra Trees | 21,30 | 0,14 | 0,610 |

Fonte: elaborado pelos autores (2026). A acurácia desta tabela contextualiza o *trade-off* custo–desempenho no lote medido; as métricas principais permanecem nas Tabelas 1 e 2.'''
    texto = bloco(texto, "**4.7 Custo computacional**", "**4.8 Figuras**", secao_47, "4.7")

    texto = texto.replace("Tabela 7, Subseção 4.7", "Tabela 6, Subseção 4.7")
    texto = texto.replace("executor oficial, Etapa 1", "classificador operacional")
    texto = texto.replace("Etapa 1 oficial", "classificador operacional")

    secao_49 = r'''**4.9 Estudo de ablação da LSTM**

A comparação entre o estudo de ablação e a avaliação principal da LSTM revelou duas fontes de diferença. A primeira foi a presença de grupos textuais repetidos entre treino e teste no *KFold* originalmente utilizado. Entre as 9.096 observações da coorte de ablação, 4.250 possuíam duplicata textual normalizada em outra partição.

O estudo foi refeito com *GroupKFold* definido pelo *hash* do texto normalizado. A alteração reduziu o acerto da configuração com 64 unidades e *dropout* de 0,5 de 87,68% para 86,35%, diferença de 1,33 ponto percentual. O resultado indica que a repetição textual produzia efeito mensurável, porém limitado.

A segunda fonte de diferença foi o desalinhamento entre a base utilizada no estudo de ablação e a referência empregada na comparação inicial. Na avaliação principal, a LSTM alcança 88,11%, enquanto o estudo corrigido alcança 86,35%. A diferença residual de 1,76 ponto percentual é compatível com as distinções entre os protocolos de particionamento e treinamento.

As quatro variantes avaliadas apresentam diferença inferior a quatro pontos percentuais. O resultado mostra baixa sensibilidade da LSTM às combinações testadas de número de unidades e *dropout*, ao mesmo tempo que confirma a importância do agrupamento de textos repetidos na construção das partições.

Fonte: elaborado pelos autores (2026).'''
    texto = bloco(texto, "**4.9 Investigação da discrepância do *ablation* do LSTM**", "**4.10 Robustez estatística: pressupostos e testes de sensibilidade**", secao_49, "4.9")

    secao_410 = r'''**4.10 Robustez estatística**

Os pressupostos da análise foram verificados segundo protocolo adaptado de Zuur, Ieno e Elphick (2010). A normalidade foi rejeitada para os sete modelos, sustentando o emprego de testes não paramétricos. As comparações por McNemar com correção de Holm-Bonferroni confirmam a superioridade estatística do LinearSVC; os diagnósticos, testes complementares e tabelas completas são apresentados no Material Suplementar.'''
    texto = bloco(texto, "**4.10 Robustez estatística: pressupostos e testes de sensibilidade**", "**5. DISCUSSÃO**", secao_410, "4.10")

    discussao = r'''**5. DISCUSSÃO**

O LinearSVC apresenta o melhor resultado tanto na concordância com o histórico quanto no acerto validado. Seu desempenho de 95,02%, associado ao tempo de treino de 2,55 segundos por lote de 1.000 registros, demonstra que uma representação TF-IDF combinada com um classificador linear constitui solução eficiente para chamados técnicos curtos e com vocabulário especializado.

O resultado também confirma a relevância de distinguir concordância administrativa de acerto validado. A diferença entre as duas métricas mostra que a avaliação de classificadores em bases institucionais depende da qualidade do rótulo de referência. A conferência humana acrescenta uma camada de governança ao separar erro de modelo, inconsistência histórica e ambiguidade taxonômica.

A combinação “IA correta e histórico incorreto” não foi observada na análise conjunta porque a regra de decisão utiliza as próprias fontes comparadas para formar a categoria validada. Essa dependência restringe estruturalmente a matriz e explica o valor zero. O resultado caracteriza o funcionamento da memória de decisão e aponta para a necessidade de uma amostra independente quando o objetivo for estimar diretamente a capacidade da IA de corrigir o histórico.

Os ganhos positivos de reclassificação indicam que os modelos contêm informação útil mesmo quando não ocupam a primeira posição no ranking global. A LSTM, por exemplo, apresenta o maior ganho líquido absoluto. A estratégia mais produtiva consiste em combinar a liderança global do LinearSVC com o uso complementar dos demais modelos para localizar divergências, identificar casos ambíguos e selecionar chamados para auditoria.

A entropia de votos acrescenta uma dimensão distinta da confiança individual. Os 3.277 chamados com alto desacordo entre modelos representam regiões da base em que diferentes hipóteses de classificação produzem respostas incompatíveis. Esse indicador direciona a revisão taxonômica e fortalece a gestão da incerteza no protocolo.

A faixa de confiança igual ou superior a 95% alcança 99,94% de acerto validado. O resultado fornece base empírica para uma política gradual de automação, com tratamento diferenciado por faixa de confiança e integração da calibração formal antes da adoção operacional em maior escala.

**Limitações**

A principal limitação de cobertura decorre do uso de dados de uma única instituição federal de ensino superior, com taxonomia própria e textos em português brasileiro. A transferência dos resultados para outras organizações requer avaliação externa sob diferentes distribuições de chamados, estruturas de categorias e práticas de registro.

A amostra conferida não é probabilística. A seleção prioriza divergências entre modelos e histórico, casos críticos e regiões de baixa confiança. Assim, os valores de acerto caracterizam os 9.044 chamados com decisão travada e não constituem estimativa inferencial do desempenho sobre os 13.965 registros. Os 490 casos sem verdade validada, entre eles 52 conflitos, foram incorporados à análise de sensibilidade; mesmo no cenário conservador, o ranking dos modelos permanece estável (COCHRAN, 1977).

A comparação neural inclui apenas a LSTM treinada sem *embeddings* pré-treinados de domínio. A avaliação do BERTimbau permitirá examinar o efeito de representações contextuais em português e ampliar a comparação entre modelos lineares, sequenciais e transformadores.

**Papel no modelo de governança preditiva**

Este estudo constitui o Eixo 1 de um modelo de governança preditiva para manutenção predial, no qual o campus universitário é compreendido como biossistema construído. A classificação transforma registros textuais dispersos em dados estruturados, auditáveis e associados a indicadores de confiança.

Esses dados alimentam três desenvolvimentos complementares. O primeiro compreende modelos de séries temporais para previsão de custos e demanda por categoria. O segundo utiliza métodos multicritério, como MCDM e TOPSIS, para priorizar intervenções segundo critérios técnicos, ambientais, sociais e institucionais. O terceiro espacializa os chamados e seus indicadores por meio de geoprocessamento.

A camada de classificação oferece, assim, a infraestrutura informacional necessária para integrar previsão, priorização e análise territorial. Sua contribuição central reside na transformação do chamado individual em evidência reutilizável para planejamento e decisão.'''
    texto = bloco(texto, "**5. DISCUSSÃO**", "**6. CONSIDERAÇÕES FINAIS**", discussao, "Discussão")

    conclusao = r'''**6. CONSIDERAÇÕES FINAIS**

O protocolo multimodelo identificou o LinearSVC como o classificador de melhor desempenho para os chamados analisados. O modelo alcançou 80,31% de concordância com o histórico e 95,02% de acerto na amostra validada, superando os demais classificadores e os três *ensembles*. Na faixa de confiança igual ou superior a 95%, o classificador operacional atingiu 99,94% de acerto em 4.675 decisões. Esses resultados, combinados ao baixo custo computacional, sustentam a adoção do LinearSVC como modelo principal, acompanhado de calibração de confiança e memória de decisão humana.

A contribuição do estudo ultrapassa a seleção de um classificador. O protocolo transforma textos operacionais ruidosos em dados estruturados e auditáveis, que podem alimentar previsão de custos e demanda, priorização multicritério de intervenções e análise espacial da manutenção. A classificação constitui, portanto, a camada informacional de base do modelo de governança preditiva aplicado ao biossistema construído universitário.

Os próximos passos concentram-se na validação externa em outras instituições, na calibração formal das probabilidades e margens de decisão e no treinamento comparativo do BERTimbau. Essas etapas permitirão avaliar a transferibilidade do protocolo, estabelecer limiares operacionais mais robustos e medir o ganho proporcionado por representações contextuais pré-treinadas em português.'''
    texto = bloco(texto, "**6. CONSIDERAÇÕES FINAIS**", "**Contribuições dos autores**", conclusao, "Conclusão")

    # Remover o checklist do manuscrito e renumerar a matriz M/N/P.
    texto, n = re.subn(
        re.escape("**Apêndice A — Checklist de itens reportados**")
        + r".*?(?="
        + re.escape("**Apêndice B — Matriz de decisão M/N/P**")
        + r")",
        "",
        texto,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise RuntimeError(f"Checklist não localizado para remoção (ocorrências={n})")
    texto = texto.replace(
        "**Apêndice B — Matriz de decisão M/N/P**",
        "**Apêndice A — Matriz de decisão M/N/P**",
        1,
    )

    # Substituições residuais de linguagem operacional/temporal.
    substituicoes = {
        "nesta consolidação": "neste estudo",
        "Nesta consolidação": "Neste estudo",
        "nesta execução": "neste estudo",
        "Nesta execução": "Neste estudo",
        "nesta rodada": "neste estudo",
        "Nesta rodada": "Neste estudo",
        "nesta data": "neste estudo",
        "Nesta data": "Neste estudo",
        "rodadas seguintes": "ciclos posteriores",
        "não substitui acurácia, calibração ou validação humana": "complementa a acurácia, a calibração e a validação humana",
        "não autoriza": "sustenta uma aplicação seletiva, em vez de",
        "não constitui": "representa",
        "deve ser lido como": "caracteriza",
    }
    for antigo, novo in substituicoes.items():
        texto = texto.replace(antigo, novo)

    # Material suplementar: preserva os detalhes retirados do corpo e o checklist.
    suplemento = """# Material Suplementar — classificação automática de chamados\n\n"
    suplemento += "## S5. Robustez estatística: diagnósticos e testes complementares\n\n"
    suplemento += (estatistica_anterior or "Os diagnósticos detalhados serão inseridos a partir dos artefatos estatísticos do repositório.") + "\n\n"
    suplemento += "## Checklist de itens reportados\n\n"
    suplemento += (checklist_anterior or "Checklist transferido do manuscrito principal.") + "\n"
    SUPLEMENTAR.write_text(suplemento, encoding="utf-8")

    # Validações editoriais mínimas.
    proibidos = [
        "nesta consolidação",
        "nesta execução",
        "nesta rodada",
        "nesta data",
        "**Tabela 4** Matriz de confusão",
        "**Apêndice A — Checklist de itens reportados**",
    ]
    minusculo = texto.lower()
    for termo in proibidos[:4]:
        if termo in minusculo:
            raise RuntimeError(f"Referência temporal residual: {termo}")
    for termo in proibidos[4:]:
        if termo in texto:
            raise RuntimeError(f"Elemento editorial residual: {termo}")

    esperados = [
        "**Tabela 4** Ganho líquido de reclassificação por modelo",
        "**Tabela 5** Entropia de Shannon",
        "**Tabela 6** Custo computacional",
        "**Apêndice A — Matriz de decisão M/N/P**",
        "**4.10 Robustez estatística**",
    ]
    for termo in esperados:
        if termo not in texto:
            raise RuntimeError(f"Elemento esperado ausente: {termo}")

    ARTIGO.write_text(texto, encoding="utf-8")

    if PLANO.exists():
        plano = PLANO.read_text(encoding="utf-8")
        estado = """- **Onde está**: a reformulação editorial e a sincronização numérica estão consolidadas na PR #75, branch `agent/corrigir-sincronizacao-artigo`.

**O que foi feito nesta rodada**: eliminadas referências temporais internas e linguagem de relatório operacional; parágrafos extensos foram segmentados; a Subseção 4.10 foi condensada e seus detalhes transferidos ao Material Suplementar; a ressalva da amostra não probabilística foi concentrada na Discussão; a matriz IA × histórico foi substituída por explicação textual da dependência estrutural da regra de decisão; o checklist foi removido do manuscrito; e a conclusão foi reduzida a três parágrafos.

**Próximo passo**: revisar o PDF regenerado e, se a paginação permanecer íntegra, preparar a PR #75 para merge por squash."""
        plano, n = re.subn(
            r"- \*\*Onde está\*\*:.*?(?=\n\n---)",
            estado,
            plano,
            count=1,
            flags=re.S,
        )
        if n == 1:
            PLANO.write_text(plano, encoding="utf-8")

    print("Revisão editorial final aplicada com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
