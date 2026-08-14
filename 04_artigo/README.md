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
- O corpo tem seis figuras e quatro tabelas principais; os apêndices contêm as Tabelas A1 a A3, e o material suplementar vai até S17 (S17 é provisória, ver Rodada 11 em `PLANO_ARTIGO_CAPITULO.md`).
- O Método tem seis subseções, na ordem 3.1 delineamento, corpus e referência revisada; 3.2 pré-processamento e representação; 3.3 modelos e configuração experimental; 3.4 validação, calibração e inferência; 3.5 reclassificação, utilidade e análises complementares; 3.6 reprodutibilidade, dados e aspectos institucionais.
- A Discussão tem quatro subseções, na ordem 5.1 adequação dos modelos e decisão multicritério; 5.2 auditoria do histórico, reclassificação e fluxo humano–IA; 5.3 limitações e alcance da evidência; 5.4 implicações para governança e continuidade da tese. As Considerações Finais têm cinco parágrafos curtos: contribuição, achados centrais, implicação operacional, limitações e continuidade da tese.
- O Passo 11 do plano de execução está concluído: o corpo científico está em 8.999 palavras (rotina única de contagem, ver `PLANO_ARTIGO_CAPITULO.md`), dentro da faixa-meta de 8.850 a 9.000. A Rodada 11 integrou ao Método (3.5), aos Resultados (4.5) e à Discussão (5.1) o resultado confirmatório do ensemble da Fase 2C (votação majoritária, votação suave ponderada e stacking não superaram o LinearSVC na mesma capacidade), com a nova Tabela S17 no material suplementar.
- As Figuras 2, 4 e 5 têm largura reduzida (Figura 2: `width=76%`; Figura 4: `width=73%`; Figura 5: `width=80%`); as Figuras 1, 3 e 6 estão em tamanho padrão.
- As Tabelas 1 a 4 do corpo e as Tabelas A1 a A3 do apêndice são floats LaTeX não divisíveis (`\begin{table}[!tbp]`/`[!tp]` com `tabularx`), não `longtable`; a legenda e o rótulo (`\caption`/`\label{tab:...}`) ficam dentro do float, com colunas flexíveis do tipo X e `\hsize`/`\linewidth` sincronizados. As Tabelas A1 a A3 usam `\footnotesize` e numeração própria A1/A2/A3, independente da sequência 1–4 do corpo.
- A lista de referências tem 45 entradas, todas citadas no corpo, sem duplicatas nem citação órfã.
- A avaliação temporal não foi executada por ausência de data no corpus, e a limitação está declarada na Subseção 5.3.
- PDF publicado com 21 páginas, dentro da faixa preferencial de 21 a 23, verificado por renderização real.
- **Rodada 10 (auditoria final de submissão) concluída**, registrada em [`docs/AUDITORIA_FINAL_SUBMISSAO.md`](../docs/AUDITORIA_FINAL_SUBMISSAO.md). Veredito: **apto com pendência documental** — o artigo ainda não está pronto para submissão. Próximas ações, por ordem de dependência: resolver a autorização institucional, a aprovação ética ou a dispensa formal junto à instituição; inserir no artigo as declarações de financiamento, conflito de interesses, contribuição dos autores e uso de inteligência artificial; regularizar a numeração do material suplementar (lacunas em S4 e, agora, na provisoriedade de S17) durante o empacotamento para o periódico escolhido.
- **Rodada 11 concluída**: integração editorial do resultado confirmatório do ensemble da Fase 2C (votação majoritária, votação suave ponderada, stacking comparados ao LinearSVC na mesma capacidade `K_f`; nenhuma combinação superou o baseline). Sem retreino de modelo-base, sem novo fit de stacking, sem execução de LSTM — todos os números vêm do manifesto já congelado da Execução Científica 1 da Fase 2C.
- O histórico detalhado das rodadas editoriais e técnicas permanece no Git e nos Pull Requests; não deve ser acumulado neste README.