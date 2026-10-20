import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import type { Modo } from '@/lib/tipos'

export interface SeletorAlgoritmoProps {
  modo: Modo
  onModoChange: (modo: Modo) => void
  /** Erro de campo 'modo', se houver. */
  erro?: string
}

/** Renderiza o radio-group GLOBAL (Needleman-Wunsch) / LOCAL (Smith-Waterman). */
export function SeletorAlgoritmo({ modo, onModoChange, erro }: SeletorAlgoritmoProps) {
  return (
    <div className="grid gap-1.5">
      <Label>Algoritmo</Label>
      <RadioGroup
        value={modo}
        onValueChange={(valor) => onModoChange(valor as Modo)}
        aria-invalid={Boolean(erro)}
      >
        <label className="flex items-center gap-2 text-sm">
          <RadioGroupItem value="GLOBAL" />
          GLOBAL (Needleman-Wunsch)
        </label>
        <label className="flex items-center gap-2 text-sm">
          <RadioGroupItem value="LOCAL" />
          LOCAL (Smith-Waterman)
        </label>
      </RadioGroup>
      {erro && <p className="text-xs text-destructive">{erro}</p>}
    </div>
  )
}
