from pathlib import Path

ARQUIVO = Path("04_artigo/artigo_classificacao_chamados_v3.md")
MARCADOR = "\\enlargethispage{2\\baselineskip}"
ALVO = "**Tabela 4** Acerto validado por faixa de confiança. A unidade é o\nchamado, 13.965 no total, 8.895 com conferência humana."
INSERCAO = "```{=latex}\n\\enlargethispage{2\\baselineskip}\n```\n\n" + ALVO

texto = ARQUIVO.read_text(encoding="utf-8")
if MARCADOR in texto:
    raise SystemExit("A correção de paginação já está presente.")
if texto.count(ALVO) != 1:
    raise SystemExit("O bloco da Tabela 4 não foi localizado de forma inequívoca.")
texto = texto.replace(ALVO, INSERCAO, 1)
ARQUIVO.write_text(texto, encoding="utf-8")
