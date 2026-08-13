#!/usr/bin/env python3
"""Testes da Fase 2B: cross-fitting aninhado dos sete modelos-base.

Usa fixtures sinteticas pequenas com um `criar_modelo` injetado (fake
deterministico via MD5, sem TensorFlow real) — os 175/25 fits e as
invariantes de vazamento sao estruturais, nao dependem da escala real de
13.972 registros nem de treinar modelos de verdade.
"""

from __future__ import annotations

import collections
import hashlib
import inspect
import json
import sys
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402

import ensemble_fase2b_crossfit as f2b  # noqa: E402
import modelos_zoo as zoo  # noqa: E402
import modelo_lstm  # noqa: E402

CLASSES = ["classe_a", "classe_b", "classe_c"]

# Arquivos historicos de OOF proibidos como fonte de meta-features na Fase 2B.
ARQUIVOS_OOF_PROIBIDOS = (
    "retreino_canonico_predicoes.csv",
    "predicoes_linear_svc_online.csv",
)


class FakeModelo:
    """Modelo fake deterministico (hash MD5 do texto -> classe), sem TF real."""

    def __init__(self, nome: str, fallback_lstm: bool = False,
                 classe_sempre_ausente: str | None = None):
        self.nome = nome
        self.fallback_lstm = fallback_lstm
        self.classe_sempre_ausente = classe_sempre_ausente
        self.classes_vistas: list[str] | None = None
        self.eh_lstm: bool | None = None

    def fit(self, textos, rotulos):
        rotulos = list(rotulos)
        assert all(isinstance(r, str) for r in rotulos), (
            "fit() recebeu rotulo nao-string: os modelos-base devem aprender "
            "R (referencia_humana), nunca Y (alvo_inadequacao, um int 0/1)."
        )
        vistas = sorted(set(rotulos))
        if self.classe_sempre_ausente in vistas:
            vistas.remove(self.classe_sempre_ausente)
        self.classes_vistas = vistas
        if self.nome == "lstm":
            self.eh_lstm = not self.fallback_lstm
        return self

    def predict_dist(self, textos):
        k = len(self.classes_vistas)
        matriz = np.zeros((len(textos), k))
        for i, texto in enumerate(textos):
            idx = int(hashlib.md5(texto.encode("utf-8")).hexdigest(), 16) % k
            matriz[i, idx] = 1.0
        return list(self.classes_vistas), matriz


def _fabricar_criar_modelo(fallback_lstm=False, classe_sempre_ausente=None):
    def _criar(nome):
        return FakeModelo(nome, fallback_lstm=fallback_lstm,
                          classe_sempre_ausente=classe_sempre_ausente)
    return _criar


def _fixar_determinismo_lstm_fake(seed: int = 42) -> None:
    """Substitui `fixar_determinismo_lstm` real (TF) nos testes: no-op."""
    return None


def _construir_gate_sintetico(por_fold: int = 3, incluir_h_fora_de_c: bool = True):
    """5 outer folds x `por_fold` registros modelaveis + 1 H fora de C no fold 1."""
    registros = []
    textos_por_id = {}
    for fold in f2b.FOLDS:
        for i in range(por_fold):
            id_sha = f"id_f{fold}_{i}"
            grupo_sha = f"grupo_f{fold}_{i}"
            classe = CLASSES[i % len(CLASSES)]
            registros.append({
                "id_sha256": id_sha,
                "grupo_sha256": grupo_sha,
                "outer_fold": fold,
                "categoria_historica": classe,
                "referencia_humana": classe,
                "historico_no_espaco_de_classes": True,
                "alvo_inadequacao": 0,
            })
            textos_por_id[id_sha] = f"texto do chamado {id_sha}"
    if incluir_h_fora_de_c:
        id_sha = "id_h_fora_de_c"
        registros.append({
            "id_sha256": id_sha,
            "grupo_sha256": "grupo_h_fora_de_c",
            "outer_fold": 1,
            "categoria_historica": "categoria_nunca_usada_como_referencia",
            "referencia_humana": CLASSES[0],
            "historico_no_espaco_de_classes": False,
            "alvo_inadequacao": 1,
        })
        textos_por_id[id_sha] = "texto do chamado h fora de c"
    return {
        "registros": registros,
        "textos_por_id": textos_por_id,
        "classes": list(CLASSES),
        "hashes": dict(f2b.HASHES_ESPERADOS),
        "total_registros": len(registros),
        "total_grupos": len({r["grupo_sha256"] for r in registros}),
        "h_dentro_de_c": sum(1 for r in registros if r["historico_no_espaco_de_classes"]),
        "h_fora_de_c": sum(1 for r in registros if not r["historico_no_espaco_de_classes"]),
    }


class TestRotacoesInternas(unittest.TestCase):
    def test_quatro_rotacoes_por_outer_fold_generalizado(self):
        for outer_fold in f2b.FOLDS:
            rotacoes = f2b.montar_rotacoes_internas(outer_fold)
            self.assertEqual(len(rotacoes), 4)
            validacoes = sorted(r["validacao"] for r in rotacoes)
            internos_esperados = sorted(f for f in f2b.FOLDS if f != outer_fold)
            self.assertEqual(validacoes, internos_esperados)
            for rot in rotacoes:
                self.assertEqual(rot["outer_fold"], outer_fold)
                self.assertEqual(len(rot["treino"]), 3)
                self.assertNotIn(rot["validacao"], rot["treino"])
                self.assertNotIn(outer_fold, rot["treino"])

    def test_exemplo_fold_1_do_enunciado(self):
        rotacoes = {r["validacao"]: r["treino"] for r in f2b.montar_rotacoes_internas(1)}
        self.assertEqual(rotacoes[2], (3, 4, 5))
        self.assertEqual(rotacoes[3], (2, 4, 5))
        self.assertEqual(rotacoes[4], (2, 3, 5))
        self.assertEqual(rotacoes[5], (2, 3, 4))

    def test_outer_fold_nunca_aparece_no_treino_interno(self):
        for outer_fold in f2b.FOLDS:
            for rot in f2b.montar_rotacoes_internas(outer_fold):
                self.assertNotIn(outer_fold, rot["treino"])
                self.assertNotEqual(rot["validacao"], outer_fold)


