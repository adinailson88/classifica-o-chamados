#!/usr/bin/env python3
"""Rematerializa a Etapa 1 oficial de produção (coluna G:K), preservando conferência humana.

Escopo restrito, por decisão explícita do pesquisador (rodada 20): ao
contrário de `resetar_experimento.py` (que também apaga N:P), este script
limpa SOMENTE G2:K{last_row} da aba principal:

    G Classificação IA · H Avaliação (%) · I Executor ·
    J Criticidade Atribuída por IA · K Comparação (fórmula)

NÃO toca em:
    - L (Classificado_Confiança_IA) — fórmula nativa da planilha que lê de
      H; recalcula sozinha para vazio/erro quando H fica vazio, sem
      precisar de limpeza explícita;
    - M (CONFERÊNCIA GLPI), N (CONFERÊNCIA IA), O (Classificação IA - 2),
      P (CONFERÊNCIA IA - 2), Q (CATEGORIA CORRETA MANUAL) — dados de
      conferência humana e da Etapa 2, fora do escopo desta rematerialização;
    - Nenhuma aba de log/histórico (LOG_TURNOS_CLASSIFICACAO,
      LOG_LINHA_A_LINHA, SNAPSHOT_ETAPA_1, EXPERIMENTO_CONFIG,
      METRICAS_EXPERIMENTO) — ficam com os registros antigos junto dos
      novos após a rematerialização; se quiser um histórico limpo, isso
      deve ser uma decisão separada e explícita.

Consequência esperada: como N (CONFERÊNCIA IA) permanece com o veredito
"Correto"/"Errado" referente à classificação ANTIGA de G, esse veredito
fica temporariamente desalinhado com o novo valor de G até ser
reconferido. Isso é intencional (decisão do pesquisador de preservar a
conferência já feita em vez de apagá-la), mas deve ficar registrado como
limitação até a reconferência acontecer.

Antes de limpar, faz BACKUP de A (ID) + G:K (valores atuais) numa aba nova
(`BACKUP_ETAPA1_<timestamp>`).

SEGURANÇA:
    - Sem --aplicar: dry-run. Conecta em modo SOMENTE LEITURA à planilha e
      reporta quantas linhas têm G não vazio (seriam limpas), sem escrever
      nada.
    - Só limpa de verdade com --aplicar E --confirmar REMATERIALIZAR.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tempo import FUSO_BAHIA  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
PALAVRA_CONFIRMACAO = "REMATERIALIZAR"
COL_G, COL_K = 7, 11


def contar_linhas_preenchidas(ws) -> int:
    """Conta quantas linhas (a partir da 2) têm G não vazio."""
    valores_g = ws.col_values(COL_G)[1:]  # pula cabeçalho
    return sum(1 for v in valores_g if str(v).strip() != "")


def backup_etapa1(sh, ws, total_linhas: int) -> str:
    """Copia A (ID) + G:K (valores atuais) para uma aba nova antes de limpar."""
    ids = ws.col_values(1)
    bloco_gk = ws.get_values(f"G1:K{max(total_linhas + 1, len(ids))}")
    linhas = max(len(ids), len(bloco_gk))
    ids += [""] * (linhas - len(ids))
    bloco_gk += [[""] * 5] * (linhas - len(bloco_gk))

    agora = datetime.now(FUSO_BAHIA).strftime("%Y%m%d_%H%M%S")
    nome_aba = f"BACKUP_ETAPA1_{agora}"
    cabecalho = ["ID", "G_Classificacao_IA", "H_Avaliacao", "I_Executor", "J_Criticidade", "K_Comparacao"]
    aba_backup = sh.add_worksheet(title=nome_aba, rows=linhas + 1, cols=len(cabecalho))
    linhas_saida = [cabecalho]
    for i in range(linhas):
        linha_gk = bloco_gk[i] if i < len(bloco_gk) else [""] * 5
        linha_gk = linha_gk + [""] * (5 - len(linha_gk))
        linhas_saida.append([ids[i], *linha_gk[:5]])
    aba_backup.update(values=linhas_saida, range_name="A1")
    return nome_aba


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--aplicar", action="store_true", help="Executa a limpeza. Sem isso, dry-run (só leitura).")
    p.add_argument("--confirmar", default="", help=f"Digite {PALAVRA_CONFIRMACAO} para confirmar.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    with args.config.open(encoding="utf-8") as f:
        config = json.load(f)
    aba = config["aba_principal"]

    import planilha as pl  # noqa: PLC0415

    try:
        sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
        ws = sh.worksheet(aba)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001
        print(f"Falha ao acessar a planilha: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    total_linhas = contar_linhas_preenchidas(ws)
    print(f"planilha={aba}")
    print(f"linhas com G (Classificacao IA) preenchido, que seriam limpas: {total_linhas}")
    print("escopo da limpeza: G2:K (Classificacao IA, Avaliacao, Executor, Criticidade, Comparacao)")
    print("colunas preservadas: L (formula, recalcula sozinha), M, N, O, P, Q e todas as abas de log")

    if not args.aplicar:
        print("modo=dry-run (nada apagado). Para aplicar: --aplicar --confirmar " + PALAVRA_CONFIRMACAO)
        return 0

    if args.confirmar != PALAVRA_CONFIRMACAO:
        print(f"ABORTADO: confirmação inválida. Passe --confirmar {PALAVRA_CONFIRMACAO}.", file=sys.stderr)
        return 2

    nome_backup = backup_etapa1(sh, ws, total_linhas)
    print(f"backup criado: {nome_backup} (coluna A + G:K, antes da limpeza)")

    ws.batch_clear([f"G2:K{ws.row_count}"])
    print(f"limpo: {aba}!G2:K{ws.row_count}")
    print("REMATERIALIZACAO concluida -- proximas execucoes do workflow etapa1_turnos vao reclassificar tudo como pendente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
