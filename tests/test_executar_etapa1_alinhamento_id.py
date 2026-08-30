#!/usr/bin/env python3
"""Regressão: o escritor da Etapa 1 não pode gravar por linha após o ID mudar."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import executar_etapa1 as etapa1  # noqa: E402


class _WorksheetFalsa:
    def __init__(self, valores):
        self.valores = valores
        self.ranges_lidos = []

    def get_values(self, range_a1, value_render_option=None):
        self.ranges_lidos.append((range_a1, value_render_option))
        return self.valores


class TestGateAlinhamentoId(unittest.TestCase):
    def test_aprova_quando_ids_continuam_nas_mesmas_linhas(self):
        ws = _WorksheetFalsa([["2026070582"], [2026080004.0]])
        lote = [
            {"linha": 14061, "id": "2026070582"},
            {"linha": 14062, "id": "2026080004"},
        ]

        confirmados = etapa1.validar_ids_antes_escrita(ws, lote)

        self.assertEqual(confirmados, 2)
        self.assertEqual(ws.ranges_lidos[0][0], "A14061:A14062")

    def test_aborta_lote_quando_id_mudou_de_linha(self):
        ws = _WorksheetFalsa([["2026080004"], ["2026070582"]])
        lote = [
            {"linha": 14061, "id": "2026070582"},
            {"linha": 14062, "id": "2026080004"},
        ]

        with self.assertRaisesRegex(RuntimeError, r"lote abortado \(2 divergencias\)"):
            etapa1.validar_ids_antes_escrita(ws, lote)

    def test_normaliza_id_numerico_do_sheets(self):
        self.assertEqual(etapa1.normalizar_id(2026070582.0), "2026070582")
        self.assertEqual(etapa1.normalizar_id("ABC-01"), "ABC-01")


if __name__ == "__main__":
    unittest.main()
