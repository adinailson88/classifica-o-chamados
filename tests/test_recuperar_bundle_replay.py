from __future__ import annotations

import hashlib
import sys
import unittest
import unittest.mock
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import recuperar_bundle_replay as rbr  # noqa: E402
import replay_bundle as rb  # noqa: E402


def sha(id_: str) -> str:
    return hashlib.sha256(id_.encode("utf-8")).hexdigest()


def registro_online(id_bruto, titulo="titulo", descricao_glpi="descricao",
                    titulo_osm="", descricao_osm="", categoria_historica="Cat A",
                    conferencia_glpi="", categoria_manual=""):
    """Formato devolvido por `recongelar_ensemble_online.ler_registros_online` /
    `construir_grupos_textuais.ler_registros`."""
    return {
        "id": id_bruto,
        "titulo": titulo,
        "descricao_glpi": descricao_glpi,
        "titulo_osm": titulo_osm,
        "descricao_osm": descricao_osm,
        "categoria_historica": categoria_historica,
        "conferencia_glpi": conferencia_glpi,
        "categoria_manual": categoria_manual,
    }


# TESTE OBRIGATORIO 1 + 2: os 4 patches do GRUPO A sao exatamente os
# informados pela auditoria, e a allowlist so usa id_sha256 (nunca ID bruto).
#
# IMPORTANTE: este teste NUNCA deriva os id_sha256 a partir de um ID bruto
# (nem aqui, nem em nenhum outro lugar deste arquivo) — os quatro hashes
# completos abaixo sao copiados literalmente de `ALLOWLIST_GRUPO_A` em
# src/recuperar_bundle_replay.py (um hash SHA-256 nao e dado sensivel: nao
# permite recuperar o ID bruto original). Comparar contra uma copia literal
# do dicionario esperado prova que o conteudo de producao e exatamente o
# aprovado, sem nunca reintroduzir nenhum dos 4 IDs brutos no repositorio.
class TestAllowlistGrupoA(unittest.TestCase):
    ESPERADO = {
        "1b1e541d103df59767dedb8e899043e09cbf580c17bb962174cc8eb6eef7c1aa": {
            "titulo_osm": "",
            "descricao_osm": "",
        },
        "441a70841acab28f41659a79a3e802ab69c0890a1567047d997beefbf849ff7b": {
            "descricao_glpi": "",
        },
        "1cb0fa284bd3556610ff4a7c5f98e349ebdde0e9743bd51dc03be40ee99323f2": {
            "descricao_glpi": "",
        },
        "79b7e901127de702822b92f706c0512fc3d20d266226c5037b02fae029bce7dd": {
            "descricao_glpi": "",
        },
    }

    def test_grupo_a_e_exatamente_o_dicionario_esperado(self):
        self.assertEqual(rbr.ALLOWLIST_GRUPO_A, self.ESPERADO)

    def test_grupo_a_so_usa_id_sha256_como_chave(self):
        for chave in rbr.ALLOWLIST_GRUPO_A:
            self.assertEqual(len(chave), 64, chave)
            int(chave, 16)  # levanta ValueError se nao for hex puro

    def test_grupo_a_so_toca_campos_textuais_e_valores_vazios(self):
        for id_sha256, campos in rbr.ALLOWLIST_GRUPO_A.items():
            for campo, valor in campos.items():
                self.assertIn(campo, rbr.cgt.CAMPOS_TEXTUAIS, id_sha256)
                self.assertEqual(valor, "", f"{id_sha256}/{campo}")


# TESTE OBRIGATORIO 3: Grupo B nao contem texto bruto (nem ID bruto) no
# codigo. Mesma regra do GRUPO A acima: os 3 hashes completos abaixo sao
# copiados literalmente de `IDS_SHA256_GRUPO_B` em
# src/recuperar_bundle_replay.py — nenhum ID bruto e usado para derivar
# nada neste arquivo de teste.
class TestAllowlistGrupoBSemTextoBruto(unittest.TestCase):
    IDS_SHA256_ESPERADOS = (
        "f9aece7ddad1b121c053107943f5e8d9eea777609cc8c39417ff6b05fb5ec72f",
        "225a8bcf4910f252639ec83895be156492b89a36ec6e3ab523d4abb87477bd66",
        "c56dd685c1898fd8e0f2c55918500b07af18fe795426e5223b16372050aee3d4",
    )

    def test_ids_sha256_grupo_b_sao_exatamente_os_esperados(self):
        self.assertEqual(
            tuple(sorted(rbr.IDS_SHA256_GRUPO_B)),
            tuple(sorted(self.IDS_SHA256_ESPERADOS)),
        )

    def test_ids_sha256_grupo_b_sao_hex_puro_de_64_caracteres(self):
        for chave in rbr.IDS_SHA256_GRUPO_B:
            self.assertEqual(len(chave), 64, chave)
            int(chave, 16)

    def test_carregar_allowlist_grupo_b_le_do_env(self):
        """ID ficticio (nunca um ID real): esta e uma checagem de
        encanamento (env var -> JSON parseado), independente de qual id
        de producao existe de verdade."""
        chave_ficticia = sha("TESTE-001")
        payload = '{"' + chave_ficticia + '": {"titulo": "x"}}'
        with unittest.mock.patch.dict(
            "os.environ", {rbr.ALLOWLIST_GRUPO_B_ENV: payload}
        ):
            self.assertEqual(
                rbr.carregar_allowlist_grupo_b(),
                {chave_ficticia: {"titulo": "x"}},
            )

    def test_carregar_allowlist_grupo_b_levanta_erro_sem_env_nem_arquivo(self):
        with unittest.mock.patch.dict("os.environ", {}, clear=False):
            import os as _os
            _os.environ.pop(rbr.ALLOWLIST_GRUPO_B_ENV, None)
            with unittest.mock.patch.object(
                rbr, "ALLOWLIST_GRUPO_B_LOCAL", Path("caminho-inexistente.local.json")
            ):
                with self.assertRaises(RuntimeError):
                    rbr.carregar_allowlist_grupo_b()


