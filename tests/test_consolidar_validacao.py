from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import consolidar_validacao as consolidar  # noqa: E402


class _WorksheetFalsa:
    def __init__(self, valores):
        self.valores = valores

    def get_values(self, *_args, **_kwargs):
        return self.valores


class _PlanilhaFalsa:
    def __init__(self, valores):
        self.valores = valores

    def worksheet(self, _nome):
        return _WorksheetFalsa(self.valores)


def _linha(**campos):
    ordem = [
        "id", "titulo", "historico", "descricao", "titulo_osm", "descricao_osm",
        "ia", "confianca", "executor", "criticidade", "comparacao", "classificado",
        "m", "n", "reclass", "p", "q",
    ]
    return [campos.get(nome, "") for nome in ordem]


class TestConsolidarValidacao(unittest.TestCase):
    def setUp(self):
        cabecalho = [
            "ID Chamado",
            "TÍTULO",
            "CATEGORIA COMPLETA",
            "DESCRIÇÃO GLPI",
            "TÍTULO O.S.M.",
            "DESCRIÇÃO O.S.M.",
            "Classificação IA",
            "Avaliação (%)",
            "Executor",
            "Criticidade Atribuída por IA",
            "Comparação",
            "Classificado_Confiança_IA",
            "CONFERÊNCIA GLPI",
            "CONFERÊNCIA IA",
            "Classificação IA - 2",
            "CONFERÊNCIA IA - 2",
            "CATEGORIA CORRETA MANUAL",
        ]
        valores = [
            cabecalho,
            _linha(id="1", titulo="t1", historico="A", descricao="d1", ia="B", confianca=0.9, m="Correto"),
            _linha(id="2", titulo="t2", historico="A", descricao="d2", ia="B", confianca=0.8, n="Correto"),
            _linha(id="3", titulo="t3", historico="A", descricao="d3", ia="B", confianca=0.6, reclass="C", p="Correto"),
            _linha(
                id="4", titulo="t4", historico="A", descricao="d4", ia="B", confianca=0.4,
                reclass="C", m="Errado", n="Errado", p="Errado", q="D",
            ),
            _linha(
                id="5", titulo="t5", historico="A", descricao="d5", ia="B", confianca=0.7,
                m="Correto", n="Correto",
            ),
        ]
        self.sh = _PlanilhaFalsa(valores)
        self.config = {
            "aba_principal": "PRINCIPAL",
            "memoria_validada": {"peso_treino": 3},
        }

    def test_consolida_m_n_p_q_e_exclui_conflito(self):
        resultado = consolidar.construir_consolidacao(
            self.sh,
            self.config,
            "28/07/2026 02:00",
        )

        self.assertEqual(resultado["decisoes"], {
            "com_conferencia": 5,
            "decididos": 4,
            "restritos": 1,
            "conflitos": 1,
        })
        self.assertEqual(resultado["memoria_validada"], 4)
        self.assertEqual(resultado["origens"], {
            "conferencia_glpi": 1,
            "conferencia_ia": 1,
            "conferencia_reclass": 1,
            "manual": 1,
        })
        self.assertEqual(resultado["metricas"]["ia_original_G"]["n"], 4)
        self.assertEqual(resultado["metricas"]["ia_original_G"]["acuracia"], 0.25)
        self.assertEqual(resultado["metricas"]["classificacao_ia_2_O"]["n"], 2)
        self.assertEqual(resultado["metricas"]["classificacao_ia_2_O"]["acuracia"], 0.5)

        faixas = {item["faixa"]: item for item in resultado["calibracao"]}
        self.assertEqual(faixas["<70"]["n"], 2)
        self.assertEqual(faixas["<70"]["taxa"], 0.0)
        self.assertEqual(faixas["70-95"]["n"], 2)
        self.assertEqual(faixas["70-95"]["taxa"], 0.5)
        self.assertEqual(faixas[">=95"]["n"], 0)
        self.assertIsNone(faixas[">=95"]["taxa"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
