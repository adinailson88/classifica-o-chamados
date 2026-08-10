#!/usr/bin/env python3
"""Gate 2A: audita se uma fonte textual historica reproduz os grupo_sha256
congelados em docs/dados/particoes_canonicas_mapa.csv.

Ferramenta estritamente READ-ONLY e efemera, usada apenas para provar (ou
refutar) a proveniencia textual de uma fonte candidata antes de qualquer
execucao pesada da Fase 2 do experimento de ensemble. Nao escreve na
planilha, nao versiona texto bruto e nao altera nenhum artefato canonico do
repositorio. A saida e um JSON sanitizado, com apenas hashes e contagens.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from conferencia_derivada import normalizar_id  # noqa: E402
from construir_grupos_textuais import (  # noqa: E402
    CAMPOS_TEXTUAIS,
    hash_grupo,
    normalizar_texto,
)
import planilha as pl  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
PARTICOES_PADRAO = RAIZ / "docs" / "dados" / "particoes_canonicas_mapa.csv"
SAIDA_PADRAO = RAIZ / "dados" / "gate2a_resultado.json"

COLUNAS_ALVO: dict[str, tuple[str, ...]] = {
    "id": ("ID Chamado", "ID"),
    "titulo": ("TÍTULO", "TITULO"),
    "descricao_glpi": ("DESCRIÇÃO GLPI", "DESCRICAO GLPI"),
    "titulo_osm": ("TÍTULO O.S.M.", "TITULO O.S.M."),
    "descricao_osm": ("DESCRIÇÃO O.S.M.", "DESCRICAO O.S.M."),
}


def carregar_particoes_canonicas(caminho: Path) -> dict[str, str]:
    """Le apenas id_sha256 -> grupo_sha256 do mapa canonico (autoritativo)."""
    with caminho.open("r", encoding="utf-8", newline="") as f:
        out: dict[str, str] = {}
        for linha in csv.DictReader(f):
            id_sha = linha.get("id_sha256", "")
            if not id_sha:
                continue
            out[id_sha] = linha.get("grupo_sha256", "")
        return out


def localizar_colunas(cabecalho: list[Any]) -> dict[str, int]:
    """Localiza as cinco colunas necessarias pelo cabecalho, nunca por posicao fixa."""
    indices: dict[str, int] = {}
    faltantes: list[str] = []
    for campo, nomes in COLUNAS_ALVO.items():
        idx = pl.localizar_coluna(cabecalho, nomes, 0)
        if not idx:
            faltantes.append(campo)
            continue
        indices[campo] = idx
    if faltantes:
        raise RuntimeError(f"Colunas ausentes na fonte historica: {sorted(faltantes)}")
    return indices


def ler_registros_fonte(sh, aba: str) -> list[dict[str, str]]:
    """Le a aba da fonte candidata e devolve apenas os cinco campos necessarios."""
    ws = sh.worksheet(aba)
    bloco = pl.ler_valores(ws, "A:Z")
    if not bloco:
        return []
    indices = localizar_colunas(bloco[0])

    def cel(linha: list[Any], c1: int) -> str:
        i = c1 - 1
        return str(linha[i] or "").strip() if len(linha) > i else ""

    registros: list[dict[str, str]] = []
    for linha in bloco[1:]:
        if not any(str(v or "").strip() for v in linha):
            continue
        registros.append({
            "id": normalizar_id(cel(linha, indices["id"])),
            "titulo": cel(linha, indices["titulo"]),
            "descricao_glpi": cel(linha, indices["descricao_glpi"]),
            "titulo_osm": cel(linha, indices["titulo_osm"]),
            "descricao_osm": cel(linha, indices["descricao_osm"]),
        })
    return registros


def auditar(registros: list[dict[str, str]], particoes: dict[str, str]) -> dict[str, Any]:
    """Compara os grupos reconstruidos da fonte candidata contra o mapa canonico.

    Duplicatas de id_sha256 na fonte so contam como identidade valida se os
    quatro campos normalizados produzirem o mesmo grupo em todas as
    ocorrencias; caso contrario a linha e ambigua e nunca e escolhida
    arbitrariamente.
    """
    total_nonempty_rows = len(registros)

    grupos_por_id: dict[str, list[str]] = defaultdict(list)
    for r in registros:
        id_norm = r.get("id", "")
        if not id_norm:
            continue
        id_sha = hashlib.sha256(id_norm.encode("utf-8")).hexdigest()
        normalizados = [normalizar_texto(r.get(c, "")) for c in CAMPOS_TEXTUAIS]
        grupos_por_id[id_sha].append(hash_grupo(normalizados))

    total_distinct_normalized_ids = len(grupos_por_id)
    duplicados = {k: v for k, v in grupos_por_id.items() if len(v) > 1}
    total_duplicate_ids = len(duplicados)
    ambiguos = {k for k, v in duplicados.items() if len(set(v)) > 1}
    total_ambiguous_duplicates = len(ambiguos)

    grupo_resolvido: dict[str, str | None] = {
        id_sha: (grupos[0] if id_sha not in ambiguos else None)
        for id_sha, grupos in grupos_por_id.items()
    }

    ids_canonicos = set(particoes)
    encontrados = ids_canonicos & set(grupo_resolvido)
    faltantes = sorted(ids_canonicos - set(grupo_resolvido))

    match_ids: list[str] = []
    mismatch_ids: list[str] = []
    for id_sha in sorted(encontrados):
        candidato = grupo_resolvido[id_sha]
        if candidato is not None and candidato == particoes[id_sha]:
            match_ids.append(id_sha)
        else:
            mismatch_ids.append(id_sha)

    total_canonical_expected = len(ids_canonicos)
    total_canonical_found = len(encontrados)
    total_canonical_missing = len(faltantes)
    total_group_match = len(match_ids)
    total_group_mismatch = len(mismatch_ids)

    gate_passed = (
        total_canonical_found == total_canonical_expected
        and total_canonical_missing == 0
        and total_group_match == total_canonical_expected
        and total_group_mismatch == 0
        and total_ambiguous_duplicates == 0
    )

    return {
        "total_nonempty_rows": total_nonempty_rows,
        "total_distinct_normalized_ids": total_distinct_normalized_ids,
        "total_duplicate_ids": total_duplicate_ids,
        "total_ambiguous_duplicates": total_ambiguous_duplicates,
        "total_canonical_expected": total_canonical_expected,
        "total_canonical_found": total_canonical_found,
        "total_canonical_missing": total_canonical_missing,
        "missing_id_sha256": faltantes,
        "total_group_match": total_group_match,
        "total_group_mismatch": total_group_mismatch,
        "mismatch_id_sha256": mismatch_ids,
        "gate_passed": gate_passed,
    }


def montar_resultado(
    auditoria: dict[str, Any],
    spreadsheet_id: str,
    aba: str,
    main_sha: str,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "source_spreadsheet_id": spreadsheet_id,
        "source_sheet": aba,
        "main_sha": main_sha,
        **auditoria,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--spreadsheet-id", required=True,
                   help="ID da planilha candidata (nao a operacional canonica)")
    p.add_argument("--aba", required=True, help="Nome da aba com os quatro campos textuais")
    p.add_argument("--credenciais", default=None)
    p.add_argument("--particoes", type=Path, default=PARTICOES_PADRAO)
    p.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    p.add_argument("--main-sha", default=None,
                   help="SHA do commit de main auditado; default GITHUB_SHA ou vazio")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    particoes = carregar_particoes_canonicas(args.particoes)
    sh = pl.abrir_planilha(args.spreadsheet_id, args.credenciais)
    registros = ler_registros_fonte(sh, args.aba)
    auditoria = auditar(registros, particoes)
    main_sha = args.main_sha or os.getenv("GITHUB_SHA") or ""
    resultado = montar_resultado(auditoria, args.spreadsheet_id, args.aba, main_sha)

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    publicavel = {k: v for k, v in resultado.items()}
    print(json.dumps(publicavel, ensure_ascii=False, indent=2))
    return 0 if resultado["gate_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
