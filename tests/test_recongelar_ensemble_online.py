from __future__ import annotations

import hashlib
import inspect
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import recongelar_ensemble_online as rec  # noqa: E402


def sha(id_: str) -> str:
    return hashlib.sha256(id_.encode("utf-8")).hexdigest()


def raw_online(id_, titulo, hist="Cat A", m="Correto", q="", descricao=""):
    """Formato devolvido por `construir_grupos_textuais.ler_registros`."""
    return {
        "id": id_,
        "titulo": titulo,
        "descricao_glpi": descricao,
        "titulo_osm": "",
        "descricao_osm": "",
        "categoria_historica": hist,
        "conferencia_glpi": m,
        "categoria_manual": q,
    }


def particao(grupo, fold):
    return {"grupo_sha256": grupo, "outer_fold": fold}


def alvo_registro(id_sha256, grupo, fold, hist, ref):
    return {
        "id_sha256": id_sha256,
        "grupo_sha256": grupo,
        "outer_fold": fold,
        "categoria_historica": hist,
        "referencia_humana": ref,
        "historico_no_espaco_de_classes": True,
        "alvo_inadequacao": int(hist != ref),
    }


class TestMontarBaseAtual(unittest.TestCase):
    def test_ignora_registros_fora_das_particoes_preservadas(self):
        particoes = {sha("1"): particao("gA", 1)}
        online = [raw_online("1", "titulo um"), raw_online("2", "titulo fora")]
        info = rec.montar_base_atual(online, particoes)
        self.assertEqual(set(info["base"]), {sha("1")})
        self.assertEqual(info["faltantes_no_online"], [])

    def test_id_preservado_ausente_no_online_vira_faltante(self):
        particoes = {sha("1"): particao("gA", 1), sha("2"): particao("gB", 2)}
        online = [raw_online("1", "titulo um")]
        info = rec.montar_base_atual(online, particoes)
        self.assertEqual(info["faltantes_no_online"], [sha("2")])

    def test_outer_fold_e_o_preservado_nao_recalculado(self):
        particoes = {sha("1"): particao("gA", 3)}
        online = [raw_online("1", "titulo um")]
        info = rec.montar_base_atual(online, particoes)
        self.assertEqual(info["base"][sha("1")]["outer_fold"], 3)

    def test_grupo_atual_recalculado_do_texto_online(self):
        particoes = {sha("1"): particao("grupo-congelado-antigo", 1)}
        online = [raw_online("1", "texto totalmente diferente do congelado")]
        info = rec.montar_base_atual(online, particoes)
        grupo_atual = info["base"][sha("1")]["grupo_atual"]
        self.assertNotEqual(grupo_atual, "grupo-congelado-antigo")


class TestGruposNaoCruzamDobras(unittest.TestCase):
    def test_sem_violacao_quando_cada_grupo_fica_em_uma_dobra(self):
        base = {
            "a": {"grupo_atual": "g1", "outer_fold": 1},
            "b": {"grupo_atual": "g1", "outer_fold": 1},
            "c": {"grupo_atual": "g2", "outer_fold": 2},
        }
        r = rec.validar_grupos_nao_cruzam_dobras(base)
        self.assertEqual(r["grupos_cruzando_dobras"], 0)
        self.assertEqual(r["total_grupos_atuais_distintos"], 2)

    def test_bloqueia_quando_grupo_atual_aparece_em_duas_dobras(self):
        # Dois IDs cujo texto ATUAL colapsou no mesmo grupo, mas cujo fold
        # foi preservado de uma epoca em que os textos eram distintos.
        base = {
            "a": {"grupo_atual": "g-colidido", "outer_fold": 1},
            "b": {"grupo_atual": "g-colidido", "outer_fold": 2},
        }
        r = rec.validar_grupos_nao_cruzam_dobras(base)
        self.assertEqual(r["grupos_cruzando_dobras"], 1)
        self.assertIn("g-colidido", r["amostra_grupos_cruzando_dobras"])


