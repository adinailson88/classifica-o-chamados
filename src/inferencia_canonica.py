#!/usr/bin/env python3
"""Inferencia estatistica sobre a rodada canonica, conforme o Passo 8 do plano.

Ferramenta offline: le as predicoes ja gravadas e o mapa de grupos textuais.
Nao acessa a planilha, nao retreina nada e nao escreve na aba.

BOOTSTRAP POR GRUPO, NAO POR LINHA. Esta e a diferenca central em relacao a
`analise_estatistica.py`, que serve a execucao legada. Reamostrar linhas
trataria como independentes os 4.586 registros que pertencem a grupos textuais
com mais de um membro, e estreitaria artificialmente os intervalos de
confianca. O bootstrap aqui sorteia GRUPOS com reposicao e reconstroi a amostra
com todos os registros de cada grupo sorteado, que e o bootstrap de
conglomerados. E a mesma unidade de dependencia que o Passo 3 usou para
particionar, o que mantem a coerencia do desenho.

PROTOCOLO DE TESTES, na ordem em que sao aplicados:

  1. Cochran Q sobre os sete vetores pareados de acerto, para a hipotese
     global de que todos os modelos tem a mesma taxa de acerto;
  2. se o Q rejeitar, McNemar pareado nos 21 pares, com correcao de Holm sobre
     essa familia.

A ordem importa: sem o teste global, 21 comparacoes pareadas seriam pesca de
significancia. Nenhum outro teste e acrescentado, conforme a exigencia de
limitar os testes as hipoteses do artigo.

Todos os testes usam exatamente as mesmas observacoes pareadas, o que e
verificado antes de calcular qualquer coisa.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "docs" / "dados"
PREDICOES_PADRAO = DADOS / "retreino_canonico_predicoes.csv"
MAPA_GRUPOS_PADRAO = DADOS / "grupos_textuais_mapa.csv"
MAPA_PARTICOES_PADRAO = DADOS / "particoes_canonicas_mapa.csv"
MANIFESTO_PADRAO = DADOS / "rodada_canonica.json"
SAIDA_JSON_PADRAO = DADOS / "inferencia_canonica.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "INFERENCIA_CANONICA.md"

REPETICOES_PADRAO = 1000
SEMENTE_PADRAO = 42
ALFA = 0.05


def carregar(predicoes: Path, mapa_grupos: Path) -> dict[str, Any]:
    """Monta as observacoes pareadas e verifica que todos os modelos as compartilham."""
    grupos_por_id: dict[str, str] = {}
    with mapa_grupos.open("r", encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            grupos_por_id[linha["id_sha256"]] = linha["grupo_sha256"]

    referencia: dict[str, str] = {}
    previsto: dict[str, dict[str, str]] = defaultdict(dict)
    confianca: dict[str, dict[str, float]] = defaultdict(dict)
    with predicoes.open("r", encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            chave = linha["id_sha256"]
            referencia[chave] = linha["referencia_humana"]
            previsto[linha["modelo"]][chave] = linha["previsto"]
            try:
                confianca[linha["modelo"]][chave] = float(linha["confianca"])
            except (KeyError, TypeError, ValueError):
                pass

    modelos = sorted(previsto)
    chaves = sorted(referencia)
    faltantes = {m: len(set(chaves) - set(previsto[m])) for m in modelos}
    return {
        "modelos": modelos,
        "chaves": chaves,
        "referencia": referencia,
        "previsto": dict(previsto),
        "confianca": dict(confianca),
        "grupos": [grupos_por_id[c] for c in chaves if c in grupos_por_id],
        "registros_sem_grupo_congelado": [c for c in chaves if c not in grupos_por_id],
        "modelos_com_observacao_faltante": {m: n for m, n in faltantes.items() if n},
    }


def matrizes(dados: dict[str, Any]) -> dict[str, Any]:
    """Vetores de acerto e de predicao, alinhados na mesma ordem de registros."""
    chaves, modelos = dados["chaves"], dados["modelos"]
    verdade = np.array([dados["referencia"][c] for c in chaves])
    acerto = np.vstack([
        np.array([dados["previsto"][m][c] == dados["referencia"][c] for c in chaves],
                 dtype=np.int8)
        for m in modelos
    ])
    predito = {m: np.array([dados["previsto"][m][c] for c in chaves]) for m in modelos}
    return {"verdade": verdade, "acerto": acerto, "predito": predito}


def indices_por_grupo(grupos: list[str]) -> list[np.ndarray]:
    """Indices dos registros de cada grupo textual, para o sorteio por conglomerado."""
    posicoes: dict[str, list[int]] = defaultdict(list)
    for i, g in enumerate(grupos):
        posicoes[g].append(i)
    return [np.array(v, dtype=np.int64) for _k, v in sorted(posicoes.items())]


def macro_f1_codificado(v: np.ndarray, p: np.ndarray, k: int) -> float:
    """Macro-F1 sobre rotulos ja codificados como inteiros de 0 a k-1.

    Reimplementado com `bincount` porque `sklearn.metrics.f1_score` sobre
    vetores de texto custa milissegundos por chamada, e o bootstrap faz
    milhares de chamadas. A matriz de confusao k x k sai de uma unica contagem.
    """
    confusao = np.bincount(v * k + p, minlength=k * k).reshape(k, k)
    tp = np.diag(confusao).astype(np.float64)
    previstos = confusao.sum(axis=0).astype(np.float64)
    verdadeiros = confusao.sum(axis=1).astype(np.float64)
    denominador = previstos + verdadeiros
    # Classe sem nenhuma ocorrencia prevista nem verdadeira entra como zero, o
    # mesmo que `zero_division=0` faz no sklearn.
    f1 = np.divide(2 * tp, denominador, out=np.zeros(k), where=denominador > 0)
    return float(f1.mean())


def bootstrap_por_grupo(verdade: np.ndarray, predito: np.ndarray,
                        blocos: list[np.ndarray], rotulos: list[str],
                        repeticoes: int = REPETICOES_PADRAO,
                        semente: int = SEMENTE_PADRAO) -> dict[str, Any]:
    """IC de percentil para acuracia e macro-F1, reamostrando grupos."""
    codigo = {r: i for i, r in enumerate(rotulos)}
    k = len(rotulos)
    # Predicao fora do conjunto de rotulos nao ocorre na rodada canonica, mas
    # se ocorresse seria contabilizada como erro, nunca como classe nova.
    v_cod = np.array([codigo[x] for x in verdade], dtype=np.int64)
    p_cod = np.array([codigo.get(x, -1) for x in predito], dtype=np.int64)
    validos = p_cod >= 0
    p_cod = np.where(validos, p_cod, (v_cod + 1) % k if k > 1 else 0)

    rng = np.random.default_rng(semente)
    n_blocos = len(blocos)
    acuracias = np.empty(repeticoes)
    macros = np.empty(repeticoes)
    for b in range(repeticoes):
        sorteados = rng.integers(0, n_blocos, size=n_blocos)
        idx = np.concatenate([blocos[s] for s in sorteados])
        v, p = v_cod[idx], p_cod[idx]
        acuracias[b] = float((v == p).mean())
        macros[b] = macro_f1_codificado(v, p, k)

    def ic(amostras: np.ndarray) -> dict[str, float]:
        return {"media": round(float(amostras.mean()), 4),
                "ic95_min": round(float(np.percentile(amostras, 2.5)), 4),
                "ic95_max": round(float(np.percentile(amostras, 97.5)), 4)}

    # Estimativa observada, na amostra inteira e sem reamostragem. E ela que o
    # artigo reporta como valor da metrica; a media das reamostragens e outra
    # grandeza e as duas nao devem ocupar a mesma coluna de uma tabela.
    observada = {"acuracia": round(float((v_cod == p_cod).mean()), 4),
                 "macro_f1": round(macro_f1_codificado(v_cod, p_cod, k), 4)}
    return {"acuracia": ic(acuracias), "macro_f1": ic(macros),
            "observado": observada}


def consenso_entre_modelos(dados: dict[str, Any]) -> dict[str, Any]:
    """Unanimidade e entropia de votos entre os modelos, por registro.

    O criterio precisa ser declarado porque nao ha um limiar canonico: aqui,
    'desacordo estrutural' e o registro em que os sete modelos distribuem os
    votos por tres ou mais categorias distintas, isto e, em que a discordancia
    nao se resume a um par de alternativas. A entropia normalizada acompanha o
    numero como medida continua, na base do numero de modelos.
    """
    chaves, modelos = dados["chaves"], dados["modelos"]
    previsto = dados["previsto"]
    n_modelos = len(modelos)
    unanimes = 0
    tres_ou_mais = 0
    soma_entropia = 0.0
    distribuicao: dict[int, int] = defaultdict(int)
    for c in chaves:
        contagem: dict[str, int] = defaultdict(int)
        for m in modelos:
            contagem[previsto[m][c]] += 1
        distintas = len(contagem)
        distribuicao[distintas] += 1
        if distintas == 1:
            unanimes += 1
        if distintas >= 3:
            tres_ou_mais += 1
        h = -sum((v / n_modelos) * math.log(v / n_modelos)
                 for v in contagem.values())
        soma_entropia += h / math.log(n_modelos) if n_modelos > 1 else 0.0
    n = len(chaves)
    return {
        "criterio_unanimidade": "os sete modelos preveem a mesma categoria",
        "criterio_desacordo_estrutural":
            "tres ou mais categorias distintas entre as sete predicoes",
        "base_da_entropia": "logaritmo do numero de modelos",
        "registros": n,
        "modelos": n_modelos,
        "unanimes": unanimes,
        "proporcao_unanimes": round(unanimes / n, 4) if n else None,
        "com_desacordo_estrutural": tres_ou_mais,
        "proporcao_com_desacordo_estrutural": round(tres_ou_mais / n, 4) if n else None,
        "entropia_media_normalizada": round(soma_entropia / n, 4) if n else None,
        "categorias_distintas_por_registro":
            {str(k): distribuicao[k] for k in sorted(distribuicao)},
    }


def correlacao_confianca_acerto(dados: dict[str, Any]) -> dict[str, Any]:
    """Spearman e ponto-bisserial entre confianca bruta e acerto, por modelo.

    Pre-requisito da calibracao: se a confianca nao ordena o acerto, nenhum
    limiar de automacao se sustenta. A versao anterior deste numero vinha de
    `estatistica.json`, que e da execucao legada e tem outro denominador; aqui
    ele sai das mesmas predicoes que produzem as demais tabelas.
    """
    from scipy import stats

    chaves = dados["chaves"]
    confianca = dados.get("confianca") or {}
    linhas = []
    for m in dados["modelos"]:
        conf_m = confianca.get(m, {})
        pares = [(conf_m[c], int(dados["previsto"][m][c] == dados["referencia"][c]))
                 for c in chaves if c in conf_m]
        if len(pares) < 3:
            continue
        conf = [p[0] for p in pares]
        acerto = [p[1] for p in pares]
        sp = stats.spearmanr(conf, acerto)
        pb = stats.pointbiserialr(acerto, conf)
        linhas.append({
            "modelo": m,
            "n": len(pares),
            "spearman_r": round(float(sp.statistic), 4),
            "spearman_p": float(sp.pvalue),
            "pointbiserial_r": round(float(pb.statistic), 4),
            "pointbiserial_p": float(pb.pvalue),
        })
    if not linhas:
        return {"modelos": [], "nota": "confianca ausente nas predicoes"}
    return {
        "definicao": ("correlacao entre o escore bruto do proprio modelo, sem "
                      "calibracao, e o indicador binario de acerto contra a "
                      "referencia humana"),
        "modelos": linhas,
        "spearman_min": min(x["spearman_r"] for x in linhas),
        "spearman_max": max(x["spearman_r"] for x in linhas),
        "pointbiserial_min": min(x["pointbiserial_r"] for x in linhas),
        "pointbiserial_max": max(x["pointbiserial_r"] for x in linhas),
        "todos_positivos_e_significativos": all(
            x["spearman_r"] > 0 and x["pointbiserial_r"] > 0
            and x["spearman_p"] < ALFA and x["pointbiserial_p"] < ALFA
            for x in linhas),
    }


def pressupostos(dados: dict[str, Any],
                 semente: int = SEMENTE_PADRAO) -> dict[str, Any]:
    """Normalidade, homogeneidade de variancia e colinearidade da confianca.

    Sao os pressupostos que justificam a escolha nao parametrica declarada no
    metodo. Antes desta rodada saiam de `estatistica.json`, que pertence a
    execucao legada e tem outro denominador; agora saem das mesmas predicoes
    das demais tabelas.
    """
    from scipy import stats
    import statsmodels.api as sm
    from statsmodels.stats.outliers_influence import variance_inflation_factor

    chaves, modelos = dados["chaves"], dados["modelos"]
    confianca = dados.get("confianca") or {}
    if any(m not in confianca for m in modelos):
        return {"modelos": [], "nota": "confianca ausente nas predicoes"}
    matriz = np.array([[confianca[m][c] for m in modelos] for c in chaves])

    # `shapiro` perde validade acima de 5.000 observacoes; a subamostra e
    # sorteada com a semente do estudo para ser reproduzivel.
    rng = np.random.default_rng(semente)
    limite = min(5000, matriz.shape[0])
    recorte = rng.choice(matriz.shape[0], size=limite, replace=False)

    matriz_vif = sm.add_constant(matriz)
    linhas = []
    for i, m in enumerate(modelos):
        w, p = stats.shapiro(matriz[recorte, i])
        linhas.append({
            "modelo": m,
            "shapiro_w": round(float(w), 4),
            "shapiro_p": float(p),
            "rejeita_normalidade": bool(p < ALFA),
            "variancia_da_confianca": round(float(matriz[:, i].var()), 5),
            "vif": round(float(variance_inflation_factor(matriz_vif, i + 1)), 3),
        })
    levene = stats.levene(*[matriz[:, i] for i in range(len(modelos))])
    return {
        "amostra_do_shapiro": limite,
        "semente_da_subamostra": semente,
        "modelos": linhas,
        "modelos_que_rejeitam_normalidade":
            sum(1 for x in linhas if x["rejeita_normalidade"]),
        "levene": {"estatistica": round(float(levene.statistic), 2),
                   "p": float(levene.pvalue),
                   "rejeita_homogeneidade": bool(levene.pvalue < ALFA)},
        "limiar_de_vif_elevado": 10.0,
        "modelos_com_vif_elevado":
            [x["modelo"] for x in linhas if x["vif"] > 10.0],
    }


def contagem_de_grupos(dados: dict[str, Any],
                       mapa_particoes: Path | None) -> dict[str, Any]:
    """Concilia as tres contagens de grupos textuais que circulam no projeto.

    Sao numeros diferentes de coisas diferentes, e confundi-los foi a origem da
    divergencia entre 9.786, 9.735 e 9.734:

    - grupos da base congelada: todas as linhas do Passo 2;
    - grupos congelados no recorte avaliado: unidade do bootstrap desta
      ferramenta, restrita as linhas que entraram nas particoes;
    - grupos do mapa de particoes: recalculados sobre o texto vivo no Passo 3,
      de modo que um texto editado depois do congelamento pode fundir-se a
      outro grupo e reduzir a contagem.
    """
    resultado: dict[str, Any] = {
        "grupos_congelados_no_recorte_avaliado": len(set(dados["grupos"])),
        "grupos_no_mapa_de_particoes": None,
        "registros_com_grupo_divergente_do_congelado": None,
        "nota": ("as contagens divergem quando o texto de um chamado e editado "
                 "na aba viva depois do congelamento; a contagem congelada e a "
                 "reproduzivel e e a usada como unidade de reamostragem"),
    }
    if mapa_particoes is None or not mapa_particoes.exists():
        return resultado
    por_id: dict[str, str] = {}
    with mapa_particoes.open("r", encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            por_id[linha["id_sha256"]] = linha["grupo_sha256"]
    congelado = dict(zip(dados["chaves"], dados["grupos"]))
    resultado["grupos_no_mapa_de_particoes"] = len(set(por_id.values()))
    resultado["registros_com_grupo_divergente_do_congelado"] = sum(
        1 for c, g in congelado.items() if c in por_id and por_id[c] != g)
    return resultado


def cochran_q(acerto: np.ndarray) -> dict[str, Any]:
    """Hipotese global: todos os modelos tem a mesma taxa de acerto."""
    from statsmodels.stats.contingency_tables import cochrans_q
    resultado = cochrans_q(acerto.T)
    return {
        "estatistica": round(float(resultado.statistic), 4),
        "p": float(resultado.pvalue),
        "graus_de_liberdade": int(acerto.shape[0] - 1),
        "rejeita_igualdade": bool(resultado.pvalue < ALFA),
        "hipotese_nula": "todos os modelos tem a mesma taxa de acerto",
    }


def mcnemar_par(a: np.ndarray, b: np.ndarray) -> dict[str, Any]:
    """McNemar pareado entre dois vetores de acerto.

    Usa o teste exato quando os discordantes sao poucos, onde a aproximacao
    qui-quadrado e ruim, e a versao com correcao de continuidade caso
    contrario. O criterio segue a pratica usual de 25 discordantes.
    """
    from statsmodels.stats.contingency_tables import mcnemar
    so_a = int(np.sum((a == 1) & (b == 0)))
    so_b = int(np.sum((a == 0) & (b == 1)))
    tabela = [[int(np.sum((a == 1) & (b == 1))), so_a],
              [so_b, int(np.sum((a == 0) & (b == 0)))]]
    exato = (so_a + so_b) < 25
    resultado = mcnemar(tabela, exact=exato, correction=not exato)
    return {
        "discordantes": so_a + so_b,
        "so_o_primeiro_acerta": so_a,
        "so_o_segundo_acerta": so_b,
        "estatistica": round(float(resultado.statistic), 4),
        "p": float(resultado.pvalue),
        "metodo": "exato" if exato else "qui-quadrado com correcao de continuidade",
    }


def holm(p_valores: list[float], alfa: float = ALFA) -> list[dict[str, Any]]:
    """Correcao de Holm-Bonferroni, que controla o erro familiar.

    Ordena os p crescentes, multiplica cada um por (m - i) e impoe monotonia,
    para que um p ajustado nunca fique abaixo do anterior. Depois do primeiro
    nao rejeitado, nenhum outro e rejeitado.
    """
    m = len(p_valores)
    ordem = sorted(range(m), key=lambda i: p_valores[i])
    ajustados = [0.0] * m
    anterior = 0.0
    for posicao, i in enumerate(ordem):
        valor = min(1.0, (m - posicao) * p_valores[i])
        anterior = max(anterior, valor)
        ajustados[i] = anterior
    return [{"p_ajustado": round(a, 6), "significativo": bool(a < alfa)}
            for a in ajustados]


def montar_relatorio(dados: dict[str, Any], repeticoes: int = REPETICOES_PADRAO,
                     semente: int = SEMENTE_PADRAO,
                     manifesto: dict[str, Any] | None = None,
                     mapa_particoes: Path | None = None) -> dict[str, Any]:
    m = matrizes(dados)
    blocos = indices_por_grupo(dados["grupos"])
    rotulos = sorted(set(m["verdade"].tolist()))
    modelos = dados["modelos"]

    intervalos = []
    for i, nome in enumerate(modelos):
        ic = bootstrap_por_grupo(m["verdade"], m["predito"][nome], blocos,
                                 rotulos, repeticoes, semente)
        observado = ic.pop("observado")
        # Tres grandezas distintas por metrica, nomeadas separadamente para que
        # nenhuma tabela troque uma pela outra: a estimativa observada, a media
        # das reamostragens e o intervalo de percentil.
        intervalos.append({
            "modelo": nome,
            "acuracia_pontual": round(float(m["acerto"][i].mean()), 4),
            "macro_f1_pontual": observado["macro_f1"],
            **ic,
        })
    intervalos.sort(key=lambda x: -x["acuracia_pontual"])

    q = cochran_q(m["acerto"])
    pares: list[dict[str, Any]] = []
    if q["rejeita_igualdade"]:
        brutos = []
        for i, j in combinations(range(len(modelos)), 2):
            r = mcnemar_par(m["acerto"][i], m["acerto"][j])
            r["par"] = [modelos[i], modelos[j]]
            pares.append(r)
            brutos.append(r["p"])
        for r, ajuste in zip(pares, holm(brutos)):
            r.update(ajuste)
        pares.sort(key=lambda x: x["p_ajustado"])

    return {
        "schema_version": 1,
        "status": "concluido",
        "hash_corpus": (manifesto or {}).get("hash_corpus"),
        "protocolo": {
            "bootstrap": ("reamostragem de grupos textuais com reposicao, "
                          "bootstrap de conglomerados; a linha nao e a unidade "
                          "de reamostragem porque registros do mesmo grupo nao "
                          "sao independentes"),
            "repeticoes": repeticoes,
            "semente": semente,
            "ordem_dos_testes": ("Cochran Q global primeiro; McNemar pareado "
                                 "apenas se o Q rejeitar, com Holm sobre os 21 pares"),
            "alfa": ALFA,
        },
        "corpus": {
            "registros": len(dados["chaves"]),
            "grupos_textuais": len(blocos),
            "categorias": len(rotulos),
            "modelos": len(modelos),
        },
        "grandezas_reportadas": {
            "acuracia_pontual": "estimativa observada na amostra inteira",
            "macro_f1_pontual": "estimativa observada na amostra inteira",
            "acuracia.media": "media das reamostragens do bootstrap",
            "macro_f1.media": "media das reamostragens do bootstrap",
            "ic95_min/ic95_max": "percentis 2,5 e 97,5 das reamostragens",
            "regra": ("o artigo reporta a estimativa observada ao lado do "
                      "intervalo do bootstrap; a media das reamostragens nao "
                      "ocupa a coluna da estimativa"),
        },
        "contagem_de_grupos": contagem_de_grupos(dados, mapa_particoes),
        "consenso_entre_modelos": consenso_entre_modelos(dados),
        "correlacao_confianca_acerto": correlacao_confianca_acerto(dados),
        "pressupostos": pressupostos(dados, semente),
        "intervalos": intervalos,
        "cochran_q": q,
        "mcnemar_pareado": pares,
        "problemas": {
            "modelos_com_observacao_faltante":
                len(dados["modelos_com_observacao_faltante"]),
            "registros_sem_grupo_congelado":
                len(dados.get("registros_sem_grupo_congelado", [])),
        },
        "nota_sobre_a_contagem_de_grupos": (
            "a unidade de reamostragem e o grupo CONGELADO no Passo 2, e nao o "
            "grupo recalculado sobre o texto vivo; os dois podem divergir se "
            "algum texto tiver sido editado depois do congelamento, e o "
            "congelado e o reproduzivel"),
    }


def renderizar_markdown(relatorio: dict[str, Any]) -> str:
    c, p, q = relatorio["corpus"], relatorio["protocolo"], relatorio["cochran_q"]
    linhas = [
        "# Inferência estatística da rodada canônica",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.",
        "",
        f"**Gerado em:** {relatorio.get('gerado_em', 'não informado')}  ",
        f"**Hash do corpus:** `{relatorio.get('hash_corpus') or 'não informado'}`",
        "",
        "## Protocolo",
        "",
        f"- Bootstrap: {p['bootstrap']}.",
        f"- Repetições: {p['repeticoes']}; semente: {p['semente']}; "
        f"nível de significância {p['alfa']}.",
        f"- Ordem dos testes: {p['ordem_dos_testes']}.",
        f"- Observações: {c['registros']} registros em {c['grupos_textuais']} grupos "
        f"textuais, {c['categorias']} categorias e {c['modelos']} modelos pareados.",
        "",
        "## Intervalos de confiança por bootstrap de grupo",
        "",
        "Três grandezas distintas, e a coluna de cada uma é declarada: a "
        "estimativa **observada** na amostra inteira, a **média** das mil "
        "reamostragens e o **intervalo** de percentil. O artigo reporta a "
        "estimativa observada ao lado do intervalo; a média das reamostragens "
        "não deve substituí-la.",
        "",
        "| Modelo | Acurácia obs. | Média boot. | IC 95% | Macro-F1 obs. | Média boot. | IC 95% |",
        "|---|---:|---:|---|---:|---:|---|",
    ]
    for i in relatorio["intervalos"]:
        a, f = i["acuracia"], i["macro_f1"]
        linhas.append(
            f"| {i['modelo']} | {i['acuracia_pontual']} | {a['media']} | "
            f"[{a['ic95_min']}; {a['ic95_max']}] | {i['macro_f1_pontual']} | "
            f"{f['media']} | [{f['ic95_min']}; {f['ic95_max']}] |")

    g = relatorio.get("contagem_de_grupos", {})
    if g:
        linhas += [
            "",
            "## Contagem de grupos textuais",
            "",
            "| Contagem | Valor |",
            "|---|---:|",
            f"| Grupos congelados no recorte avaliado (unidade do bootstrap) | "
            f"{g.get('grupos_congelados_no_recorte_avaliado')} |",
            f"| Grupos no mapa de partições, recalculados sobre o texto vivo | "
            f"{g.get('grupos_no_mapa_de_particoes')} |",
            f"| Registros cujo grupo vivo diverge do congelado | "
            f"{g.get('registros_com_grupo_divergente_do_congelado')} |",
            "",
            g.get("nota", ""),
        ]

    c_ = relatorio.get("consenso_entre_modelos", {})
    if c_:
        linhas += [
            "",
            "## Consenso entre os modelos",
            "",
            f"- Unanimidade ({c_['criterio_unanimidade']}): "
            f"{c_['unanimes']} registros, {c_['proporcao_unanimes']}.",
            f"- Desacordo estrutural ({c_['criterio_desacordo_estrutural']}): "
            f"{c_['com_desacordo_estrutural']} registros, "
            f"{c_['proporcao_com_desacordo_estrutural']}.",
            f"- Entropia média normalizada dos votos: "
            f"{c_['entropia_media_normalizada']}.",
        ]

    corr = relatorio.get("correlacao_confianca_acerto", {})
    if corr.get("modelos"):
        linhas += [
            "",
            "## Confiança bruta contra acerto",
            "",
            "| Modelo | n | Spearman | Ponto-bisserial |",
            "|---|---:|---:|---:|",
        ]
        linhas += [f"| {x['modelo']} | {x['n']} | {x['spearman_r']} | "
                   f"{x['pointbiserial_r']} |" for x in corr["modelos"]]
        linhas += [
            "",
            f"Spearman entre {corr['spearman_min']} e {corr['spearman_max']}; "
            f"ponto-bisserial entre {corr['pointbiserial_min']} e "
            f"{corr['pointbiserial_max']}. Todos positivos e significativos: "
            f"{'sim' if corr['todos_positivos_e_significativos'] else 'não'}.",
        ]

    pre = relatorio.get("pressupostos", {})
    if pre.get("modelos"):
        linhas += [
            "",
            "## Pressupostos",
            "",
            f"Shapiro-Wilk sobre subamostra de {pre['amostra_do_shapiro']} "
            f"observações, semente {pre['semente_da_subamostra']}. Fator de "
            f"Inflação de Variância entre as confianças dos modelos, limiar "
            f"convencional de {pre['limiar_de_vif_elevado']}.",
            "",
            "| Modelo | Shapiro W | Rejeita normalidade | Variância | VIF |",
            "|---|---:|---|---:|---:|",
        ]
        linhas += [
            f"| {x['modelo']} | {x['shapiro_w']} | "
            f"{'sim' if x['rejeita_normalidade'] else 'não'} | "
            f"{x['variancia_da_confianca']} | {x['vif']} |"
            for x in pre["modelos"]]
        lev = pre["levene"]
        linhas += [
            "",
            f"Normalidade rejeitada em {pre['modelos_que_rejeitam_normalidade']} "
            f"dos {len(pre['modelos'])} modelos. Levene = {lev['estatistica']}, "
            f"p = {lev['p']:.3g}: homogeneidade de variância "
            + ("rejeitada" if lev["rejeita_homogeneidade"] else "não rejeitada")
            + f". VIF acima do limiar em {len(pre['modelos_com_vif_elevado'])} "
            f"modelos: {', '.join(pre['modelos_com_vif_elevado']) or 'nenhum'}.",
        ]

    linhas += [
        "",
        "## Teste global",
        "",
        f"Cochran Q = {q['estatistica']}, {q['graus_de_liberdade']} graus de "
        f"liberdade, p = {q['p']:.3g}. Hipótese nula: {q['hipotese_nula']}. "
        + ("Rejeitada, o que autoriza as comparações pareadas."
           if q["rejeita_igualdade"] else
           "Não rejeitada; as comparações pareadas não são realizadas."),
        "",
    ]

    pares = relatorio["mcnemar_pareado"]
    if pares:
        linhas += [
            "## McNemar pareado, com correção de Holm",
            "",
            "| Par | Discordantes | Só o 1º acerta | Só o 2º acerta | p bruto | p ajustado | Significativo |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
        for r in pares:
            linhas.append(
                f"| {r['par'][0]} × {r['par'][1]} | {r['discordantes']} | "
                f"{r['so_o_primeiro_acerta']} | {r['so_o_segundo_acerta']} | "
                f"{r['p']:.3g} | {r['p_ajustado']:.3g} | "
                f"{'sim' if r['significativo'] else 'não'} |")
        nao = [r for r in pares if not r["significativo"]]
        linhas += [
            "",
            f"Dos {len(pares)} pares, {len(pares) - len(nao)} são significativos "
            f"após Holm e {len(nao)} não são. Pares não significativos indicam "
            "modelos empatados dentro do poder do teste, e o artigo não deve "
            "apresentá-los como ordenados.",
        ]

    linhas += [
        "",
        "## Proveniência",
        "",
        "- Predições: `docs/dados/retreino_canonico_predicoes.csv`.",
        "- Grupos textuais: `docs/dados/grupos_textuais_mapa.csv`, Passo 2.",
        "- Script: `src/inferencia_canonica.py`.",
        "- Nenhum modelo foi retreinado e nenhuma escrita foi feita na planilha.",
        "",
    ]
    return "\n".join(linhas)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--predicoes", type=Path, default=PREDICOES_PADRAO)
    p.add_argument("--grupos", type=Path, default=MAPA_GRUPOS_PADRAO)
    p.add_argument("--particoes", type=Path, default=MAPA_PARTICOES_PADRAO,
                   help=("mapa do Passo 3, usado apenas para conciliar as tres "
                         "contagens de grupos textuais"))
    p.add_argument("--manifesto", type=Path, default=MANIFESTO_PADRAO)
    p.add_argument("--repeticoes", type=int, default=REPETICOES_PADRAO)
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
              "no mapa do Passo 2; a unidade de reamostragem ficaria indefinida.",
              file=sys.stderr)
        return 2
    if dados["modelos_com_observacao_faltante"]:
        print("Modelos sem as mesmas observacoes pareadas: "
              f"{dados['modelos_com_observacao_faltante']}", file=sys.stderr)
        return 2
    manifesto = (json.loads(args.manifesto.read_text(encoding="utf-8"))
                 if args.manifesto.exists() else None)
    relatorio = montar_relatorio(dados, args.repeticoes, args.semente, manifesto,
                                 mapa_particoes=args.particoes)
    relatorio["gerado_em"] = agora_bahia()
    relatorio["script_origem"] = "src/inferencia_canonica.py"
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    args.markdown.write_text(renderizar_markdown(relatorio), encoding="utf-8")
    print(renderizar_markdown(relatorio))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
