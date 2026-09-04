#!/usr/bin/env python3
"""Exporta RECLASS_HISTORICO inteira para arquivo local (CSV + manifesto JSON).

FASE 1 do plano de reducao de celulas da planilha (2026-09): RECLASS_HISTORICO
e a maior aba (3.059.112 celulas alocadas em 04/09/2026, 33% do limite de
10 milhoes, crescendo ~340 mil celulas/mes) e e append-only -- cada linha e
uma decisao de reclassificacao, nunca apagada. E tambem a fonte usada por
`scripts/migracoes/restaurar_coluna_o.py` para reconstrucao forense por data
de corte (indexada por id_chamado, ver `ultimo_valor_por_id`), entao nao pode
ser truncada (Fase 3, script separado) sem que o conteudo integral seja
preservado antes em algum lugar fora do Sheets.

Este script SO LE a aba e grava um CSV completo (todas as colunas, todas as
linhas, na ordem em que estao na planilha) mais um manifesto JSON com
contagens e metadados, para conferencia de completude antes de qualquer
truncamento. NAO ESCREVE NADA na planilha.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
SAIDA_PADRAO_DIR = RAIZ / "dados" / "arquivo_reclass_historico"


def carimbo_de_data_hora(gerado: str) -> str:
    """dd/mm/aaaa hh:mm -> ddmmaaaa_hhmm, para nome de arquivo sem caracteres invalidos."""
    return gerado.replace("/", "").replace(" ", "_").replace(":", "")


def exportar(
    ws,
    aba: str,
    saida_dir: Path,
    gerado: str,
    limite_linhas: int = 0,
) -> dict[str, Any]:
    """Le a aba inteira e grava CSV + manifesto em saida_dir. Retorna o manifesto."""
    valores = ws.get_values(value_render_option="UNFORMATTED_VALUE")
    if not valores:
        return {
            "aba_origem": aba, "gerado_em": gerado, "colunas": [],
            "linhas_exportadas": 0, "linhas_na_planilha_incluindo_cabecalho": 0,
            "arquivo_csv": None,
        }

    cabecalho = valores[0]
    linhas = valores[1:]
    if limite_linhas > 0:
        linhas = linhas[:limite_linhas]

    saida_dir.mkdir(parents=True, exist_ok=True)
    carimbo = carimbo_de_data_hora(gerado)
    caminho_csv = saida_dir / f"{aba.lower()}_{carimbo}.csv"
    caminho_manifesto = saida_dir / f"{aba.lower()}_{carimbo}_manifesto.json"

    with caminho_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(cabecalho)
        w.writerows(linhas)

    manifesto = {
        "aba_origem": aba,
        "gerado_em": gerado,
        "colunas": cabecalho,
        "linhas_exportadas": len(linhas),
        "linhas_na_planilha_incluindo_cabecalho": len(valores),
        "arquivo_csv": caminho_csv.name,
    }
    with caminho_manifesto.open("w", encoding="utf-8") as f:
        json.dump(manifesto, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return manifesto


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--aba", default=None,
                    help="Nome da aba (padrao: multimodelo.aba_historico_reclassificacao "
                         "ou RECLASS_HISTORICO).")
    p.add_argument("--saida-dir", type=Path, default=SAIDA_PADRAO_DIR)
    p.add_argument("--limite-linhas", type=int, default=0,
                    help="0 = todas as linhas. Numero > 0 exporta so as N primeiras (teste).")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    with args.config.open(encoding="utf-8") as f:
        config = json.load(f)
    aba = args.aba or config.get("multimodelo", {}).get(
        "aba_historico_reclassificacao", "RECLASS_HISTORICO")

    try:
        sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
        ws = sh.worksheet(aba)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001
        print(f"Falha ao acessar a planilha: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    print(f"aba={aba} | linhas_alocadas={ws.row_count} | colunas_alocadas={ws.col_count}")

    gerado = agora_bahia()
    manifesto = exportar(ws, aba, args.saida_dir, gerado, args.limite_linhas)

    if not manifesto["arquivo_csv"]:
        print("aba vazia; nada para exportar.")
        return 0

    print(f"exportado: {manifesto['linhas_exportadas']} linhas "
          f"({len(manifesto['colunas'])} colunas) -> "
          f"{args.saida_dir / manifesto['arquivo_csv']}")
    print(f"manifesto -> {args.saida_dir / (Path(manifesto['arquivo_csv']).stem + '_manifesto.json')}")
    print("Nada foi alterado na planilha (somente leitura).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
