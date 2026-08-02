#!/usr/bin/env python3
"""Teste offline de src/benchmark_custo_modelos.py.

Nao mede desempenho de verdade -- tempo de execucao nao e testavel de forma
deterministica. Verifica o que E deterministico: a forma do resultado, a
selecao de modelos, a conversao de unidade e a garantia de que o BERTimbau
nunca e treinado por este caminho.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import benchmark_custo_modelos as bc  # noqa: E402

CONFIG = {"multimodelo": {
    "modelos_leves": ["naive_bayes", "linear_svc"],
    "modelos_pesados": ["lstm", "transformer_ft"],
}}

# Corpus minusculo, mas com repeticao suficiente para o TF-IDF nao degenerar.
TEXTOS = ["vazamento na torneira do banheiro", "lampada queimada na sala",
          "torneira pingando muita agua", "reator da lampada com defeito",
          "cano estourado no banheiro", "iluminacao do corredor apagada"] * 4
CATS = ["Hidraulica", "Eletrica", "Hidraulica", "Eletrica",
        "Hidraulica", "Eletrica"] * 4


class TestResolverModelos(unittest.TestCase):
    def test_leves(self):
        self.assertEqual(bc.resolver_modelos(CONFIG, "leves"),
                         ["naive_bayes", "linear_svc"])

    def test_todos_exclui_transformer(self):
        """O BERTimbau levaria horas e exigiria torch; nunca entra aqui."""
        r = bc.resolver_modelos(CONFIG, "todos")
        self.assertIn("lstm", r)
        self.assertNotIn("transformer_ft", r)

    def test_lista_explicita_tambem_exclui_transformer(self):
        r = bc.resolver_modelos(CONFIG, "linear_svc,transformer_ft")
        self.assertEqual(r, ["linear_svc"])

    def test_lista_com_espacos(self):
        self.assertEqual(bc.resolver_modelos(CONFIG, " linear_svc , naive_bayes "),
                         ["linear_svc", "naive_bayes"])


class TestMedir(unittest.TestCase):
    def test_forma_do_resultado(self):
        r = bc.medir("naive_bayes", TEXTOS, CATS, repeticoes=2)
        self.assertEqual(r["modelo"], "naive_bayes")
        self.assertEqual(r["n"], len(TEXTOS))
        self.assertEqual(r["repeticoes"], 2)
        self.assertTrue(r["treinado_neste_benchmark"])
        for bloco in ("treino", "inferencia"):
            self.assertIn("mediana_s", r[bloco])
            self.assertIn("min_s", r[bloco])
            self.assertIn("max_s", r[bloco])
            self.assertGreaterEqual(r[bloco]["mediana_s"], 0)
            self.assertLessEqual(r[bloco]["min_s"], r[bloco]["max_s"])

    def test_uma_repeticao_nao_reporta_desvio(self):
        """Com n=1 nao existe dispersao; reportar 0 seria mentira."""
        r = bc.medir("naive_bayes", TEXTOS, CATS, repeticoes=1)
        self.assertIsNone(r["treino"]["desvio_s"])
        self.assertIsNone(r["inferencia"]["desvio_s"])

    def test_duas_repeticoes_reportam_desvio(self):
        r = bc.medir("naive_bayes", TEXTOS, CATS, repeticoes=2)
        self.assertIsNotNone(r["treino"]["desvio_s"])

    def test_conversao_para_ms_por_mil_chamados(self):
        r = bc.medir("naive_bayes", TEXTOS, CATS, repeticoes=1)
        esperado = 1e6 * r["inferencia"]["mediana_s"] / r["n"]
        self.assertAlmostEqual(r["inferencia_ms_por_mil"], round(esperado, 2), places=1)


class TestReferenciaBertimbau(unittest.TestCase):
    def test_declara_que_nao_foi_treinado_aqui(self):
        """A proveniencia precisa sobreviver a qualquer leitura do JSON."""
        self.assertFalse(bc.BERTIMBAU_REFERENCIA["treinado_neste_benchmark"])
        self.assertIn("transformer_ft.yml", bc.BERTIMBAU_REFERENCIA["fonte"])

    def test_tem_ressalva_sobre_o_subconjunto(self):
        """O tempo medido e de treino sobre subconjunto; sem essa ressalva o
        numero seria lido como custo da base inteira."""
        self.assertIn("subconjunto", bc.BERTIMBAU_REFERENCIA["ressalva"])

    def test_medicoes_sao_reais_e_positivas(self):
        vs = bc.BERTIMBAU_REFERENCIA["treino_segundos_medido"]
        self.assertTrue(vs and all(v > 0 for v in vs))


class TestAmbiente(unittest.TestCase):
    def test_descreve_a_maquina(self):
        a = bc.ambiente()
        for chave in ("python", "sistema", "cpus_disponiveis", "sklearn"):
            self.assertIn(chave, a)
        self.assertTrue(a["observacao"])


if __name__ == "__main__":
    unittest.main()
