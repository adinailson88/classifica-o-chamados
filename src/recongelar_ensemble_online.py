#!/usr/bin/env python3
"""Recongela a base do ensemble sobre o texto ONLINE atual da planilha.

Ferramenta estritamente READ-ONLY. Substitui o Gate 2A baseado em recuperar um
texto historico: em vez de provar que uma fonte antiga reproduz os grupos
congelados, esta ferramenta aceita que o texto atual da planilha e a fonte
oficial (corrigida humanamente apos 04/08/2026) e recalcula os grupos textuais
sobre ele, preservando tudo o mais.

O que e preservado, sem nova execucao:
    - os mesmos 13.972 IDs de `docs/dados/particoes_canonicas_mapa.csv`;
    - a mesma atribuicao ID -> outer_fold desse arquivo (nenhum
      StratifiedGroupKFold e refeito aqui);
    - a categoria historica (H), a referencia humana (R) e o alvo binario
      Y = 1(H != R) do congelamento anterior em
      `docs/dados/ensemble/alvo_ensemble.json`.

O que e recalculado sobre o texto online atual:
    - o grupo_sha256 de cada registro (mesma normalizacao e mesmo hash de
      `src/construir_grupos_textuais.py`, inalterados);
    - o hash_corpus da rodada, porque o texto mudou;
    - as predicoes out-of-fold do LinearSVC, retreinado do zero fold a fold.

Duas familias de invariante sao verificadas antes de qualquer treino, e
qualquer violacao BLOQUEIA a execucao (nenhum modelo e treinado):
    1. nenhum grupo_sha256 recalculado pode aparecer em mais de um outer_fold
       preservado (senao o particionamento por grupo deixou de valer);
    2. H, R e Y precisam ser identicos ao congelamento anterior para todo
       registro dos 13.972 (a correcao humana da planilha mudou o TEXTO, nao
       os rotulos ja validados; se os rotulos tambem mudaram, a base nao e
       mais comparavel e a rodada para).

As saidas sao sanitizadas: nao publicam titulos, descricoes nem IDs brutos de
chamados; apenas SHA-256 do ID, hash do grupo e rotulos ja usados nos demais
artefatos canonicos do repositorio.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import congelar_alvo_ensemble as cae  # noqa: E402
import construir_grupos_textuais as cgt  # noqa: E402
import executar_rodada_canonica as erc  # noqa: E402
import planilha as pl  # noqa: E402
import retreinar_modelos_canonicos as rmc  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
DADOS = RAIZ / "docs" / "dados"
PARTICOES_PADRAO = DADOS / "particoes_canonicas_mapa.csv"
ALVO_CONGELADO_PADRAO = DADOS / "ensemble" / "alvo_ensemble.json"
RESUMO_CONGELADO_PADRAO = DADOS / "ensemble" / "alvo_ensemble_resumo.json"
SAIDA_DIR_PADRAO = DADOS / "ensemble" / "recongelamento_online"
ALVO_ONLINE_PADRAO = SAIDA_DIR_PADRAO / "alvo_ensemble_online.json"
PARTICOES_ONLINE_PADRAO = SAIDA_DIR_PADRAO / "particoes_ensemble_online_mapa.csv"
RESUMO_ONLINE_PADRAO = SAIDA_DIR_PADRAO / "resumo_recongelamento_online.json"
PREDICOES_ONLINE_PADRAO = SAIDA_DIR_PADRAO / "predicoes_linear_svc_online.csv"
RELATORIO_PADRAO = RAIZ / "docs" / "RECONGELAMENTO_ONLINE_ENSEMBLE.md"

SPREADSHEET_ID_CANONICO = "1lohPUQOgxzt_DMxnNLKMxnieZq1sVmh4uwBLbbgvfiQ"
ABA_CANONICA = "CHAMADOS_ESQUELETO_REDUZIDO"

TOTAL_ESPERADO = 13972
DOBRAS_ESPERADAS = 5
SEMENTE_ESPERADA = 42
FOLDS_ESPERADOS_PADRAO = list(range(1, DOBRAS_ESPERADAS + 1))

# Baseline historico do LinearSVC sobre o texto congelado anterior. Serve
# apenas para comparacao no relatorio; nunca e forcado como resultado.
BASELINE_HISTORICO = {
    "alertas_naturais": 2849,
    "inadequacoes_na_fila": 528,
    "precisao_fila_natural": 0.1853,
    "correcoes_top1": 475,
    "neutros": 53,
    "prejudicados": 2321,
}

SCHEMA_CAMPOS = [
    "id_sha256",
    "grupo_sha256",
    "outer_fold",
    "categoria_historica",
    "referencia_humana",
    "historico_no_espaco_de_classes",
    "alvo_inadequacao",
]


# --------------------------------------------------------------------------
# Carregamento do que fica preservado
# --------------------------------------------------------------------------

def carregar_particoes_preservadas(caminho: Path) -> dict[str, dict[str, Any]]:
    """ID -> {grupo_sha256 congelado, outer_fold}. Nunca recalculado aqui."""
    return cae.carregar_particoes(caminho)


def carregar_alvo_congelado(caminho: Path) -> dict[str, dict[str, Any]]:
    """id_sha256 -> registro congelado (H, R, Y) do alvo anterior."""
    payload = json.loads(caminho.read_text(encoding="utf-8"))
    registros = payload.get("records", [])
    por_id = {r["id_sha256"]: r for r in registros}
    if len(por_id) != len(registros):
        raise RuntimeError("IDs duplicados no alvo congelado anterior.")
    return por_id


def carregar_hashes_congelamento_anterior(caminho_resumo: Path) -> dict[str, Any]:
    """Hashes do congelamento anterior, lidos diretamente do artefato.

    Esses hashes dependiam do texto vivo no momento da rodada historica
    (03-04/08/2026), anterior a correcao humana subsequente. Como esse texto
    nao existe mais na planilha, os valores NAO sao recalculados aqui: sao
    lidos de `docs/dados/ensemble/alvo_ensemble_resumo.json`, ja gravado.
    """
    payload = json.loads(caminho_resumo.read_text(encoding="utf-8"))
    return {
        "hash_corpus": payload.get("hash_corpus"),
        "hash_historico_ensemble": payload.get("hash_historico_ensemble"),
        "hash_alvo_ensemble": payload.get("hash_alvo_ensemble"),
        "classes_sha256": payload.get("classes_sha256"),
        "partition_manifest_sha256": payload.get("partition_manifest_sha256"),
    }


# --------------------------------------------------------------------------
# Leitura da planilha ONLINE atual
# --------------------------------------------------------------------------

def ler_registros_online(config_path: Path, credenciais: str | None = None
                         ) -> list[dict[str, str]]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    spreadsheet_id = pl.id_planilha(config)
    if spreadsheet_id != SPREADSHEET_ID_CANONICO:
        raise RuntimeError(
            f"Spreadsheet ID divergente do canonico: {spreadsheet_id!r}"
        )
    if config.get("aba_principal") != ABA_CANONICA:
        raise RuntimeError(
            f"Aba principal divergente da canonica: {config.get('aba_principal')!r}"
        )
    sh = pl.abrir_planilha(spreadsheet_id, credenciais)
    return cgt.ler_registros(sh, config)


# --------------------------------------------------------------------------
# Recalculo do grupo textual atual e montagem da base
# --------------------------------------------------------------------------

def montar_base_atual(
    registros_online: list[dict[str, str]],
    particoes: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Recalcula grupo/H/R/texto atuais para os IDs preservados nas particoes.

    Registros do universo online que nao pertencem as particoes preservadas
    sao ignorados (sao os 148 fora do corpus atual, por construcao). IDs das
    particoes que nao aparecem mais na planilha online contam como
    `faltantes_no_online`, que por si so bloqueia a rodada: o denominador de
    13.972 deixaria de ser reconstituivel.
    """
    ids_particoes = set(particoes)
    encontrados: dict[str, dict[str, Any]] = {}
    ids_duplicados: list[str] = []

    for r in registros_online:
        id_bruto = r.get("id", "")
        if not id_bruto:
            continue
        id_sha = hashlib.sha256(id_bruto.encode("utf-8")).hexdigest()
        if id_sha not in ids_particoes:
            continue
        if id_sha in encontrados:
            ids_duplicados.append(id_sha)
            continue
        normalizados = [cgt.normalizar_texto(r.get(c, ""))
                        for c in cgt.CAMPOS_TEXTUAIS]
        grupo_atual = cgt.hash_grupo(normalizados)
        encontrados[id_sha] = {
            "grupo_atual": grupo_atual,
            "categoria_historica_atual": r.get("categoria_historica", ""),
            "referencia_humana_atual": cgt.referencia_humana(r),
            "texto_atual": rmc.montar_texto(r),
            "outer_fold": particoes[id_sha]["outer_fold"],
        }

    faltantes_no_online = sorted(ids_particoes - set(encontrados))
    return {
        "base": encontrados,
        "faltantes_no_online": faltantes_no_online,
        "ids_duplicados_no_online": sorted(set(ids_duplicados)),
    }


