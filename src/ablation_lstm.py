#!/usr/bin/env python3
"""Ablation study do LSTM: units 64/128 x dropout 0.5/0.3.

Treina modelos reais em folds e mede acerto contra a verdade validada humana.
Nao escreve na planilha.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decisao_validada as dv  # noqa: E402
import classificacao_multimodelo as cm  # noqa: E402
import memoria_validada as mv  # noqa: E402
import modelo_lstm  # noqa: E402
import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402


RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
SAIDA_JSON = RAIZ / "04_artigo" / "figuras" / "ablation_lstm_resultados.json"
SAIDA_CSV = RAIZ / "04_artigo" / "figuras" / "tabela_S3_ablation_lstm.csv"
SAIDA_FIG = RAIZ / "04_artigo" / "figuras" / "fig_ablation_lstm"
SAIDA_DIAG = RAIZ / "04_artigo" / "figuras" / "diagnostico_ablation_lstm_duplicatas.json"
SAIDA_DIAG_PROTOCOLO = RAIZ / "04_artigo" / "figuras" / "diagnostico_ablation_lstm_protocolo.json"
SAIDA_DIAG_MATERIALIZACAO = RAIZ / "04_artigo" / "figuras" / "diagnostico_materializacao_lstm_nova.json"


def _cel(linha, idx) -> str:
    return str(linha[idx] or "").strip() if idx is not None and idx < len(linha) else ""


def normalizar_texto(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", str(texto or ""))
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acento.casefold()).strip()


def hash_texto_normalizado(texto: str) -> str:
    return hashlib.sha256(normalizar_texto(texto).encode("utf-8")).hexdigest()


def carregar_elegiveis(config: dict, credenciais=None):
    sh = pl.abrir_planilha(pl.id_planilha(config), credenciais)
    ws = sh.worksheet(config["aba_principal"])
    valores = pl.ler_valores(ws, config["range_leitura"])
    cab = valores[0] if valores else []
    norm = lambda s: " ".join(str(s or "").split()).casefold()  # noqa: E731
    idx = {norm(nome): i for i, nome in enumerate(cab)}
    i_id = idx.get(norm("ID Chamado"))
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
            # O id acompanha a linha porque tudo que cruza com abas
            # materializadas precisa casar por id_chamado, nao por posicao.
            linhas.append({"linha": pos, "id": dv._normalizar_id(_cel(linha, i_id)),  # noqa: SLF001
                           "texto": texto, "historico": cat})
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
    from sklearn.model_selection import GroupKFold

    idx_validados = [i for i, item in enumerate(linhas) if item["linha"] in verdade]
    if len(idx_validados) < 2:
        raise RuntimeError("Informação insuficiente para verificar.")
    grupos_por_indice = [hash_texto_normalizado(item["texto"]) for item in linhas]
    grupos_validados = [grupos_por_indice[i] for i in idx_validados]
    n_grupos = len(set(grupos_validados))
    if n_grupos < 2:
        raise RuntimeError("Informação insuficiente para verificar.")
    kk = max(2, min(int(k_folds), n_grupos))
    acertos = []
    kf = GroupKFold(n_splits=kk)
    todos_indices = range(len(linhas))
    for fold, (_tr_rel, te_rel) in enumerate(kf.split(idx_validados, groups=grupos_validados), start=1):
        teste_idx = [idx_validados[i] for i in te_rel]
        grupos_teste = {grupos_por_indice[i] for i in teste_idx}
        treino_idx = [i for i in todos_indices if grupos_por_indice[i] not in grupos_teste]
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


def diagnosticar_duplicatas_folds(linhas: list[dict], verdade: dict[int, str], k_folds: int) -> dict:
    from sklearn.model_selection import KFold

    idx_validados = [i for i, item in enumerate(linhas) if item["linha"] in verdade]
    if len(idx_validados) < 2:
        raise RuntimeError("Informação insuficiente para verificar.")

    kk = max(2, min(int(k_folds), len(idx_validados)))
    grupos_por_indice = [hash_texto_normalizado(item["texto"]) for item in linhas]
    grupos_validados = [grupos_por_indice[i] for i in idx_validados]
    grupos_corpus = {}
    for grupo in grupos_por_indice:
        grupos_corpus[grupo] = grupos_corpus.get(grupo, 0) + 1
    grupos_validado = {}
    for grupo in grupos_validados:
        grupos_validado[grupo] = grupos_validado.get(grupo, 0) + 1

    folds = []
    total_teste = 0
    total_vazado = 0
    kf = KFold(n_splits=kk, shuffle=True, random_state=42)
    todos_indices = set(range(len(linhas)))
    for fold, (_tr_rel, te_rel) in enumerate(kf.split(idx_validados), start=1):
        teste_idx = [idx_validados[i] for i in te_rel]
        treino_idx = sorted(todos_indices - set(teste_idx))
        grupos_treino = {grupos_por_indice[i] for i in treino_idx}
        vazados = [i for i in teste_idx if grupos_por_indice[i] in grupos_treino]
        total_teste += len(teste_idx)
        total_vazado += len(vazados)
        folds.append({
            "fold": fold,
            "n_teste": len(teste_idx),
            "teste_com_duplicata_no_treino": len(vazados),
            "taxa_vazamento": round(len(vazados) / len(teste_idx), 6) if teste_idx else 0.0,
        })

    return {
        "gerado_em": agora_bahia(),
        "script_origem": "src/ablation_lstm.py",
        "metodo_avaliado": "KFold aleatorio por linha usado anteriormente no ablation",
        "normalizacao": "NFKD sem acentos, casefold, espacos colapsados",
        "k_folds": kk,
        "n_linhas_elegiveis": len(linhas),
        "n_validado": len(idx_validados),
        "grupos_texto_elegiveis": len(grupos_corpus),
        "grupos_texto_validados": len(grupos_validado),
        "grupos_duplicados_elegiveis": sum(1 for n in grupos_corpus.values() if n > 1),
        "grupos_duplicados_validados": sum(1 for n in grupos_validado.values() if n > 1),
        "teste_com_duplicata_no_treino": total_vazado,
        "taxa_vazamento": round(total_vazado / total_teste, 6) if total_teste else 0.0,
        "folds": folds,
    }


def carregar_predicoes_oficiais_lstm(sh, config: dict) -> dict[int, dict]:
    """Le a aba CLASSIF__lstm materializada pelo protocolo oficial."""
    template = config["multimodelo"]["aba_classificacao"]
    aba = template.replace("{modelo}", "lstm")
    try:
        vals = sh.worksheet(aba).get_values("A:K", value_render_option="UNFORMATTED_VALUE")
    except Exception:  # noqa: BLE001
        return {}
    out = {}
    for r in vals[1:]:
        if len(r) < 6:
            continue
        # id_chamado (coluna 2), nunca linha_planilha: este mapa e cruzado com a
        # verdade lida da aba principal, que muda de tamanho quando o GLPI ganha
        # ou perde chamados (incidente de 02/08/2026).
        linha = dv._normalizar_id(r[2] if len(r) > 2 else "")  # noqa: SLF001
        if not linha:
            continue
        pred = str(r[4] or "").strip()
        if not pred:
            continue
        out[linha] = {
            "run_id": str(r[0] or "").strip() if len(r) > 0 else "",
            "pred": pred,
            "conf": r[5],
            "faixa": str(r[6] or "").strip() if len(r) > 6 else "",
            "executor": str(r[7] or "").strip() if len(r) > 7 else "",
            "acerto_historico": str(r[8] or "").strip() if len(r) > 8 else "",
            "data": str(r[10] or "").strip() if len(r) > 10 else "",
        }
    return out


def _taxa(numerador: int, denominador: int) -> float | None:
    return round(numerador / denominador, 6) if denominador else None


def _parse_float(valor) -> float | None:
    try:
        return float(str(valor).replace("%", "").replace(",", ".").strip())
    except (TypeError, ValueError):
        return None


def _resumo_counter(valores, limite: int = 12) -> dict:
    return {str(k): int(v) for k, v in Counter(v for v in valores if str(v or "").strip()).most_common(limite)}


def resumir_predicoes_oficiais(predicoes: dict[int, dict]) -> dict:
    confs = [v for v in (_parse_float(p.get("conf")) for p in predicoes.values()) if v is not None]
    acerto_hist = [str(p.get("acerto_historico") or "").strip().casefold() for p in predicoes.values()]
    return {
        "run_ids": _resumo_counter(p.get("run_id") for p in predicoes.values()),
        "datas_gravacao": _resumo_counter((p.get("data") for p in predicoes.values()), limite=20),
        "executores": _resumo_counter(p.get("executor") for p in predicoes.values()),
        "faixas": _resumo_counter(p.get("faixa") for p in predicoes.values()),
        "acerto_historico_true": sum(1 for v in acerto_hist if v == "true"),
        "acerto_historico_false": sum(1 for v in acerto_hist if v == "false"),
        "confianca": {
            "n": len(confs),
            "media": round(float(np.mean(confs)), 6) if confs else None,
            "min": round(float(np.min(confs)), 6) if confs else None,
            "max": round(float(np.max(confs)), 6) if confs else None,
        },
    }


def diagnosticar_parametros_lstm(config: dict) -> dict:
    lstm_cfg = dict((config.get("modelo_ia", {}) or {}).get("lstm", {}) or {})
    params_ablation = modelo_lstm.resolver_parametros_lstm(lstm_cfg)
    params_producao_sem_config = modelo_lstm.resolver_parametros_lstm(None)
    def _separar(params: dict) -> tuple[dict, dict]:
        p = dict(params)
        fit = {
            "epochs": int(p.pop("epochs", 15)),
            "batch_size": int(p.pop("batch_size", 128)),
            "paciencia": int(p.pop("paciencia", 3)),
            "validation_split": float(p.pop("validation_split", 0.1)),
            "usar_class_weight": bool(p.pop("usar_class_weight", True)),
        }
        return p, fit

    init_ablation, fit_ablation = _separar(params_ablation)
    init_producao, fit_producao = _separar(params_producao_sem_config)
    return {
        "env_LSTM_PERFIL": os.getenv("LSTM_PERFIL"),
        "config_modelo_ia_lstm": lstm_cfg,
        "ablation_resolve_com_config": params_ablation,
        "producao_resolve_sem_config": params_producao_sem_config,
        "ablation_init_model": init_ablation,
        "producao_init_model": init_producao,
        "ablation_fit_efetivo": fit_ablation,
        "producao_fit_efetivo": fit_producao,
        "parametros_efetivos_iguais_no_ambiente_atual": init_ablation == init_producao and fit_ablation == fit_producao,
        "observacao": (
            "modelos_zoo._ModeloLSTM chama classificador_producao.treinar_classificador "
            "sem repassar config_experimento['modelo_ia']['lstm']; no ambiente atual, "
            "os parametros efetivos ainda podem coincidir se o perfil efetivo for padrao "
            "e os defaults de fit forem os mesmos."
        ),
    }


def diagnosticar_protocolos_lstm(sh, config: dict, linhas: list[dict], verdade: dict[int, str],
                                 k_folds_ablation: int) -> dict:
    """Compara o ablation com a avaliacao oficial sem re-treinar modelos.

    O objetivo e quantificar hipoteses metodologicas residuais com dados vivos:
    se a verdade humana coincide com o historico, como a aba oficial CLASSIF__lstm
    performa na mesma intersecao e quais diferencas de protocolo sao observaveis
    no codigo/configuracao.
    """
    # Por id_chamado: `verdade` e a aba CLASSIF__lstm sao ambas indexadas por id,
    # e a posicao na planilha muda quando a base muda de tamanho.
    por_linha = {(item.get("id") or item["linha"]): item for item in linhas}
    validadas = sorted(ln for ln in verdade if ln in por_linha)
    historico_igual = [ln for ln in validadas if por_linha[ln]["historico"] == verdade[ln]]
    historico_diferente = [ln for ln in validadas if por_linha[ln]["historico"] != verdade[ln]]

    predicoes = carregar_predicoes_oficiais_lstm(sh, config)
    resumo_predicoes = resumir_predicoes_oficiais(predicoes)
    comuns = [ln for ln in validadas if ln in predicoes]
    acertos_oficial = [ln for ln in comuns if predicoes[ln]["pred"] == verdade[ln]]
    oficial_acerta_historico_igual = [
        ln for ln in comuns
        if por_linha[ln]["historico"] == verdade[ln] and predicoes[ln]["pred"] == verdade[ln]
    ]
    oficial_acerta_historico_diferente = [
        ln for ln in comuns
        if por_linha[ln]["historico"] != verdade[ln] and predicoes[ln]["pred"] == verdade[ln]
    ]

    mm = config.get("multimodelo", {}) or {}
    return {
        "gerado_em": agora_bahia(),
        "script_origem": "src/ablation_lstm.py",
        "natureza": "diagnostico de protocolo; nao re-treina modelos e nao escreve na planilha",
        "hipoteses_testadas": [
            "avaliacao oficial usa predicoes ja materializadas em CLASSIF__lstm",
            "ablation treina LSTM novo por fold contra rotulo historico e mede contra verdade humana",
            "verdade humana pode coincidir com o historico em grande parte dos validados",
            "protocolo oficial multimodelo usa k-fold configurado separadamente do ablation",
        ],
        "config_multimodelo": {
            "k_folds_oficial": mm.get("k_folds"),
            "aba_classificacao": mm.get("aba_classificacao"),
            "memoria_validada_habilitada": bool((config.get("memoria_validada") or {}).get("habilitada", True)),
            "peso_memoria_validada": (config.get("memoria_validada") or {}).get("peso_treino"),
        },
        "config_ablation": {
            "k_folds_ablation": k_folds_ablation,
            "particionamento": "GroupKFold por hash de texto normalizado nos validados; treino usa todos os demais grupos elegiveis",
            "rotulo_treino": "CATEGORIA COMPLETA historica",
        },
        "parametros_lstm_resolvidos": diagnosticar_parametros_lstm(config),
        "escopo": {
            "n_linhas_elegiveis_ablation": len(linhas),
            "n_validadas_com_verdade": len(validadas),
            "n_predicoes_oficiais_lstm": len(predicoes),
            "n_intersecao_validada_oficial": len(comuns),
        },
        "materializacao_oficial_lstm": resumo_predicoes,
        "historico_vs_verdade": {
            "historico_igual_verdade": len(historico_igual),
            "historico_diferente_verdade": len(historico_diferente),
            "taxa_historico_igual_verdade": _taxa(len(historico_igual), len(validadas)),
        },
        "oficial_lstm_vs_verdade": {
            "acertos": len(acertos_oficial),
            "erros": len(comuns) - len(acertos_oficial),
            "taxa_acerto": _taxa(len(acertos_oficial), len(comuns)),
            "acertos_quando_historico_igual_verdade": len(oficial_acerta_historico_igual),
            "taxa_quando_historico_igual_verdade": _taxa(len(oficial_acerta_historico_igual), len([ln for ln in comuns if por_linha[ln]["historico"] == verdade[ln]])),
            "acertos_quando_historico_diferente_verdade": len(oficial_acerta_historico_diferente),
            "taxa_quando_historico_diferente_verdade": _taxa(len(oficial_acerta_historico_diferente), len([ln for ln in comuns if por_linha[ln]["historico"] != verdade[ln]])),
        },
        "diferencas_de_protocolo_verificadas_no_codigo": [
            "src/avaliacao_final.py avalia predicoes ja gravadas em CLASSIF__<modelo>; nao instancia nem treina o LSTM.",
            "src/classificacao_multimodelo.py gera CLASSIF__lstm com k-fold configurado em config_experimento.json e pode usar memoria validada como base fixa.",
            "src/ablation_lstm.py treina modelo_lstm.ClassificadorLSTM diretamente em cada fold e usa categoria historica como y de treino.",
            "src/ablation_lstm.py usa GroupKFold por hash de texto normalizado; o protocolo oficial multimodelo usa KFold por linha no lote.",
        ],
    }


def _avaliar_predicoes_por_linha(linhas: list[dict], verdade: dict[int, str], pred_por_linha: dict[int, dict]) -> dict:
    validadas = sorted(ln for ln in verdade if ln in pred_por_linha)
    acertos = [ln for ln in validadas if pred_por_linha[ln]["pred"] == verdade[ln]]
    confs = [v for v in (_parse_float(pred_por_linha[ln].get("conf")) for ln in validadas) if v is not None]
    return {
        "n_avaliado": len(validadas),
        "acertos": len(acertos),
        "erros": len(validadas) - len(acertos),
        "taxa_acerto": _taxa(len(acertos), len(validadas)),
        "confianca": {
            "n": len(confs),
            "media": round(float(np.mean(confs)), 6) if confs else None,
            "min": round(float(np.min(confs)), 6) if confs else None,
            "max": round(float(np.max(confs)), 6) if confs else None,
        },
    }


def diagnosticar_materializacao_oficial_nova(sh, config: dict, linhas: list[dict],
                                             verdade: dict[int, str]) -> dict:
    """Reexecuta o caminho oficial do LSTM em memoria, sem escrever na planilha.

    Usa o mesmo helper de classificacao_multimodelo que materializa CLASSIF__lstm,
    mas nao chama gravar_classificacao(), append_aba() nem atualizar_metricas().
    """
    mm = config["multimodelo"]
    lote = [
        {
            "linha": item["linha"],
            "id": item.get("id", ""),
            "titulo": "",
            "categoria_original": item["historico"],
            "texto": item["texto"],
        }
        for item in linhas
    ]

    memoria_cfg = config.get("memoria_validada", {})
    memoria = []
    if memoria_cfg.get("habilitada", True):
        memoria = mv.carregar_memoria_validada(sh, config["abas_experimento"]["validacao_humana"])
    peso_mem = int(memoria_cfg.get("peso_treino", 3))
    mem_textos, mem_cats = mv.expandir_treino_com_memoria([], [], memoria, peso=peso_mem)

    preds, scores, metodo, _usou_fallback = cm.prever_out_of_fold(
        "lstm",
        lote,
        mem_textos,
        mem_cats,
        k_folds=int(mm.get("k_folds", 5)),
        min_base=int(mm.get("min_base_treino", 200)),
        fracao_topup=float(mm.get("fracao_topup", 0.25)),
    )
    pred_nova = {
        (item.get("id") or item["linha"]): {"pred": str(pred), "conf": float(score)}
        for item, pred, score in zip(lote, preds, scores)
        if pred is not None
    }
    pred_antiga = carregar_predicoes_oficiais_lstm(sh, config)
    avaliacao_nova = _avaliar_predicoes_por_linha(linhas, verdade, pred_nova)
    avaliacao_antiga = _avaliar_predicoes_por_linha(linhas, verdade, pred_antiga)
    comuns = sorted(ln for ln in pred_nova if ln in pred_antiga and ln in verdade)
    mudou_pred = [ln for ln in comuns if pred_nova[ln]["pred"] != pred_antiga[ln]["pred"]]
    nova_acerta_antiga_erra = [
        ln for ln in comuns
        if pred_nova[ln]["pred"] == verdade[ln] and pred_antiga[ln]["pred"] != verdade[ln]
    ]
    antiga_acerta_nova_erra = [
        ln for ln in comuns
        if pred_antiga[ln]["pred"] == verdade[ln] and pred_nova[ln]["pred"] != verdade[ln]
    ]
    return {
        "gerado_em": agora_bahia(),
        "script_origem": "src/ablation_lstm.py",
        "natureza": "materializacao oficial nova em memoria; read-only; nao escreve em CLASSIF__lstm",
        "metodo_materializacao_nova": metodo,
        "config_multimodelo": {
            "k_folds": int(mm.get("k_folds", 5)),
            "min_base_treino": int(mm.get("min_base_treino", 200)),
            "fracao_topup": float(mm.get("fracao_topup", 0.25)),
            "memoria_validada": len(memoria),
            "peso_memoria_validada": peso_mem,
        },
        "parametros_lstm_resolvidos": diagnosticar_parametros_lstm(config),
        "escopo": {
            "n_linhas_elegiveis": len(linhas),
            "n_validadas_com_verdade": len(verdade),
            "n_predicoes_novas": len(pred_nova),
            "n_predicoes_antigas": len(pred_antiga),
            "n_intersecao_nova_antiga_validada": len(comuns),
        },
        "materializacao_nova_vs_verdade": avaliacao_nova,
        "materializacao_antiga_vs_verdade": avaliacao_antiga,
        "comparacao_nova_antiga": {
            "predicoes_diferentes": len(mudou_pred),
            "taxa_predicoes_diferentes": _taxa(len(mudou_pred), len(comuns)),
            "nova_acerta_antiga_erra": len(nova_acerta_antiga_erra),
            "antiga_acerta_nova_erra": len(antiga_acerta_nova_erra),
            "saldo_acertos_nova_menos_antiga": len(nova_acerta_antiga_erra) - len(antiga_acerta_nova_erra),
        },
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
    """Delega o desenho ao gerador dedicado da Figura 6.

    O ablation ja gravou `SAIDA_JSON`; o gerador le esse arquivo. Manter um
    unico gerador evita divergencia de estilo entre a figura do experimento e
    a figura do artigo.
    """
    from gerar_figura6_ablation import gerar as gerar_figura6

    gerar_figura6(SAIDA_JSON, SAIDA_FIG)


def parse_args():
    p = argparse.ArgumentParser(description="Ablation real do LSTM contra acerto validado.")
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--k-folds", type=int, default=3)
    p.add_argument("--epochs", type=int, default=None)
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--validation-split", type=float, default=0.1)
    p.add_argument("--diagnostico-only", action="store_true")
    p.add_argument("--diagnostico-protocolo-only", action="store_true")
    p.add_argument("--diagnostico-materializacao-oficial-only", action="store_true")
    p.add_argument("--verbose", type=int, default=2)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    lstm_cfg = dict((config.get("modelo_ia", {}) or {}).get("lstm", {}) or {})
    params = modelo_lstm.resolver_parametros_lstm(lstm_cfg)
    epochs_padrao = params.pop("epochs", 15)
    batch_size_padrao = params.pop("batch_size", 128)
    epochs = int(args.epochs or epochs_padrao)
    batch_size = int(args.batch_size or batch_size_padrao)
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
    verdade = dv.verdade_validada(
        dv.carregar_decisoes(sh, config["aba_principal"], chave="id"))
    if len(verdade) < 2:
        print("Informação insuficiente para verificar.")
        return 1

    if args.diagnostico_only:
        diagnostico = diagnosticar_duplicatas_folds(linhas, verdade, args.k_folds)
        SAIDA_DIAG.parent.mkdir(parents=True, exist_ok=True)
        SAIDA_DIAG.write_text(json.dumps(diagnostico, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"diagnostico_json={SAIDA_DIAG}")
        return 0

    if args.diagnostico_protocolo_only:
        diagnostico = diagnosticar_protocolos_lstm(sh, config, linhas, verdade, args.k_folds)
        SAIDA_DIAG_PROTOCOLO.parent.mkdir(parents=True, exist_ok=True)
        SAIDA_DIAG_PROTOCOLO.write_text(json.dumps(diagnostico, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"diagnostico_protocolo_json={SAIDA_DIAG_PROTOCOLO}")
        return 0

    if args.diagnostico_materializacao_oficial_only:
        diagnostico = diagnosticar_materializacao_oficial_nova(sh, config, linhas, verdade)
        SAIDA_DIAG_MATERIALIZACAO.parent.mkdir(parents=True, exist_ok=True)
        SAIDA_DIAG_MATERIALIZACAO.write_text(json.dumps(diagnostico, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"diagnostico_materializacao_json={SAIDA_DIAG_MATERIALIZACAO}")
        return 0

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
        "natureza": "acerto contra verdade validada humana; GroupKFold por hash de texto normalizado",
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
