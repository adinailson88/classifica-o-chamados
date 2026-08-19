#!/usr/bin/env python3
"""Testes offline de privacidade e determinismo de detectar_duplicatas().

Cobre a correcao do Lote 8G-C-B: as chaves de duplicatas_exatas deixam de
embutir texto (bruto, normalizado ou truncado) e passam a ser um digest
SHA-256 nao reversivel de (categoria, texto_norm). Nao le/escreve planilha,
credenciais ou qualquer arquivo de dados do repositorio.
"""

from __future__ import annotations

import copy
import hashlib
import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bertimbau_coreset import detectar_duplicatas, norm_texto  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CHAVE_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def _registro(linha: int, categoria: str, texto: str) -> dict:
    return {"linha": linha, "categoria": categoria, "texto": texto, "texto_norm": norm_texto(texto)}


class TestDetectarDuplicatasPrivacidade(unittest.TestCase):
    def setUp(self) -> None:
        self.registros = [
            _registro(2, "Eletrica > Iluminacao", "lampada queimada na sala 12 do bloco B"),
            _registro(3, "Eletrica > Iluminacao", "Lampada  queimada NA sala 12 do bloco B"),
            _registro(4, "Hidraulica > Vazamento", "vazamento na torneira do banheiro"),
            _registro(5, "Hidraulica > Vazamento", "vazamento na torneira do banheiro"),
            _registro(6, "Hidraulica > Vazamento", "vazamento na torneira do banheiro"),
            _registro(7, "Civil > Porta", "porta emperrada sala 4"),
        ]

    def test_agrupamento_por_categoria_e_texto_norm_preservado(self):
        duplicatas, _ = detectar_duplicatas(self.registros, quase_limiar=0.9)
        grupos_por_linhas = sorted(sorted(v) for v in duplicatas.values())
        self.assertEqual(grupos_por_linhas, [[2, 3], [4, 5, 6]])

    def test_quantidade_de_linhas_por_grupo_correta(self):
        duplicatas, _ = detectar_duplicatas(self.registros, quase_limiar=0.9)
        tamanhos = sorted(len(v) for v in duplicatas.values())
        self.assertEqual(tamanhos, [2, 3])

    def test_todas_as_chaves_seguem_formato_sha256(self):
        duplicatas, _ = detectar_duplicatas(self.registros, quase_limiar=0.9)
        self.assertTrue(duplicatas, "esperava ao menos um grupo de duplicatas exatas")
        for chave in duplicatas:
            self.assertRegex(chave, CHAVE_RE)

    def test_nenhuma_chave_contem_texto_categoria_ou_prefixos(self):
        duplicatas, _ = detectar_duplicatas(self.registros, quase_limiar=0.9)
        fragmentos_proibidos = [
            "Eletrica", "Iluminacao", "Hidraulica", "Vazamento", "Civil", "Porta",
            "lampada", "queimada", "vazamento", "torneira", "banheiro", "porta",
            "sala", "bloco",
        ]
        for chave in duplicatas:
            chave_lower = chave.lower()
            for frag in fragmentos_proibidos:
                self.assertNotIn(frag.lower(), chave_lower)

    def test_textos_diferentes_geram_identificadores_diferentes(self):
        duplicatas, _ = detectar_duplicatas(self.registros, quase_limiar=0.9)
        self.assertEqual(len(duplicatas), len(set(duplicatas.keys())))

    def test_mesma_entrada_gera_identificador_deterministico(self):
        d1, _ = detectar_duplicatas(copy.deepcopy(self.registros), quase_limiar=0.9)
        d2, _ = detectar_duplicatas(copy.deepcopy(self.registros), quase_limiar=0.9)
        self.assertEqual(sorted(d1.keys()), sorted(d2.keys()))

    def test_identificador_bate_com_sha256_categoria_nul_texto_norm(self):
        duplicatas, _ = detectar_duplicatas(self.registros, quase_limiar=0.9)
        esperado_iluminacao = "sha256:" + hashlib.sha256(
            f"Eletrica > Iluminacao\0{norm_texto('lampada queimada na sala 12 do bloco B')}".encode("utf-8")
        ).hexdigest()
        self.assertIn(esperado_iluminacao, duplicatas)

    def test_contagem_de_duplicatas_exatas_nao_muda(self):
        duplicatas, _ = detectar_duplicatas(self.registros, quase_limiar=0.9)
        total_duplicatas = sum(len(v) - 1 for v in duplicatas.values())
        self.assertEqual(total_duplicatas, 3)  # (3-1) do grupo Hidraulica + (2-1) do grupo Eletrica

    def test_detectar_duplicatas_nao_altera_registros_de_entrada(self):
        antes = copy.deepcopy(self.registros)
        detectar_duplicatas(self.registros, quase_limiar=0.9)
        self.assertEqual(self.registros, antes)

    def test_nao_ha_grupo_para_registro_unico(self):
        registros = [_registro(2, "Civil > Porta", "porta emperrada sala 4")]
        duplicatas, _ = detectar_duplicatas(registros, quase_limiar=0.9)
        self.assertEqual(duplicatas, {})


class TestGovernancaClusterReportIgnorado(unittest.TestCase):
    def test_cluster_report_esta_no_gitignore(self):
        resultado = subprocess.run(
            ["git", "check-ignore", "-q", "docs/dados/bertimbau_cluster_report.json"],
            cwd=RAIZ,
            check=False,
        )
        self.assertEqual(
            resultado.returncode, 0,
            "docs/dados/bertimbau_cluster_report.json deveria estar coberto pelo .gitignore",
        )


if __name__ == "__main__":
    unittest.main()
