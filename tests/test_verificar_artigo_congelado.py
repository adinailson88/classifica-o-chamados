from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import verificar_artigo_congelado as vac  # noqa: E402

HASH = vac.HASH_CORPUS_ESPERADO


def _sha256(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def construir_fixture(base_dir: Path) -> Path:
    """Monta um baseline minimo, correto, em base_dir/docs/dados/.

    Nao toca em nenhum arquivo real do repositorio -- tudo aqui e escrito
    num diretorio temporario descartavel.
    """
    dados = base_dir / "docs" / "dados"
    dados.mkdir(parents=True, exist_ok=True)

    rodada = {
        "hash_corpus": HASH,
        "corpus": {"linhas": vac.CORPUS_MODELAGEM_ESPERADO,
                   "categorias": vac.CATEGORIAS_MODELAGEM_ESPERADO,
                   "dobras": vac.DOBRAS_ESPERADAS},
    }
    (dados / "rodada_canonica.json").write_text(json.dumps(rodada), encoding="utf-8")

    auditoria = {
        "corpus": {"linhas_nao_vazias": vac.CORPUS_COMPLETO_ESPERADO,
                   "ids_unicos": vac.CORPUS_COMPLETO_ESPERADO,
                   "referencias_validas": vac.CORPUS_COMPLETO_ESPERADO},
    }
    (dados / "auditoria_base_canonica.json").write_text(json.dumps(auditoria), encoding="utf-8")

    calibracao = {"hash_corpus": HASH, "ece_medio": 0.05}
    (dados / "calibracao_canonica.json").write_text(json.dumps(calibracao), encoding="utf-8")

    arquivos = []
    for nome, possui_hash in (
        ("rodada_canonica.json", True),
        ("auditoria_base_canonica.json", False),
        ("calibracao_canonica.json", True),
    ):
        caminho = dados / nome
        arquivos.append({
            "path": f"docs/dados/{nome}",
            "sha256": _sha256(caminho),
            "possui_hash_corpus": possui_hash,
            "papel": "fixture de teste",
        })

    manifesto = {
        "schema_version": vac.SCHEMA_VERSION_ESPERADA,
        "status": vac.STATUS_ESPERADO,
        "trilha": vac.TRILHA_ESPERADA,
        "manifesto_criado_a_partir_do_sha": "0" * 40,
        "invariantes": {
            "hash_corpus": HASH,
            "corpus_completo": vac.CORPUS_COMPLETO_ESPERADO,
            "corpus_modelagem": vac.CORPUS_MODELAGEM_ESPERADO,
            "categorias_modelagem": vac.CATEGORIAS_MODELAGEM_ESPERADO,
            "dobras": vac.DOBRAS_ESPERADAS,
        },
        "arquivos": arquivos,
    }
    manifesto_path = dados / "MANIFESTO_ARTIGO_CONGELADO.json"
    manifesto_path.write_text(json.dumps(manifesto), encoding="utf-8")
    return manifesto_path


def _rodar(manifesto_path: Path, base_dir: Path) -> int:
    sys.argv = ["verificar_artigo_congelado.py",
                "--manifesto", str(manifesto_path), "--base-dir", str(base_dir)]
    return vac.main()


class TestVerificarArtigoCongelado(unittest.TestCase):
    def test_a_manifesto_e_arquivos_corretos_passa(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            manifesto_path = construir_fixture(base)
            self.assertEqual(_rodar(manifesto_path, base), 0)

    def test_b_arquivo_protegido_alterado_falha(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            manifesto_path = construir_fixture(base)
            alvo = base / "docs" / "dados" / "calibracao_canonica.json"
            with alvo.open("a", encoding="utf-8") as f:
                f.write(" ")  # 1 byte a mais: hash de conteudo diverge
            self.assertNotEqual(_rodar(manifesto_path, base), 0)

    def test_c_arquivo_protegido_ausente_falha(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            manifesto_path = construir_fixture(base)
            (base / "docs" / "dados" / "calibracao_canonica.json").unlink()
            self.assertNotEqual(_rodar(manifesto_path, base), 0)

    def test_d_hash_corpus_cientifico_divergente_falha(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            manifesto_path = construir_fixture(base)
            dados = base / "docs" / "dados"
            caminho = dados / "rodada_canonica.json"

            # hash_corpus interno errado, mas o sha256 do MANIFESTO e
            # recalculado para bater com o novo conteudo -- isola a falha
            # na checagem semantica do hash cientifico, nao na checagem de
            # integridade fisica do arquivo (que e o alvo do teste B).
            corrompido = {
                "hash_corpus": "0" * 64,
                "corpus": {"linhas": vac.CORPUS_MODELAGEM_ESPERADO,
                           "categorias": vac.CATEGORIAS_MODELAGEM_ESPERADO,
                           "dobras": vac.DOBRAS_ESPERADAS},
            }
            caminho.write_text(json.dumps(corrompido), encoding="utf-8")

            manifesto = json.loads(manifesto_path.read_text(encoding="utf-8"))
            for entrada in manifesto["arquivos"]:
                if entrada["path"] == "docs/dados/rodada_canonica.json":
                    entrada["sha256"] = _sha256(caminho)
            manifesto_path.write_text(json.dumps(manifesto), encoding="utf-8")

            self.assertNotEqual(_rodar(manifesto_path, base), 0)

    def test_e_n_13972_alterado_falha(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            manifesto_path = construir_fixture(base)
            dados = base / "docs" / "dados"
            caminho = dados / "rodada_canonica.json"

            alterado = {
                "hash_corpus": HASH,
                "corpus": {"linhas": 14000,  # deveria ser 13972
                           "categorias": vac.CATEGORIAS_MODELAGEM_ESPERADO,
                           "dobras": vac.DOBRAS_ESPERADAS},
            }
            caminho.write_text(json.dumps(alterado), encoding="utf-8")

            manifesto = json.loads(manifesto_path.read_text(encoding="utf-8"))
            for entrada in manifesto["arquivos"]:
                if entrada["path"] == "docs/dados/rodada_canonica.json":
                    entrada["sha256"] = _sha256(caminho)
            manifesto_path.write_text(json.dumps(manifesto), encoding="utf-8")

            self.assertNotEqual(_rodar(manifesto_path, base), 0)

    def test_f_arquivo_extra_operacional_fora_do_manifesto_nao_falha(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            manifesto_path = construir_fixture(base)
            dados = base / "docs" / "dados"
            (dados / "estatistica_operacional_teste.json").write_text(
                json.dumps({"qualquer": "coisa"}), encoding="utf-8")
            self.assertEqual(_rodar(manifesto_path, base), 0)


if __name__ == "__main__":
    unittest.main()
