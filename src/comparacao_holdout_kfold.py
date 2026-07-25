#!/usr/bin/env python3
"""Compara holdout fixo (85/15) com o protocolo k-fold out-of-fold ja usado no
artigo (Tabela 1/S1, k=5) para justificar a escolha metodologica da
Subsecao 3.5.

Motivacao: um parecer externo sugeriu substituir o k-fold por um holdout fixo
de 15%. Antes de mudar o desenho, medimos com dados reais o efeito do
desbalanceamento de categorias (varias com suporte <= 10; ver Tabela S1) sobre
a estabilidade da metrica por categoria em cada protocolo — nao supomos o
resultado.

Roda os 7 modelos comparaveis (mesmo conjunto da Tabela 1/2) sobre a base
completa (categoria historica como alvo, mesmo alvo da Tabela 1):
  - k-fold: NAO reexecutado aqui — usa a referencia ja publicada em
    `docs/dados/estatistica.json` (acuracia_bootstrap), pois e o mesmo calculo
    da Tabela 1 e reexecuta-lo aqui so adicionaria ruido de k-fold sem ganho
    de informacao.
  - holdout fixo 85/15, `random_state=42`: treina uma vez em 85%, testa nos
    15% restantes, sem re-treinar. Tenta primeiro um split ESTRATIFICADO
    (o que a maioria dos praticantes faria por padrao); se falhar (categorias
    com suporte < 2 impedem estratificacao no scikit-learn), registra a falha
    e cai para um split aleatorio simples — o resultado que um holdout "ingenuo"
    de fato produziria nesta base.

Leitura apenas; nao escreve na planilha.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import planilha as pl  # noqa: E402
import modelos_zoo as zoo  # noqa: E402
import classificacao_multimodelo as cm  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
DOCS_DADOS = RAIZ / "docs" / "dados"
TABELA_S1 = RAIZ / "04_artigo" / "figuras" / "tabela_S1_metricas_por_categoria.csv"
SAIDA_JSON = RAIZ / "04_artigo" / "figuras" / "comparacao_holdout_kfold.json"
SAIDA_CSV = RAIZ / "04_artigo" / "figuras" / "tabela_S4_holdout_vs_kfold.csv"

MODELOS = [
    "naive_bayes", "regressao_logistica", "linear_svc", "sgd",
    "extra_trees", "random_forest", "lstm",
]


def carregar_referencia_kfold() -> dict[str, dict]:
    """Le a acuracia por modelo ja publicada (mesmo calculo/alvo da Tabela 1)."""
    caminho = DOCS_DADOS / "estatistica.json"
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    ref = {}
    for item in dados.get("acuracia_bootstrap", []):
        ref[item["modelo"]] = {
            "acuracia": item.get("acuracia"),
            "ic95_min": item.get("ic95_min"),
            "ic95_max": item.get("ic95_max"),
        }
    return {
        "fonte": "docs/dados/estatistica.json#acuracia_bootstrap",
        "gerado_em_origem": dados.get("gerado_em"),
        "por_modelo": ref,
    }


def carregar_tabela_s1() -> dict[str, dict]:
    """Le o F1/suporte por categoria do k-fold ja publicado (Tabela S1)."""
    if not TABELA_S1.exists():
        return {}
    out = {}
    with TABELA_S1.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cat = row["categoria"]
            out[cat] = {
                "suporte_kfold": int(row["support"]),
                "f1_kfold": float(row["f1"].replace(",", ".")),
            }
    return out


def dividir_holdout(textos: list[str], cats: list[str], test_size: float, seed: int) -> dict:
    from sklearn.model_selection import train_test_split

    idx = list(range(len(textos)))
    resultado = {"test_size": test_size, "random_state": seed}
    try:
        tr_idx, te_idx = train_test_split(idx, test_size=test_size, random_state=seed, stratify=cats)
        resultado["estratificado"] = True
        resultado["erro_estratificacao"] = None
    except ValueError as exc:
        resultado["estratificado"] = False
        resultado["erro_estratificacao"] = str(exc)
        tr_idx, te_idx = train_test_split(idx, test_size=test_size, random_state=seed)
    resultado["tr_idx"] = tr_idx
    resultado["te_idx"] = te_idx
    return resultado


def avaliar_modelo_holdout(nome: str, textos_tr, cats_tr, textos_te, cats_te, categorias_todas: list[str]) -> dict:
    from sklearn.metrics import (accuracy_score, balanced_accuracy_score,
                                  f1_score, precision_recall_fscore_support)

    m = zoo.criar_modelo(nome)
    m.fit(textos_tr, cats_tr)
    preds, _scores = m.predict_score(textos_te)
    preds = [str(p) for p in preds]
    y_true = [str(c) for c in cats_te]

    acuracia = accuracy_score(y_true, preds)
    macro_f1 = f1_score(y_true, preds, labels=categorias_todas, average="macro", zero_division=0)
    bal_acc = balanced_accuracy_score(y_true, preds)
    precisao, recall, f1, suporte = precision_recall_fscore_support(
        y_true, preds, labels=categorias_todas, average=None, zero_division=0,
    )
    por_categoria = {
        cat: {"suporte_teste_holdout": int(suporte[i]), "f1_holdout": round(float(f1[i]), 4)}
        for i, cat in enumerate(categorias_todas)
    }
    return {
        "modelo": nome,
        "acuracia_holdout": round(float(acuracia), 4),
        "macro_f1_holdout": round(float(macro_f1), 4),
        "balanced_accuracy_holdout": round(float(bal_acc), 4),
        "por_categoria": por_categoria,
    }


def parse_args():
    p = argparse.ArgumentParser(description="Compara holdout fixo (85/15) com a referencia k-fold ja publicada.")
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--test-size", type=float, default=0.15)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--modelos", default=",".join(MODELOS))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    modelos = [m.strip() for m in args.modelos.split(",") if m.strip()]

    try:
        sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
        ws = sh.worksheet(config["aba_principal"])
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"Falha ao acessar a planilha: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    elegiveis = cm.carregar_elegiveis(ws, config)
    if len(elegiveis) < 10:
        print("Informação insuficiente para verificar.")
        return 1

    textos = [e["texto"] for e in elegiveis]
    cats = [e["categoria_original"] for e in elegiveis]
    categorias_todas = sorted(set(cats))

    split = dividir_holdout(textos, cats, args.test_size, args.seed)
    tr_idx, te_idx = split.pop("tr_idx"), split.pop("te_idx")
    textos_tr = [textos[i] for i in tr_idx]
    cats_tr = [cats[i] for i in tr_idx]
    textos_te = [textos[i] for i in te_idx]
    cats_te = [cats[i] for i in te_idx]

    suporte_treino = {c: cats_tr.count(c) for c in categorias_todas}
    suporte_teste = {c: cats_te.count(c) for c in categorias_todas}
    categorias_sem_treino = sorted(c for c in categorias_todas if suporte_treino[c] == 0)
    categorias_sem_teste = sorted(c for c in categorias_todas if suporte_teste[c] == 0)

    ref_kfold = carregar_referencia_kfold()
    tabela_s1 = carregar_tabela_s1()

    resultados_por_modelo = []
    for nome in modelos:
        print(f"[holdout_vs_kfold] treinando {nome} em {len(textos_tr)} exemplos, "
              f"testando em {len(textos_te)}...", file=sys.stderr)
        r = avaliar_modelo_holdout(nome, textos_tr, cats_tr, textos_te, cats_te, categorias_todas)
        r["kfold_referencia"] = ref_kfold["por_modelo"].get(nome)
        if r["kfold_referencia"] and r["kfold_referencia"].get("acuracia") is not None:
            r["delta_acuracia_holdout_menos_kfold"] = round(
                r["acuracia_holdout"] - r["kfold_referencia"]["acuracia"], 4,
            )
        else:
            r["delta_acuracia_holdout_menos_kfold"] = None
        resultados_por_modelo.append(r)
        print(f"[holdout_vs_kfold] {nome}: acuracia_holdout={r['acuracia_holdout']:.4f} "
              f"macro_f1_holdout={r['macro_f1_holdout']:.4f} "
              f"kfold_ref={r['kfold_referencia']}", file=sys.stderr)

    # Piores categorias no holdout: sem exemplo de teste, ou suporte de teste
    # muito baixo (<=2) com F1 pior que no k-fold para o modelo lider.
    lider = next((r for r in resultados_por_modelo if r["modelo"] == "linear_svc"), resultados_por_modelo[0])
    piores = []
    for cat in categorias_todas:
        s1 = tabela_s1.get(cat, {})
        piores.append({
            "categoria": cat,
            "suporte_total": suporte_treino[cat] + suporte_teste[cat],
            "suporte_teste_holdout": suporte_teste[cat],
            "suporte_treino_holdout": suporte_treino[cat],
            "f1_holdout_linear_svc": lider["por_categoria"].get(cat, {}).get("f1_holdout"),
            "suporte_kfold_completo": s1.get("suporte_kfold"),
            "f1_kfold_linear_svc_aprox": s1.get("f1_kfold"),
        })
    piores.sort(key=lambda d: (d["suporte_teste_holdout"], d["suporte_total"]))

    payload = {
        "gerado_em": agora_bahia(),
        "script_origem": "src/comparacao_holdout_kfold.py",
        "natureza": (
            "comparacao metodologica holdout fixo (85/15) vs referencia k-fold ja "
            "publicada (Tabela 1/S1, k=5); alvo = categoria historica; leitura apenas"
        ),
        "n_total": len(elegiveis),
        "n_categorias": len(categorias_todas),
        "holdout": {**split, "n_treino": len(tr_idx), "n_teste": len(te_idx)},
        "categorias_sem_exemplo_treino_holdout": categorias_sem_treino,
        "categorias_sem_exemplo_teste_holdout": categorias_sem_teste,
        "n_categorias_sem_exemplo_teste_holdout": len(categorias_sem_teste),
        "kfold_referencia": {"fonte": ref_kfold["fonte"], "gerado_em_origem": ref_kfold["gerado_em_origem"]},
        "por_modelo": [
            {k: v for k, v in r.items() if k != "por_categoria"} for r in resultados_por_modelo
        ],
        "piores_categorias_ordenadas_por_suporte_teste_holdout": piores[:15],
    }
    SAIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    with SAIDA_CSV.open("w", newline="", encoding="utf-8") as arq:
        campos = ["categoria", "suporte_total", "suporte_treino_holdout", "suporte_teste_holdout",
                   "f1_holdout_linear_svc", "suporte_kfold_completo", "f1_kfold_linear_svc_aprox"]
        w = csv.DictWriter(arq, fieldnames=campos)
        w.writeheader()
        for row in piores:
            w.writerow(row)

    print(f"holdout_json={SAIDA_JSON}")
    print(f"holdout_csv={SAIDA_CSV}")
    print(f"estratificado={split['estratificado']} categorias_sem_teste={len(categorias_sem_teste)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
