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
    def test_montar_bundle_junta_bruto_com_gate_zero(self):
        registros_patched = [registro_online("1", titulo="T1")]
        resultado_gate_zero = {
            "registros": [{
                "id_sha256": sha("1"),
                "categoria_historica": "Cat A",
                "referencia_humana": "Cat A",
                "grupo_sha256": "g1",
                "outer_fold": 2,
            }]
        }
        bundle = rbr.montar_bundle(resultado_gate_zero, registros_patched)
        self.assertEqual(len(bundle), 1)
        linha = bundle[0]
        self.assertEqual(linha["id_sha256"], sha("1"))
        self.assertEqual(linha["titulo"], "T1")
        self.assertEqual(linha["outer_fold"], 2)
        self.assertEqual(set(linha), set(rb.CAMPOS_BUNDLE))

    def test_montar_bundle_levanta_se_id_sha_sem_contraparte_bruta(self):
        resultado_gate_zero = {
            "registros": [{
                "id_sha256": "0" * 64,
                "categoria_historica": "Cat A",
                "referencia_humana": "Cat A",
                "grupo_sha256": "g1",
                "outer_fold": 1,
            }]
        }
        with self.assertRaises(rbr.RecuperacaoBloqueada):
            rbr.montar_bundle(resultado_gate_zero, [registro_online("1")])


class TestMontarDiagnosticoEstrutural(unittest.TestCase):
    """Cobre `montar_diagnostico_estrutural`, que reusa (sem duplicar) as
    mesmas funcoes de `recongelar_ensemble_online` que `gate_zero()` ja usa
    por dentro, so que expondo as amostras id_sha256/grupo_sha256 que
    `gate_zero()` nao expoe na excecao."""

    def test_reusa_as_quatro_funcoes_oficiais_na_mesma_sequencia(self):
        diagnostico_completo_fake = {
            "h_divergentes": 1, "amostra_h_divergentes": [sha("x")],
            "status": "bloqueado",
        }
        with unittest.mock.patch.object(
            rbr.rero, "carregar_particoes_preservadas", return_value={}
        ) as m_particoes, unittest.mock.patch.object(
            rbr.rero, "carregar_alvo_congelado", return_value={}
        ) as m_alvo, unittest.mock.patch.object(
            rbr.rero, "montar_base_atual", return_value={"base": {}, "faltantes_no_online": [],
                                                          "ids_duplicados_no_online": []}
        ) as m_base, unittest.mock.patch.object(
            rbr.rero, "montar_diagnostico", return_value=diagnostico_completo_fake
        ) as m_diag:
            resultado = rbr.montar_diagnostico_estrutural([registro_online("1")], Path("p.csv"))
        m_particoes.assert_called_once_with(Path("p.csv"))
        m_alvo.assert_called_once()
        m_base.assert_called_once()
        m_diag.assert_called_once()
        _, kwargs = m_diag.call_args
        self.assertEqual(kwargs["total_esperado"], rbr.rero.TOTAL_ESPERADO)
        self.assertEqual(kwargs["folds_esperados"], rbr.rero.FOLDS_ESPERADOS_PADRAO)
        self.assertEqual(resultado, diagnostico_completo_fake)

    def test_descarta_qualquer_campo_fora_da_allowlist_de_campos_permitidos(self):
        """Mesmo que `montar_diagnostico` (funcao oficial, fora do nosso
        controle) um dia passe a incluir H/R atuais ou outro campo nao
        sanitizado, `montar_diagnostico_estrutural` nunca repassa."""
        diagnostico_completo_fake = {
            "h_divergentes": 2,
            "amostra_h_divergentes": [sha("1")],
            "categoria_historica_atual_NUNCA_DEVERIA_VAZAR": "Categoria X",
            "referencia_humana_atual_NUNCA_DEVERIA_VAZAR": "Categoria Y",
        }
        with unittest.mock.patch.object(
            rbr.rero, "carregar_particoes_preservadas", return_value={}
        ), unittest.mock.patch.object(
            rbr.rero, "carregar_alvo_congelado", return_value={}
        ), unittest.mock.patch.object(
            rbr.rero, "montar_base_atual", return_value={"base": {}, "faltantes_no_online": [],
                                                          "ids_duplicados_no_online": []}
        ), unittest.mock.patch.object(
            rbr.rero, "montar_diagnostico", return_value=diagnostico_completo_fake
        ):
            resultado = rbr.montar_diagnostico_estrutural([registro_online("1")], Path("p.csv"))
        self.assertEqual(resultado, {"h_divergentes": 2, "amostra_h_divergentes": [sha("1")]})
        self.assertNotIn("categoria_historica_atual_NUNCA_DEVERIA_VAZAR", resultado)
        self.assertNotIn("referencia_humana_atual_NUNCA_DEVERIA_VAZAR", resultado)


