from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import comparar_regras_modelos as crm  # noqa: E402

GERADOR = "Manutenção Preventiva > Gerador"
SPLIT = "Manutenção Preventiva > Ar condicionado split"
ELETRICA = "Elétrica > Tomada"


def cenario():
    """Quatro registros: regra corrige, regra estraga, regra se abstém, ruído."""
    referencia = {"a": GERADOR, "b": SPLIT, "c": ELETRICA, "d": GERADOR}
    textos = {
        "a": "Preventiva mensal do gerador",     # regra acerta, modelo errava
        "b": "Preventiva mensal do gerador",     # regra erra, modelo acertava
        "c": "Tomada queimada na sala 10",       # regra se abstém
        "d": "Preventiva mensal do gerador",     # regra e modelo concordam
    }
    predicoes = {"a": SPLIT, "b": SPLIT, "c": ELETRICA, "d": GERADOR}
    return referencia, textos, predicoes


class TestCompararRegrasModelos(unittest.TestCase):
    def setUp(self):
        self.referencia, self.textos, self.predicoes = cenario()
        self.chaves = sorted(self.referencia)
        self.permitidas = set(self.referencia.values())

    def test_regra_so_substitui_onde_dispara(self):
        r = crm.comparar(self.chaves, self.referencia, self.textos,
                         self.predicoes, self.permitidas)
        self.assertEqual(r["regra"]["disparos"], 3)
        self.assertEqual(r["regra"]["cobertura"], 0.75)

    def test_conflitos_separam_quem_acerta(self):
        r = crm.comparar(self.chaves, self.referencia, self.textos,
                         self.predicoes, self.permitidas)
        c = r["regra"]
        # 'a' e 'b' divergem do modelo; em 'a' a regra acerta, em 'b' o modelo.
        self.assertEqual(c["conflitos_com_o_modelo"], 2)
        self.assertEqual(c["conflitos_em_que_a_regra_acerta"], 1)
        self.assertEqual(c["conflitos_em_que_o_modelo_acerta"], 1)
        self.assertEqual(c["conflitos_em_que_ambos_erram"], 0)

    def test_denominador_e_identico_nas_duas_configuracoes(self):
        r = crm.comparar(self.chaves, self.referencia, self.textos,
                         self.predicoes, self.permitidas)
        self.assertEqual(r["global"]["modelo_puro"]["n"],
                         r["global"]["hibrido"]["n"])
        self.assertEqual(r["preventivos"]["modelo_puro"]["n"],
                         r["preventivos"]["hibrido"]["n"])

    def test_recorte_preventivo_usa_a_referencia_e_nao_a_predicao(self):
        r = crm.comparar(self.chaves, self.referencia, self.textos,
                         self.predicoes, self.permitidas)
        # a, b e d têm referência preventiva; c é elétrica corretiva.
        self.assertEqual(r["preventivos"]["modelo_puro"]["n"], 3)

    def test_ganho_e_perda_sao_reportados_com_sinal(self):
        r = crm.comparar(self.chaves, self.referencia, self.textos,
                         self.predicoes, self.permitidas)
        g = r["global"]
        # A regra corrige 'a' e estraga 'b': três acertos em quatro nas duas
        # configurações, com delta nulo. O saldo zero é o ponto do teste.
        self.assertEqual(g["modelo_puro"]["acuracia"], 0.75)
        self.assertEqual(g["hibrido"]["acuracia"], 0.75)
        self.assertEqual(g["delta_acuracia"], 0.0)

    def test_relatorio_cobre_todos_os_modelos_e_nao_expoe_texto(self):
        rel = crm.montar_relatorio(
            self.chaves, self.referencia, self.textos,
            {"modelo_um": self.predicoes, "modelo_dois": self.predicoes})
        self.assertEqual(rel["problemas"]["modelos_comparados"], 2)
        self.assertEqual(rel["corpus"]["preventivos_na_referencia"], 3)
        rel["gerado_em"] = "agora"
        bruto = str(rel) + crm.renderizar_markdown(rel)
        self.assertNotIn("Tomada queimada", bruto)
        self.assertNotIn("sala 10", bruto)

    def test_registro_sem_texto_e_contabilizado(self):
        textos = dict(self.textos)
        textos["c"] = ""
        rel = crm.montar_relatorio(self.chaves, self.referencia, textos,
                                   {"modelo_um": self.predicoes})
        self.assertEqual(rel["problemas"]["registros_sem_texto"], 1)


