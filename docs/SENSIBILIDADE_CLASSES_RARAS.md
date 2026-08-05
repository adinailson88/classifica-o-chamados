# Sensibilidade ao tratamento das categorias raras

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Gerado em:** 05/08/2026 00:57  
**Hash do corpus:** `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`

## 1. Cobertura

- Linhas: 13972 de 14060 (99.37%); 88 fora.
- Categorias: 41 de 50 (82%); 9 fora.
- Motivo: 12 linhas por aritmética e 76 por estratificação.

**O desempenho principal não cobre integralmente as 50 categorias da taxonomia: vale para as 41 com suporte nas cinco dobras, e as nove ausentes são as de menor frequência.**

| Categoria excluída | Linhas | Grupos distintos | Motivo |
|:---|---:|---:|:---|
| TI / Dados / Rede > Coleta de dados | 40 | — | estratificação: sem suporte em alguma dobra |
| Hidrossanitária > ETA / ETE | 15 | — | estratificação: sem suporte em alguma dobra |
| Manutenção Preventiva > Nobreak | 9 | — | estratificação: sem suporte em alguma dobra |
| Elétrica > Sistema Fotovoltaico (FV) | 7 | — | estratificação: sem suporte em alguma dobra |
| Estrutura Predial > Instalações Especiais (gás, ar comprimido, etc.) | 5 | — | estratificação: sem suporte em alguma dobra |
| Área Externa e Ambiental > Drenagem | 4 | 4 | aritmética: menos grupos textuais distintos que dobras |
| Manutenção Preventiva > Aplicação cupinicida | 3 | 3 | aritmética: menos grupos textuais distintos que dobras |
| Manutenção Preventiva > Bomba | 3 | 3 | aritmética: menos grupos textuais distintos que dobras |
| Suprimentos / Apoio Técnico > Transporte | 2 | 2 | aritmética: menos grupos textuais distintos que dobras |

## 2. Sensibilidade ao número de dobras

uma categoria só pode ter suporte em k dobras se possuir ao menos k grupos textuais distintos, porque o grupo inteiro ocupa uma única dobra.

| k | Categorias recuperáveis por aritmética | Linhas |
|---:|---:|---:|
| 2 | 4 | 12 |
| 3 | 3 | 10 |
| 4 | 1 | 4 |
| 5 | 0 | 0 |

as categorias excluídas por estratificação já dispunham de grupos distintos suficientes para k = 5; se sobreviveriam a um k menor depende de reexecutar o particionador sobre a base viva, o que esta rodada não fez. Informação insuficiente para verificar.

reduzir k depois de observar o resultado escolheria o protocolo pela métrica; a redução só seria defensável como decisão anterior à avaliação, e ainda assim custaria treino menor por dobra.

## 3. Macro-F1 sob três convenções de denominador

- **A** — as 41 categorias com suporte nas cinco dobras (41 rótulos): convenção do artigo.
- **B** — as 50 categorias da taxonomia, com F1 igual a zero nas nove ausentes das partições (50 rótulos): limite inferior: nenhum modelo prevê categoria ausente do treino, de modo que o valor é o pior caso e não uma estimativa do desempenho sobre a taxonomia inteira.
- **C** — as 14 famílias do primeiro nível da taxonomia (14 rótulos): avaliação hierárquica: cada categoria rara é absorvida por uma família com suporte, o que fecha a lacuna de cobertura de categorias, mas não a de linhas — as 88 linhas fora das partições continuam sem predição out-of-fold.

| Modelo | Acurácia | Macro-F1 A | Macro-F1 B | Macro-F1 C |
|---|---:|---:|---:|---:|
| Regressão Logística | 0.805 | 0.6689 | 0.5485 | 0.6801 |
| LinearSVC | 0.8253 | 0.6684 | 0.5481 | 0.6816 |
| SGD | 0.8093 | 0.6669 | 0.5469 | 0.673 |
| Extra Trees | 0.8073 | 0.6362 | 0.5217 | 0.6548 |
| Random Forest | 0.797 | 0.6152 | 0.5044 | 0.6346 |
| LSTM | 0.7287 | 0.524 | 0.4297 | 0.524 |
| Naive Bayes | 0.7088 | 0.2951 | 0.242 | 0.3626 |

Ordenação estável entre A e B: sim. Entre A e C: não.

a convenção B é reescala monotônica da A pelo fator 41/50, de modo que a ordenação não pode mudar; o que muda é a magnitude, e é isso que ela serve para mostrar.

## 4. Alternativas consideradas

| Alternativa | Efeito | Custo | Adotada |
|:---|:---|:---|:---|
| menor número de dobras | recupera categorias por aritmética, mas apenas as excluídas por esse motivo; ver `dobras_viaveis` | menos dados de treino por dobra e menor comparabilidade | não |
| avaliação hierárquica por família | fecha a lacuna de cobertura de categorias, de 41 em 50 para 14 em 14 famílias, ao custo de responder a uma pergunta mais grossa | perde a granularidade que a decisão de gestão usa | reportada como sensibilidade; a leitura por tipo de manutenção, em `recortes_canonicos.json`, é a versão hierárquica que o artigo já usa no corpo |
| política de abstenção | não recupera as categorias ausentes, porque o modelo não pode abster-se a favor de uma classe que não conhece; atua sobre o erro nas categorias conhecidas | cobertura operacional menor | já medida como automação seletiva por confiança em `calibracao_canonica.json` |
| fusão de categorias raras em uma classe residual | alteraria a taxonomia institucional sob avaliação | mudaria o objeto do estudo e impediria comparação com a base administrativa | não |

## 5. Proveniência

- Predições: `docs/dados/retreino_canonico_predicoes.csv`.
- Partições e motivos de exclusão: `docs/dados/particoes_canonicas.json`.
- Script: `src/sensibilidade_classes_raras.py`.
- Nenhum modelo foi retreinado e nenhuma escrita foi feita na planilha.
