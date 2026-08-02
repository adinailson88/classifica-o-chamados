#!/usr/bin/env python3
"""Distribuicao das categorias EFETIVAMENTE utilizadas na coluna C (historico).

MOTIVACAO (2026-08-01): o artigo afirma 55 categorias historicas, numero que
deixou de fechar depois da redefinicao da fonte do IMPORTRANGE (28/07), da
mesclagem de categorias feita direto no GLPI e das correcoes manuais. Sem uma
contagem apurada da coluna C nao e possivel corrigir nem o corpo do artigo nem
a Tabela A1 do Apendice A.

DUAS NATUREZAS DE CATEGORIA (esclarecido pelo pesquisador):
  - FOLHA: contem '>' e nomeia um servico real ("Eletrica > Iluminacao").
  - RAIZ: sem '>', existe apenas porque o GLPI exige que a categoria-pai exista
    para que as filhas com '>' possam ser criadas ("Projetos e Reformas").
    Nao sao categorias de trabalho. Quando aparecem em C, indicam chamado
    classificado no nivel errado da hierarquia, nao uma classe legitima.

O script conta as duas separadamente. O numero que o artigo deve reportar como
"categorias historicas" e o de FOLHAS efetivamente utilizadas, e as raizes que
ainda carregam chamados precisam ser visiveis para o pesquisador decidir o que
fazer com elas.

READ-ONLY: le a aba principal e nao grava celula nenhuma. Nenhum texto de
chamado entra no JSON, apenas nomes de categoria e contagens.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
SAIDA_PADRAO = RAIZ / "docs" / "dados" / "distribuicao_categorias.json"

SEPARADOR = ">"


def eh_folha(categoria: str) -> bool:
    """Categoria de trabalho tem pai e filho separados por '>'."""
    return SEPARADOR in categoria


def raiz_de(categoria: str) -> str:
    """'Eletrica > Iluminacao' -> 'Eletrica'. Sem '>', devolve a propria."""
    return categoria.split(SEPARADOR)[0].strip()


def resumir(contagem: Counter[str]) -> dict[str, Any]:
    """Separa folhas de raizes e devolve o resumo. Logica pura, testavel."""
    folhas = {c: n for c, n in contagem.items() if eh_folha(c)}
    raizes = {c: n for c, n in contagem.items() if not eh_folha(c)}

    def ordenar(d: dict[str, int]) -> list[dict[str, Any]]:
        return [{"categoria": c, "n": n}
                for c, n in sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))]

    total = sum(contagem.values())
    n_folhas = sum(folhas.values())
    n_raizes = sum(raizes.values())

    # Familias: agrupa as folhas pelo primeiro nivel, para o apendice poder
    # ser lido por bloco tematico em vez de uma lista corrida de dezenas.
    familias: Counter[str] = Counter()
    for c, n in folhas.items():
        familias[raiz_de(c)] += n

    return {
        "total_chamados": total,
        "categorias_distintas": len(contagem),
        "folhas_distintas": len(folhas),
        "raizes_distintas": len(raizes),
        "chamados_em_folhas": n_folhas,
        "chamados_em_raizes": n_raizes,
        "percentual_em_raizes": round(100 * n_raizes / total, 2) if total else 0.0,
        "familias_distintas": len(familias),
        "folhas": ordenar(folhas),
        "raizes": ordenar(raizes),
        "familias": [{"familia": f, "n": n}
                     for f, n in sorted(familias.items(), key=lambda kv: (-kv[1], kv[0]))],
    }


def ler_categorias(sh, config: dict) -> Counter[str]:
    ws = sh.worksheet(config["aba_principal"])
    valores = pl.ler_valores(ws, config["range_leitura"])
    cab = valores[0] if valores else []
    norm = lambda s: " ".join(str(s or "").split()).casefold()  # noqa: E731
    idx = {norm(n): i for i, n in enumerate(cab)}
    i_cat = idx.get(norm("CATEGORIA COMPLETA"))
    i_id = idx.get(norm("ID Chamado"))
    if i_cat is None:
        raise SystemExit("coluna 'CATEGORIA COMPLETA' nao encontrada no cabecalho")
    if i_id is None:
        raise SystemExit("coluna 'ID Chamado' nao encontrada no cabecalho")

    # Exige id_chamado, como as demais ferramentas. Sem isso, uma linha com
    # categoria e sem id entra aqui e nao entra no corpus, e a distribuicao
    # fecha em 14.059 para uma base de 14.058 (apurado em 02/08/2026).
    contagem: Counter[str] = Counter()
    sem_id = 0
    for linha in valores[1:]:
        id_chamado = str(linha[i_id] or "").strip() if len(linha) > i_id else ""
        bruto = str(linha[i_cat] or "").strip() if len(linha) > i_cat else ""
        cat = pl.normalizar_categoria(bruto)
        if cat and not id_chamado:
            sem_id += 1
            continue
        if cat:
            contagem[cat] += 1
    if sem_id:
        print(f"[aviso] {sem_id} linha(s) com categoria e SEM id_chamado, "
              "descartada(s) da distribuicao")
    return contagem


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--json", type=Path, default=SAIDA_PADRAO)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    contagem = ler_categorias(sh, config)
    resumo = resumir(contagem)
    resumo["gerado_em"] = agora_bahia()
    resumo["script_origem"] = "src/distribuicao_categorias.py"
    resumo["fonte"] = "coluna C (CATEGORIA COMPLETA) da aba principal"
    resumo["criterio"] = (
        "folha = categoria com '>' (servico real); raiz = categoria sem '>', "
        "existente apenas para sustentar a hierarquia do GLPI")

    print("=== DISTRIBUICAO DA COLUNA C ===")
    print(f"  chamados com categoria      : {resumo['total_chamados']}")
    print(f"  categorias distintas        : {resumo['categorias_distintas']}")
    print(f"  folhas (com '>')            : {resumo['folhas_distintas']}")
    print(f"  raizes (sem '>')            : {resumo['raizes_distintas']}")
    print(f"  chamados em folhas          : {resumo['chamados_em_folhas']}")
    print(f"  chamados em raizes          : {resumo['chamados_em_raizes']} "
          f"({resumo['percentual_em_raizes']}%)")
    print(f"  familias de primeiro nivel  : {resumo['familias_distintas']}")

    if resumo["raizes"]:
        print("\n  RAIZES COM CHAMADOS (classificacao no nivel errado):")
        for r in resumo["raizes"]:
            print(f"    {r['n']:>6}  {r['categoria']}")

    print(f"\n  FOLHAS ({resumo['folhas_distintas']}):")
    for f in resumo["folhas"]:
        print(f"    {f['n']:>6}  {f['categoria']}")

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(resumo, ensure_ascii=False, indent=1),
                         encoding="utf-8")
    print(f"\nescrito em {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
