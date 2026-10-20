/** Lógica compartilhada entre os componentes de resultado: nenhuma regra de negócio nova, só leitura do `Resultado` já calculado pela API. */
import type { Resultado } from '@/lib/tipos'

export interface Janela {
  linhaInicio: number
  /** Exclusivo. */
  linhaFim: number
  colunaInicio: number
  /** Exclusivo. */
  colunaFim: number
  truncado: boolean
}

/**
 * Janela de exibição da matriz — docs/contrato-api.md seção 8: acima do limite de exibição,
 * mostra só a região mínima que contém o caminho do traceback, com folga de 2 células.
 * A matriz devolvida pela API nunca é cortada; o corte é só de apresentação.
 */
export function calcularJanela(resultado: Resultado, limiteExibicao: number): Janela {
  const totalLinhas = resultado.matriz.length
  const totalColunas = resultado.matriz[0]?.length ?? 0
  const truncado = totalLinhas > limiteExibicao || totalColunas > limiteExibicao

  if (!truncado) {
    return { linhaInicio: 0, linhaFim: totalLinhas, colunaInicio: 0, colunaFim: totalColunas, truncado: false }
  }

  const folga = 2
  let minI = totalLinhas - 1
  let maxI = 0
  let minJ = totalColunas - 1
  let maxJ = 0
  for (const [i, j] of resultado.caminho) {
    if (i < minI) minI = i
    if (i > maxI) maxI = i
    if (j < minJ) minJ = j
    if (j > maxJ) maxJ = j
  }

  return {
    linhaInicio: Math.max(0, minI - folga),
    linhaFim: Math.min(totalLinhas, maxI + folga + 1),
    colunaInicio: Math.max(0, minJ - folga),
    colunaFim: Math.min(totalColunas, maxJ + folga + 1),
    truncado: true,
  }
}

/** Conjunto de chaves "i,j" para consulta O(1) de quais células pertencem ao caminho do traceback. */
export function caminhoParaChaves(caminho: Resultado['caminho']): Set<string> {
  return new Set(caminho.map(([i, j]) => `${i},${j}`))
}

export interface EstatisticasAlinhamento {
  matches: number
  mismatches: number
  gaps: number
  /** Percentual de identidade (0–100) entre as posições sem gap. */
  identidade: number
}

/** Deriva matches/mismatches/gaps da linha de marcação (`|` match, `.` mismatch, espaço gap). */
export function calcularEstatisticas(resultado: Resultado): EstatisticasAlinhamento {
  const { marcacao } = resultado.alinhamento
  let matches = 0
  let mismatches = 0
  let gaps = 0

  for (const caractere of marcacao) {
    if (caractere === '|') matches++
    else if (caractere === '.') mismatches++
    else gaps++
  }

  const identidade = marcacao.length > 0 ? (matches / marcacao.length) * 100 : 0
  return { matches, mismatches, gaps, identidade }
}

export function nomeAlgoritmo(modo: Resultado['modo']): string {
  return modo === 'GLOBAL' ? 'Global — Needleman-Wunsch' : 'Local — Smith-Waterman'
}
