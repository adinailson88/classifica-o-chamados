# Governança final do repositório

Documento canônico do encerramento da Etapa 8 (governança de infraestrutura e
dados do repositório), separado da Etapa 0–11 do artigo científico registrada
em `PLANO_EXECUCAO_ATUAL.md`. Escrito no Lote 8I, a partir de auditoria
independente do estado real de `origin/main` e da API do GitHub.

## 1. Estado da Etapa 8

Encerrada. Lotes concluídos: 8B a 8H (writers, concorrência, privacidade,
governança de estado, proteção de `main`) e 8I (esta documentação e auditoria
final). Cada lote tem seu histórico completo em commits e Pull Requests; este
documento registra apenas o estado final, não a narrativa das rodadas.

## 2. Três domínios do repositório

O repositório mistura três execuções de natureza distinta. Misturá-las é o
principal risco de má interpretação futura dos dados e dos resultados.

### ARTIGO_CONGELADO

A execução científica publicada/congelada do artigo. Corpus total 14.060,
subconjunto de modelagem 13.972, 41 categorias na modelagem, 5 dobras, hash
canônico `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`.

Não deve ser recomputada silenciosamente. Dashboard e novas classificações
não alteram este resultado histórico. Qualquer mudança científica futura
exige novo corte científico, com proveniência própria — nunca sobrescrever o
manifesto vigente como consequência automática de rodar um script.

### OPERACIONAL_VIVO

Google Sheets atual, classificação/reclassificação, métricas correntes,
automações, dashboard e outputs operacionais versionados. Pode continuar
crescendo e mudando com novos registros; não redefine retroativamente o
artigo congelado. O dashboard é operacional, não evidência congelada do
artigo. Conteúdo bruto/restrito de chamados não é publicado.

### NOVOS_CORTES_CIENTIFICOS

Futuras análises — ensemble, novos experimentos BERTimbau, novos cortes
temporais, drift, mudanças de taxonomia, novos corpora. Cada novo estudo
deve ter, quando aplicável: corpus explicitamente definido, manifesto,
hashes, particionamento, seeds, resultados próprios e namespace/proveniência
própria. Nunca reutilizar silenciosamente o contrato congelado como se fosse
a mesma execução científica.

## 3. Contrato do artigo congelado

- Manifesto: [`docs/dados/MANIFESTO_ARTIGO_CONGELADO.json`](dados/MANIFESTO_ARTIGO_CONGELADO.json) — 21 artefatos com hash SHA-256 individual.
- Verificador: [`src/verificar_artigo_congelado.py`](../src/verificar_artigo_congelado.py).
- Check de PR: [`.github/workflows/verificar_artigo_congelado.yml`](../.github/workflows/verificar_artigo_congelado.yml) — só leitura, sem secrets, sem recongelamento; não impede sozinho um merge que ignore checks (depende de branch protection, ver Seção 7).

## 4. Governança dos GitHub Actions writers (Etapa 8H)

Writers auditados; staging deve ser explícito. Proibidos em código executável
dos writers auditados: `git add .`, `git add -A`, `push --force`,
`reset --hard`, `-X theirs`, `-X ours`. Conflitos reais devem falhar
explicitamente, não ser resolvidos por escolha silenciosa de lado.
`contents:write` foi reduzido nos workflows onde havia separação entre
job de leitura (guard) e job de escrita.

`dados/estado_automacao.json` não é mais resolvido por merge textual: as
quatro chaves lógicas (`avaliacao_final`, `comparar_modelos`,
`multimodelo_classificacao`, `transformer_ft`) passam por
[`src/persistir_estado_automacao.py`](../src/persistir_estado_automacao.py),
que altera semanticamente uma única chave, parte do SHA remoto mais recente
via worktree temporário, tenta o push e, se rejeitado, descarta a tentativa
inteira e recomeça do novo HEAD remoto — sem resolver conflito textual
automaticamente.

## 5. Privacidade e dados restritos

`docs/dados/bertimbau_cluster_report.json` teve identificação histórica de
exposição de fragmentos de texto operacional (via detecção de
quase-duplicatas). Estado atual:

- arquivo removido da versão corrente do repositório;
- o gerador passou a usar pseudonimização por hash determinístico SHA-256 para a representação, em vez do texto original;
- `.gitignore` impede nova inclusão do relatório;
- não houve reescrita de histórico — decisão deliberada, pelo impacto amplo em branches, tags e reprodutibilidade de commits já publicados;
- eventual confirmação futura de PII sensível no histórico exigiria processo separado e explicitamente autorizado pelo autor.

Nenhum fragmento de texto real é reproduzido neste documento.

## 6. BERTimbau holdout e Tabela S5

Existem `docs/dados/avaliacao_bertimbau_holdout.json` e o workflow
`.github/workflows/avaliacao_bertimbau_holdout.yml`. Isso não estabelece
automaticamente que esse workflow seja o gerador da `tabela_S5_holdout_bertimbau.csv`
atual — auditoria anterior (`docs/AUDITORIA_MATERIAL_SUPLEMENTAR.md`) registra
gerador não localizado no repositório. Não há cadeia automatizada comprovada
entre os dois. A Tabela S5 não foi modificada nem recalculada neste lote.

## 7. Proteção de `main`

Confirmado via API do GitHub nesta execução (Lote 8I):

- `main` com `protected=true`;
- ruleset ativo `Main - impedir delecao e force push` (id `21023311`), regras `deletion` e `non_fast_forward`, `bypass_actors=[]`;
- force-push e non-fast-forward bloqueados; deleção de `main` bloqueada;
- writers fast-forward continuam compatíveis com essa proteção.

