#!/usr/bin/env python3
"""Teste de regressao: src.planilha.normalizar_categoria aplica o mapa de-para
de config_categorias_canonicas.json (nomes de categoria GLPI renomeados que
ficaram presos no historico da planilha, ex.: 'Climatização > Ar
condicionado' -> '... > Ar condicionado split', achado em 2026-07-25:
517 chamados historicos com o nome bare tinham taxa de concordancia IA x
historico de so 59,96%, contra 94,27% da variante 'split'). Categorias fora
do mapa devem retornar inalteradas; o mapa real do repositorio e usado (nao
um fake), para pegar erros de sintaxe/encoding no JSON tambem."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import planilha as pl  # noqa: E402


class TestNormalizarCategoria(unittest.TestCase):
    def test_categoria_ar_condicionado_bare_normaliza_para_split(self):
        self.assertEqual(
            pl.normalizar_categoria("Climatização > Ar condicionado"),
            "Climatização > Ar condicionado split",
        )

    def test_categoria_sistemas_incendio_bare_normaliza_para_nome_completo(self):
        self.assertEqual(
            pl.normalizar_categoria("Manutenção Preventiva > Sistemas de incêndio"),
            "Manutenção Preventiva > Sistemas de combate a incêndio (extintores, hidrantes)",
        )

    def test_categoria_ja_canonica_permanece_inalterada(self):
        self.assertEqual(
            pl.normalizar_categoria("Climatização > Ar condicionado split"),
            "Climatização > Ar condicionado split",
        )

    def test_categoria_seguranca_incendio_nao_e_afetada(self):
        """Pai 'Segurança contra Incêndio' é legítimo e diferente — não deve
        ser confundido com o mapeamento de 'Manutenção Preventiva'."""
        original = "Segurança contra Incêndio > Sistemas de combate a incêndio (extintores, hidrantes)"
        self.assertEqual(pl.normalizar_categoria(original), original)

    def test_categoria_fora_do_mapa_retorna_inalterada(self):
        self.assertEqual(
            pl.normalizar_categoria("Elétrica > Instalações elétricas"),
            "Elétrica > Instalações elétricas",
        )

    def test_string_vazia_nao_quebra(self):
        self.assertEqual(pl.normalizar_categoria(""), "")


if __name__ == "__main__":
    unittest.main()
