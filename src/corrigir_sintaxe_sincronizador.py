#!/usr/bin/env python3
"""Aplica o passe editorial residual da PR 75 e grava o artigo imediatamente."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess

RAIZ = Path(__file__).resolve().parents[1]
BRANCH = "agent/corrigir-sincronizacao-artigo"
ARTIGO = RAIZ / "04_artigo" / "artigo_classificacao_chamados_v3.md"


def executar(*args: str) -> None:
    subprocess.run(list(args), cwd=RAIZ, check=True)


def main() -> int:
    texto = ARTIGO.read_text(encoding="utf-8")

    texto = texto.replace(
        "reaproveitada diretamente nas ciclos posteriores",
        "reaproveitada diretamente em ciclos posteriores",
    )
    texto = texto.replace(
        "Essa camada não substitui acurácia,\ncalibração ou validação humana; responde a uma pergunta distinta, sobre\nonde modelos, categorias e chamados individuais concentram maior\nincerteza estrutural.",
        "Essa camada complementa a acurácia, a calibração e a validação humana ao indicar onde modelos, categorias e chamados individuais concentram maior incerteza estrutural.",
    )
    texto = texto.replace(
        "Essa dependência estrutural restringe a combinação correspondente e impede que seu valor seja interpretado como estimativa da capacidade da IA de corrigir o histórico.",
        "Essa dependência estrutural restringe a combinação correspondente, cujo valor caracteriza o funcionamento da regra de decisão, e não a capacidade da IA de corrigir o histórico.",
    )
    texto = texto.replace(
        "O valor zero representa, portanto, uma propriedade do protocolo de decisão, e não evidência de que classificadores automáticos sejam incapazes de identificar categorias históricas inadequadas. A avaliação dessa capacidade exige uma amostra independente, anotada sem utilizar como ponto de partida as classificações comparadas.",
        "O valor zero representa, portanto, uma propriedade do protocolo de decisão. A capacidade dos classificadores de identificar categorias históricas inadequadas requer uma amostra independente, anotada sem utilizar como ponto de partida as classificações comparadas.",
    )
    texto = texto.replace(
        "Assim, os valores de acerto caracterizam os 9.044 chamados com decisão travada e não constituem estimativa inferencial do desempenho sobre os 13.965 registros.",
        "Assim, os valores de acerto descrevem os 9.044 chamados com decisão travada; a estimativa populacional para os 13.965 registros requer amostragem probabilística.",
    )
    texto = texto.replace(
        "As figuras foram geradas a partir dos dados vigentes do painel público e",
        "As figuras foram geradas a partir dos agregados publicados no painel e",
    )
    texto = texto.replace(
        "Fonte: elaborado pelos autores (2026), com base nos agregados vigentes de\nauditoria e calibração. Não há registro com conferência da reclassificação\nneste estudo.",
        "Fonte: elaborado pelos autores (2026), com base nos agregados de auditoria e calibração. A conferência da reclassificação registra zero casos na base analisada.",
    )

    texto, n = re.subn(
        r"\n\*Pendência explícita\*:.*\Z",
        "\nOs agregados públicos não incluem o cruzamento completo das combinações M × N × P. Essa decomposição pode ser produzida a partir da planilha experimental, enquanto os resultados do corpo utilizam as contagens consolidadas da memória de decisão. A Subseção 4.3 discute a dependência estrutural entre classificação operacional, histórico e verdade validada.\n",
        texto,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise RuntimeError(f"Bloco residual do Apêndice não localizado: {n}")

    proibidos = [
        "nesta consolidação",
        "nesta execução",
        "nesta rodada",
        "nesta data",
        "hoje publicados",
        "nas ciclos posteriores",
        "**Tabela 4** Matriz de confusão",
        "Tabela 4 (Subseção 4.3)",
        "**Apêndice A — Checklist de itens reportados**",
        "não autoriza",
        "deve ser lido como",
    ]
    minusculo = texto.lower()
    for termo in proibidos:
        if termo.lower() in minusculo:
            raise RuntimeError(f"Resíduo editorial encontrado: {termo}")

    ARTIGO.write_text(texto, encoding="utf-8")

    executar("git", "config", "user.name", "github-actions[bot]")
    executar("git", "config", "user.email", "github-actions[bot]@users.noreply.github.com")
    executar("git", "add", "04_artigo/artigo_classificacao_chamados_v3.md")
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=RAIZ, check=False)
    if diff.returncode != 0:
        executar("git", "commit", "-m", "docs: elimina resíduos editoriais finais [skip ci]")
        executar("git", "push", "origin", f"HEAD:{BRANCH}")

    print("Passe editorial residual aplicado e versionado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
