#!/usr/bin/env python3
"""Deriva a conferencia de CADA IA a partir da conferencia humana do GLPI (M).

MOTIVACAO (decisao do pesquisador, 2026-08-01): a coluna N (CONFERENCIA IA)
conferia UMA unica IA -- a de producao, na coluna G. Com 7 modelos comparaveis
mais o BERTimbau, uma coluna so nao representa o experimento, e reconferir a mao
oito vezes e inviavel. Em vez disso, a verdade e derivada mecanicamente:

    M = 'Correto'  -> a categoria do GLPI (C) e a verdade.
                      Para cada IA: predicao == C ? 'Correto' : 'Errado'.
    M = 'Errado'   -> o GLPI errou; a verdade so existe se o avaliador tiver
                      preenchido Q (CATEGORIA CORRETA MANUAL). Com Q preenchida,
                      a verdade e Q e as IAs sao avaliadas contra ela. Sem Q,
                      a linha fica PENDENTE (nada e afirmado).
    M vazio        -> sem conferencia; linha ignorada.

Isso e mais confiavel que N porque nao depende de o avaliador ter olhado a
predicao de cada modelo: ele julga uma vez a categoria do GLPI, e o resto e
comparacao de strings.

INDEXACAO POR id_chamado, NUNCA por numero de linha: a fonte do IMPORTRANGE
reordenou as linhas em 28/07/2026 e o historico indexado por linha passou a
apontar para chamados errados (ver scripts/migracoes/verificar_alinhamento_linhas.py).
As predicoes vem das abas CLASSIF__<modelo>, que guardam id_chamado.

O BERTimbau (transformer_ft) nao tem CLASSIF__ materializada sobre a base
inteira: a predicao dele vive na coluna O (Classificacao IA - 2), preenchida
so para os chamados reclassificados. Por isso ele entra com cobertura parcial,
e a cobertura e reportada por modelo.

Todas as categorias passam por planilha.normalizar_categoria antes da
comparacao -- sem isso, categorias que o GLPI mesclou aparecem como divergencia
falsa (incidente de 2026-08-01).

Sem --aplicar: dry-run (calcula, imprime o resumo, escreve o JSON local se
--json for passado, mas nao grava na planilha).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matriz_confusao_multimodelo as mc  # noqa: E402
import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
SAIDA_PADRAO = RAIZ / "docs" / "dados" / "conferencia_derivada.json"
SAIDA_MATRIZ_PADRAO = RAIZ / "docs" / "dados" / "matriz_confusao.json"

ABA_SAIDA_PADRAO = "CONFERENCIA_MULTIMODELO"
MODELO_COLUNA_O = "transformer_ft"

# Indices 0-based em CLASSIF__<modelo> (ver classificacao_multimodelo.py:192).
I_CLASSIF_ID = 2
I_CLASSIF_CATEGORIA = 4

def normalizar_id(valor: Any) -> str:
    """UNFORMATTED_VALUE devolve numero (1693.0); padroniza para string."""
    s = str(valor or "").strip()
    if not s:
        return ""
    try:
        return str(int(float(s)))
    except (TypeError, ValueError):
        return s


CORRETO = "Correto"
ERRADO = "Errado"
PENDENTE = ""

FONTE_GLPI = "glpi"
FONTE_MANUAL = "manual"


def norm_veredito(valor: Any) -> str:
    """'Correto' (exato, sem caixa) = acerto; qualquer outro nao vazio = erro."""
    s = str(valor or "").strip()
    if not s:
        return ""
    return CORRETO if s.casefold() == "correto" else ERRADO


def verdade_do_chamado(conf_glpi: str, categoria_glpi: str,
                       categoria_manual: str) -> tuple[str, str]:
    """Retorna (verdade, fonte). Verdade vazia = pendente, nada a afirmar."""
    veredito = norm_veredito(conf_glpi)
    if veredito == CORRETO and categoria_glpi:
        return categoria_glpi, FONTE_GLPI
    if veredito == ERRADO and categoria_manual:
        return categoria_manual, FONTE_MANUAL
    return "", ""


def conferir(predicao: str, verdade: str) -> str:
    """Conferencia de UMA IA contra a verdade. Vazio quando nada a afirmar."""
    if not verdade or not predicao:
        return PENDENTE
    return CORRETO if predicao == verdade else ERRADO


def montar_linhas(chamados: list[dict[str, Any]], modelos: list[str],
                  predicoes: dict[str, dict[str, str]]
                  ) -> tuple[list[list[Any]], dict[str, Any]]:
    """Monta as linhas da aba e o resumo. Logica pura, testavel offline.

    chamados: [{id, linha, categoria_glpi, conf_glpi, categoria_manual}]
    predicoes: {modelo: {id_chamado: categoria_prevista}}
    """
    linhas: list[list[Any]] = []
    resumo: dict[str, Any] = {
        "total_chamados": len(chamados),
        "com_conferencia_glpi": 0,
        "verdade_glpi": 0,
        "verdade_manual": 0,
        "pendente_glpi_errado_sem_q": 0,
        "sem_conferencia": 0,
        # Anomalias de preenchimento. Q so faz sentido quando M='Errado'; com
        # M='Correto' a verdade ja e C e um Q preenchido indica engano de
        # digitacao ou criterio. Nao altera a derivacao (verdade_do_chamado
        # ignora Q quando M='Correto'), mas precisa ser visto pelo pesquisador.
        "correto_com_q_preenchida": 0,
        # M='Errado' com Q identica a C: contradiz o proprio veredito.
        "errado_com_q_igual_a_c": 0,
        "por_modelo": {},
    }
    ids_correto_com_q: list[str] = []
    ids_errado_com_q_igual_c: list[str] = []
    distribuicao_q: defaultdict[str, int] = defaultdict(int)
    contagem = {m: defaultdict(int) for m in modelos}

    for ch in chamados:
        veredito = norm_veredito(ch["conf_glpi"])
        if not veredito:
            resumo["sem_conferencia"] += 1
            continue
        resumo["com_conferencia_glpi"] += 1

        manual = ch["categoria_manual"]
        if veredito == CORRETO and manual:
            resumo["correto_com_q_preenchida"] += 1
            ids_correto_com_q.append(ch["id"])
        if veredito == ERRADO and manual:
            distribuicao_q[manual] += 1
            if manual == ch["categoria_glpi"]:
                resumo["errado_com_q_igual_a_c"] += 1
                ids_errado_com_q_igual_c.append(ch["id"])

        verdade, fonte = verdade_do_chamado(
            ch["conf_glpi"], ch["categoria_glpi"], ch["categoria_manual"])
        if fonte == FONTE_GLPI:
            resumo["verdade_glpi"] += 1
        elif fonte == FONTE_MANUAL:
            resumo["verdade_manual"] += 1
        else:
            resumo["pendente_glpi_errado_sem_q"] += 1

        linha = [ch["id"], ch["linha"], ch["categoria_glpi"], veredito,
                 ch["categoria_manual"], verdade, fonte or "pendente"]
        for m in modelos:
            prevista = predicoes.get(m, {}).get(ch["id"], "")
            conf = conferir(prevista, verdade)
            linha.extend([prevista, conf])
            if not prevista:
                contagem[m]["sem_predicao"] += 1
            elif conf == CORRETO:
                contagem[m]["correto"] += 1
            elif conf == ERRADO:
                contagem[m]["errado"] += 1
            else:
                contagem[m]["pendente"] += 1
        linhas.append(linha)

    for m in modelos:
        c = contagem[m]
        avaliados = c["correto"] + c["errado"]
        resumo["por_modelo"][m] = {
            "correto": c["correto"],
            "errado": c["errado"],
            "pendente": c["pendente"],
            "sem_predicao": c["sem_predicao"],
            "avaliados": avaliados,
            "acuracia": round(c["correto"] / avaliados, 4) if avaliados else None,
        }

    # Distribuicao das categorias que o avaliador escreveu em Q (so as que viram
    # verdade, isto e, com M='Errado'). Ordenada por frequencia para o
    # pesquisador ver de imediato para onde as correcoes puxaram a base.
    resumo["distribuicao_q"] = dict(
        sorted(distribuicao_q.items(), key=lambda kv: (-kv[1], kv[0])))
    resumo["categorias_distintas_q"] = len(distribuicao_q)
    # Amostra dos IDs anomalos: o suficiente para o pesquisador ir na planilha
    # conferir, sem inchar o JSON publicado no painel.
    resumo["ids_correto_com_q_preenchida"] = ids_correto_com_q[:50]
    resumo["ids_errado_com_q_igual_a_c"] = ids_errado_com_q_igual_c[:50]
    return linhas, resumo


def cabecalho(modelos: list[str]) -> list[str]:
    cab = ["id_chamado", "linha_planilha", "categoria_glpi", "conferencia_glpi",
           "categoria_manual", "verdade", "fonte_verdade"]
    for m in modelos:
        cab.extend([f"predicao_{m}", f"conferencia_{m}"])
    return cab


def ler_chamados(sh, config: dict) -> list[dict[str, Any]]:
    ws = sh.worksheet(config["aba_principal"])
    bloco = ws.get_values("A:Q", value_render_option="UNFORMATTED_VALUE")
    cab = bloco[0] if bloco else []
    c_id = pl.localizar_coluna(cab, ("ID Chamado", "ID"), 1)
    c_cat = pl.localizar_coluna(cab, ("CATEGORIA COMPLETA",), 3)
    c_m = pl.localizar_coluna(cab, ("CONFERENCIA GLPI", "CONFERÊNCIA GLPI"), 13)
    c_q = pl.localizar_coluna(cab, ("CATEGORIA CORRETA MANUAL",), 17)

    def cel(linha, c1):
        i = c1 - 1
        return str(linha[i] or "").strip() if len(linha) > i else ""

    out = []
    for pos, linha in enumerate(bloco[1:], start=2):
        id_chamado = normalizar_id(cel(linha, c_id))
        if not id_chamado:
            continue
        out.append({
            "id": id_chamado,
            "linha": pos,
            "categoria_glpi": pl.normalizar_categoria(cel(linha, c_cat)),
            "conf_glpi": cel(linha, c_m),
            "categoria_manual": pl.normalizar_categoria(cel(linha, c_q)),
        })
    return out


def ler_predicoes(sh, config: dict, modelos: list[str]) -> dict[str, dict[str, str]]:
    mm = config.get("multimodelo", {}) or {}
    padrao = mm.get("aba_classificacao", "CLASSIF__{modelo}")
    out: dict[str, dict[str, str]] = {}

    for modelo in modelos:
        if modelo == MODELO_COLUNA_O:
            continue
        aba = padrao.replace("{modelo}", modelo)
        try:
            vals = sh.worksheet(aba).get_values(
                "A:K", value_render_option="UNFORMATTED_VALUE")
        except Exception as exc:  # noqa: BLE001
            print(f"[{modelo}] aba {aba} indisponivel: {type(exc).__name__}: {exc}",
                  file=sys.stderr)
            out[modelo] = {}
            continue
        mapa: dict[str, str] = {}
        for reg in vals[1:]:
            if len(reg) <= I_CLASSIF_CATEGORIA:
                continue
            id_chamado = normalizar_id(reg[I_CLASSIF_ID])
            cat = pl.normalizar_categoria(str(reg[I_CLASSIF_CATEGORIA] or "").strip())
            if id_chamado and cat:
                mapa[id_chamado] = cat
        out[modelo] = mapa
        print(f"[{modelo}] predicoes lidas de {aba}: {len(mapa)}")

    if MODELO_COLUNA_O in modelos:
        ws = sh.worksheet(config["aba_principal"])
        bloco = ws.get_values("A:Q", value_render_option="UNFORMATTED_VALUE")
        cab = bloco[0] if bloco else []
        c_id = pl.localizar_coluna(cab, ("ID Chamado", "ID"), 1)
        c_o = pl.localizar_coluna(
            cab, ("Classificacao IA - 2", "Classificação IA - 2"), 15)
        mapa = {}
        for linha in bloco[1:]:
            def cel(c1):
                i = c1 - 1
                return str(linha[i] or "").strip() if len(linha) > i else ""
            id_chamado = normalizar_id(cel(c_id))
            cat = pl.normalizar_categoria(cel(c_o))
            if id_chamado and cat:
                mapa[id_chamado] = cat
        out[MODELO_COLUNA_O] = mapa
        print(f"[{MODELO_COLUNA_O}] predicoes lidas da coluna O: {len(mapa)} "
              "(cobertura parcial, por natureza)")
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--aba-saida", default=ABA_SAIDA_PADRAO)
    p.add_argument("--json", type=Path, default=SAIDA_PADRAO,
                   help="Resumo sanitizado para o dashboard.")
    p.add_argument("--json-matriz", type=Path, default=SAIDA_MATRIZ_PADRAO,
                   help="Matriz de confusao por modelo, para o dashboard.")
    p.add_argument("--aplicar", action="store_true",
                   help="Sem isso, nao grava a aba na planilha.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    mm = config.get("multimodelo", {}) or {}
    modelos = list(mm.get("modelos_leves", [])) + list(mm.get("modelos_pesados", []))
    print(f"modelos: {modelos}")

    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    chamados = ler_chamados(sh, config)
    print(f"chamados lidos: {len(chamados)}")
    predicoes = ler_predicoes(sh, config, modelos)

    linhas, resumo = montar_linhas(chamados, modelos, predicoes)
    resumo["gerado_em"] = agora_bahia()
    resumo["aba"] = args.aba_saida
    resumo["regra"] = (
        "M='Correto' -> verdade = C; M='Errado' + Q preenchida -> verdade = Q; "
        "M='Errado' sem Q -> pendente; M vazio -> ignorado")

    print("\n=== RESUMO ===")
    print(f"  chamados                      : {resumo['total_chamados']}")
    print(f"  com conferencia GLPI (M)      : {resumo['com_conferencia_glpi']}")
    print(f"  verdade vinda do GLPI (M=OK)  : {resumo['verdade_glpi']}")
    print(f"  verdade vinda da coluna Q     : {resumo['verdade_manual']}")
    print(f"  pendente (M=Errado, Q vazia)  : {resumo['pendente_glpi_errado_sem_q']}")
    print(f"  sem conferencia               : {resumo['sem_conferencia']}")

    print("\n=== ANOMALIAS DE PREENCHIMENTO ===")
    print(f"  M='Correto' com Q preenchida  : {resumo['correto_com_q_preenchida']}")
    if resumo["ids_correto_com_q_preenchida"]:
        print(f"    IDs (ate 50): "
              f"{', '.join(resumo['ids_correto_com_q_preenchida'])}")
    print(f"  M='Errado' com Q igual a C    : {resumo['errado_com_q_igual_a_c']}")
    if resumo["ids_errado_com_q_igual_a_c"]:
        print(f"    IDs (ate 50): "
              f"{', '.join(resumo['ids_errado_com_q_igual_a_c'])}")

    print(f"\n=== DISTRIBUICAO DE Q ({resumo['categorias_distintas_q']} "
          "categorias distintas) ===")
    for cat, n in resumo["distribuicao_q"].items():
        print(f"  {n:>6}  {cat}")

    print("\n  modelo                  correto  errado  s/pred  acuracia")
    for m in modelos:
        r = resumo["por_modelo"][m]
        acc = f"{r['acuracia']:.4f}" if r["acuracia"] is not None else "   -  "
        print(f"  {m:<22} {r['correto']:>7} {r['errado']:>7} "
              f"{r['sem_predicao']:>7}  {acc}")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(resumo, ensure_ascii=False, indent=1),
                             encoding="utf-8")
        print(f"\nresumo escrito em {args.json}")

    # Matriz de confusao: mesma leitura da planilha, segundo artefato. A verdade
    # cresce sozinha conforme M e Q sao preenchidas, entao nao ha recorte fixo.
    if args.json_matriz:
        verdades = {}
        for ch in chamados:
            verdade, _fonte = verdade_do_chamado(
                ch["conf_glpi"], ch["categoria_glpi"], ch["categoria_manual"])
            if verdade:
                verdades[ch["id"]] = verdade
        matriz = mc.construir(verdades, predicoes, modelos)
        matriz["gerado_em"] = resumo["gerado_em"]
        matriz["fonte_verdade"] = resumo["regra"]
        matriz["pendente_glpi_errado_sem_q"] = resumo["pendente_glpi_errado_sem_q"]
        matriz["verdade_glpi"] = resumo["verdade_glpi"]
        matriz["verdade_manual"] = resumo["verdade_manual"]
        cats = matriz["categorias"]
        for m in modelos:
            matriz["modelos"][m]["top_confusoes"] = mc.top_confusoes(
                matriz["modelos"][m], cats)
        args.json_matriz.parent.mkdir(parents=True, exist_ok=True)
        args.json_matriz.write_text(
            json.dumps(matriz, ensure_ascii=False), encoding="utf-8")
        print(f"matriz de confusao escrita em {args.json_matriz} "
              f"({len(cats)} categorias, {len(verdades)} chamados com verdade)")

    if not args.aplicar:
        print("\nDRY-RUN: aba nao gravada. Rode com --aplicar para gravar.")
        return 0

    pl.escrever_aba(sh, args.aba_saida, cabecalho(modelos), linhas)
    print(f"\nOK: aba {args.aba_saida} gravada com {len(linhas)} linha(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
