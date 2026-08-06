# Artigo — classificação automática de chamados

Este diretório contém o texto científico associado ao experimento de classificação e reclassificação de chamados de manutenção predial.

## Arquivos oficiais

| Arquivo | Função |
|---|---|
| `artigo_classificacao_chamados_v3.md` | Fonte editável e versionada do artigo/capítulo |
| `artigo_classificacao_chamados_v3.docx` | Arquivo original preservado como referência de proveniência e formatação |
| `figuras/` | Figuras vetoriais e imagens em 300 dpi geradas pelos scripts do repositório |
| `referencias/` | Fichas analíticas e links para o acervo bibliográfico |
| `../docs/artigo_classificacao_chamados.pdf` | PDF publicado no GitHub Pages |

PDF público: <https://adinailson88.github.io/classificacao-chamados/artigo_classificacao_chamados.pdf>

## Geração do PDF

O workflow `.github/workflows/artigo_pdf.yml` converte o Markdown em PDF e publica o resultado em `docs/`. Ele não acessa a planilha nem substitui automaticamente números no corpo do texto.

As figuras são geradas a partir dos JSONs versionados em `docs/dados/`. Para regenerá-las, use os scripts `src/gerar_figura*.py` e as tarefas correspondentes do workflow `lstm_artigo.yml`.

## Regra para atualização de resultados

Os números do artigo saem exclusivamente dos artefatos da rodada canônica, identificados pelo `hash_corpus` registrado em `PLANO_ARTIGO_CAPITULO.md`. Os JSONs do painel pertencem à execução legada e não alimentam o texto. Antes de alterar números ou conclusões:

1. conferir o `hash_corpus`, o timestamp e o denominador do artefato utilizado;
2. rodar `python src/matriz_proveniencia.py` e verificar que nenhum número legado permanece no texto;
3. atualizar em conjunto Resumo, Abstract, tabelas, figuras, resultados, discussão e conclusão;
4. regenerar o PDF e revisar visualmente a paginação.

Não atualizar uma tabela isoladamente quando o mesmo resultado aparece em outras partes do texto.

## Vocabulário obrigatório

A referência de avaliação é a **referência humana revisada**, produto de **auditoria administrativa de rótulo** conduzida por avaliador único, com a categoria histórica à vista. Não usar “verdade validada”, “verdade final”, “verdade absoluta” nem “acerto validado”. Os 4,25% são **taxa de alteração do rótulo histórico**, e não prevalência de erro. Não há segunda avaliação humana, cegamento ou adjudicação, e nenhuma medida de concordância entre avaliadores pode ser reportada. A análise de consistência interna dos grupos de texto idêntico não substitui avaliação independente nem estima concordância interavaliadores, e a contagem de grupos divergentes não delimita teto quantitativo de desempenho: esse teto exigiria calcular a distribuição dos rótulos dentro de cada grupo, o que não foi feito.

## Regra estatística obrigatória

A unidade de análise da inferência é o **grupo de texto normalizado idêntico**, e não a linha. Registros do mesmo grupo não são independentes, e o efeito de desenho medido fica entre 4,47 e 8,83. Intervalos vêm de bootstrap de conglomerados; testes pareados, de permutação por troca de sinal da diferença por grupo; o teste global, da estatística Q de Cochran contra distribuição de permutação por grupo. Não reintroduzir McNemar por linha como inferência do artigo; ele só é reportado, no suplemento, para dimensionar o estreitamento que a suposição de independência produzia.

Testes de normalidade, homogeneidade, outliers e VIF não pertencem ao corpo. Não usar Shapiro-Wilk como justificativa de escolha não paramétrica para dado categórico, VIF entre confianças como prova de que um *ensemble* é inútil, nem correlação entre confiança e acerto como prova de calibração.

O ganho líquido de reclassificação é `corrigidos − prejudicados` e permanece o resultado principal, mas nenhuma afirmação decisória pode omitir que ele supõe custos iguais. A qualificação usa razões adimensionais, nunca valor monetário.

## Regra sobre alcance temporal

O corpus congelado **não** tem data de abertura por chamado, veredito
`sem_variavel_temporal` registrado em `docs/dados/disponibilidade_temporal.json`
e reproduzível por `python src/auditar_disponibilidade_temporal.py`. Não há,
portanto, separação temporal entre treino, calibração e teste, e nenhuma
métrica de desempenho futuro pode ser produzida ou estimada. A validação
cruzada agrupada mede generalização entre grupos de texto normalizado dentro de
um mesmo corte de extração. Toda afirmação de uso prospectivo, de decisão
automática sobre chamado novo ou de recomendação operacional deve vir
condicionada a essa lacuna e acompanhada da exigência de monitoramento e
recalibração. Não escrever "corte por data de abertura": o corte é de extração.

## Estado atual

- O BERTimbau permanece fora da comparação principal por custo computacional medido, e figura como experimento exploratório no material suplementar.
- O corpo tem seis figuras e quatro tabelas principais; os apêndices contêm as Tabelas A1 a A3, e o material suplementar vai até S16.
- O Método tem seis subseções, na ordem 3.1 delineamento, corpus e referência revisada; 3.2 pré-processamento e representação; 3.3 modelos e configuração experimental; 3.4 validação, calibração e inferência; 3.5 reclassificação, utilidade e análises complementares; 3.6 reprodutibilidade, dados e aspectos institucionais.
- A Discussão tem quatro subseções, na ordem 5.1 adequação dos modelos e decisão multicritério; 5.2 auditoria do histórico, reclassificação e fluxo humano–IA; 5.3 limitações e alcance da evidência; 5.4 implicações para governança e continuidade da tese. As Considerações Finais têm cinco parágrafos curtos: contribuição, achados centrais, implicação operacional, limitações e continuidade da tese.
- O Passo 11 do plano de execução foi concluído nesta rodada (Rodada 8): o corpo científico está em 8.917 palavras, dentro da faixa-meta de 8.850 a 9.000, já com as correções da auditoria independente da PR #202.
- As Figuras 2, 4 e 5 tiveram a largura reduzida em 20% (Figura 2: `width=76%`; Figura 4: `width=73%`; Figura 5: `width=80%`); as Figuras 1, 3 e 6 não foram alteradas.
- As Tabelas 1 a 4 do corpo são floats LaTeX não divisíveis (`\begin{table}[!tbp]` com `tabularx`), e não mais `longtable`; a legenda e o rótulo (`\caption`/`\label{tab:...}`) ficam dentro do float, acima do `tabular`, e cada tabela usa ao menos uma coluna flexível do tipo X, com `\hsize` e `\linewidth` sincronizados; as Tabelas A1 a A3 do apêndice permanecem como pipe-table/`longtable` até a Rodada 9. A inspeção visual do PDF permanece necessária: a conversão evita a soma manual de colunas fixas, mas não substitui a checagem de legibilidade e conteúdo não separável no PDF renderizado.
- A lista de referências tem 45 entradas, todas citadas no corpo (quatro entradas já órfãs antes da Rodada 8 — COHEN, 1960; LANDIS; KOCH, 1977; MCNEMAR, 1947; WONGPAKARAN *et al.*, 2013 — foram removidas na segunda auditoria da PR #202).
- A avaliação temporal não foi executada por ausência de data no corpus, e a limitação está declarada na Subseção 5.3.
- A inspeção visual do PDF (figuras redimensionadas e tabelas não divisíveis) fica pendente para a Rodada 9, após o workflow gerar o PDF a partir do merge.
- O histórico detalhado das rodadas editoriais e técnicas permanece no Git e nos Pull Requests; não deve ser acumulado neste README.