class TestHRYPreservados(unittest.TestCase):
    def test_sem_divergencia_quando_tudo_bate(self):
        base = {"a": {"categoria_historica_atual": "Cat A",
                      "referencia_humana_atual": "Cat A"}}
        congelado = {"a": alvo_registro("a", "g", 1, "Cat A", "Cat A")}
        r = rec.validar_h_r_y_preservados(base, congelado)
        self.assertEqual((r["h_divergentes"], r["r_divergentes"], r["y_divergentes"]),
                         (0, 0, 0))

    def test_h_divergente_e_detectado(self):
        base = {"a": {"categoria_historica_atual": "Cat B",
                      "referencia_humana_atual": "Cat A"}}
        congelado = {"a": alvo_registro("a", "g", 1, "Cat A", "Cat A")}
        r = rec.validar_h_r_y_preservados(base, congelado)
        self.assertEqual(r["h_divergentes"], 1)
        self.assertEqual(r["amostra_h_divergentes"], ["a"])

    def test_r_divergente_e_detectado(self):
        base = {"a": {"categoria_historica_atual": "Cat A",
                      "referencia_humana_atual": "Cat B"}}
        congelado = {"a": alvo_registro("a", "g", 1, "Cat A", "Cat A")}
        r = rec.validar_h_r_y_preservados(base, congelado)
        self.assertEqual(r["r_divergentes"], 1)

    def test_y_divergente_e_detectado_mesmo_com_h_e_r_iguais(self):
        # Y guardado no congelamento anterior esta inconsistente com o
        # proprio H/R congelados (fixture corrompida de proposito): a
        # checagem de Y precisa detectar isso por si so, independente de H
        # e R baterem individualmente.
        base = {"a": {"categoria_historica_atual": "Cat A",
                      "referencia_humana_atual": "Cat A"}}
        congelado_inconsistente = {
            "a": {**alvo_registro("a", "g", 1, "Cat A", "Cat A"), "alvo_inadequacao": 1}
        }
        r = rec.validar_h_r_y_preservados(base, congelado_inconsistente)
        self.assertEqual(r["y_divergentes"], 1)
        self.assertEqual(r["h_divergentes"], 0)
        self.assertEqual(r["r_divergentes"], 0)


class TestMontarDiagnostico(unittest.TestCase):
    def _base_info_ok(self):
        particoes = {sha("1"): particao("g1", 1), sha("2"): particao("g2", 2)}
        online = [raw_online("1", "texto um", hist="Cat A", m="Correto"),
                 raw_online("2", "texto dois", hist="Cat B", m="Correto")]
        info = rec.montar_base_atual(online, particoes)
        congelado = {
            sha("1"): alvo_registro(sha("1"), "g1", 1, "Cat A", "Cat A"),
            sha("2"): alvo_registro(sha("2"), "g2", 2, "Cat B", "Cat B"),
        }
        return info, congelado, particoes

    def test_apto_quando_tudo_preservado(self):
        info, congelado, particoes = self._base_info_ok()
        d = rec.montar_diagnostico(info, congelado, particoes)
        self.assertEqual(d["status"], "apto_para_baseline")
        self.assertEqual(d["bloqueios"], [])

    def test_total_esperado_bloqueia_denominador_divergente(self):
        info, congelado, particoes = self._base_info_ok()
        d = rec.montar_diagnostico(info, congelado, particoes, total_esperado=99999)
        self.assertIn("total_ids_particoes_divergente_do_denominador_esperado", d["bloqueios"])
        self.assertEqual(d["status"], "bloqueado")

    def test_bloqueia_por_id_faltante_no_online(self):
        particoes = {sha("1"): particao("g1", 1), sha("2"): particao("g2", 2)}
        online = [raw_online("1", "texto um")]
        info = rec.montar_base_atual(online, particoes)
        d = rec.montar_diagnostico(info, {}, particoes)
        self.assertIn("ids_faltantes_no_online", d["bloqueios"])
        self.assertEqual(d["status"], "bloqueado")

    def test_bloqueia_por_h_divergente(self):
        particoes = {sha("1"): particao("g1", 1)}
        online = [raw_online("1", "texto um", hist="Cat MUDOU", m="Correto")]
        info = rec.montar_base_atual(online, particoes)
        congelado = {sha("1"): alvo_registro(sha("1"), "g1", 1, "Cat A", "Cat A")}
        d = rec.montar_diagnostico(info, congelado, particoes)
        self.assertIn("h_divergentes", d["bloqueios"])
        self.assertEqual(d["status"], "bloqueado")


