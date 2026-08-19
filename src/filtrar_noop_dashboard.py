#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restaura JSONs de docs/dados cuja unica mudanca em relacao a HEAD seja o
campo `gerado_em` no nivel superior do objeto.

Problema que este helper resolve: alguns geradores do dashboard (ver
src/exportar_dashboard.py e src/analise_shannon.py) regravam `gerado_em` a
cada execucao mesmo quando nenhum dado substantivo mudou, o que faz o Git
enxergar diferenca e o workflow `dashboard.yml` commitar um "no-op" so por
causa do timestamp (ver historico de commits "dados do dashboard [skip ci]",
por exemplo 525edb3466481850155bd80381ad61ad01ea5cd6).

Este helper roda DEPOIS da geracao dos dados e ANTES do `git add`, sobre a
lista ja validada pela allowlist do workflow. Para cada path: se o unico
campo que diverge de HEAD e a chave `gerado_em` no nivel superior de um
objeto JSON, o arquivo e restaurado byte a byte para o conteudo de HEAD (sem
`git checkout`/`restore`/`reset`) e nao entra no commit. Qualquer outra
divergencia -- inclusive `gerado_em` aninhado, presente so de um lado, ou
qualquer outra chave -- e tratada como mudanca substantiva e preservada.

Uso:
    python src/filtrar_noop_dashboard.py -- \\
        docs/dados/calibracao.json \\
        docs/dados/resumo.json

Imprime uma linha por path: "<STATUS> <path>". Status possiveis:
    VOLATIL_RESTAURADO  arquivo restaurado para o conteudo de HEAD
    SUBSTANTIVO         mudanca real; arquivo mantido como esta
    NOVO                arquivo nao existe em HEAD; mantido como esta
    ERRO                JSON invalido (em HEAD ou no arquivo novo); arquivo
                         NAO e sobrescrito e o processo termina com codigo != 0

Falha fechada: qualquer JSON invalido aborta o job (exit code != 0) sem
sobrescrever nenhum arquivo problematico, mesmo que outros paths da mesma
chamada tenham sido restaurados com sucesso.
"""
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath

DADOS_RAIZ = "docs/dados/"
CHAVE_VOLATIL = "gerado_em"

STATUS_VOLATIL_RESTAURADO = "VOLATIL_RESTAURADO"
STATUS_SUBSTANTIVO = "SUBSTANTIVO"
STATUS_NOVO = "NOVO"
STATUS_ERRO = "ERRO"


class PathRejeitadoError(ValueError):
    pass


class JsonInvalidoError(ValueError):
    pass


def validar_path(path_str):
    """Aceita somente `docs/dados/*.json` relativo, sem travessia de diretorio."""
    normalizado = path_str.replace("\\", "/")
    if normalizado.startswith("/") or (len(normalizado) > 1 and normalizado[1] == ":"):
        raise PathRejeitadoError(f"path absoluto rejeitado: {path_str}")
    partes = normalizado.split("/")
    if ".." in partes:
        raise PathRejeitadoError(f"travessia de diretorio rejeitada: {path_str}")
    if not normalizado.startswith(DADOS_RAIZ):
        raise PathRejeitadoError(f"fora de {DADOS_RAIZ}: {path_str}")
    if not normalizado.endswith(".json"):
        raise PathRejeitadoError(f"extensao invalida (esperado .json): {path_str}")
    if normalizado.endswith("/"):
        raise PathRejeitadoError(f"diretorio nao aceito: {path_str}")
    return PurePosixPath(normalizado)


def ler_baseline_head(rel_path, cwd):
    """Le o conteudo de `rel_path` em HEAD via `git show`, somente leitura.

    Retorna None se o path nao existir em HEAD (arquivo novo).
    """
    resultado = subprocess.run(
        ["git", "show", f"HEAD:{rel_path.as_posix()}"],
        cwd=cwd,
        capture_output=True,
        check=False,
    )
    if resultado.returncode != 0:
        return None
    return resultado.stdout


def _sem_chave_topo(obj, chave):
    if isinstance(obj, dict):
        return {k: v for k, v in obj.items() if k != chave}
    return obj


def eh_apenas_gerado_em_diferente(baseline_obj, novo_obj):
    """True somente se ambos sao dict, ambos tem `gerado_em` no topo, e o
    resto do conteudo (com essa unica chave removida dos dois lados) e igual.
    """
    if not isinstance(baseline_obj, dict) or not isinstance(novo_obj, dict):
        return False
    tem_baseline = CHAVE_VOLATIL in baseline_obj
    tem_novo = CHAVE_VOLATIL in novo_obj
    if not tem_baseline or not tem_novo:
        return False
    return _sem_chave_topo(baseline_obj, CHAVE_VOLATIL) == _sem_chave_topo(novo_obj, CHAVE_VOLATIL)


def _parse_json(bytes_conteudo, origem):
    try:
        return json.loads(bytes_conteudo.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise JsonInvalidoError(f"JSON invalido em {origem}: {exc}") from exc


def processar_path(path_str, cwd=None):
    """Processa um path e retorna (path_normalizado, status).

    Levanta PathRejeitadoError para path fora das regras e JsonInvalidoError
    (fail closed) para JSON invalido em HEAD ou no arquivo novo -- em nenhum
    dos dois casos o arquivo e escrito.
    """
    cwd = cwd or Path.cwd()
    cwd = Path(cwd)
    rel_path = validar_path(path_str)
    abs_path = cwd / rel_path

    if not abs_path.exists():
        # Arquivo removido do working tree: nao ha o que restaurar
        # automaticamente; tratado como mudanca real a ser decidida pelo
        # staging normal do workflow.
        return (rel_path.as_posix(), STATUS_SUBSTANTIVO)

    baseline_bytes = ler_baseline_head(rel_path, cwd)
    if baseline_bytes is None:
        return (rel_path.as_posix(), STATUS_NOVO)

    novo_bytes = abs_path.read_bytes()

    baseline_obj = _parse_json(baseline_bytes, f"HEAD:{rel_path.as_posix()}")
    novo_obj = _parse_json(novo_bytes, rel_path.as_posix())

    if eh_apenas_gerado_em_diferente(baseline_obj, novo_obj):
        abs_path.write_bytes(baseline_bytes)
        return (rel_path.as_posix(), STATUS_VOLATIL_RESTAURADO)

    return (rel_path.as_posix(), STATUS_SUBSTANTIVO)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        print("uso: filtrar_noop_dashboard.py -- <docs/dados/arquivo.json> [...]", file=sys.stderr)
        return 2

    houve_erro = False
    for path_str in argv:
        try:
            path_norm, status = processar_path(path_str)
        except PathRejeitadoError as exc:
            print(f"REJEITADO {path_str}: {exc}", file=sys.stderr)
            houve_erro = True
            continue
        except JsonInvalidoError as exc:
            print(f"{STATUS_ERRO} {path_str}: {exc}", file=sys.stderr)
            houve_erro = True
            continue
        print(f"{status} {path_norm}")

    return 1 if houve_erro else 0


if __name__ == "__main__":
    sys.exit(main())
