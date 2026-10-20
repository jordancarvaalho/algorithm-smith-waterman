# Alinhamento de Duas Sequências de DNA

Trabalho prático de Bioinformática — alinhamento de **exatamente duas sequências de DNA por execução** usando programação dinâmica:

- **Alinhamento Global** — algoritmo de **Needleman-Wunsch**
- **Alinhamento Local** — algoritmo de **Smith-Waterman**

Os dois algoritmos foram implementados do zero, em Python puro. O projeto **não usa nenhuma biblioteca de alinhamento ou de bioinformática** — nem para calcular o alinhamento, nem para montar a matriz de programação dinâmica.

A aplicação é web e roda localmente: um processo FastAPI que calcula os alinhamentos e serve a interface.

## Autoria

Trabalho desenvolvido por:

- **Samuel Furtado Fortes**
- **Jordan Carvalho Araujo**

---

## Como executar

**Windows:**

```bat
run.bat
```

**Linux / macOS:**

```sh
./run.sh
```

O script cria o ambiente virtual (`.venv`), instala as dependências e sobe o servidor. Depois é só abrir:

```
http://localhost:8000
```

Requisito: **Python 3.10 ou superior**. Nenhum outro pré-requisito — sem banco de dados, e sem precisar de Node nem rodar nenhum build: o bundle do front-end já vem pronto e versionado em `web/`.

<details>
<summary>Subindo manualmente, sem o script</summary>

```sh
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```
</details>

---

## Como usar

1. Informe **Seq1** e **Seq2** — digitando, ou carregando um arquivo `.txt` / `.fasta` com exatamente duas sequências.
2. Escolha o algoritmo: **GLOBAL** (Needleman-Wunsch) ou **LOCAL** (Smith-Waterman).
3. Informe **Match**, **Mismatch** e **Gap**. Os valores iniciais são 2, -1 e -2, mas são apenas sugestões: os três são lidos do formulário e nunca estão fixos no código.
4. Clique em **Executar Alinhamento** — ou em **Comparar os dois**, que roda os dois algoritmos sobre a mesma entrada e mostra os resultados lado a lado.

O resultado aparece em cinco abas:

| Aba | Conteúdo |
|---|---|
| **Resultado Geral** | Algoritmo, score final, tamanho do alinhamento e tamanho de cada sequência |
| **Matriz de Pontuação** | A matriz completa (m+1)×(n+1), com o caminho do traceback destacado em vermelho |
| **Matriz de Traceback** | As direções de cada célula, com legenda |
| **Alinhamento** | As duas sequências alinhadas, com a linha de marcação e o score |
| **Resumo** | Algoritmo, parâmetros, score e tamanho |

### Exemplo

Com `Seq1 = ACGTAC`, `Seq2 = ACGTTC`, Match = 2, Mismatch = -1, Gap = -2, modo GLOBAL:

```
Seq1: A C G T A C
      | | | | . |
Seq2: A C G T T C

Score: 9       (5 matches × (+2) + 1 mismatch × (-1))
```

---

## Entendendo a saída

### Marcação do alinhamento

| Símbolo | Significado |
|---|---|
| `\|` | match — as bases coincidem |
| `.` | mismatch — bases diferentes |
| espaço | a posição envolve um gap |

### Matriz de traceback

Cada célula mostra **todas** as direções que empataram com o valor máximo. A direção efetivamente seguida aparece em destaque; as empatadas que não foram seguidas aparecem esmaecidas.

| Seta | Código | Significado |
|---|---|---|
| ↖ | `D` / `d` | diagonal — base de Seq1 alinhada com base de Seq2 |
| ↑ | `V` / `v` | vertical — base de Seq1 alinhada com gap em Seq2 |
| ← | `H` / `h` | horizontal — gap em Seq1 alinhado com base de Seq2 |
| · | `-` | sem direção — origem `[0,0]`, ou truncamento a zero no LOCAL |

Nos arquivos CSV exportados a mesma informação vai em letras: **maiúscula** é a direção seguida, **minúscula** é uma direção empatada não seguida. Exemplo: `Dvh` significa que as três direções empataram e o algoritmo seguiu a diagonal.

### Regras de desempate (determinismo)

A mesma entrada com os mesmos parâmetros produz **sempre** o mesmo alinhamento:

- **Dentro de uma célula:** diagonal → vertical → horizontal.
- **Entre células de valor máximo (só no LOCAL):** vence a primeira encontrada na varredura linha a linha, de cima para baixo e da esquerda para a direita. A especificação não definia esta regra; ela foi fixada para garantir o determinismo que a própria especificação exige.

---

## Exportação

Os botões de exportação geram, pelo navegador:

| Arquivo | Conteúdo |
|---|---|
| `alinhamento_<Seq1>_<Seq2>.txt` | Resumo completo: algoritmo, sequências, parâmetros, score, tamanho, alinhamento e legendas |
| `matriz_pontuacao_<Seq1>_<Seq2>.csv` | Todos os valores da matriz de programação dinâmica |
| `matriz_traceback_<Seq1>_<Seq2>.csv` | A direção de cada célula |
| `alinhamento_<Seq1>_<Seq2>.csv` | Uma linha por posição: Posição, Seq1, Linha, Seq2 |

