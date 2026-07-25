#!/usr/bin/env python3
"""Migra nomes de categoria obsoletos numa coluna de VALOR LITERAL da aba
principal (por padrao, 'Classificacao IA' — a saida do proprio classificador,
que pode ter aprendido nomes de categoria que o GLPI ja renomeou), usando o
mapa de-para em config_categorias_canonicas.json (fonte unica de verdade,
tambem consumida em memoria por src/planilha.py::normalizar_categoria em
todo o pipeline de classificacao/reclassificacao — este script corrige o
dado JA GRAVADO na planilha; normalizar_categoria evita que o dado errado
volte a ser aprendido/gravado no futuro).

IMPORTANTE (incidente de 2026-07-25): a coluna 'CATEGORIA COMPLETA' (C) da
aba principal e um espelho IMPORTRANGE de outra planilha (nao tem valor
proprio) — escrever nela quebra o array/spill da formula para a aba
inteira. NUNCA rodar este script contra colunas A:F. O alvo padrao
('Classificacao IA') e valor literal, escrito pelos scripts de
classificacao — confirmado manualmente antes de habilitar este script.
Se for apontar para outra coluna via --coluna, confirme antes (via leitura
com value_render_option=FORMULA) que ela NAO comeca com '=' em nenhuma
linha amostrada.

Escopo: SO a coluna informada da aba principal. NAO toca em CATEGORIA
COMPLETA (C, IMPORTRANGE) nem nas abas CLASSIF__<modelo>/RECLASS__<modelo>
(sao logs historicos do que a IA efetivamente previu em cada rodada —
reescreve-las corromperia a trilha de auditoria) nem em docs/dados/*.json
(regenerados pelos workflows a partir da planilha ja corrigida).

Sem --aplicar = dry-run (so mostra quantas linhas cada mapeamento afetaria).
Acesso via conta de servico (gspread), igual aos demais scripts do repo.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import planilha as pl  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
COLUNA_PADRAO = "Classificação IA"
COLUNAS_PROIBIDAS = {"categoria completa", "categoria compelta"}  # IMPORTRANGE — nunca escrever


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--coluna", default=COLUNA_PADRAO,
                    help=f"Cabecalho da coluna a corrigir (padrao: '{COLUNA_PADRAO}').")
    p.add_argument("--aplicar", action="store_true",
                    help="Grava as correcoes na coluna. Sem esta flag, so relata.")
    return p.parse_args()


def calcular_correcoes(ws, config: dict, mapa_categorias: dict[str, str], nome_coluna: str
                       ) -> tuple[int, dict[int, str], dict[str, int]]:
    """Le a coluna informada e retorna (indice_coluna_1based,
    {linha: nome_corrigido}, {nome_antigo: qtd}) para as linhas cujo valor
    atual e uma chave do mapa. Nao escreve nada — leitura pura."""
    col = pl.indice_coluna_por_cabecalho(ws, nome_coluna, 7)
    valores = pl.ler_valores(ws, config.get("range_leitura", "A:M"))
    a_corrigir: dict[int, str] = {}
    contagem: dict[str, int] = {k: 0 for k in mapa_categorias}
    if not valores:
        return col, a_corrigir, contagem
    idx = col - 1  # 0-based dentro da linha lida
    for pos, linha in enumerate(valores[1:], start=2):
        valor_atual = str(linha[idx] or "").strip() if idx < len(linha) else ""
        if valor_atual in mapa_categorias:
            a_corrigir[pos] = mapa_categorias[valor_atual]
            contagem[valor_atual] += 1
    return col, a_corrigir, contagem


def confirmar_nao_e_formula(ws, col_1based: int, linhas_amostra: list[int]) -> bool:
    """Guarda de seguranca (pos-incidente de 2026-07-25): le uma amostra de
    celulas com value_render_option=FORMULA e recusa prosseguir se qualquer
    uma comecar com '=' (indicaria IMPORTRANGE/ARRAYFORMULA — nunca escrever)."""
    letra = pl._coluna_letra(col_1based)  # noqa: SLF001
    for linha in linhas_amostra:
        try:
            val = ws.acell(f"{letra}{linha}", value_render_option="FORMULA").value
        except Exception:  # noqa: BLE001
            continue
        if isinstance(val, str) and val.startswith("="):
            print(f"ABORTADO: {letra}{linha} contem formula ({val!r}) — "
                  "esta coluna nao e segura para escrita literal.", file=sys.stderr)
            return False
    return True


def main() -> int:
    args = parse_args()
    if args.coluna.strip().casefold() in COLUNAS_PROIBIDAS:
        print(f"ABORTADO: '{args.coluna}' e a coluna GLPI via IMPORTRANGE — nunca escrever nela "
              "(ver incidente de 2026-07-25 no historico deste script).", file=sys.stderr)
        return 3

    mapa_categorias = pl._carregar_mapa_categorias_canonicas()  # noqa: SLF001
    if not mapa_categorias:
        print("config_categorias_canonicas.json vazio ou nao encontrado — nada a migrar.")
        return 0

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

    col, a_corrigir, contagem = calcular_correcoes(ws, config, mapa_categorias, args.coluna)

    print(f"aba={config['aba_principal']} | coluna='{args.coluna}' ({pl._coluna_letra(col)}, {col})")  # noqa: SLF001
    for antigo, qtd in contagem.items():
        print(f"  '{antigo}' -> '{mapa_categorias[antigo]}': {qtd} linha(s)")
    print(f"total_a_corrigir={len(a_corrigir)}")

    if not a_corrigir:
        print("Nenhuma linha com nome de categoria obsoleto — nada a fazer.")
        return 0

    if not args.aplicar:
        print("dry-run: nenhuma escrita feita. Rode com --aplicar para gravar.")
        return 0

    amostra = list(a_corrigir)[:5]
    if not confirmar_nao_e_formula(ws, col, amostra):
        return 4

    gravadas = pl.escrever_coluna_por_linha(ws, col, a_corrigir)
    print(f"OK: {gravadas} linha(s) corrigida(s) na coluna {pl._coluna_letra(col)}.")  # noqa: SLF001
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
