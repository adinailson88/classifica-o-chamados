#!/usr/bin/env python3
"""Testes offline de src/limpar_classif_multimodelo.py.

Cobrem a garantia de seguranca central: a limpeza so afeta abas
CLASSIF__<modelo>/turnos/metricas dos modelos alvo, nunca a aba principal
(que este modulo nem importa por nome), e dry-run nunca escreve nada.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import limpar_classif_multimodelo as lcm  # noqa: E402


class _WorksheetFalsa:
    def __init__(self, valores):
        self._valores = [list(r) for r in valores]
        self.limpou = False
        self.escritas = []

    def get_values(self, *_args, **_kwargs):
        return [list(r) for r in self._valores]

    def row_values(self, n):
        idx = n - 1
        return list(self._valores[idx]) if 0 <= idx < len(self._valores) else []

    def clear(self):
        self.limpou = True

    def update(self, range_name=None, values=None, **_kwargs):  # noqa: ARG002
        self.escritas.append(values)

    def freeze(self, **_kwargs):
        pass

    def format(self, *_args, **_kwargs):
        pass


class _SpreadsheetFalsa:
    def __init__(self, abas: dict[str, _WorksheetFalsa]):
        self._abas = abas
        self.abas_tocadas_para_escrita = set()

    def worksheet(self, nome):
        if nome not in self._abas:
            raise KeyError(nome)
        return self._abas[nome]

    def add_worksheet(self, title, rows, cols):  # usado por aba_por_nome se a aba nao existir
        raise AssertionError(f"nao deveria criar aba nova: {title}")


class TestFiltrarPorModelo(unittest.TestCase):
    def test_preserva_linhas_de_modelos_fora_do_alvo_dry_run(self):
        turnos = [
            ["modelo", "run_id", "turno"],
            ["lstm", "r1", 1],
            ["transformer_ft", "r1", 1],
            ["naive_bayes", "r1", 1],
        ]
        ws = _WorksheetFalsa(turnos)
        sh = _SpreadsheetFalsa({"MULTIMODELO_TURNOS": ws})

        resultado = lcm.filtrar_aba_por_modelo(
            sh, "MULTIMODELO_TURNOS", {"lstm", "naive_bayes"}, aplicar=False)

        self.assertEqual(resultado["linhas_removidas_dry_run"], 2)
        self.assertEqual(resultado["linhas_mantidas_dry_run"], 1)
        self.assertFalse(ws.limpou, "dry-run nao deve chamar clear()")
        self.assertEqual(ws.escritas, [], "dry-run nao deve escrever nada")

    def test_aplica_e_preserva_apenas_modelos_fora_do_alvo(self):
        turnos = [
            ["modelo", "run_id", "turno"],
            ["lstm", "r1", 1],
            ["transformer_ft", "r1", 1],
            ["naive_bayes", "r1", 1],
        ]
        ws = _WorksheetFalsa(turnos)
        sh = _SpreadsheetFalsa({"MULTIMODELO_TURNOS": ws})

        resultado = lcm.filtrar_aba_por_modelo(
            sh, "MULTIMODELO_TURNOS", {"lstm", "naive_bayes"}, aplicar=True)

        self.assertEqual(resultado["linhas_removidas"], 2)
        self.assertEqual(resultado["linhas_mantidas"], 1)
        self.assertTrue(ws.limpou)
        self.assertEqual(len(ws.escritas), 1)
        linhas_escritas = ws.escritas[0]
        # cabecalho + so a linha do transformer_ft (fora do alvo) deve sobrar
        self.assertEqual(linhas_escritas[0], ["modelo", "run_id", "turno"])
        self.assertEqual(len(linhas_escritas), 2)
        self.assertEqual(linhas_escritas[1][0], "transformer_ft")

    def test_aba_ausente_nao_lanca_excecao(self):
        sh = _SpreadsheetFalsa({})
        resultado = lcm.filtrar_aba_por_modelo(sh, "NAO_EXISTE", {"lstm"}, aplicar=True)
        self.assertFalse(resultado["existia"])


class TestLimparClassif(unittest.TestCase):
    def _config(self):
        return {"multimodelo": {"aba_classificacao": "CLASSIF__{modelo}"}}

    def test_dry_run_nao_limpa(self):
        ws = _WorksheetFalsa([["run_id", "linha_planilha"], ["r1", 2], ["r1", 3]])
        sh = _SpreadsheetFalsa({"CLASSIF__lstm": ws})

        resultado = lcm.limpar_classif(sh, self._config(), "lstm", aplicar=False)

        self.assertEqual(resultado["linhas_removidas_dry_run"], 2)
        self.assertFalse(ws.limpou)

    def test_aplicar_limpa_aba_do_modelo(self):
        ws = _WorksheetFalsa([["run_id", "linha_planilha"], ["r1", 2], ["r1", 3]])
        sh = _SpreadsheetFalsa({"CLASSIF__lstm": ws})

        resultado = lcm.limpar_classif(sh, self._config(), "lstm", aplicar=True)

        self.assertEqual(resultado["linhas_removidas"], 2)
        self.assertTrue(ws.limpou)


class TestResolverModelos(unittest.TestCase):
    def test_padrao_nunca_inclui_transformer_ft(self):
        self.assertNotIn("transformer_ft", lcm.resolver_modelos("comparaveis"))
        self.assertNotIn("transformer_ft", lcm.resolver_modelos(""))
        self.assertEqual(set(lcm.resolver_modelos("comparaveis")),
                         set(lcm.MODELOS_COMPARAVEIS_PADRAO))

    def test_lista_explicita_pode_incluir_transformer_ft(self):
        self.assertIn("transformer_ft", lcm.resolver_modelos("lstm,transformer_ft"))


class TestNuncaReferenciaAbaPrincipal(unittest.TestCase):
    def test_codigo_fonte_nao_menciona_aba_principal(self):
        codigo = Path(lcm.__file__).read_text(encoding="utf-8")
        self.assertNotIn("aba_principal", codigo,
                         "o script de limpeza nao deve saber o nome da aba principal")


if __name__ == "__main__":
    unittest.main()
