# Contrato de API e de módulos

> Fonte de verdade compartilhada entre todos os módulos. Ninguém altera este arquivo: se algo aqui estiver errado ou faltando, **pergunte ao coordenador** em vez de divergir.
>
> Regras de produto estão em `docs/prd/alinhamento-duas-sequencias.md`. Este documento define apenas **formas de dados, assinaturas e nomes**.

## 0. Convenções

- Índices: `i` percorre **Seq1** (linhas, `0..m`), `j` percorre **Seq2** (colunas, `0..n`). A linha/coluna 0 é a de inicialização.
- `matriz[i][j]` é inteiro. A matriz completa é sempre preservada e sempre devolvida.
- Todo texto visível ao usuário é PT-BR.
- Python 3.10+. `core/` e `export/` não importam nada além da biblioteca padrão.

## 1. Forma do resultado de um alinhamento

Objeto `Resultado`, devolvido como JSON pela API e consumido pelo front e pelo export:

```json
{
  "modo": "GLOBAL",
  "seq1": "ACGTAC",
  "seq2": "ACGTTC",
  "parametros": { "match": 2, "mismatch": -1, "gap": -2 },
  "matriz": [[0,-2,-4,-6,-8,-10,-12], "..."],
  "direcoes": [["-","H","H","H","H","H","H"], "..."],
  "caminho": [[6,6],[5,5],[4,4],[3,3],[2,2],[1,1],[0,0]],
  "inicio": [6, 6],
  "alinhamento": {
    "linha1":    "ACGTAC",
    "marcacao":  "||||.|",
    "linha2":    "ACGTTC"
  },
  "score": 9,
  "tamanho": 6,
  "avisos": []
}
```

- `modo`: `"GLOBAL"` ou `"LOCAL"`.
- `seq1` / `seq2`: as sequências **já normalizadas** (maiúsculas).
- `matriz`: `(m+1) × (n+1)` inteiros.
- `direcoes`: `(m+1) × (n+1)` strings, codificação da seção 2.
- `caminho`: células visitadas pelo traceback, **na ordem em que o traceback as visita** — da célula inicial até a célula de parada, inclusive. Serve ao destaque em vermelho na matriz de pontuação.
- `inicio`: `[i, j]` da célula onde o traceback começou. No GLOBAL é sempre `[m, n]`.
- `alinhamento`: as três linhas têm **exatamente o mesmo comprimento**. Gap é o caractere `-` em `linha1`/`linha2`. `marcacao`: `|` match, `.` mismatch, espaço (` `) em qualquer posição que envolva gap.
- `score`: inteiro. GLOBAL = `matriz[m][n]`. LOCAL = valor da célula de `inicio`.
- `tamanho`: comprimento do alinhamento (= `len(linha1)`).
- `avisos`: lista de avisos não bloqueantes (seção 4).

## 2. Codificação das direções

Uma única codificação serve à UI e ao CSV. Em cada célula, as letras das direções que **empataram no máximo**:

| Letra | Direção | Significado |
|---|---|---|
| `D` / `d` | diagonal | base de Seq1 alinhada com base de Seq2 |
| `V` / `v` | vertical | base de Seq1 alinhada com gap em Seq2 |
| `H` / `h` | horizontal | gap em Seq1 alinhado com base de Seq2 |

- **Maiúscula** = direção efetivamente seguida pela regra de desempate (diagonal → vertical → horizontal). **Minúscula** = direção empatada, não seguida.
- A ordem das letras na string é sempre `D`, `V`, `H`.
- Exatamente **uma** letra é maiúscula quando há alguma direção; `-` quando não há nenhuma.
- `-` ocorre em: a célula `[0][0]`; toda a linha 0 e coluna 0 do LOCAL (inicializadas com zero, sem predecessor); e qualquer célula do LOCAL cujo máximo seja o zero do truncamento.
- No GLOBAL, a linha 0 (exceto `[0][0]`) é `H` e a coluna 0 (exceto `[0][0]`) é `V`.

Exemplos: `D` (só diagonal), `Dvh` (as três empataram, seguiu diagonal), `dV` (diagonal e vertical empataram — impossível pela regra, serve só de ilustração de formato), `Vh`, `-`.

> Nota: como o desempate é determinístico, a maiúscula é sempre a primeira letra presente na ordem D→V→H.

## 3. Catálogo de erros (bloqueiam a execução)

`422` com `{ "erros": [ { "campo": ..., "codigo": ..., "mensagem": ... } ] }`. **Todos** os erros encontrados vão na mesma resposta — nunca só o primeiro.

