#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Porta de decisao do coreset: compara metricas do treino FULL vs CLUSTER_CORESET e
grava a decisao (aprovado | experimental | rejeitado) em
docs/dados/bertimbau_coreset_resumo.json.

NAO inventa metricas: recebe dois JSON de metricas ja calculadas (pela acao 'comparar'
-> COMPARACAO_MODELOS/estatistica, ou por um avaliador equivalente), cada um no formato:

    {"f1_macro": 0.71,
     "acuracia": 0.78,
     "por_categoria": {"<cat>": {"f1": .., "precision": .., "recall": .., "suporte": N}, ...}}

Criterio de seguranca (ajustavel):
  - REJEITADO  se queda de F1 macro > --alerta (default 0.02), OU se alguma categoria
    rara (suporte <= --rara-max) cair mais que --alerta-rara em F1.
  - APROVADO   se o coreset for equivalente ou melhor (queda de F1 macro <= --margem,
    default 0.005) E nenhuma categoria rara piorar materialmente.
  - EXPERIMENTAL nos casos intermediarios (precisa de mais evidencia).

Uso:
    python src/comparar_coreset.py --full metr_full.json --coreset metr_coreset.json \
        [--tempo-full-s 21000 --tempo-coreset-s 5400] [--alerta 0.02] [--margem 0.005]
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RESUMO = RAIZ / "docs" / "dados" / "bertimbau_coreset_resumo.json"


def carregar(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def por_cat_f1(m):
    return {k: float((v or {}).get("f1") or 0.0) for k, v in (m.get("por_categoria") or {}).items()}


def suportes(m):
    return {k: int((v or {}).get("suporte") or 0) for k, v in (m.get("por_categoria") or {}).items()}


def main() -> int:
    p = argparse.ArgumentParser(description="Decisao do coreset (full vs cluster_coreset).")
    p.add_argument("--full", required=True, help="JSON de metricas do treino completo.")
    p.add_argument("--coreset", required=True, help="JSON de metricas do treino coreset.")
    p.add_argument("--tempo-full-s", type=float, default=None)
    p.add_argument("--tempo-coreset-s", type=float, default=None)
    p.add_argument("--alerta", type=float, default=0.02, help="Queda de F1 macro que rejeita.")
    p.add_argument("--margem", type=float, default=0.005, help="Tolerancia para aprovar.")
    p.add_argument("--rara-max", type=int, default=30, help="Suporte <= isto = categoria rara.")
    p.add_argument("--alerta-rara", type=float, default=0.05, help="Queda de F1 que reprova numa rara.")
    args = p.parse_args()

    full, core = carregar(args.full), carregar(args.coreset)
    f1_full, f1_core = float(full.get("f1_macro") or 0.0), float(core.get("f1_macro") or 0.0)
    delta = round(f1_core - f1_full, 4)

    cf_full, cf_core = por_cat_f1(full), por_cat_f1(core)
    sup = suportes(full) or suportes(core)
    raras = sorted([c for c, n in sup.items() if 0 < n <= args.rara_max])
    raras_pioradas = []
    for c in raras:
        d = round(cf_core.get(c, 0.0) - cf_full.get(c, 0.0), 4)
        if d < -args.alerta_rara:
            raras_pioradas.append({"categoria": c, "suporte": sup.get(c), "delta_f1": d})

    # categorias (nao raras) com piora relevante
    criticas_pioradas = []
    for c in cf_full:
        if c in raras:
            continue
        d = round(cf_core.get(c, 0.0) - cf_full.get(c, 0.0), 4)
        if d < -args.alerta:
            criticas_pioradas.append({"categoria": c, "suporte": sup.get(c), "delta_f1": d})

    if delta < -args.alerta or raras_pioradas:
        decisao, motivo = "rejeitado", (
            f"Queda de F1 macro {delta} alem do alerta -{args.alerta}"
            if delta < -args.alerta else
            f"{len(raras_pioradas)} categoria(s) rara(s) piorada(s) alem de -{args.alerta_rara}")
    elif delta >= -args.margem and not criticas_pioradas:
        decisao, motivo = "aprovado", (
            f"F1 macro equivalente ou melhor (delta {delta} >= -{args.margem}) e sem piora em raras/criticas")
    else:
        decisao, motivo = "experimental", (
            f"F1 macro entre os limites (delta {delta}) ou categorias criticas a verificar; precisa de mais evidencia")

    comparacao = {
        "decidido_em": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "f1_macro_full": round(f1_full, 4),
        "f1_macro_coreset": round(f1_core, 4),
        "delta_f1_macro": delta,
        "acuracia_full": round(float(full.get("acuracia") or 0.0), 4),
        "acuracia_coreset": round(float(core.get("acuracia") or 0.0), 4),
        "tempo_full_s": args.tempo_full_s,
        "tempo_coreset_s": args.tempo_coreset_s,
        "ganho_tempo": (round(1 - args.tempo_coreset_s / args.tempo_full_s, 4)
                        if args.tempo_full_s and args.tempo_coreset_s else None),
        "categorias_raras_avaliadas": raras,
        "categorias_raras_pioradas": raras_pioradas,
        "categorias_criticas_pioradas": criticas_pioradas,
        "limiares": {"alerta_f1_macro": args.alerta, "margem_aprovacao": args.margem,
                     "rara_max_suporte": args.rara_max, "alerta_rara_f1": args.alerta_rara},
        "decisao": decisao,
        "motivo": motivo,
    }

    resumo = {}
    if RESUMO.exists():
        try:
            resumo = json.loads(RESUMO.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            resumo = {}
    resumo["decisao"] = decisao
    resumo["comparacao_full_vs_coreset"] = comparacao
    RESUMO.parent.mkdir(parents=True, exist_ok=True)
    RESUMO.write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"decisao": decisao, "delta_f1_macro": delta,
                      "raras_pioradas": len(raras_pioradas),
                      "criticas_pioradas": len(criticas_pioradas), "motivo": motivo},
                     ensure_ascii=False))
    # codigo de saida 0 sempre: a decisao e o resultado, nao uma falha de CI.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
