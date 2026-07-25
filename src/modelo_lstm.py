#!/usr/bin/env python3
"""Classificador LSTM Bidirecional (espelha o motor de produção Malha IA).

Arquitetura: Embedding(8000,128) -> BiLSTM(64) -> Dropout(0.5) -> Dense(64,ReLU)
-> Dense(K, softmax). Otimizador Adam, perda sparse_categorical_crossentropy,
EarlyStopping(restore_best_weights). 100% local (sem APIs externas de LLM).

Interface: fit(textos, categorias), predict_com_conf(textos) -> (preds, confs),
save(dir) / load(dir) para persistir e reutilizar no cron (treino 1x, predição N).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")  # silencia logs INFO do TF

import numpy as np

LSTM_VOCAB_SIZE = 8000
LSTM_MAX_LEN = 120
LSTM_EMBED_DIM = 128
LSTM_UNITS = 64
LSTM_DENSE_UNITS = 64
LSTM_DROPOUT = 0.5
LSTM_LAYERS = 1

PERFIS_LSTM = {
    "padrao": {
        "vocab_size": 8000,
        "max_len": 120,
        "embed_dim": 128,
        "units": 64,
        "dense_units": 64,
        "dropout": 0.5,
        "layers": 1,
        "epochs": 15,
        "batch_size": 128,
        "paciencia": 3,
    },
    "robusto": {
        "vocab_size": 20000,
        "max_len": 220,
        "embed_dim": 192,
        "units": 128,
        "dense_units": 128,
        "dropout": 0.45,
        "layers": 2,
        "epochs": 25,
        "batch_size": 96,
        "paciencia": 5,
    },
}


def resolver_parametros_lstm(config: dict | None = None) -> dict:
    cfg = dict(config or {})
    perfil_config = cfg.pop("perfil", "padrao")
    perfil = os.getenv("LSTM_PERFIL") or perfil_config or "padrao"
    perfil = str(perfil).lower()
    params = dict(PERFIS_LSTM.get(perfil, PERFIS_LSTM["padrao"]))
    chaves_validas = set(params) | {"validation_split", "usar_class_weight"}
    params.update({k: v for k, v in cfg.items() if k in chaves_validas and v not in (None, "")})
    return params


def _tf():
    import tensorflow as tf
    return tf


def _cel(linha, idx) -> str:
    return str(linha[idx] or "").strip() if idx is not None and idx < len(linha) else ""


def carregar_base_planilha(config: dict, credenciais: str | Path | None = None) -> tuple[list[str], list[str]]:
    """Le a aba principal e retorna textos/categorias historicas elegiveis."""
    import planilha as pl

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

    textos: list[str] = []
    categorias: list[str] = []
    for linha in valores[1:]:
        cat = _cel(linha, i_cat)
        texto = "\n".join(
            c for c in [
                _cel(linha, i_tit),
                _cel(linha, i_dg),
                _cel(linha, i_to),
                _cel(linha, i_do),
            ] if c
        )
        if cat and texto:
            textos.append(texto)
            categorias.append(cat)
    return textos, categorias


def plotar_history(history: dict, caminho: str | Path) -> None:
    """Plota loss/val_loss e accuracy/val_accuracy por epoca."""
    import matplotlib.pyplot as plt

    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    epocas = range(1, len(history.get("loss", [])) + 1)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].plot(epocas, history.get("loss", []), marker="o", label="loss")
    if history.get("val_loss"):
        axes[0].plot(epocas, history.get("val_loss", []), marker="o", label="val_loss")
    axes[0].set_title("Perda por epoca")
    axes[0].set_xlabel("Epoca")
    axes[0].set_ylabel("Loss")
    axes[0].grid(alpha=0.3)
    axes[0].legend()

    axes[1].plot(epocas, history.get("accuracy", []), marker="o", label="accuracy")
    if history.get("val_accuracy"):
        axes[1].plot(epocas, history.get("val_accuracy", []), marker="o", label="val_accuracy")
    axes[1].set_title("Acuracia por epoca")
    axes[1].set_xlabel("Epoca")
    axes[1].set_ylabel("Accuracy")
    axes[1].grid(alpha=0.3)
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(caminho, dpi=220)
    plt.close(fig)


class ClassificadorLSTM:
    def __init__(
        self,
        vocab_size: int = LSTM_VOCAB_SIZE,
        max_len: int = LSTM_MAX_LEN,
        embed_dim: int = LSTM_EMBED_DIM,
        units: int = LSTM_UNITS,
        dense_units: int = LSTM_DENSE_UNITS,
        dropout: float = LSTM_DROPOUT,
        layers: int = LSTM_LAYERS,
    ):
        self.vocab_size = vocab_size
        self.max_len = max_len
        self.embed_dim = embed_dim
        self.units = units
        self.dense_units = dense_units
        self.dropout = dropout
        self.layers = max(1, int(layers))
        self.model = None
        self.tokenizer = None
        self.classes_ = None  # np.ndarray de categorias (índice = id da classe)

    def _vetorizar(self, textos):
        tf = _tf()
        seqs = self.tokenizer.texts_to_sequences(list(textos))
        return tf.keras.preprocessing.sequence.pad_sequences(
            seqs, maxlen=self.max_len, padding="post", truncating="post"
        )

    def fit(self, textos, categorias, epochs: int = 15, batch_size: int = 128,
            validation_split: float = 0.1, paciencia: int = 3, verbose: int = 2,
            usar_class_weight: bool = True):
        tf = _tf()
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import (
            Embedding, Bidirectional, LSTM, Dense, Dropout,
        )
        from tensorflow.keras.preprocessing.text import Tokenizer
        from tensorflow.keras.callbacks import EarlyStopping
        from sklearn.utils.class_weight import compute_class_weight

        categorias = list(categorias)
        self.classes_ = np.array(sorted(set(categorias)), dtype=object)
        cat_para_id = {c: i for i, c in enumerate(self.classes_)}
        y = np.array([cat_para_id[c] for c in categorias], dtype=np.int32)

        class_weight = None
        if usar_class_weight:
            pesos = compute_class_weight(
                "balanced", classes=np.arange(len(self.classes_)), y=y
            )
            class_weight = {i: float(w) for i, w in enumerate(pesos)}

        self.tokenizer = Tokenizer(num_words=self.vocab_size, oov_token="<OOV>")
        self.tokenizer.fit_on_texts(list(textos))
        X = self._vetorizar(textos)

        n_classes = len(self.classes_)
        camadas = [Embedding(self.vocab_size, self.embed_dim, input_length=self.max_len)]
        for idx_camada in range(self.layers):
            camadas.append(Bidirectional(LSTM(
                self.units,
                return_sequences=(idx_camada < self.layers - 1),
            )))
            camadas.append(Dropout(float(self.dropout)))
        camadas.extend([
            Dense(int(self.dense_units), activation="relu"),
            Dense(n_classes, activation="softmax"),
        ])
        self.model = Sequential(camadas)
        self.model.compile(
            optimizer="adam",
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )
        early = EarlyStopping(monitor="val_loss", patience=paciencia,
                              restore_best_weights=True)
        historico = self.model.fit(
            X, y,
            epochs=epochs, batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[early], verbose=verbose,
            class_weight=class_weight,
        )
        # loss/val_loss/accuracy/val_accuracy por epoca (curvas de
        # aprendizado); nao afeta o comportamento existente do fit().
        self.history_ = {
            metrica: [float(v) for v in valores]
            for metrica, valores in historico.history.items()
        }
        return self

    def salvar_history(self, caminho) -> None:
        """Grava self.history_ (loss/val_loss/accuracy/val_accuracy por
        epoca) em JSON para diagnostico de overfitting/underfitting.
        Sem custo de treino extra: reaproveita o History ja retornado pelo
        Keras em fit(). Requer que fit() ja tenha sido chamado.
        """
        if not hasattr(self, "history_"):
            raise RuntimeError("Chame fit() antes de salvar_history().")
        caminho = Path(caminho)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(
            json.dumps(self.history_, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def predict_com_conf(self, textos):
        X = self._vetorizar(textos)
        probs = self.model.predict(X, verbose=0)
        idx = probs.argmax(axis=1)
        preds = self.classes_[idx]
        confs = probs[np.arange(len(idx)), idx]
        return preds, confs

    def predict_dist(self, textos):
        """(classes_, matriz n x K do softmax completo)."""
        X = self._vetorizar(textos)
        return self.classes_, self.model.predict(X, verbose=0)

    def save(self, diretorio: str | Path) -> None:
        d = Path(diretorio)
        d.mkdir(parents=True, exist_ok=True)
        self.model.save(d / "modelo.keras")
        with (d / "tokenizer.json").open("w", encoding="utf-8") as f:
            f.write(self.tokenizer.to_json())
        with (d / "classes.json").open("w", encoding="utf-8") as f:
            json.dump(list(self.classes_), f, ensure_ascii=False)
        with (d / "config.json").open("w", encoding="utf-8") as f:
            json.dump(
                {"vocab_size": self.vocab_size, "max_len": self.max_len,
                 "embed_dim": self.embed_dim, "units": self.units,
                 "dense_units": self.dense_units, "dropout": self.dropout,
                 "layers": self.layers}, f,
            )

    @classmethod
    def load(cls, diretorio: str | Path) -> "ClassificadorLSTM":
        tf = _tf()
        from tensorflow.keras.preprocessing.text import tokenizer_from_json
        d = Path(diretorio)
        with (d / "config.json").open("r", encoding="utf-8") as f:
            cfg = json.load(f)
        obj = cls(**cfg)
        obj.model = tf.keras.models.load_model(d / "modelo.keras")
        with (d / "tokenizer.json").open("r", encoding="utf-8") as f:
            obj.tokenizer = tokenizer_from_json(f.read())
        with (d / "classes.json").open("r", encoding="utf-8") as f:
            obj.classes_ = np.array(json.load(f), dtype=object)
        return obj


def _parse_args():
    import argparse

    p = argparse.ArgumentParser(description="Treina LSTM real e salva curva de aprendizado.")
    p.add_argument("--config", type=Path, default=Path(__file__).resolve().parents[1] / "config_experimento.json")
    p.add_argument("--credenciais", default=None)
    p.add_argument("--history-json", type=Path,
                   default=Path(__file__).resolve().parents[1] / "04_artigo" / "figuras" / "lstm_history.json")
    p.add_argument("--history-fig", type=Path,
                   default=Path(__file__).resolve().parents[1] / "04_artigo" / "figuras" / "fig5_curva_aprendizado_lstm.png")
    p.add_argument("--epochs", type=int, default=None)
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--validation-split", type=float, default=0.1)
    p.add_argument("--verbose", type=int, default=2)
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    lstm_cfg = dict((config.get("modelo_ia", {}) or {}).get("lstm", {}) or {})
    params = resolver_parametros_lstm(lstm_cfg)
    epochs = int(args.epochs or params.pop("epochs", 15))
    batch_size = int(args.batch_size or params.pop("batch_size", 128))
    paciencia = int(params.pop("paciencia", 3))
    validation_split = float(args.validation_split)
    usar_class_weight = bool(params.pop("usar_class_weight", True))

    try:
        textos, categorias = carregar_base_planilha(config, args.credenciais)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"Falha ao acessar a planilha: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    if len(textos) < 2:
        print("Informação insuficiente para verificar.")
        return 1

    print(f"treino_lstm: exemplos={len(textos)} categorias={len(set(categorias))} params={params}")
    clf = ClassificadorLSTM(**params)
    clf.fit(
        textos,
        categorias,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=validation_split,
        paciencia=paciencia,
        verbose=args.verbose,
        usar_class_weight=usar_class_weight,
    )
    clf.salvar_history(args.history_json)
    plotar_history(clf.history_, args.history_fig)
    print(f"history_json={args.history_json}")
    print(f"history_fig={args.history_fig}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
