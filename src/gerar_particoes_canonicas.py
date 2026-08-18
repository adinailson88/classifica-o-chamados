#!/usr/bin/env python3
"""Gera as particoes canonicas usadas por todos os modelos do experimento.

Ferramenta estritamente READ-ONLY. Reaproveita os grupos textuais congelados no
Passo 2 e aplica `StratifiedGroupKFold` com semente fixa sobre a referencia
humana viva (validada contra a identidade congelada no Passo 1), de modo que
nenhum grupo textual atravesse treino e teste. As mesmas particoes devem
servir aos sete modelos, a camada de regras e ao BERTimbau, conforme o Passo 3
de PLANO_EXECUCAO_ATUAL.md.

O grupo textual de cada registro vem DIRETAMENTE do mapa congelado do Passo 2
(`docs/dados/grupos_textuais_mapa.csv`), nunca recalculado do texto vivo da
planilha: se um titulo ou descricao for editado depois do congelamento, o
grupo cientifico usado na estratificacao permanece o congelado. Isso torna o
Passo 3 reprodutivel mesmo quando o texto operacional muda, e e o motivo pelo
qual este script exige protocolo canonico fixo (k=5, semente=42, base
congelada aplicada) e valida a identidade do mapa do Passo 2 e da referencia
humana do Passo 1 antes de particionar.

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

import auditar_base_canonica as abc  # noqa: E402
import construir_grupos_textuais as cgt  # noqa: E402
import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
SAIDA_JSON_PADRAO = RAIZ / "docs" / "dados" / "particoes_canonicas.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "PARTICOES_CANONICAS.md"
SAIDA_MAPA_PADRAO = RAIZ / "docs" / "dados" / "particoes_canonicas_mapa.csv"
MAPA_PASSO2_PADRAO = RAIZ / "docs" / "dados" / "grupos_textuais_mapa.csv"

K_PADRAO = 5
SEMENTE_PADRAO = 42

# Teto de rodadas de exclusao. Cada rodada retira ao menos uma categoria, e a
# base tem 50; o teto e apenas uma trava contra laco infinito, nunca atingida
# em operacao normal.
RODADAS_MAXIMAS = 20

# Identidade do protocolo canonico deste script (ARTIGO_CONGELADO, Passo 3).
# Constantes fixas, nunca derivadas da execucao atual: sao o ponto de
# comparacao que torna o CLI oficial fail-closed. Funcoes puras como
# `particionar` e `montar_relatorio` continuam aceitando outros valores, para
# uso cientifico comparativo fora deste script.
K_ESPERADO = 5
SEMENTE_ESPERADA = 42
MINIMO_GRUPOS_ESPERADO = 5
LINHAS_PARTICIONADAS_ESPERADAS = 13972
GRUPOS_PARTICIONADOS_ESPERADOS = 9734
CATEGORIAS_PARTICIONADAS_ESPERADAS = 41
CATEGORIAS_NA_REFERENCIA_ESPERADAS = 50
LINHAS_EXCLUIDAS_TOTAL_ESPERADAS = 88
MAPA_PARTICOES_SHA256_ESPERADO = (
    "9465857d83ba76ec193974982835d91e03e783587153e26597051d4dfd9abcf2")
STATUS_ESPERADO = "apto_para_treinar"


def ler_linhas_mapa_congelado(caminho: Path) -> list[dict[str, str]]:
    """Le as linhas cruas do mapa de grupos textuais do Passo 2, sem colapsar
    em dict. Preservar a lista bruta e essencial: um dict `id_sha256 ->
    grupo_sha256` colapsa linhas duplicadas antes de qualquer verificacao, e
    um CSV adulterado com uma linha repetida podia produzir o mesmo mapa
    logico apos o colapso, escondendo a adulteracao do hash.
    """
    with caminho.open("r", encoding="utf-8", newline="") as f:
        return [{"id_sha256": linha.get("id_sha256", ""),
                 "grupo_sha256": linha.get("grupo_sha256", "")}
                for linha in csv.DictReader(f) if linha.get("id_sha256")]


def validar_mapa_congelado(
    caminho: Path,
    *,
    mapa_sha256_esperado: str = cgt.MAPA_SHA256_ESPERADO,
    corpus_esperado: int = cgt.CORPUS_COMPLETO_ESPERADO,
    saida: Any = sys.stderr,
) -> tuple[bool, dict[str, str]]:
    """Gate fail-closed: confere a identidade do mapa de grupos do Passo 2.

    Le as linhas cruas do CSV (sem colapsar em dict), confere quantidade de
    linhas, IDs unicos, campos vazios e duplicatas, e SO ENTAO reconstroi a
    mesma estrutura ordenada usada por `construir_grupos_textuais.agrupar` e
    recalcula o hash com `cgt._sha256_json` a partir da lista bruta. Um
    conteudo alterado (ID trocado, grupo recalculado, linha removida,
    acrescentada ou duplicada) muda o hash e bloqueia antes de qualquer
    leitura da planilha. O dict `id_sha256 -> grupo_sha256` so e produzido
    depois que todas as verificacoes passam.
    """
    if not caminho.exists():
        print(f"Mapa da base congelada nao encontrado em {caminho}. "
              "Execute o Passo 2 ou aponte --mapa-congelado para o arquivo "
              "correto.", file=saida)
        return False, {}

    linhas = ler_linhas_mapa_congelado(caminho)
    ids = [linha["id_sha256"] for linha in linhas]
    ids_unicos = set(ids)

    divergencias = []
    if len(linhas) != corpus_esperado:
        divergencias.append(
            f"linhas: obtido={len(linhas)} esperado={corpus_esperado}")
    if len(ids_unicos) != corpus_esperado:
        divergencias.append(
            f"ids_unicos: obtido={len(ids_unicos)} esperado={corpus_esperado}")
    duplicados = len(ids) - len(ids_unicos)
    if duplicados:
        divergencias.append(f"ids_duplicados: obtido={duplicados} esperado=0")
    vazios_grupo = sum(1 for linha in linhas if not linha["grupo_sha256"])
    if vazios_grupo:
        divergencias.append(
            f"grupo_sha256_vazios: obtido={vazios_grupo} esperado=0")

    reconstruido = sorted(linhas, key=lambda x: (x["id_sha256"], x["grupo_sha256"]))
    obtido = cgt._sha256_json(reconstruido)
    if obtido != mapa_sha256_esperado:
        divergencias.append(f"mapa_sha256: obtido={obtido} esperado={mapa_sha256_esperado}")

    if divergencias:
        print(
            "Mapa de grupos textuais divergente do ARTIGO_CONGELADO: "
            "particionamento interrompido antes de ler a planilha e antes de "
            "gravar qualquer artefato canonico.\n"
            + "\n".join(divergencias) + f"\ncaminho={caminho}",
            file=saida,
        )
        return False, {}

    grupos = {linha["id_sha256"]: linha["grupo_sha256"] for linha in linhas}
    return True, grupos


def filtrar_registros_congelados(
    registros: list[dict[str, str]],
    grupos_congelados: dict[str, str],
) -> list[dict[str, str]]:
    """Mantem somente os registros vivos cujo ID pertence ao mapa congelado.

    Usado para restringir o gate de identidade do Passo 1
    (`auditar_base_canonica`) ao corpus congelado no Passo 2: linhas
    operacionais novas, com ID fora do mapa, precisam continuar liberadas sem
    influenciar a validacao de identidade da referencia humana.
    """
    congelados = []
    for r in registros:
        id_chamado = r.get("id", "")
        if not id_chamado:
            continue
        digest = hashlib.sha256(id_chamado.encode("utf-8")).hexdigest()
        if digest in grupos_congelados:
            congelados.append(r)
    return congelados


def preparar(registros: list[dict[str, str]],
             grupos_congelados: dict[str, str] | None = None) -> dict[str, Any]:
    """Extrai grupo textual e referencia humana de cada registro elegivel.

    Elegivel e o registro que tem ID e referencia humana. Sem referencia nao ha
    o que estratificar; sem ID nao ha como registrar a particao.

    A aba principal e viva: o GLPI continua alimentando linhas novas depois do
    congelamento, e textos ja lidos podem ser editados. Com
    `grupos_congelados` (mapa `id_sha256 -> grupo_sha256` do Passo 2), o passo
    considera apenas os registros do corpus congelado, contabiliza o
    excedente a parte, e usa o grupo textual JA CONGELADO em vez de recalcula-
    lo do texto vivo: o grupo cientifico usado na estratificacao nao muda
    ainda que o texto do chamado mude depois do congelamento.
    """
    ids: list[str] = []
    grupos: list[str] = []
    rotulos: list[str] = []
    descartados = 0
    fora_da_base = 0
    for r in registros:
        id_chamado = r.get("id", "")
        grupo_congelado = None
        if grupos_congelados is not None:
            digest = hashlib.sha256(id_chamado.encode("utf-8")).hexdigest()
            grupo_congelado = grupos_congelados.get(digest) if id_chamado else None
            if grupo_congelado is None:
                fora_da_base += 1
                continue
        rotulo = cgt.referencia_humana(r)
        if not id_chamado or not rotulo:
            descartados += 1
            continue
        if grupo_congelado is not None:
            grupo = grupo_congelado
        else:
            normalizados = [cgt.normalizar_texto(r.get(c, ""))
                            for c in cgt.CAMPOS_TEXTUAIS]
            grupo = cgt.hash_grupo(normalizados)
        ids.append(id_chamado)
        grupos.append(grupo)
        rotulos.append(rotulo)
    return {"ids": ids, "grupos": grupos, "rotulos": rotulos,
            "descartados": descartados, "fora_da_base_congelada": fora_da_base}


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
                     minimo_grupos: int | None = None,
                     grupos_congelados: dict[str, str] | None = None) -> dict[str, Any]:
    """Particiona somente as categorias com suporte defensavel em cada dobra.

    Categorias com menos de `minimo_grupos` grupos textuais distintos ficam fora
    do particionamento. A exclusao e nominal e reproduzivel: cada categoria
    retirada aparece no relatorio com o numero de grupos e de linhas.
    """
    minimo = k if minimo_grupos is None else minimo_grupos
    dados = preparar(registros, grupos_congelados)
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
    relatorio["base_congelada_aplicada"] = grupos_congelados is not None
    relatorio["linhas_da_base_congelada"] = (
        len(grupos_congelados) if grupos_congelados is not None else None)
    relatorio["linhas_vivas_fora_da_base_congelada"] = dados["fora_da_base_congelada"]
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
        (f"- Corpus fixado na base congelada do Passo 2, com "
         f"{relatorio['linhas_da_base_congelada']} registros; "
         f"{relatorio['linhas_vivas_fora_da_base_congelada']} linhas vivas da aba "
         "ficaram fora por serem posteriores ao congelamento."
         if relatorio["base_congelada_aplicada"] else
         "- Corpus lido direto da aba viva, sem fixação na base congelada."),
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


def validar_particoes_congeladas(
    relatorio: dict[str, Any],
    *,
    k_esperado: int = K_ESPERADO,
    semente_esperada: int = SEMENTE_ESPERADA,
    linhas_esperadas: int = LINHAS_PARTICIONADAS_ESPERADAS,
    grupos_esperados: int = GRUPOS_PARTICIONADOS_ESPERADOS,
    categorias_particionadas_esperadas: int = CATEGORIAS_PARTICIONADAS_ESPERADAS,
    categorias_na_referencia_esperadas: int = CATEGORIAS_NA_REFERENCIA_ESPERADAS,
    linhas_excluidas_total_esperadas: int = LINHAS_EXCLUIDAS_TOTAL_ESPERADAS,
    mapa_sha256_esperado: str = MAPA_PARTICOES_SHA256_ESPERADO,
    status_esperado: str = STATUS_ESPERADO,
    saida: Any = sys.stderr,
) -> bool:
    """Gate fail-closed: confere a identidade das particoes do ARTIGO_CONGELADO.

    Roda depois do particionamento e ANTES de qualquer escrita de artefato.
    `linhas_vivas_fora_da_base_congelada` deliberadamente NAO entra neste gate:
    o crescimento operacional da planilha fora do corpus congelado e esperado
    e nao deve bloquear o Passo 3.
    """
    ausentes = relatorio.get("categorias_sem_suporte_em_alguma_dobra") or []
    checagens = [
        ("k", relatorio.get("k"), k_esperado),
        ("semente", relatorio.get("semente"), semente_esperada),
        ("linhas_particionadas", relatorio.get("linhas_particionadas"), linhas_esperadas),
        ("grupos_particionados", relatorio.get("grupos_particionados"), grupos_esperados),
        ("categorias_particionadas", relatorio.get("categorias_particionadas"),
         categorias_particionadas_esperadas),
        ("categorias_na_referencia", relatorio.get("categorias_na_referencia"),
         categorias_na_referencia_esperadas),
        ("linhas_excluidas_total", relatorio.get("linhas_excluidas_total"),
         linhas_excluidas_total_esperadas),
        ("mapa_sha256", relatorio.get("mapa_sha256"), mapa_sha256_esperado),
        ("status", relatorio.get("status"), status_esperado),
        ("linhas_sem_dobra", relatorio.get("linhas_sem_dobra"), 0),
        ("grupos_divididos_entre_dobras", relatorio.get("grupos_divididos_entre_dobras"), 0),
        ("registros_descartados", relatorio.get("registros_descartados"), 0),
        ("categorias_sem_suporte_em_alguma_dobra", len(ausentes), 0),
    ]
    divergencias = [f"{nome}: obtido={obtido} esperado={esperado}"
                    for nome, obtido, esperado in checagens if obtido != esperado]
    if not divergencias:
        return True
    print(
        "Particoes obtidas divergentes do ARTIGO_CONGELADO: nenhum artefato "
        "canonico foi escrito.\n" + "\n".join(divergencias),
        file=saida,
    )
    return False


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
    p.add_argument("--mapa-congelado", type=Path, default=MAPA_PASSO2_PADRAO,
                   help=("mapa de grupos textuais do Passo 2 que define o corpus "
                         "congelado; linhas da aba viva fora dele sao ignoradas"))
    p.add_argument("--sem-base-congelada", action="store_true",
                   help="le a aba viva inteira, sem fixar o corpus do Passo 2")
    p.add_argument("--minimo-grupos", type=int, default=None,
                   help=("minimo de grupos textuais distintos para uma categoria "
                         "entrar no particionamento; padrao igual a --k"))
    p.add_argument("--json", type=Path, default=SAIDA_JSON_PADRAO)
    p.add_argument("--markdown", type=Path, default=SAIDA_MD_PADRAO)
    p.add_argument("--mapa", type=Path, default=SAIDA_MAPA_PADRAO)
    return p.parse_args()


def main() -> int:
    """CLI oficial das particoes canonicas do ARTIGO_CONGELADO.

    Representa um unico protocolo (k=5, semente=42, minimo-grupos efetivo=5,
    base congelada aplicada) e e fail-closed em quatro pontos, nesta ordem:
    protocolo do CLI, identidade do mapa de grupos do Passo 2, identidade da
    referencia humana do Passo 1 e identidade do resultado do particionamento.
    Qualquer divergencia interrompe antes da proxima etapa cara e antes de
    qualquer escrita de artefato. As funcoes puras (`particionar`,
    `montar_relatorio`) continuam aceitando outros valores para uso cientifico
    comparativo fora deste script.
    """
    args = parse_args()

    if args.sem_base_congelada:
        print("Protocolo canonico exige a base congelada do Passo 2; "
              "--sem-base-congelada nao e permitido neste script.",
              file=sys.stderr)
        return 2
    if args.k != K_ESPERADO:
        print(f"Protocolo canonico exige k={K_ESPERADO}; recebido --k={args.k}.",
              file=sys.stderr)
        return 2
    if args.semente != SEMENTE_ESPERADA:
        print(f"Protocolo canonico exige semente={SEMENTE_ESPERADA}; "
              f"recebido --semente={args.semente}.", file=sys.stderr)
        return 2
    minimo_efetivo = args.k if args.minimo_grupos is None else args.minimo_grupos
    if minimo_efetivo != MINIMO_GRUPOS_ESPERADO:
        print(f"Protocolo canonico exige minimo-grupos efetivo="
              f"{MINIMO_GRUPOS_ESPERADO}; recebido={minimo_efetivo}.",
              file=sys.stderr)
        return 2

    ok, grupos_congelados = validar_mapa_congelado(args.mapa_congelado)
    if not ok:
        return 2

    config = json.loads(args.config.read_text(encoding="utf-8"))
    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    registros = cgt.ler_registros(sh, config)

    # O gate do Passo 1 valida a identidade da referencia humana APENAS para
    # os IDs do corpus congelado no Passo 2. Linhas operacionais novas (fora
    # do mapa) sao um crescimento esperado da planilha viva e nao podem
    # influenciar essa validacao; elas continuam contabilizadas a parte em
    # `linhas_vivas_fora_da_base_congelada`, calculado por `montar_relatorio`
    # sobre a lista viva completa logo abaixo.
    registros_congelados = filtrar_registros_congelados(registros, grupos_congelados)
    auditoria = abc.auditar(registros_congelados)
    if not abc.validar_identidade_congelada(
            auditoria, corpus_esperado=abc.CORPUS_COMPLETO_ESPERADO,
            hash_esperado=abc.HASH_BASE_CANONICA_ESPERADO):
        return 2

    relatorio = montar_relatorio(registros,
                                 k=args.k, semente=args.semente,
                                 minimo_grupos=args.minimo_grupos,
                                 grupos_congelados=grupos_congelados)
    relatorio["gerado_em"] = agora_bahia()
    relatorio["fonte"] = config["aba_principal"]
    relatorio["script_origem"] = "src/gerar_particoes_canonicas.py"

    if not validar_particoes_congeladas(relatorio):
        return 2

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
