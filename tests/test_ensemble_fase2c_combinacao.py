#!/usr/bin/env python3
"""Testes da Fase 2C: combinacao dos sete modelos-base (votacao, stacking).

Usa fixtures sinteticas pequenas — nunca dados reais de 13.970 registros,
nunca fits de modelo real (o meta-modelo de stacking usa um fake injetado,
mesmo padrao de `criar_modelo` na Fase 2B). Os hashes REAIS da Execucao
Cientifica 1 (`HASHES_EXECUCAO_1_ESPERADOS`, `ensemble_fase2b_crossfit.
HASHES_ESPERADOS`) sao exercidos como constantes opacas — os testes de
`validar_proveniencia` os comparam contra conteudo de arquivo controlado
pelo teste, nunca contra dados sinteticos que precisariam reproduzi-los por
forca bruta (criptograficamente inviavel e nao e o que se quer testar).

`montar_contexto` e testado com `verificar_hashes_predicoes=False` (a
checagem criptografica das previsoes ja tem teste isolado em
`TestVerificarHashesRecomputados`) e, num teste dedicado, com o padrao
`verificar_hashes_predicoes=True` para confirmar que dados sinteticos (que
nao reproduzem os hashes reais) sao corretamente bloqueados.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402

import ensemble_fase2b_crossfit as efc  # noqa: E402
import ensemble_fase2c_combinacao as f2c  # noqa: E402

CLASSES = ["classe_a", "classe_b", "classe_c", "classe_d"]
CLASSES_41 = [f"classe_{i:02d}" for i in range(41)]
MODELOS = list(f2c.MODELOS)


def _vetor(classes: list[str], forte_em: str, intensidade: float = 0.7) -> np.ndarray:
    """Vetor de escore com massa concentrada em `forte_em`, resto uniforme."""
    n = len(classes)
    resto = (1 - intensidade) / (n - 1)
    vetor = np.full(n, resto, dtype=np.float64)
    vetor[classes.index(forte_em)] = intensidade
    return vetor


def _scores_todos_modelos(classes: list[str], forte_em: str) -> dict[str, np.ndarray]:
    return {modelo: _vetor(classes, forte_em) for modelo in MODELOS}


# --------------------------------------------------------------------------
# Escores de prioridade
# --------------------------------------------------------------------------

class TestEscoreLinearSVC(unittest.TestCase):
    def test_formula_s_ls(self):
        vetor = _vetor(CLASSES, "classe_c", intensidade=0.6)
        s, c_alt = f2c.escore_linear_svc({"linear_svc": vetor}, CLASSES, "classe_a")
        p_h = vetor[CLASSES.index("classe_a")]
        p_alt_esperado = vetor[CLASSES.index("classe_c")]
        self.assertAlmostEqual(s, p_alt_esperado - p_h)
        self.assertEqual(c_alt, "classe_c")

    def test_negativo_quando_h_e_a_mais_provavel(self):
        vetor = _vetor(CLASSES, "classe_a", intensidade=0.9)
        s, _ = f2c.escore_linear_svc({"linear_svc": vetor}, CLASSES, "classe_a")
        self.assertLess(s, 0)


class TestVotacaoMajoritaria(unittest.TestCase):
    def test_votos_top1_conta_certo(self):
        top1 = {
            "naive_bayes": "classe_a", "regressao_logistica": "classe_a",
            "linear_svc": "classe_b", "sgd": "classe_b",
            "extra_trees": "classe_b", "random_forest": "classe_c",
            "lstm": "classe_c",
        }
        v_h, votos_alt = f2c.votos_top1(top1, "classe_a")
        self.assertEqual(v_h, 2)
        self.assertEqual(votos_alt, {"classe_b": 3, "classe_c": 2})

    def test_c_alt_desempate_por_ordem_global(self):
        # classe_a e classe_c empatam em 2 votos; classe_a vem primeiro na
        # ordem global (CLASSES) e deve vencer o desempate.
        votos_alt = {"classe_c": 2, "classe_a": 2}
        self.assertEqual(f2c.escolher_c_alt_majoritario(votos_alt, CLASSES), "classe_a")

    def test_sem_votos_alternativos_devolve_none(self):
        self.assertIsNone(f2c.escolher_c_alt_majoritario({}, CLASSES))

    def test_formula_s_maj(self):
        top1 = {m: "classe_b" for m in MODELOS}
        top1[MODELOS[0]] = "classe_a"  # 1 voto em H, 6 em classe_b
        s_maj, c_alt = f2c.escore_votacao_majoritaria(top1, "classe_a", CLASSES)
        self.assertEqual(c_alt, "classe_b")
        self.assertAlmostEqual(s_maj, (6 - 1) / len(MODELOS))

    def test_unanimidade_com_historico(self):
        top1 = {m: "classe_a" for m in MODELOS}
        s_maj, c_alt = f2c.escore_votacao_majoritaria(top1, "classe_a", CLASSES)
        self.assertIsNone(c_alt)
        self.assertAlmostEqual(s_maj, -1.0)


class TestVotacaoSuave(unittest.TestCase):
    def _registros_desempenho_conhecido(self):
        """3 registros; 'linear_svc' acerta R nos 3, os outros 6 nunca."""
        registros = {}
        for i, r in enumerate(["classe_a", "classe_b", "classe_c"]):
            top1_outer = {m: "classe_d" for m in MODELOS}
            top1_outer["linear_svc"] = r
            registros[f"id{i}"] = {"R": r, "top1_outer": top1_outer}
        return registros

    def test_pesos_somam_um(self):
        pesos = f2c.pesos_votacao_suave(self._registros_desempenho_conhecido())
        self.assertAlmostEqual(sum(pesos.values()), 1.0)

    def test_pesos_proporcionais_a_acuracia(self):
        pesos = f2c.pesos_votacao_suave(self._registros_desempenho_conhecido())
        self.assertAlmostEqual(pesos["linear_svc"], 1.0)
        for modelo in MODELOS:
            if modelo != "linear_svc":
                self.assertAlmostEqual(pesos[modelo], 0.0)

    def test_bloqueia_quando_nenhum_modelo_acerta(self):
        registros = {
            "id0": {"R": "classe_a", "top1_outer": {m: "classe_d" for m in MODELOS}},
        }
        with self.assertRaises(f2c.Fase2CBloqueado):
            f2c.pesos_votacao_suave(registros)

    def test_formula_s_soft(self):
        scores = _scores_todos_modelos(CLASSES, "classe_a")
        scores["linear_svc"] = _vetor(CLASSES, "classe_c", intensidade=0.9)
        pesos = {m: (1.0 if m == "linear_svc" else 0.0) for m in MODELOS}
        s_soft, c_alt = f2c.escore_votacao_suave(scores, pesos, CLASSES, "classe_a")
        # peso 100% em linear_svc: o combinado e exatamente o vetor dele.
        vetor = scores["linear_svc"]
        esperado = vetor[CLASSES.index("classe_c")] - vetor[CLASSES.index("classe_a")]
        self.assertAlmostEqual(s_soft, esperado)
        self.assertEqual(c_alt, "classe_c")


# --------------------------------------------------------------------------
# Stacking
# --------------------------------------------------------------------------

class _MetaModeloFake:
    """Fake deterministico: memoriza X/y do fit; prediz 1.0 se a soma das
    margens (posicoes impares de X) for positiva, senao 0.0. Sem sklearn
    real, sem custo de treino."""

    def __init__(self):
        self.X_fit = None
        self.y_fit = None
        self.classes_ = np.array([0, 1])

    def fit(self, X, y):
        self.X_fit = np.array(X, copy=True)
        self.y_fit = np.array(y, copy=True)
        return self

    def predict_proba(self, X):
        margem = X[:, 1::2].sum(axis=1)
        p1 = (margem > 0).astype(np.float64)
        return np.column_stack([1 - p1, p1])


class TestStacking(unittest.TestCase):
    def test_montar_features_stacking_dimensao(self):
        scores = _scores_todos_modelos(CLASSES, "classe_b")
        feats = f2c.montar_features_stacking(scores, CLASSES, "classe_a")
        self.assertEqual(feats.shape, (2 * len(MODELOS),))

    def _contexto_sintetico_para_stacking(self):
        """5 outer folds; cada fold `f` tem um pool interno de 8 ids
        (2 Y=0, 2 Y=1, repetidos por conveniencia) que NUNCA inclui os ids
        'nativos' daquele fold — mesma invariante leakage-free da Fase 2B."""
        classes = CLASSES
        registros: dict[str, dict] = {}
        inner_por_fold: dict[int, list] = {f: [] for f in f2c.FOLDS}

        nativos_por_fold: dict[int, list[str]] = {}
        contador = 0
        for fold in f2c.FOLDS:
            ids_fold = []
            for _ in range(2):
                id_sha = f"nativo_{contador}"
                contador += 1
                ids_fold.append(id_sha)
                registros[id_sha] = {
                    "id_sha256": id_sha, "H": "classe_a", "R": "classe_a",
                    "Y": 0, "grupo_sha256": f"g_{id_sha}", "outer_fold": fold,
                    "scores_outer": _scores_todos_modelos(classes, "classe_a"),
                    "top1_outer": {m: "classe_a" for m in MODELOS},
                }
            nativos_por_fold[fold] = ids_fold

        for fold in f2c.FOLDS:
            for outro_fold in f2c.FOLDS:
                if outro_fold == fold:
                    continue
                for id_sha in nativos_por_fold[outro_fold]:
                    reg = registros[id_sha]
                    for modelo in MODELOS:
                        inner_por_fold[fold].append([
                            fold, 0, id_sha, reg["grupo_sha256"], modelo,
                            reg["scores_outer"][modelo].tolist(), reg["top1_outer"][modelo],
                        ])
        # Metade dos nativos vira Y=1 para garantir as duas classes no
        # meta-treino de cada fold (o pool de cada fold cobre todos os
        # outros folds, logo ambas as classes aparecem).
        for id_sha in list(registros)[1::2]:
            registros[id_sha]["Y"] = 1
            registros[id_sha]["R"] = "classe_b"

        return {
            "classes": classes, "registros": registros,
            "inner_por_outer_fold": inner_por_fold,
        }

    def test_treinar_stacking_um_modelo_por_fold(self):
        contexto = self._contexto_sintetico_para_stacking()
        modelos_por_fold = f2c.treinar_stacking_por_fold(contexto, criar_meta_modelo=_MetaModeloFake)
        self.assertEqual(sorted(modelos_por_fold), sorted(f2c.FOLDS))

    def test_treinar_stacking_usa_exclusivamente_o_pool_do_proprio_fold(self):
        contexto = self._contexto_sintetico_para_stacking()
        modelos_por_fold = f2c.treinar_stacking_por_fold(contexto, criar_meta_modelo=_MetaModeloFake)

        for fold in f2c.FOLDS:
            linhas = contexto["inner_por_outer_fold"][fold]
            por_id: dict[str, dict] = {}
            for _of, _if, id_sha, _grupo, modelo, vetor, _top1 in linhas:
                por_id.setdefault(id_sha, {})[modelo] = np.asarray(vetor)
            X_esperado, y_esperado = [], []
            for id_sha, scores_modelo in por_id.items():
                reg = contexto["registros"][id_sha]
                X_esperado.append(
                    f2c.montar_features_stacking(scores_modelo, contexto["classes"], reg["H"])
                )
                y_esperado.append(reg["Y"])

            fake = modelos_por_fold[fold]
            np.testing.assert_allclose(
                np.sort(fake.X_fit, axis=0), np.sort(np.vstack(X_esperado), axis=0)
            )
            self.assertEqual(sorted(fake.y_fit.tolist()), sorted(y_esperado))
            # nenhum id nativo do proprio fold entrou no meta-treino desse fold
            nativos_do_fold = {
                id_sha for id_sha, reg in contexto["registros"].items()
                if reg["outer_fold"] == fold
            }
            self.assertFalse(nativos_do_fold & set(por_id))

    def test_prever_stacking_usa_meta_modelo_do_proprio_fold(self):
        contexto = self._contexto_sintetico_para_stacking()
        modelos_por_fold = f2c.treinar_stacking_por_fold(contexto, criar_meta_modelo=_MetaModeloFake)
        for fold in f2c.FOLDS:
            modelos_por_fold[fold].fit(np.zeros((2, 2 * len(MODELOS))), np.array([0, 1]))
        previsoes = f2c.prever_stacking(contexto, modelos_por_fold)
        self.assertEqual(set(previsoes), set(contexto["registros"]))
        for valor in previsoes.values():
            self.assertGreaterEqual(valor, 0.0)
            self.assertLessEqual(valor, 1.0)

    def test_stacking_bloqueia_sem_duas_classes_de_y(self):
        contexto = self._contexto_sintetico_para_stacking()
        for linha in contexto["inner_por_outer_fold"][1]:
            id_sha = linha[2]
            contexto["registros"][id_sha]["Y"] = 0
        with self.assertRaises(f2c.Fase2CBloqueado):
            f2c.treinar_stacking_por_fold(contexto, criar_meta_modelo=_MetaModeloFake)


# --------------------------------------------------------------------------
# Fila e curvas de avaliacao
# --------------------------------------------------------------------------

class TestFilaECurvas(unittest.TestCase):
    def _registros_e_escores(self):
        registros = {
            "id1": {"H": "classe_a", "R": "classe_a", "Y": 0, "outer_fold": 1},
            "id2": {"H": "classe_a", "R": "classe_b", "Y": 1, "outer_fold": 2},
            "id3": {"H": "classe_c", "R": "classe_c", "Y": 0, "outer_fold": 3},
        }
        escores = {"id1": 0.1, "id2": 0.9, "id3": 0.5}
        c_alt = {"id1": None, "id2": "classe_b", "id3": None}
        return registros, escores, c_alt

    def test_montar_fila_ordenada_por_escore_desc(self):
        registros, escores, c_alt = self._registros_e_escores()
        fila = f2c.montar_fila(registros, escores, c_alt)
        self.assertEqual([linha["id_sha256"] for linha in fila], ["id2", "id3", "id1"])
        self.assertEqual(fila[0]["c_alt"], "classe_b")
        self.assertEqual(set(fila[0]), {"id_sha256", "H", "R", "c_alt", "score", "fold", "Y"})

    def test_curva_precisao_recall_pontos_no_intervalo_valido(self):
        registros, escores, c_alt = self._registros_e_escores()
        fila = f2c.montar_fila(registros, escores, c_alt)
        pontos = f2c.curva_precisao_recall(fila)
        self.assertTrue(pontos)
        for ponto in pontos:
            self.assertGreaterEqual(ponto["precisao"], 0.0)
            self.assertLessEqual(ponto["precisao"], 1.0)
            self.assertGreaterEqual(ponto["recall"], 0.0)
            self.assertLessEqual(ponto["recall"], 1.0)

    def test_selecionar_tau_max_f1(self):
        pontos = [
            {"limiar": 0.1, "precisao": 0.2, "recall": 1.0},
            {"limiar": 0.5, "precisao": 0.6, "recall": 0.6},
            {"limiar": 0.9, "precisao": 1.0, "recall": 0.1},
        ]
        melhor = f2c.selecionar_tau(pontos, criterio="max_f1")
        self.assertEqual(melhor["limiar"], 0.5)

    def test_selecionar_tau_criterio_desconhecido(self):
        with self.assertRaises(ValueError):
            f2c.selecionar_tau([{"limiar": 0.1, "precisao": 1.0, "recall": 1.0}], criterio="inexistente")

    def test_selecionar_tau_bloqueia_curva_vazia(self):
        with self.assertRaises(f2c.Fase2CBloqueado):
            f2c.selecionar_tau([], criterio="max_f1")

    def test_curva_ganho_recall_final_e_um(self):
        registros, escores, c_alt = self._registros_e_escores()
        fila = f2c.montar_fila(registros, escores, c_alt)
        pontos = f2c.curva_ganho(fila)
        self.assertEqual(pontos[-1]["k"], len(fila))
        self.assertAlmostEqual(pontos[-1]["recall_acumulado"], 1.0)
        self.assertEqual(pontos[-1]["capturados"], sum(r["Y"] for r in registros.values()))


# --------------------------------------------------------------------------
# Orquestradores (contexto construido a mao, sem tocar arquivo/hash)
# --------------------------------------------------------------------------

class TestOrquestradores(unittest.TestCase):
    def _contexto(self):
        registros = {}
        for i, (h, r, fold) in enumerate([
            ("classe_a", "classe_a", 1), ("classe_b", "classe_c", 2),
            ("classe_c", "classe_c", 3), ("classe_d", "classe_a", 4),
        ]):
            registros[f"id{i}"] = {
                "id_sha256": f"id{i}", "H": h, "R": r, "Y": int(h != r),
                "grupo_sha256": f"g{i}", "outer_fold": fold,
                "scores_outer": _scores_todos_modelos(CLASSES, r),
                "top1_outer": {m: r for m in MODELOS},
            }
        return {"classes": CLASSES, "registros": registros}

    def test_combinar_linear_svc(self):
        fila = f2c.combinar_linear_svc(self._contexto())
        self.assertEqual(len(fila), 4)
        self.assertEqual([f["score"] for f in fila], sorted((f["score"] for f in fila), reverse=True))

    def test_combinar_votacao_majoritaria(self):
        fila = f2c.combinar_votacao_majoritaria(self._contexto())
        self.assertEqual(len(fila), 4)

    def test_combinar_votacao_suave_devolve_pesos(self):
        fila, pesos = f2c.combinar_votacao_suave(self._contexto())
        self.assertEqual(len(fila), 4)
        self.assertAlmostEqual(sum(pesos.values()), 1.0)

    def test_combinar_stacking_usa_c_alt_da_votacao_suave(self):
        contexto = self._contexto()
        # inner_por_outer_fold ausente -> stacking precisa dele; construimos
        # um pool minimo reaproveitando os proprios registros como fake
        # "inner" de todo outer_fold que nao seja o seu proprio.
        inner_por_fold = {f: [] for f in f2c.FOLDS}
        for fold_alvo in f2c.FOLDS:
            for id_sha, reg in contexto["registros"].items():
                if reg["outer_fold"] == fold_alvo:
                    continue
                for modelo in MODELOS:
                    inner_por_fold[fold_alvo].append([
                        fold_alvo, 0, id_sha, reg["grupo_sha256"], modelo,
                        reg["scores_outer"][modelo].tolist(), reg["top1_outer"][modelo],
                    ])
        contexto["inner_por_outer_fold"] = inner_por_fold
        fila = f2c.combinar_stacking(contexto, criar_meta_modelo=_MetaModeloFake)
        self.assertEqual(len(fila), 4)
        fila_suave, pesos = f2c.combinar_votacao_suave(contexto)
        c_alt_suave = {linha["id_sha256"]: linha["c_alt"] for linha in fila_suave}
        for linha in fila:
            self.assertEqual(linha["c_alt"], c_alt_suave[linha["id_sha256"]])


# --------------------------------------------------------------------------
# Proveniencia (comparacoes de hash isoladas, sem depender de dados reais)
# --------------------------------------------------------------------------

class TestValidarProveniencia(unittest.TestCase):
    def _escrever_fixture_ok(self, entrada_dir: Path) -> None:
        (entrada_dir / "fase2b_hashes.json").write_text(
            json.dumps(dict(f2c.HASHES_EXECUCAO_1_ESPERADOS)), encoding="utf-8"
        )
        (entrada_dir / "fase2b_resumo.json").write_text(
            json.dumps({
                "hashes_entrada_gate_zero": dict(efc.HASHES_ESPERADOS),
                "contadores_estruturais": {"total_modelaveis": efc.H_DENTRO_DE_C_ESPERADO},
            }), encoding="utf-8",
        )

    def test_ok_quando_hashes_batem(self):
        with TemporaryDirectory() as tmp:
            entrada_dir = Path(tmp)
            self._escrever_fixture_ok(entrada_dir)
            resultado = f2c.validar_proveniencia(entrada_dir)
            self.assertEqual(resultado["hashes_saida"], dict(f2c.HASHES_EXECUCAO_1_ESPERADOS))

    def test_bloqueia_hash_de_saida_divergente(self):
        with TemporaryDirectory() as tmp:
            entrada_dir = Path(tmp)
            self._escrever_fixture_ok(entrada_dir)
            hashes = dict(f2c.HASHES_EXECUCAO_1_ESPERADOS)
            hashes["fase2b_science_sha256"] = "0" * 64
            (entrada_dir / "fase2b_hashes.json").write_text(json.dumps(hashes), encoding="utf-8")
            with self.assertRaises(f2c.ProveninciaDivergente):
                f2c.validar_proveniencia(entrada_dir)

    def test_bloqueia_hash_de_entrada_divergente(self):
        with TemporaryDirectory() as tmp:
            entrada_dir = Path(tmp)
            self._escrever_fixture_ok(entrada_dir)
            resumo = json.loads((entrada_dir / "fase2b_resumo.json").read_text(encoding="utf-8"))
            resumo["hashes_entrada_gate_zero"]["hash_corpus"] = "0" * 64
            (entrada_dir / "fase2b_resumo.json").write_text(json.dumps(resumo), encoding="utf-8")
            with self.assertRaises(f2c.ProveninciaDivergente):
                f2c.validar_proveniencia(entrada_dir)

    def test_bloqueia_total_modelaveis_divergente(self):
        with TemporaryDirectory() as tmp:
            entrada_dir = Path(tmp)
            self._escrever_fixture_ok(entrada_dir)
            resumo = json.loads((entrada_dir / "fase2b_resumo.json").read_text(encoding="utf-8"))
            resumo["contadores_estruturais"]["total_modelaveis"] = 1
            (entrada_dir / "fase2b_resumo.json").write_text(json.dumps(resumo), encoding="utf-8")
            with self.assertRaises(f2c.JuncaoInvalida):
                f2c.validar_proveniencia(entrada_dir)


class TestPredicoesAgregadasNpz(unittest.TestCase):
    def _linhas_sinteticas(self):
        inner_rows = [
            [1, 2, "id1", "g1", "linear_svc", _vetor(CLASSES, "classe_a").tolist(), "classe_a"],
            [1, 3, "id2", "g2", "linear_svc", _vetor(CLASSES, "classe_b").tolist(), "classe_b"],
        ]
        outer_rows = [
            [1, "id1", "g1", "linear_svc", _vetor(CLASSES, "classe_a").tolist(), "classe_a"],
            [2, "id2", "g2", "linear_svc", _vetor(CLASSES, "classe_b").tolist(), "classe_b"],
        ]
        return inner_rows, outer_rows

    def _gravar(self, entrada_dir: Path, inner_rows, outer_rows) -> None:
        arrays = efc.montar_arrays_npz(inner_rows, outer_rows)
        inner_meta = {k: v for k, v in arrays.items() if k.startswith("inner_") and k != "inner_scores"}
        outer_meta = {k: v for k, v in arrays.items() if k.startswith("outer_") and k != "outer_scores"}
        np.savez_compressed(entrada_dir / "fase2b_inner_scores.npz", scores=arrays["inner_scores"], **inner_meta)
        np.savez_compressed(entrada_dir / "fase2b_outer_scores.npz", scores=arrays["outer_scores"], **outer_meta)

    def test_round_trip_preserva_linhas(self):
        inner_rows, outer_rows = self._linhas_sinteticas()
        with TemporaryDirectory() as tmp:
            entrada_dir = Path(tmp)
            self._gravar(entrada_dir, inner_rows, outer_rows)
            inner_lido, outer_lido = f2c.carregar_predicoes_agregadas(entrada_dir)
        self.assertEqual(
            sorted(inner_lido, key=efc._chave_inner), sorted(inner_rows, key=efc._chave_inner)
        )
        self.assertEqual(
            sorted(outer_lido, key=efc._chave_outer), sorted(outer_rows, key=efc._chave_outer)
        )

    def test_verificar_hashes_recomputados_ok(self):
        inner_rows, outer_rows = self._linhas_sinteticas()
        hashes_esperados = {
            "inner_predictions_canonical_sha256": efc.calcular_predicoes_canonical_sha256(
                inner_rows, efc._chave_inner
            ),
            "outer_predictions_canonical_sha256": efc.calcular_predicoes_canonical_sha256(
                outer_rows, efc._chave_outer
            ),
        }
        f2c.verificar_hashes_recomputados(inner_rows, outer_rows, hashes_esperados)  # nao levanta

    def test_verificar_hashes_recomputados_bloqueia_divergencia(self):
        inner_rows, outer_rows = self._linhas_sinteticas()
        hashes_esperados = {
            "inner_predictions_canonical_sha256": "0" * 64,
            "outer_predictions_canonical_sha256": efc.calcular_predicoes_canonical_sha256(
                outer_rows, efc._chave_outer
            ),
        }
        with self.assertRaises(f2c.ProveninciaDivergente):
            f2c.verificar_hashes_recomputados(inner_rows, outer_rows, hashes_esperados)


class TestCarregarClasses(unittest.TestCase):
    def test_ok_com_41_classes(self):
        with TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "classes.json"
            payload = {"classes": [{"index": i, "label": c} for i, c in enumerate(CLASSES_41)]}
            caminho.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(f2c.carregar_classes(caminho), CLASSES_41)

    def test_bloqueia_total_de_classes_divergente(self):
        with TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "classes.json"
            payload = {"classes": [{"index": 0, "label": "so_uma"}]}
            caminho.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(f2c.JuncaoInvalida):
                f2c.carregar_classes(caminho)


# --------------------------------------------------------------------------
# montar_contexto: integracao end-to-end com dados sinteticos
# --------------------------------------------------------------------------

class TestMontarContexto(unittest.TestCase):
    def _montar_ambiente_sintetico(self, tmp: Path):
        registros_alvo = []
        outer_rows = []
        inner_rows = []
        for i, fold in enumerate(f2c.FOLDS, start=1):
            id_sha = f"id{i}"
            h = CLASSES_41[i % len(CLASSES_41)]
            r = CLASSES_41[(i + 1) % len(CLASSES_41)]
            registros_alvo.append({
                "id_sha256": id_sha, "grupo_sha256": f"g{i}", "outer_fold": fold,
                "categoria_historica": h, "referencia_humana": r,
                "historico_no_espaco_de_classes": True, "alvo_inadequacao": int(h != r),
            })
            for modelo in MODELOS:
                vetor = _vetor(CLASSES_41, r).tolist()
                outer_rows.append([fold, id_sha, f"g{i}", modelo, vetor, r])
                outro_fold = fold % len(f2c.FOLDS) + 1
                inner_rows.append([outro_fold, fold, id_sha, f"g{i}", modelo, vetor, r])

        (tmp / "alvo_ensemble_online.json").write_text(
            json.dumps({"metadata": {}, "records": registros_alvo}), encoding="utf-8"
        )
        (tmp / "classes_ensemble.json").write_text(
            json.dumps({"classes": [{"index": i, "label": c} for i, c in enumerate(CLASSES_41)]}),
            encoding="utf-8",
        )
        entrada_dir = tmp / "fase2b"
        entrada_dir.mkdir()
        arrays = efc.montar_arrays_npz(inner_rows, outer_rows)
        inner_meta = {k: v for k, v in arrays.items() if k.startswith("inner_") and k != "inner_scores"}
        outer_meta = {k: v for k, v in arrays.items() if k.startswith("outer_") and k != "outer_scores"}
        np.savez_compressed(entrada_dir / "fase2b_inner_scores.npz", scores=arrays["inner_scores"], **inner_meta)
        np.savez_compressed(entrada_dir / "fase2b_outer_scores.npz", scores=arrays["outer_scores"], **outer_meta)
        (entrada_dir / "fase2b_manifesto.json").write_text(
            json.dumps({"ordem_classes": CLASSES_41, "modelos": MODELOS}), encoding="utf-8"
        )
        (entrada_dir / "fase2b_hashes.json").write_text(
            json.dumps(dict(f2c.HASHES_EXECUCAO_1_ESPERADOS)), encoding="utf-8"
        )
        (entrada_dir / "fase2b_resumo.json").write_text(
            json.dumps({
                "hashes_entrada_gate_zero": dict(efc.HASHES_ESPERADOS),
                # total_modelaveis fixo no valor real de producao: este
                # campo so e conferido como contagem opaca de metadado, nao
                # recontado contra o corpus sintetico local (5 registros).
                "contadores_estruturais": {"total_modelaveis": efc.H_DENTRO_DE_C_ESPERADO},
            }), encoding="utf-8",
        )
        return entrada_dir, tmp / "alvo_ensemble_online.json", tmp / "classes_ensemble.json"

    def test_monta_contexto_com_hash_de_predicoes_desativado(self):
        with TemporaryDirectory() as tmp:
            entrada_dir, alvo_path, classes_path = self._montar_ambiente_sintetico(Path(tmp))
            contexto = f2c.montar_contexto(
                entrada_dir, alvo_path, classes_path, verificar_hashes_predicoes=False
            )
        self.assertEqual(len(contexto["registros"]), len(f2c.FOLDS))
        self.assertEqual(contexto["classes"], CLASSES_41)
        for reg in contexto["registros"].values():
            self.assertEqual(set(reg["scores_outer"]), set(MODELOS))
        self.assertEqual(set(contexto["inner_por_outer_fold"]), set(f2c.FOLDS))

    def test_monta_contexto_bloqueia_por_padrao_com_dados_nao_oficiais(self):
        # verificar_hashes_predicoes=True e o padrao: dados sinteticos nunca
        # reproduzem os hashes de predicao reais da Execucao Cientifica 1,
        # entao o gate deve bloquear — prova que a checagem esta realmente
        # ligada em `montar_contexto`, nao so disponivel isoladamente.
        with TemporaryDirectory() as tmp:
            entrada_dir, alvo_path, classes_path = self._montar_ambiente_sintetico(Path(tmp))
            with self.assertRaises(f2c.ProveninciaDivergente):
                f2c.montar_contexto(entrada_dir, alvo_path, classes_path)


if __name__ == "__main__":
    unittest.main()
