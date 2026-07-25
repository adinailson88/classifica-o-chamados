#!/usr/bin/env python3
"""Ablation study do LSTM: units 64/128 x dropout 0.5/0.3.

Treina modelos reais em folds e mede acerto contra a verdade validada humana.
Nao escreve na planilha.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decisao_validada as dv  # noqa: E402
import modelo_lstm  # noqa: E402
import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402


RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
SAIDA_JSON = RAIZ / "04_artigo" / "figuras" / "ablation_lstm_resultados.json"
SAIDA_CSV = RAIZ / "04_artigo" / "figuras" / "tabela_S3_ablation_lstm.csv"
SAIDA_FIG = RAIZ / "04_artigo" / "figuras" / "fig6_ablation_lstm.png"


def _cel(linha, idx) -> str:
    return str(linha[idx] or "").strip() if idx is not None and idx < len(linha) else ""


def carregar_elegiveis(config: dict, credenciais=None):
    sh = pl.abrir_planilha(pl.id_planilha(config), credenciais)
    ws = sh.worksheet(config["aba_principal"])
    valores = pl.ler_valores(ws, config["range_leitura"])
    cab = valores[0] if valores else []
    norm = lambda s: " ".join(str(s or "").split()).casefold()  # noqa: E731
    idx = {norm(nome): i for i, nome in enumerate(cab)}
    i_tit = idx.get(norm("TÍTULO"))
    i_cat = idx.get(norm("CATEGORIA COMPLETA"))
    i_dg = idx.get(norm("DESCRIÇÃO GLPI"))
    i_to = idx.get(norm("TÍTULO O.S.M."))
    i_do = idx.get(norm("DESCRIÇÃO O.S.M."))
    linhas = []
    for pos, linha in enumerate(valores[1:], start=2):
        cat = _cel(linha, i_cat)
        texto = "\n".join(
            c for c in [_cel(linha, i_tit), _cel(linha, i_dg), _cel(linha, i_to), _cel(linha, i_do)] if c
        )
        if cat and texto:
            linhas.append({"linha": pos, "texto": texto, "historico": cat})
    return sh, linhas


def variantes(base_params: dict) -> list[dict]:
    comuns = {k: v for k, v in base_params.items() if k not in {"units", "dropout"}}
    return [
        {"nome": "units64_dropout05_atual", **comuns, "units": 64, "dropout": 0.5},
        {"nome": "units128_dropout05", **comuns, "units": 128, "dropout": 0.5},
        {"nome": "units64_dropout03", **comuns, "units": 64, "dropout": 0.3},
        {"nome": "units128_dropout03", **comuns, "units": 128, "dropout": 0.3},
    ]


def avaliar_variante(nome: str, params: dict, linhas: list[dict], verdade: dict[int, str],
                     k_folds: int, epochs: int, batch_size: int, validation_split: float,
                     paciencia: int, usar_class_weight: bool, verbose: int) -> dict:
    from sklearn.model_selection import KFold

    idx_validados = [i for i, item in enumerate(linhas) if item["linha"] in verdade]
    if len(idx_validados) < 2:
        raise RuntimeError("Informação insuficiente para verificar.")
    kk = max(2, min(int(k_folds), len(idx_validados)))
    acertos = []
    kf = KFold(n_splits=kk, shuffle=True, random_state=42)
    todos_indices = set(range(len(linhas)))
    for fold, (tr_rel, te_rel) in enumerate(kf.split(idx_validados), start=1):
        teste_idx = [idx_validados[i] for i in te_rel]
        treino_idx = sorted(todos_indices - set(teste_idx))
        clf_params = {k: v for k, v in params.items() if k != "nome"}
        clf = modelo_lstm.ClassificadorLSTM(**clf_params)
        clf.fit(
            [linhas[i]["texto"] for i in treino_idx],
            [linhas[i]["historico"] for i in treino_idx],
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            paciencia=paciencia,
            verbose=verbose,
            usar_class_weight=usar_class_weight,
        )
        preds, _confs = clf.predict_com_conf([linhas[i]["texto"] for i in teste_idx])
        fold_acertos = [str(pred) == verdade[linhas[i]["linha"]] for pred, i in zip(preds, teste_idx)]
        acertos.extend(fold_acertos)
        print(f"[{nome}] fold={fold}/{kk} n={len(fold_acertos)} acerto={np.mean(fold_acertos):.4f}")
    arr = np.array(acertos, dtype=float)
    return {
        "variante": nome,
        "units": params["units"],
        "dropout": params["dropout"],
        "n_validado": int(len(arr)),
        "acerto_validado": round(float(arr.mean()), 4),
        "acertos": int(arr.sum()),
        "erros": int(len(arr) - arr.sum()),
    }


def salvar_csv(resultados: list[dict]) -> None:
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    campos = ["variante", "units", "dropout", "n_validado", "acerto_validado", "acertos", "erros"]
    with SAIDA_CSV.open("w", newline="", encoding="utf-8") as arq:
        escritor = csv.DictWriter(arq, fieldnames=campos)
        escritor.writeheader()
        for r in resultados:
            escritor.writerow({c: r.get(c, "") for c in campos})


def salvar_figura(resultados: list[dict]) -> None:
    import matplotlib.pyplot as plt

    ordenados = sorted(resultados, key=lambda r: r["acerto_validado"], reverse=True)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    labels = [r["variante"].replace("_", "\n") for r in ordenados]
    vals = [100 * r["acerto_validado"] for r in ordenados]
    ax.bar(labels, vals, color="#6b8f2f")
    ax.set_ylabel("Acerto validado (%)")
    ax.set_title("Ablation LSTM: unidades e dropout")
    ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.35)
    ax.spines[["top", "right"]].set_visible(False)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.2, f"{v:.2f}%", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    SAIDA_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAIDA_FIG, dpi=220)
    plt.close(fig)


def parse_args():
    p = argparse.ArgumentParser(description="Ablation real do LSTM contra acerto validado.")
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--k-folds", type=int, default=3)
    p.add_argument("--epochs", type=int, default=None)
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--validation-split", type=float, default=0.1)
    p.add_argument("--verbose", type=int, default=2)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    lstm_cfg = dict((config.get("modelo_ia", {}) or {}).get("lstm", {}) or {})
    params = modelo_lstm.resolver_parametros_lstm(lstm_cfg)
    epochs = int(args.epochs or params.pop("epochs", 15))
    batch_size = int(args.batch_size or params.pop("batch_size", 128))
    paciencia = int(params.pop("paciencia", 3))
    usar_class_weight = bool(params.pop("usar_class_weight", True))

    try:
        sh, linhas = carregar_elegiveis(config, args.credenciais)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"Falha ao acessar a planilha: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    verdade = dv.verdade_validada(dv.carregar_decisoes(sh, config["aba_principal"]))
    if len(verdade) < 2:
        print("Informação insuficiente para verificar.")
        return 1

    resultados = []
    for var in variantes(params):
        resultados.append(
            avaliar_variante(
                var["nome"], var, linhas, verdade, args.k_folds, epochs, batch_size,
                args.validation_split, paciencia, usar_class_weight, args.verbose,
            )
        )
    payload = {
        "gerado_em": agora_bahia(),
        "script_origem": "src/ablation_lstm.py",
        "natureza": "acerto contra verdade validada humana; KFold sobre linhas validadas",
        "k_folds": args.k_folds,
        "epochs": epochs,
        "batch_size": batch_size,
        "resultados": sorted(resultados, key=lambda r: r["acerto_validado"], reverse=True),
    }
    SAIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    salvar_csv(payload["resultados"])
    salvar_figura(payload["resultados"])
    print(f"ablation_json={SAIDA_JSON}")
    print(f"ablation_csv={SAIDA_CSV}")
    print(f"ablation_fig={SAIDA_FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
