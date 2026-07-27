#!/usr/bin/env python3
"""Gera a Figura 2 do artigo: concordancia com o historico x acerto validado, por faixa de confianca.

Le `docs/dados/calibracao.json` (campo `por_faixa`) -- os mesmos numeros da
Tabela 3 (Subsecao 4.4), em forma grafica. Nao recalcula nada; so plota o
que ja esta publicado no painel.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from estilo_figuras import COR, LARGURA_DUPLA, aplicar_estilo, limpar_eixo, salvar  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA_PADRAO = RAIZ / "docs" / "dados" / "calibracao.json"
SAIDA_PADRAO = RAIZ / "04_artigo" / "figuras" / "fig2_confianca_desfecho"
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

    aplicar_estilo()
    fig, ax = plt.subplots(figsize=(LARGURA_DUPLA, 2.8))
    b1 = ax.bar(x - largura / 2, concordancia, largura, label="Concordancia com o historico", color=COR["cinza"])
    b2 = ax.bar(x + largura / 2, acerto_validado, largura, label="Acerto validado (conferencia humana)", color=COR["azul"])
    ax.axhline(100 * META, color=COR["vermelho"], linestyle="--", linewidth=1.2, label=f"Meta ({int(100 * META)}%)")

    for bars in (b1, b2):
        for rect in bars:
            altura_barra = rect.get_height()
            ax.annotate(f"{altura_barra:.0f}", xy=(rect.get_x() + rect.get_width() / 2, altura_barra),
                        xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=6)

    ax.set_xticks(x)
    ax.set_xticklabels(faixas)
    ax.set_ylabel("%")
    ax.set_ylim(0, 112)
    ax.set_xlabel("Faixa de confianca")
    limpar_eixo(ax)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=3)

    fig.tight_layout()
    for caminho in salvar(fig, saida):
        print(f"figura={caminho.relative_to(RAIZ)}")
    print(f"fonte={entrada} gerado_em={gerado_em}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--entrada", type=Path, default=ENTRADA_PADRAO)
    p.add_argument("--saida", type=Path, default=SAIDA_PADRAO,
                   help="caminho sem extensao; grava .pdf e .png")
    args = p.parse_args()
    gerar(args.entrada, args.saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
