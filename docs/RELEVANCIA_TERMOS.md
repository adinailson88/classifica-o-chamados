# Relevância de termos por categoria + mapa de correlação

> Ferramenta exploratória de **triagem de taxonomia**. Responde "quais palavras
> caracterizam cada categoria?" e "quais categorias têm vocabulário sobreposto?".
> **Não** é métrica de acurácia, **não** decide categoria e **não** altera o histórico.

## Por que existe

Duas perguntas de pesquisa que o ranking de concordância não responde:

1. **O que define cada categoria, na prática?** Ex.: para hidráulica, esperamos
   `agua`, `vazamento`, `torneira`, `sanitario`. Se os termos característicos de uma
   categoria não fizerem sentido, há ruído na rotulagem ou na própria taxonomia.
2. **Quais categorias se confundem?** Categorias com vocabulário muito parecido são
   candidatas naturais a erro de classificação (histórico **e** IA) e a fusão/revisão
   na taxonomia. É o "mapa de correlação" — análogo a um mapa de geoprocessamento:
   célula **quente** = vocabulário sobreposto (correlação → 1); **fria** = separadas.

## Como mede

| Sinal | Método | Leitura |
|---|---|---|
| `top_log_odds` | Log-odds com **prior de Dirichlet informativo** (Monroe, Colaresi & Quinn, 2008), com z-score robusto | Termo **característico** da categoria frente a todas as outras. É o ranking recomendado para "palavras-chave". O prior evita que termos raros dominem. |
| `top_tfidf` | Peso médio no **centróide TF-IDF** da categoria | Termo frequente **e** discriminante dentro da categoria. |
| Mapa de correlação | **Cosseno** entre centróides TF-IDF de cada par de categorias | 1 = vocabulário sobreposto (candidatas a confusão/fusão); 0 = bem separadas. |

Representação: TF-IDF (1-grama e 2-gramas), `strip_accents`, stopwords PT-BR + ruído de
chamado/OSM (`favor`, `solicito`, `bloco`, `campus`…), `min_df` configurável.

## Privacidade

- Os termos são **agregados sobre todo o corpus**, não texto de um chamado.
- `--min-df` (default 5) descarta tokens raros; tokens puramente numéricos e com < 3
  caracteres são removidos. Isso reduz o risco de expor matrícula/nome que apareça pouco.
- Os JSON publicados (`docs/dados/*.json`) contêm apenas categorias, termos e scores —
  nenhum ID, título ou descrição livre.

## Como rodar

Dry-run (gera os JSON em `docs/dados/`, **não** grava na planilha):

```bash
python src/relevancia_termos.py --top-n 25 --min-df 5 --min-chamados-categoria 10
```

Aplicar (grava também as abas privadas `RELEVANCIA_TERMOS` e `CORRELACAO_CATEGORIAS`):

```bash
python src/relevancia_termos.py --aplicar
```

Via GitHub Actions: workflow **`relevancia_termos.yml`** (manual). Mantém `aplicar=false`
por padrão; sempre commita os JSON agregados. Exemplo:

```bash
gh workflow run relevancia_termos.yml --repo adinailson88/classificacao-chamados \
  -f aplicar=false -f top_n=25 -f min_df=5 -f min_chamados_categoria=10
```

## Cruzamento com a matriz de confusão IA×histórico

`src/cruzamento_taxonomia.py` junta dois sinais que, sozinhos, não decidem taxonomia:

- **confusão IA×histórico**: `P(IA prevê B | histórico = A)` — com que frequência os
  chamados da categoria A acabam recebendo B pela IA;
- **correlação vocabular**: o cosseno entre centróides, reaproveitando a saída de
  `relevancia_termos`.

O cruzamento ranqueia pares altos nas duas dimensões por meio de uma média geométrica.
Confusão alta sem sobreposição vocabular tende a indicar ruído; confusão alta com
sobreposição sugere categoria duplicada, necessidade de renomeação ou critério de
desambiguação. O resultado é triagem, não veredito automático.

```bash
python src/cruzamento_taxonomia.py --top 40 --min-df 5 --min-chamados-categoria 10
```

## Saídas

- `docs/dados/termos_relevantes.json` — termos característicos e TF-IDF por categoria;
- `docs/dados/correlacao_categorias.json` — matriz de cosseno e pares mais próximos;
- `docs/dados/confusao_historico_ia.json` — matriz de confusão IA × histórico;
- `docs/dados/cruzamento_taxonomia.json` — candidatos à revisão de taxonomia;
- `docs/mapa_correlacao.html` — visualização do mapa, termos e candidatos;
- abas privadas, somente com `--aplicar`: `RELEVANCIA_TERMOS`,
  `CORRELACAO_CATEGORIAS` e `CRUZAMENTO_TAXONOMIA`.

## Como interpretar

- Termos coerentes indicam identidade textual da categoria.
- Termos genéricos ou incoerentes sugerem rotulagem ruidosa ou categoria residual.
- Pares com alta correlação e confusão devem ser priorizados na revisão humana da taxonomia.
- A ferramenta não funde, renomeia ou corrige categorias automaticamente.

## Verificação atual

A lógica foi validada em corpus sintético e aplicada aos dados reais do projeto. O arquivo
`docs/dados/termos_relevantes.json`, gerado em 27/07/2026 às 05:56, registra os parâmetros
`top_n=25`, `min_df=5`, `min_chamados_categoria=10`, representação TF-IDF com 9.029 termos,
log-odds com prior de Dirichlet e correlação por cosseno entre centróides.

Os resultados públicos estão versionados e são consumidos pelo painel. O estado das abas
privadas só deve ser afirmado quando houver execução explícita com `--aplicar`; ele não é
necessário para interpretar os JSONs agregados publicados.