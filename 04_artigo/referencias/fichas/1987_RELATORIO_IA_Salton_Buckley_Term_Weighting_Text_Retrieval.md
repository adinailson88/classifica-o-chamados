# 1987 RELATORIO IA Salton Buckley Term Weighting Text Retrieval

## Referência
SALTON, Gerard; BUCKLEY, Christopher. Term-Weighting Approaches in Automatic Text Retrieval. Ithaca: Cornell University, 1987. Technical Report 87-881. Versão publicada em Information Processing & Management, v. 24, n. 5, 1988.

**Tipo documental:** Relatório técnico  
**Pasta temática:** `02_IA_e_CienciaDeDados`  
**Texto completo:** [Google Drive](https://drive.google.com/file/d/1s28ybEyfo6AKbx642jbUxCshPqXBVvJb/view)  
**Palavras-chave:** TF-IDF; ponderação de termos; recuperação de informação; representação vetorial; similaridade cosseno; classificação textual

## Síntese detalhada
O relatório revisa e compara estratégias de ponderação de termos para recuperação automática de textos. Os autores mostram que representações baseadas em termos individuais, quando adequadamente ponderadas, podem superar estruturas linguísticas mais complexas. A formulação combina frequência do termo, frequência inversa de documentos e normalização pelo comprimento do vetor. O estudo discute a tensão entre revocação e precisão e fornece modelos de referência para experimentos posteriores.

## Método e escopo
Síntese teórica apoiada em evidências experimentais acumuladas no sistema SMART. São discutidas combinações de componentes locais, globais e de normalização em esquemas de ponderação de documentos e consultas.

## Resultados e contribuição
A contribuição mais duradoura é a consolidação de esquemas TF-IDF e da similaridade cosseno como referências para representação textual. Termos frequentes em um documento, mas raros na coleção, tendem a ser mais discriminativos; a normalização reduz o favorecimento de documentos longos.

## Aplicação ao projeto
Fundamenta diretamente a representação TF-IDF utilizada nos modelos clássicos do repositório de classificação de chamados. Também ajuda a explicar por que um baseline linear ou baseado em árvores pode ser competitivo em corpora textuais estruturados e relativamente pequenos.

## Limitações e cautelas
O relatório trata principalmente recuperação de informação, não classificação supervisionada multiclasse. A versão de 1987 é tecnicamente distinta do artigo de 1988 já armazenado no acervo; não é duplicata por hash, mas contém conteúdo substancialmente relacionado. Deve-se evitar contabilizá-las como duas evidências independentes sobre o mesmo achado.

## Uso seguro na redação
Utilizar esta referência apenas para sustentar afirmações compatíveis com seu desenho e escopo. Não extrapolar resultados numéricos para a base de chamados sem validação própria. Sempre manter a citação bibliográfica associada à afirmação teórica correspondente.
