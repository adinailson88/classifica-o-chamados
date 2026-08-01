#!/usr/bin/env python3
"""Diagnostico READ-ONLY: as linhas de RECLASS_HISTORICO ainda apontam para os
mesmos chamados da aba principal?

MOTIVO: a base cresceu de 13.965 para 14.094 apos a redefinicao do IMPORTRANGE.
Todo o pipeline indexa por `linha_planilha` (numero da linha), nao por
`id_chamado`. Se as linhas novas tiverem sido INSERIDAS no meio (em vez de
acrescentadas no fim), qualquer restauracao feita por numero de linha grava o
valor de um chamado em cima de outro.

Este script compara, para cada entrada do historico, o `id_chamado` registrado
com o `id_chamado` que hoje ocupa aquela linha na aba principal. NAO ESCREVE
NADA.

Saida: total conferido, casados, divergentes, e uma amostra das divergencias.
Codigo de saida 2 se houver qualquer divergencia (para falhar o workflow).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import planilha as pl  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
CONFIG_PADRAO = RAIZ / "config_experimento.json"

I_DATA = 0
I_LINHA = 4
I_ID = 5

COLUNA_ID_PADRAO_1BASED = 2  # B = ID do chamado
FORMATOS_DATA = ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y")


def parse_data(valor):
    s = str(valor or "").strip()
    for fmt in FORMATOS_DATA:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def normalizar_id(valor) -> str:
    s = str(valor or "").strip()
    if not s:
        return ""
    try:
        return str(int(float(s)))
    except (TypeError, ValueError):
        return s


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--aba-historico", default="RECLASS_HISTORICO")
    p.add_argument("--coluna-id", default="ID Chamado",
                   help="Cabecalho da coluna de ID na aba principal "
                        "(mesma convencao de src/reclassificar_validados.py).")
    p.add_argument("--amostra", type=int, default=10)
    args = p.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    ws = sh.worksheet(config["aba_principal"])

    col_id = pl.indice_coluna_por_cabecalho(ws, args.coluna_id, COLUNA_ID_PADRAO_1BASED)
    letra = pl._coluna_letra(col_id)  # noqa: SLF001
    cab = ws.row_values(1) or []
    nome_real = cab[col_id - 1] if len(cab) >= col_id else "(vazio)"
    print(f"aba={config['aba_principal']} | coluna de ID='{nome_real}' ({letra}, {col_id})")

    atual = ws.get_values(f"{letra}:{letra}", value_render_option="UNFORMATTED_VALUE")
    id_por_linha = {i: normalizar_id(v[0] if v else "")
                    for i, v in enumerate(atual, start=1)}
    print(f"linhas com ID na aba principal: {sum(1 for v in id_por_linha.values() if v)}")

    hist = sh.worksheet(args.aba_historico).get_values(
        "A:X", value_render_option="UNFORMATTED_VALUE")
    print(f"{args.aba_historico}: {max(0, len(hist) - 1)} entradas")

    # Ultima entrada por linha (mesma regra do restaurador).
    ultimo: dict[int, tuple] = {}
    for reg in hist[1:]:
        if len(reg) <= I_ID:
            continue
        data = parse_data(reg[I_DATA])
        if data is None:
            continue
        try:
            linha = int(float(str(reg[I_LINHA]).strip()))
        except (TypeError, ValueError):
            continue
        id_hist = normalizar_id(reg[I_ID])
        if not id_hist:
            continue
        if linha not in ultimo or data > ultimo[linha][0]:
            ultimo[linha] = (data, id_hist)

    casados = 0
    divergentes = []
    sem_id_hoje = 0
    for linha, (_, id_hist) in sorted(ultimo.items()):
        id_hoje = id_por_linha.get(linha, "")
        if not id_hoje:
            sem_id_hoje += 1
            continue
        if id_hoje == id_hist:
            casados += 1
        else:
            divergentes.append((linha, id_hist, id_hoje))

    total = casados + len(divergentes)
    print(f"\nlinhas conferidas: {total}")
    print(f"  id casa:      {casados}")
    print(f"  id DIVERGE:   {len(divergentes)}")
    print(f"  sem id hoje:  {sem_id_hoje}")

    if divergentes:
        print(f"\nAmostra de divergencias (ate {args.amostra}):")
        for linha, id_hist, id_hoje in divergentes[:args.amostra]:
            print(f"  linha {linha}: historico={id_hist} | hoje={id_hoje}")
        faixas = defaultdict(int)
        for linha, _, _ in divergentes:
            faixas[linha // 1000 * 1000] += 1
        print("\nDivergencias por faixa de linha:")
        for ini in sorted(faixas):
            print(f"  {ini}-{ini + 999}: {faixas[ini]}")
        print("\nRESULTADO: as linhas NAO estao alinhadas — qualquer escrita "
              "indexada por linha_planilha grava no chamado errado.", file=sys.stderr)
        return 2

    print("\nRESULTADO: alinhamento integro — linha_planilha ainda aponta para "
          "o mesmo chamado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
