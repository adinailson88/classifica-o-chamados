#!/usr/bin/env python3
"""Gera a Figura 2 do artigo: concordancia com o historico x acerto validado, por faixa de confianca.

Le `docs/dados/calibracao.json` (campo `por_faixa`) -- os mesmos numeros da
Tabela 3 (Subsecao 4.4), em forma grafica. Nao recalcula nada; so plota o
que ja esta publicado no painel.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA_PADRAO = RAIZ / "docs" / "dados" / "calibracao.json"
SAIDA_PADRAO = RAIZ / "04_artigo" / "figuras" / "fig2_confianca_desfecho.png"
META = 0.95


def gerar(entrada: Path, saida: Path) -> None:
    dados = json.loads(entrada.read_text(encoding="utf-8"))
    por_faixa = dados["por_faixa"]
    gerado_em = dados.get("gerado_em", "")

    faixas = [f["faixa"] for f in por_faixa]
    concordancia = [100 * f["concordancia_historico"] for f in por_faixa]
    acerto_validado = [100 * f["acerto_validado"] for f in por_faixa]

    x = np.arange(len(faixas))
    largura = 0.38

    fig, ax = plt.subplots(figsize=(10, 6))
    b1 = ax.bar(x - largura / 2, concordancia, largura, label="Concordancia com o historico", color="#8c8c8c")
    b2 = ax.bar(x + largura / 2, acerto_validado, largura, label="Acerto validado (conferencia humana)", color="#1f5c8b")
    ax.axhline(100 * META, color="#c1651a", linestyle="--", linewidth=1.4, label=f"Meta ({int(100 * META)}%)")

    for bars in (b1, b2):
        for rect in bars:
            altura_barra = rect.get_height()
            ax.annotate(f"{altura_barra:.0f}", xy=(rect.get_x() + rect.get_width() / 2, altura_barra),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)

    ax.set_xticks(x)
    ax.set_xticklabels(faixas)
    ax.set_ylabel("%")
    ax.set_ylim(0, 108)
    ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.35)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="lower right", frameon=False)

    fig.tight_layout()
    saida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(saida, dpi=300)
    plt.close(fig)
    print(f"figura={saida}")
    print(f"fonte={entrada} gerado_em={gerado_em}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--entrada", type=Path, default=ENTRADA_PADRAO)
    p.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    args = p.parse_args()
    gerar(args.entrada, args.saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
