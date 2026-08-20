#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restaura JSONs de docs/dados cuja unica mudanca em relacao a HEAD seja um
campo volatil de timestamp: `gerado_em` no nivel superior do objeto (regra
geral) ou, exclusivamente para docs/dados/multimodelo_metricas.json,
`atualizado_em` em cada item da lista top-level (excecao especifica).

Problema que este helper resolve: alguns geradores do dashboard (ver
src/exportar_dashboard.py e src/analise_shannon.py) regravam `gerado_em` a
cada execucao mesmo quando nenhum dado substantivo mudou, o que faz o Git
enxergar diferenca e o workflow `dashboard.yml` commitar um "no-op" so por
causa do timestamp (ver historico de commits "dados do dashboard [skip ci]",
por exemplo 525edb3466481850155bd80381ad61ad01ea5cd6). O mesmo padrao ocorre
em docs/dados/multimodelo_metricas.json, mas ali o campo volatil e
`atualizado_em` dentro de cada item da lista, nao um `gerado_em` no topo
(ver commits 1f237f8ea1c2a53ec7a2a73a1e3a58556dfdac01 e
a3f1a7310d10b2cb93c103b9ec8431a318ab5e91: mesmas metricas por modelo, so
`atualizado_em` mudou em cada item).

Este helper roda DEPOIS da geracao dos dados e ANTES do `git add`, sobre a
lista ja validada pela allowlist do workflow. Para cada path:

- regra geral: se o objeto e um dict e o unico campo que diverge de HEAD e a
  chave `gerado_em` no nivel superior, o arquivo e restaurado;
- excecao exclusiva de docs/dados/multimodelo_metricas.json: se o topo e uma
  lista, baseline e novo tem exatamente o mesmo numero de elementos, cada
  elemento correspondente (mesma posicao) e dict, ambos os lados desse par
  tem `atualizado_em`, e o resto do par (sem essa chave) e identico, o
  arquivo e restaurado. Nenhum outro arquivo recebe essa excecao, e nenhuma
  outra chave temporal (`data`, `ultima_execucao`, `updated_at`,
  `timestamp`) e ignorada em lugar nenhum.

A restauracao e byte a byte para o conteudo de HEAD (sem
`git checkout`/`restore`/`reset`) e o arquivo nao entra no commit. Qualquer
outra divergencia -- inclusive chave aninhada, presente so de um lado,
elemento adicionado/removido/reordenado, ou qualquer outro campo -- e
tratada como mudanca substantiva e preservada.

Uso:
    python src/filtrar_noop_dashboard.py -- \\
        docs/dados/calibracao.json \\
        docs/dados/resumo.json

Imprime uma linha por path: "<STATUS> <path>". Status possiveis:
    VOLATIL_RESTAURADO  arquivo restaurado para o conteudo de HEAD
    SUBSTANTIVO         mudanca real; arquivo mantido como esta
    NOVO                arquivo nao existe em HEAD (confirmado via
                         `git ls-tree`); mantido como esta
    ERRO                JSON invalido, path rejeitado, ou falha real na
                         consulta ao Git (nunca tratada como NOVO); arquivo
                         NAO e sobrescrito e o processo termina com codigo != 0

