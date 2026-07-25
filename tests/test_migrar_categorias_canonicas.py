#!/usr/bin/env python3
"""Teste offline de scripts/migracoes/migrar_categorias_canonicas.py.

Cobre: identifica corretamente as linhas com nome de categoria obsoleto na
coluna informada (por padrao 'Classificação IA' — a saida do proprio
classificador) usando o mapa real de config_categorias_canonicas.json; NAO
marca linhas ja com o nome atual, nem categorias fora do mapa (ex.:
'Segurança contra Incêndio', que e um pai legitimo e diferente). Cobre
tambem as duas guardas de seguranca adicionadas apos o incidente de
2026-07-25 (escrita na coluna C, que e IMPORTRANGE, quebrou o array da
planilha inteira): (1) recusa explicita de 'CATEGORIA COMPLETA' como
coluna-alvo; (2) recusa de escrita se a amostra da coluna-alvo contiver
formula."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "migracoes"))

import planilha as pl  # noqa: E402
import migrar_categorias_canonicas as mig  # noqa: E402


class _WorksheetFalsa:
    def __init__(self, valores, formulas=None):
        self._valores = [list(r) for r in valores]
        self._formulas = formulas or {}  # {"G2": "=ALGO"}

    def get_values(self, *_args, **_kwargs):
        return [list(r) for r in self._valores]

    def row_values(self, n):
        idx = n - 1
        return list(self._valores[idx]) if 0 <= idx < len(self._valores) else []

    def acell(self, endereco, value_render_option=None):  # noqa: ARG002
        class _Cel:
            def __init__(self, value):
                self.value = value
        return _Cel(self._formulas.get(endereco))


class TestCalcularCorrecoes(unittest.TestCase):
    def setUp(self):
        self.mapa = pl._carregar_mapa_categorias_canonicas()  # noqa: SLF001
        self.assertTrue(self.mapa, "mapa de categorias canonicas nao deveria estar vazio")

    def _ws(self, categorias, cab_extra=("ID Chamado", "TÍTULO"), nome_coluna="CATEGORIA COMPLETA"):
        cab = list(cab_extra) + [nome_coluna]
        linhas = [cab] + [[i + 1, f"titulo {i}", cat] for i, cat in enumerate(categorias)]
        return _WorksheetFalsa(linhas)

    def test_identifica_linhas_com_nome_obsoleto(self):
        ws = self._ws([
            "Climatização > Ar condicionado",
            "Climatização > Ar condicionado split",
            "Elétrica > Instalações elétricas",
        ])
        config = {"range_leitura": "A:C"}
        col, a_corrigir, contagem = mig.calcular_correcoes(ws, config, self.mapa, "CATEGORIA COMPLETA")
        self.assertEqual(col, 3)
        self.assertEqual(a_corrigir, {2: "Climatização > Ar condicionado split"})
        self.assertEqual(contagem["Climatização > Ar condicionado"], 1)

    def test_coluna_classificacao_ia_e_identificada(self):
        ws = self._ws(
            ["Climatização > Ar condicionado", "Elétrica > Iluminação"],
            nome_coluna="Classificação IA",
        )
        config = {"range_leitura": "A:C"}
        col, a_corrigir, _ = mig.calcular_correcoes(ws, config, self.mapa, "Classificação IA")
        self.assertEqual(col, 3)
        self.assertEqual(a_corrigir, {2: "Climatização > Ar condicionado split"})

    def test_categoria_ja_canonica_nao_e_marcada(self):
        ws = self._ws(["Climatização > Ar condicionado split"] * 3)
        config = {"range_leitura": "A:C"}
        _, a_corrigir, _ = mig.calcular_correcoes(ws, config, self.mapa, "CATEGORIA COMPLETA")
        self.assertEqual(a_corrigir, {})

    def test_pai_seguranca_incendio_nao_e_tocado(self):
        ws = self._ws([
            "Segurança contra Incêndio > Sistemas de combate a incêndio (extintores, hidrantes)",
            "Manutenção Preventiva > Sistemas de incêndio",
        ])
        config = {"range_leitura": "A:C"}
        _, a_corrigir, _ = mig.calcular_correcoes(ws, config, self.mapa, "CATEGORIA COMPLETA")
        self.assertEqual(
            a_corrigir,
            {3: "Manutenção Preventiva > Sistemas de combate a incêndio (extintores, hidrantes)"},
        )

    def test_planilha_vazia_nao_quebra(self):
        ws = _WorksheetFalsa([])
        config = {"range_leitura": "A:C"}
        _, a_corrigir, _ = mig.calcular_correcoes(ws, config, self.mapa, "CATEGORIA COMPLETA")
        self.assertEqual(a_corrigir, {})


class TestGuardasDeSeguranca(unittest.TestCase):
    """Cobre as guardas adicionadas apos o incidente de 2026-07-25."""

    def test_coluna_categoria_completa_e_proibida_por_nome(self):
        self.assertIn("categoria completa", mig.COLUNAS_PROIBIDAS)

    def test_confirmar_nao_e_formula_aceita_valor_literal(self):
        ws = _WorksheetFalsa([["h"]], formulas={"G2": "Climatização > Ar condicionado split"})
        self.assertTrue(mig.confirmar_nao_e_formula(ws, 7, [2]))

    def test_confirmar_nao_e_formula_recusa_importrange(self):
        ws = _WorksheetFalsa([["h"]], formulas={"C2": '=IMPORTRANGE("id";"aba!A:F")'})
        self.assertFalse(mig.confirmar_nao_e_formula(ws, 3, [2]))

    def test_confirmar_nao_e_formula_recusa_se_qualquer_linha_da_amostra_for_formula(self):
        ws = _WorksheetFalsa([["h"]], formulas={"G2": "texto normal", "G3": "=ARRAYFORMULA(A2:A)"})
        self.assertFalse(mig.confirmar_nao_e_formula(ws, 7, [2, 3]))


if __name__ == "__main__":
    unittest.main()