class TestHashCorpus(unittest.TestCase):
    def test_hash_muda_quando_grupo_muda(self):
        base = [{"id_sha256": "a", "grupo_sha256": "g1", "referencia_humana": "Cat A"}]
        alterado = [{"id_sha256": "a", "grupo_sha256": "g2", "referencia_humana": "Cat A"}]
        self.assertNotEqual(rec.calcular_hash_corpus(base), rec.calcular_hash_corpus(alterado))

    def test_hash_muda_quando_referencia_muda(self):
        base = [{"id_sha256": "a", "grupo_sha256": "g1", "referencia_humana": "Cat A"}]
        alterado = [{"id_sha256": "a", "grupo_sha256": "g1", "referencia_humana": "Cat B"}]
        self.assertNotEqual(rec.calcular_hash_corpus(base), rec.calcular_hash_corpus(alterado))

    def test_hash_e_deterministico_e_insensivel_a_ordem(self):
        a = [{"id_sha256": "a", "grupo_sha256": "g1", "referencia_humana": "Cat A"},
             {"id_sha256": "b", "grupo_sha256": "g2", "referencia_humana": "Cat B"}]
        b = list(reversed(a))
        self.assertEqual(rec.calcular_hash_corpus(a), rec.calcular_hash_corpus(b))