Falha fechada: qualquer JSON invalido, path invalido, ou falha da consulta
Git aborta o job (exit code != 0) sem sobrescrever nenhum arquivo
problematico, mesmo que outros paths da mesma chamada tenham sido
restaurados com sucesso.
"""
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath

DADOS_RAIZ = "docs/dados/"
CHAVE_VOLATIL = "gerado_em"

PATH_MULTIMODELO_METRICAS = "docs/dados/multimodelo_metricas.json"
CHAVE_VOLATIL_ITEM = "atualizado_em"

STATUS_VOLATIL_RESTAURADO = "VOLATIL_RESTAURADO"
STATUS_SUBSTANTIVO = "SUBSTANTIVO"
STATUS_NOVO = "NOVO"
STATUS_ERRO = "ERRO"


class PathRejeitadoError(ValueError):
    pass


class JsonInvalidoError(ValueError):
    pass


class GitBaselineError(RuntimeError):
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


def _existe_em_head(rel_path, cwd):
    """True/False se `rel_path` existe em HEAD, via `git ls-tree` (somente
    leitura). Levanta GitBaselineError se a propria consulta ao Git falhar
    -- uma falha de comando NUNCA deve virar "arquivo novo" silenciosamente.
    """
    resultado = subprocess.run(
        ["git", "ls-tree", "--name-only", "-z", "HEAD", "--", rel_path.as_posix()],
        cwd=cwd,
        capture_output=True,
        check=False,
    )
    if resultado.returncode != 0:
        raise GitBaselineError(
            f"git ls-tree falhou (codigo {resultado.returncode}) para "
            f"HEAD:{rel_path.as_posix()}: "
            f"{resultado.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return bool(resultado.stdout.strip(b"\x00"))


def ler_baseline_head(rel_path, cwd):
    """Le o conteudo de `rel_path` em HEAD via `git show`, somente leitura.

    Retorna None somente se `git ls-tree` confirmar que o path nao existe em
    HEAD (arquivo novo). Qualquer falha real do Git (ls-tree ou show) levanta
    GitBaselineError em vez de ser tratada como arquivo novo.
    """
    if not _existe_em_head(rel_path, cwd):
        return None

    resultado = subprocess.run(
        ["git", "show", f"HEAD:{rel_path.as_posix()}"],
        cwd=cwd,
        capture_output=True,
        check=False,
    )
    if resultado.returncode != 0:
        raise GitBaselineError(
            f"git show falhou (codigo {resultado.returncode}) para "
            f"HEAD:{rel_path.as_posix()}: "
            f"{resultado.stderr.decode('utf-8', errors='replace').strip()}"
        )
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


def eh_apenas_atualizado_em_por_item_diferente(baseline_obj, novo_obj):
    """Excecao exclusiva de docs/dados/multimodelo_metricas.json.

    True somente se baseline e novo forem listas de mesmo tamanho, cada
    elemento correspondente (mesma posicao -- a lista nunca e reordenada
    nem casada por `modelo`) for dict, ambos os lados de cada par tiverem
    `atualizado_em`, e o resto de cada par (com essa unica chave removida
    dos dois lados) for igual. Qualquer elemento adicionado, removido,
    reordenado, que deixe de ser dict, ou com `atualizado_em` so de um lado
    invalida a excecao inteira para o arquivo.
    """
    if not isinstance(baseline_obj, list) or not isinstance(novo_obj, list):
        return False
    if len(baseline_obj) != len(novo_obj):
        return False
    for item_base, item_novo in zip(baseline_obj, novo_obj):
        if not isinstance(item_base, dict) or not isinstance(item_novo, dict):
            return False
        if CHAVE_VOLATIL_ITEM not in item_base or CHAVE_VOLATIL_ITEM not in item_novo:
            return False
        if _sem_chave_topo(item_base, CHAVE_VOLATIL_ITEM) != _sem_chave_topo(item_novo, CHAVE_VOLATIL_ITEM):
            return False
    return True


def eh_noop_volatil(rel_path, baseline_obj, novo_obj):
    """Decide se `rel_path` e um no-op volatil: aplica a regra geral
    (`gerado_em` top-level) e, exclusivamente para
    docs/dados/multimodelo_metricas.json, a excecao especifica de
    `atualizado_em` por item.
    """
    if eh_apenas_gerado_em_diferente(baseline_obj, novo_obj):
        return True
    if rel_path.as_posix() == PATH_MULTIMODELO_METRICAS:
        return eh_apenas_atualizado_em_por_item_diferente(baseline_obj, novo_obj)
    return False


def _parse_json(bytes_conteudo, origem):
    try:
        return json.loads(bytes_conteudo.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise JsonInvalidoError(f"JSON invalido em {origem}: {exc}") from exc


def processar_path(path_str, cwd=None):
    """Processa um path e retorna (path_normalizado, status).

    Levanta PathRejeitadoError para path fora das regras (inclusive
    diretorio no lugar de arquivo), JsonInvalidoError (fail closed) para
    JSON invalido em HEAD ou no arquivo novo, e GitBaselineError (fail
    closed) se a propria consulta ao Git falhar por motivo diferente de
    "path nao existe em HEAD" -- em nenhum desses casos o arquivo e escrito.
    """
    cwd = cwd or Path.cwd()
    cwd = Path(cwd)
    rel_path = validar_path(path_str)
    abs_path = cwd / rel_path

    if abs_path.exists() and abs_path.is_dir():
        # O contrato so aceita arquivo; nao depender so da extensao textual
        # ".json" -- um diretorio com esse nome tambem e rejeitado.
        raise PathRejeitadoError(f"diretorio nao aceito: {path_str}")

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

    if eh_noop_volatil(rel_path, baseline_obj, novo_obj):
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
        except GitBaselineError as exc:
            print(f"{STATUS_ERRO} {path_str}: {exc}", file=sys.stderr)
            houve_erro = True
            continue
        print(f"{status} {path_norm}")

    return 1 if houve_erro else 0


if __name__ == "__main__":
    sys.exit(main())
