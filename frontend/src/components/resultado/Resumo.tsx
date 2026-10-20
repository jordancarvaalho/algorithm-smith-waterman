import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import type { Resultado } from '@/lib/tipos'
import { nomeAlgoritmo } from './utils'

export interface ResumoProps {
  resultado: Resultado
}

/** Tabela síntese: algoritmo, sequências, parâmetros, score, tamanho do alinhamento e início/fim do traceback. */
export function Resumo({ resultado }: ResumoProps) {
  const linhas: { item: string; valor: string }[] = [
    { item: 'Algoritmo', valor: nomeAlgoritmo(resultado.modo) },
    { item: 'Seq1', valor: `${resultado.seq1} (${resultado.seq1.length} bases)` },
    { item: 'Seq2', valor: `${resultado.seq2} (${resultado.seq2.length} bases)` },
    { item: 'Match', valor: String(resultado.parametros.match) },
    { item: 'Mismatch', valor: String(resultado.parametros.mismatch) },
    { item: 'Gap', valor: String(resultado.parametros.gap) },
    { item: 'Score final', valor: String(resultado.score) },
    { item: 'Tamanho do alinhamento', valor: String(resultado.tamanho) },
    { item: 'Início do traceback [i, j]', valor: `[${resultado.inicio[0]}, ${resultado.inicio[1]}]` },
    { item: 'Fim do traceback [i, j]', valor: `[${resultado.caminho.at(-1)?.[0]}, ${resultado.caminho.at(-1)?.[1]}]` },
  ]

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Item</TableHead>
          <TableHead>Valor</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {linhas.map((linha) => (
          <TableRow key={linha.item}>
            <TableCell className="font-medium">{linha.item}</TableCell>
            <TableCell className="font-mono">{linha.valor}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
