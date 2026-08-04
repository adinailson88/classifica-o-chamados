from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import comparar_regras_modelos as crm  # noqa: E402

GERADOR = "Manutenção Preventiva > Gerador"
SPLIT = "Manutenção Preventiva > Ar condicionado split"
ELETRICA = "Elétrica > Tomada"


def cenario():
    """Quatro registros: regra corrige, regra estraga, regra se abstém, ruído."""
    referencia = {"a": GERADOR, "b": SPLIT, "c": ELETRICA, "d": GERADOR}
    textos = {
        "a": "Preventiva mensal do gerador",     # regra acerta, modelo errava
        "b": "Preventiva mensal do gerador",     # regra erra, modelo acertava
        "c": "Tomada queimada na sala 10",       # regra se abstém
        "d": "Preventiva mensal do gerador",     # regra e modelo concordam
    }
    predicoes = {"a": SPLIT, "b": SPLIT, "c": ELETRICA, "d": GERADOR}
    return referencia, textos, predicoes


class TestCompararRegrasModelos(unittest.TestCase):
    def setUp(self):
        self.referencia, self.textos, self.predicoes = cenario()
        self.chaves = sorted(self.referencia)
        self.permitidas = set(self.referencia.values())

    def test_regra_so_substitui_onde_dispara(self):
        r = crm.comparar(self.chaves, self.referencia, self.textos,
                         self.predicoes, self.permitidas)
        self.assertEqual(r["regra"]["disparos"], 3)
        self.assertEqual(r["regra"]["cobertura"], 0.75)

    def test_conflitos_separam_quem_acerta(self):
        r = crm.comparar(self.chaves, self.referencia, self.textos,
                         self.predicoes, self.permitidas)
        c = r["regra"]
        # 'a' e 'b' divergem do modelo; em 'a' a regra acerta, em 'b' o modelo.
        self.assertEqual(c["conflitos_com_o_modelo"], 2)
        self.assertEqual(c["conflitos_em_que_a_regra_acerta"], 1)
        self.assertEqual(c["conflitos_em_que_o_modelo_acerta"], 1)
        self.assertEqual(c["conflitos_em_que_ambos_erram"], 0)

    def test_denominador_e_identico_nas_duas_configuracoes(self):
        r = crm.comparar(self.chaves, self.referencia, self.textos,
                         self.predicoes, self.permitidas)
        self.assertEqual(r["global"]["modelo_puro"]["n"],
                         r["global"]["hibrido"]["n"])
        self.assertEqual(r["preventivos"]["modelo_puro"]["n"],
                         r["preventivos"]["hibrido"]["n"])

    def test_recorte_preventivo_usa_a_referencia_e_nao_a_predicao(self):
        r = crm.comparar(self.chaves, self.referencia, self.textos,
                         self.predicoes, self.permitidas)
        # a, b e d têm referência preventiva; c é elétrica corretiva.
        self.assertEqual(r["preventivos"]["modelo_puro"]["n"], 3)

    def test_ganho_e_perda_sao_reportados_com_sinal(self):
        r = crm.comparar(self.chaves, self.referencia, self.textos,
                         self.predicoes, self.permitidas)
        g = r["global"]
        # A regra corrige 'a' e estraga 'b': três acertos em quatro nas duas
        # configurações, com delta nulo. O saldo zero é o ponto do teste.
        self.assertEqual(g["modelo_puro"]["acuracia"], 0.75)
        self.assertEqual(g["hibrido"]["acuracia"], 0.75)
        self.assertEqual(g["delta_acuracia"], 0.0)

    def test_relatorio_cobre_todos_os_modelos_e_nao_expoe_texto(self):
        rel = crm.montar_relatorio(
            self.chaves, self.referencia, self.textos,
            {"modelo_um": self.predicoes, "modelo_dois": self.predicoes})
        self.assertEqual(rel["problemas"]["modelos_comparados"], 2)
        self.assertEqual(rel["corpus"]["preventivos_na_referencia"], 3)
        rel["gerado_em"] = "agora"
        bruto = str(rel) + crm.renderizar_markdown(rel)
        self.assertNotIn("Tomada queimada", bruto)
        self.assertNotIn("sala 10", bruto)

    def test_registro_sem_texto_e_contabilizado(self):
        textos = dict(self.textos)
        textos["c"] = ""
        rel = crm.montar_relatorio(self.chaves, self.referencia, textos,
                                   {"modelo_um": self.predicoes})
        self.assertEqual(rel["problemas"]["registros_sem_texto"], 1)


if __name__ == "__main__":
    unittest.main()
