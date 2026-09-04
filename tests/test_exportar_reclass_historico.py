#!/usr/bin/env python3
"""Fase 1 do plano de reducao de celulas (RECLASS_HISTORICO, 2026-09): confere
que a exportacao grava CSV + manifesto completos e consistentes, e que
--limite-linhas de fato limita (usado so para teste manual em amostra)."""

from __future__ import annotations

import csv
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "migracoes"))

import exportar_reclass_historico as exp  # noqa: E402


class _WsFake:
    def __init__(self, valores):
        self._valores = valores

    def get_values(self, value_render_option=None):  # noqa: ARG002
        return [list(r) for r in self._valores]


CABECALHO = ["data", "run_id", "modelo", "linha_planilha", "id_chamado", "categoria_depois"]


def linha(id_chamado, categoria="Eletrica > Iluminacao", data="01/08/2026 10:00"):
    return [data, "run1", "linear_svc", "10", id_chamado, categoria]


class TestExportar(unittest.TestCase):
    def test_exporta_csv_e_manifesto_completos(self):
        valores = [CABECALHO, linha("111"), linha("222"), linha("333")]
        ws = _WsFake(valores)

        with TemporaryDirectory() as tmp:
            saida_dir = Path(tmp)
            manifesto = exp.exportar(ws, "RECLASS_HISTORICO", saida_dir,
                                      gerado="04/09/2026 10:30")

            self.assertEqual(manifesto["linhas_exportadas"], 3)
            self.assertEqual(manifesto["linhas_na_planilha_incluindo_cabecalho"], 4)
            self.assertEqual(manifesto["colunas"], CABECALHO)

            caminho_csv = saida_dir / manifesto["arquivo_csv"]
            self.assertTrue(caminho_csv.exists())
            with caminho_csv.open(encoding="utf-8", newline="") as f:
                linhas_csv = list(csv.reader(f))
            self.assertEqual(linhas_csv[0], CABECALHO)
            self.assertEqual(len(linhas_csv), 4)  # cabecalho + 3
            self.assertEqual(linhas_csv[1][4], "111")

            caminho_manifesto = saida_dir / (
                Path(manifesto["arquivo_csv"]).stem + "_manifesto.json")
            self.assertTrue(caminho_manifesto.exists())
            with caminho_manifesto.open(encoding="utf-8") as f:
                do_disco = json.load(f)
            self.assertEqual(do_disco, manifesto)

    def test_limite_linhas_restringe_amostra(self):
        valores = [CABECALHO, linha("1"), linha("2"), linha("3"), linha("4")]
        ws = _WsFake(valores)

        with TemporaryDirectory() as tmp:
            manifesto = exp.exportar(ws, "RECLASS_HISTORICO", Path(tmp),
                                      gerado="04/09/2026 10:30", limite_linhas=2)

            self.assertEqual(manifesto["linhas_exportadas"], 2)
            # o total na planilha continua sendo o real, mesmo limitando a amostra exportada.
            self.assertEqual(manifesto["linhas_na_planilha_incluindo_cabecalho"], 5)

    def test_aba_vazia_nao_gera_arquivo(self):
        ws = _WsFake([])

        with TemporaryDirectory() as tmp:
            manifesto = exp.exportar(ws, "RECLASS_HISTORICO", Path(tmp),
                                      gerado="04/09/2026 10:30")

            self.assertIsNone(manifesto["arquivo_csv"])
            self.assertEqual(manifesto["linhas_exportadas"], 0)
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_carimbo_de_data_hora_sem_caracteres_invalidos_para_nome_de_arquivo(self):
        carimbo = exp.carimbo_de_data_hora("04/09/2026 10:30")
        self.assertNotIn("/", carimbo)
        self.assertNotIn(":", carimbo)
        self.assertNotIn(" ", carimbo)


if __name__ == "__main__":
    unittest.main()
