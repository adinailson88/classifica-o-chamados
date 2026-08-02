#!/usr/bin/env python3
"""Tipo de manutencao derivado da categoria historica do GLPI.

A funcao vivia em src/exportar_dashboard.py e foi extraida para ca em
02/08/2026, quando passou a ser usada tambem pela curva ABC por tipo. Nao
duplicar: quem precisar do tipo importa deste modulo.

CRITERIO, decidido pelo pesquisador em 02/08/2026:

    Preventiva      familia 'Manutencao Preventiva', com ou sem separador
    Nao manutencao  familias que nao descrevem servico de manutencao predial
    Corretiva       o restante

O terceiro tipo existe porque o criterio anterior, binario, mandava para
Corretiva tudo que nao fosse preventivo, inclusive 'Outros > Erro de chamado',
'Posto de trabalho > Contratacao de Posto de trabalho', 'Projetos e Reformas >
Reforma' e 'Suprimentos / Apoio Tecnico > Materiais'. Sao 595 chamados em
14.058, ou 4,2%, que inflavam o denominador de corretivas em 7% relativos e
viesavam qualquer razao preventiva/corretiva usada como indicador de ESG.

'TI / Dados / Rede' permanece em Corretiva por decisao expressa: 'Ponto de rede
/ fibra otica / Wi-fi', com 409 dos seus 449 chamados, e reparo de
infraestrutura predial e se comporta como corretiva. Separar apenas 'Coleta de
dados' exigiria regra por folha, e nao por familia, o que quebraria a
simplicidade do criterio por prefixo.

A classificacao e por FAMILIA, isto e, pelo trecho anterior ao primeiro '>',
comparado por igualdade e nao por prefixo. Comparar por prefixo confundiria a
familia 'Projeto', raiz legada com 7 chamados, com 'Projetos e Reformas'.
"""

from __future__ import annotations

import unicodedata

PREVENTIVA = "Preventiva"
CORRETIVA = "Corretiva"
NAO_MANUTENCAO = "Não manutenção"

TIPOS = (PREVENTIVA, CORRETIVA, NAO_MANUTENCAO)

# Sigla usada na tabela do apendice do artigo, onde cada categoria aparece
# marcada com P, C ou NM.
SIGLA = {PREVENTIVA: "P", CORRETIVA: "C", NAO_MANUTENCAO: "NM"}

FAMILIA_PREVENTIVA = "manutencao preventiva"

FAMILIAS_NAO_MANUTENCAO = frozenset({
    "outros",                     # Erro de chamado (256), Outros (28), Materiais (2)
    "suprimentos/apoio tecnico",  # Materiais (94), Limpeza (13), Transporte (2)
    "posto de trabalho",          # Contratacao de Posto de trabalho (102)
    "projetos e reformas",        # Reforma (65), Projeto (23)
    "projeto",                    # raiz legada: Eletrico (tomada e iluminacao) (7)
    "revisao",                    # raiz legada: Telecomunicacoes (3)
})


def normalizar(valor) -> str:
    """Minusculas, sem acento, com espacos colapsados."""
    texto = unicodedata.normalize("NFKD", str(valor or ""))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return " ".join(texto.split()).casefold()


def familia(categoria) -> str:
    """Trecho anterior ao primeiro '>', preservando grafia e acento.

    Categoria sem separador e a propria familia, o que cobre as raizes que o
    GLPI mantem apenas para sustentar a hierarquia.
    """
    texto = " ".join(str(categoria or "").split())
    return texto.split(">")[0].strip()


def _chave_familia(categoria) -> str:
    """Chave de comparacao: familia normalizada e sem espaco ao redor da barra.

    'Suprimentos / Apoio Tecnico' e 'Suprimentos/Apoio Tecnico' nomeiam a mesma
    familia e precisam colidir na mesma chave.
    """
    chave = normalizar(familia(categoria))
    return "/".join(parte.strip() for parte in chave.split("/"))


def tipo_manutencao(categoria) -> str:
    """Classifica a categoria historica em Preventiva, Corretiva ou Não manutenção.

    Categoria vazia devolve Corretiva, comportamento herdado do painel: ausencia
    de categoria nunca ocorre na base do experimento, porque so entram linhas
    com a coluna C preenchida, e o painel prefere o valor mais frequente a um
    rotulo proprio para o caso impossivel.
    """
    chave = _chave_familia(categoria)
    if chave == FAMILIA_PREVENTIVA:
        return PREVENTIVA
    if chave in FAMILIAS_NAO_MANUTENCAO:
        return NAO_MANUTENCAO
    return CORRETIVA


def sigla(tipo: str) -> str:
    """P, C ou NM, para a tabela do apendice."""
    return SIGLA.get(tipo, "")
