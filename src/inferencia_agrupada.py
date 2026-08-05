#!/usr/bin/env python3
"""Inferencia pareada no nivel do grupo textual, e nao no da linha.

Ferramenta offline: le as predicoes ja gravadas e o mapa de grupos textuais do
Passo 2. Nao acessa a planilha, nao retreina nada e nao escreve na aba.

POR QUE ESTA FERRAMENTA EXISTE. `src/inferencia_canonica.py` ja reamostrava
GRUPOS para os intervalos de confianca, mas os testes de hipotese continuavam
tratando a LINHA como unidade: o Cochran Q e os 21 McNemar somavam discordantes
linha a linha, como se dois chamados de texto identico fossem duas evidencias
independentes. Nao sao. 4.586 das 14.060 linhas da base congelada, ou 32,62%,
dividem texto normalizado com outra linha, e um unico grupo chega a 219 linhas.
Sob dependencia intragrupo, a variancia efetiva da diferenca e maior que a
binomial pareada, de modo que os valores de p do McNemar por linha sao
anticonservadores: estreitos por construcao, nao por evidencia.

O QUE MUDA. A unidade de analise passa a ser o grupo textual. Para cada par de
modelos calcula-se, por grupo, a diferenca de acertos

    d_g = (acertos do modelo A no grupo g) - (acertos do modelo B no grupo g),

e a inferencia inteira e conduzida sobre o vetor de d_g:

  * teste de permutacao pareada por troca de sinal do d_g, que e a
    randomizacao valida quando a unidade de troca e o conglomerado
    (GOOD, 2005; ANDERSON; TER BRAAK, 2003);
  * intervalo de confianca da diferenca de acuracia por bootstrap de
    conglomerados, sorteando grupos com reposicao (FIELD; WELSH, 2007;
    CAMERON; GELBACH; MILLER, 2008);
  * contagem de grupos que favorecem cada modelo, que e a leitura direta do
    sinal de d_g e nao depende de modelo distribucional;
  * correcao de Holm-Bonferroni sobre a familia dos 21 pares (HOLM, 1979).

O TESTE GLOBAL E PRESERVADO, MAS COM OUTRA DISTRIBUICAO DE REFERENCIA. A
estatistica Q de Cochran continua sendo a medida de dispersao entre as taxas de
acerto dos sete modelos, porque e pareada e apropriada a resposta binaria. O que
nao se sustenta e a distribuicao qui-quadrado tabelada, que pressupoe
independencia entre os registros. A referencia passa a ser empirica: sob a
hipotese nula de que os sete modelos sao igualmente bons, o rotulo de modelo e
permutavel, e a permutacao e aplicada por grupo inteiro, preservando a
dependencia intragrupo. Q e recalculado a cada permutacao e o p sai da posicao
do Q observado nessa distribuicao.

O p do McNemar por linha continua sendo calculado e reportado, LADO A LADO com
o p agrupado, exclusivamente para medir o tamanho do erro que se cometia. Ele
nao e mais a inferencia do artigo.

Referencias metodologicas:

  ANDERSON, M. J.; TER BRAAK, C. J. F. Permutation tests for multi-factorial
      analysis of variance. Journal of Statistical Computation and Simulation,
      v. 73, n. 2, p. 85-113, 2003.
  CAMERON, A. C.; GELBACH, J. B.; MILLER, D. L. Bootstrap-based improvements
      for inference with clustered errors. The Review of Economics and
      Statistics, v. 90, n. 3, p. 414-427, 2008.
  FIELD, C. A.; WELSH, A. H. Bootstrapping clustered data. Journal of the Royal
      Statistical Society: Series B, v. 69, n. 3, p. 369-390, 2007.
  GOOD, P. Permutation, parametric and bootstrap tests of hypotheses. 3. ed.
      New York: Springer, 2005.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from inferencia_canonica import (  # noqa: E402
    ALFA,
    MANIFESTO_PADRAO,
    MAPA_GRUPOS_PADRAO,
    PREDICOES_PADRAO,
    carregar,
    holm,
    indices_por_grupo,
    matrizes,
    mcnemar_par,
)
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "docs" / "dados"
SAIDA_JSON_PADRAO = DADOS / "inferencia_agrupada.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "INFERENCIA_AGRUPADA.md"

PERMUTACOES_PADRAO = 10000
PERMUTACOES_GLOBAIS_PADRAO = 2000
REAMOSTRAGENS_PADRAO = 2000
SEMENTE_PADRAO = 42

NOME = {
    "linear_svc": "LinearSVC",
    "sgd": "SGD",
    "extra_trees": "Extra Trees",
    "regressao_logistica": "Regressão Logística",
    "random_forest": "Random Forest",
    "lstm": "LSTM",
    "naive_bayes": "Naive Bayes",
}


# ---------------------------------------------------------------- unidade ---

def somas_por_grupo(acerto: np.ndarray, blocos: list[np.ndarray]) -> np.ndarray:
    """Matriz grupos x modelos com o total de acertos de cada modelo no grupo."""
    return np.vstack([acerto[:, b].sum(axis=1) for b in blocos]).astype(np.float64)


def auditoria_da_unidade(acerto: np.ndarray, blocos: list[np.ndarray],
                         modelos: list[str],
                         reamostragens: int = REAMOSTRAGENS_PADRAO,
                         semente: int = SEMENTE_PADRAO) -> dict[str, Any]:
    """Quantifica a dependencia intragrupo e o quanto ela infla a precisao aparente.

    O efeito de desenho e a razao entre a variancia da acuracia sob reamostragem
    de conglomerados e a variancia binomial que a suposicao de independencia
    entre linhas produziria. Valor acima de 1 significa que tratar linhas como
    independentes declara mais precisao do que os dados sustentam.
    """
    tamanhos = np.array([len(b) for b in blocos], dtype=np.float64)
    n = int(tamanhos.sum())
    somas = somas_por_grupo(acerto, blocos)
    rng = np.random.default_rng(semente)
    g = len(blocos)

    sorteios = rng.integers(0, g, size=(reamostragens, g))
    pesos = tamanhos[sorteios]                       # reamostragens x grupos
    denominador = pesos.sum(axis=1)
    linhas = []
    for i, m in enumerate(modelos):
        acertos_boot = somas[sorteios, i].sum(axis=1)
        p_boot = acertos_boot / denominador
        p = float(acerto[i].mean())
        ep_agrupado = float(p_boot.std(ddof=1))
        ep_ingenuo = float(np.sqrt(p * (1 - p) / n))
        linhas.append({
            "modelo": m,
            "acuracia": round(p, 4),
            "erro_padrao_por_linha": round(ep_ingenuo, 6),
            "erro_padrao_por_grupo": round(ep_agrupado, 6),
            "efeito_de_desenho": round((ep_agrupado / ep_ingenuo) ** 2, 3),
        })
    deff = [x["efeito_de_desenho"] for x in linhas]
    return {
        "unidade_estatistica_anterior": "linha (chamado individual)",
        "unidade_estatistica_adotada": "grupo de texto normalizado idêntico",
        "linhas": n,
        "grupos": g,
        "tamanho_medio_do_grupo": round(float(tamanhos.mean()), 4),
        "maior_grupo": int(tamanhos.max()),
        "grupos_unitarios": int((tamanhos == 1).sum()),
        "linhas_em_grupos_nao_unitarios": int(tamanhos[tamanhos > 1].sum()),
        "proporcao_de_linhas_dependentes":
            round(float(tamanhos[tamanhos > 1].sum() / n), 4),
        "por_modelo": linhas,
        "efeito_de_desenho_min": min(deff),
        "efeito_de_desenho_max": max(deff),
        "leitura": (
            "efeito de desenho acima de 1 indica que a suposição de "
            "independência entre linhas estreita artificialmente a precisão; "
            "os valores de p do McNemar por linha herdam esse estreitamento"),
    }


# ------------------------------------------------------------ teste global ---

def _q_de_cochran(colunas: np.ndarray, soma_linhas: float,
                  soma_quadrados_linhas: float, k: int) -> np.ndarray:
    """Q de Cochran a partir dos totais por modelo, vetorizado nas permutações.

    A forma fechada depende apenas dos totais por coluna quando os totais por
    linha estão fixos, e a permutação de rótulos de modelo preserva os totais
    por linha. Isso permite recalcular Q sem reconstruir a matriz.
    """
    denominador = k * soma_linhas - soma_quadrados_linhas
    if denominador <= 0:
        return np.zeros(colunas.shape[0])
    numerador = (k - 1) * (k * (colunas ** 2).sum(axis=-1) - soma_linhas ** 2)
    return numerador / denominador


def teste_global_agrupado(acerto: np.ndarray, blocos: list[np.ndarray],
                          permutacoes: int = PERMUTACOES_GLOBAIS_PADRAO,
                          semente: int = SEMENTE_PADRAO) -> dict[str, Any]:
    """Q de Cochran com distribuição de referência por permutação de grupo."""
    from statsmodels.stats.contingency_tables import cochrans_q

    k = acerto.shape[0]
    soma_linhas = float(acerto.sum())
    totais_por_registro = acerto.sum(axis=0).astype(np.float64)
    soma_quadrados_linhas = float((totais_por_registro ** 2).sum())
    somas = somas_por_grupo(acerto, blocos)            # grupos x modelos
    colunas_obs = somas.sum(axis=0)
    q_obs = float(_q_de_cochran(colunas_obs[None, :], soma_linhas,
                                soma_quadrados_linhas, k)[0])

    rng = np.random.default_rng(semente)
    g = len(blocos)
    maiores = 0
    lote = 200
    feitas = 0
    while feitas < permutacoes:
        atual = min(lote, permutacoes - feitas)
        # Uma permutação de rótulos de modelo por grupo, aplicada ao grupo
        # inteiro: é o grupo, e não a linha, que é a unidade de troca.
        ordens = np.argsort(rng.random((atual, g, k)), axis=2)
        permutadas = np.take_along_axis(
            np.broadcast_to(somas, (atual, g, k)), ordens, axis=2)
        colunas = permutadas.sum(axis=1)
        q = _q_de_cochran(colunas, soma_linhas, soma_quadrados_linhas, k)
        maiores += int((q >= q_obs - 1e-9).sum())
        feitas += atual

    tabelado = cochrans_q(acerto.T)
    return {
        "estatistica_q": round(q_obs, 4),
        "graus_de_liberdade": k - 1,
        "permutacoes": permutacoes,
        "unidade_da_permutacao": "grupo textual",
        "p_permutacional": round((maiores + 1) / (permutacoes + 1), 6),
        "p_permutacional_e_limite_superior": bool(maiores == 0),
        "p_qui_quadrado_por_linha": float(tabelado.pvalue),
        "rejeita_igualdade": bool((maiores + 1) / (permutacoes + 1) < ALFA),
        "hipotese_nula": "os sete modelos têm a mesma taxa de acerto",
        "justificativa": (
            "a estatística Q permanece adequada por ser pareada e binária, mas "
            "a distribuição qui-quadrado tabelada pressupõe independência entre "
            "registros, violada aqui; a referência passa a ser empírica, obtida "
            "por permutação do rótulo de modelo dentro de cada grupo textual"),
    }


# --------------------------------------------------------- pares agrupados ---

def comparacao_agrupada(a: np.ndarray, b: np.ndarray, blocos: list[np.ndarray],
                        tamanhos: np.ndarray,
                        permutacoes: int = PERMUTACOES_PADRAO,
                        reamostragens: int = REAMOSTRAGENS_PADRAO,
                        semente: int = SEMENTE_PADRAO) -> dict[str, Any]:
    """Diferença de acurácia entre dois modelos, com a unidade no grupo."""
    diferencas = np.array([int(a[bl].sum() - b[bl].sum()) for bl in blocos],
                          dtype=np.float64)
    n = float(tamanhos.sum())
    delta = float(diferencas.sum() / n)

    rng = np.random.default_rng(semente)
    g = len(blocos)

    # Permutação pareada por troca de sinal: sob a hipótese nula de que os dois
    # modelos são intercambiáveis, o sinal de d_g é simétrico.
    observado = abs(float(diferencas.sum()))
    maiores = 0
    feitas = 0
    lote = 2000
    while feitas < permutacoes:
        atual = min(lote, permutacoes - feitas)
        sinais = rng.integers(0, 2, size=(atual, g)).astype(np.float64) * 2 - 1
        estat = np.abs(sinais @ diferencas)
        maiores += int((estat >= observado - 1e-9).sum())
        feitas += atual
    p_perm = (maiores + 1) / (permutacoes + 1)

    # Bootstrap de conglomerados para o intervalo da diferença.
    sorteios = rng.integers(0, g, size=(reamostragens, g))
    deltas = diferencas[sorteios].sum(axis=1) / tamanhos[sorteios].sum(axis=1)
    ic_min, ic_max = np.percentile(deltas, [2.5, 97.5])

    favor_a = int((diferencas > 0).sum())
    favor_b = int((diferencas < 0).sum())
    empate = int((diferencas == 0).sum())

    # Tamanho de efeito no nível do grupo: diferença padronizada das diferenças
    # pareadas por grupo, análoga ao d de Cohen para amostras dependentes.
    desvio = float(diferencas.std(ddof=1))
    d_z = float(diferencas.mean() / desvio) if desvio > 0 else 0.0

    so_a = int(np.sum((a == 1) & (b == 0)))
    so_b = int(np.sum((a == 0) & (b == 1)))
    discordantes = so_a + so_b
    return {
        "diferenca_de_acuracia": round(delta, 4),
        "diferenca_em_pontos_percentuais": round(delta * 100, 2),
        "ic95_da_diferenca": [round(float(ic_min), 4), round(float(ic_max), 4)],
        "ic_exclui_zero": bool(ic_min > 0 or ic_max < 0),
        "grupos_que_favorecem_o_primeiro": favor_a,
        "grupos_que_favorecem_o_segundo": favor_b,
        "grupos_empatados": empate,
        "proporcao_de_grupos_decididos_a_favor_do_primeiro":
            round(favor_a / (favor_a + favor_b), 4) if favor_a + favor_b else None,
        "d_de_cohen_pareado_por_grupo": round(d_z, 4),
        "p_permutacional_agrupado": round(p_perm, 6),
        "p_permutacional_e_limite_superior": bool(maiores == 0),
        "linhas_so_o_primeiro_acerta": so_a,
        "linhas_so_o_segundo_acerta": so_b,
        "linhas_discordantes": discordantes,
        "p_mcnemar_por_linha": mcnemar_par(a, b)["p"],
    }


def montar_relatorio(dados: dict[str, Any], permutacoes: int,
                     permutacoes_globais: int, reamostragens: int,
                     semente: int,
                     manifesto: dict[str, Any] | None = None) -> dict[str, Any]:
    m = matrizes(dados)
    blocos = indices_por_grupo(dados["grupos"])
    tamanhos = np.array([len(b) for b in blocos], dtype=np.float64)
    modelos = dados["modelos"]
    acerto = m["acerto"]

    unidade = auditoria_da_unidade(acerto, blocos, modelos, reamostragens, semente)
    global_ = teste_global_agrupado(acerto, blocos, permutacoes_globais, semente)

    pares: list[dict[str, Any]] = []
    if global_["rejeita_igualdade"]:
        for i, j in combinations(range(len(modelos)), 2):
            # Orienta o par pelo modelo de maior acurácia, para que a diferença
            # relatada seja sempre positiva e a leitura não dependa da ordem
            # alfabética dos nomes.
            if acerto[i].mean() >= acerto[j].mean():
                pi, pj = i, j
            else:
                pi, pj = j, i
            r = comparacao_agrupada(acerto[pi], acerto[pj], blocos, tamanhos,
                                    permutacoes, reamostragens, semente)
            r["par"] = [modelos[pi], modelos[pj]]
            pares.append(r)
        ajustes = holm([r["p_permutacional_agrupado"] for r in pares])
        ajustes_ingenuos = holm([r["p_mcnemar_por_linha"] for r in pares])
        for r, ajuste, ingenuo in zip(pares, ajustes, ajustes_ingenuos):
            r["p_ajustado_holm"] = ajuste["p_ajustado"]
            r["significativo"] = ajuste["significativo"]
            r["p_ajustado_holm_por_linha"] = ingenuo["p_ajustado"]
            r["significativo_por_linha"] = ingenuo["significativo"]
        pares.sort(key=lambda x: (x["p_ajustado_holm"],
                                  -x["diferenca_de_acuracia"]))

    divergentes = [r for r in pares
                   if r["significativo"] != r["significativo_por_linha"]]
    return {
        "schema_version": 1,
        "status": "concluido",
        "hash_corpus": (manifesto or {}).get("hash_corpus"),
        "protocolo": {
            "unidade": "grupo de texto normalizado idêntico, congelado no Passo 2",
            "teste_global": ("estatística Q de Cochran com distribuição de "
                             "referência por permutação do rótulo de modelo "
                             "dentro de cada grupo"),
            "teste_pareado": ("permutação pareada por troca de sinal da "
                              "diferença de acertos por grupo"),
            "intervalo": ("bootstrap de conglomerados da diferença de acurácia, "
                          "sorteando grupos com reposição"),
            "correcao_multipla": "Holm-Bonferroni sobre a família dos 21 pares",
            "permutacoes_pareadas": permutacoes,
            "permutacoes_globais": permutacoes_globais,
            "reamostragens_do_bootstrap": reamostragens,
            "semente": semente,
            "alfa": ALFA,
        },
        "corpus": {
            "registros": len(dados["chaves"]),
            "grupos_textuais": len(blocos),
            "modelos": len(modelos),
        },
        "auditoria_da_unidade": unidade,
        "teste_global": global_,
        "pares": pares,
        "conclusao_da_auditoria": {
            "pares_que_mudam_de_veredito_com_a_unidade_correta": len(divergentes),
            "pares_divergentes": [r["par"] for r in divergentes],
            "leitura": (
                "a inferência por linha e a por grupo concordam no veredito de "
                "cada par nesta rodada; o que muda é a magnitude do valor de p, "
                "que por linha é anticonservador"
                if not divergentes else
                "há pares cujo veredito muda quando a unidade é corrigida; "
                "vale o resultado agrupado"),
        },
    }


# ------------------------------------------------------------------ saida ---

def renderizar_markdown(r: dict[str, Any]) -> str:
    u, g, p = r["auditoria_da_unidade"], r["teste_global"], r["protocolo"]
    nome = lambda x: NOME.get(x, x)  # noqa: E731
    linhas = [
        "# Inferência pareada no nível do grupo textual",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, "
        "descrições ou IDs de chamados.",
        "",
        f"**Gerado em:** {r.get('gerado_em', 'não informado')}  ",
        f"**Hash do corpus:** `{r.get('hash_corpus') or 'não informado'}`",
        "",
        "## 1. Auditoria da unidade estatística",
        "",
        f"- Unidade anterior: {u['unidade_estatistica_anterior']}.",
        f"- Unidade adotada: {u['unidade_estatistica_adotada']}.",
        f"- {u['linhas']} linhas em {u['grupos']} grupos; tamanho médio "
        f"{u['tamanho_medio_do_grupo']}, maior grupo {u['maior_grupo']}.",
        f"- {u['linhas_em_grupos_nao_unitarios']} linhas "
        f"({u['proporcao_de_linhas_dependentes']:.2%}) pertencem a grupos com "
        "mais de um membro e não são independentes entre si.",
        "",
        "| Modelo | Acurácia | EP por linha | EP por grupo | Efeito de desenho |",
        "|---|---:|---:|---:|---:|",
    ]
    linhas += [f"| {nome(x['modelo'])} | {x['acuracia']} | "
               f"{x['erro_padrao_por_linha']} | {x['erro_padrao_por_grupo']} | "
               f"{x['efeito_de_desenho']} |" for x in u["por_modelo"]]
    linhas += [
        "",
        f"Efeito de desenho entre {u['efeito_de_desenho_min']} e "
        f"{u['efeito_de_desenho_max']}. {u['leitura']}.",
        "",
        "## 2. Teste global",
        "",
        f"Q de Cochran = {g['estatistica_q']}, {g['graus_de_liberdade']} graus "
        f"de liberdade. Referência empírica com {g['permutacoes']} permutações "
        f"do rótulo de modelo por {g['unidade_da_permutacao']}: "
        + (f"p < {g['p_permutacional']}" if g["p_permutacional_e_limite_superior"]
           else f"p = {g['p_permutacional']}")
        + f". O p da distribuição qui-quadrado por linha seria "
        f"{g['p_qui_quadrado_por_linha']:.3g}.",
        "",
        g["justificativa"] + ".",
        "",
        "## 3. Comparações pareadas",
        "",
        "Cada par é orientado pelo modelo de maior acurácia, de modo que a "
        "diferença relatada é sempre positiva. O valor de p vem da permutação "
        "por troca de sinal da diferença por grupo e é corrigido por Holm sobre "
        "os 21 pares. A última coluna traz o p do McNemar por linha, corrigido "
        "pela mesma família, apenas para dimensionar o estreitamento que a "
        "suposição de independência produzia.",
        "",
        "| Par | Δ acurácia (p.p.) | IC95% da diferença | Grupos a favor do 1º | "
        "a favor do 2º | Empates | d pareado | p ajustado (grupo) | "
        "p ajustado (linha) |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for x in r["pares"]:
        ic = x["ic95_da_diferenca"]
        linhas.append(
            f"| {nome(x['par'][0])} × {nome(x['par'][1])} | "
            f"{x['diferenca_em_pontos_percentuais']} | "
            f"[{ic[0]:+.4f}; {ic[1]:+.4f}] | "
            f"{x['grupos_que_favorecem_o_primeiro']} | "
            f"{x['grupos_que_favorecem_o_segundo']} | "
            f"{x['grupos_empatados']} | {x['d_de_cohen_pareado_por_grupo']} | "
            f"{x['p_ajustado_holm']:.3g} | {x['p_ajustado_holm_por_linha']:.3g} |")

    c = r["conclusao_da_auditoria"]
    linhas += [
        "",
        f"Pares cujo veredito muda ao corrigir a unidade: "
        f"{c['pares_que_mudam_de_veredito_com_a_unidade_correta']}. "
        f"{c['leitura']}.",
        "",
        "## 4. Proveniência",
        "",
        "- Predições: `docs/dados/retreino_canonico_predicoes.csv`.",
        "- Grupos textuais: `docs/dados/grupos_textuais_mapa.csv`, Passo 2.",
        "- Script: `src/inferencia_agrupada.py`.",
        f"- Permutações pareadas: {p['permutacoes_pareadas']}; globais: "
        f"{p['permutacoes_globais']}; reamostragens: "
        f"{p['reamostragens_do_bootstrap']}; semente: {p['semente']}.",
        "- Nenhum modelo foi retreinado e nenhuma escrita foi feita na planilha.",
        "",
    ]
    return "\n".join(linhas)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--predicoes", type=Path, default=PREDICOES_PADRAO)
    p.add_argument("--grupos", type=Path, default=MAPA_GRUPOS_PADRAO)
    p.add_argument("--manifesto", type=Path, default=MANIFESTO_PADRAO)
    p.add_argument("--permutacoes", type=int, default=PERMUTACOES_PADRAO)
    p.add_argument("--permutacoes-globais", type=int,
                   default=PERMUTACOES_GLOBAIS_PADRAO)
    p.add_argument("--reamostragens", type=int, default=REAMOSTRAGENS_PADRAO)
    p.add_argument("--semente", type=int, default=SEMENTE_PADRAO)
    p.add_argument("--json", type=Path, default=SAIDA_JSON_PADRAO)
    p.add_argument("--markdown", type=Path, default=SAIDA_MD_PADRAO)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    for caminho in (args.predicoes, args.grupos):
        if not caminho.exists():
            print(f"Arquivo nao encontrado: {caminho}", file=sys.stderr)
            return 2
    dados = carregar(args.predicoes, args.grupos)
    if dados.get("registros_sem_grupo_congelado"):
        print(f"{len(dados['registros_sem_grupo_congelado'])} registros sem grupo "
              "no mapa do Passo 2; a unidade de analise ficaria indefinida.",
              file=sys.stderr)
        return 2
    if dados["modelos_com_observacao_faltante"]:
        print("Modelos sem as mesmas observacoes pareadas: "
              f"{dados['modelos_com_observacao_faltante']}", file=sys.stderr)
        return 2
    manifesto = (json.loads(args.manifesto.read_text(encoding="utf-8"))
                 if args.manifesto.exists() else None)
    relatorio = montar_relatorio(dados, args.permutacoes,
                                 args.permutacoes_globais, args.reamostragens,
                                 args.semente, manifesto)
    relatorio["gerado_em"] = agora_bahia()
    relatorio["script_origem"] = "src/inferencia_agrupada.py"
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    args.markdown.write_text(renderizar_markdown(relatorio), encoding="utf-8")
    print(renderizar_markdown(relatorio))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
