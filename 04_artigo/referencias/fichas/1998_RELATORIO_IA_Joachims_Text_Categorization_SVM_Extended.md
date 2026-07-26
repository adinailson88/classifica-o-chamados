# 1998 RELATORIO IA Joachims Text Categorization SVM Extended

## Referência
JOACHIMS, Thorsten. Text Categorization with Support Vector Machines: Learning with Many Relevant Features. Dortmund: Universität Dortmund, 1998. LS-8 Report 23, versão revisada.

**Tipo documental:** Relatório técnico  
**Pasta temática:** `02_IA_e_CienciaDeDados`  
**Texto completo:** [Google Drive](https://drive.google.com/file/d/1Nphjb74l1Qt83NHKVKErQQZ55I0vKRqF/view)  
**Palavras-chave:** SVM; classificação textual; alta dimensionalidade; TF-IDF; Reuters-21578; Ohsumed; aprendizado supervisionado

## Síntese detalhada
Joachims analisa por que máquinas de vetores de suporte são adequadas à classificação de textos: os vetores possuem alta dimensionalidade, são esparsos, contêm muitos atributos potencialmente relevantes e frequentemente admitem separação linear com boa margem. O relatório compara SVMs com Naive Bayes, Rocchio, k-NN e C4.5 em Reuters-21578 e Ohsumed, utilizando representação baseada em termos e ponderação IDF.

## Método e escopo
Estudo teórico-empírico. A justificativa pela minimização do risco estrutural é acompanhada de experimentos em duas coleções de referência, com diferentes kernels e quantidades de atributos.

## Resultados e contribuição
As SVMs apresentaram desempenho robusto e competitivo sem depender de seleção agressiva de atributos. O estudo argumenta que muitos termos de baixa posição no ranking ainda carregam informação, de modo que excluir atributos pode reduzir a capacidade discriminativa.

## Aplicação ao projeto
Fundamenta o uso de LinearSVC no projeto e ajuda a explicar seu desempenho em textos curtos de chamados. Também sustenta a manutenção de uma representação esparsa ampla e a comparação com modelos clássicos, em vez de presumir que arquiteturas profundas serão sempre superiores.

## Limitações e cautelas
A versão é um relatório técnico ampliado relacionado ao artigo de conferência de 1998 já presente no acervo. Os hashes são diferentes e o conteúdo/forma documental não são idênticos; portanto, não foi marcado como duplicata exata. Ainda assim, as duas versões não devem ser tratadas como evidências independentes.

## Uso seguro na redação
Utilizar esta referência apenas para sustentar afirmações compatíveis com seu desenho e escopo. Não extrapolar resultados numéricos para a base de chamados sem validação própria. Sempre manter a citação bibliográfica associada à afirmação teórica correspondente.
