#!/usr/bin/env python3
"""Caracteriza os grupos de texto identico que receberam referencias humanas
diferentes.

O Passo 2 contou esses grupos e parou ai: 17 grupos, 85 linhas. O numero vinha
sendo lido no artigo como piso de erro irredutivel, leitura que a contagem
sozinha nao sustenta. Divergencia dentro de um grupo pode ter tres origens
distintas, com consequencias opostas para o texto:

  1. contexto nao textual  o mesmo texto descreve intervencoes de natureza
                           diferente, e a diferenca esta fora do texto; nenhum
                           classificador de texto pode resolve-la;
  2. erro de registro      um dos registros esta na categoria errada;
  3. inconsistencia de     o revisor decidiu de modo diferente em dois casos
     anotacao              indistinguiveis.

Este script nao decide entre as tres, porque decidir exigiria reexame caso a
caso do texto dos chamados. Ele mede o que separa a primeira das outras duas:
se as categorias em disputa pertencem a TIPOS de manutencao diferentes
(preventiva contra corretiva, por exemplo), a distincao depende da natureza da
intervencao, que o texto do chamado nao carrega. Se pertencem ao mesmo tipo, a
divergencia e interna a uma familia e as hipoteses 2 e 3 ficam abertas.

Ferramenta offline e sanitizada: le apenas artefatos versionados, com IDs ja
reduzidos a SHA-256, e nao publica texto de chamado.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tempo import agora_bahia  # noqa: E402
from tipo_manutencao import tipo_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "docs" / "dados"
MAPA_PADRAO = DADOS / "grupos_textuais_mapa.csv"
PREDICOES_PADRAO = DADOS / "retreino_canonico_predicoes.csv"
SAIDA_JSON_PADRAO = DADOS / "grupos_divergentes_canonicos.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "GRUPOS_DIVERGENTES.md"


def ler_mapa_grupos(caminho: Path) -> dict[str, str]:
    """`id_sha256` -> `grupo_sha256`, do mapa congelado no Passo 2."""
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        return {linha["id_sha256"]: linha["grupo_sha256"]
                for linha in csv.DictReader(arquivo)}


def ler_referencias(caminho: Path) -> dict[str, str]:
    """`id_sha256` -> referencia humana, das predicoes da rodada canonica.

    O arquivo tem uma linha por modelo; a referencia repete-se e e lida uma vez
    por chamado. E a unica fonte versionada que liga o ID reduzido a categoria
    de referencia sem expor texto.
    """
    referencias: dict[str, str] = {}
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            referencias.setdefault(linha["id_sha256"], linha["referencia_humana"])
    return referencias


def auditar(grupos: dict[str, str], referencias: dict[str, str]) -> dict[str, Any]:
    por_grupo: dict[str, list[str]] = defaultdict(list)
    for id_sha, grupo in grupos.items():
        if id_sha in referencias:
            por_grupo[grupo].append(referencias[id_sha])

    divergentes = {g: v for g, v in por_grupo.items() if len(set(v)) > 1}
    linhas_afetadas = sum(len(v) for v in divergentes.values())
    avaliadas = sum(len(v) for v in por_grupo.values())

    pares: Counter[tuple[str, ...]] = Counter()
    linhas_por_par: Counter[tuple[str, ...]] = Counter()
    for grupo, valores in divergentes.items():
        chave = tuple(sorted(set(valores)))
        pares[chave] += 1
        linhas_por_par[chave] += len(valores)

    detalhe = []
    grupos_entre_tipos = linhas_entre_tipos = 0
    for chave, quantidade in sorted(
            pares.items(), key=lambda item: (-linhas_por_par[item[0]], item[0])):
        tipos = sorted({tipo_manutencao(c) for c in chave})
        entre_tipos = len(tipos) > 1
        if entre_tipos:
            grupos_entre_tipos += quantidade
            linhas_entre_tipos += linhas_por_par[chave]
        detalhe.append({
            "categorias": list(chave),
            "tipos": tipos,
            "entre_tipos_de_manutencao": entre_tipos,
            "grupos": quantidade,
            "linhas": linhas_por_par[chave],
        })

    return {
        "schema_version": 1,
        "cobertura": {
            "linhas_no_mapa_de_grupos": len(grupos),
            "linhas_com_referencia_avaliada": avaliadas,
            "grupos_avaliados": len(por_grupo),
        },
        "divergencia": {
            "grupos": len(divergentes),
            "linhas": linhas_afetadas,
            "proporcao_das_linhas_avaliadas": (
                round(linhas_afetadas / avaliadas, 4) if avaliadas else 0.0),
        },
        "natureza": {
            "grupos_entre_tipos_de_manutencao": grupos_entre_tipos,
            "linhas_entre_tipos_de_manutencao": linhas_entre_tipos,
            "proporcao_das_linhas_divergentes": (
                round(linhas_entre_tipos / linhas_afetadas, 4)
                if linhas_afetadas else 0.0),
            "leitura": ("divergencia entre tipos depende da natureza da "
                        "intervencao, que nao esta no texto do chamado; "
                        "divergencia dentro do mesmo tipo deixa em aberto erro "
                        "de registro e inconsistencia de anotacao"),
        },
        "pares": detalhe,
        "ressalva": ("a contagem nao autoriza chamar o valor de piso de erro "
                     "irredutivel: parte dele e ambiguidade de taxonomia, e "
                     "separar as tres origens exige reexame caso a caso"),
        "gerado_em": agora_bahia(),
        "fontes": ["docs/dados/grupos_textuais_mapa.csv",
                   "docs/dados/retreino_canonico_predicoes.csv"],
        "script_origem": "src/auditar_grupos_divergentes.py",
    }


def montar_markdown(relatorio: dict[str, Any]) -> str:
    divergencia = relatorio["divergencia"]
    natureza = relatorio["natureza"]
    linhas = [
        "# Grupos de texto idêntico com referência humana divergente",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos,",
        "> descrições ou IDs de chamados.",
        "",
        f"**Gerado em:** {relatorio['gerado_em']}",
        "",
        "## Totais",
        "",
        "| Item | Total |",
        "|---|---:|",
        f"| Linhas avaliadas | {relatorio['cobertura']['linhas_com_referencia_avaliada']} |",
        f"| Grupos avaliados | {relatorio['cobertura']['grupos_avaliados']} |",
        f"| Grupos com referência divergente | {divergencia['grupos']} |",
        f"| Linhas afetadas | {divergencia['linhas']} |",
        f"| Proporção das linhas avaliadas | {divergencia['proporcao_das_linhas_avaliadas']:.4f} |",
        "",
        "## Natureza da divergência",
        "",
        f"- Grupos entre tipos de manutenção distintos: {natureza['grupos_entre_tipos_de_manutencao']}",
        f"- Linhas nesses grupos: {natureza['linhas_entre_tipos_de_manutencao']} "
        f"({natureza['proporcao_das_linhas_divergentes']:.4f} das linhas divergentes)",
        "",
        natureza["leitura"] + ".",
        "",
        "## Pares de categorias em disputa",
        "",
        "| Categorias | Tipos | Entre tipos | Grupos | Linhas |",
        "|---|---|---|---:|---:|",
    ]
    for par in relatorio["pares"]:
        linhas.append(
            f"| {' / '.join(par['categorias'])} | {', '.join(par['tipos'])} | "
            f"{'sim' if par['entre_tipos_de_manutencao'] else 'não'} | "
            f"{par['grupos']} | {par['linhas']} |")
    linhas += ["", "## Ressalva", "", relatorio["ressalva"] + ".", ""]
    return "\n".join(linhas)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapa", type=Path, default=MAPA_PADRAO)
    parser.add_argument("--predicoes", type=Path, default=PREDICOES_PADRAO)
    parser.add_argument("--saida-json", type=Path, default=SAIDA_JSON_PADRAO)
    parser.add_argument("--saida-md", type=Path, default=SAIDA_MD_PADRAO)
    args = parser.parse_args(argv)

    relatorio = auditar(ler_mapa_grupos(args.mapa), ler_referencias(args.predicoes))
    args.saida_json.write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.saida_md.write_text(montar_markdown(relatorio), encoding="utf-8")

    print(f"grupos_divergentes={relatorio['divergencia']['grupos']}")
    print(f"linhas={relatorio['divergencia']['linhas']}")
    print(f"linhas_entre_tipos={relatorio['natureza']['linhas_entre_tipos_de_manutencao']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
