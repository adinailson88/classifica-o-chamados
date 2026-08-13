#!/usr/bin/env python3
"""Testes da Fase 2C: combinacao dos sete modelos-base (votacao, stacking).

Usa fixtures sinteticas pequenas — nunca dados reais de 13.970 registros,
nunca fits de modelo real (o meta-modelo de stacking usa um fake injetado,
mesmo padrao de `criar_modelo` na Fase 2B). Os hashes REAIS da Execucao
Cientifica 1 (`HASHES_EXECUCAO_1_ESPERADOS`, `ensemble_fase2b_crossfit.
HASHES_ESPERADOS`) sao exercidos como constantes opacas — os testes de
`validar_proveniencia` os comparam contra conteudo de arquivo controlado
pelo teste, nunca contra dados sinteticos que precisariam reproduzi-los por
forca bruta.

`montar_contexto` e testado com `verificar_hashes_predicoes=False` (a
checagem criptografica das previsoes ja tem teste isolado em
`TestVerificarHashesRecomputados`) e, num teste dedicado, com o padrao
`verificar_hashes_predicoes=True` para confirmar que dados sinteticos (que
nao reproduzem os hashes reais) sao corretamente bloqueados.

Cobertura da correcao vinculante (auditoria independente): pesos da
votacao suave derivados exclusivamente do pool interno, formula
regularizada por modelo/classe, selecao de alpha sem tocar a dobra
externa, desempate majoritario em tres niveis, capacidade K_f do
LinearSVC substituindo `max_f1`, e ausencia de chamada automatica a
`selecionar_tau` na execucao confirmatoria.
"""

from __future__ import annotations

import json
import sys
import unittest
import unittest.mock
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


def _contexto_multi_fold(classes: list[str] = CLASSES, y_alternando: bool = True) -> dict:
    """5 outer folds; cada um com 2 ids 'nativos' (H dentro de C). O pool
    interno do fold `f` contem, para CADA outro fold `g != f`, os ids
    nativos de `g` com previsoes dos 7 modelos — mesma invariante
    leakage-free da Fase 2B (T_f = uniao dos OUTROS folds), com
    `inner_fold` marcado como o fold nativo de origem (permite a validacao
    interna de alpha por leave-one-inner-fold-out)."""
    registros: dict[str, dict] = {}
    nativos_por_fold: dict[int, list[str]] = {}
    contador = 0
    for fold in f2c.FOLDS:
        ids_fold = []
        for _ in range(2):
            id_sha = f"nativo_{contador}"
            contador += 1
            ids_fold.append(id_sha)
            registros[id_sha] = {
                "id_sha256": id_sha, "H": "classe_a", "R": "classe_a", "Y": 0,
                "grupo_sha256": f"g_{id_sha}", "outer_fold": fold,
                "scores_outer": _scores_todos_modelos(classes, "classe_a"),
                "top1_outer": {m: "classe_a" for m in MODELOS},
            }
        nativos_por_fold[fold] = ids_fold

    if y_alternando:
        for id_sha in list(registros)[1::2]:
            registros[id_sha]["Y"] = 1
            registros[id_sha]["R"] = "classe_b"

    inner_por_fold: dict[int, list] = {f: [] for f in f2c.FOLDS}
    for fold in f2c.FOLDS:
        for outro_fold in f2c.FOLDS:
            if outro_fold == fold:
                continue
            for id_sha in nativos_por_fold[outro_fold]:
                reg = registros[id_sha]
                for modelo in MODELOS:
                    inner_por_fold[fold].append([
                        fold, outro_fold, id_sha, reg["grupo_sha256"], modelo,
                        reg["scores_outer"][modelo].tolist(), reg["top1_outer"][modelo],
                    ])

    return {
        "classes": classes, "registros": registros,
        "inner_por_outer_fold": inner_por_fold, "nativos_por_fold": nativos_por_fold,
    }


# --------------------------------------------------------------------------
# Escores de prioridade — LinearSVC (inalterado pela correcao)
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


