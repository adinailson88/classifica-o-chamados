#!/usr/bin/env python3
"""Auditoria READ-ONLY das abas da planilha: o que e usado, o que e lixo, e
quanto cada aba custa em celulas.

MOTIVO (2026-08-01): a planilha bateu no teto de 10.000.000 de celulas do Google
Sheets e nao aceita mais criar aba nenhuma (a criacao da CONFERENCIA_MULTIMODELO
falhou com "This action would increase the number of cells in the workbook above
the limit"). Antes de apagar qualquer coisa, e preciso saber o que ainda e
consumido pelo pipeline e pelo painel.

Para cada aba reporta:
  - celulas ALOCADAS (row_count x col_count) -- e isso que conta para o limite;
  - celulas USADAS (ultima linha/coluna com conteudo);
  - DESPERDICIO (alocadas - usadas), recuperavel so redimensionando a grade,
    sem apagar dado nenhum;
  - CLASSIFICACAO: de onde a aba e referenciada.

CLASSIFICACAO:
  config      -> declarada em config_experimento.json (o pipeline le/escreve)
  codigo      -> nome fixo em src/ ou scripts/ (ver REFERENCIADAS_NO_CODIGO)
  derivada    -> CLASSIF__<modelo> / RECLASS__<modelo> dos modelos configurados
  ORFA        -> ninguem referencia; candidata a remocao

NAO APAGA NADA. Apenas relata e ordena por custo.
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

LIMITE_CELULAS = 10_000_000

# Abas com nome fixo citadas em src/ ou scripts/, que NAO estao em
# config_experimento.json. Levantado por grep; manter em sincronia.
REFERENCIADAS_NO_CODIGO = {
    "AUDITORIA_CONFERENCIAS": "src/auditar_conferencias.py",
    "AUDITORIA_CLASSIFICACAO_2": "src/classificacao_ia_2_comite.py",
    "CALIBRACAO_VALIDADA": "src/calibracao.py",
    "CANDIDATOS_CLASSIFICACAO_2": "src/classificacao_ia_2_comite.py",
    "CLASSIFICACAO_2_DRYRUN": "src/classificacao_ia_2_comite.py",
    "COMITE_CLASSIFICACAO_2": "src/classificacao_ia_2_comite.py",
    "CONFERENCIA_MULTIMODELO": "src/conferencia_derivada.py",
    "CONTROLE_CLASSIFICACAO_2": "src/classificacao_ia_2_comite.py",
    "CORRELACAO_CATEGORIAS": "src/relevancia_termos.py",
    "CRUZAMENTO_TAXONOMIA": "src/cruzamento_taxonomia.py",
    "MEMORIA_VALIDADA_CLASSIFICACAO": "src/memoria_validada.py",
    "METRICAS_CLASSIFICACAO_2": "src/classificacao_ia_2_comite.py",
    "RECLASS_TURNOS": "src/reclassificacao_multimodelo.py",
    "RECLASS_VALIDADOS": "src/reclassificar_validados.py",
    "RELEVANCIA_TERMOS": "src/relevancia_termos.py",
    "VALIDACAO_NAO_SUPERVISIONADA": "src/validacao_nao_supervisionada.py",
    "MULTIMODELO_RECLASS_TURNOS": "src/reclassificacao_multimodelo.py",
    "VALIDACAO_HUMANA": "src/consolidar_validacao.py",
}

PREFIXOS_DESCARTAVEIS = ("BACKUP_", "TEMP_", "TESTE_", "COPIA_", "TMP_", "Copy of ",
                         "Cópia de ")


def abas_do_config(config: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    for chave, nome in (config.get("abas_experimento") or {}).items():
        out[nome] = f"config.abas_experimento.{chave}"
    out[config["aba_principal"]] = "config.aba_principal"
    mm = config.get("multimodelo") or {}
    for chave in ("aba_historico_reclassificacao", "aba_turnos", "aba_metricas"):
        if mm.get(chave):
            out[mm[chave]] = f"config.multimodelo.{chave}"
    return out


def abas_derivadas(config: dict) -> dict[str, str]:
    mm = config.get("multimodelo") or {}
    modelos = list(mm.get("modelos_leves", [])) + list(mm.get("modelos_pesados", []))
    out: dict[str, str] = {}
    for chave in ("aba_classificacao", "aba_reclassificacao"):
        template = mm.get(chave)
        if not template:
            continue
        for m in modelos:
            out[template.replace("{modelo}", m)] = f"config.multimodelo.{chave}"
    return out


def classificar(nome: str, do_config: dict, derivadas: dict) -> tuple[str, str]:
    if nome in do_config:
        return "config", do_config[nome]
    if nome in derivadas:
        return "derivada", derivadas[nome]
    if nome in REFERENCIADAS_NO_CODIGO:
        return "codigo", REFERENCIADAS_NO_CODIGO[nome]
    for p in PREFIXOS_DESCARTAVEIS:
        if nome.startswith(p):
            return "ORFA", f"prefixo descartavel '{p}'"
    return "ORFA", "nenhuma referencia encontrada"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    args = p.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    do_config = abas_do_config(config)
    derivadas = abas_derivadas(config)

    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    abas = sh.worksheets()
    print(f"abas na planilha: {len(abas)}")

    dados = []
    for ws in abas:
        alocadas = int(ws.row_count) * int(ws.col_count)
        try:
            valores = ws.get_values(value_render_option="UNFORMATTED_VALUE")
            usadas_linhas = len(valores)
            usadas_cols = max((len(r) for r in valores), default=0)
        except Exception:  # noqa: BLE001
            usadas_linhas = usadas_cols = 0
        usadas = usadas_linhas * usadas_cols
        classe, origem = classificar(ws.title, do_config, derivadas)
        dados.append({
            "nome": ws.title, "linhas": ws.row_count, "colunas": ws.col_count,
            "alocadas": alocadas, "usadas_linhas": usadas_linhas,
            "usadas": usadas, "desperdicio": max(0, alocadas - usadas),
            "classe": classe, "origem": origem,
        })

    total_aloc = sum(d["alocadas"] for d in dados)
    total_usadas = sum(d["usadas"] for d in dados)
    total_desp = sum(d["desperdicio"] for d in dados)

    print(f"\n=== TOTAL ===")
    print(f"  celulas ALOCADAS : {total_aloc:>12,}  ({100.0*total_aloc/LIMITE_CELULAS:.1f}% do limite de {LIMITE_CELULAS:,})")
    print(f"  celulas USADAS   : {total_usadas:>12,}")
    print(f"  DESPERDICIO      : {total_desp:>12,}  (recuperavel so redimensionando, sem apagar dado)")

    print(f"\n=== ABAS POR CUSTO (alocadas) ===")
    print(f"{'aba':<40}{'classe':<10}{'alocadas':>12}{'usadas':>12}{'desperdicio':>13}")
    for d in sorted(dados, key=lambda x: -x["alocadas"]):
        print(f"{d['nome'][:39]:<40}{d['classe']:<10}{d['alocadas']:>12,}"
              f"{d['usadas']:>12,}{d['desperdicio']:>13,}")

    orfas = [d for d in dados if d["classe"] == "ORFA"]
    print(f"\n=== ORFAS ({len(orfas)}) — candidatas a remocao ===")
    if not orfas:
        print("  nenhuma")
    for d in sorted(orfas, key=lambda x: -x["alocadas"]):
        print(f"  {d['nome']:<44} alocadas={d['alocadas']:>10,}  "
              f"linhas_usadas={d['usadas_linhas']:>7}  [{d['origem']}]")
    print(f"\n  ganho se todas as orfas forem removidas: "
          f"{sum(d['alocadas'] for d in orfas):,} celulas")

    print("\nNada foi apagado nem alterado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
