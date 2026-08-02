#!/usr/bin/env python3
"""Remove levas duplicadas de uma aba CLASSIF__<modelo>, preservando a original.

MOTIVACAO (2026-08-02): o run agendado das 12:16 do multimodelo foi cancelado
no meio e gravou uma SEGUNDA leva de predicoes em CLASSIF__extra_trees, que
ficou com 28.152 registros para 14.094 chamados. Como a leitura monta
{id_chamado: categoria}, o registro mais recente vence, e a leva nova foi
treinada com `memoria_validada=13703 (peso 3)`, isto e, com a conferencia
humana dentro do treino. O acerto validado do modelo saltou de 0,7958 para
0,9816, que e vazamento, nao desempenho.

Rematerializar do zero NAO resolve: hoje qualquer execucao nasce com a mesma
memoria validada no treino. A saida e descartar a leva contaminada e manter a
de 01/08, feita quando a memoria tinha 1.927 decisoes.

CRITERIO: as levas sao separadas pela coluna `data` (carimbo da execucao).
Mantem-se a leva MAIS ANTIGA por padrao, que e a original. Ids que so existem
nas levas descartadas ficam SEM predicao, o que e o estado correto: e melhor
declarar ausencia do que publicar predicao contaminada.

ESCOPO ESTRITO: le e reescreve UMA aba CLASSIF__<modelo>. Nunca abre a aba
principal. Sem --aplicar, e dry-run.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import planilha as pl  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
CONFIG_PADRAO = RAIZ / "config_experimento.json"

# Indices 0-based em CLASSIF__<modelo> (ver classificacao_multimodelo.py:192).
I_ID = 2
I_DATA = 10


def agrupar_por_leva(linhas: list[list[Any]], i_data: int = I_DATA
                     ) -> dict[str, list[int]]:
    """{carimbo de data: [indices das linhas]}. Logica pura, testavel."""
    levas: dict[str, list[int]] = defaultdict(list)
    for pos, linha in enumerate(linhas):
        carimbo = str(linha[i_data] or "").strip() if len(linha) > i_data else ""
        levas[carimbo].append(pos)
    return dict(levas)


def escolher_leva(levas: dict[str, list[int]], manter: str | None = None) -> str:
    """Qual leva preservar. Sem --manter, a de MENOR carimbo (a original).

    Os carimbos vem no formato dd/mm/aaaa HH:MM, que nao ordena como texto.
    A ordenacao e feita por (ano, mes, dia, hora, minuto) quando o formato bate,
    e cai para ordem textual quando nao bate, para nunca lancar excecao aqui.
    """
    if manter is not None:
        if manter not in levas:
            raise SystemExit(
                f"leva {manter!r} nao existe. Disponiveis: {sorted(levas)}")
        return manter

    def chave(carimbo: str):
        try:
            data, hora = carimbo.split(" ")
            d, m, a = data.split("/")
            hh, mm = hora.split(":")[:2]
            return (0, int(a), int(m), int(d), int(hh), int(mm))
        except (ValueError, IndexError):
            return (1, carimbo)

    return sorted(levas, key=chave)[0]


def resumir(linhas: list[list[Any]], levas: dict[str, list[int]],
            escolhida: str) -> dict[str, Any]:
    ids_por_leva = {}
    for carimbo, posicoes in levas.items():
        ids_por_leva[carimbo] = {
            str(linhas[p][I_ID] or "").strip() for p in posicoes
            if len(linhas[p]) > I_ID}
    mantidos = ids_por_leva.get(escolhida, set())
    perdidos: set[str] = set()
    for carimbo, ids in ids_por_leva.items():
        if carimbo != escolhida:
            perdidos |= (ids - mantidos)
    return {
        "linhas_totais": len(linhas),
        "levas": {c: len(p) for c, p in sorted(levas.items())},
        "leva_mantida": escolhida,
        "linhas_mantidas": len(levas[escolhida]),
        "linhas_removidas": len(linhas) - len(levas[escolhida]),
        "ids_na_leva_mantida": len(mantidos),
        "ids_que_ficam_sem_predicao": sorted(perdidos),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--modelo", required=True,
                   help="Nome do modelo, ex.: extra_trees")
    p.add_argument("--manter", default=None,
                   help="Carimbo da leva a preservar. Sem isso, a mais antiga.")
    p.add_argument("--aplicar", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    template = config["multimodelo"]["aba_classificacao"]
    aba = template.replace("{modelo}", args.modelo)

    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    ws = sh.worksheet(aba)
    valores = ws.get_values("A:K", value_render_option="UNFORMATTED_VALUE")
    if len(valores) < 2:
        raise SystemExit(f"{aba} tem menos de 2 linhas; nada a fazer.")
    cabecalho, linhas = valores[0], valores[1:]

    levas = agrupar_por_leva(linhas)
    escolhida = escolher_leva(levas, args.manter)
    r = resumir(linhas, levas, escolhida)

    print(f"aba={aba}")
    print(f"  linhas de dados : {r['linhas_totais']}")
    print(f"  levas encontradas: {len(r['levas'])}")
    for carimbo, n in r["levas"].items():
        marca = "  <== MANTER" if carimbo == escolhida else ""
        print(f"     {carimbo!r:<26} {n:>7} linhas{marca}")
    print(f"  linhas mantidas : {r['linhas_mantidas']}")
    print(f"  linhas removidas: {r['linhas_removidas']}")
    print(f"  ids na leva mantida: {r['ids_na_leva_mantida']}")
    sem = r["ids_que_ficam_sem_predicao"]
    print(f"  ids que ficam SEM predicao: {len(sem)}")
    if sem:
        print(f"     {', '.join(sem[:30])}{' ...' if len(sem) > 30 else ''}")

    if len(levas) == 1:
        print("\nSo existe uma leva; nada a remover.")
        return 0

    if not args.aplicar:
        print("\nDRY-RUN: nada foi gravado. Rode com --aplicar para reescrever.")
        return 0

    mantidas = [linhas[p] for p in sorted(levas[escolhida])]
    pl.escrever_aba(sh, aba, cabecalho, mantidas)
    print(f"\nOK: {aba} reescrita com {len(mantidas)} linha(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
