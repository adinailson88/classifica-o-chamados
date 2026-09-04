#!/usr/bin/env python3
"""Regressão do incidente de 09/2026: G ficou preso na IA de outro chamado a
partir da linha 13304, e ninguém notou porque a linha já tinha G preenchido
(não é mais "pendente") e o gate de escrita (PR #254) só age no momento de
gravar -- linhas que não precisam ser reescritas nunca passam por ele.

`auditar_alinhamento_id` fecha essa lacuna comparando o id_chamado atual da
coluna A com o id_chamado registrado em SNAPSHOT_ETAPA_1 na última vez que a
linha foi classificada.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import auditar_alinhamento_id as aud  # noqa: E402


class _WsSnapshot:
    def __init__(self, linhas):
        self._linhas = linhas

    def get_values(self, _range, value_render_option=None):  # noqa: ARG002
        cab = ["run_id", "linha_planilha", "id_chamado"]
        return [cab, *self._linhas]


class _WsPrincipal:
    """Fake mínimo: guarda um bloco A:M e os ranges limpos por batch_clear."""

    def __init__(self, bloco_por_linha: dict[int, dict[str, str]], linha_min: int, linha_max: int):
        self._bloco_por_linha = bloco_por_linha
        self._linha_min = linha_min
        self._linha_max = linha_max
        self.ranges_limpos: list[str] = []

    def get_values(self, range_a1, value_render_option=None):  # noqa: ARG002
        # Ignora o range pedido e devolve o bloco A:M inteiro montado no setup;
        # ler_valores() só usa o resultado, não valida o range em si.
        linhas = []
        for linha in range(self._linha_min, self._linha_max + 1):
            dados = self._bloco_por_linha.get(linha, {})
            row = [""] * 13
            row[0] = dados.get("A", "")
            row[6] = dados.get("G", "")
            row[12] = dados.get("M", "")
            linhas.append(row)
        return linhas

    def batch_clear(self, ranges):
        self.ranges_limpos.extend(ranges)


def linha_snapshot(linha_planilha, id_chamado, run_id="run1"):
    return [run_id, linha_planilha, id_chamado]


class TestEncontrarOrfas(unittest.TestCase):
    def test_linha_alinhada_nao_e_orfa(self):
        ultimo = {10: "111"}
        ws = _WsPrincipal({10: {"A": "111", "G": "Eletrica > Iluminacao"}}, 10, 10)

        orfas, protegidas = aud.encontrar_orfas(ws, ultimo)

        self.assertEqual(orfas, [])
        self.assertEqual(protegidas, [])

    def test_linha_com_id_deslocado_e_orfa(self):
        # A linha 13304 foi classificada como o chamado 128; depois um lote
        # novo entrou no meio da fonte e a linha 13304 agora e outro chamado.
        ultimo = {13304: "128"}
        ws = _WsPrincipal(
            {13304: {"A": "999", "G": "Manutencao Preventiva > Elevador"}}, 13304, 13304)

        orfas, protegidas = aud.encontrar_orfas(ws, ultimo)

        self.assertEqual(len(orfas), 1)
        self.assertEqual(orfas[0]["linha"], 13304)
        self.assertEqual(orfas[0]["id_esperado"], "128")
        self.assertEqual(orfas[0]["id_atual"], "999")
        self.assertEqual(protegidas, [])

    def test_linha_orfa_mas_conferida_fica_protegida(self):
        ultimo = {20: "50"}
        ws = _WsPrincipal(
            {20: {"A": "999", "G": "Hidrossanitaria > Hidraulica", "M": "TRUE"}}, 20, 20)

        orfas, protegidas = aud.encontrar_orfas(ws, ultimo)

        self.assertEqual(orfas, [])
        self.assertEqual(len(protegidas), 1)
        self.assertEqual(protegidas[0]["linha"], 20)

    def test_linha_pendente_g_vazio_e_ignorada(self):
        ultimo = {30: "70"}
        ws = _WsPrincipal({30: {"A": "70", "G": ""}}, 30, 30)

        orfas, protegidas = aud.encontrar_orfas(ws, ultimo)

        self.assertEqual(orfas, [])
        self.assertEqual(protegidas, [])

    def test_normaliza_id_numerico_do_sheets(self):
        self.assertEqual(aud.normalizar_id(128.0), "128")
        self.assertEqual(aud.normalizar_id("2026030128"), "2026030128")
        self.assertEqual(aud.normalizar_id(""), "")


class TestUltimaClassificacaoPorLinha(unittest.TestCase):
    def test_pega_a_ocorrencia_mais_recente_por_linha(self):
        class _Sh:
            def worksheet(self_inner, nome):  # noqa: N805
                self.assertEqual(nome, "SNAPSHOT_ETAPA_1")
                return _WsSnapshot([
                    linha_snapshot(10, "111", run_id="run1"),
                    linha_snapshot(10, "222", run_id="run2"),  # reclassificada depois
                    linha_snapshot(11, "333"),
                ])

        ultimo = aud.ultima_classificacao_por_linha(_Sh(), "SNAPSHOT_ETAPA_1")

        self.assertEqual(ultimo, {10: "222", 11: "333"})


class TestLimparOrfas(unittest.TestCase):
    def test_limpa_so_g_k_das_linhas_orfas_em_lotes(self):
        ws = _WsPrincipal({}, 1, 1)
        orfas = [{"linha": n} for n in range(1, 251)]  # forca 3 lotes de 100

        aud.limpar_orfas(ws, orfas)

        self.assertEqual(len(ws.ranges_limpos), 250)
        self.assertEqual(ws.ranges_limpos[0], "G1:K1")
        self.assertEqual(ws.ranges_limpos[-1], "G250:K250")


if __name__ == "__main__":
    unittest.main()
