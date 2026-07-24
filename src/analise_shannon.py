from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "docs" / "dados"
ESTADO_BERTIMBAU = DADOS / "bertimbau_training_state.json"
MIN_SUPORTE_CATEGORIA = 30
MAX_LINHAS_VOTOS = 200


def agora_bahia() -> str:
    tz = timezone(timedelta(hours=-3))
    return datetime.now(tz).strftime("%d/%m/%Y %H:%M")


def ler_json(nome: str):
    caminho = DADOS / nome
    if not caminho.exists():
        return []
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def salvar_json(nome: str, dados) -> None:
    caminho = DADOS / nome
    caminho.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=False),
        encoding="utf-8",
    )


def valor(row: dict, chave: str) -> str:
    v = row.get(chave)
    return str(v).strip() if v is not None else ""


def numero(row: dict, chave: str) -> float | None:
    try:
        return float(row.get(chave))
    except (TypeError, ValueError):
        return None


def entropia_shannon(contagens: Counter) -> dict:
    total = sum(contagens.values())
    if total <= 0:
        return {"n": 0, "k": 0, "h": 0.0, "h_norm": 0.0, "categorias_efetivas": 0.0}
    probs = [n / total for n in contagens.values() if n > 0]
    h = -sum(p * math.log2(p) for p in probs)
    k = len(probs)
    h_norm = h / math.log2(k) if k > 1 else 0.0
    return {
        "n": total,
        "k": k,
        "h": round(h, 4),
        "h_norm": round(h_norm, 4),
        "categorias_efetivas": round(2**h, 4),
    }


def kl_divergencia(p: dict[str, float], q: dict[str, float]) -> float:
    return sum(p[k] * math.log2(p[k] / q[k]) for k in p if p[k] > 0 and q.get(k, 0) > 0)


def jensen_shannon(c1: Counter, c2: Counter) -> float | None:
    total1 = sum(c1.values())
    total2 = sum(c2.values())
    if total1 <= 0 or total2 <= 0:
        return None
    chaves = set(c1) | set(c2)
    p = {k: c1.get(k, 0) / total1 for k in chaves}
    q = {k: c2.get(k, 0) / total2 for k in chaves}
    m = {k: (p[k] + q[k]) / 2 for k in chaves}
    return round(0.5 * kl_divergencia(p, m) + 0.5 * kl_divergencia(q, m), 4)


def risco_ambiguidade(h_norm: float, top1_pct: float) -> str:
    if h_norm >= 0.75 or top1_pct < 0.55:
        return "alta_ambiguidade"
    if h_norm >= 0.45 or top1_pct < 0.70:
        return "ambiguidade_moderada"
    return "estavel"


def arquivos_modelo() -> dict[str, Path]:
    arquivos = {"etapa1_oficial": DADOS / "registros.json"}
    for caminho in sorted(DADOS.glob("registros_*.json")):
        modelo = caminho.stem.replace("registros_", "")
        if modelo:
            arquivos[modelo] = caminho
    return {m: p for m, p in arquivos.items() if p.exists()}


