#!/usr/bin/env python3
"""Restaura a coluna O (Classificacao IA - 2) a partir da trilha RECLASS_HISTORICO.

CONTEXTO (incidente de 2026-08-01): a coluna O foi apagada manualmente para
permitir que src/reclassificar_validados.py reprocessasse o BERTimbau (esse
script so atua em linhas com O VAZIA -- a ausencia de um flag --refazer e uma
propriedade de seguranca, nao uma limitacao). O efeito colateral nao previsto:
a coluna P (CONFERENCIA IA - 2) guarda o veredito humano SOBRE O VALOR DE O.
Ao repreencher O com predicoes novas, os vereditos de P passaram a se referir a
predicoes que o avaliador nunca revisou. Consequencia medida em
docs/dados/avaliacao_bertimbau_holdout.json:

    decididos  8.895 -> 1.927
    conflitos    201 -> 7.469

Este script desfaz isso reconstruindo O a partir de RECLASS_HISTORICO, que e
append-only e registra cada gravacao de O (coluna 'categoria_depois', indice 10).
Para cada linha_planilha toma a ULTIMA entrada ANTERIOR ao corte (--corte),
que por padrao e o inicio de 2026-08-01.

ESCOPO ESTRITO:
- So escreve na coluna 'Classificacao IA - 2' da aba principal.
- NUNCA escreve em 'CATEGORIA COMPLETA' (C) -- e IMPORTRANGE; ver o incidente
  de 2026-07-25 tratado em migrar_categorias_canonicas.py.
- Guarda extra: recusa prosseguir se a coluna alvo contiver formula.
- Nao toca em G, M, N, P, Q nem em qualquer outra coluna.

Sem --aplicar = dry-run (so relata o que faria).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import planilha as pl  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
CONFIG_PADRAO = RAIZ / "config_experimento.json"

ABA_HISTORICO_PADRAO = "RECLASS_HISTORICO"
COLUNA_ALVO = "Classificacao IA - 2"
COLUNA_ALVO_DEFAULT_1BASED = 15
COLUNAS_PROIBIDAS = {"categoria completa", "categoria compelta"}

# Indices 0-based em RECLASS_HISTORICO (ver cab_historico em
# src/reclassificar_validados.py -- manter em sincronia).
I_DATA = 0
I_LINHA = 4
I_CATEGORIA_DEPOIS = 10

FORMATOS_DATA = ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y")


def parse_data(valor: Any) -> datetime | None:
    s = str(valor or "").strip()
    if not s:
        return None
    for fmt in FORMATOS_DATA:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--corte", default="01/08/2026 00:00",
                   help="So considera entradas ANTERIORES a esta data/hora "
                        "(dd/mm/aaaa hh:mm). Padrao: 01/08/2026 00:00.")
    p.add_argument("--aba-historico", default=ABA_HISTORICO_PADRAO)
    p.add_argument("--aplicar", action="store_true",
                   help="Sem isso, e dry-run (nada e gravado).")
    return p.parse_args()


def ultimo_valor_por_linha(valores: list[list[Any]], corte: datetime
                           ) -> tuple[dict[int, str], dict[str, int]]:
    """Para cada linha_planilha, a categoria da entrada mais recente < corte."""
    melhor: dict[int, tuple[datetime, str]] = {}
    diag = defaultdict(int)

    for reg in valores[1:]:
        if len(reg) <= I_CATEGORIA_DEPOIS:
            diag["linha_curta"] += 1
            continue
        data = parse_data(reg[I_DATA])
        if data is None:
            diag["data_invalida"] += 1
            continue
        if data >= corte:
            diag["posterior_ao_corte"] += 1
            continue
        try:
            linha = int(float(str(reg[I_LINHA]).strip()))
        except (TypeError, ValueError):
            diag["linha_invalida"] += 1
            continue
        categoria = str(reg[I_CATEGORIA_DEPOIS] or "").strip()
        if not categoria:
            diag["categoria_vazia"] += 1
            continue
        anterior = melhor.get(linha)
        if anterior is None or data > anterior[0]:
            melhor[linha] = (data, categoria)
        diag["consideradas"] += 1

    return {ln: cat for ln, (_, cat) in melhor.items()}, dict(diag)


def confirmar_nao_e_formula(ws, col_1based: int, linhas_amostra: list[int]) -> bool:
    letra = pl._coluna_letra(col_1based)  # noqa: SLF001
    for linha in linhas_amostra:
        try:
            val = ws.acell(f"{letra}{linha}", value_render_option="FORMULA").value
        except Exception:  # noqa: BLE001
            continue
        if isinstance(val, str) and val.startswith("="):
            print(f"ABORTADO: {letra}{linha} contem formula ({val!r}) — "
                  "esta coluna nao e segura para escrita literal.", file=sys.stderr)
            return False
    return True


def main() -> int:
    args = parse_args()

    corte = parse_data(args.corte)
    if corte is None:
        print(f"ABORTADO: --corte invalido: {args.corte!r}", file=sys.stderr)
        return 1

    if COLUNA_ALVO.strip().casefold() in COLUNAS_PROIBIDAS:
        print("ABORTADO: coluna alvo esta na lista de proibidas.", file=sys.stderr)
        return 1

    config = json.loads(args.config.read_text(encoding="utf-8"))
    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    ws = sh.worksheet(config["aba_principal"])

    col_o = pl.indice_coluna_por_cabecalho(ws, COLUNA_ALVO, COLUNA_ALVO_DEFAULT_1BASED)
    letra_o = pl._coluna_letra(col_o)  # noqa: SLF001
    cabecalho_real = (ws.row_values(1) or [])
    nome_real = cabecalho_real[col_o - 1] if len(cabecalho_real) >= col_o else "(vazio)"
    print(f"aba={config['aba_principal']} | coluna alvo='{nome_real}' ({letra_o}, {col_o})")

    if pl.normalizar_cabecalho(nome_real) in {pl.normalizar_cabecalho(x)
                                              for x in COLUNAS_PROIBIDAS}:
        print(f"ABORTADO: a coluna {letra_o} e '{nome_real}' — nunca escrever nela.",
              file=sys.stderr)
        return 1

    try:
        hist = sh.worksheet(args.aba_historico).get_values(
            "A:X", value_render_option="UNFORMATTED_VALUE")
    except Exception as exc:  # noqa: BLE001
        print(f"ABORTADO: falha ao ler {args.aba_historico}: "
              f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"{args.aba_historico}: {max(0, len(hist) - 1)} entradas | corte < {args.corte}")

    restaurar, diag = ultimo_valor_por_linha(hist, corte)
    print(f"diagnostico do historico: {diag}")
    print(f"linhas com valor restauravel: {len(restaurar)}")
    if not restaurar:
        print("Nada a restaurar.", file=sys.stderr)
        return 1

    atuais_col = ws.get_values(f"{letra_o}:{letra_o}",
                               value_render_option="UNFORMATTED_VALUE")
    atual_por_linha = {i: str(v[0]).strip() if v else ""
                       for i, v in enumerate(atuais_col, start=1)}

    mudar = {ln: cat for ln, cat in restaurar.items()
             if atual_por_linha.get(ln, "") != cat}
    iguais = len(restaurar) - len(mudar)
    vazias_agora = sum(1 for ln in mudar if not atual_por_linha.get(ln, ""))
    sobrescreve = len(mudar) - vazias_agora

    print(f"ja corretas (sem acao): {iguais}")
    print(f"a restaurar: {len(mudar)}  (vazias hoje: {vazias_agora} | "
          f"sobrescreve valor atual: {sobrescreve})")

    exemplos = sorted(mudar)[:5]
    for ln in exemplos:
        print(f"  linha {ln}: {atual_por_linha.get(ln, '')!r} -> {mudar[ln]!r}")

    if not args.aplicar:
        print("\nDRY-RUN: nada gravado. Rode com --aplicar para restaurar.")
        return 0

    if not confirmar_nao_e_formula(ws, col_o, exemplos or [2]):
        return 1

    gravadas = pl.escrever_coluna_por_linha(ws, col_o, mudar)
    print(f"OK: {gravadas} celula(s) restaurada(s) na coluna {letra_o}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
