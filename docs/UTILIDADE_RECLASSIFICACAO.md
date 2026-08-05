# Utilidade da reclassificação sob custos assimétricos

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Gerado em:** 05/08/2026 00:58  
**Hash do corpus:** `1e4762438a7e3627d3e32c1025f6bcb169e786881d8e86207806fdf98846409a`

## 1. Função de utilidade

`U = b x corrigidos - c x prejudicados - r x revisados`, dividida por b, o que deixa duas razões adimensionais e dispensa valor monetário:

- **rho** = c / b, custo do prejuízo em unidades de benefício da correção;
- **lambda** = r / b, custo da revisão em unidades de benefício da correção.

Rho = 1 e lambda = 0 reproduzem o ganho líquido simples do artigo, que permanece o resultado principal por ser transparente.

## 2. Política A — aplicação direta

O modelo reescreve a categoria sempre que diverge do histórico. A razão de equilíbrio é o valor de rho acima do qual a utilidade vira negativa.

| Modelo | Corrigidos | Prejudicados | Ganho simples | rho de equilíbrio | U/b (rho=0.25) | U/b (rho=0.5) | U/b (rho=1) | U/b (rho=2) | U/b (rho=4) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LinearSVC | 475 | 2321 | -1846 | 0.2047 | -105.2 | -685.5 | -1846.0 | -4167.0 | -8809.0 |
| SGD | 489 | 2559 | -2070 | 0.1911 | -150.8 | -790.5 | -2070.0 | -4629.0 | -9747.0 |
| Extra Trees | 422 | 2519 | -2097 | 0.1675 | -207.8 | -837.5 | -2097.0 | -4616.0 | -9654.0 |
| Regressão Logística | 492 | 2621 | -2129 | 0.1877 | -163.2 | -818.5 | -2129.0 | -4750.0 | -9992.0 |
| Random Forest | 416 | 2658 | -2242 | 0.1565 | -248.5 | -913.0 | -2242.0 | -4900.0 | -10216.0 |
| LSTM | 426 | 3621 | -3195 | 0.1176 | -479.2 | -1384.5 | -3195.0 | -6816.0 | -14058.0 |
| Naive Bayes | 309 | 3783 | -3474 | 0.0817 | -636.8 | -1582.5 | -3474.0 | -7257.0 | -14823.0 |

Com rho = 1 a utilidade é negativa em todos os sete modelos, que é o resultado já reportado. A reclassificação direta seria somente se estragar um registro valer menos de 0.205 do que vale corrigir outro, condição que nenhuma leitura razoável de custo em manutenção predial satisfaz, já que o registro corrompido propaga para a série da categoria e para a alocação de recurso, ao passo que a correção apenas recupera o valor devido.

## 3. Política B — triagem por divergência

A divergência enfileira o chamado para revisão humana em vez de reescrever o rótulo. Não há prejudicados por construção, e o limite de equilíbrio de lambda coincide com a precisão da fila.

| Modelo | Fila | Histórico errado na fila | Precisão da fila | U/b (lam=0) | U/b (lam=0.05) | U/b (lam=0.1) | U/b (lam=0.2) |
|---|---:|---:|---:|---:|---:|---:|---:|
| LinearSVC | 2849 | 528 | 0.1853 | +528.0 | +385.5 | +243.1 | -41.8 |
| SGD | 3100 | 541 | 0.1745 | +541.0 | +386.0 | +231.0 | -79.0 |
| Extra Trees | 3012 | 493 | 0.1637 | +493.0 | +342.4 | +191.8 | -109.4 |
| Regressão Logística | 3161 | 540 | 0.1708 | +540.0 | +381.9 | +223.9 | -92.2 |
| Random Forest | 3148 | 490 | 0.1557 | +490.0 | +332.6 | +175.2 | -139.6 |
| LSTM | 4168 | 547 | 0.1312 | +547.0 | +338.6 | +130.2 | -286.6 |
| Naive Bayes | 4256 | 473 | 0.1111 | +473.0 | +260.2 | +47.4 | -378.2 |

A mesma predição que não sustenta a reescrita sustenta a priorização: a fila de divergências concentra registros com histórico errado em até 18.53%, várias vezes a taxa de alteração do rótulo na base congelada, de modo que a política b tem utilidade positiva sempre que revisar custar menos do que essa fração do benefício de corrigir.

A revisão humana devolve a referência, o que é verdadeiro por construção neste desenho; o valor é portanto um teto da política, não previsão de campo.

A taxa de alteração do rótulo histórico, 4,25%, é apurada sobre as 14.060 linhas da base congelada, ao passo que a precisão da fila é apurada sobre as 13.972 avaliadas; a diferença de 88 linhas não altera a ordem de grandeza da comparação, mas os dois denominadores não devem ser fundidos.

## 4. Proveniência

- Contagens: `docs/dados/comparacao_historica.json`, rodada canônica.
- Script: `src/utilidade_reclassificacao.py`.
- Nenhum valor monetário é atribuído; todas as razões são adimensionais.
