# Artigo — classificação automática de chamados

Este diretório contém o texto científico associado ao experimento de classificação e reclassificação de chamados de manutenção predial.

## Arquivos oficiais

| Arquivo | Função |
|---|---|
| `artigo_classificacao_chamados_v3.md` | Fonte editável e versionada do artigo/capítulo |
| `artigo_classificacao_chamados_v3.docx` | Arquivo original preservado como referência de proveniência e formatação |
| `figuras/` | Figuras vetoriais e imagens em 300 dpi geradas pelos scripts do repositório |
| `referencias/` | Fichas analíticas e links para o acervo bibliográfico |
| `../docs/artigo_classificacao_chamados.pdf` | PDF publicado no GitHub Pages |

PDF público: <https://adinailson88.github.io/classificacao-chamados/artigo_classificacao_chamados.pdf>

## Geração do PDF

O workflow `.github/workflows/artigo_pdf.yml` converte o Markdown em PDF e publica o resultado em `docs/`. Ele não acessa a planilha nem substitui automaticamente números no corpo do texto.

As figuras são geradas a partir dos JSONs versionados em `docs/dados/`. Para regenerá-las, use os scripts `src/gerar_figura*.py` e as tarefas correspondentes do workflow `lstm_artigo.yml`.

## Regra para atualização de resultados

Os dados do painel são dinâmicos. Antes de alterar números ou conclusões no artigo:

1. conferir os timestamps e denominadores dos JSONs utilizados;
2. garantir que `avaliacao_final.json`, `estatistica.json` e `calibracao.json` representam a mesma rodada;
3. atualizar em conjunto Resumo, Abstract, tabelas, figuras, resultados, discussão e conclusão;
4. regenerar o PDF e revisar visualmente a paginação.

Não atualizar uma tabela isoladamente quando o mesmo resultado aparece em outras partes do texto.

## Estado atual

- O BERTimbau permanece fora das comparações finais porque `docs/dados/bertimbau_training_state.json` está com `status=sem_dados`.
- `avaliacao_final.json` e `calibracao.json` apresentam denominadores diferentes por terem sido gerados em horários distintos. Eles devem ser reconciliados antes da próxima atualização numérica do artigo.
- O histórico detalhado das rodadas editoriais e técnicas permanece no Git e nos Pull Requests; não deve ser acumulado neste README.