#!/usr/bin/env python3
"""Teste direcionado da S17 (Fase 2C) em `tabelas_suplementares_canonicas`.

Usa um manifesto sintetico minusculo, nunca o real de 13.970 registros;
verifica que os valores gravados no CSV vem literalmente do manifesto (sem
recalculo) e que a validacao de proveniencia (universo, denominador,
capacidade, run/commit da Fase 2B) bloqueia manifestos divergentes.
"""

from __future__ import annotations

import csv
import json
import sys
import unittest
import unittest.mock
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import tabelas_suplementares_canonicas as tsc  # noqa: E402


def manifesto_valido() -> dict:
    return {
        "total_modelaveis": 13970,
        "total_y1": 593,
        "k_total": 2840,
        "run_id_fase2b": "31556028058",
        "commit_fase2b": "d6a5504cd9c4360b97fd90dd88c13bd430155459",
        "k_f_por_fold": {"1": 564, "2": 560, "3": 616, "4": 507, "5": 593},
        "y1_por_fold": {"1": 124, "2": 95, "3": 135, "4": 113, "5": 126},
        "comparacao_agregada_por_metodo": {
            "linear_svc": {"total_na_fila": 2840, "capturados_y1": 523,
                           "precisao": 0.1842, "recall": 0.8820},
            "votacao_majoritaria": {"total_na_fila": 2840, "capturados_y1": 516,
                                     "precisao": 0.1817, "recall": 0.8702},
            "votacao_suave": {"total_na_fila": 2840, "capturados_y1": 503,
                               "precisao": 0.1771, "recall": 0.8482},
            "stacking": {"total_na_fila": 2840, "capturados_y1": 512,
                         "precisao": 0.1803, "recall": 0.8634},
        },
        "comparacao_por_fold": {
            metodo: {
                str(f): {"K_f": k, "capturados_y1": 10 + f,
                         "precisao": 0.1 + f / 100, "recall_fold": 0.8 + f / 100}
                for f, k in ((1, 564), (2, 560), (3, 616), (4, 507), (5, 593))
            }
            for metodo in ("linear_svc", "votacao_majoritaria",
                            "votacao_suave", "stacking")
        },
    }


class TestS17EnsembleConfirmatorio(unittest.TestCase):
    def _rodar(self, manifesto: dict) -> Path:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifesto_path = tmp_path / "manifesto.json"
            manifesto_path.write_text(json.dumps(manifesto), encoding="utf-8")
            with unittest.mock.patch.object(tsc, "FASE2C_MANIFEST", manifesto_path), \
                 unittest.mock.patch.object(tsc, "FIGURAS", tmp_path):
                caminho = tsc.s17_ensemble_confirmatorio()
                conteudo = caminho.read_text(encoding="utf-8")
            return conteudo

    def test_gera_20_linhas_agregado_mais_cinco_folds(self):
        conteudo = self._rodar(manifesto_valido())
        linhas = list(csv.DictReader(conteudo.splitlines()))
        self.assertEqual(len(linhas), 4 + 4 * 5)

    def test_valores_vem_literalmente_do_manifesto_sem_recalculo(self):
        conteudo = self._rodar(manifesto_valido())
        linhas = list(csv.DictReader(conteudo.splitlines()))
        agregado_linear_svc = next(
            l for l in linhas
            if l["escopo"] == "agregado" and l["metodo"] == "LinearSVC")
        self.assertEqual(agregado_linear_svc["K"], "2840")
        self.assertEqual(agregado_linear_svc["y1_denominador"], "593")
        self.assertEqual(agregado_linear_svc["capturados"], "523")
        self.assertEqual(agregado_linear_svc["diff_capturados_vs_linear_svc"], "0")

        agregado_stacking = next(
            l for l in linhas
            if l["escopo"] == "agregado" and l["metodo"] == "Stacking")
        self.assertEqual(agregado_stacking["capturados"], "512")
        self.assertEqual(agregado_stacking["diff_capturados_vs_linear_svc"], "-11")

    def test_diferenca_por_fold_contra_linear_svc_do_mesmo_fold(self):
        conteudo = self._rodar(manifesto_valido())
        linhas = list(csv.DictReader(conteudo.splitlines()))
        fold3_stacking = next(
            l for l in linhas
            if l["escopo"] == "fold" and l["outer_fold"] == "3"
            and l["metodo"] == "Stacking")
        # fixture sintetica: capturados = 10 + fold, identico entre metodos
        self.assertEqual(fold3_stacking["diff_capturados_vs_linear_svc"], "0")

    def test_bloqueia_universo_modelavel_divergente(self):
        manifesto = manifesto_valido()
        manifesto["total_modelaveis"] = 13972
        with self.assertRaises(SystemExit):
            self._rodar(manifesto)

    def test_bloqueia_denominador_y1_divergente(self):
        manifesto = manifesto_valido()
        manifesto["total_y1"] = 595
        with self.assertRaises(SystemExit):
            self._rodar(manifesto)

    def test_bloqueia_capacidade_k_total_divergente(self):
        manifesto = manifesto_valido()
        manifesto["k_total"] = 2849
        with self.assertRaises(SystemExit):
            self._rodar(manifesto)

    def test_bloqueia_run_ou_commit_fase2b_divergente(self):
        manifesto = manifesto_valido()
        manifesto["run_id_fase2b"] = "00000000000"
        with self.assertRaises(SystemExit):
            self._rodar(manifesto)

    def test_bloqueia_fold_faltante(self):
        manifesto = manifesto_valido()
        del manifesto["k_f_por_fold"]["5"]
        with self.assertRaises(SystemExit):
            self._rodar(manifesto)

    def test_bloqueia_metodo_inesperado(self):
        manifesto = manifesto_valido()
        manifesto["comparacao_agregada_por_metodo"]["metodo_extra"] = (
            manifesto["comparacao_agregada_por_metodo"]["stacking"])
        with self.assertRaises(SystemExit):
            self._rodar(manifesto)


if __name__ == "__main__":
    unittest.main()
