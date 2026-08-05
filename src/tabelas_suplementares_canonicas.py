#!/usr/bin/env python3
"""Tabelas suplementares S7 a S11, a partir da rodada canonica.

O Passo 11 do plano manda ao suplemento matrizes de confusao extensas,
resultados por categoria, ablacoes e testes secundarios, mantendo no corpo do
artigo apenas quatro ou cinco tabelas principais. Cinco tabelas sairam do
corpo nessa reducao e precisam continuar disponiveis, porque o texto passou a
citar seus valores em prosa:

    S7   dispersao das predicoes: entropia normalizada e Jensen-Shannon
    S8   curva ABC global, F1 macro por classe e por modelo
    S9   tarefa de tipo de manutencao
    S10  curva ABC interna a cada tipo, para o LinearSVC
    S11  efeito da camada de regras de periodicidade
    S16  calibracao completa dos sete modelos, resumida no corpo (Tabela 4)

Le apenas artefatos com `hash_corpus` da rodada canonica e aborta se houver
divergencia. Somente leitura: nao escreve na planilha nem no artigo.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "docs" / "dados"
FIGURAS = RAIZ / "04_artigo" / "figuras"

MODELO_DE_REFERENCIA = "linear_svc"

NOME = {
    "linear_svc": "LinearSVC",
    "sgd": "SGD",
    "extra_trees": "Extra Trees",
    "regressao_logistica": "Regressao Logistica",
    "random_forest": "Random Forest",
    "lstm": "LSTM",
    "naive_bayes": "Naive Bayes",
}


def carregar(nome: str) -> dict[str, Any]:
    return json.loads((DADOS / nome).read_text(encoding="utf-8"))


def conferir_hash(artefatos: dict[str, dict[str, Any]]) -> str:
    hashes = {n: d.get("hash_corpus") for n, d in artefatos.items()
              if d.get("hash_corpus")}
    distintos = set(hashes.values())
    if len(distintos) != 1:
        raise SystemExit(f"hash_corpus divergente entre artefatos: {hashes}")
    return distintos.pop()


def escrever(nome: str, cabecalho: list[str], linhas: list[list[Any]]) -> Path:
    destino = FIGURAS / nome
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)
    return destino


def s7_dispersao(historica: dict[str, Any]) -> Path:
    linhas = []
    for m in sorted(historica["modelos"],
                    key=lambda x: -x["dispersao"]["entropia_normalizada"]):
        d = m["dispersao"]
        linhas.append([NOME.get(m["modelo"], m["modelo"]),
                       d["categorias_previstas"], d["entropia_normalizada"],
                       d["js_contra_o_historico"]])
    return escrever("tabela_S7_dispersao_predicoes.csv",
                    ["modelo", "categorias_previstas", "entropia_normalizada",
                     "js_contra_o_historico"], linhas)


def s8_abc_global(recortes: dict[str, Any]) -> Path:
    linhas = []
    for m in recortes["modelos"]:
        for c in m["curva_abc"]:
            linhas.append([NOME.get(m["modelo"], m["modelo"]), c["classe"],
                           c["categorias"], c["chamados"],
                           c["proporcao_do_volume"], c["acuracia"],
                           c["macro_f1"]])
    return escrever("tabela_S8_curva_abc_global.csv",
                    ["modelo", "classe", "categorias", "chamados",
                     "proporcao_do_volume", "acuracia", "macro_f1"], linhas)


def s9_tarefa_tipo(recortes: dict[str, Any]) -> Path:
    linhas = []
    for m in sorted(recortes["modelos"],
                    key=lambda x: -x["tarefa_tipo"]["acuracia"]):
        t = m["tarefa_tipo"]
        f1 = t["f1_por_tipo"]
        linhas.append([NOME.get(m["modelo"], m["modelo"]), t["acuracia"],
                       t["macro_f1"], f1.get("Preventiva"),
                       f1.get("Corretiva"), f1.get("Não manutenção")])
    return escrever("tabela_S9_tarefa_tipo.csv",
                    ["modelo", "acuracia", "macro_f1", "f1_preventiva",
                     "f1_corretiva", "f1_nao_manutencao"], linhas)


def s10_abc_por_tipo(recortes: dict[str, Any]) -> Path:
    modelo = next(m for m in recortes["modelos"]
                  if m["modelo"] == MODELO_DE_REFERENCIA)
    linhas = []
    for tipo, classes in modelo["curva_abc_por_tipo"].items():
        for c in classes:
            linhas.append([tipo, c["classe"], c["categorias"], c["chamados"],
                           c["proporcao_do_volume"], c["acuracia"],
                           c["macro_f1"]])
    return escrever("tabela_S10_curva_abc_por_tipo.csv",
                    ["tipo", "classe", "categorias", "chamados",
                     "proporcao_do_volume_do_tipo", "acuracia", "macro_f1"],
                    linhas)


def s11_regras(regras: dict[str, Any]) -> Path:
    # `modelos` aqui e dicionario indexado pelo nome, e nao lista.
    itens = sorted(regras["modelos"].items(),
                   key=lambda kv: -kv[1]["global"]["modelo_puro"]["macro_f1"])
    linhas = []
    for nome, m in itens:
        g, r = m["global"], m["regra"]
        linhas.append([NOME.get(nome, nome),
                       g["modelo_puro"]["acuracia"], g["hibrido"]["acuracia"],
                       g["modelo_puro"]["macro_f1"], g["hibrido"]["macro_f1"],
                       g["delta_macro_f1"], r["disparos"],
                       r["conflitos_com_o_modelo"],
                       r["conflitos_em_que_a_regra_acerta"],
                       r["conflitos_em_que_o_modelo_acerta"]])
    return escrever("tabela_S11_regras_versus_modelos.csv",
                    ["modelo", "acuracia_pura", "acuracia_hibrida",
                     "macro_f1_puro", "macro_f1_hibrido", "delta_macro_f1",
                     "disparos", "conflitos", "regra_acerta",
                     "modelo_acerta"], linhas)


def s12_inferencia_agrupada(agrupada: dict[str, Any]) -> Path:
    """Os 21 pares completos, que o corpo do artigo resume em seis linhas."""
    linhas = []
    for p in agrupada["pares"]:
        ic = p["ic95_da_diferenca"]
        linhas.append([NOME.get(p["par"][0], p["par"][0]),
                       NOME.get(p["par"][1], p["par"][1]),
                       p["diferenca_de_acuracia"], ic[0], ic[1],
                       p["grupos_que_favorecem_o_primeiro"],
                       p["grupos_que_favorecem_o_segundo"],
                       p["grupos_empatados"],
                       p["d_de_cohen_pareado_por_grupo"],
                       p["p_permutacional_agrupado"], p["p_ajustado_holm"],
                       "sim" if p["significativo"] else "nao",
                       p["p_ajustado_holm_por_linha"]])
    return escrever("tabela_S12_inferencia_agrupada.csv",
                    ["modelo_1", "modelo_2", "diferenca_de_acuracia",
                     "ic95_min", "ic95_max", "grupos_a_favor_do_1",
                     "grupos_a_favor_do_2", "grupos_empatados",
                     "d_pareado_por_grupo", "p_permutacional",
                     "p_ajustado_holm", "significativo",
                     "p_ajustado_holm_por_linha"], linhas)


def s13_classes_raras(sensibilidade: dict[str, Any]) -> Path:
    """Macro-F1 sob as tres convencoes de denominador."""
    linhas = [[NOME.get(x["modelo"], x["modelo"]), x["acuracia"],
               x["macro_f1_a_avaliadas"], x["macro_f1_b_taxonomia_completa"],
               x["macro_f1_c_familias"]]
              for x in sensibilidade["convencoes_de_macro_f1"]["por_modelo"]]
    return escrever("tabela_S13_classes_raras.csv",
                    ["modelo", "acuracia", "macro_f1_41_avaliadas",
                     "macro_f1_50_taxonomia", "macro_f1_14_familias"], linhas)


def s14_utilidade(utilidade: dict[str, Any]) -> Path:
    """Utilidade das duas politicas ao longo das grades de rho e lambda."""
    rhos = utilidade["funcao_de_utilidade"]["grade_de_rho"]
    lambdas = utilidade["funcao_de_utilidade"]["grade_de_lambda"]
    linhas = []
    for m in utilidade["modelos"]:
        a, t = m["aplicacao_direta"], m["triagem_por_divergencia"]
        linhas.append([NOME.get(m["modelo"], m["modelo"]),
                       m["corrigidos"], m["prejudicados"], m["neutros"],
                       m["ganho_liquido_simples"], a["rho_de_equilibrio"]]
                      + [a["utilidade_por_rho"][f"{x:g}"] for x in rhos]
                      + [t["fila"], t["precisao_da_fila"]]
                      + [t["utilidade_por_lambda"][f"{x:g}"] for x in lambdas])
    return escrever("tabela_S14_utilidade_reclassificacao.csv",
                    ["modelo", "corrigidos", "prejudicados", "neutros",
                     "ganho_liquido_simples", "rho_de_equilibrio"]
                    + [f"U_direta_rho_{x:g}" for x in rhos]
                    + ["fila_de_triagem", "precisao_da_fila"]
                    + [f"U_triagem_lambda_{x:g}" for x in lambdas], linhas)


def s15_pressupostos(inferencia: dict[str, Any]) -> Path:
    """Verificacoes que sairam do corpo do artigo nesta rodada.

    Normalidade, homogeneidade, colinearidade entre confiancas e correlacao
    entre confianca e acerto nao decidem nada sobre a comparacao de
    classificadores binaria e pareada, e ocupavam espaco no corpo. Continuam
    publicadas aqui, porque foram calculadas e alguem pode querer confirma-las.
    """
    pre = inferencia.get("pressupostos") or {}
    corr = {x["modelo"]: x
            for x in (inferencia.get("correlacao_confianca_acerto") or {})
            .get("modelos", [])}
    linhas = []
    for x in pre.get("modelos", []):
        c = corr.get(x["modelo"], {})
        linhas.append([NOME.get(x["modelo"], x["modelo"]), x["shapiro_w"],
                       f"{x['shapiro_p']:.3g}",
                       "sim" if x["rejeita_normalidade"] else "nao",
                       x["variancia_da_confianca"], x["vif"],
                       c.get("spearman_r"), c.get("pointbiserial_r")])
    return escrever("tabela_S15_pressupostos.csv",
                    ["modelo", "shapiro_w", "shapiro_p", "rejeita_normalidade",
                     "variancia_da_confianca", "vif", "spearman_confianca_acerto",
                     "pointbiserial_confianca_acerto"], linhas)


def s16_calibracao_completa(calibracao: dict[str, Any]) -> Path:
    """Calibracao completa dos sete modelos; o corpo (Tabela 4) mostra so os
    quatro mais competitivos em acuracia, com ECE bruto e calibrado, cobertura
    e acuracia seletiva no alvo de 0,95.
    """
    linhas = []
    for m in sorted(calibracao["modelos"], key=lambda x: -x["acuracia_global"]):
        bruta, cal = m["bruta"], m["calibrada"]
        sel95 = m["automacao_seletiva"]["0.95"]
        linhas.append([NOME.get(m["modelo"], m["modelo"]),
                       bruta["ece"], cal["ece"], bruta["brier"], cal["brier"],
                       sel95["cobertura"], sel95["acuracia_seletiva"],
                       sel95["dobras_com_limiar"]])
    return escrever("tabela_S16_calibracao_completa.csv",
                    ["modelo", "ece_bruto", "ece_calibrado", "brier_bruto",
                     "brier_calibrado", "cobertura_alvo_0_95",
                     "acuracia_seletiva_alvo_0_95", "dobras_com_limiar"],
                    linhas)


def parse_args() -> argparse.Namespace:
    return argparse.ArgumentParser(description=__doc__).parse_args()


def main() -> int:
    parse_args()
    historica = carregar("comparacao_historica.json")
    recortes = carregar("recortes_canonicos.json")
    regras = carregar("regras_versus_modelos.json")
    agrupada = carregar("inferencia_agrupada.json")
    sensibilidade = carregar("sensibilidade_classes_raras.json")
    utilidade = carregar("utilidade_reclassificacao.json")
    inferencia = carregar("inferencia_canonica.json")
    calibracao = carregar("calibracao_canonica.json")
    corpus = conferir_hash({"historica": historica, "recortes": recortes,
                            "agrupada": agrupada,
                            "sensibilidade": sensibilidade,
                            "utilidade": utilidade,
                            "calibracao": calibracao})
    print(f"hash_corpus conferido: {corpus[:12]}")

    for caminho in (s7_dispersao(historica), s8_abc_global(recortes),
                    s9_tarefa_tipo(recortes), s10_abc_por_tipo(recortes),
                    s11_regras(regras), s12_inferencia_agrupada(agrupada),
                    s13_classes_raras(sensibilidade), s14_utilidade(utilidade),
                    s15_pressupostos(inferencia),
                    s16_calibracao_completa(calibracao)):
        print(f"  {caminho.name}")
    print(f"gerado em {agora_bahia()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
