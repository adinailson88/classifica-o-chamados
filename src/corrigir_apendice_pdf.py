#!/usr/bin/env python3
"""Corrige elementos identificados na inspeção visual do PDF da PR 75."""

from __future__ import annotations

import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ARTIGO = RAIZ / "04_artigo" / "artigo_classificacao_chamados_v3.md"
DADOS = RAIZ / "docs" / "dados"


def ler_json(nome: str) -> dict:
    return json.loads((DADOS / nome).read_text(encoding="utf-8"))


def inteiro(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def main() -> int:
    auditoria = ler_json("auditoria_conferencias.json")
    calibracao = ler_json("calibracao.json")
    cont = auditoria["contagens"]
    valid = calibracao["validacao_humana"]

    texto = ARTIGO.read_text(encoding="utf-8")

    # Evita glifo ausente no expoente Unicode do p-valor no XeLaTeX.
    texto = re.sub(
        r"com McNemar \*p\* ≈ [^\.]+\.",
        r"com McNemar ($p \\approx 5{,}70 \\times 10^{-8}$).",
        texto,
        count=1,
    )

    texto = texto.replace(
        "Cada item indica a subseção onde é reportado e o status na\n"
        "data de publicação; **não substitui a reconferência de números antes da\n"
        "submissão** — os status \"Sim\" abaixo atestam que o item é reportado em algum\n"
        "lugar do texto, não que o número citado já foi revalidado contra os JSONs\n"
        "vigentes.",
        "Cada item indica a subseção onde é reportado e o status desta consolidação.\n"
        "Os números foram sincronizados com os JSONs vigentes, mas devem ser\n"
        "revalidados antes da submissão caso ocorra nova materialização dos dados.",
    )
    texto = texto.replace(
        "| Tamanho da amostra e período/corte de consolidação | 3.2 | Sim, mas com data de corte a reconferir |",
        f"| Tamanho da amostra e corte de consolidação | 3.2 | Sim (n = {inteiro(calibracao['total'])}; agregados vigentes) |",
    )
    texto = texto.replace(
        "| Cobertura da validação humana na data de publicação (n e % da base) | 4 (abertura) | Sim, mas desatualizada — ver nota de revalidação de dados |",
        f"| Cobertura da validação humana (n e % da base) | 4 (abertura) | Sim ({inteiro(cont['total_com_alguma_conferencia'])} conferidos; {inteiro(cont['decisoes_travadas'])} decisões; {inteiro(cont['conflitos'])} conflitos) |",
    )

    tabela = f"""| Chamados com ao menos uma conferência (M, N ou P) | {inteiro(cont['total_com_alguma_conferencia'])} |
| Decisões travadas (categoria decidida sem conflito) | {inteiro(cont['decisoes_travadas'])} |
| Casos sem verdade validada | {inteiro(cont['restritos'])} |
| Conflitos entre fontes conferidas | {inteiro(cont['conflitos'])} |
| Comparações válidas da IA oficial contra a verdade decidida | {inteiro(valid['n_conferencia_ia'])} |
| Registros no diagnóstico da conferência GLPI | {inteiro(valid['n_conferencia_glpi'])} |
| Registros com conferência da reclassificação | {inteiro(valid['n_conferencia_reclass'])} |"""
    texto, n = re.subn(
        r"\| Chamados com ao menos uma conferência \(M, N ou P\) \|.*?\| Conferências da coluna P \(CONFERÊNCIA IA - 2\) preenchidas \| 0 \|",
        tabela,
        texto,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise RuntimeError(f"tabela do Apêndice B não localizada: {n}")

    texto = texto.replace(
        "Fonte: elaborado pelos autores (2026). A coluna P (reclassificação\n"
        "conferida) está zerada nesta consolidação — nenhuma reclassificação foi\n"
        "conferida via essa coluna especificamente até o momento.",
        "Fonte: elaborado pelos autores (2026), com base nos agregados vigentes de\n"
        "auditoria e calibração. Não há registro com conferência da reclassificação\n"
        "nesta consolidação.",
    )

    # Mantém o apêndice compacto em uma página própria no PDF.
    texto = texto.replace(
        "\n**Apêndice B — Matriz de decisão M/N/P**",
        "\n\\newpage\n\n**Apêndice B — Matriz de decisão M/N/P**",
    )
    texto = texto.replace("\\newpage\n\n\\newpage", "\\newpage")

    proibidos = [
        "| Decisões travadas (categoria decidida sem conflito) | 9.096 |",
        "| Casos restritos (categoria eliminada, sem decisão travada) | 438 |",
        "| Conflitos (M e N confirmam categorias diferentes) | 0 |",
        "Sim, mas desatualizada",
        "10⁻⁸",
    ]
    encontrados = [x for x in proibidos if x in texto]
    if encontrados:
        raise RuntimeError(f"resíduos do PDF ainda presentes: {encontrados}")

    ARTIGO.write_text(texto, encoding="utf-8")
    print("apêndice e notação científica corrigidos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
