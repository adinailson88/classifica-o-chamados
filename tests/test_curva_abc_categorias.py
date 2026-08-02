#!/usr/bin/env python3
"""Teste offline de src/curva_abc_categorias.py."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import curva_abc_categorias as abc  # noqa: E402


class TestClassificarABC(unittest.TestCase):
    def test_ordena_por_volume_decrescente(self):
        r = abc.classificar_abc([("b", 10), ("a", 50), ("c", 40)])
        self.assertEqual([l["categoria"] for l in r], ["a", "c", "b"])

    def test_acumulado_fecha_em_cem(self):
        r = abc.classificar_abc([("a", 50), ("b", 30), ("c", 20)])
        self.assertAlmostEqual(r[-1]["percentual_acumulado"], 100.0)

    def test_classe_a_e_o_menor_conjunto_que_cobre_o_corte(self):
        """80/20 classico: duas categorias cobrem 80%."""
        r = abc.classificar_abc([("a", 50), ("b", 30), ("c", 15), ("d", 5)])
        classes = {l["categoria"]: l["classe"] for l in r}
        # a fecha 50% (anterior 0 < 0,80 -> A); b fecha 80% (anterior 0,50 -> A)
        self.assertEqual(classes["a"], "A")
        self.assertEqual(classes["b"], "A")
        # c comeca em 0,80, que nao e < 0,80 -> B
        self.assertEqual(classes["c"], "B")
        # d comeca em 0,95, que nao e < 0,95 -> C
        self.assertEqual(classes["d"], "C")

    def test_categoria_unica_e_classe_a(self):
        r = abc.classificar_abc([("a", 7)])
        self.assertEqual(r[0]["classe"], "A")
        self.assertAlmostEqual(r[0]["percentual_acumulado"], 100.0)

    def test_empate_desempata_por_nome(self):
        r = abc.classificar_abc([("z", 10), ("a", 10)])
        self.assertEqual([l["categoria"] for l in r], ["a", "z"])

    def test_lista_vazia(self):
        self.assertEqual(abc.classificar_abc([]), [])

    def test_cortes_customizados(self):
        r = abc.classificar_abc([("a", 50), ("b", 30), ("c", 20)],
                                corte_a=0.5, corte_b=0.9)
        classes = {l["categoria"]: l["classe"] for l in r}
        self.assertEqual(classes["a"], "A")   # fecha 50%, anterior 0 < 0,5
        self.assertEqual(classes["b"], "B")   # anterior 0,50, entre os cortes
        self.assertEqual(classes["c"], "B")   # anterior 0,80, ainda < 0,90


class TestF1PorClasse(unittest.TestCase):
    def setUp(self):
        self.linhas = abc.classificar_abc([("a", 50), ("b", 30), ("c", 15), ("d", 5)])

    def test_media_simples_dentro_da_classe(self):
        f1 = {"a": 0.9, "b": 0.7, "c": 0.5, "d": 0.1}
        r = abc.f1_por_classe(self.linhas, f1)
        self.assertAlmostEqual(r["A"]["f1_macro"], 0.8)     # (0,9+0,7)/2
        self.assertAlmostEqual(r["B"]["f1_macro"], 0.5)
        self.assertAlmostEqual(r["C"]["f1_macro"], 0.1)
        self.assertAlmostEqual(r["global"]["f1_macro"], 0.55)

    def test_categoria_sem_f1_conta_como_zero(self):
        """Ausencia de predicao correta e desempenho nulo, nao dado faltante."""
        r = abc.f1_por_classe(self.linhas, {"a": 1.0, "b": 1.0})
        self.assertAlmostEqual(r["A"]["f1_macro"], 1.0)
        self.assertAlmostEqual(r["C"]["f1_macro"], 0.0)

    def test_cauda_derruba_o_global_e_nao_a_classe_a(self):
        """O nucleo do achado: zeros na cauda punem a media global."""
        linhas = abc.classificar_abc([("a", 900), ("b", 90)] +
                                     [(f"x{i}", 1) for i in range(10)])
        f1 = {"a": 0.95, "b": 0.90}
        r = abc.f1_por_classe(linhas, f1)
        self.assertGreater(r["A"]["f1_macro"], 0.9)
        self.assertLess(r["global"]["f1_macro"], 0.3)

    def test_soma_dos_suportes_bate_com_o_total(self):
        r = abc.f1_por_classe(self.linhas, {})
        soma = sum(r[c]["suporte"] for c in ("A", "B", "C"))
        self.assertEqual(soma, r["global"]["suporte"])

    def test_classe_vazia_devolve_none(self):
        linhas = abc.classificar_abc([("a", 100)])
        r = abc.f1_por_classe(linhas, {"a": 0.8})
        self.assertIsNone(r["B"]["f1_macro"])
        self.assertEqual(r["B"]["n_categorias"], 0)


class TestExtrairDoMatriz(unittest.TestCase):
    def _matriz(self):
        return {
            "categorias": ["Cat A", "Cat B", "Cat C"],
            "modelos": {
                "linear_svc": {"n": 100, "por_categoria": [
                    {"c": 0, "suporte": 60, "f1": 0.9},
                    {"c": 1, "suporte": 30, "f1": 0.5},
                    {"c": 2, "suporte": 0, "f1": 0.0}]},
                "transformer_ft": {"n": 40, "por_categoria": [
                    {"c": 0, "suporte": 25, "f1": 0.8}]},
            },
        }

    def test_suporte_vem_do_modelo_de_maior_cobertura(self):
        """Nao pode vir de modelo parcial, como o transformer_ft."""
        suportes, _ = abc.extrair_do_matriz(self._matriz())
        self.assertEqual(dict(suportes), {"Cat A": 60, "Cat B": 30})

    def test_ignora_categoria_sem_suporte(self):
        suportes, _ = abc.extrair_do_matriz(self._matriz())
        self.assertNotIn("Cat C", dict(suportes))

    def test_f1_por_modelo(self):
        _, f1 = abc.extrair_do_matriz(self._matriz())
        self.assertEqual(f1["linear_svc"]["Cat A"], 0.9)
        self.assertEqual(f1["transformer_ft"]["Cat A"], 0.8)


class TestMontar(unittest.TestCase):
    def test_estrutura_completa(self):
        matriz = {
            "categorias": ["A", "B"],
            "modelos": {"m": {"n": 10, "por_categoria": [
                {"c": 0, "suporte": 8, "f1": 0.9},
                {"c": 1, "suporte": 2, "f1": 0.1}]}},
        }
        d = abc.montar(matriz)
        self.assertEqual(d["n_categorias"], 2)
        self.assertEqual(d["total_chamados"], 10)
        self.assertIn("m", d["por_modelo"])
        self.assertEqual(d["classes"]["A"]["n_categorias"], 1)
        self.assertAlmostEqual(d["classes"]["A"]["percentual_volume"], 80.0)

    def test_cada_categoria_recebe_tipo_e_sigla(self):
        matriz = {
            "categorias": ["Manutenção Preventiva > Gerador", "Outros > Erro de chamado"],
            "modelos": {"m": {"n": 10, "por_categoria": [
                {"c": 0, "suporte": 8, "f1": 0.9},
                {"c": 1, "suporte": 2, "f1": 0.1}]}},
        }
        d = abc.montar(matriz)
        por_cat = {l["categoria"]: l for l in d["categorias"]}
        self.assertEqual(por_cat["Manutenção Preventiva > Gerador"]["sigla_tipo"], "P")
        self.assertEqual(por_cat["Outros > Erro de chamado"]["sigla_tipo"], "NM")
        self.assertIn("por_tipo", d)
        self.assertIn("tarefa_tipo", d)


CATS = [
    "Manutenção Preventiva > Ar condicionado split",   # 0  P
    "Manutenção Preventiva > Gerador",                 # 1  P
    "Climatização > Ar condicionado split",            # 2  C
    "Elétrica > Tomada",                               # 3  C
    "Outros > Erro de chamado",                        # 4  NM
]


def _matriz_com_celulas(celulas):
    """Monta matriz_confusao.json minima a partir das celulas, coerente com ela."""
    sup, prev, ok = {}, {}, {}
    for i, j, n in celulas:
        sup[i] = sup.get(i, 0) + n
        prev[j] = prev.get(j, 0) + n
        if i == j:
            ok[i] = ok.get(i, 0) + n
    por_categoria = []
    for c in sorted(set(sup) | set(prev)):
        p = ok.get(c, 0) / prev[c] if prev.get(c) else 0.0
        r = ok.get(c, 0) / sup[c] if sup.get(c) else 0.0
        f1 = 0.0 if (p + r) == 0 else 2 * p * r / (p + r)
        por_categoria.append({"c": c, "suporte": sup.get(c, 0),
                              "previstos": prev.get(c, 0), "f1": round(f1, 4)})
    return {"categorias": CATS,
            "modelos": {"m": {"n": sum(n for _, _, n in celulas),
                              "celulas": [list(t) for t in celulas],
                              "por_categoria": por_categoria}}}


class TestCurvaPorTipo(unittest.TestCase):
    def setUp(self):
        self.suportes = [(CATS[0], 80), (CATS[1], 20),
                         (CATS[2], 60), (CATS[3], 30), (CATS[4], 10)]
        self.f1 = {"m": {CATS[0]: 1.0, CATS[1]: 0.0,
                         CATS[2]: 0.8, CATS[3]: 0.4, CATS[4]: 0.2}}

    def test_separa_os_tres_tipos(self):
        r = abc.curva_por_tipo(self.suportes, self.f1)
        self.assertEqual(r["Preventiva"]["suporte"], 100)
        self.assertEqual(r["Corretiva"]["suporte"], 90)
        self.assertEqual(r["Não manutenção"]["suporte"], 10)

    def test_soma_dos_tipos_bate_com_a_base(self):
        r = abc.curva_por_tipo(self.suportes, self.f1)
        self.assertEqual(sum(t["suporte"] for t in r.values()),
                         sum(n for _, n in self.suportes))
        self.assertAlmostEqual(sum(t["percentual_da_base"] for t in r.values()), 100.0, places=2)

    def test_acumulado_e_relativo_ao_tipo_e_nao_a_base(self):
        """O nucleo do recorte: cada tipo tem sua propria classe A."""
        r = abc.curva_por_tipo(self.suportes, self.f1)
        prev = {l["categoria"]: l for l in r["Preventiva"]["categorias"]}
        self.assertAlmostEqual(prev[CATS[0]]["percentual"], 80.0)      # 80 de 100
        self.assertAlmostEqual(prev[CATS[0]]["percentual_acumulado"], 80.0)
        self.assertAlmostEqual(prev[CATS[1]]["percentual_acumulado"], 100.0)

    def test_categoria_media_pode_ser_b_no_total_e_a_no_tipo(self):
        global_ = {l["categoria"]: l["classe"]
                   for l in abc.classificar_abc(self.suportes)}
        r = abc.curva_por_tipo(self.suportes, self.f1)
        no_tipo = {l["categoria"]: l["classe"]
                   for l in r["Não manutenção"]["categorias"]}
        self.assertEqual(global_[CATS[4]], "C")   # 10 de 200, cauda do total
        self.assertEqual(no_tipo[CATS[4]], "A")   # unica do tipo, cobre 100% dele

    def test_f1_por_classe_dentro_do_tipo(self):
        r = abc.curva_por_tipo(self.suportes, self.f1)
        prev = r["Preventiva"]["por_modelo"]["m"]
        self.assertAlmostEqual(prev["A"]["f1_macro"], 1.0)      # so CATS[0]
        self.assertAlmostEqual(prev["global"]["f1_macro"], 0.5)  # (1,0 + 0,0)/2

    def test_tipo_sem_categoria_devolve_bloco_vazio(self):
        r = abc.curva_por_tipo([(CATS[3], 10)], {"m": {CATS[3]: 0.5}})
        self.assertEqual(r["Preventiva"]["n_categorias"], 0)
        self.assertEqual(r["Preventiva"]["suporte"], 0)
        self.assertEqual(r["Preventiva"]["categorias"], [])


class TestTarefaTipo(unittest.TestCase):
    def test_projeta_categorias_para_tipo_somando_celulas(self):
        """Trocar split preventivo por split de climatizacao erra o TIPO;
        trocar gerador por split preventivo acerta o tipo e erra a categoria."""
        celulas = [(0, 0, 70), (0, 2, 10), (1, 0, 20), (2, 2, 60), (3, 4, 30), (4, 4, 10)]
        r = abc.tarefa_tipo(_matriz_com_celulas(celulas))["m"]
        m = {(a, b): v for a, b, v in r["matriz"]}
        self.assertEqual(m[("Preventiva", "Preventiva")], 90)      # 70 + 20
        self.assertEqual(m[("Preventiva", "Corretiva")], 10)
        self.assertEqual(m[("Corretiva", "Corretiva")], 60)
        self.assertEqual(m[("Corretiva", "Não manutenção")], 30)

    def test_acuracia_de_tipo_e_maior_que_a_de_categoria(self):
        """Erro dentro do mesmo tipo desaparece na projecao."""
        celulas = [(0, 1, 50), (1, 0, 50)]   # 100% de erro de categoria, 0 de tipo
        r = abc.tarefa_tipo(_matriz_com_celulas(celulas))["m"]
        self.assertAlmostEqual(r["acuracia"], 1.0)

    def test_metricas_por_tipo(self):
        celulas = [(0, 0, 90), (0, 2, 10), (2, 2, 100)]
        r = abc.tarefa_tipo(_matriz_com_celulas(celulas))["m"]
        p = r["por_tipo"]["Preventiva"]
        self.assertEqual(p["suporte"], 100)
        self.assertEqual(p["previstos"], 90)
        self.assertAlmostEqual(p["precision"], 1.0)
        self.assertAlmostEqual(p["recall"], 0.9)
        c = r["por_tipo"]["Corretiva"]
        self.assertEqual(c["previstos"], 110)
        self.assertAlmostEqual(c["precision"], round(100 / 110, 4), places=3)

    def test_tipo_ausente_da_verdade_nao_entra_no_f1_macro(self):
        """Mesma regra de matriz_confusao_multimodelo: so tipo com suporte."""
        celulas = [(0, 0, 100), (2, 2, 100)]      # nenhum chamado Nao manutencao
        r = abc.tarefa_tipo(_matriz_com_celulas(celulas))["m"]
        self.assertEqual(r["por_tipo"]["Não manutenção"]["suporte"], 0)
        self.assertAlmostEqual(r["f1_macro"], 1.0)

    def test_n_preserva_o_total_de_chamados(self):
        celulas = [(0, 0, 90), (0, 2, 10), (2, 2, 100), (4, 4, 5)]
        r = abc.tarefa_tipo(_matriz_com_celulas(celulas))["m"]
        self.assertEqual(r["n"], 205)


class TestLinhasParaAba(unittest.TestCase):
    def _dados(self):
        matriz = _matriz_com_celulas([(0, 0, 80), (1, 1, 20), (2, 2, 60),
                                      (3, 3, 30), (4, 4, 10)])
        d = abc.montar(matriz)
        _s, f1 = abc.extrair_do_matriz(matriz)
        d["_f1_bruto"] = f1
        return d

    def test_cabecalho_traz_tipo_sigla_e_classe_no_tipo(self):
        cab, _ = abc.linhas_para_aba(self._dados(), ["m"])
        for coluna in ("tipo", "sigla_tipo", "classe", "classe_no_tipo"):
            self.assertIn(coluna, cab)

    def test_uma_linha_por_categoria_com_as_duas_classes(self):
        cab, linhas = abc.linhas_para_aba(self._dados(), ["m"])
        self.assertEqual(len(linhas), 5)
        i_cat, i_sig = cab.index("categoria"), cab.index("sigla_tipo")
        i_no_tipo = cab.index("classe_no_tipo")
        por_cat = {l[i_cat]: l for l in linhas}
        self.assertEqual(por_cat["Outros > Erro de chamado"][i_sig], "NM")
        self.assertEqual(por_cat["Outros > Erro de chamado"][i_no_tipo], "A")


if __name__ == "__main__":
    unittest.main()
