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
- O BERTimbau só pode entrar nas comparações após treino concluído, artefatos verificáveis e protocolo compatível com os demais modelos.
- O PDF deve ser regenerado e revisado visualmente após qualquer alteração estrutural ou numérica.

## Estado desta rodada

**Onde está:** a reformulação editorial foi incorporada e o artigo está publicado. A próxima atualização é numérica e metodológica, não uma nova reescrita estrutural.

**O que foi feito:** a documentação acumulada foi reduzida; workflows manuais substituídos ou redundantes foram removidos; o orquestrador temporário do BERTimbau e o prompt correspondente no README foram eliminados. A pendência do modelo passou a ser registrada somente nos documentos de estado.

**Bloqueadores atuais:**

- `docs/dados/bertimbau_training_state.json` permanece sem resultado concluído verificável;
- `avaliacao_final.json`, `estatistica.json` e `calibracao.json` precisam representar a mesma cadeia de geração antes de serem usados como fotografia única;
- qualquer atualização numérica deve ser integral, não tabela a tabela.

**Próximo passo:** decidir entre executar diretamente `transformer_ft.yml` em protocolo controlado ou documentar a exclusão definitiva do BERTimbau. Se houver treino, validar seus artefatos antes de disparar separadamente avaliação, estatística e consolidação. Somente depois reconciliar artigo, figuras, tabelas e PDF.

## Critérios para fechamento

A rodada científica poderá ser considerada fechada quando:

1. os JSONs canônicos tiverem timestamps e denominadores reconciliados;
2. a inclusão ou exclusão definitiva do BERTimbau estiver documentada;
3. Resumo, Abstract, tabelas, figuras e conclusões estiverem coerentes entre si;
4. as referências bibliográficas tiverem sido integralmente conferidas;
5. o PDF final tiver sido gerado e revisado visualmente.

## Registro histórico

Planos concluídos, auditorias antigas, números substituídos e decisões de implementação devem ser consultados no histórico do Git e nos Pull Requests. Eles não devem voltar a ser acumulados neste arquivo.
