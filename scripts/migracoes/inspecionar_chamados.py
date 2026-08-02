#!/usr/bin/env python3
"""Inspeciona chamados especificos por id_chamado. READ-ONLY.

Serve para diagnosticar "deu erro nesses chamados" sem adivinhar: mostra,
para cada id pedido, o que existe em cada coluna da aba principal, incluindo
valores de erro do Sheets (#N/D, #REF!, #VALOR!) que passariam despercebidos
numa leitura comum.

Le com FORMATTED_VALUE justamente porque e assim que os erros de formula
aparecem como texto. Uma leitura UNFORMATTED devolveria o valor subjacente e
esconderia o sintoma.

PRIVACIDADE: as colunas de texto livre (titulo e descricoes) sao reportadas
apenas como preenchida ou vazia, com o tamanho em caracteres. O conteudo nao
e impresso, para nao vazar texto de chamado em log publico de Actions.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import planilha as pl  # noqa: E402

# Colunas cujo conteudo NAO pode ser impresso; so presenca e tamanho.
COLUNAS_TEXTO_LIVRE = {"TÍTULO", "DESCRIÇÃO GLPI", "TÍTULO O.S.M.",
                       "DESCRIÇÃO O.S.M."}

# Valores de erro do Google Sheets, em pt-BR e en-US.
ERROS_SHEETS = ("#N/D", "#N/A", "#REF!", "#VALOR!", "#VALUE!", "#NOME?",
                "#NAME?", "#DIV/0!", "#NÚM!", "#NUM!", "#NULO!", "#NULL!",
                "#ERRO!", "#ERROR!")


def eh_erro(valor: str) -> bool:
    return str(valor or "").strip().upper() in {e.upper() for e in ERROS_SHEETS}


def normalizar_id(valor: Any) -> str:
    s = str(valor or "").strip()
    if not s:
        return ""
    try:
        return str(int(float(s)))
    except (TypeError, ValueError):
        return s


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path,
                   default=Path(__file__).resolve().parents[2] / "config_experimento.json")
    p.add_argument("--credenciais", default=None)
    p.add_argument("--ids", required=True,
                   help="Ids separados por virgula ou espaco.")
    return p.parse_args()


def main() -> int:
    import json
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    pedidos = [normalizar_id(x) for x in args.ids.replace(",", " ").split() if x.strip()]
    if not pedidos:
        raise SystemExit("nenhum id informado")

    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    ws = sh.worksheet(config["aba_principal"])
    bloco = ws.get_values("A:Q", value_render_option="FORMATTED_VALUE")
    cab = bloco[0] if bloco else []

    por_id: dict[str, tuple[int, list[str]]] = {}
    for pos, linha in enumerate(bloco[1:], start=2):
        i = normalizar_id(linha[0] if linha else "")
        if i:
            por_id[i] = (pos, linha)

    print(f"aba={config['aba_principal']} | linhas lidas={len(bloco) - 1} "
          f"| ids pedidos={len(pedidos)}")
    achados = sum(1 for i in pedidos if i in por_id)
    print(f"encontrados={achados} | ausentes={len(pedidos) - achados}\n")

    total_erros = 0
    for pid in pedidos:
        if pid not in por_id:
            print(f"--- {pid}: AUSENTE da aba principal")
            continue
        pos, linha = por_id[pid]
        print(f"--- {pid}  (linha {pos})")
        for idx, nome in enumerate(cab):
            valor = linha[idx] if idx < len(linha) else ""
            letra = pl._coluna_letra(idx + 1)  # noqa: SLF001
            s = str(valor or "").strip()
            if eh_erro(s):
                total_erros += 1
                print(f"      {letra} {nome:<28} >>> ERRO: {s}")
            elif nome in COLUNAS_TEXTO_LIVRE:
                estado = f"preenchida ({len(s)} car.)" if s else "VAZIA"
                print(f"      {letra} {nome:<28} {estado}")
            else:
                print(f"      {letra} {nome:<28} {s!r}" if s
                      else f"      {letra} {nome:<28} VAZIA")
    print(f"\ncelulas com valor de erro do Sheets: {total_erros}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
