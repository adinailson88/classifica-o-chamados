#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persistencia segura de uma unica chave de dados/estado_automacao.json.

Problema que este helper resolve: o arquivo e compartilhado por varios
workflows (avaliacao_final, comparar_modelos, multimodelo_classificacao,
transformer_ft), cada um escrevendo sua propria chave, mas rodando em grupos
de concurrency distintos -- nada impede duas escritas simultaneas. A
estrategia usada ate aqui pelos workflows (`git pull --rebase -X theirs`)
resolve conflito textual por hunk, nao por chave, e pode descartar
silenciosamente a atualizacao de outro processo se as duas chaves calharem
de cair no mesmo hunk (ver auditoria do Lote 8H-A).

Este helper elimina o merge textual: cada tentativa parte de um worktree
temporario e descartavel, criado a partir do SHA mais recente de
<remote>/<branch>, le o JSON desse worktree, altera SOMENTE a chave
solicitada (preservando todas as outras chaves, conhecidas ou nao), comita e
tenta push. Se o push for rejeitado (o remoto avancou), a tentativa inteira e
descartada -- worktree removido, nada de rebase/stash/-X theirs -- e uma nova
tentativa comeca do zero, a partir do novo SHA remoto.

Uso (produtivo, com push real):
    python src/persistir_estado_automacao.py \\
        --chave comparar_modelos --valor 14157 \\
        --remote origin --branch main --max-tentativas 5 --aplicar

Sem --aplicar: valida e relata o que seria alterado, sem commit/push.

Lote 8H-B1: helper criado e testado. A adocao pelos workflows fica para o
Lote 8H-B2 -- nenhum .yml e alterado aqui.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

ESTADO_RELATIVO = "dados/estado_automacao.json"

CHAVES_PERMITIDAS = frozenset({
    "avaliacao_final",
    "comparar_modelos",
    "multimodelo_classificacao",
    "transformer_ft",
})

_MARCADORES_REJEICAO_PUSH = ("[rejected]", "non-fast-forward", "fetch first", "stale info")


class ChaveNaoPermitidaError(ValueError):
    pass


class ValorInvalidoError(ValueError):
    pass


class EstadoInvalidoError(RuntimeError):
    pass


class GitError(RuntimeError):
    pass


class PushRejeitadoError(GitError):
    pass


class PersistenciaFalhouError(RuntimeError):
    pass


# --------------------------------------------------------------------------
# Validacao e logica semantica (testaveis sem Git/rede)
# --------------------------------------------------------------------------

def validar_chave(chave):
    if chave not in CHAVES_PERMITIDAS:
        raise ChaveNaoPermitidaError(
            f"chave nao permitida: {chave!r} (permitidas: {sorted(CHAVES_PERMITIDAS)})"
        )


def validar_valor(valor):
    # bool e subclasse de int em Python (isinstance(True, int) == True);
    # excluido explicitamente para nao aceitar True/False como 1/0.
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValorInvalidoError(f"valor deve ser inteiro: {valor!r}")


def carregar_estado(caminho):
    """Falha fechado: nunca retorna {} para arquivo ausente/invalido/nao-dict."""
    if not os.path.isfile(caminho):
        raise EstadoInvalidoError(f"arquivo de estado nao encontrado: {caminho}")
    with open(caminho, encoding="utf-8") as f:
        texto = f.read()
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as exc:
        raise EstadoInvalidoError(f"JSON invalido em {caminho}: {exc}") from exc
    if not isinstance(dados, dict):
        raise EstadoInvalidoError(f"{caminho} nao contem um objeto JSON (dict)")
    return dados


def aplicar_chave(estado, chave, valor):
    """Retorna uma copia de `estado` com somente `chave` alterada."""
    novo = dict(estado)
    novo[chave] = valor
    return novo


def preservar_outras_chaves(antes, depois, chave_alvo):
    """True se toda chave != chave_alvo tem o mesmo valor em `antes` e `depois`."""
    chaves_antes = set(antes) - {chave_alvo}
    chaves_depois = set(depois) - {chave_alvo}
    if chaves_antes != chaves_depois:
        return False
    return all(antes[k] == depois[k] for k in chaves_antes)


