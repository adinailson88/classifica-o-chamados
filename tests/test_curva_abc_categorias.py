#!/usr/bin/env python3
"""Teste offline de src/curva_abc_categorias.py."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import curva_abc_categorias as abc  # noqa: E402


class TestClassificarABC(unittest.TestCase):
    def test_ordena_por_volume_decrescente(self):
        r = abc.classificar_abc([("b", 10), ("a", 50), ("c", 40)])
        self.assertEqual([l["categoria"] for l in r], ["a", "c", "b"])

    def test_acumulado_fecha_em_cem(self):
        r = abc.classificar_abc([("a", 50), ("b", 30), ("c", 20)])
        self.assertAlmostEqual(r[-1]["percentual_acumulado"], 100.0)

    def test_classe_a_e_o_menor_conjunto_que_cobre_o_corte(self):
        """80/20 classico: duas categorias cobrem 80%."""
        r = abc.classificar_abc([("a", 50), ("b", 30), ("c", 15), ("d", 5)])
        classes = {l["categoria"]: l["classe"] for l in r}
        # a fecha 50% (anterior 0 < 0,80 -> A); b fecha 80% (anterior 0,50 -> A)
        self.assertEqual(classes["a"], "A")
        self.assertEqual(classes["b"], "A")
        # c comeca em 0,80, que nao e < 0,80 -> B
        self.assertEqual(classes["c"], "B")
        # d comeca em 0,95, que nao e < 0,95 -> C
        self.assertEqual(classes["d"], "C")

    def test_categoria_unica_e_classe_a(self):
        r = abc.classificar_abc([("a", 7)])
        self.assertEqual(r[0]["classe"], "A")
        self.assertAlmostEqual(r[0]["percentual_acumulado"], 100.0)

    def test_empate_desempata_por_nome(self):
        r = abc.classificar_abc([("z", 10), ("a", 10)])
        self.assertEqual([l["categoria"] for l in r], ["a", "z"])

    def test_lista_vazia(self):
        self.assertEqual(abc.classificar_abc([]), [])

    def test_cortes_customizados(self):
        r = abc.classificar_abc([("a", 50), ("b", 30), ("c", 20)],
                                corte_a=0.5, corte_b=0.9)
        classes = {l["categoria"]: l["classe"] for l in r}
        self.assertEqual(classes["a"], "A")   # fecha 50%, anterior 0 < 0,5
        self.assertEqual(classes["b"], "B")   # anterior 0,50, entre os cortes
        self.assertEqual(classes["c"], "B")   # anterior 0,80, ainda < 0,90


class TestF1PorClasse(unittest.TestCase):
    def setUp(self):
        self.linhas = abc.classificar_abc([("a", 50), ("b", 30), ("c", 15), ("d", 5)])

    def test_media_simples_dentro_da_classe(self):
        f1 = {"a": 0.9, "b": 0.7, "c": 0.5, "d": 0.1}
        r = abc.f1_por_classe(self.linhas, f1)
        self.assertAlmostEqual(r["A"]["f1_macro"], 0.8)     # (0,9+0,7)/2
        self.assertAlmostEqual(r["B"]["f1_macro"], 0.5)
        self.assertAlmostEqual(r["C"]["f1_macro"], 0.1)
        self.assertAlmostEqual(r["global"]["f1_macro"], 0.55)

    def test_categoria_sem_f1_conta_como_zero(self):
        """Ausencia de predicao correta e desempenho nulo, nao dado faltante."""
        r = abc.f1_por_classe(self.linhas, {"a": 1.0, "b": 1.0})
        self.assertAlmostEqual(r["A"]["f1_macro"], 1.0)
        self.assertAlmostEqual(r["C"]["f1_macro"], 0.0)

    def test_cauda_derruba_o_global_e_nao_a_classe_a(self):
        """O nucleo do achado: zeros na cauda punem a media global."""
        linhas = abc.classificar_abc([("a", 900), ("b", 90)] +
                                     [(f"x{i}", 1) for i in range(10)])
        f1 = {"a": 0.95, "b": 0.90}
        r = abc.f1_por_classe(linhas, f1)
        self.assertGreater(r["A"]["f1_macro"], 0.9)
        self.assertLess(r["global"]["f1_macro"], 0.3)

    def test_soma_dos_suportes_bate_com_o_total(self):
        r = abc.f1_por_classe(self.linhas, {})
        soma = sum(r[c]["suporte"] for c in ("A", "B", "C"))
        self.assertEqual(soma, r["global"]["suporte"])

    def test_classe_vazia_devolve_none(self):
        linhas = abc.classificar_abc([("a", 100)])
        r = abc.f1_por_classe(linhas, {"a": 0.8})
        self.assertIsNone(r["B"]["f1_macro"])
        self.assertEqual(r["B"]["n_categorias"], 0)


class TestExtrairDoMatriz(unittest.TestCase):
    def _matriz(self):
        return {
            "categorias": ["Cat A", "Cat B", "Cat C"],
            "modelos": {
                "linear_svc": {"n": 100, "por_categoria": [
                    {"c": 0, "suporte": 60, "f1": 0.9},
                    {"c": 1, "suporte": 30, "f1": 0.5},
                    {"c": 2, "suporte": 0, "f1": 0.0}]},
                "transformer_ft": {"n": 40, "por_categoria": [
                    {"c": 0, "suporte": 25, "f1": 0.8}]},
            },
        }

    def test_suporte_vem_do_modelo_de_maior_cobertura(self):
        """Nao pode vir de modelo parcial, como o transformer_ft."""
        suportes, _ = abc.extrair_do_matriz(self._matriz())
        self.assertEqual(dict(suportes), {"Cat A": 60, "Cat B": 30})

    def test_ignora_categoria_sem_suporte(self):
        suportes, _ = abc.extrair_do_matriz(self._matriz())
        self.assertNotIn("Cat C", dict(suportes))

    def test_f1_por_modelo(self):
        _, f1 = abc.extrair_do_matriz(self._matriz())
        self.assertEqual(f1["linear_svc"]["Cat A"], 0.9)
        self.assertEqual(f1["transformer_ft"]["Cat A"], 0.8)


class TestMontar(unittest.TestCase):
    def test_estrutura_completa(self):
        matriz = {
            "categorias": ["A", "B"],
            "modelos": {"m": {"n": 10, "por_categoria": [
                {"c": 0, "suporte": 8, "f1": 0.9},
                {"c": 1, "suporte": 2, "f1": 0.1}]}},
        }
        d = abc.montar(matriz)
        self.assertEqual(d["n_categorias"], 2)
        self.assertEqual(d["total_chamados"], 10)
        self.assertIn("m", d["por_modelo"])
        self.assertEqual(d["classes"]["A"]["n_categorias"], 1)
        self.assertAlmostEqual(d["classes"]["A"]["percentual_volume"], 80.0)


if __name__ == "__main__":
    unittest.main()
