#!/usr/bin/env python3
"""Teste global de governanca dos GitHub Actions que escrevem no repositorio
(Lote 8H-C, fechamento do 8H). Varre os 15 workflows identificados no 8H-A
como writers Git e confirma, so por leitura estatica dos YAML, que:

- nenhum resolve conflito de merge automaticamente (-X theirs/-X ours);
- nenhum faz staging amplo (git add ./-A) ou push destrutivo (--force/-f,
  reset --hard);
- dados/estado_automacao.json nunca aparece num `git add` -- os quatro
  writers logicos dessa chave chamam exclusivamente
  src/persistir_estado_automacao.py;
- o workflow experimental do Transformer continua sem contents:write;
- nenhum arquivo do ARTIGO_CONGELADO vira alvo de um workflow operacional.

As checagens de comando (git add/-X theirs/etc.) sao feitas sobre o
conteudo dos blocos `run:` de cada step, com linhas de comentario bash
(iniciadas por `#`) removidas antes de comparar -- varios destes workflows
tem comentarios que EXPLICAM por que um comando NAO e usado, e um grep cru
do texto inteiro acusaria falso positivo nesses comentarios.

Nenhum workflow e executado, nenhuma rede e usada -- so leitura de YAML/JSON.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[1]
WORKFLOWS = RAIZ / ".github" / "workflows"
MANIFESTO = RAIZ / "docs" / "dados" / "MANIFESTO_ARTIGO_CONGELADO.json"

WRITERS_15 = [
    "artigo_pdf.yml",
    "estatistica.yml",
    "transformer_ft.yml",
    "benchmark_custo.yml",
    "curva_abc.yml",
    "relevancia_termos.yml",
    "avaliacao_final.yml",
    "auditar_conferencias.yml",
    "conferencia_derivada.yml",
    "distribuicao_categorias.yml",
    "dashboard.yml",
    "material_suplementar_pdf.yml",
    "avaliacao_bertimbau_holdout.yml",
    "comparar_modelos.yml",
    "multimodelo_classificacao.yml",
]

CHAVES_ESTADO_AUTOMACAO = {
    "avaliacao_final.yml": "avaliacao_final",
    "comparar_modelos.yml": "comparar_modelos",
    "multimodelo_classificacao.yml": "multimodelo_classificacao",
    "transformer_ft.yml": "transformer_ft",
}


def carregar_yaml(caminho: Path) -> dict:
    with caminho.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def blocos_run(doc: dict) -> str:
    partes = []
    for job in (doc.get("jobs") or {}).values():
        for step in job.get("steps") or []:
            if isinstance(step, dict) and "run" in step:
                partes.append(str(step["run"]))
    return "\n".join(partes)


def sem_comentarios_bash(texto: str) -> str:
    """Remove linhas de comentario bash (`# ...`) do texto de blocos run:.

    So remove linhas cujo conteudo, apos strip, comeca com '#' -- nao mexe
    em comentarios inline no fim de uma linha de comando real, que nenhum
    dos padroes checados aqui usa.
    """
    return "\n".join(l for l in texto.splitlines() if not l.strip().startswith("#"))


def executavel(nome_arquivo: str) -> str:
    doc = carregar_yaml(WORKFLOWS / nome_arquivo)
    return sem_comentarios_bash(blocos_run(doc))


def linhas_git_add(texto: str) -> list[str]:
    return re.findall(r"^\s*git add\b(.*)$", texto, re.MULTILINE)


class TestNenhumWorkflowFaltando(unittest.TestCase):
    def test_os_15_arquivos_existem(self):
        for nome in WRITERS_15:
            self.assertTrue((WORKFLOWS / nome).is_file(), nome)


class TestSemResolucaoAutomaticaDeConflito(unittest.TestCase):
    def test_sem_x_theirs(self):
        for nome in WRITERS_15:
            with self.subTest(arquivo=nome):
                self.assertNotIn("-X theirs", executavel(nome))

    def test_sem_x_ours(self):
        for nome in WRITERS_15:
            with self.subTest(arquivo=nome):
                self.assertNotIn("-X ours", executavel(nome))


class TestSemStagingAmploOuComandoDestrutivo(unittest.TestCase):
    def test_sem_git_add_ponto(self):
        for nome in WRITERS_15:
            with self.subTest(arquivo=nome):
                texto = executavel(nome)
                for args in linhas_git_add(texto):
                    self.assertNotEqual(args.strip(), ".", f"'git add .' em {nome}")

    def test_sem_git_add_dash_a(self):
        for nome in WRITERS_15:
            with self.subTest(arquivo=nome):
                self.assertNotIn("git add -A", executavel(nome))

    def test_sem_push_force(self):
        for nome in WRITERS_15:
            with self.subTest(arquivo=nome):
                texto = executavel(nome)
                self.assertNotRegex(texto, r"git push[^\n]*(--force|-f\b)")

    def test_sem_reset_hard(self):
        for nome in WRITERS_15:
            with self.subTest(arquivo=nome):
                self.assertNotIn("reset --hard", executavel(nome))


class TestEstadoAutomacaoSoViaHelper(unittest.TestCase):
    def test_nenhum_git_add_inclui_estado_automacao(self):
        for nome in WRITERS_15:
            with self.subTest(arquivo=nome):
                texto = executavel(nome)
                for args in linhas_git_add(texto):
                    self.assertNotIn("dados/estado_automacao.json", args)

    def test_os_quatro_writers_chamam_o_helper_com_a_chave_certa(self):
        for nome, chave in CHAVES_ESTADO_AUTOMACAO.items():
            with self.subTest(arquivo=nome):
                texto = executavel(nome)
                self.assertIn("persistir_estado_automacao.py", texto)
                self.assertIn(f"--chave {chave}", texto)
                self.assertIn("--aplicar", texto)
                self.assertNotIn("guard_automacao.py --registrar", texto)


class TestWorkflowExperimentalTransformerSemContentsWrite(unittest.TestCase):
    def test_sem_contents_write_em_nenhum_nivel(self):
        caminho = WORKFLOWS / "transformer_ft_experimentos.yml"
        self.assertTrue(caminho.is_file())
        doc = carregar_yaml(caminho)
        self.assertEqual(doc.get("permissions"), {"contents": "read"})
        for nome_job, job in (doc.get("jobs") or {}).items():
            self.assertNotIn(
                "permissions", job,
                f"job '{nome_job}' de transformer_ft_experimentos.yml nao deveria "
                "declarar permissions proprias (herda contents:read do topo)",
            )


class TestArtigoCongeladoNaoViraAlvoOperacional(unittest.TestCase):
    def test_nenhum_arquivo_do_manifesto_e_referenciado(self):
        manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        caminhos_congelados = [item["path"] for item in manifesto["arquivos"]]
        self.assertTrue(caminhos_congelados, "manifesto vazio -- nada a checar")

        for nome in WRITERS_15:
            texto_bruto = (WORKFLOWS / nome).read_text(encoding="utf-8")
            for congelado in caminhos_congelados:
                base = Path(congelado).name
                self.assertNotIn(
                    base, texto_bruto,
                    f"{base} (ARTIGO_CONGELADO) referenciado em {nome}",
                )


if __name__ == "__main__":
    unittest.main()
