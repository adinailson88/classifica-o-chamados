#!/usr/bin/env python3
"""Tabelas suplementares S7 a S17, a partir da rodada canonica.

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
    S17  Fase 2C: LinearSVC vs combinacoes (votacao majoritaria, votacao
         suave, stacking), agregado e por outer fold. Numeracao provisoria,
         mantida em sequencia apos S16 apesar da lacuna ja existente em S4;
         a renumeracao continua de S5-S17 fica para a adaptacao ao periodico
         (docs/AUDITORIA_FINAL_SUBMISSAO.md, secao 9).

Le apenas artefatos com `hash_corpus` da rodada canonica e aborta se houver
divergencia. S17 e excecao: sua fonte exclusiva e o manifesto confirmatorio
da Fase 2C (docs/dados/ensemble/fase2c/fase2c_execucao_cientifica_1_manifest.json),
que nao carrega `hash_corpus` por pertencer a outra trilha experimental
(ver docs/FASE2C_RESOLUCAO_KF_DENOMINADOR.md); a funcao valida diretamente
os valores confirmatorios congelados (universo, denominador, capacidade,
proveniencia da Fase 2B) e aborta em qualquer divergencia. Somente leitura:
nao escreve na planilha nem no artigo, e nao recalcula nenhum resultado do
ensemble.
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
FASE2C_MANIFEST = (RAIZ / "docs" / "dados" / "ensemble" / "fase2c"
                   / "fase2c_execucao_cientifica_1_manifest.json")

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

NOME_METODO_FASE2C = {
    "linear_svc": "LinearSVC",
    "votacao_majoritaria": "Votacao majoritaria",
    "votacao_suave": "Votacao suave ponderada",
    "stacking": "Stacking",
}

FASE2C_VALORES_ESPERADOS = {
    "total_modelaveis": 13970,
    "total_y1": 593,
    "k_total": 2840,
    "run_id_fase2b": "31556028058",
    "commit_fase2b": "d6a5504cd9c4360b97fd90dd88c13bd430155459",
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


def s17_ensemble_confirmatorio() -> Path:
    """Fase 2C: LinearSVC vs combinacoes, agregado e por outer fold.

    Fonte exclusiva: o manifesto confirmatorio da Execucao Cientifica 1 da
    Fase 2C. Nao le nenhum artefato da rodada canonica do artigo principal e
    nao recalcula nenhum numero: cada valor gravado abaixo vem lido
    diretamente do manifesto, apos validar que universo, denominador,
    capacidade e proveniencia da Fase 2B batem com os valores confirmatorios
    congelados (docs/dados/ensemble/fase2c/EXECUCAO_CIENTIFICA_1.md).
    """
    manifesto = json.loads(FASE2C_MANIFEST.read_text(encoding="utf-8"))

    for campo, esperado in FASE2C_VALORES_ESPERADOS.items():
        obtido = manifesto.get(campo)
        if obtido != esperado:
            raise SystemExit(
                f"fase2c manifesto: {campo} esperado {esperado!r}, obtido {obtido!r}")

    metodos_agregado = manifesto["comparacao_agregada_por_metodo"]
    if set(metodos_agregado) != set(NOME_METODO_FASE2C):
        raise SystemExit(
            f"fase2c manifesto: metodos inesperados {sorted(metodos_agregado)}")

    folds = sorted(int(f) for f in manifesto["k_f_por_fold"])
    if folds != [1, 2, 3, 4, 5]:
        raise SystemExit(f"fase2c manifesto: folds inesperados {folds}")

    ordem_metodos = ("linear_svc", "votacao_majoritaria", "votacao_suave",
                      "stacking")
    ref_agregado = metodos_agregado[MODELO_DE_REFERENCIA]
    por_fold = manifesto["comparacao_por_fold"]
    y1_por_fold = manifesto["y1_por_fold"]

    linhas = []
    for metodo in ordem_metodos:
        m = metodos_agregado[metodo]
        linhas.append([
            "agregado", "", NOME_METODO_FASE2C[metodo], m["total_na_fila"],
            manifesto["total_y1"], m["capturados_y1"], m["precisao"],
            m["recall"], m["capturados_y1"] - ref_agregado["capturados_y1"],
            m["precisao"] - ref_agregado["precisao"],
            m["recall"] - ref_agregado["recall"],
        ])

    for fold in (1, 2, 3, 4, 5):
        chave = str(fold)
        ref_fold = por_fold[MODELO_DE_REFERENCIA][chave]
        for metodo in ordem_metodos:
            f = por_fold[metodo][chave]
            linhas.append([
                "fold", fold, NOME_METODO_FASE2C[metodo], f["K_f"],
                y1_por_fold[chave], f["capturados_y1"], f["precisao"],
                f["recall_fold"],
                f["capturados_y1"] - ref_fold["capturados_y1"],
                f["precisao"] - ref_fold["precisao"],
                f["recall_fold"] - ref_fold["recall_fold"],
            ])

    return escrever(
        "tabela_S17_ensemble_confirmatorio.csv",
        ["escopo", "outer_fold", "metodo", "K", "y1_denominador",
         "capturados", "precisao", "recall",
         "diff_capturados_vs_linear_svc", "diff_precisao_vs_linear_svc",
         "diff_recall_vs_linear_svc"],
        linhas,
    )


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

    caminho_s17 = s17_ensemble_confirmatorio()
    print(f"  {caminho_s17.name} (fonte: fase2c_execucao_cientifica_1_manifest.json, sem hash_corpus)")

    print(f"gerado em {agora_bahia()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
