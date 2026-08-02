import sys
import types
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

sys.modules.setdefault("planilha", types.SimpleNamespace())
sys.modules.setdefault("tempo", types.SimpleNamespace(agora_bahia=lambda: "2026-06-11T00:00:00-03:00"))

from tipo_manutencao import (  # noqa: E402
    CORRETIVA, NAO_MANUTENCAO, PREVENTIVA, TIPOS, familia, sigla, tipo_manutencao,
)


class TipoManutencaoTest(unittest.TestCase):
    def test_categoria_preventiva_com_separador(self):
        self.assertEqual(
            tipo_manutencao("Manutenção Preventiva > Gerador > Inspeção"),
            "Preventiva",
        )

    def test_categoria_preventiva_sem_espaco_antes_do_separador(self):
        self.assertEqual(
            tipo_manutencao("Manutencao Preventiva>Ar-condicionado"),
            "Preventiva",
        )

    def test_categoria_corretiva_quando_nao_tem_prefixo(self):
        self.assertEqual(
            tipo_manutencao("Elétrica > Iluminação > Lâmpada queimada"),
            "Corretiva",
        )

    def test_categoria_vazia_e_corretiva(self):
        self.assertEqual(tipo_manutencao(""), "Corretiva")

    def test_raiz_preventiva_sem_separador_e_preventiva(self):
        """Os 2 chamados da raiz caiam em Corretiva porque a regra exigia '>'."""
        self.assertEqual(tipo_manutencao("Manutenção Preventiva"), PREVENTIVA)


class NaoManutencaoTest(unittest.TestCase):
    """Decisao do pesquisador em 02/08/2026: 595 chamados que nao sao manutencao."""

    def test_erro_de_chamado(self):
        self.assertEqual(tipo_manutencao("Outros > Erro de chamado"), NAO_MANUTENCAO)

    def test_posto_de_trabalho(self):
        self.assertEqual(
            tipo_manutencao("Posto de trabalho > Contratação de Posto de trabalho"),
            NAO_MANUTENCAO)

    def test_suprimentos_com_e_sem_espaco_na_barra(self):
        self.assertEqual(
            tipo_manutencao("Suprimentos / Apoio Técnico > Materiais"), NAO_MANUTENCAO)
        self.assertEqual(
            tipo_manutencao("Suprimentos/Apoio Técnico > Materiais"), NAO_MANUTENCAO)

    def test_projetos_e_reformas(self):
        self.assertEqual(tipo_manutencao("Projetos e Reformas > Reforma"), NAO_MANUTENCAO)

    def test_raizes_legadas(self):
        self.assertEqual(
            tipo_manutencao("Projeto > Elétrico (tomada e iluminação)"), NAO_MANUTENCAO)
        self.assertEqual(tipo_manutencao("Revisão > Telecomunicações"), NAO_MANUTENCAO)

    def test_ti_permanece_corretiva(self):
        """Decisao expressa: reparo de rede e infraestrutura predial."""
        self.assertEqual(
            tipo_manutencao("TI / Dados / Rede > Ponto de rede / fibra ótica / Wi-fi"),
            CORRETIVA)

    def test_familia_nao_e_comparada_por_prefixo(self):
        """'Projeto' nao pode capturar 'Projetos e Reformas' por prefixo, nem
        o contrario; ambas sao Nao manutencao, mas por regra propria."""
        self.assertEqual(familia("Projetos e Reformas > Reforma"), "Projetos e Reformas")
        self.assertEqual(familia("Projeto > Elétrico"), "Projeto")

    def test_familia_de_categoria_sem_separador(self):
        self.assertEqual(familia("Manutenção Preventiva"), "Manutenção Preventiva")


class SemDuplicacaoTest(unittest.TestCase):
    """A funcao tem uma unica implementacao em Python; o painel a importa."""

    def test_dashboard_usa_a_mesma_funcao(self):
        import exportar_dashboard
        self.assertIs(exportar_dashboard.tipo_manutencao, tipo_manutencao)

    def test_espelho_javascript_do_painel_lista_as_mesmas_familias(self):
        """docs/index.html tem um fallback em JS que precisa nao divergir."""
        from tipo_manutencao import FAMILIAS_NAO_MANUTENCAO
        html = (RAIZ / "docs" / "index.html").read_text(encoding="utf-8")
        trecho = html.split("const FAMILIAS_NAO_MANUTENCAO")[1].split("]")[0]
        for chave in FAMILIAS_NAO_MANUTENCAO:
            self.assertIn(f'"{chave}"', trecho)


class SiglaTest(unittest.TestCase):
    def test_siglas_da_tabela_do_apendice(self):
        self.assertEqual(sigla(PREVENTIVA), "P")
        self.assertEqual(sigla(CORRETIVA), "C")
        self.assertEqual(sigla(NAO_MANUTENCAO), "NM")

    def test_todo_tipo_tem_sigla(self):
        self.assertTrue(all(sigla(t) for t in TIPOS))


if __name__ == "__main__":
    unittest.main()
