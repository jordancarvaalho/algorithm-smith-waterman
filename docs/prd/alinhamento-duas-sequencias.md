# PRD — Alinhamento de Duas Sequências de DNA (Smith-Waterman e Needleman-Wunsch)

> Tipo: Produto inicial · Data: 2026-10-19
> Status: Pronto para planejamento

## Visão geral e objetivo

Trabalho prático de Bioinformática/Programação Dinâmica: desenvolver uma aplicação que alinhe **exatamente duas sequências de DNA por execução**, por alinhamento local (Smith-Waterman) ou global (Needleman-Wunsch), implementados do zero.

O público é duplo: o aluno que implementa e o professor que avalia. A avaliação recai sobre a construção correta da matriz de programação dinâmica, o traceback, o cálculo do score, as validações de entrada e a clareza da saída. Por isso o produto não entrega apenas "o alinhamento": ele precisa **mostrar como a programação dinâmica chegou ao resultado**, com a matriz de pontuação, a matriz de direções e o caminho percorrido visíveis na tela e exportáveis em arquivo.

Resultado esperado da entrega: um avaliador consegue, em um comando, subir a aplicação, informar duas sequências e os parâmetros, executar nos dois modos, inspecionar as matrizes e o caminho do traceback, e salvar os resultados em arquivos.

## Contexto do projeto

Projeto novo, diretório vazio — não há código, stack ou convenções prévias. A única entrada é a especificação em `APR.Especificacao_Trabalho_Alinhamento_Duas_Sequencias.pdf` (corpo do documento + apêndice com três painéis de telas-modelo: Entrada/Validação, Saída na tela, Exportação).

Restrições constatadas na especificação:

- Escopo fechado em duas sequências por execução. Alinhamento múltiplo, perfis, Perfil × Sequência, Sum-of-Pairs, árvores-guia e seleção progressiva estão **fora** da especificação.
- Os algoritmos devem ser implementados pelos próprios alunos. É proibido usar biblioteca ou serviço que realize o alinhamento ou devolva pronta a matriz de programação dinâmica.
- Penalidade de gap **linear**. Modelo affine (abertura/extensão separadas) não é exigido.
- Linguagem e tecnologia de interface livres, desde que os requisitos funcionais sejam atendidos.

Duas divergências internas da especificação foram resolvidas nesta entrega:

- **Leitura de arquivo**: o corpo (2.1) trata como disponível e 2.4 exige validar arquivo inexistente/ilegível/incompatível; o painel do apêndice rotula FASTA como "opcional". Decidido implementar, porque a validação de arquivo é listada como obrigatória.
- **Exportação de arquivos**: ausente da seção 4, mas exigida explicitamente pelo painel 5 do apêndice ("o programa deverá gerar, no mínimo, os seguintes arquivos"). Decidido implementar.

A especificação também não define o desempate quando **várias células** da matriz têm o mesmo valor máximo no Smith-Waterman, embora exija determinismo. Esta lacuna foi fechada por decisão de produto (ver Regras de negócio).

## Decisões do produto

**Aplicação web local, servida por um único processo.** Backend em Python (FastAPI) que também serve o front como estático; o avaliador roda um script de conveniência e abre `localhost`. Motivo: o apêndice mostra uma interface rica (abas, matrizes coloridas, caminho destacado) que o modo texto não entrega, e um processo único elimina o atrito de "não consegui rodar".

**O backend é a autoridade sobre validação e algoritmo.** Toda regra de validação e todo o cálculo ficam no Python; o front faz apenas apresentação e conveniência visual. Motivo: o núcleo avaliado fica em um lugar só, testável sem navegador, sem risco de duas validações divergirem.

**Execução única por modo, com comparação como recurso adicional.** O usuário escolhe LOCAL ou GLOBAL e executa, como exige a especificação (2.2). Um comando adicional "Comparar os dois" roda ambos sobre a mesma entrada e apresenta os dois resultados lado a lado, atendendo 3.9 sem apagar o requisito do seletor.

