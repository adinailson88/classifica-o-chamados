from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import auditar_base_canonica as abc  # noqa: E402


def registro(id_, historico, m, q=""):
    return {"id": id_, "categoria_historica": historico,
            "conferencia_glpi": m, "categoria_manual": q}


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


if __name__ == "__main__":
    unittest.main()
