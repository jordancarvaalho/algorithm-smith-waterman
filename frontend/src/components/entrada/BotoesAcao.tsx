import { Button } from '@/components/ui/button'

export interface BotoesAcaoProps {
  onExecutar: () => void
  onComparar: () => void
  onLimpar: () => void
  carregando: boolean
}

/** Renderiza os botões "Executar Alinhamento", "Comparar os dois" e "Limpar Campos", desabilitados durante carregamento. */
export function BotoesAcao({ onExecutar, onComparar, onLimpar, carregando }: BotoesAcaoProps) {
  return (
    <div className="flex flex-wrap gap-2">
      <Button type="button" onClick={onExecutar} disabled={carregando}>
        {carregando ? 'Executando…' : 'Executar Alinhamento'}
      </Button>
      <Button type="button" variant="secondary" onClick={onComparar} disabled={carregando}>
        {carregando ? 'Executando…' : 'Comparar os dois'}
      </Button>
      <Button type="button" variant="ghost" onClick={onLimpar} disabled={carregando}>
        Limpar Campos
      </Button>
    </div>
  )
}
