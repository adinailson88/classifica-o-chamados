# Prompt para continuar em outro chat — 01/08/2026

Cole o bloco abaixo inteiro no início da conversa nova.

---

## PROJETO

Classificação automática de chamados de manutenção predial da UFSB. Repositório:
`https://github.com/adinailson88/classificacao-chamados`

Doutorado no PPG Biossistemas/UFSB. A base validada de chamados GLPI alimenta o artigo sobre classificação automática multimodelo em português brasileiro. Pipeline: Google Sheets → GitHub Actions → JSONs em `docs/dados/` → painel (GitHub Pages) e artigo (`04_artigo/artigo_classificacao_chamados_v3.md`).

Planilha: `https://docs.google.com/spreadsheets/d/1lohPUQOgxzt_DMxnNLKMxnieZq1sVmh4uwBLbbgvfiQ/edit?gid=1090243921`
Aba principal: `CHAMADOS_ESQUELETO_REDUZIDO`

## ANATOMIA DA PLANILHA — ler antes de qualquer escrita

| Colunas | Natureza | Regra |
|---|---|---|
| A–F (ID Chamado, Título, `CATEGORIA COMPLETA` em C, Descrições) | **FÓRMULA** (`IMPORTRANGE`) | **NUNCA escrever.** Escrever em C quebrou o spill da aba inteira em 25/07/2026 |
| G, H, I, J | valor literal | Saída da Etapa 1 (modelo de produção LSTM+RF) |
| K, L | **FÓRMULA** | K = `=SE(G2="";"";G2=C2)`; a Etapa 1 reaplica sozinha |
| M (`CONFERÊNCIA GLPI`) | valor literal | Conferência humana: `Correto` / `Errado` |
| N (`CONFERÊNCIA IA`) | valor literal | **Aposentada** da derivação de verdade (ver abaixo). Não apagar, não usar |
| O (`Classificação IA - 2`) | valor literal | Predição do BERTimbau |
| P, Q (`CATEGORIA CORRETA MANUAL`) | valor literal | P = conferência da IA-2; Q = categoria certa quando M=`Errado` |

**REGRA DE OURO:** indexar SEMPRE por `id_chamado`, NUNCA por número de linha. A fonte do IMPORTRANGE foi redefinida em 28/07/2026 e reordenou as linhas — 10.410 de 14.094 divergiam do histórico. Escrever indexado por linha grava no chamado errado. Isso já aconteceu e foi corrigido.

## COMO A VERDADE É DERIVADA (mudou em 01/08/2026)

A coluna N conferia **uma única IA** (a de produção, coluna G) e não representa um experimento com 8 modelos. Foi aposentada. A verdade passou a ser:

- `M = 'Correto'` → a verdade é a categoria do GLPI (coluna C)
- `M = 'Errado'` + Q preenchida → a verdade é Q
- `M = 'Errado'` sem Q → **pendente**, nada é afirmado sobre modelo nenhum
- `M` vazia → chamado fora da avaliação

Implementado em `src/conferencia_derivada.py` (por `id_chamado`) e em `src/decisao_validada.py::carregar_decisoes(so_conferencia_glpi=True)`, usado por `src/avaliacao_final.py --verdade glpi` (padrão) e `src/analise_estatistica.py`.

Efeito quando foi aplicado: validados de 1.927 → **9.305**, conflitos de 7.469 → **0**.

## O QUE ACABOU DE SER CONCLUÍDO (pelo pesquisador, fora do repositório)

A **correção manual das categorias GLPI foi finalizada**. Todos os lotes pendentes foram processados: M preenchida com `Correto`/`Errado` em toda a base, e Q preenchida **somente** quando M=`Errado`. N, O e P não foram alteradas.

Último lote: 597 chamados, linhas 12735–14095, IDs 2025014328 a 2026070489, 558 `Correto` e 39 `Errado`, Q preenchida só nos 39. Nenhum ID após a linha 14095.

Houve também correção de critério num lote anterior de 600 chamados.

**Critério consolidado que deve ser respeitado em qualquer reavaliação:** `tampa de privada`, `assento sanitário`, `tampa do vaso` e similares **não** são hidrossanitário automaticamente. Seguem o histórico GLPI já corrigido e a categoria coerente com o objeto principal — normalmente acessório/equipamento, salvo se houver vazamento, entupimento, tubulação ou descarga hidráulica.