class TestExecucaoOuterFold(unittest.TestCase):
    def setUp(self):
        self.gate = _construir_gate_sintetico()
        self.criar_modelo = _fabricar_criar_modelo()

    def _executar(self, outer_fold):
        return f2b.executar_outer_fold(
            outer_fold, self.gate, criar_modelo=self.criar_modelo,
            fixar_determinismo_lstm=_fixar_determinismo_lstm_fake,
        )

    def test_sem_grupo_compartilhado_treino_validacao_ou_externo(self):
        # A propria execucao ja levantaria VazamentoDetectado; aqui so
        # confirmamos que ela completa sem excecao com a fixture valida.
        for outer_fold in f2b.FOLDS:
            self._executar(outer_fold)  # nao deve lancar

    def test_cardinalidade_previsoes_internas(self):
        resultado = self._executar(1)
        contagem = {}
        for linha in resultado["inner_rows"]:
            chave = (linha[2], linha[4])  # (id_sha256, modelo)
            contagem[chave] = contagem.get(chave, 0) + 1
        self.assertTrue(contagem)
        self.assertTrue(all(v == 1 for v in contagem.values()))
        # todo registro modelavel de T_1 (folds 2..5) aparece, para cada modelo
        ids_t1 = {r["id_sha256"] for r in self.gate["registros"]
                  if r["outer_fold"] != 1 and r["historico_no_espaco_de_classes"]}
        ids_vistos = {chave[0] for chave in contagem}
        self.assertEqual(ids_vistos, ids_t1)

    def test_cardinalidade_previsoes_externas(self):
        resultado = self._executar(1)
        contagem = {}
        for linha in resultado["outer_rows"]:
            chave = (linha[1], linha[3])  # (id_sha256, modelo)
            contagem[chave] = contagem.get(chave, 0) + 1
        self.assertTrue(contagem)
        self.assertTrue(all(v == 1 for v in contagem.values()))
        ids_e1 = {r["id_sha256"] for r in self.gate["registros"]
                  if r["outer_fold"] == 1 and r["historico_no_espaco_de_classes"]}
        ids_vistos = {chave[0] for chave in contagem}
        self.assertEqual(ids_vistos, ids_e1)

    def test_h_fora_de_c_excluido_do_aprendizado(self):
        resultado = self._executar(1)
        ids_previstos = {l[2] for l in resultado["inner_rows"]} | {l[1] for l in resultado["outer_rows"]}
        self.assertNotIn("id_h_fora_de_c", ids_previstos)
        self.assertEqual(len(resultado["excluidos_h_fora_de_c"]), 1)
        self.assertEqual(resultado["excluidos_h_fora_de_c"][0]["id_sha256"], "id_h_fora_de_c")
        self.assertEqual(
            resultado["excluidos_h_fora_de_c"][0]["tratamento"],
            "tratamento_taxonomico_deterministico",
        )

    def test_35_fits_por_outer_fold(self):
        resultado = self._executar(1)
        self.assertEqual(len(resultado["fits_info"]), 35)
        internos = [f for f in resultado["fits_info"] if f["inner_fold"] is not None]
        externos = [f for f in resultado["fits_info"] if f["inner_fold"] is None]
        self.assertEqual(len(internos), 28)
        self.assertEqual(len(externos), 7)

    def test_bloqueio_por_vazamento_grupo_treino_validacao(self):
        gate = _construir_gate_sintetico()
        # Duplica um grupo do fold 2 para o fold 3: viola "grupo nao cruza fold".
        alvo = next(r for r in gate["registros"] if r["outer_fold"] == 2)
        clone = dict(alvo)
        clone["id_sha256"] = "id_clonado_vazamento"
        clone["outer_fold"] = 3
        # mesmo grupo_sha256 do registro do fold 2 -> vazamento treino x validacao
        gate["registros"].append(clone)
        gate["textos_por_id"][clone["id_sha256"]] = "texto clonado"
        with self.assertRaises(f2b.VazamentoDetectado):
            f2b.executar_outer_fold(1, gate, criar_modelo=self.criar_modelo,
                                    fixar_determinismo_lstm=_fixar_determinismo_lstm_fake)

    def test_bloqueio_por_fallback_lstm(self):
        criar_modelo_fallback = _fabricar_criar_modelo(fallback_lstm=True)
        with self.assertRaises(f2b.BloqueadoLstmFallback):
            f2b.executar_outer_fold(1, self.gate, criar_modelo=criar_modelo_fallback,
                                    fixar_determinismo_lstm=_fixar_determinismo_lstm_fake)

    def test_nenhum_fit_usa_y_alvo_inadequacao_como_rotulo(self):
        # FakeModelo.fit() ja teria levantado AssertionError se recebesse um Y
        # (int) em vez de R (str); rodar a fixture inteira exercita todo fit().
        for outer_fold in f2b.FOLDS:
            self._executar(outer_fold)


