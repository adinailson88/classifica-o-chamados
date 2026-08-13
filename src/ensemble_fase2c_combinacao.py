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

Contrato congelado e aprovado (auditoria independente) para as duas
decisoes que a rodada anterior deixava parametrizaveis:

  - peso da votacao suave: `w_{m,c}^(alpha) = (TP_{m,c} + alpha*pi_c) /
    (N_{m,c} + alpha)`, por MODELO e por CLASSE, estimado exclusivamente a
    partir das previsoes internas (`inner_rows`) do proprio outer fold —
    nunca da dobra externa. `alpha` escolhido em {5, 20, 100} por validacao
    interna (precisao da carga de referencia, depois recall, depois menor
    log-loss multiclasse, persistindo empate o maior alpha) — ver
    `pesos_e_alpha_votacao_suave_por_fold`, `selecionar_alpha_votacao_suave`;
  - capacidade, nao limiar: a comparacao confirmatoria entre metodos usa
    `K_f = |fila natural do LinearSVC na dobra f|` (registros com
    `previsto_linear_svc != H`), a MESMA capacidade para todos os metodos
    naquela dobra — nunca um tau otimizado na avaliacao externa. A curva
    Precision-Recall (`curva_precisao_recall`) e `selecionar_tau` continuam
    disponiveis como saida/utilitario exploratorio, nunca chamados pela
    execucao confirmatoria nem declarando `max_f1` como contrato.

Desempate de `c_alt` na votacao majoritaria: (1) mais votos; (2) maior
media das probabilidades calibradas da categoria entre os sete modelos;
(3) menor indice na ordem canonica das classes. A fila da votacao
majoritaria ordena por `v_alt - v_H` decrescente, depois pela margem de
probabilidade media decrescente, depois por `id_sha256` crescente — nunca a
ordenacao generica de escore+id usada pelos demais metodos.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
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
ALPHAS_PADRAO = (5, 20, 100)  # contrato congelado da votacao suave (secao 4.2)

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


def media_prob_calibrada(
    scores_modelo: dict[str, np.ndarray], classes: list[str], classe: str,
    modelos: list[str] = MODELOS,
) -> float:
    """Media das probabilidades calibradas de `classe` entre os sete
    modelos (segundo criterio de desempate do c_alt majoritario)."""
    idx = classes.index(classe)
    return float(np.mean([scores_modelo[m][idx] for m in modelos]))


def escolher_c_alt_majoritario(
    votos_alt: dict[str, int], classes: list[str], scores_modelo: dict[str, np.ndarray],
) -> str | None:
    """Categoria alternativa. Contrato de desempate, nesta ordem:
    (1) mais votos; (2) maior media das probabilidades calibradas da
    categoria entre os sete modelos; (3) menor indice na ordem canonica das
    classes. `None` se nenhum modelo votou fora de H (unanimidade com o
    historico)."""
    if not votos_alt:
        return None
    maximo = max(votos_alt.values())
    empatados = [c for c, v in votos_alt.items() if v == maximo]
    if len(empatados) == 1:
        return empatados[0]
    medias = {c: media_prob_calibrada(scores_modelo, classes, c) for c in empatados}
    melhor_media = max(medias.values())
    empatados_media = [c for c in empatados if np.isclose(medias[c], melhor_media)]
    if len(empatados_media) == 1:
        return empatados_media[0]
    return min(empatados_media, key=classes.index)


def escore_votacao_majoritaria(
    top1_por_modelo: dict[str, str], scores_modelo: dict[str, np.ndarray],
    H: str, classes: list[str],
) -> tuple[float, str | None, int, int]:
    """s_maj = (v_alt - v_H) / M. Devolve (s_maj, c_alt, v_alt, v_H)."""
    v_h, votos_alt = votos_top1(top1_por_modelo, H)
    c_alt = escolher_c_alt_majoritario(votos_alt, classes, scores_modelo)
    v_alt = votos_alt.get(c_alt, 0) if c_alt is not None else 0
    return (v_alt - v_h) / len(MODELOS), c_alt, v_alt, v_h


