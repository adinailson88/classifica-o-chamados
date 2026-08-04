from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import calibrar_confianca as cal  # noqa: E402


class TestDobraInterna(unittest.TestCase):
    def test_escolhe_dobra_diferente_da_externa(self):
        dobras = [1, 2, 3, 4, 5]
        for f in dobras:
            self.assertNotEqual(cal.dobra_interna(f, dobras), f)

    def test_e_deterministica(self):
        dobras = [1, 2, 3, 4, 5]
        self.assertEqual(cal.dobra_interna(3, dobras), cal.dobra_interna(3, dobras))
        self.assertEqual(cal.dobra_interna(5, dobras), 1)


class TestECE(unittest.TestCase):
    def test_calibracao_perfeita_tem_ece_zero(self):
        # Confiança 1,0 sempre acerta; 0,0 sempre erra.
        r = cal.ece([1.0] * 10 + [0.0] * 10, [1] * 10 + [0] * 10)
        self.assertEqual(r["ece"], 0.0)

    def test_excesso_de_confianca_produz_ece_positivo(self):
        # Confiança 0,95 em tudo, mas acerta só metade.
        r = cal.ece([0.95] * 10, [1] * 5 + [0] * 5)
        self.assertAlmostEqual(r["ece"], 0.45, places=2)

    def test_confianca_um_entra_na_ultima_faixa(self):
        r = cal.ece([1.0] * 4, [1] * 4, faixas=10)
        ultima = r["faixas"][-1]
        self.assertEqual(ultima["n"], 4)
        self.assertEqual(sum(f["n"] for f in r["faixas"]), 4)

    def test_faixas_somam_todos_os_registros(self):
        confs = [i / 20 for i in range(21)]
        r = cal.ece(confs, [1] * 21)
        self.assertEqual(sum(f["n"] for f in r["faixas"]), 21)


class TestBrier(unittest.TestCase):
    def test_previsao_perfeita_tem_brier_zero(self):
        self.assertEqual(cal.brier([1.0, 0.0], [1, 0]), 0.0)

    def test_previsao_maximamente_errada_tem_brier_um(self):
        self.assertEqual(cal.brier([1.0, 0.0], [0, 1]), 1.0)


class TestLimiar(unittest.TestCase):
    def test_escolhe_o_menor_limiar_que_atinge_o_alvo(self):
        confs = [0.5, 0.6, 0.7, 0.8, 0.9]
        acertos = [0, 0, 1, 1, 1]
        r = cal.escolher_limiar(confs, acertos, alvo=0.9)
        self.assertTrue(r["alcancavel"])
        self.assertEqual(r["limiar"], 0.7)
        self.assertEqual(r["acuracia_na_calibracao"], 1.0)

    def test_alvo_inalcancavel_e_reportado_e_nao_omitido(self):
        r = cal.escolher_limiar([0.5, 0.6], [0, 0], alvo=0.99)
        self.assertFalse(r["alcancavel"])
        self.assertIsNone(r["limiar"])

    def test_aplicar_limiar_reporta_cobertura_e_encaminhamento(self):
        r = cal.aplicar_limiar([0.5, 0.8, 0.9, 0.95], [0, 1, 1, 1], limiar=0.8)
        self.assertEqual(r["automatizados"], 3)
        self.assertEqual(r["cobertura"], 0.75)
        self.assertEqual(r["acuracia_seletiva"], 1.0)
        self.assertEqual(r["taxa_encaminhamento_humano"], 0.25)

    def test_sem_limiar_tudo_vai_para_humano(self):
        r = cal.aplicar_limiar([0.5, 0.8], [0, 1], limiar=None)
        self.assertEqual(r["automatizados"], 0)
        self.assertEqual(r["taxa_encaminhamento_humano"], 1.0)


class TestIsotonica(unittest.TestCase):
    def test_corrige_excesso_de_confianca(self):
        confs = [0.9] * 10 + [0.95] * 10
        acertos = [0] * 10 + [1] * 10
        modelo = cal.ajustar_isotonica(confs, acertos)
        self.assertIsNotNone(modelo)
        ajustado = list(modelo.predict(confs))
        self.assertLess(ajustado[0], 0.5)
        self.assertGreater(ajustado[-1], 0.5)

    def test_sem_variacao_de_acerto_nao_ajusta(self):
        self.assertIsNone(cal.ajustar_isotonica([0.9, 0.8], [1, 1]))


class TestCarregarPredicoes(unittest.TestCase):
    def test_csv_sem_confianca_falha_com_mensagem_util(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            caminho = Path(d) / "pred.csv"
            caminho.write_text(
                "id_sha256,dobra,referencia_humana,modelo,previsto\n"
                "abc,1,Cat A,naive_bayes,Cat A\n", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                cal.carregar_predicoes(caminho)
        self.assertIn("confianca", str(ctx.exception))

    def test_deriva_acerto_da_comparacao_com_a_referencia(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            caminho = Path(d) / "pred.csv"
            caminho.write_text(
                "id_sha256,dobra,referencia_humana,modelo,previsto,confianca\n"
                "abc,1,Cat A,m,Cat A,0.9\n"
                "def,2,Cat A,m,Cat B,0.4\n", encoding="utf-8")
            dados = cal.carregar_predicoes(caminho)
        self.assertEqual(dados["por_modelo"]["m"]["abc"]["acerto"], 1)
        self.assertEqual(dados["por_modelo"]["m"]["def"]["acerto"], 0)
        self.assertEqual(dados["dobra"]["def"], 2)


if __name__ == "__main__":
    unittest.main()
