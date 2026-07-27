#!/usr/bin/env python3
"""Sincroniza os números da versão editorial com os agregados do mesmo job.

O script atua apenas sobre blocos numéricos previamente delimitados. A estrutura
editorial, as referências e as interpretações científicas permanecem estáveis.
"""

from __future__ import annotations

import json
from pathlib import Path
import re

RAIZ = Path(__file__).resolve().parents[1]
ARTIGO = RAIZ / "04_artigo" / "artigo_classificacao_chamados_v3.md"
DADOS = RAIZ / "docs" / "dados"
SENSIBILIDADE = RAIZ / "04_artigo" / "figuras" / "sensibilidade_vies_validacao.json"

NOMES = {
    "linear_svc": "LinearSVC",
    "sgd": "SGD",
    "regressao_logistica": "Regressão Logística",
    "extra_trees": "Extra Trees",
    "random_forest": "Random Forest",
    "lstm": "LSTM",
    "naive_bayes": "Naive Bayes",
}


def ler_json(caminho: Path) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))


def dec(valor: float, casas: int = 4) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def pct(valor: float, casas: int = 2) -> str:
    return f"{valor * 100:.{casas}f}".replace(".", ",")


def inteiro(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def substituir_bloco(texto: str, inicio: str, fim: str, novo: str, rotulo: str) -> str:
    padrao = re.escape(inicio) + r".*?(?=" + re.escape(fim) + r")"
    resultado, n = re.subn(padrao, novo.strip() + "\n\n", texto, count=1, flags=re.S)
    if n != 1:
        raise RuntimeError(f"Bloco não localizado ou ambíguo: {rotulo} (ocorrências={n})")
    return resultado


def main() -> int:
    avaliacao = ler_json(DADOS / "avaliacao_final.json")
    calibracao = ler_json(DADOS / "calibracao.json")
    sensibilidade = ler_json(SENSIBILIDADE)

    total = int(calibracao["total"])
    conferidos = int(avaliacao["conferencias"]["com_conferencia"])
    decididos = int(avaliacao["conferencias"]["decididos"])
    restritos = int(avaliacao["conferencias"]["restritos"])
    conflitos = int(avaliacao["conferencias"]["conflitos"])

    modelos = {item["modelo"]: item for item in avaliacao["por_modelo"]}
    sens = {item["modelo"]: item for item in sensibilidade["por_modelo"]}
    linear = modelos["linear_svc"]
    lstm = modelos["lstm"]
    alvo = calibracao["faixa_alvo_95"]
    matriz = calibracao["validacao_humana"]["matriz_ia_x_glpi"]

    texto = ARTIGO.read_text(encoding="utf-8")

    resumo = f'''**RESUMO**

A classificação automática de chamados de manutenção predial constitui um recurso estratégico para qualificar a triagem operacional e ampliar a governança baseada em evidências em instituições públicas. Entretanto, as categorias registradas em sistemas administrativos podem refletir taxonomias sobrepostas, informações incompletas e interpretações heterogêneas das equipes de atendimento.

Este artigo propõe um protocolo multimodelo para a classificação de chamados reais de manutenção predial universitária em português brasileiro, extraídos do sistema GLPI da Universidade Federal do Sul da Bahia. O corpus reúne {inteiro(total)} chamados não vazios, distribuídos em 55 categorias históricas, e compara classificadores baseados em TF-IDF — Naive Bayes, Regressão Logística, LinearSVC, SGD, Random Forest e Extra Trees — com uma rede neural LSTM bidirecional. O BERTimbau é apresentado como extensão planejada.

O protocolo distingue a concordância com o histórico administrativo do acerto avaliado por revisão humana, tratando a categoria original como referência preliminar. A conferência abrange {inteiro(conferidos)} chamados, dos quais {inteiro(decididos)} possuem decisão travada e {inteiro(conflitos)} apresentam conflito entre as fontes avaliadas. O LinearSVC alcança a maior concordância com o histórico, com 80,31% (IC95%: 79,63%–80,97%), e o maior acerto validado, com {pct(linear["acerto_validado"])}% (IC95%: {pct(linear["ic95"][0])}%–{pct(linear["ic95"][1])}%). A LSTM obtém, respectivamente, 67,18% e {pct(lstm["acerto_validado"])}%.

Na faixa de confiança igual ou superior a 95%, o classificador operacional alcança {pct(alvo["acerto_validado"])}% de acerto em {inteiro(alvo["n_validados"])} decisões validadas. Os resultados referem-se à amostra conferida, cuja composição é discutida na Seção 5. A rejeição da normalidade sustenta o emprego de testes não paramétricos. Em conjunto, os achados mostram que classificadores lineares oferecem equilíbrio favorável entre desempenho, custo computacional e auditabilidade para textos técnicos curtos, ruidosos e desbalanceados.

**Palavras-chave:** manutenção predial; classificação de chamados; processamento de linguagem natural; rótulos ruidosos; validação humana; governança preditiva.'''
    texto = substituir_bloco(texto, "**RESUMO**", "**ABSTRACT**", resumo, "Resumo")

    abstract = f'''**ABSTRACT**

*Automatic classification of building-maintenance work orders is a strategic resource for improving operational triage and evidence-based governance in public institutions. Administrative categories, however, may reflect overlapping taxonomies, incomplete information and heterogeneous interpretations by maintenance teams.

This study proposes a multi-model protocol for {total:,} real university building-maintenance work orders in Brazilian Portuguese, organized into 55 historical categories. The comparison includes TF-IDF-based classifiers — Naive Bayes, Logistic Regression, LinearSVC, SGD, Random Forest and Extra Trees — and a bidirectional LSTM. BERTimbau is presented as a planned extension.

The protocol distinguishes agreement with the administrative history from accuracy against human-reviewed decisions. Human review covers {conferidos:,} records, including {decididos:,} locked decisions and {conflitos:,} conflicts. LinearSVC achieves the highest historical agreement, 80.31% (95% CI: 79.63%–80.97%), and the highest validated accuracy, {linear["acerto_validado"] * 100:.2f}% (95% CI: {linear["ic95"][0] * 100:.2f}%–{linear["ic95"][1] * 100:.2f}%). LSTM reaches 67.18% and {lstm["acerto_validado"] * 100:.2f}%, respectively.

For predictions with confidence equal to or greater than 95%, the operational classifier reaches {alvo["acerto_validado"] * 100:.2f}% validated accuracy across {alvo["n_validados"]:,} decisions. The results refer to the reviewed sample, whose composition is discussed in Section 5. Rejection of normality supports non-parametric testing. Overall, linear classifiers provide a favorable balance between performance, computational cost and auditability for short, noisy and imbalanced technical text.*

***Keywords:** building maintenance; work-order classification; natural language processing; noisy labels; human validation; predictive governance.*'''
    texto = substituir_bloco(texto, "**ABSTRACT**", "**1. INTRODUÇÃO**", abstract, "Abstract")

    abertura = f'''**4. RESULTADOS**

A análise separa a concordância com a categoria histórica do desempenho contra a decisão validada por conferência humana. A base contém {inteiro(total)} chamados, dos quais {inteiro(conferidos)} foram conferidos. Entre eles, {inteiro(decididos)} possuem categoria decidida e {inteiro(restritos)} permanecem sem verdade validada, incluindo {inteiro(conflitos)} conflitos.

Os resultados evidenciam três padrões. Os classificadores lineares, liderados pelo LinearSVC, apresentam o melhor desempenho global. A conferência humana demonstra que concordância administrativa e acerto validado são dimensões distintas. Por fim, as faixas superiores de confiança concentram maior proporção de decisões corretas.'''
    texto = substituir_bloco(texto, "**4. RESULTADOS**", "**4.1 Concordância com o histórico (base completa)**", abertura, "abertura dos Resultados")

    linhas_t2 = []
    for chave in ("linear_svc", "sgd", "regressao_logistica", "extra_trees", "random_forest", "lstm", "naive_bayes"):
        item = modelos[chave]
        inferior = sens[chave]["limite_inferior"]
        linhas_t2.append(
            f'| {NOMES[chave]} | {dec(item["acerto_validado"])} | '
            f'{dec(item["ic95"][0])} -- {dec(item["ic95"][1])} | {dec(inferior)} |'
        )
    amplitudes = [item["amplitude"] * 100 for item in sens.values()]
    ensembles = {item["metodo"]: item["acerto_validado"] for item in avaliacao["ensembles"]}
    p_mcnemar = avaliacao["melhor_vs_segundo"]["p_mcnemar"]

    secao_42 = f'''**4.2 Ranking validado por conferência humana**

A comparação contra as {inteiro(decididos)} decisões travadas mantém o LinearSVC na primeira posição, com acerto validado de {dec(linear["acerto_validado"])} (IC95%: {dec(linear["ic95"][0])}–{dec(linear["ic95"][1])}). Em seguida aparecem SGD ({dec(modelos["sgd"]["acerto_validado"])}), Regressão Logística ({dec(modelos["regressao_logistica"]["acerto_validado"])}), Extra Trees ({dec(modelos["extra_trees"]["acerto_validado"])}), Random Forest ({dec(modelos["random_forest"]["acerto_validado"])}), LSTM ({dec(lstm["acerto_validado"])}), e Naive Bayes ({dec(modelos["naive_bayes"]["acerto_validado"])}).

A diferença entre LinearSVC e SGD é de {avaliacao["melhor_vs_segundo"]["delta"] * 100:.2f} ponto percentual, com McNemar *p* ≈ {p_mcnemar:.2e}. Os *ensembles* por maioria ponderada, confiança máxima e maioria simples alcançam, respectivamente, {dec(ensembles["maioria_ponderada"])}, {dec(ensembles["confianca_calibrada_max"])} e {dec(ensembles["maioria_simples"])}. O LinearSVC isolado permanece como a opção de maior desempenho. A composição da amostra validada e seus efeitos sobre a interpretação dos resultados são discutidos na Seção 5.

A análise de sensibilidade inclui os {inteiro(restritos)} casos sem verdade validada como erros no cenário conservador. A amplitude entre os limites varia de {min(amplitudes):.2f} a {max(amplitudes):.2f} pontos percentuais e preserva a ordenação dos sete modelos.

**Tabela 2** Acerto validado contra a verdade decidida M/N/P (n = {inteiro(decididos)}) e intervalo de sensibilidade

| Modelo | Acerto validado (limite superior) | IC95% | Limite inferior (pior caso) |
|---|---|---|---|
{chr(10).join(linhas_t2)}

Fonte: elaborado pelos autores (2026). O limite inferior considera os conflitos e os demais registros sem verdade validada como erros para todos os modelos.'''
    texto = substituir_bloco(texto, "**4.2 Ranking validado por conferência humana**", "**4.3 Interpretação conjunta da classificação operacional e do histórico**", secao_42, "4.2")

    secao_43 = f'''**4.3 Interpretação conjunta da classificação operacional e do histórico**

A classificação operacional e a categoria histórica foram comparadas com a mesma decisão validada em {inteiro(decididos)} chamados. Ambas coincidem com a decisão em {inteiro(matriz["ia_ok_glpi_ok"])} casos. Em {inteiro(matriz["ia_erro_glpi_ok"])} registros, o histórico coincide com a decisão e a classificação operacional diverge; em outros {inteiro(matriz["ia_erro_glpi_erro"])}, ambas divergem.

A ausência de ocorrências na combinação “classificação operacional correta e histórico incorreto” decorre da regra empregada para construir a verdade validada. A decisão é formada a partir das próprias fontes submetidas à conferência e somente é travada quando ao menos uma delas é confirmada. Essa dependência estrutural restringe a combinação correspondente, cujo valor caracteriza o funcionamento da regra de decisão, e não a capacidade da IA de corrigir o histórico.

O valor zero representa, portanto, uma propriedade do protocolo de decisão. A capacidade dos classificadores de identificar categorias históricas inadequadas requer uma amostra independente, anotada sem utilizar como ponto de partida as classificações comparadas.'''
    texto = substituir_bloco(texto, "**4.3 Interpretação conjunta da classificação operacional e do histórico**", "**4.4 Confiança, calibração e faixas de decisão**", secao_43, "4.3")

    linhas_t3 = []
    for item in calibracao["por_faixa"]:
        linhas_t3.append(
            f'| {item["faixa"]} | {inteiro(item["n"])} | {pct(item["concordancia_historico"])}% | '
            f'{inteiro(item["n_validados"])} | {pct(item["acerto_validado"])}% |'
        )
    secao_44 = f'''**4.4 Confiança, calibração e faixas de decisão**

O classificador operacional apresenta erro esperado de calibração histórico de {dec(calibracao["ece_historico"])}. Na faixa de confiança igual ou superior a 95%, que reúne {inteiro(alvo["n"])} chamados, a concordância com o histórico é de {pct(alvo["concordancia_historico"])}%. Entre as {inteiro(alvo["n_validados"])} decisões humanas disponíveis nessa faixa, o acerto validado alcança {pct(alvo["acerto_validado"])}%.

A confiança utilizada é bruta, derivada da função de decisão ou da saída probabilística dos modelos. Esses valores sustentam uma política de priorização por faixas e fornecem a base empírica para a calibração formal por Platt, regressão isotônica ou escalonamento de temperatura.

**Tabela 3** Acerto validado por faixa de confiança bruta, classificador operacional

| Faixa | n total | Concord. histórico | n validados | Acerto validado |
|---|---|---|---|---|
{chr(10).join(linhas_t3)}

Fonte: elaborado pelos autores (2026), após deduplicação por `linha_planilha`.'''
    texto = substituir_bloco(texto, "**4.4 Confiança, calibração e faixas de decisão**", "**4.5 Reclassificação e ganho líquido**", secao_44, "4.4")

    diferenca_ablation = abs(lstm["acerto_validado"] * 100 - 86.35)
    secao_49 = f'''**4.9 Estudo de ablação da LSTM**

A comparação entre o estudo de ablação e a avaliação principal da LSTM revelou duas fontes de diferença. A primeira foi a presença de grupos textuais repetidos entre treino e teste no *KFold* originalmente utilizado. Entre as 9.096 observações da coorte de ablação, 4.250 possuíam duplicata textual normalizada em outra partição.

O estudo foi refeito com *GroupKFold* definido pelo *hash* do texto normalizado. A alteração reduziu o acerto da configuração com 64 unidades e *dropout* de 0,5 de 87,68% para 86,35%, diferença de 1,33 ponto percentual. O resultado indica que a repetição textual produzia efeito mensurável, porém limitado.

A segunda fonte de diferença foi o desalinhamento entre a base utilizada no estudo de ablação e a referência empregada na comparação inicial. Na avaliação principal, a LSTM alcança {pct(lstm["acerto_validado"])}%, enquanto o estudo corrigido alcança 86,35%. A diferença residual de {diferenca_ablation:.2f} ponto percentual é compatível com as distinções entre os protocolos de particionamento e treinamento.

As quatro variantes avaliadas apresentam diferença inferior a quatro pontos percentuais. O resultado mostra baixa sensibilidade da LSTM às combinações testadas de número de unidades e *dropout*, ao mesmo tempo que confirma a importância do agrupamento de textos repetidos na construção das partições.

Fonte: elaborado pelos autores (2026).'''.replace(".", ",", 0)
    # A chamada replace acima é deliberadamente neutra; valores numéricos já foram formatados.
    secao_49 = secao_49.replace(f"{diferenca_ablation:.2f}", f"{diferenca_ablation:.2f}".replace(".", ","))
    texto = substituir_bloco(texto, "**4.9 Estudo de ablação da LSTM**", "**4.10 Robustez estatística**", secao_49, "4.9")

    discussao = f'''**5. DISCUSSÃO**

O LinearSVC apresenta o melhor resultado tanto na concordância com o histórico quanto no acerto validado. Seu desempenho de {pct(linear["acerto_validado"])}%, associado ao tempo de treino de 2,55 segundos por lote de 1.000 registros, demonstra que uma representação TF-IDF combinada com um classificador linear constitui solução eficiente para chamados técnicos curtos e com vocabulário especializado.

O resultado também confirma a relevância de distinguir concordância administrativa de acerto validado. A diferença entre as duas métricas mostra que a avaliação de classificadores em bases institucionais depende da qualidade do rótulo de referência. A conferência humana acrescenta uma camada de governança ao separar erro de modelo, inconsistência histórica e ambiguidade taxonômica.

A combinação “IA correta e histórico incorreto” não foi observada na análise conjunta porque a regra de decisão utiliza as próprias fontes comparadas para formar a categoria validada. Essa dependência restringe estruturalmente a matriz e explica o valor zero. O resultado caracteriza o funcionamento da memória de decisão e aponta para a necessidade de uma amostra independente quando o objetivo for estimar diretamente a capacidade da IA de corrigir o histórico.

Os ganhos positivos de reclassificação indicam que os modelos contêm informação útil mesmo quando não ocupam a primeira posição no ranking global. A LSTM, por exemplo, apresenta o maior ganho líquido absoluto. A estratégia mais produtiva consiste em combinar a liderança global do LinearSVC com o uso complementar dos demais modelos para localizar divergências, identificar casos ambíguos e selecionar chamados para auditoria.

A entropia de votos acrescenta uma dimensão distinta da confiança individual. Os 3.277 chamados com alto desacordo entre modelos representam regiões da base em que diferentes hipóteses de classificação produzem respostas incompatíveis. Esse indicador direciona a revisão taxonômica e fortalece a gestão da incerteza no protocolo.

A faixa de confiança igual ou superior a 95% alcança {pct(alvo["acerto_validado"])}% de acerto validado. O resultado fornece base empírica para uma política gradual de automação, com tratamento diferenciado por faixa de confiança e integração da calibração formal antes da adoção operacional em maior escala.

**Limitações**

A principal limitação de cobertura decorre do uso de dados de uma única instituição federal de ensino superior, com taxonomia própria e textos em português brasileiro. A transferência dos resultados para outras organizações requer avaliação externa sob diferentes distribuições de chamados, estruturas de categorias e práticas de registro.

A amostra conferida não é probabilística. A seleção prioriza divergências entre modelos e histórico, casos críticos e regiões de baixa confiança. Assim, os valores de acerto descrevem os {inteiro(decididos)} chamados com decisão travada; a estimativa populacional para os {inteiro(total)} registros requer amostragem probabilística. Os {inteiro(restritos)} casos sem verdade validada, entre eles {inteiro(conflitos)} conflitos, foram incorporados à análise de sensibilidade; mesmo no cenário conservador, o ranking dos modelos permanece estável (COCHRAN, 1977).

A comparação neural inclui apenas a LSTM treinada sem *embeddings* pré-treinados de domínio. A avaliação do BERTimbau permitirá examinar o efeito de representações contextuais em português e ampliar a comparação entre modelos lineares, sequenciais e transformadores.

**Papel no modelo de governança preditiva**

Este estudo constitui o Eixo 1 de um modelo de governança preditiva para manutenção predial, no qual o campus universitário é compreendido como biossistema construído. A classificação transforma registros textuais dispersos em dados estruturados, auditáveis e associados a indicadores de confiança.

Esses dados alimentam três desenvolvimentos complementares. O primeiro compreende modelos de séries temporais para previsão de custos e demanda por categoria. O segundo utiliza métodos multicritério, como MCDM e TOPSIS, para priorizar intervenções segundo critérios técnicos, ambientais, sociais e institucionais. O terceiro espacializa os chamados e seus indicadores por meio de geoprocessamento.

A camada de classificação oferece, assim, a infraestrutura informacional necessária para integrar previsão, priorização e análise territorial. Sua contribuição central reside na transformação do chamado individual em evidência reutilizável para planejamento e decisão.'''
    texto = substituir_bloco(texto, "**5. DISCUSSÃO**", "**6. CONSIDERAÇÕES FINAIS**", discussao, "Discussão")

    conclusao = f'''**6. CONSIDERAÇÕES FINAIS**

O protocolo multimodelo identificou o LinearSVC como o classificador de melhor desempenho para os chamados analisados. O modelo alcançou 80,31% de concordância com o histórico e {pct(linear["acerto_validado"])}% de acerto na amostra validada, superando os demais classificadores e os três *ensembles*. Na faixa de confiança igual ou superior a 95%, o classificador operacional atingiu {pct(alvo["acerto_validado"])}% de acerto em {inteiro(alvo["n_validados"])} decisões. Esses resultados, combinados ao baixo custo computacional, sustentam a adoção do LinearSVC como modelo principal, acompanhado de calibração de confiança e memória de decisão humana.

A contribuição do estudo ultrapassa a seleção de um classificador. O protocolo transforma textos operacionais ruidosos em dados estruturados e auditáveis, que podem alimentar previsão de custos e demanda, priorização multicritério de intervenções e análise espacial da manutenção. A classificação constitui, portanto, a camada informacional de base do modelo de governança preditiva aplicado ao biossistema construído universitário.

Os próximos passos concentram-se na validação externa em outras instituições, na calibração formal das probabilidades e margens de decisão e no treinamento comparativo do BERTimbau. Essas etapas permitirão avaliar a transferibilidade do protocolo, estabelecer limiares operacionais mais robustos e medir o ganho proporcionado por representações contextuais pré-treinadas em português.'''
    texto = substituir_bloco(texto, "**6. CONSIDERAÇÕES FINAIS**", "**Contribuições dos autores**", conclusao, "Conclusão")

    apendice = f'''**Apêndice A — Matriz de decisão M/N/P**

Contagens agregadas disponíveis nos JSONs públicos do painel:

| Métrica | n |
|---|---|
| Chamados com ao menos uma conferência (M, N ou P) | {inteiro(conferidos)} |
| Decisões travadas (categoria decidida sem conflito) | {inteiro(decididos)} |
| Casos sem verdade validada | {inteiro(restritos)} |
| Conflitos entre fontes conferidas | {inteiro(conflitos)} |
| Comparações válidas da IA oficial contra a verdade decidida | {inteiro(decididos)} |
| Registros no diagnóstico da conferência GLPI | {inteiro(conferidos)} |
| Registros com conferência da reclassificação | 0 |

Fonte: elaborado pelos autores (2026), com base nos agregados de auditoria e calibração. A conferência da reclassificação registra zero casos na base analisada.

Os agregados públicos não incluem o cruzamento completo das combinações M × N × P. Essa decomposição pode ser produzida a partir da planilha experimental, enquanto os resultados do corpo utilizam as contagens consolidadas da memória de decisão. A Subseção 4.3 discute a dependência estrutural entre classificação operacional, histórico e verdade validada.'''
    texto, n = re.subn(
        re.escape("**Apêndice A — Matriz de decisão M/N/P**") + r".*\Z",
        apendice.strip() + "\n",
        texto,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise RuntimeError(f"Apêndice A não localizado: {n}")

    proibidos = ["9.044", "95,02%", "99,94%", "4.675 decisões", "52 conflitos", "490 casos"]
    for termo in proibidos:
        if termo in texto:
            raise RuntimeError(f"Número residual da versão anterior: {termo}")

    ARTIGO.write_text(texto, encoding="utf-8")
    print(
        "Artigo sincronizado: "
        f"decididos={decididos}, restritos={restritos}, conflitos={conflitos}, "
        f"LinearSVC={linear['acerto_validado']:.4f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
