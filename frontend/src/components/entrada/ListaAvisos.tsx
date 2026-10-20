import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import type { Aviso } from '@/lib/tipos'

export interface ListaAvisosProps {
  avisos: Aviso[]
}

/** Renderiza os avisos não bloqueantes de consistência de parâmetros (match_nao_positivo, mismatch_nao_negativo, gap_nao_negativo). */
export function ListaAvisos({ avisos }: ListaAvisosProps) {
  if (avisos.length === 0) return null

  return (
    <Alert className="border-amber-500/50 bg-amber-500/10 text-amber-900 dark:text-amber-200">
      <AlertTitle>Avisos de consistência</AlertTitle>
      <AlertDescription className="text-amber-900/80 dark:text-amber-200/80">
        <ul className="list-disc space-y-0.5 pl-4">
          {avisos.map((aviso, indice) => (
            <li key={`${aviso.campo}-${aviso.codigo}-${indice}`}>{aviso.mensagem}</li>
          ))}
        </ul>
      </AlertDescription>
    </Alert>
  )
}
