from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import construir_grupos_textuais as cgt  # noqa: E402


def registro(id_, titulo="", descricao="", titulo_osm="", descricao_osm="",
             historico="Cat A", m="Correto", q=""):
    return {"id": id_, "titulo": titulo, "descricao_glpi": descricao,
            "titulo_osm": titulo_osm, "descricao_osm": descricao_osm,
            "categoria_historica": historico, "conferencia_glpi": m,
            "categoria_manual": q}


class TestGruposTextuais(unittest.TestCase):
    def test_textos_identicos_apos_normalizacao_formam_um_grupo(self):
        r = cgt.agrupar([
            registro("1", "Lâmpada  QUEIMADA", "sala 10"),
            registro("2", "lampada queimada", "SALA 10"),
            registro("3", "vazamento", "banheiro"),
        ])
        self.assertEqual(r["corpus"]["grupos_textuais"], 2)
        self.assertEqual(r["corpus"]["linhas_com_duplicata"], 2)
        self.assertEqual(r["corpus"]["maior_grupo"], 2)
        self.assertEqual(r["corpus"]["grupos_unitarios"], 1)

    def test_campos_separados_nao_colidem_por_concatenacao(self):
        r = cgt.agrupar([
            registro("1", "a b", ""),
            registro("2", "a", "b"),
        ])
        self.assertEqual(r["corpus"]["grupos_textuais"], 2)

    def test_grupo_com_referencia_divergente_e_sinalizado(self):
        r = cgt.agrupar([
            registro("1", "porta emperrada", historico="Cat A", m="Correto"),
            registro("2", "porta emperrada", historico="Cat A",
                     m="Errado", q="Cat B"),
        ])
        self.assertEqual(r["rotulos_conflitantes"]["grupos_com_referencia_divergente"], 1)
        self.assertEqual(r["rotulos_conflitantes"]["linhas_afetadas"], 2)

    def test_mapa_usa_hash_do_id_e_nao_o_id(self):
        r = cgt.agrupar([registro("2026079999", "torneira pingando")])
        self.assertEqual(len(r["_mapa"]), 1)
        self.assertNotIn("2026079999", str(r["_mapa"]))
        self.assertEqual(len(r["_mapa"][0]["id_sha256"]), 64)
        self.assertEqual(len(r["_mapa"][0]["grupo_sha256"]), 64)

    def test_hash_do_mapa_independe_da_ordem_das_linhas(self):
        a = registro("1", "ar condicionado sem gelar")
        b = registro("2", "lampada queimada")
        self.assertEqual(
            cgt.agrupar([a, b])["mapa_sha256"],
            cgt.agrupar([b, a])["mapa_sha256"],
        )

    def test_grupo_maior_que_uma_dobra_bloqueia(self):
        # Cinco linhas idênticas em uma base de seis: o grupo não cabe em 1/5.
        registros = [registro(str(i), "chamado repetido") for i in range(1, 6)]
        registros.append(registro("6", "chamado unico"))
        r = cgt.montar_relatorio(registros, com_quase_duplicados=False)
        self.assertEqual(r["status"], "bloqueado")
        self.assertIn("grupos_maiores_que_uma_dobra", r["bloqueios"])

    def test_linha_sem_texto_bloqueia(self):
        r = cgt.montar_relatorio([registro("1", "algo"), registro("2")],
                                 com_quase_duplicados=False)
        self.assertEqual(r["problemas"]["linhas_sem_texto_em_todos_os_campos"], 1)
        self.assertIn("linhas_sem_texto_em_todos_os_campos", r["bloqueios"])

    def test_base_saudavel_fica_apta_para_particionar(self):
        registros = [registro(str(i), f"chamado {i}") for i in range(1, 11)]
        r = cgt.montar_relatorio(registros, com_quase_duplicados=False)
        self.assertEqual(r["status"], "apto_para_particionar")
        self.assertEqual(r["bloqueios"], [])

    def test_quase_duplicados_medem_sensibilidade_sem_agrupar(self):
        textos = {
            "g1": "troca de lampada na sala 101 do pavilhao a",
            "g2": "troca de lampada na sala 102 do pavilhao a",
            "g3": "manutencao do sistema de esgoto do restaurante universitario",
        }
        d = cgt.diagnosticar_quase_duplicados(textos, limiares=(0.5, 0.99),
                                              vizinhos=2)
        if not d["executado"]:
            self.skipTest(d["motivo"])
        self.assertEqual(d["grupos_avaliados"], 3)
        limiares = {s["limiar"]: s["grupos_com_par_acima_do_limiar"]
                    for s in d["teste_de_sensibilidade"]}
        # O par g1/g2 é quase duplicado; nada atinge 0,99 e nada é fundido.
        self.assertGreaterEqual(limiares[0.5], 2)
        self.assertEqual(limiares[0.99], 0)

    def test_detalhar_conflitos_lista_so_os_grupos_divergentes(self):
        linhas = cgt.detalhar_conflitos([
            registro("1", "porta emperrada", historico="Cat A", m="Correto"),
            registro("2", "porta emperrada", historico="Cat A",
                     m="Errado", q="Cat B"),
            registro("3", "lampada queimada", historico="Cat A", m="Correto"),
            registro("4", "lampada queimada", historico="Cat A", m="Correto"),
        ])
        self.assertEqual([l["id"] for l in linhas], ["1", "2"])
        self.assertEqual({l["referencia_humana"] for l in linhas},
                         {"Cat A", "Cat B"})
        self.assertEqual(len({l["grupo"] for l in linhas}), 1)

    def test_detalhar_conflitos_ignora_referencia_ausente(self):
        # Um único rótulo presente mais um vazio não é divergência.
        linhas = cgt.detalhar_conflitos([
            registro("1", "porta emperrada", historico="Cat A", m="Correto"),
            registro("2", "porta emperrada", historico="Cat A", m="Errado"),
        ])
        self.assertEqual(linhas, [])

    def test_detalhamento_e_o_unico_caminho_com_id_e_texto(self):
        registros = [
            registro("2026079999", "vazamento no bloco b", historico="Cat A",
                     m="Correto"),
            registro("2026078888", "vazamento no bloco b", historico="Cat A",
                     m="Errado", q="Cat B"),
        ]
        r = cgt.montar_relatorio(registros, com_quase_duplicados=False)
        publicavel = str({k: v for k, v in r.items() if not k.startswith("_")})
        self.assertNotIn("2026079999", publicavel)
        self.assertNotIn("vazamento", publicavel)
        detalhe = str(cgt.detalhar_conflitos(registros))
        self.assertIn("2026079999", detalhe)
        self.assertIn("vazamento", detalhe)

    def test_relatorio_publicavel_nao_expoe_textos_nem_ids(self):
        r = cgt.montar_relatorio(
            [registro("2026079999", "vazamento no bloco b")],
            com_quase_duplicados=False)
        r["gerado_em"] = "agora"
        publicavel = {k: v for k, v in r.items() if not k.startswith("_")}
        bruto = str(publicavel) + cgt.renderizar_markdown(r)
        self.assertNotIn("2026079999", bruto)
        self.assertNotIn("vazamento", bruto)
        self.assertIn("apto_para_particionar", bruto)


if __name__ == "__main__":
    unittest.main()
