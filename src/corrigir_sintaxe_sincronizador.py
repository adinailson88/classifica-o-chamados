#!/usr/bin/env python3
"""Valida que o passe editorial residual já foi aplicado.

A transformação foi concluída em commit anterior. Esta etapa permanece no
workflow apenas como verificação idempotente, sem editar ou publicar arquivos.
"""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ARTIGO = RAIZ / "04_artigo" / "artigo_classificacao_chamados_v3.md"


def main() -> int:
    texto = ARTIGO.read_text(encoding="utf-8")
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
    print("Passe editorial residual já aplicado; validação aprovada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
