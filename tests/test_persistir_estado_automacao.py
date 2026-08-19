from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import persistir_estado_automacao as pea  # noqa: E402


def _git(args, cwd=None):
    resultado = subprocess.run(
        ["git", *args], cwd=str(cwd) if cwd else None, capture_output=True, text=True
    )
    if resultado.returncode != 0:
        raise RuntimeError(f"git {args} falhou: {resultado.stderr}")
    return resultado.stdout


def _escrever_json(caminho: Path, dados: dict) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


# --------------------------------------------------------------------------
# Grupo 1: logica semantica pura -- sem Git, sem rede.
# --------------------------------------------------------------------------

class TestValidacaoEBemAlgebra(unittest.TestCase):
    def test_chave_permitida_nao_levanta(self):
        for chave in sorted(pea.CHAVES_PERMITIDAS):
            pea.validar_chave(chave)  # nao deve levantar

    def test_chave_nao_permitida_levanta(self):
        with self.assertRaises(pea.ChaveNaoPermitidaError):
            pea.validar_chave("chave_qualquer_inventada")

    def test_valor_inteiro_nao_levanta(self):
        pea.validar_valor(0)
        pea.validar_valor(-5)
        pea.validar_valor(14157)

    def test_valor_float_levanta(self):
        with self.assertRaises(pea.ValorInvalidoError):
            pea.validar_valor(3.5)

    def test_valor_string_levanta(self):
        with self.assertRaises(pea.ValorInvalidoError):
            pea.validar_valor("14000")

    def test_valor_bool_levanta(self):
        # bool e subclasse de int em Python; deve ser rejeitado explicitamente.
        with self.assertRaises(pea.ValorInvalidoError):
            pea.validar_valor(True)
        with self.assertRaises(pea.ValorInvalidoError):
            pea.validar_valor(False)

    def test_aplicar_chave_so_altera_a_chave_alvo(self):
        antes = {"a": 1, "b": 2, "c": 3}
        depois = pea.aplicar_chave(antes, "b", 99)
        self.assertEqual(depois, {"a": 1, "b": 99, "c": 3})
        self.assertEqual(antes, {"a": 1, "b": 2, "c": 3})  # nao mutou o original

    def test_preservar_outras_chaves_ok(self):
        antes = {"a": 1, "b": 2, "chave_desconhecida": "x"}
        depois = pea.aplicar_chave(antes, "a", 99)
        self.assertTrue(pea.preservar_outras_chaves(antes, depois, "a"))

    def test_preservar_outras_chaves_detecta_alteracao_indevida(self):
        antes = {"a": 1, "b": 2}
        depois = {"a": 99, "b": 3}  # "b" tambem mudou -- nao deveria
        self.assertFalse(pea.preservar_outras_chaves(antes, depois, "a"))

    def test_preservar_outras_chaves_detecta_chave_removida(self):
        antes = {"a": 1, "b": 2}
        depois = {"a": 99}
        self.assertFalse(pea.preservar_outras_chaves(antes, depois, "a"))

    def test_serializacao_deterministica(self):
        saida = pea.serializar_estado({"b": 2, "a": 1})
        self.assertEqual(saida, '{\n  "a": 1,\n  "b": 2\n}\n')
        self.assertTrue(saida.endswith("\n"))
        self.assertEqual(json.loads(saida), {"a": 1, "b": 2})


