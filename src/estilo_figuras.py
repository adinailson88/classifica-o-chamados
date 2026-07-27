#!/usr/bin/env python3
"""Estilo comum e gravacao das figuras do artigo.

Centraliza tres decisoes que antes estavam repetidas (e divergentes) em cada
gerador de figura:

1. Paleta segura para daltonismo (Okabe-Ito). Nenhuma informacao da figura
   depende so da cor: series distintas variam tambem em forma ou posicao.
2. Tamanho de figura pensado para a pagina do artigo. `LARGURA_COLUNA`
   (~8,5 cm) serve para figuras simples de uma coluna; `LARGURA_DUPLA`
   (~17,5 cm) serve para as figuras com muitos rotulos categoricos, que
   ficariam ilegiveis reduzidas a uma coluna.
3. Gravacao simultanea em PDF vetorial (usado pelo build do artigo) e PNG a
   300 dpi (exigido por submissao em periodico).

Uso tipico:

    from estilo_figuras import COR, LARGURA_COLUNA, aplicar_estilo, salvar

    aplicar_estilo()
    fig, ax = plt.subplots(figsize=(LARGURA_COLUNA, 2.6))
    ...
    salvar(fig, RAIZ / "04_artigo" / "figuras" / "fig2_confianca_desfecho")
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

# Paleta Okabe-Ito: distinguivel nas formas mais comuns de daltonismo.
COR = {
    "azul": "#0072B2",
    "laranja": "#E69F00",
    "verde": "#009E73",
    "vermelho": "#D55E00",
    "roxo": "#CC79A7",
    "ciano": "#56B4E9",
    "amarelo": "#F0E442",
    "cinza": "#666666",
}

CICLO = [COR["azul"], COR["laranja"], COR["verde"], COR["vermelho"],
         COR["roxo"], COR["ciano"], COR["cinza"]]

# Polegadas. 1 cm = 0,3937 in.
LARGURA_COLUNA = 3.35   # ~8,5 cm
LARGURA_DUPLA = 6.90    # ~17,5 cm


def aplicar_estilo() -> None:
    """Aplica o estilo do artigo aos parametros globais do matplotlib."""
    matplotlib.use("Agg")
    plt.rcParams.update({
        "axes.prop_cycle": matplotlib.cycler(color=CICLO),
        "axes.grid": True,
        "axes.axisbelow": True,
        "axes.edgecolor": "#333333",
        "axes.labelcolor": "#222222",
        "axes.labelsize": 8,
        "axes.titlesize": 9,
        "figure.dpi": 300,
        "font.size": 8,
        "grid.color": "#CCCCCC",
        "grid.linestyle": "--",
        "grid.linewidth": 0.5,
        "legend.fontsize": 7,
        "legend.frameon": False,
        "lines.linewidth": 1.4,
        "lines.markersize": 4,
        "savefig.bbox": "tight",
        "text.color": "#222222",
        "xtick.color": "#333333",
        "xtick.labelsize": 7,
        "ytick.color": "#333333",
        "ytick.labelsize": 7,
    })


def limpar_eixo(ax, eixo_grade: str = "y") -> None:
    """Remove molduras superiores/direitas e deixa a grade em um eixo so."""
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis=eixo_grade)
    ax.grid(axis="x" if eixo_grade == "y" else "y", visible=False)


def salvar(fig, base: Path) -> list[Path]:
    """Grava a figura em PDF vetorial e PNG a 300 dpi.

    `base` e o caminho sem extensao. Retorna os arquivos escritos, na ordem
    em que foram gerados.
    """
    base = Path(base)
    base.parent.mkdir(parents=True, exist_ok=True)
    escritos = []
    for extensao in ("pdf", "png"):
        destino = base.with_suffix(f".{extensao}")
        fig.savefig(destino, dpi=300)
        escritos.append(destino)
    plt.close(fig)
    return escritos
