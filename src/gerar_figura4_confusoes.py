#!/usr/bin/env python3
"""Gera a Figura 3 e a Tabela S2 do artigo a partir de estatistica.json.

A figura usa codigos C01..Cnn para manter o grafico legivel; a Tabela S2
mantem o mapeamento completo codigo -> categoria real em UTF-8.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from estilo_figuras import COR, LARGURA_DUPLA, aplicar_estilo, limpar_eixo, salvar  # noqa: E402


RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "docs" / "dados" / "estatistica.json"
SAIDA_FIGURA = RAIZ / "04_artigo" / "figuras" / "fig_top_confusoes"
SAIDA_TABELA = RAIZ / "04_artigo" / "figuras" / "tabela_S2_codigos_categorias.csv"
TOP_N = 15


def _carregar_top_confusoes() -> list[dict]:
    dados = json.loads(ENTRADA.read_text(encoding="utf-8"))
    top_confusoes = dados.get("top_confusoes")
    if not isinstance(top_confusoes, list):
        raise ValueError(f"Campo top_confusoes ausente ou invalido em {ENTRADA}")
    return top_confusoes


def _agregar_pares(top_confusoes: list[dict]) -> list[dict]:
    por_par: dict[tuple[str, str], dict] = {}
    for bloco in top_confusoes:
        modelo = str(bloco.get("modelo", "")).strip() or "modelo_desconhecido"
        for par in bloco.get("pares", []) or []:
            de = str(par.get("de", "")).strip()
            para = str(par.get("para", "")).strip()
            if not de or not para:
                continue
            n = int(par.get("n") or 0)
            chave = (de, para)
            if chave not in por_par:
                por_par[chave] = {"de": de, "para": para, "total": 0, "por_modelo": defaultdict(int)}
            por_par[chave]["total"] += n
            por_par[chave]["por_modelo"][modelo] += n
    return sorted(por_par.values(), key=lambda item: item["total"], reverse=True)


def _codificar_categorias(pares: list[dict]) -> dict[str, str]:
    categorias = sorted({p["de"] for p in pares} | {p["para"] for p in pares})
    return {categoria: f"C{i:02d}" for i, categoria in enumerate(categorias, start=1)}


def _salvar_tabela_s2(codigos: dict[str, str]) -> None:
    SAIDA_TABELA.parent.mkdir(parents=True, exist_ok=True)
    with SAIDA_TABELA.open("w", newline="", encoding="utf-8") as arq:
        escritor = csv.DictWriter(arq, fieldnames=["codigo", "categoria"])
        escritor.writeheader()
        for categoria, codigo in sorted(codigos.items(), key=lambda item: item[1]):
            escritor.writerow({"codigo": codigo, "categoria": categoria})


def _salvar_figura(pares_top: list[dict], codigos: dict[str, str]) -> None:
    rotulos = [f"{codigos[p['de']]} -> {codigos[p['para']]}" for p in pares_top]
    valores = [p["total"] for p in pares_top]

    aplicar_estilo()
    fig, ax = plt.subplots(figsize=(LARGURA_DUPLA, 3.6))
    y = range(len(pares_top))
    ax.barh(y, valores, color=COR["azul"], height=0.7)
    ax.set_yticks(y, labels=rotulos)
    ax.invert_yaxis()
    ax.set_xlabel("Ocorrencias agregadas entre modelos")
    ax.set_ylabel("Par categoria historica -> predicao")
    limpar_eixo(ax, eixo_grade="x")
    for idx, valor in enumerate(valores):
        ax.text(valor + max(valores) * 0.01, idx, str(valor), va="center", fontsize=6)
    fig.tight_layout()
    for caminho in salvar(fig, SAIDA_FIGURA):
        print(f"figura={caminho.relative_to(RAIZ)}")


def main() -> int:
    pares = _agregar_pares(_carregar_top_confusoes())
    if not pares:
        raise RuntimeError("Nenhum par encontrado em estatistica.json.top_confusoes.")
    pares_top = pares[:TOP_N]
    codigos = _codificar_categorias(pares_top)
    _salvar_tabela_s2(codigos)
    _salvar_figura(pares_top, codigos)
    print(f"Tabela S2 gerada: {SAIDA_TABELA.relative_to(RAIZ)} ({len(codigos)} categorias)")
    print(f"Pares plotados: {len(pares_top)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
