#!/usr/bin/env python3
"""Trunca RECLASS_HISTORICO na planilha viva, depois de arquivar tudo em CSV.

FASE 3 do plano de redução de células (2026-09): RECLASS_HISTORICO é a maior
aba (3.059.112 células em 04/09/2026, 33% do limite de 10 milhões,
crescendo ~340 mil células/mês). É a fonte usada por
scripts/migracoes/restaurar_coluna_o.py para reconstrução forense por data de
corte (indexada por id_chamado) -- não pode ser truncada sem que o conteúdo
integral esteja preservado fora do Sheets primeiro.

Diferença deste script para `rematerializar_etapa1_oficial.py`: aquele faz
backup para uma ABA NOVA antes de limpar, o que é seguro para G:K (poucas
colunas) mas aqui só moveria o problema -- uma cópia de RECLASS_HISTORICO
custaria os mesmos ~3 milhões de células em outro lugar da planilha. Por
isso o backup aqui é um EXPORT FRESCO PARA ARQUIVO (reaproveita
scripts/migracoes/exportar_reclass_historico.exportar), feito NA HORA, logo
antes de limpar -- garante que absolutamente tudo que será removido já está
arquivado, mesmo que tenham entrado linhas novas desde o último export manual.

Preserva a linha 1 (cabeçalho): limpa A2:{última coluna}{última linha}, nunca
a aba inteira -- os escritores (`reclassificacao_multimodelo.py`,
`reclassificar_validados.py`, via `pl.append_aba`) detectam o cabeçalho
existente e continuam gravando normalmente logo abaixo dele.

SEGURANÇA:
    - Sem --aplicar: dry-run. Faz o export fresco (para já deixar o arquivo
      pronto) e relata quantas linhas/células seriam liberadas, sem tocar na
      planilha.
    - Só limpa de verdade com --aplicar E --confirmar TRUNCAR.
    - Confere, antes de limpar, o export contra uma 2ª leitura independente
      (só a coluna A, chamada separada) -- aborta sem escrever nada se as
      duas contagens não baterem (proteção contra leitura parcial silenciosa,
      já medida nesta planilha durante recálculo de IMPORTRANGE).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exportar_reclass_historico import exportar  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
SAIDA_PADRAO_DIR = RAIZ / "dados" / "arquivo_reclass_historico"
PALAVRA_CONFIRMACAO = "TRUNCAR"


def calcular_intervalo_limpeza(n_colunas: int, n_linhas_dados: int) -> str:
    """A1 da faixa de dados a limpar: A2 até a última coluna/linha (cabeçalho preservado)."""
    ultima_col = pl._coluna_letra(n_colunas)  # noqa: SLF001
    ultima_linha = n_linhas_dados + 1  # +1 pelo cabeçalho na linha 1
    return f"A2:{ultima_col}{ultima_linha}"


def confirmar_leitura_completa(ws, n_linhas_exportadas: int) -> tuple[bool, int]:
    """2ª leitura INDEPENDENTE (só a coluna A, chamada separada da API) para
    confirmar que o export capturou a aba inteira -- o mesmo tipo de leitura
    incompleta e sem sinal de erro já foi medido nesta planilha durante
    recálculo de IMPORTRANGE (ver CONTEXTO.md). Uma única leitura grande
    (get_values, usada pelo export) não teria como se autoconferir; a
    redundância entre duas chamadas independentes é o sinal.

    Retorna (bateu, linhas_de_dados_na_2a_leitura).
    """
    ids_coluna_a = ws.col_values(1)
    linhas_2a_leitura = len(ids_coluna_a) - 1  # exclui o cabecalho
    return linhas_2a_leitura == n_linhas_exportadas, linhas_2a_leitura


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--aba", default=None,
                    help="Nome da aba (padrao: multimodelo.aba_historico_reclassificacao "
                         "ou RECLASS_HISTORICO).")
    p.add_argument("--saida-dir", type=Path, default=SAIDA_PADRAO_DIR)
    p.add_argument("--aplicar", action="store_true",
                    help="Trunca de verdade. Sem isso, dry-run (so exporta e relata).")
    p.add_argument("--confirmar", default="",
                    help=f"Digite {PALAVRA_CONFIRMACAO} para confirmar o truncamento.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    with args.config.open(encoding="utf-8") as f:
        config = json.load(f)
    aba = args.aba or config.get("multimodelo", {}).get(
        "aba_historico_reclassificacao", "RECLASS_HISTORICO")

    try:
        sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
        ws = sh.worksheet(aba)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001
        print(f"Falha ao acessar a planilha: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    print(f"aba={aba} | linhas_alocadas={ws.row_count} | colunas_alocadas={ws.col_count}")
    print("fazendo export fresco antes de qualquer limpeza...")
    gerado = agora_bahia()
    manifesto = exportar(ws, aba, args.saida_dir, gerado)

    if not manifesto["arquivo_csv"]:
        print("aba vazia; nada para truncar.")
        return 0

    n_linhas = manifesto["linhas_exportadas"]
    n_colunas = len(manifesto["colunas"])
    celulas_liberadas = n_linhas * n_colunas
    caminho_csv = args.saida_dir / manifesto["arquivo_csv"]
    print(f"export concluido: {n_linhas} linhas ({n_colunas} colunas) -> {caminho_csv}")

    bateu, linhas_2a_leitura = confirmar_leitura_completa(ws, n_linhas)
    if not bateu:
        print(
            f"ABORTADO: leitura divergente entre o export ({n_linhas} linhas) e uma "
            f"2a leitura independente da coluna A ({linhas_2a_leitura} linhas). "
            f"Nao trunca sem as duas leituras baterem.",
            file=sys.stderr,
        )
        return 2

    faixa = calcular_intervalo_limpeza(n_colunas, n_linhas)
    print(f"faixa a limpar (cabecalho preservado): {faixa}")
    print(f"celulas a liberar: {celulas_liberadas:,}")

    if not args.aplicar:
        print("modo=dry-run (nada limpo). Para aplicar: --aplicar --confirmar " + PALAVRA_CONFIRMACAO)
        return 0

    if args.confirmar != PALAVRA_CONFIRMACAO:
        print(f"ABORTADO: confirmacao invalida. Passe --confirmar {PALAVRA_CONFIRMACAO}.", file=sys.stderr)
        return 2

    ws.batch_clear([faixa])
    print(f"TRUNCADO: {aba}!{faixa} ({n_linhas} linhas, {celulas_liberadas:,} celulas liberadas).")
    print(f"Historico completo preservado em {caminho_csv} (baixe e arquive permanentemente -- "
          f"o artifact do GitHub Actions expira).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
