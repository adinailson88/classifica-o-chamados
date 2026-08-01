#!/usr/bin/env python3
"""Teste offline de scripts/migracoes/restaurar_coluna_o.py.

Cobre a logica pura de reconstrucao da coluna O a partir da trilha
RECLASS_HISTORICO (incidente de 2026-08-01, quando apagar O dessincronizou os
vereditos humanos da coluna P): escolhe a ULTIMA entrada por linha_planilha,
respeita o corte temporal (entradas do proprio dia do incidente nao podem ser
usadas para restaurar), e descarta entradas malformadas sem derrubar o lote.
"""

from __future__ import annotations

import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "migracoes"))

import restaurar_coluna_o as rest  # noqa: E402

CAB = [
    "data", "run_id", "modelo", "tipo_rodada", "linha_planilha", "id_chamado",
    "categoria_referencia", "categoria_antes", "confianca_antes", "acerto_antes",
    "categoria_depois", "confianca_depois", "acerto_depois", "mudou",
    "delta_confianca", "resultado", "base_comparacao", "metodo_reclassificacao",
    "limiar_alta_confianca", "usar_calibrado", "so_validados", "max_turnos",
    "tamanho_turno", "gravou_coluna_2",
]


def entrada(data: str, linha, categoria_depois: str) -> list:
    reg = [""] * len(CAB)
    reg[rest.I_DATA] = data
    reg[rest.I_LINHA] = linha
    reg[rest.I_CATEGORIA_DEPOIS] = categoria_depois
    return reg


CORTE = datetime(2026, 8, 1, 0, 0)


class TestUltimoValorPorLinha(unittest.TestCase):
    def test_indices_batem_com_o_cabecalho_real(self):
        """Se reclassificar_validados.py mudar a ordem, este teste quebra."""
        self.assertEqual(CAB[rest.I_DATA], "data")
        self.assertEqual(CAB[rest.I_LINHA], "linha_planilha")
        self.assertEqual(CAB[rest.I_CATEGORIA_DEPOIS], "categoria_depois")

    def test_toma_a_entrada_mais_recente_por_linha(self):
        valores = [CAB,
                   entrada("10/07/2026 03:00", 2, "Elétrica > Gerador"),
                   entrada("25/07/2026 03:00", 2, "Elétrica > Iluminação"),
                   entrada("18/07/2026 03:00", 2, "Elétrica > Tomada")]
        restaurar, _ = rest.ultimo_valor_por_linha(valores, CORTE)
        self.assertEqual(restaurar, {2: "Elétrica > Iluminação"})

    def test_ignora_entradas_do_dia_do_incidente(self):
        """O objetivo e voltar ao estado ANTERIOR: o que foi gravado em 01/08
        pelo reprocessamento nao pode ser usado como fonte de restauracao."""
        valores = [CAB,
                   entrada("28/07/2026 03:00", 7, "Hidráulica > Vazamento"),
                   entrada("01/08/2026 05:10", 7, "PREDICAO NOVA DO BERTIMBAU")]
        restaurar, diag = rest.ultimo_valor_por_linha(valores, CORTE)
        self.assertEqual(restaurar, {7: "Hidráulica > Vazamento"})
        self.assertEqual(diag.get("posterior_ao_corte"), 1)

    def test_varias_linhas_independentes(self):
        valores = [CAB,
                   entrada("10/07/2026 03:00", 2, "A"),
                   entrada("11/07/2026 03:00", 3, "B"),
                   entrada("12/07/2026 03:00", 2, "C")]
        restaurar, _ = rest.ultimo_valor_por_linha(valores, CORTE)
        self.assertEqual(restaurar, {2: "C", 3: "B"})

    def test_descarta_malformadas_sem_derrubar_o_lote(self):
        valores = [CAB,
                   entrada("data ruim", 2, "X"),
                   entrada("10/07/2026 03:00", "nao numero", "Y"),
                   entrada("10/07/2026 03:00", 4, ""),
                   ["10/07/2026 03:00", "run"],
                   entrada("10/07/2026 03:00", 9, "Bom")]
        restaurar, diag = rest.ultimo_valor_por_linha(valores, CORTE)
        self.assertEqual(restaurar, {9: "Bom"})
        self.assertEqual(diag.get("data_invalida"), 1)
        self.assertEqual(diag.get("linha_invalida"), 1)
        self.assertEqual(diag.get("categoria_vazia"), 1)
        self.assertEqual(diag.get("linha_curta"), 1)

    def test_linha_aceita_valor_numerico_do_sheets(self):
        """UNFORMATTED_VALUE devolve numero, nao string."""
        valores = [CAB, entrada("10/07/2026 03:00", 12.0, "Z")]
        restaurar, _ = rest.ultimo_valor_por_linha(valores, CORTE)
        self.assertEqual(restaurar, {12: "Z"})

    def test_historico_so_com_cabecalho(self):
        restaurar, _ = rest.ultimo_valor_por_linha([CAB], CORTE)
        self.assertEqual(restaurar, {})


class TestParseData(unittest.TestCase):
    def test_formatos_aceitos(self):
        self.assertEqual(rest.parse_data("01/08/2026 04:30"),
                         datetime(2026, 8, 1, 4, 30))
        self.assertEqual(rest.parse_data("01/08/2026 04:30:15"),
                         datetime(2026, 8, 1, 4, 30, 15))
        self.assertEqual(rest.parse_data("01/08/2026"), datetime(2026, 8, 1))

    def test_invalidos(self):
        for v in ("", None, "ontem", "2026-08-01"):
            self.assertIsNone(rest.parse_data(v))


class TestGuardas(unittest.TestCase):
    def test_coluna_c_esta_na_lista_de_proibidas(self):
        self.assertIn("categoria completa", rest.COLUNAS_PROIBIDAS)

    def test_coluna_alvo_nao_e_proibida(self):
        self.assertNotIn(rest.COLUNA_ALVO.casefold(), rest.COLUNAS_PROIBIDAS)


if __name__ == "__main__":
    unittest.main()