# --------------------------------------------------------------------------
# Invariantes que bloqueiam a execucao
# --------------------------------------------------------------------------

def validar_grupos_nao_cruzam_dobras(base: dict[str, dict[str, Any]]
                                     ) -> dict[str, Any]:
    """Nenhum grupo_sha256 ATUAL pode aparecer em mais de um outer_fold."""
    dobras_por_grupo: dict[str, set[int]] = defaultdict(set)
    for item in base.values():
        dobras_por_grupo[item["grupo_atual"]].add(item["outer_fold"])
    grupos_cruzando = sorted(
        g for g, dobras in dobras_por_grupo.items() if len(dobras) > 1
    )
    return {
        "total_grupos_atuais_distintos": len(dobras_por_grupo),
        "grupos_cruzando_dobras": len(grupos_cruzando),
        "amostra_grupos_cruzando_dobras": grupos_cruzando[:20],
    }


def validar_h_r_y_preservados(
    base: dict[str, dict[str, Any]],
    alvo_congelado: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Compara H, R e Y atuais contra o congelamento anterior, por ID."""
    h_divergentes: list[str] = []
    r_divergentes: list[str] = []
    y_divergentes: list[str] = []
    for id_sha, item in base.items():
        congelado = alvo_congelado.get(id_sha)
        if congelado is None:
            # Sem contraparte no alvo anterior: nao ha o que comparar aqui;
            # ausencia de contraparte e reportada por outra checagem.
            continue
        h_atual = item["categoria_historica_atual"]
        r_atual = item["referencia_humana_atual"]
        y_atual = int(h_atual != r_atual)
        if h_atual != congelado["categoria_historica"]:
            h_divergentes.append(id_sha)
        if r_atual != congelado["referencia_humana"]:
            r_divergentes.append(id_sha)
        if y_atual != congelado["alvo_inadequacao"]:
            y_divergentes.append(id_sha)
    return {
        "h_divergentes": len(h_divergentes),
        "r_divergentes": len(r_divergentes),
        "y_divergentes": len(y_divergentes),
        "amostra_h_divergentes": sorted(h_divergentes)[:20],
        "amostra_r_divergentes": sorted(r_divergentes)[:20],
        "amostra_y_divergentes": sorted(y_divergentes)[:20],
    }


def validar_cobertura_particoes_alvo(
    particoes: dict[str, dict[str, Any]],
    alvo_congelado: dict[str, dict[str, Any]],
    total_esperado: int | None = None,
    folds_esperados: list[int] | None = None,
) -> dict[str, Any]:
    """Confirma que particoes e alvo_congelado descrevem o MESMO universo.

    `validar_h_r_y_preservados` so compara H/R/Y para IDs presentes nos dois
    lados; sozinha, ela aceita silenciosamente um ID de uma fonte sem
    contraparte na outra. Esta funcao fecha essa lacuna: exige
    `set(particoes) == set(alvo_congelado)`, os dois com o tamanho esperado,
    a MESMA dobra por ID nas duas fontes e, quando `folds_esperados` e
    informado (a producao sempre informa `[1, 2, 3, 4, 5]`), que o conjunto
    de outer_folds de cada fonte seja exatamente esse. Qualquer violacao
    bloqueia a rodada antes de qualquer treino.
    """
    ids_particoes = set(particoes)
    ids_alvo = set(alvo_congelado)
    particao_sem_alvo = sorted(ids_particoes - ids_alvo)
    alvo_sem_particao = sorted(ids_alvo - ids_particoes)
    folds_particao = sorted({p["outer_fold"] for p in particoes.values()})
    folds_alvo = sorted({a["outer_fold"] for a in alvo_congelado.values()})
    dobra_divergente = sorted(
        id_sha for id_sha in ids_particoes & ids_alvo
        if particoes[id_sha]["outer_fold"] != alvo_congelado[id_sha]["outer_fold"]
    )

    diagnostico: dict[str, Any] = {
        "total_ids_particoes": len(particoes),
        "total_ids_alvo_congelado": len(alvo_congelado),
        "total_ids_particao_sem_alvo": len(particao_sem_alvo),
        "amostra_ids_particao_sem_alvo": particao_sem_alvo[:20],
        "total_ids_alvo_sem_particao": len(alvo_sem_particao),
        "amostra_ids_alvo_sem_particao": alvo_sem_particao[:20],
        "folds_particao": folds_particao,
        "folds_alvo_congelado": folds_alvo,
        "total_dobra_historica_divergente": len(dobra_divergente),
        "amostra_dobra_historica_divergente": dobra_divergente[:20],
    }
    bloqueios = []
    if total_esperado is not None:
        if diagnostico["total_ids_particoes"] != total_esperado:
            bloqueios.append("total_ids_particoes_divergente_do_denominador_esperado")
        if diagnostico["total_ids_alvo_congelado"] != total_esperado:
            bloqueios.append("total_ids_alvo_congelado_divergente_do_denominador_esperado")
    if particao_sem_alvo:
        bloqueios.append("ids_particao_sem_contraparte_no_alvo")
    if alvo_sem_particao:
        bloqueios.append("ids_alvo_sem_contraparte_na_particao")
    if folds_esperados is not None:
        if folds_particao != folds_esperados:
            bloqueios.append("folds_particao_invalidos")
        if folds_alvo != folds_esperados:
            bloqueios.append("folds_alvo_congelado_invalidos")
    if dobra_divergente:
        bloqueios.append("dobra_historica_divergente_entre_alvo_e_particao")
    diagnostico["bloqueios"] = bloqueios
    return diagnostico


def montar_diagnostico(
    base_info: dict[str, Any],
    alvo_congelado: dict[str, dict[str, Any]],
    particoes: dict[str, dict[str, Any]],
    total_esperado: int | None = None,
    folds_esperados: list[int] | None = None,
) -> dict[str, Any]:
    """Monta o diagnostico completo e decide se a rodada esta apta.

    A cobertura entre particoes e alvo_congelado (Correcao 3) e verificada
    primeiro, e sem excecao: `set(particoes) == set(alvo_congelado)`, os dois
    do tamanho esperado, os mesmos outer_folds validos nos dois lados e a
    MESMA dobra por ID em ambas as fontes historicas. So depois disso a
    cobertura ONLINE (`faltantes_no_online`) e checada. `total_esperado` e
    `folds_esperados` sao gates opcionais que ancoram o contrato de producao
    (13.972 IDs, dobras {1..5}) sem acoplar essas constantes a logica de
    comparacao em si — por isso podem ser omitidos em bases pequenas de teste.
    """
    base = base_info["base"]
    cobertura = validar_cobertura_particoes_alvo(
        particoes, alvo_congelado, total_esperado=total_esperado,
        folds_esperados=folds_esperados,
    )
    diagnostico: dict[str, Any] = dict(cobertura)
    bloqueios = list(cobertura["bloqueios"])

    diagnostico["total_ids_encontrados_no_online"] = len(base)
    diagnostico["total_faltantes_no_online"] = len(base_info["faltantes_no_online"])
    diagnostico["amostra_faltantes_no_online"] = base_info["faltantes_no_online"][:20]
    diagnostico["total_ids_duplicados_no_online"] = len(base_info["ids_duplicados_no_online"])

    diagnostico.update(validar_grupos_nao_cruzam_dobras(base))
    diagnostico.update(validar_h_r_y_preservados(base, alvo_congelado))

    grupos_congelados = {id_sha: p["grupo_sha256"] for id_sha, p in particoes.items()}
    grupos_alterados = sum(
        1 for id_sha, item in base.items()
        if grupos_congelados.get(id_sha) != item["grupo_atual"]
    )
    diagnostico["total_grupos_congelados_distintos"] = len(set(grupos_congelados.values()))
    diagnostico["total_grupos_ou_textos_alterados_em_relacao_ao_historico"] = grupos_alterados

    if diagnostico["total_faltantes_no_online"]:
        bloqueios.append("ids_faltantes_no_online")
    if diagnostico["total_ids_duplicados_no_online"]:
        bloqueios.append("ids_duplicados_no_online")
    if diagnostico["grupos_cruzando_dobras"]:
        bloqueios.append("grupos_cruzando_dobras")
    if diagnostico["h_divergentes"]:
        bloqueios.append("h_divergentes")
    if diagnostico["r_divergentes"]:
        bloqueios.append("r_divergentes")
    if diagnostico["y_divergentes"]:
        bloqueios.append("y_divergentes")
    diagnostico["bloqueios"] = bloqueios
    diagnostico["status"] = "apto_para_baseline" if not bloqueios else "bloqueado"
    return diagnostico


# --------------------------------------------------------------------------
# Recongelamento (apenas se nao houver bloqueio)
# --------------------------------------------------------------------------

def montar_registros_recongelados(
    base: dict[str, dict[str, Any]],
    particoes: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    classes = sorted({item["referencia_humana_atual"] for item in base.values()})
    registros = []
    for id_sha, item in base.items():
        h = item["categoria_historica_atual"]
        r = item["referencia_humana_atual"]
        registros.append({
            "id_sha256": id_sha,
            "grupo_sha256": item["grupo_atual"],
            "outer_fold": particoes[id_sha]["outer_fold"],
            "categoria_historica": h,
            "referencia_humana": r,
            "historico_no_espaco_de_classes": h in classes,
            "alvo_inadequacao": int(h != r),
        })
    registros.sort(key=lambda r: r["id_sha256"])
    return registros


def calcular_hash_corpus(registros: list[dict[str, Any]]) -> str:
    corpus = {
        "chaves": [r["id_sha256"] for r in registros],
        "grupos": [r["grupo_sha256"] for r in registros],
        "rotulos": [r["referencia_humana"] for r in registros],
    }
    return erc.hash_corpus(corpus)


def montar_particoes_online_csv_bytes(registros: list[dict[str, Any]]) -> bytes:
    """Manifesto de particao ONLINE: id_sha256, grupo ATUAL, dobra preservada.

    Artefato NOVO e distinto de `docs/dados/particoes_canonicas_mapa.csv`
    (que permanece intocado, como evidencia historica da origem dos folds).
    Ordenado por id_sha256, igual aos demais mapas do repositorio.
    """
    buf = io.StringIO()
    escritor = csv.writer(buf, lineterminator="\n")
    escritor.writerow(["id_sha256", "grupo_sha256", "dobra"])
    for r in sorted(registros, key=lambda r: r["id_sha256"]):
        escritor.writerow([r["id_sha256"], r["grupo_sha256"], r["outer_fold"]])
    return buf.getvalue().encode("utf-8")


def calcular_fold_assignment_sha256(pares: list[tuple[str, int]]) -> str:
    """SHA-256 canonico de (id_sha256, outer_fold) apenas — sem grupo nem
    rotulo. Muda se, e somente se, a atribuicao ID -> fold mudar."""
    itens = sorted(pares)
    return cgt._sha256_json([list(i) for i in itens])


def treinar_linear_svc_do_zero(
    base: dict[str, dict[str, Any]],
    registros: list[dict[str, Any]],
) -> dict[str, Any]:
    """Retreina o LinearSVC fold a fold, sobre o texto online atual.

    Nao reutiliza nenhuma predicao antiga: chama `avaliar_modelo`, que ajusta
    um LinearSVC novo por dobra e verifica, a cada dobra, que nenhum grupo
    textual atual do treino aparece no teste. O determinismo (SEMENTE_ESPERADA
    = 42) vem de `modelos_zoo.criar_modelo("linear_svc")`, que fixa
    `random_state=42` no proprio estimador; nao existe (nem existiu antes
    deste ajuste) um parametro `semente` aqui com efeito real — um parametro
    assim so daria a falsa impressao de que a rodada era configuravel.
    """
    ordem = [r["id_sha256"] for r in registros]
    corpus = {
        "textos": [base[id_sha]["texto_atual"] for id_sha in ordem],
        "rotulos": [base[id_sha]["referencia_humana_atual"] for id_sha in ordem],
        "grupos": [base[id_sha]["grupo_atual"] for id_sha in ordem],
        "dobras": [base[id_sha]["outer_fold"] for id_sha in ordem],
        "chaves": ordem,
    }
    resultado = rmc.avaliar_modelo("linear_svc", corpus)
    predicoes = {
        id_sha: {
            "outer_fold": base[id_sha]["outer_fold"],
            "referencia_humana": base[id_sha]["referencia_humana_atual"],
            "previsto": previsto,
        }
        for id_sha, previsto in zip(ordem, resultado["_predicoes"])
    }
    return {"resultado": resultado, "predicoes": predicoes}


def comparar_baseline(atual: dict[str, Any]) -> dict[str, Any]:
    diffs = {
        chave: round(atual.get(chave, 0) - esperado, 6) if isinstance(esperado, float)
        else atual.get(chave, 0) - esperado
        for chave, esperado in BASELINE_HISTORICO.items()
    }
    return {"historico": BASELINE_HISTORICO, "atual": atual, "diferenca": diffs}


# --------------------------------------------------------------------------
# Persistencia
# --------------------------------------------------------------------------

def escrever_predicoes(caminho: Path, predicoes: dict[str, dict[str, Any]],
                       escores: dict[str, float]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(["id_sha256", "outer_fold", "referencia_humana",
                           "previsto", "confianca"])
        for id_sha in sorted(predicoes):
            p = predicoes[id_sha]
            escritor.writerow([id_sha, p["outer_fold"], p["referencia_humana"],
                               p["previsto"], round(escores.get(id_sha, 0.0), 6)])


def renderizar_markdown(resumo: dict[str, Any]) -> str:
    linhas = [
        "# Recongelamento online da base do ensemble",
        "",
        "> Relatorio sanitizado e read-only. Substitui o Gate 2A de recuperacao "
        "textual historica: usa o texto ONLINE atual da planilha (corrigido "
        "humanamente apos 04/08/2026) como fonte, preservando IDs, outer_folds, "
        "H, R e Y do congelamento anterior.",
        "",
        f"**Estado:** `{resumo['status']}`  ",
        f"**Gerado em:** {resumo.get('gerado_em', 'nao informado')}  ",
        f"**Spreadsheet ID:** `{resumo['spreadsheet_id']}`  ",
        f"**Aba:** `{resumo['aba']}`  ",
        f"**BASE_SHA (main):** `{resumo.get('base_main_sha') or 'nao informado'}`  ",
        f"**HEAD_SHA (branch):** `{resumo.get('workflow_head_sha') or 'nao informado'}`",
        "",
        "## Diagnostico de invariantes",
        "",
        "| Verificacao | Valor |",
        "|---|---:|",
    ]
    diag = resumo["diagnostico"]
    for chave in (
        "total_ids_particoes", "total_ids_alvo_congelado",
        "total_ids_particao_sem_alvo", "total_ids_alvo_sem_particao",
        "folds_particao", "folds_alvo_congelado",
        "total_dobra_historica_divergente",
        "total_ids_encontrados_no_online",
        "total_faltantes_no_online", "total_ids_duplicados_no_online",
        "total_grupos_atuais_distintos", "total_grupos_congelados_distintos",
        "total_grupos_ou_textos_alterados_em_relacao_ao_historico",
        "grupos_cruzando_dobras", "h_divergentes", "r_divergentes",
        "y_divergentes",
    ):
        linhas.append(f"| {chave.replace('_', ' ')} | {diag[chave]} |")
    linhas += [
        "",
        f"Bloqueios: {', '.join(diag['bloqueios']) if diag['bloqueios'] else 'nenhum'}.",
        "",
        "## Hashes",
        "",
        "| Hash | Anterior | Novo | Mudou |",
        "|---|---|---|---|",
    ]
    for nome, (antigo, novo) in resumo.get("hashes_comparados", {}).items():
        linhas.append(f"| {nome} | `{antigo}` | `{novo}` | {antigo != novo} |")
    if resumo.get("baseline_linear_svc"):
        linhas += [
            "",
            "## Baseline LinearSVC: historico x atual",
            "",
            "| Metrica | Historico | Atual | Diferenca |",
            "|---|---:|---:|---:|",
        ]
        comp = resumo["baseline_linear_svc"]
        for chave in comp["historico"]:
            linhas.append(
                f"| {chave} | {comp['historico'][chave]} | "
                f"{comp['atual'].get(chave)} | {comp['diferenca'].get(chave)} |"
            )
    linhas += [
        "",
        "## Garantias",
        "",
        "- Nenhuma escrita foi realizada na planilha.",
        "- As particoes canonicas (`docs/dados/particoes_canonicas_mapa.csv`) "
        "nao foram regeneradas; o StratifiedGroupKFold nao foi reexecutado.",
        "- Nenhum texto bruto ou ID de chamado foi publicado.",
        "",
    ]
    return "\n".join(linhas)


# --------------------------------------------------------------------------
# Orquestracao
# --------------------------------------------------------------------------

def executar(
    config_path: Path = CONFIG_PADRAO,
    credenciais: str | None = None,
    particoes_path: Path = PARTICOES_PADRAO,
    alvo_congelado_path: Path = ALVO_CONGELADO_PADRAO,
    base_main_sha: str | None = None,
    workflow_head_sha: str | None = None,
    registros_online: list[dict[str, str]] | None = None,
    total_esperado: int | None = TOTAL_ESPERADO,
    folds_esperados: list[int] | None = FOLDS_ESPERADOS_PADRAO,
) -> dict[str, Any]:
    particoes = carregar_particoes_preservadas(particoes_path)
    alvo_congelado = carregar_alvo_congelado(alvo_congelado_path)
    resumo_congelado_path = alvo_congelado_path.with_name("alvo_ensemble_resumo.json")
    hashes_antigos = carregar_hashes_congelamento_anterior(resumo_congelado_path)
    if registros_online is None:
        registros_online = ler_registros_online(config_path, credenciais)

    base_info = montar_base_atual(registros_online, particoes)
    diagnostico = montar_diagnostico(base_info, alvo_congelado, particoes,
                                     total_esperado=total_esperado,
                                     folds_esperados=folds_esperados)

    resumo: dict[str, Any] = {
        "schema_version": 1,
        "status": diagnostico["status"],
        "gerado_em": agora_bahia(),
        # `ler_registros_online` ja garante spreadsheet_id == SPREADSHEET_ID_CANONICO
        # antes de devolver qualquer registro; reafirmado aqui sem nova
        # resolucao de credenciais/variavel de ambiente.
        "spreadsheet_id": SPREADSHEET_ID_CANONICO,
        "aba": ABA_CANONICA,
        "base_main_sha": base_main_sha,
        "workflow_head_sha": workflow_head_sha or os.getenv("GITHUB_SHA"),
        "diagnostico": diagnostico,
        # Valores antigos lidos diretamente do artefato congelado; nao
        # recalculados, porque dependem de um texto que a planilha online
        # nao guarda mais depois da correcao humana.
        "hash_corpus_antigo": hashes_antigos.get("hash_corpus"),
        "hash_historico_ensemble_antigo": hashes_antigos.get("hash_historico_ensemble"),
        "hash_alvo_ensemble_antigo": hashes_antigos.get("hash_alvo_ensemble"),
        "classes_sha256_antigo": hashes_antigos.get("classes_sha256"),
        # `partition_manifest_sha256` congelado anteriormente e sempre o hash
        # fisico do manifesto de ORIGEM (docs/dados/particoes_canonicas_mapa.csv);
        # nao existia, antes desta correcao, um manifesto online separado.
        "partition_manifest_origem_sha256_antigo": hashes_antigos.get("partition_manifest_sha256"),
    }

    if diagnostico["status"] != "apto_para_baseline":
        resumo["hash_corpus_novo"] = None
        resumo["hashes_comparados"] = {}
        resumo["baseline_linear_svc"] = None
        resumo["partition_manifest_origem_sha256_novo"] = None
        resumo["partition_manifest_online_sha256"] = None
        resumo["fold_assignment_sha256"] = None
        resumo["_registros"] = []
        resumo["_predicoes"] = {}
        resumo["_escores"] = {}
        resumo["_particoes_online_bytes"] = None
        return resumo

    registros = montar_registros_recongelados(base_info["base"], particoes)
    hash_corpus_novo = calcular_hash_corpus(registros)

    hash_hist_novo = cae.hash_historico(registros)
    classes_payload, classes_sha_novo = cae.montar_classes(
        registros, esperado=len({r["referencia_humana"] for r in registros})
    )

    # Manifesto de ORIGEM: o arquivo historico intocado, evidencia de onde os
    # folds vieram. Manifesto ONLINE: novo artefato com o grupo ATUAL e a
    # mesma dobra preservada. Os dois sao hasheados separadamente; nenhum dos
    # dois e forcado a bater com o outro.
    partition_manifest_origem_sha256 = cae.sha256_bytes(particoes_path.read_bytes())
    particoes_online_bytes = montar_particoes_online_csv_bytes(registros)
    partition_manifest_online_sha256 = cae.sha256_bytes(particoes_online_bytes)

    # A atribuicao ID -> fold precisa ser a MESMA nas duas fontes (particoes
    # preservadas x registros recongelados); e o que a Correcao 3 ja garante
    # antes de chegar aqui. O hash abaixo torna essa invariancia auditavel
    # sem depender de reler os dois arquivos byte a byte.
    fold_assignment_particoes = calcular_fold_assignment_sha256(
        [(id_sha, p["outer_fold"]) for id_sha, p in particoes.items()]
    )
    fold_assignment_registros = calcular_fold_assignment_sha256(
        [(r["id_sha256"], r["outer_fold"]) for r in registros]
    )
    if fold_assignment_particoes != fold_assignment_registros:
        raise RuntimeError(
            "fold_assignment_sha256 divergente entre particoes preservadas e "
            "registros recongelados; a atribuicao ID->fold nao deveria mudar."
        )
    fold_assignment_sha256 = fold_assignment_registros

    treino = treinar_linear_svc_do_zero(base_info["base"], registros)
    resultado_modelo = treino["resultado"]
    predicoes = treino["predicoes"]
    escores = dict(zip(
        [r["id_sha256"] for r in registros], resultado_modelo["_escores"]
    ))

    baseline = cae.reproduzir_baseline(registros, predicoes, validar_esperado=False)
    baseline_atual = baseline["baseline"]
    baseline_atual["acuracia"] = resultado_modelo["acuracia"]
    baseline_atual["macro_f1"] = resultado_modelo["macro_f1"]
    baseline_atual["balanced_accuracy"] = resultado_modelo["balanced_accuracy"]
    baseline_atual["grupos_vazados_para_o_treino"] = resultado_modelo[
        "grupos_vazados_para_o_treino"
    ]

    alvo_obj = {
        "metadata": {
            "schema_version": 1,
            "hash_corpus": hash_corpus_novo,
            "hash_historico_ensemble": hash_hist_novo,
            # Aponta para o manifesto ONLINE (grupo atual + fold preservado),
            # nao para o arquivo historico: e essa a particao logica desta
            # rodada. A proveniencia do arquivo historico fica preservada, com
            # nome inequivoco, no campo abaixo.
            "partition_manifest_sha256": partition_manifest_online_sha256,
            "partition_manifest_origem_sha256": partition_manifest_origem_sha256,
            "fold_assignment_sha256": fold_assignment_sha256,
            "classes_sha256": classes_sha_novo,
            "total_records": len(registros),
        },
        "records": registros,
    }
    alvo_bytes = cae.canonical_bytes(alvo_obj)
    hash_alvo_novo = cae.sha256_bytes(alvo_bytes)

    resumo.update({
        "hash_corpus_novo": hash_corpus_novo,
        "hashes_comparados": {
            "hash_corpus": (resumo["hash_corpus_antigo"], hash_corpus_novo),
            "hash_alvo_ensemble": (resumo["hash_alvo_ensemble_antigo"], hash_alvo_novo),
            "hash_historico_ensemble": (resumo["hash_historico_ensemble_antigo"], hash_hist_novo),
            "classes_sha256": (resumo["classes_sha256_antigo"], classes_sha_novo),
            "partition_manifest_origem_sha256": (
                resumo["partition_manifest_origem_sha256_antigo"],
                partition_manifest_origem_sha256,
            ),
            "partition_manifest_online_sha256": (None, partition_manifest_online_sha256),
            "fold_assignment_sha256": (None, fold_assignment_sha256),
        },
        "hash_alvo_ensemble_novo": hash_alvo_novo,
        "hash_historico_ensemble_novo": hash_hist_novo,
        "classes_sha256_novo": classes_sha_novo,
        "partition_manifest_origem_sha256_novo": partition_manifest_origem_sha256,
        "partition_manifest_online_sha256": partition_manifest_online_sha256,
        "fold_assignment_sha256": fold_assignment_sha256,
        "baseline_linear_svc": comparar_baseline(baseline_atual),
        "K_D_R_por_dobra": baseline["por_dobra"],
        "total_registros_recongelados": len(registros),
        "total_grupos_recongelados": len({r["grupo_sha256"] for r in registros}),
        "total_classes_recongeladas": len({r["referencia_humana"] for r in registros}),
        "_registros": registros,
        "_alvo_bytes": alvo_bytes,
        "_particoes_online_bytes": particoes_online_bytes,
        "_predicoes": predicoes,
        "_escores": escores,
    })
    return resumo


def gravar(resumo: dict[str, Any], saida_dir: Path, alvo_path: Path,
          particoes_online_path: Path, resumo_path: Path, predicoes_path: Path,
          relatorio_path: Path) -> None:
    saida_dir.mkdir(parents=True, exist_ok=True)
    publicavel = {k: v for k, v in resumo.items() if not k.startswith("_")}
    resumo_path.parent.mkdir(parents=True, exist_ok=True)
    resumo_path.write_text(
        json.dumps(publicavel, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if resumo["status"] == "apto_para_baseline":
        alvo_path.parent.mkdir(parents=True, exist_ok=True)
        alvo_path.write_bytes(resumo["_alvo_bytes"])
        particoes_online_path.parent.mkdir(parents=True, exist_ok=True)
        particoes_online_path.write_bytes(resumo["_particoes_online_bytes"])
        escrever_predicoes(predicoes_path, resumo["_predicoes"], resumo["_escores"])
    relatorio_path.parent.mkdir(parents=True, exist_ok=True)
    relatorio_path.write_text(renderizar_markdown(resumo), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--particoes", type=Path, default=PARTICOES_PADRAO)
    p.add_argument("--alvo-congelado", type=Path, default=ALVO_CONGELADO_PADRAO)
    p.add_argument("--saida-dir", type=Path, default=SAIDA_DIR_PADRAO)
    p.add_argument("--alvo-online", type=Path, default=ALVO_ONLINE_PADRAO)
    p.add_argument("--particoes-online", type=Path, default=PARTICOES_ONLINE_PADRAO)
    p.add_argument("--resumo", type=Path, default=RESUMO_ONLINE_PADRAO)
    p.add_argument("--predicoes", type=Path, default=PREDICOES_ONLINE_PADRAO)
    p.add_argument("--relatorio", type=Path, default=RELATORIO_PADRAO)
    p.add_argument("--base-main-sha", default=None)
    p.add_argument("--workflow-head-sha", default=None)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.particoes.exists():
        print(f"Mapa de particoes nao encontrado em {args.particoes}.", file=sys.stderr)
        return 2
    if not args.alvo_congelado.exists():
        print(f"Alvo congelado anterior nao encontrado em {args.alvo_congelado}.",
              file=sys.stderr)
        return 2

    resumo = executar(
        config_path=args.config,
        credenciais=args.credenciais,
        particoes_path=args.particoes,
        alvo_congelado_path=args.alvo_congelado,
        base_main_sha=args.base_main_sha,
        workflow_head_sha=args.workflow_head_sha,
    )
    gravar(resumo, args.saida_dir, args.alvo_online, args.particoes_online,
          args.resumo, args.predicoes, args.relatorio)
    publicavel = {k: v for k, v in resumo.items() if not k.startswith("_")}
    print(json.dumps(publicavel, ensure_ascii=False, indent=2))
    if resumo["status"] != "apto_para_baseline":
        print("Rodada BLOQUEADA: invariantes de proveniencia nao satisfeitas.",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