class TestMontarAllowlist(unittest.TestCase):
    def test_uniao_simples_de_dois_grupos(self):
        a = {sha("1"): {"titulo": "A"}}
        b = {sha("2"): {"descricao_glpi": "B"}}
        self.assertEqual(rbr.montar_allowlist(a, b), {
            sha("1"): {"titulo": "A"}, sha("2"): {"descricao_glpi": "B"},
        })


class TestAplicarAllowlist(unittest.TestCase):
    def test_campo_autorizado_e_restaurado(self):
        atuais = [registro_online("1", descricao_osm="preenchido depois")]
        allowlist = {sha("1"): {"descricao_osm": "valor historico comprovado"}}
        resultado, aplicados = rbr.aplicar_allowlist(atuais, allowlist)
        self.assertEqual(resultado[0]["descricao_osm"], "valor historico comprovado")
        self.assertEqual(aplicados, {sha("1"): ["descricao_osm"]})

    def test_registro_fora_da_allowlist_nunca_e_alterado(self):
        """TESTE OBRIGATORIO 4."""
        atuais = [registro_online("2", titulo="valor online, nunca tocado")]
        allowlist = {sha("1"): {"titulo": "so o id 1 esta autorizado"}}
        resultado, aplicados = rbr.aplicar_allowlist(atuais, allowlist)
        self.assertEqual(resultado[0], atuais[0])
        self.assertEqual(aplicados, {})

    def test_campo_fora_da_allowlist_nunca_e_alterado(self):
        """TESTE OBRIGATORIO 5: id esta na allowlist, mas so um dos seus
        campos; os demais campos desse MESMO registro ficam intocados."""
        atuais = [registro_online("1", titulo="online", descricao_glpi="tambem online")]
        allowlist = {sha("1"): {"titulo": "historico"}}
        resultado, aplicados = rbr.aplicar_allowlist(atuais, allowlist)
        self.assertEqual(resultado[0]["titulo"], "historico")
        self.assertEqual(resultado[0]["descricao_glpi"], "tambem online")
        self.assertEqual(aplicados, {sha("1"): ["titulo"]})

    def test_campo_ja_igual_ao_historico_nao_conta_como_aplicado(self):
        atuais = [registro_online("1", titulo="ja restaurado")]
        allowlist = {sha("1"): {"titulo": "ja restaurado"}}
        resultado, aplicados = rbr.aplicar_allowlist(atuais, allowlist)
        self.assertEqual(resultado[0]["titulo"], "ja restaurado")
        self.assertEqual(aplicados, {})

    def test_ignora_campo_da_allowlist_fora_dos_4_campos_textuais(self):
        atuais = [registro_online("1", categoria_historica="Cat A")]
        allowlist = {sha("1"): {"categoria_historica": "Cat B (nao deveria aplicar)"}}
        resultado, aplicados = rbr.aplicar_allowlist(atuais, allowlist)
        self.assertEqual(resultado[0]["categoria_historica"], "Cat A")
        self.assertEqual(aplicados, {})


