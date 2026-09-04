#!/usr/bin/env python3
"""Detecta e corrige linhas cuja Classificação IA (G) ficou órfã por deslocamento do IMPORTRANGE.

Contexto: as colunas A:D vêm de IMPORTRANGE puro (sem SORT/FILTER); se a fonte
insere um chamado no MEIO da tabela (não só no final), as linhas abaixo
deslocam. O gate de escrita (`executar_etapa1.validar_ids_antes_escrita`, PR
#254, 30/08/2026) só protege o INSTANTE da escrita: uma linha já classificada,
cujo G não precisa ser reescrito, nunca passa pelo gate de novo e fica presa
com a IA de outro chamado até alguém notar -- foi o que aconteceu a partir da
linha 13304 em 09/2026 (concordância C==G caiu de 91,9% para 63,3% em silêncio,
sem nenhum erro em nenhum workflow).

Este script fecha essa lacuna: compara o id_chamado ATUAL da coluna A com o
id_chamado que estava registrado quando aquela linha foi classificada pela
última vez (SNAPSHOT_ETAPA_1, que já grava linha_planilha + id_chamado a cada
turno -- não precisa de coluna nova nem de aba nova). Divergência = G órfã:
limpa SOMENTE G:K dessa linha (nunca a linha inteira, nunca M/N/O/P/Q), ela
volta a "pendente" e o próximo turno de `etapa1_turnos.yml` (já protegido pelo
gate) reclassifica certo.

Protege linhas com CONFERÊNCIA GLPI (M) = TRUE: nunca limpa o que já foi
validado por humano, mesmo que o id tenha divergido -- só registra no
relatório, para decisão manual.

SEGURANÇA:
    - Sem --aplicar: dry-run, só relata quantas linhas estão órfãs.
    - Com --aplicar: limpa G:K das linhas órfãs. Sem palavra de confirmação
      extra (diferente de `rematerializar_etapa1_oficial.py`): é uma limpeza
      cirúrgica e reversível -- a linha volta a pendente e é reclassificada
      no próximo turno, em vez de apagar a base inteira.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
RELATORIO_PADRAO = RAIZ / "dados" / "auditoria_alinhamento_ultima.json"

COL_A_ID = 1
COL_G = 7
COL_M_CONFERENCIA = 13
TAMANHO_LOTE_CLEAR = 100  # ranges por chamada de batch_clear


def normalizar_id(valor: Any) -> str:
    """Normaliza IDs vindos do Sheets sem alterar o identificador lógico."""
    bruto = str(valor or "").strip()
    if not bruto:
        return ""
    try:
        return str(int(float(bruto)))
    except (TypeError, ValueError):
        return bruto


def eh_verdadeiro(valor: Any) -> bool:
    return str(valor or "").strip().upper() in {"TRUE", "VERDADEIRO", "SIM"}


def ultima_classificacao_por_linha(sh, aba_snapshot: str) -> dict[int, str]:
    """Lê SNAPSHOT_ETAPA_1 e devolve {linha_planilha: id_chamado} da última vez
    que cada linha foi classificada. A aba é append-only e cronológica: a
    última ocorrência de cada linha_planilha no arquivo é a mais recente."""
    ws = sh.worksheet(aba_snapshot)
    vals = ws.get_values("A:C", value_render_option="UNFORMATTED_VALUE")
    # SNAPSHOT cols: 0 run_id, 1 linha_planilha, 2 id_chamado
    ultimo: dict[int, str] = {}
    for r in vals[1:]:
        if len(r) < 3:
            continue
        try:
            linha = int(r[1])
        except (TypeError, ValueError):
            continue
        ultimo[linha] = normalizar_id(r[2])
    return ultimo


def encontrar_orfas(
    ws, ultimo_id_por_linha: dict[int, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Lê A:M em UM bloco e compara id atual x id esperado por linha.

    Retorna (orfas, protegidas_conferencia).
    """
    if not ultimo_id_por_linha:
        return [], []
    linha_min, linha_max = min(ultimo_id_por_linha), max(ultimo_id_por_linha)
    bloco = pl.ler_valores(ws, f"A{linha_min}:M{linha_max}")

    def cel(linha_num: int, col1based: int) -> Any:
        off = linha_num - linha_min
        idx = col1based - 1
        row = bloco[off] if off < len(bloco) else []
        return row[idx] if idx < len(row) else ""

    orfas: list[dict[str, Any]] = []
    protegidas: list[dict[str, Any]] = []
    for linha, id_esperado in sorted(ultimo_id_por_linha.items()):
        if not id_esperado:
            continue
        g_atual = str(cel(linha, COL_G) or "").strip()
        if not g_atual:
            continue  # já pendente, nada a auditar
        id_atual = normalizar_id(cel(linha, COL_A_ID))
        if id_atual == id_esperado:
            continue  # alinhada
        registro = {"linha": linha, "id_esperado": id_esperado, "id_atual": id_atual,
                    "categoria_ia_atual": g_atual}
        if eh_verdadeiro(cel(linha, COL_M_CONFERENCIA)):
            protegidas.append(registro)
        else:
            orfas.append(registro)
    return orfas, protegidas


