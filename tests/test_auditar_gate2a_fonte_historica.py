from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import auditar_gate2a_fonte_historica as g2a  # noqa: E402
from construir_grupos_textuais import CAMPOS_TEXTUAIS, hash_grupo, normalizar_texto  # noqa: E402


def registro(id_, titulo="", descricao="", titulo_osm="", descricao_osm=""):
    return {"id": id_, "titulo": titulo, "descricao_glpi": descricao,
            "titulo_osm": titulo_osm, "descricao_osm": descricao_osm}


def id_sha(id_normalizado: str) -> str:
    return hashlib.sha256(id_normalizado.encode("utf-8")).hexdigest()


def grupo_de(titulo="", descricao="", titulo_osm="", descricao_osm=""):
    campos = {"titulo": titulo, "descricao_glpi": descricao,
              "titulo_osm": titulo_osm, "descricao_osm": descricao_osm}
    normalizados = [normalizar_texto(campos[c]) for c in CAMPOS_TEXTUAIS]
    return hash_grupo(normalizados)


class TestAuditarGate2A(unittest.TestCase):
    def test_gate_passa_quando_todos_os_grupos_batem(self):
        registros = [
            registro("1", "Lâmpada queimada", "sala 10"),
            registro("2", "Vazamento", "banheiro"),
        ]
        particoes = {
            id_sha("1"): grupo_de("Lâmpada queimada", "sala 10"),
            id_sha("2"): grupo_de("Vazamento", "banheiro"),
        }
        r = g2a.auditar(registros, particoes)
        self.assertTrue(r["gate_passed"])
        self.assertEqual(r["total_canonical_found"], 2)
        self.assertEqual(r["total_canonical_missing"], 0)
        self.assertEqual(r["total_group_match"], 2)
        self.assertEqual(r["total_group_mismatch"], 0)
        self.assertEqual(r["total_ambiguous_duplicates"], 0)

    def test_gate_falha_com_id_ausente_na_fonte(self):
        registros = [registro("1", "Lâmpada queimada", "sala 10")]
        particoes = {
            id_sha("1"): grupo_de("Lâmpada queimada", "sala 10"),
            id_sha("2"): grupo_de("Vazamento", "banheiro"),
        }
        r = g2a.auditar(registros, particoes)
        self.assertFalse(r["gate_passed"])
        self.assertEqual(r["total_canonical_missing"], 1)
        self.assertEqual(r["missing_id_sha256"], [id_sha("2")])

    def test_gate_falha_com_texto_divergente(self):
        registros = [registro("1", "Texto diferente", "sala 10")]
        particoes = {id_sha("1"): grupo_de("Lâmpada queimada", "sala 10")}
        r = g2a.auditar(registros, particoes)
        self.assertFalse(r["gate_passed"])
        self.assertEqual(r["total_group_mismatch"], 1)
        self.assertEqual(r["mismatch_id_sha256"], [id_sha("1")])

    def test_duplicata_nao_ambigua_e_aceita(self):
        registros = [
            registro("1", "Lâmpada  QUEIMADA", "sala 10"),
            registro("1", "lampada queimada", "SALA 10"),
        ]
        particoes = {id_sha("1"): grupo_de("Lâmpada queimada", "sala 10")}
        r = g2a.auditar(registros, particoes)
        self.assertEqual(r["total_duplicate_ids"], 1)
        self.assertEqual(r["total_ambiguous_duplicates"], 0)
        self.assertTrue(r["gate_passed"])

    def test_duplicata_ambigua_bloqueia_o_gate_mesmo_com_uma_versao_correta(self):
        registros = [
            registro("1", "Lâmpada queimada", "sala 10"),
            registro("1", "Texto totalmente diferente", "outro lugar"),
        ]
        particoes = {id_sha("1"): grupo_de("Lâmpada queimada", "sala 10")}
        r = g2a.auditar(registros, particoes)
        self.assertEqual(r["total_ambiguous_duplicates"], 1)
        self.assertFalse(r["gate_passed"])
        self.assertIn(id_sha("1"), r["mismatch_id_sha256"])

    def test_linhas_sem_id_sao_ignoradas(self):
        registros = [registro("", "Texto qualquer", "sala 10")]
        particoes: dict[str, str] = {}
        r = g2a.auditar(registros, particoes)
        self.assertEqual(r["total_distinct_normalized_ids"], 0)
        self.assertTrue(r["gate_passed"])

    def test_localizar_colunas_por_cabecalho_sem_acento(self):
        cabecalho = ["ID", "TITULO", "DESCRICAO GLPI", "TITULO O.S.M.", "DESCRICAO O.S.M.", "extra"]
        indices = g2a.localizar_colunas(cabecalho)
        self.assertEqual(indices["id"], 1)
        self.assertEqual(indices["titulo"], 2)
        self.assertEqual(indices["descricao_glpi"], 3)
        self.assertEqual(indices["titulo_osm"], 4)
        self.assertEqual(indices["descricao_osm"], 5)

    def test_localizar_colunas_falha_quando_falta_uma(self):
        cabecalho = ["ID", "TITULO", "DESCRICAO GLPI"]
        with self.assertRaises(RuntimeError):
            g2a.localizar_colunas(cabecalho)

    def test_montar_resultado_distingue_base_main_de_workflow_head(self):
        auditoria = g2a.auditar([], {})
        r = g2a.montar_resultado(
            auditoria,
            spreadsheet_id="SHEET_X",
            aba="ABA_X",
            base_main_sha="aaaa",
            workflow_head_sha="bbbb",
        )
        self.assertEqual(r["base_main_sha"], "aaaa")
        self.assertEqual(r["workflow_head_sha"], "bbbb")
        self.assertNotIn("main_sha", r)
        self.assertNotEqual(r["base_main_sha"], r["workflow_head_sha"])

    def test_resultado_nao_contem_campos_proibidos_de_privacidade(self):
        registros = [registro("1", "Lâmpada queimada", "sala 10")]
        particoes = {id_sha("1"): grupo_de("Lâmpada queimada", "sala 10")}
        auditoria = g2a.auditar(registros, particoes)
        r = g2a.montar_resultado(auditoria, "SHEET_X", "ABA_X", "aaaa", "bbbb")
        proibidos = {"id", "id_chamado", "titulo", "descricao", "descricao_glpi",
                     "titulo_osm", "descricao_osm"}
        self.assertFalse(proibidos & set(r))
        despejo = repr(r)
        self.assertNotIn("Lâmpada", despejo)
        self.assertNotIn("sala 10", despejo)

    def test_parse_args_aceita_spreadsheet_e_aba_como_parametros(self):
        import sys as _sys
        argv_original = _sys.argv
        try:
            _sys.argv = [
                "auditar_gate2a_fonte_historica.py",
                "--spreadsheet-id", "OUTRA_PLANILHA",
                "--aba", "OUTRA_ABA",
                "--base-main-sha", "aaaa",
                "--workflow-head-sha", "bbbb",
            ]
            args = g2a.parse_args()
        finally:
            _sys.argv = argv_original
        self.assertEqual(args.spreadsheet_id, "OUTRA_PLANILHA")
        self.assertEqual(args.aba, "OUTRA_ABA")
        self.assertEqual(args.base_main_sha, "aaaa")
        self.assertEqual(args.workflow_head_sha, "bbbb")


if __name__ == "__main__":
    unittest.main()
