#!/usr/bin/env python3
"""Utilidade da reclassificacao sob custos assimetricos.

Ferramenta offline: le `docs/dados/comparacao_historica.json`, que ja traz por
modelo as divergencias contra a categoria historica arbitradas pela referencia
humana. Nao acessa a planilha, nao retreina nada e nao produz numero novo de
desempenho.

POR QUE ELA EXISTE. O ganho liquido do artigo e

    ganho = corrigidos - prejudicados,

expressao que so vale se corrigir um registro e estragar outro tiverem o mesmo
valor absoluto, e se revisar um chamado nao custar nada. Nenhuma das duas
hipoteses e neutra em gestao publica de manutencao: um registro corrompido
propaga para a serie temporal da categoria, para a estimativa de demanda e para
a alocacao de recurso, ao passo que a correcao apenas recupera o valor que o
registro ja deveria ter. A hipotese de custos iguais e, portanto, uma escolha, e
estava implicita.

O QUE ESTA FERRAMENTA FAZ. Torna a escolha explicita e mede a sensibilidade do
veredito a ela, com a funcao de utilidade

    U = b x corrigidos - c x prejudicados - r x revisados,

normalizada pelo beneficio da correcao, o que elimina qualquer necessidade de
inventar valor monetario e deixa duas razoes adimensionais:

    rho = c / b   custo do prejuizo em unidades de beneficio da correcao;
    lam = r / b   custo da revisao humana em unidades de beneficio da correcao.

    U / b = corrigidos - rho x prejudicados - lam x revisados.

O ganho liquido simples e o caso particular rho = 1, lam = 0, e permanece o
resultado principal do artigo por ser transparente. Esta analise e qualificacao
decisoria, nao substituicao.

DUAS POLITICAS SAO AVALIADAS, porque a mesma predicao admite usos diferentes:

    A  aplicacao direta: o modelo reescreve o rotulo sempre que diverge do
       historico. Nao ha revisao, logo lam nao entra. O ponto de equilibrio e
       rho* = corrigidos / prejudicados: abaixo dele a reclassificacao paga,
       acima nao paga.

    B  triagem por divergencia: a divergencia nao reescreve nada; enfileira o
       chamado para revisao humana. Como o revisor produz a propria referencia,
       nao ha prejudicados por construcao, e o beneficio e o numero de registros
       da fila em que o historico de fato estava errado, isto e, corrigidos mais
       neutros. O custo e a revisao de toda a fila. O ponto de equilibrio e
       lam* = (corrigidos + neutros) / divergencias, que e tambem a precisao da
       fila.

O limite da politica B precisa ficar declarado: ela supoe que a revisao humana
devolve a referencia, o que e verdadeiro por construcao neste desenho e a torna
um teto, nao uma previsao de campo.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "docs" / "dados"
HISTORICA_PADRAO = DADOS / "comparacao_historica.json"
SAIDA_JSON_PADRAO = DADOS / "utilidade_reclassificacao.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "UTILIDADE_RECLASSIFICACAO.md"

# Razoes adimensionais, sem valor monetario. A grade cobre desde o prejuizo que
# vale um quarto da correcao ate o que vale quatro vezes, faixa que enquadra
# tanto a leitura otimista quanto a conservadora.
RHOS_PADRAO = (0.25, 0.5, 1.0, 2.0, 4.0)
LAMBDAS_PADRAO = (0.0, 0.05, 0.10, 0.20)

NOME = {
    "linear_svc": "LinearSVC",
    "sgd": "SGD",
    "extra_trees": "Extra Trees",
    "regressao_logistica": "Regressão Logística",
    "random_forest": "Random Forest",
    "lstm": "LSTM",
    "naive_bayes": "Naive Bayes",
}


def utilidade(corrigidos: int, prejudicados: int, revisados: int,
              rho: float, lam: float) -> float:
    """U / b, em unidades de benefício da correção."""
    return corrigidos - rho * prejudicados - lam * revisados


def politica_aplicacao_direta(r: dict[str, Any],
                              rhos: tuple[float, ...]) -> dict[str, Any]:
    """O modelo reescreve o rótulo sempre que diverge do histórico."""
    corrigidos = r["corrigidos"]
    prejudicados = r["prejudicados"]
    equilibrio = (corrigidos / prejudicados) if prejudicados else None
    return {
        "descricao": ("o modelo reescreve a categoria sempre que diverge do "
                      "histórico; não há revisão humana, logo lambda não entra"),
        "corrigidos": corrigidos,
        "prejudicados": prejudicados,
        "revisados": 0,
        "ganho_liquido_simples": corrigidos - prejudicados,
        "rho_de_equilibrio": round(equilibrio, 4) if equilibrio else None,
        "leitura_do_equilibrio": (
            "a reclassificação só teria utilidade positiva se estragar um "
            "registro custasse menos de {:.3f} do que vale corrigir outro"
            .format(equilibrio) if equilibrio else None),
        "utilidade_por_rho": {
            f"{rho:g}": round(utilidade(corrigidos, prejudicados, 0, rho, 0.0), 1)
            for rho in rhos},
        "positiva_em_algum_rho_da_grade":
            any(utilidade(corrigidos, prejudicados, 0, rho, 0.0) > 0
                for rho in rhos),
    }


def politica_triagem(r: dict[str, Any],
                     lambdas: tuple[float, ...]) -> dict[str, Any]:
    """A divergência não reescreve nada: enfileira o chamado para revisão."""
    divergencias = r["divergencias_com_o_historico"]
    recuperaveis = r["corrigidos"] + r["neutros"]
    precisao = (recuperaveis / divergencias) if divergencias else None
    return {
        "descricao": ("a divergência enfileira o chamado para revisão humana em "
                      "vez de reescrever o rótulo; por construção não há "
                      "prejudicados, e o benefício é o número de registros da "
                      "fila cujo histórico estava de fato errado"),
        "fila": divergencias,
        "registros_da_fila_com_historico_errado": recuperaveis,
        "precisao_da_fila": round(precisao, 4) if precisao else None,
        "lambda_de_equilibrio": round(precisao, 4) if precisao else None,
        "leitura_do_equilibrio": (
            "a triagem paga enquanto revisar um chamado custar menos de {:.4f} "
            "do que vale corrigir um registro".format(precisao)
            if precisao else None),
        "utilidade_por_lambda": {
            f"{lam:g}": round(utilidade(recuperaveis, 0, divergencias, 1.0, lam), 1)
            for lam in lambdas},
        "pressuposto": ("a revisão humana devolve a referência, o que é "
                        "verdadeiro por construção neste desenho; o valor é "
                        "portanto um teto da política, não previsão de campo"),
    }


def montar_relatorio(historica: dict[str, Any],
                     rhos: tuple[float, ...] = RHOS_PADRAO,
                     lambdas: tuple[float, ...] = LAMBDAS_PADRAO,
                     ) -> dict[str, Any]:
    modelos = []
    for m in historica["modelos"]:
        r = m["reclassificacao"]
        modelos.append({
            "modelo": m["modelo"],
            "divergencias": r["divergencias_com_o_historico"],
            "corrigidos": r["corrigidos"],
            "prejudicados": r["prejudicados"],
            "neutros": r["neutros"],
            "ganho_liquido_simples": r["ganho_liquido"],
            "aplicacao_direta": politica_aplicacao_direta(r, rhos),
            "triagem_por_divergencia": politica_triagem(r, lambdas),
        })
    modelos.sort(key=lambda x: -x["ganho_liquido_simples"])

    melhor_rho = max((x["aplicacao_direta"]["rho_de_equilibrio"] or 0)
                     for x in modelos)
    melhor_precisao = max((x["triagem_por_divergencia"]["precisao_da_fila"] or 0)
                          for x in modelos)
    return {
        "schema_version": 1,
        "status": "concluido",
        "hash_corpus": historica.get("hash_corpus"),
        "funcao_de_utilidade": {
            "forma": "U = b x corrigidos - c x prejudicados - r x revisados",
            "normalizacao": ("dividida por b, o que deixa duas razões "
                             "adimensionais e dispensa valor monetário"),
            "rho": "c / b, custo do prejuízo em unidades de benefício da correção",
            "lambda": "r / b, custo da revisão em unidades de benefício da correção",
            "caso_particular": ("rho = 1 e lambda = 0 reproduzem o ganho líquido "
                                "simples do artigo, que permanece o resultado "
                                "principal por ser transparente"),
            "grade_de_rho": list(rhos),
            "grade_de_lambda": list(lambdas),
            "nenhum_valor_monetario_e_atribuido": True,
        },
        "corpus": historica.get("corpus"),
        "modelos": modelos,
        "conclusao": {
            "maior_rho_de_equilibrio": round(melhor_rho, 4),
            "reclassificacao_direta_defensavel": (
                "somente se estragar um registro valer menos de "
                f"{melhor_rho:.3f} do que vale corrigir outro, condição que "
                "nenhuma leitura razoável de custo em manutenção predial "
                "satisfaz, já que o registro corrompido propaga para a série da "
                "categoria e para a alocação de recurso, ao passo que a correção "
                "apenas recupera o valor devido"),
            "sob_custos_iguais": ("com rho = 1 a utilidade é negativa em todos "
                                  "os sete modelos, que é o resultado já "
                                  "reportado"),
            "maior_precisao_de_fila": round(melhor_precisao, 4),
            "triagem_defensavel": (
                "a mesma predição que não sustenta a reescrita sustenta a "
                "priorização: a fila de divergências concentra registros com "
                f"histórico errado em até {melhor_precisao:.2%}, várias vezes a "
                "taxa de alteração do rótulo na base congelada, de modo que a "
                "política B tem utilidade positiva sempre que revisar custar "
                "menos do que essa fração do benefício de corrigir"),
            "nota_sobre_denominadores": (
                "a taxa de alteração do rótulo histórico, 4,25%, é apurada sobre "
                "as 14.060 linhas da base congelada, ao passo que a precisão da "
                "fila é apurada sobre as 13.972 avaliadas; a diferença de 88 "
                "linhas não altera a ordem de grandeza da comparação, mas os "
                "dois denominadores não devem ser fundidos"),
        },
    }


def renderizar_markdown(r: dict[str, Any]) -> str:
    f, c = r["funcao_de_utilidade"], r["conclusao"]
    nome = lambda x: NOME.get(x, x)  # noqa: E731
    rhos = f["grade_de_rho"]
    lambdas = f["grade_de_lambda"]
    linhas = [
        "# Utilidade da reclassificação sob custos assimétricos",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, "
        "descrições ou IDs de chamados.",
        "",
        f"**Gerado em:** {r.get('gerado_em', 'não informado')}  ",
        f"**Hash do corpus:** `{r.get('hash_corpus') or 'não informado'}`",
        "",
        "## 1. Função de utilidade",
        "",
        f"`{f['forma']}`, {f['normalizacao']}:",
        "",
        f"- **rho** = {f['rho']};",
        f"- **lambda** = {f['lambda']}.",
        "",
        f"{f['caso_particular'].capitalize()}.",
        "",
        "## 2. Política A — aplicação direta",
        "",
        "O modelo reescreve a categoria sempre que diverge do histórico. "
        "A razão de equilíbrio é o valor de rho acima do qual a utilidade "
        "vira negativa.",
        "",
        "| Modelo | Corrigidos | Prejudicados | Ganho simples | rho de equilíbrio | "
        + " | ".join(f"U/b (rho={x:g})" for x in rhos) + " |",
        "|---|---:|---:|---:|---:|" + "---:|" * len(rhos),
    ]
    for m in r["modelos"]:
        a = m["aplicacao_direta"]
        linhas.append(
            f"| {nome(m['modelo'])} | {a['corrigidos']} | {a['prejudicados']} | "
            f"{a['ganho_liquido_simples']:+} | {a['rho_de_equilibrio']} | "
            + " | ".join(f"{a['utilidade_por_rho'][f'{x:g}']:+.1f}" for x in rhos)
            + " |")

    linhas += [
        "",
        f"{c['sob_custos_iguais'].capitalize()}. A reclassificação direta seria "
        f"{c['reclassificacao_direta_defensavel']}.",
        "",
        "## 3. Política B — triagem por divergência",
        "",
        "A divergência enfileira o chamado para revisão humana em vez de "
        "reescrever o rótulo. Não há prejudicados por construção, e o limite de "
        "equilíbrio de lambda coincide com a precisão da fila.",
        "",
        "| Modelo | Fila | Histórico errado na fila | Precisão da fila | "
        + " | ".join(f"U/b (lam={x:g})" for x in lambdas) + " |",
        "|---|---:|---:|---:|" + "---:|" * len(lambdas),
    ]
    for m in r["modelos"]:
        t = m["triagem_por_divergencia"]
        linhas.append(
            f"| {nome(m['modelo'])} | {t['fila']} | "
            f"{t['registros_da_fila_com_historico_errado']} | "
            f"{t['precisao_da_fila']} | "
            + " | ".join(f"{t['utilidade_por_lambda'][f'{x:g}']:+.1f}"
                         for x in lambdas) + " |")

    linhas += [
        "",
        f"{c['triagem_defensavel'].capitalize()}.",
        "",
        r["modelos"][0]["triagem_por_divergencia"]["pressuposto"].capitalize() + ".",
        "",
        c["nota_sobre_denominadores"].capitalize() + ".",
        "",
        "## 4. Proveniência",
        "",
        "- Contagens: `docs/dados/comparacao_historica.json`, rodada canônica.",
        "- Script: `src/utilidade_reclassificacao.py`.",
        "- Nenhum valor monetário é atribuído; todas as razões são adimensionais.",
        "",
    ]
    return "\n".join(linhas)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--historica", type=Path, default=HISTORICA_PADRAO)
    p.add_argument("--json", type=Path, default=SAIDA_JSON_PADRAO)
    p.add_argument("--markdown", type=Path, default=SAIDA_MD_PADRAO)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.historica.exists():
        print(f"Arquivo nao encontrado: {args.historica}", file=sys.stderr)
        return 2
    historica = json.loads(args.historica.read_text(encoding="utf-8"))
    if not historica.get("modelos"):
        print("Artefato sem modelos.", file=sys.stderr)
        return 2
    relatorio = montar_relatorio(historica)
    relatorio["gerado_em"] = agora_bahia()
    relatorio["script_origem"] = "src/utilidade_reclassificacao.py"
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    args.markdown.write_text(renderizar_markdown(relatorio), encoding="utf-8")
    print(f"gerado: {args.json.relative_to(RAIZ)} e {args.markdown.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