def montar_fila_majoritaria(contexto: dict[str, Any]) -> list[dict[str, Any]]:
    """Fila da votacao majoritaria: NUNCA a ordenacao generica escore+id de
    `montar_fila`. Ordena por (1) `v_alt - v_H` decrescente — equivalente a
    `s_maj` decrescente, M e constante —, (2) margem da media de
    probabilidade calibrada (`c_alt` menos `H`) decrescente, (3)
    `id_sha256` crescente."""
    classes = contexto["classes"]
    linhas = []
    for id_sha, reg in contexto["registros"].items():
        s_maj, c_alt, v_alt, v_h = escore_votacao_majoritaria(
            reg["top1_outer"], reg["scores_outer"], reg["H"], classes
        )
        media_h = media_prob_calibrada(reg["scores_outer"], classes, reg["H"])
        media_alt = (
            media_prob_calibrada(reg["scores_outer"], classes, c_alt)
            if c_alt is not None else media_h
        )
        linhas.append({
            "id_sha256": id_sha, "H": reg["H"], "R": reg["R"], "c_alt": c_alt,
            "score": s_maj, "fold": reg["outer_fold"], "Y": reg["Y"],
            "_ordem_votos": v_alt - v_h, "_ordem_prob": media_alt - media_h,
        })
    linhas.sort(key=lambda l: (-l["_ordem_votos"], -l["_ordem_prob"], l["id_sha256"]))
    for linha in linhas:
        del linha["_ordem_votos"]
        del linha["_ordem_prob"]
    return linhas


def _agrupar_inner_por_id(linhas: list[list[Any]]) -> dict[str, dict[str, np.ndarray]]:
    por_id: dict[str, dict[str, np.ndarray]] = defaultdict(dict)
    for _of, _if, id_sha, _grupo, modelo, vetor, _top1 in linhas:
        por_id[id_sha][modelo] = np.asarray(vetor, dtype=np.float64)
    return dict(por_id)


def pesos_votacao_suave_regularizados(
    linhas_inner: list[list[Any]],
    referencia_por_id: dict[str, dict[str, Any]],
    classes: list[str],
    alpha: float,
    modelos: list[str] = MODELOS,
) -> dict[str, np.ndarray]:
    """`w_{m,c}^(alpha) = (TP_{m,c} + alpha*pi_c) / (N_{m,c} + alpha)`.

    `TP_{m,c}`/`N_{m,c}` vem EXCLUSIVAMENTE de `linhas_inner` (previsoes OOF
    internas de um outer fold): `N_{m,c}` conta quantas vezes o modelo `m`
    previu top1=`c` nessas linhas; `TP_{m,c}`, quantas dessas o `R` do
    registro tambem era `c`. `pi_c` e a frequencia de `R=c` entre os IDs
    unicos de `linhas_inner`. Nunca consulta `outer_rows`/dobra externa —
    contrato aprovado, ver docs/FASE2C_ENSEMBLE_CONTRATO.md."""
    n = len(classes)
    idx_de = {c: i for i, c in enumerate(classes)}
    n_pred: dict[str, np.ndarray] = {m: np.zeros(n, dtype=np.float64) for m in modelos}
    tp: dict[str, np.ndarray] = {m: np.zeros(n, dtype=np.float64) for m in modelos}
    r_por_id: dict[str, str] = {}
    for outer_fold, inner_fold, id_sha, grupo, modelo, vetor, top1 in linhas_inner:
        if modelo not in n_pred or top1 not in idx_de:
            continue
        idx_pred = idx_de[top1]
        n_pred[modelo][idx_pred] += 1
        r = referencia_por_id[id_sha]["R"]
        r_por_id[id_sha] = r
        if top1 == r:
            tp[modelo][idx_pred] += 1

    if not r_por_id:
        raise Fase2CBloqueado("Pool interno vazio; pesos da votacao suave indefinidos.")
    contagem_r = Counter(r_por_id.values())
    total_ids = len(r_por_id)
    pi = np.array([contagem_r.get(c, 0) / total_ids for c in classes], dtype=np.float64)

    return {
        modelo: (tp[modelo] + alpha * pi) / (n_pred[modelo] + alpha)
        for modelo in modelos
    }


def escore_combinado_suave(
    scores_modelo: dict[str, np.ndarray], pesos: dict[str, np.ndarray], classes: list[str],
) -> np.ndarray:
    """`S(c|x) = [sum_m w_{m,c} * p_m(c|x)] / [sum_m w_{m,c}]`, normalizado
    em seguida para somar 1 entre as `len(classes)` categorias."""
    n = len(classes)
    numerador = np.zeros(n, dtype=np.float64)
    denominador = np.zeros(n, dtype=np.float64)
    for modelo, w in pesos.items():
        numerador += w * scores_modelo[modelo]
        denominador += w
    combinado = np.divide(
        numerador, denominador, out=np.zeros(n, dtype=np.float64), where=denominador > 0
    )
    soma = combinado.sum()
    if soma <= 0:
        raise Fase2CBloqueado("Escore combinado da votacao suave e zero em todas as classes.")
    return combinado / soma


