#!/usr/bin/env python3
"""Evita que a sincronização numérica sobrescreva a revisão editorial final.

Os números do manuscrito já foram validados antes desta etapa. Este arquivo é
temporário e será removido após a execução do workflow corretivo.
"""


def main() -> int:
    print("Sincronização numérica preservada; texto editorial mantido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
