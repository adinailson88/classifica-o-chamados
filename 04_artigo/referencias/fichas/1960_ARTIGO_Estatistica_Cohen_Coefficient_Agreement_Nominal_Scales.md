# 1960 ARTIGO Estatistica Cohen Coefficient of Agreement for Nominal Scales

## Referência
COHEN, Jacob. A coefficient of agreement for nominal scales. Educational and Psychological Measurement, v. 20, n. 1, p. 37–46, 1960. DOI: 10.1177/001316446002000104.

**Tipo documental:** Artigo científico  
**Pasta temática:** `01_Estatistica_e_Metodologia`  
**Texto completo:** não incorporado ao acervo do Drive institucional. Dados bibliográficos conferidos em fontes secundárias antes da submissão.  
**Palavras-chave:** kappa de Cohen; concordância entre avaliadores; escala nominal; correção pelo acaso; prevalência; marginais

## Síntese detalhada
Cohen propõe o coeficiente kappa como medida de concordância entre dois avaliadores que classificam as mesmas unidades em categorias nominais mutuamente exclusivas. O ponto de partida é a crítica ao acordo bruto, que soma os casos coincidentes sem descontar a coincidência que a simples distribuição marginal produziria por acaso. Kappa corrige essa distorção, ao dividir o excesso de acordo observado sobre o acordo esperado pela margem máxima de excesso possível. O coeficiente vale 1 sob concordância perfeita, 0 quando o acordo observado iguala o esperado por acaso e valores negativos quando o acordo fica abaixo do acaso.

## Método e escopo
Desenvolvimento estatístico com definição do estimador, dedução do erro padrão aproximado e teste de significância da hipótese nula de concordância ao acaso. O escopo original cobre dois avaliadores, categorias nominais não ordenadas e classificação independente das unidades. Extensões para mais de dois avaliadores, categorias ordenadas ou ponderação de discordâncias não fazem parte deste artigo e vêm da literatura posterior.

## Resultados e contribuição
O artigo estabelece kappa como padrão de medida de confiabilidade entre avaliadores em escala nominal e explicita que a magnitude depende das distribuições marginais dos dois classificadores. Cohen registra que kappa penaliza distribuições marginais assimétricas, de modo que dois conjuntos com o mesmo acordo bruto podem receber valores de kappa distintos conforme a prevalência das categorias.

## Aplicação ao projeto
É a referência primária do Kappa de Cohen empregado na Subseção 4.1 do artigo, que mede a concordância entre cada modelo e a categoria histórica dos chamados e obtém valores de 0,7881 para o LinearSVC a 0,6496 para o LSTM. Sustenta o argumento de que a concordância com o rótulo histórico é medida de alinhamento entre duas fontes de classificação, não medida de acerto, o que é a separação metodológica central do artigo. A leitura das faixas segue Landis e Koch (1977), que não integram este artigo.

## Limitações e cautelas
O coeficiente é sensível à prevalência das categorias e às marginais, e a taxonomia institucional de manutenção predial é fortemente desbalanceada. Um kappa moderado pode conviver com acordo bruto alto quando poucas categorias concentram a maior parte dos chamados. Por isso o artigo apresenta kappa ao lado do acordo bruto e registra a ressalva com apoio em Wongpakaran et al. (2013), fichada em [`FICHAS_REFERENCIAS_ESTATISTICAS.md`](../FICHAS_REFERENCIAS_ESTATISTICAS.md). O desenho original pressupõe dois avaliadores independentes; a comparação entre sete modelos e um histórico administrativo não satisfaz a independência em sentido estrito, já que os modelos partilham a mesma matriz de atributos.

## Uso seguro na redação
Citar Cohen (1960) apenas como origem do coeficiente e da correção pelo acaso. Não atribuir a este artigo faixas de interpretação qualitativa, kappa ponderado, kappa de Fleiss ou correções de prevalência, que pertencem a fontes posteriores. Manter a ressalva de sensibilidade às marginais sempre que o coeficiente for reportado sobre a taxonomia desbalanceada dos chamados.
