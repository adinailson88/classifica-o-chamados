from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import executar_rodada_canonica as erc  # noqa: E402
import retreinar_modelos_canonicos as rmc  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_retreinar_modelos_canonicos import corpus_sintetico, registro, sha  # noqa: E402


class TestHashCorpus(unittest.TestCase):
    def setUp(self):
        self.registros, self.particoes = corpus_sintetico()
        self.corpus = rmc.preparar_corpus(self.registros, self.particoes)

    def test_mesmo_corpus_produz_o_mesmo_hash(self):
        outro = rmc.preparar_corpus(self.registros, self.particoes)
        self.assertEqual(erc.hash_corpus(self.corpus), erc.hash_corpus(outro))

    def test_hash_independe_da_ordem_de_leitura(self):
        invertido = rmc.preparar_corpus(list(reversed(self.registros)),
                                        self.particoes)
        self.assertEqual(erc.hash_corpus(self.corpus), erc.hash_corpus(invertido))

    def test_texto_editado_muda_o_hash(self):
        editados = [dict(r) for r in self.registros]
        editados[0]["titulo"] += " observacao acrescentada"
        self.assertNotEqual(erc.hash_corpus(self.corpus),
                            erc.hash_corpus(rmc.preparar_corpus(editados,
                                                                self.particoes)))

    def test_referencia_alterada_muda_o_hash(self):
        editados = [dict(r) for r in self.registros]
        editados[0]["conferencia_glpi"] = "Errado"
        editados[0]["categoria_manual"] = "Cat Hidraulica"
        self.assertNotEqual(erc.hash_corpus(self.corpus),
                            erc.hash_corpus(rmc.preparar_corpus(editados,
                                                                self.particoes)))

    def test_registro_a_mais_muda_o_hash(self):
        registros = list(self.registros)
        particoes = dict(self.particoes)
        registros.append(registro("9001", "chamado extra do corpus"))
        particoes[sha("9001")] = 1
        self.assertNotEqual(erc.hash_corpus(self.corpus),
                            erc.hash_corpus(rmc.preparar_corpus(registros,
                                                                particoes)))


class TestCarimbo(unittest.TestCase):
    def setUp(self):
        registros, particoes = corpus_sintetico()
        self.corpus = rmc.preparar_corpus(registros, particoes)

    def test_carimbo_marca_todos_os_relatorios_igualmente(self):
        a = erc.carimbar({}, "abc123", "agora", self.corpus)
        b = erc.carimbar({}, "abc123", "agora", self.corpus)
        self.assertEqual(a["hash_corpus"], b["hash_corpus"])
        self.assertEqual(a["gerado_em"], b["gerado_em"])
        self.assertTrue(a["rodada_canonica"])
        self.assertEqual(a["linhas_com_texto_alterado_apos_o_congelamento"], 0)

    def test_publicavel_remove_campos_internos(self):
        r = {"publico": 1, "_interno": 2}
        self.assertEqual(erc.publicavel(r), {"publico": 1})


if __name__ == "__main__":
    unittest.main()