def limpar_orfas(ws, orfas: list[dict[str, Any]]) -> None:
    ranges = [f"G{r['linha']}:K{r['linha']}" for r in orfas]
    for i in range(0, len(ranges), TAMANHO_LOTE_CLEAR):
        ws.batch_clear(ranges[i:i + TAMANHO_LOTE_CLEAR])


def gravar_relatorio(caminho: Path, dados: Any) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
        f.write("\n")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--relatorio", type=Path, default=RELATORIO_PADRAO)
    p.add_argument("--aplicar", action="store_true",
                    help="Limpa G:K das linhas orfas. Sem isso, dry-run (so relata).")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    with args.config.open(encoding="utf-8") as f:
        config = json.load(f)
    aba = config["aba_principal"]
    aba_snapshot = config["abas_experimento"]["snapshot_etapa_1"]

    try:
        sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
        ws = sh.worksheet(aba)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001
        print(f"Falha ao acessar a planilha: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    ultimo_id_por_linha = ultima_classificacao_por_linha(sh, aba_snapshot)
    print(f"aba={aba} | snapshot={aba_snapshot}")
    print(f"linhas com classificacao registrada no snapshot: {len(ultimo_id_por_linha)}")

    if not ultimo_id_por_linha:
        print("SNAPSHOT_ETAPA_1 vazio ou inacessivel; nada para auditar.")
        return 0

    orfas, protegidas = encontrar_orfas(ws, ultimo_id_por_linha)
    print(f"linhas orfas (G nao pertence mais a este id_chamado): {len(orfas)}")
    print(f"linhas orfas mas protegidas por CONFERENCIA GLPI=TRUE (nao tocadas): {len(protegidas)}")
    for reg in orfas[:20]:
        print(f"  linha {reg['linha']}: esperado={reg['id_esperado']} atual={reg['id_atual']} "
              f"G_atual={reg['categoria_ia_atual']!r}")

    gerado = agora_bahia()
    relatorio = {
        "gerado_em": gerado,
        "linhas_com_snapshot": len(ultimo_id_por_linha),
        "linhas_orfas": len(orfas),
        "linhas_protegidas_conferencia": len(protegidas),
        "amostra_orfas": orfas[:50],
        "amostra_protegidas_conferencia": protegidas[:20],
        "aplicado": False,
    }

    if not args.aplicar:
        print("modo=dry-run (nada limpo).")
        gravar_relatorio(args.relatorio, relatorio)
        return 0

    if orfas:
        limpar_orfas(ws, orfas)
        print(f"limpo: G:K de {len(orfas)} linha(s) orfa(s) -- voltam a pendentes no proximo turno.")

    relatorio["aplicado"] = True
    gravar_relatorio(args.relatorio, relatorio)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
