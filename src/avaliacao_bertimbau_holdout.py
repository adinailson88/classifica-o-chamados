#!/usr/bin/env python3
"""Avalia oito modelos no mesmo lote held-out usado pelo BERTimbau.

A rotina lê apenas a aba privada COMPARACAO_PREVISOES. O lote de referência é a
execução mais recente e completa de ``transformer_ft``. Para cada outro modelo,
seleciona uma execução com exatamente o mesmo conjunto de linhas. Em seguida,
compara as previsões com:

- a categoria histórica, para descrever concordância no lote total;
- a verdade humana M/N/P/Q, para calcular acerto validado no subconjunto decidido.

A saída é agregada e sanitizada: não contém texto, ID de chamado nem linha da
planilha. Este protocolo é separado da avaliação principal em CLASSIF__<modelo>,
pois o BERTimbau ainda não possui materialização OOF sobre toda a base.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import f1_score

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decisao_validada as dv  # noqa: E402
import planilha as pl  # noqa: E402
from avaliacao_final import ic_bootstrap, mcnemar_p  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
SAIDA_PADRAO = RAIZ / "docs" / "dados" / "avaliacao_bertimbau_holdout.json"
MODELO_BERTIMBAU = "transformer_ft"


def parse_float(valor: Any) -> float:
    try:
        numero = float(str(valor).replace("%", "").replace(",", ".").strip())
        return numero / 100.0 if numero > 1 else numero
    except (TypeError, ValueError):
        return 0.0


def parse_data(valor: str) -> datetime:
    texto = str(valor or "").strip()
    for formato in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            continue
    return datetime.min


def carregar_registros_comparacao(sh, nome_aba: str) -> list[dict[str, Any]]:
    valores = sh.worksheet(nome_aba).get_values(
        "A:N", value_render_option="UNFORMATTED_VALUE"
    )
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

    i_modelo = indice("modelo")
    # id_chamado, nunca linha_planilha: COMPARACAO_PREVISOES e materializada num
    # momento e a aba principal muda de tamanho depois. Casar por linha faz a
    # predicao de um chamado ser comparada com a verdade de outro. Em 02/08/2026
    # a base caiu de 14.094 para 14.058 linhas e o held-out reportou 0,13 de
    # acerto onde media 0,68.
    i_id = indice("id_chamado")
    i_original = indice("categoria_original")
    i_prevista = indice("categoria_prevista")
    i_score = indice("score")
    i_execucao = indice("executado_em")
    obrigatorios = {
        "modelo": i_modelo,
        "id_chamado": i_id,
        "categoria_original": i_original,
        "categoria_prevista": i_prevista,
        "executado_em": i_execucao,
    }
    ausentes = [nome for nome, idx in obrigatorios.items() if idx is None]
    if ausentes:
        raise RuntimeError(
            "COMPARACAO_PREVISOES sem colunas obrigatorias: " + ", ".join(ausentes)
        )

    def cel(linha: list[Any], idx: int | None) -> str:
        return str(linha[idx] or "").strip() if idx is not None and idx < len(linha) else ""

    saida: list[dict[str, Any]] = []
    for linha in valores[1:]:
        modelo = cel(linha, i_modelo).casefold()
        prevista = pl.normalizar_categoria(cel(linha, i_prevista))
        original = pl.normalizar_categoria(cel(linha, i_original))
        execucao = cel(linha, i_execucao)
        chave = dv._normalizar_id(cel(linha, i_id))  # noqa: SLF001
        if not chave:
            continue
        if not modelo or not prevista or not original or not execucao:
            continue
        saida.append(
            {
                "modelo": modelo,
                "chave": chave,
                "original": original,
                "prevista": prevista,
                "score": parse_float(cel(linha, i_score)),
                "execucao": execucao,
            }
        )
    return saida


def agrupar_execucoes(
    registros: list[dict[str, Any]],
) -> dict[str, dict[str, dict[int, dict[str, Any]]]]:
    grupos: dict[str, dict[str, dict[int, dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for registro in registros:
        grupos[registro["modelo"]][registro["execucao"]][registro["chave"]] = registro
    return {modelo: dict(execus) for modelo, execus in grupos.items()}


def selecionar_lote_bertimbau(
    grupos: dict[str, dict[str, dict[int, dict[str, Any]]]], min_lote: int
) -> tuple[str, dict[int, dict[str, Any]]]:
    execucoes = grupos.get(MODELO_BERTIMBAU, {})
    candidatos = [
        (execucao, lote)
        for execucao, lote in execucoes.items()
        if len(lote) >= min_lote
    ]
    if not candidatos:
        maior = max((len(lote) for lote in execucoes.values()), default=0)
        raise RuntimeError(
            f"Nenhuma execucao BERTimbau com ao menos {min_lote} previsoes; maior lote={maior}."
        )
    return max(candidatos, key=lambda item: (len(item[1]), parse_data(item[0])))


def selecionar_execucao_exata(
    execucoes: dict[str, dict[int, dict[str, Any]]], linhas_alvo: set[int]
) -> tuple[str, dict[int, dict[str, Any]]] | None:
    candidatos = [
        (execucao, lote)
        for execucao, lote in execucoes.items()
        if set(lote) == linhas_alvo
    ]
    if not candidatos:
        return None
    return max(candidatos, key=lambda item: parse_data(item[0]))


def calcular_metricas_modelo(
    lote: dict[int, dict[str, Any]],
    linhas_alvo: list[int],
    linhas_validadas: list[int],
    verdade: dict[int, str],
    n_boot: int,
) -> tuple[dict[str, Any], np.ndarray]:
    historico = np.array(
        [int(lote[linha]["prevista"] == lote[linha]["original"]) for linha in linhas_alvo],
        dtype=float,
    )
    acertos_validados = np.array(
        [int(lote[linha]["prevista"] == verdade[linha]) for linha in linhas_validadas],
        dtype=float,
    )
    y_historico = [lote[linha]["original"] for linha in linhas_alvo]
    y_predito = [lote[linha]["prevista"] for linha in linhas_alvo]
    lo, hi = ic_bootstrap(acertos_validados, n_boot=n_boot)
    return (
        {
            "n_total": len(linhas_alvo),
            "concordancia_historico": round(float(historico.mean()), 4),
            "f1_macro_historico": round(
                float(f1_score(y_historico, y_predito, average="macro", zero_division=0)),
                4,
            ),
            "n_validado": len(linhas_validadas),
            "acerto_validado": round(float(acertos_validados.mean()), 4),
            "ic95_validado": [round(lo, 4), round(hi, 4)],
            "confianca_media": round(
                float(np.mean([lote[linha]["score"] for linha in linhas_alvo])), 4
            ),
        },
        acertos_validados,
    )


def construir_avaliacao(
    registros: list[dict[str, Any]],
    decisoes: dict[int, dict[str, Any]],
    modelos_esperados: list[str],
    min_lote: int = 500,
    min_validados: int = 50,
    n_boot: int = 2000,
) -> dict[str, Any]:
    grupos = agrupar_execucoes(registros)
    execucao_bertimbau, lote_bertimbau = selecionar_lote_bertimbau(grupos, min_lote)
    linhas_alvo_set = set(lote_bertimbau)
    linhas_alvo = sorted(linhas_alvo_set)

    lotes: dict[str, dict[int, dict[str, Any]]] = {}
    execucoes_usadas: dict[str, str] = {}
    faltantes: list[str] = []
    for modelo in modelos_esperados:
        selecionado = selecionar_execucao_exata(grupos.get(modelo, {}), linhas_alvo_set)
        if selecionado is None:
            faltantes.append(modelo)
            continue
        execucao, lote = selecionado
        execucoes_usadas[modelo] = execucao
        lotes[modelo] = lote

    if faltantes:
        raise RuntimeError(
            "Modelos sem execucao no mesmo lote do BERTimbau: " + ", ".join(faltantes)
        )

    verdade = dv.verdade_validada(decisoes)
    linhas_validadas = [linha for linha in linhas_alvo if linha in verdade]
    if len(linhas_validadas) < min_validados:
        raise RuntimeError(
            f"Apenas {len(linhas_validadas)} linhas do holdout possuem verdade validada; "
            f"minimo={min_validados}."
        )

    resultados: list[dict[str, Any]] = []
    acertos: dict[str, np.ndarray] = {}
    for modelo in modelos_esperados:
        metrica, vetor = calcular_metricas_modelo(
            lotes[modelo], linhas_alvo, linhas_validadas, verdade, n_boot
        )
        resultados.append(
            {
                "modelo": modelo,
                "execucao": execucoes_usadas[modelo],
                **metrica,
            }
        )
        acertos[modelo] = vetor

    resultados.sort(key=lambda item: -item["acerto_validado"])
    for posicao, item in enumerate(resultados, start=1):
        item["posicao_validada"] = posicao

    bert = next(item for item in resultados if item["modelo"] == MODELO_BERTIMBAU)
    melhor_outro = next(
        item for item in resultados if item["modelo"] != MODELO_BERTIMBAU
    )
    vetor_bert = acertos[MODELO_BERTIMBAU]
    vetor_outro = acertos[melhor_outro["modelo"]]
    so_bert = int(((vetor_bert == 1) & (vetor_outro == 0)).sum())
    so_outro = int(((vetor_bert == 0) & (vetor_outro == 1)).sum())

    resumo_decisoes = dv.resumo_decisoes(decisoes)
    return {
        "gerado_em": agora_bahia(),
        "schema_version": "1.0",
        "status": "ok",
        "natureza": (
            "comparacao held-out no mesmo lote; concordancia historica e acerto humano "
            "M/N/P/Q apresentados separadamente"
        ),
        "protocolo": {
            "aba_origem": "COMPARACAO_PREVISOES",
            "lote_bertimbau": execucao_bertimbau,
            "n_lote": len(linhas_alvo),
            "n_validado_no_lote": len(linhas_validadas),
            "selecao": (
                "mesmo conjunto de linhas da execucao BERTimbau; cada modelo treinado "
                "fora do lote pelo protocolo comparar_modelos_lote.py"
            ),
            "separado_da_avaliacao_principal": True,
            "motivo_separacao": (
                "BERTimbau nao possui CLASSIF__transformer_ft OOF sobre toda a base; "
                "nao deve ser inserido artificialmente no ranking integral de sete modelos"
            ),
        },
        "decisoes_base_completa": resumo_decisoes,
        "modelos": resultados,
        "bertimbau": {
            "posicao_validada": bert["posicao_validada"],
            "acerto_validado": bert["acerto_validado"],
            "ic95_validado": bert["ic95_validado"],
            "concordancia_historico": bert["concordancia_historico"],
            "f1_macro_historico": bert["f1_macro_historico"],
            "comparado_a": melhor_outro["modelo"],
            "delta_validado": round(
                bert["acerto_validado"] - melhor_outro["acerto_validado"], 4
            ),
            "p_mcnemar": mcnemar_p(so_bert, so_outro),
            "discordantes": {
                "so_bertimbau_acerta": so_bert,
                "so_melhor_outro_acerta": so_outro,
            },
        },
        "limitacoes": [
            "O lote corresponde aos primeiros registros elegiveis, nao a uma amostra probabilistica.",
            "O acerto validado descreve somente as linhas do lote que possuem decisao humana travada.",
            "Os resultados held-out nao substituem a avaliacao integral OOF dos sete modelos materializados.",
            "O modo automatico do BERTimbau usa subamostragem estratificada e early stopping por limite computacional.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Avalia BERTimbau e sete modelos no mesmo lote held-out."
    )
    parser.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    parser.add_argument("--credenciais", default=None)
    parser.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    parser.add_argument("--min-lote", type=int, default=500)
    parser.add_argument("--min-validados", type=int, default=50)
    parser.add_argument("--n-boot", type=int, default=2000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
        aba_comparacao = config["abas_experimento"]["comparacao_previsoes"]
        registros = carregar_registros_comparacao(sh, aba_comparacao)
        # chave="id": a verdade tem de casar com COMPARACAO_PREVISOES por
        # id_chamado. Ver o comentario em carregar_registros_comparacao.
        decisoes = dv.carregar_decisoes(sh, config["aba_principal"], chave="id")
        modelos = list(config["multimodelo"]["modelos_leves"]) + list(
            config["multimodelo"].get("modelos_pesados", [])
        )
        resultado = construir_avaliacao(
            registros,
            decisoes,
            modelos,
            min_lote=args.min_lote,
            min_validados=args.min_validados,
            n_boot=args.n_boot,
        )
    except Exception as erro:  # noqa: BLE001
        print(
            f"Falha na avaliacao held-out do BERTimbau: {type(erro).__name__}: {erro}",
            file=sys.stderr,
        )
        return 1

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    bert = resultado["bertimbau"]
    print(
        f"OK: n_lote={resultado['protocolo']['n_lote']} | "
        f"n_validado={resultado['protocolo']['n_validado_no_lote']} | "
        f"BERTimbau={bert['acerto_validado']} | posicao={bert['posicao_validada']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
