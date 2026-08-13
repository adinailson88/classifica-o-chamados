#!/usr/bin/env python3
"""[FASE2B-REPLAY-RECOVER] Verificacao auditavel do bundle do REPLAY CONGELADO.

Ferramenta estritamente READ-ONLY e de ZERO FITS, exclusiva do marcador
`[FASE2B-REPLAY-RECOVER]`. Nao treina nenhum modelo, nao escreve em nenhuma
planilha (nem a operacional, nem a privada do bundle), nao configura
`REPLAY_SPREADSHEET_ID` e nao pina `REPLAY_INPUT_SHA256_ESPERADO` em
`ensemble_fase2b_crossfit.py`.

DESENHO:

    BASE ONLINE ATUAL (so texto bruto) + ALLOWLIST_GRUPO_A + ALLOWLIST_GRUPO_B
    + H/R/grupo/fold CONGELADOS -> validacao cientifica compartilhada
    (`ensemble_fase2b_crossfit.validar_bundle_replay`) + replay_input_sha256.

1. NUNCA compara a base online inteira contra nenhuma revisao historica do
   Google Drive. Este modulo nao chama a Drive Revisions API: fazer isso
   transformaria uma revisao pontual em baseline IMPLICITA sobre qualquer
   registro que tenha mudado desde entao (correcoes humanas legitimas
   incluidas), nao apenas os poucos que realmente vazaram para a Execucao
   Cientifica 1. O unico patch aplicado vem de uma ALLOWLIST EXPLICITA,
   indexada por `id_sha256` (nunca ID bruto de chamado — ver `aplicar_
   allowlist`): para cada registro da base atual, se `id_sha256` estiver na
   allowlist, aplica so os campos listados, e so quando o valor atual
   difere do valor historico comprovado; senao, preserva EXATAMENTE o
   valor atual. Nenhum outro registro/campo e tocado.

2. `ALLOWLIST_GRUPO_A` (os 4 registros da Execucao Cientifica 1) e
   `ALLOWLIST_GRUPO_B` (3 drifts adicionais) sao ambos indexados por
   id_sha256 = sha256(id_bruto.encode("utf-8")).hexdigest() — o ID bruto
   do chamado nunca aparece em nenhum arquivo versionado deste
   repositorio. Os valores do GRUPO A sao strings vazias ("", ver
   ALLOWLIST_GRUPO_A abaixo) — nao sao texto sensivel, por isso ficam
   diretamente no codigo. Os valores do GRUPO B contem texto bruto de
   chamados (titulo/descricao): NUNCA sao escritos em texto puro neste
   arquivo, que e publico. Sao carregados via `carregar_allowlist_
   grupo_b()`, mesma convencao de `planilha.id_planilha`/`replay_bundle.
   id_replay_spreadsheet()` — variavel de ambiente (Secret no CI) ->
   arquivo local gitignored -> erro.

   PROVENIENCIA: os pares id_sha256/campo do GRUPO A foram fornecidos
   diretamente pelo operador humano nesta sessao, como resultado de uma
   auditoria independente externa a este repositorio. Nenhum commit,
   documento, teste ou artefato DESTE repositorio identifica esses 4
   registros de forma verificavel por quem so tem acesso ao codigo (uma
   busca exaustiva anterior nao encontrou nada — ver historico da
   sessao). Portanto, ao contrario dos 5 hashes metodologicos (que
   qualquer leitor pode reproduzir a partir de artefatos versionados),
   este allowlist especifico depende de confianca no atestado do
   operador/auditoria externa, nao de proveniencia interna ao repositorio.
   Fica registrado aqui para que qualquer revisor futuro saiba
   exatamente que tipo de evidencia embasa este patch.

3. NUNCA usa `ensemble_fase2b_crossfit.gate_zero()` (o gate da fonte ONLINE
   VIVA — recalcula referencia_humana/alvo_inadequacao a partir das colunas
   M/Q atuais da planilha, correto para autorizar um NOVO congelamento, mas
   errado aqui: o RECOVER nao cria baseline nova, reproduz o INPUT
   CONGELADO da Execucao Cientifica 1). H (`categoria_historica`) e R
   (`referencia_humana`) vem DIRETAMENTE de `docs/dados/ensemble/
   alvo_ensemble.json` (o alvo ja congelado); grupo_sha256 e outer_fold vem
   DIRETAMENTE de `docs/dados/particoes_canonicas_mapa.csv` (as particoes ja
   congeladas) — nunca recalculados a partir de M/Q ou de texto atual. So o
   texto bruto (titulo/descricao_glpi/titulo_osm/descricao_osm) vem da base
   online + allowlists. Ver `montar_bundle`.

4. So depois do bundle montado, valida `grupo_sha256` recomputado do texto
   patcheado contra o grupo_sha256 CONGELADO (`replay_bundle.
   validar_grupos_por_registro`, reusada sem duplicar) e roda a mesma logica
   cientifica de `gate_zero_replay()` — extraida para
   `ensemble_fase2b_crossfit.validar_bundle_replay()` e compartilhada pelos
   dois — comparando contra o hash CANDIDATO (nao o pinado de producao, que
   continua None).

5. NUNCA publica o bundle bruto: nao escreve replay_bundle_candidato.csv em
   disco, nao imprime titulo/descricao/ID bruto em log nem no diagnostico.
   `recover_diagnostico.json` (unico artifact do job) so contem hashes,
   contagens, id_sha256, grupo_sha256, nomes de campo e status —
   `bundle_publicado` fica SEMPRE False; esta rotina nunca exporta o
   bundle, so verifica e reporta.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ensemble_fase2b_crossfit as efc  # noqa: E402
import construir_grupos_textuais as cgt  # noqa: E402
import recongelar_ensemble_online as rero  # noqa: E402
import replay_bundle as rb  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
SAIDA_DIR_PADRAO = RAIZ / "docs" / "dados" / "ensemble" / "replay"
NOME_DIAGNOSTICO = "recover_diagnostico.json"

# Hash do bundle candidato, ja validado localmente em sessao anterior (ver
# docs/dados/ensemble/replay/bundle_manifesto.json). Repetido aqui como
# padrao apenas para conveniencia de CLI; nunca e escrito em
# ensemble_fase2b_crossfit.py (REPLAY_INPUT_SHA256_ESPERADO permanece None).
REPLAY_INPUT_SHA256_ESPERADO_CANDIDATO = (
    "79b70349ad7f73568ef0f5eabb54dd91477c4bff3eefc5c272bcee0a7c021de1"
)

BLOQUEADOR_GRUPO_A_AUSENTE = "quatro_registros_originais_nao_identificados"

# --------------------------------------------------------------------------
# Allowlist EXPLICITA de patches, indexada por id_sha256. Nunca "toda
# divergencia contra uma revisao historica".
# --------------------------------------------------------------------------

# GRUPO A — os 4 registros originais restaurados na reconstrucao candidata
# que reproduziu replay_input_sha256 = 79b70349... (ver docs/dados/
# ensemble/replay/bundle_manifesto.json). Proveniencia: atestado do
# operador humano + auditoria independente externa a este repositorio (ver
# docstring do modulo, item 2) — nao ha, dentro deste repositorio, nenhum
# commit/arquivo que corrobore esses 4 pares id_sha256/campo de forma
# independente. Os valores sao strings vazias: nao sao texto sensivel.
ALLOWLIST_GRUPO_A: dict[str, dict[str, str]] = {
    "1b1e541d103df59767dedb8e899043e09cbf580c17bb962174cc8eb6eef7c1aa": {
        "titulo_osm": "",
        "descricao_osm": "",
    },
    "441a70841acab28f41659a79a3e802ab69c0890a1567047d997beefbf849ff7b": {
        "descricao_glpi": "",
    },
    "1cb0fa284bd3556610ff4a7c5f98e349ebdde0e9743bd51dc03be40ee99323f2": {
        "descricao_glpi": "",
    },
    "79b7e901127de702822b92f706c0512fc3d20d266226c5037b02fae029bce7dd": {
        "descricao_glpi": "",
    },
}

# GRUPO B — 3 drifts adicionais, indexados por id_sha256. Os IDS abaixo sao
# SOMENTE os id_sha256 (nunca o ID bruto do chamado); os valores textuais
# historicos comprovados vem exclusivamente de `carregar_allowlist_grupo_b`
# (Secret/arquivo local, nunca deste arquivo).
IDS_SHA256_GRUPO_B = (
    "f9aece7ddad1b121c053107943f5e8d9eea777609cc8c39417ff6b05fb5ec72f",
    "225a8bcf4910f252639ec83895be156492b89a36ec6e3ab523d4abb87477bd66",
    "c56dd685c1898fd8e0f2c55918500b07af18fe795426e5223b16372050aee3d4",
)

ALLOWLIST_GRUPO_B_ENV = "FASE2B_ALLOWLIST_GRUPO_B_JSON"
ALLOWLIST_GRUPO_B_LOCAL = RAIZ / "replay_allowlist_grupo_b.local.json"


def carregar_allowlist_grupo_b() -> dict[str, dict[str, str]]:
    """GRUPO B: 3 drifts adicionais, com valor historico ja comprovado.
    Contem texto bruto de chamados (titulo/descricao) — por isso NUNCA e
    escrito em texto puro neste arquivo, que e publico. Mesma cadeia de
    `planilha.id_planilha`/`replay_bundle.id_replay_spreadsheet`: variavel
    de ambiente (Secret no CI) -> arquivo local gitignored -> erro.

    Formato esperado (JSON): {id_sha256: {campo_textual: valor_historico}},
    chaves EXATAMENTE `IDS_SHA256_GRUPO_B` (nunca ID bruto), valores
    somente com campos de `construir_grupos_textuais.CAMPOS_TEXTUAIS`."""
    env = os.getenv(ALLOWLIST_GRUPO_B_ENV)
    if env and env.strip():
        return json.loads(env)
    if ALLOWLIST_GRUPO_B_LOCAL.exists():
        return json.loads(ALLOWLIST_GRUPO_B_LOCAL.read_text(encoding="utf-8"))
    raise RuntimeError(
        "Allowlist do GRUPO B nao definida. Configure o Secret/variavel "
        f"{ALLOWLIST_GRUPO_B_ENV} (CI) ou crie o arquivo "
        f"{ALLOWLIST_GRUPO_B_LOCAL.name} na raiz (uso local, gitignored)."
    )


class RecuperacaoBloqueada(RuntimeError):
    """Bloqueio explicito: qualquer divergencia estrutural/hashes, ou
    inconsistencia interna. Nunca contornado."""


# --------------------------------------------------------------------------
# Aplicacao da allowlist (pura, testavel sem rede)
# --------------------------------------------------------------------------

def montar_allowlist(
    grupo_a: dict[str, dict[str, str]], grupo_b: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    """Junta os dois grupos (ambos indexados por id_sha256). Nao ha logica
    alem de uniao por chave — cada grupo ja e uma allowlist explicita e
    independente."""
    allowlist: dict[str, dict[str, str]] = {}
    for grupo in (grupo_a, grupo_b):
        for id_sha256, campos in grupo.items():
            allowlist.setdefault(id_sha256, {}).update(campos)
    return allowlist


def aplicar_allowlist(
    atuais: list[dict[str, str]],
    allowlist: dict[str, dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, list[str]]]:
    """Para cada registro de `atuais`: calcula id_sha256 = sha256(id bruto);
    se estiver na allowlist E algum campo do registro divergir do valor
    historico comprovado, aplica SOMENTE esse(s) campo(s). Qualquer
    registro/campo fora da allowlist — ou cujo valor atual ja bate com o
    comprovado — permanece EXATAMENTE como estava. So toca campos de
    `construir_grupos_textuais.CAMPOS_TEXTUAIS`; qualquer outra chave de
    uma entrada da allowlist e ignorada.

    Devolve (registros_patcheados, {id_sha256: [campos_efetivamente_
    alterados]}) — o segundo valor nunca contem os VALORES, so os NOMES dos
    campos, para permitir diagnostico sanitizado."""
    aplicados: dict[str, list[str]] = {}
    resultado: list[dict[str, str]] = []
    for r in atuais:
        id_bruto = r.get("id", "")
        if not id_bruto:
            resultado.append(r)
            continue
        id_sha256 = hashlib.sha256(id_bruto.encode("utf-8")).hexdigest()
        patch = allowlist.get(id_sha256)
        if not patch:
            resultado.append(r)
            continue
        novo = dict(r)
        alterados = []
        for campo, valor_comprovado in patch.items():
            if campo not in cgt.CAMPOS_TEXTUAIS:
                continue
            if novo.get(campo, "") != valor_comprovado:
                novo[campo] = valor_comprovado
                alterados.append(campo)
        if alterados:
            aplicados[id_sha256] = sorted(alterados)
        resultado.append(novo)
    return resultado, aplicados


# --------------------------------------------------------------------------
# Verificacoes estruturais (particoes/alvo congelado vs. base online) —
# NUNCA envolvem H/R atuais: so contagens, folds e presenca/duplicidade de
# id_sha256. `r_divergentes`/`y_divergentes` (que `recongelar_ensemble_
# online.montar_diagnostico` tambem calcularia) sao DELIBERADAMENTE
# ignorados aqui — comparar R/Y atuais contra o congelado e exatamente o
# que `gate_zero()` faz para autorizar um NOVO congelamento; o RECOVER nao
# cria baseline nova, entao R/Y atuais nunca bloqueiam esta rotina (ver
# docstring do modulo, item 3).
# --------------------------------------------------------------------------

CAMPOS_DIAGNOSTICO_COBERTURA_PERMITIDOS = (
    "total_ids_particoes", "total_ids_alvo_congelado",
    "total_ids_particao_sem_alvo", "amostra_ids_particao_sem_alvo",
    "total_ids_alvo_sem_particao", "amostra_ids_alvo_sem_particao",
    "folds_particao", "folds_alvo_congelado",
    "total_dobra_historica_divergente", "amostra_dobra_historica_divergente",
    "bloqueios",
)


def validar_estrutura_congelada(
    registros_patched: list[dict[str, str]],
    particoes: dict[str, dict[str, Any]],
    alvo_congelado: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Exige, SEM tocar em R/Y atuais: particoes e alvo_congelado descrevem
    o mesmo universo de exatamente `rero.TOTAL_ESPERADO` IDs, com a mesma
    dobra por ID nas duas fontes (reusa `rero.validar_cobertura_particoes_
    alvo`, sem duplicar); e a base online patcheada, restrita a esse
    universo, nao tem ID duplicado nem ID faltante, e cobre exatamente esse
    mesmo conjunto de id_sha256 (reusa `rero.montar_base_atual` so pela
    contabilidade de cobertura online — os campos H/R que essa funcao
    tambem calcula internamente sao ignorados aqui, nunca usados). Devolve
    um diagnostico 100% sanitizado (contagens/folds/id_sha256) e a lista
    `bloqueios` (vazia se estrutura ok)."""
    cobertura = rero.validar_cobertura_particoes_alvo(
        particoes, alvo_congelado,
        total_esperado=rero.TOTAL_ESPERADO,
        folds_esperados=rero.FOLDS_ESPERADOS_PADRAO,
    )
    diagnostico = {
        campo: valor for campo, valor in cobertura.items()
        if campo in CAMPOS_DIAGNOSTICO_COBERTURA_PERMITIDOS
    }
    bloqueios = list(cobertura["bloqueios"])

    base_info = rero.montar_base_atual(registros_patched, particoes)
    faltantes_no_online = sorted(base_info["faltantes_no_online"])
    duplicados_no_online = sorted(base_info["ids_duplicados_no_online"])
    ids_online_no_corpus = set(base_info["base"])

    diagnostico["total_faltantes_no_online"] = len(faltantes_no_online)
    diagnostico["amostra_faltantes_no_online"] = faltantes_no_online[:20]
    diagnostico["total_ids_duplicados_no_online"] = len(duplicados_no_online)
    diagnostico["total_ids_online_no_corpus"] = len(ids_online_no_corpus)

    if faltantes_no_online:
        bloqueios.append("ids_faltantes_no_online")
    if duplicados_no_online:
        bloqueios.append("ids_duplicados_no_online")
    if ids_online_no_corpus != set(particoes) or ids_online_no_corpus != set(alvo_congelado):
        bloqueios.append("conjunto_ids_online_diverge_do_congelado")

    diagnostico["bloqueios"] = bloqueios
    return diagnostico