def escore_votacao_suave(
    scores_modelo: dict[str, np.ndarray], pesos: dict[str, np.ndarray], classes: list[str], H: str
) -> tuple[float, str]:
    """s_soft = max_{c != H} S(c) - S(H), com `S` ja normalizado (soma 1)."""
    combinado = escore_combinado_suave(scores_modelo, pesos, classes)
    idx_h = classes.index(H)
    idx_alt, s_alt = _melhor_alternativa(combinado, idx_h)
    return s_alt - float(combinado[idx_h]), classes[idx_alt]


def _avaliar_alpha_em_validacao(
    linhas_treino: list[list[Any]], linhas_validacao: list[list[Any]],
    referencia_por_id: dict[str, dict[str, Any]], classes: list[str], alpha: float,
) -> tuple[float, float, float]:
    """Precisao/recall da 'carga de referencia' (analogo a fila natural:
    registros cujo top1 do escore combinado diverge de H) e log-loss
    multiclasse, avaliados em `linhas_validacao` com pesos estimados
    SOMENTE em `linhas_treino` — ambos ja restritos ao pool interno de um
    outer fold (nunca a dobra externa)."""
    from sklearn.metrics import log_loss

    pesos = pesos_votacao_suave_regularizados(linhas_treino, referencia_por_id, classes, alpha)
    por_id = _agrupar_inner_por_id(linhas_validacao)

    flags: list[bool] = []
    y_bin: list[int] = []
    y_true_idx: list[int] = []
    y_pred_dist: list[np.ndarray] = []
    for id_sha, scores_modelo in por_id.items():
        if set(scores_modelo) != set(MODELOS):
            continue
        reg = referencia_por_id[id_sha]
        combinado = escore_combinado_suave(scores_modelo, pesos, classes)
        idx_h = classes.index(reg["H"])
        flags.append(int(np.argmax(combinado)) != idx_h)
        y_bin.append(int(reg["Y"]))
        y_true_idx.append(classes.index(reg["R"]))
        y_pred_dist.append(combinado)

    if not flags:
        return 0.0, 0.0, float("inf")
    flags_arr = np.asarray(flags, dtype=bool)
    y_bin_arr = np.asarray(y_bin, dtype=np.int64)
    na_carga = int(flags_arr.sum())
    capturados = int((flags_arr & (y_bin_arr == 1)).sum())
    total_y1 = int((y_bin_arr == 1).sum())
    precisao = capturados / na_carga if na_carga else 0.0
    recall = capturados / total_y1 if total_y1 else 0.0
    logloss = float(
        log_loss(y_true_idx, np.vstack(y_pred_dist), labels=list(range(len(classes))))
    )
    return precisao, recall, logloss


def selecionar_alpha_votacao_suave(
    linhas_inner_do_fold: list[list[Any]],
    referencia_por_id: dict[str, dict[str, Any]],
    classes: list[str],
    alphas: tuple[float, ...] = ALPHAS_PADRAO,
) -> tuple[float, list[dict[str, Any]]]:
    """Selecao de alpha exclusivamente por validacao interna: dentro do pool
    `linhas_inner_do_fold` (ja restrito a um outer fold), cada um dos ate 4
    `inner_fold` vira validacao uma vez, treinando nos demais — nunca a
    dobra externa. Criterio congelado, nesta ordem: maior precisao da carga
    de referencia; depois maior recall; depois menor log-loss multiclasse;
    persistindo empate, maior alpha."""
    inner_folds_presentes = sorted({linha[1] for linha in linhas_inner_do_fold})
    if len(inner_folds_presentes) < 2:
        raise Fase2CBloqueado(
            "Pool interno com menos de 2 rotacoes; validacao interna de alpha indefinida."
        )
    candidatos = []
    for alpha in alphas:
        precisoes, recalls, loglosses = [], [], []
        for fold_validacao in inner_folds_presentes:
            treino = [l for l in linhas_inner_do_fold if l[1] != fold_validacao]
            validacao = [l for l in linhas_inner_do_fold if l[1] == fold_validacao]
            p, r, ll = _avaliar_alpha_em_validacao(treino, validacao, referencia_por_id, classes, alpha)
            precisoes.append(p)
            recalls.append(r)
            loglosses.append(ll)
        candidatos.append({
            "alpha": alpha,
            "precisao": float(np.mean(precisoes)),
            "recall": float(np.mean(recalls)),
            "logloss": float(np.mean(loglosses)),
        })
    melhor = max(candidatos, key=lambda c: (c["precisao"], c["recall"], -c["logloss"], c["alpha"]))
    return melhor["alpha"], candidatos


