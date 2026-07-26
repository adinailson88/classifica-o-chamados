## Problema

O artigo permaneceu com métricas da consolidação anterior, enquanto os JSONs vivos passaram a registrar 9.070 decisões avaliáveis, 26 conflitos e novos valores por modelo. O `calibracao.json` também somava duplicatas do snapshot append-only.

## Correção

- deduplicação defensiva por `linha_planilha` na calibração;
- regeneração dos agregados somente leitura;
- sincronização automatizada do artigo com os JSONs vigentes;
- correção do Abstract e de contradições editoriais;
- regeneração das Figuras 2 e 3.

## Validação esperada

- `python -m py_compile` nos novos scripts;
- `python -m unittest discover -s tests`;
- `python src/check_final_ready.py`;
- geração do PDF pelo workflow existente após o merge.
