#!/usr/bin/env python3
"""Congela os JSONs públicos que sustentam uma versão do artigo.

O snapshot não recalcula métricas nem consulta a planilha. Ele copia os
artefatos já publicados e registra hashes SHA-256, origem do commit e o script
de geração conhecido de cada arquivo. Assim, um número citado no artigo pode
ser auditado contra um estado imutável, mesmo que o dashboard seja atualizado.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "docs" / "dados"
SNAPSHOTS = DADOS / "snapshots"

# Arquivos que sustentam as seções quantitativas do artigo/capítulo.
FONTES_ARTIGO = {
    "avaliacao_final.json": "src/avaliacao_final.py",
    "calibracao.json": "src/calibracao.py",
    "comparacao_modelos.json": "src/exportar_dashboard.py",
    "estatistica.json": "src/analise_estatistica.py",
    "jensen_shannon_modelos.json": "src/analise_shannon.py",
    "reclass_resumo.json": "src/exportar_dashboard.py",
    "shannon_modelos.json": "src/analise_shannon.py",
    "shannon_resumo.json": "src/analise_shannon.py",
}


def agora_bahia_iso() -> str:
    return datetime.now(timezone(timedelta(hours=-3))).isoformat(timespec="seconds")


def sha256(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def git_saida(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=RAIZ, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def ler_metadados(caminho: Path) -> dict:
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"json_valido": False}
    if not isinstance(dados, dict):
        return {"json_valido": True, "tipo_raiz": type(dados).__name__}
    return {
        "json_valido": True,
        "gerado_em_origem": dados.get("gerado_em"),
        "run_id_origem": dados.get("run_id"),
        "status_origem": dados.get("status"),
    }


def validar_run_id(run_id: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,100}", run_id):
        raise ValueError("run_id deve conter apenas letras, números, ponto, hífen ou sublinhado.")
    return run_id


def criar_snapshot(run_id: str, substituir: bool = False) -> Path:
    destino = SNAPSHOTS / validar_run_id(run_id)
    if destino.exists() and not substituir:
        raise FileExistsError(f"Snapshot já existe: {destino}. Use --substituir somente para refazê-lo.")
    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)

    arquivos = []
    ausentes = []
    for nome, script in FONTES_ARTIGO.items():
        origem = DADOS / nome
        if not origem.is_file():
            ausentes.append({"arquivo": nome, "script_origem": script})
            continue
        copia = destino / nome
        shutil.copy2(origem, copia)
        arquivos.append(
            {
                "arquivo": nome,
                "script_origem": script,
                "sha256": sha256(copia),
                "bytes": copia.stat().st_size,
                **ler_metadados(copia),
            }
        )

    commit = git_saida("rev-parse", "HEAD")
    sujo = git_saida("status", "--porcelain")
    manifesto = {
        "schema_version": "1.0",
        "run_id": run_id,
        "gerado_em": agora_bahia_iso(),
        "finalidade": "snapshot imutavel das fontes quantitativas do artigo_classificacao_chamados_v3.md",
        "commit_origem": commit,
        "arvore_trabalho_alterada": bool(sujo),
        "arquivos": arquivos,
        "arquivos_ausentes": ausentes,
        "observacao_validacao": (
            "A validacao humana e parcial e nao aleatoria; resultados de acerto validado "
            "nao devem ser generalizados para a base completa."
        ),
    }
    (destino / "manifesto.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return destino


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="Identificador imutável do snapshot.")
    parser.add_argument("--substituir", action="store_true", help="Refaz um snapshot existente.")
    args = parser.parse_args()
    try:
        destino = criar_snapshot(args.run_id, args.substituir)
    except (ValueError, FileExistsError) as exc:
        parser.error(str(exc))
    print(f"snapshot={destino.relative_to(RAIZ)}")
    print(f"manifesto={destino.relative_to(RAIZ) / 'manifesto.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
