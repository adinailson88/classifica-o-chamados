#!/usr/bin/env python3
"""Teste de regressao: quando torch/transformers estao indisponiveis (como no
cron automatico multimodelo_classificacao.yml, que nunca os instala),
_ModeloTransformerFT.fit() cai para LSTM/RF -- e isso precisa ficar EXPLICITO
e bloquear a publicacao sob o nome 'transformer_ft'.

Achado real de 2026-07-25: confirmado em logs de producao (run 29550863840,
17/07/2026) que a materializacao INTEIRA de CLASSIF__transformer_ft
(13.954/13.965 linhas, metodo kfold_5) foi feita com essa dependencia
ausente -- ou seja, o que esta publicado como 'transformer_ft' e LSTM
disfarcado, sem nenhum aviso persistido. Este teste roda no MESMO ambiente
sem torch/transformers (nao mocka a ausencia), entao valida o comportamento
real, nao um cenario hipotetico."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import modelos_zoo as zoo  # noqa: E402
import classificacao_multimodelo as cm  # noqa: E402
import reclassificacao_multimodelo as rm  # noqa: E402

try:
    import torch  # noqa: F401
    TORCH_DISPONIVEL = True
except Exception:  # noqa: BLE001
    TORCH_DISPONIVEL = False


class _WorksheetSemEscrita:
    """Aba falsa que RECUSA qualquer escrita — usada para provar que o fluxo
    de fallback nao grava nada quando deveria recusar publicar."""

    def __init__(self, valores):
        self._valores = [list(r) for r in valores]

    def get_values(self, *_args, **_kwargs):
        return [list(r) for r in self._valores]

    def append_rows(self, *_args, **_kwargs):
        raise AssertionError("nao deveria escrever: fallback deveria ter sido recusado")

    def update(self, *_args, **_kwargs):
        raise AssertionError("nao deveria escrever: fallback deveria ter sido recusado")

    def batch_update(self, *_args, **_kwargs):
        raise AssertionError("nao deveria escrever: fallback deveria ter sido recusado")

    def acell(self, *_args, **_kwargs):
        class _Cel:
            value = None
        return _Cel()


class _SpreadsheetSemEscrita:
    def __init__(self, abas: dict):
        self._abas = abas

    def worksheet(self, nome):
        return self._abas[nome]


@unittest.skipIf(TORCH_DISPONIVEL, "torch/transformers instalados neste ambiente — "
                                   "teste valida o caminho de fallback real, pula se nao aplicavel")
class TestFallbackExplicito(unittest.TestCase):
    def test_modelo_transformer_ft_marca_usou_fallback(self):
        m = zoo.criar_modelo("transformer_ft")
        textos = ["vazamento agua torneira", "disjuntor desarmando luz"] * 5
        cats = ["HID", "ELE"] * 5
        m.fit(textos, cats)
        self.assertTrue(m.usou_fallback)
        self.assertEqual(m.train_info.get("status"), "fallback_lstm")

    def test_prever_out_of_fold_reporta_fallback_para_transformer_ft(self):
        lote = [{"texto": f"vazamento torneira {i}", "categoria_original": "HID"}
                for i in range(5)]
        base_t = [f"vazamento torneira pia {i}" for i in range(20)] + \
                 [f"disjuntor desarmando {i}" for i in range(20)]
        base_c = ["HID"] * 20 + ["ELE"] * 20
        preds, scores, metodo, usou_fallback = cm.prever_out_of_fold(
            "transformer_ft", lote, base_t, base_c, k_folds=5, min_base=10,
            fracao_topup=0.9)
        self.assertTrue(usou_fallback)
        self.assertEqual(len(preds), len(lote))

    def test_prever_out_of_fold_nao_marca_fallback_para_outro_modelo(self):
        lote = [{"texto": f"vazamento torneira {i}", "categoria_original": "HID"}
                for i in range(5)]
        base_t = [f"vazamento torneira pia {i}" for i in range(20)] + \
                 [f"disjuntor desarmando {i}" for i in range(20)]
        base_c = ["HID"] * 20 + ["ELE"] * 20
        _, _, _, usou_fallback = cm.prever_out_of_fold(
            "naive_bayes", lote, base_t, base_c, k_folds=5, min_base=10,
            fracao_topup=0.9)
        self.assertFalse(usou_fallback)

    def test_classificar_modelo_recusa_publicar_transformer_ft_em_fallback(self):
        cab = ["ID Chamado", "TÍTULO", "CATEGORIA COMPLETA", "DESCRIÇÃO GLPI",
               "TÍTULO O.S.M.", "DESCRIÇÃO O.S.M."]
        linhas = [cab] + [
            [i, f"titulo {i}", "HID" if i % 2 == 0 else "ELE",
             f"vazamento torneira {i}" if i % 2 == 0 else f"disjuntor {i}", "", ""]
            for i in range(2, 42)
        ]
        config = {
            "multimodelo": {
                "aba_classificacao": "CLASSIF__{modelo}",
                "aba_turnos": "MULTIMODELO_TURNOS",
                "tamanho_turno": 15,
                "k_folds": 5,
                "min_base_treino": 5,
                "fracao_topup": 0.9,
            },
        }
        ws_classif = _WorksheetSemEscrita([["run_id", "linha_planilha"]])  # 0 ja feitas
        ws_turnos = _WorksheetSemEscrita([["modelo"]])
        sh = _SpreadsheetSemEscrita({
            "CLASSIF__transformer_ft": ws_classif,
            "MULTIMODELO_TURNOS": ws_turnos,
        })
        elegiveis = [{"linha": i, "id": str(i), "titulo": f"t{i}",
                     "categoria_original": "HID" if i % 2 == 0 else "ELE",
                     "texto": f"vazamento torneira {i}" if i % 2 == 0 else f"disjuntor {i}"}
                    for i in range(2, 42)]

        class _Args:
            aplicar = True

        resultado = cm.classificar_modelo(sh, config, "transformer_ft", elegiveis, 0,
                                          ([], []), _Args())
        self.assertTrue(resultado.get("pulado_fallback"))
        self.assertEqual(resultado["processados"], 0)
        # Nenhuma excecao de escrita foi levantada => nada foi gravado (as abas
        # falsas levantam AssertionError em qualquer append_rows/update/batch_update).


if __name__ == "__main__":
    unittest.main()
