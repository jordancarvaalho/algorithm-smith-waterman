/** Tipos espelhando docs/contrato-api.md seção 1. Nomes de campo idênticos ao JSON da API. */

export type Modo = 'LOCAL' | 'GLOBAL'

export interface Parametros {
  match: number
  mismatch: number
  gap: number
}

export interface Alinhamento {
  linha1: string
  marcacao: string
  linha2: string
}

export interface Resultado {
  modo: Modo
  seq1: string
  seq2: string
  parametros: Parametros
  matriz: number[][]
  direcoes: string[][]
  caminho: [number, number][]
  inicio: [number, number]
  alinhamento: Alinhamento
  score: number
  tamanho: number
  avisos: Aviso[]
}

export interface Comparacao {
  global: Resultado
  local: Resultado
}

export interface Erro {
  campo: string
  codigo: string
  mensagem: string
}

export interface Aviso {
  codigo: string
  campo: string
  mensagem: string
}

/** Corpo aceito por POST /api/alinhar (match/mismatch/gap podem chegar como número ou string). */
export interface CorpoAlinhar {
  seq1: string
  seq2: string
  modo: Modo
  match: number | string
  mismatch: number | string
  gap: number | string
}

/** Corpo aceito por POST /api/comparar — igual a CorpoAlinhar, sem modo. */
export type CorpoComparar = Omit<CorpoAlinhar, 'modo'>

export interface RespostaArquivo {
  seq1: string
  seq2: string
}

export interface RespostaErros {
  erros: Erro[]
}

export type Formato =
  | 'txt'
  | 'csv_pontuacao'
  | 'csv_traceback'
  | 'csv_alinhamento'
  | 'zip'
  | 'comparacao_zip'
