#!/usr/bin/env python3
"""Verifica a integridade da Trilha A (artigo congelado), conforme o
manifesto `docs/dados/MANIFESTO_ARTIGO_CONGELADO.json`.

Ferramenta estritamente OFFLINE: sem rede, sem Google Sheets, sem
credenciais. So le arquivos ja versionados no repositorio.

O que verifica:

  1. o manifesto existe, e um JSON valido e tem os campos obrigatorios
     (schema_version, status=CONGELADO, trilha=ARTIGO_CONGELADO,
     invariantes completas);
  2. as invariantes do manifesto batem com os valores esperados desta
     rodada canonica (hash_corpus, corpus_completo, corpus_modelagem,
     categorias_modelagem, dobras) -- valores fixos neste script, nao
     apenas lidos do proprio manifesto, para que uma adulteracao do
     manifesto tambem seja detectada;
  3. todo path listado em "arquivos" existe;
  4. o SHA-256 do CONTEUDO de cada arquivo listado bate com o valor
     declarado no manifesto. O hash e calculado no modo declarado em
     "hash_mode" (unico modo aceito: "sha256_lf_normalized"), que
     substitui CRLF por LF antes de hashear -- e SOMENTE isso. Nenhuma
     outra normalizacao (espacos, tabs, encoding, ordenacao de chaves,
     trailing whitespace) e aplicada; uma mudanca substantiva de
     conteudo continua alterando o hash. Isso existe porque o checkout
     do Windows (core.autocrlf) grava CRLF no worktree local enquanto o
     checkout do GitHub Actions/Ubuntu grava LF -- sem essa normalizacao
     o mesmo conteudo produzia hashes diferentes por plataforma;
  5. para os arquivos marcados "possui_hash_corpus": true, o campo
     hash_corpus do proprio JSON bate com o hash esperado. Arquivos
     marcados false NAO sao exigidos a ter esse campo -- eles definem o
     congelamento (auditoria_base_canonica, grupos_textuais,
     particoes_canonicas) ou legitimamente nao carregam essa chave
     (custo_bertimbau, disponibilidade_temporal, grupos_divergentes,
     tabelas_apendice, os dois .csv);
  6. duas checagens semanticas adicionais, sobre arquivos especificos:
     `rodada_canonica.json` (corpus.linhas/categorias/dobras) e
     `auditoria_base_canonica.json` (corpus.linhas_nao_vazias/
     ids_unicos/referencias_validas).

Esta ferramenta NAO recongela, NAO recalcula hash cientifico interno,
NAO acessa a planilha e NAO atualiza o manifesto. Deliberadamente nao
tem modo --fix nem --update: atualizar o baseline congelado exige
decisao humana explicita e edicao consciente do manifesto, nunca uma
consequencia automatica de rodar este script.

Retorna 0 se integro, != 0 se houver qualquer violacao.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[1]
MANIFESTO_PADRAO = RAIZ / "docs" / "dados" / "MANIFESTO_ARTIGO_CONGELADO.json"

# Valores fixos desta rodada canonica. Nao vem so do manifesto: uma
# adulteracao do proprio manifesto (mudar a invariante declarada) tambem
# precisa ser detectada, entao o esperado mora no codigo, nao so no dado.
HASH_CORPUS_ESPERADO = "1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a"
CORPUS_COMPLETO_ESPERADO = 14060
CORPUS_MODELAGEM_ESPERADO = 13972
CATEGORIAS_MODELAGEM_ESPERADO = 41
DOBRAS_ESPERADAS = 5

SCHEMA_VERSION_ESPERADA = 1
STATUS_ESPERADO = "CONGELADO"
TRILHA_ESPERADA = "ARTIGO_CONGELADO"
HASH_MODE_ESPERADO = "sha256_lf_normalized"

RODADA_CANONICA_PATH = "docs/dados/rodada_canonica.json"
AUDITORIA_BASE_PATH = "docs/dados/auditoria_base_canonica.json"


def sha256_lf_normalizado(caminho: Path) -> str:
    """SHA-256 do conteudo apos normalizar SOMENTE fim de linha CRLF->LF.

    Nao mexe em mais nada: espacos, tabs, encoding, ordenacao de chaves e
    trailing whitespace continuam contando para o hash. O objetivo unico e
    tornar o hash independente de o checkout ter sido feito com
    core.autocrlf=true (Windows, grava CRLF) ou sem conversao (Ubuntu/CI,
    grava LF como esta no blob do git) -- nao mascarar mudanca de conteudo.
    """
    dados = caminho.read_bytes()
    dados = dados.replace(b"\r\n", b"\n")
    return hashlib.sha256(dados).hexdigest()


def carregar_manifesto(caminho: Path) -> tuple[dict[str, Any] | None, list[str]]:
    problemas: list[str] = []
    if not caminho.exists():
        problemas.append(f"manifesto ausente: {caminho}")
        return None, problemas
    try:
        conteudo = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        problemas.append(f"manifesto invalido (JSON malformado): {e}")
        return None, problemas
    if not isinstance(conteudo, dict):
        problemas.append("manifesto invalido: raiz nao e um objeto JSON")
        return None, problemas
    return conteudo, problemas


def verificar_estrutura_manifesto(manifesto: dict[str, Any]) -> list[str]:
    problemas: list[str] = []

    if manifesto.get("schema_version") != SCHEMA_VERSION_ESPERADA:
        problemas.append(
            f"schema_version inesperada: obtido={manifesto.get('schema_version')!r}, "
            f"esperado={SCHEMA_VERSION_ESPERADA!r}"
        )
    if manifesto.get("status") != STATUS_ESPERADO:
        problemas.append(
            f"status inesperado: obtido={manifesto.get('status')!r}, esperado={STATUS_ESPERADO!r}"
        )
    if manifesto.get("trilha") != TRILHA_ESPERADA:
        problemas.append(
            f"trilha inesperada: obtido={manifesto.get('trilha')!r}, esperado={TRILHA_ESPERADA!r}"
        )
    if manifesto.get("hash_mode") != HASH_MODE_ESPERADO:
        problemas.append(
            f"hash_mode inesperado: obtido={manifesto.get('hash_mode')!r}, esperado={HASH_MODE_ESPERADO!r}"
        )

    invariantes = manifesto.get("invariantes")
    if not isinstance(invariantes, dict):
        problemas.append("invariantes ausentes ou em formato invalido")
        return problemas

    esperado = {
        "hash_corpus": HASH_CORPUS_ESPERADO,
        "corpus_completo": CORPUS_COMPLETO_ESPERADO,
        "corpus_modelagem": CORPUS_MODELAGEM_ESPERADO,
        "categorias_modelagem": CATEGORIAS_MODELAGEM_ESPERADO,
        "dobras": DOBRAS_ESPERADAS,
    }
    for chave, valor_esperado in esperado.items():
        obtido = invariantes.get(chave)
        if obtido != valor_esperado:
            problemas.append(
                f"invariante '{chave}' divergente: obtido={obtido!r}, esperado={valor_esperado!r}"
            )

    if not isinstance(manifesto.get("arquivos"), list) or not manifesto["arquivos"]:
        problemas.append("lista 'arquivos' ausente, vazia ou em formato invalido")

    return problemas


def verificar_arquivos(manifesto: dict[str, Any], base_dir: Path) -> list[str]:
    problemas: list[str] = []
    for entrada in manifesto.get("arquivos", []):
        if not isinstance(entrada, dict):
            problemas.append(f"entrada de arquivo em formato invalido: {entrada!r}")
            continue
        path = entrada.get("path")
        sha_esperado = entrada.get("sha256")
        possui_hash_corpus = entrada.get("possui_hash_corpus")
        if not path or not sha_esperado or possui_hash_corpus is None:
            problemas.append(f"entrada de arquivo incompleta (path/sha256/possui_hash_corpus): {entrada!r}")
            continue

        caminho = base_dir / path
        if not caminho.exists():
            problemas.append(f"AUSENTE: {path}")
            continue

        sha_obtido = sha256_lf_normalizado(caminho)
        if sha_obtido != sha_esperado:
            problemas.append(
                f"HASH DIVERGENTE: {path} (obtido={sha_obtido}, esperado={sha_esperado})"
            )
            # Se o conteudo mudou, o hash_corpus interno tambem pode ter
            # mudado; ainda assim confere abaixo para reportar os dois
            # sinais juntos no mesmo diagnostico.

        if possui_hash_corpus and path.endswith(".json"):
            try:
                dados = json.loads(caminho.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                problemas.append(f"JSON invalido em {path}, nao foi possivel checar hash_corpus: {e}")
                continue
            hash_obtido = dados.get("hash_corpus") if isinstance(dados, dict) else None
            if hash_obtido != HASH_CORPUS_ESPERADO:
                problemas.append(
                    f"HASH_CORPUS CIENTIFICO DIVERGENTE em {path}: "
                    f"obtido={hash_obtido!r}, esperado={HASH_CORPUS_ESPERADO!r}"
                )

    return problemas


def verificar_semantica_rodada_canonica(base_dir: Path) -> list[str]:
    problemas: list[str] = []
    caminho = base_dir / RODADA_CANONICA_PATH
    if not caminho.exists():
        # Ja reportado como AUSENTE por verificar_arquivos(); nao duplica aqui.
        return problemas
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        problemas.append(f"JSON invalido em {RODADA_CANONICA_PATH}: {e}")
        return problemas

    corpus = dados.get("corpus") if isinstance(dados, dict) else None
    if not isinstance(corpus, dict):
        problemas.append(f"{RODADA_CANONICA_PATH}: bloco 'corpus' ausente ou invalido")
        return problemas

    esperado = {
        "linhas": CORPUS_MODELAGEM_ESPERADO,
        "categorias": CATEGORIAS_MODELAGEM_ESPERADO,
        "dobras": DOBRAS_ESPERADAS,
    }
    for chave, valor_esperado in esperado.items():
        obtido = corpus.get(chave)
        if obtido != valor_esperado:
            problemas.append(
                f"{RODADA_CANONICA_PATH}: corpus.{chave} divergente "
                f"(obtido={obtido!r}, esperado={valor_esperado!r})"
            )
    return problemas


def verificar_semantica_auditoria_base(base_dir: Path) -> list[str]:
    problemas: list[str] = []
    caminho = base_dir / AUDITORIA_BASE_PATH
    if not caminho.exists():
        return problemas
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        problemas.append(f"JSON invalido em {AUDITORIA_BASE_PATH}: {e}")
        return problemas

    corpus = dados.get("corpus") if isinstance(dados, dict) else None
    if not isinstance(corpus, dict):
        problemas.append(f"{AUDITORIA_BASE_PATH}: bloco 'corpus' ausente ou invalido")
        return problemas

    esperado = {
        "linhas_nao_vazias": CORPUS_COMPLETO_ESPERADO,
        "ids_unicos": CORPUS_COMPLETO_ESPERADO,
        "referencias_validas": CORPUS_COMPLETO_ESPERADO,
    }
    for chave, valor_esperado in esperado.items():
        obtido = corpus.get(chave)
        if obtido != valor_esperado:
            problemas.append(
                f"{AUDITORIA_BASE_PATH}: corpus.{chave} divergente "
                f"(obtido={obtido!r}, esperado={valor_esperado!r})"
            )
    return problemas


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--manifesto", type=Path, default=MANIFESTO_PADRAO,
                   help="Caminho do manifesto (default: docs/dados/MANIFESTO_ARTIGO_CONGELADO.json).")
    p.add_argument("--base-dir", type=Path, default=RAIZ,
                   help="Diretorio-raiz contra o qual os paths do manifesto sao resolvidos (default: raiz do repositorio).")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    manifesto, problemas = carregar_manifesto(args.manifesto)
    if manifesto is None:
        for p in problemas:
            print(f"BLOQUEADO: {p}", file=sys.stderr)
        return 1

    problemas.extend(verificar_estrutura_manifesto(manifesto))
    problemas.extend(verificar_arquivos(manifesto, args.base_dir))
    problemas.extend(verificar_semantica_rodada_canonica(args.base_dir))
    problemas.extend(verificar_semantica_auditoria_base(args.base_dir))

    total_arquivos = len(manifesto.get("arquivos", []))
    if problemas:
        print(f"VIOLACOES DETECTADAS ({len(problemas)}) na trilha ARTIGO_CONGELADO:", file=sys.stderr)
        for p in problemas:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print(
        f"OK: {total_arquivos} arquivo(s) protegido(s) integro(s); "
        f"hash_corpus={HASH_CORPUS_ESPERADO}; "
        f"corpus_completo={CORPUS_COMPLETO_ESPERADO}; "
        f"corpus_modelagem={CORPUS_MODELAGEM_ESPERADO}; "
        f"categorias_modelagem={CATEGORIAS_MODELAGEM_ESPERADO}; dobras={DOBRAS_ESPERADAS}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