| código | campo | mensagem (modelo) |
|---|---|---|
| `seq_quantidade` | `arquivo` | `O arquivo deve conter exatamente duas sequências (encontradas: 3).` |
| `seq_vazia` | `seq1` \| `seq2` | `Seq1 — a sequência não pode estar vazia.` |
| `base_invalida` | `seq1` \| `seq2` | `Seq1 — base inválida: "X" na posição 5.` (posição 1-based; um erro por sequência, citando a primeira ocorrência inválida e o total) |
| `parametro_ausente` | `match` \| `mismatch` \| `gap` | `Match — parâmetro obrigatório.` |
| `parametro_nao_numerico` | `match` \| `mismatch` \| `gap` | `Gap — deve ser um número inteiro.` |
| `modo_invalido` | `modo` | `Modo inválido: use LOCAL ou GLOBAL.` |
| `arquivo_inexistente` | `arquivo` | `Arquivo não encontrado.` |
| `arquivo_ilegivel` | `arquivo` | `Não foi possível ler o arquivo.` |
| `arquivo_formato` | `arquivo` | `Formato incompatível: use .txt ou .fasta.` |

## 4. Avisos (não bloqueiam)

`"avisos": [ { "codigo": ..., "campo": ..., "mensagem": ... } ]`

| código | condição | mensagem |
|---|---|---|
| `match_nao_positivo` | `match <= 0` | `Recomenda-se Match > 0.` |
| `mismatch_nao_negativo` | `mismatch >= 0` | `Recomenda-se Mismatch < 0.` |
| `gap_nao_negativo` | `gap >= 0` | `Recomenda-se Gap < 0.` |

## 5. Endpoints

Todos aceitam e devolvem JSON, salvo onde indicado.

### `POST /api/alinhar`

Corpo: `{ "seq1": "ACGTAC", "seq2": "ACGTTC", "modo": "GLOBAL", "match": 2, "mismatch": -1, "gap": -2 }`

- `200` → `Resultado` (seção 1).
- `422` → `{ "erros": [...] }`.

`match`/`mismatch`/`gap` podem chegar como número ou string (o front envia o conteúdo do campo); a API é responsável por detectar não-numérico e devolver `parametro_nao_numerico`.

### `POST /api/comparar`

Corpo: igual, **sem** `modo`.

- `200` → `{ "global": Resultado, "local": Resultado }`
- `422` → `{ "erros": [...] }`

### `POST /api/arquivo`

`multipart/form-data`, campo `arquivo`. Aceita `.txt` e `.fasta`.

- `200` → `{ "seq1": "ACGTAC", "seq2": "ACGTTC" }` (normalizadas)
- `422` → `{ "erros": [...] }`

Formato: linhas iniciadas por `>` são cabeçalhos FASTA. Sem nenhum `>`, cada linha não vazia é uma sequência. Em ambos os casos o arquivo deve render **exatamente duas** sequências. A validação de bases também se aplica aqui.

### `POST /api/exportar/{formato}`

`formato` ∈ `txt` | `csv_pontuacao` | `csv_traceback` | `csv_alinhamento` | `zip` | `comparacao_zip`

Corpo: **o mesmo de `/api/alinhar`** (ou, para `comparacao_zip`, o mesmo de `/api/comparar`). O servidor **recalcula** o alinhamento e serializa — é isso que garante que o arquivo bate com a tela.

- `200` → corpo binário/texto com `Content-Type` adequado e `Content-Disposition: attachment; filename="..."` (seção 6).
- `422` → `{ "erros": [...] }`

### Estáticos

`GET /` serve `web/index.html`; o resto de `web/` é servido na raiz (`/app.js`, `/estilo.css`, …).

## 6. Nomes e conteúdo dos arquivos exportados

Execução única (`<S1>` e `<S2>` = as sequências normalizadas, truncadas em 20 caracteres cada se forem maiores):

| formato | nome |
|---|---|
| `txt` | `alinhamento_<S1>_<S2>.txt` |
| `csv_pontuacao` | `matriz_pontuacao_<S1>_<S2>.csv` |
| `csv_traceback` | `matriz_traceback_<S1>_<S2>.csv` |
| `csv_alinhamento` | `alinhamento_<S1>_<S2>.csv` |
| `zip` | `alinhamento_<S1>_<S2>.zip` (contém os quatro acima) |
| `comparacao_zip` | `comparacao_<S1>_<S2>.zip` |

No `comparacao_zip`, os quatro arquivos de cada algoritmo levam sufixo de modo — `matriz_pontuacao_global_<S1>_<S2>.csv`, `matriz_pontuacao_local_<S1>_<S2>.csv`, … — mais um `alinhamento_comparacao_<S1>_<S2>.txt` com os dois resumos.

### CSV de pontuação

Primeira linha: célula vazia, `-`, e as bases de Seq2. Primeira coluna: `-` e as bases de Seq1.

```
,-,A,C,G,T,T,C
-,0,-2,-4,-6,-8,-10,-12
A,-2,2,0,-2,-4,-6,-8
```

### CSV de traceback

Mesmos cabeçalhos, células com a codificação da seção 2.

### CSV de alinhamento

