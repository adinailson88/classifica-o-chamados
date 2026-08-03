from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import gerar_particoes_canonicas as gpc  # noqa: E402


def registro(id_, titulo, historico="Cat A", m="Correto", q=""):
    return {"id": id_, "titulo": titulo, "descricao_glpi": "",
            "titulo_osm": "", "descricao_osm": "",
            "categoria_historica": historico, "conferencia_glpi": m,
            "categoria_manual": q}


def base_equilibrada(por_categoria=40, categorias=("Cat A", "Cat B")):
    """Base sem duplicatas, com folga para estratificar em cinco dobras.

    O tamanho padrao e generoso de proposito: com poucas dezenas de registros o
    `StratifiedGroupKFold` chega a deixar uma dobra sem uma das categorias, e o
    teste passaria a medir o azar do sorteio em vez da regra sob teste.
    """
    registros = []
    n = 0
    for cat in categorias:
        for i in range(por_categoria):
            n += 1
            registros.append(registro(str(n), f"chamado {cat} {i}", historico=cat))
    return registros


class TestParticoesCanonicas(unittest.TestCase):
    def test_base_equilibrada_fica_apta_para_treinar(self):
        r = gpc.montar_relatorio(base_equilibrada())
        self.assertEqual(r["status"], "apto_para_treinar")
        self.assertEqual(r["bloqueios"], [])
        self.assertEqual(r["linhas_particionadas"], 80)
        self.assertEqual(len(r["dobras"]), 5)
        self.assertEqual(sum(d["linhas"] for d in r["dobras"]), 80)

    def test_nenhum_grupo_textual_atravessa_dobras(self):
        # Cinco pares de texto idêntico: cada par tem de cair na mesma dobra.
        registros = []
        for i in range(1, 16):
            cat = "Cat A" if i % 2 else "Cat B"
            registros.append(registro(f"{i}a", f"chamado {i}", historico=cat))
            registros.append(registro(f"{i}b", f"chamado {i}", historico=cat))
        r = gpc.montar_relatorio(registros)
        self.assertEqual(r["grupos_divididos_entre_dobras"], 0)
        self.assertEqual(r["grupos_particionados"], 15)
        self.assertEqual(r["linhas_particionadas"], 30)

    def test_particionamento_e_reproduzivel_com_a_mesma_semente(self):
        registros = base_equilibrada()
        a = gpc.montar_relatorio(registros, semente=42)
        b = gpc.montar_relatorio(registros, semente=42)
        self.assertEqual(a["mapa_sha256"], b["mapa_sha256"])

    def test_semente_diferente_muda_a_particao(self):
        registros = base_equilibrada(por_categoria=60)
        a = gpc.montar_relatorio(registros, semente=42)
        b = gpc.montar_relatorio(registros, semente=7)
        self.assertNotEqual(a["mapa_sha256"], b["mapa_sha256"])

    def test_hash_do_mapa_independe_da_ordem_de_leitura(self):
        registros = base_equilibrada()
        a = gpc.montar_relatorio(registros)
        b = gpc.montar_relatorio(list(reversed(registros)))
        self.assertEqual(a["mapa_sha256"], b["mapa_sha256"])

    def test_categoria_rara_fica_fora_do_particionamento(self):
        registros = base_equilibrada()
        # "Cat Rara" tem dois grupos distintos: cabe em no máximo duas dobras.
        registros.append(registro("900", "ocorrencia rara um", historico="Cat Rara"))
        registros.append(registro("901", "ocorrencia rara dois", historico="Cat Rara"))
        r = gpc.montar_relatorio(registros)
        excluidas = {c["categoria"]: c for c in r["categorias_excluidas_por_suporte"]}
        self.assertIn("Cat Rara", excluidas)
        self.assertEqual(excluidas["Cat Rara"]["grupos_distintos"], 2)
        self.assertEqual(r["linhas_excluidas_por_suporte"], 2)
        self.assertEqual(r["categorias_na_referencia"], 3)
        self.assertEqual(r["categorias_particionadas"], 2)
        # As duas linhas raras não entram em dobra alguma.
        self.assertEqual(r["linhas_particionadas"], 80)
        self.assertEqual(len(r["_mapa"]), 80)

    def test_apos_excluir_raras_toda_categoria_tem_suporte_em_toda_dobra(self):
        registros = base_equilibrada()
        registros.append(registro("900", "ocorrencia rara", historico="Cat Rara"))
        r = gpc.montar_relatorio(registros)
        self.assertEqual(r["status"], "apto_para_treinar")
        self.assertEqual(r["categorias_sem_suporte_em_alguma_dobra"], [])
        for d in r["dobras"]:
            self.assertEqual(d["categorias_com_suporte"], 2)
            self.assertEqual(d["categorias_ausentes"], [])

    def test_minimo_de_grupos_e_configuravel(self):
        registros = base_equilibrada()
        registros += [registro(f"9{i}", f"pouco frequente {i}", historico="Cat Media")
                      for i in range(20)]
        # Com o padrão (k=5), "Cat Media" tem 20 grupos e sobrevive ao sorteio.
        padrao = gpc.montar_relatorio(registros)
        self.assertEqual(padrao["categorias_particionadas"], 3)
        self.assertEqual(padrao["linhas_excluidas_por_suporte"], 0)
        # Exigindo 25 grupos, ela sai já pelo critério aritmético.
        exigente = gpc.montar_relatorio(registros, minimo_grupos=25)
        self.assertEqual(exigente["categorias_particionadas"], 2)
        self.assertEqual(exigente["linhas_excluidas_por_suporte"], 20)

    def test_categoria_sem_suporte_no_sorteio_sai_em_rodada_seguinte(self):
        registros = base_equilibrada()
        # Seis grupos passam no critério aritmético com k=5, mas são poucos
        # demais para o sorteio cobrir as cinco dobras.
        registros += [registro(f"9{i}", f"pouco frequente {i}", historico="Cat Limite")
                      for i in range(6)]
        r = gpc.montar_relatorio(registros)
        self.assertEqual(r["linhas_excluidas_por_suporte"], 0)
        por_sorteio = {c["categoria"] for c in r["categorias_excluidas_por_sorteio"]}
        self.assertEqual(por_sorteio, {"Cat Limite"})
        self.assertEqual(r["linhas_excluidas_por_sorteio"], 6)
        self.assertEqual(r["linhas_excluidas_total"], 6)
        self.assertGreaterEqual(r["rodadas_de_exclusao"], 1)
        # O relatório converge: ninguém fica sem suporte ao final.
        self.assertEqual(r["status"], "apto_para_treinar")
        self.assertEqual(r["categorias_sem_suporte_em_alguma_dobra"], [])

    def test_registro_sem_referencia_humana_e_descartado_e_bloqueia(self):
        registros = base_equilibrada()
        registros.append(registro("999", "sem referencia", m="Errado", q=""))
        r = gpc.montar_relatorio(registros)
        self.assertEqual(r["registros_descartados"], 1)
        self.assertEqual(r["linhas_particionadas"], 80)
        self.assertIn("registros_descartados", r["bloqueios"])
        self.assertEqual(r["status"], "bloqueado")

    def test_registro_sem_id_e_descartado(self):
        registros = base_equilibrada()
        registros.append(registro("", "sem identificador"))
        r = gpc.montar_relatorio(registros)
        self.assertEqual(r["registros_descartados"], 1)

    def test_relatorio_publicavel_nao_expoe_textos_nem_ids(self):
        registros = base_equilibrada()
        registros.append(registro("2026079999", "vazamento no bloco b",
                                  historico="Cat A"))
        r = gpc.montar_relatorio(registros)
        r["gerado_em"] = "agora"
        publicavel = {k: v for k, v in r.items() if not k.startswith("_")}
        bruto = str(publicavel) + gpc.renderizar_markdown(r)
        self.assertNotIn("2026079999", bruto)
        self.assertNotIn("vazamento", bruto)

    def test_mapa_registra_a_dobra_de_cada_registro(self):
        r = gpc.montar_relatorio(base_equilibrada())
        self.assertEqual(len(r["_mapa"]), 80)
        for m in r["_mapa"]:
            self.assertIn(m["dobra"], {1, 2, 3, 4, 5})
            self.assertEqual(len(m["id_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
