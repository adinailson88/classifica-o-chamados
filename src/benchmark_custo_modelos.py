#!/usr/bin/env python3
"""Mede o custo computacional de treino e inferencia de cada modelo.

MOTIVACAO (decisao do pesquisador, 2026-08-01): o artigo compara acerto entre
modelos, mas nao quantifica o que cada um custa para produzir esse acerto. Sem
isso, a afirmacao de que o transformador "nao compensa" fica retorica. Este
script transforma custo em numero medido, no MESMO ambiente em que o BERTimbau
foi treinado (runner CPU do GitHub Actions), para que a comparacao seja justa.

O que e medido, por modelo:
  - tempo de treino (fit) sobre a base inteira;
  - tempo de inferencia (predict) sobre a base inteira;
  - tempo de inferencia por mil chamados, que e a grandeza operacional.

O BERTimbau NAO e treinado aqui. Um fine-tuning dele leva horas e exigiria
torch no runner; alem disso, misturar um treino de horas com sete treinos de
segundos no mesmo job so serviria para estourar o teto de tempo. O custo dele
entra por referencia medida nos logs do proprio transformer_ft.yml, com a
proveniencia declarada no JSON (campo `fonte`), nunca como estimativa.

REPETICOES: cada modelo e treinado `--repeticoes` vezes e o script reporta a
MEDIANA, nao a media -- o runner e uma maquina compartilhada e uma unica
execucao lenta distorce a media. O desvio entre repeticoes tambem e reportado,
para que se saiba quanta confianca o numero merece.

Nenhum texto de chamado entra no JSON de saida: so tempos, contagens e a
descricao do ambiente. O texto permanece restrito a planilha.
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

import modelos_zoo as zoo  # noqa: E402
import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
SAIDA_PADRAO = RAIZ / "docs" / "dados" / "custo_computacional.json"

# Medicao do fine-tuning do BERTimbau, extraida da duracao dos jobs `treinar`
# do workflow transformer_ft.yml. Sao execucoes REAIS, no mesmo tipo de runner
# (ubuntu-latest, CPU), nao estimativas. Duas execucoes concluidas ate o fim.
BERTIMBAU_REFERENCIA = {
    "modelo": "transformer_ft",
    "treino_segundos_medido": [161 * 60, 304 * 60],
    "fonte": "duracao dos jobs 'treinar' do workflow transformer_ft.yml "
             "(runner ubuntu-latest, CPU), execucoes de 01/08/2026",
    "ressalva": "treino sobre subconjunto (estado registra validados=1927), nao "
                "sobre a base inteira; o custo da base inteira seria maior, e "
                "por isso nao cabe no teto de 6 h do GitHub Actions",
    "treinado_neste_benchmark": False,
}


def medir(modelo_nome: str, textos: list[str], cats: list[str],
          repeticoes: int) -> dict[str, Any]:
    """Treina e infere `repeticoes` vezes; devolve medianas e dispersao."""
    treinos: list[float] = []
    inferencias: list[float] = []

    for i in range(repeticoes):
        m = zoo.criar_modelo(modelo_nome)

        t0 = time.perf_counter()
        m.fit(textos, cats)
        treinos.append(time.perf_counter() - t0)

        t0 = time.perf_counter()
        m.predict_score(textos)
        inferencias.append(time.perf_counter() - t0)

        print(f"  [{modelo_nome}] rep {i + 1}/{repeticoes}: "
              f"treino {treinos[-1]:.2f}s | inferencia {inferencias[-1]:.2f}s")

    def resumo(vs: list[float]) -> dict[str, Any]:
        return {
            "mediana_s": round(statistics.median(vs), 3),
            "min_s": round(min(vs), 3),
            "max_s": round(max(vs), 3),
            # Com 2 repeticoes stdev existe; com 1, nao ha dispersao a relatar.
            "desvio_s": round(statistics.stdev(vs), 3) if len(vs) > 1 else None,
        }

    treino = resumo(treinos)
    inferencia = resumo(inferencias)
    n = len(textos)
    return {
        "modelo": modelo_nome,
        "n": n,
        "treino": treino,
        "inferencia": inferencia,
        "inferencia_ms_por_mil": round(1000 * inferencia["mediana_s"] / n * 1000, 2),
        "repeticoes": repeticoes,
        "treinado_neste_benchmark": True,
    }


def ambiente() -> dict[str, Any]:
    """Descreve a maquina. Sem isso os tempos nao sao interpretaveis."""
    import sklearn
    try:
        import os
        cpus = len(os.sched_getaffinity(0))  # type: ignore[attr-defined]
    except AttributeError:  # Windows nao tem sched_getaffinity
        import os
        cpus = os.cpu_count()
    return {
        "python": platform.python_version(),
        "sistema": f"{platform.system()} {platform.release()}",
        "processador": platform.machine(),
        "cpus_disponiveis": cpus,
        "sklearn": sklearn.__version__,
        "observacao": "runner compartilhado; tempos absolutos variam entre "
                      "execucoes, as RAZOES entre modelos sao o dado estavel",
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--json", type=Path, default=SAIDA_PADRAO)
    p.add_argument("--repeticoes", type=int, default=3,
                   help="Execucoes por modelo; reporta a mediana.")
    p.add_argument("--modelos", default="leves",
                   help="'leves', 'todos' ou lista separada por virgula. "
                        "transformer_ft nunca e treinado aqui.")
    return p.parse_args()


def resolver_modelos(config: dict, escolha: str) -> list[str]:
    mm = config.get("multimodelo", {}) or {}
    leves = list(mm.get("modelos_leves", []))
    pesados = [m for m in mm.get("modelos_pesados", []) if m != "transformer_ft"]
    if escolha == "leves":
        return leves
    if escolha == "todos":
        return leves + pesados
    pedidos = [m.strip() for m in escolha.split(",") if m.strip()]
    return [m for m in pedidos if m != "transformer_ft"]


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    modelos = resolver_modelos(config, args.modelos)
    print(f"modelos a medir: {modelos}")
    print(f"repeticoes por modelo: {args.repeticoes}")

    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    ws = sh.worksheet(config["aba_principal"])
    import classificacao_multimodelo as cm
    elegiveis = cm.carregar_elegiveis(ws, config)
    textos = [e["texto"] for e in elegiveis]
    cats = [e["categoria_original"] for e in elegiveis]
    print(f"base carregada: {len(textos)} chamados, "
          f"{len(set(cats))} categorias\n")

    resultados = [medir(m, textos, cats, args.repeticoes) for m in modelos]
    resultados.sort(key=lambda r: r["treino"]["mediana_s"])

    saida = {
        "gerado_em": agora_bahia(),
        "script_origem": "src/benchmark_custo_modelos.py",
        "n_chamados": len(textos),
        "n_categorias": len(set(cats)),
        "natureza": "custo de treino e inferencia medido no mesmo ambiente "
                    "(runner CPU) em que o BERTimbau foi treinado; a comparacao "
                    "e de ordem de grandeza, nao de milissegundos",
        "ambiente": ambiente(),
        "por_modelo": resultados,
        "transformer_ft": BERTIMBAU_REFERENCIA,
    }

    mais_rapido = resultados[0] if resultados else None
    if mais_rapido:
        bert_mediana = statistics.median(BERTIMBAU_REFERENCIA["treino_segundos_medido"])
        saida["razao_bertimbau_vs_mais_rapido"] = round(
            bert_mediana / mais_rapido["treino"]["mediana_s"], 1)
        saida["mais_rapido"] = mais_rapido["modelo"]

    print("\n=== CUSTO DE TREINO (mediana) ===")
    for r in resultados:
        print(f"  {r['modelo']:<22} treino {r['treino']['mediana_s']:>8.2f}s  "
              f"inferencia {r['inferencia']['mediana_s']:>7.2f}s")
    if mais_rapido:
        print(f"\n  transformer_ft (medido nos logs): "
              f"{statistics.median(BERTIMBAU_REFERENCIA['treino_segundos_medido']):.0f}s")
        print(f"  razao BERTimbau / {saida['mais_rapido']}: "
              f"{saida['razao_bertimbau_vs_mais_rapido']}x")

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(saida, ensure_ascii=False, indent=1),
                         encoding="utf-8")
    print(f"\nescrito em {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
