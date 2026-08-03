#!/usr/bin/env python3
"""Constroi os grupos textuais que impedem vazamento entre chamados duplicados.

Ferramenta estritamente READ-ONLY. Le A:Q da aba principal, normaliza os quatro
campos textuais consumidos pelos modelos (B, D, E, F), agrupa registros cujo
conteudo normalizado e identico e diagnostica quase duplicados sem agrupa-los
automaticamente. O agrupamento automatico e restrito a identidade exata; a
similaridade entra apenas como diagnostico com teste de sensibilidade, conforme
o Passo 2 de PLANO_EXECUCAO_ATUAL.md.

As saidas sao sanitizadas: nao publicam titulos, descricoes nem IDs de chamados.
O mapa por registro usa o SHA-256 do ID, que o Passo 3 recalcula a partir da
mesma planilha para reconstruir a juncao.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import conferencia_derivada as cd  # noqa: E402
import decisao_validada as dv  # noqa: E402
import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
SAIDA_JSON_PADRAO = RAIZ / "docs" / "dados" / "grupos_textuais.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "GRUPOS_TEXTUAIS.md"
SAIDA_MAPA_PADRAO = RAIZ / "docs" / "dados" / "grupos_textuais_mapa.csv"

CAMPOS_TEXTUAIS = ("titulo", "descricao_glpi", "titulo_osm", "descricao_osm")

# Limiares avaliados no teste de sensibilidade dos quase duplicados. Nenhum
# deles agrupa registros; servem para dimensionar o efeito de uma eventual
# fusao por similaridade antes que ela seja proposta.
LIMIARES_SENSIBILIDADE = (0.80, 0.85, 0.90, 0.95)

# Teto de vizinhos por grupo na busca de quase duplicados. Mantem o custo
# linear e e reportado no relatorio para que a cobertura nao pareca total.
VIZINHOS_POR_GRUPO = 5


def _sha256_json(objeto: Any) -> str:
    bruto = json.dumps(objeto, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(bruto).hexdigest()


def normalizar_texto(texto: str) -> str:
    """Mesma normalizacao de `ablation_lstm.py` e `comparacao_kfold_groupkfold.py`.

    Manter a funcao identica e deliberado: os grupos deste passo precisam ser
    comparaveis com a medida de duplicacao ja reportada no artigo.
    """
    sem_acento = unicodedata.normalize("NFKD", str(texto or ""))
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acento.casefold()).strip()


def hash_grupo(campos_normalizados: list[str]) -> str:
    """Hash dos quatro campos separados, nao do texto concatenado.

    A separacao evita colidir registros que so coincidem depois da juncao, como
    titulo vazio com descricao 'a b' contra titulo 'a' com descricao 'b'.
    """
    return _sha256_json(campos_normalizados)


def ler_registros(sh, config: dict[str, Any]) -> list[dict[str, str]]:
    """Le apenas os campos necessarios, localizados por cabecalho."""
    ws = sh.worksheet(config["aba_principal"])
    bloco = ws.get_values("A:Q", value_render_option="UNFORMATTED_VALUE")
    cab = bloco[0] if bloco else []
    c_id = pl.localizar_coluna(cab, ("ID Chamado", "ID"), 1)
    c_tit = pl.localizar_coluna(cab, ("TÍTULO", "TITULO"), 2)
    c_cat = pl.localizar_coluna(cab, ("CATEGORIA COMPLETA",), 3)
    c_desc = pl.localizar_coluna(cab, ("DESCRIÇÃO GLPI", "DESCRICAO GLPI"), 4)
    c_tit_osm = pl.localizar_coluna(cab, ("TÍTULO O.S.M.", "TITULO O.S.M."), 5)
    c_desc_osm = pl.localizar_coluna(cab, ("DESCRIÇÃO O.S.M.", "DESCRICAO O.S.M."), 6)
    c_m = pl.localizar_coluna(cab, ("CONFERENCIA GLPI", "CONFERÊNCIA GLPI"), 13)
    c_q = pl.localizar_coluna(cab, ("CATEGORIA CORRETA MANUAL",), 17)

    def cel(linha: list[Any], c1: int) -> str:
        i = c1 - 1
        return str(linha[i] or "").strip() if len(linha) > i else ""

    registros = []
    for linha in bloco[1:]:
        if not any(str(v or "").strip() for v in linha):
            continue
        registros.append({
            "id": cd.normalizar_id(cel(linha, c_id)),
            "titulo": cel(linha, c_tit),
            "descricao_glpi": cel(linha, c_desc),
            "titulo_osm": cel(linha, c_tit_osm),
            "descricao_osm": cel(linha, c_desc_osm),
            "categoria_historica": pl.normalizar_categoria(cel(linha, c_cat)),
            "conferencia_glpi": cel(linha, c_m),
            "categoria_manual": pl.normalizar_categoria(cel(linha, c_q)),
        })
    return registros


def referencia_humana(registro: dict[str, str]) -> str:
    """Reaplica a regra congelada no Passo 1: M='Correto' -> C; M='Errado' -> Q."""
    decisao = dv.decidir(
        registro.get("categoria_historica", ""), "", "",
        dv._norm_veredito(str(registro.get("conferencia_glpi", "") or "").strip()),
        None, None, registro.get("categoria_manual", ""),
    )
    return decisao["decidida"] or ""


def agrupar(registros: list[dict[str, str]]) -> dict[str, Any]:
    """Agrupa por identidade exata dos quatro campos normalizados.

    Logica pura, sem rede, para permitir teste offline.
    """
    membros: dict[str, list[int]] = defaultdict(list)
    texto_por_grupo: dict[str, str] = {}
    mapa: list[dict[str, str]] = []
    sem_id = sem_texto = 0

    for pos, r in enumerate(registros):
        normalizados = [normalizar_texto(r.get(c, "")) for c in CAMPOS_TEXTUAIS]
        grupo = hash_grupo(normalizados)
        membros[grupo].append(pos)
        texto_por_grupo.setdefault(grupo, " ".join(p for p in normalizados if p))
        if not any(normalizados):
            sem_texto += 1
        id_chamado = r.get("id", "")
        if not id_chamado:
            sem_id += 1
            continue
        mapa.append({
            "id_sha256": hashlib.sha256(id_chamado.encode("utf-8")).hexdigest(),
            "grupo_sha256": grupo,
        })

    tamanhos = Counter(len(v) for v in membros.values())
    maior = max(tamanhos) if tamanhos else 0
    n_linhas = len(registros)
    linhas_duplicadas = sum(len(v) for v in membros.values() if len(v) > 1)

    # Um grupo maior que uma dobra nao cabe integralmente em nenhuma delas e
    # forcaria o Passo 3 a desbalancear o particionamento. E o unico
    # impedimento estrutural detectavel antes de particionar. O teto usa o teto
    # inteiro de n/k, e nao a media exata, para que grupos unitarios sempre
    # caibam em bases pequenas.
    limite_dobra = math.ceil(n_linhas / 5) if n_linhas else 0
    grupos_grandes = sum(1 for v in membros.values() if len(v) > limite_dobra)

    # Grupos com texto identico e referencia humana divergente formam um piso
    # de erro irredutivel: nenhum modelo consegue separa-los.
    rotulos_por_grupo: dict[str, set[str]] = defaultdict(set)
    for grupo, posicoes in membros.items():
        for pos in posicoes:
            ref = referencia_humana(registros[pos])
            if ref:
                rotulos_por_grupo[grupo].add(ref)
    ambiguos = {g: r for g, r in rotulos_por_grupo.items() if len(r) > 1}
    linhas_ambiguas = sum(len(membros[g]) for g in ambiguos)

    mapa.sort(key=lambda x: (x["id_sha256"], x["grupo_sha256"]))
    distribuicao = [{"tamanho": t, "grupos": n}
                    for t, n in sorted(tamanhos.items())]

    return {
        "schema_version": 1,
        "criterio_agrupamento": (
            "identidade exata do SHA-256 dos quatro campos normalizados "
            "(titulo, descricao GLPI, titulo O.S.M., descricao O.S.M.), "
            "separados e nao concatenados"),
        "normalizacao": (
            "NFKD, remocao de diacriticos, casefold e colapso de espacos; "
            "identica a ablation_lstm.py e comparacao_kfold_groupkfold.py"),
        "corpus": {
            "linhas_nao_vazias": n_linhas,
            "linhas_sem_id": sem_id,
            "linhas_sem_texto_em_todos_os_campos": sem_texto,
            "grupos_textuais": len(membros),
            "grupos_unitarios": tamanhos.get(1, 0),
            "linhas_com_duplicata": linhas_duplicadas,
            "proporcao_linhas_com_duplicata": (
                round(linhas_duplicadas / n_linhas, 4) if n_linhas else None),
            "maior_grupo": maior,
        },
        "distribuicao_tamanhos": distribuicao,
        "particionamento": {
            "limite_por_dobra_k5": limite_dobra,
            "grupos_maiores_que_uma_dobra": grupos_grandes,
        },
        "rotulos_conflitantes": {
            "grupos_com_referencia_divergente": len(ambiguos),
            "linhas_afetadas": linhas_ambiguas,
            "nota": ("texto identico com referencia humana diferente; limita o "
                     "teto de acuracia e nao e corrigido por este passo"),
        },
        "mapa_sha256": _sha256_json(mapa),
        "hash_grupos_sha256": _sha256_json(sorted(membros)),
        "_mapa": mapa,
        "_textos_por_grupo": texto_por_grupo,
    }


def diagnosticar_quase_duplicados(
    textos_por_grupo: dict[str, str],
    limiares: tuple[float, ...] = LIMIARES_SENSIBILIDADE,
    vizinhos: int = VIZINHOS_POR_GRUPO,
) -> dict[str, Any]:
    """Mede quase duplicados entre grupos distintos, sem fundi-los.

    Usa TF-IDF de caracteres e cosseno. O resultado alimenta apenas o teste de
    sensibilidade: nenhum limiar e adotado aqui.
    """
    chaves = sorted(k for k, v in textos_por_grupo.items() if v)
    if len(chaves) < 2:
        return {"executado": False, "motivo": "menos de dois grupos com texto"}
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.neighbors import NearestNeighbors
    except ImportError:
        return {"executado": False, "motivo": "scikit-learn indisponivel"}

    corpus = [textos_por_grupo[k] for k in chaves]
    # min_df=1: descartar n-gramas raros apagaria justamente o que distingue
    # chamados quase identicos e inflaria a similaridade medida.
    matriz = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 4),
                             min_df=1, max_features=200_000).fit_transform(corpus)
    k = min(vizinhos + 1, len(chaves))
    modelo = NearestNeighbors(n_neighbors=k, metric="cosine", algorithm="brute")
    modelo.fit(matriz)
    distancias, indices = modelo.kneighbors(matriz)

    # Guarda a maior similaridade de cada grupo contra qualquer outro grupo.
    melhor: list[float] = []
    for i in range(len(chaves)):
        sims = [1.0 - float(d) for d, j in zip(distancias[i], indices[i]) if j != i]
        melhor.append(max(sims) if sims else 0.0)

    sensibilidade = []
    for limiar in limiares:
        atingidos = [i for i, s in enumerate(melhor) if s >= limiar]
        sensibilidade.append({
            "limiar": limiar,
            "grupos_com_par_acima_do_limiar": len(atingidos),
            "proporcao_dos_grupos": round(len(atingidos) / len(chaves), 4),
        })

    return {
        "executado": True,
        "grupos_avaliados": len(chaves),
        "vizinhos_por_grupo": k - 1,
        "cobertura": ("busca dos %d vizinhos mais proximos por grupo; pares alem "
                      "desse teto nao sao contados" % (k - 1)),
        "representacao": "TF-IDF char_wb 3-4 gramas, similaridade de cosseno",
        "similaridade_maxima_mediana": round(
            sorted(melhor)[len(melhor) // 2], 4) if melhor else None,
        "teste_de_sensibilidade": sensibilidade,
        "decisao": ("nenhum limiar adotado; o agrupamento permanece restrito a "
                    "identidade exata ate que um limiar seja justificado"),
    }


def renderizar_markdown(relatorio: dict[str, Any]) -> str:
    corpus = relatorio["corpus"]
    part = relatorio["particionamento"]
    conflito = relatorio["rotulos_conflitantes"]
    quase = relatorio.get("quase_duplicados", {})
    linhas = [
        "# Grupos textuais do experimento",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.",
        "",
        f"**Estado:** `{relatorio['status']}`  ",
        f"**Gerado em:** {relatorio.get('gerado_em', 'não informado')}  ",
        f"**Hash do mapa por registro:** `{relatorio['mapa_sha256']}`",
        "",
        "## Totais",
        "",
        "| Item | Total |",
        "|---|---:|",
        f"| Linhas não vazias | {corpus['linhas_nao_vazias']} |",
        f"| Grupos textuais | {corpus['grupos_textuais']} |",
        f"| Grupos unitários | {corpus['grupos_unitarios']} |",
        f"| Linhas com duplicata | {corpus['linhas_com_duplicata']} |",
        f"| Proporção de linhas com duplicata | {corpus['proporcao_linhas_com_duplicata']} |",
        f"| Maior grupo | {corpus['maior_grupo']} |",
        f"| Linhas sem texto em todos os campos | {corpus['linhas_sem_texto_em_todos_os_campos']} |",
        "",
        "## Viabilidade do particionamento",
        "",
        f"- Limite por dobra com k=5: {part['limite_por_dobra_k5']} linhas.",
        f"- Grupos maiores que uma dobra: {part['grupos_maiores_que_uma_dobra']}.",
        f"- Grupos com referência humana divergente: {conflito['grupos_com_referencia_divergente']} "
        f"({conflito['linhas_afetadas']} linhas).",
        "",
        "## Quase duplicados",
        "",
    ]
    if quase.get("executado"):
        linhas += [
            f"Diagnóstico sobre {quase['grupos_avaliados']} grupos, {quase['representacao']}. "
            f"{quase['cobertura'].capitalize()}.",
            "",
            "| Limiar | Grupos acima | Proporção |",
            "|---:|---:|---:|",
        ]
        linhas += [f"| {s['limiar']} | {s['grupos_com_par_acima_do_limiar']} | {s['proporcao_dos_grupos']} |"
                   for s in quase["teste_de_sensibilidade"]]
        linhas += ["", quase["decisao"].capitalize() + "."]
    else:
        linhas.append(f"Não executado: {quase.get('motivo', 'sem informação')}.")
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
        f"- Critério de agrupamento: {relatorio['criterio_agrupamento']}.",
        f"- Normalização: {relatorio['normalizacao']}.",
        f"- Hash da lista de grupos: `{relatorio['hash_grupos_sha256']}`.",
        "- Mapa por registro: `docs/dados/grupos_textuais_mapa.csv`, com SHA-256 do ID.",
        "- Script: `src/construir_grupos_textuais.py`.",
        "- Nenhuma escrita foi realizada na planilha.",
        "",
    ]
    return "\n".join(linhas)


def montar_relatorio(registros: list[dict[str, str]],
                     com_quase_duplicados: bool = True) -> dict[str, Any]:
    relatorio = agrupar(registros)
    relatorio["quase_duplicados"] = (
        diagnosticar_quase_duplicados(relatorio["_textos_por_grupo"])
        if com_quase_duplicados
        else {"executado": False, "motivo": "diagnostico desativado"}
    )
    problemas = {
        "linhas_sem_id": relatorio["corpus"]["linhas_sem_id"],
        "linhas_sem_texto_em_todos_os_campos":
            relatorio["corpus"]["linhas_sem_texto_em_todos_os_campos"],
        "grupos_maiores_que_uma_dobra":
            relatorio["particionamento"]["grupos_maiores_que_uma_dobra"],
        "grupos_com_referencia_divergente":
            relatorio["rotulos_conflitantes"]["grupos_com_referencia_divergente"],
    }
    # Rótulos divergentes limitam a acurácia, mas não impedem o Passo 3; só
    # bloqueiam problemas que quebram o particionamento ou a rastreabilidade.
    bloqueios = [nome for nome in ("linhas_sem_id",
                                  "linhas_sem_texto_em_todos_os_campos",
                                  "grupos_maiores_que_uma_dobra")
                 if problemas[nome]]
    relatorio["problemas"] = problemas
    relatorio["bloqueios"] = bloqueios
    relatorio["status"] = "apto_para_particionar" if not bloqueios else "bloqueado"
    return relatorio


def escrever_mapa(caminho: Path, mapa: list[dict[str, str]]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(["id_sha256", "grupo_sha256"])
        escritor.writerows([[m["id_sha256"], m["grupo_sha256"]] for m in mapa])


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--json", type=Path, default=SAIDA_JSON_PADRAO)
    p.add_argument("--markdown", type=Path, default=SAIDA_MD_PADRAO)
    p.add_argument("--mapa", type=Path, default=SAIDA_MAPA_PADRAO)
    p.add_argument("--sem-quase-duplicados", action="store_true",
                   help="pula o diagnostico de similaridade")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    relatorio = montar_relatorio(ler_registros(sh, config),
                                 com_quase_duplicados=not args.sem_quase_duplicados)
    relatorio["gerado_em"] = agora_bahia()
    relatorio["fonte"] = config["aba_principal"]
    relatorio["script_origem"] = "src/construir_grupos_textuais.py"

    escrever_mapa(args.mapa, relatorio["_mapa"])
    publicavel = {k: v for k, v in relatorio.items() if not k.startswith("_")}
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(publicavel, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    args.markdown.write_text(renderizar_markdown(relatorio), encoding="utf-8")
    print(renderizar_markdown(relatorio))
    return 0 if relatorio["status"] == "apto_para_particionar" else 2


if __name__ == "__main__":
    raise SystemExit(main())