**A matriz de traceback mostra todas as direções empatadas, com a seguida destacada.** Cada célula exibe as direções que atingiram o valor máximo; a direção efetivamente escolhida pela regra de desempate aparece em destaque, e o caminho completo é destacado em vermelho sobre a matriz de pontuação. Motivo: torna visível tanto a mecânica da programação dinâmica quanto a regra de desempate em ação.

**Entrada por digitação e por arquivo** (`.txt` e `.fasta`), com as validações de arquivo da especificação.

**Exportação por download do navegador**, com os nomes de arquivo do apêndice. Motivo: é o equivalente web honesto do diálogo "Salvar como" mostrado no mockup; gravar em pasta do servidor seria incorreto num app web.

**Matrizes grandes são exibidas até um limite configurável.** Acima dele, a tela mostra aviso e a região do traceback, enquanto o CSV exportado continua contendo a matriz **completa**. Motivo: preserva o requisito de disponibilizar a matriz sem travar a interface, e sem inventar um limite de tamanho de sequência que a especificação nega.

**Interface e mensagens em português (PT-BR).**

## Histórias de usuário

- Como aluno/usuário, quero digitar duas sequências de DNA e os parâmetros de pontuação, para executar um alinhamento sem editar código-fonte.
- Como aluno/usuário, quero carregar as duas sequências de um arquivo `.txt` ou `.fasta`, para não digitar sequências longas manualmente.
- Como aluno/usuário, quero escolher entre alinhamento LOCAL e GLOBAL, para aplicar Smith-Waterman ou Needleman-Wunsch sobre o mesmo par de sequências.
- Como aluno/usuário, quero ver a matriz de pontuação com o caminho do traceback destacado, para verificar como a programação dinâmica chegou ao score.
- Como aluno/usuário, quero ver a matriz de direções com os empates e a direção seguida, para entender a regra de desempate aplicada em cada célula.
- Como aluno/usuário, quero ver as duas sequências alinhadas com indicação de matches, mismatches e gaps, mais o score final, para interpretar o resultado.
- Como aluno/usuário, quero executar o mesmo par nos dois modos e ver os resultados lado a lado, para comparar alinhamento local e global sem reinformar a entrada.
- Como aluno/usuário, quero receber mensagens claras quando a entrada for inválida, para corrigir o que está errado antes de executar.
- Como aluno/usuário, quero exportar os resultados em arquivos, para anexá-los à entrega do trabalho.
- Como professor/avaliador, quero subir a aplicação com um comando e dependências mínimas, para avaliar o trabalho sem configurar ambiente.

## Regras de negócio e dados

### Entrada

- Cada execução recebe **exatamente duas** sequências, identificadas como Seq1 e Seq2. Nem mais, nem menos.
- Bases aceitas: **A, C, G, T**. Minúsculas são convertidas automaticamente para maiúsculas.
- As sequências podem ter comprimentos diferentes. Não há limite rígido de tamanho.
- Arquivo `.fasta`: cabeçalhos iniciados por `>` identificam as sequências; o arquivo deve conter exatamente duas. Arquivo `.txt`: aceito nos mesmos termos, com ou sem cabeçalhos FASTA.
- Match, Mismatch e Gap são **informados pelo usuário** e são números inteiros. Não podem ser fixos no código-fonte.

### Validações (bloqueiam a execução)

| Item | Regra |
|---|---|
| Número de sequências | Devem ser exatamente duas |
| Sequência vazia | Nenhuma das duas pode estar vazia |
| Caractere inválido | Qualquer caractere fora de A, C, G, T (após conversão para maiúscula) |
| Parâmetros | Match, Mismatch e Gap presentes e numéricos inteiros |
| Arquivo | Inexistente, ilegível ou em formato incompatível |

