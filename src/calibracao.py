#!/usr/bin/env python3
"""Calibração da confiança (o critério central do OBJETIVO FINAL).

Mede a relação CONFIANÇA × ACERTO: quando o modelo diz ">=95%", ele realmente
acerta ~>=95%? (não basta softmax alto). Calcula, a partir do SNAPSHOT_ETAPA_1:
- acerto por FAIXA de confiança (bins), por EXECUTOR;
- acerto vs classificação HISTÓRICA (col C) — disponível já;
- acerto vs categoria DECIDIDA pela memória de conferência M/N/P (mesma verdade de
  avaliacao_final.py, via decisao_validada.verdade_validada) — quando houver decisão
  travada. NÃO usa a marcação bruta de uma única coluna de conferência isolada: na
  prática, a coluna N (CONFERÊNCIA IA) isolada quase não recebe "Errado", o que
  produzia acerto_validado artificialmente igual a 1,0 em toda faixa de confiança
  (corrigido em 23/07/2026);
- ECE (erro de calibração esperado) e o destaque da faixa >=95%.

Read-only: não escreve na planilha. Gera docs/dados/calibracao.json (agregado,
sem texto de chamado) para o dashboard.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decisao_validada as dv  # noqa: E402
import planilha as pl  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
SAIDA = RAIZ / "docs" / "dados" / "calibracao.json"

# (limite_inferior, limite_superior, rotulo)
FAIXAS = [
    (0.0, 0.5, "<50%"),
    (0.5, 0.7, "50-70%"),
    (0.7, 0.8, "70-80%"),
    (0.8, 0.9, "80-90%"),
    (0.9, 0.95, "90-95%"),
    (0.95, 1.01, ">=95%"),
]


def parse_conf(v) -> float:
    try:
        f = float(str(v).replace("%", "").replace(",", ".").strip())
        return f / 100.0 if f > 1 else f
    except (ValueError, TypeError):
        return 0.0


def faixa_de(conf: float) -> str:
    for lo, hi, rot in FAIXAS:
        if lo <= conf < hi:
            return rot
    return ">=95%"


def carregar_validados(sh, aba) -> dict:
    """linha_planilha -> categoria_validada (só onde preenchida)."""
    try:
        vals = sh.worksheet(aba).get_all_values()
    except Exception:  # noqa: BLE001
        return {}
    if len(vals) < 2:
        return {}
    cab = {(" ".join(str(c).split()).casefold()): i for i, c in enumerate(vals[0])}
    i_ln = cab.get("linha_planilha")
    i_cv = cab.get("categoria_validada")
    if i_ln is None or i_cv is None:
        return {}
    m = {}
    for r in vals[1:]:
        ln = str(r[i_ln]).strip() if i_ln < len(r) else ""
        cv = str(r[i_cv]).strip() if i_cv < len(r) else ""
        if ln and cv:
            m[ln] = cv
    return m


def _agrega():
    return {"n": 0, "ok_hist": 0, "soma_conf": 0.0, "n_val": 0, "ok_val": 0}


def _fechar(d):
    n, nv = d["n"], d["n_val"]
    return {
        "n": n,
        "concordancia_historico": round(d["ok_hist"] / n, 4) if n else 0.0,
        "confianca_media": round(d["soma_conf"] / n, 4) if n else 0.0,
        "n_validados": nv,
        "acerto_validado": round(d["ok_val"] / nv, 4) if nv else None,
    }


def calcular(sh, config: dict) -> dict:
    abas = config["abas_experimento"]
    try:
        vals = sh.worksheet(abas["snapshot_etapa_1"]).get_values(
            "A:J", value_render_option="UNFORMATTED_VALUE")
    except Exception:  # noqa: BLE001
        vals = []
    # Verdade validada: a MESMA memoria de decisao M/N/P usada em avaliacao_final.py
    # (decisao_validada.verdade_validada), nao a marcacao bruta da coluna N isolada.
    # Motivo (achado de 2026-07-23): a coluna N (CONFERENCIA IA) isolada, na pratica,
    # so acumula marcacoes "Correto" (o fluxo humano atual raramente marca N como
    # "Errado" — o erro da IA tende a ser registrado via M ou via a reclassificacao),
    # o que fazia "acerto_validado" por faixa de confianca sair sempre 1.0, inclusive
    # em faixas de confianca baixa — resultado estatisticamente implausivel e
    # inconsistente com avaliacao_final.py. Comparar contra a categoria DECIDIDA
    # (travada por M, N ou P, qualquer uma que tenha confirmado) corrige a metrica e
    # a torna consistente com o restante do pipeline.
    decisoes = dv.carregar_decisoes(sh, config["aba_principal"])
    verdade = dv.verdade_validada(decisoes)
    # Conferencias brutas (M/N/P), mantidas so para os diagnosticos auxiliares
    # (cobertura por coluna, matriz IA x GLPI) — nao usadas mais para "acerto_validado".
    conferencias = pl.ler_conferencias(sh, config["aba_principal"])

    por_faixa = {rot: _agrega() for _, _, rot in FAIXAS}
    por_exec = {}
    geral = _agrega()
    # Matriz 2x2 IA x GLPI: cat_ia e orig comparados contra a categoria DECIDIDA
    # (M/N/P), para toda linha com decisao travada -- ver correcao abaixo.
    matriz = {"ia_ok_glpi_ok": 0, "ia_ok_glpi_erro": 0, "ia_erro_glpi_ok": 0, "ia_erro_glpi_erro": 0}
    glpi = {"n": 0, "ok": 0}      # acerto validado da classificacao historica (coluna M)
    reclass = {"n": 0, "ok": 0}   # acerto validado da reclassificacao IA-2 (coluna P)
    # SNAPSHOT cols: 1 linha, 3 cat_original, 4 cat_ia, 5 conf, 6 executor
    for r in vals[1:]:
        if len(r) < 6:
            continue
        ln = str(r[1]).strip()
        try:
            ln_int = int(float(ln)) if ln else None
        except ValueError:
            ln_int = None
        orig = str(r[3]).strip()
        cat_ia = str(r[4]).strip()
        if not cat_ia:
            continue
        conf = parse_conf(r[5])
        execu = str(r[6]).strip() if len(r) > 6 else ""
        ok_hist = int(cat_ia == orig)
        # Acerto validado: a classificacao deste executor (col G) bate com a
        # categoria decidida pela memoria de conferencia (M/N/P, o que travou).
        decidida = verdade.get(ln_int) if ln_int is not None else None
        tem_val = decidida is not None
        ok_val = int(cat_ia == decidida) if tem_val else 0
        # Conferencia humana bruta: M => acerto do historico (GLPI); N => acerto da IA.
        conf_row = conferencias.get(ln, {})
        v_glpi = conf_row.get("glpi")
        v_ia = conf_row.get("ia")
        v_reclass = conf_row.get("reclass")
        if v_glpi is not None:
            glpi["n"] += 1
            glpi["ok"] += int(v_glpi == "Correto")
        if v_reclass is not None:
            reclass["n"] += 1
            reclass["ok"] += int(v_reclass == "Correto")
        # Matriz IA x GLPI: mesma correcao do acerto_validado (achado de 2026-07-23).
        # A versao anterior exigia AMBAS as colunas M e N marcadas na linha, e
        # comparava a marcacao bruta de cada uma -- herdava o mesmo vies de selecao
        # (N raramente marcada "Errado"), o que zerava 3 das 4 celulas. Em vez
        # disso, compara a classificacao da IA (cat_ia) e a categoria historica
        # (orig) contra a mesma categoria DECIDIDA pela memoria M/N/P, para toda
        # linha com decisao travada (nao so as que tem M e N ambas marcadas).
        if tem_val:
            ia_ok = cat_ia == decidida
            glpi_ok = orig == decidida
            chave = ("ia_ok" if ia_ok else "ia_erro") + \
                    ("_glpi_ok" if glpi_ok else "_glpi_erro")
            matriz[chave] += 1

        for alvo in (geral, por_faixa[faixa_de(conf)], por_exec.setdefault(execu or "(sem)", _agrega())):
            alvo["n"] += 1
            alvo["ok_hist"] += ok_hist
            alvo["soma_conf"] += conf
            if tem_val:
                alvo["n_val"] += 1
                alvo["ok_val"] += ok_val

    # ECE vs histórico (erro de calibração esperado)
    n_tot = geral["n"]
    ece = 0.0
    if n_tot:
        for rot in por_faixa:
            d = por_faixa[rot]
            if d["n"]:
                taxa = d["ok_hist"] / d["n"]
                cmed = d["soma_conf"] / d["n"]
                ece += (d["n"] / n_tot) * abs(cmed - taxa)

    faixa95 = _fechar(por_faixa[">=95%"])
    return {
        "gerado_em": agora_bahia(),
        "run_id": config.get("run_id", ""),
        "total": n_tot,
        "validados": geral["n_val"],
        "validacao_humana": {
            "modo": ("acerto_ia_validado (e todo o acerto_validado de geral/por_faixa/"
                     "por_executor abaixo) = classificacao do executor (col G) comparada "
                     "a categoria DECIDIDA pela memoria M/N/P (decisao_validada."
                     "verdade_validada), a mesma verdade usada em avaliacao_final.json — "
                     "corrigido em 2026-07-23 (antes comparava so contra a marcacao bruta "
                     "da coluna N, que na pratica so registra 'Correto'). "
                     "acerto_glpi_validado/acerto_reclass_validado abaixo usam a marcacao "
                     "bruta de M/P, so como diagnostico de cobertura por coluna."),
            "n_conferencia_ia": geral["n_val"],
            "acerto_ia_validado": round(geral["ok_val"] / geral["n_val"], 4) if geral["n_val"] else None,
            "n_conferencia_glpi": glpi["n"],
            "acerto_glpi_validado": round(glpi["ok"] / glpi["n"], 4) if glpi["n"] else None,
            "n_conferencia_reclass": reclass["n"],
            "acerto_reclass_validado": round(reclass["ok"] / reclass["n"], 4) if reclass["n"] else None,
            # Matriz 2x2: cat_ia e orig comparados contra a categoria decidida
            # (M/N/P), para toda linha com decisao travada -- corrigido em
            # 2026-07-23 (antes exigia M e N ambas marcadas e comparava a
            # marcacao bruta, com o mesmo vies de selecao do acerto_validado).
            # ia_ok_glpi_erro = IA corrige o historico; ia_erro_glpi_ok = IA
            # piora o historico.
            "matriz_ia_x_glpi": matriz,
        },
        "ece_historico": round(ece, 4),
        "alvo_confianca": float(config.get("objetivo_final", {}).get("confianca_minima_alvo", 0.95)),
        "faixa_alvo_95": faixa95,
        "por_faixa": [{"faixa": rot, **_fechar(por_faixa[rot])} for _, _, rot in FAIXAS],
        "por_executor": [{"executor": k, **_fechar(v)} for k, v in sorted(por_exec.items())],
        # A confiança aqui é a saída BRUTA do modelo (softmax/decision_function), NÃO um
        # calibrador ajustado. Ver PLANO_CALIBRACAO.md (CalibratedClassifierCV p/ lineares
        # TF-IDF; temperature scaling p/ o LSTM). Este JSON é diagnóstico, não calibração.
        "tipo_confianca": "bruta (softmax/decision_function) — NAO calibrada",
        "calibrador_ajustado": False,
        "plano_calibracao": "PLANO_CALIBRACAO.md",
        "observacao": ("Acerto vs histórico é preliminar (a classificação histórica pode "
                       "ter erros). A confiança é bruta (softmax alto NÃO é confiança calibrada). "
                       "acerto_validado (geral, faixa_alvo_95, por_faixa, por_executor) compara "
                       "a classificação do executor à categoria DECIDIDA pela memória M/N/P "
                       "(mesma verdade de avaliacao_final.json), não à marcação bruta isolada de "
                       "uma única coluna de conferência — corrigido em 23/07/2026 porque a coluna "
                       "N (CONFERÊNCIA IA) isolada, no uso real, quase não recebe marcação "
                       "'Errado', o que produzia acerto_validado artificialmente igual a 1.0 em "
                       "todas as faixas de confiança, inclusive nas mais baixas."),
    }


def main() -> int:
    with CONFIG_PADRAO.open(encoding="utf-8") as f:
        config = json.load(f)
    try:
        sh = pl.abrir_planilha(pl.id_planilha(config))
    except Exception as e:  # noqa: BLE001
        print(f"Falha ao acessar a planilha: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    dados = calcular(sh, config)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"total={dados['total']} | validados={dados['validados']} | ECE_historico={dados['ece_historico']}")
    a = dados["faixa_alvo_95"]
    print(f"faixa >=95%: n={a['n']} | concordancia_historico={a['concordancia_historico']} | "
          f"acerto_validado={a['acerto_validado']}")
    print(f"saida={SAIDA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
