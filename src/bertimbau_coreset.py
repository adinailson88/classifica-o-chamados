#!/usr/bin/env python3
"""Gera um coreset experimental para o BERTimbau sem executar fine-tuning.

Objetivo: selecionar uma base menor, auditavel e reversivel para testes futuros,
preservando categorias raras, exemplos dificeis e divergencias. A primeira
versao usa TF-IDF + KMeans por categoria como fallback leve, sem embeddings
transformer, para caber no GitHub Actions e nao bloquear o repositorio.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
DADOS = RAIZ / "dados"
DOCS_DADOS = RAIZ / "docs" / "dados"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Gera coreset experimental do BERTimbau.")
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--max-total", type=int, default=4000)
    p.add_argument("--categoria-rara-max", type=int, default=30)
    p.add_argument("--alvo-por-cluster", type=int, default=60)
    p.add_argument("--max-clusters-categoria", type=int, default=30)
    p.add_argument("--baixa-confianca", type=float, default=0.70)
    p.add_argument("--quase-duplicata", type=float, default=0.96)
    p.add_argument("--fronteira-por-categoria", type=int, default=10)
    p.add_argument("--fixture", type=int, default=0,
                   help="Gera N registros sinteticos para validacao local sem planilha.")
    return p.parse_args()


def norm_texto(valor) -> str:
    texto = unicodedata.normalize("NFKD", str(valor or ""))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto.casefold()).strip()


def token_est(texto: str) -> int:
    palavras = re.findall(r"\w+", str(texto or ""), flags=re.UNICODE)
    return int(math.ceil(len(palavras) * 1.35) + 2)


def id_hash(valor) -> str:
    return hashlib.sha256(str(valor or "").encode("utf-8")).hexdigest()[:16]


def conf_num(valor) -> float | None:
    try:
        f = float(str(valor).replace("%", "").replace(",", ".").strip())
        return f / 100.0 if f > 1 else f
    except (TypeError, ValueError):
        return None


def cel(linha: list, idx: int | None) -> str:
    if idx is None or idx < 0 or idx >= len(linha):
        return ""
    return str(linha[idx] or "").strip()


def carregar_shannon() -> dict[int, dict]:
    caminho = DOCS_DADOS / "shannon_votos.json"
    if not caminho.exists():
        return {}
    try:
        payload = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    out = {}
    for r in payload.get("linhas_mais_ambiguas", []):
        try:
            out[int(r.get("linha"))] = r
        except (TypeError, ValueError):
            continue
    return out


def cabecalhos(valores: list[list]) -> dict[str, int]:
    if not valores:
        return {}
    return {pl.normalizar_cabecalho(nome): i for i, nome in enumerate(valores[0])}


def carregar_planilha(args: argparse.Namespace) -> list[dict]:
    with args.config.open(encoding="utf-8") as f:
        config = json.load(f)
    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    ws = sh.worksheet(config["aba_principal"])
    valores = pl.ler_valores(ws, "A:P")
    confs = pl.ler_conferencias(sh, config["aba_principal"])
    idx = cabecalhos(valores)
    aliases = {
        "id": ("id chamado",),
        "titulo": ("titulo", "título"),
        "cat": ("categoria completa",),
        "desc_glpi": ("descricao glpi", "descrição glpi"),
        "titulo_osm": ("titulo o.s.m.", "título o.s.m."),
        "desc_osm": ("descricao o.s.m.", "descrição o.s.m."),
        "cat_ia": ("classificacao ia", "classificação ia"),
        "confianca": ("avaliacao (%)", "avaliação (%)"),
    }

    def ach(chaves):
        for chave in chaves:
            n = pl.normalizar_cabecalho(chave)
            if n in idx:
                return idx[n]
        return None

    pos = {k: ach(v) for k, v in aliases.items()}
    shannon = carregar_shannon()
    registros = []
    for linha_planilha, linha in enumerate(valores[1:], start=2):
        cat_hist = cel(linha, pos["cat"])
        texto = "\n".join(x for x in [
            cel(linha, pos["titulo"]),
            cel(linha, pos["desc_glpi"]),
            cel(linha, pos["titulo_osm"]),
            cel(linha, pos["desc_osm"]),
        ] if x)
        if not cat_hist or not texto:
            continue
        cat_ia = cel(linha, pos["cat_ia"])
        conf = conf_num(cel(linha, pos["confianca"]))
        c = confs.get(str(linha_planilha), {})
        if c.get("ia") == "Correto" and cat_ia:
            cat_treino = cat_ia
            fonte = "conferencia_ia_correta"
        elif c.get("glpi") == "Correto":
            cat_treino = cat_hist
            fonte = "conferencia_glpi_correta"
        else:
            cat_treino = cat_hist
            fonte = "historico"
        registros.append({
            "linha": linha_planilha,
            "id_hash": id_hash(cel(linha, pos["id"]) or linha_planilha),
            "texto": texto,
            "texto_norm": norm_texto(texto),
            "categoria": cat_treino,
            "categoria_historica": cat_hist,
            "categoria_ia": cat_ia,
            "fonte_categoria": fonte,
            "confianca": conf,
            "tokens": token_est(texto),
            "conferencia_ia": c.get("ia"),
            "conferencia_glpi": c.get("glpi"),
            "shannon": shannon.get(linha_planilha),
        })
    return registros


def gerar_fixture(n: int) -> list[dict]:
    cats = {
        "Eletrica > Instalacoes": ["lampada queimada sala", "tomada sem energia bloco"],
        "Hidraulica > Vazamento": ["vazamento torneira banheiro", "cano rompido banheiro"],
        "Civil > Porta": ["porta com fechadura quebrada", "janela emperrada"],
        "Rara > Elevador": ["elevador parado sem resposta"],
    }
    out = []
    nomes = list(cats)
    for i in range(max(n, 1)):
        cat = nomes[i % len(nomes)]
        base = cats[cat][i % len(cats[cat])]
        texto = f"{base} ocorrencia {i % 17}"
        if i % 19 == 0:
            texto = base
        conf = 0.52 if i % 11 == 0 else 0.91
        out.append({
            "linha": i + 2,
            "id_hash": id_hash(f"fixture-{i}"),
            "texto": texto,
            "texto_norm": norm_texto(texto),
            "categoria": cat,
            "categoria_historica": cat,
            "categoria_ia": cat if i % 7 else nomes[(i + 1) % len(nomes)],
            "fonte_categoria": "fixture",
            "confianca": conf,
            "tokens": token_est(texto),
            "conferencia_ia": "Errado" if i % 13 == 0 else None,
            "conferencia_glpi": "Correto" if i % 13 == 0 else None,
            "shannon": {"entropia_normalizada": 0.9} if i % 17 == 0 else None,
        })
    return out


def marcar_dificuldade(registros: list[dict], baixa_confianca: float) -> None:
    for r in registros:
        motivos = []
        if r["confianca"] is not None and r["confianca"] < baixa_confianca:
            motivos.append("baixa_confianca")
        if r.get("categoria_ia") and r["categoria_ia"] != r["categoria_historica"]:
            motivos.append("divergencia_ia_historico")
        if r.get("conferencia_ia") == "Errado" or r.get("conferencia_glpi") == "Errado":
            motivos.append("divergencia_humana")
        if (r.get("shannon") or {}).get("entropia_normalizada", 0) >= 0.75:
            motivos.append("alta_divergencia_modelos")
        r["motivos_preservacao"] = motivos


def detectar_duplicatas(registros: list[dict], quase_limiar: float) -> tuple[dict, list[dict]]:
    exatos = defaultdict(list)
    for r in registros:
        exatos[(r["categoria"], r["texto_norm"])].append(r["linha"])
    duplicatas = {
        f"sha256:{hashlib.sha256((cat + chr(0) + txt).encode('utf-8')).hexdigest()}": linhas
        for (cat, txt), linhas in exatos.items() if len(linhas) > 1
    }
    quase = []
    por_cat = defaultdict(list)
    for r in registros:
        por_cat[r["categoria"]].append(r)
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.neighbors import NearestNeighbors
    except Exception:  # noqa: BLE001
        return duplicatas, quase
    for cat, linhas in por_cat.items():
        if len(linhas) < 3:
            continue
        vec = TfidfVectorizer(strip_accents="unicode", lowercase=True, ngram_range=(1, 2), min_df=1)
        x = vec.fit_transform([r["texto"] for r in linhas])
        nn = NearestNeighbors(n_neighbors=2, metric="cosine").fit(x)
        dist, ind = nn.kneighbors(x)
        vistos = set()
        for i, r in enumerate(linhas):
            j = int(ind[i][1])
            sim = 1.0 - float(dist[i][1])
            par = tuple(sorted((r["linha"], linhas[j]["linha"])))
            if sim >= quase_limiar and par not in vistos:
                vistos.add(par)
                quase.append({"categoria": cat, "linha_a": par[0], "linha_b": par[1], "similaridade": round(sim, 4)})
    return duplicatas, quase


def selecionar(registros: list[dict], args: argparse.Namespace) -> tuple[set[int], dict]:
    from sklearn.cluster import KMeans
    from sklearn.feature_extraction.text import TfidfVectorizer
    selecionados: set[int] = set()
    report = {"categorias": [], "metodo": "tfidf_kmeans_por_categoria"}
    por_cat = defaultdict(list)
    for r in registros:
        por_cat[r["categoria"]].append(r)
    for cat in sorted(por_cat):
        linhas = por_cat[cat]
        n = len(linhas)
        obrig = {r["linha"] for r in linhas if r["motivos_preservacao"]}
        if n <= args.categoria_rara_max:
            selecionados.update(r["linha"] for r in linhas)
            report["categorias"].append({
                "categoria": cat, "total": n, "selecionados": n,
                "clusters": 0, "preservacao": "integral_categoria_rara",
            })
            continue
        k = max(1, min(args.max_clusters_categoria, math.ceil(n / max(args.alvo_por_cluster, 1))))
        vec = TfidfVectorizer(strip_accents="unicode", lowercase=True, ngram_range=(1, 2), min_df=1,
                              max_features=30000)
        x = vec.fit_transform([r["texto"] for r in linhas])
        km = KMeans(n_clusters=k, random_state=args.seed, n_init=10)
        labels = km.fit_predict(x)
        dist = km.transform(x)
        margem = []
        for i in range(len(linhas)):
            ordem = sorted(dist[i])
            margem.append(ordem[1] - ordem[0] if len(ordem) > 1 else 1.0)
        selecionados.update(obrig)
        for cluster in range(k):
            idxs = [i for i, lab in enumerate(labels) if lab == cluster]
            if not idxs:
                continue
            centro = min(idxs, key=lambda i: dist[i][cluster])
            outlier = max(idxs, key=lambda i: dist[i][cluster])
            selecionados.add(linhas[centro]["linha"])
            selecionados.add(linhas[outlier]["linha"])
        for i in sorted(range(len(linhas)), key=lambda j: margem[j])[:args.fronteira_por_categoria]:
            selecionados.add(linhas[i]["linha"])
        report["categorias"].append({
            "categoria": cat, "total": n,
            "selecionados": sum(1 for r in linhas if r["linha"] in selecionados),
            "clusters": k,
            "preservados_dificeis": len(obrig),
            "preservacao": "dificeis_centroides_outliers_fronteira",
        })
    if args.max_total > 0 and len(selecionados) > args.max_total:
        obrig = {r["linha"] for r in registros if r["motivos_preservacao"]}
        raras = {
            r["linha"]
            for _cat, linhas in por_cat.items() if len(linhas) <= args.categoria_rara_max
            for r in linhas
        }
        fixos = obrig | raras
        candidatos = [r for r in registros if r["linha"] in selecionados and r["linha"] not in fixos]
        candidatos.sort(key=lambda r: (len(r["motivos_preservacao"]), r["tokens"]), reverse=True)
        limite_extra = max(args.max_total - len(fixos), 0)
        selecionados = set(fixos) | {r["linha"] for r in candidatos[:limite_extra]}
        report["max_total_aplicado"] = args.max_total
        report["selecionados_obrigatorios"] = len(fixos)
    return selecionados, report


def selecionar_indices(textos, labels, dificeis=None, *, seed=42, max_total=4000,
                       categoria_rara_max=30, alvo_por_cluster=60,
                       max_clusters_categoria=30, fronteira_por_categoria=10):
    """Versao reutilizavel (in-memory) da selecao por clustering: recebe textos +
    rotulos (e, opcionalmente, uma mascara de exemplos dificeis a preservar) e
    devolve a lista ORDENADA de indices posicionais selecionados.

    Mesma logica de `selecionar` (preserva categoria rara integral, centroides,
    outliers, fronteira e dificeis; aplica max_total protegendo raras+dificeis),
    para que o treino do BERTimbau no modo cluster_coreset use exatamente o mesmo
    criterio publicado nos artefatos.
    """
    from types import SimpleNamespace
    regs = []
    for i, (t, c) in enumerate(zip(textos, labels)):
        regs.append({
            "linha": i,
            "texto": str(t),
            "categoria": str(c),
            "tokens": token_est(t),
            "motivos_preservacao": (["dificil"] if dificeis and dificeis[i] else []),
        })
    args = SimpleNamespace(
        seed=seed, max_total=max_total, categoria_rara_max=categoria_rara_max,
        alvo_por_cluster=alvo_por_cluster, max_clusters_categoria=max_clusters_categoria,
        fronteira_por_categoria=fronteira_por_categoria,
    )
    selset, _rep = selecionar(regs, args)
    return sorted(selset)


def escrever_json(caminho: Path, payload) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    registros = gerar_fixture(args.fixture) if args.fixture else carregar_planilha(args)
    if not registros:
        print("Nenhum registro elegivel encontrado.", file=sys.stderr)
        return 1
    marcar_dificuldade(registros, args.baixa_confianca)
    duplicatas, quase = detectar_duplicatas(registros, args.quase_duplicata)
    selecionados, cluster_report = selecionar(registros, args)
    antes = dict(sorted(Counter(r["categoria"] for r in registros).items()))
    depois = dict(sorted(Counter(r["categoria"] for r in registros if r["linha"] in selecionados).items()))
    total = len(registros)
    n_sel = len(selecionados)
    tokens_total = sum(r["tokens"] for r in registros)
    tokens_sel = sum(r["tokens"] for r in registros if r["linha"] in selecionados)
    agora = agora_bahia()
    params = vars(args).copy()
    params.pop("config", None)
    params.pop("credenciais", None)
    resumo = {
        "status": "experimental",
        "gerado_em": agora,
        "metodo": "TF-IDF + KMeans por categoria; fallback leve sem embeddings transformer",
        "nao_substitui_full": True,
        "validado_contra_treino_real": False,
        "total_registros_elegiveis": total,
        "total_registros_selecionados": n_sel,
        "reducao_percentual_exemplos": round(1 - (n_sel / total), 4),
        "tokens_estimados_total": tokens_total,
        "tokens_estimados_selecionados": tokens_sel,
        "reducao_percentual_tokens": round(1 - (tokens_sel / tokens_total), 4) if tokens_total else 0,
        "distribuicao_categoria_antes": antes,
        "distribuicao_categoria_depois": depois,
        "categorias_preservadas_integralmente": [cat for cat, qtd in antes.items() if qtd <= args.categoria_rara_max],
        "duplicatas_exatas_detectadas": sum(len(v) - 1 for v in duplicatas.values()),
        "quase_duplicatas_detectadas": len(quase),
        "parametros": params,
        "criterios_comparacao_futura": {
            "comparar": ["full", "auto_subamostra", "cluster_coreset"],
            "metricas": ["acuracia", "precisao_por_categoria", "recall_por_categoria",
                         "f1_por_categoria", "f1_macro", "matriz_confusao",
                         "tempo_execucao", "total_exemplos", "tokens_estimados", "categorias_raras"],
            "alerta_f1_macro": 0.02,
            "decisao": "nao tornar padrao sem comparacao real e sem proteger categorias raras",
        },
    }
    ids = {
        "status": "experimental",
        "gerado_em": agora,
        "observacao": "IDs reais nao sao publicados; usar linha_planilha e id_hash para auditoria.",
        "selecionados": [
            {
                "linha_planilha": r["linha"],
                "id_hash": r["id_hash"],
                "categoria": r["categoria"],
                "tokens_estimados": r["tokens"],
                "motivos_preservacao": r["motivos_preservacao"] or ["representativo_cluster"],
            }
            for r in registros if r["linha"] in selecionados
        ],
    }
    token_stats = {
        "gerado_em": agora,
        "status": "experimental",
        "total": tokens_total,
        "selecionado": tokens_sel,
        "por_categoria": {
            cat: {
                "tokens_total": sum(r["tokens"] for r in registros if r["categoria"] == cat),
                "tokens_selecionados": sum(r["tokens"] for r in registros if r["categoria"] == cat and r["linha"] in selecionados),
            }
            for cat in antes
        },
    }
    review = {
        "status": "experimental",
        "gerado_em": agora,
        "natureza": "fila sugestiva; nao altera rotulos humanos",
        "linhas": sorted([
            {
                "linha_planilha": r["linha"],
                "categoria": r["categoria"],
                "motivos": r["motivos_preservacao"],
                "tokens_estimados": r["tokens"],
                "confianca": r["confianca"],
            }
            for r in registros if r["motivos_preservacao"]
        ], key=lambda x: (-len(x["motivos"]), x["categoria"], x["linha_planilha"]))[:500],
    }
    cluster_report.update({
        "status": "experimental",
        "gerado_em": agora,
        "duplicatas_exatas": duplicatas,
        "quase_duplicatas_amostra": quase[:500],
        "parametros": params,
    })
    escrever_json(DADOS / "bertimbau_coreset_ids.json", ids)
    escrever_json(DOCS_DADOS / "bertimbau_coreset_resumo.json", resumo)
    escrever_json(DOCS_DADOS / "bertimbau_token_stats.json", token_stats)
    escrever_json(DOCS_DADOS / "bertimbau_cluster_report.json", cluster_report)
    escrever_json(DOCS_DADOS / "bertimbau_review_queue.json", review)
    print(json.dumps({
        "status": "experimental",
        "elegiveis": total,
        "selecionados": n_sel,
        "reducao_exemplos": resumo["reducao_percentual_exemplos"],
        "reducao_tokens": resumo["reducao_percentual_tokens"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
