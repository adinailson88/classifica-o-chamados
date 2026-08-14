#!/usr/bin/env python3
"""Le o bundle privado e estatico do REPLAY CONGELADO (Execucao Cientifica 1).

Ferramenta estritamente READ-ONLY. Le uma spreadsheet PRIVADA e dedicada
(NUNCA a planilha operacional viva), compartilhada em modo Leitor com a
conta de servico usada em CI, contendo apenas valores estaticos (nunca
formula, nunca IMPORTRANGE) dos 9 campos que os sete modelos-base da Fase 2B
efetivamente consomem, congelados no momento da Execucao Cientifica 1:
id_sha256, titulo, descricao_glpi, titulo_osm, descricao_osm,
categoria_historica, referencia_humana, grupo_sha256, outer_fold.

Nao duplica nenhuma logica de normalizacao/hash: a checagem de consistencia
por registro reusa `construir_grupos_textuais.normalizar_texto`/`hash_grupo`
sem reimplementa-las. A validacao dos 5 hashes metodologicos e do sexto
fingerprint operacional (`replay_input_sha256`) fica em
`ensemble_fase2b_crossfit.gate_zero_replay`.

Ver docs/REPLAY_CONGELADO_FASE2B.md para o desenho completo, o schema do
bundle e o nivel de evidencia da reconstrucao da Execucao Cientifica 1.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import construir_grupos_textuais as cgt  # noqa: E402
import planilha as pl  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]

ABA_BUNDLE = "REPLAY_EXECUCAO_1_INPUT_CONGELADO"
ID_LOCAL_REPLAY = RAIZ / "replay_spreadsheet_id.local"  # gitignored, uso local

# Ordem canonica dos 9 campos do bundle. Mesma ordem usada como cabecalho da
# aba privada; a leitura localiza por nome de cabecalho (nao por posicao), e
# tolera reordenacao de colunas na planilha.
CAMPOS_BUNDLE = (
    "id_sha256", "titulo", "descricao_glpi", "titulo_osm", "descricao_osm",
    "categoria_historica", "referencia_humana", "grupo_sha256", "outer_fold",
)


def id_replay_spreadsheet() -> str:
    """ID da spreadsheet PRIVADA do bundle. Nunca versionado em texto puro,
    mesma convencao de `planilha.id_planilha`: variavel de ambiente
    REPLAY_SPREADSHEET_ID (Secret no CI) -> arquivo local gitignored
    `replay_spreadsheet_id.local` (uso local)."""
    env = os.getenv("REPLAY_SPREADSHEET_ID")
    if env and env.strip():
        return env.strip()
    if ID_LOCAL_REPLAY.exists():
        valor = ID_LOCAL_REPLAY.read_text(encoding="utf-8").strip()
        if valor:
            return valor
    raise RuntimeError(
        "ID da spreadsheet de replay nao definido. Configure o Secret/variavel "
        "REPLAY_SPREADSHEET_ID (CI) ou crie replay_spreadsheet_id.local (uso local)."
    )


def ler_bundle_congelado(
    spreadsheet_id: str | None = None,
    credenciais: str | None = None,
) -> list[dict[str, Any]]:
    """Le os 9 campos estaticos do bundle, na aba dedicada `ABA_BUNDLE`.

    So le valor ja resolvido (`UNFORMATTED_VALUE`, mesma opcao usada em todo
    o resto do repo): uma formula ali dentro apareceria aqui como o ultimo
    valor calculado, nunca como texto de formula, mas o desenho exige que a
    aba nunca contenha formula em primeiro lugar (ver
    docs/REPLAY_CONGELADO_FASE2B.md).
    """
    sid = spreadsheet_id or id_replay_spreadsheet()
    sh = pl.abrir_planilha(sid, credenciais)
    ws = sh.worksheet(ABA_BUNDLE)
    bloco = ws.get_values("A:I", value_render_option="UNFORMATTED_VALUE")
    if not bloco:
        raise RuntimeError(f"Bundle vazio na aba {ABA_BUNDLE!r}.")
    cab = bloco[0]
    indices = {
        campo: pl.localizar_coluna(cab, (campo,), i + 1)
        for i, campo in enumerate(CAMPOS_BUNDLE)
    }

    def cel(linha: list[Any], campo: str) -> str:
        i = indices[campo] - 1
        return str(linha[i] or "").strip() if len(linha) > i else ""

    registros = []
    for linha in bloco[1:]:
        if not any(str(v or "").strip() for v in linha):
            continue
        outer_fold_bruto = cel(linha, "outer_fold")
        registros.append({
            "id_sha256": cel(linha, "id_sha256"),
            "titulo": cel(linha, "titulo"),
            "descricao_glpi": cel(linha, "descricao_glpi"),
            "titulo_osm": cel(linha, "titulo_osm"),
            "descricao_osm": cel(linha, "descricao_osm"),
            "categoria_historica": cel(linha, "categoria_historica"),
            "referencia_humana": cel(linha, "referencia_humana"),
            "grupo_sha256": cel(linha, "grupo_sha256"),
            "outer_fold": int(float(outer_fold_bruto)) if outer_fold_bruto else None,
        })
    return registros


def validar_grupos_por_registro(registros: list[dict[str, Any]]) -> list[str]:
    """Recomputa `grupo_sha256` a partir dos 4 campos BRUTOS de cada registro
    (mesma normalizacao/hash de `construir_grupos_textuais`, sem duplicar) e
    devolve os `id_sha256` cujo `grupo_sha256` armazenado no bundle NAO bate
    com o recomputado agora. Lista vazia = bundle internamente consistente
    (nenhum campo textual foi alterado sem o grupo_sha256 acompanhar, e
    vice-versa)."""
    divergentes = []
    for r in registros:
        normalizados = [cgt.normalizar_texto(r[c]) for c in cgt.CAMPOS_TEXTUAIS]
        recomputado = cgt.hash_grupo(normalizados)
        if recomputado != r["grupo_sha256"]:
            divergentes.append(r["id_sha256"])
    return divergentes