class TestCarregarTextosEGrupos(unittest.TestCase):
    """Testa a recuperacao do texto vivo e do grupo textual recalculado,
    isolando o acesso a planilha via mock de `cgt.ler_registros`. Nenhuma
    planilha real e acessada.
    """

    def _registro(self, id_chamado, titulo="Preventiva mensal do gerador"):
        return {
            "id": id_chamado,
            "titulo": titulo,
            "descricao_glpi": "",
            "titulo_osm": "",
            "descricao_osm": "",
        }

    def test_id_congelado_faltante_e_reportado(self):
        chave_esperada = crm.hashlib.sha256(b"chamado-1").hexdigest()
        with mock.patch.object(crm.cgt, "ler_registros", return_value=[]):
            textos, grupos, problemas = crm.carregar_textos_e_grupos(
                sh=None, config={}, chaves_esperadas={chave_esperada})
        self.assertEqual(textos, {})
        self.assertTrue(any("sem texto na base viva" in p for p in problemas))

    def test_id_congelado_duplicado_e_bloqueado(self):
        chave_esperada = crm.hashlib.sha256(b"chamado-1").hexdigest()
        registros = [self._registro("chamado-1"), self._registro("chamado-1")]
        with mock.patch.object(crm.cgt, "ler_registros", return_value=registros):
            textos, grupos, problemas = crm.carregar_textos_e_grupos(
                sh=None, config={}, chaves_esperadas={chave_esperada})
        self.assertTrue(any("duplicado" in p for p in problemas))

    def test_linha_operacional_extra_e_ignorada(self):
        chave_esperada = crm.hashlib.sha256(b"chamado-1").hexdigest()
        registros = [
            self._registro("chamado-1"),
            self._registro("chamado-fora-do-corte", titulo="Chamado qualquer"),
        ]
        with mock.patch.object(crm.cgt, "ler_registros", return_value=registros):
            textos, grupos, problemas = crm.carregar_textos_e_grupos(
                sh=None, config={}, chaves_esperadas={chave_esperada})
        self.assertEqual(problemas, [])
        self.assertEqual(set(textos), {chave_esperada})
        self.assertEqual(set(grupos), {chave_esperada})


class TestCalcularHashCorpus(unittest.TestCase):
    """Prova que a referencia usada no fingerprint vem exclusivamente do CSV
    congelado, nunca de uma referencia derivada da planilha viva.
    """

    def test_referencia_viva_diferente_nao_altera_o_fingerprint(self):
        chaves = ["c1", "c2"]
        grupos = {"c1": "grupo-1", "c2": "grupo-2"}
        referencia_congelada = {"c1": GERADOR, "c2": SPLIT}
        impressao_original = crm.calcular_hash_corpus(
            chaves, grupos, referencia_congelada)

        # Mesmo se a planilha viva tivesse uma referencia_humana diferente
        # (o que este helper nem recebe como parametro), o fingerprint so
        # pode ser recalculado a partir da referencia CONGELADA do CSV.
        referencia_congelada_repetida = dict(referencia_congelada)
        impressao_repetida = crm.calcular_hash_corpus(
            chaves, grupos, referencia_congelada_repetida)
        self.assertEqual(impressao_original, impressao_repetida)

        referencia_alterada = {"c1": ELETRICA, "c2": SPLIT}
        impressao_alterada = crm.calcular_hash_corpus(
            chaves, grupos, referencia_alterada)
        self.assertNotEqual(impressao_original, impressao_alterada)

    def test_grupo_textual_divergente_altera_o_fingerprint(self):
        chaves = ["c1"]
        referencia = {"c1": GERADOR}
        original = crm.calcular_hash_corpus(chaves, {"c1": "grupo-A"}, referencia)
        alterado = crm.calcular_hash_corpus(chaves, {"c1": "grupo-B"}, referencia)
        self.assertNotEqual(original, alterado)


def _args(tmp_path, predicoes_path, esperado_path):
    config_path = tmp_path / "config.json"
    config_path.write_text("{}", encoding="utf-8")
    return argparse.Namespace(config=config_path, credenciais=None,
                              predicoes=predicoes_path, esperado=esperado_path)


def _nucleo_minimo():
    return {
        "schema_version": 1,
        "status": "concluido",
        "protocolo": "protocolo de teste",
        "corpus": {"registros": 4, "categorias": 3, "preventivos_na_referencia": 3},
        "regra": {"criterio": "teste"},
        "modelos": {},
        "modelos_com_ganho_de_macro_f1": [],
        "problemas": {"registros_sem_texto": 0, "modelos_comparados": 0},
    }


