#!/usr/bin/env python3
"""Gera a Figura 1 do artigo: pipeline de governança preditiva (diagrama estático).

Diferente das Figuras 2-6, este diagrama não deriva de um JSON do painel —
descreve as etapas fixas do protocolo metodológico (Subseção 3.1). Mantido
como script (em vez de imagem editada à mão) para poder ser regenerado em
qualquer resolução sem depender de uma ferramenta externa de diagramação.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "04_artigo" / "figuras" / "fig1_pipeline_governanca.png"

ETAPAS = [
    "1. Extracao e\nconsolidacao da base",
    "2. Higienizacao\ntextual",
    "3. Matriz de\natributos",
    "4. Treino e\ninferencia multimodelo",
    "5. Predicoes\nout-of-fold",
    "6. Comparacao com\ncategoria historica",
    "7. Analise estatistica\nnao parametrica",
    "8. Validacao humana\n(divergencias e criticos)",
]
COR_PADRAO = "#dde3ea"
COR_DESTAQUE = "#f3ddc4"
COR_SETA = "#8a3a3a"


def gerar() -> None:
    n = len(ETAPAS)
    fig, ax = plt.subplots(figsize=(20, 6.5))
    largura, altura = 1.0, 1.0
    espaco = 0.18
    passo = largura + espaco

    for i, texto in enumerate(ETAPAS):
        x = i * passo
        cor = COR_DESTAQUE if i == n - 1 else COR_PADRAO
        caixa = FancyBboxPatch(
            (x, 0), largura, altura,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            linewidth=1.0, edgecolor="#9aa5b1", facecolor=cor,
        )
        ax.add_patch(caixa)
        ax.text(x + largura / 2, altura / 2, texto, ha="center", va="center", fontsize=11)
        if i < n - 1:
            ax.annotate(
                "", xy=(x + passo, altura / 2), xytext=(x + largura, altura / 2),
                arrowprops=dict(arrowstyle="-|>", color="#555555", linewidth=1.2),
            )

    # Seta de retroalimentacao: da etapa 8 (validacao humana) de volta para a etapa 4 (treino).
    x_treino = 3 * passo + largura / 2
    x_validacao = (n - 1) * passo + largura / 2
    y_baixo = -0.35
    ax.plot([x_validacao, x_validacao], [0, y_baixo], color=COR_SETA, linewidth=1.4)
    ax.plot([x_validacao, x_treino], [y_baixo, y_baixo], color=COR_SETA, linewidth=1.4)
    ax.annotate(
        "", xy=(x_treino, 0), xytext=(x_treino, y_baixo),
        arrowprops=dict(arrowstyle="-|>", color=COR_SETA, linewidth=1.4),
    )
    ax.text(
        (x_treino + x_validacao) / 2, y_baixo - 0.18,
        "retroalimentacao: memoria de decisao (veto/trava) informa novas rodadas de treino/inferencia",
        ha="center", va="top", fontsize=11, style="italic", color=COR_SETA,
    )

    ax.set_xlim(-0.15, (n - 1) * passo + largura + 0.15)
    ax.set_ylim(y_baixo - 0.55, 1.55)
    ax.axis("off")

    fig.tight_layout()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAIDA, dpi=300)
    plt.close(fig)
    print(f"figura={SAIDA}")


if __name__ == "__main__":
    gerar()
