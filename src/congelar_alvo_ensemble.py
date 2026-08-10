#!/usr/bin/env python3
"""Congela o alvo binario do ensemble sobre a rodada canonica.

Ferramenta read-only sobre a planilha: le a aba principal, reaplica a
referencia humana revisada, junta grupos/particoes congelados e usa apenas as
predicoes OOF ja existentes do LinearSVC para reproduzir o baseline. Nao treina
modelos, nao escreve na planilha e nao publica texto ou ID bruto de chamado.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import construir_grupos_textuais as cgt  # noqa: E402
import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "docs" / "dados"
ENSEMBLE_DIR = DADOS / "ensemble"
CONFIG_PADRAO = RAIZ / "config_experimento.json"
PARTICOES_PADRAO = DADOS / "particoes_canonicas_mapa.csv"
GRUPOS_PADRAO = DADOS / "grupos_textuais_mapa.csv"
PREDICOES_PADRAO = DADOS / "retreino_canonico_predicoes.csv"
RODADA_PADRAO = DADOS / "rodada_canonica.json"
CLASSES_PADRAO = ENSEMBLE_DIR / "classes_ensemble.json"
ALVO_PADRAO = ENSEMBLE_DIR / "alvo_ensemble.json"
RESUMO_PADRAO = ENSEMBLE_DIR / "alvo_ensemble_resumo.json"
RELATORIO_PADRAO = RAIZ / "docs" / "CONGELAMENTO_ALVO_ENSEMBLE.md"

SPREADSHEET_ID_CANONICO = "1lohPUQOgxzt_DMxnNLKMxnieZq1sVmh4uwBLbbgvfiQ"
HASH_CORPUS_ESPERADO = (
    "1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a"
)
TOTAL_ESPERADO = 13972
GRUPOS_ESPERADOS = 9734
DOBRAS_ESPERADAS = 5
CLASSES_ESPERADAS = 41
SEMENTE_ESPERADA = 42
BASELINE_ESPERADO = {
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

CAMPOS_PROIBIDOS = {
    "id", "id_chamado", "titulo", "descricao", "descricao_glpi",
    "titulo_osm", "descricao_osm", "ordem_servico", "localizacao", "pessoa",
    "executor", "criticidade", "conferencia_glpi", "conferencia_ia",
    "conferencia_ia_2", "categoria_manual",
}


def canonical_bytes(objeto: Any) -> bytes:
    return json.dumps(
        objeto, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_bytes(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def sha256_json(objeto: Any) -> str:
    return sha256_bytes(canonical_bytes(objeto))


def carregar_particoes(caminho: Path) -> dict[str, dict[str, Any]]:
    with caminho.open("r", encoding="utf-8", newline="") as f:
        out: dict[str, dict[str, Any]] = {}
        for linha in csv.DictReader(f):
            id_sha = linha.get("id_sha256", "")
            if not id_sha:
                continue
            out[id_sha] = {
                "grupo_sha256": linha.get("grupo_sha256", ""),
                "outer_fold": int(linha["dobra"]),
            }
        return out


def carregar_grupos(caminho: Path) -> dict[str, str]:
    with caminho.open("r", encoding="utf-8", newline="") as f:
        return {
            linha["id_sha256"]: linha["grupo_sha256"]
            for linha in csv.DictReader(f)
            if linha.get("id_sha256")
        }


def _hash_grupo_atual(registro: dict[str, str]) -> str:
    normalizados = [cgt.normalizar_texto(registro.get(c, ""))
                    for c in cgt.CAMPOS_TEXTUAIS]
    return cgt.hash_grupo(normalizados)


def montar_registros_alvo(
    registros_planilha: list[dict[str, str]],
    particoes: dict[str, dict[str, Any]],
    grupos: dict[str, str],
) -> tuple[list[dict[str, Any]], str, int]:
    alvo: list[dict[str, Any]] = []
    itens_hash_corpus: list[list[str]] = []
    textos_alterados = 0

    for registro in registros_planilha:
        id_bruto = registro.get("id", "")
        if not id_bruto:
            continue
        id_sha = hashlib.sha256(id_bruto.encode("utf-8")).hexdigest()
        if id_sha not in particoes:
            continue
        if id_sha not in grupos:
            raise RuntimeError(f"Grupo congelado ausente para id_sha256={id_sha}")
        grupo_congelado = grupos[id_sha]

        referencia = cgt.referencia_humana(registro)
        if not referencia:
            raise RuntimeError(f"Referencia humana ausente para id_sha256={id_sha}")
        historica = registro.get("categoria_historica", "")
        grupo_atual = _hash_grupo_atual(registro)
        if grupo_atual != grupo_congelado:
            textos_alterados += 1
        itens_hash_corpus.append([id_sha, grupo_atual, referencia])
        alvo.append({
            "id_sha256": id_sha,
            "grupo_sha256": grupo_congelado,
            "outer_fold": particoes[id_sha]["outer_fold"],
            "categoria_historica": historica,
            "referencia_humana": referencia,
            "historico_no_espaco_de_classes": False,
            "alvo_inadequacao": int(historica != referencia),
        })

    classes = sorted({r["referencia_humana"] for r in alvo})
    for registro in alvo:
        registro["historico_no_espaco_de_classes"] = (
            registro["categoria_historica"] in classes
        )
    alvo.sort(key=lambda r: r["id_sha256"])
    hash_corpus = sha256_json(sorted(itens_hash_corpus))
    return alvo, hash_corpus, textos_alterados


def validar_bloqueios_basicos(
    registros: list[dict[str, Any]],
    hash_corpus: str,
    rodada: dict[str, Any],
) -> None:
    classes = sorted({r["referencia_humana"] for r in registros})
    if len(registros) != TOTAL_ESPERADO:
        raise RuntimeError(f"Total divergente: {len(registros)} != {TOTAL_ESPERADO}")
    if len({r["grupo_sha256"] for r in registros}) != GRUPOS_ESPERADOS:
        raise RuntimeError("Total de grupos textuais divergente.")
    if len({r["outer_fold"] for r in registros}) != DOBRAS_ESPERADAS:
        raise RuntimeError("Total de dobras divergente.")
    if len(classes) != CLASSES_ESPERADAS:
        raise RuntimeError("Total de classes divergente.")
    if hash_corpus != HASH_CORPUS_ESPERADO:
        raise RuntimeError(f"hash_corpus divergente: {hash_corpus}")
    if rodada.get("hash_corpus") != HASH_CORPUS_ESPERADO:
        raise RuntimeError("Manifesto da rodada canonica tem hash_corpus divergente.")
    if int(rodada.get("semente", -1)) != SEMENTE_ESPERADA:
        raise RuntimeError("Semente da rodada canonica divergente.")
    if set(registros[0]) != set(SCHEMA_CAMPOS):
        raise RuntimeError("Schema do manifesto do alvo divergente.")
    if any(set(r) != set(SCHEMA_CAMPOS) for r in registros):
        raise RuntimeError("Registro com schema divergente no manifesto.")
    if len({r["id_sha256"] for r in registros}) != len(registros):
        raise RuntimeError("IDs SHA-256 duplicados no alvo.")
    for campo in CAMPOS_PROIBIDOS:
        if campo in registros[0]:
            raise RuntimeError(f"Campo proibido presente: {campo}")


def montar_classes(registros: list[dict[str, Any]],
                   esperado: int = CLASSES_ESPERADAS) -> tuple[dict[str, Any], str]:
    classes = sorted({r["referencia_humana"] for r in registros})
    if len(classes) != esperado:
        raise RuntimeError("Total de classes divergente.")
    classes_sha = sha256_bytes(json.dumps(
        classes, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8"))
    payload = {
        "schema_version": 1,
        "n_classes": len(classes),
        "ordering_rule": "python_sorted_unicode",
        "classes": [{"index": i, "label": label} for i, label in enumerate(classes)],
        "classes_sha256": classes_sha,
    }
    return payload, classes_sha


def hash_historico(registros: list[dict[str, Any]]) -> str:
    payload = [
        {"id_sha256": r["id_sha256"], "categoria_historica": r["categoria_historica"]}
        for r in sorted(registros, key=lambda x: x["id_sha256"])
    ]
    return sha256_json(payload)


def carregar_predicoes_linear_svc(caminho: Path) -> dict[str, dict[str, Any]]:
    predicoes: dict[str, dict[str, Any]] = {}
    with caminho.open("r", encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            if linha.get("modelo") != "linear_svc":
                continue
            id_sha = linha["id_sha256"]
            if id_sha in predicoes:
                raise RuntimeError(f"Predicao LinearSVC duplicada para {id_sha}")
            predicoes[id_sha] = {
                "outer_fold": int(linha["dobra"]),
                "referencia_humana": linha["referencia_humana"],
                "previsto": linha["previsto"],
            }
    return predicoes


def reproduzir_baseline(
    registros: list[dict[str, Any]],
    predicoes: dict[str, dict[str, Any]],
    validar_esperado: bool = True,
) -> dict[str, Any]:
    por_dobra: dict[int, dict[str, int]] = defaultdict(lambda: {
        "K_f": 0,
        "D_f": 0,
        "R_f": 0,
        "inadequacoes_dentro_da_fila_natural": 0,
        "total": 0,
        "Y1": 0,
        "Y0": 0,
        "H_fora_de_C": 0,
        "H_dentro_de_C": 0,
    })
    totais = Counter()
    todos_h_fora_na_fila = True

    if set(predicoes) != {r["id_sha256"] for r in registros}:
        faltantes = {r["id_sha256"] for r in registros} - set(predicoes)
        extras = set(predicoes) - {r["id_sha256"] for r in registros}
        raise RuntimeError(
            f"Join LinearSVC incompleto: faltantes={len(faltantes)}, extras={len(extras)}"
        )

    for r in registros:
        p = predicoes[r["id_sha256"]]
        if p["outer_fold"] != r["outer_fold"]:
            raise RuntimeError(f"Dobra divergente para {r['id_sha256']}")
        if p["referencia_humana"] != r["referencia_humana"]:
            raise RuntimeError(f"Referencia divergente para {r['id_sha256']}")
        h = r["categoria_historica"]
        ref = r["referencia_humana"]
        previsto = p["previsto"]
        fila = previsto != h
        fold = int(r["outer_fold"])
        alvo = int(r["alvo_inadequacao"])
        por_dobra[fold]["total"] += 1
        por_dobra[fold]["Y1"] += alvo
        por_dobra[fold]["Y0"] += 1 - alvo
        if r["historico_no_espaco_de_classes"]:
            por_dobra[fold]["H_dentro_de_C"] += 1
        else:
            por_dobra[fold]["H_fora_de_C"] += 1
            por_dobra[fold]["D_f"] += 1
            todos_h_fora_na_fila = todos_h_fora_na_fila and fila
        if fila:
            totais["alertas_naturais"] += 1
            por_dobra[fold]["K_f"] += 1
            if alvo:
                totais["inadequacoes_na_fila"] += 1
                por_dobra[fold]["inadequacoes_dentro_da_fila_natural"] += 1
            if previsto == ref:
                totais["correcoes_top1"] += 1
            elif h == ref:
                totais["prejudicados"] += 1
            else:
                totais["neutros"] += 1

    for fold, dados in por_dobra.items():
        dados["R_f"] = dados["K_f"] - dados["D_f"]
        if dados["D_f"] > dados["K_f"]:
            raise RuntimeError(f"D_f > K_f na dobra {fold}")
        dados["precisao_fila_natural"] = round(
            dados["inadequacoes_dentro_da_fila_natural"] / dados["K_f"], 4
        ) if dados["K_f"] else 0.0

    resultado = dict(totais)
    resultado["precisao_fila_natural"] = round(
        resultado["inadequacoes_na_fila"] / resultado["alertas_naturais"], 4
    )
    if validar_esperado:
        for chave, esperado in BASELINE_ESPERADO.items():
            if resultado.get(chave) != esperado:
                raise RuntimeError(
                    f"Baseline LinearSVC divergente em {chave}: "
                    f"{resultado.get(chave)} != {esperado}"
                )
    return {
        "baseline": resultado,
        "por_dobra": {str(k): por_dobra[k] for k in sorted(por_dobra)},
        "todos_h_fora_de_c_na_fila_natural": todos_h_fora_na_fila,
    }


def frequencias(registros: list[dict[str, Any]], campo: str) -> dict[str, int]:
    return dict(sorted(Counter(r[campo] for r in registros).items()))


def inadequacoes_por(registros: list[dict[str, Any]], campo: str) -> dict[str, int]:
    c = Counter(r[campo] for r in registros if r["alvo_inadequacao"])
    return dict(sorted(c.items()))


def montar_resumo(
    registros: list[dict[str, Any]],
    hash_corpus: str,
    hash_hist: str,
    hash_alvo: str,
    classes_sha: str,
    partition_sha: str,
    baseline: dict[str, Any],
    textos_alterados: int,
) -> dict[str, Any]:
    total_y1 = sum(r["alvo_inadequacao"] for r in registros)
    total_y0 = len(registros) - total_y1
    h_dentro = sum(1 for r in registros if r["historico_no_espaco_de_classes"])
    h_fora = len(registros) - h_dentro
    fora_categorias = sorted({
        r["categoria_historica"] for r in registros
        if not r["historico_no_espaco_de_classes"]
    })
    por_dobra = {}
    for fold in sorted({r["outer_fold"] for r in registros}):
        subset = [r for r in registros if r["outer_fold"] == fold]
        por_dobra[str(fold)] = {
            "total": len(subset),
            "Y1": sum(r["alvo_inadequacao"] for r in subset),
            "Y0": sum(1 - r["alvo_inadequacao"] for r in subset),
            "H_fora_de_C": sum(not r["historico_no_espaco_de_classes"] for r in subset),
            "H_dentro_de_C": sum(r["historico_no_espaco_de_classes"] for r in subset),
        }
    y1_dentro = sum(
        r["alvo_inadequacao"] for r in registros
        if r["historico_no_espaco_de_classes"]
    )
    y1_fora = sum(
        r["alvo_inadequacao"] for r in registros
        if not r["historico_no_espaco_de_classes"]
    )
    return {
        "schema_version": 1,
        "gerado_em": agora_bahia(),
        "hash_corpus": hash_corpus,
        "hash_historico_ensemble": hash_hist,
        "hash_alvo_ensemble": hash_alvo,
        "sha256_fisico_alvo_ensemble_json": hash_alvo,
        "classes_sha256": classes_sha,
        "partition_manifest_sha256": partition_sha,
        "commit_produtor": os.getenv("GITHUB_SHA") or None,
        "total_registros": len(registros),
        "total_grupos": len({r["grupo_sha256"] for r in registros}),
        "total_dobras": len({r["outer_fold"] for r in registros}),
        "total_Y1": total_y1,
        "total_Y0": total_y0,
        "prevalencia_Y1": round(total_y1 / len(registros), 6),
        "contagens_por_dobra": por_dobra,
        "H_dentro_de_C": h_dentro,
        "H_fora_de_C": h_fora,
        "H_fora_de_C_por_dobra": {
            fold: dados["H_fora_de_C"] for fold, dados in por_dobra.items()
        },
        "categorias_historicas_fora_de_C": fora_categorias,
        "frequencia_categorias_historicas": frequencias(registros, "categoria_historica"),
        "frequencia_categorias_referencia": frequencias(registros, "referencia_humana"),
        "inadequacoes_por_categoria_historica": inadequacoes_por(
            registros, "categoria_historica"
        ),
        "inadequacoes_por_categoria_referencia": inadequacoes_por(
            registros, "referencia_humana"
        ),
        "prevalencia_Y1_H_dentro_de_C": round(y1_dentro / h_dentro, 6),
        "prevalencia_Y1_H_fora_de_C": round(y1_fora / h_fora, 6) if h_fora else 0.0,
        "baseline_linear_svc": baseline["baseline"],
        "K_D_R_por_dobra": baseline["por_dobra"],
        "todos_H_fora_de_C_na_fila_natural_linear_svc":
            baseline["todos_h_fora_de_c_na_fila_natural"],
        "linhas_com_texto_alterado_apos_o_congelamento": textos_alterados,
        "modelos_executados": "nenhum",
    }


def renderizar_markdown(resumo: dict[str, Any]) -> str:
    linhas = [
        "# Congelamento do alvo do ensemble",
        "",
        "> Relatorio sanitizado e read-only. Nao contem IDs brutos, titulos, descricoes ou texto de chamados.",
        "",
        f"- hash_corpus: `{resumo['hash_corpus']}`",
        f"- hash_historico_ensemble: `{resumo['hash_historico_ensemble']}`",
        f"- hash_alvo_ensemble: `{resumo['hash_alvo_ensemble']}`",
        f"- SHA-256 fisico de alvo_ensemble.json: `{resumo['sha256_fisico_alvo_ensemble_json']}`",
        f"- classes_sha256: `{resumo['classes_sha256']}`",
        f"- partition_manifest_sha256: `{resumo['partition_manifest_sha256']}`",
        f"- commit produtor: `{resumo['commit_produtor'] or 'nao disponivel'}`",
        f"- registros: {resumo['total_registros']}",
        f"- grupos: {resumo['total_grupos']}",
        f"- dobras: {resumo['total_dobras']}",
        f"- Y=1: {resumo['total_Y1']}",
        f"- Y=0: {resumo['total_Y0']}",
        f"- H dentro de C: {resumo['H_dentro_de_C']}",
        f"- H fora de C: {resumo['H_fora_de_C']}",
        "",
        "## Baseline LinearSVC",
        "",
    ]
    for k, v in resumo["baseline_linear_svc"].items():
        linhas.append(f"- {k}: {v}")
    linhas += [
        "",
        "## K, D e R por dobra",
        "",
        "| Dobra | K_f | D_f | R_f | Inadequacoes na fila | Precisao |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for fold, dados in resumo["K_D_R_por_dobra"].items():
        linhas.append(
            f"| {fold} | {dados['K_f']} | {dados['D_f']} | {dados['R_f']} | "
            f"{dados['inadequacoes_dentro_da_fila_natural']} | "
            f"{dados['precisao_fila_natural']} |"
        )
    linhas += [
        "",
        "## Categorias historicas fora de C",
        "",
    ]
    linhas += [f"- {c}" for c in resumo["categorias_historicas_fora_de_C"]]
    linhas += [
        "",
        "## Garantias",
        "",
        "- Nenhum modelo foi treinado ou executado.",
        "- A planilha foi lida em modo read-only.",
        "- O arquivo bruto de cache e credenciais nao sao artefatos deste relatorio.",
        "",
    ]
    return "\n".join(linhas)


def construir_artifacts(
    registros_planilha: list[dict[str, str]],
    particoes_path: Path = PARTICOES_PADRAO,
    grupos_path: Path = GRUPOS_PADRAO,
    predicoes_path: Path = PREDICOES_PADRAO,
    rodada_path: Path = RODADA_PADRAO,
) -> dict[str, Any]:
    particoes = carregar_particoes(particoes_path)
    grupos = carregar_grupos(grupos_path)
    rodada = json.loads(rodada_path.read_text(encoding="utf-8"))
    registros, hash_corpus, textos_alterados = montar_registros_alvo(
        registros_planilha, particoes, grupos
    )
    validar_bloqueios_basicos(registros, hash_corpus, rodada)
    classes_payload, classes_sha = montar_classes(registros)
    hash_hist = hash_historico(registros)
    partition_sha = sha256_bytes(particoes_path.read_bytes())
    alvo_obj = {
        "metadata": {
            "schema_version": 1,
            "hash_corpus": hash_corpus,
            "hash_historico_ensemble": hash_hist,
            "partition_manifest_sha256": partition_sha,
            "classes_sha256": classes_sha,
            "total_records": len(registros),
        },
        "records": registros,
    }
    alvo_bytes = canonical_bytes(alvo_obj)
    hash_alvo = sha256_bytes(alvo_bytes)
    baseline = reproduzir_baseline(
        registros, carregar_predicoes_linear_svc(predicoes_path)
    )
    resumo = montar_resumo(
        registros, hash_corpus, hash_hist, hash_alvo, classes_sha,
        partition_sha, baseline, textos_alterados
    )
    return {
        "classes": classes_payload,
        "classes_bytes": canonical_bytes(classes_payload),
        "alvo": alvo_obj,
        "alvo_bytes": alvo_bytes,
        "resumo": resumo,
        "resumo_bytes": canonical_bytes(resumo),
        "relatorio": renderizar_markdown(resumo).encode("utf-8"),
        "hashes": {
            "hash_corpus": hash_corpus,
            "hash_historico_ensemble": hash_hist,
            "hash_alvo_ensemble": hash_alvo,
            "classes_sha256": classes_sha,
            "partition_manifest_sha256": partition_sha,
            "sha256_fisico_do_arquivo": hash_alvo,
        },
        "contagens": {
            "total_Y1": resumo["total_Y1"],
            "total_Y0": resumo["total_Y0"],
            "H_dentro_de_C": resumo["H_dentro_de_C"],
            "H_fora_de_C": resumo["H_fora_de_C"],
            "contagens_por_dobra": resumo["contagens_por_dobra"],
            "K_D_R_por_dobra": resumo["K_D_R_por_dobra"],
        },
    }


def verificar_determinismo(a: dict[str, Any], b: dict[str, Any]) -> None:
    for chave in ("classes_bytes", "alvo_bytes"):
        if a[chave] != b[chave]:
            raise RuntimeError(f"Determinismo falhou em {chave}")
    for chave in ("hashes", "contagens"):
        if a[chave] != b[chave]:
            raise RuntimeError(f"Determinismo falhou em {chave}")


def gravar_artifacts(artifacts: dict[str, Any], args: argparse.Namespace) -> None:
    args.classes.parent.mkdir(parents=True, exist_ok=True)
    args.alvo.parent.mkdir(parents=True, exist_ok=True)
    args.resumo.parent.mkdir(parents=True, exist_ok=True)
    args.relatorio.parent.mkdir(parents=True, exist_ok=True)
    args.classes.write_bytes(artifacts["classes_bytes"])
    args.alvo.write_bytes(artifacts["alvo_bytes"])
    args.resumo.write_bytes(artifacts["resumo_bytes"])
    args.relatorio.write_bytes(artifacts["relatorio"])


def ler_registros_da_planilha(config_path: Path, credenciais: str | None = None
                              ) -> list[dict[str, str]]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    spreadsheet_id = pl.id_planilha(config)
    if spreadsheet_id != SPREADSHEET_ID_CANONICO:
        raise RuntimeError("SPREADSHEET_ID canonico divergente.")
    sh = pl.abrir_planilha(spreadsheet_id, credenciais)
    return cgt.ler_registros(sh, config)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--particoes", type=Path, default=PARTICOES_PADRAO)
    p.add_argument("--grupos", type=Path, default=GRUPOS_PADRAO)
    p.add_argument("--predicoes", type=Path, default=PREDICOES_PADRAO)
    p.add_argument("--rodada", type=Path, default=RODADA_PADRAO)
    p.add_argument("--classes", type=Path, default=CLASSES_PADRAO)
    p.add_argument("--alvo", type=Path, default=ALVO_PADRAO)
    p.add_argument("--resumo", type=Path, default=RESUMO_PADRAO)
    p.add_argument("--relatorio", type=Path, default=RELATORIO_PADRAO)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    registros_a = ler_registros_da_planilha(args.config, args.credenciais)
    primeira = construir_artifacts(
        registros_a, args.particoes, args.grupos, args.predicoes, args.rodada
    )
    registros_b = ler_registros_da_planilha(args.config, args.credenciais)
    segunda = construir_artifacts(
        registros_b, args.particoes, args.grupos, args.predicoes, args.rodada
    )
    verificar_determinismo(primeira, segunda)
    gravar_artifacts(primeira, args)
    print(json.dumps({
        "status": "concluido",
        **primeira["hashes"],
        **primeira["contagens"],
        "baseline_reproduzido": BASELINE_ESPERADO,
        "modelos_executados": "nenhum",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
