# Correção de sincronização numérica do artigo

Esta branch corrige a divergência entre o artigo e os JSONs vivos do experimento.

## Escopo

- deduplicar `SNAPSHOT_ETAPA_1` por `linha_planilha` antes da calibração, mantendo a ocorrência mais recente;
- regenerar os agregados de calibração, auditoria, avaliação final, estatística e sensibilidade;
- atualizar Resumo, Abstract, Tabelas 1 a 4, Discussão, Limitações e Considerações Finais a partir dos JSONs vigentes;
- corrigir contradições editoriais remanescentes;
- regenerar as Figuras 2 e 3 e, após o merge, o PDF do artigo.

## Segurança

O fluxo é somente leitura na planilha. Nenhuma coluna ou célula da base viva é alterada.
