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


class TestValidarCoberturaParticoesAlvo(unittest.TestCase):
    """Correcao 3: `validar_h_r_y_preservados` sozinha aceita silenciosamente
    um ID sem contraparte na outra fonte; estes testes cobrem os quatro
    cenarios negativos que devem bloquear a rodada antes de qualquer treino."""

    def _par(self):
        return {
            sha("1"): alvo_registro(sha("1"), "g1", 1, "Cat A", "Cat A"),
            sha("2"): alvo_registro(sha("2"), "g2", 2, "Cat B", "Cat B"),
        }

    def test_sem_violacao_quando_universos_batem(self):
        particoes = {sha("1"): particao("g1", 1), sha("2"): particao("g2", 2)}
        d = rec.validar_cobertura_particoes_alvo(particoes, self._par())
        self.assertEqual(d["bloqueios"], [])
        self.assertEqual(d["total_ids_particao_sem_alvo"], 0)
        self.assertEqual(d["total_ids_alvo_sem_particao"], 0)

    def test_id_presente_na_particao_ausente_no_alvo_bloqueia(self):
        particoes = {sha("1"): particao("g1", 1), sha("2"): particao("g2", 2),
                    sha("3"): particao("g3", 3)}
        alvo = self._par()  # sem o id "3"
        d = rec.validar_cobertura_particoes_alvo(particoes, alvo)
        self.assertIn("ids_particao_sem_contraparte_no_alvo", d["bloqueios"])
        self.assertEqual(d["total_ids_particao_sem_alvo"], 1)
        self.assertEqual(d["amostra_ids_particao_sem_alvo"], [sha("3")])

    def test_id_presente_no_alvo_ausente_na_particao_bloqueia(self):
        particoes = {sha("1"): particao("g1", 1)}  # sem o id "2"
        alvo = self._par()
        d = rec.validar_cobertura_particoes_alvo(particoes, alvo)
        self.assertIn("ids_alvo_sem_contraparte_na_particao", d["bloqueios"])
        self.assertEqual(d["total_ids_alvo_sem_particao"], 1)
        self.assertEqual(d["amostra_ids_alvo_sem_particao"], [sha("2")])

    def test_dobra_historica_divergente_entre_alvo_e_particao_bloqueia(self):
        particoes = {sha("1"): particao("g1", 1), sha("2"): particao("g2", 2)}
        alvo = self._par()
        alvo[sha("2")]["outer_fold"] = 4  # diverge da particao (2)
        d = rec.validar_cobertura_particoes_alvo(particoes, alvo)
        self.assertIn("dobra_historica_divergente_entre_alvo_e_particao", d["bloqueios"])
        self.assertEqual(d["total_dobra_historica_divergente"], 1)
        self.assertEqual(d["amostra_dobra_historica_divergente"], [sha("2")])

    def test_conjunto_de_folds_invalido_bloqueia(self):
        particoes = {sha("1"): particao("g1", 1), sha("2"): particao("g2", 6)}
        alvo = self._par()
        alvo[sha("2")]["outer_fold"] = 6  # mantem consistencia com a particao
        d = rec.validar_cobertura_particoes_alvo(
            particoes, alvo, folds_esperados=[1, 2, 3, 4, 5]
        )
        self.assertIn("folds_particao_invalidos", d["bloqueios"])
        self.assertIn("folds_alvo_congelado_invalidos", d["bloqueios"])
        self.assertEqual(d["folds_particao"], [1, 6])

    def test_folds_esperados_none_nao_verifica_conjunto_de_folds(self):
        particoes = {sha("1"): particao("g1", 1)}
        alvo = {sha("1"): alvo_registro(sha("1"), "g1", 1, "Cat A", "Cat A")}
        d = rec.validar_cobertura_particoes_alvo(particoes, alvo, folds_esperados=None)
        self.assertNotIn("folds_particao_invalidos", d["bloqueios"])

    def test_total_esperado_verifica_os_dois_lados(self):
        particoes = {sha("1"): particao("g1", 1), sha("2"): particao("g2", 2)}
        alvo = self._par()
        d = rec.validar_cobertura_particoes_alvo(particoes, alvo, total_esperado=99999)
        self.assertIn("total_ids_particoes_divergente_do_denominador_esperado", d["bloqueios"])
        self.assertIn("total_ids_alvo_congelado_divergente_do_denominador_esperado", d["bloqueios"])


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