class TestAlinhamentoClasses(unittest.TestCase):
    def test_classe_ausente_e_zero_preenchida_e_reportada(self):
        ordem_global = ["classe_a", "classe_b", "classe_c"]
        classes_modelo = ["classe_a", "classe_c"]  # "classe_b" nunca vista no treino
        matriz = np.array([[0.9, 0.1], [0.2, 0.8]])
        alinhado, ausentes = f2b.alinhar_scores(classes_modelo, matriz, ordem_global)
        self.assertEqual(ausentes, ["classe_b"])
        np.testing.assert_array_equal(alinhado[:, 1], [0.0, 0.0])  # coluna "classe_b"
        np.testing.assert_array_equal(alinhado[:, 0], [0.9, 0.2])
        np.testing.assert_array_equal(alinhado[:, 2], [0.1, 0.8])

    def test_classe_fora_do_espaco_global_bloqueia(self):
        with self.assertRaises(f2b.ContagemEstruturalDivergente):
            f2b.alinhar_scores(["classe_fantasma"], np.array([[1.0]]), ["classe_a"])

    def test_sem_classes_ausentes_quando_treino_ve_tudo(self):
        alinhado, ausentes = f2b.alinhar_scores(
            ["classe_a", "classe_b"], np.array([[0.5, 0.5]]), ["classe_a", "classe_b"]
        )
        self.assertEqual(ausentes, [])


class TestAgregacaoEHashes(unittest.TestCase):
    def _agregado(self, gate=None, criar_modelo=None):
        gate = gate or _construir_gate_sintetico()
        criar_modelo = criar_modelo or _fabricar_criar_modelo()
        resultados = f2b.executar_todos_os_folds(
            gate, criar_modelo=criar_modelo,
            fixar_determinismo_lstm=_fixar_determinismo_lstm_fake,
        )
        return f2b.agregar_execucao(gate, resultados), gate, criar_modelo

    def test_contagem_175_fits_e_25_lstm_em_fixture_sintetica(self):
        agregado, _, _ = self._agregado()
        self.assertEqual(agregado["manifesto"]["fits_totais"], 175)
        self.assertEqual(agregado["manifesto"]["fits_lstm_reais"], 25)
        self.assertEqual(agregado["manifesto"]["fallbacks_lstm"], 0)
        self.assertEqual(agregado["manifesto"]["fits_internos"], 140)
        self.assertEqual(agregado["manifesto"]["fits_externos"], 35)

    def test_determinismo_dos_hashes_cientificos(self):
        agregado_1, gate, criar_modelo = self._agregado()
        resultados_2 = f2b.executar_todos_os_folds(
            gate, criar_modelo=criar_modelo,
            fixar_determinismo_lstm=_fixar_determinismo_lstm_fake,
        )
        agregado_2 = f2b.agregar_execucao(gate, resultados_2)
        self.assertEqual(agregado_1["hashes"], agregado_2["hashes"])
        f2b.comparar_execucoes(agregado_1["hashes"], agregado_2["hashes"])  # nao deve lancar

    def test_bloqueio_nao_determinismo_quando_hashes_divergem(self):
        h1 = {"input_bundle_sha256": "a", "inner_predictions_canonical_sha256": "b",
              "outer_predictions_canonical_sha256": "c", "crossfit_manifest_sha256": "d",
              "fase2b_science_sha256": "e"}
        h2 = dict(h1, fase2b_science_sha256="DIFERENTE")
        with self.assertRaises(f2b.NaoDeterminismoDetectado):
            f2b.comparar_execucoes(h1, h2)

    def test_meta_exemplos_internos_e_externos_esperados_por_modelo(self):
        agregado, gate, _ = self._agregado()
        modelaveis, _ = f2b.montar_registros_modelaveis(gate["registros"], gate["classes"])
        manifesto = agregado["manifesto"]
        self.assertEqual(manifesto["meta_exemplos_internos_esperados_por_modelo"],
                         4 * len(modelaveis))
        for modelo in f2b.MODELOS:
            self.assertEqual(
                manifesto["meta_exemplos_internos_obtidos_por_modelo"][modelo],
                4 * len(modelaveis),
            )
            self.assertEqual(
                manifesto["previsoes_externas_obtidas_por_modelo"][modelo],
                len(modelaveis),
            )


class TestGateZeroHashDivergente(unittest.TestCase):
    def test_hash_corpus_divergente_e_detectado(self):
        observados = dict(f2b.HASHES_ESPERADOS)
        observados["hash_corpus"] = "0" * 64
        divergentes = f2b._hashes_divergentes(observados)
        self.assertIn("hash_corpus", divergentes)
        self.assertEqual(divergentes["hash_corpus"]["esperado"],
                         f2b.HASHES_ESPERADOS["hash_corpus"])
        self.assertEqual(len(divergentes), 1)

    def test_todos_hashes_batendo_nao_diverge(self):
        self.assertEqual(f2b._hashes_divergentes(dict(f2b.HASHES_ESPERADOS)), {})

    def test_multiplos_hashes_divergentes_reportados(self):
        observados = dict(f2b.HASHES_ESPERADOS)
        observados["classes_sha256"] = "x"
        observados["fold_assignment_sha256"] = "y"
        divergentes = f2b._hashes_divergentes(observados)
        self.assertEqual(set(divergentes), {"classes_sha256", "fold_assignment_sha256"})


class TestProibicaoOofAntigo(unittest.TestCase):
    def test_modulo_fase2b_nao_referencia_arquivos_oof_antigos(self):
        caminho = Path(f2b.__file__)
        codigo = caminho.read_text(encoding="utf-8")
        for nome_proibido in ARQUIVOS_OOF_PROIBIDOS:
            self.assertNotIn(
                nome_proibido, codigo,
                f"{caminho.name} referencia {nome_proibido!r}: OOF antigo nao pode "
                "ser usado como fonte de meta-features na Fase 2B.",
            )

    def test_nenhuma_funcao_do_modulo_abre_os_csvs_proibidos(self):
        # Defesa adicional: nenhuma string literal do modulo contem os nomes.
        caminho = Path(f2b.__file__)
        fonte = inspect.getsource(f2b)
        for nome_proibido in ARQUIVOS_OOF_PROIBIDOS:
            self.assertNotIn(nome_proibido, fonte)


