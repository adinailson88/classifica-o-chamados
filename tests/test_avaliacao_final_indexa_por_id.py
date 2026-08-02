#!/usr/bin/env python3
"""Regressao do incidente de 2026-08-02: avaliacao final casava por LINHA.

As abas CLASSIF__<modelo> sao materializadas num momento; a aba principal muda
de tamanho depois. Em 02/08/2026 a base caiu de 14.094 para 14.058 linhas (saida
de 'UFSB > Dinfra > Projetos e Obras' e de 2 chamados excluidos no GLPI) e a
avaliacao final passou a comparar a predicao de um chamado com a verdade de
outro, reportando 0,08 de acerto onde a matriz de confusao, indexada por
id_chamado, media 0,82.

O numero errado era plausivel o suficiente para ser publicado sem chamar
atencao, e por isso o teste fixa o comportamento: a chave e o id_chamado.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import avaliacao_final as af  # noqa: E402
import decisao_validada as dv  # noqa: E402

# Colunas reais de CLASSIF__<modelo> (ver classificacao_multimodelo.py):
# 0=run_id 1=linha_planilha 2=id_chamado 3=categoria_original 4=categoria_ia 5=confianca
CAB_CLASSIF = ["run_id", "linha_planilha", "id_chamado", "categoria_original",
               "categoria_ia", "confianca", "faixa", "executor", "acerto",
               "etapa", "data"]


class _Ws:
    def __init__(self, bloco):
        self._bloco = bloco

    def get_values(self, *_a, **_k):
        return self._bloco


class _Sh:
    def __init__(self, abas):
        self._abas = abas

    def worksheet(self, nome):
        if nome not in self._abas:
            raise KeyError(nome)
        return _Ws(self._abas[nome])


CONFIG = {"multimodelo": {"aba_classificacao": "CLASSIF__{modelo}"}}


def linha_classif(linha_planilha, id_chamado, categoria_ia, conf="0,90"):
    return ["run", linha_planilha, id_chamado, "hist", categoria_ia, conf,
            "alta", "exec", "True", 1, "data"]


class TestCarregarPredicoesIndexaPorId(unittest.TestCase):
    def test_chave_e_o_id_chamado_e_nao_a_linha(self):
        abas = {"CLASSIF__lstm": [CAB_CLASSIF, linha_classif(2, "1693", "Cat A")]}
        preds = af.carregar_predicoes(_Sh(abas), CONFIG, ["lstm"])
        self.assertIn("1693", preds["lstm"])
        self.assertNotIn(2, preds["lstm"])
        self.assertEqual(preds["lstm"]["1693"]["pred"], "Cat A")

    def test_id_numerico_do_sheets_vira_string(self):
        """UNFORMATTED_VALUE devolve 1693.0; a chave tem de casar com a verdade."""
        abas = {"CLASSIF__lstm": [CAB_CLASSIF, linha_classif(2, 1693.0, "Cat A")]}
        preds = af.carregar_predicoes(_Sh(abas), CONFIG, ["lstm"])
        self.assertIn("1693", preds["lstm"])

    def test_linha_sem_id_e_descartada(self):
        abas = {"CLASSIF__lstm": [CAB_CLASSIF,
                                  linha_classif(2, "", "Cat A"),
                                  linha_classif(3, "1693", "Cat B")]}
        preds = af.carregar_predicoes(_Sh(abas), CONFIG, ["lstm"])
        self.assertEqual(list(preds["lstm"]), ["1693"])

    def test_base_reordenada_nao_troca_a_predicao(self):
        """O nucleo do incidente: mesma linha, chamados diferentes."""
        abas = {"CLASSIF__lstm": [CAB_CLASSIF,
                                  linha_classif(2, "1693", "Cat A"),
                                  linha_classif(3, "1607", "Cat B")]}
        preds = af.carregar_predicoes(_Sh(abas), CONFIG, ["lstm"])
        # A predicao segue o chamado, nao a posicao.
        self.assertEqual(preds["lstm"]["1693"]["pred"], "Cat A")
        self.assertEqual(preds["lstm"]["1607"]["pred"], "Cat B")


class TestCarregarDecisoesPorId(unittest.TestCase):
    """A verdade precisa usar a MESMA chave das predicoes."""

    CAB = ["ID Chamado", "TÍTULO", "CATEGORIA COMPLETA", "D", "E", "F",
           "Classificação IA", "H", "I", "J", "K", "L", "CONFERÊNCIA GLPI",
           "CONFERÊNCIA IA", "Classificação IA - 2", "CONFERÊNCIA IA - 2",
           "CATEGORIA CORRETA MANUAL"]

    def _bloco(self):
        def linha(id_, cat, m):
            return [id_, "t", cat, "", "", "", "", "", "", "", "", "", m,
                    "", "", "", ""]
        return [self.CAB, linha("1693", "Cat A", "Correto"),
                linha("1607", "Cat B", "Correto")]

    def test_chave_id_devolve_id_chamado(self):
        d = dv.carregar_decisoes(_Sh({"P": self._bloco()}), "P",
                                 so_conferencia_glpi=True, chave="id")
        self.assertEqual(sorted(d), ["1607", "1693"])

    def test_chave_padrao_continua_por_linha(self):
        """Os demais consumidores nao podem quebrar com a mudanca."""
        d = dv.carregar_decisoes(_Sh({"P": self._bloco()}), "P",
                                 so_conferencia_glpi=True)
        self.assertEqual(sorted(d), [2, 3])

    def test_verdade_por_id_casa_com_as_predicoes(self):
        """Fim a fim: verdade e predicao usam a mesma chave e o acerto e real."""
        dec = dv.carregar_decisoes(_Sh({"P": self._bloco()}), "P",
                                   so_conferencia_glpi=True, chave="id")
        verdade = dv.verdade_validada(dec)
        abas = {"CLASSIF__lstm": [CAB_CLASSIF,
                                  linha_classif(2, "1693", "Cat A"),
                                  linha_classif(3, "1607", "Cat B")]}
        preds = af.carregar_predicoes(_Sh(abas), CONFIG, ["lstm"])
        acertos = [preds["lstm"][k]["pred"] == verdade[k] for k in verdade]
        self.assertEqual(acertos, [True, True])

    def test_id_numerico_na_aba_principal_normaliza(self):
        cab = self.CAB
        linha = [1693.0, "t", "Cat A", "", "", "", "", "", "", "", "", "",
                 "Correto", "", "", "", ""]
        d = dv.carregar_decisoes(_Sh({"P": [cab, linha]}), "P",
                                 so_conferencia_glpi=True, chave="id")
        self.assertEqual(list(d), ["1693"])


if __name__ == "__main__":
    unittest.main()
