"""Regressões da análise de sensibilidade às categorias raras."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import sensibilidade_classes_raras as scr  # noqa: E402

PARTICOES = {
    "k": 5,
    "criterio_exclusao": "critério de teste",
    "linhas_da_base_congelada": 10,
    "linhas_excluidas_total": 4,
    "categorias_na_referencia": 4,
    "linhas_excluidas_por_suporte": 3,
    "linhas_excluidas_por_sorteio": 1,
    "categorias_excluidas_por_suporte": [
        {"categoria": "F > rara", "grupos_distintos": 3, "linhas": 3,
         "dobras_possiveis": 3},
    ],
    "categorias_excluidas_por_sorteio": [
        {"categoria": "G > rarissima", "linhas": 1, "rodada": 1},
    ],
}


class TestFamilia(unittest.TestCase):
    def test_corta_no_primeiro_separador(self):
        self.assertEqual(scr.familia("A > b > c"), "A")

    def test_categoria_sem_separador_e_a_propria_familia(self):
        self.assertEqual(scr.familia("Outros"), "Outros")


class TestMacroF1(unittest.TestCase):
    def test_rotulo_declarado_e_nunca_predito_entra_como_zero(self):
        pares = [("A", "A"), ("B", "B")]
        self.assertAlmostEqual(scr.macro_f1(pares, ["A", "B"]), 1.0)
        # O rótulo C existe na taxonomia, mas nunca aparece: puxa a média.
        self.assertAlmostEqual(scr.macro_f1(pares, ["A", "B", "C"]), 2 / 3)

    def test_bate_com_o_sklearn(self):
        from sklearn.metrics import f1_score
        pares = [("A", "A"), ("A", "B"), ("B", "B"), ("C", "A"), ("C", "C")]
        rotulos = ["A", "B", "C"]
        esperado = f1_score([v for v, _ in pares], [p for _, p in pares],
                            labels=rotulos, average="macro", zero_division=0)
        self.assertAlmostEqual(scr.macro_f1(pares, rotulos), esperado, places=10)


class TestCobertura(unittest.TestCase):
    def test_conta_linhas_e_categorias_e_declara_a_limitacao(self):
        c = scr.cobertura(PARTICOES, linhas_avaliadas=6, categorias_avaliadas=2)
        self.assertEqual(c["linhas_avaliadas"], 6)
        self.assertEqual(c["categorias_excluidas"], 2)
        self.assertEqual(c["cobertura_de_categorias"], 0.5)
        self.assertIn("não cobre integralmente", c["declaracao_obrigatoria"])

    def test_separa_os_dois_motivos_de_exclusao(self):
        c = scr.cobertura(PARTICOES, 6, 2)
        motivos = {x["motivo"].split(":")[0] for x in c["detalhe"]}
        self.assertEqual(motivos, {"aritmética", "estratificação"})


class TestDobrasViaveis(unittest.TestCase):
    def test_k_menor_recupera_categoria_com_poucos_grupos(self):
        d = scr.dobras_viaveis(PARTICOES)
        self.assertEqual(d["por_k"]["3"]["categorias_recuperaveis_por_aritmetica"], 1)
        self.assertEqual(d["por_k"]["5"]["categorias_recuperaveis_por_aritmetica"], 0)

    def test_declara_o_que_nao_foi_verificado(self):
        d = scr.dobras_viaveis(PARTICOES)
        self.assertIn("Informação insuficiente para verificar.",
                      d["limite_da_analise"])


class TestConvencoes(unittest.TestCase):
    def test_convencao_completa_e_reescala_da_avaliada(self):
        por_modelo = {"m": [("A > x", "A > x"), ("B > y", "B > y")]}
        particoes = dict(PARTICOES,
                         categorias_excluidas_por_suporte=[
                             {"categoria": "C > z", "grupos_distintos": 1,
                              "linhas": 1, "dobras_possiveis": 1}],
                         categorias_excluidas_por_sorteio=[])
        v = scr.convencoes(por_modelo, particoes)
        linha = v["por_modelo"][0]
        self.assertAlmostEqual(linha["macro_f1_a_avaliadas"], 1.0)
        # Três rótulos na taxonomia, dois avaliados: 1,0 x 2/3.
        self.assertAlmostEqual(linha["macro_f1_b_taxonomia_completa"], 0.6667,
                               places=4)
        self.assertTrue(v["ordenacao_estavel_entre_a_e_b"])

    def test_familias_agregam_categorias_da_mesma_raiz(self):
        # Erro dentro da família some na agregação hierárquica.
        por_modelo = {"m": [("A > x", "A > y"), ("A > y", "A > y")]}
        v = scr.convencoes(por_modelo, dict(PARTICOES,
                                            categorias_excluidas_por_suporte=[],
                                            categorias_excluidas_por_sorteio=[]))
        linha = v["por_modelo"][0]
        self.assertAlmostEqual(linha["macro_f1_c_familias"], 1.0)
        self.assertLess(linha["macro_f1_a_avaliadas"], 1.0)


class TestArtefatoPublicado(unittest.TestCase):
    def setUp(self):
        caminho = (Path(__file__).resolve().parents[1] / "docs" / "dados"
                   / "sensibilidade_classes_raras.json")
        if not caminho.exists():
            self.skipTest("sensibilidade_classes_raras.json nao publicada.")
        self.r = json.loads(caminho.read_text(encoding="utf-8"))

    def test_cobertura_bate_com_os_denominadores_do_artigo(self):
        c = self.r["cobertura"]
        self.assertEqual(c["linhas_da_base_congelada"], 14060)
        self.assertEqual(c["linhas_avaliadas"], 13972)
        self.assertEqual(c["categorias_avaliadas"], 41)
        self.assertEqual(c["categorias_excluidas"], 9)

    def test_tres_convencoes_de_macro_f1_por_modelo(self):
        for x in self.r["convencoes_de_macro_f1"]["por_modelo"]:
            self.assertLessEqual(x["macro_f1_b_taxonomia_completa"],
                                 x["macro_f1_a_avaliadas"])


if __name__ == "__main__":
    unittest.main()
