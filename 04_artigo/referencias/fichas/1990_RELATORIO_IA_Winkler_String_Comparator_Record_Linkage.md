# 1990 RELATORIO IA Winkler String Comparator Record Linkage

## Referência
WINKLER, William E. String Comparator Metrics and Enhanced Decision Rules in the Fellegi-Sunter Model of Record Linkage. Washington, DC: U.S. Bureau of the Census, 1990. ERIC ED325505.

**Tipo documental:** Relatório técnico  
**Pasta temática:** `02_IA_e_CienciaDeDados`  
**Texto completo:** [Google Drive](https://drive.google.com/file/d/1R-JDTbErltGa9GEYvVLS8SpXjQ4F8Pnp/view)  
**Palavras-chave:** record linkage; comparação de strings; Jaro-Winkler; deduplicação; Fellegi-Sunter; correspondência probabilística

## Síntese detalhada
O relatório apresenta uma métrica de comparação de strings destinada a reconhecer correspondências parciais entre registros que não possuem identificadores únicos. O método amplia o comparador de Jaro e busca acomodar variações tipográficas em nomes e outros campos textuais. A comparação contínua é integrada ao modelo probabilístico de Fellegi-Sunter por meio de ajustes nos pesos de concordância e discordância. O trabalho utiliza registros do censo dos Estados Unidos e do Post Enumeration Survey para ilustrar como o tratamento de concordância parcial melhora o emparelhamento.

## Método e escopo
Desenvolvimento metodológico acompanhado de avaliação empírica. O relatório formula curvas de ajuste de pesos para diferentes níveis de similaridade textual e verifica seu efeito em bases com correspondências verdadeiras conhecidas.

## Resultados e contribuição
A principal contribuição é demonstrar que comparadores de strings podem ser incorporados às regras de decisão probabilísticas sem invalidar a estrutura de Fellegi-Sunter. A consideração de erros de digitação e transposições aumenta a eficácia do record linkage em relação à concordância exata.

## Aplicação ao projeto
É útil para detectar registros potencialmente duplicados ou equivalentes na base de chamados quando títulos, descrições, nomes de locais ou categorias apresentam pequenas variações. Também fundamenta procedimentos de deduplicação bibliográfica e normalização de textos antes de treinar classificadores.

## Limitações e cautelas
A qualidade dos pesos depende de amostras representativas de pares verdadeiros e falsos. Uma alta similaridade textual não comprova identidade sem contexto. O relatório é anterior a métodos modernos de embeddings e deve ser usado como fundamento clássico, não como demonstração de superioridade frente a técnicas atuais.

## Uso seguro na redação
Utilizar esta referência apenas para sustentar afirmações compatíveis com seu desenho e escopo. Não extrapolar resultados numéricos para a base de chamados sem validação própria. Sempre manter a citação bibliográfica associada à afirmação teórica correspondente.
