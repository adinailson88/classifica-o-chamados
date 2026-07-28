# Workflows manuais isolados

Os arquivos `.yml` desta pasta não são executados pelo GitHub Actions. O GitHub reconhece workflows apenas quando estão diretamente em `.github/workflows/`.

Os workflows isolados foram removidos porque duplicavam fluxos ativos, preservavam arquiteturas legadas ou permitiam operações incompatíveis com a política atual de proteção das conferências humanas.

Operações vigentes devem ser executadas exclusivamente pelos workflows ativos documentados em `docs/dados/workflows_index.json`.

## Regras

1. Não arquivar workflows obsoletos nesta pasta.
2. Novas operações devem nascer em branch e Pull Request, com dry-run por padrão quando houver escrita na planilha.
3. Preservar as colunas M, N, P e Q e localizar colunas por cabeçalho.
4. Rotinas destrutivas não devem ser mantidas como contingência permanente.

O histórico dos workflows removidos permanece disponível nos commits e Pull Requests do repositório.