def estado_bertimbau() -> dict:
    """Retorna o estado publicado sem inferir treino por arquivos legados."""
    try:
        dados = json.loads(ESTADO_BERTIMBAU.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return dados if isinstance(dados, dict) else {}


def resumo_modelo(modelo: str, registros: list[dict], hist_global: Counter) -> tuple[dict, list[dict]]:
    pred = Counter(valor(r, "p") for r in registros if valor(r, "p"))
    hist = Counter(valor(r, "o") for r in registros if valor(r, "o"))
    conc = [int(r.get("k") or 0) for r in registros if str(r.get("k", "")).strip() != ""]
    confs = [c for r in registros if (c := numero(r, "c")) is not None]
    h_pred = entropia_shannon(pred)
    h_hist = entropia_shannon(hist)
    total_pred = h_pred["n"]
    top = pred.most_common(1)[0] if pred else ("", 0)
    linha_modelo = {
        "modelo": modelo,
        "registros": len(registros),
        "categorias_previstas": h_pred["k"],
        "entropia_previsoes": h_pred["h"],
        "entropia_normalizada": h_pred["h_norm"],
        "categorias_efetivas": h_pred["categorias_efetivas"],
        "categoria_top": top[0],
        "categoria_top_pct": round(top[1] / total_pred, 4) if total_pred else None,
        "concordancia_historico": round(sum(conc) / len(conc), 4) if conc else None,
        "confianca_media": round(sum(confs) / len(confs), 4) if confs else None,
        "entropia_historico_local": h_hist["h"],
        "js_vs_historico_global": jensen_shannon(pred, hist_global),
    }

    por_categoria: list[dict] = []
    buckets: dict[str, list[dict]] = defaultdict(list)
    for r in registros:
        original = valor(r, "o")
        previsto = valor(r, "p")
        if original and previsto:
            buckets[original].append(r)
    for categoria, rows in buckets.items():
        if len(rows) < MIN_SUPORTE_CATEGORIA:
            continue
        dist = Counter(valor(r, "p") for r in rows if valor(r, "p"))
        h = entropia_shannon(dist)
        total = h["n"]
        top2 = dist.most_common(2)
        top1_nome, top1_n = top2[0] if top2 else ("", 0)
        top2_nome, top2_n = top2[1] if len(top2) > 1 else ("", 0)
        conc_cat = [int(r.get("k") or 0) for r in rows if str(r.get("k", "")).strip() != ""]
        top1_pct = top1_n / total if total else 0.0
        por_categoria.append(
            {
                "modelo": modelo,
                "categoria_historica": categoria,
                "suporte": len(rows),
                "categorias_previstas": h["k"],
                "entropia_previsoes": h["h"],
                "entropia_normalizada": h["h_norm"],
                "categorias_efetivas": h["categorias_efetivas"],
                "top_1_previsto": top1_nome,
                "top_1_pct": round(top1_pct, 4) if total else None,
                "top_2_previsto": top2_nome,
                "top_2_pct": round(top2_n / total, 4) if total else None,
                "concordancia_historico": round(sum(conc_cat) / len(conc_cat), 4) if conc_cat else None,
                "risco": risco_ambiguidade(h["h_norm"], top1_pct),
            }
        )
    return linha_modelo, por_categoria


def resumo_votos(registros_por_modelo: dict[str, list[dict]]) -> dict:
    por_linha: dict[str, dict] = defaultdict(lambda: {"pred": {}, "hist": ""})
    for modelo, registros in registros_por_modelo.items():
        for r in registros:
            linha = valor(r, "l")
            previsto = valor(r, "p")
            if not linha or not previsto:
                continue
            por_linha[linha]["pred"][modelo] = previsto
            if not por_linha[linha]["hist"]:
                por_linha[linha]["hist"] = valor(r, "o")

    linhas = []
    for linha, item in por_linha.items():
        votos = item["pred"]
        if len(votos) < 2:
            continue
        dist = Counter(votos.values())
        h = entropia_shannon(dist)
        maioria, n_maioria = dist.most_common(1)[0]
        linhas.append(
            {
                "linha": int(linha) if linha.isdigit() else linha,
                "categoria_historica": item["hist"],
                "n_modelos": len(votos),
                "categorias_votadas": h["k"],
                "entropia_votos": h["h"],
                "entropia_normalizada": h["h_norm"],
                "categorias_efetivas": h["categorias_efetivas"],
                "maioria": maioria,
                "maioria_pct": round(n_maioria / len(votos), 4),
                "modelos_divergentes": sorted([m for m, p in votos.items() if p != maioria]),
            }
        )
    linhas.sort(key=lambda r: (r["entropia_normalizada"], r["categorias_votadas"], -r["maioria_pct"]), reverse=True)
    resumo = {
        "linhas_com_2_ou_mais_modelos": len(linhas),
        "linhas_alta_ambiguidade": sum(1 for r in linhas if r["entropia_normalizada"] >= 0.75),
        "entropia_media_votos": round(sum(r["entropia_votos"] for r in linhas) / len(linhas), 4) if linhas else 0.0,
    }
    return {"resumo": resumo, "linhas_mais_ambiguas": linhas[:MAX_LINHAS_VOTOS]}


def main() -> int:
    arquivos = arquivos_modelo()
    estado_bert = estado_bertimbau()
    modelos_excluidos = []
    if estado_bert.get("status") != "ok" and "transformer_ft" in arquivos:
        arquivos.pop("transformer_ft")
        modelos_excluidos.append("transformer_ft")
        print("transformer_ft excluido: BERTimbau sem treino concluido.")
    registros_por_modelo = {
        modelo: ler_json(caminho.name)
        for modelo, caminho in arquivos.items()
    }
    registros_por_modelo = {
        modelo: rows for modelo, rows in registros_por_modelo.items() if isinstance(rows, list) and rows
    }
    historico_base = registros_por_modelo.get("etapa1_oficial") or next(iter(registros_por_modelo.values()), [])
    historico_global = Counter(valor(r, "o") for r in historico_base if valor(r, "o"))

    modelos = []
    categorias = []
    for modelo, registros in registros_por_modelo.items():
        linha_modelo, linhas_cat = resumo_modelo(modelo, registros, historico_global)
        modelos.append(linha_modelo)
        categorias.extend(linhas_cat)

    js_modelos = [
        {
            "modelo": m["modelo"],
            "js_vs_historico_global": m["js_vs_historico_global"],
            "interpretacao": "menor=distribuicao_mais_proxima_do_historico",
        }
        for m in modelos
        if m.get("js_vs_historico_global") is not None
    ]
    categorias.sort(
        key=lambda r: (r["entropia_normalizada"], r["suporte"], r["categorias_efetivas"]),
        reverse=True,
    )
    ranking_categorias = []
    por_cat: dict[str, list[dict]] = defaultdict(list)
    for r in categorias:
        por_cat[r["categoria_historica"]].append(r)
    for cat, rows in por_cat.items():
        entropias = [r["entropia_normalizada"] for r in rows if r["entropia_normalizada"] is not None]
        suportes = [r["suporte"] for r in rows]
        ranking_categorias.append(
            {
                "categoria_historica": cat,
                "modelos": len(rows),
                "suporte_max": max(suportes) if suportes else 0,
                "entropia_media_normalizada": round(sum(entropias) / len(entropias), 4) if entropias else 0.0,
                "maior_risco": sorted(rows, key=lambda x: x["entropia_normalizada"], reverse=True)[0]["risco"],
            }
        )
    ranking_categorias.sort(key=lambda r: (r["entropia_media_normalizada"], r["suporte_max"]), reverse=True)

    votos = resumo_votos(registros_por_modelo)
    modelos.sort(key=lambda r: r["entropia_normalizada"], reverse=True)
    js_modelos.sort(key=lambda r: r["js_vs_historico_global"])

    resumo = {
        "gerado_em": agora_bahia(),
        "fontes": [p.name for p in arquivos.values()],
        "criterios": {
            "base_log": 2,
            "min_suporte_categoria": MIN_SUPORTE_CATEGORIA,
            "max_linhas_votos": MAX_LINHAS_VOTOS,
            "privacidade": "sem_id_titulo_descricao_texto_livre",
        },
        "modelos": len(modelos),
        "modelos_excluidos": modelos_excluidos,
        "estado_bertimbau": estado_bert.get("status", "nao_publicado"),
        "categorias_historicas_base": len(historico_global),
        "leitura": (
            "Shannon mede dispersao/ambiguidade das distribuicoes; "
            "Jensen-Shannon mede distancia entre distribuicao prevista e historico. "
            "Nao substitui acuracia nem validacao humana."
        ),
        "principais": {
            "modelo_maior_diversidade": modelos[0]["modelo"] if modelos else None,
            "modelo_menor_js_historico": js_modelos[0]["modelo"] if js_modelos else None,
            "categorias_alta_ambiguidade": sum(1 for r in categorias if r["risco"] == "alta_ambiguidade"),
            "linhas_alta_ambiguidade_votos": votos["resumo"]["linhas_alta_ambiguidade"],
        },
    }

    salvar_json("shannon_resumo.json", resumo)
    salvar_json("shannon_modelos.json", modelos)
    salvar_json("jensen_shannon_modelos.json", js_modelos)
    salvar_json(
        "shannon_categorias.json",
        {
            "criterios": resumo["criterios"],
            "ranking_categorias": ranking_categorias,
            "por_modelo_categoria": categorias,
        },
    )
    salvar_json("shannon_votos.json", votos)
    print(
        "OK: Shannon gerado | modelos={modelos} | categorias={cats} | linhas_votos={votos}".format(
            modelos=len(modelos),
            cats=len(categorias),
            votos=len(votos["linhas_mais_ambiguas"]),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