class TestExecutarEndToEnd(unittest.TestCase):
    """Corpus sintetico com vocabulario separavel, cinco dobras, duas
    categorias. Usa `registros_online` injetado para nao depender de rede."""

    RUIDO = ("bloco a", "pavilhao central", "corredor leste", "chamado reaberto")

    def _corpus(self, n_por_categoria=10, texto_diferente=False):
        """Duas categorias separaveis; o primeiro registro simula uma
        inadequacao real (H != R) para garantir ao menos um alerta na fila
        natural, sem depender de o classificador errar por acaso."""
        particoes, alvo_congelado, online = {}, {}, []
        n = 0
        for cat, termo in (("Cat Eletrica", "lampada disjuntor tomada queimada"),
                          ("Cat Hidraulica", "vazamento torneira esgoto caixa")):
            for i in range(n_por_categoria):
                n += 1
                id_ = str(n)
                id_sha = sha(id_)
                fold = (n % 5) + 1
                texto = f"{termo} ocorrencia {i} {self.RUIDO[n % len(self.RUIDO)]}"
                if texto_diferente:
                    texto += " correcao humana pos agosto"
                grupo = rec.cgt.hash_grupo(
                    [rec.cgt.normalizar_texto(texto), "", "", ""]
                )
                particoes[id_sha] = particao(grupo, fold)
                if n == 1:
                    # Texto de "Cat Eletrica", mas H registrada como
                    # "Cat Hidraulica": inadequacao deliberada e detectavel.
                    h_registrada, r_real = "Cat Hidraulica", cat
                    alvo_congelado[id_sha] = alvo_registro(
                        id_sha, grupo, fold, h_registrada, r_real)
                    online.append(raw_online(
                        id_, texto, hist=h_registrada, m="Incorreto", q=r_real))
                else:
                    alvo_congelado[id_sha] = alvo_registro(id_sha, grupo, fold, cat, cat)
                    online.append(raw_online(id_, texto, hist=cat, m="Correto"))
        return particoes, alvo_congelado, online

    def _gravar_fixtures(self, tmp, particoes, alvo_congelado):
        particoes_path = tmp / "particoes.csv"
        with particoes_path.open("w", encoding="utf-8", newline="") as f:
            f.write("id_sha256,grupo_sha256,dobra\n")
            for id_sha, p in particoes.items():
                f.write(f"{id_sha},{p['grupo_sha256']},{p['outer_fold']}\n")

        alvo_path = tmp / "alvo_ensemble.json"
        registros = list(alvo_congelado.values())
        alvo_path.write_text(json.dumps({
            "metadata": {"schema_version": 1, "hash_corpus": "hash-antigo-ficticio"},
            "records": registros,
        }), encoding="utf-8")

        resumo_path = tmp / "alvo_ensemble_resumo.json"
        resumo_path.write_text(json.dumps({
            "hash_corpus": "hash-antigo-ficticio",
            "hash_historico_ensemble": "hist-antigo-ficticio",
            "hash_alvo_ensemble": "alvo-antigo-ficticio",
            "classes_sha256": "classes-antigo-ficticio",
            "partition_manifest_sha256": "partition-antigo-ficticio",
        }), encoding="utf-8")
        return particoes_path, alvo_path

    def test_rodada_apta_quando_h_r_y_e_folds_preservados(self):
        particoes, alvo_congelado, online = self._corpus()
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            particoes_path, alvo_path = self._gravar_fixtures(tmp, particoes, alvo_congelado)
            resumo = rec.executar(
                particoes_path=particoes_path,
                alvo_congelado_path=alvo_path,
                registros_online=online,
                total_esperado=len(particoes),
            )
        self.assertEqual(resumo["status"], "apto_para_baseline")
        self.assertEqual(resumo["diagnostico"]["h_divergentes"], 0)
        self.assertEqual(resumo["diagnostico"]["r_divergentes"], 0)
        self.assertEqual(resumo["diagnostico"]["y_divergentes"], 0)
        self.assertEqual(resumo["total_registros_recongelados"], len(particoes))
        # Os folds nos registros recongelados sao EXATAMENTE os preservados.
        for reg in resumo["_registros"]:
            self.assertEqual(reg["outer_fold"], particoes[reg["id_sha256"]]["outer_fold"])

    def test_bloqueia_e_nao_treina_quando_h_diverge(self):
        particoes, alvo_congelado, online = self._corpus()
        # Corrompe H de um registro do congelamento anterior: o H atual (na
        # planilha online, via `online`) nao muda, mas passa a divergir do
        # H congelado.
        primeiro_id = next(iter(alvo_congelado))
        alvo_congelado[primeiro_id]["categoria_historica"] = "Categoria Inventada"
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            particoes_path, alvo_path = self._gravar_fixtures(tmp, particoes, alvo_congelado)
            resumo = rec.executar(
                particoes_path=particoes_path,
                alvo_congelado_path=alvo_path,
                registros_online=online,
                total_esperado=len(particoes),
            )
        self.assertEqual(resumo["status"], "bloqueado")
        self.assertEqual(resumo["diagnostico"]["h_divergentes"], 1)
        # Nenhum treino ocorreu: nao ha predicoes nem baseline no resultado.
        self.assertEqual(resumo["_predicoes"], {})
        self.assertIsNone(resumo["baseline_linear_svc"])

    def test_bloqueia_quando_grupo_atual_cruza_dobra_preservada(self):
        particoes, alvo_congelado, online = self._corpus(n_por_categoria=3)
        ids = list(particoes)
        # Forca dois registros de dobras DIFERENTES a colapsar no mesmo
        # texto (logo, mesmo grupo_sha256 atual), sem alterar H/R/fold.
        id_a, id_b = ids[0], ids[1]
        particoes[id_b]["outer_fold"] = (particoes[id_a]["outer_fold"] % 5) + 1
        texto_unificado = "texto identico forcado para colidir grupos"
        # Reescreve os textos online dos dois IDs para o mesmo conteudo.
        online_por_id_sha = {sha(r["id"]): r for r in online}
        for id_sha in (id_a, id_b):
            online_por_id_sha[id_sha]["titulo"] = texto_unificado
            online_por_id_sha[id_sha]["descricao_glpi"] = ""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            particoes_path, alvo_path = self._gravar_fixtures(tmp, particoes, alvo_congelado)
            resumo = rec.executar(
                particoes_path=particoes_path,
                alvo_congelado_path=alvo_path,
                registros_online=online,
                total_esperado=len(particoes),
            )
        self.assertEqual(resumo["status"], "bloqueado")
        self.assertGreaterEqual(resumo["diagnostico"]["grupos_cruzando_dobras"], 1)
        self.assertEqual(resumo["_predicoes"], {})

    def test_hash_corpus_muda_quando_texto_online_muda(self):
        particoes, alvo_congelado, online = self._corpus()
        particoes2, alvo_congelado2, online2 = self._corpus(texto_diferente=True)
        # Mesmos IDs/folds/H/R, texto (logo grupo) diferente.
        for id_sha in particoes2:
            alvo_congelado2[id_sha]["categoria_historica"] = alvo_congelado[id_sha]["categoria_historica"]
            alvo_congelado2[id_sha]["referencia_humana"] = alvo_congelado[id_sha]["referencia_humana"]
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            particoes_path, alvo_path = self._gravar_fixtures(tmp, particoes, alvo_congelado)
            resumo_1 = rec.executar(
                particoes_path=particoes_path, alvo_congelado_path=alvo_path,
                registros_online=online, total_esperado=len(particoes),
            )
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            particoes_path, alvo_path = self._gravar_fixtures(tmp, particoes, alvo_congelado)
            resumo_2 = rec.executar(
                particoes_path=particoes_path, alvo_congelado_path=alvo_path,
                registros_online=online2, total_esperado=len(particoes),
            )
        self.assertEqual(resumo_1["status"], "apto_para_baseline")
        self.assertEqual(resumo_2["status"], "apto_para_baseline")
        self.assertNotEqual(resumo_1["hash_corpus_novo"], resumo_2["hash_corpus_novo"])

    def test_baseline_nao_e_carregado_de_predicoes_antigas(self):
        # Regressao estrutural: o modulo nunca deve ler o CSV de predicoes
        # historicas do LinearSVC ao montar o baseline novo.
        fonte = inspect.getsource(rec)
        self.assertNotIn("retreino_canonico_predicoes.csv", fonte)
        self.assertNotIn("carregar_predicoes_linear_svc", fonte)

        # E, na pratica, o baseline retornado e computado por um treino real
        # sobre o corpus injetado, nao por uma constante fixa.
        particoes, alvo_congelado, online = self._corpus(n_por_categoria=12)
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            particoes_path, alvo_path = self._gravar_fixtures(tmp, particoes, alvo_congelado)
            resumo = rec.executar(
                particoes_path=particoes_path, alvo_congelado_path=alvo_path,
                registros_online=online, total_esperado=len(particoes),
            )
        self.assertEqual(resumo["status"], "apto_para_baseline")
        baseline_atual = resumo["baseline_linear_svc"]["atual"]
        # Corpus sintetico e pequeno e separavel: nao deve coincidir, campo a
        # campo, com as constantes historicas de 13.972 registros.
        self.assertNotEqual(
            {k: baseline_atual.get(k, 0) for k in rec.BASELINE_HISTORICO},
            rec.BASELINE_HISTORICO,
        )
        self.assertEqual(len(resumo["_predicoes"]), len(particoes))


if __name__ == "__main__":
    unittest.main()
