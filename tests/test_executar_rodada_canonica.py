from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path
from unittest import mock

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


class TestValidarHashCorpus(unittest.TestCase):
    def test_hash_igual_ao_esperado_libera_a_rodada(self):
        self.assertTrue(erc.validar_hash_corpus("abc123", "abc123"))

    def test_hash_divergente_bloqueia_e_relata_ambos_os_hashes(self):
        saida = io.StringIO()
        self.assertFalse(erc.validar_hash_corpus("obtido999", "esperado111",
                                                  saida=saida))
        mensagem = saida.getvalue()
        self.assertIn("obtido999", mensagem)
        self.assertIn("esperado111", mensagem)

    def test_constante_padrao_e_o_hash_oficial_do_artigo_congelado(self):
        self.assertEqual(
            erc.HASH_CORPUS_ESPERADO,
            "1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a")


class TestGateBloqueiaRodadaComCorpusDivergente(unittest.TestCase):
    """Reproduz main() ate o gate sem tocar Google Sheets nem treinar nada."""

    def setUp(self):
        self.registros, self.particoes = corpus_sintetico()
        self.tmp = Path(self.enterContext(
            __import__("tempfile").TemporaryDirectory()))
        self.config_path = self.tmp / "config.json"
        self.config_path.write_text('{"aba_principal": "teste"}', encoding="utf-8")
        self.particoes_path = self.tmp / "particoes.csv"
        self.particoes_path.write_text("id_sha256,dobra\n", encoding="utf-8")
        self.grupos_ausentes = self.tmp / "grupos_inexistentes.csv"

    def _contexto_offline(self, hash_esperado):
        argv = [
            "executar_rodada_canonica.py",
            "--config", str(self.config_path),
            "--particoes", str(self.particoes_path),
            "--grupos-congelados", str(self.grupos_ausentes),
        ]
        return (
            mock.patch.object(sys, "argv", argv),
            mock.patch("executar_rodada_canonica.pl.abrir_planilha",
                       return_value=object()),
            mock.patch("executar_rodada_canonica.pl.id_planilha",
                       return_value="planilha-teste"),
            mock.patch("executar_rodada_canonica.cgt.ler_registros",
                       return_value=self.registros),
            mock.patch("executar_rodada_canonica.rmc.carregar_particoes",
                       return_value=self.particoes),
            mock.patch.object(erc, "HASH_CORPUS_ESPERADO", hash_esperado),
        )

    def test_hash_divergente_interrompe_antes_de_qualquer_calculo(self):
        argv, abrir, id_pl, ler, part, hash_esp = self._contexto_offline(
            "hash-divergente-de-proposito")
        with argv, abrir, id_pl, ler, part, hash_esp, \
             mock.patch("executar_rodada_canonica.rmc.montar_relatorio") as m_treino, \
             mock.patch("executar_rodada_canonica.crm.montar_relatorio") as m_regras, \
             mock.patch("executar_rodada_canonica.cal.montar_relatorio") as m_calib, \
             mock.patch("executar_rodada_canonica.rec.montar_relatorio") as m_recortes, \
             mock.patch("executar_rodada_canonica.chi.montar_relatorio") as m_historico, \
             mock.patch("executar_rodada_canonica.ccc.montar_relatorio") as m_custo, \
             mock.patch("executar_rodada_canonica.gravar") as m_gravar:
            codigo = erc.main()

        self.assertNotEqual(codigo, 0)
        for mock_calculo in (m_treino, m_regras, m_calib, m_recortes,
                             m_historico, m_custo):
            mock_calculo.assert_not_called()
        m_gravar.assert_not_called()

    def test_hash_igual_permite_a_rodada_prosseguir(self):
        hash_real = erc.hash_corpus(
            rmc.preparar_corpus(self.registros, self.particoes))
        marcador = RuntimeError("prosseguiu-ate-o-passo-4")
        argv, abrir, id_pl, ler, part, hash_esp = self._contexto_offline(
            hash_real)

        with argv, abrir, id_pl, ler, part, hash_esp, \
             mock.patch("executar_rodada_canonica.rmc.montar_relatorio",
                        side_effect=marcador) as m_treino:
            with self.assertRaises(RuntimeError):
                erc.main()

        m_treino.assert_called_once()


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
