import { useState } from 'react'
import { PainelEntrada } from '@/components/entrada/PainelEntrada'
import { BarraExportacao } from '@/components/entrada/BarraExportacao'
import { ResultadoGeral } from '@/components/resultado/ResultadoGeral'
import { MatrizPontuacao } from '@/components/resultado/MatrizPontuacao'
import { MatrizTraceback } from '@/components/resultado/MatrizTraceback'
import { AlinhamentoFinal } from '@/components/resultado/AlinhamentoFinal'
import { Resumo } from '@/components/resultado/Resumo'
import { ComparacaoLadoALado } from '@/components/resultado/ComparacaoLadoALado'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Toaster } from '@/components/ui/sonner'
import { TooltipProvider } from '@/components/ui/tooltip'
import { alinhar, comparar, enviarArquivo, exportar, ApiErroValidacao, ApiErroRede } from '@/lib/api'
import { LIMITE_EXIBICAO } from '@/lib/config'
import type { Aviso, Comparacao, Erro, Formato, Modo, Resultado } from '@/lib/tipos'

type IdAba =
  | 'resultado-geral'
  | 'matriz-pontuacao'
  | 'matriz-traceback'
  | 'alinhamento'
  | 'resumo'
  | 'comparacao'

/** Estado central da aplicação: entrada do formulário, resultado da última execução, comparação, erros/avisos e carregamento. */
interface EstadoApp {
  seq1: string
  seq2: string
  modo: Modo
  match: string
  mismatch: string
  gap: string
  resultado: Resultado | null
  comparacao: Comparacao | null
  erros: Erro[]
  avisos: Aviso[]
  carregando: boolean
}

const ESTADO_INICIAL: EstadoApp = {
  // Valores de conveniência: o par do exemplo da especificação, editáveis pelo usuário.
  seq1: 'ACGTAC',
  seq2: 'ACGTTC',
  modo: 'GLOBAL',
  match: '2',
  mismatch: '-1',
  gap: '-2',
  resultado: null,
  comparacao: null,
  erros: [],
  avisos: [],
  carregando: false,
}