- A validação ocorre ao acionar a execução e reporta **todos** os problemas encontrados de uma vez, cada um apontando o campo e o detalhe (ex.: `Seq1 — base inválida: "X" na posição 5`).
- O processamento só inicia após todas as validações passarem.

### Aviso não bloqueante

- Se Match ≤ 0, ou Mismatch ≥ 0, ou Gap ≥ 0, a interface exibe um aviso de consistência (o apêndice trata esses valores como "recomendados", não obrigatórios). O usuário pode prosseguir.

### Função de pontuação

- Bases iguais → Match; bases diferentes → Mismatch; base alinhada com gap → Gap.
- Penalidade de gap linear: cada posição de gap custa Gap.

### Alinhamento global (Needleman-Wunsch)

- Primeira linha e primeira coluna inicializadas com penalidades acumuladas de gap (0, Gap, 2·Gap, 3·Gap, …).
- `F(i,j) = max( F(i-1,j-1) + score(Seq1[i], Seq2[j]), F(i-1,j) + Gap, F(i,j-1) + Gap )`
- O traceback começa na célula inferior direita e termina na origem da matriz.
- O score final é o valor da célula inferior direita.

### Alinhamento local (Smith-Waterman)

- Primeira linha e primeira coluna inicializadas com zero.
- `H(i,j) = max( 0, H(i-1,j-1) + score(Seq1[i], Seq2[j]), H(i-1,j) + Gap, H(i,j-1) + Gap )`
- O traceback começa na célula de maior valor da matriz e termina ao atingir uma célula de valor zero.
- O score final é o valor da célula onde o traceback começou.

### Determinismo

- **Empate dentro da célula**: prioridade diagonal → vertical → horizontal.
- **Empate entre células de valor máximo (local)**: vence a primeira encontrada na varredura linha a linha, da esquerda para a direita, de cima para baixo (menor i; em caso de igualdade, menor j). Esta regra é exibida na interface.
- Para a mesma entrada e os mesmos parâmetros, o resultado é sempre o mesmo.
- Um gap nunca é inserido por um valor ter ficado negativo; é consequência da escolha do caminho de maior score acumulado.

### Direções

| Movimento | Interpretação |
|---|---|
| Diagonal | Base de Seq1 alinhada com base de Seq2 |
| Vertical | Base de Seq1 alinhada com gap em Seq2 |
| Horizontal | Gap em Seq1 alinhado com base de Seq2 |

- Cada célula registra **todas** as direções que atingiram o valor máximo, e qual delas foi seguida pela regra de desempate.

### Saída na tela

Obrigatoriamente presentes: método utilizado (LOCAL ou GLOBAL); sequências originais; parâmetros Match, Mismatch e Gap; matriz de programação dinâmica; matriz de direções; as duas sequências alinhadas com os gaps inseridos; indicação visual de matches, mismatches e gaps; score final; tamanho do alinhamento.

- Representação do alinhamento: `|` para match, `.` para mismatch, espaço nas posições com gap. A legenda é exibida na interface.
- Na matriz de pontuação, o caminho do traceback é destacado em vermelho.
- Acima do limite de exibição configurável, a tela exibe aviso e a região do traceback; o CSV exportado mantém a matriz completa.

### Arquivos exportados

Execução única — quatro arquivos, nomeados com as sequências (padrão do apêndice):

| Arquivo | Conteúdo |
|---|---|
| `alinhamento_<Seq1>_<Seq2>.txt` | Resumo completo: algoritmo, sequências, parâmetros, score final, tamanho do alinhamento, alinhamento final com a linha de marcação e a legenda das direções |
| `matriz_pontuacao_<Seq1>_<Seq2>.csv` | Todos os valores da matriz de programação dinâmica, com cabeçalhos de linha e coluna |
| `matriz_traceback_<Seq1>_<Seq2>.csv` | Direções por célula, codificadas por letras: `D` diagonal, `V` vertical, `H` horizontal — **maiúscula** para a direção seguida, **minúscula** para as demais direções empatadas (ex.: `Dvh`). Célula de início/parada sem direção: `-` |
| `alinhamento_<Seq1>_<Seq2>.csv` | Uma linha por posição do alinhamento: Posição, Seq1, Linha (marcação), Seq2 |

