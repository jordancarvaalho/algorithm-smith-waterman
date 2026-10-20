"""Testes do núcleo de alinhamento (core/alinhamento.py).

Cobre os critérios de aceite do PRD relativos ao caso canônico GLOBAL, às
regras de inicialização e parada do LOCAL, ao desempate dentro da célula e
ao determinismo da execução.
"""

import unittest

from core.alinhamento import alinhar

MATRIZ_CANONICA = [
    [0, -2, -4, -6, -8, -10, -12],
    [-2, 2, 0, -2, -4, -6, -8],
    [-4, 0, 4, 2, 0, -2, -4],
    [-6, -2, 2, 6, 4, 2, 0],
    [-8, -4, 0, 4, 8, 6, 4],
    [-10, -6, -2, 2, 6, 7, 5],
    [-12, -8, -4, 0, 4, 5, 9],
]


class TesteCasoCanonicoGlobal(unittest.TestCase):
    """Critério: Seq1=ACGTAC, Seq2=ACGTTC, match=2, mismatch=-1, gap=-2, GLOBAL."""

    def setUp(self):
        self.resultado = alinhar("ACGTAC", "ACGTTC", "GLOBAL", 2, -1, -2)

    def test_score_final_e_tamanho(self):
        self.assertEqual(self.resultado["score"], 9)
        self.assertEqual(self.resultado["tamanho"], 6)

    def test_alinhamento_e_marcacao(self):
        alinhamento = self.resultado["alinhamento"]
        self.assertEqual(alinhamento["linha1"], "ACGTAC")
        self.assertEqual(alinhamento["marcacao"], "||||.|")
        self.assertEqual(alinhamento["linha2"], "ACGTTC")

    def test_matriz_identica_a_secao_9_do_contrato(self):
        self.assertEqual(self.resultado["matriz"], MATRIZ_CANONICA)

    def test_celula_inferior_direita_vale_9(self):
        self.assertEqual(self.resultado["matriz"][6][6], 9)

    def test_primeira_linha_e_primeira_coluna(self):
        esperado = [0, -2, -4, -6, -8, -10, -12]
        self.assertEqual(self.resultado["matriz"][0], esperado)
        self.assertEqual([linha[0] for linha in self.resultado["matriz"]], esperado)

    def test_inicio_e_caminho_do_contrato(self):
        self.assertEqual(self.resultado["inicio"], [6, 6])
        self.assertEqual(
            self.resultado["caminho"],
            [[6, 6], [5, 5], [4, 4], [3, 3], [2, 2], [1, 1], [0, 0]],
        )


class TesteAlinhamentoLocal(unittest.TestCase):
    """Critérios de inicialização, não negatividade e score do LOCAL."""

    def setUp(self):
        # Sequências com uma região de similaridade clara cercada de ruído,
        # para garantir uma matriz com múltiplos candidatos a máximo local.
        self.resultado = alinhar("TTACGTACTT", "GGACGTACGG", "LOCAL", 2, -1, -2)

    def test_primeira_linha_e_coluna_sao_zero(self):
        matriz = self.resultado["matriz"]
        self.assertTrue(all(valor == 0 for valor in matriz[0]))
        self.assertTrue(all(linha[0] == 0 for linha in matriz))

    def test_nenhuma_celula_negativa(self):
        matriz = self.resultado["matriz"]
        self.assertTrue(all(valor >= 0 for linha in matriz for valor in linha))

    def test_score_igual_ao_maior_valor_da_matriz(self):
        matriz = self.resultado["matriz"]
        maior_valor = max(valor for linha in matriz for valor in linha)
        self.assertEqual(self.resultado["score"], maior_valor)

    def test_inicio_e_a_primeira_celula_de_valor_maximo_na_varredura(self):
        matriz = self.resultado["matriz"]
        maior_valor = max(valor for linha in matriz for valor in linha)
        primeira_ocorrencia = None
        for i, linha in enumerate(matriz):
            for j, valor in enumerate(linha):
                if valor == maior_valor:
                    primeira_ocorrencia = [i, j]
                    break
            if primeira_ocorrencia is not None:
                break
        self.assertEqual(self.resultado["inicio"], primeira_ocorrencia)

    def test_traceback_para_na_primeira_celula_zero_do_caminho(self):
        matriz = self.resultado["matriz"]
        caminho = self.resultado["caminho"]
        ultima_celula = caminho[-1]
        self.assertEqual(matriz[ultima_celula[0]][ultima_celula[1]], 0)
        # Nenhuma célula anterior no caminho pode já ser zero (a parada é a *primeira* zero).
        for celula in caminho[:-1]:
            self.assertNotEqual(matriz[celula[0]][celula[1]], 0)


