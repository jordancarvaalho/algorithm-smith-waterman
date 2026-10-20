import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { BotoesAcao } from '@/components/entrada/BotoesAcao'
import { CamposSequencias } from '@/components/entrada/CamposSequencias'
import { ListaAvisos } from '@/components/entrada/ListaAvisos'
import { ListaErros } from '@/components/entrada/ListaErros'
import { ParametrosPontuacao } from '@/components/entrada/ParametrosPontuacao'
import { SeletorAlgoritmo } from '@/components/entrada/SeletorAlgoritmo'
import { UploadArquivo } from '@/components/entrada/UploadArquivo'
import type { Aviso, Erro, Modo } from '@/lib/tipos'

export interface PainelEntradaProps {
  seq1: string
  seq2: string
  modo: Modo
  match: string
  mismatch: string
  gap: string
  onSeq1Change: (valor: string) => void
  onSeq2Change: (valor: string) => void
  onModoChange: (modo: Modo) => void
  onMatchChange: (valor: string) => void
  onMismatchChange: (valor: string) => void
  onGapChange: (valor: string) => void
  onArquivoSelecionado: (file: File) => void
  onExecutar: () => void
  onComparar: () => void
  onLimpar: () => void
  carregando: boolean
  erros: Erro[]
  avisos: Aviso[]
}

function erroDoCampo(erros: Erro[], campo: string): Erro | undefined {
  return erros.find((erro) => erro.campo === campo)
}

/** Compõe o card de "Entrada de Dados": upload, campos de sequência, seletor de algoritmo, parâmetros, erros/avisos e botões de ação. */
export function PainelEntrada({
  seq1,
  seq2,
  modo,
  match,
  mismatch,
  gap,
  onSeq1Change,
  onSeq2Change,
  onModoChange,
  onMatchChange,
  onMismatchChange,
  onGapChange,
  onArquivoSelecionado,
  onExecutar,
  onComparar,
  onLimpar,
  carregando,
  erros,
  avisos,
}: PainelEntradaProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Entrada de Dados</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4">
        <ListaErros erros={erros} />
        <ListaAvisos avisos={avisos} />

        <UploadArquivo
          onArquivoSelecionado={onArquivoSelecionado}
          carregando={carregando}
          erro={erroDoCampo(erros, 'arquivo')}
        />

        <Separator />

        <CamposSequencias
          seq1={seq1}
          seq2={seq2}
          onSeq1Change={onSeq1Change}
          onSeq2Change={onSeq2Change}
          erroSeq1={erroDoCampo(erros, 'seq1')?.mensagem}
          erroSeq2={erroDoCampo(erros, 'seq2')?.mensagem}
        />

        <Separator />

        <SeletorAlgoritmo modo={modo} onModoChange={onModoChange} erro={erroDoCampo(erros, 'modo')?.mensagem} />

        <ParametrosPontuacao
          match={match}
          mismatch={mismatch}
          gap={gap}
          onMatchChange={onMatchChange}
          onMismatchChange={onMismatchChange}
          onGapChange={onGapChange}
          erroMatch={erroDoCampo(erros, 'match')?.mensagem}
          erroMismatch={erroDoCampo(erros, 'mismatch')?.mensagem}
          erroGap={erroDoCampo(erros, 'gap')?.mensagem}
        />

        <Separator />

        <BotoesAcao
          onExecutar={onExecutar}
          onComparar={onComparar}
          onLimpar={onLimpar}
          carregando={carregando}
        />
      </CardContent>
    </Card>
  )
}
