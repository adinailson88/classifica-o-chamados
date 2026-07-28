#!/usr/bin/env python3
"""Helpers compartilhados para treinar modelos de reclassificacao.

Este modulo contem apenas a selecao e o treinamento dos modelos. Nao acessa nem
escreve na planilha. A separacao permite remover o antigo executor monolitico da
Etapa 2 sem manter dependencia indireta de um script legado.
"""

from __future__ import annotations

from typing import Any

import numpy as np

import classificador_producao as cp


def cel(linha: list[Any], idx: int | None) -> str:
    """Retorna uma celula normalizada ou string vazia quando o indice nao existe."""
    return str(linha[idx] or "").strip() if idx is not None and idx < len(linha) else ""


def treinar_reclass(modelo: str, textos: list[str], categorias: list[str], config: dict | None = None):
    """Retorna ``(predict_fn, tag)`` para o modelo solicitado.

    ``predict_fn(textos)`` devolve ``(predicoes, confiancas)``. As dependencias
    pesadas sao importadas somente quando o respectivo modelo e solicitado.
    """
    if modelo in ("transformer_ft", "bertimbau"):
        import modelos_zoo as zoo  # noqa: PLC0415

        classificador = zoo.criar_modelo("transformer_ft")
        classificador.fit(textos, categorias)
        return (lambda x: classificador.predict_score(list(x))), "TransformerFT"

    if modelo == "robusto":
        import classificador_robusto as cr  # noqa: PLC0415

        lstm_config = (config or {}).get("modelo_ia", {}).get("lstm", {})
        classificador, tag = cr.treinar(textos, categorias, lstm_config=lstm_config)
        return (lambda x: classificador.predict_com_conf(x)), tag

    if modelo == "baseline":
        from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: PLC0415
        from sklearn.linear_model import LogisticRegression  # noqa: PLC0415
        from sklearn.pipeline import Pipeline  # noqa: PLC0415

        classificador = Pipeline([
            ("tfidf", TfidfVectorizer(
                strip_accents="unicode",
                lowercase=True,
                ngram_range=(1, 2),
                min_df=1,
                max_features=30000,
            )),
            ("clf", LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
            )),
        ])
        classificador.fit(textos, categorias)

        def prever(x):
            probabilidades = classificador.predict_proba(x)
            indices = probabilidades.argmax(axis=1)
            return (
                classificador.classes_[indices],
                probabilidades[np.arange(len(indices)), indices],
            )

        return prever, "Baseline"

    lstm_config = (config or {}).get("modelo_ia", {}).get("lstm", {})
    classificador, eh_lstm = cp.treinar_classificador(
        textos,
        categorias,
        lstm_config=lstm_config,
    )
    return (
        lambda x: cp.predizer(classificador, eh_lstm, x),
        "LSTM" if eh_lstm else "RF",
    )