class TestMontarBundle(unittest.TestCase):
    """`montar_bundle` e o coracao da correcao desta rodada: H/R/grupo/fold
    vem SEMPRE dos artefatos congelados (particoes/alvo_congelado), nunca
    de M/Q atuais nem recalculados — so o texto bruto vem da base online
    patcheada."""

    def test_texto_vem_da_base_patcheada_hrfoldgrupo_vem_do_congelado(self):
        registros_patched = [registro_online("1", titulo="T1", descricao_glpi="D1")]
        particoes = {sha("1"): {"grupo_sha256": "grupo-congelado", "outer_fold": 3}}
        alvo_congelado = {sha("1"): {
            "categoria_historica": "Categoria congelada",
            "referencia_humana": "Referencia congelada",
        }}
        bundle = rbr.montar_bundle(registros_patched, particoes, alvo_congelado)
        self.assertEqual(len(bundle), 1)
        linha = bundle[0]
        self.assertEqual(linha["id_sha256"], sha("1"))
        self.assertEqual(linha["titulo"], "T1")
        self.assertEqual(linha["descricao_glpi"], "D1")
        self.assertEqual(linha["categoria_historica"], "Categoria congelada")
        self.assertEqual(linha["referencia_humana"], "Referencia congelada")
        self.assertEqual(linha["grupo_sha256"], "grupo-congelado")
        self.assertEqual(linha["outer_fold"], 3)
        self.assertEqual(set(linha), set(rb.CAMPOS_BUNDLE))

    def test_alteracao_de_mq_atuais_nunca_muda_referencia_humana_do_bundle(self):
        """`registro_online` pode carregar conferencia_glpi/categoria_manual
        (M/Q) quaisquer — `montar_bundle` nunca le essas chaves: R vem
        exclusivamente do alvo congelado, nunca recalculado."""
        registros_patched = [registro_online(
            "1", conferencia_glpi="Errado", categoria_manual="Categoria manual nova",
        )]
        particoes = {sha("1"): {"grupo_sha256": "g", "outer_fold": 1}}
        alvo_congelado = {sha("1"): {
            "categoria_historica": "Categoria congelada",
            "referencia_humana": "Referencia congelada",
        }}
        bundle = rbr.montar_bundle(registros_patched, particoes, alvo_congelado)
        self.assertEqual(bundle[0]["referencia_humana"], "Referencia congelada")
        self.assertEqual(bundle[0]["categoria_historica"], "Categoria congelada")

    def test_itera_sobre_universo_congelado_ignora_registro_online_fora_do_corpus(self):
        registros_patched = [
            registro_online("fora-do-corpus"),
            registro_online("dentro-do-corpus", titulo="T"),
        ]
        particoes = {sha("dentro-do-corpus"): {"grupo_sha256": "g", "outer_fold": 1}}
        alvo_congelado = {sha("dentro-do-corpus"): {
            "categoria_historica": "Cat A", "referencia_humana": "Cat A",
        }}
        bundle = rbr.montar_bundle(registros_patched, particoes, alvo_congelado)
        self.assertEqual(len(bundle), 1)
        self.assertEqual(bundle[0]["id_sha256"], sha("dentro-do-corpus"))

    def test_levanta_se_id_do_corpus_congelado_sem_contraparte_bruta(self):
        particoes = {sha("dentro-do-corpus"): {"grupo_sha256": "g", "outer_fold": 1}}
        alvo_congelado = {sha("dentro-do-corpus"): {
            "categoria_historica": "Cat A", "referencia_humana": "Cat A",
        }}
        with self.assertRaises(rbr.RecuperacaoBloqueada):
            rbr.montar_bundle([], particoes, alvo_congelado)


