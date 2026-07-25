#!/usr/bin/env python3
"""Quantifica o vies estrutural da amostra validada e publica um intervalo
de sensibilidade [limite inferior, limite superior] para o acerto validado
de cada modelo, em vez de um numero pontual.

MECANISMO DO VIES (achado do Adinailson, 2026-07-25): a "verdade validada"
usada em avaliacao_final.py (dv.verdade_validada) so existe quando alguma
conferencia humana marca 'Correto' (M=Correto -> historico; N=Correto -> IA;
P=Correto -> reclassificacao). Chamados em que o avaliador julgou que TODAS
as fontes conferidas erraram (nenhum 'Correto', pelo menos um 'Errado')
ficam com status='restrito' e sao EXCLUIDOS do denominador de qualquer
metrica de acerto validado. Isso torna a amostra validada, por construcao,
um subconjunto onde pelo menos uma fonte (historico OU IA) estava certa —
inflando mecanicamente o acerto validado de qualquer modelo que tenda a
concordar com o historico ou com a IA oficial. Evidencia direta: a matriz
de confusao IA-vs-GLPI na amostra validada nunca tem a celula
"IA certa, GLPI errado" vazia por acaso — e um artefato da propria selecao.

Este script NAO resolve o vies (isso exigiria redesenhar a amostragem da
conferencia humana, fora de escopo aqui) — apenas o TORNA VISIVEL, com dois
limites:
- limite_superior: acerto validado atual (so decididos; igual a
  avaliacao_final.json::por_modelo[].acerto_validado).
- limite_inferior: acerto se os 'restritos' fossem TODOS contados como erro
  de TODOS os modelos (pior caso — nao sabemos a categoria certa desses
  casos, entao nenhum modelo pode ganhar credito neles).

O numero real esta em algum ponto do intervalo [limite_inferior,
limite_superior]; nao e possivel apontar um valor exato sem uma verdade
adicional para os 'restritos' (o que exigiria nova rodada de conferencia
humana especificamente sobre eles).

Read-only na planilha. Saida: 04_artigo/figuras/sensibilidade_vies_validacao.json
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import planilha as pl  # noqa: E402
import decisao_validada as dv  # noqa: E402
import avaliacao_final as af  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
SAIDA = RAIZ / "04_artigo" / "figuras" / "sensibilidade_vies_validacao.json"


def carregar_decisoes_com_veredito(sh, aba_principal: str) -> dict[int, dict[str, Any]]:
    """Como dv.carregar_decisoes, mas preserva v_glpi/v_ia/v_reclass por linha
    (para poder caracterizar a COMPOSICAO dos 'restritos' — qual conferencia
    marcou Errado). Le a planilha 1 vez, independente de carregar_decisoes."""
    ws = sh.worksheet(aba_principal)
    bloco = ws.get_values("A:P", value_render_option="UNFORMATTED_VALUE")
    cab = bloco[0] if bloco else []
    col_historico = pl.localizar_coluna(cab, ("CATEGORIA COMPLETA",), 3)
    col_ia1 = pl.localizar_coluna(cab, ("Classificacao IA", "Classificação IA"), 7)
    col_reclass = pl.localizar_coluna(cab, ("Classificacao IA - 2", "Classificação IA - 2"), 15)
    col_conf_glpi = pl.localizar_coluna(cab, ("CONFERENCIA GLPI", "CONFERÊNCIA GLPI"), 13)
    col_conf_ia = pl.localizar_coluna(cab, ("CONFERENCIA IA", "CONFERÊNCIA IA"), 14)
    col_conf_reclass = pl.localizar_coluna(cab, ("CONFERENCIA IA - 2", "CONFERÊNCIA IA - 2"), 16)

    def cel(linha: list[Any], c1: int) -> str:
        i = c1 - 1
        return str(linha[i] or "").strip() if len(linha) > i else ""

    out: dict[int, dict[str, Any]] = {}
    for pos, linha in enumerate(bloco[1:], start=2):
        v_glpi = dv._norm_veredito(cel(linha, col_conf_glpi))  # noqa: SLF001
        v_ia = dv._norm_veredito(cel(linha, col_conf_ia))  # noqa: SLF001
        v_reclass = dv._norm_veredito(cel(linha, col_conf_reclass))  # noqa: SLF001
        if v_glpi is None and v_ia is None and v_reclass is None:
            continue
        decisao = dv.decidir(pl.normalizar_categoria(cel(linha, col_historico)), cel(linha, col_ia1),
                             cel(linha, col_reclass), v_glpi, v_ia, v_reclass)
        decisao["v_glpi"] = v_glpi
        decisao["v_ia"] = v_ia
        decisao["v_reclass"] = v_reclass
        out[pos] = decisao
    return out


def compor_restritos(decisoes: dict[int, dict[str, Any]]) -> dict[str, int]:
    """Composicao dos status='restrito': qual combinacao de conferencias
    contribuiu (Errado em GLPI/IA/reclassificacao, ou conflito entre
    'Corretos' apontando categorias diferentes)."""
    comp = Counter()
    for d in decisoes.values():
        if d["status"] != dv.STATUS_RESTRITO:
            continue
        if d.get("conflito"):
            comp["conflito_correto_divergente"] += 1
            continue
        errados = tuple(sorted(
            fonte for fonte, v in (("glpi", d["v_glpi"]), ("ia", d["v_ia"]), ("reclass", d["v_reclass"]))
            if v == "Errado"
        ))
        comp["errado_" + "_e_".join(errados)] += 1
    return dict(comp)


def main() -> int:
    config = json.loads(CONFIG_PADRAO.read_text(encoding="utf-8"))
    try:
        sh = pl.abrir_planilha(pl.id_planilha(config), None)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001
        print(f"Falha ao acessar planilha: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    modelos, estado_bertimbau = af.modelos_comparaveis(config)
    decisoes = carregar_decisoes_com_veredito(sh, config["aba_principal"])
    resumo = dv.resumo_decisoes(decisoes)
    composicao_restritos = compor_restritos(decisoes)

    verdade = dv.verdade_validada(decisoes)
    preds = af.carregar_predicoes(sh, config, modelos)
    if not preds:
        print("Sem predicoes materializadas (CLASSIF__<modelo>) — nada a calcular.", file=sys.stderr)
        return 1

    linhas_decididas = sorted(ln for ln in verdade if all(ln in preds[m] for m in preds))
    linhas_restritas = sorted(
        ln for ln, d in decisoes.items()
        if d["status"] == dv.STATUS_RESTRITO and all(ln in preds[m] for m in preds)
    )
    n_decididas = len(linhas_decididas)
    n_restritas = len(linhas_restritas)
    n_total = n_decididas + n_restritas

    por_modelo = []
    for m in sorted(preds):
        corretos = sum(1 for ln in linhas_decididas if preds[m][ln]["pred"] == verdade[ln])
        limite_superior = corretos / n_decididas if n_decididas else 0.0
        # Limite inferior: restritos entram no denominador, contam 0 acertos
        # para TODOS os modelos (nao sabemos a categoria certa deles).
        limite_inferior = corretos / n_total if n_total else 0.0
        por_modelo.append({
            "modelo": m,
            "corretos": corretos,
            "n_limite_superior": n_decididas,
            "n_limite_inferior": n_total,
            "limite_inferior": round(limite_inferior, 4),
            "limite_superior": round(limite_superior, 4),
            "amplitude": round(limite_superior - limite_inferior, 4),
        })
    por_modelo.sort(key=lambda d: -d["limite_superior"])

    saida = {
        "gerado_em": agora_bahia(),
        "script_origem": "src/analise_sensibilidade_vies_validacao.py",
        "natureza": (
            "sensibilidade do acerto validado ao vies estrutural de selecao da amostra: "
            "'restritos' (nenhuma fonte conferida como Correto) sao excluidos do calculo "
            "padrao (limite_superior); limite_inferior mostra o pior caso, contando-os "
            "como erro de todos os modelos"
        ),
        "mecanismo_do_vies": (
            "a verdade validada so existe quando M, N ou P marca 'Correto'. Chamados em "
            "que o avaliador julgou TODAS as fontes conferidas erradas (status='restrito') "
            "ficam fora do denominador de avaliacao_final.json, inflando mecanicamente o "
            "acerto de qualquer modelo que concorde com o historico ou a IA oficial"
        ),
        "conferencias": resumo,
        "composicao_restritos": composicao_restritos,
        "n_decididas_avaliaveis": n_decididas,
        "n_restritas_avaliaveis": n_restritas,
        "n_total_se_incluir_restritos": n_total,
        "por_modelo": por_modelo,
        "observacao": (
            "o valor real do acerto validado esta em algum ponto do intervalo "
            "[limite_inferior, limite_superior]; nao e possivel apontar um numero exato "
            "sem uma verdade adicional para os 'restritos' (exigiria nova rodada de "
            "conferencia humana especificamente sobre eles)"
        ),
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"conferencias={resumo} | composicao_restritos={composicao_restritos}")
    print(f"n_decididas_avaliaveis={n_decididas} | n_restritas_avaliaveis={n_restritas}")
    for d in por_modelo:
        print(f"  {d['modelo']}: [{d['limite_inferior']}, {d['limite_superior']}] "
              f"(amplitude {d['amplitude']})")
    print(f"OK: gravado em {SAIDA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
