import { Alert, AlertTitle } from '@/components/ui/alert'

/** Placeholder visual padrão para componentes ainda não implementados pelos workers de tela. */
export function EmConstrucao({ nome }: { nome: string }) {
  return (
    <Alert>
      <AlertTitle>{nome} — em construção</AlertTitle>
    </Alert>
  )
}
