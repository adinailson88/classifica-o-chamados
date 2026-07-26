#!/usr/bin/env python3
"""Sincroniza as seções numéricas do artigo com os JSONs vivos.

O script não lê texto livre dos chamados. Ele usa somente agregados públicos em
``docs/dados`` e atualiza os blocos do artigo cuja validade depende da última
materialização: Resumo/Abstract, Tabelas 1--4, Discussão, Limitações e
Considerações Finais.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ARTIGO = RAIZ / "04_artigo" / "artigo_classificacao_chamados_v3.md"
PLANO = RAIZ / "PLANO_ARTIGO_CAPITULO.md"
DADOS = RAIZ / "docs" / "dados"

NOMES = {
    "linear_svc": "LinearSVC",
    "sgd": "SGD",
    "regressao_logistica": "Regressão Logística",
    "extra_trees": "Extra Trees",
    "random_forest": "Random Forest",
    "lstm": "LSTM",
    "naive_bayes": "Naive Bayes",
}


def ler_json(nome: str):
    return json.loads((DADOS / nome).read_text(encoding="utf-8"))


def pct(valor: float, casas: int = 2) -> str:
    return f"{valor * 100:.{casas}f}".replace(".", ",") + "%"


def dec(valor: float, casas: int = 4) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def inteiro(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def substituir(texto: str, padrao: str, novo: str, *, flags=0, rotulo: str) -> str:
    saida, n = re.subn(padrao, novo, texto, count=1, flags=flags)
    if n != 1:
        raise RuntimeError(f"Bloco não localizado ou ambíguo: {rotulo} (ocorrências={n})")
    return saida


def por_modelo(lista: list[dict]) -> dict[str, dict]:
    return {item["modelo"]: item for item in lista}


def linha_modelos_validada(avaliacao: dict[str, dict]) -> str:
    ordem = ["linear_svc", "sgd", "regressao_logistica", "extra_trees", "random_forest", "lstm", "naive_bayes"]
    partes = [f"{NOMES[m]} ({pct(avaliacao[m]['acerto_validado'])})" for m in ordem]
    return ", ".join(partes[:-1]) + " e " + partes[-1]


def atualizar_artigo(texto: str) -> str:
    avaliacao_json = ler_json("avaliacao_final.json")
    auditoria = ler_json("auditoria_conferencias.json")
    estatistica = ler_json("estatistica.json")
    calibracao = ler_json("calibracao.json")
    sensibilidade_json = ler_json("sensibilidade_vies_validacao.json")
    reclass = ler_json("reclass_resumo.json")

    avaliacao = por_modelo(avaliacao_json["por_modelo"])
    historico = por_modelo(estatistica["acuracia_bootstrap"])
    kappa = por_modelo(estatistica["kappa_cohen_historico"])
    sensibilidade = por_modelo(sensibilidade_json["por_modelo"])

    cont = auditoria["contagens"]
    total = int(estatistica["n_linhas_comuns"])
    conferidos = int(cont["total_com_alguma_conferencia"])
    decididos = int(cont["decisoes_travadas"])
    restritos = int(cont["restritos"])
    conflitos = int(cont["conflitos"])
    cobertura = conferidos / total
    cobertura_decidida = decididos / total
    sem_decisao = total - decididos

    lin = avaliacao["linear_svc"]
    lstm = avaliacao["lstm"]
    lin_hist = historico["linear_svc"]
    lstm_hist = historico["lstm"]

    resumo = f"""**RESUMO**