**Exportar Todos** entrega os quatro em um `.zip`. Na comparação, um botão próprio gera os quatro arquivos de cada algoritmo (com sufixo `_global` / `_local`) mais um `.txt` comparativo.

Os CSVs saem em UTF-8 com BOM, para abrirem com acentuação correta no Excel. **As matrizes exportadas são sempre completas**, mesmo quando a tela as exibe recortada.

---

## Validações

O processamento só inicia depois que a entrada passa pela validação, e **todos** os problemas encontrados são exibidos de uma vez — não apenas o primeiro.

| Verificação | Regra |
|---|---|
| Número de sequências | Exatamente duas |
| Sequência vazia | Nenhuma das duas pode estar vazia |
| Caracteres | Apenas A, C, G e T (minúsculas são convertidas automaticamente) |
| Parâmetros | Match, Mismatch e Gap presentes e inteiros |
| Arquivo | Existente, legível e em formato compatível (`.txt` ou `.fasta`) |

Há também avisos **não bloqueantes** de consistência quando Match ≤ 0, Mismatch ≥ 0 ou Gap ≥ 0: a especificação trata esses valores como recomendados, não obrigatórios, então o alinhamento é processado mesmo assim.

A validação é feita inteiramente no backend. O front-end não revalida nada: ele envia o que o usuário digitou e exibe o que o servidor responde.

---

## Estrutura do projeto

```
core/       Algoritmos, validação e leitura de arquivos — somente biblioteca padrão
  alinhamento.py    Needleman-Wunsch, Smith-Waterman, traceback e reconstrução
  validacao.py      Normalização das sequências e validação acumulativa
  arquivos.py       Leitura de .txt e .fasta
export/     Serialização dos resultados (.txt, CSVs, .zip) — somente biblioteca padrão
app/        API FastAPI e serviço dos arquivos estáticos
frontend/   Código-fonte da interface: React + TypeScript + Tailwind + shadcn/ui (Vite)
web/        Saída do build do front-end (gerada por `npm run build`), VERSIONADA — não editar à mão
tests/      52 testes automatizados + RELATORIO.md
docs/       PRD do produto e contrato de API
```

### API

| Método | Rota | Função |
|---|---|---|
| POST | `/api/alinhar` | Executa um alinhamento no modo escolhido |
| POST | `/api/comparar` | Executa GLOBAL e LOCAL sobre a mesma entrada |
| POST | `/api/arquivo` | Extrai as duas sequências de um `.txt` / `.fasta` |
| POST | `/api/exportar/{formato}` | Gera o arquivo pedido, recalculando no servidor |
| GET | `/` | Serve a interface |

O formato exato de cada requisição e resposta está em [`docs/contrato-api.md`](docs/contrato-api.md). As decisões de produto estão em [`docs/prd/alinhamento-duas-sequencias.md`](docs/prd/alinhamento-duas-sequencias.md).

---

## Testes

```sh
pip install -r requirements.txt -r tests/requirements-dev.txt
python -m pytest tests/
```

Ou, sem nenhuma dependência além do próprio projeto:

```sh
python -m unittest discover tests
```

São 52 testes cobrindo item a item os critérios de aceite do trabalho: o caso canônico, as bordas do LOCAL, o início e a parada do traceback, empates simples e triplos, determinismo entre execuções, cada uma das validações, a exportação dos quatro arquivos e a subida real do servidor. O resultado detalhado está em [`tests/RELATORIO.md`](tests/RELATORIO.md).

`pytest` e `httpx` são dependências **apenas de desenvolvimento**. O runtime da aplicação se limita a `fastapi`, `uvicorn` e `python-multipart`.

---

## Complexidade

Para sequências de comprimentos *m* e *n*:

- **Tempo: O(m × n)** — cada célula da matriz é calculada uma única vez, a partir de três comparações de valor constante (diagonal, vertical e horizontal). O traceback percorre no máximo *m + n* células, o que não altera a ordem.
- **Espaço: O(m × n)** — a matriz completa é preservada. Existem variações que usam apenas O(min(m, n)) de memória guardando duas linhas por vez, mas elas não permitem reconstruir o caminho nem exibir a matriz — e aqui a matriz e o traceback são parte do resultado.

---

## Desenvolvimento do front-end

Quem só quer **executar** o projeto não precisa de Node: `run.bat` / `run.sh` sobem tudo só com Python, porque o bundle do front-end já está buildado e versionado em `web/`.

Para **desenvolver** a interface (código-fonte em `frontend/`), com o backend rodando em paralelo na porta 8000:

```sh
# Terminal 1 — backend
run.bat          # Windows
./run.sh         # Linux / macOS

# Terminal 2 — front-end em modo dev
cd frontend
npm install
npm run dev
```

Para regerar `web/` a partir do código-fonte depois de alterar o front-end:

```sh
cd frontend
npm run build
```

O resultado de `npm run build` deve ser commitado em `web/`, já que é o que `run.bat` / `run.sh` servem em produção. A aplicação **sempre** fala com a API: abre sem nenhum resultado na tela e nunca substitui uma falha do servidor por dados de exemplo.
