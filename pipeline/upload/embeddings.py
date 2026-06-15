from django.conf import settings

from pipeline.utils.http import upload_jsonl_files
from pipeline.log import Log


def upload_embeddings(options: dict, log: Log | None = None) -> None:
    log = log or Log()
    upload_jsonl_files(
        outbox_dir=settings.PIPELINE_DATA_DIR / "embeddings_outbox",
        archive_dir=settings.PIPELINE_DATA_DIR / "embeddings_archive",
        endpoint_path="/api/pipeline/embeddings/",
        log=log,
    )
