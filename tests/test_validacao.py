"""Testes de core/validacao.py.

Cobre os critérios de aceite de validação de entrada: base inválida citando
posição, múltiplos erros na mesma resposta, e aviso de consistência não
bloqueante processando o alinhamento mesmo assim.
"""

import unittest

from core.alinhamento import alinhar
from core.validacao import normalizar_sequencia, validar


class TesteBaseInvalida(unittest.TestCase):
    """Critério: Seq1 = ACGTAXTG não processa e aponta base X na posição correta."""

    def test_erro_cita_base_e_posicao(self):
        seq1 = normalizar_sequencia("ACGTAXTG")
        seq2 = normalizar_sequencia("ACGT")
        erros, avisos, parametros = validar(seq1, seq2, "GLOBAL", 2, -1, -2)

        self.assertEqual(len(erros), 1)
        erro = erros[0]
        self.assertEqual(erro["codigo"], "base_invalida")
        self.assertEqual(erro["campo"], "seq1")
        self.assertIn('"X"', erro["mensagem"])
        self.assertIn("posição 6", erro["mensagem"])


class TesteMultiplosErrosNaMesmaResposta(unittest.TestCase):
    """Critério: Seq2 vazia e Gap não numérico ao mesmo tempo geram os DOIS erros."""

    def test_seq2_vazia_e_gap_nao_numerico_juntos(self):
        seq1 = normalizar_sequencia("ACGT")
        seq2 = normalizar_sequencia("")
        erros, avisos, parametros = validar(seq1, seq2, "GLOBAL", 2, -1, "abc")

        codigos = {erro["codigo"] for erro in erros}
        self.assertIn("seq_vazia", codigos)
        self.assertIn("parametro_nao_numerico", codigos)
        self.assertEqual(len(erros), 2)

        campo_seq_vazia = next(e for e in erros if e["codigo"] == "seq_vazia")
        self.assertEqual(campo_seq_vazia["campo"], "seq2")
        campo_gap = next(e for e in erros if e["codigo"] == "parametro_nao_numerico")
        self.assertEqual(campo_gap["campo"], "gap")


class TesteAvisoDeConsistencia(unittest.TestCase):
    """Critério: Match = -1 gera aviso de consistência, mas o alinhamento é processado."""

    def test_match_negativo_gera_aviso_sem_bloquear(self):
        seq1 = normalizar_sequencia("ACGT")
        seq2 = normalizar_sequencia("ACGT")
        erros, avisos, parametros = validar(seq1, seq2, "GLOBAL", -1, -1, -2)

        self.assertEqual(erros, [])
        codigos_aviso = {aviso["codigo"] for aviso in avisos}
        self.assertIn("match_nao_positivo", codigos_aviso)

        # O alinhamento deve poder ser processado mesmo com o aviso presente.
        resultado = alinhar(seq1, seq2, "GLOBAL", parametros["match"], parametros["mismatch"], parametros["gap"])
        self.assertIsNotNone(resultado["score"])
        self.assertEqual(resultado["tamanho"], 4)


class TesteNormalizacao(unittest.TestCase):
    def test_minusculas_viram_maiusculas(self):
        self.assertEqual(normalizar_sequencia("acgta"), "ACGTA")

    def test_remove_espacos_e_quebras_de_linha(self):
        self.assertEqual(normalizar_sequencia(" AC GT\nAC\t"), "ACGTAC")


if __name__ == "__main__":
    unittest.main()
