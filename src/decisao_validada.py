#!/usr/bin/env python3
"""Memoria de DECISAO a partir das conferencias humanas (M/N/P) da aba principal.

Regra definida pelo pesquisador (2026-06-10):
- se o humano conferiu uma categoria (do historico, da IA ou da reclassificacao)
  como ERRADA, essa categoria fica ELIMINADA para aquele chamado — nenhuma decisao
  automatica pode repeti-la;
- se o humano conferiu uma categoria como CERTA, a decisao fica TRAVADA — o fluxo
  reusa a categoria decidida e nao gasta tempo/memoria reprocessando o chamado.

Regra adicional (2026-07-25, corrige o vies estrutural registrado em
`04_artigo/figuras/sensibilidade_vies_validacao.json`): quando o avaliador
julga TODAS as fontes conferidas erradas (nenhum M/N/P = 'Correto'), o
chamado ficava sem verdade conhecida ('restrito') e era excluido de
qualquer acerto validado. A coluna Q (CATEGORIA CORRETA MANUAL) permite ao
avaliador registrar a categoria certa nesses casos — a decisao passa a
'decidido' com fonte 'manual'. So se aplica quando NENHUMA conferencia
Correto existe (se M, N ou P ja confirmou uma categoria, essa e a
verdade; a coluna manual so entra para preencher a lacuna dos restritos).
Se a categoria manual divergir de uma conferencia ja confirmada como
Correta, isso e tratado como conflito (contraditorio) e devolvido para
revisao humana, igual aos demais conflitos.

Colunas na CHAMADOS_ESQUELETO_REDUZIDO (1-based):
- C (3)  CATEGORIA COMPLETA      <- conferida pela coluna M (13, CONFERENCIA GLPI)
- G (7)  Classificacao IA        <- conferida pela coluna N (14, CONFERENCIA IA)
- O (15) Classificacao IA - 2    <- conferida pela coluna P (16, CONFERENCIA IA - 2)
- Q (17) CATEGORIA CORRETA MANUAL <- preenchida pelo avaliador so quando M, N
  e P nao tem nenhum 'Correto' (caso contrario, fica vazia)
'Correto' = acerto; qualquer outro valor nao vazio = 'Errado'; vazio = nao conferido
(mesma convencao de planilha.ler_conferencias).

Este modulo e READ-ONLY: nao escreve na planilha e nao altera o historico.
"""

from __future__ import annotations

from typing import Any

import planilha as pl

STATUS_DECIDIDO = "decidido"
STATUS_RESTRITO = "restrito"
STATUS_SEM_VALIDACAO = "sem_validacao"


def _norm_veredito(valor: Any) -> str | None:
    s = str(valor or "").strip()
    if not s:
        return None
    return "Correto" if s.casefold() == "correto" else "Errado"


def decidir(historico: str, ia1: str, reclass: str,
            v_glpi: str | None, v_ia: str | None, v_reclass: str | None,
            categoria_manual: str = "") -> dict[str, Any]:
    """Aplica a regra de memoria a UM chamado. Logica pura (testavel offline).

    categoria_manual: preenchida pelo avaliador quando M, N e P nao tem
    nenhum 'Correto' (caso "restrito") — vira a decisao com
    fonte_decisao='manual'. Se M/N/P ja confirmou uma categoria como
    Correta, a categoria manual so e considerada para checar consistencia
    (diferenca vira conflito); a fonte confirmada tem precedencia.

    Retorna:
    - decidida: categoria travada pela conferencia (ou None);
    - fonte_decisao: qual conferencia travou ('conferencia_ia' > 'conferencia_glpi'
      > 'conferencia_reclass' > 'manual', nesta ordem de precedencia);
    - eliminadas: categorias ja conferidas como erradas (nao repetir);
    - conflito: True quando duas conferencias 'Correto' apontam categorias
      DIFERENTES, ou quando a categoria manual diverge de uma conferencia
      ja confirmada como Correta (impossivel; devolvido para revisao
      humana, sem decisao);
    - status: decidido | restrito | sem_validacao.
    """
    historico = str(historico or "").strip()
    ia1 = str(ia1 or "").strip()
    reclass = str(reclass or "").strip()
    categoria_manual = str(categoria_manual or "").strip()

    corretas: list[tuple[str, str]] = []   # (categoria, fonte)
    eliminadas: set[str] = set()
    if v_glpi == "Correto" and historico:
        corretas.append((historico, "conferencia_glpi"))
    elif v_glpi == "Errado" and historico:
        eliminadas.add(historico)
    if v_ia == "Correto" and ia1:
        corretas.append((ia1, "conferencia_ia"))
    elif v_ia == "Errado" and ia1:
        eliminadas.add(ia1)
    if v_reclass == "Correto" and reclass:
        corretas.append((reclass, "conferencia_reclass"))
    elif v_reclass == "Errado" and reclass:
        eliminadas.add(reclass)

    conflito = len({c for c, _ in corretas}) > 1
    decidida = fonte = None
    if corretas and not conflito:
        # Precedencia apenas para REGISTRO da fonte; as categorias sao iguais.
        ordem = {"conferencia_ia": 0, "conferencia_glpi": 1, "conferencia_reclass": 2}
        decidida, fonte = sorted(corretas, key=lambda cf: ordem[cf[1]])[0]
        if categoria_manual and categoria_manual != decidida:
            # Contraditorio: uma fonte foi confirmada Correta mas a categoria
            # manual diverge dela. Devolve para revisao humana, sem decisao.
            conflito = True
            decidida = fonte = None
        else:
            # Categoria decidida nunca pode constar como eliminada (conferencias
            # se referem a colunas distintas; ex.: M=Errado e N=Correto com C != G).
            eliminadas.discard(decidida)
    elif not corretas and not conflito and categoria_manual:
        decidida, fonte = categoria_manual, "manual"
        eliminadas.discard(decidida)

    if decidida:
        status = STATUS_DECIDIDO
    elif eliminadas or conflito:
        status = STATUS_RESTRITO
    else:
        status = STATUS_SEM_VALIDACAO

    return {"decidida": decidida, "fonte_decisao": fonte, "eliminadas": eliminadas,
            "conflito": conflito, "status": status,
            "historico": historico, "ia1": ia1, "reclass": reclass,
            "categoria_manual": categoria_manual}