class TestValidarEstruturaCongelada(unittest.TestCase):
    """`validar_estrutura_congelada` NUNCA calcula nem reporta
    h_divergentes/r_divergentes/y_divergentes — essa e a correcao central
    desta rodada: R/Y atuais nao bloqueiam mais o RECOVER (eles so
    determinam se um NOVO congelamento pode ser aprovado, papel exclusivo
    de `gate_zero()`, que este modulo nao chama mais)."""

    def _contexto(self, total, folds):
        return unittest.mock.patch.multiple(
            rbr.rero, TOTAL_ESPERADO=total, FOLDS_ESPERADOS_PADRAO=folds,
        )

    def test_estrutura_ok_devolve_bloqueios_vazio(self):
        registros_patched = [registro_online("1")]
        particoes = {sha("1"): {"grupo_sha256": "g", "outer_fold": 1}}
        alvo_congelado = {sha("1"): {"outer_fold": 1}}
        with self._contexto(1, [1]):
            resultado = rbr.validar_estrutura_congelada(
                registros_patched, particoes, alvo_congelado
            )
        self.assertEqual(resultado["bloqueios"], [])

    def test_nunca_reporta_h_r_ou_y_divergentes(self):
        registros_patched = [registro_online("1")]
        particoes = {sha("1"): {"grupo_sha256": "g", "outer_fold": 1}}
        alvo_congelado = {sha("1"): {"outer_fold": 1}}
        with self._contexto(1, [1]):
            resultado = rbr.validar_estrutura_congelada(
                registros_patched, particoes, alvo_congelado
            )
        self.assertNotIn("h_divergentes", resultado)
        self.assertNotIn("r_divergentes", resultado)
        self.assertNotIn("y_divergentes", resultado)

    def test_bloqueia_por_id_faltante_no_online(self):
        particoes = {sha("1"): {"grupo_sha256": "g", "outer_fold": 1}}
        alvo_congelado = {sha("1"): {"outer_fold": 1}}
        with self._contexto(1, [1]):
            resultado = rbr.validar_estrutura_congelada([], particoes, alvo_congelado)
        self.assertIn("ids_faltantes_no_online", resultado["bloqueios"])
        self.assertEqual(resultado["amostra_faltantes_no_online"], [sha("1")])

    def test_bloqueia_por_id_duplicado_no_online(self):
        registros_patched = [registro_online("1"), registro_online("1")]
        particoes = {sha("1"): {"grupo_sha256": "g", "outer_fold": 1}}
        alvo_congelado = {sha("1"): {"outer_fold": 1}}
        with self._contexto(1, [1]):
            resultado = rbr.validar_estrutura_congelada(
                registros_patched, particoes, alvo_congelado
            )
        self.assertIn("ids_duplicados_no_online", resultado["bloqueios"])

    def test_bloqueia_por_total_diferente_do_esperado(self):
        registros_patched = [registro_online("1")]
        particoes = {sha("1"): {"grupo_sha256": "g", "outer_fold": 1}}
        alvo_congelado = {sha("1"): {"outer_fold": 1}}
        with self._contexto(2, [1]):  # esperado 2, so ha 1
            resultado = rbr.validar_estrutura_congelada(
                registros_patched, particoes, alvo_congelado
            )
        self.assertIn(
            "total_ids_particoes_divergente_do_denominador_esperado",
            resultado["bloqueios"],
        )

    def test_bloqueia_por_fold_divergente_entre_particao_e_alvo(self):
        registros_patched = [registro_online("1")]
        particoes = {sha("1"): {"grupo_sha256": "g", "outer_fold": 1}}
        alvo_congelado = {sha("1"): {"outer_fold": 2}}
        with self._contexto(1, [1, 2]):
            resultado = rbr.validar_estrutura_congelada(
                registros_patched, particoes, alvo_congelado
            )
        self.assertIn(
            "dobra_historica_divergente_entre_alvo_e_particao", resultado["bloqueios"]
        )


