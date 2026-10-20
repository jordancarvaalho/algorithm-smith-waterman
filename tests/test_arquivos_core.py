"""Testes de core/arquivos.py: leitura de .txt/.fasta.

Cobre o critério de aceite de arquivo com três sequências (erro
seq_quantidade) e a leitura normal de arquivos com exatamente duas.
"""

import unittest

from core.arquivos import ler_sequencias


class TesteQuantidadeDeSequencias(unittest.TestCase):
    """Critério: arquivo .fasta com três sequências gera erro seq_quantidade."""

    def test_tres_sequencias_gera_erro_seq_quantidade(self):
        conteudo = b">seq1\nACGT\n>seq2\nACGG\n>seq3\nACGA\n"
        sequencias, erros = ler_sequencias("tres.fasta", conteudo)

        self.assertEqual(len(erros), 1)
        self.assertEqual(erros[0]["codigo"], "seq_quantidade")
        self.assertEqual(erros[0]["campo"], "arquivo")
        self.assertIn("3", erros[0]["mensagem"])


class TesteLeituraNormal(unittest.TestCase):
    def test_duas_sequencias_fasta_normalizadas(self):
        conteudo = b">seq1\nacgt\n>seq2\nACGG\n"
        sequencias, erros = ler_sequencias("duas.fasta", conteudo)
        self.assertEqual(erros, [])
        self.assertEqual(sequencias, ["ACGT", "ACGG"])

    def test_txt_sem_cabecalho_fasta(self):
        conteudo = b"ACGTAC\nACGTTC\n"
        sequencias, erros = ler_sequencias("duas.txt", conteudo)
        self.assertEqual(erros, [])
        self.assertEqual(sequencias, ["ACGTAC", "ACGTTC"])

    def test_extensao_invalida(self):
        sequencias, erros = ler_sequencias("duas.pdf", b"ACGT\nACGT\n")
        self.assertEqual(len(erros), 1)
        self.assertEqual(erros[0]["codigo"], "arquivo_formato")

    def test_base_invalida_em_arquivo(self):
        conteudo = b">seq1\nACGTX\n>seq2\nACGT\n"
        sequencias, erros = ler_sequencias("duas.fasta", conteudo)
        self.assertEqual(len(erros), 1)
        self.assertEqual(erros[0]["codigo"], "base_invalida")
        self.assertEqual(erros[0]["campo"], "seq1")


if __name__ == "__main__":
    unittest.main()
