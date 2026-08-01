#!/usr/bin/env python3
"""Sincroniza os numeros do artigo com os JSONs vigentes em docs/dados.

Escopo ESTRITO, por decisao do pesquisador: so DADOS e NUMEROS mudam. Nao
altera a estrutura do artigo, nao reescreve secoes e nao narra rodadas
anteriores, auditorias ou versoes descartadas -- o artigo nao e relatorio de
processo.

A unica excecao e a descricao da REGRA de validacao humana: a partir de
2026-08-01 a verdade passou a ser derivada apenas da conferencia do GLPI
(coluna M) e da categoria manual (coluna Q). Descrever a regra antiga tornaria
a secao de metodo factualmente errada, entao o texto da regra acompanha o dado.

Cada substituicao declara o trecho esperado e a contagem. Se um trecho nao for
encontrado, ou aparecer numero de vezes diferente do declarado, o script ABORTA
sem escrever -- assim uma mudanca de redacao nunca provoca substituicao
silenciosa ou parcial.

Sem --aplicar: dry-run (mostra cada troca, nao grava).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ARTIGO = RAIZ / "04_artigo" / "artigo_classificacao_chamados_v3.md"
DADOS = RAIZ / "docs" / "dados"

ROTULOS = {
    "linear_svc": "LinearSVC",
    "extra_trees": "Extra Trees",
    "random_forest": "Random Forest",
    "sgd": "SGD",
    "regressao_logistica": "Regressão Logística",
    "naive_bayes": "Naive Bayes",
    "lstm": "LSTM",
    "transformer_ft": "BERTimbau",
}


def num(v: float, casas: int = 4) -> str:
    return f"{v:.{casas}f}".replace(".", ",")


def mil(v: int) -> str:
    return f"{v:,}".replace(",", ".")


def carregar(nome: str):
    return json.loads((DADOS / nome).read_text(encoding="utf-8"))


def tabela1(est: dict) -> str:
    """Mantem as tres colunas originais (Modelo, Acuracia, IC95%). O IC vem do
    bootstrap em estatistica.json -- e concordancia com a categoria HISTORICA,
    entao nao depende da verdade validada."""
    linhas = sorted(est["acuracia_bootstrap"], key=lambda x: -x["acuracia"])
    corpo = "\n".join(
        f"| {ROTULOS.get(x['modelo'], x['modelo'])}{' (out-of-fold)' if x['modelo'] == 'lstm' else ''} "
        f"| {num(x['acuracia'])} | {num(x['ic95_min'])} -- {num(x['ic95_max'])} |"
        for x in linhas)
    return "| Modelo | Acurácia | IC95% |\n|---|---|---|\n" + corpo


def limite_inferior(x: dict, decididos: int, restritos: int) -> float:
    """Cenario conservador: os restritos entram no denominador como erro de
    todos os modelos (mesma definicao da Tabela 2 original)."""
    return decididos * x["acerto_validado"] / (decididos + restritos)


def tabela_validada(af: dict, decididos: int, restritos: int) -> str:
    corpo = "\n".join(
        f"| {ROTULOS.get(x['modelo'], x['modelo'])} | {num(x['acerto_validado'])} "
        f"| {num(x['ic95'][0])} -- {num(x['ic95'][1])} "
        f"| {num(limite_inferior(x, decididos, restritos))} |"
        for x in af["por_modelo"])
    return ("| Modelo | Acerto validado | IC95% | Limite inferior |\n"
            "|---|---|---|---|\n" + corpo)


def tabela_holdout(ho: dict) -> str:
    ms = sorted(ho["modelos"], key=lambda x: -x["acerto_validado"])
    corpo = "\n".join(
        f"| {ROTULOS.get(x['modelo'], x['modelo'])} | {num(x['concordancia_historico'])} "
        f"| {num(x['acerto_validado'])} "
        f"| {num(x['ic95_validado'][0])} -- {num(x['ic95_validado'][1])} |"
        for x in ms)
    return ("| Modelo | Concordância histórica | Acerto validado | IC95% validado |\n"
            "|---|---|---|---|\n" + corpo)


def construir_trocas(texto: str) -> list[tuple[str, str, int, str]]:
    """(de, para, ocorrencias_esperadas, rotulo)."""
    af = carregar("avaliacao_final.json")
    ho = carregar("avaliacao_bertimbau_holdout.json")
    est = carregar("estatistica.json")
    conf = af["conferencias"]

    base = 14094
    decididos = conf["decididos"]
    conferidos = conf["com_conferencia"]
    restritos = conf["restritos"]
    n_val_holdout = ho["protocolo"]["n_validado_no_lote"]

    t: list[tuple[str, str, int, str]] = []

    # --- Tabelas (antes dos numeros soltos, senao a troca de '13.965' mexeria
    # no cabecalho da Tabela 1 e o trecho esperado deixaria de casar). ---
    t.append((
        "**Tabela 1** Concordância com a categoria histórica por modelo (n = 13.965).\n\n"
        "| Modelo | Acurácia | IC95% |\n|---|---|---|\n"
        "| LinearSVC | 0,8031 | 0,7963 -- 0,8097 |\n"
        "| Extra Trees | 0,7894 | 0,7825 -- 0,7961 |\n"
        "| Random Forest | 0,7816 | 0,7749 -- 0,7881 |\n"
        "| SGD | 0,7767 | 0,7700 -- 0,7835 |\n"
        "| Regressão Logística | 0,7682 | 0,7613 -- 0,7751 |\n"
        "| Naive Bayes | 0,6997 | 0,6923 -- 0,7071 |\n"
        "| LSTM (out-of-fold) | 0,6718 | 0,6637 -- 0,6796 |",
        f"**Tabela 1** Concordância com a categoria histórica por modelo (n = {mil(base)}).\n\n"
        + tabela1(est),
        1, "Tabela 1"))

    t.append((
        "| Modelo | Concordância histórica | Acerto validado | IC95% validado |\n"
        "|---|---|---|---|\n"
        "| LinearSVC | 0,6560 | 0,7856 | 0,7527 -- 0,8185 |\n"
        "| BERTimbau | 0,6520 | 0,7746 | 0,7402 -- 0,8075 |\n"
        "| Regressão Logística | 0,6280 | 0,7653 | 0,7324 -- 0,7981 |\n"
        "| SGD | 0,6250 | 0,7621 | 0,7293 -- 0,7950 |\n"
        "| Extra Trees | 0,6120 | 0,7167 | 0,6808 -- 0,7527 |\n"
        "| Random Forest | 0,5950 | 0,6948 | 0,6604 -- 0,7308 |\n"
        "| LSTM | 0,5190 | 0,6526 | 0,6166 -- 0,6886 |\n"
        "| Naive Bayes | 0,5390 | 0,6354 | 0,5978 -- 0,6714 |",
        tabela_holdout(ho), 1, "Tabela do holdout BERTimbau"))

    # --- Regra da validacao humana (metodo). ---
    t.append((
        "A validação humana pode confirmar a categoria histórica, aceitar uma\n"
        "classificação automática, aceitar uma reclassificação ou definir\n"
        "manualmente uma categoria distinta.",
        "A validação humana confirma ou rejeita a categoria histórica do chamado.\n"
        "Quando a categoria histórica é confirmada, ela constitui a referência;\n"
        "quando é rejeitada, o avaliador registra manualmente a categoria correta.",
        1, "regra da validação humana"))

    t.append((
        "Dos\n13.965 chamados, 9.534 receberam ao menos uma conferência; 8.895 chegaram\n"
        "a uma categoria decidida e 639 permaneceram restritos, incluindo 201\n"
        "conflitos entre fontes marcadas como corretas.",
        f"Dos\n{mil(base)} chamados, {mil(conferidos)} receberam conferência; {mil(decididos)} chegaram\n"
        f"a uma categoria decidida e {restritos} permaneceram restritos, por\n"
        "rejeição da categoria histórica sem categoria manual registrada.",
        1, "contagem de conferências (método)"))

    # --- Numeros da secao de resultados. ---
    t.append((
        f"conferência humana cobre 9.534 chamados (68,3% da base), dos quais 8.895\n"
        "têm decisão validada (63,7% da base) e 639 permanecem restritos.",
        f"conferência humana cobre {mil(conferidos)} chamados "
        f"({num(100*conferidos/base, 1)}% da base), dos quais {mil(decididos)}\n"
        f"têm decisão validada ({num(100*decididos/base, 1)}% da base) e {restritos} permanecem restritos.",
        1, "cobertura da conferência"))

    t.append((
        "Dos 9.534 chamados conferidos, 639 (6,7%) permanecem sem",
        f"Dos {mil(conferidos)} chamados conferidos, {restritos} "
        f"({num(100*restritos/conferidos, 1)}%) permanecem sem",
        1, "restritos sobre conferidos (4.2)"))

    t.append((
        "O mecanismo estrutural aparece nos 639 chamados restritos, equivalentes a\n"
        "6,7% dos 9.534 conferidos.",
        f"O mecanismo estrutural aparece nos {restritos} chamados restritos, equivalentes a\n"
        f"{num(100*restritos/conferidos, 1)}% dos {mil(conferidos)} conferidos.",
        1, "restritos (discussão)"))

    t.append((
        "Dos 9.534 chamados conferidos, 639 permanecem sem categoria",
        f"Dos {mil(conferidos)} chamados conferidos, {restritos} permanecem sem categoria",
        1, "restritos (limitações)"))

    # --- 639 no sentido de LOTE held-out do BERTimbau (sentido diferente!). ---
    t.append((
        "O lote contém 639 chamados com categoria de referência estabelecida por",
        f"O lote contém {n_val_holdout} chamados com categoria de referência estabelecida por",
        1, "lote held-out (n validado)"))
    t.append((
        "Entre os registros do lote, 639 possuem categoria de referência estabelecida",
        f"Entre os registros do lote, {n_val_holdout} possuem categoria de referência estabelecida",
        1, "lote held-out (4.3)"))
    t.append((
        "n = 639 com decisão validada).",
        f"n = {n_val_holdout} com decisão validada).",
        1, "lote held-out (legenda)"))
    t.append((
        "*holdout* comum de 1.000 chamados, dos quais 639 possuem decisão humana.",
        f"*holdout* comum de 1.000 chamados, dos quais {n_val_holdout} possuem decisão humana.",
        1, "lote held-out (limitações)"))

    # --- Restantes de 8.895 e 639 no denominador geral. ---
    t.append((
        "validado, apurado sobre 8.895 decisões, descreve apenas a amostra",
        f"validado, apurado sobre {mil(decididos)} decisões, descreve apenas a amostra",
        1, "resumo (pt)"))
    t.append((
        "639 casos sem categoria decidida permanecem fora do denominador. Na",
        f"{restritos} casos sem categoria decidida permanecem fora do denominador. Na",
        1, "resumo (pt) restritos"))
    t.append((
        "639 cases without a decided category remain outside the denominator. In",
        f"{restritos} cases without a decided category remain outside the denominator. In",
        1, "abstract (en)"))

    t.append((
        "A avaliação contra a categoria de referência validada utiliza 8.895 chamados",
        f"A avaliação contra a categoria de referência validada utiliza {mil(decididos)} chamados",
        1, "denominador da avaliação"))
    t.append((
        "denominador de 8.895 decisões.",
        f"denominador de {mil(decididos)} decisões.",
        1, "denominador (4.2)"))
    t.append((
        "sensibilidade ao viés de seleção (n = 8.895). O limite inferior inclui os\n639 casos restritos",
        f"sensibilidade ao viés de seleção (n = {mil(decididos)}). O limite inferior inclui os\n{restritos} casos restritos",
        1, "análise de sensibilidade"))
    t.append((
        "A análise de sensibilidade incorpora os 639 restritos ao denominador como",
        f"A análise de sensibilidade incorpora os {restritos} restritos ao denominador como",
        1, "sensibilidade (texto)"))
    t.append((
        "entram uma única vez e 8.895 deles têm conferência humana.",
        f"entram uma única vez e {mil(decididos)} deles têm conferência humana.",
        1, "unidade de análise"))
    t.append((
        "chamado, 13.965 no total, 8.895 com conferência humana.",
        f"chamado, {mil(base)} no total, {mil(decididos)} com conferência humana.",
        1, "unidade de análise (legenda)"))

    # --- Particao de treino. ---
    t.append((
        "treino, já que dos 13.965 chamados cerca de 11.172 compõem cada partição",
        f"treino, já que dos {mil(base)} chamados cerca de {mil(round(base*0.8))} compõem cada partição",
        1, "partição k-fold"))

    # --- Conclusao (5.x): numeros do LinearSVC e do BERTimbau. ---
    melhor = af["por_modelo"][0]
    assert melhor["modelo"] == "linear_svc", (
        "A conclusao nomeia o LinearSVC; se outro modelo assumir a lideranca, "
        "o texto precisa ser reescrito por uma pessoa, nao por substituicao.")
    conservador = 100 * decididos * melhor["acerto_validado"] / (decididos + restritos)
    ho_bert = next(m for m in ho["modelos"] if m["modelo"] == "transformer_ft")
    ho_svc = next(m for m in ho["modelos"] if m["modelo"] == "linear_svc")

    t.append((
        "Na avaliação integral dos 8.895 chamados com categoria de referência\n"
        "estabelecida por validação humana, o LinearSVC\n"
        "alcança 95,27% de acerto validado (IC95%: 94,82%--95,69%) e nenhum dos\n"
        "três *ensembles* o supera. A análise conservadora que inclui 639 casos\n"
        "restritos reduz o limite do LinearSVC para 88,88%, sem modificar a\n"
        "ordenação dos modelos.",
        f"Na avaliação integral dos {mil(decididos)} chamados com categoria de referência\n"
        "estabelecida por validação humana, o LinearSVC\n"
        f"alcança {num(100*melhor['acerto_validado'], 2)}% de acerto validado "
        f"(IC95%: {num(100*melhor['ic95'][0], 2)}%--{num(100*melhor['ic95'][1], 2)}%) e nenhum dos\n"
        f"três *ensembles* o supera. A análise conservadora que inclui {restritos} casos\n"
        f"restritos reduz o limite do LinearSVC para {num(conservador, 2)}%, sem modificar a\n"
        "ordenação dos modelos.",
        1, "conclusão: LinearSVC"))

    t.append((
        "1.000 chamados, com 639 decisões validadas, alcança 77,46%, contra 78,56%\n"
        "do LinearSVC, sem diferença significativa.",
        f"1.000 chamados, com {n_val_holdout} decisões validadas, alcança "
        f"{num(100*ho_bert['acerto_validado'], 2)}%, contra {num(100*ho_svc['acerto_validado'], 2)}%\n"
        "do LinearSVC, sem diferença significativa.",
        1, "conclusão: BERTimbau no holdout"))

    # --- Repeticoes narrativas dos mesmos valores (resumo, 4.1, discussao). ---
    ordem = sorted(est["acuracia_bootstrap"], key=lambda x: -x["acuracia"])
    lider = ordem[0]
    demais = ", ".join(
        f"{ROTULOS[x['modelo']]} ({num(x['acuracia'])})" for x in ordem[1:])
    cq = est["cochran_q"]
    p_bert = ho["bertimbau"]["p_mcnemar"]

    t.append((
        "(80,31%) e o acerto validado (95,27%). No *holdout* comum, o LinearSVC\n"
        "alcança 78,56% e o BERTimbau 77,46%, sem diferença estatisticamente\n"
        "significativa pelo teste de McNemar (*p* = 0,510).",
        f"({num(100*lider['acuracia'], 2)}%) e o acerto validado "
        f"({num(100*melhor['acerto_validado'], 2)}%). No *holdout* comum, o LinearSVC\n"
        f"alcança {num(100*ho_svc['acerto_validado'], 2)}% e o BERTimbau "
        f"{num(100*ho_bert['acerto_validado'], 2)}%, sem diferença estatisticamente\n"
        f"significativa pelo teste de McNemar (*p* = {num(p_bert, 3)}).",
        1, "resumo: comparação integral e holdout"))

    t.append((
        "histórico (0,8031; Tabela 1) quanto o acerto validado (0,9527; Tabela 2).",
        f"histórico ({num(lider['acuracia'])}; Tabela 1) quanto o acerto validado "
        f"({num(melhor['acerto_validado'])}; Tabela 2).",
        1, "4.x: liderança do LinearSVC"))

    t.append((
        "LinearSVC na liderança, com acurácia de 0,8031 (IC95%:\n"
        "0,7963--0,8097), seguido por Extra Trees (0,7894), Random Forest\n"
        "(0,7816), SGD (0,7767), Regressão Logística (0,7682), Naive Bayes\n"
        "(0,6997) e LSTM (0,6718). O teste de Cochran Q confirma diferença global\n"
        "entre os sete modelos avaliados (Q = 2984,07; p < 0,001).",
        f"LinearSVC na liderança, com acurácia de {num(lider['acuracia'])} (IC95%:\n"
        f"{num(lider['ic95_min'])}--{num(lider['ic95_max'])}), seguido por {demais}.\n"
        f"O teste de Cochran Q confirma diferença global\n"
        f"entre os sete modelos avaliados (Q = {num(cq['Q'], 2)}; p < 0,001).",
        1, "4.1: ranking e Cochran Q"))

    t.append((
        "intercambiáveis. O acerto validado do LinearSVC (95,27%) supera sua",
        f"intercambiáveis. O acerto validado do LinearSVC "
        f"({num(100*melhor['acerto_validado'], 2)}%) supera sua",
        1, "discussão: acerto validado"))

    t.append((
        "*holdout*, o transformador alcança 77,46% de acerto validado, contra\n"
        "78,56% do LinearSVC, sem diferença significativa.",
        f"*holdout*, o transformador alcança {num(100*ho_bert['acerto_validado'], 2)}% "
        f"de acerto validado, contra\n"
        f"{num(100*ho_svc['acerto_validado'], 2)}% do LinearSVC, sem diferença significativa.",
        1, "discussão: BERTimbau no holdout"))

    t.append((
        "deve ser comparada diretamente aos 95,27% da avaliação integral.",
        f"deve ser comparada diretamente aos {num(100*melhor['acerto_validado'], 2)}% "
        "da avaliação integral.",
        1, "discussão: protocolos distintos"))

    # --- Tabela 2 e o texto que a descreve. ---
    t.append((
        "| Modelo | Acerto validado | IC95% | Limite inferior |\n"
        "|---|---|---|---|\n"
        "| LinearSVC | 0,9527 | 0,9482 -- 0,9569 | 0,8888 |\n"
        "| SGD | 0,9442 | 0,9394 -- 0,9490 | 0,8810 |\n"
        "| Regressão Logística | 0,9404 | 0,9355 -- 0,9453 | 0,8774 |\n"
        "| Extra Trees | 0,9314 | 0,9261 -- 0,9365 | 0,8690 |\n"
        "| Random Forest | 0,9268 | 0,9213 -- 0,9320 | 0,8647 |\n"
        "| LSTM | 0,8872 | 0,8805 -- 0,8940 | 0,8278 |\n"
        "| Naive Bayes | 0,8659 | 0,8588 -- 0,8731 | 0,8078 |",
        tabela_validada(af, decididos, restritos), 1, "Tabela 2"))

    seq = af["por_modelo"]
    demais_val = ", ".join(
        f"{ROTULOS[x['modelo']]} ({num(x['acerto_validado'])})" for x in seq[1:])
    delta_pp = 100 * af["melhor_vs_segundo"]["delta"]
    t.append((
        "acerto validado de 0,9527 (IC95%: 0,9482--0,9569), seguido por SGD\n"
        "(0,9442), Regressão Logística (0,9404), Extra Trees (0,9314), Random\n"
        "Forest (0,9268), LSTM (0,8872) e Naive Bayes (0,8659). A diferença entre\n"
        "o primeiro e o segundo colocado é de 0,85 ponto percentual e é\n"
        "estatisticamente significativa (McNemar, *p* < 0,001).",
        f"acerto validado de {num(melhor['acerto_validado'])} "
        f"(IC95%: {num(melhor['ic95'][0])}--{num(melhor['ic95'][1])}), seguido por\n"
        f"{demais_val}. A diferença entre\n"
        f"o primeiro e o segundo colocado é de {num(delta_pp, 2)} ponto percentual e é\n"
        "estatisticamente significativa (McNemar, *p* < 0,001).",
        1, "4.2: ranking validado"))

    faixas = ", ".join(
        f"o {ROTULOS[x['modelo']]} de {num(limite_inferior(x, decididos, restritos))} "
        f"a {num(x['acerto_validado'])}" for x in seq)
    amp = [100 * (x["acerto_validado"] - limite_inferior(x, decididos, restritos))
           for x in seq]
    t.append((
        "inferior. O LinearSVC varia de 0,8888 a 0,9527, o SGD de 0,8810 a 0,9442,\n"
        "a Regressão Logística de 0,8774 a 0,9404, o Extra Trees de 0,8690 a\n"
        "0,9314, o Random Forest de 0,8647 a 0,9268, o LSTM de 0,8278 a 0,8872 e\n"
        "o Naive Bayes de 0,8078 a 0,8659. A amplitude varia de 5,80 a 6,39\n"
        "pontos percentuais",
        f"inferior. Considerando {faixas}.\n"
        f"A amplitude varia de {num(min(amp), 2)} a {num(max(amp), 2)}\n"
        "pontos percentuais",
        1, "4.2: faixas de sensibilidade"))

    t.append((
        "concordância com o histórico (80,31%) em 14,96 pontos percentuais.",
        f"concordância com o histórico ({num(100*lider['acuracia'], 2)}%) em "
        f"{num(100*melhor['acerto_validado'] - 100*lider['acuracia'], 2)} pontos percentuais.",
        1, "discussão: diferença entre as grandezas"))

    # --- Base: todas as ocorrencias restantes de 13.965. ---
    restantes = texto.count("13.965")
    # Descontar as que ja serao trocadas pelos trechos acima.
    ja = sum(de.count("13.965") for de, _, _, _ in t)
    t.append(("13.965", mil(base), restantes - ja, "base (ocorrências restantes)"))

    return t


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--artigo", type=Path, default=ARTIGO)
    p.add_argument("--aplicar", action="store_true")
    args = p.parse_args()

    texto = args.artigo.read_text(encoding="utf-8")
    original = texto
    trocas = construir_trocas(texto)

    falhas = []
    for de, para, esperado, rotulo in trocas:
        achou = texto.count(de)
        if achou != esperado:
            falhas.append(f"  [{rotulo}] esperava {esperado} ocorrencia(s), achou {achou}")
            continue
        texto = texto.replace(de, para)
        resumo_de = de.replace("\n", " ")[:64]
        resumo_para = para.replace("\n", " ")[:64]
        print(f"  OK  [{rotulo}] x{esperado}")
        if len(de) < 120:
            print(f"        - {resumo_de}")
            print(f"        + {resumo_para}")

    if falhas:
        print("\nABORTADO: trecho(s) esperado(s) nao encontrado(s) como declarado:",
              file=sys.stderr)
        for f in falhas:
            print(f, file=sys.stderr)
        print("Nada foi escrito. Ajuste o script ao texto atual antes de aplicar.",
              file=sys.stderr)
        return 1

    print(f"\ntrocas aplicadas: {len(trocas)} | caracteres: {len(original)} -> {len(texto)}")
    sobra = texto.count("13.965") + texto.count("8.895") + texto.count("9.534")
    if sobra:
        print(f"AVISO: ainda restam {sobra} ocorrencia(s) de numeros antigos "
              "(13.965 / 8.895 / 9.534).", file=sys.stderr)

    if not args.aplicar:
        print("\nDRY-RUN: nada gravado. Rode com --aplicar para escrever.")
        return 0

    args.artigo.write_text(texto, encoding="utf-8")
    print(f"\nOK: {args.artigo} atualizado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
