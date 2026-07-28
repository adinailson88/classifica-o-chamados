#!/usr/bin/env python3
"""Memoria de treino validada a partir da aba principal.

A memoria usa somente chamados com decisao humana nao contraditoria, derivada
pelas regras vigentes da planilha:

- M confirma ou rejeita a categoria historica da coluna C;
- N confirma ou rejeita a classificacao inicial da coluna G;
- P confirma ou rejeita a reclassificacao da coluna O;
- Q informa a categoria correta quando M, N e P nao confirmam nenhuma fonte.

Linhas sem categoria decidida ou com conflito entre fontes nao entram no treino.
O modulo e somente leitura e nao cria nem sobrescreve abas de validacao.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

import decisao_validada as dv
import planilha as pl


def _cel(linha: list[Any], idx: int | None) -> str:
    return str(linha[idx] or "").strip() if idx is not None and idx < len(linha) else ""


def montar_texto_validacao(linha: list[Any], idx: dict[str, int | None]) -> str:
    partes = [
        _cel(linha, idx.get("titulo")),
        _cel(linha, idx.get("descricao_glpi")),
        _cel(linha, idx.get("titulo_osm")),
        _cel(linha, idx.get("descricao_osm")),
    ]
    return "\n".join(parte for parte in partes if parte)


def carregar_memoria_validada(sh, aba_principal: str) -> list[dict[str, str]]:
    """Retorna exemplos de treino decididos pelas conferencias M/N/P/Q."""
    try:
        ws = sh.worksheet(aba_principal)
        valores = ws.get_values("A:Q", value_render_option="UNFORMATTED_VALUE")
    except Exception:  # noqa: BLE001
        return []
    if len(valores) < 2:
        return []

    cabecalho = valores[0]
    mapa = pl.mapa_cabecalhos(cabecalho)

    def indice(*nomes: str) -> int | None:
        for nome in nomes:
            encontrado = mapa.get(pl.normalizar_cabecalho(nome))
            if encontrado:
                return encontrado - 1
        return None

    idx = {
        "id_chamado": indice("ID Chamado", "ID"),
        "titulo": indice("TITULO", "TÍTULO"),
        "descricao_glpi": indice("DESCRICAO GLPI", "DESCRIÇÃO GLPI"),
        "titulo_osm": indice("TITULO O.S.M.", "TÍTULO O.S.M."),
        "descricao_osm": indice("DESCRICAO O.S.M.", "DESCRIÇÃO O.S.M."),
    }

    decisoes = dv.carregar_decisoes(sh, aba_principal)
    memoria: list[dict[str, str]] = []
    vistos: set[tuple[str, str, str]] = set()

    for posicao, linha in enumerate(valores[1:], start=2):
        decisao = decisoes.get(posicao)
        if not decisao or decisao.get("status") != dv.STATUS_DECIDIDO:
            continue
        if decisao.get("conflito"):
            continue

        categoria = pl.normalizar_categoria(str(decisao.get("decidida") or "").strip())
        texto = montar_texto_validacao(linha, idx)
        if not categoria or not texto:
            continue

        id_chamado = _cel(linha, idx["id_chamado"])
        chave = (str(posicao), id_chamado, categoria)
        if chave in vistos:
            continue
        vistos.add(chave)

        memoria.append({
            "linha_planilha": str(posicao),
            "id_chamado": id_chamado,
            "texto": texto,
            "categoria": categoria,
            "decisao": str(decisao.get("status") or ""),
            "fonte_decisao": str(decisao.get("fonte_decisao") or ""),
            "origem": "aba_principal_M_N_P_Q",
        })

    return memoria


def expandir_treino_com_memoria(
    textos: list[str],
    categorias: list[str],
    memoria: list[dict[str, str]],
    peso: int = 3,
) -> tuple[list[str], list[str]]:
    """Duplica exemplos validados para dar mais peso aos rotulos revisados."""
    peso = max(1, int(peso or 1))
    if not memoria:
        return list(textos), list(categorias)
    textos_out = list(textos)
    categorias_out = list(categorias)
    for item in memoria:
        for _ in range(peso):
            textos_out.append(item["texto"])
            categorias_out.append(item["categoria"])
    return textos_out, categorias_out


def resumir_memoria(memoria: list[dict[str, str]]) -> dict[str, Any]:
    contagem = Counter(item["categoria"] for item in memoria)
    fontes = Counter(item.get("fonte_decisao", "") for item in memoria)
    return {
        "exemplos_validados": len(memoria),
        "categorias_validadas": len(contagem),
        "top_categorias": contagem.most_common(10),
        "fontes_decisao": dict(fontes),
    }
