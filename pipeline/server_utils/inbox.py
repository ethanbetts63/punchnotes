import shutil
from pathlib import Path
from typing import Callable

from pipeline.log import Log


def run_inbox_update(
    inbox_dir: Path,
    archive_dir: Path,
    process_fn: Callable[[Path], dict],
    glob: str = "*.jsonl",
    log: Log | None = None,
) -> None:
    """
    Read each file matching glob from inbox_dir, call process_fn(path) -> count dict,
    archive the file, then log totals.
    """
    log = log or Log()
    archive_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(inbox_dir.glob(glob)) if inbox_dir.exists() else []
    if not files:
        log(f"No files in {inbox_dir.name}/")
        return
    total: dict[str, int] = {}
    for path in files:
        result = process_fn(path)
        for k, v in (result or {}).items():
            total[k] = total.get(k, 0) + v
        shutil.move(str(path), archive_dir / path.name)
        log(f"  {path.name}: {result}")
    log.success(f"Done. {total}")