def montar_bundle(
    registros_patched: list[dict[str, str]],
    particoes: dict[str, dict[str, Any]],
    alvo_congelado: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Monta os 9 campos oficiais do bundle DIRETAMENTE dos artefatos
    congelados — nunca recalcula H/R/grupo/fold a partir de M/Q ou de texto
    atual. Texto bruto (titulo/descricao_glpi/titulo_osm/descricao_osm) vem
    de `registros_patched` (base online + allowlists); categoria_historica
    e referencia_humana vem de `alvo_congelado`; grupo_sha256 e outer_fold
    vem de `particoes`. Itera sobre `particoes` (o universo CONGELADO dos
    13.972 IDs), nunca sobre a base online — que pode ter registros fora do
    corpus. So deve ser chamada depois de `validar_estrutura_congelada`
    devolver `bloqueios` vazio (senao a contraparte de algum ID pode
    faltar)."""
    brutos_por_id_sha = {
        hashlib.sha256(r["id"].encode("utf-8")).hexdigest(): r
        for r in registros_patched
        if r.get("id")
    }
    bundle = []
    for id_sha256 in sorted(particoes):
        bruto = brutos_por_id_sha.get(id_sha256)
        alvo = alvo_congelado.get(id_sha256)
        if bruto is None or alvo is None:
            raise RecuperacaoBloqueada(
                f"id_sha256 {id_sha256!r} do universo congelado sem "
                "contraparte no online patcheado ou no alvo congelado — "
                "inconsistencia interna, rodada interrompida."
            )
        parte = particoes[id_sha256]
        bundle.append({
            "id_sha256": id_sha256,
            "titulo": bruto["titulo"],
            "descricao_glpi": bruto["descricao_glpi"],
            "titulo_osm": bruto["titulo_osm"],
            "descricao_osm": bruto["descricao_osm"],
            "categoria_historica": alvo["categoria_historica"],
            "referencia_humana": alvo["referencia_humana"],
            "grupo_sha256": parte["grupo_sha256"],
            "outer_fold": parte["outer_fold"],
        })
    return bundle


# --------------------------------------------------------------------------
# Orquestracao
# --------------------------------------------------------------------------

def executar(
    hash_esperado: str,
    config_path: Path,
    particoes_path: Path,
    credenciais: str | Path | None = None,
    allowlist_grupo_a: dict[str, dict[str, str]] | None = None,
    allowlist_grupo_b: dict[str, dict[str, str]] | None = None,
) -> dict[str, Any]:
    grupo_a = ALLOWLIST_GRUPO_A if allowlist_grupo_a is None else allowlist_grupo_a
    if not grupo_a:
        return {
            "status": "bloqueado",
            "bloqueador": BLOQUEADOR_GRUPO_A_AUSENTE,
            "bundle_publicado": False,
        }

    grupo_b = (
        carregar_allowlist_grupo_b() if allowlist_grupo_b is None else allowlist_grupo_b
    )
    allowlist = montar_allowlist(grupo_a, grupo_b)

    atuais = rero.ler_registros_online(config_path, credenciais)
    registros_patched, aplicados = aplicar_allowlist(atuais, allowlist)

    diagnostico: dict[str, Any] = {
        "grupo_a_total_configurado": len(grupo_a),
        "grupo_b_total_configurado": len(grupo_b),
        "total_ids_com_patch_efetivamente_aplicado": len(aplicados),
        "ids_sha256_com_patch_aplicado": sorted(aplicados),
        "campos_alterados_por_id_sha256": dict(sorted(aplicados.items())),
        "replay_input_sha256_esperado": hash_esperado,
    }

    particoes = rero.carregar_particoes_preservadas(particoes_path)
    alvo_congelado = rero.carregar_alvo_congelado(rero.ALVO_CONGELADO_PADRAO)

    diagnostico_estrutural = validar_estrutura_congelada(
        registros_patched, particoes, alvo_congelado
    )
    diagnostico["diagnostico_estrutural"] = diagnostico_estrutural
    if diagnostico_estrutural["bloqueios"]:
        diagnostico.update({
            "status": "bloqueado_estrutural",
            "bloqueador": "Divergencia estrutural entre particoes/alvo congelado "
                          "e a base online: " + ", ".join(diagnostico_estrutural["bloqueios"]),
            "bundle_publicado": False,
        })
        return diagnostico

    bundle = montar_bundle(registros_patched, particoes, alvo_congelado)

    grupos_divergentes = rb.validar_grupos_por_registro(bundle)
    if grupos_divergentes:
        diagnostico.update({
            "status": "bloqueado_grupo_textual_divergente",
            "bloqueador": f"{len(grupos_divergentes)} registro(s) com grupo textual "
                          "(texto patcheado) divergente do grupo_sha256 congelado.",
            "bundle_publicado": False,
            "total_grupos_divergentes": len(grupos_divergentes),
            "amostra_ids_sha256_grupo_divergente": sorted(grupos_divergentes)[:20],
        })
        return diagnostico

    try:
        resultado = efc.validar_bundle_replay(bundle, hash_esperado, particoes_path)
    except efc.Fase2BBloqueado as exc:
        diagnostico.update({
            "status": "bloqueado_validacao_cientifica",
            "bloqueador": str(exc),
            "bundle_publicado": False,
        })
        return diagnostico

    diagnostico["hashes_metodologicos"] = resultado["hashes"]
    diagnostico["contagens"] = {
        "total_registros": resultado["total_registros"],
        "total_grupos": resultado["total_grupos"],
        "h_dentro_de_c": resultado["h_dentro_de_c"],
        "h_fora_de_c": resultado["h_fora_de_c"],
        "total_classes": len(resultado["classes"]),
    }
    diagnostico["replay_input_sha256_observado"] = resultado["replay_input_sha256"]

    # Candidato verificado: replay_input_sha256 + os 5 hashes metodologicos
    # + as contagens estruturais batem exatamente. Mesmo assim, esta rotina
    # NUNCA publica o bundle (nem em disco, nem como artifact) — so
    # verifica e reporta. bundle_publicado fica sempre False por
    # construcao (ver docstring do modulo, item 5).
    diagnostico.update({
        "status": "candidato_recuperado",
        "bloqueador": None,
        "bundle_publicado": False,
        "linhas": len(bundle),
        "colunas": len(rb.CAMPOS_BUNDLE),
    })
    return diagnostico


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hash-esperado", default=REPLAY_INPUT_SHA256_ESPERADO_CANDIDATO)
    parser.add_argument("--config", type=Path, default=rero.CONFIG_PADRAO)
    parser.add_argument("--particoes", type=Path, default=rero.PARTICOES_PADRAO)
    parser.add_argument("--saida-dir", type=Path, default=SAIDA_DIR_PADRAO)
    parser.add_argument("--credenciais", default=None)
    args = parser.parse_args()

    args.saida_dir.mkdir(parents=True, exist_ok=True)
    caminho_diagnostico = args.saida_dir / NOME_DIAGNOSTICO

    try:
        diagnostico = executar(
            hash_esperado=args.hash_esperado,
            config_path=args.config,
            particoes_path=args.particoes,
            credenciais=args.credenciais,
        )
    except RecuperacaoBloqueada as exc:
        diagnostico = {
            "status": "bloqueado",
            "bloqueador": str(exc),
            "bundle_publicado": False,
        }

    caminho_diagnostico.write_text(
        json.dumps(diagnostico, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(diagnostico, ensure_ascii=False, indent=2, sort_keys=True))

    return 0 if diagnostico.get("status") == "candidato_recuperado" else 1


if __name__ == "__main__":
    raise SystemExit(main())
