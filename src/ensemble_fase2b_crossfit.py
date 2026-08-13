#!/usr/bin/env python3
"""Fase 2B: cross-fitting aninhado dos sete modelos-base do ensemble.

Ferramenta estritamente READ-ONLY sobre a planilha. Constroi, sobre o
recongelamento online ja aprovado (`src/recongelar_ensemble_online.py`,
`docs/RECONGELAMENTO_ONLINE_ENSEMBLE.md`), a camada de cross-fitting interno
dos sete modelos-base (naive_bayes, regressao_logistica, linear_svc, sgd,
extra_trees, random_forest, lstm): para cada um dos 5 outer folds canonicos,
quatro rotacoes internas produzem previsoes leakage-free sobre os folds de
treino, e um treino externo produz previsoes sobre o outer fold isolado.

NAO recalcula particoes, grupos ou o alvo Y=1(H!=R); apenas reusa o que ja
esta congelado. NAO executa votacao, stacking, calibracao nem qualquer
selecao adaptativa — essa fase produz apenas as distribuicoes de escore
(41 classes) que fases futuras vao consumir.

Os sete modelos aprendem R (referencia humana), nunca Y (alvo de
inadequacao) e nunca a categoria historica H diretamente.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

import congelar_alvo_ensemble as cae  # noqa: E402
import modelos_zoo as zoo  # noqa: E402
import recongelar_ensemble_online as rero  # noqa: E402
import replay_bundle as rb  # noqa: E402
import retreinar_modelos_canonicos as rmc  # noqa: E402
from modelo_lstm import fixar_determinismo_lstm as _fixar_determinismo_lstm_real  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DADOS_ENSEMBLE = RAIZ / "docs" / "dados" / "ensemble"
CLASSES_PATH_PADRAO = DADOS_ENSEMBLE / "classes_ensemble.json"
SAIDA_DIR_PADRAO = DADOS_ENSEMBLE / "fase2b"

FOLDS = (1, 2, 3, 4, 5)
MODELOS = list(rmc.MODELOS_PADRAO)  # ordem fixa: 7 modelos-base
SEMENTE_PADRAO = 42

TOTAL_ESPERADO = 13972
GRUPOS_ESPERADOS = 9735
H_DENTRO_DE_C_ESPERADO = 13970
H_FORA_DE_C_ESPERADO = 2
CLASSES_ESPERADAS = 41
FITS_ESPERADOS_TOTAL = 175
FITS_ESPERADOS_LSTM = 25

# Hashes aprovados no recongelamento online (docs/RECONGELAMENTO_ONLINE_ENSEMBLE.md).
# A Fase 2B nao treina nada se a planilha online divergir de qualquer um destes.
HASHES_ESPERADOS = {
    "hash_corpus": "fe9bfa4a6c521c0c73b234500e1c9d14bdeb6769470269daa38e588a7a877891",
    "hash_alvo_ensemble": "8884d6098325734a0315e8976ffa1b8bd7da15cede3a6a959904a098fbe7d57c",
    "classes_sha256": "9e6c742bd7f6410de10f857d4103a959316f588ae4f19afdb06d84a3dcea947a",
    "partition_manifest_online_sha256": "d38c041695259e9204a7450955bed209191c829e0f99b269a28cfbf4bc53b404",
    "fold_assignment_sha256": "dc17cfb2806d1c20b141c1e394b684f7c3e087a1ba922e4920497d96bcd64b7d",
}

# Sexto fingerprint, exclusivamente operacional/de reprodutibilidade (modo
# REPLAY). NAO substitui, altera ou entra no calculo de nenhum dos 5 hashes
# metodologicos acima: cobre o texto BRUTO (nao normalizado) dos 4 campos
# textuais, que os 5 hashes metodologicos nao cobrem (eles so enxergam
# grupo_sha256, ja normalizado). Fica None ate o bundle privado do REPLAY
# CONGELADO ser criado e seu conteudo auditado/aprovado — com o valor em
# None, `gate_zero_replay` bloqueia sempre, por construcao (nenhuma rodada de
# replay roda sem um valor pinado e aprovado). Ver
# docs/REPLAY_CONGELADO_FASE2B.md para o schema do bundle e o nivel de
# evidencia da reconstrucao da Execucao Cientifica 1.
REPLAY_INPUT_SHA256_ESPERADO: str | None = None


class Fase2BBloqueado(RuntimeError):
    """Erro base: qualquer subclasse interrompe a rodada sem publicar nada."""


class GateZeroBloqueado(Fase2BBloqueado):
    pass


class VazamentoDetectado(Fase2BBloqueado):
    pass


class BloqueadoLstmFallback(Fase2BBloqueado):
    pass


class ContagemEstruturalDivergente(Fase2BBloqueado):
    pass


class NaoDeterminismoDetectado(Fase2BBloqueado):
    pass


class ReplayBloqueado(Fase2BBloqueado):
    """Bloqueio exclusivo do modo REPLAY: bundle privado ausente/inconsistente,
    replay_input_sha256 nao pinado ou divergente, ou grupo_sha256 recomputado
    de algum registro do bundle nao batendo com o armazenado."""


# --------------------------------------------------------------------------
# Gate Zero: releitura online + reconstrucao do corpus, sem treinar nada
# --------------------------------------------------------------------------

def _hashes_divergentes(observados: dict[str, str]) -> dict[str, dict[str, str]]:
    """Compara hashes observados contra HASHES_ESPERADOS. Funcao pura, separada
    de `gate_zero` para ser testavel sem precisar reconstruir o corpus real de
    13.972 registros."""
    return {
        chave: {"observado": valor, "esperado": HASHES_ESPERADOS[chave]}
        for chave, valor in observados.items()
        if valor != HASHES_ESPERADOS[chave]
    }


def calcular_replay_input_sha256(registros_bundle: list[dict[str, Any]]) -> str:
    """Sexto fingerprint, exclusivo do modo REPLAY: cobre o texto BRUTO (nao
    normalizado) dos 4 campos textuais + os demais campos efetivamente
    consumidos pelo treino/particionamento, ordenado por id_sha256, em
    serializacao canonica (`cae.canonical_bytes`: ensure_ascii=False,
    sort_keys=True, separators sem espaco — mesmo estilo de
    `congelar_alvo_ensemble.hash_historico`). NAO entra no calculo de nenhum
    dos 5 hashes metodologicos (`HASHES_ESPERADOS`); e uma checagem
    inteiramente separada, somada a eles, nunca substituindo-os."""
    payload = [
        {
            "id_sha256": r["id_sha256"],
            "titulo": r["titulo"],
            "descricao_glpi": r["descricao_glpi"],
            "titulo_osm": r["titulo_osm"],
            "descricao_osm": r["descricao_osm"],
            "categoria_historica": r["categoria_historica"],
            "referencia_humana": r["referencia_humana"],
            "grupo_sha256": r["grupo_sha256"],
            "outer_fold": r["outer_fold"],
        }
        for r in sorted(registros_bundle, key=lambda x: x["id_sha256"])
    ]
    return cae.sha256_json(payload)


def gate_zero(
    config_path: Path = rero.CONFIG_PADRAO,
    credenciais: str | None = None,
    particoes_path: Path = rero.PARTICOES_PADRAO,
    alvo_congelado_path: Path = rero.ALVO_CONGELADO_PADRAO,
    classes_path: Path = CLASSES_PATH_PADRAO,
    registros_online: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Reconstroi o corpus online e valida contra os hashes ja aprovados.

    Reusa, sem duplicar, `recongelar_ensemble_online`: as mesmas particoes
    preservadas, o mesmo alvo congelado anterior e a mesma logica de
    normalizacao/hash de `construir_grupos_textuais`. Nao treina nenhum
    modelo; so bloqueia (`GateZeroBloqueado`) se qualquer hash ou contagem
    estrutural divergir do estado aprovado no recongelamento online.
    """
    particoes = rero.carregar_particoes_preservadas(particoes_path)
    alvo_congelado = rero.carregar_alvo_congelado(alvo_congelado_path)
    if registros_online is None:
        registros_online = rero.ler_registros_online(config_path, credenciais)

    base_info = rero.montar_base_atual(registros_online, particoes)
    diagnostico = rero.montar_diagnostico(
        base_info, alvo_congelado, particoes,
        total_esperado=rero.TOTAL_ESPERADO,
        folds_esperados=rero.FOLDS_ESPERADOS_PADRAO,
    )
    if diagnostico["status"] != "apto_para_baseline":
        raise GateZeroBloqueado(
            f"Recongelamento online bloqueado: {diagnostico['bloqueios']}"
        )

    registros = rero.montar_registros_recongelados(base_info["base"], particoes)
    hash_corpus = rero.calcular_hash_corpus(registros)
    classes_payload, classes_sha = cae.montar_classes(
        registros, esperado=len({r["referencia_humana"] for r in registros})
    )
    particoes_online_bytes = rero.montar_particoes_online_csv_bytes(registros)
    partition_manifest_online_sha256 = cae.sha256_bytes(particoes_online_bytes)
    fold_assignment_sha256 = rero.calcular_fold_assignment_sha256(
        [(r["id_sha256"], r["outer_fold"]) for r in registros]
    )
    alvo_obj = {
        "metadata": {
            "schema_version": 1,
            "hash_corpus": hash_corpus,
            "hash_historico_ensemble": cae.hash_historico(registros),
            "partition_manifest_sha256": partition_manifest_online_sha256,
            "partition_manifest_origem_sha256": cae.sha256_bytes(particoes_path.read_bytes()),
            "fold_assignment_sha256": fold_assignment_sha256,
            "classes_sha256": classes_sha,
            "total_records": len(registros),
        },
        "records": registros,
    }
    hash_alvo = cae.sha256_bytes(cae.canonical_bytes(alvo_obj))

    observados = {
        "hash_corpus": hash_corpus,
        "hash_alvo_ensemble": hash_alvo,
        "classes_sha256": classes_sha,
        "partition_manifest_online_sha256": partition_manifest_online_sha256,
        "fold_assignment_sha256": fold_assignment_sha256,
    }
    divergentes = _hashes_divergentes(observados)
    if divergentes:
        raise GateZeroBloqueado(
            "Hashes divergentes do congelamento online ja aprovado: "
            + json.dumps(divergentes, ensure_ascii=False, sort_keys=True)
        )

    total = len(registros)
    grupos = len({r["grupo_sha256"] for r in registros})
    folds_vistos = sorted({r["outer_fold"] for r in registros})
    h_dentro = sum(1 for r in registros if r["historico_no_espaco_de_classes"])
    h_fora = total - h_dentro
    classes = [c["label"] for c in classes_payload["classes"]]
    if (total, grupos, folds_vistos, h_dentro, h_fora, len(classes)) != (
        TOTAL_ESPERADO, GRUPOS_ESPERADOS, list(FOLDS),
        H_DENTRO_DE_C_ESPERADO, H_FORA_DE_C_ESPERADO, CLASSES_ESPERADAS,
    ):
        raise ContagemEstruturalDivergente(
            f"Contagens estruturais divergentes: total={total}, grupos={grupos}, "
            f"folds={folds_vistos}, H_dentro_de_C={h_dentro}, H_fora_de_C={h_fora}, "
            f"classes={len(classes)}"
        )

    textos_por_id = {
        id_sha: item["texto_atual"] for id_sha, item in base_info["base"].items()
    }
    return {
        "registros": registros,
        "textos_por_id": textos_por_id,
        "classes": classes,
        "hashes": observados,
        "total_registros": total,
        "total_grupos": grupos,
        "h_dentro_de_c": h_dentro,
        "h_fora_de_c": h_fora,
    }


