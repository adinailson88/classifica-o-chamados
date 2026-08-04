#!/usr/bin/env python3
"""Recortes por tipo de manutencao e por volume, sobre a rodada canonica.

Ferramenta offline: le somente `retreino_canonico_predicoes.csv`, produzido
pela rodada canonica, e nao toca na planilha nem retreina modelo algum. Refaz,
sob o protocolo novo, os recortes consolidados em 02/08/2026 no item 0.31 do
CONTEXTO.md, que ate aqui existiam apenas para a execucao legada.

Produz tres leituras, que respondem a perguntas diferentes:

    por_tipo     recorte da tarefa de 41 categorias dentro de cada tipo. Diz
                 onde o modelo erra mais.
    tarefa_tipo  verdade e predicao projetadas para Preventiva, Corretiva e
                 Nao manutencao, medidas como problema de tres classes. Diz se
                 o modelo distingue a natureza do servico, independentemente de
                 acertar a folha da taxonomia.
    curva_abc    categorias ordenadas por volume e agrupadas em classes A, B e
                 C pelo percentual acumulado, com a metrica recalculada dentro
                 de cada classe. Diz quanto da distancia entre acuracia e F1
                 macro vem da cauda.

A curva ABC tambem e recalculada DENTRO de cada tipo, sobre o volume daquele
tipo, porque a cauda de preventiva e a de corretiva nao sao a mesma cauda.

Os cortes de 80% e 95% e o criterio de tipo por familia sao os mesmos da
execucao legada, para que os recortes sejam comparaveis entre protocolos ainda
que os numeros nao sejam.
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

from tipo_manutencao import TIPOS, tipo_manutencao  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "docs" / "dados"
PREDICOES_PADRAO = DADOS / "retreino_canonico_predicoes.csv"
MANIFESTO_PADRAO = DADOS / "rodada_canonica.json"
SAIDA_JSON_PADRAO = DADOS / "recortes_canonicos.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "RECORTES_CANONICOS.md"

CORTE_A = 0.80
CORTE_B = 0.95


def carregar(caminho: Path) -> dict[str, list[tuple[str, str]]]:
    """Pares (referencia, previsto) por modelo."""
    por_modelo: dict[str, list[tuple[str, str]]] = defaultdict(list)
    with caminho.open("r", encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            por_modelo[linha["modelo"]].append(
                (linha["referencia_humana"], linha["previsto"]))
    return dict(por_modelo)


def _f1_macro(pares: list[tuple[str, str]], rotulos: list[str]) -> float:
    """F1 macro restrito a `rotulos`, calculado sobre TODOS os pares.

    Restringir os rotulos e nao os pares e deliberado: se o recorte descartasse
    as linhas de fora, um chamado de classe C previsto como classe A deixaria de
    contar como falso positivo de A, e o F1 da classe A subiria artificialmente.
    """
    if not rotulos:
        return 0.0
    from sklearn.metrics import f1_score
    verdade = [v for v, _ in pares]
    predito = [p for _, p in pares]
    return round(float(f1_score(verdade, predito, labels=rotulos,
                                average="macro", zero_division=0)), 4)


def _acuracia(pares: list[tuple[str, str]]) -> float:
    if not pares:
        return 0.0
    return round(sum(1 for v, p in pares if v == p) / len(pares), 4)


def classificar_abc(volumes: list[tuple[str, int]], corte_a: float = CORTE_A,
                    corte_b: float = CORTE_B) -> dict[str, list[str]]:
    """Classes A, B e C pelo percentual acumulado de volume.

    A categoria que cruza o corte pertence a classe que ela fecha, convencao
    identica a de `curva_abc_categorias.py`.
    """
    total = sum(n for _c, n in volumes)
    classes: dict[str, list[str]] = {"A": [], "B": [], "C": []}
    acumulado = 0
    for categoria, n in sorted(volumes, key=lambda x: (-x[1], x[0])):
        anterior = acumulado / total if total else 0.0
        acumulado += n
        if anterior < corte_a:
            classes["A"].append(categoria)
        elif anterior < corte_b:
            classes["B"].append(categoria)
        else:
            classes["C"].append(categoria)
    return classes


def recorte_por_tipo(pares: list[tuple[str, str]]) -> list[dict[str, Any]]:
    """Metricas da tarefa de 41 categorias, restritas as categorias de cada tipo."""
    saida = []
    for tipo in TIPOS:
        rotulos = sorted({v for v, _ in pares if tipo_manutencao(v) == tipo})
        do_tipo = [(v, p) for v, p in pares if tipo_manutencao(v) == tipo]
        saida.append({
            "tipo": tipo,
            "categorias": len(rotulos),
            "chamados": len(do_tipo),
            "acuracia": _acuracia(do_tipo),
            "macro_f1": _f1_macro(pares, rotulos),
        })
    return saida


def tarefa_de_tipo(pares: list[tuple[str, str]]) -> dict[str, Any]:
    """Verdade e predicao projetadas para os tres tipos."""
    from sklearn.metrics import f1_score
    verdade = [tipo_manutencao(v) for v, _ in pares]
    predito = [tipo_manutencao(p) for _, p in pares]
    presentes = [t for t in TIPOS if t in set(verdade)]
    por_tipo = f1_score(verdade, predito, labels=presentes, average=None,
                        zero_division=0)
    confusao = Counter(zip(verdade, predito))
    return {
        "acuracia": round(sum(1 for v, p in zip(verdade, predito) if v == p)
                          / len(pares), 4) if pares else 0.0,
        "macro_f1": round(float(f1_score(verdade, predito, labels=presentes,
                                         average="macro", zero_division=0)), 4),
        "f1_por_tipo": {t: round(float(v), 4) for t, v in zip(presentes, por_tipo)},
        "confusao": [{"verdade": v, "previsto": p, "n": n}
                     for (v, p), n in sorted(confusao.items())],
    }


def curva_abc(pares: list[tuple[str, str]],
              restrito_a: str | None = None) -> list[dict[str, Any]]:
    """Classes de volume e metrica dentro de cada classe.

    Com `restrito_a`, o volume acumulado e o do proprio tipo, porque a cauda de
    preventiva nao e a mesma cauda de corretiva.
    """
    if restrito_a is None:
        volumes = Counter(v for v, _ in pares)
    else:
        volumes = Counter(v for v, _ in pares if tipo_manutencao(v) == restrito_a)
    classes = classificar_abc(list(volumes.items()))
    saida = []
    total = sum(volumes.values())
    for nome in ("A", "B", "C"):
        rotulos = classes[nome]
        chamados = sum(volumes[c] for c in rotulos)
        da_classe = [(v, p) for v, p in pares if v in set(rotulos)]
        saida.append({
            "classe": nome,
            "categorias": len(rotulos),
            "chamados": chamados,
            "proporcao_do_volume": round(chamados / total, 4) if total else 0.0,
            "acuracia": _acuracia(da_classe),
            "macro_f1": _f1_macro(pares, rotulos),
        })
    return saida


def montar_relatorio(por_modelo: dict[str, list[tuple[str, str]]],
                     manifesto: dict[str, Any] | None = None) -> dict[str, Any]:
    modelos = []
    for nome, pares in sorted(por_modelo.items()):
        modelos.append({
            "modelo": nome,
            "acuracia_global": _acuracia(pares),
            "por_tipo": recorte_por_tipo(pares),
            "tarefa_tipo": tarefa_de_tipo(pares),
            "curva_abc": curva_abc(pares),
            "curva_abc_por_tipo": {t: curva_abc(pares, restrito_a=t) for t in TIPOS},
        })
    return {
        "schema_version": 1,
        "status": "concluido",
        "hash_corpus": (manifesto or {}).get("hash_corpus"),
        "origem": "docs/dados/retreino_canonico_predicoes.csv",
        "criterios": {
            "tipo": ("familia da categoria, conforme src/tipo_manutencao.py; "
                     "Preventiva, Corretiva e Nao manutencao"),
            "abc": (f"percentual acumulado de volume, corte A em {CORTE_A} e "
                    f"B em {CORTE_B}; a categoria que cruza o corte pertence a "
                    "classe que ela fecha"),
            "f1_restrito": ("o F1 de um recorte usa apenas os rotulos daquele "
                            "recorte, mas todos os pares, para que falsos "
                            "positivos vindos de fora continuem contando"),
        },
        "modelos": modelos,
    }


def renderizar_markdown(relatorio: dict[str, Any]) -> str:
    linhas = [
        "# Recortes por tipo de manutenção e por volume",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.",
        "",
        f"**Gerado em:** {relatorio.get('gerado_em', 'não informado')}  ",
        f"**Hash do corpus:** `{relatorio.get('hash_corpus') or 'não informado'}`",
        "",
        "## Critérios",
        "",
        f"- Tipo: {relatorio['criterios']['tipo']}.",
        f"- ABC: {relatorio['criterios']['abc']}.",
        f"- F1 de recorte: {relatorio['criterios']['f1_restrito']}.",
        "",
        "## Tarefa de tipo",
        "",
        "Verdade e predição projetadas para os três tipos. Responde se o modelo "
        "distingue a natureza do serviço, independentemente de acertar a folha.",
        "",
        "| Modelo | Acurácia | Macro-F1 | " + " | ".join(TIPOS) + " |",
        "|---|---:|---:|" + "---:|" * len(TIPOS),
    ]
    for m in sorted(relatorio["modelos"], key=lambda x: -x["tarefa_tipo"]["acuracia"]):
        t = m["tarefa_tipo"]
        celulas = " | ".join(str(t["f1_por_tipo"].get(x, "—")) for x in TIPOS)
        linhas.append(f"| {m['modelo']} | {t['acuracia']} | {t['macro_f1']} | {celulas} |")

    linhas += [
        "",
        "## Recorte por tipo, na tarefa de categoria",
        "",
        "| Modelo | Tipo | Categorias | Chamados | Acurácia | Macro-F1 |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for m in sorted(relatorio["modelos"], key=lambda x: x["modelo"]):
        for t in m["por_tipo"]:
            linhas.append(f"| {m['modelo']} | {t['tipo']} | {t['categorias']} | "
                          f"{t['chamados']} | {t['acuracia']} | {t['macro_f1']} |")

    linhas += [
        "",
        "## Curva ABC global",
        "",
        "| Modelo | Classe | Categorias | Chamados | % do volume | Acurácia | Macro-F1 |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for m in sorted(relatorio["modelos"], key=lambda x: x["modelo"]):
        for c in m["curva_abc"]:
            linhas.append(f"| {m['modelo']} | {c['classe']} | {c['categorias']} | "
                          f"{c['chamados']} | {c['proporcao_do_volume']} | "
                          f"{c['acuracia']} | {c['macro_f1']} |")

    linhas += [
        "",
        "## Proveniência",
        "",
        f"- Origem: `{relatorio['origem']}`.",
        "- Script: `src/recortes_canonicos.py`.",
        "- Nenhum modelo foi retreinado e nenhuma escrita foi feita na planilha.",
        "",
    ]
    return "\n".join(linhas)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--predicoes", type=Path, default=PREDICOES_PADRAO)
    p.add_argument("--manifesto", type=Path, default=MANIFESTO_PADRAO)
    p.add_argument("--json", type=Path, default=SAIDA_JSON_PADRAO)
    p.add_argument("--markdown", type=Path, default=SAIDA_MD_PADRAO)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.predicoes.exists():
        print(f"Predicoes nao encontradas em {args.predicoes}.", file=sys.stderr)
        return 2
    manifesto = (json.loads(args.manifesto.read_text(encoding="utf-8"))
                 if args.manifesto.exists() else None)
    relatorio = montar_relatorio(carregar(args.predicoes), manifesto)
    relatorio["gerado_em"] = agora_bahia()
    relatorio["script_origem"] = "src/recortes_canonicos.py"
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    args.markdown.write_text(renderizar_markdown(relatorio), encoding="utf-8")
    print(renderizar_markdown(relatorio))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
