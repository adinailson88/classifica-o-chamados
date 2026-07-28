from __future__ import annotations

import csv
from pathlib import Path

ARTICLE_PATH = Path("04_artigo/artigo_classificacao_chamados_v3.md")
SOURCE_PATH = Path("04_artigo/figuras/tabela_S1_metricas_por_categoria.csv")
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

    total = sum(quantity for _, quantity in rows)
    if total != EXPECTED_TOTAL:
        raise RuntimeError(f"Total esperado {EXPECTED_TOTAL}, encontrado {total}.")

    return sorted(rows, key=lambda item: (-item[1], item[0].casefold()))


def build_four_column_table(rows: list[tuple[str, int]]) -> str:
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
    return f"""```{{=latex}}
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
```"""


def main() -> None:
    text = ARTICLE_PATH.read_text(encoding="utf-8")

    old_intro = (
        "A Tabela A1 apresenta as 55 categorias históricas utilizadas na classificação\n"
        "dos 13.965 chamados, ordenadas por frequência decrescente."
    )
    new_intro = (
        "A Tabela A1 apresenta as 55 categorias históricas utilizadas na classificação\n"
        "dos 13.965 chamados, ordenadas por frequência decrescente e distribuídas em\n"
        "dois blocos paralelos para reduzir a extensão do apêndice."
    )
    if old_intro not in text:
        raise RuntimeError("Texto introdutório do Apêndice A não encontrado.")

    start_marker = "```{=latex}\n\\small\n```\n\n**Tabela A1** Distribuição dos chamados por categoria histórica."
    end_marker = "```{=latex}\n\\normalsize\n```"
    start = text.find(start_marker)
    if start < 0:
        raise RuntimeError("Início da tabela atual não encontrado.")
    end = text.find(end_marker, start)
    if end < 0:
        raise RuntimeError("Fim da tabela atual não encontrado.")
    end += len(end_marker)

    rows = read_distribution()
    replacement = build_four_column_table(rows)
    text = text.replace(old_intro, new_intro, 1)
    text = text[:start] + replacement + text[end:]
    ARTICLE_PATH.write_text(text, encoding="utf-8")

    if text.count("| Categoria histórica | Quantidade | Categoria histórica | Quantidade |") != 1:
        raise RuntimeError("Cabeçalho de quatro colunas não foi inserido corretamente.")
    if "| **Total geral** | **13.965** |  |  |" not in text:
        raise RuntimeError("Total geral não foi inserido corretamente.")
    if text.count("| **Total** | **13.965** |") != 0:
        raise RuntimeError("A tabela antiga ainda está presente.")


if __name__ == "__main__":
    main()
