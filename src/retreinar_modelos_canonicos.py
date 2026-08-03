#!/usr/bin/env python3
"""Retreina os sete modelos comparaveis sob as particoes canonicas do Passo 3.

Ferramenta estritamente READ-ONLY sobre a planilha. Le a aba principal, fixa o
corpus pelas particoes congeladas em `docs/dados/particoes_canonicas_mapa.csv` e
produz predicoes *out-of-fold* para todo o corpus elegivel, usando a referencia
humana revisada como rotulo, conforme o Passo 4 de PLANO_EXECUCAO_ATUAL.md.

O criterio de aceite do passo e verificado e nao suposto: nenhum registro pode
receber predicao de um modelo que tenha visto, no treino, o proprio registro ou
qualquer outro do seu grupo textual.

As saidas sao sanitizadas: nao publicam titulos, descricoes nem IDs. O mapa de
predicoes usa o SHA-256 do ID, igual ao dos Passos 2 e 3.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import construir_grupos_textuais as cgt  # noqa: E402
import modelos_zoo as zoo  # noqa: E402
import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
MAPA_PARTICOES_PADRAO = RAIZ / "docs" / "dados" / "particoes_canonicas_mapa.csv"
SAIDA_JSON_PADRAO = RAIZ / "docs" / "dados" / "retreino_canonico.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "RETREINO_CANONICO.md"
SAIDA_PRED_PADRAO = RAIZ / "docs" / "dados" / "retreino_canonico_predicoes.csv"

# Os sete modelos comparaveis do Passo 4. O BERTimbau (`transformer_ft`) fica
# fora: e o Passo 6, que tem criterio proprio de admissao.
MODELOS_PADRAO = ["naive_bayes", "regressao_logistica", "linear_svc", "sgd",
                  "extra_trees", "random_forest", "lstm"]

SEMENTE_PADRAO = 42


def carregar_particoes(caminho: Path) -> dict[str, int]:
    """Le o mapa canonico do Passo 3: SHA-256 do ID para numero da dobra."""
    with caminho.open("r", encoding="utf-8", newline="") as f:
        return {linha["id_sha256"]: int(linha["dobra"])
                for linha in csv.DictReader(f) if linha.get("id_sha256")}


def montar_texto(registro: dict[str, str]) -> str:
    """Concatena os quatro campos, na mesma ordem usada pelos modelos."""
    partes = [str(registro.get(c, "") or "").strip() for c in cgt.CAMPOS_TEXTUAIS]
    return "\n".join(p for p in partes if p)


def preparar_corpus(registros: list[dict[str, str]],
                    particoes: dict[str, int]) -> dict[str, Any]:
    """Monta texto, rotulo, grupo e dobra de cada registro do corpus canonico.

    Registros fora do mapa de particoes sao ignorados: ou sao posteriores ao
    congelamento, ou sairam no Passo 3 por suporte insuficiente da categoria.
    """
    textos: list[str] = []
    rotulos: list[str] = []
    grupos: list[str] = []
    dobras: list[int] = []
    chaves: list[str] = []
    fora = 0
    sem_rotulo = 0
    for r in registros:
        id_chamado = r.get("id", "")
        digest = hashlib.sha256(id_chamado.encode("utf-8")).hexdigest()
        if not id_chamado or digest not in particoes:
            fora += 1
            continue
        rotulo = cgt.referencia_humana(r)
        if not rotulo:
            sem_rotulo += 1
            continue
        normalizados = [cgt.normalizar_texto(r.get(c, ""))
                        for c in cgt.CAMPOS_TEXTUAIS]
        textos.append(montar_texto(r))
        rotulos.append(rotulo)
        grupos.append(cgt.hash_grupo(normalizados))
        dobras.append(particoes[digest])
        chaves.append(digest)
    return {"textos": textos, "rotulos": rotulos, "grupos": grupos,
            "dobras": dobras, "chaves": chaves,
            "linhas_fora_das_particoes": fora,
            "linhas_sem_rotulo": sem_rotulo}


def _acuracia(verdade: list[str], predito: list[str]) -> float:
    certos = sum(1 for a, b in zip(verdade, predito) if a == b)
    return certos / len(verdade) if verdade else 0.0


def _log(mensagem: str) -> None:
    print(mensagem, file=sys.stderr)


def avaliar_modelo(nome: str, corpus: dict[str, Any],
                   registrar=_log) -> dict[str, Any]:
    """Produz predicoes out-of-fold e verifica a separacao por grupo textual."""
    from sklearn.metrics import balanced_accuracy_score, f1_score

    textos, rotulos = corpus["textos"], corpus["rotulos"]
    grupos, dobras = corpus["grupos"], corpus["dobras"]
    n = len(textos)
    preditos: list[str | None] = [None] * n
    vazamentos = 0
    tempo_treino = tempo_inferencia = 0.0

    tracemalloc.start()
    for dobra in sorted(set(dobras)):
        teste = [i for i, d in enumerate(dobras) if d == dobra]
        treino = [i for i, d in enumerate(dobras) if d != dobra]
        # Criterio de aceite do Passo 4, verificado a cada dobra: o treino nao
        # pode conter nenhum grupo textual presente no teste.
        vazamentos += len({grupos[i] for i in treino} & {grupos[i] for i in teste})

        modelo = zoo.criar_modelo(nome)
        inicio = time.perf_counter()
        modelo.fit([textos[i] for i in treino], [rotulos[i] for i in treino])
        tempo_treino += time.perf_counter() - inicio

        inicio = time.perf_counter()
        p, _ = modelo.predict_score([textos[i] for i in teste])
        tempo_inferencia += time.perf_counter() - inicio
        for j, i in enumerate(teste):
            preditos[i] = str(p[j])
        registrar(f"[retreino] {nome}: dobra {dobra} concluida "
                  f"({len(treino)} treino / {len(teste)} teste)")
    _atual, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    y_pred = [p if p is not None else "" for p in preditos]
    sem_predicao = sum(1 for p in preditos if p is None)
    categorias = sorted(set(rotulos))
    return {
        "modelo": nome,
        "acuracia": round(_acuracia(rotulos, y_pred), 4),
        "macro_f1": round(float(f1_score(rotulos, y_pred, labels=categorias,
                                         average="macro", zero_division=0)), 4),
        "balanced_accuracy": round(float(balanced_accuracy_score(rotulos, y_pred)), 4),
        "tempo_treino_s": round(tempo_treino, 2),
        "tempo_inferencia_s": round(tempo_inferencia, 2),
        "pico_memoria_mb": round(pico / (1024 * 1024), 1),
        "registros_sem_predicao": sem_predicao,
        "grupos_vazados_para_o_treino": vazamentos,
        "_predicoes": y_pred,
    }


def montar_relatorio(corpus: dict[str, Any], modelos: list[str],
                     semente: int = SEMENTE_PADRAO,
                     registrar=_log) -> dict[str, Any]:
    resultados = [avaliar_modelo(nome, corpus, registrar) for nome in modelos]

    problemas = {
        "modelos_com_vazamento_de_grupo":
            sum(1 for r in resultados if r["grupos_vazados_para_o_treino"]),
        "modelos_com_registro_sem_predicao":
            sum(1 for r in resultados if r["registros_sem_predicao"]),
        "linhas_do_corpus_sem_rotulo": corpus["linhas_sem_rotulo"],
    }
    bloqueios = [nome for nome, n in problemas.items() if n]
    publicaveis = [{k: v for k, v in r.items() if not k.startswith("_")}
                   for r in resultados]
    melhor = max(publicaveis, key=lambda r: r["macro_f1"]) if publicaveis else None

    return {
        "schema_version": 1,
        "status": "apto_para_regras" if not bloqueios else "bloqueado",
        "protocolo": ("predicoes out-of-fold sobre as particoes canonicas do "
                      "Passo 3; rotulo e a referencia humana revisada; nenhum "
                      "modelo treina no grupo textual que preve"),
        "semente": semente,
        "corpus": {
            "linhas_avaliadas": len(corpus["textos"]),
            "grupos_textuais": len(set(corpus["grupos"])),
            "categorias": len(set(corpus["rotulos"])),
            "dobras": len(set(corpus["dobras"])),
            "linhas_fora_das_particoes": corpus["linhas_fora_das_particoes"],
            "linhas_sem_rotulo": corpus["linhas_sem_rotulo"],
        },
        "ambiente": {
            "python": platform.python_version(),
            "plataforma": platform.platform(),
            "dependencias": _versoes_dependencias(),
        },
        "modelos": publicaveis,
        "melhor_por_macro_f1": melhor["modelo"] if melhor else None,
        "problemas": problemas,
        "bloqueios": bloqueios,
        "_resultados": resultados,
    }


def _versoes_dependencias() -> dict[str, str]:
    versoes: dict[str, str] = {}
    for modulo in ("numpy", "sklearn", "tensorflow"):
        try:
            versoes[modulo] = __import__(modulo).__version__
        except Exception:  # noqa: BLE001
            versoes[modulo] = "indisponivel"
    return versoes


def renderizar_markdown(relatorio: dict[str, Any]) -> str:
    corpus = relatorio["corpus"]
    linhas = [
        "# Retreino canônico dos sete modelos",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.",
        "",
        f"**Estado:** `{relatorio['status']}`  ",
        f"**Gerado em:** {relatorio.get('gerado_em', 'não informado')}  ",
        f"**Melhor macro-F1:** {relatorio['melhor_por_macro_f1'] or 'não determinado'}",
        "",
        "## Protocolo",
        "",
        f"- {relatorio['protocolo']}.",
        f"- Semente: {relatorio['semente']}.",
        f"- Linhas avaliadas: {corpus['linhas_avaliadas']}, "
        f"em {corpus['grupos_textuais']} grupos textuais e {corpus['dobras']} dobras.",
        f"- Categorias: {corpus['categorias']}.",
        f"- Linhas da aba fora das partições canônicas: {corpus['linhas_fora_das_particoes']}.",
        "",
        "## Desempenho por modelo",
        "",
        "| Modelo | Acurácia | Macro-F1 | Acurácia balanceada | Treino (s) | Inferência (s) | Pico de memória (MB) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for m in sorted(relatorio["modelos"], key=lambda r: -r["macro_f1"]):
        linhas.append(
            f"| {m['modelo']} | {m['acuracia']} | {m['macro_f1']} | "
            f"{m['balanced_accuracy']} | {m['tempo_treino_s']} | "
            f"{m['tempo_inferencia_s']} | {m['pico_memoria_mb']} |")
    linhas += [
        "",
        "Os tempos somam as cinco dobras e refletem a máquina do executor; servem "
        "para comparar modelos entre si, não como medida absoluta de custo.",
        "",
        "## Validações",
        "",
        "| Verificação | Ocorrências |",
        "|---|---:|",
    ]
    linhas += [f"| {k.replace('_', ' ')} | {v} |"
               for k, v in relatorio["problemas"].items()]
    amb = relatorio["ambiente"]
    linhas += [
        "",
        "## Proveniência",
        "",
        f"- Python {amb['python']} em {amb['plataforma']}.",
        "- Dependências: "
        + ", ".join(f"{k} {v}" for k, v in amb["dependencias"].items()) + ".",
        "- Partições: `docs/dados/particoes_canonicas_mapa.csv`, Passo 3.",
        "- Predições por registro: `docs/dados/retreino_canonico_predicoes.csv`, com SHA-256 do ID.",
        "- Script: `src/retreinar_modelos_canonicos.py`.",
        "- Nenhuma escrita foi realizada na planilha.",
        "",
    ]
    return "\n".join(linhas)


def escrever_predicoes(caminho: Path, corpus: dict[str, Any],
                       resultados: list[dict[str, Any]]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(["id_sha256", "dobra", "referencia_humana",
                           "modelo", "previsto"])
        for r in resultados:
            for chave, dobra, verdade, previsto in zip(
                    corpus["chaves"], corpus["dobras"], corpus["rotulos"],
                    r["_predicoes"]):
                escritor.writerow([chave, dobra, verdade, r["modelo"], previsto])


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--particoes", type=Path, default=MAPA_PARTICOES_PADRAO)
    p.add_argument("--modelos", default=",".join(MODELOS_PADRAO))
    p.add_argument("--semente", type=int, default=SEMENTE_PADRAO)
    p.add_argument("--json", type=Path, default=SAIDA_JSON_PADRAO)
    p.add_argument("--markdown", type=Path, default=SAIDA_MD_PADRAO)
    p.add_argument("--predicoes", type=Path, default=SAIDA_PRED_PADRAO)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.particoes.exists():
        print(f"Mapa de particoes nao encontrado em {args.particoes}. "
              "Execute o Passo 3 antes deste.", file=sys.stderr)
        return 2
    modelos = [m.strip() for m in args.modelos.split(",") if m.strip()]
    config = json.loads(args.config.read_text(encoding="utf-8"))
    particoes = carregar_particoes(args.particoes)

    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    corpus = preparar_corpus(cgt.ler_registros(sh, config), particoes)
    if len(corpus["textos"]) < 10:
        print("Corpus insuficiente para retreinar.", file=sys.stderr)
        return 2

    relatorio = montar_relatorio(corpus, modelos, semente=args.semente)
    relatorio["gerado_em"] = agora_bahia()
    relatorio["fonte"] = config["aba_principal"]
    relatorio["script_origem"] = "src/retreinar_modelos_canonicos.py"

    escrever_predicoes(args.predicoes, corpus, relatorio["_resultados"])
    publicavel = {k: v for k, v in relatorio.items() if not k.startswith("_")}
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(publicavel, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    args.markdown.write_text(renderizar_markdown(relatorio), encoding="utf-8")
    print(renderizar_markdown(relatorio))
    return 0 if relatorio["status"] == "apto_para_regras" else 2


if __name__ == "__main__":
    raise SystemExit(main())
