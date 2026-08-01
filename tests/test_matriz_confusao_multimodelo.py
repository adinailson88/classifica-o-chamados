#!/usr/bin/env python3
"""Teste offline de src/matriz_confusao_multimodelo.py.

A matriz e calculada contra a verdade derivada da conferencia humana do GLPI
(coluna M, mais Q nos casos em que o GLPI errou). Ela cresce sozinha conforme a
conferencia avanca, entao os testes cobrem tanto o caso cheio quanto o caso
parcial (modelo sem predicao para parte dos chamados).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matriz_confusao_multimodelo as mc  # noqa: E402


class TestConstruir(unittest.TestCase):
    def test_matriz_perfeita(self):
        verdades = {"1": "A", "2": "B", "3": "A"}
        predicoes = {"m": {"1": "A", "2": "B", "3": "A"}}
        r = mc.construir(verdades, predicoes, ["m"])
        m = r["modelos"]["m"]
        self.assertEqual(r["categorias"], ["A", "B"])
        self.assertEqual(m["acuracia"], 1.0)
        self.assertEqual(m["f1_macro"], 1.0)
        self.assertEqual(sorted(m["celulas"]), [[0, 0, 2], [1, 1, 1]])

    def test_matriz_com_erro(self):
        verdades = {"1": "A", "2": "A", "3": "B", "4": "B"}
        predicoes = {"m": {"1": "A", "2": "B", "3": "B", "4": "B"}}
        r = mc.construir(verdades, predicoes, ["m"])
        m = r["modelos"]["m"]
        self.assertEqual(m["n"], 4)
        self.assertEqual(m["acuracia"], 0.75)
        # A: suporte 2, previsto 1, acerto 1 -> precision 1.0, recall 0.5
        a = next(c for c in m["por_categoria"] if c["c"] == 0)
        self.assertEqual((a["suporte"], a["previstos"]), (2, 1))
        self.assertEqual((a["precision"], a["recall"]), (1.0, 0.5))
        # B: suporte 2, previsto 3, acerto 2 -> precision 2/3, recall 1.0
        b = next(c for c in m["por_categoria"] if c["c"] == 1)
        self.assertEqual((b["suporte"], b["previstos"]), (2, 3))
        self.assertEqual(b["recall"], 1.0)
        self.assertAlmostEqual(b["precision"], 0.6667, places=3)

    def test_celulas_sao_esparsas(self):
        """So celulas nao nulas: a matriz densa nao cabe no payload do painel."""
        verdades = {str(i): "A" for i in range(50)}
        predicoes = {"m": {str(i): "A" for i in range(50)}}
        r = mc.construir(verdades, predicoes, ["m"])
        self.assertEqual(r["modelos"]["m"]["celulas"], [[0, 0, 50]])

    def test_modelo_sem_predicao_para_parte_dos_chamados(self):
        """Cobertura parcial (caso do BERTimbau) nao vira erro."""
        verdades = {"1": "A", "2": "A"}
        predicoes = {"m": {"1": "A"}}
        r = mc.construir(verdades, predicoes, ["m"])
        m = r["modelos"]["m"]
        self.assertEqual(m["n"], 1)
        self.assertEqual(m["acuracia"], 1.0)

    def test_modelo_sem_nenhuma_predicao(self):
        r = mc.construir({"1": "A"}, {"m": {}}, ["m"])
        m = r["modelos"]["m"]
        self.assertEqual(m["n"], 0)
        self.assertIsNone(m["acuracia"])
        self.assertIsNone(m["f1_macro"])

    def test_categoria_inventada_entra_no_indice(self):
        """Modelo preve categoria que nao existe na verdade: precisa aparecer
        como coluna da matriz, senao a confusao fica invisivel."""
        verdades = {"1": "A"}
        predicoes = {"m": {"1": "Z_INEXISTENTE"}}
        r = mc.construir(verdades, predicoes, ["m"])
        self.assertIn("Z_INEXISTENTE", r["categorias"])
        m = r["modelos"]["m"]
        self.assertEqual(m["acuracia"], 0.0)
        # F1 macro so conta categorias COM suporte na verdade.
        self.assertEqual(m["categorias_na_verdade"], 1)

    def test_varios_modelos_compartilham_o_indice(self):
        verdades = {"1": "A", "2": "B"}
        predicoes = {"m1": {"1": "A", "2": "B"}, "m2": {"1": "B", "2": "B"}}
        r = mc.construir(verdades, predicoes, ["m1", "m2"])
        self.assertEqual(r["categorias"], ["A", "B"])
        self.assertEqual(r["modelos"]["m1"]["acuracia"], 1.0)
        self.assertEqual(r["modelos"]["m2"]["acuracia"], 0.5)

    def test_n_verdade_reflete_a_conferencia(self):
        r = mc.construir({"1": "A", "2": "B"}, {"m": {}}, ["m"])
        self.assertEqual(r["n_verdade"], 2)


class TestTopConfusoes(unittest.TestCase):
    def test_ordena_por_volume_e_ignora_diagonal(self):
        verdades = {}
        predicoes = {"m": {}}
        # 5 x (A->B), 3 x (B->A), 10 acertos em A
        i = 0
        for _ in range(5):
            i += 1; verdades[str(i)] = "A"; predicoes["m"][str(i)] = "B"
        for _ in range(3):
            i += 1; verdades[str(i)] = "B"; predicoes["m"][str(i)] = "A"
        for _ in range(10):
            i += 1; verdades[str(i)] = "A"; predicoes["m"][str(i)] = "A"
        r = mc.construir(verdades, predicoes, ["m"])
        top = mc.top_confusoes(r["modelos"]["m"], r["categorias"])
        self.assertEqual(top[0], {"verdade": "A", "predito": "B", "n": 5})
        self.assertEqual(top[1], {"verdade": "B", "predito": "A", "n": 3})
        self.assertEqual(len(top), 2)  # diagonal fora

    def test_respeita_o_limite(self):
        verdades, predicoes = {}, {"m": {}}
        for i in range(30):
            verdades[str(i)] = f"C{i}"
            predicoes["m"][str(i)] = f"C{(i + 1) % 30}"
        r = mc.construir(verdades, predicoes, ["m"])
        self.assertEqual(len(mc.top_confusoes(r["modelos"]["m"], r["categorias"], limite=7)), 7)


if __name__ == "__main__":
    unittest.main()
