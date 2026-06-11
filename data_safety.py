import shutil
from pathlib import Path


def safe_to_csv(df, output_path, **to_csv_kwargs):
    output_path = Path(output_path)
    if df is None or df.empty:
        print(f"Refusing to overwrite with empty data: {output_path}")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    backup_path = output_path.with_suffix(output_path.suffix + ".bak")

    df.to_csv(temp_path, **to_csv_kwargs)
    if output_path.exists():
        shutil.copy2(output_path, backup_path)
        print(f"Backed up previous output to {backup_path}")
    temp_path.replace(output_path)
    return True
