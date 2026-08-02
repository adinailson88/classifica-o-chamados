#!/usr/bin/env python3
"""Teste offline de regressao para o bug corrigido em calibracao.py (2026-07-23):
"acerto_validado" comparava a classificacao da IA apenas contra a marcacao BRUTA
da coluna N (CONFERENCIA IA) isolada. Como, no uso real, a coluna N quase nunca
recebe "Errado" (o erro da IA costuma ficar registrado via M/GLPI, sem tocar N),
essa comparacao ficava artificialmente igual a 1.0 em toda faixa de confianca.

O calculo correto compara a classificacao do executor contra a categoria DECIDIDA
pela memoria M/N/P (decisao_validada.verdade_validada) -- a mesma verdade usada em
avaliacao_final.py -- o que inclui corretamente os casos em que o erro da IA foi
capturado via M, nao via N. Este teste reproduz os dois padroes lado a lado.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import calibracao as cb  # noqa: E402


class _WorksheetFalsa:
    def __init__(self, valores):
        self.valores = valores

    def get_values(self, *_args, **_kwargs):
        return self.valores


class _SpreadsheetFalsa:
    """Spreadsheet de mentira com valores distintos por aba (nome -> linhas)."""

    def __init__(self, abas: dict):
        self.abas = abas

    def worksheet(self, nome):
        return _WorksheetFalsa(self.abas[nome])


def _linha_principal(*valores, largura=16):
    return list(valores) + [""] * max(0, largura - len(valores))


def _linha_snapshot(*valores, largura=7):
    return list(valores) + [""] * max(0, largura - len(valores))


class TestCalibracaoAcertoValidado(unittest.TestCase):
    def setUp(self):
        cab_principal = _linha_principal(
            "ID", "TITULO", "CATEGORIA COMPLETA", "D", "E", "F",
            "Classificacao IA", "H", "I", "J", "K", "L",
            "CONFERENCIA GLPI", "CONFERENCIA IA", "Classificacao IA - 2",
            "CONFERENCIA IA - 2")
        linhas_principal = [
            cab_principal,
            # linha 2: historico confirmado certo (M=Correto), IA (G) diverge do
            # historico e N fica em branco -- erro da IA capturado via M, nao via N.
            _linha_principal("1", "", "HID", "", "", "", "ELE",
                             "", "", "", "", "", "Correto", "", "", ""),
            # linha 3: IA confirmada certa via N.
            _linha_principal("2", "", "HID", "", "", "", "HID",
                             "", "", "", "", "", "", "Correto", "", ""),
            # linha 4: IA confirmada certa via N.
            _linha_principal("3", "", "AGUA", "", "", "", "AGUA",
                             "", "", "", "", "", "", "Correto", "", ""),
            # linha 5: historico confirmado certo (M=Correto), IA diverge, N em
            # branco -- mesmo padrao da linha 2.
            _linha_principal("4", "", "ELETRICA", "", "", "", "STRUCT",
                             "", "", "", "", "", "Correto", "", "", ""),
        ]
        snap = [
            ["cab"] * 7,
            # r[1]=linha, r[2]=id_chamado, r[3]=cat_original, r[4]=cat_ia,
            # r[5]=conf, r[6]=executor. O id e o que casa com a aba principal:
            # a linha nao serve, porque a base muda de tamanho (incidente de
            # 2026-08-02).
            _linha_snapshot("x", "2", "1", "HID", "ELE", "0.97", "lstm"),
            _linha_snapshot("x", "3", "2", "HID", "HID", "0.97", "lstm"),
            _linha_snapshot("x", "4", "3", "AGUA", "AGUA", "0.97", "lstm"),
            _linha_snapshot("x", "5", "4", "ELETRICA", "STRUCT", "0.97", "lstm"),
        ]
        self.sh = _SpreadsheetFalsa({"PRINCIPAL": linhas_principal, "SNAP": snap})
        self.config = {
            "abas_experimento": {"snapshot_etapa_1": "SNAP"},
            "aba_principal": "PRINCIPAL",
            "objetivo_final": {"confianca_minima_alvo": 0.95},
            "run_id": "teste",
        }

    def test_acerto_validado_nao_fica_preso_em_1_0(self):
        dados = cb.calcular(self.sh, self.config)
        faixa = dados["faixa_alvo_95"]
        # 4 linhas decididas (M ou N), 2 corretas (linhas 3 e 4) e 2 erradas
        # (linhas 2 e 5, capturadas via M) -> acerto real = 0.5, nao 1.0.
        self.assertEqual(faixa["n_validados"], 4)
        self.assertAlmostEqual(faixa["acerto_validado"], 0.5)

    def test_matriz_ia_x_glpi_usa_verdade_decidida(self):
        # Mesma correcao aplicada a matriz_ia_x_glpi (2026-07-23): linhas 2 e 5
        # tem decisao travada via M (glpi_ok), mas a IA diverge (ia_erro) --
        # antes da correcao essas linhas eram ignoradas por N estar em branco,
        # e a matriz so contava linhas com M E N ambas marcadas.
        dados = cb.calcular(self.sh, self.config)
        matriz = dados["validacao_humana"]["matriz_ia_x_glpi"]
        self.assertEqual(matriz["ia_ok_glpi_ok"], 2)     # linhas 3 e 4
        self.assertEqual(matriz["ia_erro_glpi_ok"], 2)   # linhas 2 e 5
        self.assertEqual(matriz["ia_ok_glpi_erro"], 0)
        self.assertEqual(matriz["ia_erro_glpi_erro"], 0)
        self.assertEqual(sum(matriz.values()), 4)

    def test_acerto_bruto_da_coluna_n_isolada_seria_1_0(self):
        # Reproduz o comportamento ANTIGO (bug) para provar que a diferenca e
        # real: usando so a marcacao bruta da coluna N, so as linhas 3 e 4 "
        # contam, e as duas sao 'Correto' -> 1.0, escondendo os erros das
        # linhas 2 e 5 capturados via M.
        import planilha as pl
        conferencias = pl.ler_conferencias(self.sh, self.config["aba_principal"])
        marcados_n = [v for v in conferencias.values() if v.get("ia") is not None]
        self.assertEqual(len(marcados_n), 2)
        self.assertTrue(all(v["ia"] == "Correto" for v in marcados_n))


if __name__ == "__main__":
    unittest.main(verbosity=2)
