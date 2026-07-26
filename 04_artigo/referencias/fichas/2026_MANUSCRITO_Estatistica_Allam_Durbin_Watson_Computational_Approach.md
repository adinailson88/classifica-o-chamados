# 2026 MANUSCRITO Estatistica Allam Durbin Watson Computational Approach

## Referência
ALLAM, Ishraga Mustafa Awad. Implementation and Analysis of the Durbin-Watson Statistic for Autocorrelation Detection in Regression Models: A Computational Approach. Manuscrito independente, 2026.

**Tipo documental:** Manuscrito independente  
**Pasta temática:** `03_Predicao_Custos_e_Estatistica`  
**Texto completo:** [Google Drive](https://drive.google.com/file/d/1gwpJwY1nPCBB_ziBNZaGO8_kaeKYoB4W/view)  
**Palavras-chave:** Durbin-Watson; autocorrelação; resíduos; regressão OLS; séries temporais; programação C

## Síntese detalhada
O manuscrito apresenta uma implementação em linguagem C da estatística Durbin–Watson para detectar autocorrelação de primeira ordem em resíduos de modelos de regressão. O programa calcula a estatística, estima aproximadamente o coeficiente de autocorrelação, aceita entrada manual ou por arquivo e produz interpretações baseadas em valores críticos aproximados. O texto enfatiza uso educacional e diagnóstico de pressupostos de mínimos quadrados.

## Método e escopo
Descrição computacional do algoritmo, análise de complexidade, tratamento de erros e exemplos de interpretação. O método usa a razão entre a soma dos quadrados das diferenças consecutivas dos resíduos e a soma dos quadrados dos resíduos.

## Resultados e contribuição
A implementação é linear em relação ao número de resíduos e explicita regiões de decisão para autocorrelação positiva, negativa, ausência de evidência e resultado inconclusivo. O próprio manuscrito reconhece que valores críticos aproximados não substituem tabelas exatas ou bibliotecas estatísticas consolidadas.

## Aplicação ao projeto
Pode funcionar como apoio didático para explicar a estatística utilizada na seção de robustez do artigo. A referência principal do teste, contudo, deve continuar sendo Durbin e Watson ou literatura estatística revisada por pares.

## Limitações e cautelas
Não foi identificada publicação em periódico ou conferência no documento. Os valores críticos são simplificados e podem produzir interpretações inadequadas. O teste é voltado a resíduos de regressão ordenados e não se aplica automaticamente a sequências de acertos/erros de classificadores sem uma formulação estatística apropriada. Não deve ser usado como única base teórica.

## Uso seguro na redação
Utilizar esta referência apenas para sustentar afirmações compatíveis com seu desenho e escopo. Não extrapolar resultados numéricos para a base de chamados sem validação própria. Sempre manter a citação bibliográfica associada à afirmação teórica correspondente.
