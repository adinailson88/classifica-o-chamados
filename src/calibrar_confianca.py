#!/usr/bin/env python3
"""Calibra a confianca e mede a automacao seletiva, sob o Passo 7 do plano.

Ferramenta estritamente READ-ONLY. O criterio de aceite do passo e severo:
"nenhum dado de teste influencia calibracao ou escolha do limiar". Por isso o
desenho usa uma DOBRA INTERNA de calibracao.

Para cada dobra externa `f`:

  1. escolhe deterministicamente uma dobra interna `c`, com `c != f`;
  2. treina o modelo nas dobras que nao sao `f` nem `c`;
  3. prediz `c` e usa esses pares (escore, acerto) para ajustar o calibrador e
     escolher o limiar de automacao;
  4. aplica calibrador e limiar aos escores *out-of-fold* de `f`, produzidos no
     Passo 4 por um modelo que nunca viu `f`.

Nenhuma etapa olha para `f` antes de avalia-la. A contrapartida, registrada no
relatorio, e que o calibrador e ajustado sobre escores de um modelo treinado em
tres dobras e aplicado a escores de um modelo treinado em quatro; e a troca
usual entre ausencia de vazamento e casamento exato de distribuicao.

DEFINICOES. O ECE e o Expected Calibration Error com particao em faixas de
largura igual: a media, ponderada pelo numero de registros, do modulo da
diferenca entre acuracia e confianca media dentro de cada faixa. A metrica
complementar e o escore de Brier na formulacao binaria acerto/erro, que pune
tanto ma calibracao quanto baixa resolucao.

As saidas sao sanitizadas: nao publicam titulos, descricoes nem IDs.
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

import construir_grupos_textuais as cgt  # noqa: E402
import modelos_zoo as zoo  # noqa: E402
import planilha as pl  # noqa: E402
import retreinar_modelos_canonicos as rmc  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
MAPA_PARTICOES_PADRAO = RAIZ / "docs" / "dados" / "particoes_canonicas_mapa.csv"
PREDICOES_PADRAO = RAIZ / "docs" / "dados" / "retreino_canonico_predicoes.csv"
SAIDA_JSON_PADRAO = RAIZ / "docs" / "dados" / "calibracao_canonica.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "CALIBRACAO_CANONICA.md"

FAIXAS_PADRAO = 10
# Alvos de acuracia entre os automatizados. O limiar e o menor escore que
# atinge o alvo na dobra interna; se nenhum atingir, a configuracao e
# reportada como inalcancavel em vez de silenciosamente omitida.
ALVOS_PADRAO = (0.90, 0.95, 0.99)


def dobra_interna(f: int, dobras: list[int]) -> int:
    """Escolhe a dobra de calibracao de forma deterministica e sem sorteio."""
    ordenadas = sorted(set(dobras))
    pos = ordenadas.index(f)
    return ordenadas[(pos + 1) % len(ordenadas)]


def ece(confiancas: list[float], acertos: list[int],
        faixas: int = FAIXAS_PADRAO) -> dict[str, Any]:
    """Expected Calibration Error com faixas de largura igual."""
    n = len(confiancas)
    if not n:
        return {"ece": 0.0, "faixas": []}
    detalhe = []
    soma = 0.0
    for i in range(faixas):
        inicio, fim = i / faixas, (i + 1) / faixas
        # A ultima faixa inclui o limite superior, para que confianca 1,0 nao
        # fique de fora de todas as faixas.
        dentro = [j for j, c in enumerate(confiancas)
                  if (inicio <= c < fim) or (i == faixas - 1 and c == 1.0)]
        if not dentro:
            detalhe.append({"faixa": f"[{inicio:.1f}, {fim:.1f})", "n": 0,
                            "confianca_media": None, "acuracia": None})
            continue
        conf_media = sum(confiancas[j] for j in dentro) / len(dentro)
        acuracia = sum(acertos[j] for j in dentro) / len(dentro)
        soma += (len(dentro) / n) * abs(acuracia - conf_media)
        detalhe.append({"faixa": f"[{inicio:.1f}, {fim:.1f})", "n": len(dentro),
                        "confianca_media": round(conf_media, 4),
                        "acuracia": round(acuracia, 4)})
    return {"ece": round(soma, 4), "faixas": detalhe}


def brier(confiancas: list[float], acertos: list[int]) -> float:
    """Escore de Brier na formulacao binaria acerto/erro."""
    if not confiancas:
        return 0.0
    return round(sum((c - a) ** 2 for c, a in zip(confiancas, acertos))
                 / len(confiancas), 4)


def ajustar_isotonica(confiancas: list[float], acertos: list[int]):
    """Regressao isotonica ajustada SOMENTE na dobra interna de calibracao."""
    from sklearn.isotonic import IsotonicRegression
    if len(set(acertos)) < 2:
        return None
    modelo = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
    modelo.fit(confiancas, acertos)
    return modelo


def escolher_limiar(confiancas: list[float], acertos: list[int],
                    alvo: float) -> dict[str, Any]:
    """Menor limiar que atinge o alvo de acuracia na dobra interna."""
    candidatos = sorted(set(round(c, 3) for c in confiancas))
    for limiar in candidatos:
        sel = [i for i, c in enumerate(confiancas) if c >= limiar]
        if not sel:
            continue
        acuracia = sum(acertos[i] for i in sel) / len(sel)
        if acuracia >= alvo:
            return {"alvo": alvo, "limiar": limiar, "alcancavel": True,
                    "cobertura_na_calibracao": round(len(sel) / len(confiancas), 4),
                    "acuracia_na_calibracao": round(acuracia, 4)}
    return {"alvo": alvo, "limiar": None, "alcancavel": False,
            "cobertura_na_calibracao": 0.0, "acuracia_na_calibracao": None}


def aplicar_limiar(confiancas: list[float], acertos: list[int],
                   limiar: float | None) -> dict[str, Any]:
    """Cobertura, acuracia seletiva e encaminhamento humano na dobra externa."""
    n = len(confiancas)
    if not n or limiar is None:
        return {"cobertura": 0.0, "acuracia_seletiva": None,
                "taxa_encaminhamento_humano": 1.0, "automatizados": 0}
    auto = [i for i, c in enumerate(confiancas) if c >= limiar]
    return {
        "cobertura": round(len(auto) / n, 4),
        "acuracia_seletiva": (round(sum(acertos[i] for i in auto) / len(auto), 4)
                              if auto else None),
        "taxa_encaminhamento_humano": round(1 - len(auto) / n, 4),
        "automatizados": len(auto),
    }


def carregar_predicoes(caminho: Path) -> dict[str, Any]:
    """Predicoes do Passo 4, com confianca, agrupadas por modelo."""
    dobra: dict[str, int] = {}
    por_modelo: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    with caminho.open("r", encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f)
        if "confianca" not in (leitor.fieldnames or []):
            raise ValueError(
                "CSV de predicoes sem a coluna 'confianca'; reexecute o Passo 4.")
        for linha in leitor:
            chave = linha["id_sha256"]
            dobra[chave] = int(linha["dobra"])
            por_modelo[linha["modelo"]][chave] = {
                "acerto": int(linha["previsto"] == linha["referencia_humana"]),
                "confianca": float(linha["confianca"]),
            }
    return {"dobra": dobra, "por_modelo": dict(por_modelo)}


def calibrar_modelo(nome: str, corpus: dict[str, Any],
                    externas: dict[str, dict[str, Any]],
                    alvos: tuple[float, ...] = ALVOS_PADRAO,
                    faixas: int = FAIXAS_PADRAO,
                    registrar=rmc._log) -> dict[str, Any]:
    """Calibra e mede automacao seletiva, dobra externa por dobra externa."""
    dobras = corpus["dobras"]
    chaves = corpus["chaves"]
    conf_bruta: list[float] = []
    conf_calibrada: list[float] = []
    acertos: list[int] = []
    por_alvo: dict[float, list[dict[str, Any]]] = defaultdict(list)
    detalhe_dobras = []

    for f in sorted(set(dobras)):
        c = dobra_interna(f, dobras)
        treino = [i for i, d in enumerate(dobras) if d not in (f, c)]
        interna = [i for i, d in enumerate(dobras) if d == c]
        externa = [i for i, d in enumerate(dobras) if d == f]

        modelo = zoo.criar_modelo(nome)
        modelo.fit([corpus["textos"][i] for i in treino],
                   [corpus["rotulos"][i] for i in treino])
        prev, escore = modelo.predict_score([corpus["textos"][i] for i in interna])
        conf_int = [float(s) for s in escore]
        ac_int = [int(str(prev[j]) == corpus["rotulos"][i])
                  for j, i in enumerate(interna)]
        registrar(f"[calibracao] {nome}: dobra externa {f}, interna {c} "
                  f"({len(treino)} treino / {len(interna)} calibracao)")

        calibrador = ajustar_isotonica(conf_int, ac_int)
        limiares = {alvo: escolher_limiar(conf_int, ac_int, alvo) for alvo in alvos}

        # A dobra externa so e tocada agora, ja com calibrador e limiar fixados.
        conf_ext = [externas[chaves[i]]["confianca"] for i in externa]
        ac_ext = [externas[chaves[i]]["acerto"] for i in externa]
        cal_ext = ([float(v) for v in calibrador.predict(conf_ext)]
                   if calibrador is not None else list(conf_ext))

        conf_bruta.extend(conf_ext)
        conf_calibrada.extend(cal_ext)
        acertos.extend(ac_ext)
        for alvo, escolha in limiares.items():
            por_alvo[alvo].append(
                {"dobra": f, **escolha,
                 **aplicar_limiar(conf_ext, ac_ext, escolha["limiar"])})
        detalhe_dobras.append({
            "dobra_externa": f, "dobra_interna": c,
            "linhas_treino": len(treino), "linhas_calibracao": len(interna),
            "linhas_avaliadas": len(externa),
            "calibrador_ajustado": calibrador is not None,
        })

    def consolidar(registros: list[dict[str, Any]]) -> dict[str, Any]:
        auto = sum(r["automatizados"] for r in registros)
        # Media ponderada pelo numero de automatizados de cada dobra; a media
        # simples das acuracias daria peso igual a dobras de tamanhos distintos.
        acertos_auto = sum((r["acuracia_seletiva"] or 0) * r["automatizados"]
                           for r in registros)
        return {
            "dobras_com_limiar": sum(1 for r in registros if r["alcancavel"]),
            "automatizados": auto,
            "cobertura": round(auto / len(acertos), 4) if acertos else 0.0,
            "acuracia_seletiva": round(acertos_auto / auto, 4) if auto else None,
            "taxa_encaminhamento_humano": (
                round(1 - auto / len(acertos), 4) if acertos else 1.0),
            "limiares_por_dobra": [r["limiar"] for r in registros],
        }

    return {
        "modelo": nome,
        "acuracia_global": round(sum(acertos) / len(acertos), 4) if acertos else 0.0,
        "bruta": {"ece": ece(conf_bruta, acertos, faixas)["ece"],
                  "brier": brier(conf_bruta, acertos),
                  "confiabilidade": ece(conf_bruta, acertos, faixas)["faixas"]},
        "calibrada": {"ece": ece(conf_calibrada, acertos, faixas)["ece"],
                      "brier": brier(conf_calibrada, acertos),
                      "confiabilidade": ece(conf_calibrada, acertos, faixas)["faixas"]},
        "automacao_seletiva": {str(alvo): consolidar(regs)
                               for alvo, regs in sorted(por_alvo.items())},
        "dobras": detalhe_dobras,
    }


def montar_relatorio(corpus: dict[str, Any], externas_por_modelo: dict[str, Any],
                     modelos: list[str], alvos: tuple[float, ...] = ALVOS_PADRAO,
                     faixas: int = FAIXAS_PADRAO,
                     registrar=rmc._log) -> dict[str, Any]:
    resultados = [calibrar_modelo(nome, corpus, externas_por_modelo[nome],
                                  alvos, faixas, registrar)
                  for nome in modelos if nome in externas_por_modelo]
    melhoram = [r["modelo"] for r in resultados
                if r["calibrada"]["ece"] < r["bruta"]["ece"]]
    return {
        "schema_version": 1,
        "status": "concluido",
        "protocolo": (
            "dobra interna de calibracao: para cada dobra externa f, o modelo e "
            "treinado nas dobras que nao sao f nem a interna c, o calibrador e o "
            "limiar sao ajustados em c, e so entao f e avaliada"),
        "garantia_de_aceite": (
            "nenhum registro da dobra externa participa do ajuste do calibrador "
            "nem da escolha do limiar"),
        "ressalva": (
            "o calibrador e ajustado sobre escores de um modelo treinado em tres "
            "dobras e aplicado a escores de um modelo treinado em quatro; e a "
            "troca entre ausencia de vazamento e casamento exato de distribuicao"),
        "definicoes": {
            "ece": ("Expected Calibration Error com faixas de largura igual: "
                    f"media ponderada, sobre {faixas} faixas, do modulo da "
                    "diferenca entre acuracia e confianca media da faixa"),
            "brier": ("escore de Brier binario acerto/erro; pune ma calibracao "
                      "e baixa resolucao ao mesmo tempo"),
            "limiar": ("menor escore que atinge o alvo de acuracia na dobra "
                       "interna de calibracao"),
        },
        "corpus": {
            "registros": len(corpus["chaves"]),
            "dobras": len(set(corpus["dobras"])),
            "categorias": len(set(corpus["rotulos"])),
        },
        "alvos_de_acuracia": list(alvos),
        "modelos": resultados,
        "modelos_com_ece_melhorado": melhoram,
    }


def renderizar_markdown(relatorio: dict[str, Any]) -> str:
    c = relatorio["corpus"]
    linhas = [
        "# Calibração e automação seletiva por confiança",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.",
        "",
        f"**Gerado em:** {relatorio.get('gerado_em', 'não informado')}",
        "",
        "## Protocolo",
        "",
        f"- {relatorio['protocolo']}.",
        f"- Garantia: {relatorio['garantia_de_aceite']}.",
        f"- Ressalva: {relatorio['ressalva']}.",
        f"- Registros: {c['registros']}, em {c['dobras']} dobras e {c['categorias']} categorias.",
        "",
        "## Definições",
        "",
        f"- ECE: {relatorio['definicoes']['ece']}.",
        f"- Brier: {relatorio['definicoes']['brier']}.",
        f"- Limiar: {relatorio['definicoes']['limiar']}.",
        "",
        "## Calibração",
        "",
        "| Modelo | Acurácia | ECE bruto | ECE calibrado | Brier bruto | Brier calibrado |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in sorted(relatorio["modelos"], key=lambda x: x["calibrada"]["ece"]):
        linhas.append(
            f"| {r['modelo']} | {r['acuracia_global']} | {r['bruta']['ece']} | "
            f"{r['calibrada']['ece']} | {r['bruta']['brier']} | "
            f"{r['calibrada']['brier']} |")

    linhas += ["", "## Automação seletiva", ""]
    for alvo in relatorio["alvos_de_acuracia"]:
        linhas += [
            f"### Alvo de acurácia {alvo}",
            "",
            "| Modelo | Dobras com limiar | Cobertura | Acurácia seletiva | Encaminhamento humano |",
            "|---|---:|---:|---:|---:|",
        ]
        for r in sorted(relatorio["modelos"], key=lambda x: x["modelo"]):
            a = r["automacao_seletiva"].get(str(alvo), {})
            linhas.append(
                f"| {r['modelo']} | {a.get('dobras_com_limiar', 0)}/{len(r['dobras'])} | "
                f"{a.get('cobertura', 0.0)} | {a.get('acuracia_seletiva')} | "
                f"{a.get('taxa_encaminhamento_humano', 1.0)} |")
        linhas.append("")

    linhas += [
        "## Curva de confiabilidade do melhor modelo calibrado",
        "",
    ]
    melhor = min(relatorio["modelos"], key=lambda x: x["calibrada"]["ece"]) \
        if relatorio["modelos"] else None
    if melhor:
        linhas += [
            f"Modelo `{melhor['modelo']}`, após calibração.",
            "",
            "| Faixa | Registros | Confiança média | Acurácia |",
            "|---|---:|---:|---:|",
        ]
        linhas += [f"| {f['faixa']} | {f['n']} | {f['confianca_media']} | {f['acuracia']} |"
                   for f in melhor["calibrada"]["confiabilidade"]]

    linhas += [
        "",
        "## Proveniência",
        "",
        "- Escores externos: `docs/dados/retreino_canonico_predicoes.csv`, Passo 4.",
        "- Partições: `docs/dados/particoes_canonicas_mapa.csv`, Passo 3.",
        "- Script: `src/calibrar_confianca.py`.",
        "- Nenhuma escrita foi realizada na planilha.",
        "",
    ]
    return "\n".join(linhas)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--particoes", type=Path, default=MAPA_PARTICOES_PADRAO)
    p.add_argument("--predicoes", type=Path, default=PREDICOES_PADRAO)
    p.add_argument("--modelos", default="")
    p.add_argument("--faixas", type=int, default=FAIXAS_PADRAO)
    p.add_argument("--json", type=Path, default=SAIDA_JSON_PADRAO)
    p.add_argument("--markdown", type=Path, default=SAIDA_MD_PADRAO)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    for caminho, passo in ((args.particoes, "3"), (args.predicoes, "4")):
        if not caminho.exists():
            print(f"Arquivo do Passo {passo} nao encontrado em {caminho}.",
                  file=sys.stderr)
            return 2
    config = json.loads(args.config.read_text(encoding="utf-8"))
    dados = carregar_predicoes(args.predicoes)
    modelos = ([m.strip() for m in args.modelos.split(",") if m.strip()]
               or sorted(dados["por_modelo"]))

    particoes = rmc.carregar_particoes(args.particoes)
    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    corpus = rmc.preparar_corpus(cgt.ler_registros(sh, config), particoes)

    relatorio = montar_relatorio(corpus, dados["por_modelo"], modelos,
                                 faixas=args.faixas)
    relatorio["gerado_em"] = agora_bahia()
    relatorio["script_origem"] = "src/calibrar_confianca.py"
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    args.markdown.write_text(renderizar_markdown(relatorio), encoding="utf-8")
    print(renderizar_markdown(relatorio))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
