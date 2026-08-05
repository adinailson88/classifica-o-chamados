from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import inferencia_canonica as inf  # noqa: E402


class TestHolm(unittest.TestCase):
    def test_um_unico_teste_nao_e_ajustado(self):
        self.assertEqual(inf.holm([0.01])[0]["p_ajustado"], 0.01)

    def test_multiplica_pelo_numero_de_testes_restantes(self):
        # Menor p de três testes é multiplicado por 3, o seguinte por 2.
        r = inf.holm([0.01, 0.02, 0.5])
        self.assertAlmostEqual(r[0]["p_ajustado"], 0.03, places=6)
        self.assertAlmostEqual(r[1]["p_ajustado"], 0.04, places=6)
        self.assertAlmostEqual(r[2]["p_ajustado"], 0.5, places=6)

    def test_impoe_monotonia(self):
        # Sem monotonia, o segundo daria 0,02 x 2 = 0,04, abaixo do primeiro.
        r = inf.holm([0.03, 0.02])
        self.assertGreaterEqual(r[0]["p_ajustado"], r[1]["p_ajustado"])

    def test_nunca_passa_de_um(self):
        r = inf.holm([0.6, 0.7, 0.8])
        self.assertTrue(all(x["p_ajustado"] <= 1.0 for x in r))

    def test_holm_e_menos_conservador_que_bonferroni(self):
        p = [0.001, 0.02, 0.04]
        holm = [x["p_ajustado"] for x in inf.holm(p)]
        bonferroni = [min(1.0, 3 * x) for x in p]
        self.assertTrue(all(h <= b + 1e-12 for h, b in zip(holm, bonferroni)))
        self.assertLess(holm[-1], bonferroni[-1])


class TestMacroF1(unittest.TestCase):
    def test_bate_com_o_sklearn(self):
        from sklearn.metrics import f1_score
        rng = np.random.default_rng(7)
        k = 5
        v = rng.integers(0, k, size=400)
        p = rng.integers(0, k, size=400)
        esperado = f1_score(v, p, labels=list(range(k)), average="macro",
                            zero_division=0)
        self.assertAlmostEqual(inf.macro_f1_codificado(v, p, k), esperado,
                               places=10)

    def test_predicao_perfeita_da_um(self):
        v = np.array([0, 1, 2, 0, 1, 2])
        self.assertAlmostEqual(inf.macro_f1_codificado(v, v, 3), 1.0, places=10)

    def test_classe_ausente_conta_como_zero(self):
        # A classe 2 não aparece nem na verdade nem na predição.
        v = np.array([0, 0, 1, 1])
        p = np.array([0, 0, 1, 1])
        self.assertAlmostEqual(inf.macro_f1_codificado(v, p, 3), 2 / 3, places=10)


class TestBlocosEBootstrap(unittest.TestCase):
    def test_blocos_agrupam_registros_do_mesmo_grupo(self):
        blocos = inf.indices_por_grupo(["g1", "g2", "g1", "g1", "g2"])
        tamanhos = sorted(len(b) for b in blocos)
        self.assertEqual(tamanhos, [2, 3])
        self.assertEqual(sum(len(b) for b in blocos), 5)

    def test_bootstrap_e_reproduzivel_com_a_mesma_semente(self):
        v = np.array(["a"] * 50 + ["b"] * 50)
        p = np.array(["a"] * 45 + ["b"] * 5 + ["b"] * 50)
        blocos = inf.indices_por_grupo([f"g{i // 2}" for i in range(100)])
        r1 = inf.bootstrap_por_grupo(v, p, blocos, ["a", "b"], 50, 42)
        r2 = inf.bootstrap_por_grupo(v, p, blocos, ["a", "b"], 50, 42)
        self.assertEqual(r1, r2)

    def test_intervalo_contem_a_estimativa_pontual(self):
        v = np.array(["a"] * 60 + ["b"] * 40)
        p = np.array(["a"] * 55 + ["b"] * 5 + ["b"] * 35 + ["a"] * 5)
        blocos = inf.indices_por_grupo([f"g{i}" for i in range(100)])
        r = inf.bootstrap_por_grupo(v, p, blocos, ["a", "b"], 200, 42)
        pontual = float((v == p).mean())
        self.assertLessEqual(r["acuracia"]["ic95_min"], pontual)
        self.assertGreaterEqual(r["acuracia"]["ic95_max"], pontual)

    def test_grupos_grandes_alargam_o_intervalo(self):
        """Duplicar cada registro num mesmo grupo não deve estreitar o IC.

        É a razão de existir do bootstrap por conglomerado: reamostrar linhas
        faria o intervalo encolher como se houvesse o dobro de informação.
        """
        v = np.array(["a"] * 50 + ["b"] * 50)
        p = np.array(["a"] * 40 + ["b"] * 10 + ["b"] * 40 + ["a"] * 10)
        sozinhos = inf.indices_por_grupo([f"g{i}" for i in range(100)])
        pares = inf.indices_por_grupo([f"g{i // 2}" for i in range(100)])
        largura = lambda r: r["acuracia"]["ic95_max"] - r["acuracia"]["ic95_min"]  # noqa: E731
        solto = largura(inf.bootstrap_por_grupo(v, p, sozinhos, ["a", "b"], 300, 42))
        agrupado = largura(inf.bootstrap_por_grupo(v, p, pares, ["a", "b"], 300, 42))
        self.assertGreater(agrupado, solto)


