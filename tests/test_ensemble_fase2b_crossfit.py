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
import sys
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402

import ensemble_fase2b_crossfit as f2b  # noqa: E402

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


if __name__ == "__main__":
    unittest.main()
