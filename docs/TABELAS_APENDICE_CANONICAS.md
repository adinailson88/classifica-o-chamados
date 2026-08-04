# Tabelas do apêndice, regeradas da rodada canônica

> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.

**Gerado em:** 04/08/2026 19:20  
**Origem:** `docs/dados/retreino_canonico_predicoes.csv`

## Critérios

- Tipo: familia da categoria, conforme src/tipo_manutencao.py.
- ABC: percentual acumulado de volume dentro do proprio tipo, corte A em 0.8 e B em 0.95; a categoria que cruza o corte pertence a classe que ela fecha.
- F1: F1 do LinearSVC por categoria, calculado sobre todos os pares para preservar falsos positivos vindos de fora.

## Tabela A1 — distribuição histórica sobre a base congelada

50 categorias, 14.060 chamados.

| Categoria histórica | Quantidade |
|:---|---:|
| Manutenção Preventiva > Ar condicionado split | 1.798 |
| Climatização > Ar condicionado split | 1.640 |
| Estrutura Predial > Alvenaria / Pisos / Estrutura | 1.302 |
| Hidrossanitária > Hidráulica | 1.282 |
| Manutenção Preventiva > Gerador | 1.215 |
| Estrutura Predial > Esquadrias, porta, portão e janelas | 977 |
| Elétrica > Instalações elétricas | 945 |
| Elétrica > Iluminação | 758 |
| Manutenção Preventiva > Quadros Elétricos | 578 |
| TI / Dados / Rede > Ponto de rede / fibra ótica / Wi-fi | 404 |
| Instalação de Acessórios e Mobiliário > Instalação/reparo de equipamentos (Suportes de TV, acessórios de banheiro e quadro branco) | 290 |
| Manutenção Preventiva > Reservatório | 279 |
| Manutenção Preventiva > Vistoria em Instalações | 247 |
| Outros > Erro de chamado | 245 |
| Estrutura Predial > Infiltração | 215 |
| Estrutura Predial > Telhados, calhas, rufos, etc. | 207 |
| Manutenção Preventiva > Ar condicionado central | 165 |
| Estrutura Predial > Forro | 146 |
| Manutenção Preventiva > Iluminação | 132 |
| Elétrica > Nobreak | 128 |
| Área Externa e Ambiental > Manutenção área externa / meio ambiente / Poda de árvore / Roçagem | 109 |
| Posto de trabalho > Contratação de Posto de trabalho | 102 |
| Manutenção Preventiva > Elevador | 86 |
| Suprimentos / Apoio Técnico > Materiais | 85 |
| Projetos e Reformas > Reforma | 83 |
| Manutenção Preventiva > Sistemas de combate a incêndio (extintores, hidrantes) | 66 |
| Estrutura Predial > Pintura | 58 |
| Instalação de Acessórios e Mobiliário > Placas de identificação | 54 |
| Manutenção Preventiva > Telhados, calhas, rufos, etc. | 44 |
| TI / Dados / Rede > Coleta de dados | 40 |
| Elétrica > Gerador | 38 |
| Hidrossanitária > Bomba | 38 |
| Climatização > Ar condicionado central | 37 |
| Manutenção Preventiva > Esgoto | 33 |
| Manutenção Preventiva > Hidráulica | 33 |
| Outros > Outros | 33 |
| Segurança contra Incêndio > Sistemas de combate a incêndio (extintores, hidrantes) | 29 |
| Projetos e Reformas > Projeto | 25 |
| Equipamentos de Transporte > Elevador | 22 |
| Elétrica > Subestação | 18 |
| Hidrossanitária > ETA / ETE | 16 |
| Suprimentos / Apoio Técnico > Limpeza de equipamentos, ambiente e mobiliário | 14 |
| Manutenção Preventiva > Poços artesianos | 13 |
| Manutenção Preventiva > Nobreak | 10 |
| Elétrica > Sistema Fotovoltaico (FV) | 7 |
| Área Externa e Ambiental > Drenagem | 4 |
| Estrutura Predial > Instalações Especiais (gás, ar comprimido, etc.) | 3 |
| Manutenção Preventiva > Aplicação cupinicida | 3 |
| Manutenção Preventiva > Bomba | 3 |
| Suprimentos / Apoio Técnico > Transporte | 1 |
| **Total geral** | **14.060** |

## Tabela A2 — categorias avaliadas na rodada canônica

41 categorias e 13.972 chamados. O F1 é do `linear_svc`.