# --------------------------------------------------------------------------
# Votacao majoritaria — desempate em 3 niveis + ordenacao dedicada
# --------------------------------------------------------------------------

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

    def test_desempate_nivel1_mais_votos_sem_empate(self):
        votos_alt = {"classe_b": 3, "classe_c": 1}
        scores = _scores_todos_modelos(CLASSES, "classe_b")
        c_alt = f2c.escolher_c_alt_majoritario(votos_alt, CLASSES, scores)
        self.assertEqual(c_alt, "classe_b")

    def test_desempate_nivel2_media_probabilistica(self):
        # empate em votos (2 cada); classe_c deve ganhar por ter media de
        # probabilidade calibrada maior entre os 7 modelos.
        votos_alt = {"classe_b": 2, "classe_c": 2}
        scores = {m: _vetor(CLASSES, "classe_c", intensidade=0.5) for m in MODELOS}
        c_alt = f2c.escolher_c_alt_majoritario(votos_alt, CLASSES, scores)
        self.assertEqual(c_alt, "classe_c")

    def test_desempate_nivel3_ordem_canonica(self):
        # empate em votos E em probabilidade media (vetor uniforme) ->
        # decide pelo menor indice na ordem global (classe_a antes de classe_c).
        votos_alt = {"classe_c": 2, "classe_a": 2}
        scores = {m: np.full(len(CLASSES), 1 / len(CLASSES)) for m in MODELOS}
        c_alt = f2c.escolher_c_alt_majoritario(votos_alt, CLASSES, scores)
        self.assertEqual(c_alt, "classe_a")

    def test_sem_votos_alternativos_devolve_none(self):
        scores = _scores_todos_modelos(CLASSES, "classe_a")
        self.assertIsNone(f2c.escolher_c_alt_majoritario({}, CLASSES, scores))

    def test_formula_s_maj(self):
        top1 = {m: "classe_b" for m in MODELOS}
        top1[MODELOS[0]] = "classe_a"  # 1 voto em H, 6 em classe_b
        scores = _scores_todos_modelos(CLASSES, "classe_b")
        s_maj, c_alt, v_alt, v_h = f2c.escore_votacao_majoritaria(top1, scores, "classe_a", CLASSES)
        self.assertEqual(c_alt, "classe_b")
        self.assertEqual((v_alt, v_h), (6, 1))
        self.assertAlmostEqual(s_maj, (6 - 1) / len(MODELOS))

    def test_unanimidade_com_historico(self):
        top1 = {m: "classe_a" for m in MODELOS}
        scores = _scores_todos_modelos(CLASSES, "classe_a")
        s_maj, c_alt, v_alt, v_h = f2c.escore_votacao_majoritaria(top1, scores, "classe_a", CLASSES)
        self.assertIsNone(c_alt)
        self.assertAlmostEqual(s_maj, -1.0)

    def _contexto_ordenacao(self):
        """3 registros: dois empatam em (v_alt - v_h), diferindo so na
        margem de probabilidade media — a ordenacao deve resolver por ela,
        nunca pelo id."""
        registros = {}
        # id_z e id_a empatam em v_alt-v_h=6-1=5, mas id_a tem margem de
        # probabilidade maior (deve vir primeiro apesar de "id_a" < "id_z"
        # nao ser o motivo).
        for id_sha, intensidade in [("id_z", 0.9), ("id_a", 0.99)]:
            top1 = {m: "classe_b" for m in MODELOS}
            top1[MODELOS[0]] = "classe_a"
            scores = {m: _vetor(CLASSES, "classe_b", intensidade=intensidade) for m in MODELOS}
            registros[id_sha] = {
                "id_sha256": id_sha, "H": "classe_a", "R": "classe_a", "Y": 0,
                "outer_fold": 1, "scores_outer": scores, "top1_outer": top1,
            }
        # id_baixo: v_alt - v_h menor (fica por ultimo, criterio 1 decide).
        top1_baixo = {m: "classe_a" for m in MODELOS}
        registros["id_baixo"] = {
            "id_sha256": "id_baixo", "H": "classe_a", "R": "classe_a", "Y": 0,
            "outer_fold": 1, "scores_outer": _scores_todos_modelos(CLASSES, "classe_a"),
            "top1_outer": top1_baixo,
        }
        return {"classes": CLASSES, "registros": registros}

    def test_montar_fila_majoritaria_criterio2_desempata_por_probabilidade(self):
        fila = f2c.montar_fila_majoritaria(self._contexto_ordenacao())
        ordem = [linha["id_sha256"] for linha in fila]
        self.assertEqual(ordem, ["id_a", "id_z", "id_baixo"])

    def test_montar_fila_majoritaria_nunca_e_ordenacao_generica(self):
        # combinar_votacao_majoritaria delega em montar_fila_majoritaria,
        # nunca em montar_fila (score+id).
        contexto = self._contexto_ordenacao()
        fila_majoritaria = f2c.combinar_votacao_majoritaria(contexto)
        self.assertEqual(
            [l["id_sha256"] for l in fila_majoritaria], ["id_a", "id_z", "id_baixo"]
        )


