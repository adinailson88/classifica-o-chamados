#!/usr/bin/env python3
"""Custo de treino e inferencia por modelo, sobre a base canonica completa.

Ferramenta estritamente READ-ONLY. Reproduz o desenho de medicao ja descrito na
Subsecao 4.7 do artigo: treino UNICO sobre a base inteira, repetido tres vezes,
com a mediana reportada.

Por que nao reaproveitar os tempos da rodada canonica: la o tempo somado e o de
cinco ajustes, cada um sobre quatro quintos do corpus, porque a rodada produz
predicao *out-of-fold*. Sao grandezas diferentes. A pergunta da Subsecao 4.7 e
quanto custa colocar um modelo em producao sobre a base inteira, e nao quanto
custou avalia-lo por validacao cruzada.

A mediana de tres execucoes existe para amortecer variacao do executor. A media
seria mais sensivel a uma unica execucao lenta, que em runner compartilhado
acontece sem aviso.
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import construir_grupos_textuais as cgt  # noqa: E402
import executar_rodada_canonica as erc  # noqa: E402
import modelos_zoo as zoo  # noqa: E402
import planilha as pl  # noqa: E402
import retreinar_modelos_canonicos as rmc  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
DADOS = RAIZ / "docs" / "dados"
MAPA_PARTICOES_PADRAO = DADOS / "particoes_canonicas_mapa.csv"
MAPA_GRUPOS_PADRAO = DADOS / "grupos_textuais_mapa.csv"
MANIFESTO_PADRAO = DADOS / "rodada_canonica.json"
SAIDA_JSON_PADRAO = DADOS / "custo_computacional_canonico.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "CUSTO_COMPUTACIONAL_CANONICO.md"

REPETICOES_PADRAO = 3


def medir_modelo(nome: str, textos: list[str], rotulos: list[str],
                 repeticoes: int = REPETICOES_PADRAO,
                 registrar=rmc._log) -> dict[str, Any]:
    """Treina e infere sobre a base inteira, `repeticoes` vezes."""
    treinos: list[float] = []
    inferencias: list[float] = []
    for r in range(1, repeticoes + 1):
        modelo = zoo.criar_modelo(nome)
        inicio = time.perf_counter()
        modelo.fit(textos, rotulos)
        treinos.append(time.perf_counter() - inicio)

        inicio = time.perf_counter()
        modelo.predict_score(textos)
        inferencias.append(time.perf_counter() - inicio)
        registrar(f"[custo] {nome}: execucao {r}/{repeticoes}, "
                  f"treino {treinos[-1]:.2f}s, inferencia {inferencias[-1]:.2f}s")
    mediana_treino = statistics.median(treinos)
    return {
        "modelo": nome,
        "repeticoes": repeticoes,
        # Guardado sem arredondar para que a razao entre modelos nao dependa
        # da casa decimal exibida; um modelo rapido arredondado a zero zeraria
        # o divisor.
        "_treino_bruto": mediana_treino,
        "treino_s": round(mediana_treino, 2),
        "treino_min_s": round(min(treinos), 2),
        "treino_max_s": round(max(treinos), 2),
        "inferencia_s": round(statistics.median(inferencias), 2),
        "inferencia_min_s": round(min(inferencias), 2),
        "inferencia_max_s": round(max(inferencias), 2),
    }


def montar_relatorio(textos: list[str], rotulos: list[str], modelos: list[str],
                     repeticoes: int = REPETICOES_PADRAO,
                     registrar=rmc._log) -> dict[str, Any]:
    medidas = [medir_modelo(m, textos, rotulos, repeticoes, registrar)
               for m in modelos]
    mais_rapido = min(medidas, key=lambda x: x["_treino_bruto"]) if medidas else None
    base = mais_rapido["_treino_bruto"] if mais_rapido else 0.0
    for m in medidas:
        m["razao_para_o_mais_rapido"] = (round(m["_treino_bruto"] / base, 1)
                                         if base > 0 else None)
        del m["_treino_bruto"]
    return {
        "schema_version": 1,
        "status": "concluido",
        "desenho": ("treino unico sobre a base completa, repetido "
                    f"{repeticoes} vezes, com a mediana reportada; nao e a soma "
                    "das dobras da validacao cruzada"),
        "corpus": {"linhas": len(textos), "categorias": len(set(rotulos))},
        "ambiente": {
            "python": platform.python_version(),
            "plataforma": platform.platform(),
            "dependencias": rmc._versoes_dependencias(),
        },
        "modelos": sorted(medidas, key=lambda x: x["treino_s"]),
        "referencia_da_razao": mais_rapido["modelo"] if mais_rapido else None,
    }


def renderizar_markdown(r: dict[str, Any]) -> str:
    a = r["ambiente"]
    linhas = [
        "# Custo computacional sobre a base canônica",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.",
        "",
        f"**Gerado em:** {r.get('gerado_em', 'não informado')}  ",
        f"**Hash do corpus:** `{r.get('hash_corpus') or 'não informado'}`",
        "",
        "## Desenho",
        "",
        f"- {r['desenho']}.",
        f"- Corpus: {r['corpus']['linhas']} linhas em {r['corpus']['categorias']} categorias.",
        f"- {a['python']} em {a['plataforma']}.",
        "- Dependências: " + ", ".join(f"{k} {v}" for k, v in a["dependencias"].items()) + ".",
        "",
        "## Tempos por modelo",
        "",
        "| Modelo | Treino (s) | Faixa | Inferência (s) | Faixa | Razão para o mais rápido |",
        "|---|---:|---|---:|---|---:|",
    ]
    for m in r["modelos"]:
        linhas.append(
            f"| {m['modelo']} | {m['treino_s']} | "
            f"{m['treino_min_s']}–{m['treino_max_s']} | {m['inferencia_s']} | "
            f"{m['inferencia_min_s']}–{m['inferencia_max_s']} | "
            f"{m['razao_para_o_mais_rapido']}× |")
    linhas += [
        "",
        "Medianas de três execuções. A faixa entre mínimo e máximo indica a "
        "variação do executor e ajuda a julgar quanto de uma diferença pequena "
        "é ruído de máquina.",
        "",
        "## Proveniência",
        "",
        "- Corpus: mesmo das partições canônicas, fixado por identificador.",
        "- Script: `src/custo_computacional_canonico.py`.",
        "- Nenhuma escrita foi realizada na planilha.",
        "",
    ]
    return "\n".join(linhas)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--particoes", type=Path, default=MAPA_PARTICOES_PADRAO)
    p.add_argument("--grupos-congelados", type=Path, default=MAPA_GRUPOS_PADRAO)
    p.add_argument("--modelos", default=",".join(rmc.MODELOS_PADRAO))
    p.add_argument("--repeticoes", type=int, default=REPETICOES_PADRAO)
    p.add_argument("--json", type=Path, default=SAIDA_JSON_PADRAO)
    p.add_argument("--markdown", type=Path, default=SAIDA_MD_PADRAO)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.particoes.exists():
        print(f"Mapa de particoes nao encontrado em {args.particoes}.", file=sys.stderr)
        return 2
    modelos = [m.strip() for m in args.modelos.split(",") if m.strip()]
    config = json.loads(args.config.read_text(encoding="utf-8"))
    particoes = rmc.carregar_particoes(args.particoes)
    congelados = (rmc.carregar_grupos_congelados(args.grupos_congelados)
                  if args.grupos_congelados.exists() else None)
    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    corpus = rmc.preparar_corpus(cgt.ler_registros(sh, config), particoes, congelados)
    if len(corpus["textos"]) < 10:
        print("Corpus insuficiente para medir custo.", file=sys.stderr)
        return 2

    relatorio = montar_relatorio(corpus["textos"], corpus["rotulos"], modelos,
                                 args.repeticoes)
    relatorio["hash_corpus"] = erc.hash_corpus(corpus)
    relatorio["gerado_em"] = agora_bahia()
    relatorio["script_origem"] = "src/custo_computacional_canonico.py"
    relatorio["linhas_com_texto_alterado_apos_o_congelamento"] = corpus[
        "linhas_com_texto_alterado_apos_o_congelamento"]

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    args.markdown.write_text(renderizar_markdown(relatorio), encoding="utf-8")
    print(renderizar_markdown(relatorio))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
