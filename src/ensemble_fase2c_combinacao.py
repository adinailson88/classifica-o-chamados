#!/usr/bin/env python3
"""Fase 2C: combinacao dos sete modelos-base do ensemble (Execucao Cientifica 1).

Ferramenta estritamente READ-ONLY. NAO treina nenhum dos sete modelos-base,
NAO executa LSTM e NAO consulta a planilha operacional viva para H/R/Y.
Consome exclusivamente:

  - H, R, Y (alvo_inadequacao), grupo_sha256 e outer_fold ja congelados em
    `docs/dados/ensemble/recongelamento_online/alvo_ensemble_online.json`
    (o mesmo alvo que o Gate Zero da Fase 2B validou contra
    `ensemble_fase2b_crossfit.HASHES_ESPERADOS` — ver
    docs/FASE2C_ENSEMBLE_CONTRATO.md para a auditoria de proveniencia);
  - as previsoes internas e externas ja publicadas pela Execucao Cientifica 1
    (GitHub Actions run 31556028058, commit d6a5504c, artifact
    `fase2b-resultado-cientifico`: `fase2b_inner_scores.npz` +
    `fase2b_outer_scores.npz` + `fase2b_manifesto.json` + `fase2b_resumo.json`
    + `fase2b_hashes.json`), cujos hashes de entrada E de saida sao
    verificados byte a byte contra os valores aprovados antes de qualquer
    combinacao (`validar_proveniencia`, `verificar_hashes_recomputados`).

Alvo (ja congelado, nunca recalculado aqui): Y_i = 1(H_i != R_i). Treino do
meta-modelo de stacking usa somente H_i in C (dominio aprendido pelos sete
modelos-base), a mesma restricao da Fase 2B.

Implementa os quatro metodos do contrato vigente:

  1. baseline LinearSVC (s_ls);
  2. votacao majoritaria (s_maj);
  3. votacao suave ponderada (s_soft);
  4. stacking (s_stack = q_i).

Duas escolhas metodologicas desta rodada NAO tem contrato congelado anterior
(nenhum documento do repositorio definia Fase 2C antes desta implementacao)
e ficam explicitas, parametrizaveis e sinalizadas para confirmacao, nunca
travadas em silencio — ver docs/FASE2C_ENSEMBLE_CONTRATO.md:

  - peso da votacao suave = acuracia de cada modelo nas previsoes EXTERNAS
    (out-of-fold por construcao) contra R, normalizada para somar 1
    (`pesos_votacao_suave`);
  - selecao de tau na curva Precision-Recall de Y=1 = maximo F1 por padrao,
    outro criterio e explicito via parametro (`selecionar_tau`).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

import ensemble_fase2b_crossfit as efc  # noqa: E402
import recongelar_ensemble_online as rero  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DADOS_ENSEMBLE = RAIZ / "docs" / "dados" / "ensemble"
ENTRADA_FASE2B_PADRAO = DADOS_ENSEMBLE / "fase2b"
ALVO_PADRAO = rero.ALVO_ONLINE_PADRAO
CLASSES_PATH_PADRAO = efc.CLASSES_PATH_PADRAO
SAIDA_DIR_PADRAO = DADOS_ENSEMBLE / "fase2c"

MODELOS = list(efc.MODELOS)  # mesma ordem fixa dos 7 modelos-base, sem duplicar
FOLDS = efc.FOLDS
CLASSES_ESPERADAS = efc.CLASSES_ESPERADAS

# Hashes de proveniencia da Execucao Cientifica 1 (unica fonte aprovada; ver
# docs/REPLAY_CONGELADO_FASE2B.md secao 9 — nenhuma Execucao Cientifica 2 foi
# aprovada). Distintos de `efc.HASHES_ESPERADOS` (hashes de ENTRADA do Gate
# Zero): estes sao os hashes de SAIDA do cross-fitting, tal como publicados
# no artifact `fase2b-resultado-cientifico`. Pinados para que a Fase 2C nunca
# combine, silenciosamente, previsoes de uma reexecucao diferente — mesmo
# que essa reexecucao reproduzisse os mesmos 5 hashes de entrada.
RUN_ID_EXECUCAO_1 = "31556028058"
COMMIT_SHA_EXECUCAO_1 = "d6a5504cd9c4360b97fd90dd88c13bd430155459"
HASHES_EXECUCAO_1_ESPERADOS = {
    "input_bundle_sha256": "a533e245d97482f423bb9981df350ad6ec550133a2253c3a5f528f086459e83f",
    "inner_predictions_canonical_sha256": "98e38ea42236210ba430ed322b5872062e7ac0eba2ec3d64d06566b11802b0d1",
    "outer_predictions_canonical_sha256": "660d3f451040615a08bac1934f6ac157ac0052b5c98fe7890508c9e064d61e6d",
    "crossfit_manifest_sha256": "5e9c8cd975017867b96dcf543b90ad90c7ec989939ad934cca5dd175c32179e3",
    "fase2b_science_sha256": "931c8092e372d6d416b0763bc55bfd74c856aeb1cf4c321dd55081ea16d82470",
}


class Fase2CBloqueado(RuntimeError):
    """Erro base: qualquer subclasse interrompe a rodada sem publicar nada."""


class ProveninciaDivergente(Fase2CBloqueado):
    """Hashes da Execucao Cientifica 1 (entrada OU saida) nao batem com os
    aprovados: a Fase 2C nunca combina previsoes de uma execucao diferente."""


class JuncaoInvalida(Fase2CBloqueado):
    """IDs, folds ou classes divergentes entre previsoes e alvo congelado."""


# --------------------------------------------------------------------------
# Carregamento (read-only, nunca a planilha viva)
# --------------------------------------------------------------------------

def carregar_hashes_execucao(entrada_dir: Path) -> dict[str, str]:
    return json.loads((entrada_dir / "fase2b_hashes.json").read_text(encoding="utf-8"))


def carregar_resumo_execucao(entrada_dir: Path) -> dict[str, Any]:
    return json.loads((entrada_dir / "fase2b_resumo.json").read_text(encoding="utf-8"))


def carregar_manifesto_execucao(entrada_dir: Path) -> dict[str, Any]:
    return json.loads((entrada_dir / "fase2b_manifesto.json").read_text(encoding="utf-8"))


def carregar_alvo(alvo_path: Path = ALVO_PADRAO) -> dict[str, dict[str, Any]]:
    """H, R, Y, grupo_sha256 e outer_fold por id_sha256, direto do alvo ja
    congelado (mesma fonte que o Gate Zero da Fase 2B validou) — nunca a
    planilha operacional viva. Reusa `recongelar_ensemble_online`, sem
    duplicar leitura/parsing."""
    return rero.carregar_alvo_congelado(alvo_path)


def carregar_classes(classes_path: Path = CLASSES_PATH_PADRAO) -> list[str]:
    payload = json.loads(classes_path.read_text(encoding="utf-8"))
    classes = [c["label"] for c in sorted(payload["classes"], key=lambda c: c["index"])]
    if len(classes) != CLASSES_ESPERADAS:
        raise JuncaoInvalida(
            f"Total de classes divergente: {len(classes)} != {CLASSES_ESPERADAS}"
        )
    return classes


def _carregar_predicoes_agregadas_npz(caminho: Path, prefixo: str) -> list[list[Any]]:
    """Reconstroi as linhas no MESMO formato de lista que
    `ensemble_fase2b_crossfit` usa internamente (`_chave_inner`/
    `_chave_outer`, `calcular_predicoes_canonical_sha256`), a partir do
    `.npz` agregado (`fase2b_inner_scores.npz`/`fase2b_outer_scores.npz`),
    sem duplicar aquela logica de hash."""
    with np.load(caminho, allow_pickle=True) as npz:
        scores = npz["scores"]
        outer_fold = npz[f"{prefixo}_outer_fold"]
        id_sha256 = npz[f"{prefixo}_id_sha256"]
        grupo_sha256 = npz[f"{prefixo}_grupo_sha256"]
        modelo = npz[f"{prefixo}_modelo"]
        top1 = npz[f"{prefixo}_top1"]
        if prefixo == "inner":
            inner_fold = npz["inner_inner_fold"]
            return [
                [int(outer_fold[i]), int(inner_fold[i]), str(id_sha256[i]),
                 str(grupo_sha256[i]), str(modelo[i]), scores[i].tolist(), str(top1[i])]
                for i in range(len(id_sha256))
            ]
        return [
            [int(outer_fold[i]), str(id_sha256[i]), str(grupo_sha256[i]),
             str(modelo[i]), scores[i].tolist(), str(top1[i])]
            for i in range(len(id_sha256))
        ]


def carregar_predicoes_agregadas(
    entrada_dir: Path = ENTRADA_FASE2B_PADRAO,
) -> tuple[list[list[Any]], list[list[Any]]]:
    inner_rows = _carregar_predicoes_agregadas_npz(entrada_dir / "fase2b_inner_scores.npz", "inner")
    outer_rows = _carregar_predicoes_agregadas_npz(entrada_dir / "fase2b_outer_scores.npz", "outer")
    return inner_rows, outer_rows


def validar_proveniencia(entrada_dir: Path = ENTRADA_FASE2B_PADRAO) -> dict[str, Any]:
    """Confirma, ANTES de combinar qualquer previsao, que os manifests lidos
    reproduzem EXATAMENTE os hashes aprovados da Execucao Cientifica 1 (run
    31556028058) — os 5 hashes de ENTRADA do Gate Zero
    (`ensemble_fase2b_crossfit.HASHES_ESPERADOS`) e os 5 hashes de SAIDA do
    cross-fitting (`HASHES_EXECUCAO_1_ESPERADOS`). Bloqueia
    (`ProveninciaDivergente`) em qualquer divergencia, sem combinar nada."""
    hashes_arquivo = carregar_hashes_execucao(entrada_dir)
    resumo = carregar_resumo_execucao(entrada_dir)

    divergentes_saida = {
        chave: {"arquivo": hashes_arquivo.get(chave), "esperado": esperado}
        for chave, esperado in HASHES_EXECUCAO_1_ESPERADOS.items()
        if hashes_arquivo.get(chave) != esperado
    }
    if divergentes_saida:
        raise ProveninciaDivergente(
            "Hashes de SAIDA divergentes dos aprovados na Execucao Cientifica "
            f"1 (run {RUN_ID_EXECUCAO_1}): "
            + json.dumps(divergentes_saida, ensure_ascii=False, sort_keys=True)
        )

    hashes_entrada = resumo.get("hashes_entrada_gate_zero", {})
    divergentes_entrada = {
        chave: {"arquivo": hashes_entrada.get(chave), "esperado": esperado}
        for chave, esperado in efc.HASHES_ESPERADOS.items()
        if hashes_entrada.get(chave) != esperado
    }
    if divergentes_entrada:
        raise ProveninciaDivergente(
            "Hashes de ENTRADA (Gate Zero) divergentes do congelamento "
            "aprovado: " + json.dumps(divergentes_entrada, ensure_ascii=False, sort_keys=True)
        )

    contadores = resumo.get("contadores_estruturais", {})
    if contadores.get("total_modelaveis") != efc.H_DENTRO_DE_C_ESPERADO:
        raise JuncaoInvalida(
            f"total_modelaveis divergente: {contadores.get('total_modelaveis')} "
            f"!= {efc.H_DENTRO_DE_C_ESPERADO}"
        )
    return {"hashes_saida": hashes_arquivo, "hashes_entrada": hashes_entrada, "resumo": resumo}


def verificar_hashes_recomputados(
    inner_rows: list[list[Any]], outer_rows: list[list[Any]], hashes_esperados: dict[str, str]
) -> None:
    """Recalcula os hashes canonicos das previsoes carregadas do `.npz` e
    exige igualdade exata com os aprovados — prova que os arrays em memoria
    nao foram alterados/truncados/reordenados em relacao ao artifact
    original do run 31556028058, sem duplicar a logica de hash de
    `ensemble_fase2b_crossfit`."""
    inner_sha = efc.calcular_predicoes_canonical_sha256(inner_rows, efc._chave_inner)
    outer_sha = efc.calcular_predicoes_canonical_sha256(outer_rows, efc._chave_outer)
    divergentes = {}
    if inner_sha != hashes_esperados["inner_predictions_canonical_sha256"]:
        divergentes["inner_predictions_canonical_sha256"] = {
            "recomputado": inner_sha,
            "esperado": hashes_esperados["inner_predictions_canonical_sha256"],
        }
    if outer_sha != hashes_esperados["outer_predictions_canonical_sha256"]:
        divergentes["outer_predictions_canonical_sha256"] = {
            "recomputado": outer_sha,
            "esperado": hashes_esperados["outer_predictions_canonical_sha256"],
        }
    if divergentes:
        raise ProveninciaDivergente(
            "Previsoes carregadas nao reproduzem os hashes canonicos aprovados: "
            + json.dumps(divergentes, ensure_ascii=False, sort_keys=True)
        )


def montar_contexto(
    entrada_dir: Path = ENTRADA_FASE2B_PADRAO,
    alvo_path: Path = ALVO_PADRAO,
    classes_path: Path = CLASSES_PATH_PADRAO,
    verificar_hashes_predicoes: bool = True,
) -> dict[str, Any]:
    """Ponto de entrada unico da Fase 2C: valida proveniencia, carrega e
    junta tudo (H/R/Y/grupo/fold + previsoes internas/externas dos 7
    modelos), sem tocar a planilha viva e sem treinar nada."""
    proveniencia = validar_proveniencia(entrada_dir)
    classes = carregar_classes(classes_path)
    manifesto = carregar_manifesto_execucao(entrada_dir)
    if manifesto.get("ordem_classes") != classes:
        raise JuncaoInvalida("ordem_classes do manifesto diverge de classes_ensemble.json.")
    if manifesto.get("modelos") != MODELOS:
        raise JuncaoInvalida("Lista de modelos do manifesto diverge de MODELOS.")

    alvo = carregar_alvo(alvo_path)
    inner_rows, outer_rows = carregar_predicoes_agregadas(entrada_dir)
    if verificar_hashes_predicoes:
        verificar_hashes_recomputados(inner_rows, outer_rows, proveniencia["hashes_saida"])

    dentro_de_c = {id_sha: r for id_sha, r in alvo.items() if r["historico_no_espaco_de_classes"]}

    outer_ids = {linha[1] for linha in outer_rows}
    if outer_ids != set(dentro_de_c):
        faltantes = set(dentro_de_c) - outer_ids
        extras = outer_ids - set(dentro_de_c)
        raise JuncaoInvalida(
            "IDs das previsoes externas divergem do alvo (H dentro de C): "
            f"faltantes={len(faltantes)} extras={len(extras)}"
        )

    registros: dict[str, dict[str, Any]] = {
        id_sha: {
            "id_sha256": id_sha,
            "H": r["categoria_historica"],
            "R": r["referencia_humana"],
            "Y": r["alvo_inadequacao"],
            "grupo_sha256": r["grupo_sha256"],
            "outer_fold": r["outer_fold"],
            "scores_outer": {},
            "top1_outer": {},
        }
        for id_sha, r in dentro_de_c.items()
    }

    for outer_fold, id_sha, grupo_sha, modelo, vetor, top1 in outer_rows:
        reg = registros[id_sha]
        if reg["outer_fold"] != outer_fold:
            raise JuncaoInvalida(
                f"outer_fold divergente para {id_sha}: previsao={outer_fold} alvo={reg['outer_fold']}"
            )
        if reg["grupo_sha256"] != grupo_sha:
            raise JuncaoInvalida(f"grupo_sha256 divergente para {id_sha}")
        reg["scores_outer"][modelo] = np.asarray(vetor, dtype=np.float64)
        reg["top1_outer"][modelo] = top1

    faltando_modelo = sorted(
        id_sha for id_sha, reg in registros.items() if set(reg["scores_outer"]) != set(MODELOS)
    )
    if faltando_modelo:
        raise JuncaoInvalida(
            f"{len(faltando_modelo)} registro(s) sem previsao de todos os 7 modelos: "
            f"{faltando_modelo[:10]}"
        )

    inner_por_fold: dict[int, list[list[Any]]] = defaultdict(list)
    for linha in inner_rows:
        inner_por_fold[linha[0]].append(linha)

    return {
        "classes": classes,
        "registros": registros,
        "inner_rows": inner_rows,
        "inner_por_outer_fold": dict(inner_por_fold),
        "outer_rows": outer_rows,
        "proveniencia": proveniencia,
        "manifesto": manifesto,
    }


# --------------------------------------------------------------------------
# Escores de prioridade (contrato: id; H; R; c_alt; score; fold)
# --------------------------------------------------------------------------

def _melhor_alternativa(vetor: np.ndarray, idx_h: int) -> tuple[int, float]:
    """Indice e valor do maior componente de `vetor` fora da posicao
    `idx_h`. Reaproveitado por s_ls e s_soft: as duas sao
    'max_{c!=H} escore(c) - escore(H)', so muda qual vetor de escore entra."""
    mascara = np.ones(vetor.shape[0], dtype=bool)
    mascara[idx_h] = False
    indices_alt = np.flatnonzero(mascara)
    pos_local = int(np.argmax(vetor[mascara]))
    idx_alt = int(indices_alt[pos_local])
    return idx_alt, float(vetor[idx_alt])


def escore_linear_svc(
    scores_modelo: dict[str, np.ndarray], classes: list[str], H: str
) -> tuple[float, str]:
    """s_ls = max_{c != H} p_ls(c) - p_ls(H). Devolve (s_ls, c_alt)."""
    vetor = scores_modelo["linear_svc"]
    idx_h = classes.index(H)
    idx_alt, p_alt = _melhor_alternativa(vetor, idx_h)
    return p_alt - float(vetor[idx_h]), classes[idx_alt]


def votos_top1(top1_por_modelo: dict[str, str], H: str) -> tuple[int, dict[str, int]]:
    """v_H = numero de modelos cujo top1 e H. Devolve tambem os votos de
    cada categoria alternativa (top1 != H) por modelo."""
    v_h = sum(1 for c in top1_por_modelo.values() if c == H)
    votos_alt: dict[str, int] = defaultdict(int)
    for c in top1_por_modelo.values():
        if c != H:
            votos_alt[c] += 1
    return v_h, dict(votos_alt)


def escolher_c_alt_majoritario(votos_alt: dict[str, int], classes: list[str]) -> str | None:
    """Categoria alternativa mais votada. Empate: menor indice na ordem
    global de classes ja congelada (`classes_ensemble.json`) — nenhuma regra
    nova de desempate. `None` se nenhum modelo votou fora de H (unanimidade
    com o historico)."""
    if not votos_alt:
        return None
    maximo = max(votos_alt.values())
    empatados = [c for c, v in votos_alt.items() if v == maximo]
    return min(empatados, key=classes.index)


def escore_votacao_majoritaria(
    top1_por_modelo: dict[str, str], H: str, classes: list[str]
) -> tuple[float, str | None]:
    """s_maj = (v_alt - v_H) / M. Devolve (s_maj, c_alt)."""
    v_h, votos_alt = votos_top1(top1_por_modelo, H)
    c_alt = escolher_c_alt_majoritario(votos_alt, classes)
    v_alt = votos_alt.get(c_alt, 0) if c_alt is not None else 0
    return (v_alt - v_h) / len(MODELOS), c_alt


def pesos_votacao_suave(
    registros: dict[str, dict[str, Any]], modelos: list[str] = MODELOS
) -> dict[str, float]:
    """Peso de cada modelo = acuracia dele nas previsoes EXTERNAS (outer,
    out-of-fold por construcao da Fase 2B) contra R, normalizada para somar
    1. E a unica medida de 'desempenho dos modelos por fold' disponivel sem
    retreinar nada e sem consultar a planilha viva; nenhum contrato anterior
    do repositorio definia essa regra (Fase 2C e nova) — ver
    docs/FASE2C_ENSEMBLE_CONTRATO.md para a justificativa completa e o
    pedido de confirmacao explicita antes de qualquer resultado definitivo."""
    total = len(registros)
    if total == 0:
        raise Fase2CBloqueado("Nenhum registro para calcular pesos da votacao suave.")
    acertos: dict[str, int] = defaultdict(int)
    for reg in registros.values():
        for modelo in modelos:
            if reg["top1_outer"][modelo] == reg["R"]:
                acertos[modelo] += 1
    desempenho = {m: acertos[m] / total for m in modelos}
    soma = sum(desempenho.values())
    if soma <= 0:
        raise Fase2CBloqueado("Soma de desempenho dos modelos e zero; pesos indefinidos.")
    return {m: desempenho[m] / soma for m in modelos}


def escore_votacao_suave(
    scores_modelo: dict[str, np.ndarray], pesos: dict[str, float], classes: list[str], H: str
) -> tuple[float, str]:
    """S(c) = soma_m w_m * p_m(c). s_soft = max_{c != H} S(c) - S(H)."""
    combinado = np.zeros(len(classes), dtype=np.float64)
    for modelo, peso in pesos.items():
        combinado += peso * scores_modelo[modelo]
    idx_h = classes.index(H)
    idx_alt, s_alt = _melhor_alternativa(combinado, idx_h)
    return s_alt - float(combinado[idx_h]), classes[idx_alt]


# --------------------------------------------------------------------------
# Stacking: meta-modelo sobre as previsoes internas, leakage-free por outer
# fold (reaproveita exatamente o desenho de cross-fitting da Fase 2B: os
# meta-exemplos de treino de um outer fold vem so das previsoes internas
# DAQUELE outer fold, nunca do proprio outer fold como validacao externa).
# --------------------------------------------------------------------------

def montar_features_stacking(
    scores_modelo: dict[str, np.ndarray], classes: list[str], H: str, modelos: list[str] = MODELOS
) -> np.ndarray:
    """Para cada um dos 7 modelos: p_m(H) e max_{c!=H} p_m(c) - p_m(H) (a
    mesma margem de `escore_linear_svc`). 2 features por modelo, 14 no
    total — evita expandir para 7x41 features brutas sem perder o sinal de
    quanto cada modelo discorda de H e com que confianca."""
    idx_h = classes.index(H)
    feats = np.empty(2 * len(modelos), dtype=np.float64)
    for i, modelo in enumerate(modelos):
        vetor = scores_modelo[modelo]
        p_h = float(vetor[idx_h])
        _, p_alt = _melhor_alternativa(vetor, idx_h)
        feats[2 * i] = p_h
        feats[2 * i + 1] = p_alt - p_h
    return feats


def _criar_meta_modelo_padrao() -> Any:
    from sklearn.linear_model import LogisticRegression
    return LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)


def treinar_stacking_por_fold(
    contexto: dict[str, Any], criar_meta_modelo: Callable[[], Any] = _criar_meta_modelo_padrao
) -> dict[int, Any]:
    """Um meta-modelo por outer fold, treinado SOMENTE nas previsoes
    internas (`inner_rows`) daquele outer fold. Nenhum meta-modelo ve, no
    treino, nenhuma previsao originada do proprio outer fold — a mesma
    garantia leakage-free que o cross-fitting da Fase 2B ja construiu."""
    classes = contexto["classes"]
    registros = contexto["registros"]
    modelos_por_fold: dict[int, Any] = {}
    for outer_fold in FOLDS:
        linhas = contexto["inner_por_outer_fold"].get(outer_fold, [])
        por_id: dict[str, dict[str, np.ndarray]] = defaultdict(dict)
        for _of, _if, id_sha, _grupo, modelo, vetor, _top1 in linhas:
            por_id[id_sha][modelo] = np.asarray(vetor, dtype=np.float64)

        X_linhas: list[np.ndarray] = []
        y_valores: list[int] = []
        for id_sha, scores_modelo in por_id.items():
            if set(scores_modelo) != set(MODELOS):
                continue
            reg = registros.get(id_sha)
            if reg is None:
                continue
            X_linhas.append(montar_features_stacking(scores_modelo, classes, reg["H"]))
            y_valores.append(reg["Y"])

        if len(set(y_valores)) < 2:
            raise Fase2CBloqueado(
                f"outer_fold={outer_fold}: meta-treino sem as duas classes de Y "
                "(0 e 1); stacking indefinido nesse fold."
            )
        modelo_meta = criar_meta_modelo()
        modelo_meta.fit(np.vstack(X_linhas), np.asarray(y_valores))
        modelos_por_fold[outer_fold] = modelo_meta
    return modelos_por_fold


def prever_stacking(contexto: dict[str, Any], modelos_por_fold: dict[int, Any]) -> dict[str, float]:
    """q_i = P(Y_i=1) pelo meta-modelo do outer fold ao qual i pertence —
    nunca o meta-modelo treinado com dados do proprio outer fold."""
    classes = contexto["classes"]
    saida: dict[str, float] = {}
    for id_sha, reg in contexto["registros"].items():
        modelo_meta = modelos_por_fold[reg["outer_fold"]]
        x = montar_features_stacking(reg["scores_outer"], classes, reg["H"]).reshape(1, -1)
        idx_classe_1 = list(modelo_meta.classes_).index(1)
        saida[id_sha] = float(modelo_meta.predict_proba(x)[0, idx_classe_1])
    return saida


# --------------------------------------------------------------------------
# Filas de prioridade e curvas de avaliacao
# --------------------------------------------------------------------------

def montar_fila(
    registros: dict[str, dict[str, Any]],
    escores: dict[str, float],
    c_alt_por_id: dict[str, str | None],
) -> list[dict[str, Any]]:
    """Fila ordenada por escore decrescente, com os campos de auditoria do
    contrato: id, H, R, c_alt, score, fold (mais Y, necessario para as
    curvas de avaliacao — nunca usado como feature de nenhum escore)."""
    fila = [
        {
            "id_sha256": id_sha,
            "H": reg["H"],
            "R": reg["R"],
            "c_alt": c_alt_por_id.get(id_sha),
            "score": escores[id_sha],
            "fold": reg["outer_fold"],
            "Y": reg["Y"],
        }
        for id_sha, reg in registros.items()
    ]
    fila.sort(key=lambda linha: (-linha["score"], linha["id_sha256"]))
    return fila


def curva_precisao_recall(fila: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Precisao e recall de Y=1 em cada limiar de corte da fila
    (`sklearn.metrics.precision_recall_curve`, sem reimplementar)."""
    from sklearn.metrics import precision_recall_curve
    y_true = [linha["Y"] for linha in fila]
    scores = [linha["score"] for linha in fila]
    precisao, recall, limiares = precision_recall_curve(y_true, scores)
    pontos = [
        {"limiar": float(t), "precisao": float(p), "recall": float(r)}
        for p, r, t in zip(precisao[:-1], recall[:-1], limiares)
    ]
    pontos.sort(key=lambda p: p["limiar"])
    return pontos


