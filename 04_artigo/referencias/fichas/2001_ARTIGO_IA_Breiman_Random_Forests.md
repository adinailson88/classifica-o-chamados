# 2001 ARTIGO IA Breiman Random Forests

## Referência
BREIMAN, Leo. Random Forests. Machine Learning, v. 45, p. 5–32, 2001.

**Tipo documental:** Artigo científico  
**Pasta temática:** `02_IA_e_CienciaDeDados`  
**Texto completo:** [Google Drive](https://drive.google.com/file/d/1qteSFCImvM20eZWQh4zaIJ4eKolIbJAo/view)  
**Palavras-chave:** Random Forest; ensemble; árvores de decisão; bagging; importância de variáveis; out-of-bag; classificação

## Síntese detalhada
Breiman define Random Forest como um conjunto de árvores dependentes de vetores aleatórios independentes, cujos votos são agregados para classificação. O artigo relaciona o erro de generalização à força das árvores individuais e à correlação entre elas, introduz estimativas out-of-bag e discute importância de variáveis. A seleção aleatória de atributos em cada divisão busca aumentar diversidade sem sacrificar excessivamente a capacidade preditiva.

## Método e escopo
Desenvolvimento teórico com demonstrações sobre convergência e limites de erro, seguido de experimentos em bases de classificação e regressão e comparação com AdaBoost.

## Resultados e contribuição
O erro converge à medida que o número de árvores cresce, e o desempenho depende do equilíbrio entre árvores fortes e pouco correlacionadas. Estimativas out-of-bag fornecem avaliação interna sem separar uma base adicional e permitem medir importância de atributos.

## Aplicação ao projeto
É a referência primária do Random Forest utilizado no projeto. Fundamenta a escolha do ensemble, a análise de importância das características textuais e o uso de mecanismos internos de avaliação, embora a avaliação oficial do artigo deva permanecer separada e sem vazamento.

## Limitações e cautelas
A afirmação de que aumentar árvores não causa sobreajuste refere-se ao limite do ensemble sob o desenho do método, não elimina risco de vazamento, hiperajuste de hiperparâmetros ou viés amostral. Importância por impureza pode favorecer variáveis com mais pontos de corte e deve ser interpretada com cautela.

## Uso seguro na redação
Utilizar esta referência apenas para sustentar afirmações compatíveis com seu desenho e escopo. Não extrapolar resultados numéricos para a base de chamados sem validação própria. Sempre manter a citação bibliográfica associada à afirmação teórica correspondente.
