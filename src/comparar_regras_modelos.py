#!/usr/bin/env python3
"""Verifica a reproducao da comparacao entre regras preventivas e modelos.

Ferramenta estritamente READ-ONLY e fail-closed. Nao treina nem retreina
nenhum modelo: reaproveita as predicoes *out-of-fold* congeladas do Passo 4 e
a implementacao historica de `regras_preventivas.py`, e usa a planilha viva
apenas para recuperar o texto dos IDs ja avaliados naquela rodada.

O papel deste script mudou: ele nao regenera mais o baseline canonico, e sim
VERIFICA que a planilha viva, nas partes que importam para esta rota, ainda
reproduz o resultado cientifico congelado em
`docs/dados/regras_versus_modelos.json`. Sao cinco gates, nesta ordem:

  1. o artefato congelado `--esperado` bate por SHA-256 (CRLF->LF);
  2. o CSV de predicoes `--predicoes` bate por SHA-256 (CRLF->LF) e tem a
     estrutura esperada (13.972 IDs, sete modelos, dobras 1..5);
  3. `src/regras_preventivas.py` bate com o blob Git historico da rodada
     canonica (commit 9ceb5e76...);
  4. o texto vivo dos IDs congelados, uma vez recalculado em grupo textual
     normalizado, reproduz `HASH_CORPUS_ESPERADO` junto com o id_sha256 e a
     referencia humana -- que vem exclusivamente do CSV congelado, nunca da
     planilha viva;
  5. o nucleo cientifico recalculado bate, campo a campo, com o artefato
     congelado.

Os gates 1-3 rodam ANTES de abrir a planilha; qualquer divergencia interrompe
a execucao sem nenhum acesso ao Google Sheets. Os gates 4-5 rodam DEPOIS,
sobre o texto vivo ja lido: o gate 4 confere o fingerprint do corpus antes de
aplicar qualquer regra, e o gate 5, o ultimo, compara o resultado cientifico
recalculado com o congelado. Uma divergencia em qualquer gate interrompe a
execucao antes de escrever qualquer coisa. Este script nunca escreve
`docs/dados/regras_versus_modelos.json` nem `docs/REGRAS_VERSUS_MODELOS.md`:
atualizar esse baseline exige decisao humana e edicao consciente, nunca uma
consequencia automatica de rodar este verificador.

NOTA METODOLOGICA. Este gate NAO seria suficiente para reproduzir a LSTM,
porque nao congela o model-input bruto entregue ao Tokenizer. Mas esta rota
nao treina LSTM: ela reaproveita a predicao ja registrada no CSV congelado.
A regra de `regras_preventivas.py` normaliza Unicode/acentos, caixa e
whitespace, e o grupo textual e construido sobre os mesmos quatro campos
individualmente normalizados. Para a finalidade estreita desta rota --
aplicar uma regra deterministica sobre texto -- igualdade do grupo
normalizado garante a identidade textual relevante. Essa conclusao nao se
estende a modelos de aprendizado de maquina.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import construir_grupos_textuais as cgt  # noqa: E402
import planilha as pl  # noqa: E402
import regras_preventivas as rp  # noqa: E402
import retreinar_modelos_canonicos as rmc  # noqa: E402
import tipo_manutencao as tm  # noqa: E402
import verificar_artigo_congelado as vac  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
PREDICOES_PADRAO = RAIZ / "docs" / "dados" / "retreino_canonico_predicoes.csv"
ESPERADO_PADRAO = RAIZ / "docs" / "dados" / "regras_versus_modelos.json"
REGRAS_PREVENTIVAS_PATH = RAIZ / "src" / "regras_preventivas.py"

# Identidades historicas da rodada canonica final (commit 9ceb5e76...).
# Constantes fixas, nunca derivadas da planilha nem da execucao atual.
HASH_CORPUS_ESPERADO = (
    "1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a")
PREDICOES_SHA256_ESPERADO = (
    "ab1d45355ff2d359b5023dd2ccb580a8b407a9f4a575fb51180fdfa975a9d5a6")
REGRAS_PREVENTIVAS_BLOB_SHA1_ESPERADO = (
    "6cffcf220d7bba45dc1f6f589086557ebb191adb")
RESULTADO_SHA256_ESPERADO = (
    "ee3e6f574ef83c246e0200959ffaa122970de70d33aafb469b45610b8f35c789")

CORPUS_MODELAGEM_ESPERADO = 13972
DOBRAS_VALIDAS = frozenset({1, 2, 3, 4, 5})
MODELOS_ESPERADOS = frozenset({
    "naive_bayes", "regressao_logistica", "linear_svc", "sgd",
    "extra_trees", "random_forest", "lstm",
})

NUCLEO_CIENTIFICO_CHAVES = (
    "schema_version", "status", "protocolo", "corpus", "regra", "modelos",
    "modelos_com_ganho_de_macro_f1", "problemas",
)


def git_blob_sha1_lf(caminho: Path) -> str:
    """SHA-1 de blob Git do conteudo, apos normalizar SOMENTE CRLF->LF.

    Reproduz `git hash-object`: monta o cabecalho `blob <tamanho>\\0` sobre os
    bytes normalizados e calcula SHA-1. A normalizacao de fim de linha existe
    pelo mesmo motivo de `verificar_artigo_congelado.sha256_lf_normalizado`:
    tornar o hash independente de core.autocrlf.
    """
    dados = caminho.read_bytes().replace(b"\r\n", b"\n")
    cabecalho = f"blob {len(dados)}\0".encode("utf-8")
    return hashlib.sha1(cabecalho + dados).hexdigest()  # noqa: S324


def carregar_predicoes(caminho: Path) -> dict[str, Any]:
    """Le o CSV do Passo 4 e agrupa por modelo, preservando a referencia."""
    referencia: dict[str, str] = {}
    dobra: dict[str, int] = {}
    por_modelo: dict[str, dict[str, str]] = defaultdict(dict)
    with caminho.open("r", encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            chave = linha["id_sha256"]
            referencia[chave] = linha["referencia_humana"]
            dobra[chave] = int(linha["dobra"])
            por_modelo[linha["modelo"]][chave] = linha["previsto"]
    return {"referencia": referencia, "dobra": dobra,
            "por_modelo": dict(por_modelo)}


def validar_estrutura_predicoes(dados: dict[str, Any]) -> list[str]:
    """Defesa adicional: o arquivo exato ja e protegido por hash (Gate 2),
    mas a estrutura tambem e conferida para que um mismatch de conteudo com
    hash coincidente (improvavel, mas nao impossivel de se debugar) produza
    um diagnostico legivel em vez de uma falha silenciosa mais adiante.
    """
    problemas: list[str] = []
    chaves = set(dados["referencia"])

    if len(chaves) != CORPUS_MODELAGEM_ESPERADO:
        problemas.append(
            f"predicoes: {len(chaves)} IDs unicos, esperado "
            f"{CORPUS_MODELAGEM_ESPERADO}")

    sem_referencia = [c for c in chaves if not dados["referencia"].get(c)]
    if sem_referencia:
        problemas.append(
            f"predicoes: {len(sem_referencia)} IDs sem referencia_humana")

    dobras_invalidas = {v for v in dados["dobra"].values()
                        if v not in DOBRAS_VALIDAS}
    if dobras_invalidas:
        problemas.append(
            f"predicoes: dobras invalidas encontradas: {sorted(dobras_invalidas)}")

    modelos_obtidos = frozenset(dados["por_modelo"])
    if modelos_obtidos != MODELOS_ESPERADOS:
        problemas.append(
            f"predicoes: modelos obtidos={sorted(modelos_obtidos)}, "
            f"esperado={sorted(MODELOS_ESPERADOS)}")

    for nome, preds in dados["por_modelo"].items():
        cobertura = set(preds)
        if cobertura != chaves:
            faltantes = len(chaves - cobertura)
            extras = len(cobertura - chaves)
            problemas.append(
                f"predicoes: modelo '{nome}' nao cobre os mesmos IDs "
                f"(faltam {faltantes}, sobram {extras})")

    return problemas


def carregar_textos_e_grupos(
        sh, config: dict[str, Any],
        chaves_esperadas: set[str]) -> tuple[dict[str, str], dict[str, str], list[str]]:
    """Texto vivo e grupo textual recalculado, indexados pelo SHA-256 do ID.

    So os IDs em `chaves_esperadas` (os 13.972 da rodada congelada) sao
    retidos; qualquer outra linha da planilha viva e ignorada e nao entra no
    fingerprint. Bloqueia ID congelado duplicado na base viva e reporta, ao
    final, IDs congelados sem texto correspondente.
    """
    textos: dict[str, str] = {}
    grupos: dict[str, str] = {}
    problemas: list[str] = []

    for r in cgt.ler_registros(sh, config):
        id_chamado = r.get("id", "")
        if not id_chamado:
            continue
        chave = hashlib.sha256(id_chamado.encode("utf-8")).hexdigest()
        if chave not in chaves_esperadas:
            continue
        if chave in textos:
            problemas.append(f"ID congelado duplicado na base viva: {chave[:12]}...")
            continue
        normalizados = [cgt.normalizar_texto(r.get(c, ""))
                        for c in cgt.CAMPOS_TEXTUAIS]
        textos[chave] = rmc.montar_texto(r)
        grupos[chave] = cgt.hash_grupo(normalizados)

    faltantes = chaves_esperadas - set(textos)
    if faltantes:
        problemas.append(
            f"{len(faltantes)} ID(s) congelado(s) sem texto na base viva")

    return textos, grupos, problemas


def calcular_hash_corpus(chaves: list[str], grupos: dict[str, str],
                         referencia_congelada: dict[str, str]) -> str:
    """Fingerprint do corpus efetivamente usado: id_sha256 + grupo textual
    recalculado do texto vivo + referencia humana CONGELADA do CSV.

    A referencia vem exclusivamente do CSV de predicoes, nunca de
    `cgt.referencia_humana(registro_vivo)`: e por isso que uma referencia
    diferente na planilha viva nao pode alterar este hash.
    """
    itens = sorted(
        (chave, grupos[chave], referencia_congelada[chave])
        for chave in chaves
    )
    return cgt._sha256_json([list(item) for item in itens])


def _metricas(verdade: list[str], predito: list[str],
              categorias: list[str]) -> dict[str, float]:
    from sklearn.metrics import balanced_accuracy_score, f1_score
    if not verdade:
        return {"n": 0, "acuracia": 0.0, "macro_f1": 0.0, "balanced_accuracy": 0.0}
    certos = sum(1 for a, b in zip(verdade, predito) if a == b)
    return {
        "n": len(verdade),
        "acuracia": round(certos / len(verdade), 4),
        "macro_f1": round(float(f1_score(verdade, predito, labels=categorias,
                                         average="macro", zero_division=0)), 4),
        "balanced_accuracy": round(float(balanced_accuracy_score(verdade, predito)), 4),
    }


def comparar(chaves: list[str], referencia: dict[str, str],
             textos: dict[str, str], predicoes: dict[str, str],
             categorias_permitidas: set[str]) -> dict[str, Any]:
    """Mede modelo puro e hibrido nos mesmos registros.

    O hibrido substitui a predicao do modelo somente onde a regra dispara. Onde
    a regra se abstem, as duas configuracoes sao identicas por construcao, e e
    justamente por isso que o denominador se mantem igual.
    """
    categorias = sorted({referencia[c] for c in chaves})
    verdade = [referencia[c] for c in chaves]
    puro = [predicoes.get(c, "") for c in chaves]

    hibrido: list[str] = []
    disparos = 0
    conflitos: list[dict[str, str]] = []
    for chave, previsto_modelo in zip(chaves, puro):
        resultado = rp.aplicar(textos.get(chave, ""), categorias_permitidas)
        proposta = resultado["categoria"]
        if not proposta:
            hibrido.append(previsto_modelo)
            continue
        disparos += 1
        hibrido.append(str(proposta))
        if proposta != previsto_modelo:
            conflitos.append({
                "referencia": referencia[chave],
                "modelo": previsto_modelo,
                "regra": str(proposta),
            })

    # Quem acerta quando regra e modelo divergem. E a unica leitura que
    # justifica manter ou descartar a camada explicita.
    regra_certa = sum(1 for c in conflitos if c["regra"] == c["referencia"])
    modelo_certo = sum(1 for c in conflitos if c["modelo"] == c["referencia"])
    ambos_errados = len(conflitos) - regra_certa - modelo_certo

    # Recorte dos chamados cuja referencia e preventiva, onde a camada deveria
    # concentrar todo o seu efeito.
    idx_prev = [i for i, chave in enumerate(chaves)
                if tm.tipo_manutencao(referencia[chave]) == tm.PREVENTIVA]
    m_puro = _metricas(verdade, puro, categorias)
    m_hibrido = _metricas(verdade, hibrido, categorias)
    p_puro = _metricas([verdade[i] for i in idx_prev],
                       [puro[i] for i in idx_prev], categorias)
    p_hibrido = _metricas([verdade[i] for i in idx_prev],
                          [hibrido[i] for i in idx_prev], categorias)

    return {
        "global": {"modelo_puro": m_puro, "hibrido": m_hibrido,
                   "delta_acuracia": round(m_hibrido["acuracia"] - m_puro["acuracia"], 4),
                   "delta_macro_f1": round(m_hibrido["macro_f1"] - m_puro["macro_f1"], 4)},
        "preventivos": {"modelo_puro": p_puro, "hibrido": p_hibrido,
                        "delta_acuracia": round(p_hibrido["acuracia"] - p_puro["acuracia"], 4),
                        "delta_macro_f1": round(p_hibrido["macro_f1"] - p_puro["macro_f1"], 4)},
        "regra": {
            "disparos": disparos,
            "cobertura": round(disparos / len(chaves), 4) if chaves else 0.0,
            "conflitos_com_o_modelo": len(conflitos),
            "conflitos_em_que_a_regra_acerta": regra_certa,
            "conflitos_em_que_o_modelo_acerta": modelo_certo,
            "conflitos_em_que_ambos_erram": ambos_errados,
        },
    }


def montar_relatorio(chaves: list[str], referencia: dict[str, str],
                     textos: dict[str, str],
                     por_modelo: dict[str, dict[str, str]]) -> dict[str, Any]:
    categorias_permitidas = {referencia[c] for c in chaves}
    fora_do_alcance = sorted(rp.categorias_alvo() - categorias_permitidas)
    resultados = {nome: comparar(chaves, referencia, textos, preds,
                                 categorias_permitidas)
                  for nome, preds in sorted(por_modelo.items())}

    ganham = [n for n, r in resultados.items() if r["global"]["delta_macro_f1"] > 0]
    problemas = {
        "registros_sem_texto": sum(1 for c in chaves if not textos.get(c)),
        "modelos_comparados": len(resultados),
    }
    return {
        "schema_version": 1,
        "status": "concluido",
        "protocolo": ("regra aplicada sobre as predicoes out-of-fold do Passo 4, "
                      "nos mesmos registros e nas mesmas particoes; a referencia "
                      "humana nao e alterada em nenhuma configuracao"),
        "corpus": {
            "registros": len(chaves),
            "categorias": len(categorias_permitidas),
            "preventivos_na_referencia": sum(
                1 for c in chaves
                if tm.tipo_manutencao(referencia[c]) == tm.PREVENTIVA),
        },
        "regra": {
            "criterio": ("dispara somente com termo de periodicidade e termo de "
                         "equipamento no mesmo chamado; abstem-se caso contrario"),
            "termos_periodicidade": len(rp.TERMOS_PERIODICIDADE),
            "termos_equipamento": len(rp.TERMOS_EQUIPAMENTO),
            "categorias_alvo": len(rp.categorias_alvo()),
            "categorias_alvo_fora_do_conjunto_avaliado": fora_do_alcance,
            "modulo": "src/regras_preventivas.py",
        },
        "modelos": resultados,
        "modelos_com_ganho_de_macro_f1": sorted(ganham),
        "problemas": problemas,
    }


def nucleo_cientifico(relatorio: dict[str, Any]) -> dict[str, Any]:
    """Recorte comparavel do relatorio: exclui metadados de proveniencia
    (gerado_em, script_origem) que variam a cada execucao sem representar
    mudanca no resultado cientifico.
    """
    return {chave: relatorio[chave] for chave in NUCLEO_CIENTIFICO_CHAVES
            if chave in relatorio}


def renderizar_markdown(relatorio: dict[str, Any]) -> str:
    corpus = relatorio["corpus"]
    regra = relatorio["regra"]
    linhas = [
        "# Regras preventivas contra modelos puros",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.",
        "",
        f"**Gerado em:** {relatorio.get('gerado_em', 'não informado')}",
        "",
        "## Protocolo",
        "",
        f"- {relatorio['protocolo']}.",
        f"- Registros: {corpus['registros']}, em {corpus['categorias']} categorias, "
        f"dos quais {corpus['preventivos_na_referencia']} têm referência preventiva.",
        f"- Regra: {regra['criterio']}.",
        f"- Tabela com {regra['termos_periodicidade']} termos de periodicidade e "
        f"{regra['termos_equipamento']} de equipamento, em `{regra['modulo']}`.",
        "",
        "## Efeito global",
        "",
        "| Modelo | Acurácia pura | Acurácia híbrida | Δ | Macro-F1 puro | Macro-F1 híbrido | Δ |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for nome, r in sorted(relatorio["modelos"].items(),
                          key=lambda kv: -kv[1]["global"]["hibrido"]["macro_f1"]):
        g = r["global"]
        linhas.append(
            f"| {nome} | {g['modelo_puro']['acuracia']} | {g['hibrido']['acuracia']} | "
            f"{g['delta_acuracia']:+} | {g['modelo_puro']['macro_f1']} | "
            f"{g['hibrido']['macro_f1']} | {g['delta_macro_f1']:+} |")

    linhas += [
        "",
        "## Efeito nos chamados de referência preventiva",
        "",
        "| Modelo | Acurácia pura | Acurácia híbrida | Δ |",
        "|---|---:|---:|---:|",
    ]
    for nome, r in sorted(relatorio["modelos"].items()):
        p = r["preventivos"]
        linhas.append(
            f"| {nome} | {p['modelo_puro']['acuracia']} | {p['hibrido']['acuracia']} | "
            f"{p['delta_acuracia']:+} |")

    linhas += [
        "",
        "## Conflitos entre regra e modelo",
        "",
        "| Modelo | Disparos | Conflitos | Regra acerta | Modelo acerta | Ambos erram |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for nome, r in sorted(relatorio["modelos"].items()):
        c = r["regra"]
        linhas.append(
            f"| {nome} | {c['disparos']} | {c['conflitos_com_o_modelo']} | "
            f"{c['conflitos_em_que_a_regra_acerta']} | "
            f"{c['conflitos_em_que_o_modelo_acerta']} | "
            f"{c['conflitos_em_que_ambos_erram']} |")

    ganham = relatorio["modelos_com_ganho_de_macro_f1"]
    linhas += [
        "",
        "## Leitura",
        "",
        (f"A camada híbrida melhora o macro-F1 de {len(ganham)} dos "
         f"{len(relatorio['modelos'])} modelos"
         + (f": {', '.join(ganham)}." if ganham else ".")),
        "",
        "A regra dispara no mesmo conjunto de registros para todos os modelos, "
        "porque depende apenas do texto. O que varia entre as linhas é a predição "
        "que ela substitui, e por isso o mesmo conjunto de regras ajuda um modelo "
        "e pode prejudicar outro.",
        "",
        "## Proveniência",
        "",
        "- Predições: `docs/dados/retreino_canonico_predicoes.csv`, Passo 4.",
        "- Regras: `src/regras_preventivas.py`.",
        "- Script: `src/comparar_regras_modelos.py`.",
        "- Nenhuma escrita foi realizada na planilha.",
        "",
    ]
    return "\n".join(linhas)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--predicoes", type=Path, default=PREDICOES_PADRAO,
                   help="CSV de predicoes out-of-fold congeladas (default: "
                        "docs/dados/retreino_canonico_predicoes.csv).")
    p.add_argument("--esperado", type=Path, default=ESPERADO_PADRAO,
                   help="Resultado cientifico congelado a reproduzir (default: "
                        "docs/dados/regras_versus_modelos.json).")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    # Gate 1: artefato congelado (resultado cientifico esperado).
    if not args.esperado.exists():
        print(f"Resultado congelado nao encontrado em {args.esperado}.",
              file=sys.stderr)
        return 2
    sha_resultado = vac.sha256_lf_normalizado(args.esperado)
    if sha_resultado != RESULTADO_SHA256_ESPERADO:
        print(
            "Resultado congelado divergente do esperado; verificacao "
            "interrompida antes de abrir a planilha.\n"
            f"obtido:   {sha_resultado}\n"
            f"esperado: {RESULTADO_SHA256_ESPERADO}",
            file=sys.stderr,
        )
        return 2
    relatorio_congelado = json.loads(args.esperado.read_text(encoding="utf-8"))

    # Gate 2: predicoes congeladas.
    if not args.predicoes.exists():
        print(f"Predicoes nao encontradas em {args.predicoes}.", file=sys.stderr)
        return 2
    sha_predicoes = vac.sha256_lf_normalizado(args.predicoes)
    if sha_predicoes != PREDICOES_SHA256_ESPERADO:
        print(
            "Predicoes congeladas divergentes do esperado; verificacao "
            "interrompida antes de abrir a planilha.\n"
            f"obtido:   {sha_predicoes}\n"
            f"esperado: {PREDICOES_SHA256_ESPERADO}",
            file=sys.stderr,
        )
        return 2
    dados = carregar_predicoes(args.predicoes)
    problemas_predicoes = validar_estrutura_predicoes(dados)
    if problemas_predicoes:
        print("Estrutura das predicoes divergente do esperado:", file=sys.stderr)
        for p in problemas_predicoes:
            print(f"  - {p}", file=sys.stderr)
        return 2

    # Gate 3: implementacao historica das regras.
    blob_obtido = git_blob_sha1_lf(REGRAS_PREVENTIVAS_PATH)
    if blob_obtido != REGRAS_PREVENTIVAS_BLOB_SHA1_ESPERADO:
        print(
            "src/regras_preventivas.py divergente do blob historico da "
            "rodada canonica; verificacao interrompida antes de abrir a "
            "planilha.\n"
            f"obtido:   {blob_obtido}\n"
            f"esperado: {REGRAS_PREVENTIVAS_BLOB_SHA1_ESPERADO}",
            file=sys.stderr,
        )
        return 2

    chaves = sorted(dados["referencia"])
    config = json.loads(args.config.read_text(encoding="utf-8"))
    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    textos, grupos, problemas_texto = carregar_textos_e_grupos(
        sh, config, set(chaves))
    if problemas_texto:
        print("Texto vivo divergente do esperado:", file=sys.stderr)
        for p in problemas_texto:
            print(f"  - {p}", file=sys.stderr)
        return 2

    # Gate 4: hash do corpus final, com referencia exclusivamente do CSV.
    impressao = calcular_hash_corpus(chaves, grupos, dados["referencia"])
    if impressao != HASH_CORPUS_ESPERADO:
        print(
            "Corpus divergente do ARTIGO_CONGELADO: verificacao interrompida "
            "antes de aplicar as regras.\n"
            f"hash obtido:   {impressao}\n"
            f"hash esperado: {HASH_CORPUS_ESPERADO}",
            file=sys.stderr,
        )
        return 2

    relatorio = montar_relatorio(chaves, dados["referencia"], textos,
                                 dados["por_modelo"])

    # Gate 5: resultado cientifico recalculado precisa reproduzir o congelado.
    nucleo_atual = nucleo_cientifico(relatorio)
    nucleo_congelado = nucleo_cientifico(relatorio_congelado)
    if nucleo_atual != nucleo_congelado:
        print(
            "Resultado cientifico recalculado diverge do congelado em "
            "docs/dados/regras_versus_modelos.json; nenhum artefato foi "
            "alterado.",
            file=sys.stderr,
        )
        return 2

    relatorio["gerado_em"] = agora_bahia()
    relatorio["script_origem"] = "src/comparar_regras_modelos.py"
    print(
        "OK: reproducao confirmada. Corpus, predicoes, implementacao das "
        "regras e resultado cientifico batem com o baseline congelado "
        f"(hash_corpus={HASH_CORPUS_ESPERADO})."
    )
    print(renderizar_markdown(relatorio))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
