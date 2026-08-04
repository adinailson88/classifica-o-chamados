from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import comparacao_historica as ch  # noqa: E402


class TestConcordancia(unittest.TestCase):
    def test_acordo_total_da_kappa_um(self):
        h = ["a", "b", "a", "b"]
        r = ch.concordancia_com_historico(h, list(h))
        self.assertEqual(r["acordo_bruto"], 1.0)
        self.assertEqual(r["kappa"], 1.0)

    def test_acordo_parcial_reduz_o_kappa(self):
        h = ["a", "a", "b", "b"]
        p = ["a", "b", "b", "a"]
        r = ch.concordancia_com_historico(h, p)
        self.assertEqual(r["acordo_bruto"], 0.5)
        self.assertLess(r["kappa"], r["acordo_bruto"])


class TestGanhoDeReclassificacao(unittest.TestCase):
    def test_ignora_onde_o_modelo_concorda_com_o_historico(self):
        r = ch.ganho_de_reclassificacao(["a"] * 5, ["a"] * 5, ["b"] * 5)
        self.assertEqual(r["divergencias_com_o_historico"], 0)
        self.assertEqual(r["ganho_liquido"], 0)

    def test_corrigido_e_quando_o_modelo_acerta_e_o_historico_erra(self):
        r = ch.ganho_de_reclassificacao(["a"], ["b"], ["b"])
        self.assertEqual(r["corrigidos"], 1)
        self.assertEqual(r["prejudicados"], 0)
        self.assertEqual(r["ganho_liquido"], 1)

    def test_prejudicado_e_o_inverso(self):
        r = ch.ganho_de_reclassificacao(["a"], ["b"], ["a"])
        self.assertEqual(r["prejudicados"], 1)
        self.assertEqual(r["ganho_liquido"], -1)

    def test_ambos_errados_nao_conta_como_ganho_nem_perda(self):
        r = ch.ganho_de_reclassificacao(["a"], ["b"], ["c"])
        self.assertEqual(r["neutros"], 1)
        self.assertEqual(r["ganho_liquido"], 0)

    def test_as_tres_parcelas_somam_as_divergencias(self):
        h = ["a", "a", "a", "a"]
        p = ["b", "b", "b", "a"]
        ref = ["b", "a", "c", "a"]
        r = ch.ganho_de_reclassificacao(h, p, ref)
        self.assertEqual(r["divergencias_com_o_historico"], 3)
        self.assertEqual(r["corrigidos"] + r["prejudicados"] + r["neutros"], 3)


class TestDispersao(unittest.TestCase):
    def test_predicao_concentrada_tem_entropia_zero(self):
        d = ch.dispersao(["a", "b", "c"], ["a", "a", "a"], ["a", "b", "c"])
        self.assertEqual(d["entropia_normalizada"], 0.0)
        self.assertEqual(d["categorias_previstas"], 1)

    def test_predicao_uniforme_tem_entropia_um(self):
        cats = ["a", "b", "c", "d"]
        d = ch.dispersao(cats, list(cats), cats)
        self.assertAlmostEqual(d["entropia_normalizada"], 1.0, places=6)

    def test_distribuicoes_identicas_tem_js_zero(self):
        cats = ["a", "b"]
        d = ch.dispersao(["a", "b"], ["a", "b"], cats)
        self.assertEqual(d["js_contra_o_historico"], 0.0)

    def test_js_e_simetrica(self):
        p = [0.9, 0.1]
        q = [0.2, 0.8]
        self.assertAlmostEqual(ch.divergencia_js(p, q),
                               ch.divergencia_js(q, p), places=12)

    def test_js_e_limitada_por_log_de_dois(self):
        # Distribuições disjuntas atingem o máximo, que é ln(2) nesta base.
        self.assertAlmostEqual(ch.divergencia_js([1.0, 0.0], [0.0, 1.0]),
                               math.log(2), places=12)


class TestRelatorio(unittest.TestCase):
    def test_reune_as_tres_grandezas_por_modelo(self):
        h = ["a", "a", "b", "b"]
        ref = ["a", "b", "b", "a"]
        r = ch.montar_relatorio(h, ref, {"m1": ["a", "b", "b", "b"],
                                         "m2": ["a", "a", "a", "a"]})
        self.assertEqual(len(r["modelos"]), 2)
        for m in r["modelos"]:
            self.assertIn("concordancia", m)
            self.assertIn("reclassificacao", m)
            self.assertIn("dispersao", m)
        self.assertEqual(r["corpus"]["registros"], 4)

    def test_markdown_traz_as_tres_tabelas(self):
        r = ch.montar_relatorio(["a", "b"], ["a", "b"], {"m1": ["a", "b"]})
        r["gerado_em"] = "agora"
        md = ch.renderizar_markdown(r)
        self.assertIn("Concordância com a categoria histórica", md)
        self.assertIn("Ganho líquido de reclassificação", md)
        self.assertIn("Dispersão das predições", md)


if __name__ == "__main__":
    unittest.main()
