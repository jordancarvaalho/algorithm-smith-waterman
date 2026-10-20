import { useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import type { Erro } from '@/lib/tipos'

export interface UploadArquivoProps {
  /** Chamado com o arquivo selecionado (.txt ou .fasta); o componente de tela decide quando chamar a API. */
  onArquivoSelecionado: (file: File) => void
  carregando: boolean
  /** Erro de campo 'arquivo', se a última tentativa de upload falhou. */
  erro?: Erro
}

/** Renderiza o seletor de arquivo .txt/.fasta, o botão "Carregar Arquivo" e a mensagem de erro de upload. */
export function UploadArquivo({ onArquivoSelecionado, carregando, erro }: UploadArquivoProps) {
  const [arquivo, setArquivo] = useState<File | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  function handleCarregar() {
    if (arquivo) onArquivoSelecionado(arquivo)
  }

  return (
    <div className="grid gap-1.5">
      <Label htmlFor="campo-arquivo">Carregar de arquivo (.txt ou .fasta)</Label>
      <div className="flex items-center gap-2">
        <input
          ref={inputRef}
          id="campo-arquivo"
          type="file"
          accept=".txt,.fasta"
          aria-invalid={Boolean(erro)}
          onChange={(evento) => setArquivo(evento.target.files?.[0] ?? null)}
          className="h-8 w-full min-w-0 rounded-lg border border-input bg-transparent text-sm text-muted-foreground file:mr-2 file:h-8 file:border-0 file:bg-muted file:px-2.5 file:text-sm file:font-medium file:text-foreground aria-invalid:border-destructive"
        />
        <Button
          type="button"
          variant="outline"
          disabled={!arquivo || carregando}
          onClick={handleCarregar}
        >
          Carregar Arquivo
        </Button>
      </div>
      {erro && <p className="text-xs text-destructive">{erro.mensagem}</p>}
    </div>
  )
}
