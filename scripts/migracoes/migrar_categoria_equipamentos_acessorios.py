#!/usr/bin/env python3
"""Migração manual da categoria de equipamentos e acessórios.

Por padrão, o script roda em dry-run: escaneia o repositório, decide o cenário
de segurança e gera relatório. Alterações em artefatos só ocorrem com --aplicar
e quando a regra de decisão permitir.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import subprocess
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


OLD_FULL = "Instalação de Acessórios e Mobiliário > Instalação/Reparo de Equipamentos, Acessórios e Mobiliários"
OLD_PARENT = "Instalação de Acessórios e Mobiliário"
OLD_CHILD = "Instalação/Reparo de Equipamentos, Acessórios e Mobiliários"
NEW_NAME = "Instalação/reparo de equipamentos (Suportes de TV, acessórios de banheiro e quadro branco)"

DEFAULT_REPORT = Path("docs/RELATORIO_MIGRACAO_CATEGORIA_EQUIPAMENTOS_ACESSORIOS.md")
EXTENSIONS = {".json", ".jsonl", ".csv", ".md", ".html", ".js", ".py", ".yml", ".yaml", ".txt"}
IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache", ".mypy_cache"}
ID_FIELDS = {
    "itilcategories_id",
    "categoria_id",
    "id_categoria",
    "categoria_glpi_id",
    "category_id",
    "id_categoria_nova",
    "categoria_nova_id",
}
CATEGORY_HINTS = (
    "categoria",
    "category",
    "classificacao",
    "classificação",
    "historica",
    "histórica",
    "prevista",
    "maioria",
    "orig",
    "original",
    "label",
    "taxonomia",
)
FREE_TEXT_HINTS = (
    "descricao",
    "descrição",
    "description",
    "titulo",
    "título",
    "observacao",
    "observação",
    "texto",
    "mensagem",
    "content",
)
OPERATIONAL_PREFIXES = (
    "docs/dados/",
    "dados/",
    "dados_csv/",
    "analise_R/",
)
SELF_FILES = {
    "scripts/migracoes/migrar_categoria_equipamentos_acessorios.py",
    ".github/workflows/migracao_categoria_equipamentos_acessorios.yml",
    "docs/MIGRACAO_CATEGORIA_EQUIPAMENTOS_ACESSORIOS.md",
    "docs/RELATORIO_MIGRACAO_CATEGORIA_EQUIPAMENTOS_ACESSORIOS.md",
}


@dataclass
class Occurrence:
    path: str
    line: int
    term: str
    kind: str
    bucket: str
    safe: bool


@dataclass
class ScanResult:
    repo: str
    branch: str
    commit: str
    files_scanned: list[str] = field(default_factory=list)
    skipped_files: list[str] = field(default_factory=list)
    occurrences: list[Occurrence] = field(default_factory=list)
    id_fields_found: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    category_ids: dict[str, set[str]] = field(default_factory=lambda: {OLD_FULL: set(), NEW_NAME: set()})
    files_changed: list[str] = field(default_factory=list)
    files_unchanged: list[str] = field(default_factory=list)
    pending: list[str] = field(default_factory=list)
    validations: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    decision: str = ""
    scenario: str = ""
    validation_by_id: bool = False
    validation_textual: bool = False
    applied: bool = False


def relpath(path: Path) -> str:
    return path.as_posix()


def run_git(args: list[str]) -> str:
    try:
        out = subprocess.check_output(["git", *args], text=True, encoding="utf-8", stderr=subprocess.DEVNULL)
        return out.strip()
    except Exception:
        return "Informação insuficiente para verificar."


def repository_state() -> tuple[str, str, str]:
    repo = run_git(["config", "--get", "remote.origin.url"])
    branch = run_git(["branch", "--show-current"])
    commit = run_git(["rev-parse", "HEAD"])
    return repo, branch, commit


def is_relevant(path: Path) -> bool:
    parts = set(path.parts)
    if parts & IGNORED_DIRS:
        return False
    return path.is_file() and path.suffix.lower() in EXTENSIONS


def read_text(path: Path) -> str | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw:
        return None
    for encoding in ("utf-8", "utf-8-sig", "cp1252"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def bucket_for(path: str) -> str:
    if path.startswith(".github/workflows/"):
        return "workflow"
    if path.startswith("src/") or path.startswith("scripts/") or path.endswith(".py"):
        return "codigo-fonte"
    if path.startswith("docs/dados/") and path.endswith(".json"):
        return "JSON do dashboard"
    if path.startswith("dados/") or path.startswith("dados_csv/") or path.startswith("analise_R/"):
        return "dados brutos ou intermediarios"
    if path.startswith("docs/") and path.endswith((".md", ".html")):
        return "documentacao ou dashboard"
    if path.endswith(".csv"):
        return "CSV"
    if path.endswith(".json"):
        return "JSON derivado"
    if path.endswith((".md", ".txt")):
        return "documentacao"
    return "arquivo textual"


def context_kind(path: str, line: str) -> tuple[str, bool]:
    ctx = line.casefold()
    if any(h in ctx for h in FREE_TEXT_HINTS):
        return "texto livre de chamado", False
    if any(h in ctx for h in CATEGORY_HINTS):
        return "rotulo de categoria", True
    bucket = bucket_for(path)
    if bucket in {"JSON do dashboard", "CSV", "dados brutos ou intermediarios"}:
        return "dado derivado", True
    if bucket in {"documentacao", "documentacao ou dashboard", "workflow", "codigo-fonte"}:
        return "documentacao", True
    return "ocorrencia insegura", False


def is_category_context(keys: tuple[str, ...]) -> bool:
    joined = ".".join(keys).casefold()
    return any(h in joined for h in CATEGORY_HINTS) and not any(h in joined for h in FREE_TEXT_HINTS)


def is_free_text_context(keys: tuple[str, ...]) -> bool:
    joined = ".".join(keys).casefold()
    return any(h in joined for h in FREE_TEXT_HINTS)


def is_operational(path: str) -> bool:
    return path.startswith(OPERATIONAL_PREFIXES)


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        base = Path(current)
        for name in names:
            path = base / name
            if is_relevant(path.relative_to(root)):
                files.append(path.relative_to(root))
    return sorted(files, key=lambda p: p.as_posix())


def scan_text_file(path: Path, rel: str, text: str, result: ScanResult) -> None:
    for field in ID_FIELDS:
        if field in text:
            result.id_fields_found[field].append(rel)
    terms = (OLD_FULL, OLD_CHILD, OLD_PARENT, NEW_NAME)
    for line_no, line in enumerate(text.splitlines(), start=1):
        for term in terms:
            if term in line:
                kind, safe = context_kind(rel, line)
                result.occurrences.append(Occurrence(rel, line_no, term, kind, bucket_for(rel), safe))


def collect_json_category_ids(obj: Any, result: ScanResult) -> None:
    if isinstance(obj, dict):
        keys = {str(k) for k in obj}
        id_values = [str(obj[k]) for k in keys & ID_FIELDS if obj.get(k) not in (None, "")]
        category_values = [str(v) for k, v in obj.items() if isinstance(v, str) and is_category_context((str(k),))]
        for category in category_values:
            if category in result.category_ids and id_values:
                result.category_ids[category].update(id_values)
        for value in obj.values():
            collect_json_category_ids(value, result)
    elif isinstance(obj, list):
        for value in obj:
            collect_json_category_ids(value, result)


def collect_csv_category_ids(text: str, result: ScanResult) -> None:
    try:
        dialect = csv.Sniffer().sniff(text[:4096])
        rows = list(csv.DictReader(io.StringIO(text), dialect=dialect))
    except csv.Error:
        return
    if not rows:
        return
    fields = rows[0].keys()
    id_cols = [f for f in fields if f in ID_FIELDS]
    cat_cols = [f for f in fields if is_category_context((f,))]
    for row in rows:
        ids = [str(row.get(c, "")).strip() for c in id_cols if str(row.get(c, "")).strip()]
        for col in cat_cols:
            category = str(row.get(col, "")).strip()
            if category in result.category_ids and ids:
                result.category_ids[category].update(ids)


def merge_values(existing: Any, incoming: Any) -> tuple[Any, bool]:
    if isinstance(existing, (int, float)) and isinstance(incoming, (int, float)):
        return existing + incoming, True
    if isinstance(existing, dict) and isinstance(incoming, dict):
        merged = deepcopy(existing)
        for key, value in incoming.items():
            if key in merged:
                merged[key], ok = merge_values(merged[key], value)
                if not ok:
                    return existing, False
            else:
                merged[key] = value
        return merged, True
    if isinstance(existing, list) and isinstance(incoming, list):
        return existing + incoming, True
    if existing == incoming:
        return existing, True
    return existing, False


def transform_json(obj: Any, keys: tuple[str, ...], pending: list[str]) -> tuple[Any, bool]:
    changed = False
    if isinstance(obj, dict):
        out: dict[Any, Any] = {}
        for key, value in obj.items():
            new_key = key
            key_str = str(key)
            if key_str == OLD_FULL:
                new_key = NEW_NAME
            elif key_str == OLD_CHILD and is_category_context(keys + (key_str,)):
                new_key = NEW_NAME
            new_value, value_changed = transform_json(value, keys + (str(new_key),), pending)
            if new_key in out:
                merged, ok = merge_values(out[new_key], new_value)
                if not ok:
                    pending.append(f"conflito inseguro ao consolidar chave {new_key!r} no contexto {'.'.join(keys) or '<raiz>'}")
                    out[key] = value
                    continue
                out[new_key] = merged
                changed = True
            else:
                out[new_key] = new_value
            changed = changed or value_changed or (new_key != key)
        return out, changed
    if isinstance(obj, list):
        out_list = []
        for idx, value in enumerate(obj):
            new_value, value_changed = transform_json(value, keys + (str(idx),), pending)
            out_list.append(new_value)
            changed = changed or value_changed
        return out_list, changed
    if isinstance(obj, str):
        if is_free_text_context(keys):
            return obj, False
        if obj == OLD_FULL:
            return NEW_NAME, True
        if obj == OLD_CHILD and is_category_context(keys):
            return NEW_NAME, True
    return obj, False


def transform_csv(text: str) -> tuple[str, bool, list[str]]:
    pending: list[str] = []
    try:
        dialect = csv.Sniffer().sniff(text[:4096])
    except csv.Error:
        dialect = csv.excel
    reader = csv.reader(io.StringIO(text), dialect=dialect)
    rows = list(reader)
    if not rows:
        return text, False, pending
    headers = rows[0]
    changed = False
    for row_index, row in enumerate(rows[1:], start=2):
        for col_index, cell in enumerate(row):
            header = headers[col_index] if col_index < len(headers) else ""
            if cell == OLD_FULL:
                row[col_index] = NEW_NAME
                changed = True
            elif cell == OLD_CHILD and is_category_context((header,)):
                row[col_index] = NEW_NAME
                changed = True
            elif OLD_FULL in cell and not is_category_context((header,)):
                pending.append(f"linha {row_index}: ocorrência em coluna sem contexto categorial ({header})")
    if not changed:
        return text, False, pending
    out = io.StringIO()
    writer = csv.writer(out, dialect=dialect, lineterminator="\n")
    writer.writerows(rows)
    return out.getvalue(), True, pending


def transform_text(rel: str, text: str) -> tuple[str, bool, list[str]]:
    pending: list[str] = []
    changed = False
    lines = []
    for line_no, line in enumerate(text.splitlines(keepends=True), start=1):
        kind, safe = context_kind(rel, line)
        new_line = line
        if OLD_FULL in new_line and safe:
            new_line = new_line.replace(OLD_FULL, NEW_NAME)
        if OLD_CHILD in new_line and safe and kind == "rotulo de categoria":
            new_line = new_line.replace(OLD_CHILD, NEW_NAME)
        if new_line != line:
            changed = True
        elif OLD_FULL in line or OLD_CHILD in line:
            pending.append(f"{rel}:{line_no}: ocorrência preservada por contexto {kind}")
        lines.append(new_line)
    return "".join(lines), changed, pending


def migrate_file(path: Path, rel: str, result: ScanResult, apply: bool) -> None:
    text = read_text(path)
    if text is None:
        result.skipped_files.append(rel)
        return
    original = text
    pending: list[str] = []
    changed = False

    if path.suffix.lower() == ".json":
        try:
            data = json.loads(text)
            new_data, changed = transform_json(data, (), pending)
            if changed and not pending:
                text = json.dumps(new_data, ensure_ascii=False, indent=2) + "\n"
                json.loads(text)
        except json.JSONDecodeError as exc:
            pending.append(f"{rel}: JSON inválido antes da migração ({exc})")
            changed = False
    elif path.suffix.lower() == ".jsonl":
        new_lines = []
        for line_no, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                new_lines.append(line)
                continue
            try:
                data = json.loads(line)
                new_data, line_changed = transform_json(data, (), pending)
                new_lines.append(json.dumps(new_data, ensure_ascii=False) if line_changed else line)
                changed = changed or line_changed
            except json.JSONDecodeError as exc:
                pending.append(f"{rel}:{line_no}: JSONL inválido ({exc})")
                new_lines.append(line)
        if changed and not pending:
            text = "\n".join(new_lines) + ("\n" if original.endswith("\n") else "")
    elif path.suffix.lower() == ".csv":
        text, changed, pending = transform_csv(text)
    else:
        text, changed, pending = transform_text(rel, text)

    if pending:
        result.pending.extend(pending)
        changed = False
    if changed and text != original:
        if apply:
            path.write_text(text, encoding="utf-8")
        result.files_changed.append(rel)
    else:
        result.files_unchanged.append(rel)


def determine_scenario(result: ScanResult, args: argparse.Namespace) -> None:
    old_ids = result.category_ids.get(OLD_FULL, set())
    new_ids = result.category_ids.get(NEW_NAME, set())
    has_id_fields = any(result.id_fields_found.values())
    operational_old = any(
        is_operational(o.path) and o.term in {OLD_FULL, OLD_CHILD, OLD_PARENT}
        for o in result.occurrences
    )
    operational_new = any(is_operational(o.path) and o.term == NEW_NAME for o in result.occurrences)

    if old_ids and new_ids:
        result.validation_by_id = True
        if old_ids == new_ids:
            result.scenario = "A"
            result.decision = "validacao forte por ID de categoria; migração permitida"
        else:
            result.scenario = "D"
            result.decision = "IDs de categoria divergentes; migração automática bloqueada"
    elif has_id_fields:
        result.scenario = "F"
        result.decision = "campo de ID localizado, mas sem vínculo simultâneo antigo/novo suficiente para validar"
        result.risks.append("Informação insuficiente para verificar por ID da categoria")
    elif operational_old and operational_new:
        result.scenario = "C"
        result.validation_textual = True
        result.decision = "nome antigo e nome novo aparecem juntos sem ID de categoria; consolidação automática bloqueada"
    elif operational_new and not operational_old:
        result.scenario = "B"
        result.validation_textual = True
        if args.validar_por_texto_quando_sem_id:
            result.decision = "validação textual média; migração de artefatos textuais/JSONs permitida"
        else:
            result.decision = "nome novo localizado sem ID; validação textual não autorizada"
    elif operational_old and not operational_new:
        result.scenario = "E"
        result.validation_textual = True
        result.decision = "mudança do Helpdesk/GLPI ainda não propagada para os dados do repositório; migração bloqueada"
    else:
        result.scenario = "F"
        result.decision = "categoria não localizada; migração bloqueada salvo --forcar"

    if not has_id_fields:
        result.risks.append("Informação insuficiente para verificar por ID da categoria")


def can_apply(result: ScanResult, args: argparse.Namespace) -> bool:
    if args.forcar:
        return True
    if result.scenario == "A":
        return True
    if result.scenario == "B" and args.validar_por_texto_quando_sem_id:
        return True
    if result.scenario == "C" and args.permitir_antigo_e_novo_juntos and args.validar_por_texto_quando_sem_id:
        return True
    if result.scenario == "F" and args.permitir_antigo_ausente:
        return True
    return False


def validate_changed_jsons(result: ScanResult) -> None:
    for rel in result.files_changed:
        path = Path(rel)
        if path.suffix.lower() == ".json":
            json.loads(path.read_text(encoding="utf-8"))
            result.validations.append(f"JSON válido: {rel}")
        elif path.suffix.lower() == ".jsonl":
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    json.loads(line)
            result.validations.append(f"JSONL válido: {rel}")


def build_report(result: ScanResult) -> str:
    counts_by_bucket = Counter(o.bucket for o in result.occurrences)
    old_remaining = sorted({o.path for o in result.occurrences if o.term in {OLD_FULL, OLD_CHILD, OLD_PARENT}})
    new_files = sorted({o.path for o in result.occurrences if o.term == NEW_NAME})
    id_fields = {
        key: sorted(set(paths))
        for key, paths in result.id_fields_found.items()
        if paths
    }
    old_ids = sorted(result.category_ids.get(OLD_FULL, set()))
    new_ids = sorted(result.category_ids.get(NEW_NAME, set()))
    ids_equal = bool(old_ids and new_ids and old_ids == new_ids)

    def bullet(items: list[str], empty: str = "nenhum") -> str:
        if not items:
            return f"- {empty}"
        return "\n".join(f"- `{item}`" for item in items)

    lines = [
        "# Relatório de Migração da Categoria de Equipamentos e Acessórios",
        "",
        f"- Data/hora: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- Repositório: `{result.repo}`",
        f"- Branch: `{result.branch}`",
        f"- Commit inicial: `{result.commit}`",
        f"- Nome antigo: `{OLD_FULL}`",
        f"- Nome novo: `{NEW_NAME}`",
        f"- Cenário aplicado: `{result.scenario}`",
        f"- Decisão tomada: {result.decision}",
        f"- Modo de aplicação: {'aplicado' if result.applied else 'dry-run ou bloqueado'}",
        "",
        "## Validação por ID",
        "",
        f"- Campos de ID de categoria encontrados: `{', '.join(id_fields) if id_fields else 'nenhum'}`",
        f"- Houve validação por ID: `{'sim' if result.validation_by_id else 'não'}`",
        f"- ID antigo da categoria: `{', '.join(old_ids) if old_ids else 'Informação insuficiente para verificar.'}`",
        f"- ID novo da categoria: `{', '.join(new_ids) if new_ids else 'Informação insuficiente para verificar.'}`",
        f"- IDs são iguais: `{'sim' if ids_equal else 'não'}`",
        f"- Validação apenas textual: `{'sim' if result.validation_textual else 'não'}`",
        "",
        "## Arquivos escaneados",
        "",
        f"- Total: `{len(result.files_scanned)}`",
        f"- Ignorados/binários: `{len(result.skipped_files)}`",
        "",
        "## Ocorrências por grupo",
        "",
    ]
    if counts_by_bucket:
        lines.extend(f"- {bucket}: `{count}`" for bucket, count in sorted(counts_by_bucket.items()))
    else:
        lines.append("- nenhuma ocorrência localizada")

    lines.extend([
        "",
        "## Arquivos alterados",
        "",
        bullet(sorted(set(result.files_changed))),
        "",
        "## Arquivos não alterados",
        "",
        bullet(sorted(set(result.files_unchanged))[:200]),
        "",
        "## Arquivos com ocorrência antiga remanescente",
        "",
        bullet(old_remaining),
        "",
        "## Arquivos com ocorrência nova",
        "",
        bullet(new_files),
        "",
        "## Validações executadas",
        "",
        bullet(result.validations),
        "",
        "## Riscos",
        "",
        bullet(result.risks),
        "",
        "## Pendências",
        "",
        bullet(result.pending),
        "",
        "## Recomendação para os próximos repositórios",
        "",
        "Repetir a mesma lógica por repositório, começando por diagnóstico de ID de categoria GLPI. "
        "Não consolidar categorias sem ID igual ou sem cenário textual seguro explicitamente registrado.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aplicar", action="store_true", help="Aplica alterações quando o cenário permitir.")
    parser.add_argument("--forcar", action="store_true", help="Permite aplicar mesmo fora dos cenários seguros.")
    parser.add_argument("--relatorio", nargs="?", const=str(DEFAULT_REPORT), default=None, help="Grava relatório Markdown.")
    parser.add_argument("--permitir-antigo-ausente", action="store_true")
    parser.add_argument("--permitir-antigo-e-novo-juntos", action="store_true")
    parser.add_argument("--validar-por-texto-quando-sem-id", action="store_true")
    args = parser.parse_args()

    repo, branch, commit = repository_state()
    result = ScanResult(repo=repo, branch=branch, commit=commit)
    root = Path(".")

    for rel_path in iter_files(root):
        rel = relpath(rel_path)
        if rel in SELF_FILES:
            result.skipped_files.append(rel)
            continue
        text = read_text(rel_path)
        if text is None:
            result.skipped_files.append(rel)
            continue
        result.files_scanned.append(rel)
        scan_text_file(rel_path, rel, text, result)
        if rel_path.suffix.lower() == ".json":
            try:
                collect_json_category_ids(json.loads(text), result)
            except json.JSONDecodeError:
                result.pending.append(f"{rel}: JSON inválido antes da migração")
        elif rel_path.suffix.lower() == ".csv":
            collect_csv_category_ids(text, result)

    determine_scenario(result, args)
    allowed = can_apply(result, args)
    result.applied = bool(args.aplicar and allowed)
    if args.aplicar and not allowed:
        result.risks.append("Execução com --aplicar bloqueada pela regra de decisão")

    if result.applied:
        for rel in result.files_scanned:
            migrate_file(Path(rel), rel, result, apply=True)
        validate_changed_jsons(result)
    else:
        result.files_unchanged = list(result.files_scanned)
        result.validations.append("dry-run: nenhuma alteração aplicada")

    report = build_report(result)
    if args.relatorio:
        report_path = Path(args.relatorio)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        print(f"relatorio={report_path.as_posix()}")
    print(f"cenario={result.scenario}")
    print(f"decisao={result.decision}")
    print(f"arquivos_escaneados={len(result.files_scanned)}")
    print(f"arquivos_alterados={len(result.files_changed)}")
    if result.risks:
        print("riscos=" + " | ".join(result.risks))
    return 0 if not (args.aplicar and not allowed) else 2


if __name__ == "__main__":
    raise SystemExit(main())
