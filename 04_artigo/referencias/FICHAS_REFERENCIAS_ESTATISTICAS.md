# Fichas analíticas das referências estatísticas e metodológicas

## 1. DiCiccio e Efron (1996) — Bootstrap Confidence Intervals

**Referência:** DICICCIO, Thomas J.; EFRON, Bradley. Bootstrap Confidence Intervals. *Statistical Science*, v. 11, n. 3, p. 189–228, 1996.

**Texto completo:** [Google Drive](https://drive.google.com/file/d/1D894n542x0Dngp3KAGch2QGGzLamHugZ/view)

**Síntese:** revisão dos principais métodos de intervalos de confiança bootstrap, incluindo BCa, bootstrap-t, ABC e calibração. O trabalho mostra que correções de viés, assimetria e aceleração podem melhorar a cobertura em relação ao intervalo normal padrão.

**Aplicação no projeto:** fundamenta intervalos de confiança não paramétricos para métricas de classificação e diferenças entre modelos. Também sustenta a necessidade de documentar a unidade experimental e o esquema de reamostragem.

**Cautela:** o desempenho em pequenas amostras depende do parâmetro, do modelo e do método de reamostragem. Bootstrap não corrige automaticamente dependência entre observações.

---

## 2. Hodge e Austin (2004) — A Survey of Outlier Detection Methodologies

**Referência:** HODGE, Victoria J.; AUSTIN, Jim. A Survey of Outlier Detection Methodologies. *Artificial Intelligence Review*, v. 22, n. 2, p. 85–126, 2004. DOI: 10.1023/B:AIRE.0000045502.10941.a9.

**Texto completo:** [Google Drive](https://drive.google.com/file/d/1ABfE43LNAJpFPqbECbbyCRrzA-98Dwxx/view)

**Síntese:** revisão taxonômica de metodologias estatísticas e computacionais para detecção de outliers. Organiza abordagens não supervisionadas, supervisionadas e baseadas na modelagem exclusiva da normalidade.

**Aplicação no projeto:** orienta a auditoria de registros extremos antes do treinamento, distinguindo erro de registro, caso raro válido e mudança real de distribuição. Também justifica revisão humana em ocorrências atípicas.

**Cautela:** um outlier não é necessariamente erro. A exclusão automática pode remover casos raros relevantes e introduzir viés na amostra.

---

## 3. Demšar (2006) — Statistical Comparisons of Classifiers over Multiple Data Sets

**Referência:** DEMŠAR, Janez. Statistical Comparisons of Classifiers over Multiple Data Sets. *Journal of Machine Learning Research*, v. 7, p. 1–30, 2006.

**Texto completo:** [Google Drive](https://drive.google.com/file/d/1WaQ1y70UluZdBBMMa3i-7CYe95v9TTFG/view)

**Síntese:** sistematiza procedimentos estatísticos para comparar algoritmos de aprendizagem em múltiplos conjuntos de dados. Recomenda Wilcoxon para dois classificadores e Friedman seguido de pós-hoc para múltiplos classificadores, além de diagramas de diferença crítica.

**Aplicação no projeto:** fundamenta comparação global e pareada dos modelos quando houver vários recortes independentes ou conjuntos de avaliação. Sustenta o uso de ranks quando os escores entre bases não são diretamente comensuráveis.

**Cautela:** o desenho clássico do artigo pressupõe múltiplos conjuntos de dados independentes. Aplicação em uma única base exige definir corretamente as unidades de replicação.

---

## 4. Wongpakaran et al. (2013) — Cohen’s Kappa e Gwet’s AC1

**Referência:** WONGPAKARAN, Nahathai et al. A comparison of Cohen’s Kappa and Gwet’s AC1 when calculating inter-rater reliability coefficients: a study conducted with personality disorder samples. *BMC Medical Research Methodology*, v. 13, art. 61, 2013. DOI: 10.1186/1471-2288-13-61.

**Texto completo:** [Google Drive](https://drive.google.com/file/d/1QOvQwGQP7iOgKCzjCV9ldVGxlTUs3qtj/view)

**Síntese:** compara Cohen’s kappa e Gwet’s AC1 em avaliações categóricas. O AC1 permaneceu mais próximo do acordo percentual e menos sensível à prevalência e às marginais, enquanto o kappa apresentou valores baixos mesmo sob alto acordo em alguns cenários.

**Aplicação no projeto:** sustenta análise de concordância entre avaliadores humanos de chamados e entre decisões humanas e classificações automatizadas. Recomenda relatar acordo bruto, kappa e AC1 em conjunto.

**Cautela:** o estudo aplicado usa classificações binárias. A extrapolação para múltiplas categorias deve respeitar a formulação adequada do coeficiente.

---

## 5. Kornbrot (2014) — Point Biserial Correlation

**Referência:** KORNBROT, Diana. Point Biserial Correlation. In: *Wiley StatsRef: Statistics Reference Online*. Wiley, 2014. DOI: 10.1002/9781118445112.stat06227.

**Texto completo:** [Google Drive](https://drive.google.com/file/d/1GJcIc4O1ky7-azM9YUrtr9pLwI9DqPlJ/view)

**Síntese:** define a correlação ponto-bisserial como caso particular da correlação de Pearson entre uma variável dicotômica codificada em 0/1 e uma variável métrica. Apresenta cálculo, interpretação como tamanho de efeito e relação com Cohen’s d e teste t.

**Aplicação no projeto:** permite medir a associação entre acerto/erro e confiança do modelo, tempo de atendimento ou outra variável contínua.

**Cautela:** a interpretação inferencial depende dos pressupostos correspondentes. Correlação não demonstra causalidade e pode ser influenciada por desequilíbrio entre grupos.

---

## 6. Benavoli, Corani e Mangili (2016) — Should We Really Use Post-Hoc Tests Based on Mean-Ranks?

**Referência:** BENAVOLI, Alessio; CORANI, Giorgio; MANGILI, Francesca. Should We Really Use Post-Hoc Tests Based on Mean-Ranks? *Journal of Machine Learning Research*, v. 17, n. 5, p. 1–10, 2016.

**Texto completo:** [Google Drive](https://drive.google.com/file/d/1zhgICkgaxoKmUYDBPD88QgLA4CWbKgzc/view)

**Síntese:** demonstra que testes pós-hoc baseados em ranks médios podem produzir conclusões diferentes para o mesmo par de algoritmos conforme os demais métodos incluídos no experimento. Recomenda comparações pareadas, como Wilcoxon ou teste de sinais, com controle de multiplicidade.

**Aplicação no projeto:** justifica não usar Nemenyi ou ranks médios como única evidência das diferenças entre modelos. Sustenta comparações pareadas acompanhadas de correção de Holm.

**Cautela:** a escolha do teste deve seguir o desenho amostral. Comparações repetidas sobre as mesmas observações exigem tratamento da dependência.

---

## 7. Ogunleye, Oyejola e Obisesan (2018) — Comparison of Some Common Tests for Normality

**Referência:** OGUNLEYE, L. I.; OYEJOLA, B. A.; OBISESAN, K. O. Comparison of Some Common Tests for Normality. *International Journal of Probability and Statistics*, v. 7, n. 5, p. 130–137, 2018. DOI: 10.5923/j.ijps.20180705.02.

**Texto completo:** [Google Drive](https://drive.google.com/file/d/1nbDB5iInKiOX1NL1AxihPwFU4cx5xt57/view)

**Síntese:** compara erro tipo I e poder de Anderson–Darling, qui-quadrado, Kolmogorov–Smirnov e Shapiro–Wilk por simulação Monte Carlo. Shapiro–Wilk apresentou melhor desempenho geral para alternativas contínuas, embora nenhum teste seja uniformemente mais poderoso.

**Aplicação no projeto:** fundamenta o uso do Shapiro–Wilk como diagnóstico complementar em variáveis contínuas e reforça a necessidade de combinar testes formais com gráficos Q-Q, assimetria e curtose.

**Cautela:** em amostras muito grandes, pequenos desvios podem gerar rejeição estatística sem relevância prática. Não rejeitar a hipótese nula também não prova normalidade.

---

## 8. Noma et al. (2021) — Confidence Intervals of Prediction Accuracy Measures

**Referência:** NOMA, Hisashi et al. Confidence intervals of prediction accuracy measures for multivariable prediction models based on the bootstrap-based optimism correction methods. *Statistics in Medicine*, v. 40, n. 26, p. 5691–5701, 2021. DOI: 10.1002/sim.9148.

**Texto completo:** [Google Drive](https://drive.google.com/file/d/15FypmzANxXhdQLrcY18DnhFsd7xzqD7b/view)

**Síntese:** propõe intervalos de confiança bootstrap associados às correções de otimismo de Harrell, 0,632 e 0,632+. Mostra que corrigir apenas a estimativa pontual e manter um intervalo convencional pode causar subcobertura.

**Aplicação no projeto:** fundamenta a apresentação de incerteza para métricas de discriminação e calibração após validação interna. Também apoia bootstrap em dois estágios para incorporar a variabilidade do processo de construção do modelo.

**Cautela:** os procedimentos foram desenvolvidos para modelos preditivos multivariados e validação interna. A adaptação ao desenho deste experimento deve preservar a unidade de reamostragem e evitar vazamento entre treino e teste.

---

## 9. Minderer et al. (2021) — Revisiting the Calibration of Modern Neural Networks

**Referência:** MINDERER, Matthias et al. Revisiting the Calibration of Modern Neural Networks. In: *Advances in Neural Information Processing Systems 34 (NeurIPS 2021)*, 2021.

**Texto completo:** [Google Drive](https://drive.google.com/file/d/1dbgvSLPXkdVS-WIeM8reI5YT5YHCzux1/view)

**Síntese:** avalia calibração e acurácia de 180 modelos de 16 famílias em 79 conjuntos de dados e múltiplas variantes métricas. Mostra que algumas arquiteturas modernas são simultaneamente mais acuradas e mais bem calibradas e que a arquitetura explica diferenças não capturadas apenas pela escala ou pelo pré-treinamento.

**Aplicação no projeto:** justifica avaliar acurácia e calibração conjuntamente, construir diagramas de confiabilidade e calcular ECE, Brier score e log-loss. Também fundamenta avaliação sob mudança temporal ou de domínio.

**Cautela:** o estudo é centrado em classificação de imagens. Os princípios de calibração são transferíveis, mas os resultados numéricos e a comparação entre arquiteturas não devem ser extrapolados diretamente para chamados textuais.

---

## 10. Chan et al. (2022) — Mitigating the Multicollinearity Problem and Its Machine Learning Approach

**Referência:** CHAN, Jireh Yi-Le et al. Mitigating the Multicollinearity Problem and Its Machine Learning Approach: A Review. *Mathematics*, v. 10, n. 8, art. 1283, 2022. DOI: 10.3390/math10081283.

**Texto completo:** [Google Drive](https://drive.google.com/file/d/1_SqEZGuR-TfBjFtkXwCvMgvTr0Eo3aWL/view)

**Síntese:** revisão de diagnóstico e mitigação da multicolinearidade, cobrindo correlação, VIF, tolerância, autovalores, índice de condição, seleção de variáveis, estimadores modificados, regularização e abordagens de otimização e aprendizagem de máquina.

**Aplicação no projeto:** sustenta auditoria de correlação e VIF antes de interpretar coeficientes ou relações entre saídas dos modelos. Também fundamenta regularização quando variáveis correlacionadas mantêm valor preditivo e teórico.

**Cautela:** limiares de VIF não são universais. A decisão depende do objetivo explicativo ou preditivo, e multicolinearidade entre previsões de modelos não é idêntica à multicolinearidade entre covariáveis de uma regressão.

---

## Síntese de uso no artigo

As dez referências cobrem seis frentes metodológicas do capítulo: tratamento de outliers; verificação de normalidade; comparação global e pareada de classificadores; concordância entre avaliadores; associação entre confiança e acerto; calibração e incerteza das métricas. Elas devem ser usadas para sustentar escolhas metodológicas específicas, sem transformar testes estatísticos em evidência automática de validade externa ou causalidade.