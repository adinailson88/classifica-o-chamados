# Migração da categoria de equipamentos e acessórios

A categoria `Instalação de Acessórios e Mobiliário > Instalação/Reparo de Equipamentos, Acessórios e Mobiliários` foi renomeada no Helpdesk/GLPI para `Instalação/reparo de equipamentos (Suportes de TV, acessórios de banheiro e quadro branco)`.

A categoria antiga e a categoria nova devem ser tratadas como a mesma categoria operacional quando houver evidência de equivalência. O critério preferencial é o ID próprio da categoria no GLPI, por exemplo `itilcategories_id`, `categoria_id`, `id_categoria`, `categoria_glpi_id` ou campo equivalente. O ID do chamado (`id`, `ID Chamado`, `id_chamado`) não comprova equivalência taxonômica.

Se o repositório `classificacao-chamados` não contiver ID próprio da categoria GLPI, a rotina registra a limitação e só permite validação textual quando o operador autorizar explicitamente. Nesse caso, a evidência mínima é o aparecimento do nome novo nos dados operacionais ou artefatos atualizados e o desaparecimento do nome antigo dos dados operacionais principais.

A rotina é manual, excepcional e idempotente. Ela fica preservada em `scripts/migracoes/migrar_categoria_equipamentos_acessorios.py` e pode ser executada via workflow `migracao_categoria_equipamentos_acessorios.yml`. Ela não deve virar workflow periódico.

Comando local de diagnóstico:

```bash
python scripts/migracoes/migrar_categoria_equipamentos_acessorios.py --relatorio docs/RELATORIO_MIGRACAO_CATEGORIA_EQUIPAMENTOS_ACESSORIOS.md --validar-por-texto-quando-sem-id
```

Comando local de aplicação, somente depois de revisar o relatório:

```bash
python scripts/migracoes/migrar_categoria_equipamentos_acessorios.py --aplicar --relatorio docs/RELATORIO_MIGRACAO_CATEGORIA_EQUIPAMENTOS_ACESSORIOS.md --validar-por-texto-quando-sem-id
```

Se o relatório indicar que o nome antigo ainda aparece e o nome novo ainda não apareceu, a decisão correta é não aplicar a migração. Se nomes antigo e novo aparecerem simultaneamente sem ID de categoria, a rotina deve gerar alerta e bloquear consolidação automática.