A classificação automática de chamados de manutenção predial constitui
recurso estratégico para a qualificação da triagem operacional e para a
ampliação da governança baseada em evidências em instituições públicas.
Contudo, em bases históricas de sistemas informatizados de gestão de
chamados, a categoria originalmente registrada não deve ser tratada como
verdade absoluta, uma vez que pode refletir decisões operacionais
ruidosas, taxonomias sobrepostas, registros incompletos e interpretações
heterogêneas entre equipes de atendimento. O presente artigo propõe um
protocolo multimodelo para classificação de chamados reais de manutenção
predial universitária em português brasileiro, extraídos do sistema GLPI
da Universidade Federal do Sul da Bahia. O experimento utiliza {inteiro(total)}
chamados não vazios, organizados em 55 categorias históricas, e compara
classificadores clássicos baseados em TF-IDF (Naive Bayes, Regressão
Logística, LinearSVC, SGD, Random Forest e Extra Trees) e rede neural LSTM
bidirecional. O BERTimbau permanece como extensão planejada, sem treino
concluído ou métrica própria nesta consolidação. O diferencial metodológico
reside na distinção entre concordância com o histórico administrativo e
acerto validado por revisão humana, tratando a categoria histórica como
referência preliminar imperfeita. A avaliação humana cobre {inteiro(conferidos)}
chamados, com {inteiro(decididos)} decisões travadas e {inteiro(conflitos)}
conflitos explicitamente excluídos da verdade validada. Como a seleção não
é aleatória e prioriza divergências e casos críticos, esses resultados não
estimam o desempenho da base completa (COCHRAN, 1977). O LinearSVC lidera
tanto a concordância com o histórico ({pct(lin_hist['acuracia'])}, IC95%:
{pct(lin_hist['ic95_min'])}--{pct(lin_hist['ic95_max'])}) quanto o acerto
validado ({pct(lin['acerto_validado'])}, IC95%: {pct(lin['ic95'][0])}--
{pct(lin['ic95'][1])}), enquanto o LSTM apresenta concordância de
{pct(lstm_hist['acuracia'])} e acerto validado de {pct(lstm['acerto_validado'])}.
A normalidade da concordância por turno foi rejeitada para todos os modelos,
justificando testes não paramétricos. O custo computacional é incorporado
como dimensão de avaliação, evidenciando que modelos lineares podem oferecer
melhor relação entre desempenho e viabilidade operacional em cenários de
texto curto, ruidoso e desbalanceado.

**Palavras-chave:** manutenção predial; classificação de chamados;
processamento de linguagem natural; rótulos ruidosos; validação humana;
governança preditiva."""
    texto = substituir(texto, r"\*\*RESUMO\*\*.*?\*\*Palavras-chave:\*\*.*?governança preditiva\.", resumo, flags=re.S, rotulo="Resumo")

    abstract = f"""**ABSTRACT**

*Automatic classification of building maintenance work orders is a strategic
resource for operational triage and evidence-based governance in public
institutions. Historical labels, however, may reflect noisy decisions,
overlapping taxonomies, incomplete records and heterogeneous interpretations.
This paper proposes a multi-model protocol for {inteiro(total).replace('.', ',')}
real university building-maintenance work orders in Brazilian Portuguese,
organized into 55 historical categories. The comparison includes TF-IDF-based
classifiers and a bidirectional LSTM; BERTimbau remains a planned extension
without completed fine-tuning. The methodological contribution is the explicit
distinction between agreement with administrative history and accuracy against
human-validated decisions. Human review covers {inteiro(conferidos).replace('.', ',')}
records, with {inteiro(decididos).replace('.', ',')} locked decisions and
{inteiro(conflitos).replace('.', ',')} conflicts excluded from the validated
ground truth. Because the reviewed sample is non-random and prioritizes
disagreements and critical cases, the results do not estimate performance over
the complete database. LinearSVC leads both historical agreement
({pct(lin_hist['acuracia']).replace(',', '.')}, 95% CI:
{pct(lin_hist['ic95_min']).replace(',', '.')}--{pct(lin_hist['ic95_max']).replace(',', '.')})
and human-validated accuracy ({pct(lin['acerto_validado']).replace(',', '.')},
95% CI: {pct(lin['ic95'][0]).replace(',', '.')}--{pct(lin['ic95'][1]).replace(',', '.')}),
whereas LSTM achieves {pct(lstm_hist['acuracia']).replace(',', '.')} historical
agreement and {pct(lstm['acerto_validado']).replace(',', '.')} validated accuracy.
Normality is rejected for all models, supporting non-parametric comparisons.
Computational cost is included as an evaluation dimension, indicating that
linear models provide a favorable balance between performance and operational
feasibility for short, noisy and imbalanced technical text.*

***Keywords:** building maintenance; work-order classification; natural
language processing; noisy labels; human validation; predictive governance.*"""
    texto = substituir(texto, r"\*\*ABSTRACT\*\*.*?predictive\s+governance\.\*", abstract, flags=re.S, rotulo="Abstract")

    abertura_resultados = f"""Esta seção apresenta dois conjuntos de resultados, deliberadamente
