# Relatório de testes — W5 (Integração, testes e verificação end-to-end)

## Resumo

- **52 testes automatizados**, todos **PASSARAM** na primeira execução contra o código entregue pelos workers de `core/`, `export/`, `app/` e `web/`.
- **Nenhum defeito foi encontrado** na costura entre os módulos: as assinaturas, formas de resposta, nomes de arquivo e comportamento de validação já batiam exatamente com `docs/contrato-api.md` e com os critérios de aceite de `docs/prd/alinhamento-duas-sequencias.md`.
- **Nenhuma correção de código foi necessária** em `core/`, `export/`, `app/` ou `web/`. Este relatório documenta a verificação, não uma lista de bugs corrigidos.
- Framework de testes: **`unittest`** da biblioteca padrão (os arquivos também são descobertos e rodados pelo `pytest`, usado apenas como executor/coletor). Justificativa: `core/` e `export/` já seguem a restrição de só usar a stdlib; manter os testes em `unittest` puro significa que a suíte roda com `python -m unittest discover tests` sem nenhuma dependência extra. `pytest` foi adicionado só como conveniência de execução (`python -m pytest tests/`, com saída mais legível) — ver `tests/requirements-dev.txt`.

## Como rodar

```sh
pip install -r requirements.txt -r tests/requirements-dev.txt
python -m pytest tests/
# ou, sem nenhuma dependência extra além do próprio projeto:
python -m unittest discover tests
```

`tests/requirements-dev.txt` traz `pytest` e `httpx` (exigido pelo `fastapi.testclient.TestClient`). Nenhum dos dois entra no `requirements.txt` da raiz, que continua limitado a `fastapi`, `uvicorn` e `python-multipart` (seção 0 e 7 do contrato). `core/` e `export/` não foram tocados e continuam importando apenas a biblioteca padrão.

## Verificação da restrição de bibliotecas

Busca por imports de bibliotecas de alinhamento/bioinformática (Biopython, `Bio.*`, `pairwise2`, `parasail`, `edlib`, etc.) em todo o projeto (`core/`, `export/`, `app/`, `web/`, `requirements.txt`): **nenhuma ocorrência**. Os únicos imports em `core/` e `export/` são `re`, `csv`, `io`, `zipfile` e `__future__` (todos stdlib). `app/main.py` importa apenas `fastapi` e os próprios módulos do projeto. `requirements.txt` continua com só `fastapi`, `uvicorn`, `python-multipart`.

## Critérios de aceite do PRD — item a item

| # | Critério (resumo) | Teste(s) | Resultado |
|---|---|---|---|
| 1 | GLOBAL canônico (ACGTAC/ACGTTC, match 2/mismatch -1/gap -2): score 9, marcação `\|\|\|\|.\|`, tamanho 6 | `tests/test_alinhamento.py::TesteCasoCanonicoGlobal` (`test_score_final_e_tamanho`, `test_alinhamento_e_marcacao`); `tests/test_api.py::TesteEndpointAlinhar::test_caso_canonico_devolve_200_e_resultado_do_contrato` | **PASSOU** |
| 2 | Matriz do caso canônico idêntica à seção 9 do contrato; célula `[6][6]`=9; primeira linha/coluna `0,-2,...,-12` | `TesteCasoCanonicoGlobal::test_matriz_identica_a_secao_9_do_contrato`, `test_celula_inferior_direita_vale_9`, `test_primeira_linha_e_primeira_coluna` | **PASSOU** |
| 3 | LOCAL: primeira linha/coluna zeradas, nenhuma célula negativa, score = maior valor da matriz | `tests/test_alinhamento.py::TesteAlinhamentoLocal` (`test_primeira_linha_e_coluna_sao_zero`, `test_nenhuma_celula_negativa`, `test_score_igual_ao_maior_valor_da_matriz`) | **PASSOU** |
| 4 | LOCAL: traceback começa na 1ª célula de valor máximo na varredura (linha a linha, esquerda→direita) e para na 1ª célula zero do caminho | `TesteAlinhamentoLocal::test_inicio_e_a_primeira_celula_de_valor_maximo_na_varredura`, `test_traceback_para_na_primeira_celula_zero_do_caminho` | **PASSOU** |
| 5 | Célula com empate múltiplo: todas as direções aparecem, maiúscula correta (D > V > H) | `tests/test_alinhamento.py::TesteDesempateDentroDaCelula` — inclui um caso real de empate **triplo** (`Dvh`, achado por busca exaustiva em `AACC`×`ACAA`, match=1/mismatch=-1/gap=-1) além de empates duplos (`Dh`, `Dv`) | **PASSOU** |
| 6 | Determinismo: duas execuções idênticas produzem caminho, direções e alinhamento idênticos | `tests/test_alinhamento.py::TesteDeterminismo` (GLOBAL e LOCAL) | **PASSOU** |
| 7 | `ACGTAXTG`: erro 422 com `base_invalida` citando `X` e a posição, sem processar | `tests/test_validacao.py::TesteBaseInvalida`; `tests/test_api.py::TesteEndpointAlinhar::test_base_invalida_devolve_422_sem_processar` | **PASSOU** |
| 8 | Seq2 vazia + Gap não numérico: os DOIS erros na mesma resposta | `tests/test_validacao.py::TesteMultiplosErrosNaMesmaResposta`; `tests/test_api.py::TesteEndpointAlinhar::test_seq2_vazia_e_gap_nao_numerico_juntos` | **PASSOU** |
| 9 | Arquivo `.fasta` com três sequências: erro `seq_quantidade` | `tests/test_arquivos_core.py::TesteQuantidadeDeSequencias`; `tests/test_api.py::TesteEndpointArquivo::test_tres_sequencias_devolve_erro_seq_quantidade` | **PASSOU** |
| 10 | `acgta` × `TGCATG`: normalização para maiúsculas e comprimentos diferentes funcionando | `tests/test_alinhamento.py::TesteNormalizacaoEComprimentosDiferentes`; `tests/test_api.py::TesteEndpointAlinhar::test_normalizacao_de_minusculas_e_comprimentos_diferentes` | **PASSOU** |
| 11 | Match = -1: aviso de consistência presente **e** alinhamento processado mesmo assim | `tests/test_validacao.py::TesteAvisoDeConsistencia`; `tests/test_api.py::TesteEndpointAlinhar::test_match_negativo_gera_aviso_e_processa` | **PASSOU** |
| 12 | Exportação: os 4 arquivos com os nomes exatos do contrato, conteúdo batendo com o resultado da API | `tests/test_export.py` (`TesteNomesDeArquivo`, `TesteConteudoBateComResultadoDaApi`); `tests/test_api.py::TesteEndpointExportar` (`test_exportar_txt`, `test_exportar_csv_pontuacao_bate_com_resultado_da_tela`, `test_exportar_zip_contem_quatro_arquivos`) | **PASSOU** |
| 13 | Sequências acima do limite de exibição (60): CSV de pontuação exportado contém a matriz **completa**, `(m+1)×(n+1)` células | `tests/test_export.py::TesteMatrizCompletaAcimaDoLimiteDeExibicao` (sequências de 80×72 bases) | **PASSOU** |
| 14 | `/api/comparar` devolve GLOBAL e LOCAL sobre a mesma entrada | `tests/test_api.py::TesteEndpointComparar::test_comparar_devolve_global_e_local`; `tests/test_export.py::TesteComparacao` (zip de comparação com sufixo de modo) | **PASSOU** |
| 15 | Script de inicialização sobe a aplicação, acessível no navegador sem passos manuais | `tests/test_subida_servidor.py::TesteSubidaRealDoServidor` — sobe `uvicorn app.main:app` em processo real numa porta TCP livre (o mesmo comando usado na última linha de `run.bat`/`run.sh`) e faz requisições HTTP reais via `urllib` contra `GET /` e `POST /api/alinhar` | **PASSOU** (ver nota abaixo) |

