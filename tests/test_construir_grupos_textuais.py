from __future__ import annotations

import contextlib
import sys
import unittest
from pathlib import Path
from unittest import mock

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


@contextlib.contextmanager
def _aplicar(patches):
    with contextlib.ExitStack() as pilha:
        for p in patches:
            pilha.enter_context(p)
        yield


def _corpus_congelado_sintetico():
    """Corpus offline pequeno cujos fingerprints servem de baseline nos testes
    do gate, sem depender da base real de 14.060 linhas / 9.786 grupos.

    Sete linhas para que o maior grupo (tamanho 2) caiba no limite de uma
    dobra (ceil(7/5)=2): a identidade fica aprovavel e o status final permite
    testar main() prosseguindo ate `apto_para_particionar`.
    """
    registros = [
        registro("1", "porta emperrada", historico="Cat A", m="Correto"),
        registro("2", "porta emperrada", historico="Cat A",
                 m="Errado", q="Cat B"),
        registro("3", "lampada queimada"),
        registro("4", "vazamento no banheiro"),
        registro("5", "ar condicionado sem gelar"),
        registro("6", "torneira pingando"),
        registro("7", "janela quebrada"),
    ]
    return registros, cgt.agrupar(registros)


class TestValidarIdentidadeCongelada(unittest.TestCase):
    def setUp(self):
        self.registros, self.relatorio = _corpus_congelado_sintetico()
        self.baseline = dict(
            corpus_esperado=self.relatorio["corpus"]["linhas_nao_vazias"],
            grupos_esperado=self.relatorio["corpus"]["grupos_textuais"],
            mapa_sha256_esperado=self.relatorio["mapa_sha256"],
            hash_grupos_esperado=self.relatorio["hash_grupos_sha256"],
            grupos_divergentes_esperado=self.relatorio["rotulos_conflitantes"][
                "grupos_com_referencia_divergente"],
            linhas_afetadas_esperado=self.relatorio["rotulos_conflitantes"][
                "linhas_afetadas"],
        )

    def test_fingerprints_esperados_gate_aceita(self):
        self.assertTrue(cgt.validar_identidade_congelada(
            self.relatorio, **self.baseline))

    def test_mesmo_n_mapa_sha256_divergente_gate_bloqueia(self):
        params = dict(self.baseline, mapa_sha256_esperado="mapa-divergente")
        self.assertEqual(
            params["corpus_esperado"], self.relatorio["corpus"]["linhas_nao_vazias"])
        self.assertFalse(cgt.validar_identidade_congelada(self.relatorio, **params))

    def test_mesmo_n_hash_grupos_sha256_divergente_gate_bloqueia(self):
        params = dict(self.baseline, hash_grupos_esperado="grupos-divergente")
        self.assertEqual(
            params["corpus_esperado"], self.relatorio["corpus"]["linhas_nao_vazias"])
        self.assertFalse(cgt.validar_identidade_congelada(self.relatorio, **params))

    def test_numero_de_grupos_divergente_gate_bloqueia(self):
        params = dict(self.baseline, grupos_esperado=999)
        self.assertFalse(cgt.validar_identidade_congelada(self.relatorio, **params))

    def test_valores_de_conflito_divergentes_gate_bloqueia(self):
        params = dict(self.baseline, grupos_divergentes_esperado=0)
        self.assertFalse(cgt.validar_identidade_congelada(self.relatorio, **params))
        params = dict(self.baseline, linhas_afetadas_esperado=0)
        self.assertFalse(cgt.validar_identidade_congelada(self.relatorio, **params))

    def test_valores_de_conflito_congelados_nao_bloqueiam_por_existirem(self):
        # Os 17 grupos / 85 linhas divergentes fazem parte do congelamento
        # cientifico conhecido: o gate so bloqueia se o VALOR divergir do
        # baseline, nunca porque grupos conflitantes existem.
        self.assertGreater(self.baseline["grupos_divergentes_esperado"], 0)
        self.assertTrue(cgt.validar_identidade_congelada(
            self.relatorio, **self.baseline))

    def test_mensagem_de_erro_contem_obtido_esperado_e_explicacao(self):
        import io
        saida = io.StringIO()
        params = dict(self.baseline, mapa_sha256_esperado="mapa-esperado-diferente")
        cgt.validar_identidade_congelada(self.relatorio, saida=saida, **params)
        mensagem = saida.getvalue()
        self.assertIn(self.relatorio["mapa_sha256"], mensagem)
        self.assertIn("mapa-esperado-diferente", mensagem)
        self.assertIn("ARTIGO_CONGELADO", mensagem)

    def test_constantes_padrao_sao_as_do_artigo_congelado(self):
        self.assertEqual(cgt.CORPUS_COMPLETO_ESPERADO, 14060)
        self.assertEqual(cgt.GRUPOS_TEXTUAIS_ESPERADO, 9786)
        self.assertEqual(
            cgt.MAPA_SHA256_ESPERADO,
            "ab352b9424e31d2644ed6d075643adf562acc38767e0098eed77595e2dea0bb6")
        self.assertEqual(
            cgt.HASH_GRUPOS_SHA256_ESPERADO,
            "ad8557c109af55fd6f4a6cdd69d0eeb426c1602b66bade9473b6b8f0dc7dc32f")
        self.assertEqual(cgt.GRUPOS_COM_REFERENCIA_DIVERGENTE_ESPERADO, 17)
        self.assertEqual(cgt.LINHAS_AFETADAS_ESPERADO, 85)


