#!/usr/bin/env python3
"""Gera a Figura 1 do artigo: pipeline de governança preditiva (diagrama estático).

Diferente das Figuras 2-6, este diagrama não deriva de dados do experimento;
descreve as oito etapas fixas do protocolo metodológico (Subseção 3.1).
Mantido como script, em vez de imagem editada à mão, para poder ser
regenerado em qualquer resolução sem depender de ferramenta externa.

O layout usa duas fileiras de quatro etapas para caber na largura da página.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from estilo_figuras import COR, LARGURA_DUPLA, aplicar_estilo, salvar  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "04_artigo" / "figuras" / "fig_pipeline_governanca"

# A ordem importa e ja esteve errada: a revisao humana figurava como ultima
# etapa, com a legenda "divergencias e criticos", o que descrevia uma triagem
# amostral que o experimento nao executou. A revisao cobriu o corpus inteiro e
# PRECEDE o treino, porque e dela que sai o rotulo com que os modelos sao
# treinados. A caixa fica destacada por ser a etapa que distingue o protocolo.
ETAPAS = [
    "1. Extração e\nconsolidação da base",
    "2. Revisão humana\ndo corpus integral",
    "3. Higienização\ntextual",
    "4. Matriz de\natributos",
    "5. Partições agrupadas\ne treino out-of-fold",
    "6. Comparação com histórico\ne com a referência",
    "7. Inferência estatística\nnão paramétrica",
    "8. Calibração e automação\nseletiva por confiança",
]
INDICE_DESTAQUE = 1
INDICE_RETROALIMENTACAO = 4
POR_FILEIRA = 4
COR_CAIXA = "#E8ECF1"
COR_DESTAQUE = "#FBE3C4"
COR_BORDA = "#8A94A0"


def _posicao(indice: int) -> tuple[float, float]:
    """Coordenadas (x, y) do canto inferior esquerdo da caixa."""
    fileira, coluna = divmod(indice, POR_FILEIRA)
    return coluna * 1.18, -fileira * 1.30


def gerar(saida: Path = SAIDA) -> list[Path]:
    aplicar_estilo()
    fig, ax = plt.subplots(figsize=(LARGURA_DUPLA, 3.0))

    for i, texto in enumerate(ETAPAS):
        x, y = _posicao(i)
        cor = COR_DESTAQUE if i == INDICE_DESTAQUE else COR_CAIXA
        ax.add_patch(FancyBboxPatch(
            (x, y), 1.0, 0.9,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            linewidth=0.8, edgecolor=COR_BORDA, facecolor=cor,
        ))
        ax.text(x + 0.5, y + 0.45, texto, ha="center", va="center", fontsize=6.5)

        proximo = i + 1
        if proximo >= len(ETAPAS):
            continue
        if proximo % POR_FILEIRA:
            # Seta horizontal dentro da mesma fileira.
            ax.annotate("", xy=(x + 1.18, y + 0.45), xytext=(x + 1.0, y + 0.45),
                        arrowprops=dict(arrowstyle="-|>", color=COR["cinza"], linewidth=1.0))
        else:
            # Quebra de fileira: desce pela direita e volta pela esquerda.
            x_prox, y_prox = _posicao(proximo)
            meio = y - 0.20
            ax.plot([x + 0.5, x + 0.5], [y, meio], color=COR["cinza"], linewidth=1.0)
            ax.plot([x + 0.5, x_prox + 0.5], [meio, meio], color=COR["cinza"], linewidth=1.0)
            ax.annotate("", xy=(x_prox + 0.5, y_prox + 0.9), xytext=(x_prox + 0.5, meio),
                        arrowprops=dict(arrowstyle="-|>", color=COR["cinza"], linewidth=1.0))

    # Retroalimentacao: da etapa 8 (automacao seletiva) de volta para a etapa 5
    # (treino). O trajeto passa por baixo da segunda fileira, sem cruzar caixa.
    x8, y8 = _posicao(len(ETAPAS) - 1)
    x5, y5 = _posicao(INDICE_RETROALIMENTACAO)
    margem = x8 + 1.12
    volta = y8 - 0.30
    ax.plot([x8 + 0.5, x8 + 0.5], [y8, volta], color=COR["vermelho"], linewidth=1.1)
    ax.plot([x8 + 0.5, x5 + 0.5], [volta, volta], color=COR["vermelho"], linewidth=1.1)
    ax.annotate("", xy=(x5 + 0.5, y5), xytext=(x5 + 0.5, volta),
                arrowprops=dict(arrowstyle="-|>", color=COR["vermelho"], linewidth=1.1))
    ax.text((POR_FILEIRA - 1) * 1.18 / 2 + 0.5, volta - 0.12,
            "retroalimentação: os casos encaminhados à revisão humana realimentam o treino",
            ha="center", va="top", fontsize=6, style="italic", color=COR["vermelho"])

    ax.set_xlim(-0.10, margem + 0.12)
    ax.set_ylim(volta - 0.45, 1.00)
    ax.axis("off")

    fig.tight_layout()
    return salvar(fig, saida)


if __name__ == "__main__":
    for caminho in gerar():
        print(f"figura={caminho.relative_to(RAIZ)}")
