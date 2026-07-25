#!/usr/bin/env python3
"""Migra nomes de categoria obsoletos na coluna 'CATEGORIA COMPLETA' (C) da
planilha experimental principal, usando o mapa de-para em
config_categorias_canonicas.json (fonte unica de verdade, tambem consumida
em memoria por src/planilha.py::normalizar_categoria em todo o pipeline de
classificacao/reclassificacao — este script corrige o dado JA GRAVADO na
planilha; normalizar_categoria evita que o dado errado volte a ser
aprendido/gravado no futuro).

Escopo: SO a coluna C da aba principal (verdade GLPI). NAO toca nas abas
CLASSIF__<modelo>/RECLASS__<modelo> (sao logs historicos do que a IA
efetivamente previu em cada rodada — reescreve-las corromperia a trilha de
auditoria) nem em nenhum docs/dados/*.json (esses sao regenerados pelos
workflows a partir da planilha ja corrigida).

Sem --aplicar = dry-run (so mostra quantas linhas cada mapeamento afetaria).
Acesso via conta de servico (gspread), igual aos demais scripts do repo.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import planilha as pl  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
CONFIG_PADRAO = RAIZ / "config_experimento.json"


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--aplicar", action="store_true",
                    help="Grava as correcoes na coluna C. Sem esta flag, so relata.")
    return p.parse_args()


def calcular_correcoes(ws, config: dict, mapa_categorias: dict[str, str]
                       ) -> tuple[int, dict[int, str], dict[str, int]]:
    """Le a coluna 'CATEGORIA COMPLETA' e retorna (indice_coluna_1based,
    {linha: nome_corrigido}, {nome_antigo: qtd}) para as linhas cujo valor
    atual e uma chave do mapa. Nao escreve nada — leitura pura."""
    col_c = pl.indice_coluna_por_cabecalho(ws, "CATEGORIA COMPLETA", 3)
    valores = pl.ler_valores(ws, config.get("range_leitura", "A:M"))
    a_corrigir: dict[int, str] = {}
    contagem: dict[str, int] = {k: 0 for k in mapa_categorias}
    if not valores:
        return col_c, a_corrigir, contagem
    idx_c = col_c - 1  # 0-based dentro da linha lida
    for pos, linha in enumerate(valores[1:], start=2):
        valor_atual = str(linha[idx_c] or "").strip() if idx_c < len(linha) else ""
        if valor_atual in mapa_categorias:
            a_corrigir[pos] = mapa_categorias[valor_atual]
            contagem[valor_atual] += 1
    return col_c, a_corrigir, contagem


def main() -> int:
    args = parse_args()
    mapa_categorias = pl._carregar_mapa_categorias_canonicas()  # noqa: SLF001
    if not mapa_categorias:
        print("config_categorias_canonicas.json vazio ou nao encontrado — nada a migrar.")
        return 0

    import json
    config = json.loads(args.config.read_text(encoding="utf-8"))

    try:
        sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
        ws = sh.worksheet(config["aba_principal"])
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001
        print(f"Falha ao acessar a planilha: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    col_c, a_corrigir, contagem = calcular_correcoes(ws, config, mapa_categorias)

    print(f"aba={config['aba_principal']} | coluna_categoria={pl._coluna_letra(col_c)} ({col_c})")  # noqa: SLF001
    for antigo, qtd in contagem.items():
        print(f"  '{antigo}' -> '{mapa_categorias[antigo]}': {qtd} linha(s)")
    print(f"total_a_corrigir={len(a_corrigir)}")

    if not a_corrigir:
        print("Nenhuma linha com nome de categoria obsoleto — nada a fazer.")
        return 0

    if not args.aplicar:
        print("dry-run: nenhuma escrita feita. Rode com --aplicar para gravar.")
        return 0

    gravadas = pl.escrever_coluna_por_linha(ws, col_c, a_corrigir)
    print(f"OK: {gravadas} linha(s) corrigida(s) na coluna {pl._coluna_letra(col_c)}.")  # noqa: SLF001
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
