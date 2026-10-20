/**
 * Cliente da API — docs/contrato-api.md seção 5.
 *
 * Regras invioláveis:
 * - 422 devolve a lista de erros do contrato (ApiErro) para a UI exibir.
 * - Falha de rede/conexão resulta em ApiErroRede explícito — NUNCA um fallback para dados de exemplo.
 * - Exportação dispara download usando o filename do cabeçalho Content-Disposition.
 */
import type {
  Comparacao,
  CorpoAlinhar,
  CorpoComparar,
  Erro,
  Formato,
  Resultado,
  RespostaArquivo,
} from './tipos'

/** Erro de validação devolvido pela API (HTTP 422), com a lista completa de erros do contrato. */
export class ApiErroValidacao extends Error {
  erros: Erro[]

  constructor(erros: Erro[]) {
    super('Erro de validação da API.')
    this.name = 'ApiErroValidacao'
    this.erros = erros
  }
}

/** Falha de comunicação com o servidor (rede indisponível, servidor fora do ar, resposta inesperada). */
export class ApiErroRede extends Error {
  constructor(mensagem = 'Não foi possível falar com o servidor. Verifique se a aplicação está rodando.') {
    super(mensagem)
    this.name = 'ApiErroRede'
  }
}

async function tratarResposta<T>(resp: Response): Promise<T> {
  if (resp.status === 200) {
    return (await resp.json()) as T
  }
  if (resp.status === 422) {
    const dados = (await resp.json()) as { erros: Erro[] }
    throw new ApiErroValidacao(dados.erros)
  }
  throw new ApiErroRede(`Erro do servidor: status ${resp.status}.`)
}

async function requisitar<T>(caminho: string, corpo: unknown): Promise<T> {
  let resp: Response
  try {
    resp = await fetch(caminho, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(corpo),
    })
  } catch {
    throw new ApiErroRede()
  }
  return tratarResposta<T>(resp)
}

export function alinhar(corpo: CorpoAlinhar): Promise<Resultado> {
  return requisitar<Resultado>('/api/alinhar', corpo)
}

export function comparar(corpo: CorpoComparar): Promise<Comparacao> {
  return requisitar<Comparacao>('/api/comparar', corpo)
}

export async function enviarArquivo(file: File): Promise<RespostaArquivo> {
  const formData = new FormData()
  formData.append('arquivo', file)

  let resp: Response
  try {
    resp = await fetch('/api/arquivo', { method: 'POST', body: formData })
  } catch {
    throw new ApiErroRede()
  }
  return tratarResposta<RespostaArquivo>(resp)
}

function extrairNomeArquivo(resp: Response, formato: Formato): string {
  const disposicao = resp.headers.get('Content-Disposition')
  if (disposicao) {
    const casado = disposicao.match(/filename="?([^";]+)"?/)
    if (casado?.[1]) return casado[1]
  }
  return `exportacao_${formato}`
}

/** Dispara o download do arquivo exportado usando o filename do cabeçalho Content-Disposition. */
export async function exportar(formato: Formato, corpo: CorpoAlinhar | CorpoComparar): Promise<void> {
  let resp: Response
  try {
    resp = await fetch(`/api/exportar/${formato}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(corpo),
    })
  } catch {
    throw new ApiErroRede()
  }

  if (resp.status === 422) {
    const dados = (await resp.json()) as { erros: Erro[] }
    throw new ApiErroValidacao(dados.erros)
  }
  if (resp.status !== 200) {
    throw new ApiErroRede(`Erro na exportação: status ${resp.status}.`)
  }

  const blob = await resp.blob()
  const filename = extrairNomeArquivo(resp, formato)

  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