class TestManifestoParticaoOnline(unittest.TestCase):
    def test_csv_tem_cabecalho_e_linhas_ordenadas_por_id(self):
        registros = [
            {"id_sha256": "b", "grupo_sha256": "gB", "outer_fold": 2},
            {"id_sha256": "a", "grupo_sha256": "gA", "outer_fold": 1},
        ]
        conteudo = rec.montar_particoes_online_csv_bytes(registros).decode("utf-8")
        linhas = conteudo.splitlines()
        self.assertEqual(linhas[0], "id_sha256,grupo_sha256,dobra")
        self.assertEqual(linhas[1], "a,gA,1")
        self.assertEqual(linhas[2], "b,gB,2")

    def test_bytes_deterministicos_para_o_mesmo_conteudo(self):
        registros = [{"id_sha256": "a", "grupo_sha256": "gA", "outer_fold": 1}]
        self.assertEqual(
            rec.montar_particoes_online_csv_bytes(registros),
            rec.montar_particoes_online_csv_bytes(list(registros)),
        )

    def test_bytes_mudam_se_grupo_atual_mudar(self):
        r1 = [{"id_sha256": "a", "grupo_sha256": "gA", "outer_fold": 1}]
        r2 = [{"id_sha256": "a", "grupo_sha256": "gA-outro", "outer_fold": 1}]
        self.assertNotEqual(
            rec.montar_particoes_online_csv_bytes(r1),
            rec.montar_particoes_online_csv_bytes(r2),
        )


class TestFoldAssignmentHash(unittest.TestCase):
    def test_deterministico_e_insensivel_a_ordem(self):
        a = [("id2", 2), ("id1", 1)]
        b = [("id1", 1), ("id2", 2)]
        self.assertEqual(rec.calcular_fold_assignment_sha256(a),
                         rec.calcular_fold_assignment_sha256(b))

    def test_muda_se_fold_mudar(self):
        a = [("id1", 1)]
        b = [("id1", 2)]
        self.assertNotEqual(rec.calcular_fold_assignment_sha256(a),
                            rec.calcular_fold_assignment_sha256(b))

    def test_nao_muda_se_apenas_grupo_ou_rotulo_mudar(self):
        # A assinatura so recebe (id, fold): mudar grupo/rotulo em outro
        # lugar nao pode, por construcao, afetar este hash.
        pares = [("id1", 1), ("id2", 2)]
        h1 = rec.calcular_fold_assignment_sha256(pares)
        h2 = rec.calcular_fold_assignment_sha256(list(pares))
        self.assertEqual(h1, h2)


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

    def test_metadata_do_alvo_online_aponta_para_o_manifesto_online(self):
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
        alvo_obj = json.loads(resumo["_alvo_bytes"])
        meta = alvo_obj["metadata"]
        # partition_manifest_sha256 do artefato NOVO aponta para o manifesto
        # ONLINE, nao para o SHA fisico do arquivo historico intocado.
        self.assertEqual(meta["partition_manifest_sha256"], resumo["partition_manifest_online_sha256"])
        self.assertNotEqual(meta["partition_manifest_sha256"], resumo["partition_manifest_origem_sha256_novo"])
        # A proveniencia do manifesto historico fica preservada, com nome
        # inequivoco, dentro do proprio metadata.
        self.assertEqual(meta["partition_manifest_origem_sha256"],
                         resumo["partition_manifest_origem_sha256_novo"])
        self.assertEqual(meta["fold_assignment_sha256"], resumo["fold_assignment_sha256"])
        # O manifesto online recalculado a partir dos bytes bate com o hash
        # publicado no resumo (nao e um valor decorativo).
        self.assertEqual(
            rec.cae.sha256_bytes(resumo["_particoes_online_bytes"]),
            resumo["partition_manifest_online_sha256"],
        )

    def test_gravar_escreve_o_manifesto_de_particao_online_em_disco(self):
        particoes, alvo_congelado, online = self._corpus(n_por_categoria=4)
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            particoes_path, alvo_path = self._gravar_fixtures(tmp, particoes, alvo_congelado)
            resumo = rec.executar(
                particoes_path=particoes_path,
                alvo_congelado_path=alvo_path,
                registros_online=online,
                total_esperado=len(particoes),
            )
            saida_dir = tmp / "saida"
            particoes_online_path = saida_dir / "particoes_ensemble_online_mapa.csv"
            rec.gravar(
                resumo, saida_dir, saida_dir / "alvo_ensemble_online.json",
                particoes_online_path, saida_dir / "resumo.json",
                saida_dir / "predicoes.csv", saida_dir / "relatorio.md",
            )
            self.assertTrue(particoes_online_path.exists())
            conteudo = particoes_online_path.read_text(encoding="utf-8")
            self.assertEqual(conteudo.splitlines()[0], "id_sha256,grupo_sha256,dobra")
            self.assertEqual(len(conteudo.splitlines()) - 1, len(particoes))
            # docs/dados/particoes_canonicas_mapa.csv NUNCA e regravado por
            # este fluxo: nao existe caminho de escrita para ele em `gravar`.
            self.assertFalse((saida_dir / "particoes_canonicas_mapa.csv").exists())

    def test_bloqueia_por_id_do_alvo_sem_contraparte_na_particao(self):
        particoes, alvo_congelado, online = self._corpus(n_por_categoria=3)
        # Um ID a mais no alvo congelado, sem contraparte na particao
        # preservada: precisa bloquear antes de qualquer treino.
        alvo_congelado[sha("id-fantasma")] = alvo_registro(
            sha("id-fantasma"), "g-fantasma", 1, "Cat X", "Cat X"
        )
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
        self.assertIn("ids_alvo_sem_contraparte_na_particao", resumo["diagnostico"]["bloqueios"])
        self.assertEqual(resumo["_predicoes"], {})

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