segregados: a concordância com a categoria histórica (Subseção 4.1), que
trata o registro do GLPI como referência preliminar, e o desempenho validado
por conferência humana (Subseções 4.2 e 4.3). A base elegível contém
{inteiro(total)} chamados; a conferência humana cobre {inteiro(conferidos)}
chamados ({pct(cobertura, 1)} da base), dos quais {inteiro(decididos)} têm
decisão travada ({pct(cobertura_decidida, 1)} da base). Os {inteiro(restritos)}
casos restantes não possuem verdade validada; esse conjunto inclui
{inteiro(conflitos)} conflitos entre fontes conferidas.

Três achados resumem esta seção. Primeiro, os classificadores lineares,
liderados pelo LinearSVC, superam os ensembles de árvores e a rede neural
LSTM em concordância e acerto validado, com vantagem adicional de custo
computacional. Segundo, a validação humana confirma ruído real no rótulo
histórico, justificando a conferência dupla. Terceiro, a faixa de confiança
igual ou superior a 95% supera a meta de 95% de acerto validado na amostra
conferida, mas a confiança permanece bruta e a seleção da amostra não é
probabilística."""
    texto = substituir(texto, r"(?<=\*\*4\. RESULTADOS\*\*\n\n).*?(?=\n\n\*\*4\.1)", abertura_resultados, flags=re.S, rotulo="abertura dos Resultados")

    ordem_hist = ["linear_svc", "extra_trees", "random_forest", "sgd", "regressao_logistica", "naive_bayes", "lstm"]
    linhas_t1 = []
    for m in ordem_hist:
        h = historico[m]
        linhas_t1.append(f"| {NOMES[m]}{' (out-of-fold)' if m == 'lstm' else ''} | {dec(h['acuracia'])} | {dec(h['ic95_min'])} -- {dec(h['ic95_max'])} | {dec(kappa[m]['kappa'])} |")
    secao_41 = (
        f"A comparação contra a categoria histórica, sobre a base completa (n = {inteiro(total)}), "
        f"mantém o LinearSVC na liderança, com acurácia de {dec(lin_hist['acuracia'])} "
        f"(IC95%: {dec(lin_hist['ic95_min'])}--{dec(lin_hist['ic95_max'])}), seguido por "
        + ", ".join(f"{NOMES[m]} ({dec(historico[m]['acuracia'])})" for m in ordem_hist[1:-1])
        + f" e LSTM ({dec(lstm_hist['acuracia'])}). O teste de Cochran Q confirma diferença global "
        f"entre os sete modelos (Q = {estatistica['cochran_q']['Q']:.3f}".replace(".", ",")
        + "; p < 0,001). O BERTimbau permanece excluído por não possuir treino concluído."
        + "\n\n**Tabela 1** Concordância com a categoria histórica, base completa "
        f"(n = {inteiro(total)})\n\n| Modelo | Acurácia | IC95% bootstrap | Kappa vs. histórico |\n|---|---|---|---|\n"
        + "\n".join(linhas_t1)
        + "\n\nFonte: elaborado pelos autores (2026), com base nos agregados vigentes da comparação multimodelo."
    )
    texto = substituir(texto, r"(?<=\*\*4\.1 Concordância com o histórico \(base completa\)\*\*\n\n).*?(?=\n\nA concordância com o histórico)", secao_41, flags=re.S, rotulo="Subseção 4.1 e Tabela 1")

    segundo = avaliacao_json["melhor_vs_segundo"]
    ensembles = avaliacao_json["ensembles"]
    resumo_ens = ", ".join(f"{item['metodo'].replace('_', ' ')} ({dec(item['acerto_validado'])})" for item in ensembles)
    secao_42 = f"""A avaliação contra a verdade validada pela memória de decisão M/N/P
