# 04_artigo — rascunho do artigo/capítulo

Réplica do padrão usado em `revisao-bibliografica` (ver `PLANO_ARTIGO_CAPITULO.md`,
Seção 2): o texto do artigo/capítulo passa a morar dentro deste repositório, sob
controle de versão.

## Arquivos

- `artigo_classificacao_chamados_v3.docx` — rascunho original, trazido de fora do
  git em 2026-07-23 (fonte: `Downloads/artigo_classificacao_chamados_v3.docx`,
  datado de 2026-07-16). Mantido como referência binária/formatação.
- `artigo_classificacao_chamados_v3.md` — conversão via `pandoc -t markdown` do
  docx acima, feita em 2026-07-23, para permitir diff e edição em texto puro daqui
  em diante. Nenhum conteúdo foi reescrito na conversão.

## Estado conhecido do rascunho v3 (herdado, não revisado nesta rodada)

Estrutura: Resumo/Abstract → 1. Introdução → 2. Trabalhos relacionados (2.1–2.4) →
3. Materiais e métodos (3.1–3.8) → 4. Resultados (4.1–4.7) → 5. Discussão →
6. Conclusão.

Pendências já registradas no próprio rascunho e/ou em `PLANO_ARTIGO_CAPITULO.md`:

- **Números do Resumo (LinearSVC 80,26%, LSTM 67,57% de concordância) não foram
  revalidados nesta rodada.** Antes de citar em qualquer nova escrita, reconferir
  contra `docs/dados/avaliacao_final.json` e demais JSONs vigentes — os dados
  mudam a cada execução de workflow (ver regra em `PLANO_ARTIGO_CAPITULO.md` e na
  skill `artigo-metodologia-biossistemas`).
- **4 figuras não regeneradas** (o `.md` convertido não tem imagens embutidas — a
  seção 3.2/Figura 1 e as figuras de resultados citam geração pendente a partir dos
  JSONs do painel).
- **8º modelo (BERTimbau)**: resultado comparativo ainda não existe no rascunho.
- **Referências**: a auditoria de 2026-07-16 já encontrou 1 erro de autoria e 1
  inconsistência de ano — não aceitar a lista de referências do v3 como validada
  sem reconferência.
- Conferência humana M/N/P: no rascunho, os números de "acerto validado" refletem o
  estado da conferência na data de redação (16/07 ou antes) — reconferir estado
  atual antes de qualquer atualização.

Este README não altera o texto do artigo; apenas documenta a proveniência e o que
ainda falta confirmar antes de tratar este rascunho como fonte de números
publicáveis.