class TestExecutarFluxo(unittest.TestCase):
    def _contexto_registro_unico(self, titulo="titulo", descricao_glpi="descricao",
                                 titulo_osm="", descricao_osm=""):
        online = [registro_online("1", titulo=titulo, descricao_glpi=descricao_glpi,
                                  titulo_osm=titulo_osm, descricao_osm=descricao_osm)]
        grupo = rbr.cgt.hash_grupo(
            [rbr.cgt.normalizar_texto(c)
             for c in (titulo, descricao_glpi, titulo_osm, descricao_osm)]
        )
        particoes = {sha("1"): {"grupo_sha256": grupo, "outer_fold": 1}}
        alvo_congelado = {sha("1"): {
            "categoria_historica": "Cat A", "referencia_humana": "Cat A", "outer_fold": 1,
        }}
        return online, particoes, alvo_congelado

    # GRUPO A so precisa estar NAO-VAZIO para passar o gate inicial de
    # `executar()` — usar um id fora deste fixture (nunca sha("1")) evita
    # que o patch mexa no unico registro do teste e quebre o grupo_sha256
    # congelado que cada teste monta com cuidado.
    ALLOWLIST_GRUPO_A_INERTE = {sha("id-fora-deste-fixture"): {"titulo": "x"}}

    def test_bloqueado_estruturalmente_nao_chega_a_montar_bundle(self):
        """Sem overrides de TOTAL_ESPERADO/FOLDS_ESPERADOS_PADRAO, 1
        registro sintetico nunca bate com os 13.972 de producao -> bloqueio
        estrutural real (sem mockar `validar_estrutura_congelada`), e
        `montar_bundle` nunca chega a ser chamada."""
        online, particoes, alvo_congelado = self._contexto_registro_unico()
        with unittest.mock.patch.object(
            rbr.rero, "ler_registros_online", return_value=online
        ), unittest.mock.patch.object(
            rbr.rero, "carregar_particoes_preservadas", return_value=particoes
        ), unittest.mock.patch.object(
            rbr.rero, "carregar_alvo_congelado", return_value=alvo_congelado
        ), unittest.mock.patch.object(rbr, "montar_bundle") as m_montar_bundle:
            diagnostico = rbr.executar(
                hash_esperado=rbr.REPLAY_INPUT_SHA256_ESPERADO_CANDIDATO,
                config_path=Path("nao-usado.json"),
                particoes_path=Path("nao-usado.csv"),
                allowlist_grupo_a=self.ALLOWLIST_GRUPO_A_INERTE,
                allowlist_grupo_b={},
            )
        self.assertEqual(diagnostico["status"], "bloqueado_estrutural")
        self.assertTrue(diagnostico["diagnostico_estrutural"]["bloqueios"])
        m_montar_bundle.assert_not_called()

    def test_estrutura_ok_mas_grupo_textual_divergente_bloqueia(self):
        """TESTE OBRIGATORIO: grupo textual errado bloqueia e mostra apenas
        id_sha256."""
        online, particoes, alvo_congelado = self._contexto_registro_unico()
        particoes[sha("1")]["grupo_sha256"] = "grupo-nunca-vai-bater-com-o-texto"
        with unittest.mock.patch.object(
            rbr.rero, "ler_registros_online", return_value=online
        ), unittest.mock.patch.object(
            rbr.rero, "carregar_particoes_preservadas", return_value=particoes
        ), unittest.mock.patch.object(
            rbr.rero, "carregar_alvo_congelado", return_value=alvo_congelado
        ), unittest.mock.patch.object(
            rbr, "validar_estrutura_congelada", return_value={"bloqueios": []}
        ), unittest.mock.patch.object(
            rbr.efc, "validar_bundle_replay"
        ) as m_cientifico:
            diagnostico = rbr.executar(
                hash_esperado=rbr.REPLAY_INPUT_SHA256_ESPERADO_CANDIDATO,
                config_path=Path("nao-usado.json"),
                particoes_path=Path("nao-usado.csv"),
                allowlist_grupo_a=self.ALLOWLIST_GRUPO_A_INERTE,
                allowlist_grupo_b={},
            )
        self.assertEqual(diagnostico["status"], "bloqueado_grupo_textual_divergente")
        self.assertEqual(diagnostico["total_grupos_divergentes"], 1)
        self.assertEqual(diagnostico["amostra_ids_sha256_grupo_divergente"], [sha("1")])
        m_cientifico.assert_not_called()

    def test_grupo_ok_mas_validacao_cientifica_bloqueia(self):
        """TESTE OBRIGATORIO: cinco hashes divergentes bloqueiam."""
        online, particoes, alvo_congelado = self._contexto_registro_unico()
        with unittest.mock.patch.object(
            rbr.rero, "ler_registros_online", return_value=online
        ), unittest.mock.patch.object(
            rbr.rero, "carregar_particoes_preservadas", return_value=particoes
        ), unittest.mock.patch.object(
            rbr.rero, "carregar_alvo_congelado", return_value=alvo_congelado
        ), unittest.mock.patch.object(
            rbr, "validar_estrutura_congelada", return_value={"bloqueios": []}
        ), unittest.mock.patch.object(
            rbr.efc, "validar_bundle_replay",
            side_effect=rbr.efc.GateZeroBloqueado("5 hashes metodologicos divergentes"),
        ) as m_cientifico:
            diagnostico = rbr.executar(
                hash_esperado=rbr.REPLAY_INPUT_SHA256_ESPERADO_CANDIDATO,
                config_path=Path("nao-usado.json"),
                particoes_path=Path("nao-usado.csv"),
                allowlist_grupo_a=self.ALLOWLIST_GRUPO_A_INERTE,
                allowlist_grupo_b={},
            )
        m_cientifico.assert_called_once()
        self.assertEqual(diagnostico["status"], "bloqueado_validacao_cientifica")
        self.assertFalse(diagnostico["bundle_publicado"])

    def test_hash_candidato_divergente_bloqueia(self):
        """TESTE OBRIGATORIO: hash candidato divergente bloqueia. A propria
        `validar_bundle_replay` (real, na producao) levanta ReplayBloqueado
        quando o hash nao bate — aqui simulamos exatamente essa excecao."""
        online, particoes, alvo_congelado = self._contexto_registro_unico()
        with unittest.mock.patch.object(
            rbr.rero, "ler_registros_online", return_value=online
        ), unittest.mock.patch.object(
            rbr.rero, "carregar_particoes_preservadas", return_value=particoes
        ), unittest.mock.patch.object(
            rbr.rero, "carregar_alvo_congelado", return_value=alvo_congelado
        ), unittest.mock.patch.object(
            rbr, "validar_estrutura_congelada", return_value={"bloqueios": []}
        ), unittest.mock.patch.object(
            rbr.efc, "validar_bundle_replay",
            side_effect=rbr.efc.ReplayBloqueado("replay_input_sha256 divergente"),
        ):
            diagnostico = rbr.executar(
                hash_esperado="0" * 64,
                config_path=Path("nao-usado.json"),
                particoes_path=Path("nao-usado.csv"),
                allowlist_grupo_a=self.ALLOWLIST_GRUPO_A_INERTE,
                allowlist_grupo_b={},
            )
        self.assertEqual(diagnostico["status"], "bloqueado_validacao_cientifica")
        self.assertFalse(diagnostico["bundle_publicado"])

    def test_fluxo_completo_aprovado_reporta_candidato_recuperado_sem_publicar(self):
        online, particoes, alvo_congelado = self._contexto_registro_unico()
        resultado_cientifico = {
            "hashes": {"hash_corpus": "x"},
            "total_registros": 1, "total_grupos": 1,
            "h_dentro_de_c": 1, "h_fora_de_c": 0, "classes": ["Cat A"],
            "replay_input_sha256": "HASH-FINAL-DE-TESTE",
        }
        with unittest.mock.patch.object(
            rbr.rero, "ler_registros_online", return_value=online
        ), unittest.mock.patch.object(
            rbr.rero, "carregar_particoes_preservadas", return_value=particoes
        ), unittest.mock.patch.object(
            rbr.rero, "carregar_alvo_congelado", return_value=alvo_congelado
        ), unittest.mock.patch.object(
            rbr, "validar_estrutura_congelada", return_value={"bloqueios": []}
        ), unittest.mock.patch.object(
            rbr.efc, "validar_bundle_replay", return_value=resultado_cientifico
        ):
            diagnostico = rbr.executar(
                hash_esperado=rbr.REPLAY_INPUT_SHA256_ESPERADO_CANDIDATO,
                config_path=Path("nao-usado.json"),
                particoes_path=Path("nao-usado.csv"),
                allowlist_grupo_a=self.ALLOWLIST_GRUPO_A_INERTE,
                allowlist_grupo_b={},
            )
        self.assertEqual(diagnostico["status"], "candidato_recuperado")
        self.assertFalse(diagnostico["bundle_publicado"])
        self.assertEqual(diagnostico["replay_input_sha256_observado"], "HASH-FINAL-DE-TESTE")
        self.assertEqual(diagnostico["linhas"], 1)


