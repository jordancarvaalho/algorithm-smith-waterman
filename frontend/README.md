# Front-end — Alinhamento de Duas Sequências de DNA

Vite + React + TypeScript + Tailwind CSS + shadcn/ui. Consome a API FastAPI descrita em `docs/contrato-api.md`.

## Desenvolvimento

```sh
npm install
npm run dev
```

Sobe o servidor de desenvolvimento do Vite com proxy de `/api` para `http://localhost:8000` (configurado em `vite.config.ts`). Suba o backend separadamente nessa porta:

```sh
.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```

## Build

```sh
npm run build
```

Roda `tsc -b` e depois `vite build`, escrevendo a saída em `../web` (`build.outDir`, com `emptyOutDir: true`). O FastAPI (`app/main.py`) serve `web/` na raiz do processo único.

**`web/` é saída de build gerada por este comando — não edite os arquivos ali à mão.** Qualquer alteração deve ser feita em `frontend/src/` e reconstruída com `npm run build`.

## Estrutura

- `src/lib/tipos.ts` — tipos TypeScript espelhando o contrato da API (seção 1 de `docs/contrato-api.md`).
- `src/lib/api.ts` — cliente HTTP (`alinhar`, `comparar`, `enviarArquivo`, `exportar`).
- `src/lib/config.ts` — `LIMITE_EXIBICAO`.
- `src/lib/direcoes.ts` — decodificação da codificação de direções do traceback.
- `src/components/entrada/` — componentes do painel de entrada (formulário, upload, erros/avisos, ações, exportação).
- `src/components/resultado/` — componentes das abas de resultado (matrizes, alinhamento, resumo, comparação).
- `src/App.tsx` — casca da aplicação: layout de duas colunas, estado central e navegação por abas.
