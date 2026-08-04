#!/usr/bin/env python3
"""Tabelas A1 e A2 do apendice, regeradas a partir da rodada canonica.

Por que existe. As duas tabelas do apendice foram escritas a mao sobre a
execucao legada e nao sobrevivem a troca de rodada: a A1 fechava em 14.058 e a
A2 listava categorias que a rodada canonica nao usa, entre elas as raizes
legadas 'Projeto' e 'Revisao', que somam poucos chamados e ficaram fora das
particoes por falta de suporte. Corrigir celula a celula reintroduz o erro na
proxima rodada, entao a tabela passa a ser gerada.

A1  distribuicao das 50 categorias historicas sobre a base congelada, cujo
    total e 14.060. E o corpus, nao o denominador de metrica.

A2  as 41 categorias da referencia humana que entraram nas particoes, com tipo,
    volume, classe da curva ABC interna ao tipo e F1 do LinearSVC, mais o bloco
    das 9 categorias que ficaram fora e o motivo de cada exclusao. O
    denominador e 13.972.

Os criterios de tipo e de corte ABC nao sao reimplementados aqui: vem de
`tipo_manutencao` e de `recortes_canonicos`, que produziram os numeros do corpo
do artigo. Duplicar a regra faria o apendice divergir da Tabela 10 sem que
ninguem percebesse.

Somente leitura: nao escreve na planilha nem no artigo.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from recortes_canonicos import carregar, classificar_abc  # noqa: E402
from tempo import agora_bahia  # noqa: E402
from tipo_manutencao import TIPOS, sigla, tipo_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "docs" / "dados"
PREDICOES_PADRAO = DADOS / "retreino_canonico_predicoes.csv"
AUDITORIA_PADRAO = DADOS / "auditoria_base_canonica.json"
PARTICOES_PADRAO = DADOS / "particoes_canonicas.json"
SAIDA_JSON_PADRAO = DADOS / "tabelas_apendice_canonicas.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "TABELAS_APENDICE_CANONICAS.md"

MODELO_DE_REFERENCIA = "linear_svc"


def f1_por_categoria(pares: list[tuple[str, str]],
                     categorias: list[str]) -> dict[str, float]:
    """F1 de cada categoria, calculado sobre TODOS os pares.

    Mesma razao do `_f1_macro` de `recortes_canonicos`: restringir os rotulos e
    nao as linhas preserva os falsos positivos vindos de fora do recorte.
    """
    from sklearn.metrics import f1_score

    verdade = [v for v, _ in pares]
    predito = [p for _, p in pares]
    valores = f1_score(verdade, predito, labels=categorias,
                       average=None, zero_division=0)
    return {c: round(float(v), 4) for c, v in zip(categorias, valores)}


def montar_a1(auditoria: dict[str, Any]) -> dict[str, Any]:
    """Distribuicao historica sobre a base congelada."""
    distribuicao = [
        {"categoria": item["categoria"], "n": item["n"]}
        for item in auditoria["taxonomia_historica"]["distribuicao"]
    ]
    distribuicao.sort(key=lambda x: (-x["n"], x["categoria"]))
    return {
        "denominador": "corpus congelado",
        "total": sum(item["n"] for item in distribuicao),
        "categorias": len(distribuicao),
        "linhas": distribuicao,
    }


def montar_a2(pares: list[tuple[str, str]],
              particoes: dict[str, Any]) -> dict[str, Any]:
    """Categorias avaliadas, por tipo e classe ABC interna, mais as excluidas."""
    volumes: dict[str, int] = {}
    for verdade, _previsto in pares:
        volumes[verdade] = volumes.get(verdade, 0) + 1

    tipos = {c: tipo_manutencao(c) for c in volumes}
    total_por_tipo = {t: sum(n for c, n in volumes.items() if tipos[c] == t)
                      for t in TIPOS}

    # A classe ABC e interna ao tipo, igual a Tabela 10 do corpo: a categoria
    # compete por volume apenas com as do proprio tipo.
    classe_de: dict[str, str] = {}
    for t in TIPOS:
        do_tipo = [(c, n) for c, n in volumes.items() if tipos[c] == t]
        for nome, membros in classificar_abc(do_tipo).items():
            for c in membros:
                classe_de[c] = nome

    categorias = sorted(volumes)
    f1 = f1_por_categoria(pares, categorias)

    linhas = []
    for t in TIPOS:
        do_tipo = sorted(((c, n) for c, n in volumes.items() if tipos[c] == t),
                         key=lambda x: (-x[1], x[0]))
        for categoria, n in do_tipo:
            linhas.append({
                "categoria": categoria,
                "tipo": t,
                "sigla": sigla(t),
                "n": n,
                "proporcao_do_tipo": round(n / total_por_tipo[t], 4)
                if total_por_tipo[t] else 0.0,
                "classe": classe_de[categoria],
                "f1_linear_svc": f1[categoria],
            })

    excluidas = []
    for item in particoes.get("categorias_excluidas_por_suporte", []):
        excluidas.append({
            "categoria": item["categoria"],
            "linhas": item["linhas"],
            "motivo": "suporte",
            "detalhe": (f"{item['grupos_distintos']} grupos textuais distintos, "
                        f"insuficientes para {particoes['k']} dobras"),
        })
    for item in particoes.get("categorias_excluidas_por_sorteio", []):
        excluidas.append({
            "categoria": item["categoria"],
            "linhas": item["linhas"],
            "motivo": "sorteio",
            "detalhe": ("ausente de ao menos uma dobra apos o sorteio, na "
                        f"rodada {item['rodada']}"),
        })
    excluidas.sort(key=lambda x: (-x["linhas"], x["categoria"]))

    return {
        "denominador": "linhas avaliadas",
        "total": sum(volumes.values()),
        "categorias": len(volumes),
        "modelo_do_f1": MODELO_DE_REFERENCIA,
        "total_por_tipo": total_por_tipo,
        "linhas": linhas,
        "excluidas": excluidas,
        "linhas_excluidas": sum(item["linhas"] for item in excluidas),
    }


def montar_relatorio(predicoes: Path, auditoria: Path,
                     particoes: Path) -> dict[str, Any]:
    por_modelo = carregar(predicoes)
    if MODELO_DE_REFERENCIA not in por_modelo:
        raise SystemExit(f"modelo {MODELO_DE_REFERENCIA} ausente de {predicoes}")
    dados_auditoria = json.loads(auditoria.read_text(encoding="utf-8"))
    dados_particoes = json.loads(particoes.read_text(encoding="utf-8"))

    return {
        "schema_version": 1,
        "status": "concluido",
        "a1": montar_a1(dados_auditoria),
        "a2": montar_a2(por_modelo[MODELO_DE_REFERENCIA], dados_particoes),
        "criterios": {
            "tipo": "familia da categoria, conforme src/tipo_manutencao.py",
            "abc": ("percentual acumulado de volume dentro do proprio tipo, "
                    "corte A em 0.8 e B em 0.95; a categoria que cruza o corte "
                    "pertence a classe que ela fecha"),
            "f1": ("F1 do LinearSVC por categoria, calculado sobre todos os "
                   "pares para preservar falsos positivos vindos de fora"),
        },
        "origem": str(predicoes.relative_to(RAIZ)).replace("\\", "/"),
        "script_origem": "src/tabelas_apendice_canonicas.py",
        "gerado_em": agora_bahia(),
    }


def _milhar(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def _pct(v: float) -> str:
    return f"{v * 100:.2f}".replace(".", ",")


def _num(v: float) -> str:
    return f"{v:.4f}".replace(".", ",")


def renderizar_markdown(relatorio: dict[str, Any]) -> str:
    a1, a2 = relatorio["a1"], relatorio["a2"]
    linhas = [
        "# Tabelas do apêndice, regeradas da rodada canônica",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, "
        "descrições ou IDs de chamados.",
        "",
        f"**Gerado em:** {relatorio['gerado_em']}  ",
        f"**Origem:** `{relatorio['origem']}`",
        "",
        "## Critérios",
        "",
        f"- Tipo: {relatorio['criterios']['tipo']}.",
        f"- ABC: {relatorio['criterios']['abc']}.",
        f"- F1: {relatorio['criterios']['f1']}.",
        "",
        "## Tabela A1 — distribuição histórica sobre a base congelada",
        "",
        f"{a1['categorias']} categorias, {_milhar(a1['total'])} chamados.",
        "",
        "| Categoria histórica | Quantidade |",
        "|:---|---:|",
    ]
    for item in a1["linhas"]:
        linhas.append(f"| {item['categoria']} | {_milhar(item['n'])} |")
    linhas.append(f"| **Total geral** | **{_milhar(a1['total'])}** |")

    linhas += [
        "",
        "## Tabela A2 — categorias avaliadas na rodada canônica",
        "",
        f"{a2['categorias']} categorias e {_milhar(a2['total'])} chamados. "
        f"O F1 é do `{a2['modelo_do_f1']}`.",
        "",
        "| Categoria de referência | Tipo | n | % do tipo | Classe | F1 |",
        "|:---|:-:|---:|---:|:-:|---:|",
    ]
    tipo_corrente = None
    for item in a2["linhas"]:
        if item["tipo"] != tipo_corrente:
            tipo_corrente = item["tipo"]
            total = a2["total_por_tipo"][tipo_corrente]
            linhas.append(f"| **{tipo_corrente}** | **{item['sigla']}** | "
                          f"**{_milhar(total)}** | **100,00** | | |")
        linhas.append(
            f"| {item['categoria']} | {item['sigla']} | {_milhar(item['n'])} | "
            f"{_pct(item['proporcao_do_tipo'])} | {item['classe']} | "
            f"{_num(item['f1_linear_svc'])} |")

    linhas += [
        "",
        "### Categorias fora das partições",
        "",
        f"{len(a2['excluidas'])} categorias e {a2['linhas_excluidas']} linhas "
        "ficaram fora por não sustentarem as cinco dobras.",
        "",
        "| Categoria de referência | Linhas | Motivo |",
        "|:---|---:|:---|",
    ]
    for item in a2["excluidas"]:
        linhas.append(f"| {item['categoria']} | {item['linhas']} | "
                      f"{item['detalhe']} |")

    linhas += [
        "",
        "## Proveniência",
        "",
        f"- Script: `{relatorio['script_origem']}`.",
        "- Nenhuma escrita foi realizada na planilha nem no artigo.",
        "",
    ]
    return "\n".join(linhas)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--predicoes", type=Path, default=PREDICOES_PADRAO)
    p.add_argument("--auditoria", type=Path, default=AUDITORIA_PADRAO)
    p.add_argument("--particoes", type=Path, default=PARTICOES_PADRAO)
    p.add_argument("--saida-json", type=Path, default=SAIDA_JSON_PADRAO)
    p.add_argument("--saida-md", type=Path, default=SAIDA_MD_PADRAO)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    relatorio = montar_relatorio(args.predicoes, args.auditoria, args.particoes)
    args.saida_json.write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    args.saida_md.write_text(renderizar_markdown(relatorio), encoding="utf-8")
    a2 = relatorio["a2"]
    print(f"A1: {relatorio['a1']['categorias']} categorias, "
          f"{relatorio['a1']['total']} chamados")
    print(f"A2: {a2['categorias']} categorias, {a2['total']} chamados, "
          f"{len(a2['excluidas'])} excluidas com {a2['linhas_excluidas']} linhas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
