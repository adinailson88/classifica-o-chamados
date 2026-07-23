# AGENTS.md - classificacao-chamados

## Regime de trabalho

Atuar em modo tecnico, objetivo e verificavel. Nao presumir dados da planilha sem leitura direta.

Quando houver insuficiencia de dados, declarar exatamente: `Informação insuficiente para verificar.`


## Pendencia inicial para novas sessoes

Ao iniciar uma nova sessao, verificar se existe docs/CODEX_PROXIMA_SESSAO.md.

Se existir, ler o arquivo antes de alterar qualquer coisa e perguntar ao Adinailson se deseja tratar a pendencia registrada.

Nao avancar para outros repositorios sem confirmacao explicita.

## Trabalho no artigo/capitulo da tese

Sempre que o pedido for sobre o artigo/capitulo de classificacao de chamados (redigir,
revisar estrutura, atualizar numeros, preparar submissao), ler `PLANO_ARTIGO_CAPITULO.md`
antes de escrever qualquer texto. Esse arquivo tem a estrutura fixa do artigo mapeada as
fontes de dado do repo e o bloco "Estado desta rodada" com onde a redacao parou. Ao
terminar a rodada, substituir esse bloco (nao acrescentar sem criterio) com: onde esta,
o que foi feito, proximo passo. Nao criar arquivo novo de plano/rascunho para essa
finalidade.

## Escopo do repositorio

Este repositorio implementa um experimento independente de classificacao e reclassificacao automatica de chamados, conforme roteiro metodologico do Malha IA.

O projeto nao deve alterar o repositorio operacional `malha-ia` nem seus workflows. Scripts aqui devem ser novos, ainda que possam consultar padroes tecnicos ja existentes.

## Regras da planilha experimental

1. A planilha principal vai de `A:M`.
2. As colunas devem ser localizadas por cabecalho, nao por posicao fixa herdada.
3. Linhas totalmente vazias devem ser ignoradas.
4. O total de linhas deve ser dinamico; o script nao deve assumir quantidade fixa.
5. A leitura deve considerar crescimento futuro da planilha.
6. Escritas na planilha so podem ocorrer quando o comando tiver flag explicita de aplicacao.

## Colunas esperadas

```text
ID Chamado
TÍTULO
CATEGORIA COMPLETA
DESCRIÇÃO GLPI
TÍTULO O.S.M.
DESCRIÇÃO O.S.M.
Classificação IA
Avaliação (%)
Executor
Criticidade Atribuída por IA
Comparação
Classificado_Confiança_IA
CONFERÊNCIA
```

## Validacao

Validar sintaxe Python com:

```bash
python -m py_compile src/validar_planilha_experimento.py
```

Nao declarar acesso a Google Sheets como validado sem execucao real com credenciais.

