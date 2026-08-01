# Contexto para continuar em outro chat — 01/08/2026

Cole o bloco abaixo inteiro no início da conversa nova.

---

## PROJETO

Repositório `adinailson88/classificacao-chamados` (público). Experimento de doutorado (PPG Biossistemas/UFSB) que compara IAs locais na classificação de chamados de manutenção predial da UFSB, com validação humana. Produtos: painel em GitHub Pages (`docs/index.html`) e artigo (`04_artigo/artigo_classificacao_chamados_v3.md`, PDF em `docs/artigo_classificacao_chamados.pdf`).

Pipeline: Google Sheets (aba `CHAMADOS_ESQUELETO_REDUZIDO`) → GitHub Actions → JSONs em `docs/dados/` → painel e artigo. Nenhum dado sensível vai para o GitHub.

## ANATOMIA DA PLANILHA — indispensável

| Colunas | Natureza | Observação |
|---|---|---|
| A–F (ID Chamado, Título, `CATEGORIA COMPLETA`, Descrições) | **FÓRMULA** (`IMPORTRANGE`) | Espelham outra planilha. **NUNCA escrever** — quebra o spill da aba inteira (incidente de 25/07/2026) |
| G, H, I, J (Classificação IA, Avaliação %, Executor, Criticidade) | valor literal | Saída da Etapa 1, modelo de **produção** (LSTM+RF) |
| K, L | **FÓRMULA** | K = `=SE(G2="";"";G2=C2)`; reaplicada sozinha pela Etapa 1 |
| M (`CONFERÊNCIA GLPI`), N (`CONFERÊNCIA IA`), O (`Classificação IA - 2`), P, Q (`CATEGORIA CORRETA MANUAL`) | valor literal | Conferência humana e BERTimbau |

**Regra de ouro aprendida em 01/08:** indexar SEMPRE por `id_chamado`, NUNCA por número de linha. A fonte do IMPORTRANGE foi redefinida em 28/07 e reordenou as linhas — 10.410 de 14.094 divergiam do histórico. Escrever indexado por linha grava no chamado errado (foi cometido e corrigido nesta sessão).

## ESTADO ATUAL — números vigentes

- Base: **14.094 chamados** (era 13.965 antes da redefinição do IMPORTRANGE)
- Verdade validada: **9.305** (`M='Correto'` → categoria do GLPI; `M='Errado'` + Q preenchida → Q)
- Pendentes: **242** (GLPI errado, coluna Q ainda vazia) — é a fila de trabalho do pesquisador
- Conflitos: **0**

Acerto validado (n = 9.305), de `docs/dados/avaliacao_final.json`:

| modelo | acerto | IC95% |
|---|---|---|
| linear_svc | 0,8394 | 0,8318–0,8465 |
| extra_trees | 0,8262 | 0,8186–0,8335 |
| random_forest | 0,8202 | 0,8120–0,8277 |
| regressao_logistica | 0,8078 | 0,7995–0,8158 |
| sgd | 0,8060 | 0,7976–0,8141 |
| lstm | 0,7405 | 0,7309–0,7490 |
| naive_bayes | 0,7366 | 0,7278–0,7455 |

BERTimbau (`transformer_ft`) aparece em 1º na matriz de confusão com 0,8419, **mas não é comparável**: a predição dele vem da coluna O, preenchida preferencialmente sobre chamados já validados, enquanto os sete acima são *out-of-fold* sobre a base inteira. É vantagem de protocolo. **O LinearSVC é o número defensável.**

## O QUE MUDOU NESTA SESSÃO (01/08/2026)

