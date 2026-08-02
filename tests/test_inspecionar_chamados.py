#!/usr/bin/env python3
"""Teste offline de scripts/migracoes/inspecionar_chamados.py."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts" / "migracoes"))
sys.path.insert(0, str(RAIZ / "src"))

import inspecionar_chamados as ic  # noqa: E402


class TestEhErro(unittest.TestCase):
    def test_erros_pt_br(self):
        for v in ("#N/D", "#REF!", "#VALOR!", "#NOME?", "#DIV/0!"):
            self.assertTrue(ic.eh_erro(v), v)

    def test_erros_en_us(self):
        for v in ("#N/A", "#VALUE!", "#NAME?"):
            self.assertTrue(ic.eh_erro(v), v)

    def test_ignora_caixa_e_espaco(self):
        self.assertTrue(ic.eh_erro("  #n/d  "))

    def test_valor_normal_nao_e_erro(self):
        for v in ("Correto", "Elétrica > Iluminação", "", None, "0.97"):
            self.assertFalse(ic.eh_erro(v), repr(v))

    def test_texto_que_apenas_contem_cerquilha(self):
        """'#N/D encontrado' e conteudo, nao valor de erro da celula."""
        self.assertFalse(ic.eh_erro("#N/D encontrado no relatorio"))


class TestNormalizarId(unittest.TestCase):
    def test_numero_vira_inteiro(self):
        self.assertEqual(ic.normalizar_id(2026070492.0), "2026070492")

    def test_espacos(self):
        self.assertEqual(ic.normalizar_id(" 2026070492 "), "2026070492")

    def test_vazio(self):
        self.assertEqual(ic.normalizar_id(None), "")


class TestPrivacidade(unittest.TestCase):
    def test_colunas_de_texto_livre_declaradas(self):
        """O conteudo dessas colunas nao pode ser impresso em log publico."""
        for c in ("TÍTULO", "DESCRIÇÃO GLPI", "TÍTULO O.S.M.", "DESCRIÇÃO O.S.M."):
            self.assertIn(c, ic.COLUNAS_TEXTO_LIVRE)

    def test_categoria_e_conferencia_nao_sao_texto_livre(self):
        """Precisam ser impressas: sao o objeto do diagnostico."""
        for c in ("CATEGORIA COMPLETA", "CONFERÊNCIA GLPI", "CATEGORIA CORRETA MANUAL"):
            self.assertNotIn(c, ic.COLUNAS_TEXTO_LIVRE)


if __name__ == "__main__":
    unittest.main()
