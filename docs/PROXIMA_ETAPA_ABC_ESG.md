# Prompt de continuação — curva ABC e recorte preventiva/corretiva

Cole o bloco abaixo em um chat novo do Claude Code, aberto na raiz do
repositório `classificacao-chamados`.

---

## CONTEXTO

Repositório: https://github.com/adinailson88/classificacao-chamados
Diretório local: `C:\Users\adina\repos\classificacao-chamados`
Doutorado no PPG Biossistemas/UFSB. A base validada de chamados GLPI alimenta o
artigo em `04_artigo/artigo_classificacao_chamados_v3.md`.

Pipeline: GLPI → `glpi-google-sheets-sync` → planilha `CHAMADOS` → IMPORTRANGE →
planilha do experimento → GitHub Actions → JSONs em `docs/dados/` → painel
(GitHub Pages) e artigo.

Planilha do experimento, aba principal `CHAMADOS_ESQUELETO_REDUZIDO`:
https://docs.google.com/spreadsheets/d/1lohPUQOgxzt_DMxnNLKMxnieZq1sVmh4uwBLbbgvfiQ/edit?gid=1090243921

### Estado da base (corte de 01/08/2026)

14.058 chamados, conferência humana integral (0 pendentes, 0 anomalias):
13.452 com a categoria do GLPI confirmada e 606 corrigidos manualmente, o que
dá taxa de erro do rótulo histórico de 4,3%. São 50 categorias históricas em
uso (folhas com `>`), mais 1 raiz residual com 2 chamados, em 14 famílias.

A base é viva: a planilha puxa do GLPI continuamente. O artigo declara corte
por data de abertura, até 1º de agosto de 2026. Chamados de agosto em diante
(o primeiro é `2026080002`) ficam fora do corte e NÃO devem ser incorporados
aos números do artigo sem refazer a cadeia inteira.

### Números vigentes (n = 14.058, acerto validado)

| Modelo | Acerto | IC95% | F1 macro |
|---|---|---|---|
| LinearSVC | 0,8198 | 0,8138–0,8260 | 0,5567 |
| SGD | 0,8013 | 0,7949–0,8079 | 0,5598 |
| Extra Trees | 0,7984 | 0,7920–0,8053 | 0,4967 |
| Regressão Logística | 0,7963 | 0,7899–0,8030 | 0,5549 |
| Random Forest | 0,7897 | 0,7834–0,7966 | 0,4700 |
| LSTM | 0,7106 | 0,7032–0,7182 | 0,4017 |
| Naive Bayes | 0,7088 | 0,7014–0,7164 | 0,2382 |

LinearSVC lidera (McNemar contra o 2º: p = 4,8×10⁻¹⁶). Concordância histórica
do LinearSVC: 0,8049. Held-out comum (983 validados): BERTimbau 0,6785 e
LinearSVC 0,6734, sem significância. Custo de treino na base inteira:
LinearSVC 2,68 s, LSTM 133,65 s, BERTimbau 161 a 304 min.

O BERTimbau tem 9.507 predições contra 14.058 dos demais e por isso está fora
do ranking principal. Não o inclua em comparação direta.

## TAREFA

Produzir três recortes de F1, além do global que já existe, e levá-los à
planilha, ao painel e depois ao artigo.

1. **F1 global** (já existe: `f1_macro` em `docs/dados/matriz_confusao.json`).
2. **F1 por tipo de manutenção**, separando preventiva de corretiva.
3. **Curva ABC das categorias DENTRO de cada tipo**, com F1 por classe A, B e C.
4. **Curva ABC global**, com F1 por classe (já implementado, ver abaixo).

O objetivo declarado pelo pesquisador: a separação preventiva/corretiva será
usada futuramente para o argumento de ESG na tese. No artigo, entra como
avaliação; a ligação com ESG fica para a tese.

### O que já está pronto

