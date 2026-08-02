#!/usr/bin/env python3
"""Teste offline de src/distribuicao_categorias.py.

Cobre a distincao que o pesquisador estabeleceu em 2026-08-01: categorias com
'>' sao servicos reais; categorias sem '>' existem apenas porque o GLPI exige
a categoria-pai para permitir as filhas, e nao contam como classe de trabalho.
"""

from __future__ import annotations

import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import distribuicao_categorias as dc  # noqa: E402


class TestEhFolha(unittest.TestCase):
    def test_com_separador_e_folha(self):
        self.assertTrue(dc.eh_folha("Elétrica > Iluminação"))

    def test_sem_separador_e_raiz(self):
        for c in ("Projetos e Reformas", "Outros", "Climatização"):
            self.assertFalse(dc.eh_folha(c), c)

    def test_raiz_de(self):
        self.assertEqual(dc.raiz_de("Elétrica > Iluminação"), "Elétrica")
        self.assertEqual(dc.raiz_de("Outros"), "Outros")

    def test_raiz_de_com_dois_niveis(self):
        self.assertEqual(dc.raiz_de("A > B > C"), "A")


class TestResumir(unittest.TestCase):
    def setUp(self):
        self.c = Counter({
            "Elétrica > Iluminação": 100,
            "Elétrica > Gerador": 50,
            "Hidrossanitária > Hidráulica": 30,
            "Projetos e Reformas": 5,      # raiz com chamado
            "Outros": 2,                    # raiz com chamado
        })

    def test_separa_folhas_de_raizes(self):
        r = dc.resumir(self.c)
        self.assertEqual(r["categorias_distintas"], 5)
        self.assertEqual(r["folhas_distintas"], 3)
        self.assertEqual(r["raizes_distintas"], 2)

    def test_conta_chamados_por_natureza(self):
        r = dc.resumir(self.c)
        self.assertEqual(r["total_chamados"], 187)
        self.assertEqual(r["chamados_em_folhas"], 180)
        self.assertEqual(r["chamados_em_raizes"], 7)
        self.assertAlmostEqual(r["percentual_em_raizes"], round(100 * 7 / 187, 2))

    def test_familias_agrupam_apenas_folhas(self):
        """A familia 'Elétrica' soma as duas folhas; raizes nao viram familia."""
        r = dc.resumir(self.c)
        fam = {f["familia"]: f["n"] for f in r["familias"]}
        self.assertEqual(fam, {"Elétrica": 150, "Hidrossanitária": 30})
        self.assertEqual(r["familias_distintas"], 2)

    def test_ordenacao_por_frequencia_depois_alfabetica(self):
        c = Counter({"A > z": 5, "A > a": 5, "A > m": 9})
        r = dc.resumir(c)
        self.assertEqual([f["categoria"] for f in r["folhas"]],
                         ["A > m", "A > a", "A > z"])

    def test_base_sem_raizes(self):
        c = Counter({"A > b": 3})
        r = dc.resumir(c)
        self.assertEqual(r["raizes_distintas"], 0)
        self.assertEqual(r["chamados_em_raizes"], 0)
        self.assertEqual(r["percentual_em_raizes"], 0.0)

    def test_contagem_vazia_nao_divide_por_zero(self):
        r = dc.resumir(Counter())
        self.assertEqual(r["total_chamados"], 0)
        self.assertEqual(r["percentual_em_raizes"], 0.0)

    def test_soma_das_partes_bate_com_o_total(self):
        r = dc.resumir(self.c)
        self.assertEqual(r["chamados_em_folhas"] + r["chamados_em_raizes"],
                         r["total_chamados"])
        self.assertEqual(r["folhas_distintas"] + r["raizes_distintas"],
                         r["categorias_distintas"])


if __name__ == "__main__":
    unittest.main()