(n = {inteiro(avaliacao_json['n_avaliado'])}) mantém a liderança do LinearSVC,
com acerto validado de {dec(lin['acerto_validado'])} (IC95%:
{dec(lin['ic95'][0])}--{dec(lin['ic95'][1])}). A ordenação completa é
{linha_modelos_validada(avaliacao)}. A diferença entre o primeiro e o segundo
colocado é de {pct(segundo['delta'])}, com McNemar p =
{segundo['p_mcnemar']:.3e}. Os ensembles avaliados foram {resumo_ens}; nenhum
supera o LinearSVC isolado. A recomendação permanece utilizar o LinearSVC com
calibração, sem combinar modelos nesta consolidação."""
    texto = substituir(texto, r"(?<=\*\*4\.2 Ranking validado por conferência humana\*\*\n\n).*?(?=\n\n\*\*Viés estrutural)", secao_42, flags=re.S, rotulo="abertura 4.2")

    linhas_t2 = []
    for m in ["linear_svc", "sgd", "regressao_logistica", "extra_trees", "random_forest", "lstm", "naive_bayes"]:
        a = avaliacao[m]
        s = sensibilidade[m]
        linhas_t2.append(f"| {NOMES[m]} | {dec(a['acerto_validado'])} | {dec(a['ic95'][0])} -- {dec(a['ic95'][1])} | {dec(s['limite_inferior'])} |")
    amplitudes = [item["amplitude"] for item in sensibilidade.values()]
    tabela_t2 = "\n".join(linhas_t2)
    vies_tabela = f"""**Viés estrutural da seleção da amostra validada**: a verdade validada só
existe quando ao menos uma fonte conferida é confirmada como correta. Dos
{inteiro(conferidos)} chamados com alguma conferência, {inteiro(restritos)}
não possuem categoria de referência, incluindo {inteiro(conflitos)} conflitos.
Por isso, o acerto validado é apresentado como limite superior, acompanhado de
um limite inferior conservador que inclui todos esses casos no denominador como
erros. A amplitude varia de {pct(min(amplitudes))} a {pct(max(amplitudes))}, sem
alterar o ranking relativo dos sete modelos.

**Tabela 2** Acerto validado contra a verdade decidida M/N/P
(n = {inteiro(decididos)}) e intervalo de sensibilidade

| Modelo | Acerto validado (limite superior) | IC95% | Limite inferior (pior caso) |
|---|---|---|---|
{tabela_t2}

Fonte: elaborado pelos autores (2026). O limite inferior é uma análise de pior
caso; os conflitos e demais linhas sem verdade validada não recebem crédito para
nenhum modelo."""
    texto = substituir(texto, r"\*\*Viés estrutural da seleção da amostra validada\*\*:.*?Fonte: elaborado pelos autores \(2026\).*?(?=\n\nA rematerialização completa)", vies_tabela, flags=re.S, rotulo="viés e Tabela 2")

    matriz = calibracao["validacao_humana"]["matriz_ia_x_glpi"]
    n_matriz = sum(matriz.values())
    hist_ok = matriz["ia_ok_glpi_ok"] + matriz["ia_erro_glpi_ok"]
    ia_ok = matriz["ia_ok_glpi_ok"] + matriz["ia_ok_glpi_erro"]
    secao_43 = f"""A classificação oficial e a categoria histórica foram comparadas contra a
mesma verdade validada em {inteiro(n_matriz)} decisões. O histórico coincide
com a decisão em {pct(hist_ok / n_matriz)}, enquanto a IA oficial coincide em
{pct(ia_ok / n_matriz)}. A matriz contém {inteiro(matriz['ia_ok_glpi_ok'])}
casos em que ambos acertam, {inteiro(matriz['ia_erro_glpi_erro'])} em que ambos
divergem da decisão, {inteiro(matriz['ia_erro_glpi_ok'])} em que o histórico
acerta e a IA erra e {inteiro(matriz['ia_ok_glpi_erro'])} em que a IA corrige o
histórico.

**Tabela 4** Matriz de confusão IA × histórico contra a verdade decidida
(M/N/P) (n = {inteiro(n_matriz)})

| | Histórico correto | Histórico incorreto |
|---|---|---|
| **IA correta** | {inteiro(matriz['ia_ok_glpi_ok'])} | {inteiro(matriz['ia_ok_glpi_erro'])} |
| **IA incorreta** | {inteiro(matriz['ia_erro_glpi_ok'])} | {inteiro(matriz['ia_erro_glpi_erro'])} |

