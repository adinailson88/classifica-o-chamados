#!/usr/bin/env python3
"""Teste offline de scripts/migracoes/migrar_categorias_canonicas.py.

Cobre: identifica corretamente as linhas com nome de categoria obsoleto
(coluna C) usando o mapa real de config_categorias_canonicas.json; NAO marca
linhas ja com o nome atual, nem categorias fora do mapa (ex.: 'Segurança
contra Incêndio', que e um pai legitimo e diferente, nao deve ser tocado)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "migracoes"))

import planilha as pl  # noqa: E402
import migrar_categorias_canonicas as mig  # noqa: E402


class _WorksheetFalsa:
    def __init__(self, valores):
        self._valores = [list(r) for r in valores]

    def get_values(self, *_args, **_kwargs):
        return [list(r) for r in self._valores]

    def row_values(self, n):
        idx = n - 1
        return list(self._valores[idx]) if 0 <= idx < len(self._valores) else []


class TestCalcularCorrecoes(unittest.TestCase):
    def setUp(self):
        self.mapa = pl._carregar_mapa_categorias_canonicas()  # noqa: SLF001
        self.assertTrue(self.mapa, "mapa de categorias canonicas nao deveria estar vazio")

    def _ws(self, categorias):
        cab = ["ID Chamado", "TÍTULO", "CATEGORIA COMPLETA"]
        linhas = [cab] + [[i + 1, f"titulo {i}", cat] for i, cat in enumerate(categorias)]
        return _WorksheetFalsa(linhas)

    def test_identifica_linhas_com_nome_obsoleto(self):
        ws = self._ws([
            "Climatização > Ar condicionado",
            "Climatização > Ar condicionado split",
            "Elétrica > Instalações elétricas",
        ])
        config = {"range_leitura": "A:C"}
        col_c, a_corrigir, contagem = mig.calcular_correcoes(ws, config, self.mapa)
        self.assertEqual(col_c, 3)
        self.assertEqual(a_corrigir, {2: "Climatização > Ar condicionado split"})
        self.assertEqual(contagem["Climatização > Ar condicionado"], 1)

    def test_categoria_ja_canonica_nao_e_marcada(self):
        ws = self._ws(["Climatização > Ar condicionado split"] * 3)
        config = {"range_leitura": "A:C"}
        _, a_corrigir, _ = mig.calcular_correcoes(ws, config, self.mapa)
        self.assertEqual(a_corrigir, {})

    def test_pai_seguranca_incendio_nao_e_tocado(self):
        ws = self._ws([
            "Segurança contra Incêndio > Sistemas de combate a incêndio (extintores, hidrantes)",
            "Manutenção Preventiva > Sistemas de incêndio",
        ])
        config = {"range_leitura": "A:C"}
        _, a_corrigir, _ = mig.calcular_correcoes(ws, config, self.mapa)
        self.assertEqual(
            a_corrigir,
            {3: "Manutenção Preventiva > Sistemas de combate a incêndio (extintores, hidrantes)"},
        )

    def test_planilha_vazia_nao_quebra(self):
        ws = _WorksheetFalsa([])
        config = {"range_leitura": "A:C"}
        col_c, a_corrigir, contagem = mig.calcular_correcoes(ws, config, self.mapa)
        self.assertEqual(a_corrigir, {})


if __name__ == "__main__":
    unittest.main()