class TestCarregarEstado(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="pea-carregar-")
        self.tmp_path = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_arquivo_ausente_falha_fechado(self):
        with self.assertRaises(pea.EstadoInvalidoError):
            pea.carregar_estado(str(self.tmp_path / "nao_existe.json"))

    def test_json_invalido_falha_fechado(self):
        caminho = self.tmp_path / "estado.json"
        caminho.write_text("{isto nao e json valido", encoding="utf-8")
        with self.assertRaises(pea.EstadoInvalidoError):
            pea.carregar_estado(str(caminho))

    def test_payload_nao_dict_falha_fechado(self):
        caminho = self.tmp_path / "estado.json"
        caminho.write_text("[1, 2, 3]", encoding="utf-8")
        with self.assertRaises(pea.EstadoInvalidoError):
            pea.carregar_estado(str(caminho))

    def test_payload_escalar_falha_fechado(self):
        caminho = self.tmp_path / "estado.json"
        caminho.write_text("42", encoding="utf-8")
        with self.assertRaises(pea.EstadoInvalidoError):
            pea.carregar_estado(str(caminho))

    def test_dict_valido_carrega(self):
        caminho = self.tmp_path / "estado.json"
        _escrever_json(caminho, {"comparar_modelos": 100})
        self.assertEqual(pea.carregar_estado(str(caminho)), {"comparar_modelos": 100})


# --------------------------------------------------------------------------
# Grupo 2: cenarios com Git real, mas 100% local (remote = bare repo em
# diretorio temporario). Nenhuma rede, nenhum GitHub real.
# --------------------------------------------------------------------------

ESTADO_SEED = {
    "avaliacao_final": 14058,
    "comparar_modelos": 14094,
    "multimodelo_classificacao": 14151,
    "transformer_ft": 14057,
    "chave_desconhecida_preexistente": "nao deve ser tocada",
}


class BaseGitTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="pea-git-")
        self.tmp_path = Path(self._tmp.name)

        self.remote = self.tmp_path / "remote.git"
        _git(["init", "--bare", "-b", "main", str(self.remote)])

        self.seed = self.tmp_path / "seed"
        _git(["clone", str(self.remote), str(self.seed)])
        _git(["config", "user.name", "seed"], cwd=self.seed)
        _git(["config", "user.email", "seed@example.com"], cwd=self.seed)

        _escrever_json(self.seed / "dados" / "estado_automacao.json", ESTADO_SEED)
        _git(["add", "dados/estado_automacao.json"], cwd=self.seed)
        _git(["commit", "-m", "estado inicial de teste"], cwd=self.seed)
        _git(["push", "origin", "main"], cwd=self.seed)

        self.cwd_a = self._clone("cwd-a")

    def tearDown(self):
        self._tmp.cleanup()

    def _clone(self, nome):
        destino = self.tmp_path / nome
        _git(["clone", str(self.remote), str(destino)])
        _git(["config", "user.name", nome], cwd=destino)
        _git(["config", "user.email", f"{nome}@example.com"], cwd=destino)
        return destino

    def _ler_estado_remoto(self):
        saida = _git(["show", "main:dados/estado_automacao.json"], cwd=self.remote)
        return json.loads(saida)

    def _sha_remoto(self):
        return _git(["rev-parse", "main"], cwd=self.remote).strip()

    def _worktrees_registrados(self, cwd):
        saida = _git(["worktree", "list", "--porcelain"], cwd=cwd)
        return [l.split(" ", 1)[1] for l in saida.splitlines() if l.startswith("worktree ")]

    def _empurrar_alteracao_direta(self, clone_dir, caminho_relativo, conteudo, mensagem):
        """Simula 'outro processo': escreve, comita e da push direto no remote."""
        alvo = clone_dir / caminho_relativo
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(conteudo, encoding="utf-8", newline="\n")
        _git(["add", "--", caminho_relativo], cwd=clone_dir)
        _git(["commit", "-m", mensagem], cwd=clone_dir)
        _git(["push", "origin", "main"], cwd=clone_dir)


class TestPersistenciaBasica(unittest.TestCase):
    pass  # agrupador; os testes reais ficam nas subclasses abaixo por clareza


