#!/usr/bin/env python3
"""Gera a Figura 4 do artigo: trade-off entre acerto validado e custo computacional.

Cruza dois JSONs sem recalcular nada:
  - `docs/dados/comparacao_modelos.json`: tempo de treino por modelo classico,
    lote de 1.000 registros (inicio=0, limite=1000) -- unico registro de
    custo computacional disponivel no painel.
  - `docs/dados/avaliacao_final.json` (`por_modelo`): acerto validado (base
    completa, conferencia humana).

So entram os modelos presentes em AMBOS os arquivos -- LSTM e BERTimbau nao
tem custo medido nesta base e ficam de fora naturalmente, sem filtro
explicito.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from estilo_figuras import COR, LARGURA_DUPLA, aplicar_estilo, salvar  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CUSTO_PADRAO = RAIZ / "docs" / "dados" / "comparacao_modelos.json"
AVALIACAO_PADRAO = RAIZ / "docs" / "dados" / "avaliacao_final.json"
SAIDA_PADRAO = RAIZ / "04_artigo" / "figuras" / "fig_tradeoff_custo"

NOMES_EXIBICAO = {
    "naive_bayes": "Naive Bayes",
    "linear_svc": "LinearSVC",
    "sgd": "SGD",
    "regressao_logistica": "Regressão Log.",
    "random_forest": "Random Forest",
    "extra_trees": "Extra Trees",
}


def gerar(custo_path: Path, avaliacao_path: Path, saida: Path) -> None:
    custo_lista = json.loads(custo_path.read_text(encoding="utf-8"))
    avaliacao = json.loads(avaliacao_path.read_text(encoding="utf-8"))

    # Lote de referencia: primeiros 1.000 registros (inicio=0, limite=1000) por modelo.
    custo_por_modelo = {}
    executado_em = None
    for r in custo_lista:
        if r.get("inicio") == 0 and r.get("limite") == 1000:
            custo_por_modelo[r["modelo"]] = r["tempo_treino_s"]
            executado_em = r.get("executado_em", executado_em)

    acerto_por_modelo = {r["modelo"]: r["acerto_validado"] for r in avaliacao["por_modelo"]}
    conferencia_data = avaliacao.get("gerado_em", "")

    modelos = [m for m in custo_por_modelo if m in acerto_por_modelo]
    if not modelos:
        raise RuntimeError("Nenhum modelo em comum entre custo e avaliacao final.")

    xs = [custo_por_modelo[m] for m in modelos]
    ys = [100 * acerto_por_modelo[m] for m in modelos]
    labels = [NOMES_EXIBICAO.get(m, m) for m in modelos]

    aplicar_estilo()
    fig, ax = plt.subplots(figsize=(LARGURA_DUPLA, 2.8))
    ax.scatter(xs, ys, s=45, color=COR["azul"], edgecolor="white", linewidth=0.8, zorder=3)
    # Rotulos dos pontos mais a direita viram para dentro, para nao vazar da figura.
    limite = sorted(xs)[len(xs) // 2]
    for x, y, label in zip(xs, ys, labels):
        a_esquerda = x > limite
        ax.annotate(label, xy=(x, y),
                    xytext=(-5 if a_esquerda else 5, 3), textcoords="offset points",
                    ha="right" if a_esquerda else "left", fontsize=6)

    ax.set_xscale("log")
    ax.set_xlabel("Tempo de treino (s, escala log)")
    ax.set_ylabel("Acerto validado (%)")
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    for caminho in salvar(fig, saida):
        print(f"figura={caminho.relative_to(RAIZ)}")
    print(f"modelos={modelos}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--custo", type=Path, default=CUSTO_PADRAO)
    p.add_argument("--avaliacao", type=Path, default=AVALIACAO_PADRAO)
    p.add_argument("--saida", type=Path, default=SAIDA_PADRAO,
                   help="caminho sem extensao; grava .pdf e .png")
    args = p.parse_args()
    gerar(args.custo, args.avaliacao, args.saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
