# 04_artigo — rascunho do artigo/capítulo

Réplica do padrão usado em `revisao-bibliografica` (ver `PLANO_ARTIGO_CAPITULO.md`,
Seção 2): o texto do artigo/capítulo passa a morar dentro deste repositório, sob
controle de versão.

## Arquivos

- `artigo_classificacao_chamados_v3.docx` — rascunho original, trazido de fora do
  git em 2026-07-23 (fonte: `Downloads/artigo_classificacao_chamados_v3.docx`,
  datado de 2026-07-16). Mantido como referência binária/formatação.
- `artigo_classificacao_chamados_v3.md` — conversão via `pandoc -t markdown` do
  docx acima, feita em 2026-07-23. Nesta mesma data, a estrutura de títulos foi
  realinhada à estrutura fixa de `PLANO_ARTIGO_CAPITULO.md` (Seção 2 renomeada
  para "Referencial conceitual", Seção 3 para "Método" com nova Subseção 3.9
  "Disponibilidade de dados e scripts", nova Subseção 4.8 "Figuras" destacada do
  texto que já existia em 4.7, Seção 6 renomeada para "Considerações finais", e
  Apêndices A–C acrescentados ao final). **Nenhum parágrafo de conteúdo já escrito
  foi reescrito ou teve números alterados** — só títulos, numeração e três blocos
  novos que eram exigidos pela estrutura do plano e ainda não existiam (Apêndice A
  é fatual, extraído de `AGENTS.md`; Apêndices B e C ficam marcados como
  pendência explícita, sem conteúdo inventado). O `.docx` original **não foi
  alterado** — permanece como registro de proveniência.

## Estado atual (após a reformulação editorial enxuta)

Estrutura: Resumo/Abstract → 1. Introdução → 2. Referencial conceitual (2.1–2.4) →
3. Método (3.1–3.9) → 4. Resultados (4.1–4.9) → 5. Discussão (com Limitações) →
6. Considerações finais → Declarações → Referências. **Sem apêndices.**

Extensão: ~12.100 palavras, 22 páginas no formato do workflow de PDF.

O que a rodada de reformulação fez:

- Removeu o ruído técnico do texto (colunas de planilha, executores, "Etapa 1
  oficial", rematerialização, JSON, painel). Termos internos foram substituídos
  por linguagem de artigo: "classificação automática em produção" e "decisão
  validada pela conferência humana".
- Eliminou a subseção 4.8 "Figuras". As seis figuras passaram para as subseções
  onde o resultado é discutido, e as antigas 4.9/4.10 viraram 4.8/4.9.
- Removeu os Apêndices A (checklist) e B (matriz M/N/P), e as citações à Tabela
  Suplementar S4, cujo arquivo nunca foi gerado.
- Condensou Limitações e Considerações Finais em três parágrafos cada.

### Figuras

As seis figuras são geradas por script a partir de JSON versionado, em **PDF
vetorial** (usado pelo build) e **PNG a 300 dpi** (submissão), com paleta
Okabe-Ito. O estilo comum vive em `src/estilo_figuras.py`. A numeração dos
arquivos acompanha a ordem de leitura (`fig3_top_confusoes`,
`fig4_tradeoff_custo`). Para regerar tudo, use a tarefa `figuras_artigo` do
workflow `lstm_artigo.yml` ou rode os seis `src/gerar_figura*.py`.

### Pendências que permanecem

- **8º modelo (BERTimbau)**: sem treino concluído; declarado no texto como
  extensão planejada e excluído de todas as comparações.
- **Referências**: a auditoria de 2026-07-16 encontrou 1 erro de autoria e 1
  inconsistência de ano. A lista ainda não foi integralmente reconferida.
- **Números congelados em n = 9.096.** O artigo descreve um recorte da
  conferência humana. Os JSONs vigentes já registram cobertura maior, então
  qualquer atualização de números precisa ser feita no artigo inteiro de uma vez,
  não tabela a tabela.
- Os números do Resumo e do Abstract foram conferidos contra as Tabelas 1 e 2 e
  batem. O Abstract em inglês trazia valores anteriores ao reprocessamento dos
  modelos (79.89% e 74.71%) e foi corrigido.
