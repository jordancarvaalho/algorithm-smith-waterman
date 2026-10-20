import { Badge } from '@/components/ui/badge'
import type { Resultado } from '@/lib/tipos'

export interface AlinhamentoFinalProps {
  resultado: Resultado
}

/** As três linhas monoespaçadas do alinhamento (linha1/marcação/linha2), com rolagem horizontal sincronizada e a legenda de match/mismatch/gap. */
export function AlinhamentoFinal({ resultado }: AlinhamentoFinalProps) {
  const { linha1, marcacao, linha2 } = resultado.alinhamento

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <span className="text-sm text-muted-foreground">Score final</span>
        <Badge>{resultado.score}</Badge>
        <span className="text-sm text-muted-foreground">Tamanho do alinhamento</span>
        <Badge variant="secondary">{resultado.tamanho}</Badge>
      </div>

      <div className="overflow-x-auto rounded-md border bg-card p-4">
        <pre className="w-fit font-mono text-sm leading-6 whitespace-pre">
          <span className="text-muted-foreground">Seq1: </span>
          {linha1}
          {'\n'}
          <span className="text-muted-foreground">      </span>
          {marcacao}
          {'\n'}
          <span className="text-muted-foreground">Seq2: </span>
          {linha2}
        </pre>
      </div>

      <p className="text-sm text-muted-foreground">
        Legenda: <span className="font-mono font-semibold text-foreground">|</span> match,{' '}
        <span className="font-mono font-semibold text-foreground">.</span> mismatch, espaço indica gap.
      </p>
    </div>
  )
}
