#!/usr/bin/env python3
"""Gera a Figura 5 do artigo: curva de aprendizado do LSTM por epoca.

Le `04_artigo/figuras/lstm_history.json`, gravado por `src/modelo_lstm.py`
durante o treino. Separar a plotagem do treino permite regerar a figura sem
credencial de planilha e sem reexecutar a rede.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from estilo_figuras import COR, LARGURA_DUPLA, aplicar_estilo, limpar_eixo, salvar  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA_PADRAO = RAIZ / "04_artigo" / "figuras" / "lstm_history.json"
SAIDA_PADRAO = RAIZ / "04_artigo" / "figuras" / "fig5_curva_aprendizado_lstm"


def gerar(entrada: Path, saida: Path) -> list[Path]:
    historico = json.loads(entrada.read_text(encoding="utf-8"))
    for campo in ("loss", "val_loss", "accuracy", "val_accuracy"):
        if campo not in historico:
            raise ValueError(f"Campo {campo} ausente em {entrada}")

    epocas = range(1, len(historico["loss"]) + 1)

    aplicar_estilo()
    fig, (ax_perda, ax_acc) = plt.subplots(1, 2, figsize=(LARGURA_DUPLA, 2.6))

    ax_perda.plot(epocas, historico["loss"], marker="o",
                  color=COR["azul"], label="Treino")
    ax_perda.plot(epocas, historico["val_loss"], marker="s", linestyle="--",
                  color=COR["laranja"], label="Validação")
    ax_perda.set_xlabel("Época")
    ax_perda.set_ylabel("Perda")
    ax_perda.legend()
    limpar_eixo(ax_perda)

    ax_acc.plot(epocas, historico["accuracy"], marker="o",
                color=COR["azul"], label="Treino")
    ax_acc.plot(epocas, historico["val_accuracy"], marker="s", linestyle="--",
                color=COR["laranja"], label="Validação")
    ax_acc.set_xlabel("Época")
    ax_acc.set_ylabel("Acurácia")
    ax_acc.legend()
    limpar_eixo(ax_acc)

    melhor = max(range(len(historico["val_accuracy"])),
                 key=lambda i: historico["val_accuracy"][i])
    rotulo = f"melhor: {historico['val_accuracy'][melhor]:.4f}".replace(".", ",")
    ax_acc.annotate(rotulo,
                    xy=(melhor + 1, historico["val_accuracy"][melhor]),
                    xytext=(0, -12), textcoords="offset points",
                    ha="center", fontsize=6, color=COR["cinza"])

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
