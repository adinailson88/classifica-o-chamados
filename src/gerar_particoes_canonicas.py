#!/usr/bin/env python3
"""Gera as particoes canonicas usadas por todos os modelos do experimento.

Ferramenta estritamente READ-ONLY. Reaproveita os grupos textuais do Passo 2 e
aplica `StratifiedGroupKFold` com semente fixa sobre a referencia humana
congelada no Passo 1, de modo que nenhum grupo textual atravesse treino e
teste. As mesmas particoes devem servir aos sete modelos, a camada de regras e
ao BERTimbau, conforme o Passo 3 de PLANO_EXECUCAO_ATUAL.md.

As saidas sao sanitizadas: nao publicam titulos, descricoes nem IDs. O mapa por
registro usa o SHA-256 do ID, igual ao do Passo 2, para que a juncao seja
reconstruivel sem expor a base.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import construir_grupos_textuais as cgt  # noqa: E402
import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
SAIDA_JSON_PADRAO = RAIZ / "docs" / "dados" / "particoes_canonicas.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "PARTICOES_CANONICAS.md"
SAIDA_MAPA_PADRAO = RAIZ / "docs" / "dados" / "particoes_canonicas_mapa.csv"

K_PADRAO = 5
SEMENTE_PADRAO = 42

# Teto de rodadas de exclusao. Cada rodada retira ao menos uma categoria, e a
# base tem 50; o teto e apenas uma trava contra laco infinito, nunca atingida
# em operacao normal.
RODADAS_MAXIMAS = 20


def preparar(registros: list[dict[str, str]]) -> dict[str, list[str]]:
    """Extrai grupo textual e referencia humana de cada registro elegivel.

    Elegivel e o registro que tem ID e referencia humana. Sem referencia nao ha
    o que estratificar; sem ID nao ha como registrar a particao.
    """
    ids: list[str] = []
    grupos: list[str] = []
    rotulos: list[str] = []
    descartados = 0
    for r in registros:
        id_chamado = r.get("id", "")
        rotulo = cgt.referencia_humana(r)
        if not id_chamado or not rotulo:
            descartados += 1
            continue
        normalizados = [cgt.normalizar_texto(r.get(c, ""))
                        for c in cgt.CAMPOS_TEXTUAIS]
        ids.append(id_chamado)
        grupos.append(cgt.hash_grupo(normalizados))
        rotulos.append(rotulo)
    return {"ids": ids, "grupos": grupos, "rotulos": rotulos,
            "descartados": descartados}


def classes_sem_estratificacao(grupos: list[str], rotulos: list[str],
                               minimo: int) -> list[dict[str, Any]]:
    """Categorias com menos grupos textuais distintos que o minimo exigido.

    Uma categoria presente em `g` grupos aparece em no maximo `g` dobras, porque
    o grupo inteiro vai para uma unica dobra. Com `g < k` o suporte em todas as
    dobras e impossivel por aritmetica, e nao por defeito do sorteio.

    A funcao apenas identifica; nenhuma categoria e fundida com outra. A
    taxonomia congelada no Passo 1 permanece intacta e a exclusao e nominal.
    """
    grupos_por_rotulo: dict[str, set[str]] = defaultdict(set)
    linhas_por_rotulo: Counter[str] = Counter()
    for grupo, rotulo in zip(grupos, rotulos):
        grupos_por_rotulo[rotulo].add(grupo)
        linhas_por_rotulo[rotulo] += 1
    faltantes = [
        {"categoria": rotulo, "grupos_distintos": len(gs),
         "linhas": linhas_por_rotulo[rotulo], "dobras_possiveis": len(gs)}
        for rotulo, gs in grupos_por_rotulo.items() if len(gs) < minimo
    ]
    faltantes.sort(key=lambda x: (x["grupos_distintos"], x["categoria"]))
    return faltantes


def particionar(ids: list[str], grupos: list[str], rotulos: list[str],
                k: int = K_PADRAO, semente: int = SEMENTE_PADRAO) -> dict[str, Any]:
    """Aplica StratifiedGroupKFold e verifica as invariantes do particionamento."""
    from sklearn.model_selection import StratifiedGroupKFold

    n = len(ids)
    dobra_por_indice = [-1] * n
    divisor = StratifiedGroupKFold(n_splits=k, shuffle=True, random_state=semente)
    for numero, (_treino, teste) in enumerate(
            divisor.split(range(n), rotulos, groups=grupos), start=1):
        for i in teste:
            dobra_por_indice[i] = numero

    nao_atribuidos = sum(1 for d in dobra_por_indice if d < 0)

    # Invariante central do passo: um grupo textual inteiro pertence a uma unica
    # dobra. Se falhar, o particionamento nao serve e nada deve ser publicado.
    dobras_por_grupo: dict[str, set[int]] = defaultdict(set)
    for grupo, dobra in zip(grupos, dobra_por_indice):
        dobras_por_grupo[grupo].add(dobra)
    grupos_divididos = sum(1 for ds in dobras_por_grupo.values() if len(ds) > 1)

    rotulos_totais = sorted(set(rotulos))
    detalhe_dobras = []
    for numero in range(1, k + 1):
        indices = [i for i, d in enumerate(dobra_por_indice) if d == numero]
        presentes = {rotulos[i] for i in indices}
        detalhe_dobras.append({
            "dobra": numero,
            "linhas": len(indices),
            "grupos": len({grupos[i] for i in indices}),
            "categorias_com_suporte": len(presentes),
            "categorias_ausentes": sorted(set(rotulos_totais) - presentes),
        })

    mapa = [{
        "id_sha256": hashlib.sha256(i.encode("utf-8")).hexdigest(),
        "grupo_sha256": g,
        "dobra": d,
    } for i, g, d in zip(ids, grupos, dobra_por_indice)]
    mapa.sort(key=lambda x: (x["id_sha256"], x["grupo_sha256"]))

    return {
        "k": k,
        "semente": semente,
        "algoritmo": "sklearn.model_selection.StratifiedGroupKFold, shuffle=True",
        "linhas_particionadas": n,
        "grupos_particionados": len(dobras_por_grupo),
        "linhas_sem_dobra": nao_atribuidos,
        "grupos_divididos_entre_dobras": grupos_divididos,
        "dobras": detalhe_dobras,
        "mapa_sha256": cgt._sha256_json(mapa),
        "_mapa": mapa,
    }


def montar_relatorio(registros: list[dict[str, str]], k: int = K_PADRAO,
                     semente: int = SEMENTE_PADRAO,
                     minimo_grupos: int | None = None) -> dict[str, Any]:
    """Particiona somente as categorias com suporte defensavel em cada dobra.

    Categorias com menos de `minimo_grupos` grupos textuais distintos ficam fora
    do particionamento. A exclusao e nominal e reproduzivel: cada categoria
    retirada aparece no relatorio com o numero de grupos e de linhas.
    """
    minimo = k if minimo_grupos is None else minimo_grupos
    dados = preparar(registros)
    raras = classes_sem_estratificacao(dados["grupos"], dados["rotulos"], minimo)
    excluidas = {r["categoria"] for r in raras}

    # Ter ao menos `minimo` grupos e condicao necessaria, nao suficiente: o
    # sorteio ainda pode reunir numa unica dobra todos os grupos de uma
    # categoria. Excluir e reparticionar ate a convergencia deixa somente
    # categorias com suporte verificado em todas as dobras, que era o criterio
    # pedido. O laco e determinista e cada rodada fica registrada.
    linhas_por_rotulo = Counter(dados["rotulos"])
    rodadas: list[dict[str, Any]] = []
    for _ in range(RODADAS_MAXIMAS):
        elegiveis = [i for i, rotulo in enumerate(dados["rotulos"])
                     if rotulo not in excluidas]
        if not elegiveis:
            break
        relatorio = particionar([dados["ids"][i] for i in elegiveis],
                                [dados["grupos"][i] for i in elegiveis],
                                [dados["rotulos"][i] for i in elegiveis],
                                k=k, semente=semente)
        ausentes = sorted({c for d in relatorio["dobras"]
                           for c in d["categorias_ausentes"]})
        if not ausentes:
            break
        rodadas.append({"rodada": len(rodadas) + 1, "categorias_retiradas": ausentes})
        excluidas.update(ausentes)

    por_sorteio = [
        {"categoria": c,
         "linhas": linhas_por_rotulo[c],
         "rodada": r["rodada"]}
        for r in rodadas for c in r["categorias_retiradas"]
    ]
    relatorio["categorias_excluidas_por_sorteio"] = por_sorteio
    relatorio["rodadas_de_exclusao"] = len(rodadas)
    relatorio["registros_descartados"] = dados["descartados"]
    relatorio["categorias_na_referencia"] = len(set(dados["rotulos"]))
    relatorio["categorias_particionadas"] = len(
        {dados["rotulos"][i] for i in elegiveis})
    relatorio["minimo_grupos_por_categoria"] = minimo
    relatorio["categorias_excluidas_por_suporte"] = raras
    relatorio["linhas_excluidas_por_suporte"] = sum(r["linhas"] for r in raras)
    relatorio["linhas_excluidas_por_sorteio"] = sum(c["linhas"] for c in por_sorteio)
    relatorio["linhas_excluidas_total"] = (
        relatorio["linhas_excluidas_por_suporte"]
        + relatorio["linhas_excluidas_por_sorteio"])
    relatorio["criterio_exclusao"] = (
        f"categoria com menos de {minimo} grupos textuais distintos nao pode ter "
        f"suporte nas {k} dobras, porque um grupo inteiro ocupa uma unica dobra; "
        "categorias que mesmo assim ficam sem suporte em alguma dobra saem em "
        "rodadas seguintes; a exclusao e nominal e nenhuma categoria e fundida "
        "com outra")

    ausentes = sorted({c for d in relatorio["dobras"]
                       for c in d["categorias_ausentes"]})

    problemas = {
        "linhas_sem_dobra": relatorio["linhas_sem_dobra"],
        "grupos_divididos_entre_dobras": relatorio["grupos_divididos_entre_dobras"],
        "registros_descartados": relatorio["registros_descartados"],
        "categorias_sem_suporte_em_alguma_dobra": len(ausentes),
    }
    bloqueios = [nome for nome, n in problemas.items() if n]
    relatorio["problemas"] = problemas
    relatorio["bloqueios"] = bloqueios
    relatorio["categorias_sem_suporte_em_alguma_dobra"] = ausentes
    relatorio["status"] = "apto_para_treinar" if not bloqueios else "bloqueado"
    relatorio["schema_version"] = 1
    return relatorio


def renderizar_markdown(relatorio: dict[str, Any]) -> str:
    raras = relatorio["categorias_excluidas_por_suporte"]
    linhas = [
        "# Partições canônicas do experimento",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.",
        "",
        f"**Estado:** `{relatorio['status']}`  ",
        f"**Gerado em:** {relatorio.get('gerado_em', 'não informado')}  ",
        f"**Hash do mapa por registro:** `{relatorio['mapa_sha256']}`",
        "",
        "## Protocolo",
        "",
        f"- Algoritmo: {relatorio['algoritmo']}.",
        f"- Dobras: {relatorio['k']}; semente: {relatorio['semente']}.",
        f"- Linhas particionadas: {relatorio['linhas_particionadas']}.",
        f"- Grupos textuais particionados: {relatorio['grupos_particionados']}.",
        f"- Grupos divididos entre dobras: {relatorio['grupos_divididos_entre_dobras']}.",
        f"- Categorias particionadas: {relatorio['categorias_particionadas']} "
        f"de {relatorio['categorias_na_referencia']} na referência.",
        "",
        "## Distribuição por dobra",
        "",
        "| Dobra | Linhas | Grupos | Categorias com suporte |",
        "|---:|---:|---:|---:|",
    ]
    linhas += [f"| {d['dobra']} | {d['linhas']} | {d['grupos']} | {d['categorias_com_suporte']} |"
               for d in relatorio["dobras"]]
    linhas += ["", "## Categorias excluídas por suporte insuficiente", ""]
    if raras:
        linhas += [
            f"Das {relatorio['categorias_na_referencia']} categorias da referência humana, "
            f"{len(raras)} {'aparecem' if len(raras) > 1 else 'aparece'} em menos de "
            f"{relatorio['minimo_grupos_por_categoria']} grupos "
            "textuais distintos. Como um grupo inteiro ocupa uma única dobra, o suporte em todas "
            f"as {relatorio['k']} dobras é aritmeticamente impossível, e por isso "
            f"{'ficam' if len(raras) > 1 else 'fica'} fora do particionamento, somando "
            f"{relatorio['linhas_excluidas_por_suporte']} linhas. "
            "A exclusão é nominal: a taxonomia congelada no Passo 1 não é alterada e nenhuma "
            "categoria é fundida com outra.",
            "",
            "| Categoria | Grupos distintos | Linhas | Dobras possíveis |",
            "|---|---:|---:|---:|",
        ]
        linhas += [f"| {r['categoria']} | {r['grupos_distintos']} | {r['linhas']} | {r['dobras_possiveis']} |"
                   for r in raras]
    else:
        linhas.append("Nenhuma categoria saiu pelo critério aritmético.")

    por_sorteio = relatorio["categorias_excluidas_por_sorteio"]
    linhas += ["", "## Categorias excluídas por ausência efetiva em alguma dobra", ""]
    if por_sorteio:
        linhas += [
            f"Ter ao menos {relatorio['minimo_grupos_por_categoria']} grupos é condição "
            "necessária, não suficiente: o sorteio ainda pode reunir numa única dobra todos os "
            f"grupos de uma categoria. Estas saíram em {relatorio['rodadas_de_exclusao']} "
            "rodada(s) de reparticionamento, até que todas as categorias remanescentes tivessem "
            "suporte verificado em todas as dobras.",
            "",
            "| Categoria | Linhas | Rodada |",
            "|---|---:|---:|",
        ]
        linhas += [f"| {c['categoria']} | {c['linhas']} | {c['rodada']} |"
                   for c in por_sorteio]
    else:
        linhas.append("Nenhuma: o primeiro particionamento já cobriu todas as categorias elegíveis.")

    if raras or por_sorteio:
        linhas += [
            "",
            f"No total, {relatorio['linhas_excluidas_total']} linhas ficaram fora das partições. "
            "Qualquer métrica derivada delas vale para as "
            f"{relatorio['categorias_particionadas']} categorias particionadas, e não para as "
            f"{relatorio['categorias_na_referencia']} da taxonomia. O artigo precisa declarar "
            "esse denominador sempre que reportar resultados.",
        ]
    linhas += [
        "",
        "## Validações",
        "",
        "| Verificação | Ocorrências |",
        "|---|---:|",
    ]
    linhas += [f"| {k.replace('_', ' ')} | {v} |"
               for k, v in relatorio["problemas"].items()]
    linhas += [
        "",
        "## Proveniência",
        "",
        "- Grupos textuais: `src/construir_grupos_textuais.py`, Passo 2.",
        "- Referência humana: regra congelada no Passo 1.",
        "- Mapa por registro: `docs/dados/particoes_canonicas_mapa.csv`, com SHA-256 do ID.",
        "- Script: `src/gerar_particoes_canonicas.py`.",
        "- Nenhuma escrita foi realizada na planilha.",
        "",
    ]
    return "\n".join(linhas)


def escrever_mapa(caminho: Path, mapa: list[dict[str, Any]]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(["id_sha256", "grupo_sha256", "dobra"])
        escritor.writerows([[m["id_sha256"], m["grupo_sha256"], m["dobra"]]
                            for m in mapa])


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--k", type=int, default=K_PADRAO)
    p.add_argument("--semente", type=int, default=SEMENTE_PADRAO)
    p.add_argument("--minimo-grupos", type=int, default=None,
                   help=("minimo de grupos textuais distintos para uma categoria "
                         "entrar no particionamento; padrao igual a --k"))
    p.add_argument("--json", type=Path, default=SAIDA_JSON_PADRAO)
    p.add_argument("--markdown", type=Path, default=SAIDA_MD_PADRAO)
    p.add_argument("--mapa", type=Path, default=SAIDA_MAPA_PADRAO)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    relatorio = montar_relatorio(cgt.ler_registros(sh, config),
                                 k=args.k, semente=args.semente,
                                 minimo_grupos=args.minimo_grupos)
    relatorio["gerado_em"] = agora_bahia()
    relatorio["fonte"] = config["aba_principal"]
    relatorio["script_origem"] = "src/gerar_particoes_canonicas.py"

    escrever_mapa(args.mapa, relatorio["_mapa"])
    publicavel = {k: v for k, v in relatorio.items() if not k.startswith("_")}
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(publicavel, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    args.markdown.write_text(renderizar_markdown(relatorio), encoding="utf-8")
    print(renderizar_markdown(relatorio))
    return 0 if relatorio["status"] == "apto_para_treinar" else 2


if __name__ == "__main__":
    raise SystemExit(main())