function App() {
  const [estado, setEstado] = useState<EstadoApp>(ESTADO_INICIAL)
  const [abaAtiva, setAbaAtiva] = useState<IdAba>('resultado-geral')

  function corpoRequisicao() {
    return {
      seq1: estado.seq1,
      seq2: estado.seq2,
      match: estado.match,
      mismatch: estado.mismatch,
      gap: estado.gap,
    }
  }

  async function executarAlinhamento() {
    setEstado((e) => ({ ...e, carregando: true, erros: [] }))
    try {
      const resultado = await alinhar({ ...corpoRequisicao(), modo: estado.modo })
      setEstado((e) => ({ ...e, resultado, avisos: resultado.avisos, carregando: false }))
      setAbaAtiva('resultado-geral')
    } catch (erro) {
      if (erro instanceof ApiErroValidacao) {
        setEstado((e) => ({ ...e, erros: erro.erros, carregando: false }))
      } else if (erro instanceof ApiErroRede) {
        setEstado((e) => ({
          ...e,
          erros: [{ campo: 'seq1', codigo: 'conexao_api', mensagem: erro.message }],
          carregando: false,
        }))
      } else {
        throw erro
      }
    }
  }

  async function executarComparacao() {
    setEstado((e) => ({ ...e, carregando: true, erros: [] }))
    try {
      const resultadoComparacao = await comparar(corpoRequisicao())
      setEstado((e) => ({
        ...e,
        comparacao: resultadoComparacao,
        resultado: resultadoComparacao.global,
        carregando: false,
      }))
      setAbaAtiva('comparacao')
    } catch (erro) {
      if (erro instanceof ApiErroValidacao) {
        setEstado((e) => ({ ...e, erros: erro.erros, carregando: false }))
      } else if (erro instanceof ApiErroRede) {
        setEstado((e) => ({
          ...e,
          erros: [{ campo: 'seq1', codigo: 'conexao_api', mensagem: erro.message }],
          carregando: false,
        }))
      } else {
        throw erro
      }
    }
  }

  async function carregarArquivo(file: File) {
    setEstado((e) => ({ ...e, erros: [] }))
    try {
      const { seq1, seq2 } = await enviarArquivo(file)
      setEstado((e) => ({ ...e, seq1, seq2 }))
    } catch (erro) {
      if (erro instanceof ApiErroValidacao) {
        setEstado((e) => ({ ...e, erros: erro.erros }))
      } else if (erro instanceof ApiErroRede) {
        setEstado((e) => ({
          ...e,
          erros: [{ campo: 'arquivo', codigo: 'conexao_api', mensagem: erro.message }],
        }))
      } else {
        throw erro
      }
    }
  }

  function limparCampos() {
    setEstado(ESTADO_INICIAL)
  }

  async function exportarFormato(formato: Formato) {
    try {
      const isComparacao = formato === 'comparacao_zip'
      await exportar(formato, isComparacao ? corpoRequisicao() : { ...corpoRequisicao(), modo: estado.modo })
    } catch (erro) {
      if (erro instanceof ApiErroValidacao) {
        setEstado((e) => ({ ...e, erros: erro.erros }))
      } else if (erro instanceof ApiErroRede) {
        setEstado((e) => ({
          ...e,
          erros: [{ campo: 'seq1', codigo: 'conexao_api', mensagem: erro.message }],
        }))
      } else {
        throw erro
      }
    }
  }

  return (
    <TooltipProvider>
      <div className="min-h-svh bg-background text-foreground">
        <header className="border-b px-6 py-4">
          <h1 className="text-xl font-semibold">Alinhamento de Duas Sequências de DNA</h1>
          <p className="text-sm text-muted-foreground">
            Programação Dinâmica: Smith-Waterman (Local) &amp; Needleman-Wunsch (Global)
          </p>
        </header>

        <main className="grid grid-cols-1 gap-6 p-6 lg:grid-cols-[360px_1fr]">
          <aside>
            <PainelEntrada
              seq1={estado.seq1}
              seq2={estado.seq2}
              modo={estado.modo}
              match={estado.match}
              mismatch={estado.mismatch}
              gap={estado.gap}
              onSeq1Change={(seq1) => setEstado((e) => ({ ...e, seq1 }))}
              onSeq2Change={(seq2) => setEstado((e) => ({ ...e, seq2 }))}
              onModoChange={(modo) => setEstado((e) => ({ ...e, modo }))}
              onMatchChange={(match) => setEstado((e) => ({ ...e, match }))}
              onMismatchChange={(mismatch) => setEstado((e) => ({ ...e, mismatch }))}
              onGapChange={(gap) => setEstado((e) => ({ ...e, gap }))}
              onArquivoSelecionado={carregarArquivo}
              onExecutar={executarAlinhamento}
              onComparar={executarComparacao}
              onLimpar={limparCampos}
              carregando={estado.carregando}
              erros={estado.erros}
              avisos={estado.avisos}
            />
          </aside>

          <section className="flex flex-col gap-4">
            <BarraExportacao
              onExportar={exportarFormato}
              temResultado={estado.resultado !== null}
              temComparacao={estado.comparacao !== null}
            />

            <Tabs value={abaAtiva} onValueChange={(valor) => setAbaAtiva(valor as IdAba)}>
              <TabsList>
                <TabsTrigger value="resultado-geral">Resultado Geral</TabsTrigger>
                <TabsTrigger value="matriz-pontuacao">Matriz de Pontuação</TabsTrigger>
                <TabsTrigger value="matriz-traceback">Matriz de Traceback</TabsTrigger>
                <TabsTrigger value="alinhamento">Alinhamento</TabsTrigger>
                <TabsTrigger value="resumo">Resumo</TabsTrigger>
                {estado.comparacao && <TabsTrigger value="comparacao">Comparação</TabsTrigger>}
              </TabsList>

              <TabsContent value="resultado-geral">
                {estado.resultado ? (
                  <ResultadoGeral resultado={estado.resultado} />
                ) : (
                  <p className="text-sm text-muted-foreground">
                    Informe as duas sequências e os parâmetros e clique em Executar Alinhamento.
                  </p>
                )}
              </TabsContent>

              <TabsContent value="matriz-pontuacao">
                {estado.resultado && (
                  <MatrizPontuacao resultado={estado.resultado} limiteExibicao={LIMITE_EXIBICAO} />
                )}
              </TabsContent>

              <TabsContent value="matriz-traceback">
                {estado.resultado && (
                  <MatrizTraceback resultado={estado.resultado} limiteExibicao={LIMITE_EXIBICAO} />
                )}
              </TabsContent>

              <TabsContent value="alinhamento">
                {estado.resultado && <AlinhamentoFinal resultado={estado.resultado} />}
              </TabsContent>

              <TabsContent value="resumo">
                {estado.resultado && <Resumo resultado={estado.resultado} />}
              </TabsContent>

              {estado.comparacao && (
                <TabsContent value="comparacao">
                  <ComparacaoLadoALado comparacao={estado.comparacao} limiteExibicao={LIMITE_EXIBICAO} />
                </TabsContent>
              )}
            </Tabs>
          </section>
        </main>

        <Toaster />
      </div>
    </TooltipProvider>
  )
}

export default App
