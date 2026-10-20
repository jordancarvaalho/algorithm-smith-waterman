"""Leitura e extração de sequências a partir de arquivos .txt/.fasta."""

from .validacao import BASES_VALIDAS, NOMES_CAMPO, normalizar_sequencia

EXTENSOES_VALIDAS = (".txt", ".fasta")


def _erro(codigo: str, campo: str, mensagem: str) -> dict:
    return {"campo": campo, "codigo": codigo, "mensagem": mensagem}


def _extensao_valida(nome: str) -> bool:
    nome_lower = (nome or "").lower()
    return nome_lower.endswith(EXTENSOES_VALIDAS)


def _extrair_sequencias_textuais(texto: str) -> list[str]:
    """Separa o conteúdo em sequências: cabeçalhos FASTA (`>`) ou uma por linha não vazia."""
    linhas = texto.splitlines()
    tem_cabecalho = any(linha.strip().startswith(">") for linha in linhas)

    if tem_cabecalho:
        sequencias: list[list[str]] = []
        atual: list[str] | None = None
        for linha in linhas:
            linha_limpa = linha.strip()
            if not linha_limpa:
                continue
            if linha_limpa.startswith(">"):
                atual = []
                sequencias.append(atual)
            elif atual is not None:
                atual.append(linha_limpa)
        return ["".join(partes) for partes in sequencias]

    return [linha.strip() for linha in linhas if linha.strip()]


def _bases_invalidas(campo: str, seq_normalizada: str) -> list[dict]:
    """Verifica bases inválidas numa sequência já normalizada (mesma regra do contrato)."""
    nome = NOMES_CAMPO.get(campo, campo)
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


def ler_sequencias(nome: str, conteudo: bytes) -> tuple[list[str], list[dict]]:
    """Extrai as duas sequências de um arquivo `.txt`/`.fasta`.

    Valida extensão, legibilidade, quantidade (exatamente duas) e bases.
    Devolve (sequencias_normalizadas, erros).
    """
    if not _extensao_valida(nome):
        return [], [_erro("arquivo_formato", "arquivo", "Formato incompatível: use .txt ou .fasta.")]

    try:
        texto = conteudo.decode("utf-8")
    except UnicodeDecodeError:
        return [], [_erro("arquivo_ilegivel", "arquivo", "Não foi possível ler o arquivo.")]

    sequencias_textuais = _extrair_sequencias_textuais(texto)
    sequencias_normalizadas = [normalizar_sequencia(seq) for seq in sequencias_textuais]

    if len(sequencias_normalizadas) != 2:
        mensagem = (
            f"O arquivo deve conter exatamente duas sequências "
            f"(encontradas: {len(sequencias_normalizadas)})."
        )
        return sequencias_normalizadas, [_erro("seq_quantidade", "arquivo", mensagem)]

    erros: list[dict] = []
    erros.extend(_bases_invalidas("seq1", sequencias_normalizadas[0]))
    erros.extend(_bases_invalidas("seq2", sequencias_normalizadas[1]))

    return sequencias_normalizadas, erros
