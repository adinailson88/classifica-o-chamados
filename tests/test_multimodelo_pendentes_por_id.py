#!/usr/bin/env python3
"""Regressao do incidente de 2026-08-02: pendentes eram detectados por LINHA.

`linhas_ja_classificadas` lia a coluna B (linha_planilha) de CLASSIF__<modelo>.
Quando a base caiu de 14.094 para 14.058 chamados, todo chamado passou a ocupar
outra linha, apareceu como pendente e foi reclassificado e ACRESCENTADO a aba,
que terminou com 28.152 registros para 14.058 chamados.

Como a leitura da aba monta {id_chamado: categoria}, a segunda predicao venceu,
e ela havia sido treinada com a conferencia humana no treino, elevando o acerto
validado do extra_trees de 0,7958 para 0,9816.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import classificacao_multimodelo as cm  # noqa: E402

CAB = ["run_id", "linha_planilha", "id_chamado", "categoria_original",
       "categoria_ia", "confianca"]


class _Ws:
    def __init__(self, coluna_c):
        self._c = coluna_c

    def get_values(self, *_a, **_k):
        return self._c


class _Sh:
    def __init__(self, coluna_c, existe=True):
        self._c = coluna_c
        self._existe = existe

    def worksheet(self, _nome):
        if not self._existe:
            raise KeyError("aba inexistente")
        return _Ws(self._c)


class TestIdsJaClassificados(unittest.TestCase):
    def test_le_ids_da_coluna_c(self):
        sh = _Sh([["id_chamado"], ["1693"], ["1607"]])
        self.assertEqual(cm.ids_ja_classificados(sh, "X"), {"1693", "1607"})

    def test_normaliza_numero_do_sheets(self):
        sh = _Sh([["id_chamado"], [1693.0], [2025014328.0]])
        self.assertEqual(cm.ids_ja_classificados(sh, "X"),
                         {"1693", "2025014328"})

    def test_ignora_vazios(self):
        sh = _Sh([["id_chamado"], [""], ["1693"], [None], []])
        self.assertEqual(cm.ids_ja_classificados(sh, "X"), {"1693"})

    def test_aba_inexistente_devolve_vazio(self):
        self.assertEqual(cm.ids_ja_classificados(_Sh([], existe=False), "X"), set())

    def test_id_nao_numerico_e_preservado(self):
        sh = _Sh([["id_chamado"], ["ABC-1"]])
        self.assertEqual(cm.ids_ja_classificados(sh, "X"), {"ABC-1"})


class TestNormalizarId(unittest.TestCase):
    def test_mesma_regra_das_outras_ferramentas(self):
        self.assertEqual(cm.normalizar_id(1693.0), "1693")
        self.assertEqual(cm.normalizar_id(" 1693 "), "1693")
        self.assertEqual(cm.normalizar_id(""), "")


class TestPendentesNaoDependemDaLinha(unittest.TestCase):
    """O nucleo do incidente, em forma de teste."""

    def test_chamado_que_mudou_de_linha_nao_vira_pendente(self):
        elegiveis = [
            {"linha": 2, "id": "1693"},
            {"linha": 3, "id": "1607"},
        ]
        feitos = cm.ids_ja_classificados(_Sh([["id_chamado"], ["1693"], ["1607"]]), "X")
        # A base encolheu e os dois desceram de posicao; os ids nao mudaram.
        elegiveis_apos_mudanca = [
            {"linha": 900, "id": "1693"},
            {"linha": 901, "id": "1607"},
        ]
        pendentes = [e for e in elegiveis_apos_mudanca
                     if cm.normalizar_id(e["id"]) not in feitos]
        self.assertEqual(pendentes, [], "chamado ja classificado virou pendente")
        # Sanidade: com a regra antiga (por linha) os dois seriam pendentes.
        pendentes_por_linha = [e for e in elegiveis_apos_mudanca
                               if e["linha"] not in {2, 3}]
        self.assertEqual(len(pendentes_por_linha), 2)
        del elegiveis

    def test_chamado_novo_continua_pendente(self):
        feitos = cm.ids_ja_classificados(_Sh([["id_chamado"], ["1693"]]), "X")
        elegiveis = [{"linha": 2, "id": "1693"}, {"linha": 3, "id": "2026070492"}]
        pendentes = [e for e in elegiveis
                     if cm.normalizar_id(e["id"]) not in feitos]
        self.assertEqual([e["id"] for e in pendentes], ["2026070492"])

    def test_id_numerico_na_aba_principal_casa_com_a_aba_classif(self):
        """A aba principal devolve 1693.0 e a CLASSIF__ tambem; as duas
        precisam produzir a mesma chave."""
        feitos = cm.ids_ja_classificados(_Sh([["id_chamado"], [1693.0]]), "X")
        elegiveis = [{"linha": 2, "id": 1693.0}]
        pendentes = [e for e in elegiveis
                     if cm.normalizar_id(e["id"]) not in feitos]
        self.assertEqual(pendentes, [])


if __name__ == "__main__":
    unittest.main()