class TestDiagnosticoSanitizado(unittest.TestCase):
    """TESTE OBRIGATORIO: diagnostico e sanitizado (nunca texto bruto).

    Usa cenarios 100% sinteticos com sentinelas (nunca IDs/texto reais dos
    GRUPOS A/B): se `executar()` vazasse qualquer valor bruto no
    diagnostico, seria exatamente este tipo de sentinela que apareceria."""

    ID_BRUTO_SENTINELA = "ID_BRUTO_PROIBIDO"
    DADO_BRUTO_SENTINELA = "DADO_BRUTO_PROIBIDO"

    def _sem_sentinelas(self, diagnostico: dict) -> None:
        import json
        bruto = json.dumps(diagnostico, ensure_ascii=False)
        self.assertNotIn(self.ID_BRUTO_SENTINELA, bruto)
        self.assertNotIn(self.DADO_BRUTO_SENTINELA, bruto)

    def test_diagnostico_bloqueado_grupo_a_vazio(self):
        diagnostico = rbr.executar(
            hash_esperado=rbr.REPLAY_INPUT_SHA256_ESPERADO_CANDIDATO,
            config_path=Path("nao-usado.json"),
            particoes_path=Path("nao-usado.csv"),
            allowlist_grupo_a={},
        )
        self._sem_sentinelas(diagnostico)

    def test_diagnostico_com_patch_aplicado_e_estrutura_ok_nao_vaza_nada(self):
        """Registro sintetico cujo ID BRUTO e cujo valor historico
        comprovado sao ambos sentinelas proibidas — prova que nem
        `ids_sha256_com_patch_aplicado`/`campos_alterados_por_id_sha256`
        nem `diagnostico_estrutural` jamais os repetem."""
        titulo_online = "titulo bem diferente do historico"
        online = [registro_online(self.ID_BRUTO_SENTINELA, titulo=titulo_online)]
        allowlist_sintetica = {
            sha(self.ID_BRUTO_SENTINELA): {"titulo": self.DADO_BRUTO_SENTINELA},
        }
        # grupo_sha256 congelado precisa bater com o texto JA PATCHEADO
        # (titulo=DADO_BRUTO_SENTINELA, demais campos = default de
        # registro_online) para o fluxo passar da checagem de grupo
        # textual e chegar ate a validacao cientifica mockada abaixo.
        grupo_pos_patch = rbr.cgt.hash_grupo([
            rbr.cgt.normalizar_texto(c)
            for c in (self.DADO_BRUTO_SENTINELA, "descricao", "", "")
        ])
        particoes = {
            sha(self.ID_BRUTO_SENTINELA): {"grupo_sha256": grupo_pos_patch, "outer_fold": 1},
        }
        alvo_congelado = {sha(self.ID_BRUTO_SENTINELA): {
            "categoria_historica": "Cat A", "referencia_humana": "Cat A", "outer_fold": 1,
        }}

        with unittest.mock.patch.object(
            rbr.rero, "ler_registros_online", return_value=online
        ), unittest.mock.patch.object(
            rbr.rero, "carregar_particoes_preservadas", return_value=particoes
        ), unittest.mock.patch.object(
            rbr.rero, "carregar_alvo_congelado", return_value=alvo_congelado
        ), unittest.mock.patch.multiple(
            rbr.rero, TOTAL_ESPERADO=1, FOLDS_ESPERADOS_PADRAO=[1],
        ), unittest.mock.patch.object(
            rbr.efc, "validar_bundle_replay",
            side_effect=rbr.efc.GateZeroBloqueado("parede de teste"),
        ):
            diagnostico = rbr.executar(
                hash_esperado=rbr.REPLAY_INPUT_SHA256_ESPERADO_CANDIDATO,
                config_path=Path("nao-usado.json"),
                particoes_path=Path("nao-usado.csv"),
                allowlist_grupo_a=allowlist_sintetica,
                allowlist_grupo_b={},
            )
        # confirma que o patch FOI de fato detectado e aplicado (nao e um
        # teste vazio) e que a estrutura passou (chegou ate a validacao
        # cientifica) — so entao verifica que nada vazou.
        self.assertEqual(
            diagnostico["ids_sha256_com_patch_aplicado"], [sha(self.ID_BRUTO_SENTINELA)]
        )
        self.assertEqual(
            diagnostico["campos_alterados_por_id_sha256"],
            {sha(self.ID_BRUTO_SENTINELA): ["titulo"]},
        )
        self.assertEqual(diagnostico["status"], "bloqueado_validacao_cientifica")
        self._sem_sentinelas(diagnostico)

    def test_diagnostico_de_grupo_textual_divergente_so_expoe_id_sha256(self):
        online = [registro_online(self.ID_BRUTO_SENTINELA, titulo=self.DADO_BRUTO_SENTINELA)]
        particoes = {
            sha(self.ID_BRUTO_SENTINELA): {
                "grupo_sha256": "grupo-nunca-vai-bater", "outer_fold": 1,
            }
        }
        alvo_congelado = {sha(self.ID_BRUTO_SENTINELA): {
            "categoria_historica": self.DADO_BRUTO_SENTINELA,
            "referencia_humana": self.DADO_BRUTO_SENTINELA,
            "outer_fold": 1,
        }}
        with unittest.mock.patch.object(
            rbr.rero, "ler_registros_online", return_value=online
        ), unittest.mock.patch.object(
            rbr.rero, "carregar_particoes_preservadas", return_value=particoes
        ), unittest.mock.patch.object(
            rbr.rero, "carregar_alvo_congelado", return_value=alvo_congelado
        ), unittest.mock.patch.multiple(
            rbr.rero, TOTAL_ESPERADO=1, FOLDS_ESPERADOS_PADRAO=[1],
        ):
            diagnostico = rbr.executar(
                hash_esperado=rbr.REPLAY_INPUT_SHA256_ESPERADO_CANDIDATO,
                config_path=Path("nao-usado.json"),
                particoes_path=Path("nao-usado.csv"),
                allowlist_grupo_a={sha(self.ID_BRUTO_SENTINELA): {"titulo": ""}},
                allowlist_grupo_b={},
            )
        self.assertEqual(diagnostico["status"], "bloqueado_grupo_textual_divergente")
        self.assertEqual(
            diagnostico["amostra_ids_sha256_grupo_divergente"],
            [sha(self.ID_BRUTO_SENTINELA)],
        )
        self._sem_sentinelas(diagnostico)


