#!/usr/bin/env python3
"""Teste offline de regressao: _append_resiliente nao duplica linhas quando um
erro transitorio ocorre DEPOIS de o Sheets ja ter commitado a escrita no
servidor (achado real de 2026-07-18: append de 4.737 linhas em
RECLASS__random_forest sofreu APIError transitorio, o retry reenviou o mesmo
lote e duplicou exatamente 4.737 linhas, confirmado por auditoria em
2026-07-23). Sem a checagem de linhas ja commitadas antes do retry, qualquer
erro transitorio pos-commit duplica o lote inteiro."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import reclassificacao_multimodelo as rm  # noqa: E402


class _WorksheetFalsa:
    def __init__(self, linhas_iniciais=1):
        self.n_linhas = linhas_iniciais

    def get_values(self, *_args, **_kwargs):
        return [["x"]] * self.n_linhas


class _SpreadsheetFalsa:
    def __init__(self, linhas_iniciais=1):
        self.ws = _WorksheetFalsa(linhas_iniciais)

    def worksheet(self, _nome):
        return self.ws


class TestAppendResiliente(unittest.TestCase):
    def test_nao_reenvia_quando_escrita_ja_commitada_no_servidor(self):
        """Simula: append_aba lanca erro transitorio, mas a aba ja cresceu (o
        servidor commitou antes do cliente ver o erro). O retry deve ser
        cancelado, nao reenviado."""
        sh = _SpreadsheetFalsa(linhas_iniciais=1)  # so cabecalho
        lote = [["run", "modelo", i, f"id{i}"] for i in range(10)]

        chamadas = {"n": 0}

        def append_aba_fake(_sh, _nome, _cab, _linhas, colunas_percentuais=None):
            chamadas["n"] += 1
            if chamadas["n"] == 1:
                # Simula: a escrita foi commitada no servidor...
                sh.ws.n_linhas += len(lote)
                # ...mas o cliente recebe um erro de rede antes de saber disso.
                raise ConnectionError("Connection aborted.")
            raise AssertionError("nao deveria reenviar: escrita ja tinha sido commitada")

        with mock.patch.object(rm.pl, "append_aba", side_effect=append_aba_fake):
            resultado = rm._append_resiliente(sh, "RECLASS__random_forest",
                                               ["cab"], lote, tentativas=5, espera=0)

        self.assertEqual(resultado, len(lote))
        self.assertEqual(chamadas["n"], 1)

    def test_reenvia_quando_escrita_realmente_falhou(self):
        """Erro transitorio genuino (aba nao cresceu): deve reenviar normalmente
        ate ter sucesso, sem falso-negativo bloqueando o retry legitimo."""
        sh = _SpreadsheetFalsa(linhas_iniciais=1)
        lote = [["run", "modelo", i, f"id{i}"] for i in range(10)]

        chamadas = {"n": 0}

        def append_aba_fake(_sh, _nome, _cab, _linhas, colunas_percentuais=None):
            chamadas["n"] += 1
            if chamadas["n"] < 3:
                raise ConnectionError("Connection aborted.")
            sh.ws.n_linhas += len(lote)
            return len(lote)

        with mock.patch.object(rm.pl, "append_aba", side_effect=append_aba_fake):
            resultado = rm._append_resiliente(sh, "RECLASS__random_forest",
                                               ["cab"], lote, tentativas=5, espera=0)

        self.assertEqual(resultado, len(lote))
        self.assertEqual(chamadas["n"], 3)
        self.assertEqual(sh.ws.n_linhas, 1 + len(lote))


if __name__ == "__main__":
    unittest.main()