- A legenda da codificação de direções consta do `.txt` e da interface.
- No modo comparação, um comando próprio exporta os quatro arquivos de cada algoritmo com sufixo de modo (`matriz_pontuacao_global_<Seq1>_<Seq2>.csv`, `matriz_pontuacao_local_<Seq1>_<Seq2>.csv`, …) mais um `.txt` único com os dois resumos. Os nomes sem sufixo permanecem reservados à execução única.
- "Exportar todos" entrega os arquivos em um `.zip`.

## Fluxos

### Execução de um alinhamento

1. O usuário informa Seq1 e Seq2 — digitando ou carregando arquivo `.txt`/`.fasta` — escolhe o modo (LOCAL ou GLOBAL), informa Match, Mismatch e Gap, e aciona Executar.
2. O sistema normaliza as sequências para maiúsculas e valida entrada e parâmetros. Havendo erros, exibe **todos** eles junto aos campos correspondentes e não processa nada.
3. Passando a validação, o sistema exibe aviso de consistência se Match ≤ 0 ou Mismatch/Gap ≥ 0, e segue.
4. O sistema cria a matriz, inicializa conforme o método, preenche as células, identifica o ponto inicial do traceback, executa o traceback, reconstrói as duas sequências alinhadas e calcula o score.
5. O sistema apresenta: resultado geral (algoritmo, score, tamanho do alinhamento, tamanho de cada sequência), matriz de pontuação com o caminho destacado, matriz de direções, alinhamento final com a linha de marcação, e resumo dos parâmetros.
6. Se a matriz exceder o limite de exibição, a tela mostra aviso e a região do traceback, informando que o CSV conterá a matriz completa.

### Carregamento por arquivo

1. O usuário seleciona um arquivo `.txt` ou `.fasta`.
2. O sistema lê o arquivo e extrai as sequências.
3. Arquivo inexistente, ilegível, em formato incompatível, ou que não contenha exatamente duas sequências: o sistema exibe o erro correspondente e não preenche os campos.
4. Lido com sucesso, o sistema preenche Seq1 e Seq2 nos campos, onde ainda podem ser editados antes da execução.

### Comparação Local × Global

1. Com as sequências e os parâmetros informados, o usuário aciona "Comparar os dois".
2. O sistema executa Smith-Waterman e Needleman-Wunsch sobre a mesma entrada, sem reinformar nada.
3. O sistema apresenta os dois resultados lado a lado: alinhamento, score, tamanho do alinhamento e matrizes de cada algoritmo.
4. O usuário pode exportar a comparação, obtendo os arquivos de ambos os algoritmos com sufixo de modo mais o `.txt` comparativo.

### Exportação

1. Com um resultado na tela, o usuário aciona Exportar e escolhe: arquivo de texto, matrizes em CSV, alinhamento em CSV, ou todos.
2. O sistema gera os arquivos com o conteúdo exatamente correspondente ao que está na tela — exceto as matrizes, que saem completas mesmo quando a tela as truncou.
3. O navegador entrega os arquivos por download, permitindo ao usuário escolher a pasta.

## Critérios de aceite