class TestSemDriveRevisionsApi(unittest.TestCase):
    """TESTE OBRIGATORIO: nenhuma Drive Revisions API e necessaria."""

    def test_modulo_nao_expoe_nenhuma_funcao_de_drive_api(self):
        for nome_proibido in (
            "buscar_revisao_historica", "_sessao_drive_autorizada",
            "carregar_registros_da_revisao",
        ):
            self.assertFalse(hasattr(rbr, nome_proibido), nome_proibido)

    def test_modulo_nao_referencia_googleapis_drive(self):
        """A palavra 'revisao' ainda aparece em prosa explicando POR QUE a
        Drive API foi removida (ver docstring do modulo) — o que importa e
        que nao ha URL da API nem chamada de rede para ela."""
        fonte = Path(rbr.__file__).read_text(encoding="utf-8")
        self.assertNotIn("googleapis.com", fonte)
        self.assertNotIn("AuthorizedSession", fonte)
        self.assertNotIn("openpyxl", fonte)

    def test_workflow_nao_instala_openpyxl_no_job_recover(self):
        workflow = (RAIZ / ".github" / "workflows" / "ensemble_fase2b_crossfit.yml") \
            .read_text(encoding="utf-8")
        inicio = workflow.index("bundle_recover:")
        trecho = workflow[inicio:]
        self.assertNotIn("openpyxl", trecho)


