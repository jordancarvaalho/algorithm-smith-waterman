"""Normalização e validação de sequências e parâmetros de alinhamento."""

import re

BASES_VALIDAS = "ACGT"
MODOS_VALIDOS = {"GLOBAL", "LOCAL"}
NOMES_CAMPO = {"seq1": "Seq1", "seq2": "Seq2"}
_PADRAO_INTEIRO = re.compile(r"^[+-]?\d+$")


def normalizar_sequencia(texto: str) -> str:
    """Remove espaços/quebras de linha e converte para maiúsculas. Não valida."""
    if texto is None:
        return ""
    return re.sub(r"\s+", "", texto).upper()


def _erro(codigo: str, campo: str, mensagem: str) -> dict:
    return {"campo": campo, "codigo": codigo, "mensagem": mensagem}


def _aviso(codigo: str, campo: str, mensagem: str) -> dict:
    return {"codigo": codigo, "campo": campo, "mensagem": mensagem}


def _validar_sequencia(campo: str, seq_normalizada: str) -> list[dict]:
    """Valida uma sequência já normalizada: vazia ou com base inválida."""
    nome = NOMES_CAMPO[campo]
    if seq_normalizada == "":
        return [_erro("seq_vazia", campo, f"{nome} — a sequência não pode estar vazia.")]

    invalidas = [(pos, base) for pos, base in enumerate(seq_normalizada, start=1) if base not in BASES_VALIDAS]
    if not invalidas:
        return []
    primeira_pos, primeira_base = invalidas[0]
    total = len(invalidas)
    mensagem = (
        f'{nome} — base inválida: "{primeira_base}" na posição {primeira_pos} '
        f"(total de ocorrências inválidas: {total})."
    )
    return [_erro("base_invalida", campo, mensagem)]


def _converter_parametro(campo: str, nome: str, valor) -> tuple[dict | None, int | None]:
    """Converte match/mismatch/gap para int. Devolve (erro_ou_none, valor_ou_none)."""
    if valor is None:
        return _erro("parametro_ausente", campo, f"{nome} — parâmetro obrigatório."), None

    if isinstance(valor, bool):
        return _erro("parametro_nao_numerico", campo, f"{nome} — deve ser um número inteiro."), None

    if isinstance(valor, int):
        return None, valor

    if isinstance(valor, float):
        if valor.is_integer():
            return None, int(valor)
        return _erro("parametro_nao_numerico", campo, f"{nome} — deve ser um número inteiro."), None

    if isinstance(valor, str):
        texto = valor.strip()
        if texto == "":
            return _erro("parametro_ausente", campo, f"{nome} — parâmetro obrigatório."), None
        if _PADRAO_INTEIRO.match(texto):
            return None, int(texto)
        try:
            numero = float(texto)
        except ValueError:
            return _erro("parametro_nao_numerico", campo, f"{nome} — deve ser um número inteiro."), None
        if numero.is_integer():
            return None, int(numero)
        return _erro("parametro_nao_numerico", campo, f"{nome} — deve ser um número inteiro."), None

    return _erro("parametro_nao_numerico", campo, f"{nome} — deve ser um número inteiro."), None


def validar(seq1: str, seq2: str, modo: str, match, mismatch, gap) -> tuple[list[dict], list[dict], dict]:
    """Valida sequências, modo e parâmetros. Devolve (erros, avisos, parametros_convertidos).

    Acumula todos os erros encontrados. `parametros` só é confiável quando `erros == []`.
    `modo` igual a "" ou None é aceito sem erro.
    """
    erros: list[dict] = []
    avisos: list[dict] = []

    seq1_norm = normalizar_sequencia(seq1)
    seq2_norm = normalizar_sequencia(seq2)
    erros.extend(_validar_sequencia("seq1", seq1_norm))
    erros.extend(_validar_sequencia("seq2", seq2_norm))

    if modo not in (None, "", *MODOS_VALIDOS):
        erros.append(_erro("modo_invalido", "modo", "Modo inválido: use LOCAL ou GLOBAL."))

    erro_match, match_convertido = _converter_parametro("match", "Match", match)
    erro_mismatch, mismatch_convertido = _converter_parametro("mismatch", "Mismatch", mismatch)
    erro_gap, gap_convertido = _converter_parametro("gap", "Gap", gap)

    for erro in (erro_match, erro_mismatch, erro_gap):
        if erro is not None:
            erros.append(erro)

    if erro_match is None and match_convertido <= 0:
        avisos.append(_aviso("match_nao_positivo", "match", "Recomenda-se Match > 0."))
    if erro_mismatch is None and mismatch_convertido >= 0:
        avisos.append(_aviso("mismatch_nao_negativo", "mismatch", "Recomenda-se Mismatch < 0."))
    if erro_gap is None and gap_convertido >= 0:
        avisos.append(_aviso("gap_nao_negativo", "gap", "Recomenda-se Gap < 0."))

    parametros = {
        "match": match_convertido,
        "mismatch": mismatch_convertido,
        "gap": gap_convertido,
    }

    return erros, avisos, parametros
