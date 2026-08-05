"""Regressao: o ablation procura a verdade por id_chamado, nao por linha.

`dv.carregar_decisoes(..., chave='id')` devolve um mapa indexado pelo
`id_chamado`. Enquanto `avaliar_variante` e `diagnosticar_duplicatas_folds`
procuravam por `item['linha']`, nenhum registro era encontrado e o ablation
abortava com "Informação insuficiente para verificar." — sem erro visivel, o
que e exatamente o modo de falha que ja tinha derrubado quatro ferramentas.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import ablation_lstm as ab  # noqa: E402


def _linhas():
    return [
        {"linha": 2, "id": "2025000001", "texto": "vazamento na pia",
         "historico": "Hidrossanitária > Hidráulica"},
        {"linha": 3, "id": "2025000002", "texto": "lampada queimada",
         "historico": "Elétrica > Iluminação"},
        {"linha": 4, "id": "2025000003", "texto": "porta emperrada",
         "historico": "Estrutura Predial > Esquadrias"},
    ]


class TestChaveVerdade(unittest.TestCase):
    def test_usa_o_id_quando_existe(self):
        self.assertEqual(ab.chave_verdade(_linhas()[0]), "2025000001")

    def test_cai_para_a_linha_quando_nao_ha_id(self):
        self.assertEqual(ab.chave_verdade({"linha": 7, "id": ""}), 7)

    def test_mapa_por_id_encontra_os_registros(self):
        verdade = {"2025000001": "Hidrossanitária > Hidráulica",
                   "2025000003": "Estrutura Predial > Esquadrias"}
        encontrados = [i for i, item in enumerate(_linhas())
                       if ab.chave_verdade(item) in verdade]
        self.assertEqual(encontrados, [0, 2])

    def test_mapa_por_linha_continua_funcionando(self):
        verdade = {2: "Hidrossanitária > Hidráulica"}
        semelhantes = [dict(item, id="") for item in _linhas()]
        encontrados = [i for i, item in enumerate(semelhantes)
                       if ab.chave_verdade(item) in verdade]
        self.assertEqual(encontrados, [0])


class TestRotuloDeTreino(unittest.TestCase):
    def test_prefere_a_referencia_humana(self):
        verdade = {"2025000001": "Estrutura Predial > Alvenaria"}
        self.assertEqual(ab.rotulo_de_treino(_linhas()[0], verdade),
                         "Estrutura Predial > Alvenaria")

    def test_usa_o_historico_quando_nao_ha_referencia(self):
        self.assertEqual(ab.rotulo_de_treino(_linhas()[1], {}),
                         "Elétrica > Iluminação")

    def test_nao_treina_contra_o_historico_onde_a_referencia_diverge(self):
        """O rotulo de treino nao pode ser o historico quando ha referencia.

        Treinar contra o historico e medir contra a referencia humana premiava
        o modelo por concordar com o rotulo que se pretendia auditar.
        """
        item = _linhas()[0]
        verdade = {"2025000001": "Estrutura Predial > Alvenaria"}
        self.assertNotEqual(ab.rotulo_de_treino(item, verdade), item["historico"])


if __name__ == "__main__":
    unittest.main()
