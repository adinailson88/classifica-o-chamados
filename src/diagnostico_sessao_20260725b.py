#!/usr/bin/env python3
"""Diagnostico READ-ONLY de uso unico (2026-07-25, parte 2): confirmar que
as colunas 'Classificacao IA' (G) e 'Classificacao IA - 2' (O) da aba
principal sao celulas com VALOR literal (escritas pelos scripts de
classificacao), nao formula/IMPORTRANGE -- antes de rodar qualquer correcao
de nomenclatura nelas, dado o incidente anterior nesta mesma sessao (escrita
na coluna C, que e IMPORTRANGE, quebrou o array). NAO escreve nada."""

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

    col_g = pl.indice_coluna_por_cabecalho(ws, "Classificacao IA", 7)
    col_o = pl.indice_coluna_por_cabecalho(ws, "Classificacao IA - 2", 15)
    print(f"coluna 'Classificacao IA' (G) = indice {col_g}")
    print(f"coluna 'Classificacao IA - 2' (O) = indice {col_o}")

    for endereco in ("G1", "G2", "G3", "G160", "G500", "O2", "O160", "O500"):
        try:
            val = ws.acell(endereco, value_render_option="FORMULA").value
        except Exception as e:  # noqa: BLE001
            val = f"ERRO: {type(e).__name__}: {e}"
        print(f"{endereco} (formula): {val!r}")

    print()
    print("=== valores atuais G2:G6, O2:O6 (UNFORMATTED) ===")
    print("G2:G6:", ws.get_values("G2:G6", value_render_option="UNFORMATTED_VALUE"))
    print("O2:O6:", ws.get_values("O2:O6", value_render_option="UNFORMATTED_VALUE"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
