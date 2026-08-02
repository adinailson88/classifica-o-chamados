#!/usr/bin/env python3
"""Teste offline de scripts/migracoes/remover_leva_duplicada_classif.py.

Regressao do incidente de 2026-08-02: um run cancelado no meio gravou uma
segunda leva em CLASSIF__extra_trees, que ficou com 28.152 registros para
14.094 chamados. A leva nova, treinada com a conferencia humana dentro do
treino, elevou o acerto validado de 0,7958 para 0,9816.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts" / "migracoes"))
sys.path.insert(0, str(RAIZ / "src"))

import remover_leva_duplicada_classif as rl  # noqa: E402


def linha(id_chamado, categoria, data):
    """Layout de CLASSIF__<modelo>: id no indice 2, data no indice 10."""
    return ["run", 2, id_chamado, "hist", categoria, "0,9", "alta", "exec",
            "True", 1, data]


class TestAgruparPorLeva(unittest.TestCase):
    def test_separa_por_carimbo(self):
        linhas = [linha("1", "A", "01/08/2026 10:00"),
                  linha("2", "B", "01/08/2026 10:00"),
                  linha("1", "C", "02/08/2026 12:16")]
        levas = rl.agrupar_por_leva(linhas)
        self.assertEqual(sorted(levas), ["01/08/2026 10:00", "02/08/2026 12:16"])
        self.assertEqual(levas["01/08/2026 10:00"], [0, 1])
        self.assertEqual(levas["02/08/2026 12:16"], [2])

    def test_linha_curta_cai_em_carimbo_vazio(self):
        levas = rl.agrupar_por_leva([["run", 2, "1"]])
        self.assertEqual(levas, {"": [0]})


class TestEscolherLeva(unittest.TestCase):
    def test_mantem_a_mais_antiga_por_padrao(self):
        levas = {"02/08/2026 12:16": [1], "01/08/2026 10:00": [0]}
        self.assertEqual(rl.escolher_leva(levas), "01/08/2026 10:00")

    def test_ordena_por_data_e_nao_por_texto(self):
        """'02/08' < '11/07' como texto, mas 11/07 e anterior no calendario."""
        levas = {"02/08/2026 10:00": [1], "11/07/2026 10:00": [0]}
        self.assertEqual(rl.escolher_leva(levas), "11/07/2026 10:00")

    def test_desempata_por_hora(self):
        levas = {"01/08/2026 23:00": [1], "01/08/2026 09:00": [0]}
        self.assertEqual(rl.escolher_leva(levas), "01/08/2026 09:00")

    def test_manter_explicito(self):
        levas = {"01/08/2026 10:00": [0], "02/08/2026 12:16": [1]}
        self.assertEqual(rl.escolher_leva(levas, "02/08/2026 12:16"),
                         "02/08/2026 12:16")

    def test_manter_inexistente_aborta(self):
        with self.assertRaises(SystemExit):
            rl.escolher_leva({"01/08/2026 10:00": [0]}, "31/12/2099 00:00")

    def test_carimbo_malformado_nao_lanca(self):
        levas = {"lixo": [1], "01/08/2026 10:00": [0]}
        self.assertEqual(rl.escolher_leva(levas), "01/08/2026 10:00")


class TestResumir(unittest.TestCase):
    def test_conta_o_que_sai_e_o_que_fica(self):
        linhas = [linha("1", "A", "01/08/2026 10:00"),
                  linha("2", "B", "01/08/2026 10:00"),
                  linha("1", "C", "02/08/2026 12:16"),
                  linha("2", "D", "02/08/2026 12:16")]
        levas = rl.agrupar_por_leva(linhas)
        r = rl.resumir(linhas, levas, "01/08/2026 10:00")
        self.assertEqual(r["linhas_totais"], 4)
        self.assertEqual(r["linhas_mantidas"], 2)
        self.assertEqual(r["linhas_removidas"], 2)
        self.assertEqual(r["ids_na_leva_mantida"], 2)
        self.assertEqual(r["ids_que_ficam_sem_predicao"], [])

    def test_id_exclusivo_da_leva_removida_fica_sem_predicao(self):
        """Os 20 chamados novos so existem na leva contaminada. Melhor
        declarar ausencia do que publicar predicao com vazamento."""
        linhas = [linha("1", "A", "01/08/2026 10:00"),
                  linha("1", "B", "02/08/2026 12:16"),
                  linha("99", "C", "02/08/2026 12:16")]
        levas = rl.agrupar_por_leva(linhas)
        r = rl.resumir(linhas, levas, "01/08/2026 10:00")
        self.assertEqual(r["ids_que_ficam_sem_predicao"], ["99"])
        self.assertEqual(r["linhas_mantidas"], 1)

    def test_leva_unica_nao_remove_nada(self):
        linhas = [linha("1", "A", "01/08/2026 10:00")]
        levas = rl.agrupar_por_leva(linhas)
        r = rl.resumir(linhas, levas, "01/08/2026 10:00")
        self.assertEqual(r["linhas_removidas"], 0)


if __name__ == "__main__":
    unittest.main()
