#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke test do BERTimbau: valida o caminho de fine-tuning com dados SINTETICOS
minusculos, SEM planilha e SEM secrets. Objetivo: garantir que o pipeline importa,
treina por 1 epoca e prediz — rapido e barato — antes de gastar um treino real.

Uso:
    python src/smoke_transformer.py --n 40

Nunca escreve na planilha. Sai com 0 se o pipeline rodou (inclusive em fallback
LSTM/RF quando torch/transformers nao estao instalados); sai !=0 so em erro real.
"""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def gerar_dados(n: int):
    bases = {
        "ELETRICA": ["lampada queimada no corredor", "tomada sem energia na sala",
                     "disjuntor desarmando", "falta de energia no bloco"],
        "HIDRAULICA": ["vazamento na torneira", "vaso sanitario entupido",
                       "cano estourado no banheiro", "infiltracao de agua no teto"],
        "CIVIL": ["porta com fechadura quebrada", "rachadura na parede",
                  "piso solto na entrada", "janela nao fecha"],
    }
    textos, cats = [], []
    chaves = list(bases)
    for i in range(n):
        c = chaves[i % len(chaves)]
        textos.append(bases[c][i % len(bases[c])] + f" ocorrencia {i}")
        cats.append(c)
    return textos, cats


def main() -> int:
    p = argparse.ArgumentParser(description="Smoke test do BERTimbau (sem planilha).")
    p.add_argument("--n", type=int, default=40)
    args = p.parse_args()

    # Hiperparametros minusculos para o smoke ser rapido (nao e treino real).
    os.environ.setdefault("TRANSFORMER_EPOCHS", "1")
    os.environ.setdefault("TRANSFORMER_MAXLEN", "32")
    os.environ.setdefault("TRANSFORMER_BATCH", "8")

    import modelos_zoo as zoo
    textos, cats = gerar_dados(args.n)
    print(f"[smoke] treinando transformer_ft em {len(textos)} exemplos sinteticos...")
    m = zoo.criar_modelo("transformer_ft")
    m.fit(textos, cats)
    preds, confs = m.predict_score(textos[:6])
    print(f"[smoke] train_info: {getattr(m, 'train_info', {})}")
    print(f"[smoke] predicoes de amostra: {list(zip(preds[:6], [round(float(c), 3) for c in confs[:6]]))}")
    print("[smoke] OK: pipeline do BERTimbau executou (treino + predicao).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
