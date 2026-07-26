# Correção de sincronização numérica do artigo

Esta branch corrige a divergência entre o artigo e os JSONs vivos do experimento.

## Escopo

- deduplicar `SNAPSHOT_ETAPA_1` por `linha_planilha` antes da calibração, mantendo a ocorrência mais recente;
- regenerar os agregados de calibração, auditoria, avaliação final, estatística e sensibilidade;
- atualizar Resumo, Abstract, Tabelas 1 a 4, Discussão, Limitações e Considerações Finais a partir dos JSONs vigentes;
- corrigir contradições editoriais remanescentes;
- regenerar as Figuras 2 e 3 e, após o merge, o PDF do artigo.

## Estado validado na execução

- corpus deduplicado: 13.965 chamados;
- duplicatas removidas do snapshot append-only: 4.500;
- chamados com alguma conferência: 9.534;
- decisões travadas: 9.044;
- casos sem verdade validada: 490, incluindo 52 conflitos.

Os valores acima são gerados novamente pelo workflow antes da sincronização do texto, não inseridos manualmente no artigo. A regeneração estatística requer `statsmodels`, e as figuras requerem `matplotlib`; ambas as dependências são instaladas explicitamente no workflow corretivo.

## Segurança

O fluxo é somente leitura na planilha. Nenhuma coluna ou célula da base viva é alterada.