# --------------------------------------------------------------------------
# Gate Zero REPLAY: input CONGELADO (bundle privado), nunca a planilha viva
# --------------------------------------------------------------------------
#
# Separacao deliberada de `gate_zero()` acima, que permanece INALTERADA e e
# a unica usada por [FASE2B-RUN]: aquela e o Gate de proveniencia da fonte
# online viva (protege qualquer NOVO recongelamento/baseline). Esta e o
# replay cientifico sobre um input ja congelado — nunca produz uma nova
# baseline, so reproduz uma execucao ja aprovada. As duas nunca sao chamadas
# na mesma rodada (marcadores [FASE2B-RUN] e [FASE2B-REPLAY] sao mutuamente
# exclusivos no workflow).
#
# Reusa, sem reimplementar, as MESMAS funcoes de calculo cientifico de
# `recongelar_ensemble_online`/`congelar_alvo_ensemble` que `gate_zero()` usa:
# `montar_registros_recongelados`, `calcular_hash_corpus`, `cae.montar_classes`,
# `montar_particoes_online_csv_bytes`, `calcular_fold_assignment_sha256`,
# `cae.canonical_bytes`/`sha256_bytes`, `_hashes_divergentes`. A unica coisa
# nova e de onde vem `registros_bundle` (bundle privado estatico, nunca a
# planilha operacional) e as duas checagens que so fazem sentido no modo
# replay: `replay_input_sha256` e a consistencia grupo_sha256 por registro.

