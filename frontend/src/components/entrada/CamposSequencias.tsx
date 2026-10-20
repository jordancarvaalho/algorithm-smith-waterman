import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'

export interface CamposSequenciasProps {
  seq1: string
  seq2: string
  onSeq1Change: (valor: string) => void
  onSeq2Change: (valor: string) => void
  /** Mensagem de erro específica do campo seq1 (campo 'seq1' no contrato), se houver. */
  erroSeq1?: string
  /** Mensagem de erro específica do campo seq2 (campo 'seq2' no contrato), se houver. */
  erroSeq2?: string
}

const CLASSE_TEXTAREA =
  'min-h-20 w-full resize-y rounded-lg border border-input bg-transparent px-2.5 py-1.5 font-mono text-sm uppercase transition-colors outline-none placeholder:text-muted-foreground placeholder:normal-case focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 dark:bg-input/30'

const CLASSE_TEXTAREA_ERRO = 'border-destructive ring-3 ring-destructive/20'

/** Renderiza os dois textareas de Sequência 1 e Sequência 2, com contador de bases e destaque de erro por campo. */
export function CamposSequencias({
  seq1,
  seq2,
  onSeq1Change,
  onSeq2Change,
  erroSeq1,
  erroSeq2,
}: CamposSequenciasProps) {
  return (
    <div className="grid gap-3">
      <div className="grid gap-1.5">
        <div className="flex items-center justify-between">
          <Label htmlFor="campo-seq1">Sequência 1</Label>
          <span className="text-xs text-muted-foreground">{seq1.length} base(s)</span>
        </div>
        <textarea
          id="campo-seq1"
          value={seq1}
          onChange={(evento) => onSeq1Change(evento.target.value)}
          placeholder="Ex.: ACGTAC"
          aria-invalid={Boolean(erroSeq1)}
          className={cn(CLASSE_TEXTAREA, erroSeq1 && CLASSE_TEXTAREA_ERRO)}
        />
        {erroSeq1 && <p className="text-xs text-destructive">{erroSeq1}</p>}
      </div>

      <div className="grid gap-1.5">
        <div className="flex items-center justify-between">
          <Label htmlFor="campo-seq2">Sequência 2</Label>
          <span className="text-xs text-muted-foreground">{seq2.length} base(s)</span>
        </div>
        <textarea
          id="campo-seq2"
          value={seq2}
          onChange={(evento) => onSeq2Change(evento.target.value)}
          placeholder="Ex.: ACGTTC"
          aria-invalid={Boolean(erroSeq2)}
          className={cn(CLASSE_TEXTAREA, erroSeq2 && CLASSE_TEXTAREA_ERRO)}
        />
        {erroSeq2 && <p className="text-xs text-destructive">{erroSeq2}</p>}
      </div>
    </div>
  )
}
