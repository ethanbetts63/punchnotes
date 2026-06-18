import shutil
from pathlib import Path
from typing import Callable

from pipeline.log import Log


def run_inbox_update(
    inbox_dir: Path,
    archive_dir: Path,
    process_fn: Callable[[Path], dict],
    log: Log,
    glob: str = "*.jsonl",
) -> None:
    archive_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(inbox_dir.glob(glob)) if inbox_dir.exists() else []
    if not files:
        log(f"No files in {inbox_dir.name}/")
        return
    totals: dict = {}
    for path in files:
        result = process_fn(path)
        shutil.move(str(path), archive_dir / path.name)
        for k, v in result.items():
            totals[k] = totals.get(k, 0) + v
        log(f"  {path.name}: {result}")
    log.success(f"Done. {totals}")
