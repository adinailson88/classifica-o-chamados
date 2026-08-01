#!/usr/bin/env python3
"""Diagnostico READ-ONLY: despeja o estado real da aba principal, sem inferencia.

Motivo: as conclusoes sobre desalinhamento entre as colunas IMPORTRANGE (A:F) e
as colunas literais (G, M, N, O, P, Q) foram INFERIDAS a partir de contadores
agregados. Este script mostra o dado cru para que a conclusao possa ser
confirmada ou descartada olhando a planilha.

Nao escreve nada. Reporta:
  1. O cabecalho completo com letra e indice de cada coluna (revela colunas
     ocultas, deslocadas ou renomeadas -- ocultar no Sheets NAO esconde da API,
     mas pode ter deslocado posicoes se colunas foram inseridas/removidas).
  2. Quais colunas contem FORMULA (identifica de fato o alcance do IMPORTRANGE,
     em vez de assumir A:F).
  3. Amostra de linhas em conflito (M='Correto' e N='Correto' com C != G), lado
     a lado, para inspecao visual.
  4. Amostra de linhas sem conflito, para comparacao.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import planilha as pl  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
CONFIG_PADRAO = RAIZ / "config_experimento.json"

ALVOS = [
    ("ID Chamado", ("ID Chamado", "ID"), 1),
    ("CATEGORIA COMPLETA", ("CATEGORIA COMPLETA",), 3),
    ("Classificacao IA", ("Classificacao IA", "Classificação IA"), 7),
    ("CONFERENCIA GLPI", ("CONFERENCIA GLPI", "CONFERÊNCIA GLPI"), 13),
    ("CONFERENCIA IA", ("CONFERENCIA IA", "CONFERÊNCIA IA"), 14),
    ("Classificacao IA - 2", ("Classificacao IA - 2", "Classificação IA - 2"), 15),
    ("CONFERENCIA IA - 2", ("CONFERENCIA IA - 2", "CONFERÊNCIA IA - 2"), 16),
    ("CATEGORIA CORRETA MANUAL", ("CATEGORIA CORRETA MANUAL",), 17),
]


def corta(valor, n=42):
    s = str(valor or "").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--amostra", type=int, default=12)
    args = p.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    ws = sh.worksheet(config["aba_principal"])
    print(f"aba={config['aba_principal']} | linhas={ws.row_count} | colunas={ws.col_count}")

    # ---------- 1. Cabecalho real ----------
    cab = ws.row_values(1) or []
    print(f"\n=== CABECALHO ({len(cab)} colunas) ===")
    for i, nome in enumerate(cab, start=1):
        print(f"  {pl._coluna_letra(i):>3} ({i:>2}): {nome!r}")  # noqa: SLF001

    # ---------- 2. Quais colunas sao formula ----------
    print("\n=== FORMULA vs VALOR LITERAL (linha 2) ===")
    try:
        formulas = ws.get_values("A2:Z2", value_render_option="FORMULA")
        linha_f = formulas[0] if formulas else []
        for i, val in enumerate(linha_f, start=1):
            if i > len(cab):
                break
            s = str(val or "")
            tipo = "FORMULA" if s.startswith("=") else "literal"
            print(f"  {pl._coluna_letra(i):>3} ({i:>2}) {tipo:>7}: "  # noqa: SLF001
                  f"{corta(cab[i-1], 28):<28} {corta(s, 40)}")
    except Exception as exc:  # noqa: BLE001
        print(f"  falha ao ler formulas: {type(exc).__name__}: {exc}")

    # ---------- 3. Indices resolvidos ----------
    idx = {}
    print("\n=== COLUNAS RESOLVIDAS POR NOME ===")
    for rotulo, nomes, padrao in ALVOS:
        c = pl.localizar_coluna(cab, nomes, padrao)
        idx[rotulo] = c
        achou = "por nome" if c != padrao or (len(cab) >= c and cab[c-1]) else "PADRAO (nao achou)"
        print(f"  {rotulo:<26} -> {pl._coluna_letra(c)} ({c})  [{achou}]")  # noqa: SLF001

    # ---------- 4. Amostras ----------
    bloco = ws.get_values("A:Q", value_render_option="UNFORMATTED_VALUE")

    def cel(linha, c1):
        i = c1 - 1
        return str(linha[i] or "").strip() if len(linha) > i else ""

    conflito, ok = [], []
    n_cg = n_cg_igual = 0          # C vs G, onde ambos preenchidos
    n_co = n_co_igual = 0          # C vs O, onde ambos preenchidos
    n_m_ok = n_m_ok_c_eq_o = 0     # M='Correto': C bate com O?
    for pos, linha in enumerate(bloco[1:], start=2):
        m = cel(linha, idx["CONFERENCIA GLPI"]).casefold()
        n = cel(linha, idx["CONFERENCIA IA"]).casefold()
        c = cel(linha, idx["CATEGORIA COMPLETA"])
        g = cel(linha, idx["Classificacao IA"])
        o = cel(linha, idx["Classificacao IA - 2"])
        if c and g:
            n_cg += 1
            n_cg_igual += (c == g)
        if c and o:
            n_co += 1
            n_co_igual += (c == o)
        if m == "correto" and c and o:
            n_m_ok += 1
            n_m_ok_c_eq_o += (c == o)
        if m == "correto" and n == "correto":
            (conflito if c != g else ok).append((pos, linha))

    def taxa(a, b):
        return f"{a}/{b} = {(100.0 * a / b if b else 0):.1f}%"

    print("\n=== TAXAS DE CONCORDANCIA (diagnostico de alinhamento) ===")
    print(f"  C == G (historico vs IA):   {taxa(n_cg_igual, n_cg)}")
    print(f"  C == O (historico vs IA-2): {taxa(n_co_igual, n_co)}")
    print(f"  C == O onde M='Correto':    {taxa(n_m_ok_c_eq_o, n_m_ok)}")
    print("  Referencia: a concordancia historica do LSTM ficava entre 67% e 71%.")
    print("  Uma taxa C==G MUITO abaixo disso indica que G nao pertence mais a")
    print("  mesma linha que C (coluna literal que nao acompanhou o IMPORTRANGE).")

    print(f"\n=== M='Correto' E N='Correto' ===")
    print(f"  com C != G (conflito): {len(conflito)}")
    print(f"  com C == G (coerente): {len(ok)}")

    def mostrar(titulo, amostras):
        print(f"\n--- {titulo} (ate {args.amostra}) ---")
        for pos, linha in amostras[: args.amostra]:
            print(f"  linha {pos} | ID={cel(linha, idx['ID Chamado'])}")
            print(f"      C  (histórico) = {corta(cel(linha, idx['CATEGORIA COMPLETA']), 60)}")
            print(f"      G  (IA)        = {corta(cel(linha, idx['Classificacao IA']), 60)}")
            print(f"      O  (IA-2)      = {corta(cel(linha, idx['Classificacao IA - 2']), 60)}")
            print(f"      M={cel(linha, idx['CONFERENCIA GLPI'])!r} "
                  f"N={cel(linha, idx['CONFERENCIA IA'])!r} "
                  f"P={cel(linha, idx['CONFERENCIA IA - 2'])!r} "
                  f"Q={corta(cel(linha, idx['CATEGORIA CORRETA MANUAL']), 30)!r}")

    mostrar("CONFLITO: M e N Corretos, mas C != G", conflito)
    mostrar("COERENTE: M e N Corretos, C == G", ok)

    print("\nNada foi escrito.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
