#!/usr/bin/env python3
"""Fase 2 do plano de reducao de celulas (RECLASS_HISTORICO, 2026-09):
exportar_estabilidade_reclassificacao agrega o log append-only por
id_chamado -- angulo que reclass_resumo.json (snapshot mais recente por
modelo) nao cobre: quantas vezes cada chamado foi reclassificado ao todo,
se a categoria oscilou entre a primeira e a ultima entrada, e o resultado
mais recente. O JSON publicado nunca deve conter id_chamado (repo publico),
so agregados."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from exportar_dashboard import exportar_estabilidade_reclassificacao  # noqa: E402

CAB = ["data", "run_id", "modelo", "tipo_rodada", "linha_planilha", "id_chamado",
       "categoria_referencia", "categoria_antes", "confianca_antes", "acerto_antes",
       "categoria_depois", "confianca_depois", "acerto_depois", "mudou",
       "delta_confianca", "resultado", "base_comparacao", "metodo_reclassificacao"]


def linha(data, id_chamado, cat_ref, cat_antes, cat_depois, resultado, modelo="linear_svc"):
    return [data, "run1", modelo, "baixa_confianca", "10", id_chamado, cat_ref, cat_antes,
            "0.5", "False", cat_depois, "0.7", "True", str(cat_antes != cat_depois),
            "0.2", resultado, "historico", "topup"]


class _WorksheetFalsa:
    def __init__(self, valores):
        self.valores = valores

    def get_values(self, *_args, **_kwargs):
        return self.valores


class _SpreadsheetFalsa:
    def __init__(self, abas: dict):
        self.abas = abas

    def worksheet(self, nome):
        return self.abas[nome]  # deixa KeyError propagar como erro real, se pedirem aba errada


CONFIG = {"multimodelo": {"aba_historico_reclassificacao": "RECLASS_HISTORICO"}}


class TestEstabilidadeReclassificacao(unittest.TestCase):
    def test_agrega_por_id_e_conta_reclassificacoes(self):
        valores = [
            CAB,
            # chamado 111: reclassificado 2x, oscila (A->B->A), termina "mantido_correto"
            linha("17/07/2026 07:00", "111", "A", "A", "B", "corrigido"),
            linha("18/07/2026 09:00", "111", "A", "B", "A", "mantido_correto"),
            # chamado 222: reclassificado 1x so, muda de categoria, "corrigido"
            linha("17/07/2026 07:00", "222", "C", "D", "C", "corrigido"),
        ]
        sh = _SpreadsheetFalsa({"RECLASS_HISTORICO": _WorksheetFalsa(valores)})

        saida = exportar_estabilidade_reclassificacao(sh, CONFIG)

        self.assertEqual(saida["total_entradas_historico"], 3)
        self.assertEqual(saida["total_chamados_reclassificados"], 2)
        self.assertEqual(saida["distribuicao_qtd_reclassificacoes"], {"1": 1, "2": 1})
        self.assertEqual(saida["reclassificacoes_por_chamado"]["maximo"], 2)
        # resultado mais recente: 111 -> mantido_correto (18/07), 222 -> corrigido (unica entrada)
        self.assertEqual(saida["resultado_mais_recente"],
                          {"mantido_correto": 1, "corrigido": 1})
        # 111: categoria_antes da 1a entrada = "A"; categoria_depois da ultima = "A" -> nao mudou
        # 222: categoria_antes da 1a (unica) entrada = "D"; categoria_depois = "C" -> mudou
        self.assertEqual(saida["mudou_categoria_desde_a_primeira"], {"sim": 1, "nao": 1})
        self.assertNotIn("111", str(saida))  # nenhum id_chamado vaza pro JSON publico
        self.assertNotIn("222", str(saida))

    def test_usa_ordem_cronologica_mesmo_se_linhas_fora_de_ordem(self):
        # a entrada mais recente (18/07) aparece ANTES da mais antiga (17/07) no arquivo --
        # o agregador deve ordenar por data, nao assumir ordem de leitura.
        valores = [
            CAB,
            linha("18/07/2026 09:00", "333", "A", "B", "A", "mantido_correto"),
            linha("17/07/2026 07:00", "333", "A", "A", "B", "corrigido"),
        ]
        sh = _SpreadsheetFalsa({"RECLASS_HISTORICO": _WorksheetFalsa(valores)})

        saida = exportar_estabilidade_reclassificacao(sh, CONFIG)

        self.assertEqual(saida["resultado_mais_recente"], {"mantido_correto": 1})

    def test_bucket_4_ou_mais(self):
        valores = [CAB] + [
            linha(f"17/07/2026 0{n}:00", "444", "A", "A", "A", "mantido_correto")
            for n in range(1, 5)
        ]
        sh = _SpreadsheetFalsa({"RECLASS_HISTORICO": _WorksheetFalsa(valores)})

        saida = exportar_estabilidade_reclassificacao(sh, CONFIG)

        self.assertEqual(saida["distribuicao_qtd_reclassificacoes"], {"4_ou_mais": 1})

    def test_aba_vazia_devolve_estrutura_zerada(self):
        sh = _SpreadsheetFalsa({"RECLASS_HISTORICO": _WorksheetFalsa([CAB])})

        saida = exportar_estabilidade_reclassificacao(sh, CONFIG)

        self.assertEqual(saida["total_entradas_historico"], 0)
        self.assertEqual(saida["total_chamados_reclassificados"], 0)
        self.assertEqual(saida["distribuicao_qtd_reclassificacoes"], {})

    def test_coluna_id_chamado_ausente_nao_quebra(self):
        cab_sem_id = [c for c in CAB if c != "id_chamado"]
        sh = _SpreadsheetFalsa({"RECLASS_HISTORICO": _WorksheetFalsa([cab_sem_id])})

        saida = exportar_estabilidade_reclassificacao(sh, CONFIG)

        self.assertEqual(saida["total_chamados_reclassificados"], 0)


if __name__ == "__main__":
    unittest.main()