class TestPushNormal(BaseGitTestCase):
    def test_push_normal_funciona_e_atualiza_so_a_chave_alvo(self):
        resultado = pea.persistir(
            "comparar_modelos", 99999,
            remote=str(self.remote), branch="main",
            cwd=str(self.cwd_a), aplicar=True,
        )
        self.assertEqual(resultado["status"], "ok")

        final = self._ler_estado_remoto()
        esperado = dict(ESTADO_SEED)
        esperado["comparar_modelos"] = 99999
        self.assertEqual(final, esperado)

    def test_preserva_as_outras_tres_chaves_e_a_desconhecida(self):
        pea.persistir(
            "avaliacao_final", 20000,
            remote=str(self.remote), cwd=str(self.cwd_a), aplicar=True,
        )
        final = self._ler_estado_remoto()
        self.assertEqual(final["avaliacao_final"], 20000)
        self.assertEqual(final["comparar_modelos"], ESTADO_SEED["comparar_modelos"])
        self.assertEqual(final["multimodelo_classificacao"], ESTADO_SEED["multimodelo_classificacao"])
        self.assertEqual(final["transformer_ft"], ESTADO_SEED["transformer_ft"])
        self.assertEqual(
            final["chave_desconhecida_preexistente"],
            ESTADO_SEED["chave_desconhecida_preexistente"],
        )

    def test_commit_altera_somente_o_arquivo_de_estado(self):
        resultado = pea.persistir(
            "transformer_ft", 15000,
            remote=str(self.remote), cwd=str(self.cwd_a), aplicar=True,
        )
        arquivos = _git(
            ["diff-tree", "--no-commit-id", "--name-only", "-r", resultado["commit"]],
            cwd=self.remote,
        ).splitlines()
        self.assertEqual(arquivos, ["dados/estado_automacao.json"])

    def test_mensagem_de_commit_no_padrao_esperado(self):
        resultado = pea.persistir(
            "multimodelo_classificacao", 16000,
            remote=str(self.remote), cwd=str(self.cwd_a), aplicar=True,
        )
        msg = _git(["log", "-1", "--format=%s", resultado["commit"]], cwd=self.remote).strip()
        self.assertEqual(msg, "estado automacao: multimodelo_classificacao [skip ci]")


class TestNoOp(BaseGitTestCase):
    def test_no_op_nao_cria_commit(self):
        sha_antes = self._sha_remoto()
        resultado = pea.persistir(
            "comparar_modelos", ESTADO_SEED["comparar_modelos"],
            remote=str(self.remote), cwd=str(self.cwd_a), aplicar=True,
        )
        self.assertEqual(resultado["status"], "no-op")
        self.assertEqual(self._sha_remoto(), sha_antes)


class TestAllowlistStaging(BaseGitTestCase):
    def test_staging_fora_da_allowlist_falha(self):
        _escrever_json(self.cwd_a / "dados" / "estado_automacao.json", dict(ESTADO_SEED))
        (self.cwd_a / "arquivo_inesperado.txt").write_text("nao deveria estar aqui", encoding="utf-8")
        _git(["add", "dados/estado_automacao.json"], cwd=self.cwd_a)
        # arquivo_inesperado.txt fica untracked, sem git add -- e mesmo assim
        # deve ser detectado, pois git status --porcelain lista untracked tambem.
        with self.assertRaises(pea.GitError):
            pea._verificar_staging_exclusivo(str(self.cwd_a), pea.ESTADO_RELATIVO)

    def test_staging_so_do_arquivo_de_estado_passa(self):
        _escrever_json(self.cwd_a / "dados" / "estado_automacao.json", dict(ESTADO_SEED, comparar_modelos=1))
        _git(["add", "dados/estado_automacao.json"], cwd=self.cwd_a)
        pea._verificar_staging_exclusivo(str(self.cwd_a), pea.ESTADO_RELATIVO)  # nao deve levantar


