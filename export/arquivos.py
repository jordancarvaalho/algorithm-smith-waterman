"""Serialização pura do Resultado de um alinhamento para .txt, .csv e .zip.

Todas as funções recebem o `Resultado` (seção 1 do contrato de API) como
`dict` e devolvem `str` ou `bytes`. Nenhuma função escreve em disco, mantém
estado global ou depende de `core/`. Usa apenas a biblioteca padrão.
"""

from __future__ import annotations

import csv
import io
import zipfile

_TRUNCAR_EM = 20

_NOME_MODO = {
    "GLOBAL": "GLOBAL (Needleman-Wunsch)",
    "LOCAL": "LOCAL (Smith-Waterman)",
}

_TEMPLATES_NOME = {
    "txt": "alinhamento{sufixo}_{s1}_{s2}.txt",
    "csv_pontuacao": "matriz_pontuacao{sufixo}_{s1}_{s2}.csv",
    "csv_traceback": "matriz_traceback{sufixo}_{s1}_{s2}.csv",
    "csv_alinhamento": "alinhamento{sufixo}_{s1}_{s2}.csv",
    "zip": "alinhamento{sufixo}_{s1}_{s2}.zip",
    "comparacao_zip": "comparacao_{s1}_{s2}.zip",
}

_LEGENDA_ALINHAMENTO = "Legenda do alinhamento: | match, . mismatch, espaço indica gap."
_LEGENDA_DIRECOES = (
    "Legenda das direções (matriz de traceback): D diagonal, V vertical, H horizontal.\n"
    "Maiúscula = direção seguida; minúscula = direção empatada não seguida; - = sem direção.\n"
    "Desempate dentro da célula: diagonal, vertical, horizontal.\n"
    "Início do traceback (LOCAL): primeira célula de valor máximo na varredura de cima para "
    "baixo, da esquerda para a direita."
)


def _truncar(sequencia: str) -> str:
    """Trunca uma sequência em até 20 caracteres, para uso em nomes de arquivo."""
    return sequencia[:_TRUNCAR_EM]


def nome_arquivo(formato: str, resultado: dict, sufixo_modo: str | None = None) -> str:
    """Monta o nome de arquivo exportado conforme a seção 6 do contrato."""
    template = _TEMPLATES_NOME[formato]
    sufixo = f"_{sufixo_modo}" if sufixo_modo else ""
    s1 = _truncar(resultado["seq1"])
    s2 = _truncar(resultado["seq2"])
    return template.format(sufixo=sufixo, s1=s1, s2=s2)


def _escrever_csv(cabecalho: list[str], linhas: list[list[str]]) -> str:
    """Serializa cabeçalho e linhas em CSV (vírgula, \\r\\n, UTF-8 com BOM)."""
    buffer = io.StringIO()
    escritor = csv.writer(buffer, delimiter=",", lineterminator="\r\n")
    escritor.writerow(cabecalho)
    for linha in linhas:
        escritor.writerow(linha)
    return buffer.getvalue()


def _cabecalho_matriz(resultado: dict) -> list[str]:
    return ["", "-", *resultado["seq2"]]


def gerar_csv_pontuacao(resultado: dict) -> str:
    """Gera o CSV com a matriz de programação dinâmica completa."""
    seq1 = resultado["seq1"]
    matriz = resultado["matriz"]
    linhas = []
    for i, valores in enumerate(matriz):
        rotulo = "-" if i == 0 else seq1[i - 1]
        linhas.append([rotulo, *[str(v) for v in valores]])
    return _escrever_csv(_cabecalho_matriz(resultado), linhas)


def gerar_csv_traceback(resultado: dict) -> str:
    """Gera o CSV com a matriz de direções (codificação da seção 2)."""
    seq1 = resultado["seq1"]
    direcoes = resultado["direcoes"]
    linhas = []
    for i, valores in enumerate(direcoes):
        rotulo = "-" if i == 0 else seq1[i - 1]
        linhas.append([rotulo, *valores])
    return _escrever_csv(_cabecalho_matriz(resultado), linhas)


def gerar_csv_alinhamento(resultado: dict) -> str:
    """Gera o CSV com uma linha por posição do alinhamento final."""
    alinhamento = resultado["alinhamento"]
    linha1 = alinhamento["linha1"]
    marcacao = alinhamento["marcacao"]
    linha2 = alinhamento["linha2"]
    linhas = [
        [str(pos), linha1[pos - 1], marcacao[pos - 1], linha2[pos - 1]]
        for pos in range(1, resultado["tamanho"] + 1)
    ]
    return _escrever_csv(["Posicao", "Seq1", "Linha", "Seq2"], linhas)


