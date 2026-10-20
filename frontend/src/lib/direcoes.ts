/** Utilidades para a codificação de direções do traceback — docs/contrato-api.md seção 2. */

export type LetraDirecao = 'D' | 'V' | 'H'

export interface DirecaoDecodificada {
  /** Letra em maiúscula: 'D', 'V' ou 'H'. */
  letra: LetraDirecao
  /** Seta correspondente: ↖ diagonal, ↑ vertical, ← horizontal. */
  seta: string
  /** true quando esta foi a direção efetivamente seguida pelo desempate (letra maiúscula na célula). */
  seguida: boolean
}

const SETA_POR_LETRA: Record<LetraDirecao, string> = {
  D: '↖',
  V: '↑',
  H: '←',
}

/** Símbolo exibido quando a célula não tem nenhuma direção ('-'). */
export const SETA_SEM_DIRECAO = '·'

/**
 * Decodifica a string de uma célula da matriz de direções (ex.: 'Dvh', 'D', '-')
 * na lista de direções presentes, na ordem D, V, H, com indicação de qual foi seguida.
 */
export function decodificarDirecoes(codigo: string): DirecaoDecodificada[] {
  if (!codigo || codigo === '-') return []

  return codigo.split('').map((caractere) => {
    const letra = caractere.toUpperCase() as LetraDirecao
    return {
      letra,
      seta: SETA_POR_LETRA[letra],
      seguida: caractere === caractere.toUpperCase(),
    }
  })
}

/** Devolve a letra da direção seguida em uma célula, ou null se a célula for '-'. */
export function direcaoSeguida(codigo: string): LetraDirecao | null {
  const decodificadas = decodificarDirecoes(codigo)
  return decodificadas.find((d) => d.seguida)?.letra ?? null
}
