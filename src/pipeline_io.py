"""Safe file persistence helpers for research data pulls.

The scrapers in this repository are run manually behind logged-in browser
sessions, so a failed rerun must not be able to destroy a previous successful
pull. These helpers make CSV writes atomic, preserve timestamped backups, and
merge new rows with existing data by stable record IDs.
"""

from __future__ import annotations

import csv
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


class UnsafeWriteError(RuntimeError):
    """Raised when a write could discard existing research data."""


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as csvfile:
        return list(csv.DictReader(csvfile))


def stable_row_key(row: dict[str, object], key_fields: Sequence[str]) -> tuple[str, str]:
    for field in key_fields:
        value = str(row.get(field, "") or "").strip()
        if value:
            return field, value
    values = tuple(str(row.get(field, "") or "").strip() for field in sorted(row))
    return "__row__", repr(values)


def merge_rows(
    existing_rows: Iterable[dict[str, object]],
    new_rows: Iterable[dict[str, object]],
    key_fields: Sequence[str],
) -> list[dict[str, object]]:
    merged: dict[tuple[str, str], dict[str, object]] = {}
    order: list[tuple[str, str]] = []

    for row in existing_rows:
        key = stable_row_key(row, key_fields)
        if key not in merged:
            order.append(key)
        merged[key] = dict(row)

    for row in new_rows:
        key = stable_row_key(row, key_fields)
        if key not in merged:
            order.append(key)
        merged[key] = dict(row)

    return [merged[key] for key in order]


def backup_existing_file(path: Path, backup_dir: Path | None = None) -> Path | None:
    if not path.exists():
        return None

    backup_root = backup_dir or path.parent / "backups"
    backup_root.mkdir(parents=True, exist_ok=True)
    backup_path = backup_root / f"{path.name}.{utc_timestamp()}.bak"
    shutil.copy2(path, backup_path)
    return backup_path


def atomic_write_csv(rows: Sequence[dict[str, object]], path: Path, fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)

    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
            csvfile.flush()
            os.fsync(csvfile.fileno())
        os.replace(temp_path, path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def safe_write_csv(
    rows: Sequence[dict[str, object]],
    path: Path,
    fieldnames: Sequence[str],
    *,
    key_fields: Sequence[str] = (),
    merge_existing: bool = True,
    allow_empty: bool = False,
    allow_shrink: bool = False,
    backup_dir: Path | None = None,
) -> tuple[int, Path | None]:
    if not rows and not allow_empty:
        raise UnsafeWriteError(
            f"Refusing to write zero rows to {path}. Use allow_empty=True only for an intentional empty dataset."
        )

    existing_rows = read_csv_rows(path)
    output_rows: Sequence[dict[str, object]]
    if merge_existing and key_fields:
        output_rows = merge_rows(existing_rows, rows, key_fields)
    else:
        output_rows = rows

    if existing_rows and len(output_rows) < len(existing_rows) and not allow_shrink:
        raise UnsafeWriteError(
            f"Refusing to replace {len(existing_rows)} existing rows with {len(output_rows)} rows at {path}. "
            "Use --replace --allow-shrink only after confirming this is intentional."
        )

    backup_path = backup_existing_file(path, backup_dir=backup_dir)
    atomic_write_csv(output_rows, path, fieldnames)
    return len(output_rows), backup_path