class TestExecutarFluxo(unittest.TestCase):
    def test_com_grupo_a_e_b_fornecidos_chega_ate_gate_zero(self):
        with unittest.mock.patch.object(
            rbr.rero, "ler_registros_online", return_value=[registro_online("1")]
        ), unittest.mock.patch.object(
            rbr.efc, "gate_zero", side_effect=rbr.efc.GateZeroBloqueado("parede de teste")
        ) as m_gate_zero:
            diagnostico = rbr.executar(
                hash_esperado=rbr.REPLAY_INPUT_SHA256_ESPERADO_CANDIDATO,
                config_path=Path("nao-usado.json"),
                particoes_path=Path("nao-usado.csv"),
                allowlist_grupo_a={sha("1"): {"titulo": "x"}},
                allowlist_grupo_b={},
            )
        m_gate_zero.assert_called_once()
        self.assertEqual(diagnostico["status"], "bloqueado_gate_zero")
        # particoes_path fake -> recalculo do diagnostico estrutural falha
        # de forma controlada (nunca derruba a rodada, nunca mascara o
        # bloqueador original).
        self.assertIn("diagnostico_estrutural_erro", diagnostico)

    def test_bloqueio_do_gate_zero_enriquece_com_diagnostico_estrutural(self):
        """Quando o Gate Zero bloqueia, `executar()` recalcula o
        diagnostico estrutural (h/r/y divergentes, grupos cruzando dobras
        etc.) reusando as funcoes oficiais, e anexa so os campos
        sanitizados ao resultado."""
        diagnostico_estrutural_fake = {
            "h_divergentes": 0, "amostra_h_divergentes": [],
            "r_divergentes": 3, "amostra_r_divergentes": [sha("1"), sha("2")],
            "y_divergentes": 3, "amostra_y_divergentes": [sha("1"), sha("2")],
            "grupos_cruzando_dobras": 1,
            "amostra_grupos_cruzando_dobras": ["g" * 64],
            "status": "bloqueado",
        }
        with unittest.mock.patch.object(
            rbr.rero, "ler_registros_online", return_value=[registro_online("1")]
        ), unittest.mock.patch.object(
            rbr.efc, "gate_zero",
            side_effect=rbr.efc.GateZeroBloqueado("grupos_cruzando_dobras"),
        ), unittest.mock.patch.object(
            rbr, "montar_diagnostico_estrutural", return_value=diagnostico_estrutural_fake
        ) as m_estrutural:
            diagnostico = rbr.executar(
                hash_esperado=rbr.REPLAY_INPUT_SHA256_ESPERADO_CANDIDATO,
                config_path=Path("nao-usado.json"),
                particoes_path=Path("nao-usado.csv"),
                allowlist_grupo_a={sha("1"): {"titulo": "x"}},
                allowlist_grupo_b={},
            )
        m_estrutural.assert_called_once()
        self.assertEqual(diagnostico["diagnostico_estrutural"], diagnostico_estrutural_fake)
        self.assertNotIn("diagnostico_estrutural_erro", diagnostico)

    def test_hash_divergente_reporta_status_especifico_sem_publicar(self):
        atuais = [registro_online("1")]
        resultado_gate_zero = {
            "registros": [{
                "id_sha256": sha("1"),
                "categoria_historica": "Cat A",
                "referencia_humana": "Cat A",
                "grupo_sha256": rbr.cgt.hash_grupo(
                    [rbr.cgt.normalizar_texto(c) for c in
                     (atuais[0]["titulo"], atuais[0]["descricao_glpi"],
                      atuais[0]["titulo_osm"], atuais[0]["descricao_osm"])]
                ),
                "outer_fold": 1,
            }],
            "hashes": {"hash_corpus": "x"},
            "total_registros": 1, "total_grupos": 1,
            "h_dentro_de_c": 1, "h_fora_de_c": 0, "classes": ["Cat A"],
        }
        with unittest.mock.patch.object(
            rbr.rero, "ler_registros_online", return_value=atuais
        ), unittest.mock.patch.object(
            rbr.efc, "gate_zero", return_value=resultado_gate_zero
        ):
            diagnostico = rbr.executar(
                hash_esperado="0" * 64,
                config_path=Path("nao-usado.json"),
                particoes_path=Path("nao-usado.csv"),
                allowlist_grupo_a={sha("1"): {"titulo": "titulo"}},
                allowlist_grupo_b={},
            )
        self.assertEqual(diagnostico["status"], "hash_candidato_divergente")
        self.assertFalse(diagnostico["bundle_publicado"])
        self.assertIn("replay_input_sha256_observado", diagnostico)


