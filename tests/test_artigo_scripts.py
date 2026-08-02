from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import ablation_lstm as ablation  # noqa: E402
import exportar_tabela_por_categoria as tabela_s1  # noqa: E402
import gerar_figura4_confusoes as figura4  # noqa: E402
import modelo_lstm  # noqa: E402


class TestExportarTabelaPorCategoria(unittest.TestCase):
    def test_normalizar_cabecalho_remove_acento_e_pontuacao(self):
        self.assertEqual(tabela_s1._normalizar_cabecalho(" F1-Score (%) "), "f1_score")
        self.assertEqual(tabela_s1._normalizar_cabecalho("Precisão"), "precisao")

    def test_carregar_json_publico_e_exportar_ordenado_por_concordancia(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            entrada = tmp_path / "metricas.json"
            saida = tmp_path / "tabela.csv"
            entrada.write_text(
                json.dumps([
                    {"categoria": "B", "qtd_classificados": 2, "taxa_concordancia": 0.9},
                    {"categoria": "A", "qtd_classificados": 1, "taxa_concordancia": 0.1},
                ]),
                encoding="utf-8",
            )

            with mock.patch.object(tabela_s1, "ENTRADA_JSON", entrada), mock.patch.object(tabela_s1, "SAIDA", saida):
                linhas = tabela_s1.carregar_do_json_publico()
                caminho = tabela_s1.exportar(linhas)

            self.assertEqual(caminho, saida)
            with saida.open(encoding="utf-8", newline="") as arq:
                rows = list(csv.DictReader(arq))
            self.assertEqual([r["categoria"] for r in rows], ["A", "B"])
            self.assertEqual(rows[0]["fonte"], "docs/dados/metricas_por_categoria.json (concordancia vs. historico; sem precision/recall/F1)")


class TestGerarFigura4Confusoes(unittest.TestCase):
    def test_agregar_pares_soma_por_modelo_e_ignora_incompletos(self):
        pares = figura4._agregar_pares([
            {"modelo": "m1", "pares": [
                {"de": "A", "para": "B", "n": 2},
                {"de": "", "para": "C", "n": 9},
            ]},
            {"modelo": "m2", "pares": [{"de": "A", "para": "B", "n": 3}]},
            {"modelo": "", "pares": [{"de": "C", "para": "D", "n": 1}]},
        ])

        self.assertEqual(pares[0]["de"], "A")
        self.assertEqual(pares[0]["para"], "B")
        self.assertEqual(pares[0]["total"], 5)
        self.assertEqual(dict(pares[0]["por_modelo"]), {"m1": 2, "m2": 3})
        self.assertEqual(pares[1]["por_modelo"]["modelo_desconhecido"], 1)

    def test_codificar_categorias_e_salvar_tabela_s2(self):
        with tempfile.TemporaryDirectory() as tmp:
            saida = Path(tmp) / "s2.csv"
            pares = [{"de": "Z", "para": "A", "total": 4}]
            codigos = figura4._codificar_categorias(pares)
            with mock.patch.object(figura4, "SAIDA_TABELA", saida):
                figura4._salvar_tabela_s2(codigos)

            self.assertEqual(codigos, {"A": "C01", "Z": "C02"})
            with saida.open(encoding="utf-8", newline="") as arq:
                rows = list(csv.DictReader(arq))
            self.assertEqual(rows, [{"codigo": "C01", "categoria": "A"}, {"codigo": "C02", "categoria": "Z"}])


class TestAblationLSTM(unittest.TestCase):
    def test_normalizar_e_hash_texto(self):
        self.assertEqual(ablation.normalizar_texto("  Ár   CONDICIONADO\nNão GELA  "), "ar condicionado nao gela")
        self.assertEqual(ablation.hash_texto_normalizado("Água"), ablation.hash_texto_normalizado("agua"))

    def test_diagnosticar_duplicatas_folds_mede_vazamento_do_kfold_antigo(self):
        linhas = [
            {"linha": i + 2, "texto": "Mesmo texto", "historico": "A"}
            for i in range(6)
        ]
        verdade = {item["linha"]: "A" for item in linhas}

        diag = ablation.diagnosticar_duplicatas_folds(linhas, verdade, 3)

        self.assertEqual(diag["n_validado"], 6)
        self.assertEqual(diag["grupos_duplicados_validados"], 1)
        self.assertEqual(diag["teste_com_duplicata_no_treino"], 6)
        self.assertEqual(diag["taxa_vazamento"], 1.0)
        self.assertEqual([f["n_teste"] for f in diag["folds"]], [2, 2, 2])

    def test_diagnosticar_protocolos_lstm_compara_historico_e_aba_oficial(self):
        class FakeWorksheet:
            def get_values(self, *_args, **_kwargs):
                return [
                    ["run_id", "linha_planilha", "id", "historico", "categoria_ia", "confianca", "faixa", "executor", "acerto"],
                    ["r", 2, "1", "A", "A", 0.9, "", "lstm", "TRUE"],
                    ["r", 3, "2", "A", "A", 0.8, "", "lstm", "TRUE"],
                ]

        class FakeSheet:
            def worksheet(self, nome):
                self.nome = nome
                return FakeWorksheet()

        # A aba CLASSIF__ traz os ids "1" e "2"; a verdade e indexada pelos
        # mesmos ids, nunca pela linha (incidente de 2026-08-02).
        linhas = [
            {"linha": 2, "id": "1", "texto": "x", "historico": "A"},
            {"linha": 3, "id": "2", "texto": "y", "historico": "A"},
            {"linha": 4, "id": "3", "texto": "z", "historico": "B"},
        ]
        verdade = {"1": "A", "2": "B", "3": "B"}
        config = {
            "multimodelo": {"aba_classificacao": "CLASSIF__{modelo}", "k_folds": 5},
            "memoria_validada": {"habilitada": True, "peso_treino": 3},
        }

        diag = ablation.diagnosticar_protocolos_lstm(FakeSheet(), config, linhas, verdade, 3)

        self.assertEqual(diag["escopo"]["n_validadas_com_verdade"], 3)
        self.assertEqual(diag["escopo"]["n_intersecao_validada_oficial"], 2)
        self.assertEqual(diag["materializacao_oficial_lstm"]["run_ids"], {"r": 2})
        self.assertEqual(diag["materializacao_oficial_lstm"]["executores"], {"lstm": 2})
        self.assertEqual(diag["parametros_lstm_resolvidos"]["parametros_efetivos_iguais_no_ambiente_atual"], True)
        self.assertEqual(diag["historico_vs_verdade"]["historico_igual_verdade"], 2)
        self.assertEqual(diag["historico_vs_verdade"]["taxa_historico_igual_verdade"], 0.666667)
        self.assertEqual(diag["oficial_lstm_vs_verdade"]["acertos"], 1)
        self.assertEqual(diag["oficial_lstm_vs_verdade"]["taxa_acerto"], 0.5)

    def test_diagnosticar_materializacao_oficial_nova_nao_escreve_planilha(self):
        class FakeSheet:
            def worksheet(self, nome):
                class FakeWorksheet:
                    def get_values(self, *_args, **_kwargs):
                        if nome == "CLASSIF__lstm":
                            return [
                                ["run_id", "linha_planilha", "id", "historico", "categoria_ia", "confianca"],
                                ["r", 2, "1", "A", "B", 0.2],
                                ["r", 3, "2", "B", "B", 0.8],
                            ]
                        return [[]]
                return FakeWorksheet()

        # id_chamado e a chave: a aba CLASSIF__ e materializada antes e a base
        # muda de tamanho depois (incidente de 2026-08-02).
        linhas = [
            {"linha": 2, "id": "1", "texto": "x", "historico": "A"},
            {"linha": 3, "id": "2", "texto": "y", "historico": "B"},
        ]
        verdade = {"1": "A", "2": "B"}
        config = {
            "multimodelo": {
                "aba_classificacao": "CLASSIF__{modelo}",
                "k_folds": 5,
                "min_base_treino": 200,
                "fracao_topup": 0.25,
            },
            "modelo_ia": {"lstm": {"perfil": "padrao", "usar_class_weight": True}},
            "memoria_validada": {"habilitada": False, "peso_treino": 3},
            "abas_experimento": {"validacao_humana": "VALIDACAO_HUMANA"},
        }

        with mock.patch.object(ablation.cm, "prever_out_of_fold", return_value=(["A", "B"], [0.9, 0.7], "kfold_5", False)) as prever:
            diag = ablation.diagnosticar_materializacao_oficial_nova(FakeSheet(), config, linhas, verdade)

        prever.assert_called_once()
        self.assertEqual(diag["materializacao_nova_vs_verdade"]["taxa_acerto"], 1.0)
        self.assertEqual(diag["materializacao_antiga_vs_verdade"]["taxa_acerto"], 0.5)
        self.assertEqual(diag["comparacao_nova_antiga"]["nova_acerta_antiga_erra"], 1)


class TestModeloLSTMHistoryCLI(unittest.TestCase):
    def test_salvar_history_exige_fit_e_grava_json(self):
        clf = modelo_lstm.ClassificadorLSTM()
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "history.json"
            with self.assertRaises(RuntimeError):
                clf.salvar_history(caminho)

            clf.history_ = {"loss": [1, 0.5], "val_accuracy": [0.2, 0.4]}
            clf.salvar_history(caminho)
            self.assertEqual(json.loads(caminho.read_text(encoding="utf-8")), clf.history_)

    def test_main_cli_salva_history_sem_treino_real(self):
        class FakeLSTM:
            instancias = []

            def __init__(self, **params):
                self.params = params
                self.history_ = {"loss": [1.0], "accuracy": [0.75]}
                FakeLSTM.instancias.append(self)

            def fit(self, textos, categorias, **kwargs):
                self.fit_args = (list(textos), list(categorias), kwargs)
                return self

            def salvar_history(self, caminho):
                Path(caminho).write_text(json.dumps(self.history_), encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config = tmp_path / "config.json"
            history_json = tmp_path / "history.json"
            history_fig = tmp_path / "history.png"
            config.write_text(json.dumps({"modelo_ia": {"lstm": {"epochs": 3, "batch_size": 4}}}), encoding="utf-8")
            argv = [
                "modelo_lstm.py",
                "--config", str(config),
                "--history-json", str(history_json),
                "--history-fig", str(history_fig),
                "--epochs", "1",
                "--batch-size", "2",
                "--verbose", "0",
            ]

            with mock.patch.object(sys, "argv", argv), \
                    mock.patch.object(modelo_lstm, "carregar_base_planilha", return_value=(["a", "b"], ["A", "B"])), \
                    mock.patch.object(modelo_lstm, "ClassificadorLSTM", FakeLSTM), \
                    mock.patch.object(modelo_lstm, "plotar_history") as plotar:
                rc = modelo_lstm.main()

            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(history_json.read_text(encoding="utf-8")), {"loss": [1.0], "accuracy": [0.75]})
            self.assertEqual(FakeLSTM.instancias[0].fit_args[2]["epochs"], 1)
            self.assertEqual(FakeLSTM.instancias[0].fit_args[2]["batch_size"], 2)
            plotar.assert_called_once_with({"loss": [1.0], "accuracy": [0.75]}, history_fig)


if __name__ == "__main__":
    unittest.main()
