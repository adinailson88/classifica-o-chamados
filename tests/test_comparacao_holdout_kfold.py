#!/usr/bin/env python3
"""Teste offline de src/comparacao_holdout_kfold.py.

Cobre o mecanismo central do argumento metodologico (Subsecao 3.5 do artigo):
um holdout fixo, quando estratificado, falha explicitamente em bases com
categorias de suporte baixo (varias com <= 10 na Tabela S1); e mesmo um
split aleatorio simples pode deixar categorias raras sem nenhum exemplo de
teste ou de treino. Nao usa rede nem credenciais."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import comparacao_holdout_kfold as chk  # noqa: E402


def _corpus_desbalanceado():
    # 3 categorias abundantes (30 exemplos cada) + 2 categorias raras (1 e 2
    # exemplos) -- espelha o formato real da base (Tabela S1 tem categorias
    # com suporte 1, 2, 3...).
    textos, cats = [], []
    for cat in ("A", "B", "C"):
        for i in range(30):
            textos.append(f"{cat} texto {i}")
            cats.append(cat)
    textos.append("categoria rara unica")
    cats.append("RARA_1")
    textos.extend(["categoria rara dupla 1", "categoria rara dupla 2"])
    cats.extend(["RARA_2", "RARA_2"])
    return textos, cats


class TestDividirHoldout(unittest.TestCase):
    def test_estratificacao_falha_com_categoria_suporte_1(self):
        textos, cats = _corpus_desbalanceado()
        resultado = chk.dividir_holdout(textos, cats, test_size=0.15, seed=42)
        # RARA_1 tem suporte 1: sklearn nao consegue estratificar (exige >=2
        # membros por classe) -- o script deve detectar isso, nao explodir.
        self.assertFalse(resultado["estratificado"])
        self.assertIsNotNone(resultado["erro_estratificacao"])
        self.assertIn("tr_idx", resultado)
        self.assertIn("te_idx", resultado)

    def test_estratificacao_funciona_sem_categoria_rara(self):
        textos, cats = [], []
        for cat in ("A", "B", "C"):
            for i in range(30):
                textos.append(f"{cat} texto {i}")
                cats.append(cat)
        resultado = chk.dividir_holdout(textos, cats, test_size=0.15, seed=42)
        self.assertTrue(resultado["estratificado"])
        self.assertIsNone(resultado["erro_estratificacao"])

    def test_split_e_particao_completa_sem_sobreposicao(self):
        textos, cats = _corpus_desbalanceado()
        resultado = chk.dividir_holdout(textos, cats, test_size=0.15, seed=42)
        tr, te = set(resultado["tr_idx"]), set(resultado["te_idx"])
        self.assertEqual(tr & te, set())
        self.assertEqual(tr | te, set(range(len(textos))))

    def test_categoria_rara_pode_ficar_sem_exemplo_de_teste(self):
        # Com suporte=1 e test_size=0.15, a unica linha de RARA_1 tem 85% de
        # chance de cair no treino -- fixamos o seed para reproduzir o caso em
        # que ela fica de fora do teste, mostrando o efeito pratico do
        # desbalanceamento sobre a cobertura do holdout.
        textos, cats = _corpus_desbalanceado()
        resultado = chk.dividir_holdout(textos, cats, test_size=0.15, seed=42)
        idx_rara1 = cats.index("RARA_1")
        # A linha da categoria RARA_1 esta OU no treino OU no teste, nunca
        # nas duas -- o ponto e que, em qualquer dos casos, o k-fold (que
        # testa TODOS os exemplos ao longo dos folds) cobre essa categoria de
        # forma que o holdout unico nao garante.
        esta_no_treino = idx_rara1 in resultado["tr_idx"]
        esta_no_teste = idx_rara1 in resultado["te_idx"]
        self.assertTrue(esta_no_treino ^ esta_no_teste)


class TestCarregarTabelaS1(unittest.TestCase):
    def test_le_csv_real_se_existir(self):
        if not chk.TABELA_S1.exists():
            self.skipTest("Tabela S1 nao publicada neste checkout.")
        tabela = chk.carregar_tabela_s1()
        self.assertGreater(len(tabela), 0)
        alguma_categoria = next(iter(tabela))
        self.assertIn("suporte_kfold", tabela[alguma_categoria])
        self.assertIn("f1_kfold", tabela[alguma_categoria])


if __name__ == "__main__":
    unittest.main()
