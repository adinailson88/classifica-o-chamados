# Metodologia Shannon e Jensen-Shannon

## Objetivo

A camada Shannon adiciona uma leitura informacional ao experimento de classificacao de chamados. Ela nao mede acuracia diretamente. Seu objetivo e quantificar dispersao, ambiguidade e distancia distributiva das previsoes das IAs em relacao a categoria historica.

## Dados usados

Entradas publicas e sanitizadas:

1. `docs/dados/registros.json`: fonte oficial da Etapa 1.
2. `docs/dados/registros_<modelo>.json`: predicoes publicadas por IA.

Os arquivos usados nao contêm ID do chamado, titulo, descricao ou texto livre. A saida preserva essa regra de privacidade.

## Calculos

### Entropia de Shannon

Para uma distribuicao de categorias com probabilidades `p_i`:

```text
H(X) = - soma(p_i * log2(p_i))
```

A entropia normalizada usa:

```text
H_norm = H(X) / log2(k)
```

em que `k` e o numero de categorias observadas na distribuicao avaliada. O painel tambem publica o numero de categorias efetivas:

```text
categorias_efetivas = 2 ^ H(X)
```

### Shannon por IA

Para cada IA, calcula-se a distribuicao das categorias previstas (`p`). A entropia alta indica previsoes mais espalhadas; a entropia baixa indica concentracao em poucas categorias. Essa leitura precisa ser confrontada com concordancia, calibracao e validacao humana.

### Shannon por categoria historica

Para cada categoria historica (`o`) e para cada IA, calcula-se a distribuicao das previsoes (`p`) dentro daquela categoria. O suporte minimo padrao e 30 registros. Categorias com alta entropia normalizada indicam fronteira taxonomica ambigua, mistura semantica ou baixa separabilidade operacional.

### Entropia de votos entre IAs

Para linhas presentes em duas ou mais fontes de modelo, as previsoes das IAs sao tratadas como votos. Calcula-se a entropia da distribuicao desses votos. Linhas com entropia alta indicam maior desacordo entre IAs e podem formar uma fila de auditoria humana.

### Divergencia Jensen-Shannon

Para comparar a distribuicao prevista por uma IA com a distribuicao historica, usa-se a divergencia Jensen-Shannon:

```text
JS(P, Q) = 0,5 * KL(P || M) + 0,5 * KL(Q || M)
M = 0,5 * (P + Q)
```

com logaritmo em base 2. Valores menores indicam distribuicao prevista mais proxima da distribuicao historica. Isso nao prova maior acerto; indica menor distorcao distributiva.

## Saidas publicadas

1. `docs/dados/shannon_resumo.json`: fonte, criterios, data de geracao e destaques.
2. `docs/dados/shannon_modelos.json`: entropia por IA, categorias efetivas, concordancia historica e Jensen-Shannon.
3. `docs/dados/jensen_shannon_modelos.json`: ranking de distancia distributiva contra o historico.
4. `docs/dados/shannon_categorias.json`: categorias historicas mais ambiguas e detalhe por modelo/categoria.
5. `docs/dados/shannon_votos.json`: linhas sanitizadas com maior entropia de votos entre IAs.

## Interpretacao

1. Shannon alto por IA: a IA espalha suas previsoes por mais categorias.
2. Shannon baixo por IA: a IA concentra previsoes em menos categorias.
3. Jensen-Shannon baixo: a distribuicao prevista se parece mais com o historico.
4. Categoria com Shannon alto: a categoria historica gera previsoes divididas, sugerindo ambiguidade ou sobreposicao taxonomica.
5. Linha com entropia de votos alta: as IAs discordam mais entre si e a linha deve ser candidata a auditoria.

## Limitacoes

1. A entropia nao distingue acerto de erro.
2. A distribuicao historica pode conter rotulos incorretos.
3. Categorias raras sao filtradas por suporte minimo, mas ainda exigem cautela.
4. A decisao final continua dependente da conferencia humana nas colunas M, N e P.

## Execucao

```bash
python src/analise_shannon.py
```

O workflow `dashboard.yml` executa esse script automaticamente apos `src/exportar_dashboard.py`.