`src/curva_abc_categorias.py` e `tests/test_curva_abc_categorias.py`, com 16
testes passando. Já faz:
- `classificar_abc(suportes, corte_a=0.80, corte_b=0.95)`: ordena por volume e
  atribui classe pelo percentual acumulado. A categoria que cruza o corte
  pertence à classe que ela fecha, de modo que A é o menor conjunto que cobre
  ao menos 80% do volume.
- `f1_por_classe(linhas_abc, f1_por_categoria)`: F1 macro (média simples)
  dentro de cada classe, mais o global. Categoria sem F1 conta como zero.
- `extrair_do_matriz(matriz)`: lê suporte e F1 por categoria de
  `docs/dados/matriz_confusao.json`. O suporte vem do modelo de MAIOR cobertura,
  para não tomar como referência o `transformer_ft`, que é parcial.
- `montar(matriz)`: junta tudo e devolve o dicionário publicável.
- CLI com `--aplicar` para gravar a aba, `--json` para o artefato.

**Falta**: a separação preventiva/corretiva, a curva ABC dentro de cada tipo, a
escrita efetiva da aba, o workflow e o consumo no painel.

### Classificador de tipo que já existe

`src/exportar_dashboard.py:79`:

```python
def tipo_manutencao(categoria):
    """Classifica o chamado pelo prefixo da categoria historica."""
    normalizada = _normalizar_categoria(categoria)
    if normalizada.startswith("manutencao preventiva >") or normalizada.startswith("manutencao preventiva>"):
        return "Preventiva"
    return "Corretiva"
```

Há testes em `tests/test_tipo_manutencao.py`. Considere extrair essa função
para um módulo próprio em vez de duplicá-la, já que passará a ser usada por
mais de um script.

**Atenção a um ponto de julgamento**: pelo critério atual, tudo que não começa
com `Manutenção Preventiva >` é Corretiva, inclusive famílias como `Projetos e
Reformas`, `Posto de trabalho`, `Suprimentos / Apoio Técnico` e `Outros > Erro
de chamado`, que não são manutenção corretiva em sentido estrito. Levante isso
com o pesquisador antes de consolidar, porque afeta o argumento de ESG. A
família `Manutenção Preventiva` responde por 4.702 dos 14.058 chamados.

### Diagnóstico do F1 que motivou esta tarefa

O F1 macro do LinearSVC é 0,5567 contra acurácia de 0,8198. A perda concentra-se
na cauda: **13 categorias com F1 igual a zero**, quase todas com suporte de 2 a
7 chamados, valores em que nenhum classificador supervisionado aprende a classe
e o k-fold garante que ela nunca esteve no treino. Cada zero custa 1/57 da média.

Efeito de recortar por suporte mínimo (LinearSVC):

| Recorte | F1 macro | Categorias |
|---|---|---|
| Todas | 0,5567 | 57 |
| Suporte ≥ 10 | 0,6603 | 44 |
| Suporte ≥ 30 | 0,7105 | 35 |
| Suporte ≥ 100 | 0,7851 | 22 |

Duas categorias volumosas com F1 baixo, cuja causa é taxonômica e não do
modelo: `Estrutura Predial > Alvenaria / Pisos / Estrutura` (suporte 1.137,
F1 0,4781) e `Instalação de Acessórios e Mobiliário > Instalação/reparo de
equipamentos` (suporte 362, F1 0,3956, mais uma variante de grafia com suporte
45 e F1 zero). As duas grafias nomeiam a mesma coisa e deveriam ser unificadas.

A taxonomia tem pares que nomeiam o mesmo objeto em famílias diferentes:
`Ar condicionado split` aparece em Manutenção Preventiva (1.795) e em
Climatização (1.640); o mesmo ocorre com `Ar condicionado central`, `Gerador`,
`Nobreak`, `Elevador`, `Telhados` e `Sistemas de combate a incêndio`. O critério
que os separa é justamente preventivo contra corretivo, o que torna a tarefa
desta etapa diretamente ligada ao maior componente de erro medido.