| Categoria de referência | Tipo | n | % do tipo | Classe | F1 |
|:---|:-:|---:|---:|:-:|---:|
| **Preventiva** | **P** | **4.902** | **100,00** | | |
| Manutenção Preventiva > Ar condicionado split | P | 1.987 | 40,53 | A | 0,9972 |
| Manutenção Preventiva > Gerador | P | 1.208 | 24,64 | A | 0,9954 |
| Manutenção Preventiva > Quadros Elétricos | P | 578 | 11,79 | A | 0,9843 |
| Manutenção Preventiva > Reservatório | P | 318 | 6,49 | A | 0,9139 |
| Manutenção Preventiva > Vistoria em Instalações | P | 244 | 4,98 | B | 0,9419 |
| Manutenção Preventiva > Ar condicionado central | P | 168 | 3,43 | B | 0,9970 |
| Manutenção Preventiva > Iluminação | P | 132 | 2,69 | B | 0,9535 |
| Manutenção Preventiva > Elevador | P | 86 | 1,75 | B | 0,9655 |
| Manutenção Preventiva > Sistemas de combate a incêndio (extintores, hidrantes) | P | 66 | 1,35 | C | 0,8905 |
| Manutenção Preventiva > Telhados, calhas, rufos, etc. | P | 44 | 0,90 | C | 0,2162 |
| Manutenção Preventiva > Esgoto | P | 31 | 0,63 | C | 0,4286 |
| Manutenção Preventiva > Hidráulica | P | 27 | 0,55 | C | 0,0000 |
| Manutenção Preventiva > Poços artesianos | P | 13 | 0,27 | C | 1,0000 |
| **Corretiva** | **C** | **8.485** | **100,00** | | |
| Climatização > Ar condicionado split | C | 1.448 | 17,07 | A | 0,9550 |
| Hidrossanitária > Hidráulica | C | 1.263 | 14,89 | A | 0,8651 |
| Estrutura Predial > Alvenaria / Pisos / Estrutura | C | 1.138 | 13,41 | A | 0,4610 |
| Estrutura Predial > Esquadrias, porta, portão e janelas | C | 1.003 | 11,82 | A | 0,8712 |
| Elétrica > Instalações elétricas | C | 909 | 10,71 | A | 0,7248 |
| Elétrica > Iluminação | C | 764 | 9,00 | A | 0,8901 |
| TI / Dados / Rede > Ponto de rede / fibra ótica / Wi-fi | C | 412 | 4,86 | A | 0,7173 |
| Instalação de Acessórios e Mobiliário > Instalação/reparo de equipamentos (Suportes de TV, acessórios de banheiro e quadro branco) | C | 405 | 4,77 | B | 0,4730 |
| Estrutura Predial > Telhados, calhas, rufos, etc. | C | 203 | 2,39 | B | 0,4962 |
| Estrutura Predial > Infiltração | C | 202 | 2,38 | B | 0,6493 |
| Estrutura Predial > Forro | C | 168 | 1,98 | B | 0,7746 |
| Elétrica > Nobreak | C | 150 | 1,77 | B | 0,7855 |
| Área Externa e Ambiental > Manutenção área externa / meio ambiente / Poda de árvore / Roçagem | C | 103 | 1,21 | C | 0,6288 |
| Instalação de Acessórios e Mobiliário > Placas de identificação | C | 69 | 0,81 | C | 0,6494 |
| Estrutura Predial > Pintura | C | 60 | 0,71 | C | 0,5890 |
| Elétrica > Gerador | C | 43 | 0,51 | C | 0,7723 |
| Hidrossanitária > Bomba | C | 43 | 0,51 | C | 0,7238 |
| Climatização > Ar condicionado central | C | 33 | 0,39 | C | 0,7324 |
| Segurança contra Incêndio > Sistemas de combate a incêndio (extintores, hidrantes) | C | 29 | 0,34 | C | 0,4815 |
| Equipamentos de Transporte > Elevador | C | 21 | 0,25 | C | 0,7692 |
| Elétrica > Subestação | C | 19 | 0,22 | C | 0,6061 |
| **Não manutenção** | **NM** | **585** | **100,00** | | |
| Outros > Erro de chamado | NM | 258 | 44,10 | A | 0,3978 |
| Posto de trabalho > Contratação de Posto de trabalho | NM | 102 | 17,44 | A | 0,9561 |
| Suprimentos / Apoio Técnico > Materiais | NM | 96 | 16,41 | A | 0,4790 |
| Projetos e Reformas > Reforma | NM | 65 | 11,11 | A | 0,2407 |
| Outros > Outros | NM | 28 | 4,79 | B | 0,3404 |
| Projetos e Reformas > Projeto | NM | 23 | 3,93 | B | 0,0000 |
| Suprimentos / Apoio Técnico > Limpeza de equipamentos, ambiente e mobiliário | NM | 13 | 2,22 | C | 0,0909 |

### Categorias fora das partições

9 categorias e 88 linhas ficaram fora por não sustentarem as cinco dobras.

| Categoria de referência | Linhas | Motivo |
|:---|---:|:---|
| TI / Dados / Rede > Coleta de dados | 40 | ausente de ao menos uma dobra apos o sorteio, na rodada 2 |
| Hidrossanitária > ETA / ETE | 15 | ausente de ao menos uma dobra apos o sorteio, na rodada 2 |
| Manutenção Preventiva > Nobreak | 9 | ausente de ao menos uma dobra apos o sorteio, na rodada 2 |
| Elétrica > Sistema Fotovoltaico (FV) | 7 | ausente de ao menos uma dobra apos o sorteio, na rodada 1 |
| Estrutura Predial > Instalações Especiais (gás, ar comprimido, etc.) | 5 | ausente de ao menos uma dobra apos o sorteio, na rodada 1 |
| Área Externa e Ambiental > Drenagem | 4 | 4 grupos textuais distintos, insuficientes para 5 dobras |
| Manutenção Preventiva > Aplicação cupinicida | 3 | 3 grupos textuais distintos, insuficientes para 5 dobras |
| Manutenção Preventiva > Bomba | 3 | 3 grupos textuais distintos, insuficientes para 5 dobras |
| Suprimentos / Apoio Técnico > Transporte | 2 | 2 grupos textuais distintos, insuficientes para 5 dobras |

## Proveniência

- Script: `src/tabelas_apendice_canonicas.py`.
- Nenhuma escrita foi realizada na planilha nem no artigo.