def validar_bundle_replay(
    registros_bundle: list[dict[str, Any]],
    replay_input_sha256_esperado: str | None,
    particoes_path: Path = rero.PARTICOES_PADRAO,
) -> dict[str, Any]:
    """Logica cientifica do modo REPLAY, compartilhada por `gate_zero_replay()`
    (producao, hash PINADO em `REPLAY_INPUT_SHA256_ESPERADO`) e pelo
    mecanismo de recuperacao/verificacao do bundle candidato em
    `src/recuperar_bundle_replay.py` (hash CANDIDATO, nunca pinado aqui).
    `registros_bundle` ja e o input CONGELADO (H/R/grupo/fold vindos do
    proprio bundle, nunca recalculados de fonte viva) — esta funcao so
    valida, nesta ordem, ANTES de liberar qualquer fit:

      1. replay_input_sha256 recomputado == replay_input_sha256_esperado;
      2. grupo_sha256 recomputado == grupo_sha256 armazenado, por registro;
      3. os 5 hashes metodologicos recomputados == HASHES_ESPERADOS.

    Qualquer divergencia em qualquer uma das tres levanta `ReplayBloqueado`
    (ou `GateZeroBloqueado`/`ContagemEstruturalDivergente`, reaproveitando as
    mesmas excecoes de `gate_zero()` onde a checagem e literalmente a mesma),
    sem treinar nada."""
    if replay_input_sha256_esperado is None:
        raise ReplayBloqueado(
            "replay_input_sha256_esperado nao foi informado: nenhum fit sera "
            "executado."
        )

    replay_input_sha256 = calcular_replay_input_sha256(registros_bundle)
    if replay_input_sha256 != replay_input_sha256_esperado:
        raise ReplayBloqueado(
            "replay_input_sha256 divergente do esperado: "
            f"esperado={replay_input_sha256_esperado!r} "
            f"observado={replay_input_sha256!r}"
        )

    grupos_divergentes = rb.validar_grupos_por_registro(registros_bundle)
    if grupos_divergentes:
        raise ReplayBloqueado(
            f"grupo_sha256 recomputado diverge do armazenado em "
            f"{len(grupos_divergentes)} registro(s) do bundle: "
            f"{sorted(grupos_divergentes)[:20]}"
        )

    particoes = rero.carregar_particoes_preservadas(particoes_path)
    base = {
        r["id_sha256"]: {
            "grupo_atual": r["grupo_sha256"],
            "categoria_historica_atual": r["categoria_historica"],
            "referencia_humana_atual": r["referencia_humana"],
            "texto_atual": rmc.montar_texto(r),
            "outer_fold": particoes[r["id_sha256"]]["outer_fold"],
        }
        for r in registros_bundle
    }
    registros = rero.montar_registros_recongelados(base, particoes)

    hash_corpus = rero.calcular_hash_corpus(registros)
    classes_payload, classes_sha = cae.montar_classes(
        registros, esperado=len({r["referencia_humana"] for r in registros})
    )
    particoes_online_bytes = rero.montar_particoes_online_csv_bytes(registros)
    partition_manifest_online_sha256 = cae.sha256_bytes(particoes_online_bytes)
    fold_assignment_sha256 = rero.calcular_fold_assignment_sha256(
        [(r["id_sha256"], r["outer_fold"]) for r in registros]
    )
    alvo_obj = {
        "metadata": {
            "schema_version": 1,
            "hash_corpus": hash_corpus,
            "hash_historico_ensemble": cae.hash_historico(registros),
            "partition_manifest_sha256": partition_manifest_online_sha256,
            "partition_manifest_origem_sha256": cae.sha256_bytes(
                particoes_path.read_bytes()
            ),
            "fold_assignment_sha256": fold_assignment_sha256,
            "classes_sha256": classes_sha,
            "total_records": len(registros),
        },
        "records": registros,
    }
    hash_alvo = cae.sha256_bytes(cae.canonical_bytes(alvo_obj))

    observados = {
        "hash_corpus": hash_corpus,
        "hash_alvo_ensemble": hash_alvo,
        "classes_sha256": classes_sha,
        "partition_manifest_online_sha256": partition_manifest_online_sha256,
        "fold_assignment_sha256": fold_assignment_sha256,
    }
    divergentes = _hashes_divergentes(observados)
    if divergentes:
        raise GateZeroBloqueado(
            "Hashes metodologicos divergentes do congelamento aprovado (modo "
            "replay): " + json.dumps(divergentes, ensure_ascii=False, sort_keys=True)
        )

    total = len(registros)
    grupos = len({r["grupo_sha256"] for r in registros})
    folds_vistos = sorted({r["outer_fold"] for r in registros})
    h_dentro = sum(1 for r in registros if r["historico_no_espaco_de_classes"])
    h_fora = total - h_dentro
    classes = [c["label"] for c in classes_payload["classes"]]
    if (total, grupos, folds_vistos, h_dentro, h_fora, len(classes)) != (
        TOTAL_ESPERADO, GRUPOS_ESPERADOS, list(FOLDS),
        H_DENTRO_DE_C_ESPERADO, H_FORA_DE_C_ESPERADO, CLASSES_ESPERADAS,
    ):
        raise ContagemEstruturalDivergente(
            f"Contagens estruturais divergentes (replay): total={total}, "
            f"grupos={grupos}, folds={folds_vistos}, H_dentro_de_C={h_dentro}, "
            f"H_fora_de_C={h_fora}, classes={len(classes)}"
        )

    textos_por_id = {id_sha: item["texto_atual"] for id_sha, item in base.items()}
    return {
        "registros": registros,
        "textos_por_id": textos_por_id,
        "classes": classes,
        "hashes": observados,
        "replay_input_sha256": replay_input_sha256,
        "total_registros": total,
        "total_grupos": grupos,
        "h_dentro_de_c": h_dentro,
        "h_fora_de_c": h_fora,
    }


