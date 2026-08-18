from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import auditar_base_canonica as abc  # noqa: E402


def registro(id_, historico, m, q=""):
    return {"id": id_, "categoria_historica": historico,
            "conferencia_glpi": m, "categoria_manual": q}


def relatorio_congelado_sintetico():
    """Relatorio offline cujo hash bate com as constantes esperadas do gate,
    para testar o gate sem depender da base real de 14.060 linhas."""
    registros = [registro("1", "Cat A", "Correto"),
                 registro("2", "Cat B", "Errado", "Cat A")]
    return abc.auditar(registros), registros


class TestAuditoriaBaseCanonica(unittest.TestCase):
    def test_base_valida_fica_apta(self):
        r = abc.auditar([
            registro("1", "Cat A", "Correto"),
            registro("2", "Cat B", "Errado", "Cat A"),
        ])
        self.assertEqual(r["status"], "apto_para_congelar")
        self.assertEqual(r["corpus"]["referencias_validas"], 2)
        self.assertEqual(r["corpus"]["fontes"], {"glpi": 1, "manual": 1})
        self.assertEqual(r["taxonomia_historica"]["categorias"], 2)
        self.assertEqual(r["taxonomia_referencia"]["categorias"], 1)

    def test_categoria_manual_fora_da_taxonomia_bloqueia(self):
        r = abc.auditar([
            registro("1", "Cat A", "Correto"),
            registro("2", "Cat A", "Errado", "Cat Legada"),
        ])
        self.assertEqual(r["status"], "bloqueado")
        self.assertEqual(
            r["reconciliacao"]["categorias_referencia_fora_taxonomia_historica"],
            [{"categoria": "Cat Legada", "n": 1}],
        )

    def test_q_divergente_de_m_correto_bloqueia_por_conflito(self):
        r = abc.auditar([
            registro("1", "Cat A", "Correto", "Cat B"),
        ])
        self.assertEqual(r["status"], "bloqueado")
        self.assertEqual(r["problemas"]["conflitos_referencia"], 1)
        self.assertEqual(r["problemas"]["linhas_sem_referencia"], 1)

    def test_detecta_inconsistencias_sem_publicar_ids(self):
        r = abc.auditar([
            registro("1", "", "Correto"),
            registro("1", "Cat A", "talvez"),
            registro("", "Cat A", "Errado"),
        ])
        self.assertEqual(r["problemas"]["linhas_sem_id"], 1)
        self.assertEqual(r["problemas"]["ids_duplicados"], 1)
        self.assertEqual(r["problemas"]["linhas_sem_categoria_historica"], 1)
        self.assertEqual(r["problemas"]["vereditos_invalidos"], 1)
        self.assertNotIn("ids_duplicados_lista", r)
        self.assertEqual(len(r["ids_duplicados_sha256"]), 64)

    def test_hash_independe_da_ordem_das_linhas(self):
        a = registro("1", "Cat A", "Correto")
        b = registro("2", "Cat B", "Errado", "Cat A")
        self.assertEqual(
            abc.auditar([a, b])["hash_base_canonica_sha256"],
            abc.auditar([b, a])["hash_base_canonica_sha256"],
        )

    def test_markdown_nao_expoe_ids(self):
        r = abc.auditar([registro("2026079999", "Cat A", "Correto")])
        r["gerado_em"] = "agora"
        md = abc.renderizar_markdown(r)
        self.assertNotIn("2026079999", md)
        self.assertIn("apto_para_congelar", md)