class TesteDesempateDentroDaCelula(unittest.TestCase):
    """Critério: célula com empate múltiplo mostra todas as direções, maiúscula correta."""

    def test_empate_entre_duas_direcoes_diagonal_vence_vertical(self):
        # match=1, mismatch=-1, gap=-1 com "AAA"x"AAA" gera empates D/V e D/H conhecidos.
        resultado = alinhar("AAA", "AAA", "GLOBAL", 1, -1, -1)
        direcoes = resultado["direcoes"]
        self.assertIn("Dh", direcoes[1][2])
        self.assertIn("Dv", direcoes[2][1])
        # A maiúscula é sempre a primeira letra presente na ordem D, V, H.
        for linha in direcoes:
            for codigo in linha:
                if codigo == "-":
                    continue
                letras_maiusculas = [c for c in codigo if c.isupper()]
                self.assertEqual(len(letras_maiusculas), 1)
                self.assertEqual(codigo[0].upper(), letras_maiusculas[0])

    def test_empate_triplo_diagonal_vertical_horizontal(self):
        # Caso real (encontrado por busca exaustiva) onde as três direções
        # empatam no máximo de uma célula: a ordem D, V, H deve aparecer
        # completa, com D (primeira da prioridade) maiúscula.
        resultado = alinhar("AACC", "ACAA", "GLOBAL", 1, -1, -1)
        direcoes = resultado["direcoes"]
        codigos = {codigo for linha in direcoes for codigo in linha}
        self.assertIn("Dvh", codigos)


class TesteDeterminismo(unittest.TestCase):
    """Critério: mesma entrada e parâmetros produzem sempre o mesmo resultado."""

    def test_duas_execucoes_identicas_global(self):
        r1 = alinhar("ACGTACGTAC", "ACGTTCGTAG", "GLOBAL", 2, -1, -2)
        r2 = alinhar("ACGTACGTAC", "ACGTTCGTAG", "GLOBAL", 2, -1, -2)
        self.assertEqual(r1["caminho"], r2["caminho"])
        self.assertEqual(r1["direcoes"], r2["direcoes"])
        self.assertEqual(r1["alinhamento"], r2["alinhamento"])
        self.assertEqual(r1["score"], r2["score"])

    def test_duas_execucoes_identicas_local(self):
        r1 = alinhar("TTACGTACTT", "GGACGTACGG", "LOCAL", 2, -1, -2)
        r2 = alinhar("TTACGTACTT", "GGACGTACGG", "LOCAL", 2, -1, -2)
        self.assertEqual(r1["caminho"], r2["caminho"])
        self.assertEqual(r1["direcoes"], r2["direcoes"])
        self.assertEqual(r1["alinhamento"], r2["alinhamento"])
        self.assertEqual(r1["score"], r2["score"])


class TesteNormalizacaoEComprimentosDiferentes(unittest.TestCase):
    """Critério: acgta x TGCATG — maiúsculas e comprimentos diferentes funcionam."""

    def test_sequencias_minusculas_e_tamanhos_diferentes(self):
        from core.validacao import normalizar_sequencia

        seq1 = normalizar_sequencia("acgta")
        seq2 = normalizar_sequencia("TGCATG")
        self.assertEqual(seq1, "ACGTA")
        self.assertEqual(seq2, "TGCATG")

        resultado = alinhar(seq1, seq2, "GLOBAL", 2, -1, -2)
        self.assertEqual(len(resultado["matriz"]), 6)
        self.assertEqual(len(resultado["matriz"][0]), 7)
        self.assertEqual(resultado["tamanho"], len(resultado["alinhamento"]["linha1"]))


if __name__ == "__main__":
    unittest.main()
