#!/usr/bin/env python3
"""Compara modelo puro e camada hibrida de regras preventivas.

Ferramenta estritamente READ-ONLY. Reaproveita as predicoes *out-of-fold* do
Passo 4 e aplica a camada explicita de `regras_preventivas.py` sobre os mesmos
registros e as mesmas particoes, conforme o Passo 5 de
PLANO_EXECUCAO_ATUAL.md.

O ponto do passo e medir, e nao presumir, o valor das regras de dominio. Por
isso as duas configuracoes compartilham denominador: todo numero comparado
vem exatamente do mesmo conjunto de registros, e a referencia humana nunca e
alterada.

As saidas sao sanitizadas: nao publicam titulos, descricoes nem IDs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import construir_grupos_textuais as cgt  # noqa: E402
import planilha as pl  # noqa: E402
import regras_preventivas as rp  # noqa: E402
import retreinar_modelos_canonicos as rmc  # noqa: E402
import tipo_manutencao as tm  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
PREDICOES_PADRAO = RAIZ / "docs" / "dados" / "retreino_canonico_predicoes.csv"
SAIDA_JSON_PADRAO = RAIZ / "docs" / "dados" / "regras_versus_modelos.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "REGRAS_VERSUS_MODELOS.md"


def carregar_predicoes(caminho: Path) -> dict[str, Any]:
    """Le o CSV do Passo 4 e agrupa por modelo, preservando a referencia."""
    referencia: dict[str, str] = {}
    dobra: dict[str, int] = {}
    por_modelo: dict[str, dict[str, str]] = defaultdict(dict)
    with caminho.open("r", encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            chave = linha["id_sha256"]
            referencia[chave] = linha["referencia_humana"]
            dobra[chave] = int(linha["dobra"])
            por_modelo[linha["modelo"]][chave] = linha["previsto"]
    return {"referencia": referencia, "dobra": dobra,
            "por_modelo": dict(por_modelo)}


def carregar_textos(sh, config: dict[str, Any],
                    chaves: set[str]) -> dict[str, str]:
    """Texto dos registros avaliados, indexado pelo SHA-256 do ID."""
    textos: dict[str, str] = {}
    for r in cgt.ler_registros(sh, config):
        id_chamado = r.get("id", "")
        if not id_chamado:
            continue
        chave = hashlib.sha256(id_chamado.encode("utf-8")).hexdigest()
        if chave in chaves:
            textos[chave] = rmc.montar_texto(r)
    return textos


def _metricas(verdade: list[str], predito: list[str],
              categorias: list[str]) -> dict[str, float]:
    from sklearn.metrics import balanced_accuracy_score, f1_score
    if not verdade:
        return {"n": 0, "acuracia": 0.0, "macro_f1": 0.0, "balanced_accuracy": 0.0}
    certos = sum(1 for a, b in zip(verdade, predito) if a == b)
    return {
        "n": len(verdade),
        "acuracia": round(certos / len(verdade), 4),
        "macro_f1": round(float(f1_score(verdade, predito, labels=categorias,
                                         average="macro", zero_division=0)), 4),
        "balanced_accuracy": round(float(balanced_accuracy_score(verdade, predito)), 4),
    }


def comparar(chaves: list[str], referencia: dict[str, str],
             textos: dict[str, str], predicoes: dict[str, str],
             categorias_permitidas: set[str]) -> dict[str, Any]:
    """Mede modelo puro e hibrido nos mesmos registros.

    O hibrido substitui a predicao do modelo somente onde a regra dispara. Onde
    a regra se abstem, as duas configuracoes sao identicas por construcao, e e
    justamente por isso que o denominador se mantem igual.
    """
    categorias = sorted({referencia[c] for c in chaves})
    verdade = [referencia[c] for c in chaves]
    puro = [predicoes.get(c, "") for c in chaves]

    hibrido: list[str] = []
    disparos = 0
    conflitos: list[dict[str, str]] = []
    for chave, previsto_modelo in zip(chaves, puro):
        resultado = rp.aplicar(textos.get(chave, ""), categorias_permitidas)
        proposta = resultado["categoria"]
        if not proposta:
            hibrido.append(previsto_modelo)
            continue
        disparos += 1
        hibrido.append(str(proposta))
        if proposta != previsto_modelo:
            conflitos.append({
                "referencia": referencia[chave],
                "modelo": previsto_modelo,
                "regra": str(proposta),
            })

    # Quem acerta quando regra e modelo divergem. E a unica leitura que
    # justifica manter ou descartar a camada explicita.
    regra_certa = sum(1 for c in conflitos if c["regra"] == c["referencia"])
    modelo_certo = sum(1 for c in conflitos if c["modelo"] == c["referencia"])
    ambos_errados = len(conflitos) - regra_certa - modelo_certo

    # Recorte dos chamados cuja referencia e preventiva, onde a camada deveria
    # concentrar todo o seu efeito.
    idx_prev = [i for i, chave in enumerate(chaves)
                if tm.tipo_manutencao(referencia[chave]) == tm.PREVENTIVA]
    m_puro = _metricas(verdade, puro, categorias)
    m_hibrido = _metricas(verdade, hibrido, categorias)
    p_puro = _metricas([verdade[i] for i in idx_prev],
                       [puro[i] for i in idx_prev], categorias)
    p_hibrido = _metricas([verdade[i] for i in idx_prev],
                          [hibrido[i] for i in idx_prev], categorias)

    return {
        "global": {"modelo_puro": m_puro, "hibrido": m_hibrido,
                   "delta_acuracia": round(m_hibrido["acuracia"] - m_puro["acuracia"], 4),
                   "delta_macro_f1": round(m_hibrido["macro_f1"] - m_puro["macro_f1"], 4)},
        "preventivos": {"modelo_puro": p_puro, "hibrido": p_hibrido,
                        "delta_acuracia": round(p_hibrido["acuracia"] - p_puro["acuracia"], 4),
                        "delta_macro_f1": round(p_hibrido["macro_f1"] - p_puro["macro_f1"], 4)},
        "regra": {
            "disparos": disparos,
            "cobertura": round(disparos / len(chaves), 4) if chaves else 0.0,
            "conflitos_com_o_modelo": len(conflitos),
            "conflitos_em_que_a_regra_acerta": regra_certa,
            "conflitos_em_que_o_modelo_acerta": modelo_certo,
            "conflitos_em_que_ambos_erram": ambos_errados,
        },
    }


def montar_relatorio(chaves: list[str], referencia: dict[str, str],
                     textos: dict[str, str],
                     por_modelo: dict[str, dict[str, str]]) -> dict[str, Any]:
    categorias_permitidas = {referencia[c] for c in chaves}
    fora_do_alcance = sorted(rp.categorias_alvo() - categorias_permitidas)
    resultados = {nome: comparar(chaves, referencia, textos, preds,
                                 categorias_permitidas)
                  for nome, preds in sorted(por_modelo.items())}

    ganham = [n for n, r in resultados.items() if r["global"]["delta_macro_f1"] > 0]
    problemas = {
        "registros_sem_texto": sum(1 for c in chaves if not textos.get(c)),
        "modelos_comparados": len(resultados),
    }
    return {
        "schema_version": 1,
        "status": "concluido",
        "protocolo": ("regra aplicada sobre as predicoes out-of-fold do Passo 4, "
                      "nos mesmos registros e nas mesmas particoes; a referencia "
                      "humana nao e alterada em nenhuma configuracao"),
        "corpus": {
            "registros": len(chaves),
            "categorias": len(categorias_permitidas),
            "preventivos_na_referencia": sum(
                1 for c in chaves
                if tm.tipo_manutencao(referencia[c]) == tm.PREVENTIVA),
        },
        "regra": {
            "criterio": ("dispara somente com termo de periodicidade e termo de "
                         "equipamento no mesmo chamado; abstem-se caso contrario"),
            "termos_periodicidade": len(rp.TERMOS_PERIODICIDADE),
            "termos_equipamento": len(rp.TERMOS_EQUIPAMENTO),
            "categorias_alvo": len(rp.categorias_alvo()),
            "categorias_alvo_fora_do_conjunto_avaliado": fora_do_alcance,
            "modulo": "src/regras_preventivas.py",
        },
        "modelos": resultados,
        "modelos_com_ganho_de_macro_f1": sorted(ganham),
        "problemas": problemas,
    }


def renderizar_markdown(relatorio: dict[str, Any]) -> str:
    corpus = relatorio["corpus"]
    regra = relatorio["regra"]
    linhas = [
        "# Regras preventivas contra modelos puros",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.",
        "",
        f"**Gerado em:** {relatorio.get('gerado_em', 'não informado')}",
        "",
        "## Protocolo",
        "",
        f"- {relatorio['protocolo']}.",
        f"- Registros: {corpus['registros']}, em {corpus['categorias']} categorias, "
        f"dos quais {corpus['preventivos_na_referencia']} têm referência preventiva.",
        f"- Regra: {regra['criterio']}.",
        f"- Tabela com {regra['termos_periodicidade']} termos de periodicidade e "
        f"{regra['termos_equipamento']} de equipamento, em `{regra['modulo']}`.",
        "",
        "## Efeito global",
        "",
        "| Modelo | Acurácia pura | Acurácia híbrida | Δ | Macro-F1 puro | Macro-F1 híbrido | Δ |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for nome, r in sorted(relatorio["modelos"].items(),
                          key=lambda kv: -kv[1]["global"]["hibrido"]["macro_f1"]):
        g = r["global"]
        linhas.append(
            f"| {nome} | {g['modelo_puro']['acuracia']} | {g['hibrido']['acuracia']} | "
            f"{g['delta_acuracia']:+} | {g['modelo_puro']['macro_f1']} | "
            f"{g['hibrido']['macro_f1']} | {g['delta_macro_f1']:+} |")

    linhas += [
        "",
        "## Efeito nos chamados de referência preventiva",
        "",
        "| Modelo | Acurácia pura | Acurácia híbrida | Δ |",
        "|---|---:|---:|---:|",
    ]
    for nome, r in sorted(relatorio["modelos"].items()):
        p = r["preventivos"]
        linhas.append(
            f"| {nome} | {p['modelo_puro']['acuracia']} | {p['hibrido']['acuracia']} | "
            f"{p['delta_acuracia']:+} |")

    linhas += [
        "",
        "## Conflitos entre regra e modelo",
        "",
        "| Modelo | Disparos | Conflitos | Regra acerta | Modelo acerta | Ambos erram |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for nome, r in sorted(relatorio["modelos"].items()):
        c = r["regra"]
        linhas.append(
            f"| {nome} | {c['disparos']} | {c['conflitos_com_o_modelo']} | "
            f"{c['conflitos_em_que_a_regra_acerta']} | "
            f"{c['conflitos_em_que_o_modelo_acerta']} | "
            f"{c['conflitos_em_que_ambos_erram']} |")

    ganham = relatorio["modelos_com_ganho_de_macro_f1"]
    linhas += [
        "",
        "## Leitura",
        "",
        (f"A camada híbrida melhora o macro-F1 de {len(ganham)} dos "
         f"{len(relatorio['modelos'])} modelos"
         + (f": {', '.join(ganham)}." if ganham else ".")),
        "",
        "A regra dispara no mesmo conjunto de registros para todos os modelos, "
        "porque depende apenas do texto. O que varia entre as linhas é a predição "
        "que ela substitui, e por isso o mesmo conjunto de regras ajuda um modelo "
        "e pode prejudicar outro.",
        "",
        "## Proveniência",
        "",
        "- Predições: `docs/dados/retreino_canonico_predicoes.csv`, Passo 4.",
        "- Regras: `src/regras_preventivas.py`.",
        "- Script: `src/comparar_regras_modelos.py`.",
        "- Nenhuma escrita foi realizada na planilha.",
        "",
    ]
    return "\n".join(linhas)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--predicoes", type=Path, default=PREDICOES_PADRAO)
    p.add_argument("--json", type=Path, default=SAIDA_JSON_PADRAO)
    p.add_argument("--markdown", type=Path, default=SAIDA_MD_PADRAO)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.predicoes.exists():
        print(f"Predicoes nao encontradas em {args.predicoes}. "
              "Execute o Passo 4 antes deste.", file=sys.stderr)
        return 2
    config = json.loads(args.config.read_text(encoding="utf-8"))
    dados = carregar_predicoes(args.predicoes)
    chaves = sorted(dados["referencia"])

    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    textos = carregar_textos(sh, config, set(chaves))

    relatorio = montar_relatorio(chaves, dados["referencia"], textos,
                                 dados["por_modelo"])
    relatorio["gerado_em"] = agora_bahia()
    relatorio["script_origem"] = "src/comparar_regras_modelos.py"

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    args.markdown.write_text(renderizar_markdown(relatorio), encoding="utf-8")
    print(renderizar_markdown(relatorio))
    return 0 if not relatorio["problemas"]["registros_sem_texto"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
