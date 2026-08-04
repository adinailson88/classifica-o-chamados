from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import regras_preventivas as rp  # noqa: E402


class TestRegrasPreventivas(unittest.TestCase):
    def test_dispara_com_periodicidade_e_equipamento(self):
        r = rp.aplicar("Manutenção preventiva mensal do gerador do campus")
        self.assertTrue(r["disparou"])
        self.assertEqual(r["categoria"], "Manutenção Preventiva > Gerador")
        self.assertIn("mensal", r["termos_periodicidade"])
        self.assertEqual(r["termo_equipamento"], "gerador")

    def test_abstem_se_falta_periodicidade(self):
        r = rp.aplicar("Gerador não liga, sala de máquinas sem energia")
        self.assertFalse(r["disparou"])
        self.assertIsNone(r["categoria"])
        self.assertEqual(r["motivo"], "sem termo de periodicidade")

    def test_abstem_se_falta_equipamento(self):
        r = rp.aplicar("Serviço trimestral conforme cronograma do contrato")
        self.assertFalse(r["disparou"])
        self.assertIsNone(r["categoria"])
        self.assertEqual(r["motivo"], "sem termo de equipamento")

    def test_acento_e_caixa_nao_alteram_o_disparo(self):
        a = rp.aplicar("PREVENTIVA SEMESTRAL DO ELEVADOR")
        b = rp.aplicar("preventiva semestral do elevador")
        self.assertEqual(a["categoria"], b["categoria"])
        self.assertEqual(a["categoria"], "Manutenção Preventiva > Elevador")

    def test_termo_especifico_vence_o_generico(self):
        r = rp.aplicar("Preventiva anual do ar condicionado central do bloco")
        self.assertEqual(r["categoria"],
                         "Manutenção Preventiva > Ar condicionado central")

    def test_fronteira_de_palavra_evita_disparo_dentro_de_outra_palavra(self):
        # 'calha' não pode casar em 'trabalha'; sem fronteira, casaria.
        r = rp.aplicar("Equipe que trabalha na rotina de limpeza do pátio")
        self.assertNotEqual(r["categoria"],
                            "Manutenção Preventiva > Telhados, calhas, rufos, etc.")

    def test_categoria_fora_do_conjunto_avaliado_nao_e_proposta(self):
        texto = "Preventiva mensal do poço artesiano do campus"
        livre = rp.aplicar(texto)
        self.assertEqual(livre["categoria"], "Manutenção Preventiva > Poços artesianos")
        restrito = rp.aplicar(texto, {"Manutenção Preventiva > Gerador"})
        self.assertIsNone(restrito["categoria"])
        self.assertEqual(restrito["motivo"], "categoria fora do conjunto avaliado")

    def test_categorias_alvo_pertencem_a_familia_preventiva(self):
        for categoria in rp.categorias_alvo():
            self.assertTrue(categoria.startswith(rp.FAMILIA))


if __name__ == "__main__":
    unittest.main()
