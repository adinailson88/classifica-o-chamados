# Plano — Artigo/Capítulo “Classificação Automática de Chamados”

Este documento registra somente a estrutura, os critérios editoriais e o estado atual do artigo/capítulo. O histórico das rodadas anteriores permanece nos commits e Pull Requests.

Atualizado em 28/07/2026, no fuso America/Bahia.

## Regra de uso

Antes de alterar o artigo:

1. ler `CONTEXTO.md`, este plano e `04_artigo/README.md`;
2. conferir os timestamps e denominadores dos JSONs utilizados;
3. não reaproveitar números de rodadas antigas sem revalidação;
4. ao concluir uma rodada, substituir a seção “Estado desta rodada”, sem acumular histórico.

## Escopo científico

O artigo avalia a classificação automática de chamados de manutenção predial em português brasileiro como camada de estruturação de dados para governança preditiva da infraestrutura pública.

A análise distingue três objetos:

- concordância entre a classificação automática e a categoria administrativa histórica;
- acerto contra a decisão validada pela conferência humana;
- reclassificação e identificação de problemas na taxonomia histórica.

O texto deve tratar a categoria histórica como referência administrativa, não como verdade absoluta.

## Estrutura do artigo

1. Introdução.
2. Referencial conceitual.
3. Método.
4. Resultados.
5. Discussão e limitações.
6. Considerações finais.
7. Declarações e referências.

A fonte editável é `04_artigo/artigo_classificacao_chamados_v3.md`. O PDF publicado fica em `docs/artigo_classificacao_chamados.pdf`.

## Fontes canônicas

| Assunto | Fonte |
|---|---|
| Resultado validado por modelo | `docs/dados/avaliacao_final.json` |
| Comparação estatística | `docs/dados/estatistica.json` |
| Calibração e faixas de confiança | `docs/dados/calibracao.json` e `docs/dados/calibracao_ajustada_modelos.json` |
| Estado do BERTimbau | `docs/dados/bertimbau_training_state.json` e `docs/dados/bertimbau_metr_full.json` |
| Figuras e tabelas derivadas | scripts em `src/` e JSONs em `docs/dados/` |
| Regras operacionais | `AGENTS.md`, `README.md` e `CONTEXTO.md` |

## Critérios editoriais

- Toda afirmação teórica deve ter referência bibliográfica adequada.
- Datas de execução, IDs de workflow, caminhos internos e linguagem de relatório técnico não devem aparecer no corpo científico, salvo quando metodologicamente indispensáveis.
- Resultados estatísticos detalhados devem permanecer em material suplementar quando não forem necessários à interpretação principal.
- Números repetidos no Resumo, Abstract, tabelas, figuras, resultados, discussão e conclusão devem ser atualizados em conjunto.
- O BERTimbau é apresentado em subseção própria (holdout comum de oito modelos) e não é inserido artificialmente no ranking integral dos sete modelos, por não possuir predições *out-of-fold* sobre toda a base.
- O PDF deve ser regenerado e revisado visualmente após qualquer alteração estrutural ou numérica.

## Estado desta rodada

**Onde está:** o artigo permanece cientificamente fechado, com resultados e conclusões inalterados. A redação metodológica foi revisada para retirar do corpo científico os identificadores internos das colunas de conferência da planilha.

**O que foi feito:** as referências a M/N/P/Q e à categoria manual Q foram substituídas, apenas no artigo, por categorias conceituais de decisão: confirmação da categoria histórica, aceitação da classificação automática, aceitação da reclassificação, definição manual de categoria alternativa e categoria de referência validada. Nenhum dado, cálculo, denominador, resultado, regra operacional da planilha ou código de processamento foi alterado. O PDF público foi regenerado a partir da fonte Markdown revisada.

**Próximo passo:** preencher a categoria manual Q dos 639 casos restritos (201 deles em conflito) e avaliar a viabilidade de uma execução *out-of-fold* integral do BERTimbau sobre toda a base.

## Critérios para fechamento

A rodada científica foi considerada fechada porque:

1. os JSONs canônicos (`avaliacao_final.json`, `avaliacao_bertimbau_holdout.json`, `estatistica.json`) têm denominadores reconciliados (8.895 decisões integrais; 639 casos no holdout comum);
2. a avaliação held-out do BERTimbau está documentada em subseção própria, separada do ranking integral dos sete modelos;
3. Resumo, Abstract, tabelas, figuras e conclusões estão coerentes entre si;
4. as referências bibliográficas (incluindo DEVLIN *et al.*, 2019 e SOUZA; NOGUEIRA; LOTUFO, 2020) foram conferidas;
5. o PDF final foi gerado e revisado visualmente.

## Registro histórico

Planos concluídos, auditorias antigas, números substituídos e decisões de implementação devem ser consultados no histórico do Git e nos Pull Requests. Eles não devem voltar a ser acumulados neste arquivo.
