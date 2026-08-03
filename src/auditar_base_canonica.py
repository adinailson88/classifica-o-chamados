#!/usr/bin/env python3
"""Audita a base e a taxonomia que antecedem a nova execucao experimental.

Ferramenta estritamente READ-ONLY. Le A:Q da aba principal, deriva a referencia
humana somente de M e Q por ``decisao_validada.py`` e produz artefatos
sanitizados. Titulos, descricoes e IDs nao sao publicados; os IDs participam
apenas do hash deterministico.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import conferencia_derivada as cd  # noqa: E402
import decisao_validada as dv  # noqa: E402
import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
SAIDA_JSON_PADRAO = RAIZ / "docs" / "dados" / "auditoria_base_canonica.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "AUDITORIA_BASE_CANONICA.md"


def _sha256_json(objeto: Any) -> str:
    bruto = json.dumps(objeto, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(bruto).hexdigest()


def ler_registros(sh, config: dict[str, Any]) -> list[dict[str, str]]:
    """Le apenas os campos necessarios, localizados por cabecalho."""
    ws = sh.worksheet(config["aba_principal"])
    bloco = ws.get_values("A:Q", value_render_option="UNFORMATTED_VALUE")
    cab = bloco[0] if bloco else []
    c_id = pl.localizar_coluna(cab, ("ID Chamado", "ID"), 1)
    c_cat = pl.localizar_coluna(cab, ("CATEGORIA COMPLETA",), 3)
    c_m = pl.localizar_coluna(cab, ("CONFERENCIA GLPI", "CONFERÊNCIA GLPI"), 13)
    c_q = pl.localizar_coluna(cab, ("CATEGORIA CORRETA MANUAL",), 17)

    def cel(linha: list[Any], c1: int) -> str:
        i = c1 - 1
        return str(linha[i] or "").strip() if len(linha) > i else ""

    registros = []
    for linha in bloco[1:]:
        # Ignora somente linhas totalmente vazias. Linhas parciais precisam ser
        # preservadas para a auditoria apontar a anomalia.
        if not any(str(v or "").strip() for v in linha):
            continue
        registros.append({
            "id": cd.normalizar_id(cel(linha, c_id)),
            "categoria_historica": pl.normalizar_categoria(cel(linha, c_cat)),
            "conferencia_glpi": cel(linha, c_m),
            "categoria_manual": pl.normalizar_categoria(cel(linha, c_q)),
        })
    return registros


def auditar(registros: list[dict[str, str]]) -> dict[str, Any]:
    """Audita registros ja normalizados. Logica pura para testes offline."""
    ids = [r.get("id", "") for r in registros]
    ids_validos = [i for i in ids if i]
    duplicados = sorted(i for i, n in Counter(ids_validos).items() if n > 1)
    cont_hist: Counter[str] = Counter()
    cont_ref: Counter[str] = Counter()
    cont_fonte: Counter[str] = Counter()
    sem_id = sem_historico = sem_referencia = veredito_invalido = conflitos = 0
    pares_hash: list[dict[str, str]] = []

    for r in registros:
        id_chamado = r.get("id", "")
        historico = r.get("categoria_historica", "")
        manual = r.get("categoria_manual", "")
        veredito_bruto = str(r.get("conferencia_glpi", "") or "").strip()
        veredito = cd.norm_veredito(veredito_bruto)
        if not id_chamado:
            sem_id += 1
        if not historico:
            sem_historico += 1
        else:
            cont_hist[historico] += 1
        if veredito_bruto and veredito_bruto.casefold() not in {"correto", "errado"}:
            veredito_invalido += 1

        # A referencia canônica deve passar pela mesma função usada pelos
        # consumidores experimentais. N e P são deliberadamente ignoradas:
        # a revisão final confirmou C em M ou informou a correção em Q.
        decisao = dv.decidir(
            historico, "", "", dv._norm_veredito(veredito_bruto), None, None, manual
        )
        referencia = decisao["decidida"] or ""
        fonte = {
            "conferencia_glpi": cd.FONTE_GLPI,
            "manual": cd.FONTE_MANUAL,
        }.get(decisao["fonte_decisao"], "")
        if decisao["conflito"]:
            conflitos += 1
        if referencia:
            cont_ref[referencia] += 1
            cont_fonte[fonte] += 1
        else:
            sem_referencia += 1
        if id_chamado:
            pares_hash.append({
                "id": id_chamado,
                "historico": historico,
                "referencia": referencia,
                "fonte": fonte,
            })

    cats_hist = set(cont_hist)
    cats_ref = set(cont_ref)
    fora_historica = sorted(cats_ref - cats_hist)
    sem_suporte_ref = sorted(cats_hist - cats_ref)
    problemas = {
        "linhas_sem_id": sem_id,
        "ids_duplicados": len(duplicados),
        "linhas_sem_categoria_historica": sem_historico,
        "vereditos_invalidos": veredito_invalido,
        "conflitos_referencia": conflitos,
        "linhas_sem_referencia": sem_referencia,
        "categorias_referencia_fora_taxonomia_historica": len(fora_historica),
    }
    bloqueios = [nome for nome, n in problemas.items() if n]
    pares_hash.sort(key=lambda x: (x["id"], x["historico"], x["referencia"], x["fonte"]))

    def distribuicao(contagem: Counter[str]) -> list[dict[str, Any]]:
        return [{"categoria": c, "n": n}
                for c, n in sorted(contagem.items(), key=lambda kv: (-kv[1], kv[0]))]

    return {
        "schema_version": 1,
        "status": "apto_para_congelar" if not bloqueios else "bloqueado",
        "regra_referencia": (
            "M='Correto' -> categoria historica; M='Errado' + Q preenchida -> "
            "categoria manual; demais casos sem referencia"),
        "corpus": {
            "linhas_nao_vazias": len(registros),
            "ids_validos": len(ids_validos),
            "ids_unicos": len(set(ids_validos)),
            "referencias_validas": sum(cont_ref.values()),
            "fontes": dict(sorted(cont_fonte.items())),
        },
        "taxonomia_historica": {
            "categorias": len(cont_hist),
            "distribuicao": distribuicao(cont_hist),
            "sha256": _sha256_json(sorted(cont_hist)),
        },
        "taxonomia_referencia": {
            "categorias": len(cont_ref),
            "distribuicao": distribuicao(cont_ref),
            "sha256": _sha256_json(sorted(cont_ref)),
        },
        "reconciliacao": {
            "categorias_referencia_fora_taxonomia_historica": [
                {"categoria": c, "n": cont_ref[c]} for c in fora_historica
            ],
            "categorias_historicas_sem_suporte_na_referencia": [
                {"categoria": c, "n_historico": cont_hist[c]} for c in sem_suporte_ref
            ],
        },
        "problemas": problemas,
        "bloqueios": bloqueios,
        # Nao publica os IDs; registra somente quantidade e hash da lista.
        "ids_duplicados_sha256": _sha256_json(duplicados),
        "hash_base_canonica_sha256": _sha256_json(pares_hash),
        "hash_escopo": "id, categoria historica, referencia humana e fonte; ordenados por id",
    }


def renderizar_markdown(relatorio: dict[str, Any]) -> str:
    corpus = relatorio["corpus"]
    hist = relatorio["taxonomia_historica"]
    ref = relatorio["taxonomia_referencia"]
    extras = relatorio["reconciliacao"]["categorias_referencia_fora_taxonomia_historica"]
    linhas = [
        "# Auditoria da base canônica",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.",
        "",
        f"**Estado:** `{relatorio['status']}`  ",
        f"**Gerado em:** {relatorio.get('gerado_em', 'não informado')}  ",
        f"**Hash da base:** `{relatorio['hash_base_canonica_sha256']}`",
        "",
        "## Totais",
        "",
        "| Item | Total |",
        "|---|---:|",
        f"| Linhas não vazias | {corpus['linhas_nao_vazias']} |",
        f"| IDs válidos | {corpus['ids_validos']} |",
        f"| IDs únicos | {corpus['ids_unicos']} |",
        f"| Referências humanas válidas | {corpus['referencias_validas']} |",
        f"| Categorias históricas | {hist['categorias']} |",
        f"| Categorias com suporte na referência | {ref['categorias']} |",
        "",
        "## Reconciliação da taxonomia",
        "",
    ]
    if extras:
        linhas += [
            "O congelamento permanece bloqueado porque a referência humana contém categorias que não aparecem na taxonomia histórica vigente:",
            "",
            "| Categoria | Suporte na referência |",
            "|---|---:|",
        ]
        linhas += [f"| {e['categoria']} | {e['n']} |" for e in extras]
    else:
        linhas.append("Todas as categorias da referência pertencem à taxonomia histórica.")
    linhas += [
        "",
        "## Validações",
        "",
        "| Verificação | Ocorrências |",
        "|---|---:|",
    ]
    linhas += [f"| {k.replace('_', ' ')} | {v} |"
               for k, v in relatorio["problemas"].items()]
    linhas += [
        "",
        "## Proveniência",
        "",
        f"- Regra: {relatorio['regra_referencia']}.",
        f"- Hash da taxonomia histórica: `{hist['sha256']}`.",
        f"- Hash da taxonomia da referência: `{ref['sha256']}`.",
        f"- Escopo do hash da base: {relatorio['hash_escopo']}.",
        "- Script: `src/auditar_base_canonica.py`.",
        "- Nenhuma escrita foi realizada na planilha.",
        "",
    ]
    return "\n".join(linhas)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--json", type=Path, default=SAIDA_JSON_PADRAO)
    p.add_argument("--markdown", type=Path, default=SAIDA_MD_PADRAO)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    relatorio = auditar(ler_registros(sh, config))
    relatorio["gerado_em"] = agora_bahia()
    relatorio["fonte"] = config["aba_principal"]
    relatorio["script_origem"] = "src/auditar_base_canonica.py"
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    args.markdown.write_text(renderizar_markdown(relatorio), encoding="utf-8")
    print(renderizar_markdown(relatorio))
    return 0 if relatorio["status"] == "apto_para_congelar" else 2


if __name__ == "__main__":
    raise SystemExit(main())