class TestDominioAprendido(unittest.TestCase):
    def test_r_fora_de_c_bloqueia(self):
        registros = [{
            "id_sha256": "id1", "grupo_sha256": "g1", "outer_fold": 1,
            "categoria_historica": "classe_a", "referencia_humana": "classe_fantasma",
            "historico_no_espaco_de_classes": True, "alvo_inadequacao": 0,
        }]
        with self.assertRaises(f2b.ContagemEstruturalDivergente):
            f2b.montar_registros_modelaveis(registros, ["classe_a", "classe_b"])

    def test_filtra_apenas_h_fora_de_c(self):
        gate = _construir_gate_sintetico()
        modelaveis, excluidos = f2b.montar_registros_modelaveis(
            gate["registros"], gate["classes"]
        )
        self.assertEqual(len(excluidos), 1)
        self.assertEqual(excluidos[0]["id_sha256"], "id_h_fora_de_c")
        self.assertTrue(all(r["historico_no_espaco_de_classes"] for r in modelaveis))


class TestPersistenciaNpz(unittest.TestCase):
    def test_round_trip_preserva_hashes_e_dtype_float(self):
        import tempfile

        gate = _construir_gate_sintetico()
        criar_modelo = _fabricar_criar_modelo()
        resultados = f2b.executar_todos_os_folds(
            gate, criar_modelo=criar_modelo,
            fixar_determinismo_lstm=_fixar_determinismo_lstm_fake,
        )
        agregado_direto = f2b.agregar_execucao(gate, resultados)

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            for r in resultados:
                f2b.gravar_resultado_fold(r, tmp)
            recarregados = [f2b.carregar_resultado_fold(tmp, fold) for fold in f2b.FOLDS]
            agregado_recarregado = f2b.agregar_execucao(gate, recarregados)
            self.assertEqual(agregado_direto["hashes"], agregado_recarregado["hashes"])

            saida = tmp / "agregado"
            f2b.gravar_agregado(agregado_recarregado, saida)
            with np.load(saida / "fase2b_outer_scores.npz", allow_pickle=True) as npz:
                self.assertEqual(npz["scores"].dtype.kind, "f")
                self.assertEqual(npz["scores"].shape[1], len(gate["classes"]))
            with np.load(saida / "fase2b_inner_scores.npz", allow_pickle=True) as npz:
                self.assertEqual(npz["scores"].dtype.kind, "f")
                self.assertEqual(npz["scores"].shape[1], len(gate["classes"]))


