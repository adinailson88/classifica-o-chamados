#!/usr/bin/env python3
"""Mede o custo computacional do BERTimbau sob o protocolo canonico.

Ferramenta estritamente READ-ONLY. Serve ao Passo 6 de PLANO_EXECUCAO_ATUAL.md,
que exige decidir a admissao do BERTimbau na comparacao principal "por evidencia
computacional, sem alegacao vaga de custo".

O que e MEDIDO: a taxa real de passos de treino por segundo, obtida executando
um numero pequeno de passos sobre os proprios dados do experimento, com os
mesmos hiperparametros do `_ModeloTransformerFT`, alem da taxa de tokenizacao e
de inferencia.

O que e EXTRAPOLADO: o tempo total das cinco dobras, calculado a partir da taxa
medida. A extrapolacao e linear no numero de passos, o que e adequado porque o
custo por passo e estavel apos o aquecimento; ainda assim o relatorio separa os
dois campos, para que ninguem leia a projecao como medicao.

Nao treina modelo ate o fim, nao publica predicao e nao escreve na planilha.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import construir_grupos_textuais as cgt  # noqa: E402
import planilha as pl  # noqa: E402
import retreinar_modelos_canonicos as rmc  # noqa: E402
from tempo import agora_bahia  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
CONFIG_PADRAO = RAIZ / "config_experimento.json"
MAPA_PARTICOES_PADRAO = RAIZ / "docs" / "dados" / "particoes_canonicas_mapa.csv"
SAIDA_JSON_PADRAO = RAIZ / "docs" / "dados" / "custo_bertimbau.json"
SAIDA_MD_PADRAO = RAIZ / "docs" / "CUSTO_BERTIMBAU.md"

# Teto efetivo de um job no executor hospedado do GitHub. Acima disso o job e
# cancelado, independentemente de `timeout-minutes`.
LIMITE_JOB_S = 6 * 3600

PASSOS_MEDIDOS_PADRAO = 30
PASSOS_AQUECIMENTO = 3


def ambiente() -> dict[str, Any]:
    info: dict[str, Any] = {
        "python": platform.python_version(),
        "plataforma": platform.platform(),
        "processadores": os.cpu_count(),
    }
    try:
        import torch
        info["torch"] = torch.__version__
        info["cuda_disponivel"] = bool(torch.cuda.is_available())
        info["dispositivo"] = ("cuda:" + torch.cuda.get_device_name(0)
                               if torch.cuda.is_available() else "cpu")
        info["threads_torch"] = torch.get_num_threads()
    except ImportError:
        info["torch"] = "indisponivel"
        info["cuda_disponivel"] = False
        info["dispositivo"] = "indisponivel"
    try:
        import transformers
        info["transformers"] = transformers.__version__
    except ImportError:
        info["transformers"] = "indisponivel"
    return info


def medir(textos: list[str], rotulos: list[str], base: str,
          epochs: int, max_len: int, batch: int, lr: float,
          passos: int = PASSOS_MEDIDOS_PADRAO,
          registrar=print) -> dict[str, Any]:
    """Executa alguns passos reais de fine-tuning e devolve as taxas medidas."""
    import torch
    from torch.utils.data import DataLoader, TensorDataset
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    categorias = sorted(set(rotulos))
    lab2id = {c: i for i, c in enumerate(categorias)}

    inicio = time.perf_counter()
    tokenizador = AutoTokenizer.from_pretrained(base)
    tempo_tokenizador = time.perf_counter() - inicio

    # Tokeniza somente o necessario para alimentar os passos medidos; tokenizar
    # o corpus inteiro custaria minutos e nao muda a taxa por amostra.
    amostra = min(len(textos), max(batch * (passos + PASSOS_AQUECIMENTO), batch))
    inicio = time.perf_counter()
    cod = tokenizador(textos[:amostra], truncation=True, padding="max_length",
                      max_length=max_len, return_tensors="pt")
    tempo_tokenizacao = time.perf_counter() - inicio
    taxa_tokenizacao = amostra / tempo_tokenizacao if tempo_tokenizacao else 0.0

    inicio = time.perf_counter()
    modelo = AutoModelForSequenceClassification.from_pretrained(
        base, num_labels=len(categorias))
    tempo_carga_modelo = time.perf_counter() - inicio

    y = torch.tensor([lab2id[r] for r in rotulos[:amostra]])
    conjunto = TensorDataset(cod["input_ids"], cod["attention_mask"], y)
    carregador = DataLoader(conjunto, batch_size=batch, shuffle=False)
    otimizador = torch.optim.AdamW(modelo.parameters(), lr=lr)

    modelo.train()
    tempos: list[float] = []
    for i, (ids, mascara, alvo) in enumerate(carregador):
        if i >= passos + PASSOS_AQUECIMENTO:
            break
        inicio = time.perf_counter()
        otimizador.zero_grad()
        saida = modelo(input_ids=ids, attention_mask=mascara, labels=alvo)
        saida.loss.backward()
        otimizador.step()
        decorrido = time.perf_counter() - inicio
        # Os primeiros passos incluem alocacao e aquecimento de kernels; entram
        # no log, nao na media.
        if i >= PASSOS_AQUECIMENTO:
            tempos.append(decorrido)
        registrar(f"[custo_bertimbau] passo {i + 1}: {decorrido:.2f}s")

    modelo.eval()
    with torch.no_grad():
        ids, mascara, _alvo = next(iter(carregador))
        inicio = time.perf_counter()
        modelo(input_ids=ids, attention_mask=mascara)
        tempo_lote_inferencia = time.perf_counter() - inicio

    s_por_passo = sum(tempos) / len(tempos) if tempos else 0.0
    return {
        "passos_medidos": len(tempos),
        "passos_de_aquecimento_descartados": PASSOS_AQUECIMENTO,
        "segundos_por_passo": round(s_por_passo, 3),
        "segundos_por_passo_min": round(min(tempos), 3) if tempos else None,
        "segundos_por_passo_max": round(max(tempos), 3) if tempos else None,
        "amostras_por_segundo_treino": round(batch / s_por_passo, 2) if s_por_passo else 0.0,
        "amostras_por_segundo_inferencia": (
            round(batch / tempo_lote_inferencia, 2) if tempo_lote_inferencia else 0.0),
        "amostras_por_segundo_tokenizacao": round(taxa_tokenizacao, 1),
        "segundos_carga_tokenizador": round(tempo_tokenizador, 2),
        "segundos_carga_modelo": round(tempo_carga_modelo, 2),
    }


def extrapolar(medida: dict[str, Any], n_treino: int, n_teste: int,
               k: int, epochs: int, batch: int) -> dict[str, Any]:
    """Projeta o custo das k dobras a partir da taxa medida."""
    s_por_passo = medida["segundos_por_passo"]
    passos_por_epoca = math.ceil(n_treino / batch)
    passos_por_dobra = passos_por_epoca * epochs
    treino_dobra = passos_por_dobra * s_por_passo

    taxa_inf = medida["amostras_por_segundo_inferencia"] or 1.0
    taxa_tok = medida["amostras_por_segundo_tokenizacao"] or 1.0
    inferencia_dobra = n_teste / taxa_inf
    tokenizacao_dobra = (n_treino + n_teste) / taxa_tok
    dobra = treino_dobra + inferencia_dobra + tokenizacao_dobra
    total = dobra * k

    return {
        "passos_por_epoca": passos_por_epoca,
        "passos_por_dobra": passos_por_dobra,
        "segundos_por_dobra": round(dobra, 1),
        "horas_por_dobra": round(dobra / 3600, 2),
        "horas_todas_as_dobras": round(total / 3600, 2),
        "cabe_em_um_job_do_executor": bool(dobra < LIMITE_JOB_S),
        "dobras_que_cabem_em_um_job": int(LIMITE_JOB_S // dobra) if dobra else 0,
        "limite_do_job_horas": LIMITE_JOB_S / 3600,
        "base_do_calculo": ("tempo por passo medido, multiplicado pelos passos de "
                            "todas as epocas, mais tokenizacao e inferencia da dobra"),
    }


def montar_relatorio(medida: dict[str, Any], projecao: dict[str, Any],
                     contexto: dict[str, Any]) -> dict[str, Any]:
    cabe = projecao["cabe_em_um_job_do_executor"]
    completo = cabe and projecao["horas_todas_as_dobras"] <= LIMITE_JOB_S / 3600
    return {
        "schema_version": 1,
        "status": "medido",
        "veredito": ("protocolo_integral_viavel" if completo else
                     "protocolo_integral_inviavel_no_executor_atual"),
        "natureza_dos_numeros": {
            "medido": ("segundos por passo, taxa de tokenizacao, taxa de "
                       "inferencia e tempos de carga"),
            "extrapolado": ("tempo por dobra e tempo das cinco dobras, obtidos "
                            "multiplicando a taxa medida pelo numero de passos"),
        },
        "contexto": contexto,
        "medicao": medida,
        "projecao": projecao,
        "ambiente": ambiente(),
    }


def renderizar_markdown(relatorio: dict[str, Any]) -> str:
    m, p, c = relatorio["medicao"], relatorio["projecao"], relatorio["contexto"]
    a = relatorio["ambiente"]
    linhas = [
        "# Custo computacional do BERTimbau sob o protocolo canônico",
        "",
        "> Relatório sanitizado e somente leitura. Não contém títulos, descrições ou IDs de chamados.",
        "",
        f"**Veredito:** `{relatorio['veredito']}`  ",
        f"**Gerado em:** {relatorio.get('gerado_em', 'não informado')}",
        "",
        "## O que é medido e o que é extrapolado",
        "",
        f"- Medido: {relatorio['natureza_dos_numeros']['medido']}.",
        f"- Extrapolado: {relatorio['natureza_dos_numeros']['extrapolado']}.",
        "",
        "## Configuração",
        "",
        f"- Modelo base: `{c['modelo_base']}`.",
        f"- Épocas {c['epochs']}, comprimento máximo {c['max_len']}, lote {c['batch']}, taxa {c['lr']}.",
        f"- Dobra medida: {c['dobra_medida']}, com {c['n_treino']} linhas de treino "
        f"e {c['n_teste']} de teste, em {c['categorias']} categorias.",
        "",
        "## Taxas medidas",
        "",
        "| Grandeza | Valor |",
        "|---|---:|",
        f"| Passos cronometrados | {m.get('passos_medidos', '—')} |",
        f"| Segundos por passo | {m['segundos_por_passo']} |",
        f"| Faixa por passo (mín–máx) | {m.get('segundos_por_passo_min', '—')}–{m.get('segundos_por_passo_max', '—')} |",
        f"| Amostras/s no treino | {m.get('amostras_por_segundo_treino', '—')} |",
        f"| Amostras/s na inferência | {m['amostras_por_segundo_inferencia']} |",
        f"| Amostras/s na tokenização | {m['amostras_por_segundo_tokenizacao']} |",
        f"| Carga do modelo (s) | {m.get('segundos_carga_modelo', '—')} |",
        "",
        "## Projeção do protocolo integral",
        "",
        "| Grandeza | Valor |",
        "|---|---:|",
        f"| Passos por época | {p['passos_por_epoca']} |",
        f"| Passos por dobra | {p['passos_por_dobra']} |",
        f"| Horas por dobra | {p['horas_por_dobra']} |",
        f"| Horas nas cinco dobras | {p['horas_todas_as_dobras']} |",
        f"| Limite de um job do executor (h) | {p['limite_do_job_horas']} |",
        f"| Dobras que cabem em um job | {p['dobras_que_cabem_em_um_job']} |",
        "",
        "## Ambiente",
        "",
        f"- {a['python']} em {a['plataforma']}, {a['processadores']} processadores.",
        f"- torch {a.get('torch')}, transformers {a.get('transformers')}.",
        f"- Dispositivo: {a.get('dispositivo')}; CUDA disponível: {a.get('cuda_disponivel')}.",
        "",
        "## Proveniência",
        "",
        "- Partições: `docs/dados/particoes_canonicas_mapa.csv`, Passo 3.",
        "- Hiperparâmetros espelhados de `_ModeloTransformerFT`, em `src/modelos_zoo.py`.",
        "- Script: `src/medir_custo_bertimbau.py`.",
        "- Nenhum modelo foi treinado até o fim e nenhuma predição foi publicada.",
        "- Nenhuma escrita foi realizada na planilha.",
        "",
    ]
    return "\n".join(linhas)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    p.add_argument("--credenciais", default=None)
    p.add_argument("--particoes", type=Path, default=MAPA_PARTICOES_PADRAO)
    p.add_argument("--dobra", type=int, default=1)
    p.add_argument("--passos", type=int, default=PASSOS_MEDIDOS_PADRAO)
    p.add_argument("--json", type=Path, default=SAIDA_JSON_PADRAO)
    p.add_argument("--markdown", type=Path, default=SAIDA_MD_PADRAO)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.particoes.exists():
        print(f"Mapa de particoes nao encontrado em {args.particoes}.", file=sys.stderr)
        return 2
    amb = ambiente()
    if amb["torch"] == "indisponivel" or amb["transformers"] == "indisponivel":
        print("torch/transformers indisponiveis; instale requirements-transformer.txt.",
              file=sys.stderr)
        return 2

    config = json.loads(args.config.read_text(encoding="utf-8"))
    particoes = rmc.carregar_particoes(args.particoes)
    sh = pl.abrir_planilha(pl.id_planilha(config), args.credenciais)
    corpus = rmc.preparar_corpus(cgt.ler_registros(sh, config), particoes)

    treino = [i for i, d in enumerate(corpus["dobras"]) if d != args.dobra]
    teste = [i for i, d in enumerate(corpus["dobras"]) if d == args.dobra]
    if not treino or not teste:
        print(f"Dobra {args.dobra} inexistente nas particoes.", file=sys.stderr)
        return 2

    base = os.environ.get("TRANSFORMER_BASE", "neuralmind/bert-base-portuguese-cased")
    epochs = int(os.environ.get("TRANSFORMER_EPOCHS", "3"))
    max_len = int(os.environ.get("TRANSFORMER_MAXLEN", "192"))
    batch = int(os.environ.get("TRANSFORMER_BATCH", "16"))
    lr = float(os.environ.get("TRANSFORMER_LR", "2e-5"))

    medida = medir([corpus["textos"][i] for i in treino],
                   [corpus["rotulos"][i] for i in treino],
                   base, epochs, max_len, batch, lr, passos=args.passos)
    projecao = extrapolar(medida, len(treino), len(teste),
                          k=len(set(corpus["dobras"])), epochs=epochs, batch=batch)
    contexto = {
        "modelo_base": base, "epochs": epochs, "max_len": max_len,
        "batch": batch, "lr": lr, "dobra_medida": args.dobra,
        "n_treino": len(treino), "n_teste": len(teste),
        "categorias": len(set(corpus["rotulos"])),
    }

    relatorio = montar_relatorio(medida, projecao, contexto)
    relatorio["gerado_em"] = agora_bahia()
    relatorio["script_origem"] = "src/medir_custo_bertimbau.py"
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    args.markdown.write_text(renderizar_markdown(relatorio), encoding="utf-8")
    print(renderizar_markdown(relatorio))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
