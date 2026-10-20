import { useMemo } from 'react'
import { cn } from 'cn'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import type { Resultado } from '@/lib/tipos'
import { calcularJanela, caminhoParaChaves } from './utils'

export interface MatrizPontuacaoProps {
  resultado: Resultado
  /** Limite de exibição (lib/config.ts); acima disso, exibir apenas a janela do traceback com folga de 2 células. */
  limiteExibicao: number
}

/** Matriz (m+1)×(n+1) de scores, com cabeçalhos das bases de Seq1/Seq2 e o caminho do traceback destacado em vermelho. */
export function MatrizPontuacao({ resultado, limiteExibicao }: MatrizPontuacaoProps) {
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
                  const noCaminho = caminho.has(`${i},${j}`)
                  return (
                    <td
                      key={j}
                      className={cn(
                        'px-2 py-1 text-center font-mono tabular-nums',
                        noCaminho && 'bg-red-600 font-semibold text-white',
                      )}
                    >
                      {resultado.matriz[i][j]}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
