from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import congelar_alvo_ensemble as cae  # noqa: E402


def registro(id_, hist, ref, fold=1, grupo=None):
    id_sha = hashlib.sha256(id_.encode("utf-8")).hexdigest()
    return {
        "id_sha256": id_sha,
        "grupo_sha256": grupo or hashlib.sha256(f"g-{id_}".encode()).hexdigest(),
        "outer_fold": fold,
        "categoria_historica": hist,
        "referencia_humana": ref,
        "historico_no_espaco_de_classes": hist in {"Cat A", "Cat B"},
        "alvo_inadequacao": int(hist != ref),
    }


def pred(reg, previsto):
    return {
        "outer_fold": reg["outer_fold"],
        "referencia_humana": reg["referencia_humana"],
        "previsto": previsto,
    }


class TestSerializacaoEHashes(unittest.TestCase):
    def test_serializacao_canonica_deterministica(self):
        a = {"b": 1, "a": ["x", "y"]}
        b = {"a": ["x", "y"], "b": 1}
        self.assertEqual(cae.canonical_bytes(a), cae.canonical_bytes(b))
        self.assertEqual(cae.sha256_json(a), cae.sha256_json(b))

    def test_hash_historico_deterministico(self):
        regs = [registro("2", "Cat A", "Cat A"), registro("1", "Cat B", "Cat A")]
        self.assertEqual(cae.hash_historico(regs), cae.hash_historico(list(reversed(regs))))

    def test_hash_alvo_deterministico(self):
        regs = [registro("2", "Cat A", "Cat A"), registro("1", "Cat B", "Cat A")]
        obj = {"metadata": {"schema_version": 1}, "records": sorted(regs, key=lambda r: r["id_sha256"])}
        self.assertEqual(cae.sha256_bytes(cae.canonical_bytes(obj)), cae.sha256_json(obj))

    def test_alteracao_de_h_modifica_hash_historico_e_alvo(self):
        regs_a = [registro("1", "Cat A", "Cat A")]
        regs_b = [registro("1", "Cat B", "Cat A")]
        alvo_a = {"metadata": {}, "records": regs_a}
        alvo_b = {"metadata": {}, "records": regs_b}
        self.assertNotEqual(cae.hash_historico(regs_a), cae.hash_historico(regs_b))
        self.assertNotEqual(cae.sha256_json(alvo_a), cae.sha256_json(alvo_b))

    def test_alteracao_de_r_modifica_hash_alvo(self):
        regs_a = [registro("1", "Cat A", "Cat A")]
        regs_b = [registro("1", "Cat A", "Cat B")]
        alvo_a = {"metadata": {}, "records": regs_a}
        alvo_b = {"metadata": {}, "records": regs_b}
        self.assertNotEqual(cae.sha256_json(alvo_a), cae.sha256_json(alvo_b))


