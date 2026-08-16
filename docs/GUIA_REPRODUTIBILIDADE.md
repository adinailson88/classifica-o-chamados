# Guia de reprodutibilidade do artigo

> Mapa de quais arquivos são essenciais para reproduzir os números, tabelas e
> figuras do artigo `04_artigo/artigo_classificacao_chamados_v3.md`, em que
> ordem rodar os scripts, e o que não é reproduzível fora deste repositório
> sem acesso à planilha original. Não substitui `docs/MATRIZ_PROVENIENCIA.md`,
> que é a fonte de verdade número-a-número; este guia organiza o caminho de
> execução que produz os artefatos que a matriz rastreia.

## 1. O que você precisa ter, fora do repositório

O corpus bruto (título, descrição do chamado, título e descrição da ordem de
serviço) nunca é versionado como texto livre — só como resumo criptográfico
(hash SHA-256) e agregados sem PII, por política de privacidade (ver skill
`dashboard-json-github-pages`). Isso significa que **reproduzir do zero exige
acesso à planilha de origem**, não só a este repositório.

Para rodar qualquer script que leia a planilha, são necessários dois segredos:

| Segredo | O que é | Onde é usado |
|---|---|---|
| `SPREADSHEET_ID` | ID da planilha Google Sheets, aba `CHAMADOS_ESQUELETO_REDUZIDO` (colunas A:Q, ver `config_experimento.json`) | env var lida por `src/planilha.py` |
| `GCP_SA_KEY` | Chave JSON de conta de serviço do Google Cloud com acesso de leitura à planilha | gravada em `credenciais_sa.json`, lida via `GOOGLE_APPLICATION_CREDENTIALS` |

Localmente, em vez de segredos de CI, `config_experimento.json` aceita
`spreadsheet_id.local` (arquivo não versionado) no lugar do `SPREADSHEET_ID`
de ambiente. As colunas esperadas (`colunas_esperadas` no mesmo arquivo)
precisam existir com esses cabeçalhos exatos para os scripts localizarem as
colunas por nome, não por posição fixa.

**Sem esses dois itens, você não regenera o corpus do zero** — mas, como a
Seção 3 explica, boa parte do artigo já pode ser reconstruída só com o que
está congelado e versionado no repositório, sem tocar a planilha de novo.

## 2. Pipeline completo, na ordem de execução

Numeração conforme `PLANO_EXECUCAO_ATUAL.md` (Passos 1 a 10; o Passo 6 é
decisão documentada, sem script, e o Passo 9 está formalmente encerrado como
não aplicável). Passos 1 a 3 requerem a planilha; a partir do Passo 4, os
scripts partem do corpus já congelado.

| Passo | Script | Entrada | Saída principal | Workflow (se houver) |
|---|---|---|---|---|
| 1. Congelar e auditar a base | `src/auditar_base_canonica.py` | Planilha (A:Q) | `docs/dados/auditoria_base_canonica.json`, `docs/AUDITORIA_BASE_CANONICA.md` | `auditar_base_canonica.yml` |
| 2. Construir grupos textuais | `src/construir_grupos_textuais.py` | Planilha + auditoria do Passo 1 | `docs/dados/grupos_textuais.json`, `docs/GRUPOS_TEXTUAIS.md` | `construir_grupos_textuais.yml` |
| 3. Gerar partições canônicas | `src/gerar_particoes_canonicas.py` | Planilha + grupos do Passo 2 | `docs/dados/particoes_canonicas.json`, `docs/dados/particoes_canonicas_mapa.csv`, `docs/PARTICOES_CANONICAS.md` | `gerar_particoes_canonicas.yml` |
| 4, 5, 7. Retreino, regras e calibração | `src/executar_rodada_canonica.py` (orquestra `retreinar_modelos_canonicos.py`, `comparar_regras_modelos.py`, `calibrar_confianca.py`, `recortes_canonicos.py`, `custo_computacional_canonico.py` internamente) | Planilha + partições do Passo 3 | `docs/dados/rodada_canonica.json`, `retreino_canonico.json` (+ `.csv` de predições), `regras_versus_modelos.json`, `calibracao_canonica.json`, `recortes_canonicos.json`, `comparacao_historica.json`, `custo_computacional_canonico.json` | `rodada_canonica.yml` |
| 6. Decisão sobre o BERTimbau | — (decisão documentada, ver `docs/CUSTO_BERTIMBAU.md`) | `src/medir_custo_bertimbau.py` para a medição de custo | `docs/dados/custo_bertimbau.json` | `medir_custo_bertimbau.yml` |
| 8. Inferência estatística | `src/inferencia_canonica.py`, `src/inferencia_agrupada.py` | Predições do Passo 4 (`retreino_canonico_predicoes.csv`) | `docs/dados/inferencia_canonica.json`, `docs/dados/inferencia_agrupada.json` | `inferencia_canonica.yml` |
| — Sensibilidade e utilidade complementares | `src/sensibilidade_classes_raras.py`, `src/utilidade_reclassificacao.py`, `src/auditar_grupos_divergentes.py`, `src/auditar_disponibilidade_temporal.py` | Artefatos dos passos acima | `sensibilidade_classes_raras.json`, `utilidade_reclassificacao.json`, `grupos_divergentes_canonicos.json`, `disponibilidade_temporal.json` | sem workflow dedicado; rodar localmente |
| — Tabelas do apêndice | `src/tabelas_apendice_canonicas.py` | Artefatos acima | `docs/dados/tabelas_apendice_canonicas.json` | sem workflow dedicado |
| 10. Proveniência | `src/matriz_proveniencia.py` | Todos os artefatos acima | `docs/MATRIZ_PROVENIENCIA.md` (confere hash, aponta números legados remanescentes) | sem workflow dedicado; rodar localmente antes de editar o texto |