### Nota sobre o critério 15 (script de inicialização)

`run.bat`/`run.sh` foram revisados manualmente (não reescritos): ambos resolvem o diretório do projeto, criam/reutilizam `.venv`, instalam `requirements.txt` e terminam exatamente com `uvicorn app.main:app --host 0.0.0.0 --port 8000`. O teste automatizado não invoca os scripts por inteiro (criar um venv do zero e reinstalar dependências a cada execução da suíte seria lento e desnecessário), mas exercita de fato o comando final que eles executam, em um processo `uvicorn` real escutando em TCP, com requisições HTTP reais — não apenas via `TestClient` ASGI in-process. Isso cobre a parte do critério que é testável sem gastos de tempo desproporcionais; a parte "um comando cria o venv e instala dependências do zero" foi verificada por leitura de código, não por execução cronometrada na suíte.

## Teste de integração HTTP real

`tests/test_api.py` usa `fastapi.testclient.TestClient` (transporte ASGI real, sem mocks) contra a aplicação completa — `POST /api/alinhar`, `POST /api/comparar`, `POST /api/arquivo`, `POST /api/exportar/{formato}` (todos os seis formatos) e os estáticos (`GET /` e os assets referenciados por ele). `tests/test_subida_servidor.py` complementa com um processo `uvicorn` real em porta TCP, conforme a nota acima.

### Nota sobre o teste de estáticos (pós-migração do front-end)

O front-end foi migrado de HTML/CSS/JS puro para **React + TypeScript + Tailwind + shadcn/ui** (código-fonte em `frontend/`, build via Vite). O bundle gerado por `npm run build` é versionado em `web/` e nomeia seus arquivos com hash de conteúdo (`/assets/index-<hash>.js`, `/assets/index-<hash>.css`), que muda a cada rebuild. Por isso `TesteEstaticos::test_arquivos_estaticos_servidos_na_raiz`, que pedia `/app.js`, `/estilo.css` e `/config.js` (nomes do front antigo), foi substituído por `test_assets_referenciados_pelo_html_sao_servidos`: o teste faz `GET /`, extrai do próprio HTML servido os caminhos em `src`/`href`, e confirma que cada um responde 200 com content-type condizente com sua extensão. Assim o teste verifica o critério (o HTML e tudo que ele referencia são servidos) em vez de nomes de arquivo específicos, e continua válido depois de qualquer rebuild do front.

## Itens em aberto

Nenhum. Todos os 15 critérios de aceite do PRD passaram sem necessidade de correção em `core/`, `export/`, `app/` ou `web/`. A suíte inteira (`python -m pytest tests/`) termina **verde**: 52 passed.