# --------------------------------------------------------------------------
# Votacao suave — pesos regularizados (contrato aprovado)
# --------------------------------------------------------------------------

class TestPesosVotacaoSuaveRegularizados(unittest.TestCase):
    def _fixture_formula(self):
        classes = ["a", "b", "c"]
        linhas = [
            # outer_fold, inner_fold, id, grupo, modelo, vetor, top1
            [1, 2, "id1", "g1", "linear_svc", [1, 0, 0], "a"],
            [1, 2, "id1", "g1", "naive_bayes", [0, 1, 0], "b"],
            [1, 3, "id2", "g2", "linear_svc", [1, 0, 0], "a"],
            [1, 3, "id2", "g2", "naive_bayes", [1, 0, 0], "a"],
            [1, 4, "id3", "g3", "linear_svc", [0, 0, 1], "c"],
            [1, 4, "id3", "g3", "naive_bayes", [0, 1, 0], "b"],
        ]
        referencia = {
            "id1": {"R": "a"}, "id2": {"R": "a"}, "id3": {"R": "b"},
        }
        return classes, linhas, referencia

    def test_formula_w_mc_alpha_5(self):
        classes, linhas, referencia = self._fixture_formula()
        pesos = f2c.pesos_votacao_suave_regularizados(
            linhas, referencia, classes, alpha=5, modelos=["linear_svc", "naive_bayes"]
        )
        # indices: a=0, b=1, c=2
        self.assertAlmostEqual(pesos["linear_svc"][0], 0.7619047619047619)  # w_ls_a
        self.assertAlmostEqual(pesos["linear_svc"][1], 0.3333333333333333)  # w_ls_b
        self.assertAlmostEqual(pesos["linear_svc"][2], 0.0)                 # w_ls_c
        self.assertAlmostEqual(pesos["naive_bayes"][0], 0.7222222222222222)  # w_nb_a
        self.assertAlmostEqual(pesos["naive_bayes"][1], 0.38095238095238093)  # w_nb_b
        self.assertAlmostEqual(pesos["naive_bayes"][2], 0.0)                  # w_nb_c

    def test_pesos_derivados_apenas_do_pool_interno_sem_tocar_registros_nativos(self):
        # Construir dois contextos identicos no pool interno de um fold,
        # diferindo SOMENTE em registros que sao "nativos" daquele fold
        # (nunca aparecem no proprio pool interno dele, por construcao) —
        # os pesos daquele fold devem ser identicos.
        ctx_a = _contexto_multi_fold()
        ctx_b = _contexto_multi_fold()
        fold_alvo = 1
        for id_sha in ctx_b["nativos_por_fold"][fold_alvo]:
            ctx_b["registros"][id_sha]["R"] = "classe_d"
            ctx_b["registros"][id_sha]["Y"] = 1
            ctx_b["registros"][id_sha]["scores_outer"] = _scores_todos_modelos(CLASSES, "classe_d")
            ctx_b["registros"][id_sha]["top1_outer"] = {m: "classe_d" for m in MODELOS}

        pesos_a = f2c.pesos_votacao_suave_regularizados(
            ctx_a["inner_por_outer_fold"][fold_alvo], ctx_a["registros"], CLASSES, alpha=20,
        )
        pesos_b = f2c.pesos_votacao_suave_regularizados(
            ctx_b["inner_por_outer_fold"][fold_alvo], ctx_b["registros"], CLASSES, alpha=20,
        )
        for modelo in MODELOS:
            np.testing.assert_allclose(pesos_a[modelo], pesos_b[modelo])

    def test_bloqueia_pool_interno_vazio(self):
        with self.assertRaises(f2c.Fase2CBloqueado):
            f2c.pesos_votacao_suave_regularizados([], {}, CLASSES, alpha=5)


