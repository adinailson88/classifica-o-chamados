#!/usr/bin/env python3
"""Verifica se o corpus congelado carrega data de abertura do chamado.

A comparacao principal do artigo usa validacao cruzada agrupada por texto, que
estima generalizacao entre grupos textuais. Ela nao estima desempenho futuro:
para isso seria preciso separar treino, calibracao e teste no tempo, o que
exige uma variavel temporal por chamado.

Este script responde, de modo reproduzivel, se essa variavel existe. Ele
percorre o contrato de colunas da aba principal, declarado em `AGENTS.md`, e os
artefatos versionados da rodada canonica, coletando todo nome de campo e
classificando-o em tres situacoes:

  1. `candidato`            nome compativel com data do chamado (abertura,
                            criacao, periodo, ano, mes);
  2. `carimbo_de_execucao`  data de geracao do proprio artefato, que registra
                            quando o arquivo foi produzido e nada diz sobre
                            quando o chamado foi aberto;
  3. ignorado               os demais.

O veredito e `sem_variavel_temporal` quando nenhum candidato sobrevive. Nesse
caso a avaliacao temporal nao pode ser executada sobre os artefatos congelados,
e a limitacao correspondente deve constar do artigo.

Ferramenta offline e sanitizada: le apenas arquivos versionados, com IDs ja
reduzidos a SHA-256, e nao publica texto de chamado.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "docs" / "dados"
AGENTS_PADRAO = RAIZ / "AGENTS.md"
SAIDA_JSON_PADRAO = DADOS / "disponibilidade_temporal.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "DISPONIBILIDADE_TEMPORAL.md"

# Artefatos que definem o corpus congelado e as particoes da rodada canonica.
# Se a data de abertura existisse em algum lugar reproduzivel, estaria aqui.
ARTEFATOS_PADRAO = (
    "auditoria_base_canonica.json",
    "rodada_canonica.json",
    "grupos_textuais.json",
    "particoes_canonicas.json",
    "grupos_textuais_mapa.csv",
    "particoes_canonicas_mapa.csv",
    "retreino_canonico_predicoes.csv",
)

# Nome de campo compativel com data do proprio chamado.
PADRAO_CANDIDATO = re.compile(
    r"data|date|abertura|criacao|cria(c|ç)[aã]o|created|opened|abertos?|"
    r"timestamp|periodo|per[ií]odo|\bano\b|\bmes\b|\bm[eê]s\b|dt_",
    re.IGNORECASE)

# Campos cujo nome casa com o padrao mas registram quando o ARTEFATO foi
# gerado, e nao quando o chamado foi aberto.
CARIMBOS_DE_EXECUCAO = frozenset({
    "gerado_em", "gerado", "data_hora", "atualizado_em", "executado_em",
    "data_geracao", "medido_em",
})


def colunas_do_contrato(caminho: Path) -> list[str]:
    """Le o bloco `Colunas esperadas` de AGENTS.md.

    O contrato da aba principal e a fonte do corpus: nenhuma coluna fora dele
    chega aos modelos. Ler o bloco em vez de repetir a lista aqui evita que a
    auditoria e o contrato divirjam em silencio.
    """
    texto = caminho.read_text(encoding="utf-8")
    bloco = re.search(r"## Colunas esperadas\s*```text\n(.*?)```", texto, re.S)
    if not bloco:
        return []
    colunas = []
    for linha in bloco.group(1).splitlines():
        partes = linha.strip().split(None, 1)
        if len(partes) == 2:
            colunas.append(partes[1].strip())
    return colunas


def _campos_json(objeto: Any, prefixo: str = "") -> set[str]:
    """Todo nome de chave do JSON, em qualquer profundidade."""
    campos: set[str] = set()
    if isinstance(objeto, dict):
        for chave, valor in objeto.items():
            campos.add(f"{prefixo}{chave}")
            campos |= _campos_json(valor, f"{prefixo}{chave}.")
    elif isinstance(objeto, list):
        for item in objeto[:50]:
            campos |= _campos_json(item, prefixo)
    return campos


def campos_do_artefato(caminho: Path) -> list[str]:
    if caminho.suffix == ".csv":
        with caminho.open(encoding="utf-8", newline="") as arquivo:
            cabecalho = next(csv.reader(arquivo), [])
        return [c.strip() for c in cabecalho if c.strip()]
    return sorted(_campos_json(json.loads(caminho.read_text(encoding="utf-8"))))


def classificar(campo: str) -> str:
    folha = campo.rsplit(".", 1)[-1]
    if folha in CARIMBOS_DE_EXECUCAO:
        return "carimbo_de_execucao"
    if PADRAO_CANDIDATO.search(campo):
        return "candidato"
    return "ignorado"


def auditar(contrato: list[str], artefatos: list[Path]) -> dict[str, Any]:
    fontes: list[dict[str, Any]] = []

    def registrar(nome: str, natureza: str, campos: list[str],
                  presente: bool = True) -> None:
        classificados = {c: classificar(c) for c in campos}
        fontes.append({
            "fonte": nome,
            "natureza": natureza,
            "presente": presente,
            "campos": len(campos),
            "candidatos": sorted(c for c, s in classificados.items()
                                 if s == "candidato"),
            "carimbos_de_execucao": sorted(c for c, s in classificados.items()
                                           if s == "carimbo_de_execucao"),
        })

    registrar("AGENTS.md :: Colunas esperadas", "contrato da aba principal",
              contrato, presente=bool(contrato))
    for caminho in artefatos:
        if not caminho.exists():
            registrar(f"docs/dados/{caminho.name}", "artefato canonico", [],
                      presente=False)
            continue
        registrar(f"docs/dados/{caminho.name}", "artefato canonico",
                  campos_do_artefato(caminho))

    candidatos = sorted({c for f in fontes for c in f["candidatos"]})
    ausentes = [f["fonte"] for f in fontes if not f["presente"]]
    veredito = "variavel_temporal_disponivel" if candidatos else "sem_variavel_temporal"

    return {
        "schema_version": 1,
        "pergunta": ("o corpus congelado carrega data de abertura do chamado, "
                     "que permita separar treino, calibracao e teste no tempo?"),
        "veredito": veredito,
        "candidatos": candidatos,
        "fontes_ausentes": ausentes,
        "fontes": fontes,
        "consequencia": (
            "a avaliacao temporal nao pode ser executada sobre os artefatos "
            "congelados; a validacao cruzada agrupada estima generalizacao "
            "entre grupos textuais, e nao desempenho futuro sob deriva "
            "temporal, de modo que toda afirmacao de uso prospectivo precisa "
            "ser condicional"
            if veredito == "sem_variavel_temporal" else
            "ha campo candidato a data do chamado; conferir cobertura, "
            "consistencia e volume antes de desenhar a divisao temporal"),
        "carimbos_ignorados": (
            "campos como gerado_em registram quando o artefato foi produzido e "
            "nao quando o chamado foi aberto; nao servem a divisao temporal"),
        "gerado_em": agora_bahia(),
        "script_origem": "src/auditar_disponibilidade_temporal.py",
    }


def montar_markdown(relatorio: dict[str, Any]) -> str:
    linhas = [
        "# Disponibilidade de data de abertura no corpus congelado",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos,",
        "> descrições ou IDs de chamados.",
        "",
        f"**Gerado em:** {relatorio['gerado_em']}",
        "",
        f"**Pergunta:** {relatorio['pergunta']}",
        "",
        f"**Veredito:** `{relatorio['veredito']}`",
        "",
        "## Fontes inspecionadas",
        "",
        "| Fonte | Natureza | Presente | Campos | Candidatos a data do chamado | Carimbos de execução |",
        "|---|---|---|---:|---|---|",
    ]
    for fonte in relatorio["fontes"]:
        linhas.append(
            f"| {fonte['fonte']} | {fonte['natureza']} | "
            f"{'sim' if fonte['presente'] else 'não'} | {fonte['campos']} | "
            f"{', '.join(fonte['candidatos']) or '—'} | "
            f"{', '.join(fonte['carimbos_de_execucao']) or '—'} |")
    linhas += [
        "",
        "## Leitura",
        "",
        relatorio["consequencia"] + ".",
        "",
        relatorio["carimbos_ignorados"] + ".",
        "",
    ]
    return "\n".join(linhas)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agents", type=Path, default=AGENTS_PADRAO)
    parser.add_argument("--dados", type=Path, default=DADOS)
    parser.add_argument("--saida-json", type=Path, default=SAIDA_JSON_PADRAO)
    parser.add_argument("--saida-md", type=Path, default=SAIDA_MD_PADRAO)
    args = parser.parse_args(argv)

    relatorio = auditar(colunas_do_contrato(args.agents),
                        [args.dados / nome for nome in ARTEFATOS_PADRAO])
    args.saida_json.write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.saida_md.write_text(montar_markdown(relatorio), encoding="utf-8")

    print(f"veredito={relatorio['veredito']}")
    print(f"candidatos={len(relatorio['candidatos'])}")
    print(f"fontes_ausentes={len(relatorio['fontes_ausentes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
