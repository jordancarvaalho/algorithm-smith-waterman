"""Algoritmos de alinhamento global (Needleman-Wunsch) e local (Smith-Waterman)."""


def _pontuacao(base1: str, base2: str, match: int, mismatch: int) -> int:
    """Pontuação de alinhar duas bases: Match se iguais, Mismatch se diferentes."""
    return match if base1 == base2 else mismatch


def _codigo_direcao(diagonal: bool, vertical: bool, horizontal: bool) -> str:
    """Codifica as direções empatadas no máximo: ordem D, V, H; primeira é a seguida."""
    candidatas = [letra for letra, igual in (("D", diagonal), ("V", vertical), ("H", horizontal)) if igual]
    if not candidatas:
        return "-"
    seguida = candidatas[0]
    return "".join(letra if letra == seguida else letra.lower() for letra in candidatas)


def _letra_seguida(codigo_celula: str) -> str | None:
    """Extrai a letra maiúscula (direção seguida) de um código de célula, ou None."""
    for letra in codigo_celula:
        if letra.isupper():
            return letra
    return None


def _preencher_global(
    seq1: str, seq2: str, match: int, mismatch: int, gap: int
) -> tuple[list[list[int]], list[list[str]]]:
    m, n = len(seq1), len(seq2)
    matriz = [[0] * (n + 1) for _ in range(m + 1)]
    direcoes = [["-"] * (n + 1) for _ in range(m + 1)]

    for j in range(1, n + 1):
        matriz[0][j] = j * gap
        direcoes[0][j] = "H"
    for i in range(1, m + 1):
        matriz[i][0] = i * gap
        direcoes[i][0] = "V"

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            diagonal = matriz[i - 1][j - 1] + _pontuacao(seq1[i - 1], seq2[j - 1], match, mismatch)
            vertical = matriz[i - 1][j] + gap
            horizontal = matriz[i][j - 1] + gap
            valor = max(diagonal, vertical, horizontal)
            matriz[i][j] = valor
            direcoes[i][j] = _codigo_direcao(diagonal == valor, vertical == valor, horizontal == valor)

    return matriz, direcoes


def _preencher_local(
    seq1: str, seq2: str, match: int, mismatch: int, gap: int
) -> tuple[list[list[int]], list[list[str]]]:
    m, n = len(seq1), len(seq2)
    matriz = [[0] * (n + 1) for _ in range(m + 1)]
    direcoes = [["-"] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            diagonal = matriz[i - 1][j - 1] + _pontuacao(seq1[i - 1], seq2[j - 1], match, mismatch)
            vertical = matriz[i - 1][j] + gap
            horizontal = matriz[i][j - 1] + gap
            valor = max(diagonal, vertical, horizontal, 0)
            matriz[i][j] = valor
            if valor == 0:
                direcoes[i][j] = "-"
            else:
                direcoes[i][j] = _codigo_direcao(diagonal == valor, vertical == valor, horizontal == valor)

    return matriz, direcoes


def _encontrar_inicio_local(matriz: list[list[int]]) -> list[int]:
    """Primeira célula de valor máximo, varrendo linha a linha, de cima para baixo e da esquerda para a direita."""
    melhor_i, melhor_j, melhor_valor = 0, 0, matriz[0][0]
    for i, linha in enumerate(matriz):
        for j, valor in enumerate(linha):
            if valor > melhor_valor:
                melhor_i, melhor_j, melhor_valor = i, j, valor
    return [melhor_i, melhor_j]


def _rastrear(
    modo: str, matriz: list[list[int]], direcoes: list[list[str]], inicio: list[int]
) -> tuple[list[list[int]], list[str]]:
    """Executa o traceback a partir de `inicio`. Devolve (caminho, movimentos)."""
    caminho: list[list[int]] = []
    movimentos: list[str] = []
    i, j = inicio

    while True:
        caminho.append([i, j])
        if modo == "GLOBAL":
            if i == 0 and j == 0:
                break
        else:
            if matriz[i][j] == 0:
                break

        letra = _letra_seguida(direcoes[i][j])
        if letra is None:
            break
        movimentos.append(letra)
        if letra == "D":
            i, j = i - 1, j - 1
        elif letra == "V":
            i, j = i - 1, j
        else:
            i, j = i, j - 1

    return caminho, movimentos


def _reconstruir_alinhamento(
    seq1: str, seq2: str, caminho: list[list[int]], movimentos: list[str]
) -> tuple[str, str, str]:
    linha1: list[str] = []
    linha2: list[str] = []
    marcacao: list[str] = []

    for indice, movimento in enumerate(movimentos):
        i_atual, j_atual = caminho[indice]
        if movimento == "D":
            base1, base2 = seq1[i_atual - 1], seq2[j_atual - 1]
            linha1.append(base1)
            linha2.append(base2)
            marcacao.append("|" if base1 == base2 else ".")
        elif movimento == "V":
            linha1.append(seq1[i_atual - 1])
            linha2.append("-")
            marcacao.append(" ")
        else:
            linha1.append("-")
            linha2.append(seq2[j_atual - 1])
            marcacao.append(" ")

    return (
        "".join(reversed(linha1)),
        "".join(reversed(marcacao)),
        "".join(reversed(linha2)),
    )


def alinhar(seq1: str, seq2: str, modo: str, match: int, mismatch: int, gap: int) -> dict:
    """Calcula o alinhamento GLOBAL (Needleman-Wunsch) ou LOCAL (Smith-Waterman).

    Pressupõe `seq1`/`seq2` já normalizadas e validadas, e `modo` em {"GLOBAL", "LOCAL"}.
    Devolve o dicionário `Resultado` (seção 1 do contrato); `avisos` sai vazio e é
    preenchido pela camada que chamou `validar`.
    """
    m, n = len(seq1), len(seq2)

    if modo == "GLOBAL":
        matriz, direcoes = _preencher_global(seq1, seq2, match, mismatch, gap)
        inicio = [m, n]
    else:
        matriz, direcoes = _preencher_local(seq1, seq2, match, mismatch, gap)
        inicio = _encontrar_inicio_local(matriz)

    caminho, movimentos = _rastrear(modo, matriz, direcoes, inicio)
    linha1, marcacao, linha2 = _reconstruir_alinhamento(seq1, seq2, caminho, movimentos)
    score = matriz[inicio[0]][inicio[1]]

    return {
        "modo": modo,
        "seq1": seq1,
        "seq2": seq2,
        "parametros": {"match": match, "mismatch": mismatch, "gap": gap},
        "matriz": matriz,
        "direcoes": direcoes,
        "caminho": caminho,
        "inicio": inicio,
        "alinhamento": {"linha1": linha1, "marcacao": marcacao, "linha2": linha2},
        "score": score,
        "tamanho": len(linha1),
        "avisos": [],
    }
