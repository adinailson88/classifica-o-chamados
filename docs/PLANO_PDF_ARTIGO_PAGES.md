# Plano — PDF do artigo publicado no GitHub Pages

Registrado em 2026-07-23, a pedido do Adinailson: publicar uma versão em PDF do
rascunho do artigo/capítulo junto do painel no GitHub Pages, e (objetivo de mais
longo prazo) aproximar o texto do artigo dos dados vivos do painel.

## O que existe hoje

- **Workflow**: `.github/workflows/artigo_pdf.yml`. Converte
  `04_artigo/artigo_classificacao_chamados_v3.md` para
  `docs/artigo_classificacao_chamados.pdf` via `pandoc` + `xelatex` (imagem Docker
  `pandoc/extra`), e commita o PDF direto na branch `main` (`[skip ci]`, não
  reaciona outros workflows).
- **Gatilho**: push em `main` que altere o `.md` do artigo, ou disparo manual
  (`workflow_dispatch`). **Não** roda no cron de 30 min do `dashboard.yml` nem
  quando só os JSONs de `docs/dados/` mudam — ver limitação abaixo.
- **Link público**: `docs/index.html` (cabeçalho do painel) aponta para
  `artigo_classificacao_chamados.pdf`, ao lado da descrição do painel.
- Não usa credenciais nem lê a planilha — só lê o `.md` já versionado.

## O que este pipeline NÃO faz (limitação deliberada)

"Modelar o artigo de acordo com os dados do dashboard" tem duas leituras
diferentes, e só a primeira está implementada:

1. **Publicar um PDF sempre atualizado com o texto mais recente do artigo** —
   feito. Qualquer edição em `04_artigo/artigo_classificacao_chamados_v3.md`
   gera um novo PDF automaticamente.
2. **Reescrever sozinho os números citados no texto toda vez que os JSONs de
   `docs/dados/` mudarem** — **não implementado**. Isso exigiria um motor de
   substituição de números no meio da prosa (equivalente ao
   `generated_numbers.tex` do repositório `revisao-bibliografica`, mas operando
   sobre parágrafos em português, não sobre macros LaTeX isoladas), com risco
   real de reescrever um número errado sem revisão humana — o tipo de erro que
   a regra "não citar sem reconferir" do `PLANO_ARTIGO_CAPITULO.md` existe
   para evitar. Fica registrado como possível evolução futura, não como algo
   pendente desta rodada.

Na prática: o PDF sempre reflete o `.md` fielmente, mas **o `.md` ainda precisa
ser atualizado à mão** quando os números de `docs/dados/*.json` mudam — o
processo continua sendo "revalidar, depois editar o `.md`", como já registrado
em `PLANO_ARTIGO_CAPITULO.md`.

## Achado relacionado desta rodada (2026-07-23)

Ao tentar montar as tabelas 3–7 do artigo (ver "Estado desta rodada" em
`PLANO_ARTIGO_CAPITULO.md`), foi descoberto que `docs/dados/calibracao.json`
tinha `acerto_validado = 1,0` em **todas** as faixas de confiança — bug de
viés de seleção em `src/calibracao.py` (a métrica só contava linhas onde a
coluna N — CONFERÊNCIA IA — estava marcada, e essa coluna, no uso real, quase
só recebe "Correto"). Corrigido no commit `21258deb` (comparar contra a
categoria DECIDIDA pela memória M/N/P, a mesma verdade de
`avaliacao_final.py`, em vez da marcação bruta isolada de uma única coluna).
Regenerado via disparo manual do workflow `dashboard.yml`; números atuais (pós
correção) já são plausíveis (curva crescente de acerto com a confiança,
~96,8% na faixa ≥95%).

**Ainda não corrigido, mesmo problema estrutural**: o campo
`validacao_humana.matriz_ia_x_glpi` de `calibracao.json` continua comparando
diretamente as marcações brutas de M e N (não a verdade decidida), então
segue mostrando variância zero (`ia_ok_glpi_erro=0`, `ia_erro_glpi_ok=0`) pelo
mesmo viés de seleção. **Não usar esse campo na Tabela 4.3 (matriz de
confusão IA×GLPI) do artigo até ele passar por correção equivalente.**
