"""API da aplicação de alinhamento de duas sequências de DNA.

Serve os endpoints de alinhamento/comparação/exportação definidos em
docs/contrato-api.md e os arquivos estáticos do diretório web/.

A validação de domínio é toda feita por core.validacao.validar — este
módulo apenas lê o corpo da requisição de forma permissiva (sem deixar o
Pydantic recusar a requisição) e traduz o resultado da validação para as
respostas HTTP do contrato.
"""
from pathlib import Path

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from core.alinhamento import alinhar
from core.arquivos import ler_sequencias
from core.validacao import normalizar_sequencia, validar
from export.arquivos import (
    gerar_comparacao_zip,
    gerar_csv_alinhamento,
    gerar_csv_pontuacao,
    gerar_csv_traceback,
    gerar_txt,
    gerar_zip,
    nome_arquivo,
)

app = FastAPI(title="Alinhamento de Duas Sequências de DNA")

FORMATOS_TEXTO = {
    "txt": ("text/plain; charset=utf-8", gerar_txt),
    "csv_pontuacao": ("text/csv; charset=utf-8", gerar_csv_pontuacao),
    "csv_traceback": ("text/csv; charset=utf-8", gerar_csv_traceback),
    "csv_alinhamento": ("text/csv; charset=utf-8", gerar_csv_alinhamento),
}
FORMATOS_VALIDOS = set(FORMATOS_TEXTO) | {"zip", "comparacao_zip"}


async def _ler_corpo_json(request: Request) -> dict:
    """Lê o corpo como JSON de forma tolerante — nunca levanta erro de schema."""
    try:
        corpo = await request.json()
    except Exception:
        return {}
    return corpo if isinstance(corpo, dict) else {}


def _extrair_campos(corpo: dict):
    seq1 = corpo.get("seq1")
    seq2 = corpo.get("seq2")
    modo = corpo.get("modo")
    match = corpo.get("match")
    mismatch = corpo.get("mismatch")
    gap = corpo.get("gap")

    seq1 = "" if seq1 is None else str(seq1)
    seq2 = "" if seq2 is None else str(seq2)
    if modo is None:
        modo = ""
    elif not isinstance(modo, str):
        modo = str(modo)

    return seq1, seq2, modo, match, mismatch, gap


def _erro_modo_ausente() -> dict:
    return {
        "campo": "modo",
        "codigo": "modo_invalido",
        "mensagem": "Modo inválido: use LOCAL ou GLOBAL.",
    }


def _validar_alinhar(corpo: dict):
    """Validação para /api/alinhar e para /api/exportar/{formato} (exceto comparacao_zip).

    core.validacao.validar() aceita modo vazio/None sem erro (é o caso de uso do
    /api/comparar) e já devolve modo_invalido para qualquer valor não vazio que
    não seja LOCAL/GLOBAL. Como /api/alinhar exige modo, é esta função que
    acrescenta o erro quando modo vier vazio, None ou ausente.
    """
    seq1, seq2, modo, match, mismatch, gap = _extrair_campos(corpo)
    seq1_norm = normalizar_sequencia(seq1)
    seq2_norm = normalizar_sequencia(seq2)

    erros, avisos, parametros = validar(seq1_norm, seq2_norm, modo, match, mismatch, gap)
    if not modo:
        erros = [_erro_modo_ausente(), *erros]

    modo_normalizado = modo.strip().upper() if modo else modo
    return erros, avisos, parametros, seq1_norm, seq2_norm, modo_normalizado


def _validar_comparar(corpo: dict):
    """Validação para /api/comparar e /api/exportar/comparacao_zip — sem modo."""
    seq1, seq2, _modo, match, mismatch, gap = _extrair_campos(corpo)
    seq1_norm = normalizar_sequencia(seq1)
    seq2_norm = normalizar_sequencia(seq2)

    erros, avisos, parametros = validar(seq1_norm, seq2_norm, "", match, mismatch, gap)
    return erros, avisos, parametros, seq1_norm, seq2_norm


def _anexo(conteudo: bytes, media_type: str, nome: str) -> Response:
    return Response(
        content=conteudo,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )


@app.post("/api/alinhar")
async def rota_alinhar(request: Request):
    corpo = await _ler_corpo_json(request)
    erros, avisos, parametros, seq1, seq2, modo = _validar_alinhar(corpo)
    if erros:
        return JSONResponse({"erros": erros}, status_code=422)

    resultado = alinhar(seq1, seq2, modo, parametros["match"], parametros["mismatch"], parametros["gap"])
    resultado["avisos"] = avisos
    return resultado


@app.post("/api/comparar")
async def rota_comparar(request: Request):
    corpo = await _ler_corpo_json(request)
    erros, avisos, parametros, seq1, seq2 = _validar_comparar(corpo)
    if erros:
        return JSONResponse({"erros": erros}, status_code=422)

    resultado_global = alinhar(seq1, seq2, "GLOBAL", parametros["match"], parametros["mismatch"], parametros["gap"])
    resultado_global["avisos"] = avisos

    resultado_local = alinhar(seq1, seq2, "LOCAL", parametros["match"], parametros["mismatch"], parametros["gap"])
    resultado_local["avisos"] = avisos

    return {"global": resultado_global, "local": resultado_local}


@app.post("/api/arquivo")
async def rota_arquivo(arquivo: UploadFile = File(...)):
    conteudo = await arquivo.read()
    sequencias, erros = ler_sequencias(arquivo.filename or "", conteudo)
    if erros:
        return JSONResponse({"erros": erros}, status_code=422)

    return {"seq1": sequencias[0], "seq2": sequencias[1]}


@app.post("/api/exportar/{formato}")
async def rota_exportar(formato: str, request: Request):
    if formato not in FORMATOS_VALIDOS:
        return JSONResponse(
            {"erros": [{
                "campo": "formato",
                "codigo": "formato_invalido",
                "mensagem": "Formato de exportação não encontrado.",
            }]},
            status_code=404,
        )

    corpo = await _ler_corpo_json(request)

    if formato == "comparacao_zip":
        erros, avisos, parametros, seq1, seq2 = _validar_comparar(corpo)
        if erros:
            return JSONResponse({"erros": erros}, status_code=422)

        resultado_global = alinhar(seq1, seq2, "GLOBAL", parametros["match"], parametros["mismatch"], parametros["gap"])
        resultado_global["avisos"] = avisos
        resultado_local = alinhar(seq1, seq2, "LOCAL", parametros["match"], parametros["mismatch"], parametros["gap"])
        resultado_local["avisos"] = avisos

        conteudo = gerar_comparacao_zip(resultado_global, resultado_local)
        nome = nome_arquivo("comparacao_zip", resultado_global)
        return _anexo(conteudo, "application/zip", nome)

    erros, avisos, parametros, seq1, seq2, modo = _validar_alinhar(corpo)
    if erros:
        return JSONResponse({"erros": erros}, status_code=422)

    resultado = alinhar(seq1, seq2, modo, parametros["match"], parametros["mismatch"], parametros["gap"])
    resultado["avisos"] = avisos

    if formato == "zip":
        conteudo = gerar_zip(resultado)
        nome = nome_arquivo("zip", resultado)
        return _anexo(conteudo, "application/zip", nome)

    media_type, gerador = FORMATOS_TEXTO[formato]
    texto = gerador(resultado)
    nome = nome_arquivo(formato, resultado)
    return _anexo(texto.encode("utf-8-sig"), media_type, nome)


# --- Estáticos (web/) -------------------------------------------------------
# web/ é construído em paralelo por outro worker: a aplicação precisa subir
# normalmente mesmo que o diretório ainda não exista, por isso o mount só
# acontece se ele já estiver presente. As rotas /api/* acima são registradas
# antes para terem prioridade sobre o mount em "/".
_DIRETORIO_WEB = Path(__file__).resolve().parent.parent / "web"

if _DIRETORIO_WEB.is_dir():
    app.mount("/", StaticFiles(directory=_DIRETORIO_WEB, html=True), name="estaticos")
else:
    @app.get("/")
    async def rota_raiz_sem_web():
        return JSONResponse(
            {"mensagem": "Diretório web/ ainda não encontrado. A interface estará disponível assim que for criada."},
        )