class TestGateBloqueiaMainComBaseDivergente(unittest.TestCase):
    """Reproduz main() ate o gate sem tocar Google Sheets nem calcular o
    diagnostico caro de quase duplicados."""

    def setUp(self):
        self.registros, self.relatorio_esperado = _corpus_congelado_sintetico()
        self.tmp = Path(self.enterContext(
            __import__("tempfile").TemporaryDirectory()))
        self.config_path = self.tmp / "config.json"
        self.config_path.write_text('{"aba_principal": "teste"}', encoding="utf-8")
        self.json_path = self.tmp / "grupos.json"
        self.md_path = self.tmp / "grupos.md"
        self.mapa_path = self.tmp / "mapa.csv"

    def _contexto_offline(self, **constantes):
        argv = [
            "construir_grupos_textuais.py",
            "--config", str(self.config_path),
            "--json", str(self.json_path),
            "--markdown", str(self.md_path),
            "--mapa", str(self.mapa_path),
        ]
        patches = [
            mock.patch.object(sys, "argv", argv),
            mock.patch("construir_grupos_textuais.pl.abrir_planilha",
                       return_value=object()),
            mock.patch("construir_grupos_textuais.pl.id_planilha",
                       return_value="planilha-teste"),
            mock.patch("construir_grupos_textuais.ler_registros",
                       return_value=self.registros),
        ]
        nomes_constantes = {
            "corpus_esperado": "CORPUS_COMPLETO_ESPERADO",
            "grupos_esperado": "GRUPOS_TEXTUAIS_ESPERADO",
            "mapa_sha256_esperado": "MAPA_SHA256_ESPERADO",
            "hash_grupos_esperado": "HASH_GRUPOS_SHA256_ESPERADO",
            "grupos_divergentes_esperado": "GRUPOS_COM_REFERENCIA_DIVERGENTE_ESPERADO",
            "linhas_afetadas_esperado": "LINHAS_AFETADAS_ESPERADO",
        }
        for chave, valor in constantes.items():
            patches.append(mock.patch.object(cgt, nomes_constantes[chave], valor))
        return patches

    def test_identidade_divergente_retorna_nao_zero_e_nao_escreve_saidas(self):
        patches = self._contexto_offline(
            corpus_esperado=self.relatorio_esperado["corpus"]["linhas_nao_vazias"],
            grupos_esperado=self.relatorio_esperado["corpus"]["grupos_textuais"],
            mapa_sha256_esperado="mapa-divergente-de-proposito",
            hash_grupos_esperado=self.relatorio_esperado["hash_grupos_sha256"],
            grupos_divergentes_esperado=self.relatorio_esperado[
                "rotulos_conflitantes"]["grupos_com_referencia_divergente"],
            linhas_afetadas_esperado=self.relatorio_esperado[
                "rotulos_conflitantes"]["linhas_afetadas"],
        )
        with _aplicar(patches), \
             mock.patch("construir_grupos_textuais.diagnosticar_quase_duplicados") as m_diag, \
             mock.patch("construir_grupos_textuais.escrever_mapa") as m_mapa:
            codigo = cgt.main()

        self.assertNotEqual(codigo, 0)
        m_diag.assert_not_called()
        m_mapa.assert_not_called()
        self.assertFalse(self.json_path.exists())
        self.assertFalse(self.md_path.exists())
        self.assertFalse(self.mapa_path.exists())

    def test_identidade_correta_permite_main_prosseguir(self):
        patches = self._contexto_offline(
            corpus_esperado=self.relatorio_esperado["corpus"]["linhas_nao_vazias"],
            grupos_esperado=self.relatorio_esperado["corpus"]["grupos_textuais"],
            mapa_sha256_esperado=self.relatorio_esperado["mapa_sha256"],
            hash_grupos_esperado=self.relatorio_esperado["hash_grupos_sha256"],
            grupos_divergentes_esperado=self.relatorio_esperado[
                "rotulos_conflitantes"]["grupos_com_referencia_divergente"],
            linhas_afetadas_esperado=self.relatorio_esperado[
                "rotulos_conflitantes"]["linhas_afetadas"],
        )
        with _aplicar(patches):
            codigo = cgt.main()

        self.assertEqual(codigo, 0)
        self.assertTrue(self.json_path.exists())
        self.assertTrue(self.md_path.exists())
        self.assertTrue(self.mapa_path.exists())


if __name__ == "__main__":
    unittest.main()
