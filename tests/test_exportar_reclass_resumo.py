#!/usr/bin/env python3
"""Teste offline de regressao: exportar_reclass_resumo deduplica por
linha_planilha antes de agregar (achado de 2026-07-23: RECLASS__random_forest
tinha 4.737 linhas duplicadas, total_reclassificado=18.049 excedendo o
tamanho da base de 13.965 chamados). Sem a deduplicacao, uma linha
reclassificada duas vezes seria contada duas vezes em total_reclassificado
e em corrigidos/prejudicados, inflando o ganho liquido."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from exportar_dashboard import exportar_reclass_resumo  # noqa: E402


class _WorksheetFalsa:
    def __init__(self, valores):
        self.valores = valores

    def get_values(self, *_args, **_kwargs):
        return self.valores


class _SpreadsheetFalsa:
    def __init__(self, abas: dict):
        self.abas = abas

    def worksheet(self, nome):
        return _WorksheetFalsa(self.abas[nome])


class TestExportarReclassResumo(unittest.TestCase):
    def test_deduplica_linha_planilha_repetida(self):
        cab = ["run_id", "modelo", "linha_planilha", "id_chamado", "categoria_original",
               "categoria_prevista", "resultado", "base_comparacao", "mudou", "data"]
        linhas = [
            cab,
            # linha 2 reclassificada DUAS vezes (duplicata real, como no achado)
            ["r1", "rf", "2", "x", "A", "B", "corrigido", "validada", "true", "2026-07-23"],
            ["r1", "rf", "2", "x", "A", "B", "corrigido", "validada", "true", "2026-07-23"],
            # linha 3, unica
            ["r1", "rf", "3", "x", "C", "C", "mantido_correto", "validada", "false", "2026-07-23"],
        ]
        sh = _SpreadsheetFalsa({"RECLASS__random_forest": linhas})
        config = {"multimodelo": {
            "aba_reclassificacao": "RECLASS__{modelo}",
            "modelos_leves": ["random_forest"], "modelos_pesados": [],
        }}
        saida = exportar_reclass_resumo(sh, config)
        m = saida["por_modelo"][0]
        self.assertEqual(m["modelo"], "random_forest")
        # 2 linhas distintas (linha_planilha 2 e 3), nao 3 linhas brutas.
        self.assertEqual(m["total_reclassificado"], 2)
        self.assertEqual(m["linhas_duplicadas_removidas"], 1)
        self.assertEqual(m["corrigidos"], 1)  # so 1x, nao 2x

    def test_sem_duplicatas_nao_remove_nada(self):
        cab = ["run_id", "modelo", "linha_planilha", "id_chamado", "categoria_original",
               "categoria_prevista", "resultado", "base_comparacao", "mudou", "data"]
        linhas = [
            cab,
            ["r1", "svc", "2", "x", "A", "A", "mantido_correto", "validada", "false", "2026-07-23"],
            ["r1", "svc", "3", "x", "B", "B", "mantido_correto", "validada", "false", "2026-07-23"],
        ]
        sh = _SpreadsheetFalsa({"RECLASS__linear_svc": linhas})
        config = {"multimodelo": {
            "aba_reclassificacao": "RECLASS__{modelo}",
            "modelos_leves": ["linear_svc"], "modelos_pesados": [],
        }}
        saida = exportar_reclass_resumo(sh, config)
        m = saida["por_modelo"][0]
        self.assertEqual(m["total_reclassificado"], 2)
        self.assertEqual(m["linhas_duplicadas_removidas"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
