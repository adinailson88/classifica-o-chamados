#!/usr/bin/env python3
"""Fase 4 do plano de reducao de celulas (RECLASS_HISTORICO, 2026-09):
ler_historico_combinado() precisa continuar dando aos consumidores forenses
(restaurar_coluna_o.py, verificar_alinhamento_linhas.py) acesso ao historico
anterior ao truncamento da Fase 3 -- que so existe no CSV arquivado, ja que a
aba viva foi encolhida para so as entradas recentes."""

from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import planilha as pl  # noqa: E402

CAB = ["data", "id_chamado", "categoria_depois"]


class _WsFalsa:
    def __init__(self, valores):
        self._valores = valores

    def get_values(self, range_a1, value_render_option=None):  # noqa: ARG002
        return self._valores


class _ShFalsa:
    def __init__(self, abas):
        self._abas = abas

    def worksheet(self, nome):
        return self._abas[nome]


def escrever_csv(caminho: Path, linhas: list[list[str]]) -> None:
    with caminho.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(linhas)


class TestLerHistoricoCombinado(unittest.TestCase):
    def test_sem_arquivo_le_so_a_planilha_viva(self):
        vivo = [CAB, ["04/09/2026 10:00", "111", "A"]]
        sh = _ShFalsa({"RECLASS_HISTORICO": _WsFalsa(vivo)})

        hist = pl.ler_historico_combinado(sh, "RECLASS_HISTORICO")

        self.assertEqual(hist, vivo)

    def test_combina_arquivo_com_planilha_viva(self):
        vivo = [CAB, ["04/09/2026 12:00", "222", "B"]]  # entrada recente, pos-truncamento
        sh = _ShFalsa({"RECLASS_HISTORICO": _WsFalsa(vivo)})

        with TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "arquivo.csv"
            escrever_csv(caminho, [CAB, ["17/07/2026 07:00", "111", "A"]])  # entrada antiga

            hist = pl.ler_historico_combinado(sh, "RECLASS_HISTORICO", arquivo_csv=caminho)

        # cabecalho da planilha viva, depois arquivo, depois viva -- as duas entradas
        # de dado presentes, nenhuma perdida.
        self.assertEqual(hist[0], CAB)
        self.assertEqual(len(hist), 3)
        self.assertIn(["17/07/2026 07:00", "111", "A"], hist)
        self.assertIn(["04/09/2026 12:00", "222", "B"], hist)

    def test_arquivo_vazio_nao_quebra(self):
        vivo = [CAB, ["04/09/2026 12:00", "222", "B"]]
        sh = _ShFalsa({"RECLASS_HISTORICO": _WsFalsa(vivo)})

        with TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "vazio.csv"
            caminho.touch()

            hist = pl.ler_historico_combinado(sh, "RECLASS_HISTORICO", arquivo_csv=caminho)

        self.assertEqual(hist, vivo)

    def test_planilha_viva_sem_dados_ainda_usa_cabecalho_do_arquivo(self):
        # cenario logo apos o truncamento: a aba viva tem so o cabecalho.
        vivo = [CAB]
        sh = _ShFalsa({"RECLASS_HISTORICO": _WsFalsa(vivo)})

        with TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "arquivo.csv"
            escrever_csv(caminho, [CAB, ["17/07/2026 07:00", "111", "A"]])

            hist = pl.ler_historico_combinado(sh, "RECLASS_HISTORICO", arquivo_csv=caminho)

        self.assertEqual(hist, [CAB, ["17/07/2026 07:00", "111", "A"]])


if __name__ == "__main__":
    unittest.main()