Fonte: elaborado pelos autores (2026), usando a mesma verdade decidida da
Subseção 4.2."""
    texto = substituir(texto, r"(?<=\*\*4\.3 A classificação oficial frente ao histórico: matriz de confusão\nvalidada\*\*\n\n).*?(?=\n\n\*\*4\.4)", secao_43, flags=re.S, rotulo="Subseção 4.3 e Tabela 4")

    faixas = calibracao["por_faixa"]
    linhas_t3 = []
    for f in faixas:
        av = "--" if f["acerto_validado"] is None else pct(f["acerto_validado"])
        linhas_t3.append(f"| {f['faixa'].replace('>=', '>= ')} | {inteiro(f['n'])} | {pct(f['concordancia_historico'])} | {inteiro(f['n_validados'])} | {av} |")
    alvo = calibracao["faixa_alvo_95"]
    tabela_t3 = "\n".join(linhas_t3)
    secao_44 = f"""A calibração bruta da Etapa 1 oficial apresenta ECE histórico de
{dec(calibracao['ece_historico'])}. Na faixa igual ou superior a 95% de
confiança (n = {inteiro(alvo['n'])}), a concordância com o histórico é de
{pct(alvo['concordancia_historico'])} e o acerto validado alcança
{pct(alvo['acerto_validado'])} sobre {inteiro(alvo['n_validados'])} decisões.
A confiança permanece bruta, sem Platt, isotônica ou *temperature scaling*;
portanto, a meta deve ser interpretada como diagnóstico da amostra conferida.

**Tabela 3** Acerto validado por faixa de confiança bruta, executor oficial

| Faixa | n total | Concord. histórico | n validados | Acerto validado |
|---|---|---|---|---|
{tabela_t3}

Fonte: elaborado pelos autores (2026). O snapshot foi deduplicado por
`linha_planilha`, mantendo a ocorrência mais recente. A amostra de conferência
não é probabilística."""
    texto = substituir(texto, r"(?<=\*\*4\.4 Confiança, calibração e faixas de decisão\*\*\n\n).*?(?=\n\n\*\*4\.5)", secao_44, flags=re.S, rotulo="Subseção 4.4 e Tabela 3")

    # Correções editoriais remanescentes.
    texto = texto.replace("Fonte: elaborado pelos autores (2026), gerado a partir da descrição desta\nsubseção (`04_artigo/figuras/fig1_pipeline_governanca.png`).", "Fonte: elaborado pelos autores (2026), a partir do fluxo metodológico descrito nesta subseção.")
    texto = re.sub(r"Os ensembles serão reavaliados somente após.*?BERTimbau\.", "Os três ensembles avaliados não superam o LinearSVC isolado; a recomendação é manter o classificador linear com calibração.", texto, flags=re.S)

    resultados_reclass = {x["modelo"]: x for x in reclass.get("por_modelo", [])}
    positivos = [NOMES[m] for m, x in resultados_reclass.items() if m in NOMES and x.get("ganho_liquido", 0) > 0]
    negativos = [NOMES[m] for m, x in resultados_reclass.items() if m in NOMES and x.get("ganho_liquido", 0) < 0]
    frase_sinal = (
        f"Todos os modelos apresentam ganho líquido positivo ({', '.join(positivos)})."
        if positivos and not negativos else
        f"Apresentam ganho positivo: {', '.join(positivos)}; ganho negativo: {', '.join(negativos)}."
    )
    texto = substituir(texto, r"O resultado da reclassificação \(Subseção 4\.5\).*?(?=\n\nA camada de entropia)", "O resultado da reclassificação (Subseção 4.5) deve ser interpretado por modelo e por consolidação. " + frase_sinal + " O ganho combina comparações contra verdade validada e contra histórico; por isso, não autoriza reclassificação indiscriminada nem constitui veredito permanente sobre um classificador.", flags=re.S, rotulo="parágrafo de reclassificação na Discussão")

    texto = texto.replace("(categoria, criticidade e confiança calibrada)", "(categoria, criticidade, confiança bruta e indicadores de calibração)")
    texto = texto.replace("discutida em detalhe nas Limitações", "discutida em detalhe na Subseção 4.9")

    discussao_inicial = f"""A comparação entre concordância histórica e desempenho validado mantém o
LinearSVC na liderança: {pct(lin['acerto_validado'])} de acerto validado na
amostra decidida e {pct(lin_hist['acuracia'])} de concordância com o histórico.
A conferência humana não é aleatória e prioriza divergências e casos críticos;
assim, os resultados descrevem a amostra conferida, não a população completa
(COCHRAN, 1977).

