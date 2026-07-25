#!/usr/bin/env python3
"""Gera a tabela suplementar S1 (metricas por categoria) a partir de
docs/dados/metricas_por_categoria.json.

Fonte publica, sem credencial de planilha. Nao recalcula nada: so formata
o que ja esta publicado. Le a concordancia contra o historico (nao e
precision/recall/F1 no sentido scikit-learn; este JSON nao tem esse
schema -- ver campos reais abaixo).

Uso:
    python src/exportar_tabela_por_categoria.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "docs" / "dados" / "metricas_por_categoria.json"
SAIDA = RAIZ / "04_artigo" / "figuras" / "tabela_S1_metricas_por_categoria.csv"

CAMPOS = [
    "categoria",
    "qtd_classificados",
    "qtd_true",
    "qtd_false",
    "taxa_concordancia",
    "confianca_media",
    "qtd_abaixo_70",
    "qtd_70_95",
    "qtd_acima_95",
    "atualizado_em",
]


def carregar() -> list[dict]:
    dados = json.loads(ENTRADA.read_text(encoding="utf-8"))
    if not isinstance(dados, list):
        raise ValueError(f"Esperava uma lista em {ENTRADA}, recebi {type(dados)}")
    return dados


def exportar(dados: list[dict]) -> Path:
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    linhas = sorted(dados, key=lambda item: item.get("taxa_concordancia", 0.0))
    with SAIDA.open("w", newline="", encoding="utf-8") as arq:
        escritor = csv.DictWriter(arq, fieldnames=CAMPOS)
        escritor.writeheader()
        for item in linhas:
            escritor.writerow({campo: item.get(campo, "") for campo in CAMPOS})
    return SAIDA


def resumo_extremos(dados: list[dict], n: int = 5) -> None:
    por_concordancia = sorted(
        dados, key=lambda item: item.get("taxa_concordancia", 0.0)
    )
    piores = por_concordancia[:n]
    melhores = por_concordancia[-n:][::-1]
    print(f"\n{n} categorias com MENOR concordância vs. histórico:")
    for item in piores:
        print(
            f"  {item['categoria']}: {item['taxa_concordancia']:.4f} "
            f"(support={item['qtd_classificados']})"
        )
    print(f"\n{n} categorias com MAIOR concordância vs. histórico:")
    for item in melhores:
        print(
            f"  {item['categoria']}: {item['taxa_concordancia']:.4f} "
            f"(support={item['qtd_classificados']})"
        )


def main() -> int:
    dados = carregar()
    caminho = exportar(dados)
    print(f"Tabela S1 gerada: {caminho.relative_to(RAIZ)} ({len(dados)} categorias)")
    print(
        "Aviso metodologico: este JSON reporta concordancia da IA oficial "
        "(Etapa 1) contra a CATEGORIA HISTORICA, nao precision/recall/F1 no "
        "sentido scikit-learn -- o schema publicado nao tem essas metricas "
        "por categoria. Nao afirmar 'F1 por categoria' no texto do artigo "
        "sem gerar esse dado separadamente (ex.: classification_report)."
    )
    resumo_extremos(dados)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
