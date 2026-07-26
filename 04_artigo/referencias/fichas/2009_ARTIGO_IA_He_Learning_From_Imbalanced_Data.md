# 2009 ARTIGO IA He Learning From Imbalanced Data

## Referência
HE, Haibo; GARCIA, Edwardo A. Learning from Imbalanced Data. IEEE Transactions on Knowledge and Data Engineering, v. 21, n. 9, p. 1263–1284, 2009. DOI: 10.1109/TKDE.2008.239.

**Tipo documental:** Artigo científico de revisão  
**Pasta temática:** `02_IA_e_CienciaDeDados`  
**Texto completo:** [Google Drive](https://drive.google.com/file/d/1q6WscrPky3RvA4o3tc0yA7AdhwwpDOcI/view)  
**Palavras-chave:** desbalanceamento de classes; classificação; reamostragem; custo sensível; métricas; classe minoritária

## Síntese detalhada
O artigo revisa o problema de aprendizado com dados desbalanceados, no qual uma ou mais classes possuem representação muito inferior às demais. Os autores distinguem desbalanceamento relativo, raridade absoluta, sobreposição entre classes, pequenos subconceitos e dificuldades internas às próprias classes. São revisadas soluções de reamostragem, aprendizado sensível a custos, métodos baseados em kernel e aprendizado ativo, além de métricas mais informativas do que a acurácia global.

## Método e escopo
Revisão crítica do estado da arte acompanhada de taxonomia dos tipos de desbalanceamento, estratégias algorítmicas e critérios de avaliação.

## Resultados e contribuição
O artigo demonstra que a razão entre classes, isoladamente, não explica toda a dificuldade. Sobreposição, ruído e baixa representatividade da minoria podem ser mais determinantes. Acurácia agregada pode ocultar desempenho quase nulo em classes raras; curvas precisão–revocação, ROC, custos e medidas por classe são necessárias.

## Aplicação ao projeto
É central para o artigo de classificação de chamados, pois as categorias do GLPI possuem frequências desiguais. Sustenta macro-F1, recall por classe, matrizes de confusão e análise específica de categorias raras, bem como cautela na interpretação de alta acurácia global.

## Limitações e cautelas
A revisão enfatiza principalmente problemas binários, embora discuta extensões multiclasse. Técnicas de reamostragem podem causar sobreajuste ou distorcer probabilidades. A escolha de estratégia deve considerar o objetivo operacional e os custos reais de cada erro.

## Uso seguro na redação
Utilizar esta referência apenas para sustentar afirmações compatíveis com seu desenho e escopo. Não extrapolar resultados numéricos para a base de chamados sem validação própria. Sempre manter a citação bibliográfica associada à afirmação teórica correspondente.