class TestDiagnosticoSanitizado(unittest.TestCase):
    """TESTE OBRIGATORIO 7: diagnostico e sanitizado (nunca texto bruto).

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

    def test_diagnostico_com_patch_aplicado_nao_vaza_id_bruto_nem_valor_historico(self):
        """Registro sintetico cujo ID BRUTO e a propria sentinela proibida
        (prova que o ID bruto, mesmo que fosse essa string, nunca vazaria —
        so o id_sha256 aparece) e cujo valor historico comprovado tambem e
        uma sentinela (prova que o CONTEUDO do campo nunca vaza — so o
        NOME do campo, permitido por especificacao)."""
        atuais = [registro_online(self.ID_BRUTO_SENTINELA,
                                  descricao_osm="valor online, diferente do historico")]
        allowlist_sintetica = {
            sha(self.ID_BRUTO_SENTINELA): {"descricao_osm": self.DADO_BRUTO_SENTINELA},
        }
        with unittest.mock.patch.object(
            rbr.rero, "ler_registros_online", return_value=atuais
        ), unittest.mock.patch.object(
            rbr.efc, "gate_zero", side_effect=rbr.efc.GateZeroBloqueado("parede de teste")
        ):
            diagnostico = rbr.executar(
                hash_esperado=rbr.REPLAY_INPUT_SHA256_ESPERADO_CANDIDATO,
                config_path=Path("nao-usado.json"),
                particoes_path=Path("nao-usado.csv"),
                allowlist_grupo_a=allowlist_sintetica,
                allowlist_grupo_b={},
            )
        # confirma que o patch FOI de fato detectado e aplicado (nao e um
        # teste vazio) — so o id_sha256 e o nome do campo aparecem.
        self.assertEqual(
            diagnostico["ids_sha256_com_patch_aplicado"],
            [sha(self.ID_BRUTO_SENTINELA)],
        )
        self.assertEqual(
            diagnostico["campos_alterados_por_id_sha256"],
            {sha(self.ID_BRUTO_SENTINELA): ["descricao_osm"]},
        )
        self._sem_sentinelas(diagnostico)


class TestSemDriveRevisionsApi(unittest.TestCase):
    """TESTE OBRIGATORIO 8: nenhuma Drive Revisions API e necessaria."""

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


class TestWorkflowNaoLiberaFitsNemPublicaCsv(unittest.TestCase):
    """TESTES OBRIGATORIOS 6 (csv), 9 (fits) e 10 (escrita)."""

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
        """TESTE OBRIGATORIO 9: o marcador nao libera gate_zero cientifico,
        canario, crossfit, crossfit replay nem agregacao."""
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
        """TESTE OBRIGATORIO 6: o workflow nao publica
        replay_bundle_candidato.csv."""
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
        """TESTE OBRIGATORIO 10: nenhum passo do job escreve na Google
        Sheet."""
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
    """TESTE OBRIGATORIO 11."""

    def test_replay_allowlist_grupo_b_local_json_esta_no_gitignore(self):
        conteudo = (RAIZ / ".gitignore").read_text(encoding="utf-8")
        linhas = [l.strip() for l in conteudo.splitlines()]
        self.assertIn("replay_allowlist_grupo_b.local.json", linhas)


if __name__ == "__main__":
    unittest.main()
