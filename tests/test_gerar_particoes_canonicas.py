from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import auditar_base_canonica as abc  # noqa: E402
import construir_grupos_textuais as cgt  # noqa: E402
import gerar_particoes_canonicas as gpc  # noqa: E402


def registro(id_, titulo, historico="Cat A", m="Correto", q=""):
    return {"id": id_, "titulo": titulo, "descricao_glpi": "",
            "titulo_osm": "", "descricao_osm": "",
            "categoria_historica": historico, "conferencia_glpi": m,
            "categoria_manual": q}


def mapa_grupos_congelados(registros):
    """Reconstroi o mapa `id_sha256 -> grupo_sha256` que o Passo 2 congelaria
    para os registros dados, do mesmo jeito que `construir_grupos_textuais`
    calcularia a partir do texto no momento do congelamento."""
    mapa = {}
    for r in registros:
        if not r.get("id"):
            continue
        digest = hashlib.sha256(r["id"].encode("utf-8")).hexdigest()
        normalizados = [cgt.normalizar_texto(r.get(c, ""))
                        for c in cgt.CAMPOS_TEXTUAIS]
        mapa[digest] = cgt.hash_grupo(normalizados)
    return mapa


def escrever_mapa_csv(caminho, mapa):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(["id_sha256", "grupo_sha256"])
        escritor.writerows(sorted(mapa.items()))


def hash_esperado_do_mapa(mapa):
    reconstruido = sorted(
        ({"id_sha256": k, "grupo_sha256": v} for k, v in mapa.items()),
        key=lambda x: (x["id_sha256"], x["grupo_sha256"]))
    return cgt._sha256_json(reconstruido)


def relatorio_particoes_congelado_valido():
    """Relatorio sintetico que bate com as constantes esperadas do Passo 3."""
    return {
        "k": gpc.K_ESPERADO,
        "semente": gpc.SEMENTE_ESPERADA,
        "linhas_particionadas": gpc.LINHAS_PARTICIONADAS_ESPERADAS,
        "grupos_particionados": gpc.GRUPOS_PARTICIONADOS_ESPERADOS,
        "categorias_particionadas": gpc.CATEGORIAS_PARTICIONADAS_ESPERADAS,
        "categorias_na_referencia": gpc.CATEGORIAS_NA_REFERENCIA_ESPERADAS,
        "linhas_excluidas_total": gpc.LINHAS_EXCLUIDAS_TOTAL_ESPERADAS,
        "mapa_sha256": gpc.MAPA_PARTICOES_SHA256_ESPERADO,
        "status": gpc.STATUS_ESPERADO,
        "linhas_sem_dobra": 0,
        "grupos_divididos_entre_dobras": 0,
        "registros_descartados": 0,
        "categorias_sem_suporte_em_alguma_dobra": [],
    }


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

    def test_base_congelada_ignora_linhas_novas_da_aba_viva(self):
        congelados = base_equilibrada()
        grupos = mapa_grupos_congelados(congelados)
        # A aba viva ganhou dois chamados novos, ainda sem revisão humana.
        vivos = congelados + [
            registro("9001", "chamado novo um", m=""),
            registro("9002", "chamado novo dois", m=""),
        ]
        r = gpc.montar_relatorio(vivos, grupos_congelados=grupos)
        self.assertTrue(r["base_congelada_aplicada"])
        self.assertEqual(r["linhas_da_base_congelada"], 80)
        self.assertEqual(r["linhas_vivas_fora_da_base_congelada"], 2)
        # O crescimento operacional não vira defeito de dados nem bloqueio.
        self.assertEqual(r["registros_descartados"], 0)
        self.assertEqual(r["linhas_particionadas"], 80)
        self.assertEqual(r["status"], "apto_para_treinar")

    def test_sem_base_congelada_a_linha_nova_volta_a_bloquear(self):
        vivos = base_equilibrada() + [registro("9001", "chamado novo", m="")]
        r = gpc.montar_relatorio(vivos)
        self.assertFalse(r["base_congelada_aplicada"])
        self.assertEqual(r["registros_descartados"], 1)
        self.assertEqual(r["status"], "bloqueado")

    def test_linha_congelada_sem_referencia_continua_bloqueando(self):
        registros = base_equilibrada()
        # Um registro do próprio corpus congelado perdeu a referência humana:
        # isso é defeito de dados, não crescimento da aba, e deve bloquear.
        registros.append(registro("9001", "dentro do corpus", m="Errado", q=""))
        grupos = mapa_grupos_congelados(registros)
        r = gpc.montar_relatorio(registros, grupos_congelados=grupos)
        self.assertEqual(r["linhas_vivas_fora_da_base_congelada"], 0)
        self.assertEqual(r["registros_descartados"], 1)
        self.assertEqual(r["status"], "bloqueado")

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


