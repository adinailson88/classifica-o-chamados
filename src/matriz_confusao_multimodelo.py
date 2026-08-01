#!/usr/bin/env python3
"""Matriz de confusao por IA, calculada contra a verdade derivada da conferencia
humana do GLPI (ver src/conferencia_derivada.py).

Logica PURA: recebe verdade e predicoes ja resolvidas, devolve estruturas
prontas para o JSON do painel. Nao le planilha nem escreve arquivo -- quem faz
isso e conferencia_derivada.py, que ja tem os dados em memoria (uma unica
leitura da planilha alimenta os dois artefatos).

A verdade cresce sozinha conforme o pesquisador confere mais chamados na coluna
M e preenche a coluna Q dos casos em que o GLPI errou. Por isso a matriz nao
tem parametro de recorte: ela sempre reflete o estado atual da conferencia.

MATRIZ ESPARSA: com ~40 categorias e 8 modelos, a matriz densa daria 12.800
celulas por publicacao no GitHub Pages. Como a maioria e zero, so as celulas
nao nulas sao emitidas, no formato [i_verdade, j_predicao, n].
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def _f1(precision: float, recall: float) -> float:
    return 0.0 if (precision + recall) == 0 else 2 * precision * recall / (precision + recall)


def matriz_de_um_modelo(pares: list[tuple[str, str]], indice: dict[str, int]
                        ) -> dict[str, Any]:
    """pares: [(verdade, predicao)] ja filtrados (ambos nao vazios)."""
    celulas: dict[tuple[int, int], int] = defaultdict(int)
    suporte: dict[str, int] = defaultdict(int)   # quantos exemplos daquela verdade
    previstos: dict[str, int] = defaultdict(int)  # quantas vezes foi predita
    acertos: dict[str, int] = defaultdict(int)

    for verdade, predicao in pares:
        celulas[(indice[verdade], indice[predicao])] += 1
        suporte[verdade] += 1
        previstos[predicao] += 1
        if verdade == predicao:
            acertos[verdade] += 1

    n = len(pares)
    total_acertos = sum(acertos.values())

    por_categoria = []
    f1s, f1s_ponderados = [], 0.0
    for cat, i in sorted(indice.items(), key=lambda kv: kv[1]):
        sup = suporte.get(cat, 0)
        prev = previstos.get(cat, 0)
        ok = acertos.get(cat, 0)
        if sup == 0 and prev == 0:
            continue
        precision = ok / prev if prev else 0.0
        recall = ok / sup if sup else 0.0
        f1 = _f1(precision, recall)
        por_categoria.append({
            "c": i, "suporte": sup, "previstos": prev,
            "precision": round(precision, 4), "recall": round(recall, 4),
            "f1": round(f1, 4),
        })
        # F1 macro considera apenas categorias COM suporte real (presentes na
        # verdade). Categorias que o modelo inventou entram na precision delas,
        # mas nao inflam nem deprimem a media macro.
        if sup > 0:
            f1s.append(f1)
            f1s_ponderados += f1 * sup

    total_suporte = sum(suporte.values())
    return {
        "n": n,
        "acuracia": round(total_acertos / n, 4) if n else None,
        "f1_macro": round(sum(f1s) / len(f1s), 4) if f1s else None,
        "f1_weighted": round(f1s_ponderados / total_suporte, 4) if total_suporte else None,
        "categorias_na_verdade": len(f1s),
        "celulas": [[i, j, k] for (i, j), k in sorted(celulas.items())],
        "por_categoria": por_categoria,
    }


def construir(verdades: dict[str, str], predicoes: dict[str, dict[str, str]],
              modelos: list[str]) -> dict[str, Any]:
    """verdades: {id_chamado: categoria verdadeira} (so os ja resolvidos).
    predicoes: {modelo: {id_chamado: categoria prevista}}.
    """
    categorias: set[str] = set(verdades.values())
    for m in modelos:
        for id_chamado in verdades:
            p = predicoes.get(m, {}).get(id_chamado)
            if p:
                categorias.add(p)
    ordenadas = sorted(categorias)
    indice = {c: i for i, c in enumerate(ordenadas)}

    saida: dict[str, Any] = {
        "categorias": ordenadas,
        "n_verdade": len(verdades),
        "modelos": {},
    }
    for m in modelos:
        pares = []
        for id_chamado, verdade in verdades.items():
            p = predicoes.get(m, {}).get(id_chamado)
            if p:
                pares.append((verdade, p))
        saida["modelos"][m] = matriz_de_um_modelo(pares, indice)
    return saida


def top_confusoes(matriz_modelo: dict[str, Any], categorias: list[str],
                  limite: int = 15) -> list[dict[str, Any]]:
    """Maiores celulas FORA da diagonal: onde o modelo mais troca categorias."""
    fora = [(i, j, n) for i, j, n in matriz_modelo["celulas"] if i != j]
    fora.sort(key=lambda t: -t[2])
    return [{"verdade": categorias[i], "predito": categorias[j], "n": n}
            for i, j, n in fora[:limite]]