class TestCarregarResultadoFoldRegressao(unittest.TestCase):
    """Regressao do bug de desempenho: `carregar_resultado_fold` reindexava
    `npz["chave"]` dentro do loop por linha. Como `NpzFile.__getitem__` nao
    tem cache, isso redescomprimia o array inteiro a cada linha (O(n) por
    acesso x O(n) linhas = O(n^2)). A correcao materializa cada array UMA
    vez antes dos loops. Este teste prova as duas coisas sem depender de
    limite de tempo: (a) cada chave e acessada exatamente 1x, e (b) os dados
    recarregados sao byte-a-byte identicos aos gravados."""

    def test_round_trip_identico_e_cada_chave_npz_acessada_uma_unica_vez(self):
        import tempfile

        gate = _construir_gate_sintetico()
        criar_modelo = _fabricar_criar_modelo()
        resultado = f2b.executar_outer_fold(
            1, gate, criar_modelo=criar_modelo,
            fixar_determinismo_lstm=_fixar_determinismo_lstm_fake,
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            f2b.gravar_resultado_fold(resultado, tmp)

            import numpy.lib.npyio as npyio
            contagem_por_chave = collections.Counter()
            original_getitem = npyio.NpzFile.__getitem__

            def getitem_contado(self, key):
                contagem_por_chave[key] += 1
                return original_getitem(self, key)

            with unittest.mock.patch.object(npyio.NpzFile, "__getitem__", getitem_contado):
                recarregado = f2b.carregar_resultado_fold(tmp, 1)

            chaves_relevantes = {
                "inner_outer_fold", "inner_inner_fold", "inner_id_sha256",
                "inner_grupo_sha256", "inner_modelo", "inner_scores", "inner_top1",
                "outer_outer_fold", "outer_id_sha256", "outer_grupo_sha256",
                "outer_modelo", "outer_scores", "outer_top1",
            }
            self.assertTrue(chaves_relevantes.issubset(contagem_por_chave),
                            "nem todas as chaves esperadas foram lidas do NPZ")
            for chave in chaves_relevantes:
                self.assertEqual(
                    contagem_por_chave[chave], 1,
                    f"{chave} foi acessada {contagem_por_chave[chave]}x via "
                    "npz[...]; esperado exatamente 1x (materializada antes do "
                    "loop, nao redescomprimida por linha).",
                )

            # Round-trip: mesmas linhas (ordem canonica, ja que gravar_resultado_fold
            # ordena antes de salvar), mesmos scores, sem arredondamento.
            self.assertEqual(
                sorted(recarregado["inner_rows"], key=f2b._chave_inner),
                sorted(resultado["inner_rows"], key=f2b._chave_inner),
            )
            self.assertEqual(
                sorted(recarregado["outer_rows"], key=f2b._chave_outer),
                sorted(resultado["outer_rows"], key=f2b._chave_outer),
            )
            self.assertEqual(recarregado["fits_info"], resultado["fits_info"])
            self.assertEqual(
                recarregado["excluidos_h_fora_de_c"],
                resultado["excluidos_h_fora_de_c"],
            )
            self.assertEqual(
                recarregado["total_modelaveis_no_fold"],
                resultado["total_modelaveis_no_fold"],
            )

    def test_scores_preservam_precisao_float_total(self):
        import tempfile

        gate = _construir_gate_sintetico()
        criar_modelo = _fabricar_criar_modelo()
        resultado = f2b.executar_outer_fold(
            2, gate, criar_modelo=criar_modelo,
            fixar_determinismo_lstm=_fixar_determinismo_lstm_fake,
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            f2b.gravar_resultado_fold(resultado, tmp)
            recarregado = f2b.carregar_resultado_fold(tmp, 2)

        originais = {(l[2], l[4]): l[5] for l in resultado["inner_rows"]}
        recarregados = {(l[2], l[4]): l[5] for l in recarregado["inner_rows"]}
        self.assertEqual(set(originais), set(recarregados))
        for chave, vetor_original in originais.items():
            self.assertEqual(vetor_original, recarregados[chave])  # sem arredondamento


class TestControlesDeParalelismoFase2B(unittest.TestCase):
    """Regressao dos controles de determinismo adicionados apos o
    BLOQUEADO_NAO_DETERMINISTICO das Execucoes 1x2: n_jobs=1 fixado so no
    caminho da Fase 2B (nao em modelos_zoo.py) e nenhum hiperparametro
    cientifico alterado."""

    def test_extra_trees_fase2b_usa_n_jobs_1(self):
        modelo = f2b.criar_modelo_fase2b("extra_trees")
        clf = modelo.pipe.named_steps["clf"]
        self.assertEqual(clf.n_jobs, 1)

    def test_random_forest_fase2b_usa_n_jobs_1(self):
        modelo = f2b.criar_modelo_fase2b("random_forest")
        clf = modelo.pipe.named_steps["clf"]
        self.assertEqual(clf.n_jobs, 1)

    def test_random_state_e_hiperparametros_cientificos_preservados(self):
        esperado = {
            "extra_trees": {"n_estimators": 200, "random_state": 42,
                            "class_weight": "balanced"},
            "random_forest": {"n_estimators": 200, "random_state": 42,
                              "class_weight": "balanced"},
        }
        for nome, campos in esperado.items():
            clf = f2b.criar_modelo_fase2b(nome).pipe.named_steps["clf"]
            for campo, valor in campos.items():
                self.assertEqual(getattr(clf, campo), valor,
                                 f"{nome}.{campo} mudou em relacao ao esperado")

    def test_criar_modelo_fase2b_nao_altera_zoo_criar_modelo(self):
        # calling criar_modelo_fase2b nao pode mudar o que zoo.criar_modelo
        # devolve depois (cada chamada constroi um pipeline novo).
        f2b.criar_modelo_fase2b("extra_trees")
        f2b.criar_modelo_fase2b("random_forest")
        direto_et = zoo.criar_modelo("extra_trees").pipe.named_steps["clf"]
        direto_rf = zoo.criar_modelo("random_forest").pipe.named_steps["clf"]
        self.assertEqual(direto_et.n_jobs, -1,
                         "modelos_zoo.criar_modelo nao pode ter sido alterado pela Fase 2B")
        self.assertEqual(direto_rf.n_jobs, -1,
                         "modelos_zoo.criar_modelo nao pode ter sido alterado pela Fase 2B")

    def test_outros_modelos_identicos_entre_fase2b_e_zoo(self):
        for nome in ("naive_bayes", "regressao_logistica", "linear_svc", "sgd"):
            m_fase2b = f2b.criar_modelo_fase2b(nome)
            m_zoo = zoo.criar_modelo(nome)
            self.assertEqual(type(m_fase2b), type(m_zoo))
            self.assertEqual(
                m_fase2b.pipe.named_steps["clf"].get_params(),
                m_zoo.pipe.named_steps["clf"].get_params(),
                f"hiperparametros de {nome} divergem entre Fase 2B e modelos_zoo",
            )
            self.assertEqual(
                m_fase2b.pipe.named_steps["tfidf"].get_params(),
                m_zoo.pipe.named_steps["tfidf"].get_params(),
            )

    def test_lstm_fase2b_e_zoo_sao_o_mesmo_tipo(self):
        m_fase2b = f2b.criar_modelo_fase2b("lstm")
        m_zoo = zoo.criar_modelo("lstm")
        self.assertEqual(type(m_fase2b), type(m_zoo))

    def test_semente_padrao_da_fase2b_e_42(self):
        self.assertEqual(f2b.SEMENTE_PADRAO, 42)

    def test_fixar_determinismo_lstm_seed_padrao_e_42(self):
        import inspect as _inspect
        assinatura = _inspect.signature(modelo_lstm.fixar_determinismo_lstm)
        self.assertEqual(assinatura.parameters["seed"].default, 42)

    def test_arquitetura_lstm_nao_mudou(self):
        # Pin de regressao: garante que a microcorrecao de threading nao
        # alterou nenhum hiperparametro cientifico da LSTM.
        self.assertEqual(modelo_lstm.LSTM_VOCAB_SIZE, 8000)
        self.assertEqual(modelo_lstm.LSTM_MAX_LEN, 120)
        self.assertEqual(modelo_lstm.LSTM_EMBED_DIM, 128)
        self.assertEqual(modelo_lstm.LSTM_UNITS, 64)
        self.assertEqual(modelo_lstm.LSTM_DENSE_UNITS, 64)
        self.assertEqual(modelo_lstm.LSTM_DROPOUT, 0.5)
        self.assertEqual(modelo_lstm.LSTM_LAYERS, 1)
        perfil_padrao = modelo_lstm.PERFIS_LSTM["padrao"]
        self.assertEqual(perfil_padrao["epochs"], 15)
        self.assertEqual(perfil_padrao["batch_size"], 128)
        self.assertEqual(perfil_padrao["paciencia"], 3)

    def test_workflow_define_threading_do_tensorflow(self):
        caminho = (Path(__file__).resolve().parents[1] / ".github" / "workflows"
                  / "ensemble_fase2b_crossfit.yml")
        conteudo = caminho.read_text(encoding="utf-8")
        self.assertIn('TF_NUM_INTRAOP_THREADS: "1"', conteudo)
        self.assertIn('TF_NUM_INTEROP_THREADS: "1"', conteudo)
        # variaveis preexistentes precisam continuar la
        for var in ("PYTHONHASHSEED", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                    "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "TF_DETERMINISTIC_OPS",
                    "TF_ENABLE_ONEDNN_OPTS"):
            self.assertIn(var, conteudo)

    def test_workflow_distingue_marcador_run_de_marcador_canary(self):
        caminho = (Path(__file__).resolve().parents[1] / ".github" / "workflows"
                  / "ensemble_fase2b_crossfit.yml")
        conteudo = caminho.read_text(encoding="utf-8")
        self.assertIn("[FASE2B-RUN]", conteudo)
        self.assertIn("[FASE2B-CANARY]", conteudo)
        self.assertIn("autorizado_cientifico", conteudo)
        self.assertIn("autorizado_canario", conteudo)


class TestFingerprintAmbiente(unittest.TestCase):
    def test_coletar_fingerprint_nao_lanca_e_tem_campos_essenciais(self):
        fp = f2b.coletar_fingerprint_ambiente()
        for campo in ("python_version", "platform", "machine", "cpu_count",
                      "numpy_version", "env_determinismo"):
            self.assertIn(campo, fp)
        self.assertIn("PYTHONHASHSEED", fp["env_determinismo"])
        self.assertIn("TF_NUM_INTRAOP_THREADS", fp["env_determinismo"])
        self.assertIn("TF_NUM_INTEROP_THREADS", fp["env_determinismo"])

    def test_fingerprint_nao_contem_chaves_de_dados_de_chamados(self):
        fp = f2b.coletar_fingerprint_ambiente()
        proibidas = {"id", "id_chamado", "titulo", "descricao", "texto",
                    "referencia_humana", "categoria_historica"}
        self.assertEqual(proibidas & set(fp), set())


class TestComparacaoCanario(unittest.TestCase):
    def _executar_fold1(self, gate, seed_extra=0):
        criar_modelo = _fabricar_criar_modelo()
        return f2b.executar_outer_fold(
            1, gate, criar_modelo=criar_modelo,
            fixar_determinismo_lstm=_fixar_determinismo_lstm_fake,
        )

    def test_replicas_identicas_dao_canario_deterministico(self):
        gate = _construir_gate_sintetico()
        resultado_a = self._executar_fold1(gate)
        resultado_b = self._executar_fold1(gate)
        comparacao = f2b.comparar_canario(resultado_a, resultado_b)
        self.assertEqual(comparacao["veredito"], "CANARIO_DETERMINISTICO")
        self.assertTrue(comparacao["inner_iguais"])
        self.assertTrue(comparacao["outer_iguais"])
        self.assertTrue(comparacao["fits_iguais"])
        for modelo, info in comparacao["por_modelo"].items():
            self.assertTrue(info["inner_identico"], modelo)
            self.assertTrue(info["outer_identico"], modelo)

    def test_replica_divergente_e_detectada_e_reportada_por_modelo(self):
        gate = _construir_gate_sintetico()
        resultado_a = self._executar_fold1(gate)
        resultado_b = json.loads(json.dumps(resultado_a))  # copia profunda
        # perturba um unico score de um unico modelo na replica B
        for linha in resultado_b["outer_rows"]:
            if linha[3] == "lstm":
                linha[4][0] = linha[4][0] + 0.5
                break
        comparacao = f2b.comparar_canario(resultado_a, resultado_b)
        self.assertEqual(comparacao["veredito"], "CANARIO_NAO_DETERMINISTICO")
        self.assertFalse(comparacao["outer_iguais"])
        self.assertFalse(comparacao["por_modelo"]["lstm"]["outer_identico"])
        self.assertTrue(comparacao["por_modelo"]["naive_bayes"]["outer_identico"])


class TestCalcularReplayInputSha256(unittest.TestCase):
    def _registro(self, id_sha="a", titulo="t", descricao_glpi="d", titulo_osm="",
                  descricao_osm="", categoria_historica="Cat A",
                  referencia_humana="Cat A", grupo_sha256="g", outer_fold=1):
        return {
            "id_sha256": id_sha, "titulo": titulo, "descricao_glpi": descricao_glpi,
            "titulo_osm": titulo_osm, "descricao_osm": descricao_osm,
            "categoria_historica": categoria_historica,
            "referencia_humana": referencia_humana,
            "grupo_sha256": grupo_sha256, "outer_fold": outer_fold,
        }

    def test_deterministico_e_insensivel_a_ordem(self):
        a = [self._registro("a"), self._registro("b", titulo="outro")]
        b = list(reversed(a))
        self.assertEqual(f2b.calcular_replay_input_sha256(a),
                         f2b.calcular_replay_input_sha256(b))

    def test_sensivel_a_cada_um_dos_9_campos(self):
        base = self._registro()
        hash_base = f2b.calcular_replay_input_sha256([base])
        for campo in ("id_sha256", "titulo", "descricao_glpi", "titulo_osm",
                     "descricao_osm", "categoria_historica", "referencia_humana",
                     "grupo_sha256"):
            alterado = dict(base)
            alterado[campo] = str(alterado[campo]) + "-mudou"
            self.assertNotEqual(f2b.calcular_replay_input_sha256([alterado]),
                                hash_base, campo)
        alterado_fold = dict(base)
        alterado_fold["outer_fold"] = base["outer_fold"] + 1
        self.assertNotEqual(f2b.calcular_replay_input_sha256([alterado_fold]), hash_base)

    def test_ignora_campos_extras_fora_do_schema_dos_9(self):
        # Prova que um eventual "id_bruto" carregado a mais no dict do
        # registro (nunca deveria existir no bundle) NAO entra no hash: o
        # payload so le os 9 campos nomeados, por construcao.
        base = self._registro()
        com_extra = dict(base, id_bruto="2026070033")
        self.assertEqual(f2b.calcular_replay_input_sha256([base]),
                         f2b.calcular_replay_input_sha256([com_extra]))


class TestGateZeroReplayBloqueios(unittest.TestCase):
    def _registro(self, id_sha="a", titulo="t", descricao_glpi="d", titulo_osm="",
                  descricao_osm="", categoria_historica="Cat A",
                  referencia_humana="Cat A", grupo_sha256=None, outer_fold=1):
        campos = [titulo, descricao_glpi, titulo_osm, descricao_osm]
        if grupo_sha256 is None:
            grupo_sha256 = f2b.rero.cgt.hash_grupo([f2b.rero.cgt.normalizar_texto(c) for c in campos])
        return {
            "id_sha256": id_sha, "titulo": titulo, "descricao_glpi": descricao_glpi,
            "titulo_osm": titulo_osm, "descricao_osm": descricao_osm,
            "categoria_historica": categoria_historica,
            "referencia_humana": referencia_humana,
            "grupo_sha256": grupo_sha256, "outer_fold": outer_fold,
        }

    def test_bloqueia_quando_replay_input_sha256_esperado_nao_pinado(self):
        # Estado padrao do repositorio: REPLAY_INPUT_SHA256_ESPERADO = None.
        self.assertIsNone(f2b.REPLAY_INPUT_SHA256_ESPERADO)
        with self.assertRaises(f2b.ReplayBloqueado):
            f2b.gate_zero_replay(registros_bundle=[self._registro()])

    def test_bloqueia_quando_replay_input_sha256_diverge_do_pinado(self):
        bundle = [self._registro()]
        with unittest.mock.patch.object(f2b, "REPLAY_INPUT_SHA256_ESPERADO", "0" * 64):
            with self.assertRaises(f2b.ReplayBloqueado):
                f2b.gate_zero_replay(registros_bundle=bundle)

    def test_bloqueia_quando_grupo_sha256_de_um_registro_esta_corrompido(self):
        bundle = [self._registro("a"), self._registro("b", titulo="outro")]
        bundle[1]["grupo_sha256"] = "f" * 64  # nao bate com os campos textuais
        # Pina o esperado exatamente igual ao hash do bundle CORROMPIDO, para
        # provar que a checagem de grupo_sha256 por registro (passo 2) pega o
        # que a checagem de replay_input_sha256 (passo 1) sozinha nao pegaria.
        replay_input_do_bundle_corrompido = f2b.calcular_replay_input_sha256(bundle)
        with unittest.mock.patch.object(
            f2b, "REPLAY_INPUT_SHA256_ESPERADO", replay_input_do_bundle_corrompido
        ):
            with self.assertRaises(f2b.ReplayBloqueado):
                f2b.gate_zero_replay(registros_bundle=bundle)


class TestGateZeroReplayParidadeComGateZeroVivo(unittest.TestCase):
    """Corpus sintetico pequeno, alimentado nos dois formatos (registros_online
    para gate_zero() e registros_bundle para gate_zero_replay()): prova que os
    5 hashes metodologicos batem entre os dois modos quando os dados de
    entrada representam o mesmo corpus — sem duplicar nenhuma logica
    cientifica entre as duas funcoes."""

    def _corpus_sintetico(self, n=10):
        particoes, alvo_congelado, online, bundle = {}, {}, [], []
        rotulos = ["Cat A", "Cat B"]
        for i in range(1, n + 1):
            id_ = str(i)
            id_sha = hashlib.sha256(id_.encode("utf-8")).hexdigest()
            fold = ((i - 1) % 5) + 1
            cat = rotulos[i % 2]
            titulo, descricao = f"titulo {i}", f"descricao {i}"
            grupo = f2b.rero.cgt.hash_grupo(
                [f2b.rero.cgt.normalizar_texto(c) for c in (titulo, descricao, "", "")]
            )
            particoes[id_sha] = {"grupo_sha256": grupo, "outer_fold": fold}
            alvo_congelado[id_sha] = {
                "id_sha256": id_sha, "grupo_sha256": grupo, "outer_fold": fold,
                "categoria_historica": cat, "referencia_humana": cat,
                "historico_no_espaco_de_classes": True, "alvo_inadequacao": 0,
            }
            online.append({
                "id": id_, "titulo": titulo, "descricao_glpi": descricao,
                "titulo_osm": "", "descricao_osm": "",
                "categoria_historica": cat, "conferencia_glpi": "Correto",
                "categoria_manual": "",
            })
            bundle.append({
                "id_sha256": id_sha, "titulo": titulo, "descricao_glpi": descricao,
                "titulo_osm": "", "descricao_osm": "",
                "categoria_historica": cat, "referencia_humana": cat,
                "grupo_sha256": grupo, "outer_fold": fold,
            })
        return particoes, alvo_congelado, online, bundle

    def test_hashes_metodologicos_identicos_entre_run_e_replay(self):
        import tempfile

        n = 10
        particoes, alvo_congelado, online, bundle = self._corpus_sintetico(n)

        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            particoes_path = tmp / "particoes.csv"
            with particoes_path.open("w", encoding="utf-8", newline="") as f:
                f.write("id_sha256,grupo_sha256,dobra\n")
                for id_sha, p in particoes.items():
                    f.write(f"{id_sha},{p['grupo_sha256']},{p['outer_fold']}\n")
            alvo_path = tmp / "alvo_ensemble.json"
            alvo_path.write_text(
                json.dumps({"metadata": {"schema_version": 1},
                           "records": list(alvo_congelado.values())}),
                encoding="utf-8",
            )

            with unittest.mock.patch.multiple(
                f2b, TOTAL_ESPERADO=n, GRUPOS_ESPERADOS=n,
                H_DENTRO_DE_C_ESPERADO=n, H_FORA_DE_C_ESPERADO=0,
                CLASSES_ESPERADAS=2,
            ), unittest.mock.patch.object(f2b.rero, "TOTAL_ESPERADO", n):
                # 1a passagem: descobre os hashes "corretos" do corpus
                # sintetico sem depender de HASHES_ESPERADOS (constante da
                # producao, alheia a este corpus de teste).
                with unittest.mock.patch.object(f2b, "_hashes_divergentes",
                                                return_value={}):
                    gate_provisorio = f2b.gate_zero(
                        particoes_path=particoes_path, alvo_congelado_path=alvo_path,
                        registros_online=online,
                    )
                hashes_sinteticos = gate_provisorio["hashes"]
                replay_input_sintetico = f2b.calcular_replay_input_sha256(bundle)

                with unittest.mock.patch.object(f2b, "HASHES_ESPERADOS",
                                                hashes_sinteticos), \
                     unittest.mock.patch.object(f2b, "REPLAY_INPUT_SHA256_ESPERADO",
                                                replay_input_sintetico):
                    gate_run = f2b.gate_zero(
                        particoes_path=particoes_path, alvo_congelado_path=alvo_path,
                        registros_online=online,
                    )
                    gate_replay = f2b.gate_zero_replay(
                        particoes_path=particoes_path, registros_bundle=bundle,
                    )

        self.assertEqual(gate_run["hashes"], gate_replay["hashes"])
        self.assertEqual(gate_run["hashes"], hashes_sinteticos)
        self.assertEqual(gate_replay["replay_input_sha256"], replay_input_sintetico)
        self.assertEqual(gate_run["registros"], gate_replay["registros"])
        self.assertEqual(gate_run["textos_por_id"], gate_replay["textos_por_id"])


class TestWorkflowMarcadorReplay(unittest.TestCase):
    CAMINHO_WORKFLOW = (Path(__file__).resolve().parents[1] / ".github" / "workflows"
                       / "ensemble_fase2b_crossfit.yml")

    def _workflow(self) -> dict:
        import yaml
        with self.CAMINHO_WORKFLOW.open(encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_workflow_reconhece_fase2b_replay_e_e_mutuamente_exclusivo(self):
        conteudo = self.CAMINHO_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("[FASE2B-REPLAY]", conteudo)
        self.assertIn("[FASE2B-REPLAY-PREFLIGHT]", conteudo)
        self.assertIn("autorizado_replay", conteudo)
        self.assertIn("autorizado_replay_preflight", conteudo)
        # os quatro marcadores continuam mutuamente exclusivos na mesma checagem
        self.assertIn("[FASE2B-RUN]", conteudo)
        self.assertIn("[FASE2B-CANARY]", conteudo)

    def test_jobs_de_replay_dependem_do_marcador_autorizado_replay(self):
        conteudo = self.CAMINHO_WORKFLOW.read_text(encoding="utf-8")
        for job in ("gate_zero_replay:", "crossfit_fold_replay:", "agregar_replay:"):
            self.assertIn(job, conteudo)
        self.assertIn("needs.autorizacao.outputs.autorizado_replay == 'true'", conteudo)

    def test_autorizacao_expoe_os_cinco_outputs_mutuamente_exclusivos(self):
        wf = self._workflow()
        outputs = set(wf["jobs"]["autorizacao"]["outputs"])
        self.assertEqual(
            outputs,
            {"autorizado_cientifico", "autorizado_canario",
             "autorizado_replay", "autorizado_replay_preflight",
             "autorizado_replay_recover"},
        )

    def test_preflight_libera_apenas_gate_zero_replay(self):
        """Garantia central da microcorrecao: o job gate_zero_replay aceita
        o preflight, mas crossfit_fold_replay e agregar_replay NUNCA podem
        depender de autorizado_replay_preflight — so de autorizado_replay."""
        wf = self._workflow()
        jobs = wf["jobs"]

        condicao_gate_zero_replay = jobs["gate_zero_replay"]["if"]
        self.assertIn("autorizado_replay_preflight", condicao_gate_zero_replay)
        self.assertIn("autorizado_replay ==", condicao_gate_zero_replay)

        for nome_job in ("crossfit_fold_replay", "agregar_replay"):
            condicao = jobs[nome_job]["if"]
            self.assertNotIn(
                "autorizado_replay_preflight", condicao,
                f"{nome_job} nao pode depender de autorizado_replay_preflight "
                "(o preflight nao pode liberar fits/agregacao)",
            )
            self.assertEqual(
                condicao, "needs.autorizacao.outputs.autorizado_replay == 'true'",
                f"{nome_job} deve depender exclusivamente de autorizado_replay",
            )

    def test_nenhum_job_de_fit_ou_lstm_referencia_o_preflight(self):
        """Confere, por nome de job, que nenhum job que executa fits (RUN,
        CANARY, replay completo) tem o preflight na sua condicao `if`."""
        wf = self._workflow()
        jobs_com_fit = (
            "gate_zero", "crossfit_fold", "agregar",
            "replica_a", "replica_b", "canario_comparar",
            "crossfit_fold_replay", "agregar_replay",
        )
        for nome_job in jobs_com_fit:
            condicao = wf["jobs"][nome_job]["if"]
            self.assertNotIn("autorizado_replay_preflight", condicao, nome_job)

    def test_ordem_de_checagem_preflight_antes_de_replay_no_shell(self):
        # [FASE2B-REPLAY-PREFLIGHT] precisa ser checado antes de
        # [FASE2B-REPLAY] no script de autorizacao (embora bash `==` com `*`
        # ja distinga os dois literais sem ambiguidade, a ordem elif deixa a
        # intencao explicita e evita regressao se a checagem mudar de forma).
        conteudo = self.CAMINHO_WORKFLOW.read_text(encoding="utf-8")
        pos_preflight = conteudo.index('"[FASE2B-REPLAY-PREFLIGHT]"')
        pos_replay = conteudo.index('"[FASE2B-REPLAY]"')
        self.assertLess(pos_preflight, pos_replay)


if __name__ == "__main__":
    unittest.main()
