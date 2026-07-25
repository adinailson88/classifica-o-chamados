#!/usr/bin/env python3
"""Gera a tabela suplementar S1 (metricas por categoria) do artigo.

Fonte primaria: aba viva da planilha experimental identificada por GID
(nao por nome -- o Adinailson so passou a URL com
`gid=1862157493`, o nome da aba nao foi confirmado). Requer credencial de
conta de servico (`credenciais_sa.json` ou `GOOGLE_APPLICATION_CREDENTIALS`)
e `SPREADSHEET_ID`/`spreadsheet_id.local`, como o resto do repo (ver
`src/planilha.py`).

Fallback: se nao houver credencial disponivel na sessao, usa o JSON ja
publicado em `docs/dados/metricas_por_categoria.json` (concordancia vs.
historico -- schema mais pobre, sem precision/recall/F1). O CSV de saida
sempre registra qual fonte foi usada, para nao misturar silenciosamente
dado da planilha viva com dado desatualizado do JSON publico.

Colunas nao sao assumidas por posicao (regra do AGENTS.md): sao
localizadas por cabecalho da primeira linha da aba viva. Como o schema
real dessa aba ainda nao foi confirmado por ninguem com acesso, o script
imprime os cabecalhos encontrados e faz o melhor mapeamento possivel para
["categoria", "support"/"qtd_classificados", "precision", "recall",
"f1"/"f1_score", "concordancia"/"taxa_concordancia"] por nome
normalizado (sem acento, minusculo, "_" no lugar de espaco) -- ajuste
ALIAS_COLUNAS abaixo se os nomes reais da aba forem diferentes.

Uso:
    python src/exportar_tabela_por_categoria.py                # tenta planilha viva, cai para JSON
    python src/exportar_tabela_por_categoria.py --so-json       # forca o fallback (sem credencial)
    python src/exportar_tabela_por_categoria.py --gid 123456    # aba viva com outro GID
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

ENTRADA_JSON = RAIZ / "docs" / "dados" / "metricas_por_categoria.json"
SAIDA = RAIZ / "04_artigo" / "figuras" / "tabela_S1_metricas_por_categoria.csv"

# GID da aba mencionada pelo Adinailson em 24/07/2026:
# https://docs.google.com/spreadsheets/d/1lohPUQOgxzt_DMxnNLKMxnieZq1sVmh4uwBLbbgvfiQ/edit?gid=1862157493
GID_PADRAO = 1862157493

# Mapeamento por nome normalizado (sem acento/maiuscula, "_" no lugar de
# espaco) -> nome de campo canonico usado no CSV de saida. Cobre variantes
# prováveis; ajustar depois de ver os cabecalhos reais impressos em stderr.
ALIAS_COLUNAS = {
    "categoria": "categoria",
    "categoria_completa": "categoria",
    "categoria_historica": "categoria",
    "support": "support",
    "suporte": "support",
    "qtd_classificados": "support",
    "n": "support",
    "precision": "precision",
    "precisao": "precision",
    "recall": "recall",
    "revocacao": "recall",
    "f1": "f1",
    "f1_score": "f1",
    "f1score": "f1",
    "concordancia": "concordancia",
    "taxa_concordancia": "concordancia",
    "acuracia": "concordancia",
}

CAMPOS_SAIDA = ["categoria", "support", "precision", "recall", "f1", "concordancia", "fonte"]


def _normalizar_cabecalho(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = texto.strip().lower()
    texto = re.sub(r"[^a-z0-9]+", "_", texto).strip("_")
    return texto


def carregar_da_planilha(gid: int) -> list[dict] | None:
    """Tenta ler a aba viva por GID. Retorna None se faltar credencial ou
    o GID nao existir -- quem chama decide se cai para o fallback."""
    try:
        import planilha  # src/planilha.py, mesmo padrao do resto do repo
    except ImportError as exc:
        print(f"[planilha] modulo indisponivel: {exc}", file=sys.stderr)
        return None

    try:
        config = {}
        config_path = RAIZ / "config_experimento.json"
        if config_path.exists():
            config = json.loads(config_path.read_text(encoding="utf-8"))
        sid = planilha.id_planilha(config)
        sh = planilha.abrir_planilha(sid)
    except Exception as exc:  # sem credencial, sem SPREADSHEET_ID, sem rede etc.
        print(f"[planilha] nao foi possivel abrir a planilha viva: {exc}", file=sys.stderr)
        return None

    try:
        aba = sh.get_worksheet_by_id(gid)
    except Exception as exc:
        print(f"[planilha] aba com gid={gid} nao encontrada: {exc}", file=sys.stderr)
        return None
    if aba is None:
        print(f"[planilha] aba com gid={gid} nao encontrada (retorno None).", file=sys.stderr)
        return None

    valores = aba.get_all_values()
    if not valores:
        print(f"[planilha] aba '{aba.title}' (gid={gid}) esta vazia.", file=sys.stderr)
        return None

    cabecalho_bruto = valores[0]
    cabecalho_normalizado = [_normalizar_cabecalho(c) for c in cabecalho_bruto]
    print(
        f"[planilha] aba '{aba.title}' (gid={gid}) -- cabecalhos encontrados: "
        f"{cabecalho_bruto}",
        file=sys.stderr,
    )

    mapa_indice = {}
    nao_mapeados = []
    for idx, nome_norm in enumerate(cabecalho_normalizado):
        campo = ALIAS_COLUNAS.get(nome_norm)
        if campo:
            mapa_indice[campo] = idx
        else:
            nao_mapeados.append(cabecalho_bruto[idx])
    if nao_mapeados:
        print(
            f"[planilha] AVISO: colunas nao reconhecidas (ajuste ALIAS_COLUNAS "
            f"se forem relevantes): {nao_mapeados}",
            file=sys.stderr,
        )
    if "categoria" not in mapa_indice:
        print(
            "[planilha] ERRO: nenhuma coluna de categoria reconhecida nesta aba "
            "-- nao da para montar a tabela a partir dela.",
            file=sys.stderr,
        )
        return None

    linhas = []
    for linha in valores[1:]:
        if not any(c.strip() for c in linha if isinstance(c, str)):
            continue  # linha totalmente vazia
        registro = {"fonte": f"planilha:{aba.title}(gid={gid})"}
        for campo in ("categoria", "support", "precision", "recall", "f1", "concordancia"):
            idx = mapa_indice.get(campo)
            registro[campo] = linha[idx] if idx is not None and idx < len(linha) else ""
        linhas.append(registro)
    return linhas


def carregar_do_json_publico() -> list[dict]:
    dados = json.loads(ENTRADA_JSON.read_text(encoding="utf-8"))
    if not isinstance(dados, list):
        raise ValueError(f"Esperava uma lista em {ENTRADA_JSON}, recebi {type(dados)}")
    linhas = []
    for item in dados:
        linhas.append(
            {
                "categoria": item.get("categoria", ""),
                "support": item.get("qtd_classificados", ""),
                "precision": "",
                "recall": "",
                "f1": "",
                "concordancia": item.get("taxa_concordancia", ""),
                "fonte": "docs/dados/metricas_por_categoria.json (concordancia vs. historico; sem precision/recall/F1)",
            }
        )
    return linhas


def exportar(linhas: list[dict]) -> Path:
    def chave_ordenacao(item):
        valor = item.get("concordancia") or item.get("f1") or 0
        try:
            return float(str(valor).replace(",", "."))
        except ValueError:
            return 0.0

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    linhas_ordenadas = sorted(linhas, key=chave_ordenacao)
    with SAIDA.open("w", newline="", encoding="utf-8") as arq:
        escritor = csv.DictWriter(arq, fieldnames=CAMPOS_SAIDA)
        escritor.writeheader()
        for item in linhas_ordenadas:
            escritor.writerow({campo: item.get(campo, "") for campo in CAMPOS_SAIDA})
    return SAIDA


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gid", type=int, default=GID_PADRAO,
                        help="GID da aba viva de metricas por categoria.")
    parser.add_argument("--so-json", action="store_true",
                        help="Ignora a planilha viva e usa so o JSON publico.")
    args = parser.parse_args()

    linhas = None
    if not args.so_json:
        linhas = carregar_da_planilha(args.gid)

    if linhas is None:
        print(
            "[fallback] usando docs/dados/metricas_por_categoria.json "
            "(concordancia vs. historico -- SEM precision/recall/F1). "
            "Rode de novo com credencial de planilha para pegar o schema "
            "completo da aba viva.",
            file=sys.stderr,
        )
        linhas = carregar_do_json_publico()

    caminho = exportar(linhas)
    print(f"Tabela S1 gerada: {caminho.relative_to(RAIZ)} ({len(linhas)} categorias)")
    print(f"Fonte usada: {linhas[0]['fonte'] if linhas else 'nenhuma'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
