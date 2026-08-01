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


def entrada(data: str, id_chamado, categoria_depois: str, linha=999) -> list:
    reg = [""] * len(CAB)
    reg[rest.I_DATA] = data
    reg[rest.I_LINHA] = linha
    reg[rest.I_ID] = id_chamado
    reg[rest.I_CATEGORIA_DEPOIS] = categoria_depois
    return reg


CORTE = datetime(2026, 8, 1, 0, 0)


class TestUltimoValorPorId(unittest.TestCase):
    def test_indices_batem_com_o_cabecalho_real(self):
        """Se reclassificar_validados.py mudar a ordem, este teste quebra."""
        self.assertEqual(CAB[rest.I_DATA], "data")
        self.assertEqual(CAB[rest.I_LINHA], "linha_planilha")
        self.assertEqual(CAB[rest.I_ID], "id_chamado")
        self.assertEqual(CAB[rest.I_CATEGORIA_DEPOIS], "categoria_depois")

    def test_toma_a_entrada_mais_recente_por_id(self):
        valores = [CAB,
                   entrada("10/07/2026 03:00", 1607, "Elétrica > Gerador"),
                   entrada("25/07/2026 03:00", 1607, "Elétrica > Iluminação"),
                   entrada("18/07/2026 03:00", 1607, "Elétrica > Tomada")]
        restaurar, _ = rest.ultimo_valor_por_id(valores, CORTE)
        self.assertEqual(restaurar, {"1607": "Elétrica > Iluminação"})

    def test_indexa_por_id_e_ignora_a_linha_registrada(self):
        """O nucleo do incidente: a mesma linha_planilha pode ter servido a
        chamados diferentes em epocas diferentes (o IMPORTRANGE deslocou as
        linhas). A chave tem de ser o ID."""
        valores = [CAB,
                   entrada("10/07/2026 03:00", 1607, "Cat do 1607", linha=10),
                   entrada("11/07/2026 03:00", 1693, "Cat do 1693", linha=10)]
        restaurar, _ = rest.ultimo_valor_por_id(valores, CORTE)
        self.assertEqual(restaurar, {"1607": "Cat do 1607",
                                     "1693": "Cat do 1693"})

    def test_ignora_entradas_do_dia_do_incidente(self):
        """O objetivo e voltar ao estado ANTERIOR: o que foi gravado em 01/08
        pelo reprocessamento nao pode ser usado como fonte de restauracao."""
        valores = [CAB,
                   entrada("28/07/2026 03:00", 77, "Hidráulica > Vazamento"),
                   entrada("01/08/2026 05:10", 77, "PREDICAO NOVA DO BERTIMBAU")]
        restaurar, diag = rest.ultimo_valor_por_id(valores, CORTE)
        self.assertEqual(restaurar, {"77": "Hidráulica > Vazamento"})
        self.assertEqual(diag.get("posterior_ao_corte"), 1)

    def test_varios_chamados_independentes(self):
        valores = [CAB,
                   entrada("10/07/2026 03:00", 2, "A"),
                   entrada("11/07/2026 03:00", 3, "B"),
                   entrada("12/07/2026 03:00", 2, "C")]
        restaurar, _ = rest.ultimo_valor_por_id(valores, CORTE)
        self.assertEqual(restaurar, {"2": "C", "3": "B"})

    def test_descarta_malformadas_sem_derrubar_o_lote(self):
        valores = [CAB,
                   entrada("data ruim", 2, "X"),
                   entrada("10/07/2026 03:00", "", "Y"),
                   entrada("10/07/2026 03:00", 4, ""),
                   ["10/07/2026 03:00", "run"],
                   entrada("10/07/2026 03:00", 9, "Bom")]
        restaurar, diag = rest.ultimo_valor_por_id(valores, CORTE)
        self.assertEqual(restaurar, {"9": "Bom"})
        self.assertEqual(diag.get("data_invalida"), 1)
        self.assertEqual(diag.get("id_vazio"), 1)
        self.assertEqual(diag.get("categoria_vazia"), 1)
        self.assertEqual(diag.get("linha_curta"), 1)

    def test_id_aceita_valor_numerico_do_sheets(self):
        """UNFORMATTED_VALUE devolve numero (12.0), nao string."""
        valores = [CAB, entrada("10/07/2026 03:00", 12.0, "Z")]
        restaurar, _ = rest.ultimo_valor_por_id(valores, CORTE)
        self.assertEqual(restaurar, {"12": "Z"})

    def test_id_alfanumerico_preservado(self):
        """Ha IDs longos no historico real (ex.: 2019050189)."""
        valores = [CAB, entrada("10/07/2026 03:00", "2019050189", "W")]
        restaurar, _ = rest.ultimo_valor_por_id(valores, CORTE)
        self.assertEqual(restaurar, {"2019050189": "W"})

    def test_historico_so_com_cabecalho(self):
        restaurar, _ = rest.ultimo_valor_por_id([CAB], CORTE)
        self.assertEqual(restaurar, {})


class TestNormalizarId(unittest.TestCase):
    def test_formas_equivalentes(self):
        self.assertEqual(rest.normalizar_id(1693), "1693")
        self.assertEqual(rest.normalizar_id(1693.0), "1693")
        self.assertEqual(rest.normalizar_id(" 1693 "), "1693")
        self.assertEqual(rest.normalizar_id("1693"), "1693")

    def test_vazios(self):
        for v in ("", None, "   "):
            self.assertEqual(rest.normalizar_id(v), "")


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
