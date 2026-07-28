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
    if len({category for category, _ in rows}) != len(rows):
        raise RuntimeError("Há categorias duplicadas na fonte.")
    if sum(quantity for _, quantity in rows) != EXPECTED_TOTAL:
        raise RuntimeError("O total das categorias não corresponde a 13.965 chamados.")

    return sorted(rows, key=lambda item: (-item[1], item[0].casefold()))


def build_appendix(rows: list[tuple[str, int]]) -> str:
    split_at = (len(rows) + 1) // 2
    left = rows[:split_at]
    right = rows[split_at:]

    table_rows: list[str] = []
    for index, (left_category, left_quantity) in enumerate(left):
        if index < len(right):
            right_category, right_quantity = right[index]
            table_rows.append(
                f"| {left_category} | {format_pt_br(left_quantity)} | "
                f"{right_category} | {format_pt_br(right_quantity)} |"
            )
        else:
            table_rows.append(
                f"| {left_category} | {format_pt_br(left_quantity)} |  |  |"
            )

    rows_text = "\n".join(table_rows)
    return f"""{APPENDIX_HEADING}

A Tabela A1 apresenta as 55 categorias históricas utilizadas na classificação
dos 13.965 chamados, ordenadas por frequência decrescente e distribuídas em
dois blocos paralelos para reduzir a extensão do apêndice.

```{{=latex}}
\\scriptsize
\\setlength{{\\tabcolsep}}{{2.5pt}}
\\renewcommand{{\\arraystretch}}{{0.92}}
```

**Tabela A1** Distribuição dos chamados por categoria histórica.

| Categoria histórica | Quantidade | Categoria histórica | Quantidade |
|:---|---:|:---|---:|
{rows_text}
| **Total geral** | **{format_pt_br(EXPECTED_TOTAL)}** |  |  |

*Fonte: elaboração própria a partir do corpus analisado.*

```{{=latex}}
\\normalsize
\\setlength{{\\tabcolsep}}{{6pt}}
\\renewcommand{{\\arraystretch}}{{1}}
```
"""


def main() -> None:
    text = ARTICLE_PATH.read_text(encoding="utf-8")
    start = text.find(APPENDIX_HEADING)
    if start < 0:
        raise RuntimeError("Título do Apêndice A não encontrado.")

    rows = read_distribution()
    corrected = text[:start] + build_appendix(rows)
    ARTICLE_PATH.write_text(corrected, encoding="utf-8")

    if corrected.count(APPENDIX_HEADING) != 1:
        raise RuntimeError("O título do apêndice não aparece exatamente uma vez.")
    if corrected.count("| Categoria histórica | Quantidade | Categoria histórica | Quantidade |") != 1:
        raise RuntimeError("O cabeçalho da tabela não aparece exatamente uma vez.")
    if corrected.count("*Fonte: elaboração própria a partir do corpus analisado.*") != 1:
        raise RuntimeError("A fonte da tabela não aparece exatamente uma vez.")
    if not corrected.rstrip().endswith("\\renewcommand{\\arraystretch}{1}\n```"):
        raise RuntimeError("O fechamento do apêndice não está íntegro.")


if __name__ == "__main__":
    main()