Interpretação conservadora. Marcar `Errado` só quando o objeto principal for inequívoco, a categoria correta existir na planilha, Q for diferente de C e houver coerência com casos semelhantes já validados. Evitar falso positivo em: tampa/assento sanitário; banheiro ou porta como mera localização; "rede" que não seja rede lógica; goteira/infiltração ambígua; ar-condicionado vazando; limpeza de reservatório já bem classificada; chamados mistos; pedidos amplos de reforma, vistoria ou manutenção geral.

## CONSEQUÊNCIA: TODOS OS NÚMEROS DERIVADOS ESTÃO DEFASADOS

Os artefatos vigentes foram gerados quando a base validada era **9.305 chamados**, com **242 pendentes** e **4.547 sem conferência**. Com a conferência concluída, esses três números mudam e **tudo que depende deles precisa ser regerado**: aba `CONFERENCIA_MULTIMODELO`, `docs/dados/conferencia_derivada.json`, `matriz_confusao.json`, `avaliacao_final.json`, `estatistica.json`, o painel e o artigo.

Números atuais (a serem substituídos), de `docs/dados/avaliacao_final.json`, n = 9.305:

| modelo | acerto validado | IC95% |
|---|---|---|
| linear_svc | 0,8394 | 0,8318–0,8465 |
| extra_trees | 0,8262 | 0,8186–0,8335 |
| random_forest | 0,8202 | 0,8120–0,8277 |
| regressao_logistica | 0,8078 | 0,7995–0,8158 |
| sgd | 0,8060 | 0,7976–0,8141 |
| lstm | 0,7405 | 0,7309–0,7490 |
| naive_bayes | 0,7366 | 0,7278–0,7455 |

Base: **14.094 chamados**. Predições out-of-fold rematerializadas em 01/08 (98.658 predições, 7 modelos, k-fold 5).

**Ressalva que deve sobreviver a qualquer atualização:** o BERTimbau (`transformer_ft`) aparece em 1º na matriz de confusão (0,8419), mas **não é comparável** aos sete acima — a predição dele vem da coluna O, preenchida preferencialmente sobre chamados já validados, enquanto os demais são *out-of-fold* sobre a base inteira. É vantagem de protocolo, não de modelo. O **LinearSVC é o número defensável**.

## PRÓXIMO PASSO 1 — AUDITORIA DA PLANILHA (read-only, antes de qualquer coisa)

Rodar o workflow `conferencia_derivada.yml` em **dry-run** (`aplicar=false`). Ele já responde, sem escrever nada:

- **M vazia** → campo `sem_conferencia`
- **M=`Errado` com Q vazia** → campo `pendente_glpi_errado_sem_q`
- **total conferido** → `com_conferencia_glpi`
- **total com verdade** → `verdade_glpi` (M=Correto) + `verdade_manual` (M=Errado com Q)

Duas verificações **não cobertas** pelas ferramentas atuais e que precisam ser implementadas:

- **M=`Correto` com Q preenchida indevidamente**
- **distribuição final das categorias em Q**

Sugestão: acrescentar ambas ao `src/conferencia_derivada.py` (a função pura `montar_linhas` já percorre todos os chamados) ou a `scripts/migracoes/dump_amostra_planilha.py`, que é read-only. Há testes em `tests/test_conferencia_derivada.py` — manter a cobertura.

## PRÓXIMO PASSO 2 — REGERAR A CADEIA

Depois da auditoria limpa, nesta ordem:

1. `conferencia_derivada.yml` com `aplicar=true` — regrava a aba `CONFERENCIA_MULTIMODELO`, o `conferencia_derivada.json` e o `matriz_confusao.json`
2. `avaliacao_final.yml` — recalcula acerto validado, IC95 e ensembles sobre a verdade nova
3. `estatistica.yml` — Cochran Q, McNemar, kappa, bootstrap
4. `avaliacao_bertimbau_holdout.yml` — comparação held-out dos 8 modelos
5. `dashboard.yml` — republica o painel
6. `python src/sincronizar_numeros_artigo.py` — dry-run, conferir, depois `--aplicar`. O script é **idempotente** e **aborta sem escrever** se algum trecho esperado não casar. Ele também se recusa a operar se o líder do ranking deixar de ser o LinearSVC — nesse caso a conclusão do artigo precisa ser reescrita por uma pessoa, não por substituição de string
7. O push no `.md` dispara `artigo_pdf.yml`, que republica o PDF

