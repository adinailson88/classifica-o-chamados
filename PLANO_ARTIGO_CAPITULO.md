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

**Onde está:** o artigo ganhou uma subseção de resultados e teve os números reconciliados com os JSONs canônicos vigentes. A conferência humana cobre o corpus integral, de modo que a limitação de recorte amostral deixou de existir.

**O que foi feito:** acrescentou-se a Subseção 4.11, que recorta o desempenho por volume de categoria, mediante curva ABC, e por natureza da manutenção, em três tipos. As Tabelas 8, 9 e 10 são novas, assim como a Tabela A2 do Apêndice A, que discrimina as 56 categorias da referência validada com marcação P, C ou NM e classe ABC interna ao tipo. A Subseção 5.4 passou a declarar a ordem de incorporação da camada classificada a indicadores institucionais, decorrente da hierarquia de confiabilidade medida. Os números do corte foram atualizados após a correção, no GLPI, da categoria raiz `Manutenção Preventiva`: acerto validado do LinearSVC de 0,8197, F1 macro de 0,5523, Cochran Q de 2448,55 e 56 categorias com suporte na referência. O Kappa de Cohen, desatualizado desde rodada anterior, passou a 0,7902 a 0,6694, e a afirmação de que ele reproduzia a mesma ordenação da acurácia foi corrigida, porque há duas trocas de posição.

**Próximo passo:** avaliar a viabilidade de uma execução *out-of-fold* integral do BERTimbau sobre toda a base e considerar validação externa em outra instituição.

## Critérios para fechamento

A rodada científica foi considerada fechada porque:

1. os JSONs canônicos (`avaliacao_final.json`, `avaliacao_bertimbau_holdout.json`, `estatistica.json`) têm denominadores reconciliados (8.895 decisões integrais; 639 casos no holdout comum);
2. a avaliação held-out do BERTimbau está documentada em subseção própria, separada do ranking integral dos sete modelos;
3. Resumo, Abstract, tabelas, figuras e conclusões estão coerentes entre si;
4. as referências bibliográficas (incluindo DEVLIN *et al.*, 2019 e SOUZA; NOGUEIRA; LOTUFO, 2020) foram conferidas;
5. o PDF final foi gerado e revisado visualmente.

## Registro histórico

Planos concluídos, auditorias antigas, números substituídos e decisões de implementação devem ser consultados no histórico do Git e nos Pull Requests. Eles não devem voltar a ser acumulados neste arquivo.
