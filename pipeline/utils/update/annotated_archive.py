import json
import shutil

from django.conf import settings

from pipeline.log import Log
from pipeline.utils.comedian_aliases import load_relationships
from pipeline.utils.update.annotated import ingest_annotated_set, refresh_all_stats


def run_update_annotated(log: Log, archive: bool = False) -> None:
    data_dir = settings.PIPELINE_DATA_DIR
    private_dir = settings.PIPELINE_PRIVATE_DATA_DIR
    if archive:
        source_dir = private_dir / "bit_annotated_set_archive"
        dest_dir = None
    else:
        source_dir = data_dir / "annotated_set_inbox"
        dest_dir = private_dir / "bit_annotated_set_archive"
        dest_dir.mkdir(parents=True, exist_ok=True)

    paths = sorted(source_dir.glob("*.json"))
    if not paths:
        log(f"No files in {source_dir.name}.")
        return

    relationships = load_relationships()
    failed_dir = data_dir / "set_inbox" if archive else None
    succeeded = failed = 0
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            result = ingest_annotated_set(data, relationships, defer_refresh=True)
            log.success(f"  {path.name}: {result['comedian']} — {result['lines']} lines, {result['bits']} bits")
            if dest_dir:
                shutil.move(str(path), dest_dir / path.name)
            succeeded += 1
        except Exception as e:
            log.error(f"  {path.name}: FAILED — {e}")
            if failed_dir:
                failed_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(path), failed_dir / path.name)
                log(f"  {path.name}: copied to set_inbox/ for re-annotation")
            failed += 1

    if succeeded:
        log("Refreshing stats...")
        refresh_all_stats()

    log.success(f"\nDone. {succeeded} imported, {failed} failed.")
