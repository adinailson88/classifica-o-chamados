from __future__ import annotations

import hashlib
import os
import sys
import unittest
import unittest.mock
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import planilha as pl  # noqa: E402
import replay_bundle as rb  # noqa: E402


def sha(id_: str) -> str:
    return hashlib.sha256(id_.encode("utf-8")).hexdigest()


def registro_bundle(id_bruto, titulo="titulo", descricao_glpi="descricao",
                    titulo_osm="", descricao_osm="", categoria_historica="Cat A",
                    referencia_humana="Cat A", outer_fold=1, grupo_sha256=None):
    """Formato devolvido por `replay_bundle.ler_bundle_congelado`."""
    campos = [titulo, descricao_glpi, titulo_osm, descricao_osm]
    if grupo_sha256 is None:
        grupo_sha256 = rb.cgt.hash_grupo([rb.cgt.normalizar_texto(c) for c in campos])
    return {
        "id_sha256": sha(id_bruto),
        "titulo": titulo,
        "descricao_glpi": descricao_glpi,
        "titulo_osm": titulo_osm,
        "descricao_osm": descricao_osm,
        "categoria_historica": categoria_historica,
        "referencia_humana": referencia_humana,
        "grupo_sha256": grupo_sha256,
        "outer_fold": outer_fold,
    }


class TestLerBundleCongelado(unittest.TestCase):
    def _sh(self, linhas: list[list]):
        cabecalho = list(rb.CAMPOS_BUNDLE)
        return pl.LocalSpreadsheet({rb.ABA_BUNDLE: [cabecalho] + linhas})

    def test_le_registros_do_bundle_com_todos_os_9_campos(self):
        r = registro_bundle("1", titulo="titulo um", categoria_historica="Cat X")
        linha = [r[c] for c in rb.CAMPOS_BUNDLE]
        sh = self._sh([linha])
        with unittest.mock.patch.object(rb.pl, "abrir_planilha", return_value=sh):
            registros = rb.ler_bundle_congelado("qualquer-id")
        self.assertEqual(len(registros), 1)
        lido = registros[0]
        for campo in rb.CAMPOS_BUNDLE:
            if campo == "outer_fold":
                self.assertEqual(lido[campo], r[campo])
            else:
                self.assertEqual(lido[campo], r[campo], campo)

    def test_pula_linhas_totalmente_vazias(self):
        r = registro_bundle("1")
        linha = [r[c] for c in rb.CAMPOS_BUNDLE]
        linha_vazia = ["" for _ in rb.CAMPOS_BUNDLE]
        sh = self._sh([linha, linha_vazia])
        with unittest.mock.patch.object(rb.pl, "abrir_planilha", return_value=sh):
            registros = rb.ler_bundle_congelado("qualquer-id")
        self.assertEqual(len(registros), 1)

    def test_bundle_vazio_levanta_erro(self):
        sh = pl.LocalSpreadsheet({rb.ABA_BUNDLE: []})
        with unittest.mock.patch.object(rb.pl, "abrir_planilha", return_value=sh):
            with self.assertRaises(RuntimeError):
                rb.ler_bundle_congelado("qualquer-id")

    def test_outer_fold_aceita_numero_ou_texto(self):
        r = registro_bundle("1", outer_fold=3)
        linha_numero = [r[c] for c in rb.CAMPOS_BUNDLE]
        linha_texto = list(linha_numero)
        linha_texto[rb.CAMPOS_BUNDLE.index("outer_fold")] = "3"
        for linha in (linha_numero, linha_texto):
            sh = self._sh([linha])
            with unittest.mock.patch.object(rb.pl, "abrir_planilha", return_value=sh):
                registros = rb.ler_bundle_congelado("qualquer-id")
            self.assertEqual(registros[0]["outer_fold"], 3)


class TestIdReplaySpreadsheet(unittest.TestCase):
    def test_usa_variavel_de_ambiente_quando_definida(self):
        with unittest.mock.patch.dict(os.environ, {"REPLAY_SPREADSHEET_ID": "abc123"}):
            self.assertEqual(rb.id_replay_spreadsheet(), "abc123")

    def test_levanta_erro_sem_env_nem_arquivo_local(self):
        os.environ.pop("REPLAY_SPREADSHEET_ID", None)
        with unittest.mock.patch.object(rb, "ID_LOCAL_REPLAY", Path("caminho-inexistente.local")):
            with self.assertRaises(RuntimeError):
                rb.id_replay_spreadsheet()


class TestValidarGruposPorRegistro(unittest.TestCase):
    def test_sem_divergencia_quando_bundle_consistente(self):
        registros = [registro_bundle("1"), registro_bundle("2", titulo="outro titulo")]
        self.assertEqual(rb.validar_grupos_por_registro(registros), [])

    def test_detecta_grupo_sha256_corrompido(self):
        r = registro_bundle("1")
        r["grupo_sha256"] = "0" * 64  # nao bate com os 4 campos textuais
        self.assertEqual(rb.validar_grupos_por_registro([r]), [r["id_sha256"]])

    def test_detecta_apenas_o_registro_corrompido_entre_varios(self):
        ok1 = registro_bundle("1")
        corrompido = registro_bundle("2")
        corrompido["grupo_sha256"] = "f" * 64
        ok2 = registro_bundle("3")
        divergentes = rb.validar_grupos_por_registro([ok1, corrompido, ok2])
        self.assertEqual(divergentes, [corrompido["id_sha256"]])

    def test_sensivel_a_qualquer_um_dos_quatro_campos_textuais(self):
        base = registro_bundle("1", titulo="A", descricao_glpi="B",
                               titulo_osm="C", descricao_osm="D")
        for campo in rb.cgt.CAMPOS_TEXTUAIS:
            corrompido = dict(base)
            corrompido[campo] = base[campo] + " mudou"
            # grupo_sha256 continua o antigo (nao recalculado): deve divergir
            self.assertEqual(rb.validar_grupos_por_registro([corrompido]),
                             [corrompido["id_sha256"]], campo)


if __name__ == "__main__":
    unittest.main()
