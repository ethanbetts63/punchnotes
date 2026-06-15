from django.conf import settings

from pipeline.local_utils.http import pipeline_session, server_url
from pipeline.log import Log


def _post_history(session, record: dict) -> None:
    try:
        session.post(server_url("/api/pipeline/audio-history/"), json=record)
    except Exception:
        pass


def generate_audio(options: dict, log: Log | None = None) -> None:
    import yt_dlp
    from pipeline.management.commands.fetch_audio import episode_filename, find_audio, ydl_options
    from pipeline.models import Video

    log = log or Log()
    data_dir = settings.PIPELINE_DATA_DIR
    inbox_dir = data_dir / "0_audio_inbox"
    archive_dir = data_dir / "audio_archive"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    session = pipeline_session()
    resp = session.get(server_url("/api/pipeline/audio-history/"))
    resp.raise_for_status()
    server_data = resp.json()
    downloaded_ids = set(server_data.get("downloaded", []))
    failed_ids = set(server_data.get("failed", []))

    retry_failures = options.get("retry_failures", False)
    limit = options.get("limit")

    episodes = list(
        Video.objects.exclude(video_id__isnull=True).exclude(video_id="").order_by("-number", "video_id")
    )
    if not episodes:
        log("No Episode rows found. Import episode metadata first.")
        return

    already_present = skipped_failed = downloaded = failed = attempted = 0

    for episode in episodes:
        video_id = episode.video_id

        if find_audio(video_id, inbox_dir, archive_dir) or video_id in downloaded_ids:
            already_present += 1
            continue

        if video_id in failed_ids and not retry_failures:
            skipped_failed += 1
            continue

        if limit is not None and attempted >= limit:
            break

        attempted += 1
        outtmpl = str(inbox_dir / episode_filename(episode))
        dl_opts = ydl_options(options, {"format": "bestaudio/best", "outtmpl": outtmpl})
        episode_url = episode.url or f"https://www.youtube.com/watch?v={video_id}"

        log(f"  [{video_id}] downloading audio...")
        try:
            with yt_dlp.YoutubeDL(dl_opts) as ydl:
                ydl.download([episode_url])
        except yt_dlp.utils.DownloadError as e:
            failed += 1
            _post_history(session, {"video_id": video_id, "episode_number": episode.number, "status": "failed", "error": str(e)})
            log.warning(f"  [{video_id}] failed: {e}")
            continue

        downloaded += 1
        _post_history(session, {"video_id": video_id, "episode_number": episode.number, "status": "downloaded"})
        log(f"  [{video_id}] done")

    log.success(
        f"Done. {downloaded} downloaded, {already_present} already present, "
        f"{skipped_failed} skipped failures, {failed} failed."
    )
