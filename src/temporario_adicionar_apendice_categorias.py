from __future__ import annotations

import csv
from pathlib import Path

ARTICLE_PATH = Path("04_artigo/artigo_classificacao_chamados_v3.md")
SOURCE_PATH = Path("04_artigo/figuras/tabela_S1_metricas_por_categoria.csv")
APPENDIX_HEADING = "**APÊNDICE A — DISTRIBUIÇÃO DAS CATEGORIAS HISTÓRICAS DO CORPUS**"
EXPECTED_CATEGORIES = 55
EXPECTED_TOTAL = 13_965


def format_pt_br(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def read_distribution() -> list[tuple[str, int]]:
    with SOURCE_PATH.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = [
            (row["categoria"].strip(), int(row["support"]))
            for row in reader
            if row.get("categoria") and row.get("support")
        ]

    if len(rows) != EXPECTED_CATEGORIES:
        raise RuntimeError(
            f"Esperadas {EXPECTED_CATEGORIES} categorias, encontradas {len(rows)}."
        )

    total = sum(quantity for _, quantity in rows)
    if total != EXPECTED_TOTAL:
        raise RuntimeError(
            f"Total esperado {EXPECTED_TOTAL}, encontrado {total}."
        )

    if len({category for category, _ in rows}) != len(rows):
        raise RuntimeError("Há categorias duplicadas na fonte.")

    return sorted(rows, key=lambda item: (-item[1], item[0].casefold()))


def build_appendix(rows: list[tuple[str, int]]) -> str:
    table_rows = "\n".join(
        f"| {category} | {format_pt_br(quantity)} |"
        for category, quantity in rows
    )

    return f"""
```{{=latex}}
\\FloatBarrier
\\clearpage
```

{APPENDIX_HEADING}

A Tabela A1 apresenta as 55 categorias históricas utilizadas na classificação
dos 13.965 chamados, ordenadas por frequência decrescente.

```{{=latex}}
\\small
```

**Tabela A1** Distribuição dos chamados por categoria histórica.

| Categoria histórica | Quantidade de chamados |
|:---|---:|
{table_rows}
| **Total** | **{format_pt_br(EXPECTED_TOTAL)}** |

*Fonte: elaboração própria a partir do corpus analisado.*

```{{=latex}}
\\normalsize
```
"""


def main() -> None:
    text = ARTICLE_PATH.read_text(encoding="utf-8")

    if APPENDIX_HEADING in text:
        raise RuntimeError("O Apêndice A já existe no artigo.")

    anchor = (
        "A base é dinâmica, pois novos chamados continuam a ser incorporados e a\n"
        "taxonomia institucional pode ser revisada ao longo do tempo. Os\n"
        "resultados da Seção 4 referem-se ao corpus descrito acima."
    )
    replacement = (
        f"{anchor} A distribuição completa dos chamados entre as 55 categorias\n"
        "históricas é apresentada no Apêndice A."
    )
    if anchor not in text:
        raise RuntimeError("Trecho de referência da Subseção 3.2 não encontrado.")

    rows = read_distribution()
    text = text.replace(anchor, replacement, 1)
    text = text.rstrip() + "\n" + build_appendix(rows)
    ARTICLE_PATH.write_text(text, encoding="utf-8")

    if text.count(APPENDIX_HEADING) != 1:
        raise RuntimeError("O título do apêndice não foi inserido exatamente uma vez.")
    if "| **Total** | **13.965** |" not in text:
        raise RuntimeError("A linha de total não foi inserida corretamente.")


if __name__ == "__main__":
    main()
