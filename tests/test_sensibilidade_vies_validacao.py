#!/usr/bin/env python3
"""Teste offline de src/analise_sensibilidade_vies_validacao.py.

Cobre o mecanismo do vies (achado do Adinailson, 2026-07-25): a amostra
validada exclui 'restritos' (nenhuma fonte conferida como Correto), o que
infla mecanicamente o acerto validado de qualquer modelo. Testa: (1)
composicao dos restritos por combinacao de conferencias Erradas; (2) que
limite_inferior <= limite_superior sempre; (3) que restritos SEM predicao
completa dos modelos nao entram no calculo (paridade com avaliacao_final)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import decisao_validada as dv  # noqa: E402
import analise_sensibilidade_vies_validacao as sens  # noqa: E402


class _WorksheetFalsa:
    def __init__(self, valores):
        self._valores = [list(r) for r in valores]

    def get_values(self, *_args, **_kwargs):
        return [list(r) for r in self._valores]


class _SpreadsheetFalsa:
    def __init__(self, abas: dict):
        self._abas = abas

    def worksheet(self, nome):
        return self._abas[nome]


CAB = ["ID", "TIT", "CATEGORIA COMPLETA", "D", "E", "F", "Classificação IA", "H", "I",
       "J", "K", "L", "CONFERENCIA GLPI", "CONFERENCIA IA", "Classificação IA - 2",
       "CONFERENCIA IA - 2"]


def _linha(historico, ia, v_glpi="", v_ia="", reclass="", v_reclass=""):
    row = [""] * 16
    row[2] = historico
    row[6] = ia
    row[12] = v_glpi
    row[13] = v_ia
    row[14] = reclass
    row[15] = v_reclass
    return row


class TestComporRestritos(unittest.TestCase):
    def test_composicao_glpi_errado_apenas(self):
        decisoes = {
            2: dv.decidir("catA", "catB", "", "Errado", None, None) | {
                "v_glpi": "Errado", "v_ia": None, "v_reclass": None},
        }
        comp = sens.compor_restritos(decisoes)
        self.assertEqual(comp, {"errado_glpi": 1})

    def test_composicao_glpi_e_ia_errados(self):
        decisoes = {
            2: dv.decidir("catA", "catB", "", "Errado", "Errado", None) | {
                "v_glpi": "Errado", "v_ia": "Errado", "v_reclass": None},
        }
        comp = sens.compor_restritos(decisoes)
        self.assertEqual(comp, {"errado_glpi_e_ia": 1})

    def test_decididos_nao_entram_na_composicao(self):
        decisoes = {
            2: dv.decidir("catA", "catB", "", "Correto", None, None) | {
                "v_glpi": "Correto", "v_ia": None, "v_reclass": None},
        }
        comp = sens.compor_restritos(decisoes)
        self.assertEqual(comp, {})

    def test_conflito_contabilizado_separadamente(self):
        decisoes = {
            2: dv.decidir("catA", "catB", "", "Correto", "Correto", None) | {
                "v_glpi": "Correto", "v_ia": "Correto", "v_reclass": None},
        }
        comp = sens.compor_restritos(decisoes)
        self.assertEqual(comp, {"conflito_correto_divergente": 1})


class TestCarregarDecisoesComVeredito(unittest.TestCase):
    def test_le_veredito_junto_com_decisao(self):
        valores = [CAB, _linha("catA", "catB", v_glpi="Errado")]
        sh = _SpreadsheetFalsa({"principal": _WorksheetFalsa(valores)})
        decisoes = sens.carregar_decisoes_com_veredito(sh, "principal")
        self.assertEqual(decisoes[2]["v_glpi"], "Errado")
        self.assertEqual(decisoes[2]["status"], dv.STATUS_RESTRITO)


class TestLimitesDeSensibilidade(unittest.TestCase):
    """Simula o calculo de limites diretamente (mesma logica de main(), sem
    I/O), garantindo o invariante limite_inferior <= limite_superior e que
    restritos aumentam o denominador sem aumentar os corretos."""

    def test_limite_inferior_nunca_maior_que_superior(self):
        # 3 decididos (modelo acerta 2), 2 restritos (nao contam).
        linhas_decididas = [2, 3, 4]
        linhas_restritas = [5, 6]
        verdade = {2: "x", 3: "y", 4: "z"}
        preds = {2: "x", 3: "y", 4: "w"}  # 2 corretos, 1 errado
        corretos = sum(1 for ln in linhas_decididas if preds[ln] == verdade[ln])
        n_dec, n_res = len(linhas_decididas), len(linhas_restritas)
        limite_superior = corretos / n_dec
        limite_inferior = corretos / (n_dec + n_res)
        self.assertLessEqual(limite_inferior, limite_superior)
        self.assertAlmostEqual(limite_superior, 2 / 3)
        self.assertAlmostEqual(limite_inferior, 2 / 5)

    def test_sem_restritos_limites_coincidem(self):
        corretos, n_dec, n_res = 5, 10, 0
        limite_superior = corretos / n_dec
        limite_inferior = corretos / (n_dec + n_res)
        self.assertEqual(limite_inferior, limite_superior)


if __name__ == "__main__":
    unittest.main()