class TestNaoUsaGateZeroOnlineVivo(unittest.TestCase):
    """TESTE OBRIGATORIO: gate_zero() online permanece inalterada, e o
    RECOVER nunca a chama — usa exclusivamente `validar_bundle_replay`
    (compartilhada com `gate_zero_replay()`), que nunca recalcula R/Y a
    partir de M/Q atuais."""

    def test_modulo_recover_nao_referencia_gate_zero_vivo(self):
        fonte = Path(rbr.__file__).read_text(encoding="utf-8")
        self.assertNotIn("efc.gate_zero(", fonte)
        self.assertIn("efc.validar_bundle_replay(", fonte)

    def test_ensemble_fase2b_crossfit_expoe_validar_bundle_replay(self):
        self.assertTrue(hasattr(rbr.efc, "validar_bundle_replay"))
        self.assertTrue(hasattr(rbr.efc, "gate_zero_replay"))
        self.assertTrue(hasattr(rbr.efc, "gate_zero"))


class TestWorkflowNaoLiberaFitsNemPublicaCsv(unittest.TestCase):
    """TESTES OBRIGATORIOS: csv nao publicado, marcador nao libera fits,
    nenhuma escrita em planilha."""

    @classmethod
    def setUpClass(cls):
        import yaml

        caminho = RAIZ / ".github" / "workflows" / "ensemble_fase2b_crossfit.yml"
        cls.workflow = yaml.safe_load(caminho.read_text(encoding="utf-8"))
        cls.jobs = cls.workflow["jobs"]

    def test_job_bundle_recover_existe_e_so_depende_de_testes_e_autorizacao(self):
        job = self.jobs["bundle_recover"]
        self.assertEqual(set(job["needs"]), {"testes", "autorizacao"})
        self.assertIn("autorizado_replay_recover", job["if"])

    def test_bundle_recover_nao_aparece_no_needs_de_nenhum_job_de_fit(self):
        jobs_de_fit_ou_gate = (
            "gate_zero", "crossfit_fold", "agregar",
            "replica_a", "replica_b", "canario_comparar",
            "gate_zero_replay", "crossfit_fold_replay", "agregar_replay",
        )
        for nome in jobs_de_fit_ou_gate:
            needs = self.jobs[nome].get("needs", [])
            if isinstance(needs, str):
                needs = [needs]
            self.assertNotIn("bundle_recover", needs, nome)
            condicao = self.jobs[nome].get("if", "")
            self.assertNotIn("autorizado_replay_recover", condicao, nome)

    def test_bundle_recover_so_publica_diagnostico_json_sanitizado(self):
        job = self.jobs["bundle_recover"]
        passos_upload = [
            passo for passo in job["steps"]
            if passo.get("uses", "").startswith("actions/upload-artifact")
        ]
        self.assertEqual(len(passos_upload), 1)
        caminho_artifact = passos_upload[0]["with"]["path"]
        self.assertIn("recover_diagnostico.json", caminho_artifact)
        self.assertNotIn(".csv", caminho_artifact)

    def test_bundle_recover_nao_escreve_em_nenhuma_planilha(self):
        job = self.jobs["bundle_recover"]
        for passo in job["steps"]:
            run = passo.get("run", "")
            self.assertNotIn("escrever", run.lower())
            self.assertNotIn("gravar", run.lower())
            self.assertNotIn("--modo-replay", run)
            self.assertNotIn("REPLAY_SPREADSHEET_ID", run)

    def test_codigo_fonte_recover_nao_chama_escrita_de_planilha(self):
        """`.update(` fica de fora de proposito: `dict.update()` (usado em
        `montar_allowlist`/`aplicar_allowlist`) e uma chamada legitima sem
        relacao com gspread; as chamadas de escrita reais do gspread tem
        nomes mais especificos, cobertos abaixo."""
        fonte = Path(rbr.__file__).read_text(encoding="utf-8")
        for chamada_de_escrita in (
            ".append_row(", ".append_rows(", "escrever_aba",
            ".batch_update(", ".insert_row(", ".update_cell(",
            ".update_acell(", "abrir_worksheet",
        ):
            self.assertNotIn(chamada_de_escrita, fonte, chamada_de_escrita)


class TestGitignoreAllowlistGrupoB(unittest.TestCase):
    def test_replay_allowlist_grupo_b_local_json_esta_no_gitignore(self):
        conteudo = (RAIZ / ".gitignore").read_text(encoding="utf-8")
        linhas = [l.strip() for l in conteudo.splitlines()]
        self.assertIn("replay_allowlist_grupo_b.local.json", linhas)


if __name__ == "__main__":
    unittest.main()
