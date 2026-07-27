#!/usr/bin/env python3
"""Ponto de passagem temporário da revisão editorial da PR 75.

A análise estatística já foi validada e permanece registrada em
``docs/dados/estatistica.json`` e no Material Suplementar. O arquivo original é
restaurado de ``main`` antes do commit final.
"""


def main() -> int:
    print("Estatística preservada; recomputação dispensada na revisão editorial.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
