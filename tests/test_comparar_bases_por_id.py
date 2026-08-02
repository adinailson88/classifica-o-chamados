#!/usr/bin/env python3
"""Teste offline de scripts/migracoes/comparar_bases_por_id.py.

Cobre a logica pura de comparacao. O acesso as planilhas nao e testado aqui:
depende de credencial e e exercido pelo workflow.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts" / "migracoes"))
sys.path.insert(0, str(RAIZ / "src"))

import comparar_bases_por_id as cb  # noqa: E402


class TestNormalizarId(unittest.TestCase):
    def test_numero_do_sheets_vira_inteiro(self):
        self.assertEqual(cb.normalizar_id(1693.0), "1693")

    def test_string_com_espaco(self):
        self.assertEqual(cb.normalizar_id(" 1693 "), "1693")

    def test_id_longo_preservado(self):
        self.assertEqual(cb.normalizar_id("2025014328"), "2025014328")

    def test_vazio(self):
        for v in ("", None, "   "):
            self.assertEqual(cb.normalizar_id(v), "")


class TestComparar(unittest.TestCase):
    def test_conjuntos_iguais(self):
        r = cb.comparar(["1", "2", "3"], ["3", "2", "1"])
        self.assertEqual(r["em_ambas"], 3)
        self.assertEqual(r["so_em_a"], [])
        self.assertEqual(r["so_em_b"], [])

    def test_excedente_em_a(self):
        """O caso real: a base maior tem ids que a menor nao tem."""
        r = cb.comparar(["1", "2", "3", "9"], ["1", "2", "3"])
        self.assertEqual(r["so_em_a"], ["9"])
        self.assertEqual(r["so_em_b"], [])
        self.assertEqual(r["em_ambas"], 3)

    def test_diferenca_nos_dois_sentidos(self):
        r = cb.comparar(["1", "2"], ["2", "3"])
        self.assertEqual(r["so_em_a"], ["1"])
        self.assertEqual(r["so_em_b"], ["3"])

    def test_duplicados_sao_reportados_sem_afetar_conjuntos(self):
        r = cb.comparar(["1", "1", "2"], ["1", "2"])
        self.assertEqual(r["linhas_a"], 3)
        self.assertEqual(r["distintos_a"], 2)
        self.assertEqual(r["duplicados_a"], ["1"])
        self.assertEqual(r["so_em_a"], [])

    def test_ordenacao_por_tamanho_depois_alfabetica(self):
        """Ids curtos (antigos) e longos (ano+sequencial) convivem na base."""
        r = cb.comparar(["2025014328", "99", "1693"], [])
        self.assertEqual(r["so_em_a"], ["99", "1693", "2025014328"])

    def test_listas_vazias(self):
        r = cb.comparar([], [])
        self.assertEqual((r["em_ambas"], r["so_em_a"], r["so_em_b"]), (0, [], []))


if __name__ == "__main__":
    unittest.main()
