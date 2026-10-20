import { useEffect, useRef } from 'react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import type { Erro } from '@/lib/tipos'

export interface ListaErrosProps {
  erros: Erro[]
}

/** Renderiza o resumo de erros de validação (422) no topo do formulário, um item por erro, com rolagem até o resumo. */
export function ListaErros({ erros }: ListaErrosProps) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (erros.length > 0) {
      ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [erros])

  if (erros.length === 0) return null

  return (
    <div ref={ref}>
      <Alert variant="destructive">
        <AlertTitle>
          {erros.length === 1
            ? '1 erro encontrado na validação'
            : `${erros.length} erros encontrados na validação`}
        </AlertTitle>
        <AlertDescription>
          <ul className="list-disc space-y-0.5 pl-4">
            {erros.map((erro, indice) => (
              <li key={`${erro.campo}-${erro.codigo}-${indice}`}>{erro.mensagem}</li>
            ))}
          </ul>
        </AlertDescription>
      </Alert>
    </div>
  )
}
