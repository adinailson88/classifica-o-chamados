#!/usr/bin/env python3
"""Elimina métricas residuais da consolidação anterior no artigo.

O sincronizador principal substitui os blocos de resultados. Este passe final
corrige referências numéricas dispersas em trechos conceituais e históricos,
sempre derivando os valores correntes dos JSONs públicos.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ARTIGO = RAIZ / "04_artigo" / "artigo_classificacao_chamados_v3.md"
PLANO = RAIZ / "PLANO_ARTIGO_CAPITULO.md"
DADOS = RAIZ / "docs" / "dados"


def ler_json(nome: str) -> dict:
    return json.loads((DADOS / nome).read_text(encoding="utf-8"))


def dec(valor: float, casas: int = 4) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def pct(valor: float, casas: int = 2) -> str:
    return f"{valor * 100:.{casas}f}".replace(".", ",") + "%"


def inteiro(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def main() -> int:
    avaliacao = ler_json("avaliacao_final.json")
    estatistica = ler_json("estatistica.json")
    calibracao = ler_json("calibracao.json")

    val = {item["modelo"]: item for item in avaliacao["por_modelo"]}
    hist = {item["modelo"]: item for item in estatistica["acuracia_bootstrap"]}

    texto = ARTIGO.read_text(encoding="utf-8")
    original = texto

    # Subseção 3.4.1: referências dispersas às Tabelas 1 e 2.
    texto = texto.replace(
        "histórico (0,8029; Tabela 1) quanto o acerto validado (0,9493; Tabela 2)",
        f"histórico ({dec(hist['linear_svc']['acuracia'])}; Tabela 1) quanto o acerto validado ({dec(val['linear_svc']['acerto_validado'])}; Tabela 2)",
    )
    texto = texto.replace(
        "histórico (0,6996; Tabela 1) quanto no acerto validado (0,8609; Tabela\n2)",
        f"histórico ({dec(hist['naive_bayes']['acuracia'])}; Tabela 1) quanto no acerto validado ({dec(val['naive_bayes']['acerto_validado'])}; Tabela\n2)",
    )

    # Pontuação e apresentação da Subseção 4.1/4.2.
    texto = texto.replace(
        f"e LSTM ({dec(hist['lstm']['acuracia'])}), O teste de Cochran Q",
        f"e LSTM ({dec(hist['lstm']['acuracia'])}). O teste de Cochran Q",
    )
    segundo = avaliacao["melhor_vs_segundo"]
    nomes_ensemble = {
        "maioria_ponderada": "maioria ponderada",
        "confianca_calibrada_max": "confiança calibrada máxima",
        "maioria_simples": "maioria simples",
    }
    ensembles = " e ".join(
        [
            ", ".join(
                f"{nomes_ensemble[item['metodo']]} ({dec(item['acerto_validado'])})"
                for item in avaliacao["ensembles"][:-1]
            ),
            f"{nomes_ensemble[avaliacao['ensembles'][-1]['metodo']]} ({dec(avaliacao['ensembles'][-1]['acerto_validado'])})",
        ]
    )
    p_mcnemar = segundo["p_mcnemar"]
    p_texto = f"{p_mcnemar:.2e}".replace(".", ",").replace("e-08", " × 10⁻⁸")
    paragrafo_42 = (
        f"A diferença entre o primeiro e o segundo colocado é de {pct(segundo['delta']).replace('%', ' ponto percentual')}, "
        f"com McNemar *p* ≈ {p_texto}. Os *ensembles* avaliados foram {ensembles}; "
        "nenhum supera o LinearSVC isolado. A recomendação permanece utilizar o "
        "LinearSVC com calibração, sem combinar modelos nesta consolidação."
    )
    texto = re.sub(
        r"A diferença entre o primeiro e o segundo.*?sem combinar modelos nesta consolidação\.",
        paragrafo_42,
        texto,
        count=1,
        flags=re.S,
    )

    # Subseção 4.9: o denominador 9.096 pertence à coorte histórica do ablation;
    # atualiza-se apenas a comparação com a avaliação oficial corrente.
    lstm_atual = val["lstm"]["acerto_validado"]
    delta_ablation = lstm_atual - 0.8635
    texto = texto.replace(
        "isso reduziu a configuração atual (64 unidades, *dropout* de 0,5) de\n"
        "87,68% para 86,35% (7.854/9.096), uma correção pequena (1,33 ponto\n"
        "percentual). Segundo, e principal:",
        "isso reduziu a configuração atual (64 unidades, *dropout* de 0,5) de\n"
        "87,68% para 86,35% (7.854/9.096), uma correção pequena (1,33 ponto\n"
        "percentual). Esses denominadores pertencem à coorte congelada do estudo\n"
        "de ablação e não devem ser confundidos com a contagem corrente de decisões\n"
        "travadas. Segundo, e principal:",
    )
    texto = texto.replace("0,8790", dec(lstm_atual))
    texto = texto.replace(
        "mais próximo dos 0,8635 deste *ablation* corrigido (diferença residual\n"
        "de 1,55 pontos percentuais",
        f"mais próximo dos 0,8635 deste *ablation* corrigido (diferença residual\n"
        f"de {pct(delta_ablation).replace('%', ' pontos percentuais')}",
    )

    # Discussão: matriz atual da IA oficial versus histórico.
    matriz = calibracao["validacao_humana"]["matriz_ia_x_glpi"]
    n = sum(matriz.values())
    hist_erro = matriz["ia_ok_glpi_erro"] + matriz["ia_erro_glpi_erro"]
    taxa_hist_erro = hist_erro / n if n else 0.0
    novo_matriz = (
        "Ainda assim, a distinção entre concordância e acerto validado continua\n"
        "metodologicamente necessária. Na matriz IA × histórico da Subseção 4.3,\n"
        f"o histórico acerta e a IA erra em {inteiro(matriz['ia_erro_glpi_ok'])} casos, enquanto a IA corrige o\n"
        f"histórico em {inteiro(matriz['ia_ok_glpi_erro'])} casos. Há ainda {inteiro(matriz['ia_erro_glpi_erro'])} casos em que ambos divergem\n"
        f"da decisão, correspondentes a {pct(taxa_hist_erro)} de erro confirmado no rótulo histórico\n"
        "entre as decisões válidas. Essa proporção descreve a amostra conferida e\n"
        "não deve ser generalizada para a base completa. A validação humana permanece\n"
        "indispensável para distinguir erro do modelo, erro histórico e conflito\n"
        "taxonômico."
    )
    if "quando os dois discordam da decisão final" in texto:
        texto, n_sub = re.subn(
            r"Ainda assim, a distinção entre concordância e acerto validado continua.*?representativa\.",
            novo_matriz,
            texto,
            count=1,
            flags=re.S,
        )
        if n_sub != 1:
            raise RuntimeError(f"parágrafo residual da matriz não localizado: {n_sub}")

    # Considerações finais: restaura o verbo e melhora a leitura do ranking.
    ranking = (
        f"o LinearSVC obteve {pct(val['linear_svc']['acerto_validado'])}, seguido por SGD "
        f"({pct(val['sgd']['acerto_validado'])}), Regressão Logística "
        f"({pct(val['regressao_logistica']['acerto_validado'])}), Extra Trees "
        f"({pct(val['extra_trees']['acerto_validado'])}), Random Forest "
        f"({pct(val['random_forest']['acerto_validado'])}), LSTM "
        f"({pct(val['lstm']['acerto_validado'])}) e Naive Bayes "
        f"({pct(val['naive_bayes']['acerto_validado'])})"
    )
    texto = re.sub(
        r"Na amostra parcial e não probabilística de 9\.044 decisões\ntravadas, LinearSVC \(95,02%\), SGD \(94,11%\), Regressão Logística \(93,71%\), Extra Trees \(92,86%\), Random Forest \(92,41%\), LSTM \(88,11%\) e Naive Bayes \(86,27%\)\.",
        f"Na amostra parcial e não probabilística de {inteiro(avaliacao['n_avaliado'])} decisões\ntravadas, {ranking}.",
        texto,
    )

    # Verificações residuais que não devem permanecer como métricas correntes.
    proibidos = [
        "histórico (0,8029; Tabela 1)",
        "acerto validado (0,9493; Tabela 2)",
        "histórico (0,6996; Tabela 1)",
        "acerto validado (0,8609; Tabela",
        "0,8790",
        "577 casos",
        "3,51% dos casos",
        "e LSTM (0,6718), O teste",
    ]
    encontrados = [padrao for padrao in proibidos if padrao in texto]
    if encontrados:
        raise RuntimeError(f"métricas residuais ainda presentes: {encontrados}")

    if texto != original:
        ARTIGO.write_text(texto, encoding="utf-8")

    plano = PLANO.read_text(encoding="utf-8")
    plano = plano.replace(
        "**Onde está**: as 6 etapas do plano estão concluídas (branch\n"
        "`docs/reformulacao-editorial-governanca-preditiva`, PR #73, ainda sem\n"
        "merge — mudança de conteúdo grande, revisão em fatias pelo Adinailson\n"
        "antes de mesclar).",
        "**Onde está**: as seis etapas foram incorporadas à `main` pelas PRs #73 e\n"
        "#74. A sincronização numérica posterior está sendo concluída na PR #75.",
    )
    plano = plano.replace(
        "neurais/*ensembles* com vantagem de custo; ruído real de ~3,5% no\n"
        "histórico; meta de calibração próxima mas não formalmente",
        "neurais/*ensembles* com vantagem de custo; ruído confirmado no\n"
        "histórico; meta de calibração próxima mas não formalmente",
    )
    plano = re.sub(
        r"\*\*Próximo passo\*\*: \(1\) o Adinailson revisar/mesclar a PR #73;.*?13\.965 linhas\.",
        "**Próximo passo**: revisar o PDF regenerado após o merge da PR #75 e, se a\n"
        "formatação estiver íntegra, encerrar formalmente a rodada editorial.",
        plano,
        count=1,
        flags=re.S,
    )
    PLANO.write_text(plano, encoding="utf-8")

    print("resíduos numéricos e editoriais corrigidos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