**Limitação conhecida e aceita:** foi estudado um segundo ruleset para exigir
Pull Request e o check `verificar`. A tentativa de usar a GitHub Actions
Integration (id 15368) como bypass foi rejeitada pelo GitHub com HTTP 422:
"Actor GitHub Actions integration must be part of the ruleset source or owner
organization" — limitação de repositório pessoal (sem organização). Por
decisão arquitetural, não foi criada nova identidade técnica, Deploy Key,
GitHub App própria, machine user, nem uso de `RepositoryRole` por
aproximação. PR e check `verificar` permanecem disciplina operacional, não
enforcement completo do servidor. Isto não é um bug de código pendente.

## 8. Limitações conhecidas e decisões aceitas

1. PR e check `verificar` não são tecnicamente obrigatórios no servidor (Seção 7).
2. Gerador da Tabela S5 não confirmado no repositório (Seção 6).
3. Histórico do Git não foi reescrito após a exposição identificada em `bertimbau_cluster_report.json`; risco residual no histórico aceito conscientemente (Seção 5).
4. Não existe documento de autorização institucional/ética para uso científico dos registros do GLPI (ver `PLANO_EXECUCAO_ATUAL.md`, pendência de 05/08/2026) — fora do escopo desta etapa de governança de infraestrutura.

## 9. Regras para trabalhos futuros

- Nunca sobrescrever os 21 artefatos do manifesto congelado como efeito colateral de rodar um script operacional.
- Todo novo corte científico declara seu próprio manifesto, hash e proveniência, sem reaproveitar o namespace do artigo congelado.
- Escritas em `dados/estado_automacao.json` usam exclusivamente `src/persistir_estado_automacao.py`.
- Nenhum workflow experimental do BERTimbau escreve em Google Sheets ou em `main`.
- Nenhum dado bruto/restrito de chamado é publicado em `docs/`.
- Mudanças administrativas (rulesets, secrets, permissões) exigem decisão explícita do autor, registrada em Pull Request própria — não decorrem de rotina automática.

## 10. Auditoria de encerramento (Lote 8I)

Executada em worktree isolado a partir de `origin/main` (SHA `a198fec1d8293063d9b73dc23bd155d9c3f26e43`), sem alterar a working tree principal.

| Verificação | Resultado |
|---|---|
| `python src/verificar_artigo_congelado.py` | OK: 21/21 artefatos íntegros; hash `1e4762438a7e...846409a`; corpus 14.060/13.972; 41 categorias; 5 dobras |
| `pytest -q` (suíte completa) | 917 passed, 2 warnings, 131 subtests passed |
| `tests/test_governanca_writers_git.py` + `tests/test_estado_automacao_workflows.py` + `tests/test_persistir_estado_automacao.py` + `tests/test_transformer_ft_governanca.py` | 74 passed, 131 subtests passed |
| `tests/test_bertimbau_coreset_privacidade.py` | 11 passed |
| `docs/dados/bertimbau_cluster_report.json` no HEAD | ausente; presente apenas no histórico (sem reescrita) |
| `.github/workflows/transformer_ft_experimentos.yml` | `workflow_dispatch` manual, `permissions: contents: read`, sem escrita em Google Sheets (roda sem `--aplicar`), sem `git add/commit/push`, upload de artifact com allowlist estrita (sem `bertimbau_cluster_report.json`) |
| `dados/estado_automacao.json` versionado por `git add` em workflow | nenhuma ocorrência fora de `src/persistir_estado_automacao.py` |
| Padrões proibidos (`git add .`, `git add -A`, `push --force`, `reset --hard`, `-X theirs`, `-X ours`) em `.github/workflows/` e `src/` | nenhuma ocorrência executável (só menções em comentário explicando a ausência) |
| Ruleset remoto (API) | 1 ruleset ativo, id `21023311`, regras `deletion` + `non_fast_forward`, `bypass_actors=[]`; nenhum segundo ruleset |
| `main` `protected` (API) | `true` |

### Auditoria de fronteira dos três domínios

1. Algum workflow operacional modifica arquivo do manifesto congelado? **Não** — os únicos workflows que citam nomes de arquivos do manifesto (`gerar_particoes_canonicas.yml`, `inferencia_canonica.yml`, `construir_grupos_textuais.yml`, `auditar_base_canonica.yml`) são todos `workflow_dispatch` manual com `permissions: contents: read`, sem escrita.
2. Algum dashboard é tratado como resultado congelado? **Não** — a allowlist de `dashboard.yml` cobre apenas arquivos operacionais (métricas de experimento, calibração, multimodelo, shannon), sem sobreposição com os 21 arquivos do manifesto.
3. Algum novo experimento científico sobrescreve outputs congelados? **Não observado** nesta auditoria.
4. Algum artefato com texto bruto/restrito está publicamente versionado no HEAD? **Não** — `bertimbau_cluster_report.json` está ausente do HEAD e coberto por `.gitignore`.
5. Algum workflow experimental escreve em Google Sheets? **Não** — `transformer_ft_experimentos.yml` roda os experimentos sem `--aplicar`.
6. Alguma documentação afirma proveniência científica não comprovada? **Não** — este documento registra explicitamente que o gerador da Tabela S5 não está confirmado (Seção 6), em vez de presumir a cadeia.

Nenhum item classificado como BLOQUEADOR ou IMPORTANTE nesta auditoria.