class TestEscoreCombinadoSuave(unittest.TestCase):
    def test_soma_um_e_nao_negativo(self):
        pesos = {m: np.full(len(CLASSES), 0.5) for m in MODELOS}
        scores = _scores_todos_modelos(CLASSES, "classe_b")
        combinado = f2c.escore_combinado_suave(scores, pesos, CLASSES)
        self.assertAlmostEqual(combinado.sum(), 1.0)
        self.assertTrue((combinado >= 0).all())

    def test_formula_s_soft(self):
        scores = _scores_todos_modelos(CLASSES, "classe_a")
        scores["linear_svc"] = _vetor(CLASSES, "classe_c", intensidade=0.9)
        pesos = {m: (np.ones(len(CLASSES)) if m == "linear_svc" else np.zeros(len(CLASSES)))
                 for m in MODELOS}
        s_soft, c_alt = f2c.escore_votacao_suave(scores, pesos, CLASSES, "classe_a")
        # peso 100% em linear_svc: o combinado normalizado e o vetor dele.
        vetor = scores["linear_svc"]
        esperado = vetor[CLASSES.index("classe_c")] - vetor[CLASSES.index("classe_a")]
        self.assertAlmostEqual(s_soft, esperado)
        self.assertEqual(c_alt, "classe_c")


class TestSelecaoAlpha(unittest.TestCase):
    def test_alpha_selecionado_entre_candidatos_padrao(self):
        ctx = _contexto_multi_fold()
        alpha, candidatos = f2c.selecionar_alpha_votacao_suave(
            ctx["inner_por_outer_fold"][1], ctx["registros"], CLASSES
        )
        self.assertIn(alpha, f2c.ALPHAS_PADRAO)
        self.assertEqual({c["alpha"] for c in candidatos}, set(f2c.ALPHAS_PADRAO))

    def test_selecao_de_alpha_independe_da_dobra_externa(self):
        # Mudar registros "nativos" do fold alvo (dados que so aparecem na
        # dobra EXTERNA daquele fold, nunca no seu proprio pool interno)
        # nao pode mudar a escolha de alpha nem os candidatos.
        fold_alvo = 1
        ctx_a = _contexto_multi_fold()
        ctx_b = _contexto_multi_fold()
        for id_sha in ctx_b["nativos_por_fold"][fold_alvo]:
            ctx_b["registros"][id_sha]["R"] = "classe_d"
            ctx_b["registros"][id_sha]["Y"] = 1

        alpha_a, candidatos_a = f2c.selecionar_alpha_votacao_suave(
            ctx_a["inner_por_outer_fold"][fold_alvo], ctx_a["registros"], CLASSES
        )
        alpha_b, candidatos_b = f2c.selecionar_alpha_votacao_suave(
            ctx_b["inner_por_outer_fold"][fold_alvo], ctx_b["registros"], CLASSES
        )
        self.assertEqual(alpha_a, alpha_b)
        self.assertEqual(candidatos_a, candidatos_b)

    def test_bloqueia_pool_com_menos_de_2_rotacoes_internas(self):
        linha_unica = [[1, 2, "id1", "g1", "linear_svc", [1, 0, 0, 0], "classe_a"]]
        with self.assertRaises(f2c.Fase2CBloqueado):
            f2c.selecionar_alpha_votacao_suave(linha_unica, {"id1": {"R": "classe_a"}}, CLASSES)


