#!/usr/bin/env python3
"""Aplica correções idempotentes ao sincronizador do artigo.

Corrige as expressões incompatíveis com f-strings do Python 3.11 e aponta a
análise de sensibilidade para o artefato efetivamente produzido em
``04_artigo/figuras``.
"""

from pathlib import Path

CAMINHO = Path(__file__).with_name("sincronizar_artigo_dados.py")


def main() -> int:
    texto = CAMINHO.read_text(encoding="utf-8")
    original = texto

    texto = texto.replace(
        '    amplitudes = [item["amplitude"] for item in sensibilidade.values()]\n'
        '    vies_tabela = f"""',
        '    amplitudes = [item["amplitude"] for item in sensibilidade.values()]\n'
        '    tabela_t2 = "\\n".join(linhas_t2)\n'
        '    vies_tabela = f"""',
    )
    texto = texto.replace('{"\\n".join(linhas_t2)}', '{tabela_t2}')

    texto = texto.replace(
        '    alvo = calibracao["faixa_alvo_95"]\n'
        '    secao_44 = f"""',
        '    alvo = calibracao["faixa_alvo_95"]\n'
        '    tabela_t3 = "\\n".join(linhas_t3)\n'
        '    secao_44 = f"""',
    )
    texto = texto.replace('{"\\n".join(linhas_t3)}', '{tabela_t3}')

    texto = texto.replace(
        '    sensibilidade_json = ler_json("sensibilidade_vies_validacao.json")',
        '    sensibilidade_json = json.loads((RAIZ / "04_artigo" / "figuras" / "sensibilidade_vies_validacao.json").read_text(encoding="utf-8"))',
    )

    if texto == original:
        print("sincronizador já estava corrigido")
        return 0

    CAMINHO.write_text(texto, encoding="utf-8")
    print(f"sincronizador corrigido: {CAMINHO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
