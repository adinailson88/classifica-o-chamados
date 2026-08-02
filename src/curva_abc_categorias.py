#!/usr/bin/env python3
"""Curva ABC das categorias e F1 recalculado por classe de volume.

MOTIVACAO (2026-08-02): o F1 macro do LinearSVC e 0,5567 contra acuracia de
0,8198. A diferenca nao se distribui pelas categorias, concentra-se na cauda:
13 categorias tem F1 zero, quase todas com suporte de 2 a 7 chamados, valores
em que nenhum classificador supervisionado aprende a classe e o k-fold garante
que ela nunca esteve no treino. Cada zero custa 1/57 da media.

A curva ABC separa o que e aprendivel do que e ruido estatistico:
    classe A: categorias que acumulam ate 80% do volume
    classe B: de 80% a 95%
    classe C: de 95% a 100%

O F1 macro e entao recalculado dentro de cada classe. O numero da classe A
responde a pergunta operacional relevante, que e o desempenho nas categorias
que concentram o trabalho de manutencao, sem que a media seja dominada por
categorias de suporte irrisorio.

RECORTE POR TIPO (2026-08-02): a mesma leitura e feita dentro de cada tipo de
manutencao (Preventiva, Corretiva e Nao manutencao, ver src/tipo_manutencao.py),
com a curva ABC recalculada sobre o volume DAQUELE tipo. Duas quantidades
distintas sao produzidas, porque respondem a perguntas diferentes:

    por_tipo     F1 macro das categorias agrupadas por tipo, isto e, um recorte
                 da metrica que ja existe. Diz onde o modelo erra mais.
    tarefa_tipo  matriz de confusao projetada para o tipo, obtida mapeando
                 verdade e predicao de categoria para tipo. Diz se o modelo
                 distingue preventivo de corretivo, que e o eixo dos pares
                 simetricos de confusao da taxonomia ('Ar condicionado split'
                 existe em Manutencao Preventiva com 1.795 chamados e em
                 Climatizacao com 1.640) e o que sustenta qualquer contagem de
                 preventivas usada como indicador.

FONTE: docs/dados/matriz_confusao.json, que ja traz suporte e F1 por categoria
para cada modelo, mais as celulas esparsas [i_verdade, j_predicao, n], que
permitem projetar a matriz para o tipo sem reexecutar modelo algum. O calculo e
puro e nao depende da planilha; a escrita da aba e opcional e feita so com
--aplicar.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tipo_manutencao import TIPOS, sigla, tipo_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
MATRIZ_PADRAO = RAIZ / "docs" / "dados" / "matriz_confusao.json"
SAIDA_PADRAO = RAIZ / "docs" / "dados" / "curva_abc_categorias.json"
ABA_PADRAO = "CURVA_ABC_CATEGORIAS"

CORTE_A = 0.80
CORTE_B = 0.95


def classificar_abc(suportes: list[tuple[str, int]],
                    corte_a: float = CORTE_A,
                    corte_b: float = CORTE_B) -> list[dict[str, Any]]:
    """Ordena por volume e atribui classe ABC pelo percentual ACUMULADO.

    A categoria que cruza o corte pertence a classe que ela fecha, convencao
    usual da curva ABC: o acumulado passa a contar DEPOIS de incluir a
    categoria, de modo que a classe A e o menor conjunto que cobre ao menos
    `corte_a` do volume.
    """
    ordenado = sorted(suportes, key=lambda kv: (-kv[1], kv[0]))
    total = sum(n for _, n in ordenado)
    linhas: list[dict[str, Any]] = []
    acumulado = 0
    for pos, (cat, n) in enumerate(ordenado, start=1):
        anterior = acumulado / total if total else 0.0
        acumulado += n
        frac = acumulado / total if total else 0.0
        if anterior < corte_a:
            classe = "A"
        elif anterior < corte_b:
            classe = "B"
        else:
            classe = "C"
        linhas.append({
            "posicao": pos,
            "categoria": cat,
            "suporte": n,
            "percentual": round(100 * n / total, 4) if total else 0.0,
            "percentual_acumulado": round(100 * frac, 4),
            "classe": classe,
        })
    return linhas


def f1_por_classe(linhas_abc: list[dict[str, Any]],
                  f1_por_categoria: dict[str, float]) -> dict[str, Any]:
    """F1 macro dentro de cada classe ABC, mais o global, para UM modelo.

    Media simples do F1 das categorias da classe, que e a definicao de macro.
    Categorias sem F1 informado sao tratadas como zero, porque ausencia de
    predicao correta e desempenho nulo, nao dado faltante.
    """
    out: dict[str, Any] = {}
    for classe in ("A", "B", "C"):
        cats = [l["categoria"] for l in linhas_abc if l["classe"] == classe]
        if not cats:
            out[classe] = {"n_categorias": 0, "suporte": 0, "f1_macro": None}
            continue
        f1s = [float(f1_por_categoria.get(c, 0.0)) for c in cats]
        sup = sum(l["suporte"] for l in linhas_abc if l["classe"] == classe)
        out[classe] = {
            "n_categorias": len(cats),
            "suporte": sup,
            "f1_macro": round(sum(f1s) / len(f1s), 4),
        }
    todas = [float(f1_por_categoria.get(l["categoria"], 0.0)) for l in linhas_abc]
    out["global"] = {
        "n_categorias": len(todas),
        "suporte": sum(l["suporte"] for l in linhas_abc),
        "f1_macro": round(sum(todas) / len(todas), 4) if todas else None,
    }
    return out


def extrair_do_matriz(matriz: dict) -> tuple[list[tuple[str, int]], dict[str, dict[str, float]]]:
    """(suportes, {modelo: {categoria: f1}}) a partir de matriz_confusao.json.

    O suporte vem da VERDADE e portanto e o mesmo para todos os modelos; e
    lido do modelo com maior cobertura para evitar tomar como referencia um
    modelo de cobertura parcial, como o transformer_ft.
    """
    cats = matriz["categorias"]
    modelos = matriz["modelos"]
    referencia = max(modelos.items(), key=lambda kv: kv[1].get("n", 0))[1]
    suportes = [(cats[c["c"]], int(c["suporte"]))
                for c in referencia.get("por_categoria", [])
                if c.get("suporte", 0) > 0]
    f1 = {}
    for nome, m in modelos.items():
        f1[nome] = {cats[c["c"]]: float(c.get("f1") or 0.0)
                    for c in m.get("por_categoria", [])
                    if c.get("suporte", 0) > 0}
    return suportes, f1


def _resumo_classes(linhas: list[dict[str, Any]]) -> dict[str, Any]:
    total = sum(l["suporte"] for l in linhas)
    out = {}
    for classe in ("A", "B", "C"):
        sel = [l for l in linhas if l["classe"] == classe]
        suporte = sum(l["suporte"] for l in sel)
        out[classe] = {
            "n_categorias": len(sel),
            "suporte": suporte,
            "percentual_volume": round(100 * suporte / total, 2) if total else 0.0,
        }
    return out


def curva_por_tipo(suportes: list[tuple[str, int]],
                   f1: dict[str, dict[str, float]],
                   corte_a: float = CORTE_A,
                   corte_b: float = CORTE_B) -> dict[str, Any]:
    """Curva ABC e F1 por classe DENTRO de cada tipo de manutencao.

    O percentual acumulado e calculado sobre o volume do proprio tipo, e nao
    sobre o volume total, de modo que cada tipo tenha sua propria classe A. Os
    cortes permanecem em 80% e 95%, iguais aos da curva global, para que as duas
    leituras sejam comparaveis.
    """
    total_geral = sum(n for _, n in suportes)
    saida: dict[str, Any] = {}
    for tipo in TIPOS:
        do_tipo = [(c, n) for c, n in suportes if tipo_manutencao(c) == tipo]
        linhas = classificar_abc(do_tipo, corte_a, corte_b)
        suporte = sum(n for _, n in do_tipo)
        saida[tipo] = {
            "sigla": sigla(tipo),
            "n_categorias": len(linhas),
            "suporte": suporte,
            "percentual_da_base": round(100 * suporte / total_geral, 2) if total_geral else 0.0,
            "classes": _resumo_classes(linhas),
            "categorias": linhas,
            "por_modelo": {nome: f1_por_classe(linhas, mapa)
                           for nome, mapa in f1.items()},
        }
    return saida


def projetar_para_tipo(matriz: dict) -> dict[str, dict[tuple[str, str], int]]:
    """{modelo: {(tipo_verdadeiro, tipo_predito): n}}, a partir das celulas.

    A matriz de categorias e projetada para o tipo somando as celulas que caem
    na mesma combinacao. Nao ha reexecucao de modelo: a predicao de categoria de
    cada chamado ja determina o tipo predito.
    """
    cats = matriz["categorias"]
    tipos = [tipo_manutencao(c) for c in cats]
    saida: dict[str, dict[tuple[str, str], int]] = {}
    for nome, m in matriz["modelos"].items():
        cont: dict[tuple[str, str], int] = {}
        for i, j, n in m.get("celulas", []):
            chave = (tipos[i], tipos[j])
            cont[chave] = cont.get(chave, 0) + int(n)
        saida[nome] = cont
    return saida


def metricas_tipo(contagem: dict[tuple[str, str], int]) -> dict[str, Any]:
    """Precisao, revocacao e F1 de cada tipo, mais acuracia e F1 macro do tipo.

    F1 macro considera apenas tipos COM suporte real na verdade, mesma regra de
    src/matriz_confusao_multimodelo.py: um tipo que o modelo inventa entra na
    precisao dele, mas nao deprime a media macro.
    """
    n = sum(contagem.values())
    acertos = sum(v for (a, b), v in contagem.items() if a == b)
    por_tipo: dict[str, Any] = {}
    f1s = []
    for tipo in TIPOS:
        suporte = sum(v for (a, _), v in contagem.items() if a == tipo)
        previstos = sum(v for (_, b), v in contagem.items() if b == tipo)
        ok = contagem.get((tipo, tipo), 0)
        precision = ok / previstos if previstos else 0.0
        recall = ok / suporte if suporte else 0.0
        f1 = 0.0 if (precision + recall) == 0 else 2 * precision * recall / (precision + recall)
        por_tipo[tipo] = {
            "sigla": sigla(tipo),
            "suporte": suporte,
            "previstos": previstos,
            "acertos": ok,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        }
        if suporte > 0:
            f1s.append(f1)
    return {
        "n": n,
        "acuracia": round(acertos / n, 4) if n else None,
        "f1_macro": round(sum(f1s) / len(f1s), 4) if f1s else None,
        "por_tipo": por_tipo,
        "matriz": [[a, b, v] for (a, b), v in sorted(contagem.items())],
    }


def tarefa_tipo(matriz: dict) -> dict[str, Any]:
    """metricas_tipo para cada modelo."""
    return {nome: metricas_tipo(cont)
            for nome, cont in projetar_para_tipo(matriz).items()}


def montar(matriz: dict, corte_a: float = CORTE_A,
           corte_b: float = CORTE_B) -> dict[str, Any]:
    suportes, f1 = extrair_do_matriz(matriz)
    linhas = classificar_abc(suportes, corte_a, corte_b)
    for l in linhas:
        l["tipo"] = tipo_manutencao(l["categoria"])
        l["sigla_tipo"] = sigla(l["tipo"])
    por_modelo = {nome: f1_por_classe(linhas, mapa) for nome, mapa in f1.items()}
    return {
        "corte_a": corte_a,
        "corte_b": corte_b,
        "n_categorias": len(linhas),
        "total_chamados": sum(l["suporte"] for l in linhas),
        "classes": _resumo_classes(linhas),
        "categorias": linhas,
        "por_modelo": por_modelo,
        "por_tipo": curva_por_tipo(suportes, f1, corte_a, corte_b),
        "tarefa_tipo": tarefa_tipo(matriz),
    }


def linhas_para_aba(dados: dict, modelos: list[str]) -> tuple[list[str], list[list[Any]]]:
    """Uma linha por categoria, com a classe ABC global e a classe dentro do tipo.

    As duas classes convivem porque respondem a perguntas diferentes: `classe` e
    a posicao da categoria no volume total, `classe_no_tipo` e a posicao dela
    entre as categorias do mesmo tipo de manutencao. Uma categoria preventiva de
    volume medio pode ser B no total e A dentro da preventiva.
    """
    cab = ["posicao", "categoria", "tipo", "sigla_tipo", "suporte", "percentual",
           "percentual_acumulado", "classe", "classe_no_tipo",
           "percentual_no_tipo"] + [f"f1_{m}" for m in modelos]
    matriz = dados["_f1_bruto"]
    no_tipo = {l["categoria"]: l
               for bloco in dados.get("por_tipo", {}).values()
               for l in bloco["categorias"]}
    linhas = []
    for l in dados["categorias"]:
        dentro = no_tipo.get(l["categoria"], {})
        linha = [l["posicao"], l["categoria"], l["tipo"], l["sigla_tipo"],
                 l["suporte"], l["percentual"], l["percentual_acumulado"],
                 l["classe"], dentro.get("classe", ""), dentro.get("percentual", 0.0)]
        for m in modelos:
            linha.append(matriz.get(m, {}).get(l["categoria"], 0.0))
        linhas.append(linha)
    return cab, linhas


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--matriz", type=Path, default=MATRIZ_PADRAO)
    p.add_argument("--json", type=Path, default=SAIDA_PADRAO)
    p.add_argument("--aba", default=ABA_PADRAO)
    p.add_argument("--corte-a", type=float, default=CORTE_A)
    p.add_argument("--corte-b", type=float, default=CORTE_B)
    p.add_argument("--aplicar", action="store_true",
                   help="Sem isso, nao grava a aba na planilha.")
    return p.parse_args()


def main() -> int:
    # O dry-run precisa ser legivel no console do Windows, cuja pagina de codigo
    # padrao nao cobre os acentos de 'Nao manutencao' nem os nomes de categoria.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    matriz = json.loads(args.matriz.read_text(encoding="utf-8"))
    dados = montar(matriz, args.corte_a, args.corte_b)
    _sup, f1_bruto = extrair_do_matriz(matriz)
    dados["_f1_bruto"] = f1_bruto

    from tempo import agora_bahia
    dados["gerado_em"] = agora_bahia()
    dados["script_origem"] = "src/curva_abc_categorias.py"
    dados["fonte"] = "docs/dados/matriz_confusao.json"
    dados["criterio"] = (
        f"classe A ate {args.corte_a:.0%} do volume acumulado; B ate "
        f"{args.corte_b:.0%}; C o restante. F1 macro = media simples do F1 "
        "das categorias da classe.")

    print(f"=== CURVA ABC ({dados['n_categorias']} categorias, "
          f"{dados['total_chamados']} chamados) ===")
    for classe, d in dados["classes"].items():
        print(f"  classe {classe}: {d['n_categorias']:>3} categorias | "
              f"{d['suporte']:>6} chamados | {d['percentual_volume']:>5.2f}% do volume")

    def _f1(d, k):
        v = d[k]["f1_macro"]
        return f"{v:.4f}" if v is not None else "   -  "

    print("\n=== F1 MACRO POR CLASSE (curva global) ===")
    print(f"  {'modelo':<22} {'A':>8} {'B':>8} {'C':>8} {'global':>8}")
    ordem = sorted(dados["por_modelo"].items(),
                   key=lambda kv: -(kv[1]["A"]["f1_macro"] or 0))
    for nome, d in ordem:
        print(f"  {nome:<22} {_f1(d,'A'):>8} {_f1(d,'B'):>8} {_f1(d,'C'):>8} {_f1(d,'global'):>8}")

    print("\n=== TAREFA DE TIPO (verdade e predicao projetadas para o tipo) ===")
    print(f"  {'modelo':<22} {'acuracia':>9} {'f1 macro':>9}   " +
          "  ".join(f"f1 {sigla(t)}" for t in TIPOS))
    for nome, d in sorted(dados["tarefa_tipo"].items(),
                          key=lambda kv: -(kv[1]["acuracia"] or 0)):
        celulas = "  ".join(f"{d['por_tipo'][t]['f1']:>5.4f}" for t in TIPOS)
        print(f"  {nome:<22} {d['acuracia']:>9.4f} {d['f1_macro']:>9.4f}   {celulas}")

    for tipo, bloco in dados["por_tipo"].items():
        print(f"\n=== CURVA ABC DENTRO DE {tipo.upper()} "
              f"({bloco['n_categorias']} categorias, {bloco['suporte']} chamados, "
              f"{bloco['percentual_da_base']:.2f}% da base) ===")
        for classe, d in bloco["classes"].items():
            print(f"  classe {classe}: {d['n_categorias']:>3} categorias | "
                  f"{d['suporte']:>6} chamados | {d['percentual_volume']:>5.2f}% do tipo")
        print(f"  {'modelo':<22} {'A':>8} {'B':>8} {'C':>8} {'tipo':>8}")
        ordem = sorted(bloco["por_modelo"].items(),
                       key=lambda kv: -(kv[1]["A"]["f1_macro"] or 0))
        for nome, d in ordem:
            print(f"  {nome:<22} {_f1(d,'A'):>8} {_f1(d,'B'):>8} {_f1(d,'C'):>8} {_f1(d,'global'):>8}")

    modelos = sorted(dados["por_modelo"])
    cab, linhas = linhas_para_aba(dados, modelos)

    publicavel = {k: v for k, v in dados.items() if k != "_f1_bruto"}
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(publicavel, ensure_ascii=False, indent=1),
                         encoding="utf-8")
    print(f"\nJSON escrito em {args.json}")

    if not args.aplicar:
        print(f"DRY-RUN: aba {args.aba} nao gravada ({len(linhas)} linhas prontas).")
        return 0

    import planilha as pl
    sh = pl.abrir_planilha(pl.id_planilha(json.loads(
        args.config.read_text(encoding="utf-8"))), args.credenciais)
    pl.escrever_aba(sh, args.aba, cab, linhas)
    print(f"OK: aba {args.aba} gravada com {len(linhas)} linha(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
