import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export interface ParametrosPontuacaoProps {
  /** Valores em texto, como digitados pelo usuário (a API aceita número ou string e detecta não-numérico). */
  match: string
  mismatch: string
  gap: string
  onMatchChange: (valor: string) => void
  onMismatchChange: (valor: string) => void
  onGapChange: (valor: string) => void
  erroMatch?: string
  erroMismatch?: string
  erroGap?: string
}

/** Renderiza os três campos Match/Mismatch/Gap com dica de valores recomendados e erro por campo. */
export function ParametrosPontuacao({
  match,
  mismatch,
  gap,
  onMatchChange,
  onMismatchChange,
  onGapChange,
  erroMatch,
  erroMismatch,
  erroGap,
}: ParametrosPontuacaoProps) {
  return (
    <div className="grid grid-cols-3 gap-2">
      <div className="grid gap-1.5">
        <Label htmlFor="campo-match">Match</Label>
        <Input
          id="campo-match"
          value={match}
          onChange={(evento) => onMatchChange(evento.target.value)}
          aria-invalid={Boolean(erroMatch)}
        />
        <p className="text-xs text-muted-foreground">Recomendado &gt; 0</p>
        {erroMatch && <p className="text-xs text-destructive">{erroMatch}</p>}
      </div>

      <div className="grid gap-1.5">
        <Label htmlFor="campo-mismatch">Mismatch</Label>
        <Input
          id="campo-mismatch"
          value={mismatch}
          onChange={(evento) => onMismatchChange(evento.target.value)}
          aria-invalid={Boolean(erroMismatch)}
        />
        <p className="text-xs text-muted-foreground">Recomendado &lt; 0</p>
        {erroMismatch && <p className="text-xs text-destructive">{erroMismatch}</p>}
      </div>

      <div className="grid gap-1.5">
        <Label htmlFor="campo-gap">Gap</Label>
        <Input
          id="campo-gap"
          value={gap}
          onChange={(evento) => onGapChange(evento.target.value)}
          aria-invalid={Boolean(erroGap)}
        />
        <p className="text-xs text-muted-foreground">Recomendado &lt; 0</p>
        {erroGap && <p className="text-xs text-destructive">{erroGap}</p>}
      </div>
    </div>
  )
}
