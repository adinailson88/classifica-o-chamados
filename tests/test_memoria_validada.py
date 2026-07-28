from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import memoria_validada as mv  # noqa: E402


class _WorksheetFalsa:
    def __init__(self, valores):
        self.valores = valores

    def get_values(self, *_args, **_kwargs):
        return [list(linha) for linha in self.valores]


class _SpreadsheetFalsa:
    def __init__(self, valores):
        self.valores = valores

    def worksheet(self, nome):
        if nome != "PRINCIPAL":
            raise KeyError(nome)
        return _WorksheetFalsa(self.valores)


def _linha(*valores, largura=17):
    return list(valores) + [""] * max(0, largura - len(valores))


class TestMemoriaValidadaPrincipal(unittest.TestCase):
    def setUp(self):
        cabecalho = _linha(
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
        )
        self.planilha = _SpreadsheetFalsa([
            cabecalho,
            _linha("1", "texto M", "CAT_M", "descricao", "", "", "OUTRA", "", "", "", "", "", "Correto"),
            _linha("2", "texto N", "HIST", "descricao", "", "", "CAT_N", "", "", "", "", "", "Errado", "Correto"),
            _linha("3", "texto P", "HIST", "descricao", "", "", "IA", "", "", "", "", "", "Errado", "Errado", "CAT_P", "Correto"),
            _linha("4", "texto Q", "HIST", "descricao", "", "", "IA", "", "", "", "", "", "Errado", "Errado", "RECLASS", "Errado", "CAT_Q"),
            _linha("5", "conflito", "CAT_A", "descricao", "", "", "CAT_B", "", "", "", "", "", "Correto", "Correto"),
            _linha("6", "sem validacao", "HIST", "descricao"),
        ])

    def test_carrega_apenas_decisoes_nao_contraditorias(self):
        memoria = mv.carregar_memoria_validada(self.planilha, "PRINCIPAL")

        self.assertEqual([item["categoria"] for item in memoria], [
            "CAT_M",
            "CAT_N",
            "CAT_P",
            "CAT_Q",
        ])
        self.assertEqual([item["fonte_decisao"] for item in memoria], [
            "conferencia_glpi",
            "conferencia_ia",
            "conferencia_reclass",
            "manual",
        ])
        self.assertTrue(all(item["origem"] == "aba_principal_M_N_P_Q" for item in memoria))
        self.assertNotIn("conflito", "\n".join(item["texto"] for item in memoria))

    def test_expansao_respeita_peso(self):
        memoria = mv.carregar_memoria_validada(self.planilha, "PRINCIPAL")[:1]
        textos, categorias = mv.expandir_treino_com_memoria(["base"], ["BASE"], memoria, peso=2)

        self.assertEqual(textos, ["base", "texto M\ndescricao", "texto M\ndescricao"])
        self.assertEqual(categorias, ["BASE", "CAT_M", "CAT_M"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
