"""Remove linhas duplicadas das abas CLASSIF__<modelo> (mesma linha_planilha).

Causa conhecida: em 14/07/2026 uma falha transitoria da API fez o
classificacao_multimodelo tratar a base inteira como pendente e re-anexar
~13,9 mil linhas em CLASSIF__random_forest (27.838 linhas para 13.954 unicas).
Para cada linha_planilha, mantem a ULTIMA ocorrencia (o append mais recente) e
reescreve a aba em uma unica escrita em lote. Linhas sem chave sao preservadas.

Dry-run por padrao (so relatorio); --aplicar reescreve as abas com duplicatas.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gspread  # noqa: E402
import planilha as pl  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"

# Cabecalho gravado por gravar_classificacao (classificacao_multimodelo.py);
# confianca (coluna 6) formatada como % com valores em fracao 0-1.
COLUNAS_PERCENTUAIS = [6]


def resolver_modelos(config: dict, escolha: str) -> list[str]:
    mm = config.get("multimodelo", {}) or {}
    leves = list(mm.get("modelos_leves", []))
    pesados = list(mm.get("modelos_pesados", []))
    if escolha == "todos":
        return leves + pesados
    if escolha == "leves":
        return leves
    if escolha == "pesados":
        return pesados
    return [m.strip() for m in escolha.split(",") if m.strip()]


def limpar_aba(sh, aba: str, aplicar: bool) -> dict:
    try:
        ws = sh.worksheet(aba)
    except gspread.WorksheetNotFound:
        print(f"[{aba}] aba inexistente; nada a fazer")
        return {"aba": aba, "existe": False}
    vals = pl.ler_valores(ws, "A:K")
    if not vals:
        print(f"[{aba}] aba vazia; nada a fazer")
        return {"aba": aba, "existe": True, "total": 0, "removidas": 0}
    cab, linhas = vals[0], vals[1:]
    ultima = {}
    sem_chave = set()
    for i, r in enumerate(linhas):
        chave = str(r[1]).strip() if len(r) > 1 else ""
        if chave:
            ultima[chave] = i
        else:
            sem_chave.add(i)
    manter = sorted(set(ultima.values()) | sem_chave)
    novas = [linhas[i] for i in manter]
    removidas = len(linhas) - len(novas)
    print(f"[{aba}] total={len(linhas)} | unicas={len(ultima)} | "
          f"sem_chave={len(sem_chave)} | duplicadas_removiveis={removidas}")
    if removidas and aplicar:
        pl.escrever_aba(sh, aba, cab, novas, colunas_percentuais=COLUNAS_PERCENTUAIS)
        print(f"[{aba}] reescrita com {len(novas)} linhas (removidas {removidas})")
    elif removidas:
        print(f"[{aba}] DRY-RUN: nada gravado; use --aplicar para reescrever")
    return {"aba": aba, "existe": True, "total": len(linhas),
            "mantidas": len(novas), "removidas": removidas, "aplicado": bool(removidas and aplicar)}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--modelos", default="todos",
                   help="todos | leves | pesados | lista separada por virgula")
    p.add_argument("--aplicar", action="store_true",
                   help="Reescreve as abas com duplicatas (sem isso: so relatorio)")
    p.add_argument("--config", default=str(CONFIG_PADRAO))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    with Path(args.config).open(encoding="utf-8") as f:
        config = json.load(f)
    mm = config.get("multimodelo", {}) or {}
    template = mm.get("aba_classificacao", "CLASSIF__{modelo}")
    modelos = resolver_modelos(config, args.modelos)
    if not modelos:
        print("Nenhum modelo selecionado.", file=sys.stderr)
        return 1
    sh = pl.abrir_planilha(pl.id_planilha(config))
    resultados = [limpar_aba(sh, template.replace("{modelo}", m), args.aplicar)
                  for m in modelos]
    total_rem = sum(r.get("removidas", 0) for r in resultados)
    print(f"OK: {'aplicado' if args.aplicar else 'dry-run'} | "
          f"duplicatas encontradas={total_rem}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
