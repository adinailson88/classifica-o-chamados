"""Regressões da inferência pareada no nível do grupo textual.

O que estes testes protegem é a propriedade que motivou o módulo: a unidade de
análise precisa ser o grupo, não a linha. Um refatoramento que voltasse a somar
discordantes linha a linha passaria despercebido sem eles.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import inferencia_agrupada as ia  # noqa: E402


def blocos_de(tamanhos: list[int]) -> list[np.ndarray]:
    """Blocos de índices contíguos com os tamanhos pedidos."""
    saida, inicio = [], 0
    for t in tamanhos:
        saida.append(np.arange(inicio, inicio + t))
        inicio += t
    return saida


class TestSomasPorGrupo(unittest.TestCase):
    def test_agrega_acertos_do_grupo(self):
        acerto = np.array([[1, 1, 0, 1], [0, 0, 1, 1]], dtype=np.int8)
        somas = ia.somas_por_grupo(acerto, blocos_de([3, 1]))
        # Grupo 0 tem as três primeiras linhas; grupo 1, a última.
        self.assertEqual(somas.tolist(), [[2.0, 1.0], [1.0, 1.0]])


class TestAuditoriaDaUnidade(unittest.TestCase):
    def test_sem_duplicata_o_efeito_de_desenho_fica_perto_de_um(self):
        rng = np.random.default_rng(3)
        acerto = (rng.random((2, 600)) < 0.7).astype(np.int8)
        r = ia.auditoria_da_unidade(acerto, blocos_de([1] * 600),
                                    ["a", "b"], reamostragens=400, semente=1)
        self.assertEqual(r["grupos"], 600)
        self.assertEqual(r["proporcao_de_linhas_dependentes"], 0.0)
        for x in r["por_modelo"]:
            self.assertLess(abs(x["efeito_de_desenho"] - 1.0), 0.35)

    def test_duplicacao_integral_infla_o_efeito_de_desenho(self):
        # Cada grupo tem dez cópias da mesma linha: a informação é a de 60
        # observações, não a de 600, e o efeito de desenho precisa acusar isso.
        rng = np.random.default_rng(5)
        base = (rng.random((2, 60)) < 0.7).astype(np.int8)
        acerto = np.repeat(base, 10, axis=1)
        r = ia.auditoria_da_unidade(acerto, blocos_de([10] * 60),
                                    ["a", "b"], reamostragens=600, semente=1)
        self.assertEqual(r["proporcao_de_linhas_dependentes"], 1.0)
        self.assertGreater(r["efeito_de_desenho_min"], 4.0)


class TestComparacaoAgrupada(unittest.TestCase):
    def _blocos(self, tamanhos: list[int]):
        b = blocos_de(tamanhos)
        return b, np.array(tamanhos, dtype=np.float64)

    def test_modelos_identicos_nao_produzem_diferenca(self):
        a = np.array([1, 0, 1, 1, 0, 1], dtype=np.int8)
        blocos, tamanhos = self._blocos([2, 2, 2])
        r = ia.comparacao_agrupada(a, a.copy(), blocos, tamanhos,
                                   permutacoes=200, reamostragens=200)
        self.assertEqual(r["diferenca_de_acuracia"], 0.0)
        self.assertEqual(r["grupos_que_favorecem_o_primeiro"], 0)
        self.assertEqual(r["grupos_que_favorecem_o_segundo"], 0)
        self.assertEqual(r["grupos_empatados"], 3)
        self.assertGreater(r["p_permutacional_agrupado"], 0.5)

    def test_contagem_de_grupos_a_favor_usa_o_saldo_do_grupo(self):
        # Grupo 0: A acerta 2, B acerta 0  -> favorece A.
        # Grupo 1: A acerta 0, B acerta 1  -> favorece B.
        # Grupo 2: empate.
        a = np.array([1, 1, 0, 1], dtype=np.int8)
        b = np.array([0, 0, 1, 1], dtype=np.int8)
        blocos, tamanhos = self._blocos([2, 1, 1])
        r = ia.comparacao_agrupada(a, b, blocos, tamanhos,
                                   permutacoes=200, reamostragens=200)
        self.assertEqual(r["grupos_que_favorecem_o_primeiro"], 1)
        self.assertEqual(r["grupos_que_favorecem_o_segundo"], 1)
        self.assertEqual(r["grupos_empatados"], 1)

    def test_p_agrupado_e_mais_conservador_sob_duplicacao(self):
        # A vantagem de A é real, mas cada evidência aparece dez vezes. O
        # McNemar por linha conta dez, o teste agrupado conta uma.
        rng = np.random.default_rng(11)
        base_a = (rng.random(80) < 0.75).astype(np.int8)
        base_b = (rng.random(80) < 0.60).astype(np.int8)
        a = np.repeat(base_a, 10)
        b = np.repeat(base_b, 10)
        blocos, tamanhos = self._blocos([10] * 80)
        r = ia.comparacao_agrupada(a, b, blocos, tamanhos,
                                   permutacoes=2000, reamostragens=500)
        self.assertGreater(r["p_permutacional_agrupado"], r["p_mcnemar_por_linha"])

    def test_intervalo_da_diferenca_contem_a_estimativa(self):
        rng = np.random.default_rng(13)
        a = (rng.random(400) < 0.8).astype(np.int8)
        b = (rng.random(400) < 0.7).astype(np.int8)
        blocos, tamanhos = self._blocos([2] * 200)
        r = ia.comparacao_agrupada(a, b, blocos, tamanhos,
                                   permutacoes=500, reamostragens=800)
        menor, maior = r["ic95_da_diferenca"]
        self.assertLessEqual(menor, r["diferenca_de_acuracia"])
        self.assertGreaterEqual(maior, r["diferenca_de_acuracia"])


class TestTesteGlobal(unittest.TestCase):
    def test_modelos_iguais_nao_rejeitam(self):
        rng = np.random.default_rng(17)
        base = (rng.random(300) < 0.7).astype(np.int8)
        acerto = np.vstack([base, base.copy(), base.copy()])
        r = ia.teste_global_agrupado(acerto, blocos_de([1] * 300),
                                     permutacoes=200, semente=2)
        self.assertFalse(r["rejeita_igualdade"])

    def test_modelo_muito_pior_e_detectado(self):
        rng = np.random.default_rng(19)
        bom = (rng.random(300) < 0.9).astype(np.int8)
        ruim = (rng.random(300) < 0.3).astype(np.int8)
        acerto = np.vstack([bom, bom.copy(), ruim])
        r = ia.teste_global_agrupado(acerto, blocos_de([1] * 300),
                                     permutacoes=200, semente=2)
        self.assertTrue(r["rejeita_igualdade"])

    def test_reporta_o_p_tabelado_para_contraste(self):
        rng = np.random.default_rng(23)
        acerto = (rng.random((3, 200)) < 0.6).astype(np.int8)
        r = ia.teste_global_agrupado(acerto, blocos_de([2] * 100),
                                     permutacoes=200, semente=2)
        self.assertIn("p_qui_quadrado_por_linha", r)
        self.assertEqual(r["unidade_da_permutacao"], "grupo textual")


class TestArtefatoPublicado(unittest.TestCase):
    def setUp(self):
        import json
        caminho = (Path(__file__).resolve().parents[1] / "docs" / "dados"
                   / "inferencia_agrupada.json")
        if not caminho.exists():
            self.skipTest("inferencia_agrupada.json nao publicada neste checkout.")
        self.r = json.loads(caminho.read_text(encoding="utf-8"))

    def test_unidade_declarada_e_o_grupo(self):
        u = self.r["auditoria_da_unidade"]
        self.assertIn("grupo", u["unidade_estatistica_adotada"])
        self.assertGreater(u["efeito_de_desenho_min"], 1.0)

    def test_todos_os_pares_foram_corrigidos_por_holm(self):
        pares = self.r["pares"]
        self.assertEqual(len(pares), 21)
        for p in pares:
            self.assertIn("p_ajustado_holm", p)
            self.assertGreaterEqual(p["p_ajustado_holm"],
                                    p["p_permutacional_agrupado"] - 1e-12)

    def test_cada_par_traz_efeito_incerteza_e_contagem_de_grupos(self):
        for p in self.r["pares"]:
            self.assertIn("diferenca_de_acuracia", p)
            self.assertEqual(len(p["ic95_da_diferenca"]), 2)
            self.assertIn("grupos_que_favorecem_o_primeiro", p)
            self.assertIn("d_de_cohen_pareado_por_grupo", p)


if __name__ == "__main__":
    unittest.main()