def _bloco_resumo(resultado: dict) -> list[str]:
    """Monta as linhas de resumo (algoritmo, sequências, parâmetros, score, alinhamento)."""
    parametros = resultado["parametros"]
    alinhamento = resultado["alinhamento"]
    return [
        f"ALINHAMENTO {_NOME_MODO[resultado['modo']]}",
        f"Sequência 1: {resultado['seq1']}",
        f"Sequência 2: {resultado['seq2']}",
        f"Match: {parametros['match']}",
        f"Mismatch: {parametros['mismatch']}",
        f"Gap: {parametros['gap']}",
        f"Score final: {resultado['score']}",
        f"Tamanho do alinhamento: {resultado['tamanho']}",
        "",
        "Alinhamento final:",
        f"Seq1: {alinhamento['linha1']}",
        f"      {alinhamento['marcacao']}",
        f"Seq2: {alinhamento['linha2']}",
    ]


def gerar_txt(resultado: dict) -> str:
    """Gera o .txt de resumo completo de uma execução única (seção 6)."""
    nome_pontuacao = nome_arquivo("csv_pontuacao", resultado)
    nome_traceback = nome_arquivo("csv_traceback", resultado)
    linhas = [
        *_bloco_resumo(resultado),
        "",
        _LEGENDA_ALINHAMENTO,
        _LEGENDA_DIRECOES,
        "",
        f"Matriz de pontuação: ver {nome_pontuacao}",
        f"Matriz de traceback: ver {nome_traceback}",
    ]
    return "\n".join(linhas) + "\n"


def gerar_zip(resultado: dict) -> bytes:
    """Gera o .zip com os quatro arquivos de uma execução única."""
    arquivos = {
        nome_arquivo("txt", resultado): gerar_txt(resultado),
        nome_arquivo("csv_pontuacao", resultado): gerar_csv_pontuacao(resultado),
        nome_arquivo("csv_traceback", resultado): gerar_csv_traceback(resultado),
        nome_arquivo("csv_alinhamento", resultado): gerar_csv_alinhamento(resultado),
    }
    return _empacotar(arquivos)


def _empacotar(arquivos: dict[str, str]) -> bytes:
    """Empacota um mapa nome -> conteúdo textual num .zip em memória."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for nome, conteudo in arquivos.items():
            zf.writestr(nome, conteudo.encode("utf-8-sig"))
    return buffer.getvalue()


def gerar_txt_comparacao(resultado_global: dict, resultado_local: dict) -> str:
    """Gera o .txt único com os resumos de GLOBAL e LOCAL lado a lado."""
    linhas = [
        *_bloco_resumo(resultado_global),
        "",
        "-" * 40,
        "",
        *_bloco_resumo(resultado_local),
        "",
        _LEGENDA_ALINHAMENTO,
        _LEGENDA_DIRECOES,
        "",
        f"Matriz de pontuação (GLOBAL): ver {nome_arquivo('csv_pontuacao', resultado_global, 'global')}",
        f"Matriz de traceback (GLOBAL): ver {nome_arquivo('csv_traceback', resultado_global, 'global')}",
        f"Matriz de pontuação (LOCAL): ver {nome_arquivo('csv_pontuacao', resultado_local, 'local')}",
        f"Matriz de traceback (LOCAL): ver {nome_arquivo('csv_traceback', resultado_local, 'local')}",
    ]
    return "\n".join(linhas) + "\n"


def gerar_comparacao_zip(resultado_global: dict, resultado_local: dict) -> bytes:
    """Gera o .zip da comparação: os quatro arquivos de cada algoritmo + o .txt comparativo."""
    arquivos: dict[str, str] = {}
    for resultado, sufixo in ((resultado_global, "global"), (resultado_local, "local")):
        arquivos[nome_arquivo("txt", resultado, sufixo)] = gerar_txt(resultado)
        arquivos[nome_arquivo("csv_pontuacao", resultado, sufixo)] = gerar_csv_pontuacao(resultado)
        arquivos[nome_arquivo("csv_traceback", resultado, sufixo)] = gerar_csv_traceback(resultado)
        arquivos[nome_arquivo("csv_alinhamento", resultado, sufixo)] = gerar_csv_alinhamento(resultado)

    nome_comparativo = nome_arquivo("txt", resultado_global, "comparacao")
    arquivos[nome_comparativo] = gerar_txt_comparacao(resultado_global, resultado_local)
    return _empacotar(arquivos)
