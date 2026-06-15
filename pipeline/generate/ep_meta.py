import shutil

from django.conf import settings

from pipeline.log import Log


def generate_ep_meta(options: dict, log: Log | None = None) -> None:
    log = log or Log()
    from django.core.management import call_command

    outbox_dir = settings.PIPELINE_DATA_DIR / "ep_meta_outbox"
    outbox_dir.mkdir(parents=True, exist_ok=True)

    mode = "--full" if options.get("full", True) else "--basic"
    call_command("fetch_episodes", mode)

    src_name = "full_kt_episodes.jsonl" if mode == "--full" else "basic_kt_episodes.jsonl"
    src = settings.PIPELINE_DATA_DIR / src_name
    if src.exists():
        dest = outbox_dir / src.name
        shutil.copy2(src, dest)
        log(f"Written to {dest}")
    else:
        log.warning("fetch_episodes produced no output file.")
