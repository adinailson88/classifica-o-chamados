#!/usr/bin/env python3
"""Diagnostico READ-ONLY de uso unico (2026-07-25): entender exatamente que
formula/mecanismo popula as colunas A-F (ID..DESCRICAO O.S.M.) da aba
principal, apos o incidente em que escrever um valor literal na coluna C
quebrou o array/spill de uma formula, zerando A-F para ~156 linhas (ja
restaurado via Historico de versoes pelo Adinailson). NAO escreve nada.
Remover este arquivo e o workflow correspondente apos o uso, seguindo o
mesmo padrao ja usado no diagnostico de 2026-07-23 (mojibake)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import planilha as pl  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"


def main() -> int:
    config = json.loads(CONFIG_PADRAO.read_text(encoding="utf-8"))
    sh = pl.abrir_planilha(pl.id_planilha(config), None)
    ws = sh.worksheet(config["aba_principal"])

    print("=== Formulas em A1:F5 (value_render_option=FORMULA) ===")
    formulas = ws.get_values("A1:F5", value_render_option="FORMULA")
    for i, linha in enumerate(formulas, start=1):
        print(f"linha {i}: {linha}")

    print()
    print("=== Formulas em A2, A3, C2, C3, C160, C161 isoladas ===")
    for endereco in ("A2", "A3", "C2", "C3", "C159", "C160", "C161", "A159", "A160", "A161"):
        try:
            val = ws.acell(endereco, value_render_option="FORMULA").value
        except Exception as e:  # noqa: BLE001
            val = f"ERRO: {type(e).__name__}: {e}"
        print(f"{endereco}: {val!r}")

    print()
    print("=== Total de linhas com dado (get_values A:A, UNFORMATTED) ===")
    vals_a = ws.get_values("A:A", value_render_option="UNFORMATTED_VALUE")
    print(f"linhas em A: {len(vals_a)}")

    print()
    print("=== Amostra das primeiras 3 linhas de dado (A:F, UNFORMATTED) ===")
    vals = ws.get_values("A2:F4", value_render_option="UNFORMATTED_VALUE")
    for i, linha in enumerate(vals, start=2):
        print(f"linha {i}: {linha}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
