# Classificação de Chamados

## [Abrir o artigo em PDF](https://adinailson88.github.io/classificacao-chamados/artigo_classificacao_chamados.pdf)

[Visualizar o painel](https://adinailson88.github.io/classificacao-chamados/) · [Acompanhar workflows](https://github.com/adinailson88/classificacao-chamados/actions) · [Abrir o texto-fonte do artigo](04_artigo/artigo_classificacao_chamados_v3.md)

Repositório experimental para classificação e reclassificação automática de chamados de manutenção predial, com validação humana, comparação de modelos e publicação de resultados em painel e artigo científico.

## Prompt para continuar a rodada do BERTimbau

Copie o bloco abaixo em uma nova conversa depois que o workflow `Transformer fine-tuning (BERTimbau)` terminar.

<details>
<summary><strong>Abrir prompt de continuidade</strong></summary>

```text
Repositório: adinailson88/classificacao-chamados.

Continue a rodada do BERTimbau iniciada pelos PRs #84 e #85.

Antes de alterar qualquer arquivo, leia:
- AGENTS.md;
- CONTEXTO.md;
- PLANO_ARTIGO_CAPITULO.md, especialmente "Estado desta rodada";
- .github/workflows/temporario_rodada_bertimbau.yml;
- .github/workflows/transformer_ft.yml.

1. Localize a execução de transformer_ft.yml iniciada por workflow_dispatch com modo=auto, acao=comparar, forcar_treino=true e limite=1000. Registre run ID, horários, conclusão, jobs e logs relevantes.
2. Se falhou ou foi cancelada, identifique a causa exata e corrija somente o necessário em branch + PR. Não execute as etapas seguintes antes de um treino concluído com sucesso.
3. Se concluiu com sucesso, confirme que docs/dados/bertimbau_training_state.json registra status=ok e que docs/dados/bertimbau_metr_full.json corresponde ao run. Não trate a janela held-out de 1.000 registros como resultado sobre os 13.965 chamados.
4. Verifique se a sequência automática concluiu, nesta ordem: avaliacao_final.yml, estatistica.yml e consolidar_validacao_classificacao_2.yml com aplicar=true. Dispare apenas o passo ausente ou que falhou.
5. Valide os JSONs vigentes usados nas Tabelas 1, 2 e 3: avaliacao_final.json, estatistica.json, calibracao.json, bertimbau_training_state.json, bertimbau_metr_full.json e estado_automacao.json. Confira denominadores, timestamps, decididos, restritos e matriz_ia_x_glpi.
6. Avalie separadamente se é necessário executar acao=reclassificar_validados para obter concordância do BERTimbau sobre toda a base validada. Antes, confirme se o modelo treinado é persistido e reutilizável; não provoque novo treino sem necessidade.
7. Reconcile os resultados com o artigo e o painel. Atualize apenas números, tabelas, figuras e afirmações efetivamente afetados. Verifique especialmente Tabelas 1–3, Subseção 4.3, Resumo, Abstract, Discussão, Limitações e Considerações Finais.
8. Regere e valide o PDF. Depois, remova o workflow temporario_rodada_bertimbau.yml e este prompt do README, atualize CONTEXTO.md e substitua "Estado desta rodada" no PLANO_ARTIGO_CAPITULO.md.

Regras:
- trabalhar em branch + Pull Request, nunca diretamente em main;
- nunca apagar ou alterar indevidamente as colunas M, N, P ou Q da planilha principal;
- qualquer escrita em planilha viva exige dry-run documentado antes de --aplicar;
- não inventar resultados de workflow ou da planilha;
- antes de commits de código, executar python -m unittest discover -s tests e python -m py_compile nos arquivos alterados;
- um commit por etapa lógica.

Ao final, apresente uma tabela com etapa, workflow/run, resultado, arquivos atualizados, números principais e pendências.
```

</details>

## Objetivo do projeto

O projeto avalia modelos de aprendizagem de máquina para apoiar a classificação de chamados de manutenção predial. O experimento mantém separadas três dimensões:

- classificação em relação ao histórico administrativo;
- acerto em relação à decisão validada por conferência humana;
- reclassificação e potencial correção da taxonomia histórica.

Os resultados alimentam o painel público e o artigo/capítulo da tese em Biossistemas Construídos.

## Componentes principais

| Componente | Local |
|---|---|
| Artigo em Markdown | [`04_artigo/artigo_classificacao_chamados_v3.md`](04_artigo/artigo_classificacao_chamados_v3.md) |
| Artigo em PDF | [`docs/artigo_classificacao_chamados.pdf`](docs/artigo_classificacao_chamados.pdf) |
| Painel público | [`docs/index.html`](docs/index.html) |
| Dados agregados | [`docs/dados/`](docs/dados/) |
| Plano e estado da pesquisa | [`PLANO_ARTIGO_CAPITULO.md`](PLANO_ARTIGO_CAPITULO.md) |
| Contexto técnico atual | [`CONTEXTO.md`](CONTEXTO.md) |
| Regras do repositório | [`AGENTS.md`](AGENTS.md) |
| Código do experimento | [`src/`](src/) |
| Testes | [`tests/`](tests/) |

## Workflows principais

| Workflow | Função |
|---|---|
| `transformer_ft.yml` | Fine-tuning e avaliação do BERTimbau |
| `avaliacao_final.yml` | Acerto validado, intervalos e análise de erros |
| `estatistica.yml` | Estatísticas e comparações entre modelos |
| `consolidar_validacao_classificacao_2.yml` | Memória validada, calibração e matriz IA × histórico |
| `dashboard.yml` | Atualização do painel e dos dados publicados |
| `artigo_pdf.yml` | Geração do PDF a partir do Markdown |

## Regras operacionais

1. Alterações de código e documentação devem ser feitas em branch e Pull Request.
2. Escritas na planilha exigem opção explícita de aplicação e, quando cabível, dry-run anterior.
3. As colunas de conferência humana devem ser preservadas, especialmente M, N, P e Q.
4. Resultados do artigo devem ser conferidos nos JSONs vigentes antes de qualquer atualização textual.
5. O histórico detalhado das rodadas não deve ser acumulado neste README; deve permanecer em `CONTEXTO.md`, `PLANO_ARTIGO_CAPITULO.md`, commits e Pull Requests.

## Autoria e contexto

Pesquisa de Adinailson Guimarães de Oliveira, doutorando no Programa de Pós-Graduação em Biossistemas Construídos da Universidade Federal do Sul da Bahia, com aplicação em manutenção predial orientada por dados e governança preditiva da infraestrutura pública.