class TestValidarIdentidadeCongelada(unittest.TestCase):
    def setUp(self):
        self.relatorio, _ = relatorio_congelado_sintetico()
        self.hash_real = self.relatorio["hash_base_canonica_sha256"]

    def test_identidade_correta_gate_aceita(self):
        self.assertTrue(abc.validar_identidade_congelada(
            self.relatorio, corpus_esperado=2, hash_esperado=self.hash_real))

    def test_hash_divergente_gate_bloqueia(self):
        saida = io.StringIO()
        self.assertFalse(abc.validar_identidade_congelada(
            self.relatorio, corpus_esperado=2,
            hash_esperado="hash-divergente-de-proposito", saida=saida))

    def test_n_correto_mas_hash_divergente_gate_bloqueia(self):
        # Prova que o gate nao aceita apenas por contagens baterem: dois
        # corpora podem ter o mesmo N e conteudo diferente.
        self.assertEqual(self.relatorio["corpus"]["linhas_nao_vazias"], 2)
        self.assertEqual(self.relatorio["corpus"]["ids_validos"], 2)
        self.assertEqual(self.relatorio["corpus"]["ids_unicos"], 2)
        self.assertEqual(self.relatorio["corpus"]["referencias_validas"], 2)
        self.assertFalse(abc.validar_identidade_congelada(
            self.relatorio, corpus_esperado=2,
            hash_esperado="hash-de-outro-corpus-com-mesmo-n"))

    def test_mensagem_de_erro_contem_obtido_esperado_e_explicacao(self):
        saida = io.StringIO()
        abc.validar_identidade_congelada(
            self.relatorio, corpus_esperado=2,
            hash_esperado="hash-esperado-diferente", saida=saida)
        mensagem = saida.getvalue()
        self.assertIn(self.hash_real, mensagem)
        self.assertIn("hash-esperado-diferente", mensagem)
        self.assertIn("ARTIGO_CONGELADO", mensagem)

    def test_constantes_padrao_sao_as_do_artigo_congelado(self):
        self.assertEqual(abc.CORPUS_COMPLETO_ESPERADO, 14060)
        self.assertEqual(
            abc.HASH_BASE_CANONICA_ESPERADO,
            "e10c78e4db0026cfcbfa5267ddac034a3c8d3a7a0a1d63fa0cf2ce52f165b174")


class TestGateBloqueiaMainComBaseDivergente(unittest.TestCase):
    """Reproduz main() ate o gate sem tocar Google Sheets."""

    def setUp(self):
        self.registros = [registro("1", "Cat A", "Correto"),
                          registro("2", "Cat B", "Errado", "Cat A")]
        self.tmp = Path(self.enterContext(
            __import__("tempfile").TemporaryDirectory()))
        self.config_path = self.tmp / "config.json"
        self.config_path.write_text('{"aba_principal": "teste"}', encoding="utf-8")
        self.json_path = self.tmp / "auditoria.json"
        self.md_path = self.tmp / "auditoria.md"

    def _contexto_offline(self, corpus_esperado, hash_esperado):
        argv = [
            "auditar_base_canonica.py",
            "--config", str(self.config_path),
            "--json", str(self.json_path),
            "--markdown", str(self.md_path),
        ]
        return (
            mock.patch.object(sys, "argv", argv),
            mock.patch("auditar_base_canonica.pl.abrir_planilha",
                       return_value=object()),
            mock.patch("auditar_base_canonica.pl.id_planilha",
                       return_value="planilha-teste"),
            mock.patch("auditar_base_canonica.ler_registros",
                       return_value=self.registros),
            mock.patch.object(abc, "CORPUS_COMPLETO_ESPERADO", corpus_esperado),
            mock.patch.object(abc, "HASH_BASE_CANONICA_ESPERADO", hash_esperado),
        )

    def test_identidade_divergente_retorna_nao_zero_e_nao_escreve_saidas(self):
        argv, abrir, id_pl, ler, corpus_esp, hash_esp = self._contexto_offline(
            2, "hash-divergente-de-proposito")
        with argv, abrir, id_pl, ler, corpus_esp, hash_esp:
            codigo = abc.main()

        self.assertNotEqual(codigo, 0)
        self.assertFalse(self.json_path.exists())
        self.assertFalse(self.md_path.exists())

    def test_identidade_correta_permite_main_prosseguir(self):
        hash_real = abc.auditar(self.registros)["hash_base_canonica_sha256"]
        argv, abrir, id_pl, ler, corpus_esp, hash_esp = self._contexto_offline(
            2, hash_real)
        with argv, abrir, id_pl, ler, corpus_esp, hash_esp:
            codigo = abc.main()

        self.assertEqual(codigo, 0)
        self.assertTrue(self.json_path.exists())
        self.assertTrue(self.md_path.exists())


if __name__ == "__main__":
    unittest.main()
