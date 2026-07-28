#!/usr/bin/env python3
"""Atualiza o artigo com os resultados canônicos finais do BERTimbau.

Script temporário da PR #101. Trabalha por seções delimitadas e valida a
remoção de afirmações/números obsoletos antes de gravar o Markdown.
"""

from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ARTIGO = RAIZ / "04_artigo" / "artigo_classificacao_chamados_v3.md"


def substituir_exato(texto: str, antigo: str, novo: str, *, n: int = 1) -> str:
    achados = texto.count(antigo)
    if achados != n:
        raise RuntimeError(f"Trecho esperado {n} vez(es), encontrado {achados}: {antigo[:90]!r}")
    return texto.replace(antigo, novo)


def substituir_secao(texto: str, inicio: str, fim: str, novo: str) -> str:
    i = texto.find(inicio)
    if i < 0:
        raise RuntimeError(f"Início de seção não encontrado: {inicio}")
    j = texto.find(fim, i + len(inicio))
    if j < 0:
        raise RuntimeError(f"Fim de seção não encontrado: {fim}")
    return texto[:i] + novo.rstrip() + "\n\n" + texto[j:]


def main() -> int:
    texto = ARTIGO.read_text(encoding="utf-8")

    texto = substituir_exato(
        texto,
        "**CLASSIFICAÇÃO MULTIMODELO DE CHAMADOS DE MANUTENÇÃO PREDIAL\n"
        "UNIVERSITÁRIA EM PORTUGUÊS BRASILEIRO SOB RÓTULOS HISTÓRICOS RUIDOSOS**\n\n"
        "*Multi-model classification of university building maintenance work\n"
        "orders in Brazilian Portuguese under noisy historical labels*",
        "**CLASSIFICAÇÃO AUTOMÁTICA MULTIMODELO DE CHAMADOS DE MANUTENÇÃO PREDIAL\n"
        "UNIVERSITÁRIA EM PORTUGUÊS BRASILEIRO COM VALIDAÇÃO HUMANA**\n\n"
        "*Multi-model automatic classification of university building maintenance work\n"
        "orders in Brazilian Portuguese with human validation*",
    )

    resumo = """**RESUMO**

A classificação automática de chamados de manutenção predial constitui
recurso estratégico para qualificar a triagem operacional e ampliar a
governança baseada em evidências em instituições públicas. Em bases
históricas de sistemas informatizados de gestão de chamados, contudo, a
categoria originalmente registrada não deve ser tratada como verdade
absoluta, pois pode refletir decisões operacionais ruidosas, taxonomias
sobrepostas, registros incompletos e interpretações heterogêneas entre
equipes. Este artigo propõe um protocolo multimodelo para classificação
de chamados reais de manutenção predial universitária em português
brasileiro, extraídos do sistema institucional da Universidade Federal do
Sul da Bahia. O experimento utiliza 13.965 chamados não vazios,
organizados em 55 categorias históricas. A comparação principal avalia
seis classificadores clássicos baseados em TF-IDF e uma rede neural LSTM
bidirecional por predições *out-of-fold* sobre toda a base. O BERTimbau,
transformador pré-treinado em português, é ajustado e avaliado
separadamente em um *holdout* comum de 1.000 chamados, pois não dispõe de
predições *out-of-fold* materializadas para o corpus integral. O
diferencial metodológico reside na distinção entre concordância com o
histórico administrativo e acerto validado por revisão humana. O acerto
validado, apurado sobre 8.895 decisões, descreve apenas a amostra
conferida e constitui limite superior por construção amostral, dado que
639 casos sem categoria decidida permanecem fora do denominador. Na
comparação integral, o LinearSVC lidera a concordância com o histórico
(80,31%) e o acerto validado (95,27%). No *holdout* comum, o LinearSVC
alcança 78,56% e o BERTimbau 77,46%, sem diferença estatisticamente
significativa pelo teste de McNemar (*p* = 0,510). Os resultados indicam
que o modelo contextual é competitivo no recorte avaliado, mas não há
evidência de superioridade sobre o classificador linear. O custo
computacional permanece dimensão relevante da decisão e favorece modelos
lineares em cenários de texto curto, ruidoso e desbalanceado."""
    texto = substituir_secao(texto, "**RESUMO**", "**Palavras-chave:**", resumo)

    abstract = """**ABSTRACT**

*Automatic classification of building maintenance work orders is a
strategic resource for improving operational triage and evidence-based
governance in public institutions. However, the originally assigned
category in historical service-management databases should not be treated
as unquestionable ground truth because it may reflect noisy operational
decisions, overlapping taxonomies, incomplete records, and heterogeneous
interpretations. This paper proposes a multi-model protocol for
classifying real university building maintenance requests in Brazilian
Portuguese from the Federal University of Southern Bahia. The experiment
uses 13,965 non-empty records organized into 55 historical categories.
The main comparison evaluates six TF-IDF-based classical classifiers and
a bidirectional LSTM through out-of-fold predictions over the complete
corpus. BERTimbau, a Portuguese pre-trained transformer, is fine-tuned and
evaluated separately on a common holdout of 1,000 work orders because
full-corpus out-of-fold predictions are not available for this model. The
methodological contribution is the distinction between agreement with the
administrative history and human-validated accuracy. Human-validated
accuracy is calculated over 8,895 decisions and describes only the
reviewed sample; it is an upper bound by sampling construction because
639 cases without a decided category remain outside the denominator. In
the full-corpus comparison, LinearSVC leads both agreement with history
(80.31%) and human-validated accuracy (95.27%). In the common holdout,
LinearSVC reaches 78.56% and BERTimbau 77.46%, with no statistically
significant difference under McNemar's test (p = 0.510). The contextual
model is therefore competitive in the evaluated subset, but there is no
evidence that it outperforms the linear classifier. Computational cost
remains a relevant decision dimension and favors linear models in short,
noisy, and imbalanced text settings.*"""
    texto = substituir_secao(texto, "**ABSTRACT**", "***Keywords:**", abstract)

    texto = substituir_exato(
        texto,
        "O estudo compara modelos clássicos\n"
        "baseados em TF-IDF (Naive Bayes, Regressão Logística, LinearSVC, SGD,\n"
        "Random Forest e Extra Trees) com uma rede neural LSTM bidirecional. O\n"
        "BERTimbau é mantido como extensão planejada e não integra as comparações\n"
        "enquanto não houver treino concluído e métricas próprias rastreáveis.",
        "O estudo compara modelos clássicos\n"
        "baseados em TF-IDF (Naive Bayes, Regressão Logística, LinearSVC, SGD,\n"
        "Random Forest e Extra Trees) com uma rede neural LSTM bidirecional. O\n"
        "BERTimbau também é ajustado, mas sua avaliação permanece em protocolo\n"
        "*holdout* separado, com métricas próprias rastreáveis, porque não há\n"
        "predições *out-of-fold* desse modelo sobre toda a base.",
    )

    texto = substituir_exato(
        texto,
        "Um oitavo modelo, o transformador pré-treinado em português BERTimbau,\n"
        "permanece como extensão planejada. Seu ajuste fino depende do avanço da\n"
        "base validada e ainda não foi concluído, razão pela qual o modelo não\n"
        "integra tabelas, rankings, testes inferenciais nem conclusões\n"
        "comparativas deste artigo.",
        "Um oitavo modelo, o BERTimbau-Base, incorpora representações contextuais\n"
        "pré-treinadas em português brasileiro e é ajustado para as 55 categorias\n"
        "do corpus (DEVLIN *et al.*, 2019; SOUZA; NOGUEIRA; LOTUFO, 2020). O\n"
        "treino foi concluído em modo automático, com subamostragem estratificada\n"
        "e parada antecipada por restrição computacional. Como o modelo não possui\n"
        "predições *out-of-fold* materializadas sobre toda a base, ele não é\n"
        "inserido artificialmente no ranking integral dos sete modelos. Sua\n"
        "comparação é apresentada em protocolo *holdout* comum na Subseção 4.3.",
    )

    marcador_35 = (
        "As Tabelas 1 e 2 reportam o protocolo por linha, por\n"
        "coerência com a materialização em produção, e o material suplementar\n"
        "traz a comparação completa entre os dois.\n"
    )
    insercao_35 = marcador_35 + """

A avaliação do BERTimbau segue protocolo adicional e não substitui a
comparação *out-of-fold*. A execução completa mais recente do transformador
define um lote de 1.000 chamados. Os outros sete modelos são retreinados
fora exatamente dessas linhas e avaliados no mesmo conjunto, evitando
sobreposição entre treino e teste. O lote contém 639 chamados com decisão
humana M/N/P/Q. Reportam-se concordância com o histórico, acerto validado,
intervalos por *bootstrap* e McNemar entre o BERTimbau e o melhor modelo
alternativo. Como o lote corresponde aos primeiros registros elegíveis e
não a uma amostra probabilística, os resultados descrevem esse recorte e
não substituem a avaliação integral da base."""
    texto = substituir_exato(texto, marcador_35, insercao_35)

    validacao = """Duas unidades de análise convivem no protocolo e não devem ser
confundidas. O **chamado** é o registro individual de manutenção, unidade
das Tabelas 1, 2 e 3. A **conferência** é cada julgamento humano emitido
sobre uma fonte de classificação. A decisão M/N/P/Q pode manter o
histórico, aceitar uma classificação automática, aceitar a
reclassificação ou registrar manualmente uma categoria distinta. Dos
13.965 chamados, 9.534 receberam ao menos uma conferência; 8.895 chegaram
a uma categoria decidida e 639 permaneceram restritos, incluindo 201
conflitos entre fontes marcadas como corretas. A priorização recai sobre
chamados em que há divergência entre modelos, alta confiança da IA contra
o histórico, baixa confiança generalizada, classes raras e pares de
categorias com alta confusão recíproca. Essa estrutura permite separar
uma decisão validada de casos ainda sem referência suficiente, em
consonância com a perspectiva de que a verdade operacional deve ser
construída progressivamente (ZHANG *et al.*, 2025)."""
    texto = substituir_secao(
        texto,
        "Duas unidades de análise convivem no protocolo e não devem ser",
        "```{=latex}\n\\FloatBarrier\n```\n\n**3.7 Memória de decisão",
        validacao + "\n\n```{=latex}\n\\FloatBarrier\n```\n\n**3.7 Memória de decisão",
    )

    resultados_intro = """**4. RESULTADOS**

Esta seção apresenta três conjuntos de resultados deliberadamente
segregados. O primeiro é a concordância dos sete modelos com a categoria
histórica na base completa (Subseção 4.1), em que o registro do GLPI é
referência preliminar, não verdade absoluta. O segundo é o desempenho
desses mesmos modelos contra a decisão humana M/N/P/Q (Subseção 4.2). O
terceiro é a comparação dos oito modelos no *holdout* comum que inclui o
BERTimbau (Subseção 4.3). A base elegível contém 13.965 chamados. A
conferência humana cobre 9.534 chamados (68,3% da base), dos quais 8.895
têm decisão validada (63,7% da base) e 639 permanecem restritos. Entre os
restritos, 201 apresentam conflito entre fontes marcadas como corretas.

Três achados resumem a seção. Primeiro, o LinearSVC lidera a comparação
integral, tanto em concordância histórica quanto em acerto validado, e
mantém vantagem operacional de custo. Segundo, no *holdout* comum, o
BERTimbau ocupa a segunda posição e não difere significativamente do
LinearSVC, o que caracteriza competitividade sem demonstrar
superioridade. Terceiro, a faixa de confiança igual ou superior a 95%
alcança acerto validado superior a 95%, com as ressalvas de calibração e
seleção amostral discutidas na Subseção 4.4.

```{=latex}
\FloatBarrier
```

"""
    texto = substituir_secao(texto, "**4. RESULTADOS**", "**4.1 Concordância", resultados_intro + "**4.1 Concordância")

    texto = substituir_exato(
        texto,
        "A comparação exclui o BERTimbau,\n"
        "cujo treino não foi concluído.",
        "A comparação integral exclui o BERTimbau porque o modelo não possui\n"
        "predições *out-of-fold* sobre as 13.965 linhas; o treino concluído é\n"
        "avaliado separadamente na Subseção 4.3.",
    )

    secao_42 = """**4.2 Ranking validado por conferência humana**

A avaliação contra a decisão humana M/N/P/Q utiliza 8.895 chamados com
categoria decidida. O LinearSVC permanece o melhor modelo isolado, com
acerto validado de 0,9527 (IC95%: 0,9482--0,9569), seguido por SGD
(0,9442), Regressão Logística (0,9404), Extra Trees (0,9314), Random
Forest (0,9268), LSTM (0,8872) e Naive Bayes (0,8659). A diferença entre
o primeiro e o segundo colocado é de 0,85 ponto percentual e é
estatisticamente significativa (McNemar, *p* < 0,001). Foram avaliados
também três *ensembles*: maioria ponderada (0,9493), confiança calibrada
máxima (0,9484) e maioria simples (0,9467). Todos ficam abaixo do
LinearSVC, com McNemar *p* < 0,05 em favor do modelo isolado. A
recomendação é, portanto, usar o LinearSVC isolado, com calibração.

O número pontual constitui limite superior condicionado ao desenho da
validação. Dos 9.534 chamados conferidos, 639 (6,7%) permanecem sem
categoria decidida. Esse conjunto reúne 340 casos em que apenas o
histórico foi marcado como errado, 98 em que histórico e classificação
automática foram marcados como errados e 201 conflitos entre fontes
marcadas como corretas. Sem categoria manual adicional, esses registros
não oferecem referência contra a qual medir o acerto e ficam fora do
denominador de 8.895 decisões.

A análise de sensibilidade incorpora os 639 restritos ao denominador como
erro de todos os modelos, cenário conservador que produz um limite
inferior. O LinearSVC varia de 0,8888 a 0,9527, o SGD de 0,8810 a 0,9442,
a Regressão Logística de 0,8774 a 0,9404, o Extra Trees de 0,8690 a
0,9314, o Random Forest de 0,8647 a 0,9268, o LSTM de 0,8278 a 0,8872 e
o Naive Bayes de 0,8078 a 0,8659. A amplitude varia de 5,80 a 6,39
pontos percentuais, mas o ranking relativo permanece inalterado. A
conclusão sobre qual modelo priorizar é robusta ao cenário conservador;
os valores absolutos exigem a ressalva amostral.

**Tabela 2** Acerto validado por modelo e limite inferior de
sensibilidade ao viés de seleção (n = 8.895). O limite inferior inclui os
639 casos restritos como erro de todos os modelos.

| Modelo | Acerto validado | IC95% | Limite inferior |
|---|---|---|---|
| LinearSVC | 0,9527 | 0,9482 -- 0,9569 | 0,8888 |
| SGD | 0,9442 | 0,9394 -- 0,9490 | 0,8810 |
| Regressão Logística | 0,9404 | 0,9355 -- 0,9453 | 0,8774 |
| Extra Trees | 0,9314 | 0,9261 -- 0,9365 | 0,8690 |
| Random Forest | 0,9268 | 0,9213 -- 0,9320 | 0,8647 |
| LSTM | 0,8872 | 0,8805 -- 0,8940 | 0,8278 |
| Naive Bayes | 0,8659 | 0,8588 -- 0,8731 | 0,8078 |"""
    texto = substituir_secao(texto, "**4.2 Ranking validado", "**4.3 A classificação automática", secao_42 + "\n\n**4.3 A classificação automática")

    secao_43 = """**4.3 BERTimbau no holdout comum de oito modelos**

O BERTimbau foi comparado aos sete modelos no mesmo lote de 1.000
chamados, com treino realizado fora dessas linhas. Entre os registros do
lote, 639 possuem decisão humana M/N/P/Q e formam o denominador do acerto
validado. O LinearSVC ocupa a primeira posição, com 0,7856 (IC95%:
0,7527--0,8185), e o BERTimbau a segunda, com 0,7746 (IC95%:
0,7402--0,8075). A diferença é de 1,10 ponto percentual em favor do
LinearSVC e não é estatisticamente significativa (McNemar, *p* = 0,510;
38 discordâncias em que somente o BERTimbau acerta e 45 em que somente o
LinearSVC acerta).

O resultado indica que o pré-treinamento contextual em português torna o
BERTimbau competitivo neste corpus, mas não sustenta superioridade sobre
o classificador linear. A leitura deve permanecer separada do ranking da
Subseção 4.2: o lote corresponde aos primeiros registros elegíveis, não é
probabilístico e não cobre o corpus integral. Além disso, o modo
automático do BERTimbau usa subamostragem estratificada e parada
antecipada por limite computacional. A comparação responde se o modelo é
competitivo em um recorte comum, mas não substitui uma execução
*out-of-fold* integral.

**Tabela 3** Comparação dos oito modelos no mesmo holdout (n = 1.000;
n = 639 com decisão validada).

| Modelo | Concordância histórica | Acerto validado | IC95% validado |
|---|---|---|---|
| LinearSVC | 0,6560 | 0,7856 | 0,7527 -- 0,8185 |
| BERTimbau | 0,6520 | 0,7746 | 0,7402 -- 0,8075 |
| Regressão Logística | 0,6280 | 0,7653 | 0,7324 -- 0,7981 |
| SGD | 0,6250 | 0,7621 | 0,7293 -- 0,7950 |
| Extra Trees | 0,6120 | 0,7167 | 0,6808 -- 0,7527 |
| Random Forest | 0,5950 | 0,6948 | 0,6604 -- 0,7308 |
| LSTM | 0,5190 | 0,6526 | 0,6166 -- 0,6886 |
| Naive Bayes | 0,5390 | 0,6354 | 0,5978 -- 0,6714 |

```{=latex}
\FloatBarrier
```"""
    texto = substituir_secao(texto, "**4.3 A classificação automática", "**4.4 Confiança", secao_43 + "\n\n**4.4 Confiança")

    texto = substituir_exato(
        texto,
        "O diagnóstico de Shannon abrange oito fontes comparáveis, a\n"
        "classificação automática em produção e os sete modelos avaliados. O\n"
        "BERTimbau foi excluído por não ter treino concluído.",
        "O diagnóstico de Shannon abrange oito fontes comparáveis, a\n"
        "classificação automática em produção e os sete modelos com predições\n"
        "sobre toda a base. O BERTimbau foi excluído dessa análise porque não\n"
        "possui predições integrais materializadas.",
    )
    texto = substituir_exato(
        texto,
        "Não\n"
        "há medição comparável de custo para LSTM ou BERTimbau, portanto não é\n"
        "possível ordenar esses dois modelos frente aos demais.",
        "Não\n"
        "há medição padronizada de custo para LSTM ou BERTimbau no mesmo ambiente\n"
        "e protocolo, portanto não é possível ordená-los frente aos demais.",
    )

    secao_51 = """**5.1 Concordância histórica, acerto validado e BERTimbau**

A comparação entre concordância histórica (Subseção 4.1) e desempenho
validado (Subseção 4.2) revela que as duas grandezas não são
intercambiáveis. O acerto validado do LinearSVC (95,27%) supera sua
concordância com o histórico (80,31%) em 14,96 pontos percentuais. Essa
diferença não pode ser interpretada como taxa de erro do histórico, pois
a amostra conferida é não probabilística e a própria regra de decisão
condiciona quais casos recebem categoria de referência.

O mecanismo estrutural aparece nos 639 chamados restritos, equivalentes a
6,7% dos 9.534 conferidos. Eles incluem casos em que todas as fontes
avaliadas foram rejeitadas e 201 conflitos entre fontes marcadas como
corretas. A análise de sensibilidade os trata como erro de todos os
modelos e encontra amplitudes entre 5,80 e 6,39 pontos percentuais, sem
alterar o ranking. Assim, a escolha qualitativa do LinearSVC permanece
robusta, mas o valor pontual de acerto validado deve ser sempre
acompanhado da ressalva amostral.

O desenho atual também não permite estimar uma taxa empírica de erro do
rótulo histórico. Quando o histórico é marcado como errado e nenhuma
categoria alternativa é decidida, o chamado permanece restrito; sem o
preenchimento da categoria manual Q, não há referência final para afirmar
qual fonte acertou. A hipótese de rótulos potencialmente ruidosos continua
fundamentada na literatura e justifica a conferência, mas não deve ser
apresentada como taxa confirmada por esta amostra (KEJRIWAL *et al.*,
2024; ZHANG *et al.*, 2025).

A avaliação do BERTimbau acrescenta uma terceira perspectiva. No mesmo
*holdout*, o transformador alcança 77,46% de acerto validado, contra
78,56% do LinearSVC, sem diferença significativa. O pré-treinamento
contextual reduz a distância observada entre modelos lineares e a LSTM
que aprende *embeddings* do zero, mas não produz ganho demonstrável sobre
o LinearSVC. Como os protocolos são distintos, a métrica do BERTimbau não
deve ser comparada diretamente aos 95,27% da avaliação integral. O
resultado sustenta sua competitividade e justifica uma futura execução
*out-of-fold* completa, não sua adoção preferencial imediata."""
    texto = substituir_secao(texto, "**5.1 Concordância histórica", "**5.2 Reclassificação", secao_51 + "\n\n```{=latex}\n\\FloatBarrier\n```\n\n**5.2 Reclassificação")

    secao_53 = """**5.3 Limitações**

Os dados provêm de uma única instituição federal de ensino superior, com
textos em português brasileiro e taxonomia institucional própria.
Estender o desempenho relatado a outras instituições, taxonomias ou
idiomas exige validação externa.

A amostra conferida por avaliadores humanos não é probabilística, pois
prioriza divergências entre modelo e histórico e casos de maior
criticidade. Os números de acerto validado descrevem a amostra conferida,
e não estimam por inferência o desempenho da base completa (COCHRAN,
1977). Dos 9.534 chamados conferidos, 639 permanecem sem categoria
decidida e ficam fora do denominador padrão. A análise de sensibilidade
apura amplitude de 5,80 a 6,39 pontos percentuais entre o cenário
conservador e o valor pontual, sem alterar o ranking relativo.

A regra M/N/P/Q ainda depende do preenchimento manual de uma categoria
quando todas as fontes são rejeitadas ou entram em conflito. Enquanto
essa categoria não é informada, o protocolo não permite quantificar a
taxa de erro do histórico nem atribuir acerto a um modelo nesses casos.
A validação confirma a necessidade de governança sobre os rótulos, mas
não autoriza estimar, com o desenho atual, a prevalência de categorias
históricas incorretas.

As Tabelas 1 e 2 usam particionamento por linha, e não por grupo textual.
A comparação da Subseção 3.5 mostra superestimação média de 0,58 ponto
percentual, sem alteração relevante da ordenação. Os valores absolutos
devem ser lidos com essa margem.

O BERTimbau teve o ajuste fino concluído, mas foi avaliado apenas em um
*holdout* comum de 1.000 chamados, dos quais 639 possuem decisão humana.
Não há predições *out-of-fold* integrais nem medição de custo executada no
mesmo ambiente dos demais modelos, o que impede inseri-lo no ranking
principal ou comparar eficiência computacional de forma direta. A LSTM,
por sua vez, treina *embeddings* do zero, sem vetores pré-treinados em
português, condição que limita a comparação entre arquiteturas neurais."""
    texto = substituir_secao(texto, "**5.3 Limitações**", "**5.4 Contribuição", secao_53 + "\n\n```{=latex}\n\\FloatBarrier\n```\n\n**5.4 Contribuição")

    conclusao = """**6. CONSIDERAÇÕES FINAIS**

A contribuição central deste artigo é metodológica. O protocolo separa a
concordância com o rótulo histórico do acerto validado por conferência
humana e registra decisões, vetos e categorias manuais como conhecimento
persistente. Essa camada evita tratar o histórico como verdade automática
e, ao mesmo tempo, impede concluir que toda divergência da IA representa
correção do registro original.

Na avaliação integral de 8.895 chamados com decisão M/N/P/Q, o LinearSVC
alcança 95,27% de acerto validado (IC95%: 94,82%--95,69%) e nenhum dos
três *ensembles* o supera. A análise conservadora que inclui 639 casos
restritos reduz o limite do LinearSVC para 88,88%, sem modificar a
ordenação dos modelos. A recomendação operacional permanece usar o
LinearSVC isolado, com calibração formal antes de automatizar decisões de
alta confiança.

O BERTimbau foi efetivamente treinado e avaliado. No *holdout* comum de
1.000 chamados, com 639 decisões validadas, alcança 77,46%, contra 78,56%
do LinearSVC, sem diferença significativa. O resultado mostra que o
transformador é competitivo, mas não demonstra superioridade e não pode
ser combinado ao ranking integral sem uma execução *out-of-fold* sobre
toda a base.

A finalização metodológica também exige reconhecer o que os dados não
respondem. Como casos sem categoria decidida permanecem restritos, o
desenho atual não estima a taxa de erro do histórico. A próxima etapa de
validação deve preencher a categoria manual Q nesses casos, com prioridade
para conflitos e rejeição de todas as fontes. Em paralelo, a validação
externa em outras instituições e a execução integral do BERTimbau poderão
testar a estabilidade dos resultados sob taxonomias e volumes distintos.
A camada classificada poderá então alimentar modelos de previsão de
demanda e de priorização multicritério de intervenções sobre uma base cuja
incerteza e origem das decisões permanecem auditáveis."""
    texto = substituir_secao(texto, "**6. CONSIDERAÇÕES FINAIS**", "**REFERÊNCIAS**", conclusao + "\n\n**REFERÊNCIAS**")

    # Ajustes residuais em trechos que permanecem fora das seções reescritas.
    ajustes = {
        "0,9524": "0,9527",
        "95,24%": "95,27%",
        "0,8617": "0,8659",
        "0,8647; Tabela 2": "0,8659; Tabela 2",
        "8.928": "8.895",
        "606 casos restritos": "639 casos restritos",
        "606 restritos": "639 restritos",
        "168 registram conflito": "201 registram conflito",
    }
    for antigo, novo in ajustes.items():
        texto = texto.replace(antigo, novo)

    ref_devlin = """DEVLIN, J.; CHANG, M.-W.; LEE, K.; TOUTANOVA, K. BERT:
Pre-training of deep bidirectional transformers for language
understanding. In: CONFERENCE OF THE NORTH AMERICAN CHAPTER OF THE
ASSOCIATION FOR COMPUTATIONAL LINGUISTICS, 2019, Minneapolis.
Proceedings [...]. Minneapolis: ACL, 2019. p. 4171--4186.

"""
    texto = substituir_exato(texto, "DICICCIO, T. J.; EFRON, B.", ref_devlin + "DICICCIO, T. J.; EFRON, B.")

    ref_souza = """SOUZA, F.; NOGUEIRA, R.; LOTUFO, R. BERTimbau: pretrained BERT
models for Brazilian Portuguese. In: BRAZILIAN CONFERENCE ON INTELLIGENT
SYSTEMS, 9., 2020. Proceedings [...]. Cham: Springer, 2020. p. 403--417.
DOI: 10.1007/978-3-030-61377-8_28.

"""
    texto = substituir_exato(texto, "SPEARMAN, C.", ref_souza + "SPEARMAN, C.")

    proibidos = [
        "17.790",
        "1,83%",
        "treino não foi concluído",
        "ajuste fino depende do avanço",
        "remains a planned extension",
        "neither completed training",
        "8.928",
        "0,9524",
        "95,24%",
        "0,8858",
        "88,58%",
        "606 restritos",
        "606 casos restritos",
    ]
    presentes = [item for item in proibidos if item in texto]
    if presentes:
        raise RuntimeError(f"Conteúdo obsoleto ainda presente: {presentes}")

    obrigatorios = [
        "BERTimbau no holdout comum de oito modelos",
        "0,7746",
        "0,7856",
        "*p* = 0,510",
        "8.895",
        "639 casos",
        "SOUZA, F.; NOGUEIRA, R.; LOTUFO, R.",
        "DEVLIN, J.; CHANG, M.-W.; LEE, K.; TOUTANOVA, K.",
    ]
    ausentes = [item for item in obrigatorios if item not in texto]
    if ausentes:
        raise RuntimeError(f"Conteúdo final ausente: {ausentes}")

    ARTIGO.write_text(texto, encoding="utf-8")
    print(f"Artigo atualizado: {ARTIGO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
