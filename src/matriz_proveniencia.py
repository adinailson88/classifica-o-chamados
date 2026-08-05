#!/usr/bin/env python3
"""Matriz de proveniencia da rodada canonica, conforme o Passo 10 do plano.

Ferramenta offline, sem acesso a planilha. Faz tres coisas:

  1. verifica que todos os artefatos canonicos carregam o MESMO `hash_corpus`,
     porque numeros carimbados com hashes diferentes descrevem corpora
     diferentes e nao podem aparecer lado a lado numa mesma tabela;
  2. monta a tabela que liga cada grandeza publicavel ao artefato, ao script,
     ao denominador, ao numero de categorias e ao hash;
  3. varre a fonte do artigo em busca de numeros da execucao LEGADA que ainda
     nao foram substituidos.

O item 3 e o que encontra erro de verdade. O plano exige verificar que
"resultados antigos nao permanecem no Resumo, Abstract, discussao ou
conclusao", e essa e uma revisao que ninguem faz bem a olho: os numeros
legados sao plausiveis, estao no formato certo e nao chamam atencao.

A varredura reporta ocorrencia e linha, e nunca edita o artigo. Trocar numero
em texto cientifico e decisao editorial do autor.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "docs" / "dados"
ARTIGO_PADRAO = RAIZ / "04_artigo" / "artigo_classificacao_chamados_v3.md"
SAIDA_JSON_PADRAO = DADOS / "matriz_proveniencia.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "MATRIZ_PROVENIENCIA.md"

# Artefatos que devem carregar o hash da rodada canonica.
CANONICOS = [
    ("Retreino dos sete modelos", "retreino_canonico.json",
     "src/retreinar_modelos_canonicos.py"),
    ("Regras contra modelos", "regras_versus_modelos.json",
     "src/comparar_regras_modelos.py"),
    ("Calibracao e automacao seletiva", "calibracao_canonica.json",
     "src/calibrar_confianca.py"),
    ("Recortes por tipo e volume", "recortes_canonicos.json",
     "src/recortes_canonicos.py"),
    ("Inferencia estatistica", "inferencia_canonica.json",
     "src/inferencia_canonica.py"),
    ("Inferencia pareada por grupo textual", "inferencia_agrupada.json",
     "src/inferencia_agrupada.py"),
    ("Sensibilidade as categorias raras", "sensibilidade_classes_raras.json",
     "src/sensibilidade_classes_raras.py"),
    ("Utilidade da reclassificacao", "utilidade_reclassificacao.json",
     "src/utilidade_reclassificacao.py"),
]

# Artefatos do congelamento, anteriores a rodada e sem hash_corpus por
# construcao: eles definem o corpus, nao derivam dele.
CONGELAMENTO = [
    ("Auditoria da base", "auditoria_base_canonica.json",
     "src/auditar_base_canonica.py"),
    ("Grupos textuais", "grupos_textuais.json",
     "src/construir_grupos_textuais.py"),
    ("Particoes canonicas", "particoes_canonicas.json",
     "src/gerar_particoes_canonicas.py"),
]


def _relativo(caminho: Path) -> str:
    """Caminho relativo a raiz quando possivel; absoluto caso contrario.

    Um artigo fora da arvore do repositorio e caso legitimo, sobretudo em
    teste, e nao pode derrubar o relatorio inteiro.
    """
    try:
        return str(caminho.relative_to(RAIZ)).replace("\\", "/")
    except ValueError:
        return str(caminho).replace("\\", "/")


def _ler(caminho: Path) -> dict[str, Any] | None:
    if not caminho.exists():
        return None
    return json.loads(caminho.read_text(encoding="utf-8"))


def verificar_coerencia(dados: Path = DADOS) -> dict[str, Any]:
    """Todos os artefatos derivados precisam do mesmo hash_corpus."""
    manifesto = _ler(dados / "rodada_canonica.json") or {}
    esperado = manifesto.get("hash_corpus")
    linhas = []
    for rotulo, arquivo, script in CANONICOS:
        conteudo = _ler(dados / arquivo)
        obtido = (conteudo or {}).get("hash_corpus")
        linhas.append({
            "artefato": rotulo, "arquivo": f"docs/dados/{arquivo}",
            "script": script, "hash_corpus": obtido,
            "ausente": conteudo is None,
            "coerente": bool(conteudo is not None and obtido == esperado),
        })
    divergentes = [x for x in linhas if not x["coerente"]]
    return {"hash_esperado": esperado, "artefatos": linhas,
            "divergentes": len(divergentes)}


def _formatos(valor: float) -> set[str]:
    """Como um numero pode aparecer no texto: com ponto e com virgula.

    Duas casas ficam de fora de proposito. Uma acuracia de 0,6915 truncada em
    0,69 colide com qualquer percentual, proporcao ou celula de tabela do
    artigo, e o alarme falso resultante custa mais atencao do que a ocorrencia
    verdadeira que eventualmente encontraria.
    """
    saida: set[str] = set()
    for casas in (3, 4):
        texto = f"{valor:.{casas}f}"
        saida.add(texto)
        saida.add(texto.replace(".", ","))
    return saida


def numeros_legados(dados: Path = DADOS) -> dict[str, list[str]]:
    """Valores que so existem na execucao legada e nao devem sobreviver.

    Sao as acuracias do bootstrap por linha, publicadas em `estatistica.json`,
    e o total de 14.058 chamados, substituido por 13.972 na rodada canonica.
    """
    legado: dict[str, list[str]] = {}
    estat = _ler(dados / "estatistica.json") or {}
    for item in estat.get("acuracia_bootstrap", []):
        rotulo = f"acuracia legada de {item['modelo']}"
        legado[rotulo] = sorted(_formatos(float(item["acuracia"])))
    legado["corpus legado"] = ["14.058", "14,058", "14058"]
    legado["categorias legadas"] = ["56 categorias"]
    return legado


def auditar_artigo(caminho: Path, legado: dict[str, list[str]]) -> dict[str, Any]:
    """Localiza ocorrencias de numeros legados na fonte do artigo."""
    if not caminho.exists():
        return {"arquivo": str(caminho), "lido": False, "ocorrencias": []}
    linhas = caminho.read_text(encoding="utf-8").split("\n")
    ocorrencias = []
    for rotulo, formas in sorted(legado.items()):
        for numero, linha in enumerate(linhas, start=1):
            for forma in formas:
                # A fronteira precisa distinguir dois casos que se parecem. Um
                # digito, ou um separador SEGUIDO de digito, indica que a forma
                # e pedaco de um numero maior, e nao deve casar: 0,80 dentro de
                # 0,8046. Ja um separador terminal e pontuacao da frase e deve
                # casar, senao todo numero em fim de periodo escaparia da
                # varredura, que e o caso mais comum em prosa.
                padrao = r"(?<![\d,.])" + re.escape(forma) + r"(?![\d]|[.,]\d)"
                if re.search(padrao, linha):
                    ocorrencias.append({"valor_legado": rotulo, "forma": forma,
                                        "linha": numero})
                    break
    ocorrencias.sort(key=lambda x: (x["linha"], x["valor_legado"]))
    return {"arquivo": _relativo(caminho), "lido": True,
            "ocorrencias": ocorrencias}


def montar_matriz(dados: Path = DADOS) -> list[dict[str, Any]]:
    """Liga cada grandeza publicavel a sua origem verificavel."""
    manifesto = _ler(dados / "rodada_canonica.json") or {}
    corpus = manifesto.get("corpus", {})
    hash_curto = (manifesto.get("hash_corpus") or "")[:12]
    base = {
        "denominador": corpus.get("linhas"),
        "categorias": corpus.get("categorias"),
        "particoes": corpus.get("dobras"),
        "hash_corpus": hash_curto,
    }
    grandezas = [
        ("Acuracia e macro-F1 por modelo", "docs/RETREINO_CANONICO.md",
         "src/retreinar_modelos_canonicos.py"),
        ("Ganho ou perda da camada de regras", "docs/REGRAS_VERSUS_MODELOS.md",
         "src/comparar_regras_modelos.py"),
        ("ECE, Brier e curva de confiabilidade", "docs/CALIBRACAO_CANONICA.md",
         "src/calibrar_confianca.py"),
        ("Cobertura e acuracia seletiva por limiar", "docs/CALIBRACAO_CANONICA.md",
         "src/calibrar_confianca.py"),
        ("Recorte por tipo e tarefa de tipo", "docs/RECORTES_CANONICOS.md",
         "src/recortes_canonicos.py"),
        ("Curva ABC por volume", "docs/RECORTES_CANONICOS.md",
         "src/recortes_canonicos.py"),
        ("Intervalos de confianca", "docs/INFERENCIA_CANONICA.md",
         "src/inferencia_canonica.py"),
        ("Efeito de desenho da dependencia intragrupo",
         "docs/INFERENCIA_AGRUPADA.md", "src/inferencia_agrupada.py"),
        ("Cochran Q com referencia por permutacao de grupo",
         "docs/INFERENCIA_AGRUPADA.md", "src/inferencia_agrupada.py"),
        ("Diferenca de acuracia, IC, grupos a favor e p ajustado por par",
         "docs/INFERENCIA_AGRUPADA.md", "src/inferencia_agrupada.py"),
        ("Cobertura e macro-F1 sob tres convencoes de denominador",
         "docs/SENSIBILIDADE_CLASSES_RARAS.md",
         "src/sensibilidade_classes_raras.py"),
        ("Razao de equilibrio e utilidade da reclassificacao",
         "docs/UTILIDADE_RECLASSIFICACAO.md",
         "src/utilidade_reclassificacao.py"),
        ("Cochran Q e McNemar por linha, mantidos so para contraste",
         "docs/INFERENCIA_CANONICA.md", "src/inferencia_canonica.py"),
        ("Custo computacional do BERTimbau", "docs/CUSTO_BERTIMBAU.md",
         "src/medir_custo_bertimbau.py"),
        ("Concordancia historica, Kappa e ganho liquido",
         "docs/dados/comparacao_historica.json",
         "src/executar_rodada_canonica.py"),
        ("Dispersao das predicoes e Jensen-Shannon",
         "docs/dados/comparacao_historica.json",
         "src/executar_rodada_canonica.py"),
        ("Unanimidade e desacordo estrutural entre modelos",
         "docs/INFERENCIA_CANONICA.md", "src/inferencia_canonica.py"),
        ("Conciliacao das contagens de grupos textuais",
         "docs/INFERENCIA_CANONICA.md", "src/inferencia_canonica.py"),
        ("Tabelas A1 a A3 do apendice",
         "docs/dados/tabelas_apendice_canonicas.json",
         "src/tabelas_apendice_canonicas.py"),
    ]
    fora = grandezas_fora_da_rodada_canonica()
    return ([{"grandeza": g, "artefato": a, "script": s, **base}
             for g, a, s in grandezas] + fora)


def grandezas_fora_da_rodada_canonica() -> list[dict[str, Any]]:
    """Grandezas do artigo que NAO saem da rodada canonica.

    Existem e sao legitimas, mas respondem a outro protocolo e a outro
    denominador. Precisam figurar na matriz justamente para que ninguem as
    compare com as tabelas do corpo, que foi a origem da discrepancia do LSTM
    entre 0,7287, 0,8635 e 0,8768.
    """
    return [
        {
            "grandeza": "Corpus congelado, referencia humana e taxonomia",
            "artefato": "docs/dados/auditoria_base_canonica.json",
            "script": "src/auditar_base_canonica.py",
            "denominador": 14060, "categorias": 50, "particoes": None,
            "hash_corpus": "congelamento",
            "ressalva": ("denominador do corpus e da cobertura da revisao, "
                         "nunca das metricas, que valem para 13.972 linhas"),
        },
        {
            "grandeza": "Grupos textuais da base congelada",
            "artefato": "docs/dados/grupos_textuais.json",
            "script": "src/construir_grupos_textuais.py",
            "denominador": 14060, "categorias": 50, "particoes": None,
            "hash_corpus": "congelamento",
            "ressalva": ("9.786 grupos na base inteira; 9.735 no recorte de "
                         "13.972 linhas; 9.734 no mapa de particoes, "
                         "recalculado sobre o texto vivo"),
        },
        {
            "grandeza": "Grupos com referencia humana divergente e sua natureza",
            "artefato": "docs/dados/grupos_divergentes_canonicos.json",
            "script": "src/auditar_grupos_divergentes.py",
            "denominador": 13972, "categorias": 41, "particoes": None,
            "hash_corpus": "congelamento",
            "ressalva": ("17 grupos e 85 linhas medidos sobre as linhas com "
                         "referencia avaliada; 14 grupos e 74 linhas opoem "
                         "categorias de TIPOS de manutencao distintos, de modo "
                         "que a contagem nao pode ser lida como piso de erro "
                         "de anotacao"),
        },
        {
            "grandeza": "Disponibilidade de data de abertura no corpus congelado",
            "artefato": "docs/dados/disponibilidade_temporal.json",
            "script": "src/auditar_disponibilidade_temporal.py",
            "denominador": None, "categorias": None, "particoes": None,
            "hash_corpus": "congelamento",
            "ressalva": ("veredito sem_variavel_temporal: nenhum campo do "
                         "contrato de colunas nem dos artefatos da rodada "
                         "localiza o chamado no tempo, de modo que a avaliacao "
                         "temporal nao e executavel e a validacao cruzada "
                         "agrupada nao estima desempenho futuro"),
        },
        {
            "grandeza": "Curva de aprendizado do LSTM (Figura 6)",
            "artefato": "04_artigo/figuras/lstm_history.json",
            "script": "src/modelo_lstm.py",
            "denominador": None, "categorias": None, "particoes": None,
            "hash_corpus": "fora da rodada canonica",
            "ressalva": ("treino unico sobre a aba viva de 25/07/2026, com "
                         "rotulo historico e validacao interna de 10%; nao "
                         "comparavel com as Tabelas 2 e 3"),
        },
        {
            "grandeza": "Ablation de unidades e dropout do LSTM",
            "artefato": "04_artigo/figuras/ablation_lstm_resultados.json",
            "script": "src/ablation_lstm.py",
            "denominador": 9096, "categorias": None, "particoes": 3,
            "hash_corpus": "fora da rodada canonica",
            "ressalva": ("snapshot legado de 24/07/2026, cobertura parcial da "
                         "revisao humana e rotulo de treino historico; o "
                         "script foi corrigido depois e os numeros nao foram "
                         "regerados"),
        },
        {
            "grandeza": "KFold por linha contra GroupKFold por texto",
            "artefato": "04_artigo/figuras/comparacao_kfold_groupkfold.json",
            "script": "src/comparacao_kfold_groupkfold.py",
            "denominador": 14094, "categorias": None, "particoes": 5,
            "hash_corpus": "fora da rodada canonica",
            "ressalva": ("base de 01/08/2026, anterior ao congelamento em "
                         "14.060, e alvo e a categoria historica"),
        },
    ]


def montar_relatorio(dados: Path = DADOS,
                     artigo: Path = ARTIGO_PADRAO) -> dict[str, Any]:
    coerencia = verificar_coerencia(dados)
    legado = numeros_legados(dados)
    auditoria = auditar_artigo(artigo, legado)
    congelamento = [
        {"artefato": rotulo, "arquivo": f"docs/dados/{arquivo}", "script": script,
         "presente": (dados / arquivo).exists()}
        for rotulo, arquivo, script in CONGELAMENTO
    ]
    problemas = {
        "artefatos_com_hash_divergente": coerencia["divergentes"],
        "artefatos_do_congelamento_ausentes":
            sum(1 for c in congelamento if not c["presente"]),
        "numeros_legados_ainda_no_artigo": len(auditoria["ocorrencias"]),
    }
    return {
        "schema_version": 1,
        "status": ("bloqueado" if problemas["artefatos_com_hash_divergente"]
                   else "concluido"),
        "hash_corpus": coerencia["hash_esperado"],
        "coerencia": coerencia,
        "congelamento": congelamento,
        "matriz": montar_matriz(dados),
        "auditoria_do_artigo": auditoria,
        "problemas": problemas,
        "nota": ("a varredura do artigo aponta, nunca corrige: substituir "
                 "numero em texto cientifico e decisao editorial do autor"),
        "cobertura_da_varredura": (
            "sao procuradas as acuracias registradas em estatistica.json, o "
            "total de chamados e a contagem de categorias da execucao legada. "
            "O artigo pode conter numeros de rodadas intermediarias que nao "
            "estao em nenhum JSON versionado, e esses a varredura nao alcanca; "
            "a contagem e piso, nao teto"),
    }


def renderizar_markdown(r: dict[str, Any]) -> str:
    linhas = [
        "# Matriz de proveniência da rodada canônica",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.",
        "",
        f"**Estado:** `{r['status']}`  ",
        f"**Gerado em:** {r.get('gerado_em', 'não informado')}  ",
        f"**Hash do corpus:** `{r.get('hash_corpus') or 'não informado'}`",
        "",
        "## Coerência dos artefatos derivados",
        "",
        "| Artefato | Arquivo | Script | Hash confere |",
        "|---|---|---|---|",
    ]
    for a in r["coerencia"]["artefatos"]:
        estado = "sim" if a["coerente"] else ("ausente" if a["ausente"] else "NÃO")
        linhas.append(f"| {a['artefato']} | `{a['arquivo']}` | `{a['script']}` | {estado} |")

    linhas += [
        "",
        "## Artefatos do congelamento",
        "",
        "Definem o corpus e por isso não carregam `hash_corpus`: ele é derivado deles.",
        "",
        "| Artefato | Arquivo | Script | Presente |",
        "|---|---|---|---|",
    ]
    for c in r["congelamento"]:
        linhas.append(f"| {c['artefato']} | `{c['arquivo']}` | `{c['script']}` | "
                      f"{'sim' if c['presente'] else 'NÃO'} |")

    linhas += [
        "",
        "## Rastreabilidade das grandezas publicáveis",
        "",
        "| Grandeza | Artefato | Script | Denominador | Categorias | Partições | Hash | Ressalva |",
        "|---|---|---|---:|---:|---:|---|---|",
    ]
    for m in r["matriz"]:
        vazio = lambda x: "—" if x is None else x  # noqa: E731
        linhas.append(
            f"| {m['grandeza']} | `{m['artefato']}` | `{m['script']}` | "
            f"{vazio(m['denominador'])} | {vazio(m['categorias'])} | "
            f"{vazio(m['particoes'])} | `{m['hash_corpus']}` | "
            f"{m.get('ressalva', '—')} |")

    aud = r["auditoria_do_artigo"]
    linhas += ["", "## Números legados ainda presentes no artigo", ""]
    if not aud["lido"]:
        linhas.append(f"Fonte não encontrada em `{aud['arquivo']}`.")
    elif not aud["ocorrencias"]:
        linhas.append("Nenhum número da execução legada foi localizado.")
    else:
        linhas += [
            f"Encontradas {len(aud['ocorrencias'])} ocorrências em `{aud['arquivo']}`. "
            + r["nota"] + ".",
            "",
            "| Linha | Forma no texto | Valor legado |",
            "|---:|---|---|",
        ]
        linhas += [f"| {o['linha']} | `{o['forma']}` | {o['valor_legado']} |"
                   for o in aud["ocorrencias"]]

    linhas += [
        "",
        "## Validações",
        "",
        "| Verificação | Ocorrências |",
        "|---|---:|",
    ]
    linhas += [f"| {k.replace('_', ' ')} | {v} |" for k, v in r["problemas"].items()]
    linhas += ["", f"**Cobertura da varredura:** {r['cobertura_da_varredura']}.", ""]
    linhas += ["## Proveniência", "",
               "- Script: `src/matriz_proveniencia.py`.",
               "- Nenhuma escrita foi realizada na planilha nem no artigo.", ""]
    return "\n".join(linhas)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dados", type=Path, default=DADOS)
    p.add_argument("--artigo", type=Path, default=ARTIGO_PADRAO)
    p.add_argument("--json", type=Path, default=SAIDA_JSON_PADRAO)
    p.add_argument("--markdown", type=Path, default=SAIDA_MD_PADRAO)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    relatorio = montar_relatorio(args.dados, args.artigo)
    relatorio["gerado_em"] = agora_bahia()
    relatorio["script_origem"] = "src/matriz_proveniencia.py"
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    args.markdown.write_text(renderizar_markdown(relatorio), encoding="utf-8")
    print(renderizar_markdown(relatorio))
    return 0 if relatorio["status"] == "concluido" else 2


if __name__ == "__main__":
    raise SystemExit(main())
