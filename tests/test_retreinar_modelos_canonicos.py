from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import retreinar_modelos_canonicos as rmc  # noqa: E402


def registro(id_, titulo, historico="Cat A", m="Correto", q="", descricao=""):
    return {"id": id_, "titulo": titulo, "descricao_glpi": descricao,
            "titulo_osm": "", "descricao_osm": "",
            "categoria_historica": historico, "conferencia_glpi": m,
            "categoria_manual": q}


def sha(id_):
    return hashlib.sha256(id_.encode("utf-8")).hexdigest()


# Vocabulário compartilhado pelas duas categorias. Sem ele, o corpus fica
# separável demais e todos os registros recebem a mesma confiança, o que
# impediria testar a variação do escore.
RUIDO = ("bloco a", "pavilhao central", "sala de aula", "corredor",
         "urgente hoje", "chamado reaberto", "setor administrativo")


def corpus_sintetico(por_categoria=25):
    """Duas categorias separáveis, com ruído lexical comum, em cinco dobras."""
    registros, particoes = [], {}
    n = 0
    for cat, termo in (("Cat Eletrica", "lampada queimada disjuntor tomada"),
                       ("Cat Hidraulica", "vazamento torneira esgoto caixa")):
        for i in range(por_categoria):
            n += 1
            id_ = str(n)
            texto = f"{termo} ocorrencia {i} {RUIDO[n % len(RUIDO)]}"
            registros.append(registro(id_, texto, historico=cat))
            particoes[sha(id_)] = (i % 5) + 1
    return registros, particoes