## ENTREGÁVEIS, NESTA ORDEM

1. Estender `src/curva_abc_categorias.py` com o recorte por tipo de manutenção
   e a curva ABC dentro de cada tipo. Manter a lógica pura e testável offline.
2. Gravar a aba na planilha (nome sugerido: `CURVA_ABC_CATEGORIAS`), com
   workflow próprio, dry-run por padrão.
3. Consumir no painel (`docs/index.html` e `src/exportar_dashboard.py`).
4. Só então levar ao artigo.

## REGRAS DO PROJETO (não negociáveis)

- **Indexar SEMPRE por `id_chamado`, NUNCA por número de linha.** Em 02/08/2026
  onze pontos do código foram corrigidos por causa disso. Quando a base muda de
  tamanho, casar por linha compara a predição de um chamado com a verdade de
  outro, sem gerar erro, devolvendo número plausível e falso. Regressão fixada
  em `tests/test_avaliacao_final_indexa_por_id.py`.
- **Nenhuma escrita na planilha sem dry-run apresentado antes**, com contagens,
  intervalo, primeiro e último ID e distribuição das alterações, e sem
  autorização explícita do pesquisador.
- **Nunca alterar as colunas A–F** (fórmula IMPORTRANGE), **K e L** (fórmula),
  nem **M, N, O, P e Q** (conferência humana). A coluna N está aposentada da
  derivação da verdade desde 01/08/2026; não usar.
- **A verdade vem só de M e Q**: `M='Correto'` trava a categoria do GLPI (C);
  `M='Errado'` com Q preenchida trava Q. Use
  `dv.carregar_decisoes(..., chave="id", so_conferencia_glpi=True)`.
- **Predições para avaliação nunca com memória validada.** O multimodelo roda
  com `--sem-memoria-validada`; sem isso a conferência humana entra no treino e
  o acerto sobe para 0,98, que é vazamento. O classificador de produção (Etapa 1)
  segue usando a memória, que é onde ela faz sentido.
- **Não inventar resultado de workflow.** Se não pôde rodar, dizer qual e por quê.
- Suíte: `python -m pytest tests/ -q` (249 testes hoje). Todo comportamento novo
  entra com teste.

## ESTILO DO ARTIGO (quando chegar nele)

- **Nunca usar travessão em prosa.** O pesquisador considera que "dá pinta de
  escrita por IA". Usar vírgula, parêntese ou ponto.
- **Nunca terminar parágrafo com fragmento curto de remate em antítese**, do tipo
  "é piso, não teto" ou "vantagem de protocolo, não de modelo". Mesmo motivo.
- Acionar a skill `meu-estilo-textual` ANTES de redigir, não depois.
- Alvo medido no texto atual: média de 25 palavras por frase, zero travessões em
  prosa, voz impessoal, citações ABNT autor-data integradas ao parágrafo.
- **Só dados e números mudam** no artigo, salvo decisão explícita em contrário.
  Não narrar auditorias, rodadas anteriores nem versões descartadas.
- O artigo é autossuficiente: não nomear as técnicas do Eixo 2 da tese (SES,
  ARIMA, AHP-TOPSIS). A ligação com a governança preditiva é feita em termos
  gerais na Introdução e na Subseção 5.4.

## O QUE O ARTIGO JÁ SUSTENTA

Contribuição metodológica: separar concordância com o histórico de acerto
validado por conferência humana. Achados: taxa de erro do rótulo histórico de
4,3%; empate entre modelo linear de 2,68 s e transformador de 161 a 304 min;
parte do erro é da taxonomia e não do modelo (pares simétricos de confusão).
Já existe a Subseção 4.10 de análise de erro, onde o recorte ABC e por tipo
provavelmente se encaixa.

Estado do artigo: PR #160 aberto, não mergeado, com todos os números do corte
de 14.058.
