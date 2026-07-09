from django.conf import settings

from pipeline.log import Log
from pipeline.utils.http import upload_jsonl_files_chunked


SEGMENT_EMBEDDINGS_UPLOAD_CHUNK_SIZE = 100


def upload_segment_embeddings(options: dict, log: Log) -> None:
    upload_jsonl_files_chunked(
        outbox_dir=settings.PIPELINE_DATA_DIR / "segment_embeddings_outbox",
        endpoint_path="/api/pipeline/segment-embeddings/",
        chunk_size=SEGMENT_EMBEDDINGS_UPLOAD_CHUNK_SIZE,
        log=log,
    )
