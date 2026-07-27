#!/usr/bin/env python3
"""Gera as Figuras 7 e 8 do artigo: mapas de calor da taxonomia.

Figura 7 aproxima a leitura do painel público em forma estática. Dois painéis
lado a lado mostram as dez categorias de maior e de menor concordância com o
histórico, cada uma descrita por três indicadores comparáveis na mesma escala
de 0 a 1: concordância, confiança média e proporção de predições emitidas com
confiança igual ou superior a 95%.

Figura 8 recorta a matriz de confusão sobre as categorias mais envolvidas em
troca recíproca, no mesmo estilo visual, para mostrar que os erros se
concentram em fronteiras específicas da taxonomia.

Fontes, ambas versionadas:
  - `docs/dados/metricas_por_categoria.json` (Figura 7)
  - `docs/dados/estatistica.json`, campo `top_confusoes` (Figura 8)
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

sys.path.insert(0, str(Path(__file__).resolve().parent))
from estilo_figuras import LARGURA_DUPLA, aplicar_estilo, salvar  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CATEGORIAS_PADRAO = RAIZ / "docs" / "dados" / "metricas_por_categoria.json"
ESTATISTICA_PADRAO = RAIZ / "docs" / "dados" / "estatistica.json"
SAIDA_CALOR = RAIZ / "04_artigo" / "figuras" / "fig_calor_categorias"
SAIDA_MATRIZ = RAIZ / "04_artigo" / "figuras" / "fig_matriz_confusao"

TOP_N = 10
SUPORTE_MINIMO = 30
MAX_ROTULO = 26

# Mesma progressao fria-quente do painel publico, segura para daltonismo por
# variar luminosidade de forma monotonica.
ESCALA = LinearSegmentedColormap.from_list("painel", [
    "#0D1B2A", "#1B4965", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51",
])


def _cortar(texto: str, limite: int = MAX_ROTULO) -> str:
    return texto if len(texto) <= limite else texto[: limite - 1] + "…"


def _rotulos(categorias: list[str]) -> list[str]:
    """Rotula pela subcategoria, prefixando a categoria-mae quando houver colisao.

    Subcategorias homonimas sob categorias-mae distintas sao comuns nesta
    taxonomia, e sao justamente as mais confundidas entre si (por exemplo,
    "Ar condicionado split" sob Climatizacao e sob Manutencao Preventiva).
    Rotular so pela folha tornaria a figura ambigua exatamente no ponto que
    ela precisa evidenciar.
    """
    folhas = [c.split(" > ")[-1] if " > " in c else c for c in categorias]
    repetidas = {f for f in folhas if folhas.count(f) > 1}
    saida = []
    for categoria, folha in zip(categorias, folhas):
        if folha in repetidas and " > " in categoria:
            mae = categoria.split(" > ")[0]
            saida.append(f"{_cortar(mae, 12)} › {_cortar(folha, MAX_ROTULO - 14)}")
        else:
            saida.append(_cortar(folha))
    return saida


def _painel(ax, linhas, titulo, colunas):
    matriz = np.array([[v for _, v in linha[1]] for linha in linhas])
    ax.imshow(matriz, cmap=ESCALA, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(colunas)), labels=colunas, fontsize=6)
    ax.set_yticks(range(len(linhas)),
                  labels=_rotulos([nome for nome, _ in linhas]), fontsize=6)
    ax.set_title(titulo, fontsize=8, pad=6)
    for i, (_, valores) in enumerate(linhas):
        for k, (_, v) in enumerate(valores):
            # Texto claro sobre celula escura, escuro sobre celula clara.
            cor = "white" if v < 0.45 else "#1A1A1A"
            ax.text(k, i, f"{v:.2f}".replace(".", ","), ha="center", va="center",
                    fontsize=5.5, color=cor)
    ax.set_xticks(np.arange(-0.5, len(colunas), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(linhas), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.6)
    ax.grid(which="major", visible=False)
    ax.tick_params(which="minor", length=0)


def gerar_calor(entrada: Path, saida: Path) -> list[Path]:
    dados = json.loads(entrada.read_text(encoding="utf-8"))
    elegiveis = [c for c in dados if c.get("qtd_classificados", 0) >= SUPORTE_MINIMO]
    if len(elegiveis) < 2 * TOP_N:
        raise RuntimeError(f"Categorias elegiveis insuficientes: {len(elegiveis)}")
    elegiveis.sort(key=lambda c: c["taxa_concordancia"], reverse=True)

    def descrever(c):
        n = c["qtd_classificados"] or 1
        return (c["categoria"], [
            ("Concordância", c["taxa_concordancia"]),
            ("Confiança média", c["confianca_media"]),
            ("Alta confiança", c.get("qtd_acima_95", 0) / n),
        ])

    melhores = [descrever(c) for c in elegiveis[:TOP_N]]
    piores = [descrever(c) for c in reversed(elegiveis[-TOP_N:])]
    colunas = [rotulo for rotulo, _ in melhores[0][1]]

    aplicar_estilo()
    fig, (esq, dir_) = plt.subplots(1, 2, figsize=(LARGURA_DUPLA, 3.4),
                                    gridspec_kw={"wspace": 0.62})
    _painel(esq, melhores, f"{TOP_N} categorias de maior concordância", colunas)
    _painel(dir_, piores, f"{TOP_N} categorias de menor concordância", colunas)

    barra = fig.colorbar(plt.cm.ScalarMappable(cmap=ESCALA), ax=[esq, dir_],
                         fraction=0.025, pad=0.02)
    barra.set_label("Valor do indicador", fontsize=6)
    barra.ax.tick_params(labelsize=5.5)
    return salvar(fig, saida)


def gerar_matriz(entrada: Path, saida: Path, n_categorias: int = 8) -> list[Path]:
    dados = json.loads(entrada.read_text(encoding="utf-8"))
    agregado: dict[tuple[str, str], int] = defaultdict(int)
    for bloco in dados.get("top_confusoes", []):
        for par in bloco.get("pares", []) or []:
            de, para = str(par.get("de", "")).strip(), str(par.get("para", "")).strip()
            if de and para:
                agregado[(de, para)] += int(par.get("n") or 0)
    if not agregado:
        raise RuntimeError("Nenhum par de confusao em top_confusoes.")

    # Seleciona as categorias mais envolvidas em troca, somando as duas direcoes.
    envolvimento: dict[str, int] = defaultdict(int)
    for (de, para), n in agregado.items():
        envolvimento[de] += n
        envolvimento[para] += n
    categorias = [c for c, _ in sorted(envolvimento.items(),
                                       key=lambda kv: -kv[1])[:n_categorias]]

    matriz = np.array([[agregado.get((de, para), 0) for para in categorias]
                       for de in categorias], dtype=float)

    aplicar_estilo()
    fig, ax = plt.subplots(figsize=(LARGURA_DUPLA * 0.62, 3.2))
    maximo = matriz.max() or 1
    ax.imshow(matriz / maximo, cmap=ESCALA, vmin=0, vmax=1, aspect="auto")
    rotulos = _rotulos(categorias)
    ax.set_xticks(range(len(categorias)), labels=rotulos, fontsize=5.5,
                  rotation=40, ha="right")
    ax.set_yticks(range(len(categorias)), labels=rotulos, fontsize=5.5)
    ax.set_xlabel("Categoria predita", fontsize=7)
    ax.set_ylabel("Categoria histórica", fontsize=7)
    for i in range(len(categorias)):
        for k in range(len(categorias)):
            valor = matriz[i, k]
            if not valor:
                continue
            cor = "white" if valor / maximo < 0.45 else "#1A1A1A"
            ax.text(k, i, f"{int(valor)}", ha="center", va="center",
                    fontsize=5.5, color=cor)
    ax.set_xticks(np.arange(-0.5, len(categorias), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(categorias), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.6)
    ax.grid(which="major", visible=False)
    ax.tick_params(which="minor", length=0)
    fig.tight_layout()
    return salvar(fig, saida)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--categorias", type=Path, default=CATEGORIAS_PADRAO)
    p.add_argument("--estatistica", type=Path, default=ESTATISTICA_PADRAO)
    p.add_argument("--saida-calor", type=Path, default=SAIDA_CALOR)
    p.add_argument("--saida-matriz", type=Path, default=SAIDA_MATRIZ)
    args = p.parse_args()
    for caminho in gerar_calor(args.categorias, args.saida_calor):
        print(f"figura={caminho.relative_to(RAIZ)}")
    for caminho in gerar_matriz(args.estatistica, args.saida_matriz):
        print(f"figura={caminho.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
