#!/usr/bin/env python3
"""Testes do lote A3-2: `src/filtrar_noop_dashboard.py` restaura para HEAD os
JSONs de docs/dados cuja unica mudanca seja o campo `gerado_em` no nivel
superior, sem `git checkout`/`restore`/`reset`, e sem tocar em nenhum outro
tipo de divergencia. Cobre a logica pura (sem Git), o uso de HEAD via `git
show` em um repositorio local temporario, o CLI, a regressao historica do
padrao observado em commits "dados do dashboard [skip ci]" e um teste
estatico de que a integracao em dashboard.yml preserva triggers/allowlist e
chama o helper antes do `git add`.

Nenhum teste acessa rede, planilha real ou GitHub Actions.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import filtrar_noop_dashboard as fnd  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
WORKFLOWS = RAIZ / ".github" / "workflows"


def _git(args, cwd):
    resultado = subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True
    )
    if resultado.returncode != 0:
        raise RuntimeError(f"git {args} falhou: {resultado.stderr}")
    return resultado.stdout


# --------------------------------------------------------------------------
# Grupo 1: logica semantica pura -- sem Git.
# --------------------------------------------------------------------------

class TestValidarPath(unittest.TestCase):
    def test_path_valido_aceito(self):
        p = fnd.validar_path("docs/dados/calibracao.json")
        self.assertEqual(p.as_posix(), "docs/dados/calibracao.json")

    def test_path_absoluto_rejeitado(self):
        with self.assertRaises(fnd.PathRejeitadoError):
            fnd.validar_path("/etc/passwd")

    def test_path_absoluto_windows_rejeitado(self):
        with self.assertRaises(fnd.PathRejeitadoError):
            fnd.validar_path("C:/Windows/system.json")

    def test_travessia_diretorio_rejeitada(self):
        with self.assertRaises(fnd.PathRejeitadoError):
            fnd.validar_path("docs/dados/../../etc/passwd.json")

    def test_fora_de_docs_dados_rejeitado(self):
        with self.assertRaises(fnd.PathRejeitadoError):
            fnd.validar_path("src/filtrar_noop_dashboard.py")

    def test_extensao_diferente_de_json_rejeitada(self):
        with self.assertRaises(fnd.PathRejeitadoError):
            fnd.validar_path("docs/dados/mapa.csv")

    def test_diretorio_nao_aceito(self):
        with self.assertRaises(fnd.PathRejeitadoError):
            fnd.validar_path("docs/dados/")


class TestEhApenasGeradoEmDiferente(unittest.TestCase):
    def test_somente_gerado_em_muda(self):
        baseline = {"gerado_em": "19/08/2026 19:59", "total": 100, "taxa": 0.91}
        novo = {"gerado_em": "19/08/2026 20:29", "total": 100, "taxa": 0.91}
        self.assertTrue(fnd.eh_apenas_gerado_em_diferente(baseline, novo))

    def test_gerado_em_e_valor_substantivo_mudam(self):
        baseline = {"gerado_em": "19/08/2026 19:59", "total": 100}
        novo = {"gerado_em": "19/08/2026 20:29", "total": 101}
        self.assertFalse(fnd.eh_apenas_gerado_em_diferente(baseline, novo))

    def test_gerado_em_aninhado_muda_nao_aplica_excecao(self):
        baseline = {"gerado_em": "19/08/2026 19:59", "objeto": {"gerado_em": "a"}}
        novo = {"gerado_em": "19/08/2026 20:29", "objeto": {"gerado_em": "b"}}
        self.assertFalse(fnd.eh_apenas_gerado_em_diferente(baseline, novo))

    def test_gerado_em_so_no_novo(self):
        baseline = {"total": 100}
        novo = {"gerado_em": "19/08/2026 20:29", "total": 100}
        self.assertFalse(fnd.eh_apenas_gerado_em_diferente(baseline, novo))

    def test_gerado_em_so_no_baseline(self):
        baseline = {"gerado_em": "19/08/2026 19:59", "total": 100}
        novo = {"total": 100}
        self.assertFalse(fnd.eh_apenas_gerado_em_diferente(baseline, novo))

    def test_lista_no_topo_nao_aplica_excecao(self):
        baseline = [{"modelo": "a", "gerado_em": "x"}]
        novo = [{"modelo": "a", "gerado_em": "y"}]
        self.assertFalse(fnd.eh_apenas_gerado_em_diferente(baseline, novo))

    def test_escalar_no_topo_nao_aplica_excecao(self):
        self.assertFalse(fnd.eh_apenas_gerado_em_diferente(42, 42))


# --------------------------------------------------------------------------
# Grupo 2: processar_path sobre um repositorio Git local temporario.
# --------------------------------------------------------------------------

class BaseRepoTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="fnd-repo-")
        self.repo = Path(self._tmp.name)
        _git(["init", "-b", "main", str(self.repo)], cwd=self.repo.parent)
        _git(["config", "user.name", "teste"], cwd=self.repo)
        _git(["config", "user.email", "teste@example.com"], cwd=self.repo)
        (self.repo / "docs" / "dados").mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def _commitar(self, rel_path: str, conteudo: str, mensagem="seed"):
        alvo = self.repo / rel_path
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(conteudo, encoding="utf-8")
        _git(["add", "--", rel_path], cwd=self.repo)
        _git(["commit", "-m", mensagem], cwd=self.repo)

    def _escrever_sem_commit(self, rel_path: str, conteudo: str):
        alvo = self.repo / rel_path
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(conteudo, encoding="utf-8")

    def _ler(self, rel_path: str) -> str:
        return (self.repo / rel_path).read_text(encoding="utf-8")


class TestProcessarPathCasos(BaseRepoTestCase):
    def test_caso_a_restaura_baseline_quando_so_gerado_em_muda(self):
        rel = "docs/dados/calibracao.json"
        self._commitar(rel, json.dumps({"gerado_em": "19/08/2026 19:59", "total": 100}))
        self._escrever_sem_commit(rel, json.dumps({"gerado_em": "19/08/2026 20:29", "total": 100}))

        path_norm, status = fnd.processar_path(rel, cwd=self.repo)

        self.assertEqual(status, fnd.STATUS_VOLATIL_RESTAURADO)
        self.assertEqual(path_norm, rel)
        self.assertEqual(json.loads(self._ler(rel)), {"gerado_em": "19/08/2026 19:59", "total": 100})

    def test_caso_b_mantem_quando_ha_mudanca_substantiva(self):
        rel = "docs/dados/calibracao.json"
        self._commitar(rel, json.dumps({"gerado_em": "19/08/2026 19:59", "total": 100}))
        novo_conteudo = json.dumps({"gerado_em": "19/08/2026 20:29", "total": 101})
        self._escrever_sem_commit(rel, novo_conteudo)

        _path_norm, status = fnd.processar_path(rel, cwd=self.repo)

        self.assertEqual(status, fnd.STATUS_SUBSTANTIVO)
        self.assertEqual(self._ler(rel), novo_conteudo)

    def test_caso_c_arquivo_novo_sem_baseline_permanece(self):
        rel = "docs/dados/novo_arquivo.json"
        conteudo = json.dumps({"gerado_em": "19/08/2026 20:29", "total": 1})
        self._escrever_sem_commit(rel, conteudo)

        _path_norm, status = fnd.processar_path(rel, cwd=self.repo)

        self.assertEqual(status, fnd.STATUS_NOVO)
        self.assertEqual(self._ler(rel), conteudo)

    def test_caso_d_arquivo_removido_nao_e_restaurado(self):
        rel = "docs/dados/resumo.json"
        self._commitar(rel, json.dumps({"gerado_em": "19/08/2026 19:59", "total": 100}))
        (self.repo / rel).unlink()

        _path_norm, status = fnd.processar_path(rel, cwd=self.repo)

        self.assertEqual(status, fnd.STATUS_SUBSTANTIVO)
        self.assertFalse((self.repo / rel).exists())

    def test_caso_e_json_invalido_no_novo_falha_fechado_e_preserva(self):
        rel = "docs/dados/calibracao.json"
        self._commitar(rel, json.dumps({"gerado_em": "19/08/2026 19:59", "total": 100}))
        conteudo_quebrado = "{isto nao e json valido"
        self._escrever_sem_commit(rel, conteudo_quebrado)

        with self.assertRaises(fnd.JsonInvalidoError):
            fnd.processar_path(rel, cwd=self.repo)

        self.assertEqual(self._ler(rel), conteudo_quebrado)

    def test_caso_e_json_invalido_no_baseline_falha_fechado_e_preserva_novo(self):
        rel = "docs/dados/calibracao.json"
        self._commitar(rel, "{isto no head nao e json valido")
        conteudo_novo = json.dumps({"gerado_em": "19/08/2026 20:29", "total": 1})
        self._escrever_sem_commit(rel, conteudo_novo)

        with self.assertRaises(fnd.JsonInvalidoError):
            fnd.processar_path(rel, cwd=self.repo)

        self.assertEqual(self._ler(rel), conteudo_novo)

    def test_caso_f_lista_modificada_nao_aplica_excecao(self):
        rel = "docs/dados/multimodelo_metricas.json"
        self._commitar(rel, json.dumps([{"modelo": "a", "atualizado_em": "x"}]))
        novo_conteudo = json.dumps([{"modelo": "a", "atualizado_em": "y"}])
        self._escrever_sem_commit(rel, novo_conteudo)

        _path_norm, status = fnd.processar_path(rel, cwd=self.repo)

        self.assertEqual(status, fnd.STATUS_SUBSTANTIVO)
        self.assertEqual(self._ler(rel), novo_conteudo)

    def test_caso_g_gerado_em_so_no_novo_nao_restaura(self):
        rel = "docs/dados/resumo.json"
        self._commitar(rel, json.dumps({"total": 100}))
        novo_conteudo = json.dumps({"gerado_em": "19/08/2026 20:29", "total": 100})
        self._escrever_sem_commit(rel, novo_conteudo)

        _path_norm, status = fnd.processar_path(rel, cwd=self.repo)

        self.assertEqual(status, fnd.STATUS_SUBSTANTIVO)
        self.assertEqual(self._ler(rel), novo_conteudo)

    def test_caso_g_gerado_em_so_no_baseline_nao_restaura(self):
        rel = "docs/dados/resumo.json"
        self._commitar(rel, json.dumps({"gerado_em": "19/08/2026 19:59", "total": 100}))
        novo_conteudo = json.dumps({"total": 100})
        self._escrever_sem_commit(rel, novo_conteudo)

        _path_norm, status = fnd.processar_path(rel, cwd=self.repo)

        self.assertEqual(status, fnd.STATUS_SUBSTANTIVO)
        self.assertEqual(self._ler(rel), novo_conteudo)

    def test_caso_h_gerado_em_aninhado_muda_nao_restaura(self):
        rel = "docs/dados/comparacao_categoria.json"
        self._commitar(rel, json.dumps({"gerado_em": "19/08/2026 19:59", "obj": {"gerado_em": "a"}}))
        novo_conteudo = json.dumps({"gerado_em": "19/08/2026 20:29", "obj": {"gerado_em": "b"}})
        self._escrever_sem_commit(rel, novo_conteudo)

        _path_norm, status = fnd.processar_path(rel, cwd=self.repo)

        self.assertEqual(status, fnd.STATUS_SUBSTANTIVO)
        self.assertEqual(self._ler(rel), novo_conteudo)

    def test_path_fora_de_docs_dados_rejeitado_em_processar_path(self):
        with self.assertRaises(fnd.PathRejeitadoError):
            fnd.processar_path("outra_pasta/arquivo.json", cwd=self.repo)

    def test_path_com_travessia_rejeitado_em_processar_path(self):
        with self.assertRaises(fnd.PathRejeitadoError):
            fnd.processar_path("docs/dados/../../fora.json", cwd=self.repo)

    def test_path_nao_json_rejeitado_em_processar_path(self):
        with self.assertRaises(fnd.PathRejeitadoError):
            fnd.processar_path("docs/dados/mapa.csv", cwd=self.repo)

    def test_idempotencia_segunda_execucao_nao_muda_nada(self):
        rel = "docs/dados/calibracao.json"
        self._commitar(rel, json.dumps({"gerado_em": "19/08/2026 19:59", "total": 100}))
        self._escrever_sem_commit(rel, json.dumps({"gerado_em": "19/08/2026 20:29", "total": 100}))

        fnd.processar_path(rel, cwd=self.repo)
        conteudo_apos_primeira = self._ler(rel)
        _path_norm, status_segunda = fnd.processar_path(rel, cwd=self.repo)

        self.assertEqual(status_segunda, fnd.STATUS_VOLATIL_RESTAURADO)
        self.assertEqual(self._ler(rel), conteudo_apos_primeira)

    def test_bytes_restaurados_sao_exatamente_os_bytes_do_head(self):
        rel = "docs/dados/calibracao.json"
        conteudo_head = '{"gerado_em": "19/08/2026 19:59", "total": 100}'
        self._commitar(rel, conteudo_head)
        self._escrever_sem_commit(rel, '{"gerado_em": "19/08/2026 20:29", "total": 100}')

        fnd.processar_path(rel, cwd=self.repo)

        bytes_head = subprocess.run(
            ["git", "show", f"HEAD:{rel}"], cwd=self.repo, capture_output=True, check=True
        ).stdout
        self.assertEqual((self.repo / rel).read_bytes(), bytes_head)

    def test_multiplos_paths_mistos_restaura_apenas_os_noop(self):
        rel_a = "docs/dados/calibracao.json"
        rel_b = "docs/dados/resumo.json"
        rel_c = "docs/dados/shannon_resumo.json"
        self._commitar(rel_a, json.dumps({"gerado_em": "t1", "total": 100}), mensagem="seed a")
        self._commitar(rel_b, json.dumps({"gerado_em": "t1", "total": 1}), mensagem="seed b")
        self._commitar(rel_c, json.dumps({"gerado_em": "t1", "total": 9}), mensagem="seed c")

        self._escrever_sem_commit(rel_a, json.dumps({"gerado_em": "t2", "total": 100}))  # noop
        novo_b = json.dumps({"gerado_em": "t2", "total": 2})  # substantivo
        self._escrever_sem_commit(rel_b, novo_b)
        self._escrever_sem_commit(rel_c, json.dumps({"gerado_em": "t2", "total": 9}))  # noop

        resultados = {}
        for rel in (rel_a, rel_b, rel_c):
            _p, status = fnd.processar_path(rel, cwd=self.repo)
            resultados[rel] = status

        self.assertEqual(resultados[rel_a], fnd.STATUS_VOLATIL_RESTAURADO)
        self.assertEqual(resultados[rel_b], fnd.STATUS_SUBSTANTIVO)
        self.assertEqual(resultados[rel_c], fnd.STATUS_VOLATIL_RESTAURADO)

        self.assertEqual(json.loads(self._ler(rel_a)), {"gerado_em": "t1", "total": 100})
        self.assertEqual(self._ler(rel_b), novo_b)
        self.assertEqual(json.loads(self._ler(rel_c)), {"gerado_em": "t1", "total": 9})

        status_git = _git(["status", "--porcelain", "--", "docs/dados"], cwd=self.repo)
        alterados = [l[3:] for l in status_git.splitlines() if l.strip()]
        self.assertEqual(alterados, [rel_b])


# --------------------------------------------------------------------------
# Grupo 3: regressao historica -- reproduz semanticamente o padrao observado
# no commit 525edb3466481850155bd80381ad61ad01ea5cd6 ("dados do dashboard
# [skip ci]"), onde calibracao.json mudou so em "gerado_em".
# --------------------------------------------------------------------------

class TestRegressaoHistoricaGeradoEmOnly(BaseRepoTestCase):
    def test_padrao_commit_525edb34_fica_sem_diff(self):
        rel = "docs/dados/calibracao.json"
        antes = {
            "gerado_em": "19/08/2026 19:59",
            "run_id": "EXP_CLASSIFICACAO_CHAMADOS_2026_06_001",
            "total": 14160,
            "validados": 14057,
            "acerto_ia_validado": 0.9198,
        }
        depois = dict(antes, **{"gerado_em": "19/08/2026 20:01"})
        self._commitar(rel, json.dumps(antes))
        self._escrever_sem_commit(rel, json.dumps(depois))

        _path_norm, status = fnd.processar_path(rel, cwd=self.repo)

        self.assertEqual(status, fnd.STATUS_VOLATIL_RESTAURADO)
        status_git = _git(["status", "--porcelain", "--", rel], cwd=self.repo)
        self.assertEqual(status_git.strip(), "", "arquivo deveria estar sem diff apos a restauracao")


# --------------------------------------------------------------------------
# Grupo 4: CLI (main).
# --------------------------------------------------------------------------

class TestCli(BaseRepoTestCase):
    def _rodar_no_repo(self, argv):
        cwd_antigo = Path.cwd()
        try:
            os.chdir(self.repo)
            return fnd.main(argv)
        finally:
            os.chdir(cwd_antigo)

    def test_cli_sem_argumentos_retorna_erro(self):
        self.assertEqual(fnd.main([]), 2)

    def test_cli_restaura_e_retorna_zero(self):
        rel = "docs/dados/calibracao.json"
        self._commitar(rel, json.dumps({"gerado_em": "t1", "total": 100}))
        self._escrever_sem_commit(rel, json.dumps({"gerado_em": "t2", "total": 100}))

        codigo = self._rodar_no_repo(["--", rel])

        self.assertEqual(codigo, 0)
        self.assertEqual(json.loads(self._ler(rel)), {"gerado_em": "t1", "total": 100})

    def test_cli_json_invalido_retorna_nao_zero(self):
        rel = "docs/dados/calibracao.json"
        self._commitar(rel, json.dumps({"gerado_em": "t1", "total": 100}))
        self._escrever_sem_commit(rel, "{quebrado")

        codigo = self._rodar_no_repo(["--", rel])

        self.assertNotEqual(codigo, 0)
        self.assertEqual(self._ler(rel), "{quebrado")

    def test_cli_path_rejeitado_retorna_nao_zero(self):
        codigo = self._rodar_no_repo(["--", "fora/de/docs_dados.json"])
        self.assertNotEqual(codigo, 0)


# --------------------------------------------------------------------------
# Grupo 5: teste estatico de dashboard.yml (so leitura, sem executar nada).
# --------------------------------------------------------------------------

class TestIntegracaoDashboardYml(unittest.TestCase):
    def setUp(self):
        self.texto = (WORKFLOWS / "dashboard.yml").read_text(encoding="utf-8")
        import yaml
        with (WORKFLOWS / "dashboard.yml").open(encoding="utf-8") as f:
            self.doc = yaml.safe_load(f)
        self.on = self.doc["on"] if "on" in self.doc else self.doc[True]

    def test_schedule_30min_inalterado(self):
        self.assertEqual(self.on["schedule"][0]["cron"], "*/30 * * * *")

    def test_workflow_run_upstreams_inalterados(self):
        self.assertEqual(
            self.on["workflow_run"]["workflows"],
            [
                "Comparar modelos (lote)",
                "Multimodelo - reclassificacao",
                "Transformer fine-tuning (BERTimbau)",
            ],
        )

    def test_workflow_dispatch_presente(self):
        self.assertIn("workflow_dispatch", self.on)

    def test_concurrency_inalterada(self):
        self.assertEqual(self.doc["concurrency"]["group"], "escrita-planilha")
        self.assertEqual(self.doc["concurrency"]["cancel-in-progress"], False)

    def test_permissions_inalteradas(self):
        self.assertEqual(self.doc["permissions"]["contents"], "write")

    def test_chama_o_helper(self):
        self.assertIn("python src/filtrar_noop_dashboard.py -- ", self.texto)

    def test_helper_chamado_antes_do_git_add(self):
        idx_helper = self.texto.index("filtrar_noop_dashboard.py")
        idx_git_add = self.texto.index('git add -- "${STAGE_LIST[@]}"')
        self.assertLess(idx_helper, idx_git_add)

    def test_releitura_do_git_status_apos_o_helper(self):
        idx_helper = self.texto.index("filtrar_noop_dashboard.py")
        trecho_apos = self.texto[idx_helper:]
        self.assertIn("git status --porcelain -- docs/dados", trecho_apos)

    def test_staging_continua_por_allowlist_explicita(self):
        self.assertIn("validar_e_montar_stage", self.texto)
        self.assertIn("BLOQUEADO: arquivo(s) inesperado(s) alterado(s) em docs/dados", self.texto)

    def test_allowlist_fixas_inalterada(self):
        esperado = [
            "log_turnos_classificacao.json",
            "metricas_por_categoria.json",
            "log_turnos_reclassificacao.json",
            "metricas_experimento.json",
            "comparacao_modelos.json",
            "comparacao_categoria.json",
            "multimodelo_turnos.json",
            "multimodelo_metricas.json",
            "multimodelo_reclass_turnos.json",
            "comparacao_previsoes.json",
            "reclass_resumo.json",
            "calibracao.json",
            "registros.json",
            "calibracao_modelos.json",
            "calibracao_ajustada_modelos.json",
            "resumo.json",
            "shannon_resumo.json",
            "shannon_modelos.json",
            "jensen_shannon_modelos.json",
            "shannon_categorias.json",
            "shannon_votos.json",
        ]
        for nome in esperado:
            self.assertIn(nome, self.texto)

    def test_produtores_de_dados_inalterados(self):
        self.assertIn("run: python src/exportar_dashboard.py", self.texto)
        self.assertIn("run: python src/analise_shannon.py", self.texto)

    def test_sem_git_add_dot_ou_dash_a(self):
        self.assertNotIn("git add .", self.texto)
        self.assertNotIn("git add -A", self.texto)

    def test_sem_theirs_ours_ou_force_em_codigo_executavel(self):
        # Linhas de comentario (que so explicam a ausencia desses padroes) sao
        # ignoradas; o que importa e nao haver uso executavel real.
        linhas_codigo = "\n".join(
            l for l in self.texto.splitlines() if not l.strip().startswith("#")
        )
        for proibido in ("-X theirs", "-X ours", "push --force", "reset --hard"):
            self.assertNotIn(proibido, linhas_codigo)


if __name__ == "__main__":
    unittest.main()