class TestPesosEAlphaPorFold(unittest.TestCase):
    def test_um_resultado_por_outer_fold(self):
        ctx = _contexto_multi_fold()
        info = f2c.pesos_e_alpha_votacao_suave_por_fold(ctx)
        self.assertEqual(sorted(info), sorted(f2c.FOLDS))
        for fold, dados in info.items():
            self.assertIn(dados["alpha"], f2c.ALPHAS_PADRAO)
            self.assertEqual(set(dados["pesos"]), set(MODELOS))


# --------------------------------------------------------------------------
# Stacking (inalterado pela correcao, exceto a fonte do c_alt no orquestrador)
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

    def test_treinar_stacking_um_modelo_por_fold(self):
        contexto = _contexto_multi_fold()
        modelos_por_fold = f2c.treinar_stacking_por_fold(contexto, criar_meta_modelo=_MetaModeloFake)
        self.assertEqual(sorted(modelos_por_fold), sorted(f2c.FOLDS))

    def test_treinar_stacking_usa_exclusivamente_o_pool_do_proprio_fold(self):
        contexto = _contexto_multi_fold()
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
            nativos_do_fold = set(contexto["nativos_por_fold"][fold])
            self.assertFalse(nativos_do_fold & set(por_id))

    def test_prever_stacking_usa_meta_modelo_do_proprio_fold(self):
        contexto = _contexto_multi_fold()
        modelos_por_fold = f2c.treinar_stacking_por_fold(contexto, criar_meta_modelo=_MetaModeloFake)
        for fold in f2c.FOLDS:
            modelos_por_fold[fold].fit(np.zeros((2, 2 * len(MODELOS))), np.array([0, 1]))
        previsoes = f2c.prever_stacking(contexto, modelos_por_fold)
        self.assertEqual(set(previsoes), set(contexto["registros"]))
        for valor in previsoes.values():
            self.assertGreaterEqual(valor, 0.0)
            self.assertLessEqual(valor, 1.0)

    def test_stacking_bloqueia_sem_duas_classes_de_y(self):
        contexto = _contexto_multi_fold()
        for linha in contexto["inner_por_outer_fold"][1]:
            id_sha = linha[2]
            contexto["registros"][id_sha]["Y"] = 0
        with self.assertRaises(f2c.Fase2CBloqueado):
            f2c.treinar_stacking_por_fold(contexto, criar_meta_modelo=_MetaModeloFake)


# --------------------------------------------------------------------------
# Fila, curvas de avaliacao e capacidade K_f
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

    def test_selecionar_tau_exige_criterio_explicito(self):
        # sem valor padrao: chamar sem `criterio` e TypeError, nao um
        # comportamento implicito de max_f1.
        with self.assertRaises(TypeError):
            f2c.selecionar_tau([{"limiar": 0.1, "precisao": 1.0, "recall": 1.0}])

    def test_selecionar_tau_max_f1_quando_pedido_explicitamente(self):
        pontos = [
            {"limiar": 0.1, "precisao": 0.2, "recall": 1.0},
            {"limiar": 0.5, "precisao": 0.6, "recall": 0.6},
            {"limiar": 0.9, "precisao": 1.0, "recall": 0.1},
        ]
        melhor = f2c.selecionar_tau(pontos, criterio="max_f1")
        self.assertEqual(melhor["limiar"], 0.5)

    def test_selecionar_tau_criterio_desconhecido(self):
        with self.assertRaises(ValueError):
            f2c.selecionar_tau(
                [{"limiar": 0.1, "precisao": 1.0, "recall": 1.0}], criterio="inexistente"
            )

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

    def test_capacidade_linear_svc_por_fold(self):
        contexto = {
            "registros": {
                "id1": {"H": "classe_a", "outer_fold": 1, "top1_outer": {"linear_svc": "classe_b"}},
                "id2": {"H": "classe_a", "outer_fold": 1, "top1_outer": {"linear_svc": "classe_a"}},
                "id3": {"H": "classe_c", "outer_fold": 2, "top1_outer": {"linear_svc": "classe_a"}},
            }
        }
        capacidade = f2c.capacidade_linear_svc_por_fold(contexto)
        self.assertEqual(capacidade, {1: 1, 2: 1})

    def test_aplicar_capacidade_por_fold_trunca_por_dobra(self):
        fila = [
            {"id_sha256": "a", "fold": 1, "Y": 1}, {"id_sha256": "b", "fold": 1, "Y": 0},
            {"id_sha256": "c", "fold": 1, "Y": 0}, {"id_sha256": "d", "fold": 2, "Y": 1},
        ]
        selecionados = f2c.aplicar_capacidade_por_fold(fila, {1: 2, 2: 1})
        self.assertEqual([l["id_sha256"] for l in selecionados], ["a", "b", "d"])

    def test_resumo_capacidade(self):
        fila_capacidade = [{"Y": 1}, {"Y": 0}, {"Y": 1}, {"Y": 0}]
        resumo = f2c.resumo_capacidade(fila_capacidade)
        self.assertEqual(resumo, {"total_na_fila": 4, "capturados_y1": 2, "precisao": 0.5})