def selecionar_tau(pontos: list[dict[str, Any]], criterio: str = "max_f1") -> dict[str, Any]:
    """Selecao de tau sobre a curva Precision-Recall de Y=1. `criterio` e
    parametrizavel porque a regra de selecao definitiva (F1 maximo, precisao
    minima alvo, recall minimo alvo) ainda nao foi confirmada como contrato
    congelado desta fase — ver docs/FASE2C_ENSEMBLE_CONTRATO.md. 'max_f1' e
    o unico criterio aplicado sem nenhum parametro extra e serve apenas como
    referencia tecnica, nunca como resultado cientifico definitivo."""
    if not pontos:
        raise Fase2CBloqueado("Curva Precision-Recall vazia; tau indefinido.")
    if criterio == "max_f1":
        def _f1(p: dict[str, Any]) -> float:
            soma = p["precisao"] + p["recall"]
            return 0.0 if soma == 0 else 2 * p["precisao"] * p["recall"] / soma
        return max(pontos, key=_f1)
    raise ValueError(f"Criterio de selecao de tau desconhecido: {criterio!r}")


def curva_ganho(fila: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Curva de ganho (gains chart): para cada tamanho de fila K (ordenada
    por escore decrescente), quantas inadequacoes reais (Y=1) foram
    capturadas e com que precisao/recall acumulados."""
    total_y1 = sum(linha["Y"] for linha in fila)
    pontos = []
    capturados = 0
    for k, linha in enumerate(fila, start=1):
        capturados += linha["Y"]
        pontos.append({
            "k": k,
            "capturados": capturados,
            "precisao_acumulada": capturados / k,
            "recall_acumulado": (capturados / total_y1) if total_y1 else 0.0,
        })
    return pontos


# --------------------------------------------------------------------------
# Orquestracao por metodo
# --------------------------------------------------------------------------

def combinar_linear_svc(contexto: dict[str, Any]) -> list[dict[str, Any]]:
    escores: dict[str, float] = {}
    c_alt: dict[str, str | None] = {}
    for id_sha, reg in contexto["registros"].items():
        s, c = escore_linear_svc(reg["scores_outer"], contexto["classes"], reg["H"])
        escores[id_sha], c_alt[id_sha] = s, c
    return montar_fila(contexto["registros"], escores, c_alt)


def combinar_votacao_majoritaria(contexto: dict[str, Any]) -> list[dict[str, Any]]:
    escores: dict[str, float] = {}
    c_alt: dict[str, str | None] = {}
    for id_sha, reg in contexto["registros"].items():
        s, c = escore_votacao_majoritaria(reg["top1_outer"], reg["H"], contexto["classes"])
        escores[id_sha], c_alt[id_sha] = s, c
    return montar_fila(contexto["registros"], escores, c_alt)


def combinar_votacao_suave(
    contexto: dict[str, Any], pesos: dict[str, float] | None = None
) -> tuple[list[dict[str, Any]], dict[str, float]]:
    pesos = pesos if pesos is not None else pesos_votacao_suave(contexto["registros"])
    escores: dict[str, float] = {}
    c_alt: dict[str, str | None] = {}
    for id_sha, reg in contexto["registros"].items():
        s, c = escore_votacao_suave(reg["scores_outer"], pesos, contexto["classes"], reg["H"])
        escores[id_sha], c_alt[id_sha] = s, c
    return montar_fila(contexto["registros"], escores, c_alt), pesos


def combinar_stacking(
    contexto: dict[str, Any],
    criar_meta_modelo: Callable[[], Any] = _criar_meta_modelo_padrao,
    pesos_c_alt: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """c_alt do stacking reaproveita o c_alt da votacao suave: o stacking
    produz somente q_i (um escore de prioridade), nunca uma categoria
    alternativa propria — ver docs/FASE2C_ENSEMBLE_CONTRATO.md."""
    modelos_por_fold = treinar_stacking_por_fold(contexto, criar_meta_modelo)
    escores = prever_stacking(contexto, modelos_por_fold)
    pesos = pesos_c_alt if pesos_c_alt is not None else pesos_votacao_suave(contexto["registros"])
    c_alt: dict[str, str | None] = {}
    for id_sha, reg in contexto["registros"].items():
        _, c = escore_votacao_suave(reg["scores_outer"], pesos, contexto["classes"], reg["H"])
        c_alt[id_sha] = c
    return montar_fila(contexto["registros"], escores, c_alt)


# --------------------------------------------------------------------------
# Persistencia
# --------------------------------------------------------------------------

def gravar_fila(fila: list[dict[str, Any]], caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    payload = [
        {**linha, "score": round(linha["score"], 10)}
        for linha in fila
    ]
    caminho.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--entrada-dir", type=Path, default=ENTRADA_FASE2B_PADRAO)
    p.add_argument("--alvo", type=Path, default=ALVO_PADRAO)
    p.add_argument("--classes", type=Path, default=CLASSES_PATH_PADRAO)
    p.add_argument("--saida-dir", type=Path, default=SAIDA_DIR_PADRAO)
    p.add_argument("--somente-validar-proveniencia", action="store_true",
                   help="roda so a checagem de proveniencia/hashes (barato, zero fits, "
                        "nao combina nem grava nada)")
    p.add_argument("--metodo", choices=["linear_svc", "votacao_majoritaria",
                                        "votacao_suave", "stacking", "todos"],
                   default=None)
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.somente_validar_proveniencia:
        proveniencia = validar_proveniencia(args.entrada_dir)
        inner_rows, outer_rows = carregar_predicoes_agregadas(args.entrada_dir)
        verificar_hashes_recomputados(inner_rows, outer_rows, proveniencia["hashes_saida"])
        print(json.dumps({
            "status": "proveniencia_confirmada",
            "run_id": RUN_ID_EXECUCAO_1,
            "commit_sha": COMMIT_SHA_EXECUCAO_1,
            "hashes_saida": proveniencia["hashes_saida"],
        }, ensure_ascii=False, indent=2))
        return 0

    if args.metodo is None:
        print("Informe --somente-validar-proveniencia ou --metodo.", file=sys.stderr)
        return 2

    contexto = montar_contexto(args.entrada_dir, args.alvo, args.classes)
    metodos = (["linear_svc", "votacao_majoritaria", "votacao_suave", "stacking"]
               if args.metodo == "todos" else [args.metodo])

    resultado_status = {}
    for metodo in metodos:
        if metodo == "linear_svc":
            fila = combinar_linear_svc(contexto)
        elif metodo == "votacao_majoritaria":
            fila = combinar_votacao_majoritaria(contexto)
        elif metodo == "votacao_suave":
            fila, pesos = combinar_votacao_suave(contexto)
            resultado_status["pesos_votacao_suave"] = pesos
        else:
            fila = combinar_stacking(contexto)
        gravar_fila(fila, args.saida_dir / f"fase2c_fila_{metodo}.json")
        resultado_status[metodo] = {"total_fila": len(fila)}

    print(json.dumps(resultado_status, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