class TestBlindagemFailClosed(unittest.TestCase):
    """Lote 8D-3A: o Passo 3 usa o grupo textual congelado no Passo 2, valida
    a identidade do mapa do Passo 2, a referencia humana do Passo 1 e o
    resultado do particionamento, e bloqueia o protocolo nao canonico."""

    # A: mapa congelado correto e aceito.
    def test_A_mapa_congelado_correto_e_aceito(self):
        registros = base_equilibrada()
        mapa = mapa_grupos_congelados(registros)
        esperado = hash_esperado_do_mapa(mapa)
        with tempfile.TemporaryDirectory() as d:
            caminho = Path(d) / "mapa.csv"
            escrever_mapa_csv(caminho, mapa)
            ok, carregado = gpc.validar_mapa_congelado(
                caminho, mapa_sha256_esperado=esperado, corpus_esperado=len(mapa))
        self.assertTrue(ok)
        self.assertEqual(carregado, mapa)

    # B: mapa congelado adulterado bloqueia antes de particionar.
    def test_B_mapa_congelado_adulterado_bloqueia(self):
        registros = base_equilibrada()
        mapa = mapa_grupos_congelados(registros)
        esperado = hash_esperado_do_mapa(mapa)
        adulterado = dict(mapa)
        chave = next(iter(adulterado))
        adulterado[chave] = "0" * 64
        with tempfile.TemporaryDirectory() as d:
            caminho = Path(d) / "mapa.csv"
            escrever_mapa_csv(caminho, adulterado)
            ok, carregado = gpc.validar_mapa_congelado(
                caminho, mapa_sha256_esperado=esperado, corpus_esperado=len(mapa))
        self.assertFalse(ok)
        self.assertEqual(carregado, {})

    # C: texto vivo alterado, mas mapa congelado igual -> grupo usado
    # continua sendo o grupo congelado.
    def test_C_grupo_vem_do_mapa_congelado_mesmo_com_texto_vivo_alterado(self):
        r1 = registro("1", "titulo original", historico="Cat A")
        digest = hashlib.sha256(b"1").hexdigest()
        grupo_congelado = "a" * 64
        grupos = {digest: grupo_congelado}
        r1_alterado = dict(r1)
        r1_alterado["titulo"] = "texto totalmente diferente do congelamento"
        dados = gpc.preparar([r1_alterado], grupos_congelados=grupos)
        self.assertEqual(dados["grupos"], [grupo_congelado])

    # D: referencia humana alterada com o mesmo N bloqueia o gate do Passo 1.
    def test_D_referencia_humana_alterada_bloqueia_gate_passo1(self):
        base_regs = [
            {"id": "1", "categoria_historica": "Cat A",
             "conferencia_glpi": "Correto", "categoria_manual": ""},
            {"id": "2", "categoria_historica": "Cat B",
             "conferencia_glpi": "Correto", "categoria_manual": ""},
        ]
        original = abc.auditar(base_regs)
        hash_esperado = original["hash_base_canonica_sha256"]
        self.assertTrue(abc.validar_identidade_congelada(
            original, corpus_esperado=2, hash_esperado=hash_esperado))

        alterados = [dict(r) for r in base_regs]
        alterados[0]["categoria_historica"] = "Cat C"
        novo = abc.auditar(alterados)
        self.assertFalse(abc.validar_identidade_congelada(
            novo, corpus_esperado=2, hash_esperado=hash_esperado))

    # E: --sem-base-congelada bloqueia sem abrir a planilha nem escrever nada.
    def test_E_sem_base_congelada_bloqueia_e_nao_abre_planilha(self):
        argv = ["gerar_particoes_canonicas.py", "--sem-base-congelada"]
        with mock.patch("sys.argv", argv), \
             mock.patch.object(gpc.pl, "abrir_planilha") as m_abrir, \
             mock.patch.object(gpc, "escrever_mapa") as m_escrever:
            codigo = gpc.main()
        self.assertNotEqual(codigo, 0)
        m_abrir.assert_not_called()
        m_escrever.assert_not_called()

    # F: --k diferente de 5 bloqueia.
    def test_F_k_diferente_de_5_bloqueia(self):
        argv = ["gerar_particoes_canonicas.py", "--k", "3"]
        with mock.patch("sys.argv", argv), \
             mock.patch.object(gpc.pl, "abrir_planilha") as m_abrir:
            codigo = gpc.main()
        self.assertNotEqual(codigo, 0)
        m_abrir.assert_not_called()

    # G: --semente diferente de 42 bloqueia.
    def test_G_semente_diferente_de_42_bloqueia(self):
        argv = ["gerar_particoes_canonicas.py", "--semente", "7"]
        with mock.patch("sys.argv", argv), \
             mock.patch.object(gpc.pl, "abrir_planilha") as m_abrir:
            codigo = gpc.main()
        self.assertNotEqual(codigo, 0)
        m_abrir.assert_not_called()

    # H: --minimo-grupos diferente de 5 bloqueia.
    def test_H_minimo_grupos_diferente_de_5_bloqueia(self):
        argv = ["gerar_particoes_canonicas.py", "--minimo-grupos", "10"]
        with mock.patch("sys.argv", argv), \
             mock.patch.object(gpc.pl, "abrir_planilha") as m_abrir:
            codigo = gpc.main()
        self.assertNotEqual(codigo, 0)
        m_abrir.assert_not_called()

    # I: resultado de particao com mapa_sha256 divergente bloqueia antes de
    # escrever.
    def test_I_particoes_com_mapa_sha256_divergente_bloqueia(self):
        relatorio = relatorio_particoes_congelado_valido()
        relatorio["mapa_sha256"] = "0" * 64
        self.assertFalse(gpc.validar_particoes_congeladas(relatorio))

    # J: identidade correta das particoes e aceita.
    def test_J_particoes_com_identidade_correta_sao_aceitas(self):
        self.assertTrue(
            gpc.validar_particoes_congeladas(relatorio_particoes_congelado_valido()))

    # K: falha de identidade das particoes nao escreve mapa, JSON nem Markdown.
    def test_K_falha_de_identidade_das_particoes_nao_escreve_artefatos(self):
        registros = base_equilibrada()
        grupos = mapa_grupos_congelados(registros)
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            mapa_congelado = d / "mapa_passo2.csv"
            escrever_mapa_csv(mapa_congelado, grupos)
            config = d / "config.json"
            config.write_text(json.dumps({"aba_principal": "aba_teste"}),
                              encoding="utf-8")
            saida_json = d / "particoes.json"
            saida_md = d / "particoes.md"
            saida_mapa = d / "mapa_saida.csv"

            argv = ["gerar_particoes_canonicas.py",
                    "--config", str(config),
                    "--mapa-congelado", str(mapa_congelado),
                    "--json", str(saida_json),
                    "--markdown", str(saida_md),
                    "--mapa", str(saida_mapa)]

            with mock.patch("sys.argv", argv), \
                 mock.patch.object(gpc, "validar_mapa_congelado",
                                   return_value=(True, grupos)), \
                 mock.patch.object(gpc.pl, "abrir_planilha", return_value=object()), \
                 mock.patch.object(gpc.pl, "id_planilha", return_value="id-fake"), \
                 mock.patch.object(gpc.cgt, "ler_registros", return_value=registros), \
                 mock.patch.object(gpc.abc, "auditar",
                                   return_value={"status": "apto_para_congelar"}), \
                 mock.patch.object(gpc.abc, "validar_identidade_congelada",
                                   return_value=True), \
                 mock.patch.object(gpc, "escrever_mapa") as m_escrever:
                codigo = gpc.main()

            self.assertNotEqual(codigo, 0)
            m_escrever.assert_not_called()
            self.assertFalse(saida_json.exists())
            self.assertFalse(saida_md.exists())

    # L: crescimento operacional (linhas fora do mapa congelado) nao entra no
    # gate do Passo 1 e nao bloqueia a identidade congelada.
    def test_L_registros_fora_do_mapa_nao_entram_no_gate_passo1(self):
        congelados = [
            {"id": "1", "categoria_historica": "Cat A",
             "conferencia_glpi": "Correto", "categoria_manual": ""},
            {"id": "2", "categoria_historica": "Cat B",
             "conferencia_glpi": "Correto", "categoria_manual": ""},
        ]
        grupos = {hashlib.sha256(r["id"].encode("utf-8")).hexdigest(): "grupo-x"
                  for r in congelados}
        hash_esperado = abc.auditar(congelados)["hash_base_canonica_sha256"]

        vivos = congelados + [
            {"id": "9001", "categoria_historica": "Cat Nova",
             "conferencia_glpi": "", "categoria_manual": ""},
        ]

        # Sem filtrar, a linha operacional nova muda o corpus e quebraria o gate.
        auditoria_sem_filtro = abc.auditar(vivos)
        self.assertFalse(abc.validar_identidade_congelada(
            auditoria_sem_filtro, corpus_esperado=2, hash_esperado=hash_esperado))

        # Filtrando pelo mapa congelado, a linha nova fica de fora e o gate aceita.
        filtrados = gpc.filtrar_registros_congelados(vivos, grupos)
        self.assertEqual({r["id"] for r in filtrados}, {"1", "2"})
        auditoria_filtrada = abc.auditar(filtrados)
        self.assertTrue(abc.validar_identidade_congelada(
            auditoria_filtrada, corpus_esperado=2, hash_esperado=hash_esperado))

    # M: alteracao de referencia humana dentro do corpus congelado bloqueia.
    def test_M_alteracao_de_referencia_dentro_do_corpus_congelado_bloqueia(self):
        congelados = [
            {"id": "1", "categoria_historica": "Cat A",
             "conferencia_glpi": "Correto", "categoria_manual": ""},
            {"id": "2", "categoria_historica": "Cat B",
             "conferencia_glpi": "Correto", "categoria_manual": ""},
        ]
        grupos = {hashlib.sha256(r["id"].encode("utf-8")).hexdigest(): "grupo-x"
                  for r in congelados}
        hash_esperado = abc.auditar(congelados)["hash_base_canonica_sha256"]

        alterados = [dict(r) for r in congelados]
        alterados[0]["categoria_historica"] = "Cat C"  # mesmo N, referencia muda
        filtrados = gpc.filtrar_registros_congelados(alterados, grupos)
        self.assertEqual(len(filtrados), 2)
        auditoria = abc.auditar(filtrados)
        self.assertFalse(abc.validar_identidade_congelada(
            auditoria, corpus_esperado=2, hash_esperado=hash_esperado))

    # N: linha duplicada no CSV do Passo 2 bloqueia (o dict colapsaria a
    # duplicata antes do hash; a validacao agora usa a lista crua).
    def test_N_linha_duplicada_no_mapa_do_passo2_bloqueia(self):
        registros = base_equilibrada()
        mapa = mapa_grupos_congelados(registros)
        esperado = hash_esperado_do_mapa(mapa)
        with tempfile.TemporaryDirectory() as d:
            caminho = Path(d) / "mapa.csv"
            caminho.parent.mkdir(parents=True, exist_ok=True)
            linhas_ordenadas = sorted(mapa.items())
            with caminho.open("w", encoding="utf-8", newline="") as f:
                escritor = csv.writer(f)
                escritor.writerow(["id_sha256", "grupo_sha256"])
                escritor.writerows(linhas_ordenadas)
                # Linha repetida, identica a uma ja existente: o mapa logico
                # (colapsado em dict) ficaria igual, mas o CSV real mudou.
                escritor.writerow(linhas_ordenadas[0])
            ok, carregado = gpc.validar_mapa_congelado(
                caminho, mapa_sha256_esperado=esperado, corpus_esperado=len(mapa))
        self.assertFalse(ok)
        self.assertEqual(carregado, {})

    # O: linha operacional extra nao entra nas particoes nem muda o grupo dos
    # registros congelados.
    def test_O_linha_operacional_extra_nao_altera_grupos_nem_particoes(self):
        congelados = base_equilibrada()
        grupos = mapa_grupos_congelados(congelados)
        extra = registro("9001", "chamado novo", m="")
        vivos = congelados + [extra]

        sem_extra = gpc.montar_relatorio(congelados, grupos_congelados=grupos)
        com_extra = gpc.montar_relatorio(vivos, grupos_congelados=grupos)

        self.assertEqual(com_extra["linhas_vivas_fora_da_base_congelada"], 1)
        self.assertEqual(com_extra["linhas_particionadas"],
                         sem_extra["linhas_particionadas"])
        self.assertEqual(com_extra["grupos_particionados"],
                         sem_extra["grupos_particionados"])
        self.assertEqual(com_extra["mapa_sha256"], sem_extra["mapa_sha256"])

    # P: linha com id_sha256 vazio no CSV do Passo 2 bloqueia, em vez de ser
    # silenciosamente ignorada na leitura.
    def test_P_id_vazio_no_csv_bloqueia(self):
        registros = base_equilibrada()
        mapa = mapa_grupos_congelados(registros)
        esperado = hash_esperado_do_mapa(mapa)
        with tempfile.TemporaryDirectory() as d:
            caminho = Path(d) / "mapa.csv"
            caminho.parent.mkdir(parents=True, exist_ok=True)
            with caminho.open("w", encoding="utf-8", newline="") as f:
                escritor = csv.writer(f)
                escritor.writerow(["id_sha256", "grupo_sha256"])
                escritor.writerows(sorted(mapa.items()))
                # Linha adicional malformada: id_sha256 vazio, grupo preenchido.
                escritor.writerow(["", "a" * 64])
            ok, carregado = gpc.validar_mapa_congelado(
                caminho, mapa_sha256_esperado=esperado, corpus_esperado=len(mapa))
        self.assertFalse(ok)
        self.assertEqual(carregado, {})


if __name__ == "__main__":
    unittest.main()