1. **Reprocessamento completo** após mesclagem de categorias no GLPI: mapa canônico corrigido (PR #126), abas `CLASSIF__` zeradas e rematerializadas — 98.658 predições, 7 modelos × 14.094, OOF k-fold 5.
2. **BERTimbau retreinado** (4 épocas, 2h35) — 1.927 reclassificados na coluna O, acerto 84,6% contra 53,1% da IA original.
3. **Coluna N aposentada.** Ela conferia UMA IA (a de produção, coluna G) e não representa um experimento com 8 modelos. A verdade passou a ser derivada só de M + Q. Efeito: validados de 1.927 → **9.305**, conflitos de 7.469 → **0**.
4. **Aba `CONFERENCIA_MULTIMODELO`** criada (9.547 linhas): por chamado, a predição e a conferência de cada um dos 8 modelos, derivadas mecanicamente.
5. **Matriz de confusão por IA** no painel, aba "Matriz de confusao". Atualiza sozinha a cada 6 h.
6. **Coluna G realinhada**: `C == G` de 9,1% → **91,9%**.
7. **Artigo sincronizado** com os JSONs vigentes.

## ARQUIVOS-CHAVE CRIADOS/ALTERADOS HOJE

| Arquivo | Papel |
|---|---|
| `src/conferencia_derivada.py` | Deriva conferência de cada IA de M+Q; gera a aba e 2 JSONs |
| `src/matriz_confusao_multimodelo.py` | Matriz de confusão esparsa por modelo |
| `src/sincronizar_numeros_artigo.py` | Sincroniza números do artigo; **aborta** se um trecho não casar; idempotente |
| `src/decisao_validada.py` | Ganhou `so_conferencia_glpi=True` (ignora N e P) |
| `src/avaliacao_final.py` | Ganhou `--verdade glpi` (padrão) |
| `scripts/migracoes/restaurar_coluna_o.py` | Restaura coluna O do `RECLASS_HISTORICO`, por ID |
| `scripts/migracoes/verificar_alinhamento_linhas.py` | Diagnóstico read-only de alinhamento |
| `scripts/migracoes/dump_amostra_planilha.py` | Dump read-only: cabeçalho, fórmulas, taxas C==G / C==O |
| `scripts/migracoes/auditar_abas_planilha.py` | Auditoria de custo em células por aba |

## PENDÊNCIA ABERTA

**Teto de 10 milhões de células do Google Sheets.** Auditoria mediu 9.008.123 alocadas (90,1%) para 7.427.340 usadas — **1.580.783 de desperdício**. Detalhes no `CONTEXTO.md`, item 0.1. Resumo:

- **Não há lixo relevante**: só 2 abas órfãs, 84 mil células (0,8%). Apagar não resolve.
- O ganho está em **redimensionar a grade alocada**, sem apagar dado. Piores: `COMPARACAO_MODELOS` (260.000 alocadas para 1.313 usadas), `CLASSIF__transformer_ft` (220.000 para 11), `CONTROLE_CLASSIFICACAO_2` (180.000 para 261), `RECLASS_VALIDADOS` (260.000 para 50.115), `VALIDACAO_HUMANA` e `LOG_TURNOS_RECLASSIFICACAO` (alocadas e vazias).
- **NÃO APAGAR** `BACKUP_ETAPA1_20260726_131413` nem `BACKUP_ETAPA1_20260801_162324` — são fontes de recuperação.
- `RECLASS_HISTORICO` ocupa 2,7 milhões (30% do total). Compactar liberaria ~2,3 milhões, **mas só depois de exportar o histórico completo** — foi essa trilha que permitiu recuperar a coluna O.

Ferramenta pronta: workflow `auditar_abas_planilha.yml` (read-only, reexecutável).

## AUTOMAÇÃO ATIVA

Todos os workflows de escrita estão habilitados. O `conferencia_derivada.yml` roda a cada 6 h: relê a planilha, regrava a aba `CONFERENCIA_MULTIMODELO`, o resumo e a matriz de confusão, e o Pages republica. **Conforme a coluna M for conferida e a Q preenchida, os números do painel e a base de 9.305 crescem sozinhos.**

## REGRAS DO PROJETO

- Artigo: **só dados e números mudam**. Não alterar estrutura nem reescrever seções. Nunca narrar auditorias, rodadas anteriores ou versões descartadas — artigo não é relatório de processo.
- Toda escrita na planilha: dry-run antes, `--aplicar` explícito depois.
- Preservar sempre as colunas de conferência humana M, N, P e Q.
- Não confundir **concordância com o histórico** (contra a coluna C) com **acerto validado** (contra a verdade humana).

## PRÓXIMO PASSO SUGERIDO

Redimensionar as grades das abas para liberar o 1,58 milhão de células, começando pelas de maior desperdício. Não é urgente — há espaço no momento —, mas volta a travar assim que uma aba nova precisar ser criada.
