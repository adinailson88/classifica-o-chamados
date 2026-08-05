#!/usr/bin/env python3
"""Sensibilidade da cobertura e do macro-F1 ao tratamento das categorias raras.

Ferramenta offline: le as predicoes canonicas e o relatorio de particoes. Nao
acessa a planilha, nao retreina nada e nao altera o protocolo da rodada.

O PROBLEMA. O protocolo agrupado exige que uma categoria disponha de grupos
textuais distintos em numero suficiente para figurar nas cinco dobras. Nove das
50 categorias nao satisfazem essa condicao e ficaram fora das particoes, com 88
linhas. O denominador das metricas caiu de 14.060 para 13.972 linhas e de 50
para 41 categorias. Isso precisa ser dimensionado, e nao apenas declarado: o
macro-F1 reportado e uma media sobre as 41 categorias que sobreviveram, e as
nove que sairam sao justamente as mais dificeis.

O QUE ESTA FERRAMENTA MEDE, sem alterar o protocolo nem refazer o treino:

  1. cobertura de linhas e de categorias, com a decomposicao do motivo da
     exclusao entre aritmetica (menos grupos distintos que dobras) e
     estratificacao (ausencia efetiva em alguma dobra);
  2. macro-F1 sob tres convencoes de denominador, para separar o que e
     desempenho do que e composicao da metrica:
       A  as 41 categorias avaliadas, que e a convencao do artigo;
       B  as 50 categorias da taxonomia, atribuindo F1 igual a zero as nove
          ausentes, que e o limite INFERIOR honesto: nenhum modelo pode prever
          categoria que nao esteve no treino;
       C  as 14 familias do primeiro nivel da taxonomia, que e a avaliacao
          hierarquica, na qual toda categoria rara e absorvida por uma familia
          com suporte;
  3. numero minimo de dobras que tornaria cada categoria excluida
     aritmeticamente elegivel, a partir da contagem de grupos distintos
     registrada no Passo 3;
  4. estabilidade da ordenacao dos modelos entre as tres convencoes.

O QUE ELA NAO FAZ, E POR QUE. Nao reexecuta o particionador com k menor nem
reavalia as 88 linhas: ambos exigem leitura da planilha viva e retreino, e
mudar o numero de dobras apos ver o resultado seria escolher o protocolo pela
metrica. As cinco categorias excluidas por estratificacao tinham grupos
distintos suficientes para k = 5 e ainda assim ficaram sem suporte em alguma
dobra; se sobreviveriam a k = 3 e questao que so o reparticionamento decide, e
esta registrado como tal.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "docs" / "dados"
PREDICOES_PADRAO = DADOS / "retreino_canonico_predicoes.csv"
PARTICOES_PADRAO = DADOS / "particoes_canonicas.json"
MANIFESTO_PADRAO = DADOS / "rodada_canonica.json"
SAIDA_JSON_PADRAO = DADOS / "sensibilidade_classes_raras.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "SENSIBILIDADE_CLASSES_RARAS.md"

SEPARADOR = " > "

NOME = {
    "linear_svc": "LinearSVC",
    "sgd": "SGD",
    "extra_trees": "Extra Trees",
    "regressao_logistica": "Regressão Logística",
    "random_forest": "Random Forest",
    "lstm": "LSTM",
    "naive_bayes": "Naive Bayes",
}


def familia(categoria: str) -> str:
    """Primeiro nível da taxonomia, isto é, a família que agrega a categoria."""
    return categoria.split(SEPARADOR, 1)[0].strip()


def ler_predicoes(caminho: Path) -> dict[str, list[tuple[str, str]]]:
    """Pares (referência, previsto) por modelo, na ordem do arquivo."""
    por_modelo: dict[str, list[tuple[str, str]]] = defaultdict(list)
    with caminho.open("r", encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            por_modelo[linha["modelo"]].append(
                (linha["referencia_humana"], linha["previsto"]))
    return dict(por_modelo)


def macro_f1(pares: list[tuple[str, str]],
             rotulos: list[str] | None = None) -> float:
    """Macro-F1 sobre um conjunto declarado de rótulos.

    O conjunto é declarado, e não inferido dos dados, porque é exatamente ele
    que distingue as três convenções: uma categoria listada e nunca predita
    nem presente entra com F1 igual a zero e puxa a média para baixo.
    """
    alvo = rotulos if rotulos is not None else sorted(
        {v for v, _ in pares} | {p for _, p in pares})
    tp = defaultdict(int)
    previstos = defaultdict(int)
    verdadeiros = defaultdict(int)
    for v, p in pares:
        verdadeiros[v] += 1
        previstos[p] += 1
        if v == p:
            tp[v] += 1
    soma = 0.0
    for c in alvo:
        denominador = previstos[c] + verdadeiros[c]
        soma += (2 * tp[c] / denominador) if denominador else 0.0
    return soma / len(alvo) if alvo else 0.0


def cobertura(particoes: dict[str, Any], linhas_avaliadas: int,
              categorias_avaliadas: int) -> dict[str, Any]:
    aritmetica = particoes.get("categorias_excluidas_por_suporte") or []
    estratificacao = particoes.get("categorias_excluidas_por_sorteio") or []
    linhas_congeladas = particoes.get("linhas_da_base_congelada") or (
        linhas_avaliadas + particoes.get("linhas_excluidas_total", 0))
    total_categorias = particoes.get("categorias_na_referencia")
    excluidas = [
        {"categoria": c["categoria"], "linhas": c["linhas"],
         "grupos_distintos": c.get("grupos_distintos"),
         "motivo": "aritmética: menos grupos textuais distintos que dobras",
         "dobras_maximas": c.get("dobras_possiveis")}
        for c in aritmetica
    ] + [
        {"categoria": c["categoria"], "linhas": c["linhas"],
         "grupos_distintos": None,
         "motivo": "estratificação: sem suporte em alguma dobra",
         "dobras_maximas": None}
        for c in estratificacao
    ]
    excluidas.sort(key=lambda x: -x["linhas"])
    return {
        "k_da_rodada": particoes.get("k"),
        "criterio": particoes.get("criterio_exclusao"),
        "linhas_da_base_congelada": linhas_congeladas,
        "linhas_avaliadas": linhas_avaliadas,
        "linhas_excluidas": particoes.get("linhas_excluidas_total"),
        "cobertura_de_linhas": round(linhas_avaliadas / linhas_congeladas, 6)
        if linhas_congeladas else None,
        "categorias_da_taxonomia": total_categorias,
        "categorias_avaliadas": categorias_avaliadas,
        "categorias_excluidas": len(excluidas),
        "cobertura_de_categorias": round(categorias_avaliadas / total_categorias, 4)
        if total_categorias else None,
        "linhas_excluidas_por_aritmetica": particoes.get("linhas_excluidas_por_suporte"),
        "linhas_excluidas_por_estratificacao": particoes.get("linhas_excluidas_por_sorteio"),
        "detalhe": excluidas,
        "declaracao_obrigatoria": (
            "o desempenho principal não cobre integralmente as 50 categorias da "
            "taxonomia: vale para as 41 com suporte nas cinco dobras, e as nove "
            "ausentes são as de menor frequência"),
    }


def dobras_viaveis(particoes: dict[str, Any]) -> dict[str, Any]:
    """Menor k que tornaria cada categoria excluída aritmeticamente elegível."""
    aritmetica = particoes.get("categorias_excluidas_por_suporte") or []
    estratificacao = particoes.get("categorias_excluidas_por_sorteio") or []
    por_k: dict[int, dict[str, Any]] = {}
    for k in (2, 3, 4, 5):
        recuperadas = [c for c in aritmetica if c.get("grupos_distintos", 0) >= k]
        por_k[k] = {
            "categorias_recuperaveis_por_aritmetica": len(recuperadas),
            "linhas_recuperaveis_por_aritmetica": sum(c["linhas"] for c in recuperadas),
            "categorias": [c["categoria"] for c in recuperadas],
        }
    return {
        "definicao": ("uma categoria só pode ter suporte em k dobras se possuir "
                      "ao menos k grupos textuais distintos, porque o grupo "
                      "inteiro ocupa uma única dobra"),
        "por_k": {str(k): v for k, v in por_k.items()},
        "categorias_excluidas_por_estratificacao": len(estratificacao),
        "linhas_excluidas_por_estratificacao":
            sum(c["linhas"] for c in estratificacao),
        "limite_da_analise": (
            "as categorias excluídas por estratificação já dispunham de grupos "
            "distintos suficientes para k = 5; se sobreviveriam a um k menor "
            "depende de reexecutar o particionador sobre a base viva, o que "
            "esta rodada não fez. Informação insuficiente para verificar."),
        "objecao_de_protocolo": (
            "reduzir k depois de observar o resultado escolheria o protocolo "
            "pela métrica; a redução só seria defensável como decisão anterior "
            "à avaliação, e ainda assim custaria treino menor por dobra"),
    }


def convencoes(por_modelo: dict[str, list[tuple[str, str]]],
               particoes: dict[str, Any]) -> dict[str, Any]:
    """Macro-F1 sob as três convenções de denominador."""
    qualquer = next(iter(por_modelo.values()))
    avaliadas = sorted({v for v, _ in qualquer})
    excluidas = [c["categoria"] for c in
                 (particoes.get("categorias_excluidas_por_suporte") or [])]
    excluidas += [c["categoria"] for c in
                  (particoes.get("categorias_excluidas_por_sorteio") or [])]
    taxonomia = sorted(set(avaliadas) | set(excluidas))
    familias = sorted({familia(c) for c in taxonomia})

    linhas = []
    for modelo, pares in sorted(por_modelo.items()):
        pares_familia = [(familia(v), familia(p)) for v, p in pares]
        acuracia = sum(1 for v, p in pares if v == p) / len(pares)
        linhas.append({
            "modelo": modelo,
            "acuracia": round(acuracia, 4),
            "macro_f1_a_avaliadas": round(macro_f1(pares, avaliadas), 4),
            "macro_f1_b_taxonomia_completa": round(macro_f1(pares, taxonomia), 4),
            "macro_f1_c_familias": round(macro_f1(pares_familia, familias), 4),
        })
    linhas.sort(key=lambda x: -x["macro_f1_a_avaliadas"])

    def ordem(chave: str) -> list[str]:
        return [x["modelo"] for x in sorted(linhas, key=lambda y: -y[chave])]

    ordem_a, ordem_b, ordem_c = ordem("macro_f1_a_avaliadas"), \
        ordem("macro_f1_b_taxonomia_completa"), ordem("macro_f1_c_familias")
    return {
        "convencao_a": {
            "rotulos": len(avaliadas),
            "descricao": "as 41 categorias com suporte nas cinco dobras",
            "uso": "convenção do artigo",
        },
        "convencao_b": {
            "rotulos": len(taxonomia),
            "descricao": ("as 50 categorias da taxonomia, com F1 igual a zero "
                          "nas nove ausentes das partições"),
            "uso": ("limite inferior: nenhum modelo prevê categoria ausente do "
                    "treino, de modo que o valor é o pior caso e não uma "
                    "estimativa do desempenho sobre a taxonomia inteira"),
        },
        "convencao_c": {
            "rotulos": len(familias),
            "descricao": "as 14 famílias do primeiro nível da taxonomia",
            "uso": ("avaliação hierárquica: cada categoria rara é absorvida por "
                    "uma família com suporte, o que fecha a lacuna de cobertura "
                    "de categorias, mas não a de linhas — as 88 linhas fora das "
                    "partições continuam sem predição out-of-fold"),
        },
        "por_modelo": linhas,
        "ordenacao_a": ordem_a,
        "ordenacao_b": ordem_b,
        "ordenacao_c": ordem_c,
        "ordenacao_estavel_entre_a_e_b": ordem_a == ordem_b,
        "ordenacao_estavel_entre_a_e_c": ordem_a == ordem_c,
        "nota_sobre_b": ("a convenção B é reescala monotônica da A pelo fator "
                         "41/50, de modo que a ordenação não pode mudar; o que "
                         "muda é a magnitude, e é isso que ela serve para "
                         "mostrar"),
    }


def montar_relatorio(por_modelo: dict[str, list[tuple[str, str]]],
                     particoes: dict[str, Any],
                     manifesto: dict[str, Any] | None = None) -> dict[str, Any]:
    qualquer = next(iter(por_modelo.values()))
    conv = convencoes(por_modelo, particoes)
    return {
        "schema_version": 1,
        "status": "concluido",
        "hash_corpus": (manifesto or {}).get("hash_corpus"),
        "protocolo": (
            "análise de sensibilidade sobre as predições canônicas já gravadas; "
            "nenhum modelo foi retreinado, nenhuma partição foi refeita e o "
            "protocolo da rodada permanece o do Passo 3"),
        "cobertura": cobertura(particoes, len(qualquer),
                               len({v for v, _ in qualquer})),
        "dobras_viaveis": dobras_viaveis(particoes),
        "convencoes_de_macro_f1": conv,
        "alternativas_avaliadas": [
            {"alternativa": "menor número de dobras",
             "efeito": ("recupera categorias por aritmética, mas apenas as "
                        "excluídas por esse motivo; ver `dobras_viaveis`"),
             "custo": "menos dados de treino por dobra e menor comparabilidade",
             "adotada": False},
            {"alternativa": "avaliação hierárquica por família",
             "efeito": ("fecha a lacuna de cobertura de categorias, de 41 em 50 "
                        "para 14 em 14 famílias, ao custo de responder a uma "
                        "pergunta mais grossa"),
             "custo": "perde a granularidade que a decisão de gestão usa",
             "adotada": ("reportada como sensibilidade; a leitura por tipo de "
                         "manutenção, em `recortes_canonicos.json`, é a versão "
                         "hierárquica que o artigo já usa no corpo")},
            {"alternativa": "política de abstenção",
             "efeito": ("não recupera as categorias ausentes, porque o modelo "
                        "não pode abster-se a favor de uma classe que não "
                        "conhece; atua sobre o erro nas categorias conhecidas"),
             "custo": "cobertura operacional menor",
             "adotada": ("já medida como automação seletiva por confiança em "
                         "`calibracao_canonica.json`")},
            {"alternativa": "fusão de categorias raras em uma classe residual",
             "efeito": "alteraria a taxonomia institucional sob avaliação",
             "custo": ("mudaria o objeto do estudo e impediria comparação com a "
                       "base administrativa"),
             "adotada": False},
        ],
    }


def renderizar_markdown(r: dict[str, Any]) -> str:
    c, d, v = r["cobertura"], r["dobras_viaveis"], r["convencoes_de_macro_f1"]
    nome = lambda x: NOME.get(x, x)  # noqa: E731
    linhas = [
        "# Sensibilidade ao tratamento das categorias raras",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, "
        "descrições ou IDs de chamados.",
        "",
        f"**Gerado em:** {r.get('gerado_em', 'não informado')}  ",
        f"**Hash do corpus:** `{r.get('hash_corpus') or 'não informado'}`",
        "",
        "## 1. Cobertura",
        "",
        f"- Linhas: {c['linhas_avaliadas']} de {c['linhas_da_base_congelada']} "
        f"({c['cobertura_de_linhas']:.2%}); {c['linhas_excluidas']} fora.",
        f"- Categorias: {c['categorias_avaliadas']} de "
        f"{c['categorias_da_taxonomia']} ({c['cobertura_de_categorias']:.0%}); "
        f"{c['categorias_excluidas']} fora.",
        f"- Motivo: {c['linhas_excluidas_por_aritmetica']} linhas por aritmética "
        f"e {c['linhas_excluidas_por_estratificacao']} por estratificação.",
        "",
        f"**{c['declaracao_obrigatoria'].capitalize()}.**",
        "",
        "| Categoria excluída | Linhas | Grupos distintos | Motivo |",
        "|:---|---:|---:|:---|",
    ]
    linhas += [f"| {x['categoria']} | {x['linhas']} | "
               f"{x['grupos_distintos'] if x['grupos_distintos'] is not None else '—'} | "
               f"{x['motivo']} |" for x in c["detalhe"]]

    linhas += [
        "",
        "## 2. Sensibilidade ao número de dobras",
        "",
        d["definicao"] + ".",
        "",
        "| k | Categorias recuperáveis por aritmética | Linhas |",
        "|---:|---:|---:|",
    ]
    for k in sorted(d["por_k"], key=int):
        x = d["por_k"][k]
        linhas.append(f"| {k} | {x['categorias_recuperaveis_por_aritmetica']} | "
                      f"{x['linhas_recuperaveis_por_aritmetica']} |")
    linhas += [
        "",
        d["limite_da_analise"],
        "",
        d["objecao_de_protocolo"] + ".",
        "",
        "## 3. Macro-F1 sob três convenções de denominador",
        "",
        f"- **A** — {v['convencao_a']['descricao']} ({v['convencao_a']['rotulos']} "
        f"rótulos): {v['convencao_a']['uso']}.",
        f"- **B** — {v['convencao_b']['descricao']} ({v['convencao_b']['rotulos']} "
        f"rótulos): {v['convencao_b']['uso']}.",
        f"- **C** — {v['convencao_c']['descricao']} ({v['convencao_c']['rotulos']} "
        f"rótulos): {v['convencao_c']['uso']}.",
        "",
        "| Modelo | Acurácia | Macro-F1 A | Macro-F1 B | Macro-F1 C |",
        "|---|---:|---:|---:|---:|",
    ]
    linhas += [f"| {nome(x['modelo'])} | {x['acuracia']} | "
               f"{x['macro_f1_a_avaliadas']} | {x['macro_f1_b_taxonomia_completa']} | "
               f"{x['macro_f1_c_familias']} |" for x in v["por_modelo"]]
    linhas += [
        "",
        f"Ordenação estável entre A e B: "
        f"{'sim' if v['ordenacao_estavel_entre_a_e_b'] else 'não'}. "
        f"Entre A e C: {'sim' if v['ordenacao_estavel_entre_a_e_c'] else 'não'}.",
        "",
        v["nota_sobre_b"] + ".",
        "",
        "## 4. Alternativas consideradas",
        "",
        "| Alternativa | Efeito | Custo | Adotada |",
        "|:---|:---|:---|:---|",
    ]
    linhas += [f"| {a['alternativa']} | {a['efeito']} | {a['custo']} | "
               f"{a['adotada'] if a['adotada'] else 'não'} |"
               for a in r["alternativas_avaliadas"]]
    linhas += [
        "",
        "## 5. Proveniência",
        "",
        "- Predições: `docs/dados/retreino_canonico_predicoes.csv`.",
        "- Partições e motivos de exclusão: `docs/dados/particoes_canonicas.json`.",
        "- Script: `src/sensibilidade_classes_raras.py`.",
        "- Nenhum modelo foi retreinado e nenhuma escrita foi feita na planilha.",
        "",
    ]
    return "\n".join(linhas)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--predicoes", type=Path, default=PREDICOES_PADRAO)
    p.add_argument("--particoes", type=Path, default=PARTICOES_PADRAO)
    p.add_argument("--manifesto", type=Path, default=MANIFESTO_PADRAO)
    p.add_argument("--json", type=Path, default=SAIDA_JSON_PADRAO)
    p.add_argument("--markdown", type=Path, default=SAIDA_MD_PADRAO)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    for caminho in (args.predicoes, args.particoes):
        if not caminho.exists():
            print(f"Arquivo nao encontrado: {caminho}", file=sys.stderr)
            return 2
    por_modelo = ler_predicoes(args.predicoes)
    if not por_modelo:
        print("Nenhuma predicao encontrada.", file=sys.stderr)
        return 2
    particoes = json.loads(args.particoes.read_text(encoding="utf-8"))
    manifesto = (json.loads(args.manifesto.read_text(encoding="utf-8"))
                 if args.manifesto.exists() else None)
    relatorio = montar_relatorio(por_modelo, particoes, manifesto)
    relatorio["gerado_em"] = agora_bahia()
    relatorio["script_origem"] = "src/sensibilidade_classes_raras.py"
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    args.markdown.write_text(renderizar_markdown(relatorio), encoding="utf-8")
    print(f"gerado: {args.json.relative_to(RAIZ)} e {args.markdown.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