def pesos_e_alpha_votacao_suave_por_fold(
    contexto: dict[str, Any], alphas: tuple[float, ...] = ALPHAS_PADRAO,
) -> dict[int, dict[str, Any]]:
    """Para cada outer fold: seleciona alpha por validacao interna e estima
    os pesos regularizados finais no pool interno inteiro daquele fold, com
    o alpha escolhido. Nunca usa a dobra externa em nenhuma das duas
    etapas."""
    classes = contexto["classes"]
    registros = contexto["registros"]
    resultado: dict[int, dict[str, Any]] = {}
    for outer_fold in FOLDS:
        linhas = contexto["inner_por_outer_fold"].get(outer_fold, [])
        alpha, candidatos = selecionar_alpha_votacao_suave(linhas, registros, classes, alphas)
        pesos = pesos_votacao_suave_regularizados(linhas, registros, classes, alpha)
        resultado[outer_fold] = {"alpha": alpha, "pesos": pesos, "candidatos_alpha": candidatos}
    return resultado


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


def selecionar_tau(pontos: list[dict[str, Any]], criterio: str) -> dict[str, Any]:
    """UTILITARIO EXPLORATORIO — nunca chamado pela execucao confirmatoria
    da Fase 2C e nunca usado para publicar resultado cientifico. `max_f1`
    NAO foi aprovado como regra vinculante de selecao de limiar (a regra
    aprovada e capacidade `K_f` por dobra — ver `capacidade_linear_svc_por_fold`/
    `aplicar_capacidade_por_fold`). Otimizar `tau` sobre a mesma curva
    Precision-Recall usada como avaliacao (dobra externa) e vazamento de
    selecao — por isso `criterio` nao tem valor padrao: cada chamada precisa
    ser deliberada, nunca implicita."""
    if not pontos:
        raise Fase2CBloqueado("Curva Precision-Recall vazia; tau indefinido.")
    if criterio == "max_f1":
        def _f1(p: dict[str, Any]) -> float:
            soma = p["precisao"] + p["recall"]
            return 0.0 if soma == 0 else 2 * p["precisao"] * p["recall"] / soma
        return max(pontos, key=_f1)
    raise ValueError(f"Criterio de selecao de tau desconhecido: {criterio!r}")


# --------------------------------------------------------------------------
# Capacidade K_f (comparacao confirmatoria, nunca limiar otimizado na
# avaliacao externa)
# --------------------------------------------------------------------------

def capacidade_linear_svc_por_fold(contexto: dict[str, Any]) -> dict[int, int]:
    """`K_f = |B_f^{LSVC}|`: tamanho da fila natural do LinearSVC (registros
    com `previsto != H`) em cada outer fold — mesmo conceito ja congelado em
    `congelar_alvo_ensemble.reproduzir_baseline`, aqui so contado por
    dobra."""
    contagem: dict[int, int] = defaultdict(int)
    for reg in contexto["registros"].values():
        if reg["top1_outer"]["linear_svc"] != reg["H"]:
            contagem[reg["outer_fold"]] += 1
    return dict(contagem)


def aplicar_capacidade_por_fold(
    fila: list[dict[str, Any]], capacidade_por_fold: dict[int, int]
) -> list[dict[str, Any]]:
    """Mantem, em cada outer fold `f`, somente os `K_f` primeiros registros
    da fila (ja ordenada pelo escore do proprio metodo) — nunca um limiar
    unico escolhido pela avaliacao externa."""
    por_fold: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for linha in fila:
        por_fold[linha["fold"]].append(linha)
    selecionados: list[dict[str, Any]] = []
    for fold, linhas in por_fold.items():
        k = capacidade_por_fold.get(fold, 0)
        selecionados.extend(linhas[:k])
    return selecionados


def resumo_capacidade(fila_capacidade: list[dict[str, Any]]) -> dict[str, Any]:
    """Contagem de `Y=1` capturados e precisao dentro da fila truncada em
    `K_f` — comparacao confirmatoria entre metodos, sem escolha de limiar."""
    total = len(fila_capacidade)
    capturados = sum(linha["Y"] for linha in fila_capacidade)
    return {
        "total_na_fila": total,
        "capturados_y1": capturados,
        "precisao": capturados / total if total else 0.0,
    }


