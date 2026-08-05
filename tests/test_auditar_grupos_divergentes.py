from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import auditar_grupos_divergentes as agd  # noqa: E402


PREVENTIVA = "Manutenção Preventiva > Reservatório"
CORRETIVA = "Hidrossanitária > Hidráulica"
OUTRA_CORRETIVA = "Elétrica > Instalações elétricas"


class TestAuditarGruposDivergentes(unittest.TestCase):
    def test_grupo_homogeneo_nao_conta_como_divergente(self):
        r = agd.auditar({"a": "g1", "b": "g1"},
                        {"a": CORRETIVA, "b": CORRETIVA})
        self.assertEqual(r["divergencia"]["grupos"], 0)
        self.assertEqual(r["divergencia"]["linhas"], 0)

    def test_divergencia_entre_tipos_e_separada_da_interna(self):
        grupos = {"a": "g1", "b": "g1", "c": "g2", "d": "g2"}
        referencias = {"a": CORRETIVA, "b": PREVENTIVA,
                       "c": CORRETIVA, "d": OUTRA_CORRETIVA}
        r = agd.auditar(grupos, referencias)
        self.assertEqual(r["divergencia"]["grupos"], 2)
        self.assertEqual(r["divergencia"]["linhas"], 4)
        self.assertEqual(r["natureza"]["grupos_entre_tipos_de_manutencao"], 1)
        self.assertEqual(r["natureza"]["linhas_entre_tipos_de_manutencao"], 2)

    def test_linha_sem_referencia_avaliada_fica_de_fora(self):
        r = agd.auditar({"a": "g1", "b": "g1", "c": "g1"},
                        {"a": CORRETIVA, "b": PREVENTIVA})
        self.assertEqual(r["cobertura"]["linhas_no_mapa_de_grupos"], 3)
        self.assertEqual(r["cobertura"]["linhas_com_referencia_avaliada"], 2)
        self.assertEqual(r["divergencia"]["linhas"], 2)

    def test_pares_sao_agregados_por_conjunto_de_categorias(self):
        grupos = {"a": "g1", "b": "g1", "c": "g2", "d": "g2"}
        referencias = {"a": CORRETIVA, "b": PREVENTIVA,
                       "c": PREVENTIVA, "d": CORRETIVA}
        r = agd.auditar(grupos, referencias)
        self.assertEqual(len(r["pares"]), 1)
        self.assertEqual(r["pares"][0]["grupos"], 2)
        self.assertEqual(r["pares"][0]["linhas"], 4)
        self.assertTrue(r["pares"][0]["entre_tipos_de_manutencao"])

    def test_markdown_nao_expoe_id_nem_texto_de_chamado(self):
        r = agd.auditar({"a": "g1", "b": "g1"},
                        {"a": CORRETIVA, "b": PREVENTIVA})
        markdown = agd.montar_markdown(r)
        self.assertIn("Grupos com referência divergente", markdown)
        self.assertNotIn("g1", markdown)
        self.assertNotIn("id_sha256", markdown)


if __name__ == "__main__":
    unittest.main()
