#!/usr/bin/env python3
"""Figuras 2 a 6 do artigo, geradas a partir da rodada canonica.

Por que existe. Os geradores antigos (`gerar_figura2_confianca_desfecho.py`,
`gerar_figura3_tradeoff_custo.py`, `gerar_figura4_confusoes.py` e
`gerar_figura7_mapas_calor.py`) leem `calibracao.json`, `avaliacao_final.json`,
`estatistica.json` e `metricas_por_categoria.json`, que sao artefatos da
execucao legada e descrevem outro corpus. Regerar as figuras por eles
reintroduziria numeros que as tabelas ja nao usam.

Este modulo le apenas artefatos com `hash_corpus` da rodada canonica, mais o
CSV de predicoes que os originou, e recusa-se a rodar se os hashes divergirem.

Figuras produzidas:

    fig_confianca_desfecho   curva de confiabilidade do melhor modelo calibrado
    fig_calor_categorias     F1 e suporte das categorias extremas
    fig_matriz_confusao      recorte da matriz sobre as categorias em troca
    fig_top_confusoes        pares com maior confusao reciproca
    fig_tradeoff_custo       acuracia contra tempo de treino

As Figuras 7 e 8, do LSTM, continuam nos geradores proprios: descrevem uma
analise de sensibilidade sob protocolo distinto, declarado na Subsecao 4.8.

Somente leitura: nao escreve na planilha.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt  # noqa: E402

from estilo_figuras import (COR, LARGURA_DUPLA, aplicar_estilo,  # noqa: E402
                            limpar_eixo, salvar)
from tipo_manutencao import sigla, tipo_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "docs" / "dados"
FIGURAS = RAIZ / "04_artigo" / "figuras"
PREDICOES = DADOS / "retreino_canonico_predicoes.csv"

MODELO_PRINCIPAL = "linear_svc"
MODELO_CALIBRADO = "extra_trees"
SUPORTE_MINIMO = 30

NOME = {
    "linear_svc": "LinearSVC",
    "sgd": "SGD",
    "extra_trees": "Extra Trees",
    "regressao_logistica": "Regressão Logística",
    "random_forest": "Random Forest",
    "lstm": "LSTM",
    "naive_bayes": "Naive Bayes",
}


def carregar_json(nome: str) -> dict[str, Any]:
    return json.loads((DADOS / nome).read_text(encoding="utf-8"))


def conferir_hash(artefatos: dict[str, dict[str, Any]]) -> str:
    """Aborta se os artefatos nao descreverem o mesmo corpus."""
    hashes = {nome: d.get("hash_corpus") for nome, d in artefatos.items()
              if d.get("hash_corpus")}
    distintos = set(hashes.values())
    if len(distintos) != 1:
        raise SystemExit(f"hash_corpus divergente entre artefatos: {hashes}")
    return distintos.pop()


def carregar_predicoes() -> dict[str, list[tuple[str, str]]]:
    por_modelo: dict[str, list[tuple[str, str]]] = defaultdict(list)
    with PREDICOES.open("r", encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            por_modelo[linha["modelo"]].append(
                (linha["referencia_humana"], linha["previsto"]))
    return dict(por_modelo)


def abreviar(categoria: str, limite: int = 34) -> str:
    """Folha da categoria, com a sigla do tipo e encurtada para o eixo.

    A sigla nao e enfeite: a taxonomia repete a mesma folha sob familias
    distintas, e 'Ar condicionado split' existe tanto sob Manutencao
    Preventiva quanto sob Climatizacao. Sem o prefixo, duas barras da figura
    ficariam com rotulo identico e valores diferentes.
    """
    folha = categoria.split(">")[-1].strip()
    marca = sigla(tipo_manutencao(categoria))
    if len(folha) > limite:
        folha = folha[:limite - 1].rstrip() + "…"
    return f"[{marca}] {folha}"


def formatar_decimal(ax, eixo: str = "x") -> None:
    """Virgula decimal no eixo, para casar com o restante do artigo."""
    from matplotlib.ticker import FuncFormatter

    formatador = FuncFormatter(lambda v, _p: f"{v:.1f}".replace(".", ","))
    (ax.xaxis if eixo == "x" else ax.yaxis).set_major_formatter(formatador)


# --------------------------------------------------------------------------
# Figura 2 — curva de confiabilidade do melhor modelo calibrado
# --------------------------------------------------------------------------
def figura_confiabilidade(calibracao: dict[str, Any]) -> None:
    modelo = next(m for m in calibracao["modelos"]
                  if m["modelo"] == MODELO_CALIBRADO)
    faixas = modelo["calibrada"]["confiabilidade"]
    # 'faixa' vem como '[0.0, 0.1)'; o centro sai dos limites declarados.
    centros = [(float(f["faixa"][1:-1].split(",")[0])
                + float(f["faixa"][1:-1].split(",")[1])) / 2 for f in faixas]
    confianca = [f["confianca_media"] for f in faixas]
    acuracia = [f["acuracia"] for f in faixas]
    registros = [f["n"] for f in faixas]

    fig, (ax, ax2) = plt.subplots(
        2, 1, figsize=(LARGURA_DUPLA, 4.2), sharex=True,
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.12})

    ax.plot([0, 1], [0, 1], color=COR["cinza"], linestyle=":", linewidth=1.0,
            label="calibração perfeita")
    ax.plot(confianca, acuracia, marker="o", color=COR["azul"],
            label="acurácia observada")
    ax.set_ylabel("Acurácia observada")
    ax.set_ylim(0, 1.02)
    ax.legend(loc="upper left")
    formatar_decimal(ax, eixo="y")
    limpar_eixo(ax)

    ax2.bar(centros, registros, width=0.085, color=COR["laranja"])
    ax2.set_ylabel("Registros")
    ax2.set_xlabel("Confiança calibrada")
    ax2.set_xlim(0, 1)
    formatar_decimal(ax2)
    limpar_eixo(ax2)

    salvar(fig, FIGURAS / "fig_confianca_desfecho")


# --------------------------------------------------------------------------
# Figura 3 — categorias extremas por F1
# --------------------------------------------------------------------------
def figura_categorias(pares: list[tuple[str, str]]) -> None:
    from sklearn.metrics import f1_score

    suporte = Counter(v for v, _ in pares)
    elegiveis = sorted(c for c, n in suporte.items() if n >= SUPORTE_MINIMO)
    valores = f1_score([v for v, _ in pares], [p for _, p in pares],
                       labels=elegiveis, average=None, zero_division=0)
    f1 = dict(zip(elegiveis, (round(float(v), 4) for v in valores)))
    ordem = sorted(elegiveis, key=lambda c: f1[c])
    piores, melhores = ordem[:10], ordem[-10:]
    selecao = piores + melhores

    fig, ax = plt.subplots(figsize=(LARGURA_DUPLA, 5.0))
    cores = [COR["vermelho"]] * len(piores) + [COR["verde"]] * len(melhores)
    posicoes = range(len(selecao))
    ax.barh(list(posicoes), [f1[c] for c in selecao], color=cores, height=0.72)
    ax.set_yticks(list(posicoes))
    ax.set_yticklabels([f"{abreviar(c)}  (n={suporte[c]})" for c in selecao])
    ax.set_xlabel(f"F1 do {NOME[MODELO_PRINCIPAL]}")
    ax.set_xlim(0, 1.05)
    for i, c in enumerate(selecao):
        ax.text(f1[c] + 0.012, i, f"{f1[c]:.3f}".replace(".", ","),
                va="center", fontsize=6.5)
    formatar_decimal(ax)
    limpar_eixo(ax, eixo_grade="x")
    salvar(fig, FIGURAS / "fig_calor_categorias")


# --------------------------------------------------------------------------
# Figura 4 — recorte da matriz de confusao
# --------------------------------------------------------------------------
def figura_matriz(por_modelo: dict[str, list[tuple[str, str]]]) -> None:
    trocas: Counter = Counter()
    for pares in por_modelo.values():
        for v, p in pares:
            if v != p:
                trocas[(v, p)] += 1

    envolvimento: Counter = Counter()
    for (v, p), n in trocas.items():
        envolvimento[v] += n
        envolvimento[p] += n
    eixo = [c for c, _ in envolvimento.most_common(8)]

    matriz = [[trocas.get((v, p), 0) if v != p else 0 for p in eixo]
              for v in eixo]

    fig, ax = plt.subplots(figsize=(LARGURA_DUPLA, 5.4))
    im = ax.imshow(matriz, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(eixo)))
    ax.set_xticklabels([abreviar(c, 22) for c in eixo], rotation=40,
                       ha="right", fontsize=6.5)
    ax.set_yticks(range(len(eixo)))
    ax.set_yticklabels([abreviar(c, 26) for c in eixo], fontsize=6.5)
    ax.set_xlabel("Categoria prevista")
    ax.set_ylabel("Categoria de referência")
    ax.grid(False)
    maximo = max(max(linha) for linha in matriz) or 1
    for i, linha in enumerate(matriz):
        for j, n in enumerate(linha):
            if n:
                ax.text(j, i, str(n), ha="center", va="center", fontsize=6,
                        color="white" if n > 0.55 * maximo else "#222222")
    fig.colorbar(im, ax=ax, shrink=0.7, label="Chamados (soma dos 7 modelos)")
    salvar(fig, FIGURAS / "fig_matriz_confusao")


# --------------------------------------------------------------------------
# Figura 5 — pares com maior confusao reciproca
# --------------------------------------------------------------------------
def figura_pares(por_modelo: dict[str, list[tuple[str, str]]]) -> None:
    trocas: Counter = Counter()
    for pares in por_modelo.values():
        for v, p in pares:
            if v != p:
                trocas[(v, p)] += 1

    reciprocos: Counter = Counter()
    for (v, p), n in trocas.items():
        reciprocos[tuple(sorted((v, p)))] += n
    top = reciprocos.most_common(15)[::-1]

    fig, ax = plt.subplots(figsize=(LARGURA_DUPLA, 5.2))
    posicoes = range(len(top))
    ax.barh(list(posicoes), [n for _, n in top], color=COR["azul"], height=0.72)
    ax.set_yticks(list(posicoes))
    ax.set_yticklabels([f"{abreviar(a, 24)} ↔ {abreviar(b, 24)}"
                        for (a, b), _ in top], fontsize=6.5)
    ax.set_xlabel("Trocas recíprocas (soma dos 7 modelos)")
    for i, (_, n) in enumerate(top):
        ax.text(n + max(x for _, x in top) * 0.01, i, str(n), va="center",
                fontsize=6.5)
    limpar_eixo(ax, eixo_grade="x")
    salvar(fig, FIGURAS / "fig_tradeoff_pares_tmp")
    # Nome final mantido por compatibilidade com o texto do artigo.
    for extensao in ("pdf", "png"):
        origem = FIGURAS / f"fig_tradeoff_pares_tmp.{extensao}"
        origem.replace(FIGURAS / f"fig_top_confusoes.{extensao}")


# --------------------------------------------------------------------------
# Figura 6 — acuracia contra custo de treino
# --------------------------------------------------------------------------
def figura_custo(retreino: dict[str, Any], custo: dict[str, Any]) -> None:
    acuracia = {m["modelo"]: m["acuracia"] for m in retreino["modelos"]}
    treino = {m["modelo"]: m["treino_s"] for m in custo["modelos"]}

    fig, ax = plt.subplots(figsize=(LARGURA_DUPLA, 3.6))
    for i, modelo in enumerate(sorted(treino, key=lambda m: treino[m])):
        ax.scatter(treino[modelo], acuracia[modelo], s=46,
                   color=COR[list(COR)[i % len(COR)]], zorder=3)
        ax.annotate(NOME.get(modelo, modelo),
                    (treino[modelo], acuracia[modelo]),
                    textcoords="offset points", xytext=(6, 4), fontsize=7)
    ax.set_xscale("log")
    ax.set_xlabel("Tempo de treino sobre a base completa (s, escala log)")
    ax.set_ylabel("Acurácia contra a referência humana")
    formatar_decimal(ax, eixo="y")
    limpar_eixo(ax)
    salvar(fig, FIGURAS / "fig_tradeoff_custo")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apenas", nargs="*", default=None,
                   help="subconjunto: confiabilidade, categorias, matriz, "
                        "pares, custo")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    aplicar_estilo()

    retreino = carregar_json("retreino_canonico.json")
    calibracao = carregar_json("calibracao_canonica.json")
    custo = carregar_json("custo_computacional_canonico.json")
    corpus = conferir_hash({"retreino": retreino, "calibracao": calibracao,
                            "custo": custo})
    print(f"hash_corpus conferido: {corpus[:12]}")

    por_modelo = carregar_predicoes()
    pares = por_modelo[MODELO_PRINCIPAL]

    tarefas = {
        "confiabilidade": lambda: figura_confiabilidade(calibracao),
        "categorias": lambda: figura_categorias(pares),
        "matriz": lambda: figura_matriz(por_modelo),
        "pares": lambda: figura_pares(por_modelo),
        "custo": lambda: figura_custo(retreino, custo),
    }
    escolhidas = args.apenas or list(tarefas)
    for nome in escolhidas:
        tarefas[nome]()
        print(f"  {nome}: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