def gate_zero_replay(
    spreadsheet_id: str | None = None,
    credenciais: str | None = None,
    particoes_path: Path = rero.PARTICOES_PADRAO,
    registros_bundle: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Equivalente de `gate_zero()` para o modo REPLAY de PRODUCAO: le o
    bundle PRIVADO e estatico (nunca a planilha operacional viva) e delega
    toda a validacao cientifica a `validar_bundle_replay()`, usando o hash
    PINADO `REPLAY_INPUT_SHA256_ESPERADO` — nunca um hash candidato. Cada
    job do workflow chama esta funcao de forma independente — se o bundle
    privado mudar entre dois jobs de uma mesma rodada, o job seguinte
    bloqueia em vez de treinar sobre um input diferente dos irmaos."""
    if registros_bundle is None:
        registros_bundle = rb.ler_bundle_congelado(spreadsheet_id, credenciais)
    return validar_bundle_replay(
        registros_bundle, REPLAY_INPUT_SHA256_ESPERADO, particoes_path
    )


# --------------------------------------------------------------------------
# Rotacoes internas e filtragem do dominio aprendido
# --------------------------------------------------------------------------

def montar_rotacoes_internas(outer_fold: int, folds=FOLDS) -> list[dict[str, Any]]:
    """4 rotacoes por outer fold: cada uma valida em 1 fold interno e treina
    nos 3 restantes (excluido sempre o outer fold, nunca visto aqui)."""
    if outer_fold not in folds:
        raise ValueError(f"outer_fold invalido: {outer_fold!r}")
    internos = [g for g in folds if g != outer_fold]
    rotacoes = []
    for g in internos:
        treino = tuple(sorted(f for f in internos if f != g))
        rotacoes.append({"outer_fold": outer_fold, "validacao": g, "treino": treino})
    return rotacoes


def montar_registros_modelaveis(
    registros: list[dict[str, Any]], classes: list[str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Filtra H in C (dominio aprendido). Valida R in C para todo modelavel."""
    classes_set = set(classes)
    modelaveis = [r for r in registros if r["historico_no_espaco_de_classes"]]
    excluidos = [r for r in registros if not r["historico_no_espaco_de_classes"]]
    fora_de_c = [r["id_sha256"] for r in modelaveis if r["referencia_humana"] not in classes_set]
    if fora_de_c:
        raise ContagemEstruturalDivergente(
            f"R fora de C no dominio aprendido: {sorted(fora_de_c)[:20]}"
        )
    return modelaveis, excluidos


# --------------------------------------------------------------------------
# Alinhamento das 41 classes
# --------------------------------------------------------------------------

def alinhar_scores(
    classes_modelo, matriz: np.ndarray, ordem_global: list[str]
) -> tuple[np.ndarray, list[str]]:
    """Realinha a matriz n x k_modelo do modelo para n x 41, na ordem global.

    Classes que o treino nao viu ficam com 0 nas colunas correspondentes e
    sao reportadas em `classes_ausentes`. Uma classe prevista pelo modelo
    fora do espaco global de 41 e um erro de integridade dos dados, nao uma
    situacao esperada de "classe rara" — a rodada bloqueia.
    """
    indice_global = {c: i for i, c in enumerate(ordem_global)}
    n = matriz.shape[0]
    k = len(ordem_global)
    saida = np.zeros((n, k), dtype=np.float64)
    vistas = set()
    for j, classe in enumerate(classes_modelo):
        pos = indice_global.get(classe)
        if pos is None:
            raise ContagemEstruturalDivergente(
                f"Modelo previu classe fora do espaco global de 41: {classe!r}"
            )
        saida[:, pos] = matriz[:, j]
        vistas.add(classe)
    classes_ausentes = [c for c in ordem_global if c not in vistas]
    return saida, classes_ausentes


# --------------------------------------------------------------------------
# Cross-fitting por outer fold
# --------------------------------------------------------------------------

# Modelos cujo n_jobs e puramente computacional (nao afeta random_state,
# n_estimators, criterio de split ou qualquer outro hiperparametro cientifico)
# e por isso e fixado em 1 so dentro da Fase 2B, para eliminar uma fonte de
# nao-determinismo entre runners com contagem de CPU diferente. n_estimators,
# random_state, class_weight etc. continuam exatamente os de modelos_zoo.py.
MODELOS_COM_NJOBS_FIXADO_NA_FASE2B = ("extra_trees", "random_forest")


def criar_modelo_fase2b(nome: str, criar_modelo_base: Callable = zoo.criar_modelo):
    """Mesma fabrica de `modelos_zoo.criar_modelo`, sem duplicar nenhum
    hiperparametro: constroi o modelo real e so sobrescreve `n_jobs=1` nos
    dois modelos de arvore, via `set_params` no estimador ja instanciado.
    Isso evita reconstruir o pipeline (zero risco de o TF-IDF ou os
    hiperparametros de arvore divergirem de `modelos_zoo.py`) e nao altera
    `n_jobs` de nenhuma outra rotina do repositorio que chame
    `modelos_zoo.criar_modelo` diretamente."""
    modelo = criar_modelo_base(nome)
    if nome in MODELOS_COM_NJOBS_FIXADO_NA_FASE2B:
        modelo.pipe.named_steps["clf"].set_params(n_jobs=1)
    return modelo


def _assert_sem_vazamento(grupos_treino: set[str], grupos_validacao: set[str],
                          grupos_externo: set[str], ids_treino: set[str],
                          ids_validacao: set[str], contexto: str) -> None:
    if grupos_treino & grupos_validacao:
        raise VazamentoDetectado(f"{contexto}: grupos_treino ∩ grupos_validacao != ∅")
    if grupos_treino & grupos_externo:
        raise VazamentoDetectado(f"{contexto}: grupos_treino ∩ grupos_externo != ∅")
    if ids_treino & ids_validacao:
        raise VazamentoDetectado(f"{contexto}: IDs_treino ∩ IDs_validacao != ∅")


def _fit_e_prever(nome_modelo: str, textos_treino, rotulos_treino, textos_alvo,
                   ordem_classes: list[str], criar_modelo: Callable, seed: int,
                   contexto: str, fixar_determinismo_lstm: Callable
                   ) -> tuple[np.ndarray, list[str], bool | None]:
    if nome_modelo == "lstm":
        fixar_determinismo_lstm(seed)
    modelo = criar_modelo(nome_modelo)
    modelo.fit(textos_treino, rotulos_treino)
    eh_lstm = None
    if nome_modelo == "lstm":
        eh_lstm = getattr(modelo, "eh_lstm", None)
        if eh_lstm is not True:
            raise BloqueadoLstmFallback(
                f"{contexto}: eh_lstm={eh_lstm!r} (fallback proibido na Fase 2B)"
            )
    classes_modelo, matriz = modelo.predict_dist(textos_alvo)
    alinhado, ausentes = alinhar_scores(classes_modelo, np.asarray(matriz), ordem_classes)
    return alinhado, ausentes, eh_lstm


def executar_outer_fold(
    outer_fold: int,
    gate: dict[str, Any],
    criar_modelo: Callable = criar_modelo_fase2b,
    seed: int = SEMENTE_PADRAO,
    fixar_determinismo_lstm: Callable = _fixar_determinismo_lstm_real,
) -> dict[str, Any]:
    """Executa as 4 rotacoes internas + 1 treino externo de 1 outer fold.

    28 fits internos (4 rotacoes x 7 modelos) + 7 fits externos = 35 fits.
    `criar_modelo` e `fixar_determinismo_lstm` sao injetaveis para testes
    (fakes deterministicos, sem TF real).
    """
    registros = gate["registros"]
    textos = gate["textos_por_id"]
    ordem_classes = gate["classes"]
    modelaveis, excluidos = montar_registros_modelaveis(registros, ordem_classes)

    por_fold: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for r in modelaveis:
        por_fold[r["outer_fold"]].append(r)

    val_externo = por_fold[outer_fold]
    grupos_externo = {r["grupo_sha256"] for r in val_externo}
    ids_externo = {r["id_sha256"] for r in val_externo}

    inner_rows: list[list[Any]] = []
    outer_rows: list[list[Any]] = []
    fits_info: list[dict[str, Any]] = []

    for rot in montar_rotacoes_internas(outer_fold):
        g = rot["validacao"]
        treino_regs = [r for tf in rot["treino"] for r in por_fold[tf]]
        val_regs = por_fold[g]
        grupos_treino = {r["grupo_sha256"] for r in treino_regs}
        grupos_val = {r["grupo_sha256"] for r in val_regs}
        ids_treino = {r["id_sha256"] for r in treino_regs}
        ids_val = {r["id_sha256"] for r in val_regs}
        contexto = f"outer_fold={outer_fold} inner_validacao={g}"
        _assert_sem_vazamento(grupos_treino, grupos_val, grupos_externo,
                             ids_treino, ids_val, contexto)

        X_treino = [textos[r["id_sha256"]] for r in treino_regs]
        y_treino = [r["referencia_humana"] for r in treino_regs]
        X_val = [textos[r["id_sha256"]] for r in val_regs]

        for nome_modelo in MODELOS:
            alinhado, ausentes, eh_lstm = _fit_e_prever(
                nome_modelo, X_treino, y_treino, X_val, ordem_classes,
                criar_modelo, seed, f"{contexto} modelo={nome_modelo}",
                fixar_determinismo_lstm,
            )
            for i, r in enumerate(val_regs):
                vetor = alinhado[i].tolist()
                top1 = ordem_classes[int(np.argmax(alinhado[i]))]
                inner_rows.append([outer_fold, g, r["id_sha256"], r["grupo_sha256"],
                                   nome_modelo, vetor, top1])
            fits_info.append({
                "outer_fold": outer_fold, "inner_fold": g, "modelo": nome_modelo,
                "n_treino": len(treino_regs), "n_previsto": len(val_regs),
                "eh_lstm": eh_lstm, "classes_ausentes": ausentes,
            })

    treino_regs = [r for r in modelaveis if r["outer_fold"] != outer_fold]
    grupos_treino = {r["grupo_sha256"] for r in treino_regs}
    ids_treino = {r["id_sha256"] for r in treino_regs}
    _assert_sem_vazamento(grupos_treino, set(), grupos_externo,
                         ids_treino, ids_externo, f"outer_fold={outer_fold} externo")

    X_treino = [textos[r["id_sha256"]] for r in treino_regs]
    y_treino = [r["referencia_humana"] for r in treino_regs]
    X_val = [textos[r["id_sha256"]] for r in val_externo]

    for nome_modelo in MODELOS:
        alinhado, ausentes, eh_lstm = _fit_e_prever(
            nome_modelo, X_treino, y_treino, X_val, ordem_classes,
            criar_modelo, seed, f"outer_fold={outer_fold} externo modelo={nome_modelo}",
            fixar_determinismo_lstm,
        )
        for i, r in enumerate(val_externo):
            vetor = alinhado[i].tolist()
            top1 = ordem_classes[int(np.argmax(alinhado[i]))]
            outer_rows.append([outer_fold, r["id_sha256"], r["grupo_sha256"],
                               nome_modelo, vetor, top1])
        fits_info.append({
            "outer_fold": outer_fold, "inner_fold": None, "modelo": nome_modelo,
            "n_treino": len(treino_regs), "n_previsto": len(val_externo),
            "eh_lstm": eh_lstm, "classes_ausentes": ausentes,
        })

    excluidos_do_fold = [r for r in excluidos if r["outer_fold"] == outer_fold]
    return {
        "outer_fold": outer_fold,
        "inner_rows": inner_rows,
        "outer_rows": outer_rows,
        "fits_info": fits_info,
        "excluidos_h_fora_de_c": [
            {"id_sha256": r["id_sha256"], "grupo_sha256": r["grupo_sha256"],
             "tratamento": "tratamento_taxonomico_deterministico"}
            for r in excluidos_do_fold
        ],
        "total_modelaveis_no_fold": len(val_externo),
    }


def executar_todos_os_folds(
    gate: dict[str, Any], criar_modelo: Callable = criar_modelo_fase2b,
    seed: int = SEMENTE_PADRAO, folds=FOLDS,
    fixar_determinismo_lstm: Callable = _fixar_determinismo_lstm_real,
) -> list[dict[str, Any]]:
    return [
        executar_outer_fold(f, gate, criar_modelo=criar_modelo, seed=seed,
                            fixar_determinismo_lstm=fixar_determinismo_lstm)
        for f in folds
    ]


# --------------------------------------------------------------------------
# Hashes canonicos e agregacao final
# --------------------------------------------------------------------------

def _chave_inner(linha: list[Any]) -> tuple:
    outer_fold, inner_fold, id_sha256, _grupo, modelo, _vetor, _top1 = linha
    return (outer_fold, inner_fold, modelo, id_sha256)


def _chave_outer(linha: list[Any]) -> tuple:
    outer_fold, id_sha256, _grupo, modelo, _vetor, _top1 = linha
    return (outer_fold, modelo, id_sha256)


def calcular_input_bundle_sha256(gate: dict[str, Any], modelaveis: list[dict[str, Any]],
                                 excluidos: list[dict[str, Any]]) -> str:
    payload = {
        **gate["hashes"],
        "total_registros": gate["total_registros"],
        "total_modelaveis": len(modelaveis),
        "ids_h_fora_de_c": sorted(r["id_sha256"] for r in excluidos),
    }
    return cae.sha256_json(payload)


def calcular_predicoes_canonical_sha256(linhas: list[list[Any]], chave) -> str:
    ordenadas = sorted(linhas, key=chave)
    return cae.sha256_json(ordenadas)


def agregar_execucao(gate: dict[str, Any], resultados_por_fold: list[dict[str, Any]]
                     ) -> dict[str, Any]:
    """Junta os outer folds, valida as invariantes obrigatorias e computa os
    5 hashes cientificos. Levanta a excecao apropriada em qualquer violacao."""
    resultados_por_fold = sorted(resultados_por_fold, key=lambda r: r["outer_fold"])
    folds_vistos = [r["outer_fold"] for r in resultados_por_fold]
    if folds_vistos != list(FOLDS):
        raise ContagemEstruturalDivergente(f"Outer folds recebidos: {folds_vistos}")

    inner_rows: list[list[Any]] = []
    outer_rows: list[list[Any]] = []
    fits_info: list[dict[str, Any]] = []
    excluidos_h_fora_de_c: list[dict[str, Any]] = []
    for resultado in resultados_por_fold:
        inner_rows.extend(resultado["inner_rows"])
        outer_rows.extend(resultado["outer_rows"])
        fits_info.extend(resultado["fits_info"])
        excluidos_h_fora_de_c.extend(resultado["excluidos_h_fora_de_c"])

    modelaveis, excluidos = montar_registros_modelaveis(gate["registros"], gate["classes"])
    total_modelaveis = len(modelaveis)

    total_fits = len(fits_info)
    if total_fits != FITS_ESPERADOS_TOTAL:
        raise ContagemEstruturalDivergente(
            f"Total de fits divergente: {total_fits} != {FITS_ESPERADOS_TOTAL}"
        )
    fits_lstm = [f for f in fits_info if f["modelo"] == "lstm"]
    if len(fits_lstm) != FITS_ESPERADOS_LSTM:
        raise ContagemEstruturalDivergente(
            f"Total de fits LSTM divergente: {len(fits_lstm)} != {FITS_ESPERADOS_LSTM}"
        )
    fallbacks_lstm = sum(1 for f in fits_lstm if f["eh_lstm"] is not True)
    if fallbacks_lstm:
        raise BloqueadoLstmFallback(f"{fallbacks_lstm} fits de LSTM usaram fallback.")

    esperado_inner_por_modelo = 4 * total_modelaveis
    esperado_outer_por_modelo = total_modelaveis
    contagem_interna: dict[str, int] = defaultdict(int)
    for linha in inner_rows:
        contagem_interna[linha[4]] += 1
    contagem_externa: dict[str, int] = defaultdict(int)
    for linha in outer_rows:
        contagem_externa[linha[3]] += 1
    for modelo in MODELOS:
        if contagem_interna.get(modelo, 0) != esperado_inner_por_modelo:
            raise ContagemEstruturalDivergente(
                f"Meta-exemplos internos do modelo {modelo}: "
                f"{contagem_interna.get(modelo, 0)} != {esperado_inner_por_modelo}"
            )
        if contagem_externa.get(modelo, 0) != esperado_outer_por_modelo:
            raise ContagemEstruturalDivergente(
                f"Previsoes externas do modelo {modelo}: "
                f"{contagem_externa.get(modelo, 0)} != {esperado_outer_por_modelo}"
            )

    # Cardinalidade exata por outer fold: um registro modelavel de T_f recebe
    # exatamente 1 previsao interna por modelo DENTRO daquele outer fold f —
    # nao globalmente. O mesmo registro pertence a T_f de ate 4 outer folds
    # distintos (todos exceto o seu proprio), cada um com sua propria rotacao
    # de treino, entao ele acumula ate 4 previsoes internas no total, uma por
    # contexto de outer fold. A chave inclui outer_fold por isso.
    contagem_par_interno: dict[tuple[int, str, str], int] = defaultdict(int)
    for linha in inner_rows:
        contagem_par_interno[(linha[0], linha[2], linha[4])] += 1
    duplicadas_internas = [k for k, v in contagem_par_interno.items() if v != 1]
    if duplicadas_internas:
        raise ContagemEstruturalDivergente(
            f"Registros com != 1 previsao interna por modelo (por outer fold): "
            f"{duplicadas_internas[:10]}"
        )
    # Previsoes externas: cada registro modelavel pertence a exatamente 1
    # outer fold (o seu proprio), entao a unicidade e global por (id, modelo).
    contagem_par_externo: dict[tuple[str, str], int] = defaultdict(int)
    for linha in outer_rows:
        contagem_par_externo[(linha[1], linha[3])] += 1
    duplicadas_externas = [k for k, v in contagem_par_externo.items() if v != 1]
    if duplicadas_externas:
        raise ContagemEstruturalDivergente(
            f"Registros com != 1 previsao externa por modelo: {duplicadas_externas[:10]}"
        )

    if len(excluidos_h_fora_de_c) != len(excluidos):
        raise ContagemEstruturalDivergente(
            f"H fora de C excluidos divergente: {len(excluidos_h_fora_de_c)} != {len(excluidos)}"
        )

    input_bundle_sha256 = calcular_input_bundle_sha256(gate, modelaveis, excluidos)
    inner_predictions_canonical_sha256 = calcular_predicoes_canonical_sha256(
        inner_rows, _chave_inner
    )
    outer_predictions_canonical_sha256 = calcular_predicoes_canonical_sha256(
        outer_rows, _chave_outer
    )

    classes_ausentes_por_treino = [
        {"outer_fold": f["outer_fold"], "inner_fold": f["inner_fold"],
         "modelo": f["modelo"], "classes_ausentes": f["classes_ausentes"]}
        for f in fits_info if f["classes_ausentes"]
    ]

    manifesto = {
        "schema_version": 1,
        "ordem_classes": gate["classes"],
        "modelos": MODELOS,
        "folds_externos": list(FOLDS),
        "rotacoes_internas_por_fold": {
            str(f): montar_rotacoes_internas(f) for f in FOLDS
        },
        "fits_totais": total_fits,
        "fits_internos": sum(1 for f in fits_info if f["inner_fold"] is not None),
        "fits_externos": sum(1 for f in fits_info if f["inner_fold"] is None),
        "fits_lstm_esperados": FITS_ESPERADOS_LSTM,
        "fits_lstm_reais": len(fits_lstm),
        "fallbacks_lstm": fallbacks_lstm,
        "meta_exemplos_internos_esperados_por_modelo": esperado_inner_por_modelo,
        "meta_exemplos_internos_obtidos_por_modelo": dict(contagem_interna),
        "previsoes_externas_esperadas_por_modelo": esperado_outer_por_modelo,
        "previsoes_externas_obtidas_por_modelo": dict(contagem_externa),
        "total_modelaveis": total_modelaveis,
        "total_excluidos_h_fora_de_c": len(excluidos_h_fora_de_c),
        "excluidos_h_fora_de_c": sorted(
            excluidos_h_fora_de_c, key=lambda r: r["id_sha256"]
        ),
        "classes_ausentes_por_treino": classes_ausentes_por_treino,
        "hashes_entrada": gate["hashes"],
    }
    crossfit_manifest_sha256 = cae.sha256_json(manifesto)

    contadores_estruturais = {
        "fits_totais": total_fits,
        "fits_lstm": len(fits_lstm),
        "fallbacks_lstm": fallbacks_lstm,
        "total_modelaveis": total_modelaveis,
        "total_excluidos_h_fora_de_c": len(excluidos_h_fora_de_c),
    }
    fase2b_science_sha256 = cae.sha256_json({
        "input_bundle_sha256": input_bundle_sha256,
        "inner_predictions_canonical_sha256": inner_predictions_canonical_sha256,
        "outer_predictions_canonical_sha256": outer_predictions_canonical_sha256,
        "crossfit_manifest_sha256": crossfit_manifest_sha256,
        "contadores_estruturais": contadores_estruturais,
    })

    hashes = {
        "input_bundle_sha256": input_bundle_sha256,
        "inner_predictions_canonical_sha256": inner_predictions_canonical_sha256,
        "outer_predictions_canonical_sha256": outer_predictions_canonical_sha256,
        "crossfit_manifest_sha256": crossfit_manifest_sha256,
        "fase2b_science_sha256": fase2b_science_sha256,
    }

    resumo = {
        "schema_version": 1,
        "status": "concluido",
        "hashes": hashes,
        "contadores_estruturais": contadores_estruturais,
        "hashes_entrada_gate_zero": gate["hashes"],
        "total_registros": gate["total_registros"],
        "total_grupos": gate["total_grupos"],
        "h_dentro_de_c": gate["h_dentro_de_c"],
        "h_fora_de_c": gate["h_fora_de_c"],
    }

    return {
        "manifesto": manifesto,
        "resumo": resumo,
        "hashes": hashes,
        "inner_rows": inner_rows,
        "outer_rows": outer_rows,
        "fits_info": fits_info,
    }


def montar_arrays_npz(inner_rows: list[list[Any]], outer_rows: list[list[Any]]
                      ) -> dict[str, np.ndarray]:
    """Empacota as matrizes de escore em arrays NumPy, ordenados canonicamente
    (mesma ordem usada no hash), prontos para `np.savez`."""
    inner_ordenadas = sorted(inner_rows, key=_chave_inner)
    outer_ordenadas = sorted(outer_rows, key=_chave_outer)
    inner_scores = np.array([linha[5] for linha in inner_ordenadas], dtype=np.float64)
    outer_scores = np.array([linha[4] for linha in outer_ordenadas], dtype=np.float64)
    return {
        "inner_outer_fold": np.array([l[0] for l in inner_ordenadas], dtype=np.int64),
        "inner_inner_fold": np.array([l[1] for l in inner_ordenadas], dtype=np.int64),
        "inner_id_sha256": np.array([l[2] for l in inner_ordenadas], dtype=object),
        "inner_grupo_sha256": np.array([l[3] for l in inner_ordenadas], dtype=object),
        "inner_modelo": np.array([l[4] for l in inner_ordenadas], dtype=object),
        "inner_scores": inner_scores,
        "inner_top1": np.array([l[6] for l in inner_ordenadas], dtype=object),
        "outer_outer_fold": np.array([l[0] for l in outer_ordenadas], dtype=np.int64),
        "outer_id_sha256": np.array([l[1] for l in outer_ordenadas], dtype=object),
        "outer_grupo_sha256": np.array([l[2] for l in outer_ordenadas], dtype=object),
        "outer_modelo": np.array([l[3] for l in outer_ordenadas], dtype=object),
        "outer_scores": outer_scores,
        "outer_top1": np.array([l[5] for l in outer_ordenadas], dtype=object),
    }


def comparar_execucoes(hashes_execucao_1: dict[str, str],
                       hashes_execucao_2: dict[str, str]) -> None:
    """Compara os 5 hashes cientificos de duas execucoes independentes.
    Levanta `NaoDeterminismoDetectado` (sem arredondar nada) se divergirem."""
    divergentes = {
        chave: (hashes_execucao_1.get(chave), hashes_execucao_2.get(chave))
        for chave in ("input_bundle_sha256", "inner_predictions_canonical_sha256",
                      "outer_predictions_canonical_sha256", "crossfit_manifest_sha256",
                      "fase2b_science_sha256")
        if hashes_execucao_1.get(chave) != hashes_execucao_2.get(chave)
    }
    if divergentes:
        raise NaoDeterminismoDetectado(
            "BLOQUEADO_NAO_DETERMINISMO: "
            + json.dumps(divergentes, ensure_ascii=False, sort_keys=True)
        )


def comparar_canario(resultado_a: dict[str, Any], resultado_b: dict[str, Any]
                     ) -> dict[str, Any]:
    """Compara EXATAMENTE (sem arredondar nada) os resultados de UM outer
    fold entre duas replicas independentes do canario de determinismo
    (Parte 6). So diagnostico: nunca decide sozinho a validade cientifica de
    uma Execucao Cientifica completa, so a do proprio canario."""
    inner_hash_a = calcular_predicoes_canonical_sha256(resultado_a["inner_rows"], _chave_inner)
    inner_hash_b = calcular_predicoes_canonical_sha256(resultado_b["inner_rows"], _chave_inner)
    outer_hash_a = calcular_predicoes_canonical_sha256(resultado_a["outer_rows"], _chave_outer)
    outer_hash_b = calcular_predicoes_canonical_sha256(resultado_b["outer_rows"], _chave_outer)

    def _chave_fit(f):
        return (f["inner_fold"] is None, f["inner_fold"] or 0, f["modelo"])

    fits_hash_a = cae.sha256_json(sorted(resultado_a["fits_info"], key=_chave_fit))
    fits_hash_b = cae.sha256_json(sorted(resultado_b["fits_info"], key=_chave_fit))

    por_modelo: dict[str, Any] = {}
    for modelo in MODELOS:
        inner_a = {_chave_inner(l): l for l in resultado_a["inner_rows"] if l[4] == modelo}
        inner_b = {_chave_inner(l): l for l in resultado_b["inner_rows"] if l[4] == modelo}
        outer_a = {_chave_outer(l): l for l in resultado_a["outer_rows"] if l[3] == modelo}
        outer_b = {_chave_outer(l): l for l in resultado_b["outer_rows"] if l[3] == modelo}

        mesmas_chaves_inner = set(inner_a) == set(inner_b)
        divergentes_inner = sorted(
            chave for chave in (set(inner_a) & set(inner_b))
            if inner_a[chave][5] != inner_b[chave][5] or inner_a[chave][6] != inner_b[chave][6]
        )
        mesmas_chaves_outer = set(outer_a) == set(outer_b)
        divergentes_outer = sorted(
            chave for chave in (set(outer_a) & set(outer_b))
            if outer_a[chave][4] != outer_b[chave][4] or outer_a[chave][5] != outer_b[chave][5]
        )
        por_modelo[modelo] = {
            "inner_total": len(inner_a),
            "inner_identico": mesmas_chaves_inner and not divergentes_inner,
            "inner_divergentes": len(divergentes_inner),
            "outer_total": len(outer_a),
            "outer_identico": mesmas_chaves_outer and not divergentes_outer,
            "outer_divergentes": len(divergentes_outer),
            "amostra_ids_divergentes_outer": [str(c[1]) for c in divergentes_outer[:10]],
        }

    todos_identicos = (
        inner_hash_a == inner_hash_b and outer_hash_a == outer_hash_b
        and fits_hash_a == fits_hash_b
        and all(m["inner_identico"] and m["outer_identico"] for m in por_modelo.values())
    )
    return {
        "veredito": "CANARIO_DETERMINISTICO" if todos_identicos else "CANARIO_NAO_DETERMINISTICO",
        "inner_predictions_canonical_sha256_a": inner_hash_a,
        "inner_predictions_canonical_sha256_b": inner_hash_b,
        "inner_iguais": inner_hash_a == inner_hash_b,
        "outer_predictions_canonical_sha256_a": outer_hash_a,
        "outer_predictions_canonical_sha256_b": outer_hash_b,
        "outer_iguais": outer_hash_a == outer_hash_b,
        "fits_estrutural_sha256_a": fits_hash_a,
        "fits_estrutural_sha256_b": fits_hash_b,
        "fits_iguais": fits_hash_a == fits_hash_b,
        "por_modelo": por_modelo,
    }


# --------------------------------------------------------------------------
# Persistencia
# --------------------------------------------------------------------------

def gravar_resultado_fold(resultado: dict[str, Any], saida_dir: Path) -> None:
    saida_dir.mkdir(parents=True, exist_ok=True)
    f = resultado["outer_fold"]
    arrays = montar_arrays_npz(resultado["inner_rows"], resultado["outer_rows"])
    np.savez_compressed(saida_dir / f"fase2b_fold_{f}_scores.npz", **arrays)
    publicavel = {
        "outer_fold": f,
        "fits_info": resultado["fits_info"],
        "excluidos_h_fora_de_c": resultado["excluidos_h_fora_de_c"],
        "total_modelaveis_no_fold": resultado["total_modelaveis_no_fold"],
        "total_inner_rows": len(resultado["inner_rows"]),
        "total_outer_rows": len(resultado["outer_rows"]),
    }
    (saida_dir / f"fase2b_fold_{f}_fits.json").write_text(
        json.dumps(publicavel, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def carregar_resultado_fold(entrada_dir: Path, outer_fold: int) -> dict[str, Any]:
    fits = json.loads((entrada_dir / f"fase2b_fold_{outer_fold}_fits.json").read_text(
        encoding="utf-8"
    ))
    with np.load(entrada_dir / f"fase2b_fold_{outer_fold}_scores.npz",
                allow_pickle=True) as npz:
        # Cada chave e materializada UMA UNICA VEZ antes dos loops. `NpzFile`
        # nao armazena em cache o array descomprimido: indexar `npz["chave"]`
        # dentro de um loop por linha faz o NumPy redescomprimir o array
        # inteiro do zip a cada iteracao, o que e O(n) por acesso e portanto
        # O(n^2) no total — e o unico motivo do job de agregacao ter estourado
        # o timeout com o corpus real (medido: ~7h projetadas por fold com o
        # padrao antigo, contra ~1s com os arrays ja materializados). Os
        # valores lidos, a ordem das linhas e os tipos permanecem os mesmos;
        # so o custo de acesso muda.
        inner_outer_fold = npz["inner_outer_fold"]
        inner_inner_fold = npz["inner_inner_fold"]
        inner_id_sha256 = npz["inner_id_sha256"]
        inner_grupo_sha256 = npz["inner_grupo_sha256"]
        inner_modelo = npz["inner_modelo"]
        inner_scores = npz["inner_scores"]
        inner_top1 = npz["inner_top1"]
        outer_outer_fold = npz["outer_outer_fold"]
        outer_id_sha256 = npz["outer_id_sha256"]
        outer_grupo_sha256 = npz["outer_grupo_sha256"]
        outer_modelo = npz["outer_modelo"]
        outer_scores = npz["outer_scores"]
        outer_top1 = npz["outer_top1"]

        inner_rows = [
            [int(inner_outer_fold[i]), int(inner_inner_fold[i]),
             str(inner_id_sha256[i]), str(inner_grupo_sha256[i]),
             str(inner_modelo[i]), inner_scores[i].tolist(),
             str(inner_top1[i])]
            for i in range(len(inner_id_sha256))
        ]
        outer_rows = [
            [int(outer_outer_fold[i]), str(outer_id_sha256[i]),
             str(outer_grupo_sha256[i]), str(outer_modelo[i]),
             outer_scores[i].tolist(), str(outer_top1[i])]
            for i in range(len(outer_id_sha256))
        ]
    return {
        "outer_fold": outer_fold,
        "inner_rows": inner_rows,
        "outer_rows": outer_rows,
        "fits_info": fits["fits_info"],
        "excluidos_h_fora_de_c": fits["excluidos_h_fora_de_c"],
        "total_modelaveis_no_fold": fits["total_modelaveis_no_fold"],
    }


def gravar_agregado(agregado: dict[str, Any], saida_dir: Path) -> None:
    saida_dir.mkdir(parents=True, exist_ok=True)
    (saida_dir / "fase2b_manifesto.json").write_text(
        json.dumps(agregado["manifesto"], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (saida_dir / "fase2b_resumo.json").write_text(
        json.dumps(agregado["resumo"], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (saida_dir / "fase2b_hashes.json").write_text(
        json.dumps(agregado["hashes"], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    arrays = montar_arrays_npz(agregado["inner_rows"], agregado["outer_rows"])
    inner_meta = {k: v for k, v in arrays.items() if k.startswith("inner_") and k != "inner_scores"}
    outer_meta = {k: v for k, v in arrays.items() if k.startswith("outer_") and k != "outer_scores"}
    np.savez_compressed(saida_dir / "fase2b_inner_scores.npz",
                        scores=arrays["inner_scores"], **inner_meta)
    np.savez_compressed(saida_dir / "fase2b_outer_scores.npz",
                        scores=arrays["outer_scores"], **outer_meta)


def gravar_gate_zero(gate: dict[str, Any], saida_dir: Path) -> None:
    """Artefato sanitizado do Gate Zero: so hashes e contagens, sem texto/ID."""
    saida_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "apto",
        "hashes": gate["hashes"],
        "total_registros": gate["total_registros"],
        "total_grupos": gate["total_grupos"],
        "h_dentro_de_c": gate["h_dentro_de_c"],
        "h_fora_de_c": gate["h_fora_de_c"],
        "total_classes": len(gate["classes"]),
    }
    (saida_dir / "fase2b_gate_zero.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def gravar_gate_zero_replay(gate: dict[str, Any], saida_dir: Path) -> None:
    """Artefato sanitizado do Gate Zero REPLAY: hashes, contagens e o sexto
    fingerprint replay_input_sha256 — nunca texto/ID."""
    saida_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "apto",
        "modo": "replay",
        "replay_input_sha256": gate["replay_input_sha256"],
        "hashes": gate["hashes"],
        "total_registros": gate["total_registros"],
        "total_grupos": gate["total_grupos"],
        "h_dentro_de_c": gate["h_dentro_de_c"],
        "h_fora_de_c": gate["h_fora_de_c"],
        "total_classes": len(gate["classes"]),
    }
    (saida_dir / "fase2b_gate_zero_replay.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


# --------------------------------------------------------------------------
# Fingerprint do ambiente (DIAGNOSTICO — nunca entra nos hashes cientificos)
# --------------------------------------------------------------------------

_ENV_DETERMINISMO = (
    "PYTHONHASHSEED", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "TF_DETERMINISTIC_OPS",
    "TF_ENABLE_ONEDNN_OPTS", "TF_NUM_INTRAOP_THREADS", "TF_NUM_INTEROP_THREADS",
)


def coletar_fingerprint_ambiente() -> dict[str, Any]:
    """Diagnostico sanitizado do ambiente de execucao: nenhum dado de chamado,
    so versoes de biblioteca, CPU/SO e configuracao de paralelismo efetiva.
    Usado apenas para investigar nao-determinismo entre runners; nunca entra
    em `input_bundle_sha256`/`crossfit_manifest_sha256`/`fase2b_science_sha256`."""
    import contextlib
    import io
    import platform
    import subprocess

    fingerprint: dict[str, Any] = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "image_os": os.environ.get("ImageOS"),
        "image_version": os.environ.get("ImageVersion"),
        "runner_os": os.environ.get("RUNNER_OS"),
        "runner_arch": os.environ.get("RUNNER_ARCH"),
        "runner_name": os.environ.get("RUNNER_NAME"),
        "numpy_version": np.__version__,
    }

    try:
        import scipy
        fingerprint["scipy_version"] = scipy.__version__
    except Exception as e:  # noqa: BLE001
        fingerprint["scipy_version"] = f"indisponivel: {type(e).__name__}"

    try:
        import sklearn
        fingerprint["sklearn_version"] = sklearn.__version__
    except Exception as e:  # noqa: BLE001
        fingerprint["sklearn_version"] = f"indisponivel: {type(e).__name__}"

    try:
        import tensorflow as tf
        import keras
        fingerprint["tensorflow_version"] = tf.__version__
        fingerprint["keras_version"] = keras.__version__
        fingerprint["tf_intra_op_parallelism_threads"] = (
            tf.config.threading.get_intra_op_parallelism_threads()
        )
        fingerprint["tf_inter_op_parallelism_threads"] = (
            tf.config.threading.get_inter_op_parallelism_threads()
        )
    except Exception as e:  # noqa: BLE001
        fingerprint["tensorflow_erro"] = f"{type(e).__name__}: {e}"

    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            np.show_config()
        fingerprint["numpy_show_config"] = buf.getvalue()
    except Exception as e:  # noqa: BLE001
        fingerprint["numpy_show_config"] = f"indisponivel: {type(e).__name__}"

    try:
        import threadpoolctl
        fingerprint["threadpool_info"] = threadpoolctl.threadpool_info()
    except Exception as e:  # noqa: BLE001
        fingerprint["threadpool_info"] = f"indisponivel: {type(e).__name__}"

    try:
        resultado = subprocess.run(["lscpu"], capture_output=True, text=True, timeout=10)
        fingerprint["lscpu"] = resultado.stdout
    except Exception as e:  # noqa: BLE001
        fingerprint["lscpu"] = f"indisponivel: {type(e).__name__}"

    try:
        conteudo = Path("/proc/cpuinfo").read_text(encoding="utf-8")
        linhas_modelo = [l for l in conteudo.splitlines() if l.startswith("model name")]
        linhas_flags = [l for l in conteudo.splitlines() if l.startswith("flags")]
        fingerprint["cpu_model_name"] = linhas_modelo[0] if linhas_modelo else None
        flags_relevantes = {"avx", "avx2", "avx512f", "avx512bw", "avx512vl",
                            "avx512_vnni", "fma", "sse4_1", "sse4_2", "f16c"}
        flags_presentes = set(linhas_flags[0].split()) if linhas_flags else set()
        fingerprint["simd_flags_relevantes"] = sorted(flags_relevantes & flags_presentes)
    except Exception as e:  # noqa: BLE001
        fingerprint["cpuinfo_erro"] = f"{type(e).__name__}: {e}"

    fingerprint["env_determinismo"] = {
        chave: os.environ.get(chave) for chave in _ENV_DETERMINISMO
    }
    return fingerprint


def gravar_fingerprint_ambiente(saida_dir: Path, nome_arquivo: str) -> None:
    saida_dir.mkdir(parents=True, exist_ok=True)
    payload = coletar_fingerprint_ambiente()
    (saida_dir / nome_arquivo).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def gravar_proveniencia(saida_dir: Path, run_id: str | None, commit_sha: str | None,
                        execucao: str | None) -> None:
    saida_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "gerado_em": agora_bahia(),
        "run_id": run_id,
        "commit_sha": commit_sha,
        "execucao": execucao,
    }
    (saida_dir / "fase2b_proveniencia_run.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=rero.CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--particoes", type=Path, default=rero.PARTICOES_PADRAO)
    p.add_argument("--alvo-congelado", type=Path, default=rero.ALVO_CONGELADO_PADRAO)
    p.add_argument("--classes", type=Path, default=CLASSES_PATH_PADRAO)
    p.add_argument("--modo-replay", action="store_true",
                   help="usa gate_zero_replay() sobre o bundle privado congelado, "
                        "em vez de gate_zero() sobre a planilha operacional viva "
                        "(mutuamente exclusivo com a rodada [FASE2B-RUN])")
    p.add_argument("--replay-spreadsheet-id", default=None,
                   help="ID da spreadsheet privada do bundle REPLAY; se omitido, "
                        "resolve via REPLAY_SPREADSHEET_ID (env/Secret) ou "
                        "replay_spreadsheet_id.local")
    p.add_argument("--somente-gate-zero", action="store_true",
                   help="roda so o Gate Zero (releitura + validacao de hashes), sem treinar nada")
    p.add_argument("--outer-fold", type=int, default=None,
                   help="roda so este outer fold e grava scores parciais")
    p.add_argument("--agregar", action="store_true",
                   help="agrega os resultados parciais de --entrada-dir")
    p.add_argument("--comparar-canario", action="store_true",
                   help="compara EXATAMENTE duas replicas de --outer-fold (canario de determinismo)")
    p.add_argument("--entrada-a", type=Path, default=None,
                   help="diretorio com o resultado da replica A (--comparar-canario)")
    p.add_argument("--entrada-b", type=Path, default=None,
                   help="diretorio com o resultado da replica B (--comparar-canario)")
    p.add_argument("--entrada-dir", type=Path, default=SAIDA_DIR_PADRAO)
    p.add_argument("--saida-dir", type=Path, default=SAIDA_DIR_PADRAO)
    p.add_argument("--run-id", default=None)
    p.add_argument("--commit-sha", default=None)
    p.add_argument("--execucao", default=None)
    return p.parse_args()


def _montar_gate(args: argparse.Namespace) -> dict[str, Any]:
    """Despacha entre `gate_zero()` (fonte online viva, [FASE2B-RUN]) e
    `gate_zero_replay()` (bundle privado congelado, [FASE2B-REPLAY]),
    conforme `--modo-replay`. Nenhuma das duas funcoes muda; so a escolha de
    qual chamar e nova."""
    if args.modo_replay:
        return gate_zero_replay(
            spreadsheet_id=args.replay_spreadsheet_id,
            credenciais=args.credenciais,
            particoes_path=args.particoes,
        )
    return gate_zero(
        config_path=args.config, credenciais=args.credenciais,
        particoes_path=args.particoes, alvo_congelado_path=args.alvo_congelado,
        classes_path=args.classes,
    )


def main() -> int:
    args = parse_args()
    if args.somente_gate_zero:
        gate = _montar_gate(args)
        if args.modo_replay:
            gravar_gate_zero_replay(gate, args.saida_dir)
            gravar_fingerprint_ambiente(
                args.saida_dir, "fase2b_fingerprint_gate_zero_replay.json"
            )
        else:
            gravar_gate_zero(gate, args.saida_dir)
            gravar_fingerprint_ambiente(args.saida_dir, "fase2b_fingerprint_gate_zero.json")
        print(json.dumps(gate["hashes"], ensure_ascii=False, indent=2))
        return 0

    if args.comparar_canario:
        if args.outer_fold is None or args.entrada_a is None or args.entrada_b is None:
            print("Informe --outer-fold, --entrada-a e --entrada-b para --comparar-canario.",
                  file=sys.stderr)
            return 2
        resultado_a = carregar_resultado_fold(args.entrada_a, args.outer_fold)
        resultado_b = carregar_resultado_fold(args.entrada_b, args.outer_fold)
        comparacao = comparar_canario(resultado_a, resultado_b)
        args.saida_dir.mkdir(parents=True, exist_ok=True)
        (args.saida_dir / "fase2b_canario_comparacao.json").write_text(
            json.dumps(comparacao, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(comparacao, ensure_ascii=False, indent=2))
        return 0 if comparacao["veredito"] == "CANARIO_DETERMINISTICO" else 1

    if args.agregar:
        gate = _montar_gate(args)
        resultados = [carregar_resultado_fold(args.entrada_dir, f) for f in FOLDS]
        agregado = agregar_execucao(gate, resultados)
        gravar_agregado(agregado, args.saida_dir)
        gravar_proveniencia(args.saida_dir, args.run_id, args.commit_sha, args.execucao)
        print(json.dumps(agregado["hashes"], ensure_ascii=False, indent=2))
        return 0

    if args.outer_fold is None:
        print("Informe --outer-fold N ou --agregar.", file=sys.stderr)
        return 2

    gate = _montar_gate(args)
    resultado = executar_outer_fold(args.outer_fold, gate)
    gravar_resultado_fold(resultado, args.saida_dir)
    gravar_fingerprint_ambiente(
        args.saida_dir, f"fase2b_fingerprint_fold_{args.outer_fold}.json"
    )
    print(json.dumps({
        "outer_fold": args.outer_fold,
        "fits": len(resultado["fits_info"]),
        "inner_rows": len(resultado["inner_rows"]),
        "outer_rows": len(resultado["outer_rows"]),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
