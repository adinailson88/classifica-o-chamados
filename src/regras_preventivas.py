#!/usr/bin/env python3
"""Camada explicita de regras de periodicidade preventiva.

Modulo separado e auditavel, como exige o Passo 5 de PLANO_EXECUCAO_ATUAL.md.
Nao aprende nada dos dados: e uma tabela de termos escrita a mao, que pode ser
lida, contestada e alterada sem retreinar modelo nenhum.

DESENHO. A regra so dispara quando encontra, no mesmo chamado, um termo de
PERIODICIDADE e um termo de EQUIPAMENTO. Exigir os dois e deliberado: sozinho,
'ar condicionado' aparece tanto em preventiva programada quanto em corretiva
por defeito, e sozinho 'mensal' aparece em contratos e medicoes que nao sao
manutencao. A conjuncao troca cobertura por precisao, que e a unica troca
defensavel para uma camada que se propoe a sobrepor o modelo.

A regra se abstem quando nao encontra os dois termos, e abstencao nao e erro:
o comparador usa a predicao do modelo nesses casos.

Os termos de periodicidade ficam SOMENTE aqui. Os modelos estatisticos leem o
texto inteiro e podem capturar os mesmos sinais implicitamente; o que o passo
proibe e criar uma variavel explicita de periodicidade dentro deles.
"""

from __future__ import annotations

import re
import unicodedata

FAMILIA = "Manutenção Preventiva"

# Periodicidade explicita e vocabulario de programacao. Escrito sem acento
# porque a comparacao ocorre sobre texto normalizado.
TERMOS_PERIODICIDADE = (
    "preventiva", "preventivo", "periodica", "periodico", "periodicidade",
    "semanal", "quinzenal", "mensal", "bimestral", "trimestral",
    "quadrimestral", "semestral", "anual", "rotina", "cronograma",
    "programada", "programado", "plano de manutencao", "pmoc",
)

# Equipamento ou sistema, mapeado para a folha da taxonomia congelada. A chave
# e o termo normalizado; o valor e o nome exato da categoria, que precisa
# coincidir com a referencia humana caractere a caractere.
TERMOS_EQUIPAMENTO: tuple[tuple[str, str], ...] = (
    ("split", f"{FAMILIA} > Ar condicionado split"),
    ("ar condicionado central", f"{FAMILIA} > Ar condicionado central"),
    ("central de ar", f"{FAMILIA} > Ar condicionado central"),
    ("chiller", f"{FAMILIA} > Ar condicionado central"),
    ("fancoil", f"{FAMILIA} > Ar condicionado central"),
    ("ar condicionado", f"{FAMILIA} > Ar condicionado split"),
    ("climatizacao", f"{FAMILIA} > Ar condicionado split"),
    ("gerador", f"{FAMILIA} > Gerador"),
    ("grupo gerador", f"{FAMILIA} > Gerador"),
    ("quadro eletrico", f"{FAMILIA} > Quadros Elétricos"),
    ("quadros eletricos", f"{FAMILIA} > Quadros Elétricos"),
    ("qgbt", f"{FAMILIA} > Quadros Elétricos"),
    ("reservatorio", f"{FAMILIA} > Reservatório"),
    ("caixa d agua", f"{FAMILIA} > Reservatório"),
    ("caixa dagua", f"{FAMILIA} > Reservatório"),
    ("cisterna", f"{FAMILIA} > Reservatório"),
    ("vistoria", f"{FAMILIA} > Vistoria em Instalações"),
    ("inspecao predial", f"{FAMILIA} > Vistoria em Instalações"),
    ("iluminacao", f"{FAMILIA} > Iluminação"),
    ("luminaria", f"{FAMILIA} > Iluminação"),
    ("elevador", f"{FAMILIA} > Elevador"),
    ("extintor", f"{FAMILIA} > Sistemas de combate a incêndio (extintores, hidrantes)"),
    ("hidrante", f"{FAMILIA} > Sistemas de combate a incêndio (extintores, hidrantes)"),
    ("combate a incendio", f"{FAMILIA} > Sistemas de combate a incêndio (extintores, hidrantes)"),
    ("telhado", f"{FAMILIA} > Telhados, calhas, rufos, etc."),
    ("calha", f"{FAMILIA} > Telhados, calhas, rufos, etc."),
    ("rufo", f"{FAMILIA} > Telhados, calhas, rufos, etc."),
    ("esgoto", f"{FAMILIA} > Esgoto"),
    ("fossa", f"{FAMILIA} > Esgoto"),
    ("hidraulica", f"{FAMILIA} > Hidráulica"),
    ("poco artesiano", f"{FAMILIA} > Poços artesianos"),
)


def normalizar(texto: str) -> str:
    """Minusculas, sem acento, com espacos colapsados."""
    sem_acento = unicodedata.normalize("NFKD", str(texto or ""))
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acento.casefold()).strip()


def _contem(texto_normalizado: str, termo: str) -> bool:
    """Casa o termo respeitando fronteira de palavra.

    Sem a fronteira, 'split' casaria dentro de outra palavra e 'calha' casaria
    em 'trabalha', o que produziria disparos silenciosamente errados.
    """
    return re.search(rf"(?<!\w){re.escape(termo)}(?!\w)", texto_normalizado) is not None


def periodicidade(texto: str) -> list[str]:
    """Termos de periodicidade encontrados, em ordem de declaracao."""
    alvo = normalizar(texto)
    return [t for t in TERMOS_PERIODICIDADE if _contem(alvo, t)]


def equipamento(texto: str) -> tuple[str, str] | None:
    """Primeiro termo de equipamento encontrado e a categoria correspondente.

    A ordem da tabela e significativa: os termos mais especificos vem antes,
    de modo que 'ar condicionado central' seja testado antes de
    'ar condicionado'.
    """
    alvo = normalizar(texto)
    for termo, categoria in TERMOS_EQUIPAMENTO:
        if _contem(alvo, termo):
            return termo, categoria
    return None


def aplicar(texto: str, categorias_permitidas: set[str] | None = None
            ) -> dict[str, object]:
    """Aplica a regra a um chamado.

    Devolve sempre o mesmo formato, com `categoria` em `None` quando a regra se
    abstem. `categorias_permitidas` impede que a regra proponha categoria fora
    do conjunto avaliado, o que inventaria rotulo que o modelo nao pode prever.
    """
    termos_p = periodicidade(texto)
    achado = equipamento(texto)
    if not termos_p or achado is None:
        return {"categoria": None, "disparou": False,
                "termos_periodicidade": termos_p,
                "termo_equipamento": achado[0] if achado else None,
                "motivo": ("sem termo de periodicidade" if not termos_p
                           else "sem termo de equipamento")}
    termo_eq, categoria = achado
    if categorias_permitidas is not None and categoria not in categorias_permitidas:
        return {"categoria": None, "disparou": False,
                "termos_periodicidade": termos_p, "termo_equipamento": termo_eq,
                "motivo": "categoria fora do conjunto avaliado"}
    return {"categoria": categoria, "disparou": True,
            "termos_periodicidade": termos_p, "termo_equipamento": termo_eq,
            "motivo": "periodicidade e equipamento presentes"}


def categorias_alvo() -> set[str]:
    """Conjunto de categorias que a tabela de regras consegue propor."""
    return {categoria for _termo, categoria in TERMOS_EQUIPAMENTO}
