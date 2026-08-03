# 2022 ARTIGO IA Marcuzzo et al. A multi-level approach for hierarchical Ticket Classification

## Referência
MARCUZZO, Matteo; ZANGARI, Alessandro; GIUDICE, Lorenzo; GASPARETTO, Andrea; SCHIAVINATO, Michele; ALBARELLI, Andrea. A multi-level approach for hierarchical Ticket Classification. In: PROCEEDINGS OF THE 2022 COLING WORKSHOP: THE 8TH WORKSHOP ON NOISY USER-GENERATED TEXT (W-NUT 2022), 2022. Anais [...]. [S.l.]: Association for Computational Linguistics, 2022. p. 201–214. Disponível em: https://aclanthology.org/2022.wnut-1.22. Acesso em: 3 ago. 2026.

**Tipo documental:** Artigo em anais de workshop  
**Pasta temática:** `02_IA_e_Classificacao_de_Texto`  
**Texto completo:** PDF obtido na ACL Anthology e lido integralmente para esta ficha.  
**Palavras-chave:** classificação de chamados; classificação hierárquica; cauda longa; desbalanceamento de classes; corte por frequência mínima; BERT

## Síntese detalhada
O artigo trata da categorização automática de chamados de suporte organizados em hierarquia de dois níveis e propõe uma abordagem multinível que explora a dependência entre rótulo principal e subrótulo. Os autores constroem o conjunto Linux Bugs a partir do rastreador público de defeitos do kernel Linux, usando o campo "product" como rótulo principal e o campo "component" como subrótulo. Para evitar ambiguidade entre subrótulos homônimos de ramos distintos, os subrótulos são achatados de modo a preservar o ramo de origem, distinguindo por exemplo `Network_Other` de `Drivers_Other`.

## Método e escopo
Classificação hierárquica de texto com modelos de linguagem contextualizados baseados em BERT, comparando estratégias de sumarização do corpo do chamado. Cada chamado recebe exatamente um rótulo principal e um subrótulo. O pré-processamento descarta relatos sem texto de mensagem válido, aplica caixa baixa e concatena o título ao corpo da mensagem. As métricas reportadas, além da acurácia, são macro-médias calculadas por rótulo e depois promediadas, sem ponderação pela frequência de cada rótulo.

## Resultados e contribuição
Após o pré-processamento, o conjunto final reúne 35.050 descrições de defeitos, 17 rótulos de primeiro nível e 73 subrótulos, com média de 2.026 caracteres por chamado. A contribuição metodológica que interessa a este projeto não está no modelo, e sim no tratamento explícito da cauda longa: para reduzir o desbalanceamento de classes, os autores afirmam que "we discard all labels and sub-labels that appear less than 100 times" (Marcuzzo et al., 2022, p. 202), decisão declarada no corpo do artigo e não relegada a nota de rodapé.

## Aplicação ao projeto
É a referência que sustenta o critério de exclusão adotado no Passo 3 do plano de execução, implementado em `src/gerar_particoes_canonicas.py`. A correspondência é estrutural e não apenas temática: o domínio é classificação de chamados, a taxonomia é hierárquica de dois níveis com achatamento do ramo de origem — exatamente a forma de `Elétrica > Subestação` na base da UFSB — e o problema enfrentado é a mesma cauda longa de categorias com pouquíssimas ocorrências. O precedente autoriza declarar que retirar categorias sem suporte suficiente é prática corrente na literatura de classificação de chamados, e não expediente ad hoc deste trabalho. Convém registrar que o corte aqui adotado é bem menos agressivo: cinco grupos textuais distintos, contra cem ocorrências no artigo de referência.

## Limitações e cautelas
Os autores não justificam estatisticamente o valor 100 nem apresentam análise de sensibilidade ao limiar, de modo que a ficha autoriza citar a prática, não o número. Também não discutem o efeito da exclusão sobre a interpretação das métricas, questão que este projeto precisa tratar por conta própria ao declarar o denominador de categorias efetivamente avaliadas. O corte deles opera por frequência bruta de rótulos; o deste projeto opera por número de grupos textuais distintos, o que é critério diferente e mais restritivo em bases com muita duplicação. O protocolo de particionamento também difere: o artigo não usa validação cruzada agrupada por texto.

## Uso seguro na redação
Citar Marcuzzo et al. (2022) como precedente de exclusão de rótulos de baixa frequência em classificação hierárquica de chamados, sempre explicitando que o limiar deles é de cem ocorrências e que o critério deste trabalho é outro. Não atribuir a eles o uso de `StratifiedGroupKFold`, o agrupamento por texto idêntico nem qualquer recomendação sobre limiar ótimo. Não usar esta ficha para sustentar afirmações sobre desempenho de modelos, que dependeriam de leitura dirigida das tabelas de resultados.
