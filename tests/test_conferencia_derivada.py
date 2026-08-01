#!/usr/bin/env python3
"""Teste offline de src/conferencia_derivada.py.

Cobre a regra definida pelo pesquisador em 2026-08-01: a conferencia de cada IA
e derivada da conferencia humana do GLPI (coluna M), em vez de uma coluna N
unica que so conferia a IA de producao.

    M='Correto'              -> verdade = C; cada IA e comparada com C
    M='Errado' + Q pree.     -> verdade = Q
    M='Errado' sem Q         -> PENDENTE (nada afirmado; o avaliador decide)
    M vazio                  -> chamado ignorado
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import conferencia_derivada as cd  # noqa: E402

MODELOS = ["lstm", "random_forest", "transformer_ft"]


def chamado(id_, conf_glpi, categoria_glpi, categoria_manual="", linha=2):
    return {"id": id_, "linha": linha, "categoria_glpi": categoria_glpi,
            "conf_glpi": conf_glpi, "categoria_manual": categoria_manual}


class TestVerdadeDoChamado(unittest.TestCase):
    def test_glpi_correto_vira_verdade(self):
        self.assertEqual(cd.verdade_do_chamado("Correto", "Elétrica > Gerador", ""),
                         ("Elétrica > Gerador", cd.FONTE_GLPI))

    def test_glpi_errado_com_q_usa_q(self):
        self.assertEqual(
            cd.verdade_do_chamado("Errado", "Elétrica > Gerador", "Hidráulica > Vazamento"),
            ("Hidráulica > Vazamento", cd.FONTE_MANUAL))

    def test_glpi_errado_sem_q_fica_pendente(self):
        """O caso que o pesquisador pediu para NAO afirmar nada."""
        self.assertEqual(cd.verdade_do_chamado("Errado", "Elétrica > Gerador", ""),
                         ("", ""))

    def test_sem_conferencia_fica_pendente(self):
        self.assertEqual(cd.verdade_do_chamado("", "Elétrica > Gerador", ""), ("", ""))

    def test_qualquer_valor_nao_correto_e_errado(self):
        """Mesma convencao de planilha.ler_conferencias."""
        for v in ("Errado", "errado", "ERRADO", "x", "nao", "0"):
            verdade, fonte = cd.verdade_do_chamado(v, "C", "Q")
            self.assertEqual((verdade, fonte), ("Q", cd.FONTE_MANUAL), v)

    def test_correto_ignora_caixa(self):
        for v in ("Correto", "correto", "CORRETO", " Correto "):
            self.assertEqual(cd.verdade_do_chamado(v, "C", "")[1], cd.FONTE_GLPI, v)


class TestConferir(unittest.TestCase):
    def test_acerto_e_erro(self):
        self.assertEqual(cd.conferir("A", "A"), cd.CORRETO)
        self.assertEqual(cd.conferir("B", "A"), cd.ERRADO)

    def test_sem_verdade_ou_sem_predicao_nao_afirma(self):
        self.assertEqual(cd.conferir("A", ""), cd.PENDENTE)
        self.assertEqual(cd.conferir("", "A"), cd.PENDENTE)


class TestMontarLinhas(unittest.TestCase):
    def test_glpi_correto_avalia_todas_as_ias(self):
        chamados = [chamado("1693", "Correto", "Elétrica > Gerador")]
        predicoes = {
            "lstm": {"1693": "Elétrica > Gerador"},          # acerta
            "random_forest": {"1693": "Hidráulica > Vazamento"},  # erra
            "transformer_ft": {},                             # sem predicao
        }
        linhas, resumo = cd.montar_linhas(chamados, MODELOS, predicoes)
        self.assertEqual(len(linhas), 1)
        self.assertEqual(resumo["verdade_glpi"], 1)
        self.assertEqual(resumo["por_modelo"]["lstm"]["correto"], 1)
        self.assertEqual(resumo["por_modelo"]["random_forest"]["errado"], 1)
        self.assertEqual(resumo["por_modelo"]["transformer_ft"]["sem_predicao"], 1)
        self.assertEqual(resumo["por_modelo"]["lstm"]["acuracia"], 1.0)
        self.assertEqual(resumo["por_modelo"]["random_forest"]["acuracia"], 0.0)
        self.assertIsNone(resumo["por_modelo"]["transformer_ft"]["acuracia"])

    def test_glpi_errado_sem_q_nao_afirma_nada_sobre_as_ias(self):
        """Nucleo do pedido: sem verdade conhecida, nenhuma IA e julgada."""
        chamados = [chamado("1693", "Errado", "Elétrica > Gerador")]
        predicoes = {m: {"1693": "Qualquer Coisa"} for m in MODELOS}
        linhas, resumo = cd.montar_linhas(chamados, MODELOS, predicoes)
        self.assertEqual(resumo["pendente_glpi_errado_sem_q"], 1)
        for m in MODELOS:
            self.assertEqual(resumo["por_modelo"][m]["correto"], 0)
            self.assertEqual(resumo["por_modelo"][m]["errado"], 0)
            self.assertEqual(resumo["por_modelo"][m]["pendente"], 1)
            self.assertIsNone(resumo["por_modelo"][m]["acuracia"])

    def test_glpi_errado_com_q_avalia_contra_q(self):
        chamados = [chamado("1693", "Errado", "Elétrica > Gerador",
                            categoria_manual="Hidráulica > Vazamento")]
        predicoes = {
            "lstm": {"1693": "Hidráulica > Vazamento"},   # acerta a verdade manual
            "random_forest": {"1693": "Elétrica > Gerador"},  # repete o GLPI errado
            "transformer_ft": {},
        }
        _, resumo = cd.montar_linhas(chamados, MODELOS, predicoes)
        self.assertEqual(resumo["verdade_manual"], 1)
        self.assertEqual(resumo["por_modelo"]["lstm"]["correto"], 1)
        self.assertEqual(resumo["por_modelo"]["random_forest"]["errado"], 1)

    def test_sem_conferencia_nao_entra_na_aba(self):
        chamados = [chamado("1693", "", "Elétrica > Gerador")]
        predicoes = {m: {"1693": "Elétrica > Gerador"} for m in MODELOS}
        linhas, resumo = cd.montar_linhas(chamados, MODELOS, predicoes)
        self.assertEqual(linhas, [])
        self.assertEqual(resumo["sem_conferencia"], 1)
        self.assertEqual(resumo["com_conferencia_glpi"], 0)

    def test_indexa_por_id_nao_por_linha(self):
        """A licao do incidente: linha nao identifica chamado."""
        chamados = [chamado("1607", "Correto", "Cat A", linha=9),
                    chamado("1693", "Correto", "Cat B", linha=10)]
        predicoes = {"lstm": {"1607": "Cat A", "1693": "Cat B"},
                     "random_forest": {}, "transformer_ft": {}}
        _, resumo = cd.montar_linhas(chamados, MODELOS, predicoes)
        self.assertEqual(resumo["por_modelo"]["lstm"]["correto"], 2)
        self.assertEqual(resumo["por_modelo"]["lstm"]["errado"], 0)

    def test_cabecalho_tem_duas_colunas_por_modelo(self):
        cab = cd.cabecalho(MODELOS)
        self.assertEqual(cab[:7], ["id_chamado", "linha_planilha", "categoria_glpi",
                                   "conferencia_glpi", "categoria_manual",
                                   "verdade", "fonte_verdade"])
        for m in MODELOS:
            self.assertIn(f"predicao_{m}", cab)
            self.assertIn(f"conferencia_{m}", cab)
        self.assertEqual(len(cab), 7 + 2 * len(MODELOS))

    def test_linha_tem_o_mesmo_tamanho_do_cabecalho(self):
        chamados = [chamado("1693", "Correto", "Cat A")]
        predicoes = {m: {"1693": "Cat A"} for m in MODELOS}
        linhas, _ = cd.montar_linhas(chamados, MODELOS, predicoes)
        self.assertEqual(len(linhas[0]), len(cd.cabecalho(MODELOS)))

    def test_bertimbau_com_cobertura_parcial(self):
        """transformer_ft so tem predicao para parte da base; isso nao pode
        contaminar a acuracia dos demais nem virar 'errado'."""
        chamados = [chamado("1", "Correto", "Cat A"), chamado("2", "Correto", "Cat A")]
        predicoes = {"lstm": {"1": "Cat A", "2": "Cat B"},
                     "random_forest": {}, "transformer_ft": {"1": "Cat A"}}
        _, resumo = cd.montar_linhas(chamados, MODELOS, predicoes)
        t = resumo["por_modelo"]["transformer_ft"]
        self.assertEqual((t["correto"], t["errado"], t["sem_predicao"]), (1, 0, 1))
        self.assertEqual(t["acuracia"], 1.0)
        self.assertEqual(resumo["por_modelo"]["lstm"]["acuracia"], 0.5)


class TestNormalizarId(unittest.TestCase):
    def test_numero_do_sheets(self):
        self.assertEqual(cd.normalizar_id(1693.0), "1693")
        self.assertEqual(cd.normalizar_id("1693"), "1693")
        self.assertEqual(cd.normalizar_id(" 1693 "), "1693")

    def test_id_longo_preservado(self):
        self.assertEqual(cd.normalizar_id("2019050189"), "2019050189")

    def test_vazio(self):
        for v in ("", None, "  "):
            self.assertEqual(cd.normalizar_id(v), "")


if __name__ == "__main__":
    unittest.main()
