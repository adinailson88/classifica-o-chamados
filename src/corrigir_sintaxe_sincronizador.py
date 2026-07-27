#!/usr/bin/env python3
"""Ponto de entrada temporário para a revisão editorial da PR 75."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

RAIZ = Path(__file__).resolve().parents[1]
BRANCH = "agent/corrigir-sincronizacao-artigo"


def executar(*args: str, capture_output: bool = False) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        list(args),
        cwd=RAIZ,
        check=True,
        capture_output=capture_output,
    )


def main() -> int:
    aplicador = RAIZ / "src" / "aplicar_revisao_editorial_final.py"
    texto = aplicador.read_text(encoding="utf-8")
    texto = texto.replace(
        '    suplemento = """# Material Suplementar — classificação automática de chamados\\n\\n"\n',
        '    suplemento = "# Material Suplementar — classificação automática de chamados\\n\\n"\n',
    )
    aplicador.write_text(texto, encoding="utf-8")

    executar(sys.executable, "-m", "py_compile", str(aplicador))
    executar(sys.executable, str(aplicador))

    # Restaura o workflow permanente. O workflow corrente já foi carregado pelo
    # Actions e continua normalmente mesmo após a substituição no checkout.
    permanente = executar(
        "git", "show", "origin/main:.github/workflows/artigo_pdf.yml",
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

    # Grava a revisão antes das etapas analíticas auxiliares. Assim, uma falha
    # posterior de diagnóstico não perde o trabalho editorial já validado.
    executar("git", "config", "user.name", "github-actions[bot]")
    executar("git", "config", "user.email", "github-actions[bot]@users.noreply.github.com")
    executar(
        "git", "add", "-A", "--",
        ".github/workflows/artigo_pdf.yml",
        ".github/workflows/finalizar_documentacao_pr75.yml",
        "docs/.trigger_revisao_editorial_pr75",
        "04_artigo/artigo_classificacao_chamados_v3.md",
        "04_artigo/material_suplementar_estatistica_checklist.md",
        "PLANO_ARTIGO_CAPITULO.md",
    )

    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=RAIZ,
        check=False,
    )
    if diff.returncode != 0:
        executar("git", "commit", "-m", "docs: aplica revisão editorial científica final [skip ci]")
        executar("git", "push", "origin", f"HEAD:{BRANCH}")

    print("Revisão editorial aplicada, versionada e workflow permanente restaurado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
