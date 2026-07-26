#!/usr/bin/env python3
"""Executa o exportador do dashboard com calibração deduplicada.

Mantém o restante de ``exportar_dashboard.py`` inalterado e substitui apenas
``calibracao.calcular`` pela versão que consolida o SNAPSHOT_ETAPA_1 por
``linha_planilha`` antes de agregar as métricas.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import calibracao  # noqa: E402
import calibracao_deduplicada  # noqa: E402
import exportar_dashboard  # noqa: E402

calibracao.calcular = calibracao_deduplicada.calcular


if __name__ == "__main__":
    raise SystemExit(exportar_dashboard.main())