def serializar_estado(estado):
    return json.dumps(estado, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def escrever_estado(caminho, estado):
    os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)
    # newline="\n" forca LF mesmo em Windows: evita diff-noise de CRLF no
    # arquivo versionado, que e sempre LF no repositorio.
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(serializar_estado(estado))


# --------------------------------------------------------------------------
# Git (sempre argumentos em lista, nunca shell=True)
# --------------------------------------------------------------------------

def _run_git(args, cwd):
    resultado = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if resultado.returncode != 0:
        raise GitError(
            f"git {' '.join(args)} falhou (codigo {resultado.returncode}): "
            f"{resultado.stderr.strip()}"
        )
    return resultado.stdout


def _push(remote, branch, cwd):
    resultado = subprocess.run(
        ["git", "push", remote, f"HEAD:{branch}"],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if resultado.returncode == 0:
        return
    saida = f"{resultado.stdout}\n{resultado.stderr}"
    if any(marcador in saida for marcador in _MARCADORES_REJEICAO_PUSH):
        raise PushRejeitadoError(saida.strip())
    raise GitError(f"git push falhou (codigo {resultado.returncode}): {saida.strip()}")


def _configurar_autor(worktree):
    _run_git(["config", "user.name", "github-actions[bot]"], cwd=worktree)
    _run_git(["config", "user.email", "github-actions[bot]@users.noreply.github.com"], cwd=worktree)


def _criar_worktree_temporario(sha, cwd):
    base_tmp = os.environ.get("RUNNER_TEMP") or None
    caminho = tempfile.mkdtemp(prefix="persistir-estado-", dir=base_tmp)
    try:
        _run_git(["worktree", "add", "--detach", caminho, sha], cwd=cwd)
    except GitError:
        shutil.rmtree(caminho, ignore_errors=True)
        raise
    return caminho


def _remover_worktree(caminho, cwd):
    """So remove o worktree que ESTA funcao/chamador criou -- nunca outro."""
    try:
        _run_git(["worktree", "remove", "--force", caminho], cwd=cwd)
    except GitError:
        shutil.rmtree(caminho, ignore_errors=True)
        try:
            _run_git(["worktree", "prune"], cwd=cwd)
        except GitError:
            pass


def _verificar_staging_exclusivo(worktree, caminho_relativo):
    saida = _run_git(["status", "--porcelain"], cwd=worktree)
    linhas = [l for l in saida.splitlines() if l.strip()]
    inesperadas = [l for l in linhas if l[3:] != caminho_relativo]
    if inesperadas:
        raise GitError("staging fora da allowlist: " + "; ".join(inesperadas))
    if not linhas:
        raise GitError("nada staged para commit (estado inesperado)")


# --------------------------------------------------------------------------
# Algoritmo de persistencia
# --------------------------------------------------------------------------

def _sha_remoto_mais_recente(remote, branch, cwd):
    _run_git(["fetch", remote, branch], cwd=cwd)
    return _run_git(["rev-parse", "FETCH_HEAD"], cwd=cwd).strip()


def _uma_tentativa(chave, valor, remote, branch, cwd, before_push=None):
    sha_remoto = _sha_remoto_mais_recente(remote, branch, cwd)
    worktree = _criar_worktree_temporario(sha_remoto, cwd)
    try:
        caminho_estado = os.path.join(worktree, *ESTADO_RELATIVO.split("/"))
        estado_antes = carregar_estado(caminho_estado)

        if estado_antes.get(chave) == valor:
            return {"status": "no-op", "sha_base": sha_remoto, "chave": chave, "valor": valor}

        estado_depois = aplicar_chave(estado_antes, chave, valor)
        if not preservar_outras_chaves(estado_antes, estado_depois, chave):
            raise RuntimeError("violacao de invariante: outras chaves seriam alteradas")

        escrever_estado(caminho_estado, estado_depois)
        _configurar_autor(worktree)
        _run_git(["add", "--", ESTADO_RELATIVO], cwd=worktree)
        _verificar_staging_exclusivo(worktree, ESTADO_RELATIVO)
        _run_git(["commit", "-m", f"estado automacao: {chave} [skip ci]"], cwd=worktree)

        if before_push is not None:
            # Hook interno so para testes simularem uma escrita concorrente
            # entre o commit local e o push. Nao exposto na CLI.
            before_push(worktree)

        _push(remote, branch, cwd=worktree)
        commit_sha = _run_git(["rev-parse", "HEAD"], cwd=worktree).strip()
        return {"status": "ok", "sha_base": sha_remoto, "commit": commit_sha, "chave": chave, "valor": valor}
    finally:
        _remover_worktree(worktree, cwd)


def _dry_run(chave, valor, remote, branch, cwd):
    sha_remoto = _sha_remoto_mais_recente(remote, branch, cwd)
    worktree = _criar_worktree_temporario(sha_remoto, cwd)
    try:
        caminho_estado = os.path.join(worktree, *ESTADO_RELATIVO.split("/"))
        estado_antes = carregar_estado(caminho_estado)
        no_op = estado_antes.get(chave) == valor
        if not no_op:
            estado_depois = aplicar_chave(estado_antes, chave, valor)
            if not preservar_outras_chaves(estado_antes, estado_depois, chave):
                raise RuntimeError("violacao de invariante: outras chaves seriam alteradas")
        print("[persistir_estado] APLICAR=false — nenhum commit/push realizado.")
        print(
            f"[persistir_estado] base={sha_remoto} chave={chave} "
            f"valor_atual={estado_antes.get(chave)!r} valor_solicitado={valor} no_op={no_op}"
        )
        return {"status": "no-op" if no_op else "dry-run", "sha_base": sha_remoto, "chave": chave, "valor": valor}
    finally:
        _remover_worktree(worktree, cwd)


def persistir(chave, valor, *, remote="origin", branch="main", max_tentativas=5,
              cwd=None, aplicar=True, before_push=None):
    """Persiste `valor` na `chave` de dados/estado_automacao.json.

    Cada tentativa parte de um worktree temporario criado a partir do SHA
    mais recente de <remote>/<branch> -- nunca de git pull/rebase/stash.
    Se o push for rejeitado (remoto avancou), a tentativa e descartada e uma
    nova comeca do zero, ate `max_tentativas`.
    """
    cwd = cwd or os.getcwd()
    validar_chave(chave)
    validar_valor(valor)

    if not aplicar:
        return _dry_run(chave, valor, remote, branch, cwd)

    erro_final = None
    for _tentativa in range(1, max_tentativas + 1):
        try:
            return _uma_tentativa(chave, valor, remote, branch, cwd, before_push=before_push)
        except PushRejeitadoError as exc:
            erro_final = exc
            continue

    raise PersistenciaFalhouError(
        f"push rejeitado apos {max_tentativas} tentativa(s) para a chave '{chave}'"
    ) from erro_final


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv=None):
    p = argparse.ArgumentParser(
        description="Persiste uma unica chave de dados/estado_automacao.json de forma concorrente segura."
    )
    p.add_argument("--chave", required=True, choices=sorted(CHAVES_PERMITIDAS))
    p.add_argument("--valor", required=True, type=int)
    p.add_argument("--remote", default="origin")
    p.add_argument("--branch", default="main")
    p.add_argument("--max-tentativas", dest="max_tentativas", type=int, default=5)
    p.add_argument("--aplicar", action="store_true", help="Sem esta flag, roda em modo dry-run (sem commit/push).")
    args = p.parse_args(argv)

    resultado = persistir(
        args.chave,
        args.valor,
        remote=args.remote,
        branch=args.branch,
        max_tentativas=args.max_tentativas,
        aplicar=args.aplicar,
    )
    print(f"[persistir_estado] resultado: {resultado}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
