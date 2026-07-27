#!/usr/bin/env python3
"""Gera a Figura 6 do artigo: ablation do LSTM por unidades e dropout.

Le `04_artigo/figuras/ablation_lstm_resultados.json`, gravado por
`src/ablation_lstm.py`. Separar a plotagem do experimento permite regerar a
figura sem reexecutar o ablation completo.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from estilo_figuras import COR, LARGURA_COLUNA, aplicar_estilo, limpar_eixo, salvar  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA_PADRAO = RAIZ / "04_artigo" / "figuras" / "ablation_lstm_resultados.json"
SAIDA_PADRAO = RAIZ / "04_artigo" / "figuras" / "fig_ablation_lstm"


def gerar(entrada: Path, saida: Path) -> list[Path]:
    dados = json.loads(entrada.read_text(encoding="utf-8"))
    resultados = dados.get("resultados")
    if not resultados:
        raise ValueError(f"Campo resultados ausente ou vazio em {entrada}")

    resultados = sorted(resultados, key=lambda r: r["acerto_validado"])
    rotulos = [f"{r['units']} un.\ndropout {str(r['dropout']).replace('.', ',')}"
               for r in resultados]
    valores = [100 * r["acerto_validado"] for r in resultados]
    # A variante em producao recebe destaque de cor; as demais ficam neutras.
    cores = [COR["azul"] if "atual" in r["variante"] else COR["cinza"]
             for r in resultados]

    aplicar_estilo()
    fig, ax = plt.subplots(figsize=(LARGURA_COLUNA, 2.6))
    barras = ax.barh(range(len(resultados)), valores, color=cores, height=0.65)
    ax.set_yticks(range(len(resultados)), labels=rotulos)
    ax.set_xlabel("Acerto validado (%)")
    ax.set_xlim(80, max(valores) + 2)
    limpar_eixo(ax, eixo_grade="x")

    for barra, valor in zip(barras, valores):
        ax.text(valor + 0.15, barra.get_y() + barra.get_height() / 2,
                f"{valor:.2f}".replace(".", ","), va="center", fontsize=7)

    fig.tight_layout()
    return salvar(fig, saida)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--entrada", type=Path, default=ENTRADA_PADRAO)
    p.add_argument("--saida", type=Path, default=SAIDA_PADRAO,
                   help="caminho sem extensao; grava .pdf e .png")
    args = p.parse_args()
    for caminho in gerar(args.entrada, args.saida):
        print(f"figura={caminho.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
