from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import custo_computacional_canonico as ccc  # noqa: E402

ELETRICA = ["lampada queimada no corredor", "disjuntor desarmado na sala",
            "tomada sem energia no bloco", "quadro eletrico com falha"]
HIDRAULICA = ["vazamento na torneira", "esgoto entupido na copa",
              "caixa d agua com infiltracao", "cano estourado no jardim"]


class TestMedicao(unittest.TestCase):
    def setUp(self):
        self.textos = ELETRICA + HIDRAULICA
        self.rotulos = ["eletrica"] * 4 + ["hidraulica"] * 4
        self.silencio = lambda _m: None

    def test_repete_o_numero_pedido_de_execucoes(self):
        chamadas = []
        ccc.medir_modelo("naive_bayes", self.textos, self.rotulos, 3,
                         lambda m: chamadas.append(m))
        self.assertEqual(len(chamadas), 3)

    def test_reporta_mediana_dentro_da_faixa(self):
        r = ccc.medir_modelo("naive_bayes", self.textos, self.rotulos, 3,
                             self.silencio)
        self.assertEqual(r["repeticoes"], 3)
        self.assertLessEqual(r["treino_min_s"], r["treino_s"])
        self.assertLessEqual(r["treino_s"], r["treino_max_s"])
        self.assertLessEqual(r["inferencia_min_s"], r["inferencia_s"])
        self.assertLessEqual(r["inferencia_s"], r["inferencia_max_s"])

    def test_tempos_nao_sao_negativos(self):
        # Um corpus de oito linhas treina em menos de 10 ms, e a exibicao com
        # duas casas arredonda para zero. O teste garante coerencia, nao
        # magnitude: a magnitude so tem sentido sobre a base real.
        r = ccc.medir_modelo("naive_bayes", self.textos, self.rotulos, 1,
                             self.silencio)
        self.assertGreaterEqual(r["treino_s"], 0.0)
        self.assertGreaterEqual(r["inferencia_s"], 0.0)


class TestRelatorio(unittest.TestCase):
    def setUp(self):
        self.textos = ELETRICA + HIDRAULICA
        self.rotulos = ["eletrica"] * 4 + ["hidraulica"] * 4
        self.silencio = lambda _m: None

    def test_ordena_do_mais_rapido_ao_mais_lento(self):
        r = ccc.montar_relatorio(self.textos, self.rotulos,
                                 ["naive_bayes", "random_forest"], 1,
                                 self.silencio)
        tempos = [m["treino_s"] for m in r["modelos"]]
        self.assertEqual(tempos, sorted(tempos))

    def test_razao_usa_o_tempo_bruto_e_nao_o_arredondado(self):
        """Modelo rapido demais arredonda para 0,00 e zeraria o divisor."""
        r = ccc.montar_relatorio(self.textos, self.rotulos,
                                 ["naive_bayes", "random_forest"], 1,
                                 self.silencio)
        razoes = [m["razao_para_o_mais_rapido"] for m in r["modelos"]]
        self.assertTrue(all(x is not None for x in razoes))
        self.assertTrue(all(x >= 1.0 for x in razoes))
        # O campo interno nao pode vazar para a saida publicavel.
        self.assertNotIn("_treino_bruto", r["modelos"][0])

    def test_razao_do_mais_rapido_e_um(self):
        r = ccc.montar_relatorio(self.textos, self.rotulos,
                                 ["naive_bayes", "random_forest"], 1,
                                 self.silencio)
        self.assertEqual(r["modelos"][0]["razao_para_o_mais_rapido"], 1.0)
        self.assertEqual(r["referencia_da_razao"], r["modelos"][0]["modelo"])

    def test_registra_corpus_e_ambiente(self):
        r = ccc.montar_relatorio(self.textos, self.rotulos, ["naive_bayes"], 1,
                                 self.silencio)
        self.assertEqual(r["corpus"]["linhas"], 8)
        self.assertEqual(r["corpus"]["categorias"], 2)
        self.assertIn("sklearn", r["ambiente"]["dependencias"])

    def test_markdown_declara_o_desenho(self):
        r = ccc.montar_relatorio(self.textos, self.rotulos, ["naive_bayes"], 1,
                                 self.silencio)
        r["gerado_em"] = "agora"
        md = ccc.renderizar_markdown(r)
        self.assertIn("treino unico sobre a base completa", md)
        self.assertIn("nao e a soma", md)


if __name__ == "__main__":
    unittest.main()
