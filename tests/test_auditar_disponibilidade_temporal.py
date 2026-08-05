from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import auditar_disponibilidade_temporal as adt  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]


class TestClassificacaoDeCampos(unittest.TestCase):
    def test_carimbo_de_execucao_nao_vira_candidato(self):
        self.assertEqual(adt.classificar("gerado_em"), "carimbo_de_execucao")
        self.assertEqual(adt.classificar("corpus.gerado_em"), "carimbo_de_execucao")

    def test_campo_de_data_do_chamado_e_candidato(self):
        for campo in ("data_abertura", "DATA DE ABERTURA", "dt_criacao",
                      "opened_at", "mes"):
            self.assertEqual(adt.classificar(campo), "candidato", campo)

    def test_campo_sem_relacao_com_tempo_e_ignorado(self):
        for campo in ("id_sha256", "grupo_sha256", "referencia_humana",
                      "confianca", "dobra"):
            self.assertEqual(adt.classificar(campo), "ignorado", campo)


class TestAuditoria(unittest.TestCase):
    def test_sem_candidato_o_veredito_bloqueia_a_avaliacao_temporal(self):
        relatorio = adt.auditar(["ID Chamado", "TÍTULO"], [])
        self.assertEqual(relatorio["veredito"], "sem_variavel_temporal")
        self.assertEqual(relatorio["candidatos"], [])
        self.assertIn("condicional", relatorio["consequencia"])

    def test_um_candidato_muda_o_veredito(self):
        relatorio = adt.auditar(["ID Chamado", "DATA DE ABERTURA"], [])
        self.assertEqual(relatorio["veredito"], "variavel_temporal_disponivel")
        self.assertEqual(relatorio["candidatos"], ["DATA DE ABERTURA"])

    def test_artefato_ausente_e_declarado_e_nao_silenciado(self):
        with tempfile.TemporaryDirectory() as tmp:
            relatorio = adt.auditar([], [Path(tmp) / "nao_existe.json"])
        self.assertEqual(relatorio["fontes_ausentes"],
                         ["AGENTS.md :: Colunas esperadas",
                          "docs/dados/nao_existe.json"])

    def test_markdown_nao_expoe_id_nem_texto_de_chamado(self):
        relatorio = adt.auditar(["ID Chamado"], [])
        markdown = adt.montar_markdown(relatorio)
        self.assertIn("sem_variavel_temporal", markdown)
        self.assertNotIn("id_sha256", markdown)


class TestContratoDeColunas(unittest.TestCase):
    def test_le_o_bloco_de_colunas_do_agents(self):
        colunas = adt.colunas_do_contrato(RAIZ / "AGENTS.md")
        self.assertIn("ID Chamado", colunas)
        self.assertIn("CATEGORIA CORRETA MANUAL", colunas)


class TestArtefatoPublicado(unittest.TestCase):
    def test_o_relatorio_versionado_mantem_o_veredito(self):
        caminho = RAIZ / "docs" / "dados" / "disponibilidade_temporal.json"
        relatorio = json.loads(caminho.read_text(encoding="utf-8"))
        self.assertEqual(relatorio["veredito"], "sem_variavel_temporal")
        self.assertEqual(relatorio["fontes_ausentes"], [])


if __name__ == "__main__":
    unittest.main()
