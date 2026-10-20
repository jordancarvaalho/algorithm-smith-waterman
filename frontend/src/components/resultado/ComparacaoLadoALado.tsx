import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import type { Comparacao, Resultado } from '@/lib/tipos'
import { LegendaDirecoes } from './LegendaDirecoes'
import { MatrizPontuacao } from './MatrizPontuacao'
import { MatrizTraceback } from './MatrizTraceback'
import { nomeAlgoritmo } from './utils'

export interface ComparacaoLadoALadoProps {
  comparacao: Comparacao
  /** Limite de exibição (lib/config.ts), repassado às mini-matrizes de cada coluna. */
  limiteExibicao: number
}

function Coluna({ resultado, limiteExibicao }: { resultado: Resultado; limiteExibicao: number }) {
  const { linha1, marcacao, linha2 } = resultado.alinhamento

  return (
    <Card className="flex-1">
      <CardHeader>
        <CardTitle className="flex items-center justify-between gap-2">
          {nomeAlgoritmo(resultado.modo)}
          <Badge>{resultado.score}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div className="overflow-x-auto rounded-md border bg-card p-3">
          <pre className="w-fit font-mono text-xs leading-5 whitespace-pre">
            {linha1}
            {'\n'}
            {marcacao}
            {'\n'}
            {linha2}
          </pre>
        </div>

        <p className="text-sm text-muted-foreground">Tamanho do alinhamento: {resultado.tamanho}</p>

        <Separator />

        <div className="flex flex-col gap-2">
          <h4 className="text-sm font-medium">Matriz de pontuação</h4>
          <MatrizPontuacao resultado={resultado} limiteExibicao={limiteExibicao} />
        </div>

        <div className="flex flex-col gap-2">
          <h4 className="text-sm font-medium">Matriz de traceback</h4>
          <MatrizTraceback resultado={resultado} limiteExibicao={limiteExibicao} comLegenda={false} />
        </div>
      </CardContent>
    </Card>
  )
}

/** Comparação GLOBAL × LOCAL: tabela resumo e as duas colunas lado a lado, cada uma com alinhamento, score, tamanho e matrizes. Empilha em tela estreita. */
export function ComparacaoLadoALado({ comparacao, limiteExibicao }: ComparacaoLadoALadoProps) {
  const { global, local } = comparacao

  return (
    <div className="flex flex-col gap-6">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Algoritmo</TableHead>
            <TableHead>Score</TableHead>
            <TableHead>Tamanho do alinhamento</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell className="font-medium">{nomeAlgoritmo(global.modo)}</TableCell>
            <TableCell>{global.score}</TableCell>
            <TableCell>{global.tamanho}</TableCell>
          </TableRow>
          <TableRow>
            <TableCell className="font-medium">{nomeAlgoritmo(local.modo)}</TableCell>
            <TableCell>{local.score}</TableCell>
            <TableCell>{local.tamanho}</TableCell>
          </TableRow>
        </TableBody>
      </Table>

      <div className="flex flex-col gap-6 lg:flex-row">
        <Coluna resultado={global} limiteExibicao={limiteExibicao} />
        <Coluna resultado={local} limiteExibicao={limiteExibicao} />
      </div>

      <LegendaDirecoes />
    </div>
  )
}