class TestSemArgumentosGitProibidos(unittest.TestCase):
    @staticmethod
    def _codigo_executavel():
        """Remove docstrings e comentarios: o modulo EXPLICA em prosa por que
        nao usa rebase/stash/-X theirs (contendo esses termos como texto), o
        que e diferente de invoca-los. So o codigo executavel importa aqui.
        """
        codigo = (Path(__file__).resolve().parents[1] / "src" / "persistir_estado_automacao.py").read_text(
            encoding="utf-8"
        )
        dentro_docstring = False
        linhas = []
        for linha in codigo.splitlines():
            n = linha.count('"""')
            if n % 2 == 1:
                dentro_docstring = not dentro_docstring
                continue
            if n >= 2 or dentro_docstring:
                continue
            if linha.strip().startswith("#"):
                continue
            linhas.append(linha)
        return "\n".join(linhas)

    def test_codigo_executavel_nao_contem_comandos_proibidos(self):
        codigo = self._codigo_executavel()
        proibidos = [
            "push -f",
            "reset --hard",
            "git stash",
            "\"stash\"",
            "'stash'",
            "-X theirs",
            "-X ours",
            "\"rebase\"",
            "'rebase'",
            "\"add\", \".\"",
            "'add', '.'",
            "\"add\", \"-A\"",
            "'add', '-A'",
        ]
        for termo in proibidos:
            self.assertNotIn(termo, codigo, f"comando proibido encontrado em codigo executavel: {termo!r}")

    def test_unico_uso_de_force_e_worktree_remove(self):
        # "--force" so pode aparecer preso a "worktree"+"remove" na mesma
        # linha (limpeza do proprio worktree temporario) -- nunca junto de
        # "push" ou "reset".
        codigo = self._codigo_executavel()
        for linha in codigo.splitlines():
            if "--force" in linha:
                self.assertIn("worktree", linha)
                self.assertIn("remove", linha)
                self.assertNotIn("push", linha)
                self.assertNotIn("reset", linha)


class TestCorridaConcorrente(BaseGitTestCase):
    def test_corrida_real_duas_chaves_sobrevivem(self):
        """O teste mais importante do lote (secao 12, item 13 do 8H-B1).

        Helper A prepara localmente uma alteracao de 'comparar_modelos'.
        Antes do push de A, outro clone atualiza 'avaliacao_final' e
        consegue publicar primeiro. O push de A e rejeitado
        (non-fast-forward); A refaz fetch, relê o estado (que ja contem a
        atualizacao concorrente), reaplica so a sua propria chave e publica
        com sucesso. O estado final deve conter as DUAS atualizacoes.
        """
        chamadas = {"n": 0}

        def before_push(_worktree):
            chamadas["n"] += 1
            if chamadas["n"] == 1:
                outro_clone = self._clone("cwd-b-concorrente")
                estado = json.loads(
                    (outro_clone / "dados" / "estado_automacao.json").read_text(encoding="utf-8")
                )
                estado["avaliacao_final"] = 77777
                _escrever_json(outro_clone / "dados" / "estado_automacao.json", estado)
                _git(["add", "dados/estado_automacao.json"], cwd=outro_clone)
                _git(["commit", "-m", "estado automacao: avaliacao_final [skip ci]"], cwd=outro_clone)
                _git(["push", "origin", "main"], cwd=outro_clone)

        resultado = pea.persistir(
            "comparar_modelos", 55555,
            remote=str(self.remote), cwd=str(self.cwd_a),
            aplicar=True, before_push=before_push,
        )

        self.assertEqual(resultado["status"], "ok")
        self.assertGreaterEqual(chamadas["n"], 2)  # houve pelo menos uma rejeicao + retry

        final = self._ler_estado_remoto()
        self.assertEqual(final["comparar_modelos"], 55555)
        self.assertEqual(final["avaliacao_final"], 77777)
        # as duas chaves nao tocadas por nenhum dos dois lados continuam intactas.
        self.assertEqual(final["multimodelo_classificacao"], ESTADO_SEED["multimodelo_classificacao"])
        self.assertEqual(final["transformer_ft"], ESTADO_SEED["transformer_ft"])
        self.assertEqual(
            final["chave_desconhecida_preexistente"],
            ESTADO_SEED["chave_desconhecida_preexistente"],
        )

    def test_avanco_remoto_em_arquivo_nao_relacionado_e_preservado(self):
        chamadas = {"n": 0}

        def before_push(_worktree):
            chamadas["n"] += 1
            if chamadas["n"] == 1:
                outro_clone = self._clone("cwd-c-nao-relacionado")
                self._empurrar_alteracao_direta(
                    outro_clone,
                    "outro_arquivo_nao_relacionado.txt",
                    "conteudo de um commit concorrente, arquivo nao relacionado\n",
                    "commit concorrente em arquivo fora da allowlist deste helper",
                )

        resultado = pea.persistir(
            "transformer_ft", 33333,
            remote=str(self.remote), cwd=str(self.cwd_a),
            aplicar=True, before_push=before_push,
        )

        self.assertEqual(resultado["status"], "ok")
        conteudo_concorrente = _git(
            ["show", "main:outro_arquivo_nao_relacionado.txt"], cwd=self.remote
        )
        self.assertIn("commit concorrente", conteudo_concorrente)

        final = self._ler_estado_remoto()
        self.assertEqual(final["transformer_ft"], 33333)


