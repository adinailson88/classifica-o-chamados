#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guarda de automacao condicionada dos workflows de geracao de dados.

Decide se um workflow PESADO/condicionado deve realmente executar nesta rodada,
comparando uma metrica do experimento (lida de docs/dados/resumo.json, que o
dashboard.yml republica a cada 30 min) com o valor registrado na ultima execucao
bem-sucedida (dados/estado_automacao.json).

Objetivo: nos disparos automaticos (cron/workflow_run) so gastar tempo/quota quando
houve avanco suficiente (ex.: "a cada 100 novas conferencias humanas" ou "+1000
chamados classificados"); caso contrario, encerrar com SUCESSO controlado e log claro.
O disparo manual (workflow_dispatch) deve ignorar esta guarda e sempre rodar.

Dois modos:

  Decisao (default):
    python src/guard_automacao.py --chave avaliacao_final --metrica validados \
        --limiar 100 [--forcar-se-aba-zero multimodelo_metricas]
    -> escreve em $GITHUB_OUTPUT: executar=true|false, valor_atual=<int>, motivo=<txt>

  Registro (apos a execucao pesada concluir com sucesso):
    python src/guard_automacao.py --registrar --chave avaliacao_final --valor 345
    -> grava dados/estado_automacao.json (so avanca o marcador quando o trabalho deu certo)

Sem segredos, sem rede: le apenas arquivos versionados do repositorio.
"""
import argparse
import json
import os
import sys

RESUMO_PADRAO = "docs/dados/resumo.json"
ESTADO_PADRAO = "dados/estado_automacao.json"


def carregar_json(caminho):
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, OSError) as e:
        print(f"[guard] aviso: nao consegui ler {caminho}: {e}", file=sys.stderr)
        return None


def metrica_atual(resumo, nome):
    if resumo is None:
        return 0
    if nome == "registros":
        return int(resumo.get("registros") or 0)
    if nome == "validados":
        cal = resumo.get("calibracao") or {}
        return int(cal.get("validados") or 0)
    raise SystemExit(f"[guard] metrica desconhecida: {nome} (use registros|validados)")


def contagem_aba(resumo, aba):
    if resumo is None:
        return 0
    return int((resumo.get("abas") or {}).get(aba) or 0)


def escrever_saidas(**kv):
    linha = "".join(f"{k}={v}\n" for k, v in kv.items())
    destino = os.environ.get("GITHUB_OUTPUT")
    if destino:
        with open(destino, "a", encoding="utf-8") as f:
            f.write(linha)
    sys.stdout.write(linha)


def modo_registrar(args):
    estado = carregar_json(args.estado) or {}
    estado[args.chave] = int(args.valor)
    os.makedirs(os.path.dirname(args.estado) or ".", exist_ok=True)
    with open(args.estado, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    print(f"[guard] estado atualizado: {args.chave} = {args.valor} em {args.estado}")


def modo_decidir(args):
    resumo = carregar_json(args.resumo)
    atual = metrica_atual(resumo, args.metrica)
    estado = carregar_json(args.estado) or {}
    ultimo = estado.get(args.chave)

    executar = False
    if args.forcar_se_aba_zero and contagem_aba(resumo, args.forcar_se_aba_zero) == 0 and atual > 0:
        executar, motivo = True, f"aba '{args.forcar_se_aba_zero}' ainda vazia (primeira materializacao)"
    elif ultimo is None:
        executar = atual > 0
        motivo = "primeira execucao registrada" if executar else "sem dados para processar ainda"
    else:
        delta = atual - int(ultimo)
        if delta >= args.limiar:
            executar, motivo = True, f"avanco suficiente: +{delta} >= limiar {args.limiar} (metrica {args.metrica})"
        else:
            motivo = f"avanco insuficiente: +{delta} < limiar {args.limiar} (metrica {args.metrica}); encerrando com sucesso"

    print(f"[guard] chave={args.chave} metrica={args.metrica} atual={atual} ultimo={ultimo} -> executar={executar}")
    print(f"[guard] motivo: {motivo}")
    escrever_saidas(executar=str(executar).lower(), valor_atual=atual, motivo=motivo)


def main():
    p = argparse.ArgumentParser(description="Guarda de automacao condicionada.")
    p.add_argument("--chave", required=True, help="Identificador do workflow no estado.")
    p.add_argument("--resumo", default=RESUMO_PADRAO)
    p.add_argument("--estado", default=ESTADO_PADRAO)
    p.add_argument("--metrica", default="registros", help="registros|validados")
    p.add_argument("--limiar", type=int, default=1000)
    p.add_argument("--forcar-se-aba-zero", dest="forcar_se_aba_zero", default="",
                   help="Nome da aba em resumo.abas que, se == 0, forca a execucao.")
    p.add_argument("--registrar", action="store_true", help="Modo registro do marcador.")
    p.add_argument("--valor", type=int, default=0, help="Valor a registrar (modo --registrar).")
    args = p.parse_args()
    if args.registrar:
        modo_registrar(args)
    else:
        modo_decidir(args)


if __name__ == "__main__":
    main()
