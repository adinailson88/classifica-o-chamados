#!/usr/bin/env python3
"""Limpa as abas CLASSIF__<modelo>/turnos/metricas de modelos escolhidos,
para forcar uma REMATERIALIZACAO COMPLETA (nao incremental) na proxima
execucao de src/classificacao_multimodelo.py.

ESCOPO ESTRITO (nao mexe em mais nada):
- So le/escreve nas abas CLASSIF__<modelo> dos modelos passados em --modelos.
- So filtra (nao apaga tudo) as linhas correspondentes a esses modelos em
  MULTIMODELO_TURNOS e MULTIMODELO_METRICAS -- linhas de outros modelos
  (ex.: transformer_ft, se nao estiver na lista) sao preservadas.
- NUNCA abre a aba principal (CHAMADOS_ESQUELETO_REDUZIDO) para escrita.
  Nao toca em G, K, L, M, N, O, P nem em qualquer outra coluna dela.
- Por padrao, exclui "transformer_ft" da lista mesmo se --modelos=todos for
  usado por engano -- so entra se passado explicitamente por nome.

Sem --aplicar = dry-run (so conta e imprime o que seria apagado).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import planilha as pl  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"

MODELOS_COMPARAVEIS_PADRAO = [
    "naive_bayes", "regressao_logistica", "linear_svc",
    "sgd", "extra_trees", "random_forest", "lstm",
]


def nome_aba(template: str, modelo: str) -> str:
    return template.replace("{modelo}", modelo)


def resolver_modelos(escolha: str) -> list[str]:
    e = (escolha or "").strip().lower()
    if e in ("", "comparaveis", "padrao"):
        return list(MODELOS_COMPARAVEIS_PADRAO)
    return [m.strip() for m in e.split(",") if m.strip()]


def limpar_classif(sh, config: dict, modelo: str, aplicar: bool) -> dict[str, Any]:
    mm = config["multimodelo"]
    aba = nome_aba(mm["aba_classificacao"], modelo)
    try:
        ws = sh.worksheet(aba)
        valores = ws.get_values("A:A", value_render_option="UNFORMATTED_VALUE")
        n_linhas = max(0, len(valores) - 1)
        cabecalho = ws.row_values(1) if n_linhas or valores else []
    except Exception as exc:  # noqa: BLE001
        return {"modelo": modelo, "aba": aba, "existia": False, "linhas_removidas": 0,
                "erro": str(exc)}

    if not aplicar:
        return {"modelo": modelo, "aba": aba, "existia": True,
                "linhas_removidas_dry_run": n_linhas}

    cab = cabecalho or ["run_id", "linha_planilha", "id_chamado", "categoria_original",
                        "categoria_ia", "confianca", "faixa", "executor",
                        "acerto_historico", "etapa", "data"]
    pl.escrever_aba(sh, aba, cab, [])
    return {"modelo": modelo, "aba": aba, "existia": True, "linhas_removidas": n_linhas}


def filtrar_aba_por_modelo(sh, nome_tabela: str, modelos_alvo: set[str], aplicar: bool,
                           col_modelo_1based: int = 1) -> dict[str, Any]:
    try:
        ws = sh.worksheet(nome_tabela)
    except Exception as exc:  # noqa: BLE001
        return {"aba": nome_tabela, "existia": False, "erro": str(exc)}

    valores = ws.get_values("A:Z", value_render_option="UNFORMATTED_VALUE")
    if not valores:
        return {"aba": nome_tabela, "existia": True, "linhas_removidas": 0}
    cabecalho, corpo = valores[0], valores[1:]
    idx = col_modelo_1based - 1
    mantidas = [r for r in corpo if not (len(r) > idx and str(r[idx]).strip() in modelos_alvo)]
    removidas = len(corpo) - len(mantidas)

    if not aplicar:
        return {"aba": nome_tabela, "existia": True, "linhas_removidas_dry_run": removidas,
                "linhas_mantidas_dry_run": len(mantidas)}

    pl.escrever_aba(sh, nome_tabela, cabecalho, mantidas)
    return {"aba": nome_tabela, "existia": True, "linhas_removidas": removidas,
            "linhas_mantidas": len(mantidas)}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--modelos", default="comparaveis",
                   help="'comparaveis' (7, padrao, SEM transformer_ft), ou lista "
                        "separada por virgula (ex.: 'lstm' ou 'lstm,naive_bayes').")
    p.add_argument("--aplicar", action="store_true",
                   help="Sem isso, e dry-run (so conta, nao apaga nada).")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    modelos = resolver_modelos(args.modelos)

    if not modelos:
        print("Nenhum modelo resolvido a partir de --modelos.", file=sys.stderr)
        return 1

    print(f"Modelos alvo: {modelos}")
    if "transformer_ft" in modelos:
        print("AVISO: transformer_ft esta na lista -- confirme que isso e intencional "
              "(o padrao 'comparaveis' NUNCA inclui esse modelo).", file=sys.stderr)

    try:
        sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"Falha ao acessar a planilha: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    mm = config["multimodelo"]
    resultados = {"aplicar": args.aplicar, "modelos": modelos, "classif": [], "turnos": None,
                 "metricas": None}

    for modelo in modelos:
        resultados["classif"].append(limpar_classif(sh, config, modelo, args.aplicar))

    resultados["turnos"] = filtrar_aba_por_modelo(
        sh, mm["aba_turnos"], set(modelos), args.aplicar, col_modelo_1based=1)
    resultados["metricas"] = filtrar_aba_por_modelo(
        sh, mm["aba_metricas"], set(modelos), args.aplicar, col_modelo_1based=1)

    print(json.dumps(resultados, ensure_ascii=False, indent=2))
    if not args.aplicar:
        print("\nDRY-RUN: nada foi apagado. Rode de novo com --aplicar para executar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