class TestEstimativaObservada(unittest.TestCase):
    """A estimativa observada e a media do bootstrap sao grandezas distintas."""

    def _dados(self):
        v = np.array(["a"] * 60 + ["b"] * 40)
        p = np.array(["a"] * 55 + ["b"] * 5 + ["b"] * 35 + ["a"] * 5)
        blocos = inf.indices_por_grupo([f"g{i}" for i in range(100)])
        return v, p, blocos

    def test_observado_bate_com_o_calculo_direto(self):
        from sklearn.metrics import f1_score
        v, p, blocos = self._dados()
        r = inf.bootstrap_por_grupo(v, p, blocos, ["a", "b"], 50, 42)
        self.assertAlmostEqual(r["observado"]["acuracia"],
                               round(float((v == p).mean()), 4), places=4)
        esperado = f1_score(v, p, labels=["a", "b"], average="macro",
                            zero_division=0)
        self.assertAlmostEqual(r["observado"]["macro_f1"], round(esperado, 4),
                               places=4)

    def test_observado_nao_depende_do_numero_de_repeticoes(self):
        v, p, blocos = self._dados()
        poucas = inf.bootstrap_por_grupo(v, p, blocos, ["a", "b"], 30, 42)
        muitas = inf.bootstrap_por_grupo(v, p, blocos, ["a", "b"], 300, 42)
        self.assertEqual(poucas["observado"], muitas["observado"])

    def test_media_do_bootstrap_nao_e_a_estimativa_observada(self):
        """Confundir as duas produziu 0,6664 onde o retreino media 0,6684."""
        v, p, blocos = self._dados()
        r = inf.bootstrap_por_grupo(v, p, blocos, ["a", "b"], 400, 42)
        self.assertIn("media", r["macro_f1"])
        self.assertIn("macro_f1", r["observado"])
        self.assertIsNot(r["macro_f1"]["media"], r["observado"]["macro_f1"])


class TestConsensoEntreModelos(unittest.TestCase):
    def _dados(self, previsoes: dict[str, list[str]]):
        chaves = [f"c{i}" for i in range(len(next(iter(previsoes.values()))))]
        return {
            "chaves": chaves,
            "modelos": sorted(previsoes),
            "previsto": {m: dict(zip(chaves, v)) for m, v in previsoes.items()},
        }

    def test_conta_unanimidade(self):
        d = self._dados({"m1": ["a", "a"], "m2": ["a", "b"], "m3": ["a", "c"]})
        r = inf.consenso_entre_modelos(d)
        self.assertEqual(r["unanimes"], 1)
        self.assertEqual(r["proporcao_unanimes"], 0.5)

    def test_desacordo_estrutural_exige_tres_categorias(self):
        d = self._dados({"m1": ["a", "a"], "m2": ["b", "b"], "m3": ["b", "c"]})
        r = inf.consenso_entre_modelos(d)
        # Primeiro registro tem duas categorias; o segundo, três.
        self.assertEqual(r["com_desacordo_estrutural"], 1)

    def test_distribuicao_soma_o_total_de_registros(self):
        d = self._dados({"m1": ["a", "a", "b"], "m2": ["a", "b", "c"],
                         "m3": ["a", "c", "c"]})
        r = inf.consenso_entre_modelos(d)
        self.assertEqual(
            sum(r["categorias_distintas_por_registro"].values()), 3)

    def test_unanimidade_zera_a_entropia(self):
        d = self._dados({"m1": ["a"], "m2": ["a"], "m3": ["a"]})
        self.assertEqual(inf.consenso_entre_modelos(d)["entropia_media_normalizada"], 0.0)


