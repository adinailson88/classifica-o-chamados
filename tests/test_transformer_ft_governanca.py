#!/usr/bin/env python3
"""Teste estatico de governanca do Lote 8G-B: verifica, so por leitura dos YAML
(sem executar nenhum workflow), que a separacao operacional/cientifica do
BERTimbau ficou como decidido -- escopo minimo de `contents: write`, guarda das
100 conferencias sem o hardcode `valor_atual=0`, workflow experimental sem
nenhuma persistencia automatica em `main` nem na planilha, e artifacts com
allowlist estrita que exclui qualquer saida que possa conter fragmento de
texto de chamado.

As checagens de "comando ausente" (git add/commit/push, --aplicar, --autostash
etc.) sao feitas apenas sobre o conteudo dos blocos `run:` de cada step, nunca
sobre o arquivo YAML inteiro: os proprios comentarios de governanca dos
workflows citam esses termos para explicar que NAO sao usados, e um grep cru
do arquivo inteiro acusaria falso positivo nesses comentarios.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[1]
OPERACIONAL = RAIZ / ".github" / "workflows" / "transformer_ft.yml"
EXPERIMENTAL = RAIZ / ".github" / "workflows" / "transformer_ft_experimentos.yml"
MANIFESTO = RAIZ / "docs" / "dados" / "MANIFESTO_ARTIGO_CONGELADO.json"

JOB_PERSISTENCIA = "persistir_estado"

PROIBIDOS_ARTIFACT = (
    "bertimbau_cluster_report.json",
    "bertimbau_review_queue.json",
    "bertimbau_coreset_ids.json",
)


def carregar_yaml(caminho: Path) -> dict:
    with caminho.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def secao_on(doc: dict):
    # PyYAML (resolvedor YAML 1.1) interpreta a chave 'on:' como booleano True.
    for chave in (True, "on", "On", "ON"):
        if chave in doc:
            return doc[chave]
    raise KeyError("secao 'on' nao encontrada no workflow")


def jobs(doc: dict) -> dict:
    return doc.get("jobs") or {}


def blocos_run(doc: dict) -> str:
    """Concatena o conteudo de todos os blocos run: de todos os jobs/steps."""
    partes = []
    for job in jobs(doc).values():
        for step in job.get("steps") or []:
            if isinstance(step, dict) and "run" in step:
                partes.append(str(step["run"]))
    return "\n".join(partes)


def jobs_com_contents_write(doc: dict) -> list[str]:
    achados = []
    for nome, job in jobs(doc).items():
        perms = job.get("permissions") or {}
        if perms.get("contents") == "write":
            achados.append(nome)
    return achados


def linhas_git_add(texto: str) -> list[str]:
    return re.findall(r"^\s*git add (.+)$", texto, re.MULTILINE)


def steps_upload_artifact(doc: dict) -> list[dict]:
    achados = []
    for job in jobs(doc).values():
        for step in job.get("steps") or []:
            if isinstance(step, dict) and str(step.get("uses", "")).startswith("actions/upload-artifact"):
                achados.append(step)
    return achados


def caminhos_do_step_artifact(step: dict) -> list[str]:
    valor = (step.get("with") or {}).get("path", "")
    if isinstance(valor, list):
        linhas = valor
    else:
        linhas = str(valor).splitlines()
    return [ln.strip() for ln in linhas if ln.strip()]


class TestWorkflowOperacional(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = carregar_yaml(OPERACIONAL)
        cls.texto_bruto = OPERACIONAL.read_text(encoding="utf-8")
        cls.texto_run = blocos_run(cls.doc)

    def test_1_nome_preservado(self):
        self.assertEqual(self.doc["name"], "Transformer fine-tuning (BERTimbau)")

    def test_2_mantem_schedule(self):
        self.assertIn("schedule", secao_on(self.doc))

    def test_3_mantem_workflow_dispatch(self):
        self.assertIn("workflow_dispatch", secao_on(self.doc))

    def test_4_permissoes_globais_read(self):
        self.assertEqual(self.doc["permissions"], {"contents": "read"})

    def test_5_somente_job_persistencia_tem_write(self):
        self.assertEqual(jobs_com_contents_write(self.doc), [JOB_PERSISTENCIA])

    def test_6_cluster_coreset_nao_e_modo_operacional(self):
        inputs = secao_on(self.doc)["workflow_dispatch"]["inputs"]
        self.assertNotIn("cluster_coreset", inputs["modo"]["options"])
        for nome_job in jobs(self.doc):
            self.assertNotEqual(nome_job, "cluster_coreset")

    def test_7_comparar_nao_e_acao_operacional(self):
        inputs = secao_on(self.doc)["workflow_dispatch"]["inputs"]
        self.assertNotIn("acao", inputs)
        self.assertNotIn("comparar_modelos_lote.py", self.texto_bruto)

    def test_8_selecao_experimental_indisponivel_na_reclassificacao(self):
        env_treinar = self.doc["jobs"]["treinar"]["env"]
        self.assertEqual(env_treinar["TRANSFORMER_SELECT"], "none")
        inputs = secao_on(self.doc)["workflow_dispatch"]["inputs"]
        self.assertNotIn("selecao_treino", inputs)

    def test_9_sem_hardcode_valor_atual_zero(self):
        self.assertNotIn("valor_atual=0", self.texto_bruto)

    def test_10_staging_git_restrito_ao_estado_operacional(self):
        # Lote 8H-B2: dados/estado_automacao.json saiu deste commit textual --
        # e persistido separadamente pelo helper seguro (ver test_10b).
        linhas = linhas_git_add(self.texto_run)
        self.assertEqual(len(linhas), 1, f"esperado exatamente 1 'git add', achado: {linhas}")
        caminhos = set(linhas[0].split())
        self.assertEqual(caminhos, {"docs/dados/bertimbau_training_state.json"})

    def test_10b_estado_automacao_persistido_pelo_helper_seguro(self):
        # dados/estado_automacao.json nao pode mais aparecer em nenhum `git add`
        # (ja garantido por test_10, que exige exatamente 1 add e so o path do
        # training_state); aqui confirmamos que o mecanismo antigo (registro via
        # guard_automacao.py) foi removido e o helper seguro assumiu o lugar.
        self.assertNotIn("guard_automacao.py --registrar", self.texto_run)
        self.assertIn("persistir_estado_automacao.py", self.texto_run)
        self.assertIn("--chave transformer_ft", self.texto_run)
        self.assertIn("--aplicar", self.texto_run)

    def test_11_sem_comandos_destrutivos_ou_amplos(self):
        self.assertNotIn("git add .", self.texto_run)
        self.assertNotIn("git add -A", self.texto_run)
        self.assertNotIn("--autostash", self.texto_run)
        self.assertNotIn("stash", self.texto_run)
        self.assertNotIn("--force", self.texto_run)
        self.assertNotRegex(self.texto_run, r"git push[^\n]*(-f\b|--force)")

    def test_job_persistencia_so_roda_apos_treino_real(self):
        job = self.doc["jobs"][JOB_PERSISTENCIA]
        self.assertEqual(job["permissions"], {"contents": "write"})
        condicao = str(job["if"])
        self.assertIn("needs.treinar.outputs.houve_treino == 'true'", condicao)
        self.assertIn("needs.treinar.result == 'success'", condicao)

    def test_comentario_obsoleto_evidencia_artigo_removido(self):
        self.assertNotIn("evidencia usada pelo artigo", self.texto_bruto)
        self.assertNotIn("evidência usada pelo artigo", self.texto_bruto)


class TestWorkflowExperimental(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = carregar_yaml(EXPERIMENTAL)
        cls.texto_run = blocos_run(cls.doc)

    def test_12_somente_workflow_dispatch(self):
        on = secao_on(self.doc)
        self.assertEqual(set(on.keys()), {"workflow_dispatch"})

    def test_13_sem_schedule(self):
        self.assertNotIn("schedule", secao_on(self.doc))

    def test_14_permissoes_globais_read(self):
        self.assertEqual(self.doc["permissions"], {"contents": "read"})

    def test_15_nenhum_job_com_contents_write(self):
        self.assertEqual(jobs_com_contents_write(self.doc), [])
        for job in jobs(self.doc).values():
            self.assertNotIn("permissions", job)

    def test_16_sem_persistencia_automatica_em_git(self):
        self.assertNotIn("git add", self.texto_run)
        self.assertNotIn("git commit", self.texto_run)
        self.assertNotIn("git push", self.texto_run)

    def test_17_comparacao_sem_aplicar(self):
        job_comparar = self.doc["jobs"]["comparar"]
        texto_comparar = "\n".join(
            str(step["run"]) for step in job_comparar["steps"] if isinstance(step, dict) and "run" in step
        )
        self.assertNotIn("--aplicar", texto_comparar)

    def test_18_artifacts_com_allowlist_explicita(self):
        steps = steps_upload_artifact(self.doc)
        self.assertGreaterEqual(len(steps), 2, "esperados artifacts para cluster_coreset e comparar")
        for step in steps:
            caminhos = caminhos_do_step_artifact(step)
            self.assertTrue(caminhos, f"step de artifact sem path explicito: {step}")
            for caminho in caminhos:
                self.assertNotIn("*", caminho, f"path com wildcard nao e allowlist explicita: {caminho}")

    def test_19_artifacts_nao_incluem_saidas_com_texto_de_chamado(self):
        steps = steps_upload_artifact(self.doc)
        todos_caminhos = [c for step in steps for c in caminhos_do_step_artifact(step)]
        for proibido in PROIBIDOS_ARTIFACT:
            for caminho in todos_caminhos:
                self.assertNotIn(proibido, caminho)


class TestArtigoCongeladoForaDeEscopo(unittest.TestCase):
    """Item 20: nenhum arquivo do ARTIGO_CONGELADO e produtor ou target destes
    workflows (nem como saida gerada, nem como caminho referenciado)."""

    def test_20_manifesto_nao_referenciado(self):
        import json

        manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        caminhos_congelados = [item["path"] for item in manifesto["arquivos"]]
        self.assertTrue(caminhos_congelados, "manifesto vazio — nada a checar")

        for caminho_wf in (OPERACIONAL, EXPERIMENTAL):
            texto = caminho_wf.read_text(encoding="utf-8")
            for congelado in caminhos_congelados:
                nome = Path(congelado).name
                self.assertNotIn(nome, texto, f"{nome} (ARTIGO_CONGELADO) referenciado em {caminho_wf.name}")


if __name__ == "__main__":
    unittest.main()