# --------------------------------------------------------------------------
# Orquestradores (contexto construido a mao, sem tocar arquivo/hash)
# --------------------------------------------------------------------------

class TestOrquestradores(unittest.TestCase):
    def test_combinar_linear_svc(self):
        ctx = _contexto_multi_fold()
        fila = f2c.combinar_linear_svc(ctx)
        self.assertEqual(len(fila), len(ctx["registros"]))
        self.assertEqual([f["score"] for f in fila], sorted((f["score"] for f in fila), reverse=True))

    def test_combinar_votacao_majoritaria(self):
        ctx = _contexto_multi_fold()
        fila = f2c.combinar_votacao_majoritaria(ctx)
        self.assertEqual(len(fila), len(ctx["registros"]))

    def test_combinar_votacao_suave_pesos_por_fold(self):
        ctx = _contexto_multi_fold()
        fila, info_por_fold = f2c.combinar_votacao_suave(ctx)
        self.assertEqual(len(fila), len(ctx["registros"]))
        self.assertEqual(sorted(info_por_fold), sorted(f2c.FOLDS))
        for linha in fila:
            self.assertIn(linha["fold"], info_por_fold)

    def test_combinar_stacking_c_alt_usa_pesos_do_proprio_fold(self):
        ctx = _contexto_multi_fold()
        fila = f2c.combinar_stacking(ctx, criar_meta_modelo=_MetaModeloFake)
        self.assertEqual(len(fila), len(ctx["registros"]))
        fila_suave, info_por_fold = f2c.combinar_votacao_suave(ctx)
        c_alt_suave = {linha["id_sha256"]: linha["c_alt"] for linha in fila_suave}
        for linha in fila:
            self.assertEqual(linha["c_alt"], c_alt_suave[linha["id_sha256"]])

    def test_comparar_metodos_por_capacidade(self):
        ctx = _contexto_multi_fold()
        filas = {
            "linear_svc": f2c.combinar_linear_svc(ctx),
            "votacao_majoritaria": f2c.combinar_votacao_majoritaria(ctx),
        }
        comparacao, capacidade = f2c.comparar_metodos_por_capacidade(ctx, filas)
        self.assertEqual(set(comparacao), set(filas))
        self.assertEqual(set(capacidade), set(f2c.capacidade_linear_svc_por_fold(ctx)))
        for resumo in comparacao.values():
            self.assertIn("precisao", resumo)

    def test_nenhum_orquestrador_chama_selecionar_tau(self):
        # ausencia de escolha de tau na avaliacao externa: selecionar_tau
        # nunca e chamado por nenhuma das rotas confirmatorias.
        ctx = _contexto_multi_fold()
        with unittest.mock.patch.object(
            f2c, "selecionar_tau", side_effect=AssertionError("selecionar_tau nao deveria ser chamado")
        ):
            f2c.combinar_linear_svc(ctx)
            f2c.combinar_votacao_majoritaria(ctx)
            fila_suave, info_por_fold = f2c.combinar_votacao_suave(ctx)
            f2c.combinar_stacking(ctx, criar_meta_modelo=_MetaModeloFake, info_por_fold=info_por_fold)
            f2c.comparar_metodos_por_capacidade(ctx, {"votacao_suave": fila_suave})


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