class TestRetreinoCanonico(unittest.TestCase):
    def setUp(self):
        self.registros, self.particoes = corpus_sintetico()
        self.corpus = rmc.preparar_corpus(self.registros, self.particoes)
        self.silencio = lambda _m: None

    def test_corpus_usa_apenas_registros_das_particoes(self):
        vivos = self.registros + [registro("9001", "chamado novo fora do corpus")]
        c = rmc.preparar_corpus(vivos, self.particoes)
        self.assertEqual(len(c["textos"]), 50)
        self.assertEqual(c["linhas_fora_das_particoes"], 1)
        self.assertEqual(sorted(set(c["dobras"])), [1, 2, 3, 4, 5])

    def test_detecta_texto_editado_apos_o_congelamento(self):
        import construir_grupos_textuais as cgt
        congelados = {}
        for r in self.registros:
            normalizados = [cgt.normalizar_texto(r.get(c, ""))
                            for c in cgt.CAMPOS_TEXTUAIS]
            congelados[sha(r["id"])] = cgt.hash_grupo(normalizados)
        # Sem edição, nenhuma divergência.
        limpo = rmc.preparar_corpus(self.registros, self.particoes, congelados)
        self.assertEqual(limpo["linhas_com_texto_alterado_apos_o_congelamento"], 0)
        # Um texto editado na aba viva precisa aparecer na contagem.
        editados = [dict(r) for r in self.registros]
        editados[0]["titulo"] = editados[0]["titulo"] + " observacao acrescentada"
        sujo = rmc.preparar_corpus(editados, self.particoes, congelados)
        self.assertEqual(sujo["linhas_com_texto_alterado_apos_o_congelamento"], 1)
        # O corpus continua completo: a deriva é reportada, não descartada.
        self.assertEqual(len(sujo["textos"]), len(limpo["textos"]))

    def test_sem_mapa_congelado_a_verificacao_e_omitida(self):
        c = rmc.preparar_corpus(self.registros, self.particoes)
        self.assertEqual(c["linhas_com_texto_alterado_apos_o_congelamento"], 0)

    def test_texto_junta_os_quatro_campos_na_ordem(self):
        r = registro("1", "titulo", descricao="descricao")
        self.assertEqual(rmc.montar_texto(r), "titulo\ndescricao")

    def test_predicao_out_of_fold_cobre_todo_o_corpus(self):
        r = rmc.avaliar_modelo("naive_bayes", self.corpus, self.silencio)
        self.assertEqual(r["registros_sem_predicao"], 0)
        self.assertEqual(len(r["_predicoes"]), 50)

    def test_nenhum_grupo_textual_vaza_para_o_treino(self):
        r = rmc.avaliar_modelo("naive_bayes", self.corpus, self.silencio)
        self.assertEqual(r["grupos_vazados_para_o_treino"], 0)

    def test_vazamento_de_grupo_e_detectado_e_bloqueia(self):
        # Dois registros de texto idêntico colocados em dobras diferentes:
        # partição inválida que o Passo 3 nunca produziria, mas que este passo
        # precisa recusar em vez de treinar em cima dela.
        registros, particoes = corpus_sintetico()
        registros.append(registro("900", "texto repetido", historico="Cat Eletrica"))
        registros.append(registro("901", "texto repetido", historico="Cat Eletrica"))
        particoes[sha("900")] = 1
        particoes[sha("901")] = 2
        corpus = rmc.preparar_corpus(registros, particoes)
        rel = rmc.montar_relatorio(corpus, ["naive_bayes"], registrar=self.silencio)
        self.assertEqual(rel["status"], "bloqueado")
        self.assertIn("modelos_com_vazamento_de_grupo", rel["bloqueios"])

    def test_relatorio_reune_metricas_e_ambiente(self):
        rel = rmc.montar_relatorio(self.corpus, ["naive_bayes", "linear_svc"],
                                   registrar=self.silencio)
        self.assertEqual(rel["status"], "apto_para_regras")
        self.assertEqual(len(rel["modelos"]), 2)
        self.assertIn(rel["melhor_por_macro_f1"], {"naive_bayes", "linear_svc"})
        for m in rel["modelos"]:
            # Corpus sintético é trivialmente separável; serve para verificar
            # que a métrica é calculada, não para medir qualidade de modelo.
            self.assertGreater(m["acuracia"], 0.5)
            self.assertGreaterEqual(m["tempo_treino_s"], 0.0)
        self.assertIn("sklearn", rel["ambiente"]["dependencias"])

    def test_relatorio_publicavel_nao_expoe_textos_nem_ids(self):
        registros, particoes = corpus_sintetico()
        registros.append(registro("2026079999", "vazamento no bloco b",
                                  historico="Cat Hidraulica"))
        particoes[sha("2026079999")] = 3
        corpus = rmc.preparar_corpus(registros, particoes)
        rel = rmc.montar_relatorio(corpus, ["naive_bayes"], registrar=self.silencio)
        rel["gerado_em"] = "agora"
        publicavel = {k: v for k, v in rel.items() if not k.startswith("_")}
        bruto = str(publicavel) + rmc.renderizar_markdown(rel)
        self.assertNotIn("2026079999", bruto)
        self.assertNotIn("bloco b", bruto)

    def test_predicoes_saem_com_hash_do_id_e_dobra(self):
        import csv
        import tempfile
        rel = rmc.montar_relatorio(self.corpus, ["naive_bayes"],
                                   registrar=self.silencio)
        with tempfile.TemporaryDirectory() as d:
            destino = Path(d) / "pred.csv"
            rmc.escrever_predicoes(destino, self.corpus, rel["_resultados"])
            with destino.open(encoding="utf-8") as f:
                linhas = list(csv.DictReader(f))
        self.assertEqual(len(linhas), 50)
        self.assertEqual(len(linhas[0]["id_sha256"]), 64)
        self.assertIn(int(linhas[0]["dobra"]), {1, 2, 3, 4, 5})
        self.assertEqual(linhas[0]["modelo"], "naive_bayes")

    def test_predicoes_trazem_a_confianca_do_modelo(self):
        import csv
        import tempfile
        rel = rmc.montar_relatorio(self.corpus, ["naive_bayes"],
                                   registrar=self.silencio)
        with tempfile.TemporaryDirectory() as d:
            destino = Path(d) / "pred.csv"
            rmc.escrever_predicoes(destino, self.corpus, rel["_resultados"])
            with destino.open(encoding="utf-8") as f:
                linhas = list(csv.DictReader(f))
        self.assertIn("confianca", linhas[0])
        for linha in linhas:
            confianca = float(linha["confianca"])
            self.assertGreaterEqual(confianca, 0.0)
            self.assertLessEqual(confianca, 1.0)
        # Escores constantes indicariam que o campo não veio do modelo.
        self.assertGreater(len({l["confianca"] for l in linhas}), 1)

    def test_escore_acompanha_cada_predicao(self):
        r = rmc.avaliar_modelo("naive_bayes", self.corpus, self.silencio)
        self.assertEqual(len(r["_escores"]), len(r["_predicoes"]))
        self.assertTrue(all(isinstance(e, float) for e in r["_escores"]))

    def test_registro_do_corpus_sem_rotulo_bloqueia(self):
        registros, particoes = corpus_sintetico()
        registros.append(registro("900", "sem referencia", m="Errado", q=""))
        particoes[sha("900")] = 1
        corpus = rmc.preparar_corpus(registros, particoes)
        self.assertEqual(corpus["linhas_sem_rotulo"], 1)
        rel = rmc.montar_relatorio(corpus, ["naive_bayes"], registrar=self.silencio)
        self.assertIn("linhas_do_corpus_sem_rotulo", rel["bloqueios"])


if __name__ == "__main__":
    unittest.main()
