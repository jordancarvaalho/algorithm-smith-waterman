"""Testes de export/arquivos.py.

Cobre os critérios de aceite: nomes de arquivo exatos do contrato, conteúdo
batendo com o Resultado da API, e a matriz COMPLETA ((m+1)x(n+1) células) no
CSV de pontuação mesmo para sequências acima do limite de exibição (60).
"""

import csv
import io
import unittest
import zipfile

from core.alinhamento import alinhar
from export.arquivos import (
    gerar_comparacao_zip,
    gerar_csv_alinhamento,
    gerar_csv_pontuacao,
    gerar_csv_traceback,
    gerar_txt,
    gerar_zip,
    nome_arquivo,
)

RESULTADO_CANONICO = alinhar("ACGTAC", "ACGTTC", "GLOBAL", 2, -1, -2)


class TesteNomesDeArquivo(unittest.TestCase):
    """Critério: exportação com os 4 nomes exatos do contrato."""

    def test_nomes_exatos_execucao_unica(self):
        self.assertEqual(nome_arquivo("txt", RESULTADO_CANONICO), "alinhamento_ACGTAC_ACGTTC.txt")
        self.assertEqual(
            nome_arquivo("csv_pontuacao", RESULTADO_CANONICO), "matriz_pontuacao_ACGTAC_ACGTTC.csv"
        )
        self.assertEqual(
            nome_arquivo("csv_traceback", RESULTADO_CANONICO), "matriz_traceback_ACGTAC_ACGTTC.csv"
        )
        self.assertEqual(
            nome_arquivo("csv_alinhamento", RESULTADO_CANONICO), "alinhamento_ACGTAC_ACGTTC.csv"
        )
        self.assertEqual(nome_arquivo("zip", RESULTADO_CANONICO), "alinhamento_ACGTAC_ACGTTC.zip")


class TesteConteudoCsvPontuacao(unittest.TestCase):
    """O CSV de pontuação deve bater exatamente com o exemplo da seção 6 do contrato."""

    def test_csv_pontuacao_bate_com_contrato(self):
        csv_texto = gerar_csv_pontuacao(RESULTADO_CANONICO)
        linhas = csv_texto.strip("﻿").splitlines()
        self.assertEqual(linhas[0], ",-,A,C,G,T,T,C")
        self.assertEqual(linhas[1], "-,0,-2,-4,-6,-8,-10,-12")
        self.assertEqual(linhas[2], "A,-2,2,0,-2,-4,-6,-8")

    def test_csv_usa_crlf_e_bom(self):
        csv_bytes = gerar_csv_pontuacao(RESULTADO_CANONICO).encode("utf-8-sig")
        self.assertTrue(csv_bytes.startswith(b"\xef\xbb\xbf"))
        self.assertIn(b"\r\n", csv_bytes)


class TesteConteudoBateComResultadoDaApi(unittest.TestCase):
    """Critério: conteúdo exportado bate com o resultado apresentado na tela (API)."""

    def test_csv_alinhamento_bate_com_marcacao_do_resultado(self):
        csv_texto = gerar_csv_alinhamento(RESULTADO_CANONICO)
        leitor = csv.reader(io.StringIO(csv_texto))
        linhas = list(leitor)
        self.assertEqual(linhas[0], ["Posicao", "Seq1", "Linha", "Seq2"])

        alinhamento = RESULTADO_CANONICO["alinhamento"]
        for pos, linha in enumerate(linhas[1:], start=1):
            self.assertEqual(linha[0], str(pos))
            self.assertEqual(linha[1], alinhamento["linha1"][pos - 1])
            self.assertEqual(linha[2], alinhamento["marcacao"][pos - 1])
            self.assertEqual(linha[3], alinhamento["linha2"][pos - 1])

    def test_txt_contem_score_e_alinhamento_do_resultado(self):
        texto = gerar_txt(RESULTADO_CANONICO)
        self.assertIn("Score final: 9", texto)
        self.assertIn("ACGTAC", texto)
        self.assertIn("||||.|", texto)

    def test_zip_contem_os_quatro_arquivos_com_conteudo_correto(self):
        conteudo_zip = gerar_zip(RESULTADO_CANONICO)
        with zipfile.ZipFile(io.BytesIO(conteudo_zip)) as zf:
            nomes = set(zf.namelist())
            self.assertEqual(
                nomes,
                {
                    "alinhamento_ACGTAC_ACGTTC.txt",
                    "matriz_pontuacao_ACGTAC_ACGTTC.csv",
                    "matriz_traceback_ACGTAC_ACGTTC.csv",
                    "alinhamento_ACGTAC_ACGTTC.csv",
                },
            )
            csv_pontuacao_do_zip = zf.read("matriz_pontuacao_ACGTAC_ACGTTC.csv").decode("utf-8-sig")
            self.assertEqual(csv_pontuacao_do_zip, gerar_csv_pontuacao(RESULTADO_CANONICO))


class TesteMatrizCompletaAcimaDoLimiteDeExibicao(unittest.TestCase):
    """Critério: sequências acima do limite de exibição (60) exportam a matriz COMPLETA."""

    def test_csv_pontuacao_tem_m_mais_1_por_n_mais_1_celulas(self):
        seq1 = "ACGT" * 20  # 80 bases, acima do LIMITE_EXIBICAO = 60
        seq2 = "TGCA" * 18  # 72 bases
        resultado = alinhar(seq1, seq2, "GLOBAL", 2, -1, -2)

        csv_texto = gerar_csv_pontuacao(resultado)
        linhas = [linha for linha in csv_texto.strip("﻿").split("\r\n") if linha]

        m, n = len(seq1), len(seq2)
        # 1 linha de cabeçalho + (m+1) linhas de dados; cada linha tem 1 rótulo + (n+1) valores.
        self.assertEqual(len(linhas), m + 2)
        for linha_dados in linhas[1:]:
            valores = linha_dados.split(",")
            self.assertEqual(len(valores), n + 2)  # rótulo + (n+1) células

    def test_matriz_retornada_pelo_core_tambem_e_completa(self):
        seq1 = "ACGT" * 20
        seq2 = "TGCA" * 18
        resultado = alinhar(seq1, seq2, "GLOBAL", 2, -1, -2)
        self.assertEqual(len(resultado["matriz"]), len(seq1) + 1)
        self.assertEqual(len(resultado["matriz"][0]), len(seq2) + 1)


class TesteComparacao(unittest.TestCase):
    """Critério: comparação exporta os arquivos de ambos os algoritmos com sufixo de modo."""

    def test_zip_de_comparacao_contem_arquivos_dos_dois_modos(self):
        resultado_global = alinhar("ACGTAC", "ACGTTC", "GLOBAL", 2, -1, -2)
        resultado_local = alinhar("ACGTAC", "ACGTTC", "LOCAL", 2, -1, -2)
        conteudo_zip = gerar_comparacao_zip(resultado_global, resultado_local)

        with zipfile.ZipFile(io.BytesIO(conteudo_zip)) as zf:
            nomes = set(zf.namelist())
            self.assertIn("matriz_pontuacao_global_ACGTAC_ACGTTC.csv", nomes)
            self.assertIn("matriz_pontuacao_local_ACGTAC_ACGTTC.csv", nomes)
            self.assertIn("alinhamento_comparacao_ACGTAC_ACGTTC.txt", nomes)


if __name__ == "__main__":
    unittest.main()
