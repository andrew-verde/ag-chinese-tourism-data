import csv
import shutil
from pathlib import Path
from typing import Iterable, Sequence


def backup_existing(path: Path) -> None:
    if path.exists():
        backup_path = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, backup_path)
        print(f"  既存ファイルをバックアップしました: {backup_path}")


def replace_with_backup(temp_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    backup_existing(output_path)
    temp_path.replace(output_path)


def safe_write_bytes(output_path: Path | str, data: bytes) -> bool:
    output_path = Path(output_path)
    if not data:
        print(f"  ✗ 空データのため既存ファイルを保持します: {output_path}")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    temp_path.write_bytes(data)
    replace_with_backup(temp_path, output_path)
    return True


def safe_write_text(output_path: Path | str, content: str, encoding: str = "utf-8") -> bool:
    output_path = Path(output_path)
    if not content:
        print(f"  ✗ 空テキストのため既存ファイルを保持します: {output_path}")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    temp_path.write_text(content, encoding=encoding)
    replace_with_backup(temp_path, output_path)
    return True


def safe_copy_file(source_path: Path | str, output_path: Path | str) -> bool:
    source_path = Path(source_path)
    output_path = Path(output_path)

    if not source_path.exists() or source_path.stat().st_size == 0:
        print(f"  ✗ コピー元が存在しないか空です。既存ファイルを保持します: {source_path}")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    shutil.copy2(source_path, temp_path)
    replace_with_backup(temp_path, output_path)
    return True


def safe_write_csv(
    output_path: Path | str,
    headers: Sequence[str],
    rows: Iterable[Sequence[object]],
    encoding: str = "utf-8",
) -> bool:
    output_path = Path(output_path)
    rows = list(rows)

    if not headers:
        print(f"  ✗ ヘッダーが空のため既存ファイルを保持します: {output_path}")
        return False
    if not rows:
        print(f"  ✗ データ行が0件のため既存ファイルを保持します: {output_path}")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    with temp_path.open("w", newline="", encoding=encoding) as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    replace_with_backup(temp_path, output_path)
    return True