class TestCleanupDeWorktrees(BaseGitTestCase):
    def test_nenhum_worktree_abandonado_apos_sucesso(self):
        pea.persistir(
            "comparar_modelos", 12345,
            remote=str(self.remote), cwd=str(self.cwd_a), aplicar=True,
        )
        registrados = self._worktrees_registrados(self.cwd_a)
        self.assertEqual(len(registrados), 1)  # so o proprio cwd_a

    def test_nenhum_worktree_abandonado_apos_falha_controlada(self):
        chamadas = {"n": 0}

        def before_push_sempre_conflita(_worktree):
            chamadas["n"] += 1
            outro_clone = self._clone(f"cwd-d-{chamadas['n']}")
            self._empurrar_alteracao_direta(
                outro_clone,
                "arquivo_de_conflito.txt",
                f"muda a cada tentativa: {chamadas['n']}\n",
                f"commit concorrente que sempre chega primeiro ({chamadas['n']})",
            )

        with self.assertRaises(pea.PersistenciaFalhouError):
            pea.persistir(
                "comparar_modelos", 999,
                remote=str(self.remote), cwd=str(self.cwd_a),
                aplicar=True, max_tentativas=2,
                before_push=before_push_sempre_conflita,
            )

        registrados = self._worktrees_registrados(self.cwd_a)
        self.assertEqual(len(registrados), 1)  # so o proprio cwd_a, nada abandonado


class TestDryRun(BaseGitTestCase):
    def test_dry_run_nao_da_push_nem_commit(self):
        sha_antes = self._sha_remoto()
        resultado = pea.persistir(
            "comparar_modelos", 55555,
            remote=str(self.remote), cwd=str(self.cwd_a), aplicar=False,
        )
        self.assertEqual(resultado["status"], "dry-run")
        self.assertEqual(self._sha_remoto(), sha_antes)
        registrados = self._worktrees_registrados(self.cwd_a)
        self.assertEqual(len(registrados), 1)

    def test_dry_run_detecta_no_op(self):
        resultado = pea.persistir(
            "comparar_modelos", ESTADO_SEED["comparar_modelos"],
            remote=str(self.remote), cwd=str(self.cwd_a), aplicar=False,
        )
        self.assertEqual(resultado["status"], "no-op")

    def test_aplicar_e_false_por_padrao_sem_informar_o_argumento(self):
        # Chamada programatica SEM aplicar=True: precisa se comportar como
        # dry-run mesmo sem ninguem pedir explicitamente -- opt-in, nao
        # opt-out. Nenhum commit/push pode acontecer por omissao.
        sha_antes = self._sha_remoto()
        novo_valor = ESTADO_SEED["comparar_modelos"] + 1

        resultado = pea.persistir(
            "comparar_modelos", novo_valor,
            remote=str(self.remote), cwd=str(self.cwd_a),
        )

        self.assertEqual(resultado["status"], "dry-run")
        self.assertEqual(self._sha_remoto(), sha_antes)
        registrados = self._worktrees_registrados(self.cwd_a)
        self.assertEqual(len(registrados), 1)  # nenhum worktree abandonado


if __name__ == "__main__":
    unittest.main()
