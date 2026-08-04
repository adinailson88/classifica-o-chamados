from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matriz_proveniencia as mp  # noqa: E402

HASH = "abc123def456"


def montar_dados(diretorio: Path, hash_comum: str = HASH,
                 divergente: str | None = None) -> Path:
    dados = diretorio / "dados"
    dados.mkdir(parents=True, exist_ok=True)
    (dados / "rodada_canonica.json").write_text(json.dumps({
        "hash_corpus": hash_comum,
        "corpus": {"linhas": 13972, "categorias": 41, "dobras": 5},
    }), encoding="utf-8")
    for _rotulo, arquivo, _script in mp.CANONICOS:
        valor = divergente if (divergente and arquivo ==
                               "calibracao_canonica.json") else hash_comum
        (dados / arquivo).write_text(json.dumps({"hash_corpus": valor}),
                                     encoding="utf-8")
    for _rotulo, arquivo, _script in mp.CONGELAMENTO:
        (dados / arquivo).write_text("{}", encoding="utf-8")
    (dados / "estatistica.json").write_text(json.dumps({
        "acuracia_bootstrap": [{"modelo": "linear_svc", "acuracia": 0.8046}],
    }), encoding="utf-8")
    return dados


class TestCoerencia(unittest.TestCase):
    def test_todos_com_o_mesmo_hash_conferem(self):
        with tempfile.TemporaryDirectory() as d:
            dados = montar_dados(Path(d))
            r = mp.verificar_coerencia(dados)
        self.assertEqual(r["divergentes"], 0)
        self.assertEqual(r["hash_esperado"], HASH)

    def test_hash_divergente_e_apontado(self):
        with tempfile.TemporaryDirectory() as d:
            dados = montar_dados(Path(d), divergente="outro999")
            r = mp.verificar_coerencia(dados)
        self.assertEqual(r["divergentes"], 1)
        ruim = [a for a in r["artefatos"] if not a["coerente"]][0]
        self.assertIn("calibracao", ruim["arquivo"])

    def test_artefato_ausente_nao_conta_como_coerente(self):
        with tempfile.TemporaryDirectory() as d:
            dados = montar_dados(Path(d))
            (dados / "inferencia_canonica.json").unlink()
            r = mp.verificar_coerencia(dados)
        ausente = [a for a in r["artefatos"] if a["ausente"]][0]
        self.assertFalse(ausente["coerente"])
        self.assertEqual(r["divergentes"], 1)

    def test_hash_divergente_bloqueia_o_relatorio(self):
        with tempfile.TemporaryDirectory() as d:
            dados = montar_dados(Path(d), divergente="outro999")
            r = mp.montar_relatorio(dados, Path(d) / "inexistente.md")
        self.assertEqual(r["status"], "bloqueado")


class TestFormatos(unittest.TestCase):
    def test_gera_ponto_e_virgula(self):
        formas = mp._formatos(0.8046)
        self.assertIn("0.8046", formas)
        self.assertIn("0,8046", formas)
        self.assertIn("0,805", formas)

    def test_nao_gera_duas_casas(self):
        """Duas casas colidem com percentuais e células de tabela.

        A varredura chegou a acusar `0,69` numa coluna de percentual de volume
        como se fosse a acurácia legada do LSTM.
        """
        formas = mp._formatos(0.6915)
        self.assertNotIn("0,69", formas)
        self.assertNotIn("0.69", formas)


class TestAuditoriaDoArtigo(unittest.TestCase):
    def escrever(self, diretorio: Path, texto: str) -> Path:
        caminho = diretorio / "artigo.md"
        caminho.write_text(texto, encoding="utf-8")
        return caminho

    def test_encontra_numero_legado_e_reporta_a_linha(self):
        with tempfile.TemporaryDirectory() as d:
            caminho = self.escrever(Path(d), "linha um\nacuracia de 0,8046 aqui\n")
            r = mp.auditar_artigo(caminho, {"legado": ["0,8046"]})
        self.assertEqual(len(r["ocorrencias"]), 1)
        self.assertEqual(r["ocorrencias"][0]["linha"], 2)

    def test_nao_casa_numero_dentro_de_numero_maior(self):
        # '0,80' não pode casar dentro de '0,8046', senão o alarme vira ruído.
        with tempfile.TemporaryDirectory() as d:
            caminho = self.escrever(Path(d), "o valor 0,8046 aparece\n")
            r = mp.auditar_artigo(caminho, {"legado": ["0,80"]})
        self.assertEqual(r["ocorrencias"], [])

    def test_casa_numero_isolado_com_pontuacao_ao_redor(self):
        with tempfile.TemporaryDirectory() as d:
            caminho = self.escrever(Path(d), "chegou a 0,80, o que basta.\n")
            r = mp.auditar_artigo(caminho, {"legado": ["0,80"]})
        self.assertEqual(len(r["ocorrencias"]), 1)

    def test_conta_uma_ocorrencia_por_linha_e_por_valor(self):
        with tempfile.TemporaryDirectory() as d:
            caminho = self.escrever(Path(d), "0,8046 e 0.8046 na mesma linha\n")
            r = mp.auditar_artigo(caminho, {"legado": ["0,8046", "0.8046"]})
        self.assertEqual(len(r["ocorrencias"]), 1)

    def test_artigo_ausente_nao_quebra(self):
        r = mp.auditar_artigo(Path("nao_existe.md"), {"legado": ["1"]})
        self.assertFalse(r["lido"])
        self.assertEqual(r["ocorrencias"], [])

    def test_ocorrencias_saem_ordenadas_por_linha(self):
        with tempfile.TemporaryDirectory() as d:
            caminho = self.escrever(Path(d), "nada\n14.058 aqui\nnada\n0,8046 ali\n")
            r = mp.auditar_artigo(caminho, {"a": ["0,8046"], "b": ["14.058"]})
        self.assertEqual([o["linha"] for o in r["ocorrencias"]], [2, 4])


class TestMatriz(unittest.TestCase):
    def test_toda_grandeza_carrega_denominador_e_hash(self):
        with tempfile.TemporaryDirectory() as d:
            dados = montar_dados(Path(d))
            matriz = mp.montar_matriz(dados)
        self.assertTrue(matriz)
        for linha in matriz:
            self.assertEqual(linha["denominador"], 13972)
            self.assertEqual(linha["categorias"], 41)
            self.assertEqual(linha["particoes"], 5)
            self.assertEqual(linha["hash_corpus"], HASH[:12])
            self.assertTrue(linha["script"].startswith("src/"))

    def test_markdown_lista_as_ocorrencias_legadas(self):
        with tempfile.TemporaryDirectory() as d:
            dados = montar_dados(Path(d))
            artigo = Path(d) / "artigo.md"
            artigo.write_text("total de 14.058 chamados\n", encoding="utf-8")
            r = mp.montar_relatorio(dados, artigo)
            r["gerado_em"] = "agora"
            md = mp.renderizar_markdown(r)
        self.assertEqual(r["problemas"]["numeros_legados_ainda_no_artigo"], 1)
        self.assertIn("14.058", md)
        self.assertIn("Números legados", md)


if __name__ == "__main__":
    unittest.main()
