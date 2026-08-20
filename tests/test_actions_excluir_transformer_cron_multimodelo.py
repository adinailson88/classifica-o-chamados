#!/usr/bin/env python3
"""Teste estatico do lote A4-2: confirma, so por leitura do YAML (sem
executar nenhum workflow), que `transformer_ft` saiu exclusivamente da
selecao AUTOMATICA de modelos do schedule em `multimodelo_classificacao.yml`,
enquanto tudo o resto do contrato do workflow permanece intacto -- cron,
workflow_dispatch, inputs manuais (incluindo a disponibilidade de
'pesados'/'todos'/transformer_ft explicito), flags obrigatorias do schedule
(--sem-memoria-validada, --aplicar, max_turnos=0), guard, concurrency e
permissions.

Motivacao (auditoria A4-1): o schedule nunca instala torch/transformers (so
tensorflow, para o lstm), entao transformer_ft sempre cai em fallback LSTM/RF
e classificacao_multimodelo.py RECUSA publicar esse fallback sob o nome do
modelo pedido -- nos runs auditados, a maior parte do tempo do step
"Classificar por modelo" era gasta treinando esse fallback so para
descarta-lo. Nao ha alteracao de resolver_modelos() nem de nenhum script
Python: a correcao usa soh o mecanismo ja existente de lista explicita
separada por virgula, aceito por resolver_modelos().

Nenhum workflow e executado, nenhuma rede e usada -- so leitura de YAML/texto.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[1]
WORKFLOW = RAIZ / ".github" / "workflows" / "multimodelo_classificacao.yml"

MODELOS_CRON_ESPERADOS = [
    "naive_bayes",
    "regressao_logistica",
    "linear_svc",
    "sgd",
    "extra_trees",
    "random_forest",
    "lstm",
]


def carregar_yaml(caminho: Path) -> dict:
    with caminho.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def secao_on(doc: dict):
    # PyYAML (resolvedor YAML 1.1) interpreta a chave 'on:' como booleano True.
    for chave in (True, "on", "On", "ON"):
        if chave in doc:
            return doc[chave]
    raise KeyError("secao 'on' nao encontrada no workflow")


def step_por_nome(job: dict, nome: str) -> dict:
    for step in job.get("steps") or []:
        if isinstance(step, dict) and step.get("name") == nome:
            return step
    raise AssertionError(f"step {nome!r} nao encontrado")


class TestContratoDoGatilho(unittest.TestCase):
    """Itens 1-3: cron, workflow_dispatch e inputs manuais inalterados."""

    @classmethod
    def setUpClass(cls):
        cls.doc = carregar_yaml(WORKFLOW)
        cls.on = secao_on(cls.doc)
        cls.texto_bruto = WORKFLOW.read_text(encoding="utf-8")

    def test_1_cron_inalterado(self):
        schedule = self.on["schedule"]
        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule[0]["cron"], "5,20,35,50 * * * *")

    def test_2_workflow_dispatch_presente(self):
        self.assertIn("workflow_dispatch", self.on)

    def test_3_inputs_manuais_preservados(self):
        inputs = self.on["workflow_dispatch"]["inputs"]
        self.assertEqual(
            set(inputs.keys()),
            {"modelos", "max_turnos", "sem_memoria_validada", "aplicar", "lstm_perfil"},
        )
        self.assertEqual(inputs["modelos"]["default"], "leves")
        self.assertEqual(inputs["max_turnos"]["default"], "0")
        self.assertEqual(inputs["sem_memoria_validada"]["default"], False)
        self.assertEqual(inputs["aplicar"]["default"], False)
        self.assertEqual(inputs["lstm_perfil"]["default"], "padrao")
        self.assertEqual(inputs["lstm_perfil"]["options"], ["padrao", "robusto"])


class TestSelecaoDeModelosNoSchedule(unittest.TestCase):
    """Itens 4-8: selecao automatica do schedule vs. selecao manual."""

    @classmethod
    def setUpClass(cls):
        cls.doc = carregar_yaml(WORKFLOW)
        cls.job = cls.doc["jobs"]["multimodelo"]
        cls.step = step_por_nome(cls.job, "Classificar por modelo")
        cls.modelos_env = str(cls.step["env"]["MODELOS"])

    def _lista_fallback_do_schedule(self) -> list[str]:
        # Extrai o literal apos "||" na expressao:
        #   ${{ github.event.inputs.modelos || '<lista>' }}
        # (usado pelo schedule, que nao tem github.event.inputs).
        m = re.search(r"\|\|\s*'([^']*)'\s*\}\}", self.modelos_env)
        self.assertIsNotNone(m, f"fallback nao encontrado em MODELOS: {self.modelos_env!r}")
        return [item.strip() for item in m.group(1).split(",") if item.strip()]

    def test_4_schedule_seleciona_exatamente_os_sete_modelos(self):
        self.assertEqual(self._lista_fallback_do_schedule(), MODELOS_CRON_ESPERADOS)

    def test_5_transformer_ft_fora_da_lista_automatica(self):
        self.assertNotIn("transformer_ft", self._lista_fallback_do_schedule())

    def test_6_expressao_respeita_input_manual_verbatim(self):
        # A expressao so cai no fallback quando github.event.inputs.modelos
        # esta vazio (ou seja, no schedule, que nao tem inputs). Em
        # workflow_dispatch, inputs.modelos SEMPRE tem valor (o input tem
        # default: "leves"), entao a expressao resolve para o valor literal
        # do input, sem qualquer interferencia desta mudanca.
        self.assertTrue(
            self.modelos_env.startswith("${{ github.event.inputs.modelos ||"),
            f"MODELOS deixou de repassar o input manual verbatim: {self.modelos_env!r}",
        )

    def test_7_selecao_manual_todos_permanece_disponivel(self):
        # 'todos' e resolvido em resolver_modelos() (nao tocado por este
        # lote); aqui so confirmamos que o workflow repassa $MODELOS direto
        # ao script, sem nenhum `if`/`case` que filtre ou valide seu valor.
        self.assertIn('--modelos "$MODELOS"', self.step["run"])
        self.assertNotRegex(self.step["run"], r'if\s*\[\s*"\$MODELOS"')
        self.assertNotIn("case $MODELOS", self.step["run"])

    def test_8_selecao_manual_pesados_permanece_disponivel(self):
        # 'pesados' nao entra na lista AUTOMATICA do schedule (correto: ela
        # deve conter os modelos por nome, nao o atalho), mas a mesma
        # garantia estrutural do teste 7 (repasse verbatim do input) cobre a
        # disponibilidade manual de 'pesados'.
        self.assertNotIn("pesados", self._lista_fallback_do_schedule())
        self.assertIn("${{ github.event.inputs.modelos ||", self.modelos_env)

    def test_9_selecao_manual_explicita_de_transformer_ft_nao_bloqueada(self):
        # Nenhuma linha FUNCIONAL (bash, fora de comentarios) valida/filtra
        # o conteudo de MODELOS -- o unico lugar que poderia bloquear
        # 'transformer_ft' explicito seria um allowlist/`if` no codigo do
        # step, que nao existe. O step tem um comentario explicativo que
        # cita 'transformer_ft' de proposito (documentando a exclusao do
        # automatico); por isso as linhas de comentario sao ignoradas aqui.
        linhas_funcionais = [
            ln for ln in self.step["run"].splitlines() if ln.strip() and not ln.strip().startswith("#")
        ]
        self.assertNotIn("transformer_ft", "\n".join(linhas_funcionais))


class TestFlagsObrigatoriasDoSchedule(unittest.TestCase):
    """Itens 9-11: --sem-memoria-validada, --aplicar e max_turnos=0 no schedule."""

    @classmethod
    def setUpClass(cls):
        cls.doc = carregar_yaml(WORKFLOW)
        cls.job = cls.doc["jobs"]["multimodelo"]
        cls.step = step_por_nome(cls.job, "Classificar por modelo")
        cls.run_texto = str(cls.step["run"])

    def test_10_sem_memoria_validada_obrigatorio_no_schedule(self):
        self.assertIn(
            '[ "${{ github.event.inputs.sem_memoria_validada }}" = "true" ] '
            '|| [ "${{ github.event_name }}" = "schedule" ]',
            self.run_texto,
        )
        self.assertIn('SEM_MEM="--sem-memoria-validada"', self.run_texto)

    def test_11_aplicar_no_schedule(self):
        self.assertIn(
            '[ "${{ github.event.inputs.aplicar }}" = "true" ] '
            '|| [ "${{ github.event_name }}" = "schedule" ]',
            self.run_texto,
        )
        self.assertIn('APLICAR="--aplicar"', self.run_texto)

    def test_12_max_turnos_zero_no_schedule(self):
        max_turnos_env = str(self.step["env"]["MAX_TURNOS"])
        self.assertEqual(max_turnos_env, "${{ github.event.inputs.max_turnos || '0' }}")


class TestGuardConcurrencyPermissionsInalterados(unittest.TestCase):
    """Item 12 da tarefa: guard, concurrency e permissions nao foram tocados."""

    @classmethod
    def setUpClass(cls):
        cls.doc = carregar_yaml(WORKFLOW)

    def test_concurrency_inalterada(self):
        self.assertEqual(
            self.doc["concurrency"],
            {"group": "multimodelo-pipeline", "cancel-in-progress": False, "queue": "max"},
        )

    def test_permissions_globais_inalteradas(self):
        self.assertEqual(self.doc["permissions"], {"contents": "read"})

    def test_permissions_do_job_multimodelo_inalteradas(self):
        self.assertEqual(self.doc["jobs"]["multimodelo"]["permissions"], {"contents": "write"})

    def test_guard_job_inalterado(self):
        guard = self.doc["jobs"]["guard"]
        self.assertNotIn("permissions", guard)
        step = step_por_nome(guard, "Avaliar avanco da base (>=1000 chamados ou multimodelo vazio)")
        self.assertEqual(
            step["run"],
            "python src/guard_automacao.py --chave multimodelo_classificacao "
            "--metrica registros --limiar 1000 --forcar-se-aba-zero multimodelo_metricas",
        )

    def test_condicao_if_do_job_multimodelo_inalterada(self):
        condicao = str(self.doc["jobs"]["multimodelo"]["if"])
        self.assertIn("github.event_name == 'workflow_dispatch'", condicao)
        self.assertIn("github.event_name == 'schedule'", condicao)
        self.assertIn("needs.guard.outputs.executar == 'true'", condicao)

    def test_tensorflow_continua_instalado_no_schedule(self):
        # O lstm permanece no cron; a instalacao de TensorFlow nao muda.
        job = self.doc["jobs"]["multimodelo"]
        step = step_por_nome(job, "TensorFlow se LSTM estiver no escopo")
        condicao = str(step["if"])
        self.assertIn("github.event_name == 'schedule'", condicao)
        self.assertEqual(step["run"], "python -m pip install --retries 5 --timeout 120 tensorflow==2.17.0")


if __name__ == "__main__":
    unittest.main()