def carregar_decisoes(sh, aba_principal: str,
                      col_historico: int = 3, col_ia1: int = 7, col_reclass: int = 15,
                      col_conf_glpi: int = 13, col_conf_ia: int = 14,
                      col_conf_reclass: int = 16, col_categoria_manual: int = 17
                      ) -> dict[int, dict[str, Any]]:
    """Le a aba principal UMA vez (A:Q) e monta a memoria de decisao por linha.

    Retorna {linha_planilha (int, 1-based): decisao} apenas para linhas com pelo
    menos uma conferencia preenchida OU com categoria manual preenchida. Linhas
    sem nenhuma das duas ficam fora do mapa (status implicitamente
    'sem_validacao').
    """
    try:
        ws = sh.worksheet(aba_principal)
        bloco = ws.get_values("A:Q", value_render_option="UNFORMATTED_VALUE")
    except Exception:  # noqa: BLE001
        return {}
    cab = bloco[0] if bloco else []
    col_historico = pl.localizar_coluna(cab, ("CATEGORIA COMPLETA",), col_historico)
    col_ia1 = pl.localizar_coluna(cab, ("Classificacao IA", "Classificação IA"), col_ia1)
    col_reclass = pl.localizar_coluna(cab, ("Classificacao IA - 2", "Classificação IA - 2"), col_reclass)
    col_conf_glpi = pl.localizar_coluna(cab, ("CONFERENCIA GLPI", "CONFERÊNCIA GLPI"), col_conf_glpi)
    col_conf_ia = pl.localizar_coluna(cab, ("CONFERENCIA IA", "CONFERÊNCIA IA"), col_conf_ia)
    col_conf_reclass = pl.localizar_coluna(cab, ("CONFERENCIA IA - 2", "CONFERÊNCIA IA - 2"), col_conf_reclass)
    col_categoria_manual = pl.localizar_coluna(
        cab, ("CATEGORIA CORRETA MANUAL",), col_categoria_manual)

    def cel(linha: list[Any], c1: int) -> str:
        i = c1 - 1
        return str(linha[i] or "").strip() if len(linha) > i else ""

    out: dict[int, dict[str, Any]] = {}
    for pos, linha in enumerate(bloco[1:], start=2):
        v_glpi = _norm_veredito(cel(linha, col_conf_glpi))
        v_ia = _norm_veredito(cel(linha, col_conf_ia))
        v_reclass = _norm_veredito(cel(linha, col_conf_reclass))
        categoria_manual = pl.normalizar_categoria(cel(linha, col_categoria_manual))
        if v_glpi is None and v_ia is None and v_reclass is None and not categoria_manual:
            continue
        # Todas as quatro categorias passam pelo mapa canonico. Antes, so C e Q
        # eram normalizadas: G e O entravam cruas. Como `decidir` decide conflito
        # por igualdade de STRING, um chamado cuja categoria o GLPI mesclou
        # aparecia com C ja no nome novo e G/O ainda no nome antigo -- duas
        # conferencias 'Correto' apontando para strings diferentes, ou seja,
        # conflito artificial. Ver o salto de 201 para 7.469 conflitos em
        # 2026-08-01, apos a mesclagem de categorias no GLPI.
        out[pos] = decidir(pl.normalizar_categoria(cel(linha, col_historico)),
                           pl.normalizar_categoria(cel(linha, col_ia1)),
                           pl.normalizar_categoria(cel(linha, col_reclass)),
                           v_glpi, v_ia, v_reclass, categoria_manual)
    return out


def verdade_validada(decisoes: dict[int, dict[str, Any]]) -> dict[int, str]:
    """{linha: categoria decidida} apenas dos chamados com decisao travada."""
    return {ln: d["decidida"] for ln, d in decisoes.items() if d.get("decidida")}


def resumo_decisoes(decisoes: dict[int, dict[str, Any]]) -> dict[str, Any]:
    dec = sum(1 for d in decisoes.values() if d["status"] == STATUS_DECIDIDO)
    res = sum(1 for d in decisoes.values() if d["status"] == STATUS_RESTRITO)
    conf = sum(1 for d in decisoes.values() if d.get("conflito"))
    return {"com_conferencia": len(decisoes), "decididos": dec,
            "restritos": res, "conflitos": conf}