class TestMainVerificacao(unittest.TestCase):
    """Testa a ordem dos portoes em `main()` com mocks/dados sinteticos.
    Nenhuma planilha real e acessada e nenhum artefato canonico e escrito.
    """

    def setUp(self):
        import tempfile
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmpdir.name)
        self.addCleanup(self._tmpdir.cleanup)

        self.esperado_path = self.tmp_path / "esperado.json"
        self.predicoes_path = self.tmp_path / "predicoes.csv"
        self.esperado_path.write_text(
            json.dumps(_nucleo_minimo()), encoding="utf-8")
        self.predicoes_path.write_text("id_sha256,referencia_humana,dobra,modelo,previsto\n",
                                       encoding="utf-8")
        self.args = _args(self.tmp_path, self.predicoes_path, self.esperado_path)

    def _sha_side_effect(self, esperado_ok, predicoes_ok):
        def _f(caminho):
            if caminho == self.esperado_path:
                return (crm.RESULTADO_SHA256_ESPERADO if esperado_ok
                        else "0" * 64)
            if caminho == self.predicoes_path:
                return (crm.PREDICOES_SHA256_ESPERADO if predicoes_ok
                        else "0" * 64)
            raise AssertionError(f"caminho inesperado: {caminho}")
        return _f

    def test_a_predicoes_com_fingerprint_divergente_bloqueia_antes_da_planilha(self):
        with (mock.patch.object(crm, "parse_args", return_value=self.args),
              mock.patch.object(crm.vac, "sha256_lf_normalizado",
                                side_effect=self._sha_side_effect(True, False)),
              mock.patch.object(crm.pl, "abrir_planilha") as abrir):
            resultado = crm.main()
        self.assertEqual(resultado, 2)
        abrir.assert_not_called()

    def test_b_resultado_congelado_com_fingerprint_divergente_bloqueia_antes_da_planilha(self):
        with (mock.patch.object(crm, "parse_args", return_value=self.args),
              mock.patch.object(crm.vac, "sha256_lf_normalizado",
                                side_effect=self._sha_side_effect(False, True)),
              mock.patch.object(crm.pl, "abrir_planilha") as abrir):
            resultado = crm.main()
        self.assertEqual(resultado, 2)
        abrir.assert_not_called()

    def test_c_regras_preventivas_divergente_bloqueia_antes_da_planilha(self):
        with (mock.patch.object(crm, "parse_args", return_value=self.args),
              mock.patch.object(crm.vac, "sha256_lf_normalizado",
                                side_effect=self._sha_side_effect(True, True)),
              mock.patch.object(crm, "carregar_predicoes",
                                return_value={"referencia": {}, "dobra": {},
                                              "por_modelo": {}}),
              mock.patch.object(crm, "validar_estrutura_predicoes",
                                return_value=[]),
              mock.patch.object(crm, "git_blob_sha1_lf", return_value="0" * 40),
              mock.patch.object(crm.pl, "abrir_planilha") as abrir):
            resultado = crm.main()
        self.assertEqual(resultado, 2)
        abrir.assert_not_called()

    def test_h_texto_grupo_divergente_bloqueia_antes_de_montar_relatorio(self):
        chaves = {"c1": GERADOR}
        with (mock.patch.object(crm, "parse_args", return_value=self.args),
              mock.patch.object(crm.vac, "sha256_lf_normalizado",
                                side_effect=self._sha_side_effect(True, True)),
              mock.patch.object(crm, "carregar_predicoes",
                                return_value={"referencia": chaves, "dobra": {"c1": 1},
                                              "por_modelo": {"modelo_um": {"c1": GERADOR}}}),
              mock.patch.object(crm, "validar_estrutura_predicoes",
                                return_value=[]),
              mock.patch.object(crm, "git_blob_sha1_lf",
                                return_value=crm.REGRAS_PREVENTIVAS_BLOB_SHA1_ESPERADO),
              mock.patch.object(crm.pl, "id_planilha", return_value="fake-id"),
              mock.patch.object(crm.pl, "abrir_planilha", return_value=object()),
              mock.patch.object(crm, "carregar_textos_e_grupos",
                                return_value=({"c1": "texto"}, {"c1": "grupo-sintetico"}, [])),
              mock.patch.object(crm, "montar_relatorio") as montar):
            resultado = crm.main()
        self.assertEqual(resultado, 2)
        montar.assert_not_called()

    def test_i_caminho_feliz_retorna_0_e_nao_escreve_artefato(self):
        chaves = {"c1": GERADOR}
        nucleo_congelado = _nucleo_minimo()
        relatorio_atual = dict(nucleo_congelado)
        bytes_antes = self.esperado_path.read_bytes()
        with (mock.patch.object(crm, "parse_args", return_value=self.args),
              mock.patch.object(crm.vac, "sha256_lf_normalizado",
                                side_effect=self._sha_side_effect(True, True)),
              mock.patch.object(crm, "carregar_predicoes",
                                return_value={"referencia": chaves, "dobra": {"c1": 1},
                                              "por_modelo": {"modelo_um": {"c1": GERADOR}}}),
              mock.patch.object(crm, "validar_estrutura_predicoes",
                                return_value=[]),
              mock.patch.object(crm, "git_blob_sha1_lf",
                                return_value=crm.REGRAS_PREVENTIVAS_BLOB_SHA1_ESPERADO),
              mock.patch.object(crm.pl, "id_planilha", return_value="fake-id"),
              mock.patch.object(crm.pl, "abrir_planilha", return_value=object()),
              mock.patch.object(crm, "carregar_textos_e_grupos",
                                return_value=({"c1": "texto"}, {"c1": "grupo-sintetico"}, [])),
              mock.patch.object(crm, "calcular_hash_corpus",
                                return_value=crm.HASH_CORPUS_ESPERADO),
              mock.patch.object(crm, "montar_relatorio",
                                return_value=relatorio_atual) as montar,
              mock.patch.object(crm, "renderizar_markdown", return_value="")):
            resultado = crm.main()
        self.assertEqual(resultado, 0)
        montar.assert_called_once()
        self.assertEqual(self.esperado_path.read_bytes(), bytes_antes)
        self.assertFalse((self.tmp_path / "regras_versus_modelos.json").exists())
        self.assertFalse((self.tmp_path / "REGRAS_VERSUS_MODELOS.md").exists())

    def test_j_resultado_cientifico_divergente_retorna_2_sem_escrita(self):
        chaves = {"c1": GERADOR}
        relatorio_divergente = _nucleo_minimo()
        relatorio_divergente["status"] = "divergente"
        bytes_antes = self.esperado_path.read_bytes()
        with (mock.patch.object(crm, "parse_args", return_value=self.args),
              mock.patch.object(crm.vac, "sha256_lf_normalizado",
                                side_effect=self._sha_side_effect(True, True)),
              mock.patch.object(crm, "carregar_predicoes",
                                return_value={"referencia": chaves, "dobra": {"c1": 1},
                                              "por_modelo": {"modelo_um": {"c1": GERADOR}}}),
              mock.patch.object(crm, "validar_estrutura_predicoes",
                                return_value=[]),
              mock.patch.object(crm, "git_blob_sha1_lf",
                                return_value=crm.REGRAS_PREVENTIVAS_BLOB_SHA1_ESPERADO),
              mock.patch.object(crm.pl, "id_planilha", return_value="fake-id"),
              mock.patch.object(crm.pl, "abrir_planilha", return_value=object()),
              mock.patch.object(crm, "carregar_textos_e_grupos",
                                return_value=({"c1": "texto"}, {"c1": "grupo-sintetico"}, [])),
              mock.patch.object(crm, "calcular_hash_corpus",
                                return_value=crm.HASH_CORPUS_ESPERADO),
              mock.patch.object(crm, "montar_relatorio",
                                return_value=relatorio_divergente)):
            resultado = crm.main()
        self.assertEqual(resultado, 2)
        self.assertEqual(self.esperado_path.read_bytes(), bytes_antes)


class TestNucleoCientifico(unittest.TestCase):
    def test_ignora_metadados_de_proveniencia(self):
        relatorio = _nucleo_minimo()
        relatorio["gerado_em"] = "2026-01-01T00:00:00-03:00"
        relatorio["script_origem"] = "src/comparar_regras_modelos.py"
        nucleo = crm.nucleo_cientifico(relatorio)
        self.assertNotIn("gerado_em", nucleo)
        self.assertNotIn("script_origem", nucleo)
        self.assertEqual(set(nucleo), set(crm.NUCLEO_CIENTIFICO_CHAVES))


if __name__ == "__main__":
    unittest.main()
