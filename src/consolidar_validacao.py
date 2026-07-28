#!/usr/bin/env python3
"""Consolida memória, métricas e calibração pela verdade única M/N/P/Q.

A rotina reutiliza ``decisao_validada.py`` e ``memoria_validada.py``. Não
implementa regra paralela de verdade e exclui decisões contraditórias. Lê a aba
principal em A:Q e, somente com ``--aplicar``, atualiza abas privadas de apoio.
Nunca altera a aba principal nem as colunas M, N, O, P ou Q.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decisao_validada as dv  # noqa: E402
import memoria_validada as mv  # noqa: E402
import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"

ABA_MEMORIA = "MEMORIA_VALIDADA_CLASSIFICACAO"
ABA_METRICAS = "METRICAS_CLASSIFICACAO_2"
ABA_CALIBRACAO = "CALIBRACAO_VALIDADA"
ABA_CONTROLE = "CONTROLE_CLASSIFICACAO_2"


def carregar_config(caminho: Path) -> dict[str, Any]:
    with caminho.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def parse_float(valor: Any, default: float = 0.0) -> float:
    try:
        numero = float(str(valor).replace("%", "").replace(",", ".").strip())
        return numero / 100.0 if numero > 1 else numero
    except (TypeError, ValueError):
        return default


def metricas_binarias(registros: list[dict[str, Any]], campo_predicao: str) -> dict[str, Any]:
    avaliados = [
        registro
        for registro in registros
        if registro.get("verdade") and registro.get(campo_predicao)
    ]
    if not avaliados:
        return {"n": 0, "acertos": 0, "acuracia": None}
    acertos = sum(
        1 for registro in avaliados
        if registro[campo_predicao] == registro["verdade"]
    )
    return {
        "n": len(avaliados),
        "acertos": acertos,
        "acuracia": round(acertos / len(avaliados), 4),
    }


def construir_consolidacao(sh, config: dict[str, Any], gerado: str) -> dict[str, Any]:
    """Calcula a consolidação sem escrever na planilha."""
    aba = config["aba_principal"]
    ws = sh.worksheet(aba)
    valores = pl.ler_valores(ws, "A:Q")
    cabecalho = valores[0] if valores else []
    mapa = pl.mapa_cabecalhos(cabecalho)

    def indice(*nomes: str) -> int | None:
        for nome in nomes:
            encontrado = mapa.get(pl.normalizar_cabecalho(nome))
            if encontrado:
                return encontrado - 1
        return None

    def cel(linha: list[Any], idx: int | None) -> str:
        return str(linha[idx] or "").strip() if idx is not None and idx < len(linha) else ""

    i_categoria = indice("CATEGORIA COMPLETA")
    i_ia = indice("Classificacao IA", "Classificação IA")
    i_confianca = indice("Avaliacao (%)", "Avaliação (%)")
    i_reclass = indice("Classificacao IA - 2", "Classificação IA - 2")

    decisoes = dv.carregar_decisoes(sh, aba)
    resumo_decisoes = dv.resumo_decisoes(decisoes)
    memoria = mv.carregar_memoria_validada(sh, aba)

    registros: list[dict[str, Any]] = []
    for posicao, linha in enumerate(valores[1:], start=2):
        decisao = decisoes.get(posicao)
        verdade = ""
        fonte = ""
        if (
            decisao
            and decisao.get("status") == dv.STATUS_DECIDIDO
            and not decisao.get("conflito")
        ):
            verdade = pl.normalizar_categoria(str(decisao.get("decidida") or "").strip())
            fonte = str(decisao.get("fonte_decisao") or "")

        registros.append({
            "linha": posicao,
            "historico": pl.normalizar_categoria(cel(linha, i_categoria)),
            "ia_original": pl.normalizar_categoria(cel(linha, i_ia)),
            "confianca_ia": parse_float(cel(linha, i_confianca)),
            "reclassificacao": pl.normalizar_categoria(cel(linha, i_reclass)),
            "verdade": verdade,
            "fonte_verdade": fonte,
        })

    metrica_ia = metricas_binarias(registros, "ia_original")
    metrica_reclass = metricas_binarias(registros, "reclassificacao")

    faixas = {
        "<70": lambda valor: valor < 0.70,
        "70-95": lambda valor: 0.70 <= valor < 0.95,
        ">=95": lambda valor: valor >= 0.95,
    }
    calibracao = []
    for nome, pertence in faixas.items():
        avaliados = [
            registro for registro in registros
            if registro["verdade"]
            and registro["ia_original"]
            and pertence(registro["confianca_ia"])
        ]
        acertos = sum(
            1 for registro in avaliados
            if registro["ia_original"] == registro["verdade"]
        )
        calibracao.append({
            "faixa": nome,
            "n": len(avaliados),
            "acertos": acertos,
            "taxa": round(acertos / len(avaliados), 4) if avaliados else None,
        })

    peso_treino = int(config.get("memoria_validada", {}).get("peso_treino", 3))
    linhas_memoria = [
        [
            item.get("linha_planilha", ""),
            item.get("id_chamado", ""),
            str(item.get("texto", ""))[:500],
            item.get("categoria", ""),
            item.get("fonte_decisao", ""),
            peso_treino,
            "SIM",
            "",
            gerado,
        ]
        for item in memoria
    ]

    origens = Counter(
        str(decisao.get("fonte_decisao") or "")
        for decisao in decisoes.values()
        if decisao.get("status") == dv.STATUS_DECIDIDO
        and not decisao.get("conflito")
        and decisao.get("decidida")
    )

    return {
        "gerado_em": gerado,
        "regra_verdade": "decisao_validada M/N/P/Q; conflitos excluidos",
        "decisoes": resumo_decisoes,
        "memoria_validada": len(memoria),
        "origens": dict(origens),
        "metricas": {
            "ia_original_G": metrica_ia,
            "classificacao_ia_2_O": metrica_reclass,
        },
        "calibracao": calibracao,
        "linhas_memoria": linhas_memoria,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Consolida validação humana M/N/P/Q em abas privadas."
    )
    parser.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    parser.add_argument("--credenciais", default=None)
    parser.add_argument("--aplicar", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = carregar_config(args.config)
    gerado = agora_bahia()

    try:
        sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
        resultado = construir_consolidacao(sh, config, gerado)
    except FileNotFoundError as erro:
        print(str(erro), file=sys.stderr)
        return 2
    except Exception as erro:  # noqa: BLE001
        print(f"Falha ao consolidar validação: {type(erro).__name__}: {erro}", file=sys.stderr)
        return 1

    resumo_publico = {chave: valor for chave, valor in resultado.items() if chave != "linhas_memoria"}
    resumo_publico["modo"] = "aplicar" if args.aplicar else "dry-run"
    print(json.dumps(resumo_publico, ensure_ascii=False, indent=2))

    if not args.aplicar:
        print("modo=dry-run (nada gravado na planilha).")
        return 0

    pl.escrever_aba(
        sh,
        ABA_MEMORIA,
        [
            "linha",
            "id_chamado",
            "texto_resumido_opcional",
            "categoria_validada",
            "origem_validacao",
            "peso_treino",
            "usar_para_treino",
            "observacao_tecnica",
            "data_execucao",
        ],
        resultado["linhas_memoria"],
    )

    linhas_metricas = [
        [
            nome,
            metrica["n"],
            metrica["acertos"],
            "" if metrica["acuracia"] is None else metrica["acuracia"],
            gerado,
        ]
        for nome, metrica in resultado["metricas"].items()
    ]
    pl.escrever_aba(
        sh,
        ABA_METRICAS,
        ["modelo", "qtd_validados", "qtd_acertos", "acuracia_validada", "data_execucao"],
        linhas_metricas,
        colunas_percentuais=[4],
    )

    linhas_calibracao = [
        [
            item["faixa"],
            item["n"],
            item["acertos"],
            "" if item["taxa"] is None else item["taxa"],
            "IA original G vs verdade única M/N/P/Q",
            gerado,
        ]
        for item in resultado["calibracao"]
    ]
    pl.escrever_aba(
        sh,
        ABA_CALIBRACAO,
        [
            "faixa_confianca",
            "qtd_casos",
            "acertos",
            "taxa_acerto_real",
            "base_calibracao",
            "data_execucao",
        ],
        linhas_calibracao,
        colunas_percentuais=[4],
    )

    decisoes = resultado["decisoes"]
    pl.append_aba(
        sh,
        ABA_CONTROLE,
        [
            "data_execucao",
            "etapa",
            "status",
            "qtd_com_conferencia",
            "qtd_decididos",
            "qtd_restritos",
            "qtd_conflitos",
            "qtd_memoria",
            "regra_verdade",
        ],
        [[
            gerado,
            "consolidacao-validacao",
            "OK",
            decisoes["com_conferencia"],
            decisoes["decididos"],
            decisoes["restritos"],
            decisoes["conflitos"],
            resultado["memoria_validada"],
            resultado["regra_verdade"],
        ]],
    )
    print("OK: abas privadas de validação consolidadas pela regra M/N/P/Q.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