```
Posicao,Seq1,Linha,Seq2
1,A,|,A
5,A,.,T
```

A coluna `Linha` traz `|`, `.` ou espaço, conforme a `marcacao`.

### Arquivo .txt

```
ALINHAMENTO GLOBAL (Needleman-Wunsch)
Sequência 1: ACGTAC
Sequência 2: ACGTTC
Match: 2
Mismatch: -1
Gap: -2
Score final: 9
Tamanho do alinhamento: 6

Alinhamento final:
Seq1: ACGTAC
      ||||.|
Seq2: ACGTTC

Legenda do alinhamento: | match, . mismatch, espaço indica gap.
Legenda das direções (matriz de traceback): D diagonal, V vertical, H horizontal.
Maiúscula = direção seguida; minúscula = direção empatada não seguida; - = sem direção.
Desempate dentro da célula: diagonal, vertical, horizontal.
Início do traceback (LOCAL): primeira célula de valor máximo na varredura de cima para baixo, da esquerda para a direita.

Matriz de pontuação: ver matriz_pontuacao_ACGTAC_ACGTTC.csv
Matriz de traceback: ver matriz_traceback_ACGTAC_ACGTTC.csv
```

## 7. Assinaturas dos módulos Python

### `core/` (dono: worker do core)

```python
# core/validacao.py
def normalizar_sequencia(texto: str) -> str: ...
    # remove espaços/quebras, converte para maiúsculas. NÃO valida.

def validar(seq1: str, seq2: str, modo: str, match, mismatch, gap) -> tuple[list[dict], list[dict], dict]: ...
    # Devolve (erros, avisos, parametros_convertidos).
    # erros/avisos no formato das seções 3 e 4. Acumula TODOS os erros.
    # parametros_convertidos = {"match": int, "mismatch": int, "gap": int} (só é confiável se erros == []).
    # modo == "" ou None é aceito sem erro (uso do /api/comparar).

# core/alinhamento.py
def alinhar(seq1: str, seq2: str, modo: str, match: int, mismatch: int, gap: int) -> dict: ...
    # Devolve o Resultado da seção 1, como dict pronto para JSON.
    # Pressupõe entrada já validada e normalizada.

# core/arquivos.py
def ler_sequencias(nome: str, conteudo: bytes) -> tuple[list[str], list[dict]]: ...
    # Devolve (sequencias_normalizadas, erros). Valida extensão, legibilidade,
    # quantidade (exatamente duas) e bases.
```

### `export/` (dono: worker de exportação)

```python
# export/arquivos.py
def gerar_txt(resultado: dict) -> str: ...
def gerar_csv_pontuacao(resultado: dict) -> str: ...
def gerar_csv_traceback(resultado: dict) -> str: ...
def gerar_csv_alinhamento(resultado: dict) -> str: ...
def gerar_zip(resultado: dict) -> bytes: ...
def gerar_txt_comparacao(resultado_global: dict, resultado_local: dict) -> str: ...
def gerar_comparacao_zip(resultado_global: dict, resultado_local: dict) -> bytes: ...
def nome_arquivo(formato: str, resultado: dict, sufixo_modo: str | None = None) -> str: ...
```

Todos recebem o `Resultado` da seção 1 como `dict` — `export/` não importa `core/`.

Encoding de todos os arquivos de texto: **UTF-8 com BOM** (`utf-8-sig`), para o Excel abrir os CSVs com acentos corretos. Separador: vírgula. Quebra de linha: `\r\n` nos CSVs.

## 8. Limite de exibição (front)

Constante em `web/config.js`: `LIMITE_EXIBICAO = 60`.

Se `m+1 > LIMITE_EXIBICAO` ou `n+1 > LIMITE_EXIBICAO`, a tela exibe aviso e apenas a janela da matriz que contém o caminho do traceback (com uma folga de 2 células em cada direção), informando que o CSV exportado traz a matriz completa. O backend **sempre** devolve a matriz inteira.

## 9. Caso canônico (vale para todos os aceites)

`Seq1 = ACGTAC`, `Seq2 = ACGTTC`, `match = 2`, `mismatch = -1`, `gap = -2`, modo `GLOBAL`:

```
        -    A    C    G    T    T    C
   -    0   -2   -4   -6   -8  -10  -12
   A   -2    2    0   -2   -4   -6   -8
   C   -4    0    4    2    0   -2   -4
   G   -6   -2    2    6    4    2    0
   T   -8   -4    0    4    8    6    4
   A  -10   -6   -2    2    6    7    5
   C  -12   -8   -4    0    4    5    9
```

`score = 9`, `tamanho = 6`, `linha1 = ACGTAC`, `marcacao = ||||.|`, `linha2 = ACGTTC`, `inicio = [6,6]`, `caminho = [[6,6],[5,5],[4,4],[3,3],[2,2],[1,1],[0,0]]`.
