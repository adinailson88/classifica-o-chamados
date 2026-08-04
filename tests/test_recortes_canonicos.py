from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import recortes_canonicos as rc  # noqa: E402
import tipo_manutencao as tm  # noqa: E402

PREV = "Manutenção Preventiva > Gerador"
PREV2 = "Manutenção Preventiva > Elevador"
CORR = "Elétrica > Tomada"
NM = "Outros > Erro de chamado"


class TestClassificarABC(unittest.TestCase):
    def test_categoria_que_cruza_o_corte_fecha_a_classe(self):
        # 80 + 15 + 5: a primeira fecha A, a segunda fecha B.
        classes = rc.classificar_abc([("a", 80), ("b", 15), ("c", 5)])
        self.assertEqual(classes["A"], ["a"])
        self.assertEqual(classes["B"], ["b"])
        self.assertEqual(classes["C"], ["c"])

    def test_toda_categoria_recebe_exatamente_uma_classe(self):
        volumes = [(f"cat{i}", 100 - i) for i in range(30)]
        classes = rc.classificar_abc(volumes)
        todas = classes["A"] + classes["B"] + classes["C"]
        self.assertEqual(len(todas), 30)
        self.assertEqual(len(set(todas)), 30)

    def test_empate_de_volume_e_desempatado_por_nome(self):
        classes = rc.classificar_abc([("b", 50), ("a", 50)])
        self.assertEqual(classes["A"], ["a", "b"])


class TestTarefaDeTipo(unittest.TestCase):
    def test_erro_dentro_do_mesmo_tipo_nao_conta_como_erro_de_tipo(self):
        # Prevê a folha errada, mas o tipo continua Preventiva.
        pares = [(PREV, PREV2)] * 10
        r = rc.tarefa_de_tipo(pares)
        self.assertEqual(r["acuracia"], 1.0)

    def test_erro_entre_tipos_derruba_a_acuracia(self):
        pares = [(PREV, CORR)] * 5 + [(PREV, PREV)] * 5
        r = rc.tarefa_de_tipo(pares)
        self.assertEqual(r["acuracia"], 0.5)

    def test_confusao_registra_o_par_de_tipos(self):
        r = rc.tarefa_de_tipo([(PREV, CORR)])
        self.assertEqual(r["confusao"],
                         [{"verdade": tm.PREVENTIVA, "previsto": tm.CORRETIVA, "n": 1}])


class TestRecortePorTipo(unittest.TestCase):
    def test_conta_categorias_e_chamados_de_cada_tipo(self):
        pares = [(PREV, PREV)] * 3 + [(PREV2, PREV2)] * 2 + [(CORR, CORR)] * 4
        r = {x["tipo"]: x for x in rc.recorte_por_tipo(pares)}
        self.assertEqual(r[tm.PREVENTIVA]["categorias"], 2)
        self.assertEqual(r[tm.PREVENTIVA]["chamados"], 5)
        self.assertEqual(r[tm.CORRETIVA]["chamados"], 4)
        self.assertEqual(r[tm.NAO_MANUTENCAO]["chamados"], 0)

    def test_falso_positivo_vindo_de_fora_penaliza_o_recorte(self):
        # Um chamado corretivo previsto como preventivo é falso positivo de
        # 'Gerador'. Se o recorte descartasse os pares de fora, ele sumiria.
        so_preventivos = [(PREV, PREV)] * 9
        com_invasor = so_preventivos + [(CORR, PREV)]
        limpo = {x["tipo"]: x for x in rc.recorte_por_tipo(so_preventivos)}
        sujo = {x["tipo"]: x for x in rc.recorte_por_tipo(com_invasor)}
        self.assertEqual(limpo[tm.PREVENTIVA]["macro_f1"], 1.0)
        self.assertLess(sujo[tm.PREVENTIVA]["macro_f1"], 1.0)
        # A acurácia do recorte não muda: ela olha só os chamados do tipo.
        self.assertEqual(sujo[tm.PREVENTIVA]["acuracia"], 1.0)


class TestCurvaABC(unittest.TestCase):
    def test_classes_cobrem_todos_os_chamados(self):
        pares = [(PREV, PREV)] * 80 + [(CORR, CORR)] * 15 + [(NM, NM)] * 5
        classes = rc.curva_abc(pares)
        self.assertEqual(sum(c["chamados"] for c in classes), 100)
        self.assertAlmostEqual(sum(c["proporcao_do_volume"] for c in classes),
                               1.0, places=3)

    def test_recorte_por_tipo_usa_o_volume_do_proprio_tipo(self):
        pares = ([(PREV, PREV)] * 80 + [(PREV2, PREV2)] * 20
                 + [(CORR, CORR)] * 1000)
        global_ = rc.curva_abc(pares)
        dentro = rc.curva_abc(pares, restrito_a=tm.PREVENTIVA)
        # No global, as preventivas são cauda; dentro do tipo, 'Gerador' é classe A.
        self.assertEqual(sum(c["chamados"] for c in dentro), 100)
        self.assertNotEqual([c["categorias"] for c in global_],
                            [c["categorias"] for c in dentro])


class TestRelatorio(unittest.TestCase):
    def test_reune_os_tres_recortes_por_modelo(self):
        pares = [(PREV, PREV)] * 10 + [(CORR, CORR)] * 10
        r = rc.montar_relatorio({"m1": pares, "m2": pares})
        self.assertEqual(len(r["modelos"]), 2)
        for m in r["modelos"]:
            self.assertIn("por_tipo", m)
            self.assertIn("tarefa_tipo", m)
            self.assertIn("curva_abc", m)
            self.assertEqual(len(m["curva_abc_por_tipo"]), len(tm.TIPOS))

    def test_carrega_o_hash_do_manifesto(self):
        r = rc.montar_relatorio({"m1": [(PREV, PREV)]},
                                {"hash_corpus": "abc123"})
        self.assertEqual(r["hash_corpus"], "abc123")

    def test_markdown_nao_expoe_texto_de_chamado(self):
        r = rc.montar_relatorio({"m1": [(PREV, PREV)]})
        r["gerado_em"] = "agora"
        md = rc.renderizar_markdown(r)
        self.assertIn("Tarefa de tipo", md)
        self.assertIn("Curva ABC", md)


if __name__ == "__main__":
    unittest.main()
