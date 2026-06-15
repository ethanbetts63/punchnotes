from django.conf import settings

from pipeline.utils.http import upload_jsonl_files
from pipeline.log import Log


def upload_ep_meta(options: dict, log: Log) -> None:
    upload_jsonl_files(
        outbox_dir=settings.PIPELINE_DATA_DIR / "ep_meta_outbox",
        archive_dir=settings.PIPELINE_DATA_DIR / "ep_meta_archive",
        endpoint_path="/api/pipeline/ep-meta/",
        log=log,
    )
