#!/usr/bin/env python3
"""Teste estatico dos 4 workflows que escrevem dados/estado_automacao.json
(Lote 8H-B2): confirma, so por leitura dos YAML, que cada um migrou do
mecanismo antigo (guard_automacao.py --registrar + git add/commit + git pull
--rebase/-X theirs/--autostash) para src/persistir_estado_automacao.py
--aplicar, com a chave e o valor corretos, e que dados/estado_automacao.json
nao aparece mais em nenhum `git add` do repositorio.

Nenhum workflow e executado, nenhuma rede e usada -- so leitura de YAML.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[1]
WORKFLOWS = RAIZ / ".github" / "workflows"


def carregar_yaml(caminho: Path) -> dict:
    with caminho.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def blocos_run(doc: dict) -> str:
    """Concatena o conteudo de todos os blocos run: de todos os jobs/steps."""
    partes = []
    for job in (doc.get("jobs") or {}).values():
        for step in job.get("steps") or []:
            if isinstance(step, dict) and "run" in step:
                partes.append(str(step["run"]))
    return "\n".join(partes)


def linhas_git_add(texto: str) -> list[str]:
    return re.findall(r"^\s*git add (.+)$", texto, re.MULTILINE)


CASOS = [
    {
        "arquivo": "comparar_modelos.yml",
        "chave": "comparar_modelos",
        "commit_proprio": None,
    },
    {
        "arquivo": "multimodelo_classificacao.yml",
        "chave": "multimodelo_classificacao",
        "commit_proprio": None,
    },
    {
        "arquivo": "avaliacao_final.yml",
        "chave": "avaliacao_final",
        "commit_proprio": {"docs/dados/avaliacao_final.json", "docs/dados/analise_erros.json"},
    },
    {
        "arquivo": "transformer_ft.yml",
        "chave": "transformer_ft",
        "commit_proprio": {"docs/dados/bertimbau_training_state.json"},
    },
]

VALOR_ESPERADO = {
    "comparar_modelos.yml": "needs.guard.outputs.valor_atual",
    "multimodelo_classificacao.yml": "needs.guard.outputs.valor_atual",
    "avaliacao_final.yml": "needs.guard.outputs.valor_atual",
    "transformer_ft.yml": "needs.preparar.outputs.valor_atual",
}


def _carregar(nome: str):
    doc = carregar_yaml(WORKFLOWS / nome)
    return doc, blocos_run(doc)


class TestOsQuatroWorkflowsExistem(unittest.TestCase):
    def test_arquivos_existem(self):
        for caso in CASOS:
            self.assertTrue((WORKFLOWS / caso["arquivo"]).is_file(), caso["arquivo"])


class TestInvocaOHelperComChaveEAplicar(unittest.TestCase):
    def test_chama_o_helper_com_chave_e_aplicar_corretos(self):
        for caso in CASOS:
            with self.subTest(arquivo=caso["arquivo"]):
                _doc, texto = _carregar(caso["arquivo"])
                self.assertIn("persistir_estado_automacao.py", texto)
                self.assertIn(f"--chave {caso['chave']}", texto)
                self.assertIn("--aplicar", texto)

    def test_valor_referencia_a_saida_correta_da_guarda(self):
        for caso in CASOS:
            with self.subTest(arquivo=caso["arquivo"]):
                _doc, texto = _carregar(caso["arquivo"])
                achado = re.search(r"--valor\s+['\"]?\$\{\{([^}]*)\}\}", texto)
                self.assertIsNotNone(achado, f"nenhum --valor '${{{{ ... }}}}' em {caso['arquivo']}")
                self.assertIn(VALOR_ESPERADO[caso["arquivo"]], achado.group(1))


class TestMecanismoAntigoRemovido(unittest.TestCase):
    def test_nao_chama_mais_guard_registrar_para_essa_chave(self):
        for caso in CASOS:
            with self.subTest(arquivo=caso["arquivo"]):
                _doc, texto = _carregar(caso["arquivo"])
                self.assertNotIn("--registrar", texto)

    def test_nenhum_git_add_inclui_estado_automacao(self):
        for caso in CASOS:
            with self.subTest(arquivo=caso["arquivo"]):
                _doc, texto = _carregar(caso["arquivo"])
                for linha in linhas_git_add(texto):
                    self.assertNotIn("dados/estado_automacao.json", linha)

    def test_workflows_sem_artefato_proprio_nao_tem_mais_bloco_git_de_estado(self):
        for caso in CASOS:
            if caso["commit_proprio"] is not None:
                continue
            with self.subTest(arquivo=caso["arquivo"]):
                _doc, texto = _carregar(caso["arquivo"])
                self.assertNotIn("git commit", texto)
                self.assertNotIn("git push", texto)
                self.assertNotIn("git pull", texto)
                self.assertNotIn("-X theirs", texto)
                self.assertNotIn("-X ours", texto)
                self.assertNotIn("--autostash", texto)


class TestCommitProprioRestritoAosArtefatosDoWorkflow(unittest.TestCase):
    def test_git_add_do_artefato_proprio_nao_inclui_estado(self):
        for caso in CASOS:
            if caso["commit_proprio"] is None:
                continue
            with self.subTest(arquivo=caso["arquivo"]):
                _doc, texto = _carregar(caso["arquivo"])
                linhas = linhas_git_add(texto)
                self.assertEqual(len(linhas), 1, f"esperado exatamente 1 'git add' em {caso['arquivo']}, achado: {linhas}")
                caminhos = set(linhas[0].split())
                self.assertEqual(caminhos, caso["commit_proprio"])


class TestOrdemPersistirDepoisDoArtefatoProprio(unittest.TestCase):
    """Item 7 do lote: so registra o marcador se o artefato proprio persistiu
    com sucesso (ou como no-op) -- nunca antes, nunca se o commit falhar."""

    def test_step_do_helper_vem_depois_do_commit_do_artefato_proprio(self):
        for caso in CASOS:
            if caso["commit_proprio"] is None:
                continue
            with self.subTest(arquivo=caso["arquivo"]):
                doc, _texto = _carregar(caso["arquivo"])
                nomes = []
                for job in (doc.get("jobs") or {}).values():
                    for step in job.get("steps") or []:
                        if isinstance(step, dict) and "run" in step:
                            nomes.append(str(step.get("name", "")))
                indice_commit = next(i for i, n in enumerate(nomes) if "commit" in n.lower())
                indice_helper = next(i for i, n in enumerate(nomes) if "persistir marcador" in n.lower())
                self.assertLess(
                    indice_commit, indice_helper,
                    f"em {caso['arquivo']}, o step do helper deve vir depois do commit do artefato proprio",
                )


if __name__ == "__main__":
    unittest.main()
