#!/usr/bin/env python3
"""Regressão: o escritor da Etapa 1 não pode gravar por linha após o ID mudar,
e a fórmula da coluna K (Comparação) precisa acompanhar a planilha quando ela
cresce (ver TestGarantirFormulaK)."""

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


class _CelulaFalsa:
    def __init__(self, value):
        self.value = value


class _WorksheetK:
    def __init__(self, formula_ultima_linha):
        self._formula_ultima_linha = formula_ultima_linha
        self.updates = []

    def acell(self, ref, value_render_option=None):
        assert value_render_option == "FORMULA", "deve ler a FORMULA, nao o valor computado"
        return _CelulaFalsa(self._formula_ultima_linha)

    def update(self, range_name=None, values=None, value_input_option=None):
        self.updates.append({"range_name": range_name, "values": values,
                              "value_input_option": value_input_option})


class TestGarantirFormulaK(unittest.TestCase):
    """Regressão de 09/2026: o gatilho antigo checava o VALOR computado de K2
    (`ws.acell("K2").value`), que fica vazio ("") sempre que G2 ainda não foi
    classificada -- mas também fica vazio quando K2 TEM fórmula e G2 está
    vazia por já ter sido processada e depois limpa. Uma vez que a linha 2
    fosse classificada ao menos uma vez, K2 nunca mais ficava vazia, e o
    bloco de aplicação da fórmula nunca mais rodava -- linhas novas, inseridas
    na planilha depois disso, ficavam com K permanentemente em branco (nem
    fórmula nenhuma, não só resultado vazio)."""

    def test_aplica_quando_ultima_linha_nao_tem_formula(self):
        ws = _WorksheetK(formula_ultima_linha="")

        aplicou = etapa1.garantir_formula_k(ws, total=3)

        self.assertTrue(aplicou)
        self.assertEqual(len(ws.updates), 1)
        u = ws.updates[0]
        self.assertEqual(u["range_name"], "K2:K4")
        self.assertEqual(len(u["values"]), 3)
        self.assertEqual(u["values"][0][0], '=SE(G2="";"";G2=C2)')
        self.assertEqual(u["values"][2][0], '=SE(G4="";"";G4=C4)')
        self.assertEqual(u["value_input_option"], "USER_ENTERED")

    def test_nao_reaplica_quando_ultima_linha_ja_tem_formula(self):
        ws = _WorksheetK(formula_ultima_linha='=SE(G4="";"";G4=C4)')

        aplicou = etapa1.garantir_formula_k(ws, total=3)

        self.assertFalse(aplicou)
        self.assertEqual(ws.updates, [])

    def test_le_formula_e_nao_o_valor_computado_vazio(self):
        # K4 TEM formula, mas ela resulta em "" porque G4 ainda esta vazia --
        # o antigo gatilho (baseado no valor) trataria isso como "sem
        # cobertura" e reaplicaria sem necessidade; o correto e reconhecer que
        # ja ha formula e nao fazer nada.
        ws = _WorksheetK(formula_ultima_linha='=SE(G4="";"";G4=C4)')

        aplicou = etapa1.garantir_formula_k(ws, total=3)

        self.assertFalse(aplicou)


if __name__ == "__main__":
    unittest.main()