A regra de decisão exclui do denominador os {inteiro(restritos)} chamados sem
verdade validada ({pct(restritos / conferidos)} dos conferidos), conjunto que
inclui {inteiro(conflitos)} conflitos. A análise de sensibilidade mantém o
ranking dos sete modelos, mas mostra que o valor pontual de acerto validado é
um limite superior e não deve ser comparado isoladamente a benchmarks externos."""
    texto = substituir(texto, r"(?<=\*\*5\. DISCUSSÃO\*\*\n\n).*?(?=\n\nAinda assim)", discussao_inicial, flags=re.S, rotulo="abertura da Discussão")

    meta_texto = f"""A faixa igual ou superior a 95% de confiança da Etapa 1 oficial alcança
{pct(alvo['acerto_validado'])} de acerto validado sobre
{inteiro(alvo['n_validados'])} decisões. O resultado supera a meta nominal de
95% nesta amostra, mas não encerra a validação: a confiança é bruta e
{inteiro(sem_decisao)} chamados ({pct(sem_decisao / total, 1)} da base) ainda
não possuem decisão travada."""
    texto = substituir(texto, r"A meta de confiança calibrada.*?(?=\n\n\*\*Limitações\*\*)", meta_texto, flags=re.S, rotulo="meta na Discussão")

    texto = re.sub(r"\(4,6% dos\nchamados conferidos\)", f"({pct(restritos / conferidos)} dos chamados conferidos, incluindo {inteiro(conflitos)} conflitos)", texto)

    conclusao = f"""O presente capítulo consolida um protocolo multimodelo de classificação de
chamados de manutenção predial universitária em português brasileiro, com sete
modelos comparáveis, memória de decisão por validação humana e análise de
incerteza informacional. O BERTimbau permanece como extensão planejada, sem
ajuste fino concluído ou métricas próprias. A contribuição central é produzir
dado estruturado e auditável para a governança preditiva, distinguindo
concordância com o histórico de acerto contra decisões humanas.

Na amostra parcial e não probabilística de {inteiro(decididos)} decisões
travadas, {linha_modelos_validada(avaliacao)}. Nenhum dos três ensembles supera
o LinearSVC isolado; a recomendação é utilizar o LinearSVC com calibração. Os
{inteiro(conflitos)} conflitos permanecem fora da verdade validada até revisão
humana específica.

A faixa de confiança igual ou superior a 95% da classificação oficial apresenta
{pct(alvo['acerto_validado'])} de acerto validado. O valor supera a meta nominal
na amostra conferida, mas a confiança ainda é bruta e {inteiro(sem_decisao)}
chamados não possuem decisão travada; portanto, o resultado não autoriza
liberação automática irrestrita em produção."""
    texto = substituir(texto, r"(?<=\*\*6\. CONSIDERAÇÕES FINAIS\*\*\n\n).*?(?=\n\nA curva real)", conclusao, flags=re.S, rotulo="abertura das Considerações Finais")
    texto = texto.replace("a conclusão da conferência\nhumana pendente (31,7% da base ainda sem decisão travada)", f"a conclusão da conferência humana pendente ({pct(sem_decisao / total, 1)} da base ainda sem decisão travada)")

    return texto


def atualizar_plano(texto: str) -> str:
    estado = """**Onde está**: reformulação editorial já incorporada à `main` pelas PRs
#73 e #74. A correção de sincronização numérica está em execução na branch
`agent/corrigir-sincronizacao-artigo`.

**O que foi feito nesta rodada**: identificada e corrigida a duplicação do
`SNAPSHOT_ETAPA_1` na calibração, mantendo a última ocorrência por
`linha_planilha`; criado sincronizador reproduzível para atualizar
Resumo/Abstract, Tabelas 1--4, Discussão, Limitações e Considerações Finais a
partir dos JSONs vigentes; corrigidas contradições editoriais remanescentes e a
exposição de caminho interno na fonte da Figura 1.

**Próximo passo**: executar o workflow corretivo com credencial da planilha,
validar a suíte completa, regenerar Figuras 2 e 3 e o PDF, e revisar visualmente
o artefato antes do merge da PR corretiva."""
    return substituir(texto, r"\*\*Onde está\*\*:.*?\*\*Próximo passo\*\*:.*?(?=\n\n---)", estado, flags=re.S, rotulo="Estado desta rodada no plano")


def main() -> int:
    artigo = ARTIGO.read_text(encoding="utf-8")
    atualizado = atualizar_artigo(artigo)
    ARTIGO.write_text(atualizado, encoding="utf-8")

    plano = PLANO.read_text(encoding="utf-8")
    PLANO.write_text(atualizar_plano(plano), encoding="utf-8")

    print(f"artigo sincronizado: {ARTIGO}")
    print(f"plano atualizado: {PLANO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
