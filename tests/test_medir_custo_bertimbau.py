from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import medir_custo_bertimbau as mcb  # noqa: E402


def medida(segundos_por_passo=2.0, inferencia=8.0, tokenizacao=500.0):
    return {
        "passos_medidos": 30,
        "segundos_por_passo": segundos_por_passo,
        "amostras_por_segundo_inferencia": inferencia,
        "amostras_por_segundo_tokenizacao": tokenizacao,
    }


class TestExtrapolacao(unittest.TestCase):
    def test_passos_por_epoca_arredondam_para_cima(self):
        # 100 linhas em lotes de 16 exigem 7 passos, não 6.
        p = mcb.extrapolar(medida(), n_treino=100, n_teste=25, k=5,
                           epochs=1, batch=16)
        self.assertEqual(p["passos_por_epoca"], 7)

    def test_epocas_multiplicam_os_passos(self):
        um = mcb.extrapolar(medida(), 1000, 250, 5, epochs=1, batch=16)
        tres = mcb.extrapolar(medida(), 1000, 250, 5, epochs=3, batch=16)
        self.assertEqual(tres["passos_por_dobra"], 3 * um["passos_por_dobra"])

    def test_projeta_o_custo_das_cinco_dobras(self):
        p = mcb.extrapolar(medida(segundos_por_passo=2.0), n_treino=11178,
                           n_teste=2794, k=5, epochs=3, batch=16)
        # 699 passos por época, 2097 por dobra, a 2 s: mais de uma hora por dobra.
        self.assertEqual(p["passos_por_epoca"], 699)
        self.assertEqual(p["passos_por_dobra"], 2097)
        self.assertGreater(p["horas_por_dobra"], 1.0)
        self.assertAlmostEqual(p["horas_todas_as_dobras"],
                               round(p["segundos_por_dobra"] * 5 / 3600, 2), places=1)

    def test_reconhece_quando_a_dobra_nao_cabe_no_job(self):
        lento = mcb.extrapolar(medida(segundos_por_passo=20.0), 11178, 2794, 5,
                               epochs=3, batch=16)
        self.assertFalse(lento["cabe_em_um_job_do_executor"])
        self.assertEqual(lento["dobras_que_cabem_em_um_job"], 0)

    def test_reconhece_quando_a_dobra_cabe_no_job(self):
        rapido = mcb.extrapolar(medida(segundos_por_passo=0.05), 11178, 2794, 5,
                                epochs=3, batch=16)
        self.assertTrue(rapido["cabe_em_um_job_do_executor"])
        self.assertGreaterEqual(rapido["dobras_que_cabem_em_um_job"], 1)


class TestRelatorio(unittest.TestCase):
    def contexto(self):
        return {"modelo_base": "neuralmind/bert-base-portuguese-cased",
                "epochs": 3, "max_len": 192, "batch": 16, "lr": 2e-5,
                "dobra_medida": 1, "n_treino": 11178, "n_teste": 2794,
                "categorias": 41}

    def test_veredito_inviavel_quando_excede_o_job(self):
        p = mcb.extrapolar(medida(segundos_por_passo=20.0), 11178, 2794, 5, 3, 16)
        r = mcb.montar_relatorio(medida(segundos_por_passo=20.0), p, self.contexto())
        self.assertEqual(r["veredito"],
                         "protocolo_integral_inviavel_no_executor_atual")

    def test_relatorio_separa_medido_de_extrapolado(self):
        p = mcb.extrapolar(medida(), 11178, 2794, 5, 3, 16)
        r = mcb.montar_relatorio(medida(), p, self.contexto())
        r["gerado_em"] = "agora"
        md = mcb.renderizar_markdown(r)
        self.assertIn("O que é medido e o que é extrapolado", md)
        self.assertIn("Medido:", md)
        self.assertIn("Extrapolado:", md)

    def test_ambiente_registra_disponibilidade_das_dependencias(self):
        a = mcb.ambiente()
        self.assertIn("torch", a)
        self.assertIn("transformers", a)
        self.assertIn("cuda_disponivel", a)


if __name__ == "__main__":
    unittest.main()
