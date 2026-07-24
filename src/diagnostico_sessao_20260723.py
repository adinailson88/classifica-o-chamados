#!/usr/bin/env python3
"""Diagnostico READ-ONLY de duas pendencias tecnicas encontradas em 23/07/2026
ao preparar o artigo (ver PLANO_ARTIGO_CAPITULO.md, "Estado desta rodada"):

1. Mojibake nos nomes de categoria lidos das abas CLASSIF__<modelo> por
   src/analise_estatistica.py (contamina estatistica.json/top_confusoes,
   cruzamento_taxonomia.json, confusao_historico_ia.json).
2. total_reclassificado do Random Forest (RECLASS__random_forest) excede o
   tamanho da base -- suspeita de linhas duplicadas / falha silenciosa em
   linhas_ja_reclass().

Nao escreve na planilha. Nao versiona texto de chamado (so nomes de
categoria, ja publicos nos JSONs do painel, e contagens agregadas). Uso
unico, para rodar via workflow_dispatch com o secret GCP_SA_KEY existente e
depois ser removido do repositorio.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import planilha as pl  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"


def diag_mojibake(sh, config):
    print("=" * 70)
    print("DIAGNOSTICO 1: mojibake em CLASSIF__<modelo>")
    print("=" * 70)
    mm = config["multimodelo"]
    template = mm["aba_classificacao"]
    modelo = "linear_svc"
    aba = template.replace("{modelo}", modelo)
    try:
        ws = sh.worksheet(aba)
        vals = ws.get_values("A:F", value_render_option="UNFORMATTED_VALUE")
    except Exception as e:  # noqa: BLE001
        print(f"falha ao ler {aba}: {type(e).__name__}: {e}")
        return
    print(f"aba={aba} linhas={len(vals)}")
    achou = 0
    for r in vals[1:200]:
        if len(r) > 3 and "�" in str(r[3]):
            print(f"linha={r[1] if len(r) > 1 else '?'} col_D(cat_original) repr={str(r[3])!r}")
            achou += 1
        if achou >= 3:
            break
    if achou == 0:
        print("nenhuma ocorrencia de mojibake nas primeiras 200 linhas amostradas.")

    # Compara a mesma linha na aba principal (coluna C = CATEGORIA COMPLETA)
    aba_principal = config["aba_principal"]
    ws_p = sh.worksheet(aba_principal)
    cab = ws_p.row_values(1)
    col_hist = pl.localizar_coluna(cab, ("CATEGORIA COMPLETA",), 3)
    for r in vals[1:200]:
        if len(r) > 3 and "�" in str(r[3]):
            ln = r[1]
            try:
                ln_i = int(ln)
                valor_principal = ws_p.cell(ln_i, col_hist).value
                print(f"mesma linha ({ln}) na aba principal, coluna C: repr={str(valor_principal)!r}")
            except Exception as e:  # noqa: BLE001
                print(f"nao foi possivel ler a aba principal na linha {ln}: {e}")
            break


def diag_random_forest_duplicado(sh, config):
    print("=" * 70)
    print("DIAGNOSTICO 2: duplicacao em RECLASS__random_forest")
    print("=" * 70)
    mm = config["multimodelo"]
    template = mm["aba_reclassificacao"]
    aba = template.replace("{modelo}", "random_forest")
    try:
        ws = sh.worksheet(aba)
        vals = ws.get_values("C:C", value_render_option="UNFORMATTED_VALUE")
    except Exception as e:  # noqa: BLE001
        print(f"falha ao ler {aba}: {type(e).__name__}: {e}")
        return
    linhas = [str(r[0]).strip() for r in vals[1:] if r and str(r[0]).strip()]
    total = len(linhas)
    cont = Counter(linhas)
    dup = {k: v for k, v in cont.items() if v > 1}
    print(f"aba={aba} total_linhas={total} linhas_unicas={len(cont)} linhas_duplicadas_distintas={len(dup)}")
    if dup:
        exemplos = list(dup.items())[:5]
        print(f"exemplos de linha duplicada (linha: contagem): {exemplos}")
        print(f"soma de ocorrencias extras (total - unicas) = {total - len(cont)}")
    else:
        print("nenhuma linha duplicada encontrada por valor da coluna C.")

    # Compara com outro modelo para referencia (mesma logica, mesma base)
    aba_ref = template.replace("{modelo}", "linear_svc")
    try:
        ws_ref = sh.worksheet(aba_ref)
        vals_ref = ws_ref.get_values("C:C", value_render_option="UNFORMATTED_VALUE")
        linhas_ref = [str(r[0]).strip() for r in vals_ref[1:] if r and str(r[0]).strip()]
        print(f"referencia ({aba_ref}): total_linhas={len(linhas_ref)} linhas_unicas={len(set(linhas_ref))}")
    except Exception as e:  # noqa: BLE001
        print(f"falha ao ler {aba_ref} para referencia: {type(e).__name__}: {e}")


def main() -> int:
    with CONFIG_PADRAO.open(encoding="utf-8") as f:
        config = json.load(f)
    try:
        sh = pl.abrir_planilha(pl.id_planilha(config))
    except Exception as e:  # noqa: BLE001
        print(f"Falha ao acessar a planilha: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    diag_mojibake(sh, config)
    print()
    diag_random_forest_duplicado(sh, config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
