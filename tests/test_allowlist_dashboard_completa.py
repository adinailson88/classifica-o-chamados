#!/usr/bin/env python3
"""Regressao: todo JSON que exportar_dashboard.py ou analise_shannon.py grava em
docs/dados precisa estar cadastrado na allowlist (FIXAS) do workflow
dashboard.yml -- senao o job falha em "Commit dos dados" com "BLOQUEADO:
arquivo(s) inesperado(s)" (fail-closed por design, ver comentario "Allowlist
default-deny" em .github/workflows/dashboard.yml).

Faltou cadastrar estabilidade_reclassificacao.json no PR #258 (Fase 2 do plano
de reducao de celulas do RECLASS_HISTORICO) e a primeira execucao real do
workflow em 04/09/2026 bloqueou o commit -- este teste fixa o comportamento
para a proxima vez que um JSON novo for adicionado ao dashboard.

So leitura estatica (regex sobre o codigo-fonte e o YAML). Nenhum workflow
roda, nenhuma rede e usada.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
WORKFLOW = RAIZ / ".github" / "workflows" / "dashboard.yml"

sys.path.insert(0, str(RAIZ / "src"))
from exportar_dashboard import ABAS  # noqa: E402


def extrair_fixas(texto: str) -> set[str]:
    m = re.search(r"FIXAS=\(\n(.*?)\n\s*\)", texto, re.S)
    if not m:
        raise AssertionError("bloco FIXAS=(...) nao encontrado em dashboard.yml")
    return {linha.strip() for linha in m.group(1).splitlines() if linha.strip()}


def extrair_literais_json(caminho: Path, padrao: str) -> set[str]:
    texto = caminho.read_text(encoding="utf-8")
    return set(re.findall(padrao, texto))


class TestAllowlistDashboardCompleta(unittest.TestCase):
    def test_todo_json_literal_de_exportar_dashboard_esta_na_allowlist(self):
        fixas = extrair_fixas(WORKFLOW.read_text(encoding="utf-8"))
        literais = extrair_literais_json(
            RAIZ / "src" / "exportar_dashboard.py", r'SAIDA / "([a-zA-Z0-9_]+\.json)"')
        faltando = literais - fixas
        self.assertFalse(
            faltando,
            f"JSON(s) escrito(s) por exportar_dashboard.py mas ausente(s) da "
            f"allowlist FIXAS em dashboard.yml: {sorted(faltando)}. Sem isso o "
            f"workflow bloqueia o commit com 'arquivo inesperado' (fail-closed).",
        )

    def test_todo_json_de_analise_shannon_esta_na_allowlist(self):
        fixas = extrair_fixas(WORKFLOW.read_text(encoding="utf-8"))
        literais = extrair_literais_json(
            RAIZ / "src" / "analise_shannon.py", r'salvar_json\(\s*"([a-zA-Z0-9_]+\.json)"')
        faltando = literais - fixas
        self.assertFalse(
            faltando, f"JSON(s) do analise_shannon.py fora da allowlist: {sorted(faltando)}")

    def test_chaves_fixas_de_abas_estao_na_allowlist(self):
        fixas = extrair_fixas(WORKFLOW.read_text(encoding="utf-8"))
        esperados = {f"{chave_json}.json" for chave_json, _ in ABAS}
        faltando = esperados - fixas
        self.assertFalse(faltando, f"chave(s) de ABAS fora da allowlist: {sorted(faltando)}")


if __name__ == "__main__":
    unittest.main()
