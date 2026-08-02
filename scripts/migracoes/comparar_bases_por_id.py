#!/usr/bin/env python3
"""Compara duas bases de chamados por id_chamado. READ-ONLY.

MOTIVACAO (2026-08-01): a planilha do experimento tem 14.094 chamados e uma
segunda planilha tem 14.059. O pesquisador afirma que a menor esta correta.
Contar linhas nao explica nada; e preciso saber QUAIS ids sobram para que a
causa apareca (chamado excluido no GLPI, entidade indevida, merge incremental
que reintroduziu registro apagado, recorte por data, etc.).

Indexa por id_chamado, nunca por numero de linha: a fonte do IMPORTRANGE ja
reordenou linhas antes (28/07/2026) e comparar por posicao produz resultado
falso.

As abas sao resolvidas por GID quando informado, porque o gid e o que aparece
na URL e o nome da aba nem sempre e conhecido. Sem gid, usa a primeira aba.

Nenhuma escrita, em nenhuma das duas planilhas. Nenhum texto de chamado no
relatorio: apenas ids e contagens.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import planilha as pl  # noqa: E402


def normalizar_id(valor: Any) -> str:
    """UNFORMATTED_VALUE devolve numero (1693.0); padroniza para string."""
    s = str(valor or "").strip()
    if not s:
        return ""
    try:
        return str(int(float(s)))
    except (TypeError, ValueError):
        return s


def aba_por_gid(sh, gid: int | None):
    """Resolve a aba pelo gid da URL. Sem gid, devolve a primeira."""
    if gid is None:
        return sh.get_worksheet(0)
    for ws in sh.worksheets():
        if int(ws.id) == int(gid):
            return ws
    disponiveis = ", ".join(f"{ws.title}(gid={ws.id})" for ws in sh.worksheets())
    raise SystemExit(f"gid {gid} nao encontrado. Abas: {disponiveis}")


def ler_ids(sh, gid: int | None, coluna: str, cabecalho: bool) -> tuple[list[str], str]:
    ws = aba_por_gid(sh, gid)
    valores = ws.get_values(f"{coluna}:{coluna}",
                            value_render_option="UNFORMATTED_VALUE")
    linhas = valores[1:] if cabecalho else valores
    ids = []
    for linha in linhas:
        v = normalizar_id(linha[0] if linha else "")
        if v:
            ids.append(v)
    return ids, ws.title


def comparar(ids_a: list[str], ids_b: list[str]) -> dict[str, Any]:
    """Logica pura: separa o que e exclusivo de cada lado e o que repete."""
    sa, sb = set(ids_a), set(ids_b)
    so_a = sorted(sa - sb, key=lambda x: (len(x), x))
    so_b = sorted(sb - sa, key=lambda x: (len(x), x))

    def duplicados(ids: list[str]) -> list[str]:
        vistos, dup = set(), set()
        for i in ids:
            (dup if i in vistos else vistos).add(i)
        return sorted(dup)

    return {
        "linhas_a": len(ids_a),
        "linhas_b": len(ids_b),
        "distintos_a": len(sa),
        "distintos_b": len(sb),
        "duplicados_a": duplicados(ids_a),
        "duplicados_b": duplicados(ids_b),
        "em_ambas": len(sa & sb),
        "so_em_a": so_a,
        "so_em_b": so_b,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--planilha-a", required=True, help="ID da planilha A")
    p.add_argument("--gid-a", type=int, default=None)
    p.add_argument("--coluna-a", default="A")
    p.add_argument("--planilha-b", required=True, help="ID da planilha B")
    p.add_argument("--gid-b", type=int, default=None)
    p.add_argument("--coluna-b", default="A")
    p.add_argument("--sem-cabecalho", action="store_true",
                   help="Trata a primeira linha como dado.")
    p.add_argument("--credenciais", default=None)
    p.add_argument("--json", type=Path, default=None,
                   help="Opcional: grava o relatorio. Por padrao so imprime.")
    p.add_argument("--limite-listagem", type=int, default=100)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    cab = not args.sem_cabecalho

    def abrir(pid: str):
        try:
            return pl.abrir_planilha(pid, args.credenciais)
        except Exception as exc:  # noqa: BLE001
            raise SystemExit(
                f"nao foi possivel abrir {pid}: {type(exc).__name__}: {exc}\n"
                "Se for falta de permissao, compartilhe a planilha com o e-mail "
                "da conta de servico (papel de leitor basta).") from exc

    sh_a = abrir(args.planilha_a)
    ids_a, nome_a = ler_ids(sh_a, args.gid_a, args.coluna_a, cab)
    sh_b = abrir(args.planilha_b)
    ids_b, nome_b = ler_ids(sh_b, args.gid_b, args.coluna_b, cab)

    r = comparar(ids_a, ids_b)
    r["planilha_a"] = {"id": args.planilha_a, "aba": nome_a, "coluna": args.coluna_a}
    r["planilha_b"] = {"id": args.planilha_b, "aba": nome_b, "coluna": args.coluna_b}

    print("=== COMPARACAO POR id_chamado ===")
    print(f"  A: aba {nome_a!r} coluna {args.coluna_a} -> "
          f"{r['linhas_a']} linhas, {r['distintos_a']} ids distintos")
    print(f"  B: aba {nome_b!r} coluna {args.coluna_b} -> "
          f"{r['linhas_b']} linhas, {r['distintos_b']} ids distintos")
    print(f"  em ambas : {r['em_ambas']}")
    print(f"  so em A  : {len(r['so_em_a'])}")
    print(f"  so em B  : {len(r['so_em_b'])}")
    if r["duplicados_a"]:
        print(f"  DUPLICADOS em A: {len(r['duplicados_a'])} -> "
              f"{r['duplicados_a'][:20]}")
    if r["duplicados_b"]:
        print(f"  DUPLICADOS em B: {len(r['duplicados_b'])} -> "
              f"{r['duplicados_b'][:20]}")

    lim = args.limite_listagem
    if r["so_em_a"]:
        print(f"\n  IDS SO EM A (ate {lim}):")
        for i in r["so_em_a"][:lim]:
            print(f"    {i}")
    if r["so_em_b"]:
        print(f"\n  IDS SO EM B (ate {lim}):")
        for i in r["so_em_b"][:lim]:
            print(f"    {i}")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(r, ensure_ascii=False, indent=1),
                             encoding="utf-8")
        print(f"\nrelatorio escrito em {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
