import { Badge } from '@/components/ui/badge'
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import type { Resultado } from '@/lib/tipos'
import { calcularEstatisticas, nomeAlgoritmo } from './utils'

export interface ResultadoGeralProps {
  resultado: Resultado
}

/** Cartões de destaque do resultado: algoritmo, score, tamanho do alinhamento e das sequências, e contagens derivadas da marcação. */
export function ResultadoGeral({ resultado }: ResultadoGeralProps) {
  const stats = calcularEstatisticas(resultado)

  const cartoes: { rotulo: string; valor: string | number }[] = [
    { rotulo: 'Algoritmo', valor: nomeAlgoritmo(resultado.modo) },
    { rotulo: 'Score final', valor: resultado.score },
    { rotulo: 'Tamanho do alinhamento', valor: resultado.tamanho },
    { rotulo: 'Tamanho de Seq1', valor: resultado.seq1.length },
    { rotulo: 'Tamanho de Seq2', valor: resultado.seq2.length },
    { rotulo: 'Matches', valor: stats.matches },
    { rotulo: 'Mismatches', valor: stats.mismatches },
    { rotulo: 'Gaps', valor: stats.gaps },
  ]

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {cartoes.map((cartao) => (
          <Card key={cartao.rotulo} size="sm">
            <CardHeader>
              <CardDescription>{cartao.rotulo}</CardDescription>
              <CardTitle className="text-xl break-words">{cartao.valor}</CardTitle>
            </CardHeader>
          </Card>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm">
        <span className="flex items-center gap-2 text-muted-foreground">
          Identidade <Badge variant="secondary">{stats.identidade.toFixed(1)}%</Badge>
        </span>
        <span className="text-muted-foreground">
          Seq1: <span className="font-mono text-foreground">{resultado.seq1}</span>
        </span>
        <span className="text-muted-foreground">
          Seq2: <span className="font-mono text-foreground">{resultado.seq2}</span>
        </span>
      </div>
    </div>
  )
}
