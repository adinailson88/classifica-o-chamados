from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import modelos_zoo as zoo  # noqa: E402

ELETRICA = ["lampada queimada no corredor", "disjuntor desarmado na sala",
            "tomada sem energia no bloco", "quadro eletrico com falha",
            "reator da luminaria queimado"]
HIDRAULICA = ["vazamento na torneira do banheiro", "esgoto entupido na copa",
              "caixa d agua com infiltracao", "cano estourado no jardim",
              "descarga com vazamento continuo"]


class TestModeloMargemBinario(unittest.TestCase):
    """O LinearSVC com duas classes expunha inversão de eixos em _proba."""

    def setUp(self):
        self.textos = ELETRICA + HIDRAULICA
        self.rotulos = ["eletrica"] * len(ELETRICA) + ["hidraulica"] * len(HIDRAULICA)
        self.modelo = zoo.criar_modelo("linear_svc").fit(self.textos, self.rotulos)

    def test_predicao_binaria_devolve_uma_classe_por_amostra(self):
        preds, scores = self.modelo.predict_score(self.textos)
        self.assertEqual(len(preds), len(self.textos))
        self.assertEqual(len(scores), len(self.textos))
        self.assertTrue(set(preds) <= {"eletrica", "hidraulica"})

    def test_distribuicao_binaria_tem_uma_linha_por_amostra(self):
        classes, matriz = self.modelo.predict_dist(self.textos)
        self.assertEqual(len(classes), 2)
        self.assertEqual(matriz.shape, (len(self.textos), 2))
        for linha in matriz:
            self.assertAlmostEqual(float(linha.sum()), 1.0, places=6)

    def test_multiclasse_continua_funcionando(self):
        textos = self.textos + ["porta emperrada na entrada",
                                "fechadura quebrada no armario",
                                "janela sem trinco na sala",
                                "dobradica solta no portao",
                                "vidro trincado na recepcao"]
        rotulos = self.rotulos + ["marcenaria"] * 5
        modelo = zoo.criar_modelo("linear_svc").fit(textos, rotulos)
        classes, matriz = modelo.predict_dist(textos)
        self.assertEqual(len(classes), 3)
        self.assertEqual(matriz.shape, (len(textos), 3))


class TestLinearSvcDeterministico(unittest.TestCase):
    """SEED=42 do contrato experimental precisa alcancar o LinearSVC de fato,
    nao so figurar como parametro `semente` decorativo em outro modulo."""

    def test_random_state_42_no_estimador_criado(self):
        estimador = zoo.criar_modelo("linear_svc").pipe.named_steps["clf"]
        self.assertEqual(estimador.random_state, 42)

    def test_outros_hiperparametros_do_linear_svc_preservados(self):
        estimador = zoo.criar_modelo("linear_svc").pipe.named_steps["clf"]
        self.assertEqual(estimador.class_weight, "balanced")
        self.assertEqual(estimador.C, 1.0)
        self.assertEqual(estimador.loss, "squared_hinge")
        self.assertEqual(estimador.penalty, "l2")
        self.assertEqual(estimador.tol, 1e-4)

    def test_duas_instancias_treinadas_no_mesmo_corpus_preveem_identico(self):
        textos = ELETRICA + HIDRAULICA
        rotulos = ["eletrica"] * len(ELETRICA) + ["hidraulica"] * len(HIDRAULICA)
        m1 = zoo.criar_modelo("linear_svc").fit(textos, rotulos)
        m2 = zoo.criar_modelo("linear_svc").fit(textos, rotulos)
        p1, s1 = m1.predict_score(textos)
        p2, s2 = m2.predict_score(textos)
        self.assertEqual(list(p1), list(p2))
        self.assertEqual([round(float(x), 10) for x in s1],
                         [round(float(x), 10) for x in s2])


if __name__ == "__main__":
    unittest.main()