class TestContagemDeGrupos(unittest.TestCase):
    """As três contagens de grupos são coisas diferentes e não se substituem."""

    def _mapa(self, tmp: Path, pares: list[tuple[str, str]]) -> Path:
        caminho = tmp / "particoes.csv"
        linhas = ["id_sha256,grupo_sha256,dobra"]
        linhas += [f"{i},{g},1" for i, g in pares]
        caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        return caminho

    def test_conta_grupos_congelados_do_recorte(self):
        d = {"chaves": ["i1", "i2", "i3"], "grupos": ["g1", "g1", "g2"]}
        r = inf.contagem_de_grupos(d, None)
        self.assertEqual(r["grupos_congelados_no_recorte_avaliado"], 2)
        self.assertIsNone(r["grupos_no_mapa_de_particoes"])

    def test_texto_editado_funde_grupos_e_reduz_a_contagem(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            # Congelado: i1 sozinho; vivo: i1 caiu no grupo de i2.
            mapa = self._mapa(tmp, [("i1", "gA"), ("i2", "gA"), ("i3", "gB")])
            d = {"chaves": ["i1", "i2", "i3"], "grupos": ["g1", "gA", "gB"]}
            r = inf.contagem_de_grupos(d, mapa)
            self.assertEqual(r["grupos_congelados_no_recorte_avaliado"], 3)
            self.assertEqual(r["grupos_no_mapa_de_particoes"], 2)
            self.assertEqual(r["registros_com_grupo_divergente_do_congelado"], 1)


class TestMcNemar(unittest.TestCase):
    def test_modelos_identicos_nao_diferem(self):
        a = np.array([1, 0, 1, 1, 0] * 20)
        r = inf.mcnemar_par(a, a.copy())
        self.assertEqual(r["discordantes"], 0)
        self.assertEqual(r["p"], 1.0)

    def test_conta_os_discordantes_de_cada_lado(self):
        a = np.array([1, 1, 0, 0])
        b = np.array([1, 0, 1, 0])
        r = inf.mcnemar_par(a, b)
        self.assertEqual(r["so_o_primeiro_acerta"], 1)
        self.assertEqual(r["so_o_segundo_acerta"], 1)
        self.assertEqual(r["discordantes"], 2)

    def test_poucos_discordantes_usam_o_teste_exato(self):
        a = np.array([1] * 100 + [0] * 5)
        b = np.array([1] * 100 + [1] * 5)
        self.assertEqual(inf.mcnemar_par(a, b)["metodo"], "exato")

    def test_muitos_discordantes_usam_qui_quadrado(self):
        a = np.array([1] * 100 + [0] * 100)
        b = np.array([0] * 100 + [1] * 100)
        self.assertIn("qui-quadrado", inf.mcnemar_par(a, b)["metodo"])


class TestCochran(unittest.TestCase):
    def test_modelos_iguais_nao_rejeitam(self):
        linha = np.array([1, 0, 1, 1, 0] * 20, dtype=np.int8)
        q = inf.cochran_q(np.vstack([linha, linha.copy(), linha.copy()]))
        self.assertFalse(q["rejeita_igualdade"])
        self.assertEqual(q["graus_de_liberdade"], 2)

    def test_modelo_muito_pior_rejeita(self):
        bom = np.ones(200, dtype=np.int8)
        ruim = np.zeros(200, dtype=np.int8)
        q = inf.cochran_q(np.vstack([bom, bom.copy(), ruim]))
        self.assertTrue(q["rejeita_igualdade"])


if __name__ == "__main__":
    unittest.main()
