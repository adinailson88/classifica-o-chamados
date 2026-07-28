#!/usr/bin/env python3
"""Testes offline da avaliação held-out comum dos oito modelos."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import decisao_validada as dv  # noqa: E402
from avaliacao_bertimbau_holdout import (  # noqa: E402
    agrupar_execucoes,
    construir_avaliacao,
    selecionar_execucao_exata,
    selecionar_lote_bertimbau,
)


MODELOS = [
    "naive_bayes",
    "regressao_logistica",
    "linear_svc",
    "sgd",
    "extra_trees",
    "random_forest",
    "lstm",
    "transformer_ft",
]


def registro(modelo, linha, prevista, original="A", execucao="28/07/2026 02:00"):
    return {
        "modelo": modelo,
        "linha": linha,
        "original": original,
        "prevista": prevista,
        "score": 0.8,
        "execucao": execucao,
    }


class TestSelecaoExecucoes(unittest.TestCase):
    def test_seleciona_maior_lote_bertimbau(self):
        regs = [
            registro("transformer_ft", 2, "A", execucao="28/07/2026 01:00"),
            registro("transformer_ft", 3, "A", execucao="28/07/2026 01:00"),
            registro("transformer_ft", 2, "A", execucao="28/07/2026 02:00"),
            registro("transformer_ft", 3, "A", execucao="28/07/2026 02:00"),
            registro("transformer_ft", 4, "A", execucao="28/07/2026 02:00"),
        ]
        execucao, lote = selecionar_lote_bertimbau(agrupar_execucoes(regs), min_lote=2)
        self.assertEqual(execucao, "28/07/2026 02:00")
        self.assertEqual(set(lote), {2, 3, 4})

    def test_execucao_precisa_ter_mesmas_linhas(self):
        grupos = agrupar_execucoes(
            [
                registro("linear_svc", 2, "A", execucao="28/07/2026 01:00"),
                registro("linear_svc", 3, "A", execucao="28/07/2026 01:00"),
                registro("linear_svc", 2, "A", execucao="28/07/2026 02:00"),
            ]
        )
        selecionada = selecionar_execucao_exata(grupos["linear_svc"], {2, 3})
        self.assertIsNotNone(selecionada)
        self.assertEqual(selecionada[0], "28/07/2026 01:00")
        self.assertIsNone(selecionar_execucao_exata(grupos["linear_svc"], {2, 3, 4}))


class TestAvaliacaoComum(unittest.TestCase):
    def test_constroi_ranking_com_oito_modelos(self):
        registros = []
        verdade = {2: "A", 3: "B", 4: "A", 5: "B"}
        for posicao, modelo in enumerate(MODELOS):
            for linha in sorted(verdade):
                prevista = verdade[linha]
                # Cada modelo adicional erra progressivamente a última linha.
                if posicao > 0 and linha == 5:
                    prevista = "A"
                registros.append(registro(modelo, linha, prevista, original=verdade[linha]))

        decisoes = {
            linha: {
                "status": dv.STATUS_DECIDIDO,
                "decidida": categoria,
                "conflito": False,
                "fonte_decisao": "manual",
            }
            for linha, categoria in verdade.items()
        }
        resultado = construir_avaliacao(
            registros,
            decisoes,
            MODELOS,
            min_lote=4,
            min_validados=4,
            n_boot=30,
        )
        self.assertEqual(resultado["status"], "ok")
        self.assertEqual(resultado["protocolo"]["n_lote"], 4)
        self.assertEqual(len(resultado["modelos"]), 8)
        self.assertEqual(resultado["modelos"][0]["modelo"], "naive_bayes")
        self.assertEqual(resultado["bertimbau"]["acerto_validado"], 0.75)
        self.assertTrue(resultado["protocolo"]["separado_da_avaliacao_principal"])

    def test_recusa_modelo_sem_lote_exato(self):
        registros = []
        for modelo in MODELOS:
            linhas = [2, 3, 4] if modelo != "lstm" else [2, 3]
            for linha in linhas:
                registros.append(registro(modelo, linha, "A"))
        decisoes = {
            linha: {
                "status": dv.STATUS_DECIDIDO,
                "decidida": "A",
                "conflito": False,
                "fonte_decisao": "manual",
            }
            for linha in (2, 3, 4)
        }
        with self.assertRaisesRegex(RuntimeError, "lstm"):
            construir_avaliacao(
                registros,
                decisoes,
                MODELOS,
                min_lote=3,
                min_validados=3,
                n_boot=10,
            )


if __name__ == "__main__":
    unittest.main()
