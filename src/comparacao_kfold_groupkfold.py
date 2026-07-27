#!/usr/bin/env python3
"""Reexecuta os sete modelos comparaveis sob dois protocolos de particionamento.

Motivacao. O ablation do LSTM (Subsecao 4.8) mediu que 46,72% das linhas
validadas possuem duplicata textual normalizada em outra parte da base, e por
isso adota GroupKFold por hash de texto. O protocolo principal das Tabelas 1 e
2, porem, usa KFold embaralhado por linha, que deixa o mesmo texto cair em
treino e teste. Este script mede o efeito dessa diferenca sobre a acuracia de
cada modelo, para que o artigo possa reportar os dois protocolos em vez de
supor que o vazamento e desprezivel.

  - kfold:      KFold(n_splits=k, shuffle=True, random_state=42) sobre linhas,
                identico ao usado em `classificacao_multimodelo.py`.
  - groupkfold: GroupKFold(n_splits=k) sobre grupos de texto normalizado,
                nenhum grupo textual aparece em treino e teste ao mesmo tempo.

O alvo e a categoria historica, o mesmo da Tabela 1, o que torna os numeros
diretamente comparaveis com `docs/dados/estatistica.json#acuracia_bootstrap`.

Somente leitura. Nao escreve na planilha e nao toca nas abas de producao.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import planilha as pl  # noqa: E402
import modelos_zoo as zoo  # noqa: E402
import classificacao_multimodelo as cm  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
SAIDA_JSON = RAIZ / "04_artigo" / "figuras" / "comparacao_kfold_groupkfold.json"
SAIDA_CSV = RAIZ / "04_artigo" / "figuras" / "tabela_S5_kfold_vs_groupkfold.csv"

MODELOS = [
    "naive_bayes", "regressao_logistica", "linear_svc", "sgd",
    "extra_trees", "random_forest", "lstm",
]


def normalizar_texto(texto: str) -> str:
    """Mesma normalizacao do ablation, para que os grupos sejam comparaveis."""
    sem_acento = unicodedata.normalize("NFKD", str(texto or ""))
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acento.casefold()).strip()


def hash_texto(texto: str) -> str:
    return hashlib.sha256(normalizar_texto(texto).encode("utf-8")).hexdigest()


def medir_duplicatas(textos: list[str]) -> dict:
    grupos = [hash_texto(t) for t in textos]
    contagem: dict[str, int] = {}
    for g in grupos:
        contagem[g] = contagem.get(g, 0) + 1
    duplicadas = sum(1 for g in grupos if contagem[g] > 1)
    return {
        "n_linhas": len(textos),
        "n_grupos_textuais": len(contagem),
        "linhas_com_duplicata": duplicadas,
        "proporcao_com_duplicata": round(duplicadas / len(textos), 4) if textos else None,
    }


def _acuracia(y_true: list[str], y_pred: list[str]) -> float:
    certos = sum(1 for a, b in zip(y_true, y_pred) if a == b)
    return certos / len(y_true) if y_true else 0.0


def avaliar(nome: str, textos: list[str], cats: list[str],
            grupos: list[str] | None, k: int) -> dict:
    """Roda um modelo out-of-fold sob o protocolo indicado.

    Com `grupos`, usa GroupKFold e remove do treino todo grupo textual presente
    no teste. Sem `grupos`, reproduz o KFold por linha do pipeline principal.
    """
    from sklearn.model_selection import GroupKFold, KFold
    from sklearn.metrics import balanced_accuracy_score, f1_score

    n = len(textos)
    preds: list[str | None] = [None] * n
    if grupos is None:
        particoes = KFold(n_splits=k, shuffle=True, random_state=42).split(range(n))
        for tr_idx, te_idx in particoes:
            m = zoo.criar_modelo(nome)
            m.fit([textos[i] for i in tr_idx], [cats[i] for i in tr_idx])
            p, _ = m.predict_score([textos[i] for i in te_idx])
            for j, i in enumerate(te_idx):
                preds[i] = str(p[j])
    else:
        kk = max(2, min(k, len(set(grupos))))
        for _tr_idx, te_idx in GroupKFold(n_splits=kk).split(range(n), groups=grupos):
            grupos_teste = {grupos[i] for i in te_idx}
            # O treino exclui todo o grupo textual que aparece no teste, e nao
            # apenas as linhas sorteadas para o teste.
            tr_idx = [i for i in range(n) if grupos[i] not in grupos_teste]
            m = zoo.criar_modelo(nome)
            m.fit([textos[i] for i in tr_idx], [cats[i] for i in tr_idx])
            p, _ = m.predict_score([textos[i] for i in te_idx])
            for j, i in enumerate(te_idx):
                preds[i] = str(p[j])

    y_pred = [p if p is not None else "" for p in preds]
    rotulos = sorted(set(cats))
    return {
        "modelo": nome,
        "acuracia": round(_acuracia(cats, y_pred), 4),
        "macro_f1": round(float(f1_score(cats, y_pred, labels=rotulos,
                                         average="macro", zero_division=0)), 4),
        "balanced_accuracy": round(float(balanced_accuracy_score(cats, y_pred)), 4),
    }


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--k-folds", type=int, default=5)
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
    grupos = [hash_texto(t) for t in textos]
    duplicatas = medir_duplicatas(textos)
    print(f"[kfold_vs_groupkfold] {duplicatas['n_linhas']} linhas, "
          f"{duplicatas['n_grupos_textuais']} grupos textuais, "
          f"{100 * duplicatas['proporcao_com_duplicata']:.2f}% com duplicata",
          file=sys.stderr)

    resultados = []
    for nome in modelos:
        print(f"[kfold_vs_groupkfold] {nome}: kfold...", file=sys.stderr)
        r_kf = avaliar(nome, textos, cats, None, args.k_folds)
        print(f"[kfold_vs_groupkfold] {nome}: groupkfold...", file=sys.stderr)
        r_gk = avaliar(nome, textos, cats, grupos, args.k_folds)
        delta = round(r_kf["acuracia"] - r_gk["acuracia"], 4)
        resultados.append({
            "modelo": nome,
            "kfold": r_kf,
            "groupkfold": r_gk,
            "delta_acuracia_kfold_menos_groupkfold": delta,
        })
        print(f"[kfold_vs_groupkfold] {nome}: kfold={r_kf['acuracia']:.4f} "
              f"groupkfold={r_gk['acuracia']:.4f} delta={delta:+.4f}", file=sys.stderr)

    ordem_kf = [r["modelo"] for r in sorted(resultados, key=lambda r: -r["kfold"]["acuracia"])]
    ordem_gk = [r["modelo"] for r in sorted(resultados, key=lambda r: -r["groupkfold"]["acuracia"])]

    saida = {
        "gerado_em": agora_bahia(),
        "script_origem": "src/comparacao_kfold_groupkfold.py",
        "natureza": "acuracia contra a categoria historica, mesmo alvo da Tabela 1",
        "k_folds": args.k_folds,
        "duplicatas_textuais": duplicatas,
        "resultados": resultados,
        "ranking_kfold": ordem_kf,
        "ranking_groupkfold": ordem_gk,
        "ranking_preservado": ordem_kf == ordem_gk,
    }
    SAIDA_JSON.parent.mkdir(parents=True, exist_ok=True)
    SAIDA_JSON.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")

    with SAIDA_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["modelo", "acuracia_kfold", "acuracia_groupkfold", "delta",
                    "macro_f1_kfold", "macro_f1_groupkfold"])
        for r in resultados:
            w.writerow([r["modelo"], r["kfold"]["acuracia"], r["groupkfold"]["acuracia"],
                        r["delta_acuracia_kfold_menos_groupkfold"],
                        r["kfold"]["macro_f1"], r["groupkfold"]["macro_f1"]])

    print(f"json={SAIDA_JSON}")
    print(f"csv={SAIDA_CSV}")
    print(f"ranking_preservado={saida['ranking_preservado']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