## PRÓXIMO PASSO 3 — REGISTRO

Registrar no `CONTEXTO.md` (seção "Próxima ação") que a correção manual das categorias GLPI foi concluída, com os totais finais da auditoria. **Não** narrar o processo no artigo — artigo não é relatório de processo.

## PENDÊNCIA ABERTA — teto de células do Google Sheets

Auditoria de 01/08 (`scripts/migracoes/auditar_abas_planilha.py`, workflow `auditar_abas_planilha.yml`, read-only): **9.008.123 células alocadas (90,1% do limite de 10 milhões)** para 7.427.340 usadas — **1.580.783 de desperdício**.

- **Não há lixo relevante**: só 2 abas órfãs, 84 mil células (0,8%). Apagar não resolve.
- O ganho está em **redimensionar a grade alocada**, sem apagar dado. Piores: `COMPARACAO_MODELOS` (260.000 alocadas para 1.313 usadas), `CLASSIF__transformer_ft` (220.000 para 11), `CONTROLE_CLASSIFICACAO_2` (180.000 para 261), `RECLASS_VALIDADOS` (260.000 para 50.115), `VALIDACAO_HUMANA` e `LOG_TURNOS_RECLASSIFICACAO` (alocadas e vazias).
- **NÃO APAGAR** `BACKUP_ETAPA1_20260726_131413` nem `BACKUP_ETAPA1_20260801_162324` — são fontes de recuperação.
- `RECLASS_HISTORICO` ocupa 2,7 milhões (30% do total). Compactar liberaria ~2,3 milhões, **mas só depois de exportar o histórico completo** — foi essa trilha que permitiu recuperar a coluna O em 01/08.

Sintoma: a criação de aba nova falha com `This action would increase the number of cells in the workbook above the limit`.

## FERRAMENTAS DISPONÍVEIS NO REPOSITÓRIO

| Arquivo | Função |
|---|---|
| `src/conferencia_derivada.py` | Deriva a conferência de cada IA de M+Q; gera a aba e 2 JSONs |
| `src/matriz_confusao_multimodelo.py` | Matriz de confusão esparsa por modelo (lógica pura) |
| `src/sincronizar_numeros_artigo.py` | Sincroniza números do artigo; aborta se um trecho não casar; idempotente |
| `src/avaliacao_final.py` | `--verdade glpi` (padrão) / `--verdade conferencias` (legado) |
| `scripts/migracoes/dump_amostra_planilha.py` | Dump read-only: cabeçalho, quais colunas são fórmula, taxas C==G e C==O |
| `scripts/migracoes/verificar_alinhamento_linhas.py` | Diagnóstico read-only de alinhamento linha × id_chamado |
| `scripts/migracoes/auditar_abas_planilha.py` | Auditoria de custo em células por aba |
| `scripts/migracoes/restaurar_coluna_o.py` | Restaura a coluna O do `RECLASS_HISTORICO`, por ID |

Suíte de testes: `python -m pytest tests/ -q` (155 testes).

## AUTOMAÇÃO ATIVA

Todos os workflows de escrita estão habilitados. O `conferencia_derivada.yml` roda a cada 6 h e regrava a aba, o resumo e a matriz de confusão; o Pages republica em seguida. **A base de verdade cresce sozinha conforme M e Q são preenchidas** — o que significa que a auditoria e a regeneração acima podem já ter sido feitas parcialmente pelo cron. Sempre conferir o `gerado_em` dos JSONs antes de concluir qualquer coisa.

## REGRAS DE TRABALHO

- Nenhuma escrita na planilha sem **dry-run** apresentado antes, com contagens, intervalo, primeiro/último ID e distribuição das alterações, e sem autorização explícita.
- Nunca alterar ou apagar as colunas M, N, O, P e Q.
- Nunca escrever nas colunas A–F (fórmula) nem em K e L (fórmula).
- **Não inventar resultado de workflow.** Se um workflow não pôde ser executado, dizer exatamente qual e por quê.
- Se faltar credencial ou permissão, dizer qual acesso falta ou qual workflow precisa ser disparado manualmente pela interface do GitHub.
- Artigo: só dados e números mudam. Não alterar estrutura, não reescrever seções, não narrar auditorias ou rodadas anteriores.
- Não confundir **concordância com o histórico** (contra a coluna C) com **acerto validado** (contra a verdade humana). São grandezas diferentes e o artigo as separa.