- Dado Seq1 = `ACGTAC`, Seq2 = `ACGTTC`, Match = 2, Mismatch = -1, Gap = -2 e modo GLOBAL, quando o usuário executa, então o score final é **9**, o alinhamento é `ACGTAC` / `ACGTTC` com marcação `||||.|`, e o tamanho do alinhamento é 6.
- Dado o mesmo par e parâmetros em modo GLOBAL, quando o usuário abre a matriz de pontuação, então a célula inferior direita vale 9, a primeira linha é `0, -2, -4, -6, -8, -10, -12` e a primeira coluna é `0, -2, -4, -6, -8, -10, -12`.
- Dado modo LOCAL, quando a matriz é inicializada, então a primeira linha e a primeira coluna contêm apenas zeros, nenhuma célula da matriz é negativa, e o score final é igual ao maior valor da matriz.
- Dado modo LOCAL, quando o traceback é executado, então ele começa na primeira célula de valor máximo na varredura de cima para baixo e da esquerda para a direita, e termina na primeira célula de valor zero encontrada no caminho.
- Dada uma célula cujo máximo é atingido por duas ou três direções, quando a matriz de direções é exibida, então todas as direções empatadas aparecem na célula e a direção seguida — diagonal, ou vertical se não houver diagonal empatada, ou horizontal em último caso — aparece destacada.
- Dada a mesma entrada e os mesmos parâmetros, quando a execução é repetida, então o alinhamento, o score e o caminho do traceback são idênticos.
- Dado `Seq1 = ACGTAXTG`, quando o usuário executa, então o sistema não processa e exibe erro indicando base inválida `X` e sua posição.
- Dada uma entrada com Seq2 vazia e Gap não numérico ao mesmo tempo, quando o usuário executa, então o sistema exibe **os dois** erros na mesma resposta.
- Dado um arquivo com três sequências, quando o usuário o carrega, então o sistema exibe erro de quantidade de sequências e não preenche os campos.
- Dado `Seq1 = acgta` e `Seq2 = TGCATG`, quando o usuário executa, então as sequências são tratadas como `ACGTA` e `TGCATG` e o alinhamento ocorre normalmente apesar dos comprimentos diferentes.
- Dado Match = -1, quando o usuário executa, então o sistema exibe aviso de consistência e ainda assim processa o alinhamento.
- Dado um resultado em tela, quando o usuário exporta todos os arquivos, então são gerados `alinhamento_<Seq1>_<Seq2>.txt`, `matriz_pontuacao_<Seq1>_<Seq2>.csv`, `matriz_traceback_<Seq1>_<Seq2>.csv` e `alinhamento_<Seq1>_<Seq2>.csv`, com os mesmos valores apresentados na tela.
- Dadas sequências maiores que o limite de exibição, quando o usuário executa e exporta, então a tela exibe aviso e a região do traceback, e o CSV de pontuação contém a matriz **completa**, com (m+1) × (n+1) células.
- Dado um par de sequências e parâmetros informados, quando o usuário aciona a comparação, então os resultados de Smith-Waterman e Needleman-Wunsch aparecem lado a lado sem que a entrada precise ser reinformada.
- Dado o projeto recém-obtido, quando o avaliador executa o script de inicialização, então a aplicação sobe e fica acessível no navegador sem passos manuais adicionais.

## Stack e restrições técnicas decididas

- **Backend: Python com FastAPI**, servindo também o front estático no mesmo processo. Dependências limitadas a `fastapi` e `uvicorn`.
- **Algoritmos em Python puro**, sem nenhuma biblioteca de bioinformática ou de alinhamento — exigência explícita da especificação. Matriz construída e preenchida pelo próprio código.
- **Front-end: React + TypeScript + Tailwind + shadcn/ui** (código-fonte em `frontend/`, build via Vite). Decisão posterior, substituindo a escolha original de HTML/CSS/JS sem framework. Justificativa: o bundle gerado (`npm run build`) é versionado em `web/` e servido estaticamente pelo mesmo backend FastAPI, então o avaliador continua precisando só de Python para executar o projeto — sem Node, sem build — mesmo com o front-end usando framework.
- **Script de inicialização** (`run.bat` / `run.sh`) que instala as dependências e sobe o servidor em um comando.
- **Complexidade**: preenchimento da matriz em O(m × n) de tempo e O(m × n) de memória, pois a matriz completa é preservada para exibição e traceback. A explicação é parte da entrega.
- **Idioma da interface e das mensagens**: português (PT-BR).
