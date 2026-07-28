from pathlib import Path
import re

ARTIGO = Path("04_artigo/artigo_classificacao_chamados_v3.md")
PLANO = Path("PLANO_ARTIGO_CAPITULO.md")

texto = ARTIGO.read_text(encoding="utf-8")

substituicoes = [
    (
        r"O lote contém 639 chamados com decisão\s+humana M/N/P/Q\.",
        "O lote contém 639 chamados com categoria de referência estabelecida por\nvalidação humana.",
        1,
    ),
    (
        r"A decisão M/N/P/Q pode manter o\s+histórico, aceitar uma classificação automática, aceitar a\s+reclassificação ou registrar manualmente uma categoria distinta\.",
        "A validação humana pode confirmar a categoria histórica, aceitar uma\nclassificação automática, aceitar uma reclassificação ou definir\nmanualmente uma categoria distinta. A categoria resultante desse processo\nconstitui a referência validada utilizada na avaliação dos modelos. Quando\nnenhuma das fontes é confirmada e não há categoria alternativa definida\npelo avaliador, o chamado permanece sem categoria de referência.",
        1,
    ),
    (
        r"contra a decisão humana M/N/P/Q \(Subseção 4\.2\)",
        "contra a categoria de referência estabelecida por validação humana (Subseção 4.2)",
        1,
    ),
    (
        r"A avaliação contra a decisão humana M/N/P/Q utiliza 8\.895 chamados com\s+categoria decidida\.",
        "A avaliação contra a categoria de referência validada utiliza 8.895 chamados\npara os quais a conferência humana estabeleceu uma categoria final.",
        1,
    ),
    (
        r"Entre os registros do\s+lote, 639 possuem decisão humana M/N/P/Q e formam o denominador do acerto\s+validado\.",
        "Entre os registros do lote, 639 possuem categoria de referência estabelecida\npor validação humana e formam o denominador do acerto validado.",
        1,
    ),
    (
        r"sem o\s+preenchimento da categoria manual Q, não há referência final",
        "sem a definição manual de uma categoria alternativa, não há referência final",
        1,
    ),
    (
        r"A regra M/N/P/Q ainda depende do preenchimento manual de uma categoria\s+quando todas as fontes são rejeitadas ou entram em conflito\.",
        "O protocolo de validação ainda depende da definição manual de uma categoria\nalternativa quando todas as fontes avaliadas são rejeitadas ou quando há\nconflito entre classificações consideradas corretas.",
        1,
    ),
    (
        r"Na avaliação integral de 8\.895 chamados com decisão M/N/P/Q, o LinearSVC",
        "Na avaliação integral dos 8.895 chamados com categoria de referência\nestabelecida por validação humana, o LinearSVC",
        1,
    ),
    (
        r"A próxima etapa de\s+validação deve preencher a categoria manual Q nesses casos, com prioridade\s+para conflitos e rejeição de todas as fontes\.",
        "A próxima etapa de validação deve definir manualmente uma categoria de\nreferência nesses casos, priorizando os conflitos entre fontes e as situações\nem que todas as classificações avaliadas foram rejeitadas.",
        1,
    ),
]

for padrao, novo, esperado in substituicoes:
    texto, quantidade = re.subn(padrao, novo, texto, flags=re.MULTILINE)
    if quantidade != esperado:
        raise SystemExit(
            f"Substituição inesperada: {padrao!r}; encontrado={quantidade}; esperado={esperado}"
        )

proibidos = ["M/N/P/Q", "categoria manual Q"]
restantes = [termo for termo in proibidos if termo in texto]
if restantes:
    raise SystemExit(f"Termos operacionais ainda presentes no artigo: {restantes}")

ARTIGO.write_text(texto, encoding="utf-8")

plano_texto = PLANO.read_text(encoding="utf-8")
novo_estado = """## Estado desta rodada

**Onde está:** o artigo permanece cientificamente fechado, com resultados e conclusões inalterados. A redação metodológica foi revisada para retirar do corpo científico os identificadores internos das colunas de conferência da planilha.

**O que foi feito:** as referências a M/N/P/Q e à categoria manual Q foram substituídas, apenas no artigo, por categorias conceituais de decisão: confirmação da categoria histórica, aceitação da classificação automática, aceitação da reclassificação, definição manual de categoria alternativa e categoria de referência validada. Nenhum dado, cálculo, denominador, resultado, regra operacional da planilha ou código de processamento foi alterado. O PDF público foi regenerado a partir da fonte Markdown revisada.

**Próximo passo:** preencher a categoria manual Q dos 639 casos restritos (201 deles em conflito) e avaliar a viabilidade de uma execução *out-of-fold* integral do BERTimbau sobre toda a base.

## Critérios para fechamento"""

plano_texto, quantidade = re.subn(
    r"## Estado desta rodada\n.*?\n## Critérios para fechamento",
    novo_estado,
    plano_texto,
    count=1,
    flags=re.DOTALL,
)
if quantidade != 1:
    raise SystemExit("Não foi possível substituir o Estado desta rodada no plano.")

PLANO.write_text(plano_texto, encoding="utf-8")
