#!/usr/bin/env python3
"""Executa os Passos 4, 5 e 7 numa unica rodada, sobre uma unica leitura da aba.

Ferramenta estritamente READ-ONLY. Existe para eliminar uma inconsistencia
estrutural: enquanto cada passo lia a planilha por conta propria, o retreino, a
comparacao com as regras e a calibracao podiam ver conteudos diferentes, porque
a aba e viva. Bastava um texto editado entre duas execucoes para que numeros que
descrevem o mesmo experimento deixassem de fechar entre si.

Aqui a aba e lida UMA vez. O mesmo corpus em memoria alimenta os tres passos, e
todos os artefatos saem carimbados com o mesmo `hash_corpus` e o mesmo instante.
Numeros de rodadas diferentes continuam podendo divergir; numeros da MESMA
rodada nao podem mais.

O plano ja pedia isso ao exigir "uma unica execucao canonica, reproduzivel e
comum a todos os modelos". Este script torna a exigencia verificavel.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import calibrar_confianca as cal  # noqa: E402
import comparar_regras_modelos as crm  # noqa: E402
import construir_grupos_textuais as cgt  # noqa: E402
import planilha as pl  # noqa: E402
import retreinar_modelos_canonicos as rmc  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
DADOS = RAIZ / "docs" / "dados"
MAPA_PARTICOES_PADRAO = DADOS / "particoes_canonicas_mapa.csv"
MAPA_GRUPOS_PADRAO = DADOS / "grupos_textuais_mapa.csv"
MANIFESTO_PADRAO = DADOS / "rodada_canonica.json"


def hash_corpus(corpus: dict[str, Any]) -> str:
    """Identidade do conteudo efetivamente usado nesta rodada.

    Combina, por registro, o SHA-256 do ID, o hash do grupo textual e o rotulo.
    Dois artefatos com o mesmo valor descrevem o mesmo corpus; valores
    diferentes explicam, sem discussao, por que os numeros nao batem.
    """
    itens = sorted(zip(corpus["chaves"], corpus["grupos"], corpus["rotulos"]))
    return cgt._sha256_json([list(i) for i in itens])


def carimbar(relatorio: dict[str, Any], impressao: str, quando: str,
             corpus: dict[str, Any]) -> dict[str, Any]:
    relatorio["hash_corpus"] = impressao
    relatorio["gerado_em"] = quando
    relatorio["rodada_canonica"] = True
    relatorio["linhas_com_texto_alterado_apos_o_congelamento"] = corpus[
        "linhas_com_texto_alterado_apos_o_congelamento"]
    return relatorio


def publicavel(relatorio: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in relatorio.items() if not k.startswith("_")}


def gravar(caminho_json: Path, caminho_md: Path, relatorio: dict[str, Any],
           markdown: str) -> None:
    caminho_json.parent.mkdir(parents=True, exist_ok=True)
    caminho_md.parent.mkdir(parents=True, exist_ok=True)
    caminho_json.write_text(
        json.dumps(publicavel(relatorio), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    caminho_md.write_text(markdown, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--particoes", type=Path, default=MAPA_PARTICOES_PADRAO)
    p.add_argument("--grupos-congelados", type=Path, default=MAPA_GRUPOS_PADRAO)
    p.add_argument("--modelos", default=",".join(rmc.MODELOS_PADRAO))
    p.add_argument("--semente", type=int, default=rmc.SEMENTE_PADRAO)
    p.add_argument("--sem-calibracao", action="store_true",
                   help="pula o Passo 7, que custa cinco ajustes extras por modelo")
    p.add_argument("--manifesto", type=Path, default=MANIFESTO_PADRAO)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.particoes.exists():
        print(f"Mapa de particoes nao encontrado em {args.particoes}.", file=sys.stderr)
        return 2
    modelos = [m.strip() for m in args.modelos.split(",") if m.strip()]
    config = json.loads(args.config.read_text(encoding="utf-8"))

    # ---- leitura unica da aba -------------------------------------------
    particoes = rmc.carregar_particoes(args.particoes)
    congelados = (rmc.carregar_grupos_congelados(args.grupos_congelados)
                  if args.grupos_congelados.exists() else None)
    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    registros = cgt.ler_registros(sh, config)
    corpus = rmc.preparar_corpus(registros, particoes, congelados)
    if len(corpus["textos"]) < 10:
        print("Corpus insuficiente para a rodada.", file=sys.stderr)
        return 2

    impressao = hash_corpus(corpus)
    quando = agora_bahia()
    rmc._log(f"[rodada] corpus com {len(corpus['textos'])} linhas, hash {impressao[:12]}")

    # ---- Passo 4: retreino ----------------------------------------------
    retreino = rmc.montar_relatorio(corpus, modelos, semente=args.semente)
    retreino["fonte"] = config["aba_principal"]
    retreino["script_origem"] = "src/executar_rodada_canonica.py"
    carimbar(retreino, impressao, quando, corpus)
    rmc.escrever_predicoes(rmc.SAIDA_PRED_PADRAO, corpus, retreino["_resultados"])
    gravar(rmc.SAIDA_JSON_PADRAO, rmc.SAIDA_MD_PADRAO, retreino,
           rmc.renderizar_markdown(retreino))

    # As predicoes seguem em memoria: nenhuma releitura da aba entre os passos.
    por_modelo_previsto = {r["modelo"]: dict(zip(corpus["chaves"], r["_predicoes"]))
                           for r in retreino["_resultados"]}
    referencia = dict(zip(corpus["chaves"], corpus["rotulos"]))
    textos = dict(zip(corpus["chaves"], corpus["textos"]))

    # ---- Passo 5: regras contra modelos ---------------------------------
    regras = crm.montar_relatorio(list(corpus["chaves"]), referencia, textos,
                                  por_modelo_previsto)
    regras["script_origem"] = "src/executar_rodada_canonica.py"
    carimbar(regras, impressao, quando, corpus)
    gravar(crm.SAIDA_JSON_PADRAO, crm.SAIDA_MD_PADRAO, regras,
           crm.renderizar_markdown(regras))

    # ---- Passo 7: calibracao --------------------------------------------
    calibracao = None
    if not args.sem_calibracao:
        externas = {
            r["modelo"]: {
                chave: {"acerto": int(previsto == referencia[chave]),
                        "confianca": escore}
                for chave, previsto, escore in zip(
                    corpus["chaves"], r["_predicoes"], r["_escores"])
            }
            for r in retreino["_resultados"]
        }
        calibracao = cal.montar_relatorio(corpus, externas, modelos)
        calibracao["script_origem"] = "src/executar_rodada_canonica.py"
        carimbar(calibracao, impressao, quando, corpus)
        gravar(cal.SAIDA_JSON_PADRAO, cal.SAIDA_MD_PADRAO, calibracao,
               cal.renderizar_markdown(calibracao))

    # ---- manifesto -------------------------------------------------------
    manifesto = {
        "schema_version": 1,
        "gerado_em": quando,
        "hash_corpus": impressao,
        "fonte": config["aba_principal"],
        "semente": args.semente,
        "modelos": modelos,
        "corpus": {
            "linhas": len(corpus["textos"]),
            "grupos_textuais": len(set(corpus["grupos"])),
            "categorias": len(set(corpus["rotulos"])),
            "dobras": len(set(corpus["dobras"])),
            "linhas_fora_das_particoes": corpus["linhas_fora_das_particoes"],
            "linhas_com_texto_alterado_apos_o_congelamento":
                corpus["linhas_com_texto_alterado_apos_o_congelamento"],
        },
        "passos": {
            "4_retreino": {"status": retreino["status"],
                           "arquivo": "docs/dados/retreino_canonico.json"},
            "5_regras": {"status": regras["status"],
                         "arquivo": "docs/dados/regras_versus_modelos.json"},
            "7_calibracao": ({"status": calibracao["status"],
                              "arquivo": "docs/dados/calibracao_canonica.json"}
                             if calibracao else {"status": "nao_executado"}),
        },
        "garantia": ("os tres passos usaram a mesma leitura da aba e o mesmo "
                     "corpus em memoria; artefatos com hash_corpus igual sao "
                     "mutuamente consistentes"),
    }
    args.manifesto.parent.mkdir(parents=True, exist_ok=True)
    args.manifesto.write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifesto, ensure_ascii=False, indent=2))
    return 0 if retreino["status"] == "apto_para_regras" else 2


if __name__ == "__main__":
    raise SystemExit(main())
