# `dados/` — arquivos privados e intermediários

Esta pasta é reservada a caches, snapshots, estados de automação e artefatos intermediários usados pelos scripts e workflows.

Ela não deve ser confundida com `docs/dados/`, que contém somente resultados agregados e sanitizados destinados ao painel público e ao artigo.

## Conteúdo esperado

Podem existir nesta pasta:

- caches temporários da planilha;
- snapshots usados para reprodutibilidade;
- estados de automação e controle de avanço;
- artefatos de treino e avaliação;
- relatórios intermediários que não devem ser publicados.

A presença e o esquema desses arquivos dependem do workflow que os gerou. O código deve localizar colunas por cabeçalho e validar o esquema antes de processar dados.

## Regras de segurança

1. Não versionar credenciais, IDs privados, tokens ou chaves de conta de serviço.
2. Não publicar títulos, descrições ou outros textos livres dos chamados.
3. Respeitar o `.gitignore` e revisar qualquer novo arquivo antes de adicioná-lo ao Git.
4. Preservar as colunas de conferência humana, especialmente M, N, P e Q.
5. Não tratar cache ou snapshot antigo como fonte atual sem conferir a data de geração.

## Escrita na planilha

Toda escrita na planilha viva deve exigir opção explícita, como `--aplicar`. Quando houver risco de alteração ampla, executar e registrar um dry-run antes da aplicação.

Rotinas que escrevem devem:

- usar gravação em lote;
- preservar valores humanos e campos fora do escopo;
- registrar quantidade de linhas lidas, alteradas, ignoradas e restringidas;
- remover arquivos locais de credencial ao final, inclusive em caso de falha.

## Publicação

Somente resultados agregados, sem texto identificável de chamados, podem ser copiados para `docs/dados/`.

Os arquivos públicos devem registrar, quando aplicável:

- data de geração;
- script ou workflow de origem;
- denominador analisado;
- natureza da métrica;
- limitações do recorte.

## Fonte de verdade

A planilha é a fonte operacional dos chamados e das conferências humanas. Os JSONs versionados são fotografias derivadas e devem ser interpretados pelos respectivos timestamps, escopo e denominadores.
