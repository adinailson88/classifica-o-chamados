#!/usr/bin/env python3
"""Comparacoes contra a categoria historica, sobre a rodada canonica.

Ferramenta offline. Produz as tres grandezas do artigo que dependem da coluna
C, isto e, do rotulo administrativo produzido pelo GLPI:

    concordancia  acordo bruto e Kappa de Cohen entre cada modelo e a categoria
                  historica. Aqui o Kappa e legitimo: sao duas fontes de
                  classificacao independentes, e nenhuma viu a outra decidir.
    reclassificacao  ganho liquido, contando quantos chamados o modelo corrige
                  e quantos prejudica em relacao ao historico, ambos julgados
                  pela referencia humana.
    dispersao     entropia de Shannon normalizada da distribuicao prevista e
                  divergencia de Jensen-Shannon contra a distribuicao
                  historica.

UMA MELHORIA EM RELACAO AO DESENHO LEGADO. O artigo registra que o ganho
liquido anterior "combina parcelas comparadas contra a decisao validada e
contra o historico, duas referencias de naturezas distintas". Na base canonica
todo registro tem referencia humana, entao a comparacao usa uma unica
referencia para todos os casos, e a ressalva deixa de ser necessaria.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any


def concordancia_com_historico(historicas: list[str], previstas: list[str],
                               ) -> dict[str, Any]:
    """Acordo bruto e Kappa de Cohen entre modelo e categoria historica."""
    from sklearn.metrics import cohen_kappa_score
    if not historicas:
        return {"n": 0, "acordo_bruto": 0.0, "kappa": 0.0}
    acertos = sum(1 for h, p in zip(historicas, previstas) if h == p)
    return {
        "n": len(historicas),
        "acordo_bruto": round(acertos / len(historicas), 4),
        "kappa": round(float(cohen_kappa_score(historicas, previstas)), 4),
    }


def ganho_de_reclassificacao(historicas: list[str], previstas: list[str],
                             referencias: list[str]) -> dict[str, Any]:
    """Quantos chamados o modelo corrige e quantos prejudica.

    So conta onde a predicao DIFERE do historico, porque concordar com o
    historico nao reclassifica nada. Corrigido e o caso em que o modelo acerta
    a referencia e o historico erra; prejudicado, o inverso. Quando os dois
    erram, a troca nao melhora nem piora o rotulo e entra em `neutros`.
    """
    corrigidos = prejudicados = neutros = 0
    for h, p, r in zip(historicas, previstas, referencias):
        if p == h:
            continue
        if p == r:
            corrigidos += 1
        elif h == r:
            prejudicados += 1
        else:
            neutros += 1
    return {
        "divergencias_com_o_historico": corrigidos + prejudicados + neutros,
        "corrigidos": corrigidos,
        "prejudicados": prejudicados,
        "neutros": neutros,
        "ganho_liquido": corrigidos - prejudicados,
    }


def _distribuicao(valores: list[str], categorias: list[str]) -> list[float]:
    contagem = Counter(valores)
    total = sum(contagem.values())
    return [contagem.get(c, 0) / total if total else 0.0 for c in categorias]


def _entropia(p: list[float]) -> float:
    return -sum(x * math.log(x) for x in p if x > 0)


def divergencia_js(p: list[float], q: list[float]) -> float:
    """Jensen-Shannon entre duas distribuicoes, na base natural.

    Simetrica e limitada, ao contrario da divergencia de Kullback-Leibler, que
    seria infinita sempre que o modelo nunca previsse uma categoria presente no
    historico. Com 41 categorias e modelos que ignoram a cauda, esse caso
    ocorre, e por isso a escolha nao e cosmetica.
    """
    m = [(a + b) / 2 for a, b in zip(p, q)]
    def kl(x: list[float], y: list[float]) -> float:
        return sum(a * math.log(a / b) for a, b in zip(x, y) if a > 0 and b > 0)
    return (kl(p, m) + kl(q, m)) / 2


def dispersao(historicas: list[str], previstas: list[str],
              categorias: list[str]) -> dict[str, Any]:
    """Entropia normalizada da predicao e distancia ate o historico."""
    p = _distribuicao(previstas, categorias)
    q = _distribuicao(historicas, categorias)
    teto = math.log(len(categorias)) if len(categorias) > 1 else 1.0
    return {
        "categorias_previstas": len({v for v in previstas if v}),
        "entropia_normalizada": round(_entropia(p) / teto, 4) if teto else 0.0,
        "js_contra_o_historico": round(divergencia_js(p, q), 4),
        "base_da_normalizacao": ("logaritmo natural do numero de categorias da "
                                 "referencia"),
    }


def montar_relatorio(historicas: list[str], referencias: list[str],
                     por_modelo: dict[str, list[str]]) -> dict[str, Any]:
    categorias = sorted(set(referencias) | set(historicas))
    modelos = []
    for nome, previstas in sorted(por_modelo.items()):
        modelos.append({
            "modelo": nome,
            "concordancia": concordancia_com_historico(historicas, previstas),
            "reclassificacao": ganho_de_reclassificacao(historicas, previstas,
                                                        referencias),
            "dispersao": dispersao(historicas, previstas, categorias),
        })
    return {
        "schema_version": 1,
        "status": "concluido",
        "protocolo": (
            "comparacoes contra a categoria historica da coluna C, sobre as "
            "predicoes out-of-fold da rodada canonica; a referencia humana "
            "arbitra quem acerta em cada divergencia"),
        "nota_sobre_o_kappa": (
            "aqui o Kappa e legitimo porque modelo e categoria historica sao "
            "fontes independentes; o mesmo nao valeria entre a referencia "
            "humana e a categoria historica, que o revisor viu ao decidir"),
        "corpus": {
            "registros": len(historicas),
            "categorias_na_referencia": len(set(referencias)),
            "categorias_no_historico": len(set(historicas)),
        },
        "modelos": modelos,
    }


def renderizar_markdown(r: dict[str, Any]) -> str:
    c = r["corpus"]
    linhas = [
        "# Comparações contra a categoria histórica",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.",
        "",
        f"**Gerado em:** {r.get('gerado_em', 'não informado')}  ",
        f"**Hash do corpus:** `{r.get('hash_corpus') or 'não informado'}`",
        "",
        "## Protocolo",
        "",
        f"- {r['protocolo']}.",
        f"- Sobre o Kappa: {r['nota_sobre_o_kappa']}.",
        f"- Registros: {c['registros']}, com {c['categorias_na_referencia']} "
        f"categorias na referência e {c['categorias_no_historico']} no histórico.",
        "",
        "## Concordância com a categoria histórica",
        "",
        "| Modelo | Acordo bruto | Kappa de Cohen |",
        "|---|---:|---:|",
    ]
    for m in sorted(r["modelos"], key=lambda x: -x["concordancia"]["acordo_bruto"]):
        linhas.append(f"| {m['modelo']} | {m['concordancia']['acordo_bruto']} | "
                      f"{m['concordancia']['kappa']} |")

    linhas += [
        "",
        "## Ganho líquido de reclassificação",
        "",
        "Contado apenas onde a predição diverge do histórico. A referência humana "
        "arbitra: corrigido é o caso em que o modelo acerta e o histórico erra.",
        "",
        "| Modelo | Divergências | Corrigidos | Prejudicados | Neutros | Ganho líquido |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for m in sorted(r["modelos"], key=lambda x: -x["reclassificacao"]["ganho_liquido"]):
        g = m["reclassificacao"]
        linhas.append(
            f"| {m['modelo']} | {g['divergencias_com_o_historico']} | "
            f"{g['corrigidos']} | {g['prejudicados']} | {g['neutros']} | "
            f"{g['ganho_liquido']:+} |")

    linhas += [
        "",
        "## Dispersão das predições",
        "",
        "| Modelo | Categorias previstas | Entropia normalizada | JS contra o histórico |",
        "|---|---:|---:|---:|",
    ]
    for m in sorted(r["modelos"], key=lambda x: -x["dispersao"]["entropia_normalizada"]):
        d = m["dispersao"]
        linhas.append(f"| {m['modelo']} | {d['categorias_previstas']} | "
                      f"{d['entropia_normalizada']} | {d['js_contra_o_historico']} |")

    linhas += [
        "",
        "## Proveniência",
        "",
        "- Predições e categoria histórica: rodada canônica.",
        "- Script: `src/comparacao_historica.py`.",
        "- Nenhuma escrita foi realizada na planilha.",
        "",
    ]
    return "\n".join(linhas)
