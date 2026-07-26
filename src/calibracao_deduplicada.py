#!/usr/bin/env python3
"""Calibração da Etapa 1 com deduplicação defensiva do snapshot.

O SNAPSHOT_ETAPA_1 é append-only. Durante rematerializações, uma mesma
``linha_planilha`` pode aparecer várias vezes. A calibração deve considerar
somente o estado mais recente de cada linha, como já faz o exportador de
``registros.json``. Este módulo envolve ``calibracao.calcular`` sem alterar a
leitura das demais abas e mantém a última ocorrência de cada linha.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import calibracao as base  # noqa: E402
import planilha as pl  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
SAIDA = RAIZ / "docs" / "dados" / "calibracao.json"
_CALCULAR_BASE = base.calcular


def deduplicar_snapshot(valores: list[list[Any]]) -> tuple[list[list[Any]], int]:
    """Mantém cabeçalho e a última ocorrência de cada ``linha_planilha``.

    A coluna ``linha_planilha`` ocupa o índice 1 no esquema atual do
    SNAPSHOT_ETAPA_1. Linhas sem chave não são descartadas nem combinadas.
    A ordem final segue a posição da última ocorrência no snapshot.
    """
    if len(valores) < 2:
        return valores, 0

    cabecalho = valores[0]
    ultimas: dict[str, tuple[int, list[Any]]] = {}
    sem_chave: list[tuple[int, list[Any]]] = []

    for posicao, linha in enumerate(valores[1:], start=1):
        chave = str(linha[1]).strip() if len(linha) > 1 else ""
        if chave:
            ultimas[chave] = (posicao, linha)
        else:
            sem_chave.append((posicao, linha))

    consolidadas = sorted([*ultimas.values(), *sem_chave], key=lambda item: item[0])
    saida = [cabecalho, *(linha for _, linha in consolidadas)]
    removidas = len(valores) - len(saida)
    return saida, removidas


class _WorksheetSnapshotDeduplicado:
    def __init__(self, worksheet):
        self._worksheet = worksheet
        self.duplicadas_removidas = 0

    def get_values(self, *args, **kwargs):
        valores = self._worksheet.get_values(*args, **kwargs)
        valores, removidas = deduplicar_snapshot(valores)
        self.duplicadas_removidas = removidas
        return valores

    def __getattr__(self, nome):
        return getattr(self._worksheet, nome)


class _SpreadsheetSnapshotDeduplicado:
    def __init__(self, spreadsheet, aba_snapshot: str):
        self._spreadsheet = spreadsheet
        self._aba_snapshot = aba_snapshot
        self.snapshot_wrapper: _WorksheetSnapshotDeduplicado | None = None

    def worksheet(self, nome: str):
        worksheet = self._spreadsheet.worksheet(nome)
        if nome == self._aba_snapshot:
            self.snapshot_wrapper = _WorksheetSnapshotDeduplicado(worksheet)
            return self.snapshot_wrapper
        return worksheet

    def __getattr__(self, nome):
        return getattr(self._spreadsheet, nome)


def calcular(sh, config: dict) -> dict:
    aba_snapshot = config["abas_experimento"]["snapshot_etapa_1"]
    proxy = _SpreadsheetSnapshotDeduplicado(sh, aba_snapshot)
    dados = _CALCULAR_BASE(proxy, config)
    removidas = proxy.snapshot_wrapper.duplicadas_removidas if proxy.snapshot_wrapper else 0
    dados["snapshot_deduplicacao"] = {
        "chave": "linha_planilha",
        "criterio": "mantida a ultima ocorrencia",
        "linhas_duplicadas_removidas": removidas,
    }
    return dados


def main() -> int:
    with CONFIG_PADRAO.open(encoding="utf-8") as arquivo:
        config = json.load(arquivo)
    try:
        sh = pl.abrir_planilha(pl.id_planilha(config))
    except Exception as exc:  # noqa: BLE001
        print(f"Falha ao acessar a planilha: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    dados = calcular(sh, config)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    removidas = dados["snapshot_deduplicacao"]["linhas_duplicadas_removidas"]
    print(
        f"total={dados['total']} | validados={dados['validados']} | "
        f"ECE_historico={dados['ece_historico']} | duplicadas_removidas={removidas}"
    )
    print(f"saida={SAIDA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
