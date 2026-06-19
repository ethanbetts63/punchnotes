from django.conf import settings

from pipeline.utils.http import upload_jsonl_files_chunked
from pipeline.log import Log


EMBEDDINGS_UPLOAD_CHUNK_SIZE = 100


def upload_embeddings(options: dict, log: Log) -> None:
    upload_jsonl_files_chunked(
        outbox_dir=settings.PIPELINE_DATA_DIR / "embeddings_outbox",
        archive_dir=settings.PIPELINE_PRIVATE_DATA_DIR / "embeddings_archive",
        endpoint_path="/api/pipeline/embeddings/",
        chunk_size=EMBEDDINGS_UPLOAD_CHUNK_SIZE,
        log=log,
    )
