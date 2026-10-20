import { useMemo } from 'react'
import { cn } from 'cn'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { decodificarDirecoes, SETA_SEM_DIRECAO } from '@/lib/direcoes'
import type { Resultado } from '@/lib/tipos'
import { calcularJanela, caminhoParaChaves } from './utils'
import { LegendaDirecoes } from './LegendaDirecoes'

export interface MatrizTracebackProps {
  resultado: Resultado
  /** Limite de exibição (lib/config.ts); acima disso, exibir apenas a janela do traceback. */
  limiteExibicao: number
  /** false esconde a legenda embutida — usado na comparação lado a lado, que mostra uma legenda única para as duas colunas. Padrão: true. */
  comLegenda?: boolean
}

/** Matriz de direções: cada célula mostra as setas das direções empatadas, com a seguida destacada e as demais esmaecidas. */
export function MatrizTraceback({ resultado, limiteExibicao, comLegenda = true }: MatrizTracebackProps) {
  const janela = useMemo(() => calcularJanela(resultado, limiteExibicao), [resultado, limiteExibicao])
  const caminho = useMemo(() => caminhoParaChaves(resultado.caminho), [resultado.caminho])

  const linhas = useMemo(
    () => Array.from({ length: janela.linhaFim - janela.linhaInicio }, (_, k) => janela.linhaInicio + k),
    [janela],
  )
  const colunas = useMemo(
    () => Array.from({ length: janela.colunaFim - janela.colunaInicio }, (_, k) => janela.colunaInicio + k),
    [janela],
  )

  const totalLinhas = resultado.matriz.length
  const totalColunas = resultado.matriz[0]?.length ?? 0

  return (
    <div className="flex flex-col gap-3">
      {janela.truncado && (
        <Alert>
          <AlertTitle>Matriz acima do limite de exibição ({limiteExibicao})</AlertTitle>
          <AlertDescription>
            A matriz completa tem {totalLinhas} × {totalColunas} células. A tela mostra apenas a janela ao redor do
            caminho do traceback, com folga de 2 células em cada direção. O CSV exportado traz a matriz inteira.
          </AlertDescription>
        </Alert>
      )}

      <div className="max-h-[32rem] overflow-auto rounded-md border">
        <table className="w-full border-separate border-spacing-0 text-xs">
          <thead>
            <tr>
              <th className="sticky top-0 left-0 z-20 border-b border-r bg-muted px-2 py-1 font-mono font-medium">
                -
              </th>
              {colunas.map((j) => (
                <th
                  key={j}
                  className="sticky top-0 z-10 min-w-8 border-b bg-muted px-2 py-1 text-center font-mono font-medium"
                >
                  {j === 0 ? '-' : resultado.seq2[j - 1]}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {linhas.map((i) => (
              <tr key={i}>
                <th className="sticky left-0 z-10 border-r bg-muted px-2 py-1 text-center font-mono font-medium">
                  {i === 0 ? '-' : resultado.seq1[i - 1]}
                </th>
                {colunas.map((j) => {
                  const direcoes = decodificarDirecoes(resultado.direcoes[i][j])
                  const noCaminho = caminho.has(`${i},${j}`)
                  return (
                    <td
                      key={j}
                      className={cn(
                        'px-2 py-1 text-center font-mono',
                        noCaminho && 'bg-red-50 dark:bg-red-950/30',
                      )}
                    >
                      {direcoes.length === 0 ? (
                        <span className="text-muted-foreground">{SETA_SEM_DIRECAO}</span>
                      ) : (
                        direcoes.map((d, indice) => (
                          <span
                            key={d.letra + indice}
                            className={cn(d.seguida ? 'font-bold text-red-600' : 'text-muted-foreground/60')}
                          >
                            {d.seta}
                          </span>
                        ))
                      )}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {comLegenda && <LegendaDirecoes />}
    </div>
  )
}
