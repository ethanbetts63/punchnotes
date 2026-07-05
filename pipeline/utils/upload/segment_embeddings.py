from django.conf import settings

from pipeline.log import Log
from pipeline.utils.http import upload_jsonl_files_chunked


SEGMENT_EMBEDDINGS_UPLOAD_CHUNK_SIZE = 100


def upload_segment_embeddings(options: dict, log: Log) -> None:
    archive_dir = settings.PIPELINE_PRIVATE_DATA_DIR / "segment_embeddings_archive"
    upload_from_archive = options.get("archive", False)
    upload_jsonl_files_chunked(
        outbox_dir=archive_dir if upload_from_archive else settings.PIPELINE_DATA_DIR / "segment_embeddings_outbox",
        archive_dir=archive_dir,
        endpoint_path="/api/pipeline/segment-embeddings/",
        chunk_size=SEGMENT_EMBEDDINGS_UPLOAD_CHUNK_SIZE,
        log=log,
        move_to_archive=not upload_from_archive,
    )
