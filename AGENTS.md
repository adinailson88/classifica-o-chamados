# AGENTS.md - classificacao-chamados

## Regime de trabalho

Atuar em modo tecnico, objetivo e verificavel. Nao presumir dados da planilha sem leitura direta.

Quando houver insuficiencia de dados, declarar exatamente: `Informação insuficiente para verificar.`

## Pendencia inicial para novas sessoes

Ao iniciar uma nova sessao, verificar se existe `docs/CODEX_PROXIMA_SESSAO.md`.

Se existir, ler o arquivo antes de alterar qualquer coisa e perguntar ao Adinailson se deseja tratar a pendencia registrada.

Nao avancar para outros repositorios sem confirmacao explicita.

## Trabalho no artigo/capitulo da tese

Sempre que o pedido for sobre o artigo/capitulo de classificacao de chamados, ler `PLANO_ARTIGO_CAPITULO.md` antes de escrever. Ao terminar a rodada, substituir o bloco "Estado desta rodada" com o ponto atual, o que foi feito e o proximo passo. Nao criar planos paralelos para a mesma finalidade.

## Escopo do repositorio

Este repositorio implementa um experimento independente de classificacao e reclassificacao automatica de chamados, conforme roteiro metodologico do Malha IA.

O projeto nao deve alterar o repositorio operacional `malha-ia` nem seus workflows.

## Regras da planilha experimental

1. A planilha principal vigente vai de `A:Q`.
2. As colunas devem ser localizadas por cabecalho, nao por posicao fixa herdada.
3. Linhas totalmente vazias devem ser ignoradas.
4. O total de linhas deve ser dinamico; nenhum script pode assumir quantidade fixa.
5. Escritas na planilha exigem flag explicita de aplicacao e dry-run anterior reportado.
6. Nunca apagar ou sobrescrever as conferencias humanas M, N e P nem a categoria manual Q.
7. A verdade validada deve ser derivada por `src/decisao_validada.py`.
8. A memoria de treino validada deve usar apenas decisoes nao contraditorias de M/N/P/Q.

## Colunas esperadas

```text
A  ID Chamado
B  TÍTULO
C  CATEGORIA COMPLETA
D  DESCRIÇÃO GLPI
E  TÍTULO O.S.M.
F  DESCRIÇÃO O.S.M.
G  Classificação IA
H  Avaliação (%)
I  Executor
J  Criticidade Atribuída por IA
K  Comparação
L  Classificado_Confiança_IA
M  CONFERÊNCIA GLPI
N  CONFERÊNCIA IA
O  Classificação IA - 2
P  CONFERÊNCIA IA - 2
Q  CATEGORIA CORRETA MANUAL
```

A coluna Q só deve ser preenchida quando M, N e P não confirmarem nenhuma categoria como correta. Conflitos devem retornar para revisão humana.

## Validacao

Antes de cada commit de codigo, executar:

```bash
python -m unittest discover -s tests
python -m py_compile src/*.py
```

Nao declarar acesso ao Google Sheets como validado sem execucao real com credenciais.
