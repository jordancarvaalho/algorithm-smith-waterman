import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'

/** Sem props: conteúdo fixo definido pelo contrato (docs/contrato-api.md seção 2). */
export type LegendaDirecoesProps = Record<string, never>

const DIRECOES = [
  { seta: '↖', letra: 'D', nome: 'Diagonal', significado: 'base de Seq1 alinhada com base de Seq2' },
  { seta: '↑', letra: 'V', nome: 'Vertical', significado: 'base de Seq1 alinhada com gap em Seq2' },
  { seta: '←', letra: 'H', nome: 'Horizontal', significado: 'gap em Seq1 alinhado com base de Seq2' },
]

/** Legenda fixa das direções, do destaque e das duas regras de desempate. */
export function LegendaDirecoes(_props: LegendaDirecoesProps) {
  return (
    <Card size="sm">
      <CardHeader>
        <CardTitle>Legenda das direções</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3 text-sm">
        <ul className="flex flex-col gap-1">
          {DIRECOES.map((d) => (
            <li key={d.letra} className="flex items-baseline gap-2">
              <span className="w-5 text-center font-mono font-bold text-red-600">{d.seta}</span>
              <span className="text-muted-foreground">
                {d.nome} ({d.letra}) — {d.significado}
              </span>
            </li>
          ))}
          <li className="flex items-baseline gap-2">
            <span className="w-5 text-center font-mono text-muted-foreground">·</span>
            <span className="text-muted-foreground">Sem direção (célula de início/parada, sem predecessor)</span>
          </li>
        </ul>

        <p className="text-muted-foreground">
          Quando mais de uma direção empata no valor máximo de uma célula, todas aparecem. A seta em{' '}
          <span className="font-bold text-red-600">vermelho</span> é a direção efetivamente seguida pelo traceback; as
          demais, empatadas mas não seguidas, aparecem esmaecidas.
        </p>

        <Separator />

        <p className="text-muted-foreground">
          <strong className="text-foreground">Desempate dentro da célula:</strong> diagonal → vertical → horizontal.
        </p>
        <p className="text-muted-foreground">
          <strong className="text-foreground">Início do traceback (LOCAL):</strong> a primeira célula de maior valor
          encontrada na varredura da matriz de cima para baixo e da esquerda para a direita.
        </p>
      </CardContent>
    </Card>
  )
}
