from pathlib import Path

arquivo = Path("04_artigo/artigo_classificacao_chamados_v3.md")
texto = arquivo.read_text(encoding="utf-8")

bloco_atual = r'''```{=latex}
\enlargethispage{2\baselineskip}
```

**Tabela 4** Acerto validado por faixa de confiança. A unidade é o
chamado, 13.965 no total, 8.895 com conferência humana.

| Faixa | n total | Concord. histórico | n validados | Acerto validado |
|---|---|---|---|---|
| < 50% | 3.673 | 43,42% | 634 | 55,05% |
| 50–70% | 1.492 | 74,06% | 632 | 91,77% |
| 70–80% | 912 | 83,99% | 522 | 96,93% |
| 80–90% | 1.593 | 84,43% | 1.126 | 98,67% |
| 90–95% | 1.234 | 94,98% | 1.087 | 99,17% |
| >= 95% | 5.061 | 98,70% | 4.894 | 99,84% |'''

bloco_novo = r'''```{=latex}
\begin{minipage}{\linewidth}
\small
\noindent\textbf{Tabela 4} Acerto validado por faixa de confiança. A unidade é o
chamado, 13.965 no total, 8.895 com conferência humana.
\par\smallskip
\centering
\begin{tabular}{@{}lrrrr@{}}
\toprule
Faixa & n total & Concord. histórico & n validados & Acerto validado \\
\midrule
\textless{} 50\% & 3.673 & 43,42\% & 634 & 55,05\% \\
50–70\% & 1.492 & 74,06\% & 632 & 91,77\% \\
70–80\% & 912 & 83,99\% & 522 & 96,93\% \\
80–90\% & 1.593 & 84,43\% & 1.126 & 98,67\% \\
90–95\% & 1.234 & 94,98\% & 1.087 & 99,17\% \\
\textgreater{}= 95\% & 5.061 & 98,70\% & 4.894 & 99,84\% \\
\bottomrule
\end{tabular}
\end{minipage}
```'''

if texto.count(bloco_atual) != 1:
    raise SystemExit("O bloco atual da Tabela 4 não foi localizado de forma inequívoca.")

texto = texto.replace(bloco_atual, bloco_novo, 1)
arquivo.write_text(texto, encoding="utf-8")
