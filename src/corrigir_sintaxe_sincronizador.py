#!/usr/bin/env python3
"""Ponto de entrada temporário para a revisão editorial da PR 75."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

RAIZ = Path(__file__).resolve().parents[1]


def main() -> int:
    aplicador = RAIZ / "src" / "aplicar_revisao_editorial_final.py"
    texto = aplicador.read_text(encoding="utf-8")
    texto = texto.replace(
        '    suplemento = """# Material Suplementar — classificação automática de chamados\\n\\n"\n',
        '    suplemento = "# Material Suplementar — classificação automática de chamados\\n\\n"\n',
    )
    aplicador.write_text(texto, encoding="utf-8")

    subprocess.run(
        [sys.executable, "-m", "py_compile", str(aplicador)],
        cwd=RAIZ,
        check=True,
    )
    subprocess.run(
        [sys.executable, str(aplicador)],
        cwd=RAIZ,
        check=True,
    )

    # O workflow permanente é restaurado no próprio checkout. O workflow em
    # execução já foi carregado pelo Actions e não é afetado por esta troca.
    permanente = subprocess.run(
        ["git", "show", "origin/main:.github/workflows/artigo_pdf.yml"],
        cwd=RAIZ,
        check=True,
        capture_output=True,
    ).stdout
    (RAIZ / ".github" / "workflows" / "artigo_pdf.yml").write_bytes(permanente)

    for relativo in (
        ".github/workflows/finalizar_documentacao_pr75.yml",
        "docs/.trigger_revisao_editorial_pr75",
    ):
        caminho = RAIZ / relativo
        if caminho.exists():
            caminho.unlink()

    print("Revisão editorial aplicada e workflow permanente restaurado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