Todos os artefatos "canônicos" carregam `hash_corpus` (exceto os do
congelamento em si, que o definem) e os scripts recusam-se a rodar se os
hashes divergirem entre si — é a trava que impede misturar dados de rodadas
diferentes sem perceber.

## 3. Depois do congelamento: o que roda sem tocar a planilha

Uma vez que os Passos 1 a 8 produziram os JSONs acima, **as figuras e a
maior parte das tabelas do artigo se regeram só a partir deles**, sem
precisar da planilha nem das credenciais de novo:

| Saída | Script | Lê |
|---|---|---|
| Figura 1 (pipeline) | `src/gerar_figura1_pipeline.py` | nada externo — diagrama estático, edite `ETAPAS` no próprio script |
| Figuras 2 a 5 (confiabilidade, calor de categorias, matriz de confusão, trade-off de custo) | `src/gerar_figuras_canonicas.py` | `docs/dados/calibracao_canonica.json`, `custo_computacional_canonico.json`, `retreino_canonico.json`, `retreino_canonico_predicoes.csv` |
| Figura 6 (curva de aprendizado do LSTM) | `src/modelo_lstm.py` (gera `04_artigo/figuras/lstm_history.json` durante o próprio treino) | fora da rodada canônica — treino único, não comparável às Tabelas 2 e 3 (ver ressalva na matriz de proveniência) |
| PDF do artigo | pandoc/xelatex via `.github/workflows/artigo_pdf.yml` | só `04_artigo/artigo_classificacao_chamados_v3.md` |
| Material suplementar (Tabelas S1–S16) | scripts em `04_artigo/figuras/*.csv` (gerador por tabela) + `.github/workflows/material_suplementar_pdf.yml` | os mesmos JSONs canônicos acima |

Ou seja: se seu objetivo é só **auditar ou regenerar as figuras e o PDF a
partir dos números já congelados**, basta clonar o repositório e rodar os
scripts da Seção 3 — não precisa da planilha nem dos dois segredos da Seção 1.
Só precisa deles se quiser **recongelar o corpus do zero** (Passos 1–3) ou
re-treinar os modelos (Passo 4 em diante).

## 4. Scripts a evitar — legados, não a fonte do artigo atual

`src/gerar_figuras_canonicas.py` documenta isso no próprio topo: os
geradores antigos abaixo leem artefatos de uma execução anterior, que
descrevem outro corpus, e reintroduziriam números que o artigo já não usa.

- `src/gerar_figura2_confianca_desfecho.py`
- `src/gerar_figura3_tradeoff_custo.py`
- `src/gerar_figura4_confusoes.py`
- `src/gerar_figura7_mapas_calor.py`

Não rode esses quatro para tentar atualizar as figuras do artigo — use
`src/gerar_figuras_canonicas.py`. Da mesma forma, `04_artigo/figuras/*.json`
fora dos listados na Seção 3 (por exemplo `ablation_lstm_resultados.json`,
`comparacao_kfold_groupkfold.json`) são snapshots explicitamente marcados
como "fora da rodada canônica" na matriz de proveniência — servem de
análise de sensibilidade no suplemento, não de fonte para o corpo do artigo.

## 5. Dependências Python

Quatro arquivos de requirements, por peso da tarefa:

| Arquivo | Uso |
|---|---|
| `requirements-leves.txt` | scripts de auditoria/particionamento que só leem a planilha (Passos 1–3) |
| `requirements.txt` | pipeline principal (`gspread`, `google-auth`, `numpy`, `scikit-learn`, `tensorflow`) — cobre a rodada canônica inteira |
| `requirements-estatistica.txt` | inferência estatística (Passo 8) |
| `requirements-transformer.txt` | só para o experimento exploratório do BERTimbau |

## 6. Painel público (fora do escopo deste guia)

O painel (`docs/index.html`) lê os mesmos JSONs canônicos desta lista para a
aba Reclassificação (ver commit do seletor Artigo/Operacional), mas as
demais abas ainda leem dados operacionais vivos, não os canônicos. Isso é
tratado à parte, não é dependência para reproduzir o artigo.

## Proveniência deste guia

Escrito a partir da leitura de `PLANO_EXECUCAO_ATUAL.md` (Passos 0–11),
`docs/MATRIZ_PROVENIENCIA.md`, `.github/workflows/*.yml` e
`config_experimento.json`. Não gerado por script; atualize manualmente se a
rodada canônica mudar de hash ou se novos passos forem adicionados ao plano.
