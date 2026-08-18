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
    # Mesma funcao que o validador usa (LF-normalizada), nao um sha256 cru:
    # o manifesto declara hashes nesse modo, entao as fixtures dos testes
    # B-F tambem precisam declarar nesse modo para nao confundir "conteudo
    # realmente mudou" com "so mudou hash_mode".
    return vac.sha256_lf_normalizado(caminho)


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
        "hash_mode": vac.HASH_MODE_ESPERADO,
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

    def test_g_portabilidade_crlf_lf(self):
        """CRLF <-> LF do MESMO conteudo semantico nao pode falsear violacao
        (motivo desta microcorrecao: passou nos testes A-F originais e so
        falhou no runner Ubuntu, porque o worktree Windows grava CRLF)."""
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            manifesto_path = construir_fixture(base)
            dados = base / "docs" / "dados"

            conteudo_lf = b"id,grupo\n1,A\n2,B\n3,C\n"
            caminho = dados / "mapa_portabilidade_teste.csv"
            caminho.write_bytes(conteudo_lf)
            sha_esperado = vac.sha256_lf_normalizado(caminho)

            manifesto = json.loads(manifesto_path.read_text(encoding="utf-8"))
            manifesto["arquivos"].append({
                "path": "docs/dados/mapa_portabilidade_teste.csv",
                "sha256": sha_esperado,
                "possui_hash_corpus": False,
                "papel": "fixture de teste de portabilidade CRLF/LF",
            })
            manifesto_path.write_text(json.dumps(manifesto), encoding="utf-8")

            # Conteudo com LF puro (equivalente a um checkout Ubuntu/CI): PASSA.
            self.assertEqual(_rodar(manifesto_path, base), 0)

            # MESMO conteudo semantico, so com CRLF (equivalente a um
            # checkout Windows com core.autocrlf=true): continua PASSANDO,
            # sem editar o manifesto -- e exatamente o cenario do bug real.
            conteudo_crlf = conteudo_lf.replace(b"\n", b"\r\n")
            caminho.write_bytes(conteudo_crlf)
            self.assertEqual(_rodar(manifesto_path, base), 0)

            # Mudanca REAL de um caractere (nao so de fim de linha): FALHA.
            conteudo_alterado = conteudo_crlf.replace(b"2,B", b"2,Z")
            caminho.write_bytes(conteudo_alterado)
            self.assertNotEqual(_rodar(manifesto_path, base), 0)

    def test_h_hash_mode_ausente_ou_divergente_falha(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            manifesto_path = construir_fixture(base)

            manifesto = json.loads(manifesto_path.read_text(encoding="utf-8"))
            manifesto["hash_mode"] = "sha256_puro"  # nao e o modo aceito
            manifesto_path.write_text(json.dumps(manifesto), encoding="utf-8")
            self.assertNotEqual(_rodar(manifesto_path, base), 0)

            del manifesto["hash_mode"]
            manifesto_path.write_text(json.dumps(manifesto), encoding="utf-8")
            self.assertNotEqual(_rodar(manifesto_path, base), 0)


if __name__ == "__main__":
    unittest.main()