def comparar_metodos_por_capacidade(
    contexto: dict[str, Any], filas_por_metodo: dict[str, list[dict[str, Any]]]
) -> tuple[dict[str, dict[str, Any]], dict[int, int]]:
    """Comparacao confirmatoria: cada metodo truncado na MESMA capacidade
    `K_f` (fila natural do LinearSVC) por dobra — nunca um `tau` otimizado
    na dobra externa."""
    capacidade = capacidade_linear_svc_por_fold(contexto)
    resultado = {
        metodo: resumo_capacidade(aplicar_capacidade_por_fold(fila, capacidade))
        for metodo, fila in filas_por_metodo.items()
    }
    return resultado, capacidade


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
    """Usa `montar_fila_majoritaria`: NUNCA a ordenacao generica escore+id."""
    return montar_fila_majoritaria(contexto)


def combinar_votacao_suave(
    contexto: dict[str, Any],
    info_por_fold: dict[int, dict[str, Any]] | None = None,
    alphas: tuple[float, ...] = ALPHAS_PADRAO,
) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    """Pesos e alpha estimados POR OUTER FOLD (contrato aprovado); cada
    registro usa exclusivamente os pesos do proprio outer fold."""
    info_por_fold = (
        info_por_fold if info_por_fold is not None
        else pesos_e_alpha_votacao_suave_por_fold(contexto, alphas)
    )
    escores: dict[str, float] = {}
    c_alt: dict[str, str | None] = {}
    for id_sha, reg in contexto["registros"].items():
        pesos = info_por_fold[reg["outer_fold"]]["pesos"]
        s, c = escore_votacao_suave(reg["scores_outer"], pesos, contexto["classes"], reg["H"])
        escores[id_sha], c_alt[id_sha] = s, c
    return montar_fila(contexto["registros"], escores, c_alt), info_por_fold


def combinar_stacking(
    contexto: dict[str, Any],
    criar_meta_modelo: Callable[[], Any] = _criar_meta_modelo_padrao,
    info_por_fold: dict[int, dict[str, Any]] | None = None,
    alphas: tuple[float, ...] = ALPHAS_PADRAO,
) -> list[dict[str, Any]]:
    """c_alt do stacking reaproveita o c_alt da votacao suave (pesos por
    outer fold do contrato aprovado): o stacking produz somente q_i (um
    escore de prioridade), nunca uma categoria alternativa propria — ver
    docs/FASE2C_ENSEMBLE_CONTRATO.md."""
    modelos_por_fold = treinar_stacking_por_fold(contexto, criar_meta_modelo)
    escores = prever_stacking(contexto, modelos_por_fold)
    info_por_fold = (
        info_por_fold if info_por_fold is not None
        else pesos_e_alpha_votacao_suave_por_fold(contexto, alphas)
    )
    c_alt: dict[str, str | None] = {}
    for id_sha, reg in contexto["registros"].items():
        pesos = info_por_fold[reg["outer_fold"]]["pesos"]
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

    # Pesos/alpha da votacao suave (contrato aprovado, so pool interno)
    # calculados uma vez e reaproveitados por votacao_suave e stacking (c_alt).
    info_por_fold = None
    if {"votacao_suave", "stacking"} & set(metodos):
        info_por_fold = pesos_e_alpha_votacao_suave_por_fold(contexto)

    filas_por_metodo: dict[str, list[dict[str, Any]]] = {}
    resultado_status: dict[str, Any] = {}
    for metodo in metodos:
        if metodo == "linear_svc":
            fila = combinar_linear_svc(contexto)
        elif metodo == "votacao_majoritaria":
            fila = combinar_votacao_majoritaria(contexto)
        elif metodo == "votacao_suave":
            fila, info_por_fold = combinar_votacao_suave(contexto, info_por_fold)
            resultado_status["alpha_por_fold"] = {
                f: info["alpha"] for f, info in info_por_fold.items()
            }
        else:
            fila = combinar_stacking(contexto, info_por_fold=info_por_fold)
        filas_por_metodo[metodo] = fila
        gravar_fila(fila, args.saida_dir / f"fase2c_fila_{metodo}.json")
        resultado_status[metodo] = {"total_fila": len(fila)}

    # Comparacao confirmatoria: MESMA capacidade K_f (fila natural do
    # LinearSVC por dobra) para todos os metodos rodados nesta chamada —
    # nunca um tau otimizado na avaliacao externa.
    if len(filas_por_metodo) > 1:
        comparacao, capacidade = comparar_metodos_por_capacidade(contexto, filas_por_metodo)
        resultado_status["comparacao_por_capacidade"] = comparacao
        resultado_status["capacidade_k_f"] = capacidade

    print(json.dumps(resultado_status, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