class TestSchemaEAlvo(unittest.TestCase):
    def test_schema_exato_dos_sete_campos(self):
        r = registro("1", "Cat A", "Cat A")
        self.assertEqual(set(r), set(cae.SCHEMA_CAMPOS))

    def test_alvo_igual_int_h_diferente_r(self):
        self.assertEqual(registro("1", "Cat A", "Cat A")["alvo_inadequacao"], 0)
        self.assertEqual(registro("2", "Cat B", "Cat A")["alvo_inadequacao"], 1)

    def test_indicador_igual_h_in_c(self):
        self.assertTrue(registro("1", "Cat A", "Cat A")["historico_no_espaco_de_classes"])
        self.assertFalse(registro("2", "Cat X", "Cat A")["historico_no_espaco_de_classes"])

    def test_classes_ordenadas(self):
        payload, classes_sha = cae.montar_classes([
            registro("1", "Cat A", "Cat B"),
            registro("2", "Cat A", "Cat A"),
        ], esperado=2)
        self.assertEqual([c["label"] for c in payload["classes"]], ["Cat A", "Cat B"])
        esperado = hashlib.sha256(
            json.dumps(["Cat A", "Cat B"], ensure_ascii=False,
                       separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        self.assertEqual(classes_sha, esperado)

    def test_ausencia_de_campos_proibidos(self):
        self.assertTrue(cae.CAMPOS_PROIBIDOS.isdisjoint(cae.SCHEMA_CAMPOS))

    def test_grupos_e_dobras_presentes(self):
        r = registro("1", "Cat A", "Cat A", fold=5)
        self.assertEqual(len(r["grupo_sha256"]), 64)
        self.assertEqual(r["outer_fold"], 5)


class TestBaselineLinearSvc(unittest.TestCase):
    def test_join_completo_linear_svc_e_calculo_k_d_r(self):
        regs = [
            registro("1", "Cat A", "Cat A", 1),
            registro("2", "Cat X", "Cat A", 1),
            registro("3", "Cat A", "Cat B", 2),
        ]
        preds = {
            regs[0]["id_sha256"]: pred(regs[0], "Cat A"),
            regs[1]["id_sha256"]: pred(regs[1], "Cat A"),
            regs[2]["id_sha256"]: pred(regs[2], "Cat B"),
        }
        r = cae.reproduzir_baseline(regs, preds, validar_esperado=False)
        self.assertEqual(r["baseline"]["alertas_naturais"], 2)
        self.assertEqual(r["baseline"]["inadequacoes_na_fila"], 2)
        self.assertEqual(r["baseline"]["correcoes_top1"], 2)
        self.assertEqual(r["por_dobra"]["1"]["K_f"], 1)
        self.assertEqual(r["por_dobra"]["1"]["D_f"], 1)
        self.assertEqual(r["por_dobra"]["1"]["R_f"], 0)
        self.assertTrue(r["todos_h_fora_de_c_na_fila_natural"])

    def test_join_incompleto_bloqueia(self):
        regs = [registro("1", "Cat A", "Cat A")]
        with self.assertRaises(RuntimeError):
            cae.reproduzir_baseline(regs, {}, validar_esperado=False)

    def test_dobra_divergente_bloqueia(self):
        r = registro("1", "Cat A", "Cat A", 1)
        p = pred(r, "Cat A")
        p["outer_fold"] = 2
        with self.assertRaises(RuntimeError):
            cae.reproduzir_baseline([r], {r["id_sha256"]: p}, validar_esperado=False)

    def test_bloqueio_d_f_maior_que_k_f(self):
        r = registro("1", "Cat X", "Cat A", 1)
        with self.assertRaises(RuntimeError):
            cae.reproduzir_baseline(
                [r], {r["id_sha256"]: pred(r, "Cat X")}, validar_esperado=False
            )

    def test_carregar_predicoes_rejeita_duplicacao(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "pred.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["id_sha256", "dobra", "referencia_humana", "modelo", "previsto", "confianca"])
                w.writerow(["a" * 64, 1, "Cat A", "linear_svc", "Cat A", "0.9"])
                w.writerow(["a" * 64, 1, "Cat A", "linear_svc", "Cat A", "0.9"])
            with self.assertRaises(RuntimeError):
                cae.carregar_predicoes_linear_svc(path)


class TestResumoESeguranca(unittest.TestCase):
    def test_frequencias_e_prevalencias(self):
        regs = [
            registro("1", "Cat A", "Cat A", 1),
            registro("2", "Cat X", "Cat A", 1),
        ]
        baseline = {
            "baseline": {
                "alertas_naturais": 1,
                "inadequacoes_na_fila": 1,
                "precisao_fila_natural": 1.0,
                "correcoes_top1": 1,
                "neutros": 0,
                "prejudicados": 0,
            },
            "por_dobra": {"1": {"K_f": 1, "D_f": 1, "R_f": 0,
                                "inadequacoes_dentro_da_fila_natural": 1,
                                "precisao_fila_natural": 1.0}},
            "todos_h_fora_de_c_na_fila_natural": True,
        }
        resumo = cae.montar_resumo(regs, "h", "hh", "ha", "hc", "hp", baseline, 0)
        self.assertEqual(resumo["total_Y1"], 1)
        self.assertEqual(resumo["total_Y0"], 1)
        self.assertEqual(resumo["H_fora_de_C"], 1)
        self.assertEqual(resumo["categorias_historicas_fora_de_C"], ["Cat X"])

    def test_sem_importacao_de_rotina_de_treino(self):
        fonte = (RAIZ / "src" / "congelar_alvo_ensemble.py").read_text(encoding="utf-8")
        proibidos = [
            "import retreinar_modelos_canonicos",
            "import modelos_zoo",
            ".fit(",
            "criar_modelo(",
            "escrever_aba(",
            "append_aba(",
            "escrever_coluna_por_linha(",
        ]
        for termo in proibidos:
            self.assertNotIn(termo, fonte)


if __name__ == "__main__":
    unittest.main()
