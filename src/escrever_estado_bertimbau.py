#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Escreve o estado operacional do treino do BERTimbau em
dados/bertimbau_training_state.json (data, modo, contagens, commit, status).

Nao inventa metricas: as metricas finais por categoria vem da acao 'comparar'
(COMPARACAO_MODELOS -> estatistica.json). Aqui registramos so o que e operacional
e usado para a guarda/dashboard. Sem nenhum conteudo de chamado.

Uso (no workflow, apos um treino bem-sucedido):
    python src/escrever_estado_bertimbau.py --status ok --modo auto \
        --acao reclassificar_validados --commit "$GITHUB_SHA" \
        --macro-f1-val 0.0   # opcional
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
# Em docs/dados/ para o dashboard conseguir buscar via fetch e o Pages publicar.
ESTADO = RAIZ / "docs" / "dados" / "bertimbau_training_state.json"
RESUMO = RAIZ / "docs" / "dados" / "resumo.json"


def validados_atuais() -> int:
    try:
        d = json.loads(RESUMO.read_text(encoding="utf-8"))
        return int((d.get("calibracao") or {}).get("validados") or 0)
    except Exception:  # noqa: BLE001
        return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Escreve o estado do treino do BERTimbau.")
    p.add_argument("--status", required=True, help="ok | sem_dados | falha | smoke")
    p.add_argument("--modo", default="")
    p.add_argument("--acao", default="")
    p.add_argument("--commit", default="")
    p.add_argument("--n-treino", default="")
    p.add_argument("--macro-f1-val", default="")
    p.add_argument("--motivo", default="")
    args = p.parse_args()

    validados = validados_atuais()
    estado = {
        "status": args.status,
        "ultimo_treino_em": agora_bahia() if args.status == "ok" else None,
        "modo": args.modo or None,
        "acao": args.acao or None,
        "registros_conferidos_no_treino": validados if args.status == "ok" else None,
        "n_treino": int(args.n_treino) if str(args.n_treino).isdigit() else None,
        "assinatura_base": f"validados={validados}" if args.status == "ok" else None,
        "metricas": {
            "macro_f1_validacao": float(args.macro_f1_val)
            if _is_float(args.macro_f1_val) else None,
            "nota": "Metricas finais por categoria (acuracia, precision, recall, F1 macro, "
                    "matriz de confusao, classes com amostra insuficiente) vem da acao "
                    "'comparar' (COMPARACAO_MODELOS -> estatistica.json).",
        },
        "artefatos": "coluna O (Classificacao IA - 2) na planilha"
        if args.acao == "reclassificar_validados" and args.status == "ok"
        else ("COMPARACAO_MODELOS" if args.acao == "comparar" and args.status == "ok" else None),
        "commit_referencia": args.commit or None,
        "motivo": args.motivo or None,
    }
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[estado-bertimbau] escrito {ESTADO} (status={args.status}, validados={validados})")
    return 0


def _is_float(s) -> bool:
    try:
        float(s)
        return True
    except (TypeError, ValueError):
        return False


if __name__ == "__main__":
    raise SystemExit(main())
