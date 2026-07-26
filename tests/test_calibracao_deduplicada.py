#!/usr/bin/env python3
"""Testes offline da deduplicação defensiva do SNAPSHOT_ETAPA_1."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import calibracao_deduplicada as cd  # noqa: E402


class TestDeduplicarSnapshot(unittest.TestCase):
    def test_mantem_ultima_ocorrencia_por_linha_planilha(self):
        valores = [
            ["data", "linha_planilha", "id", "historico", "ia", "conf", "executor"],
            ["t1", "2", "a", "H", "A", 0.4, "lstm"],
            ["t1", "3", "b", "H", "B", 0.5, "lstm"],
            ["t2", "2", "a", "H", "H", 0.9, "lstm"],
        ]

        deduplicadas, removidas = cd.deduplicar_snapshot(valores)

        self.assertEqual(removidas, 1)
        self.assertEqual(len(deduplicadas), 3)
        self.assertEqual(deduplicadas[1][1], "3")
        self.assertEqual(deduplicadas[2][1], "2")
        self.assertEqual(deduplicadas[2][4], "H")
        self.assertEqual(deduplicadas[2][5], 0.9)

    def test_preserva_linhas_sem_chave(self):
        valores = [
            ["data", "linha_planilha", "id", "historico", "ia", "conf", "executor"],
            ["t1", "", "a", "H", "A", 0.4, "lstm"],
            ["t2", "", "b", "H", "B", 0.5, "lstm"],
        ]

        deduplicadas, removidas = cd.deduplicar_snapshot(valores)

        self.assertEqual(removidas, 0)
        self.assertEqual(deduplicadas, valores)

    def test_snapshot_vazio_ou_so_cabecalho(self):
        self.assertEqual(cd.deduplicar_snapshot([]), ([], 0))
        cabecalho = [["data", "linha_planilha"]]
        self.assertEqual(cd.deduplicar_snapshot(cabecalho), (cabecalho, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
