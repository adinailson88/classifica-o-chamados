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


def raw_registro(id_, hist="Cat A", ref="Cat A", titulo="titulo original"):
    return {
        "id": id_,
        "titulo": titulo,
        "descricao_glpi": "",
        "titulo_osm": "",
        "descricao_osm": "",
        "categoria_historica": hist,
        "conferencia_glpi": "Incorreto" if hist != ref else "Correto",
        "categoria_manual": ref if hist != ref else "",
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

    def test_grupo_gravado_segue_preparacao_canonica(self):
        raw = raw_registro("1", titulo="texto atual alterado")
        id_sha = hashlib.sha256(b"1").hexdigest()
        grupo_particao = hashlib.sha256(b"grupo-particao").hexdigest()
        grupo_passo2 = hashlib.sha256(b"grupo-passo2").hexdigest()
        particoes = {id_sha: {
            "grupo_sha256": grupo_particao,
            "outer_fold": 1,
        }}
        registros, diagnostico = cae.montar_registros_alvo(
            [raw], particoes, {id_sha: grupo_passo2}, {id_sha: "Cat A"}
        )
        self.assertEqual(registros[0]["grupo_sha256"], grupo_particao)
        self.assertEqual(diagnostico["particao_x_atual_divergentes"], 1)

    def test_texto_atual_alterado_nao_muda_manifesto_quando_h_e_r_sao_iguais(self):
        id_sha = hashlib.sha256(b"1").hexdigest()
        grupo = hashlib.sha256(b"grupo-congelado").hexdigest()
        particoes = {id_sha: {"grupo_sha256": grupo, "outer_fold": 3}}
        refs = {id_sha: "Cat A"}
        registros_a, diagnostico_a = cae.montar_registros_alvo(
            [raw_registro("1", titulo="texto original")], particoes, {id_sha: grupo}, refs
        )
        registros_b, diagnostico_b = cae.montar_registros_alvo(
            [raw_registro("1", titulo="texto modificado")], particoes, {id_sha: grupo}, refs
        )
        self.assertEqual(registros_a[0]["grupo_sha256"], grupo)
        self.assertEqual(registros_b[0]["grupo_sha256"], grupo)
        self.assertEqual(registros_a[0]["outer_fold"], 3)
        self.assertEqual(registros_b[0]["outer_fold"], 3)
        self.assertEqual(cae.hash_historico(registros_a), cae.hash_historico(registros_b))
        self.assertEqual(cae.sha256_json(registros_a), cae.sha256_json(registros_b))
        self.assertGreaterEqual(
            diagnostico_a["particao_x_atual_divergentes"]
            + diagnostico_b["particao_x_atual_divergentes"],
            1,
        )

    def test_grupos_congelados_reais_preservam_total_canonico(self):
        particoes = cae.carregar_particoes(cae.PARTICOES_PADRAO)
        diagnostico = cae.validar_invariantes_particao(particoes)
        self.assertEqual(diagnostico["total_ids_particao"], cae.TOTAL_ESPERADO)
        self.assertEqual(diagnostico["total_grupos_particao"], cae.GRUPOS_ESPERADOS)
        self.assertEqual(diagnostico["dobras_particao"], [1, 2, 3, 4, 5])
        self.assertEqual(diagnostico["grupos_divididos_entre_dobras"], 0)

    def test_dois_grupos_passo2_x_particao_sao_diagnostico_fechado(self):
        particoes = cae.carregar_particoes(cae.PARTICOES_PADRAO)
        grupos = cae.carregar_grupos(cae.GRUPOS_PADRAO)
        diagnostico = cae.validar_grupos_particoes(particoes, grupos)
        self.assertEqual(diagnostico["passo2_x_particao_divergentes"], 2)
        self.assertEqual(
            set(diagnostico["ids_passo2_x_particao_divergentes"]),
            cae.IDS_PASSO2_X_PARTICAO_ESPERADOS,
        )
        self.assertEqual(diagnostico["grupos_passo2_distintos"], 9735)
        self.assertEqual(diagnostico["grupos_particao_distintos"], 9734)

    def test_id_de_particao_ausente_do_passo2_bloqueia(self):
        particoes = cae.carregar_particoes(cae.PARTICOES_PADRAO)
        grupos = cae.carregar_grupos(cae.GRUPOS_PADRAO)
        grupos.pop(next(iter(particoes)))
        with self.assertRaisesRegex(RuntimeError, "Mapa de grupos diverge"):
            cae.validar_grupos_particoes(particoes, grupos)

    def test_referencia_humana_atual_divergente_da_oof_bloqueia(self):
        raw = raw_registro("1", hist="Cat A", ref="Cat B")
        id_sha = hashlib.sha256(b"1").hexdigest()
        grupo = cae._hash_grupo_atual(raw)
        particoes = {id_sha: {"grupo_sha256": grupo, "outer_fold": 1}}
        with self.assertRaisesRegex(RuntimeError, "Referencias humanas divergentes"):
            cae.montar_registros_alvo(
                [raw], particoes, {id_sha: grupo}, {id_sha: "Cat A"}
            )

    def test_divergencia_entre_grupo_e_particao_bloqueia(self):
        id_sha = "a" * 64
        with self.assertRaisesRegex(RuntimeError, "Mapa de grupos diverge"):
            cae.validar_grupos_particoes(
                {id_sha: {"grupo_sha256": "b" * 64, "outer_fold": 1}},
                {id_sha: "c" * 64},
            )

    def test_hash_corpus_vem_da_rodada_canonica(self):
        rodada = json.loads(cae.RODADA_PADRAO.read_text(encoding="utf-8"))
        self.assertEqual(rodada["hash_corpus"], cae.HASH_CORPUS_ESPERADO)


class TestDeterminismo(unittest.TestCase):
    def test_verificar_determinismo_aceita_execucoes_identicas(self):
        a = {
            "classes_bytes": b"x",
            "alvo_bytes": b"y",
            "hashes": {"hash_alvo_ensemble": "h"},
            "contagens": {"total_Y1": 1},
        }
        b = dict(a)
        cae.verificar_determinismo(a, b)

    def test_verificar_determinismo_bloqueia_bytes_divergentes(self):
        a = {
            "classes_bytes": b"x",
            "alvo_bytes": b"y",
            "hashes": {"hash_alvo_ensemble": "h"},
            "contagens": {"total_Y1": 1},
        }
        b = dict(a, alvo_bytes=b"y-alterado")
        with self.assertRaisesRegex(RuntimeError, "Determinismo falhou em alvo_bytes"):
            cae.verificar_determinismo(a, b)

    def test_verificar_determinismo_bloqueia_hashes_divergentes(self):
        a = {
            "classes_bytes": b"x",
            "alvo_bytes": b"y",
            "hashes": {"hash_alvo_ensemble": "h"},
            "contagens": {"total_Y1": 1},
        }
        b = dict(a, hashes={"hash_alvo_ensemble": "outro"})
        with self.assertRaisesRegex(RuntimeError, "Determinismo falhou em hashes"):
            cae.verificar_determinismo(a, b)

    def test_verificar_determinismo_bloqueia_contagens_divergentes(self):
        a = {
            "classes_bytes": b"x",
            "alvo_bytes": b"y",
            "hashes": {"hash_alvo_ensemble": "h"},
            "contagens": {"total_Y1": 1},
        }
        b = dict(a, contagens={"total_Y1": 2})
        with self.assertRaisesRegex(RuntimeError, "Determinismo falhou em contagens"):
            cae.verificar_determinismo(a, b)


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
        diagnostico = {
            "total_ids_particao": 2,
            "total_grupos_particao": 2,
            "dobras_particao": [1],
            "grupos_divididos_entre_dobras": 0,
            "passo2_x_particao_divergentes": 0,
            "ids_passo2_x_particao_divergentes": [],
            "grupos_passo2_distintos": 2,
            "grupos_particao_distintos": 2,
            "particao_x_atual_divergentes": 0,
            "passo2_x_atual_divergentes": 0,
            "grupos_atuais_distintos": 2,
        }
        resumo = cae.montar_resumo(
            regs, "h", "hh", "ha", "hc", "hp", baseline, diagnostico
        )
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
