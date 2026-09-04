#!/usr/bin/env python3
"""Fase 3 do plano de reducao de celulas (RECLASS_HISTORICO, 2026-09):
truncar_reclass_historico calcula a faixa de limpeza corretamente (cabecalho
sempre preservado) e nunca limpa nada quando as contagens de linhas de duas
leituras independentes nao batem."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "migracoes"))

import truncar_reclass_historico as trunc  # noqa: E402


class TestCalcularIntervaloLimpeza(unittest.TestCase):
    def test_preserva_cabecalho_e_cobre_ate_a_ultima_linha(self):
        faixa = trunc.calcular_intervalo_limpeza(n_colunas=24, n_linhas_dados=127462)
        # 24a coluna = X; +1 pelo cabecalho na linha 1.
        self.assertEqual(faixa, "A2:X127463")

    def test_uma_so_coluna(self):
        self.assertEqual(trunc.calcular_intervalo_limpeza(n_colunas=1, n_linhas_dados=5), "A2:A6")

    def test_mais_de_26_colunas_usa_duas_letras(self):
        # 27a coluna = AA.
        self.assertEqual(trunc.calcular_intervalo_limpeza(n_colunas=27, n_linhas_dados=10), "A2:AA11")


class _WsColunaA:
    def __init__(self, ids_com_cabecalho):
        self._ids = ids_com_cabecalho

    def col_values(self, indice):
        assert indice == 1
        return self._ids


class TestConfirmarLeituraCompleta(unittest.TestCase):
    def test_bate_quando_as_duas_leituras_concordam(self):
        ws = _WsColunaA(["id_chamado", "1", "2", "3"])  # cabecalho + 3 linhas

        bateu, n = trunc.confirmar_leitura_completa(ws, n_linhas_exportadas=3)

        self.assertTrue(bateu)
        self.assertEqual(n, 3)

    def test_nao_bate_quando_a_2a_leitura_tem_menos_linhas(self):
        # simula leitura parcial/incompleta (ver CONTEXTO.md: IMPORTRANGE ja
        # devolveu leitura incompleta sem sinal de erro nesta planilha).
        ws = _WsColunaA(["id_chamado", "1", "2"])  # so 2 linhas, esperava 3

        bateu, n = trunc.confirmar_leitura_completa(ws, n_linhas_exportadas=3)

        self.assertFalse(bateu)
        self.assertEqual(n, 2)

    def test_nao_bate_quando_a_2a_leitura_tem_mais_linhas(self):
        # simula o inverso: linhas novas entraram entre o export e a 2a leitura.
        ws = _WsColunaA(["id_chamado", "1", "2", "3", "4"])

        bateu, n = trunc.confirmar_leitura_completa(ws, n_linhas_exportadas=3)

        self.assertFalse(bateu)
        self.assertEqual(n, 4)


if __name__ == "__main__":
    unittest.main()
