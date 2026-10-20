import { useState } from 'react'
import { Button } from '@/components/ui/button'
import type { Formato } from '@/lib/tipos'

export interface BarraExportacaoProps {
  onExportar: (formato: Formato) => void
  /** Habilita os botões apenas quando há um Resultado (ou Comparacao) na tela. */
  temResultado: boolean
  /** Mostra o botão extra "Exportar Comparação (.ZIP)" quando o usuário acabou de rodar /api/comparar. */
  temComparacao: boolean
}

const FORMATOS_UNICOS: { formato: Formato; rotulo: string }[] = [
  { formato: 'txt', rotulo: 'TXT' },
  { formato: 'csv_pontuacao', rotulo: 'CSV Pontuação' },
  { formato: 'csv_traceback', rotulo: 'CSV Traceback' },
  { formato: 'csv_alinhamento', rotulo: 'CSV Alinhamento' },
]

/** Renderiza os botões de exportação (TXT, CSV Pontuação, CSV Traceback, CSV Alinhamento, ZIP, Comparação ZIP). */
export function BarraExportacao({ onExportar, temResultado, temComparacao }: BarraExportacaoProps) {
  const [baixando, setBaixando] = useState<Formato | null>(null)

  async function handleExportar(formato: Formato) {
    setBaixando(formato)
    try {
      await onExportar(formato)
    } finally {
      setBaixando(null)
    }
  }

  const desabilitado = !temResultado || baixando !== null

  return (
    <div className="flex flex-wrap items-center gap-2 rounded-lg border bg-card p-3">
      <span className="text-sm font-medium text-muted-foreground">Exportar:</span>
      {FORMATOS_UNICOS.map(({ formato, rotulo }) => (
        <Button
          key={formato}
          type="button"
          variant="outline"
          size="sm"
          disabled={desabilitado}
          onClick={() => handleExportar(formato)}
        >
          {rotulo}
        </Button>
      ))}
      <Button
        type="button"
        variant="secondary"
        size="sm"
        disabled={desabilitado}
        onClick={() => handleExportar(temComparacao ? 'comparacao_zip' : 'zip')}
      >
        {temComparacao ? 'Exportar Comparação (.zip)' : 'Exportar todos (.zip)'}
      </Button>
    </div>
  )
}
