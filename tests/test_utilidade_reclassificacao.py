"""Regressões da análise de utilidade da reclassificação.

O ponto que estes testes fixam é que o ganho líquido simples deixa de ser a
única leitura sem deixar de ser reprodutível: ele precisa continuar saindo da
função de utilidade quando rho = 1 e lambda = 0.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import utilidade_reclassificacao as ur  # noqa: E402

HISTORICA = {
    "hash_corpus": "teste",
    "corpus": {"registros": 100},
    "modelos": [
        {"modelo": "bom",
         "reclassificacao": {"divergencias_com_o_historico": 100,
                             "corrigidos": 40, "prejudicados": 50,
                             "neutros": 10, "ganho_liquido": -10}},
        {"modelo": "ruim",
         "reclassificacao": {"divergencias_com_o_historico": 200,
                             "corrigidos": 20, "prejudicados": 170,
                             "neutros": 10, "ganho_liquido": -150}},
    ],
}


class TestUtilidade(unittest.TestCase):
    def test_custos_iguais_e_sem_revisao_reproduzem_o_ganho_liquido(self):
        self.assertEqual(ur.utilidade(40, 50, 999, rho=1.0, lam=0.0), -10)

    def test_prejuizo_mais_caro_piora_a_utilidade(self):
        self.assertLess(ur.utilidade(40, 50, 0, 2.0, 0.0),
                        ur.utilidade(40, 50, 0, 1.0, 0.0))

    def test_custo_de_revisao_entra_com_sinal_negativo(self):
        self.assertLess(ur.utilidade(40, 0, 100, 1.0, 0.1),
                        ur.utilidade(40, 0, 100, 1.0, 0.0))


class TestAplicacaoDireta(unittest.TestCase):
    def test_razao_de_equilibrio_e_corrigidos_sobre_prejudicados(self):
        r = ur.politica_aplicacao_direta(
            HISTORICA["modelos"][0]["reclassificacao"], (1.0,))
        self.assertAlmostEqual(r["rho_de_equilibrio"], 0.8, places=4)

    def test_no_equilibrio_a_utilidade_zera(self):
        conta = HISTORICA["modelos"][0]["reclassificacao"]
        rho = conta["corrigidos"] / conta["prejudicados"]
        self.assertAlmostEqual(
            ur.utilidade(conta["corrigidos"], conta["prejudicados"], 0, rho, 0.0),
            0.0, places=9)

    def test_revisados_e_zero_nesta_politica(self):
        r = ur.politica_aplicacao_direta(
            HISTORICA["modelos"][0]["reclassificacao"], (1.0,))
        self.assertEqual(r["revisados"], 0)


class TestTriagem(unittest.TestCase):
    def test_beneficio_e_corrigidos_mais_neutros(self):
        r = ur.politica_triagem(HISTORICA["modelos"][0]["reclassificacao"], (0.0,))
        self.assertEqual(r["registros_da_fila_com_historico_errado"], 50)
        self.assertAlmostEqual(r["precisao_da_fila"], 0.5, places=4)

    def test_lambda_de_equilibrio_coincide_com_a_precisao_da_fila(self):
        r = ur.politica_triagem(HISTORICA["modelos"][0]["reclassificacao"], (0.0,))
        self.assertEqual(r["lambda_de_equilibrio"], r["precisao_da_fila"])

    def test_pressuposto_do_teto_esta_declarado(self):
        r = ur.politica_triagem(HISTORICA["modelos"][0]["reclassificacao"], (0.0,))
        self.assertIn("teto", r["pressuposto"])


class TestRelatorio(unittest.TestCase):
    def test_nenhum_valor_monetario(self):
        r = ur.montar_relatorio(HISTORICA)
        self.assertTrue(r["funcao_de_utilidade"]["nenhum_valor_monetario_e_atribuido"])

    def test_ordena_pelo_ganho_liquido_simples(self):
        r = ur.montar_relatorio(HISTORICA)
        self.assertEqual([m["modelo"] for m in r["modelos"]], ["bom", "ruim"])

    def test_markdown_sai_sem_excecao(self):
        r = ur.montar_relatorio(HISTORICA)
        r["gerado_em"] = "2026-08-05"
        texto = ur.renderizar_markdown(r)
        self.assertIn("Política A", texto)
        self.assertIn("Política B", texto)


class TestArtefatoPublicado(unittest.TestCase):
    def setUp(self):
        caminho = (Path(__file__).resolve().parents[1] / "docs" / "dados"
                   / "utilidade_reclassificacao.json")
        if not caminho.exists():
            self.skipTest("utilidade_reclassificacao.json nao publicada.")
        self.r = json.loads(caminho.read_text(encoding="utf-8"))

    def test_ganho_simples_bate_com_a_comparacao_historica(self):
        historica = json.loads(
            (Path(__file__).resolve().parents[1] / "docs" / "dados"
             / "comparacao_historica.json").read_text(encoding="utf-8"))
        esperado = {m["modelo"]: m["reclassificacao"]["ganho_liquido"]
                    for m in historica["modelos"]}
        obtido = {m["modelo"]: m["ganho_liquido_simples"] for m in self.r["modelos"]}
        self.assertEqual(obtido, esperado)

    def test_utilidade_negativa_em_toda_a_grade_de_rho(self):
        for m in self.r["modelos"]:
            self.assertFalse(m["aplicacao_direta"]["positiva_em_algum_rho_da_grade"])


if __name__ == "__main__":
    unittest.main()
