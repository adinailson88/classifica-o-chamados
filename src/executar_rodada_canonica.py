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

import construir_grupos_textuais as cgt  # noqa: E402
import custo_computacional_canonico as ccc  # noqa: E402
import retreinar_modelos_canonicos as rmc  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
DADOS = RAIZ / "docs" / "dados"
MAPA_PARTICOES_PADRAO = DADOS / "particoes_canonicas_mapa.csv"
MAPA_GRUPOS_PADRAO = DADOS / "grupos_textuais_mapa.csv"
MANIFESTO_PADRAO = DADOS / "rodada_canonica.json"
SAIDA_HISTORICO_JSON = DADOS / "comparacao_historica.json"
SAIDA_HISTORICO_MD = RAIZ / "docs" / "COMPARACAO_HISTORICA.md"

# Hash do corpus do ARTIGO_CONGELADO (docs/dados/MANIFESTO_ARTIGO_CONGELADO.json).
# Constante fixa, nunca derivada da execucao atual nem lida da planilha: e o
# ponto de comparacao que torna a rodada canonica fail-closed.
HASH_CORPUS_ESPERADO = (
    "1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a")

# Aposentadoria fail-closed da rodada canonica: ver docs/RETREINO_CANONICO.md
# e o achado metodologico do lote 8D-3B. HASH_CORPUS_ESPERADO combina
# id_sha256, grupo textual normalizado e referencia humana, mas nao congela o
# model-input bruto entregue ao Tokenizer da LSTM; por isso ele permanece no
# modulo como registro/defesa historica, sem servir de autorizacao suficiente
# para regenerar os artefatos do ARTIGO_CONGELADO a partir da planilha viva.
MENSAGEM_APOSENTADORIA = (
    "Regeneracao da rodada canonica aposentada: o ARTIGO_CONGELADO nao "
    "possui fingerprint congelado do model-input textual bruto suficiente "
    "para provar identidade exata da entrada da LSTM. A planilha "
    "operacional viva nao pode ser usada para recriar resultados sob a "
    "identidade canonica. Um novo experimento deve ser executado como NOVO "
    "CORTE CIENTIFICO, com nova identidade."
)


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


def validar_hash_corpus(impressao: str, esperado: str = HASH_CORPUS_ESPERADO,
                        saida: Any = sys.stderr) -> bool:
    """Gate fail-closed: bloqueia a rodada se o corpus atual divergir do
    ARTIGO_CONGELADO. Esta e a rodada canonica do artigo congelado, nao um
    novo corte cientifico; um hash diferente nao e aceito nem substitui
    `esperado`, apenas interrompe a execucao.
    """
    if impressao == esperado:
        return True
    print(
        "Corpus divergente do ARTIGO_CONGELADO: rodada canonica interrompida.\n"
        f"hash obtido:   {impressao}\n"
        f"hash esperado: {esperado}\n"
        "A planilha operacional nao corresponde ao artigo congelado; "
        "nenhuma rodada canonica sera executada.",
        file=saida,
    )
    return False


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
    p.add_argument("--sem-custo", action="store_true",
                   help="pula a medicao de custo, que repete o treino na base inteira")
    p.add_argument("--custo-repeticoes", type=int, default=ccc.REPETICOES_PADRAO)
    p.add_argument("--manifesto", type=Path, default=MANIFESTO_PADRAO)
    return p.parse_args()


def main() -> int:
    parse_args()
    print(MENSAGEM_APOSENTADORIA, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
