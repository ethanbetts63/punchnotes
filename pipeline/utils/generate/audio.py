from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings

from pipeline.utils.http import pipeline_session, server_url
from pipeline.utils.filenames import safe_filename_part
from pipeline.log import Log


DEFAULT_COOKIES_NAME = "www.youtube.com_cookies.txt"


def video_filename(video) -> str:
    publish_date = video.date.isoformat() if video.date else "unknown-date"
    title = safe_filename_part(video.title)
    return f"{video.video_id} - {publish_date} - {title}.%(ext)s"


def find_audio(video_id: str, *audio_dirs: Path) -> Path | None:
    for audio_dir in audio_dirs:
        matches = list(audio_dir.glob(f"{video_id} - *.*"))
        if matches:
            return matches[0]
    return None


def ydl_options(options: dict, extra: dict | None = None) -> dict:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "js_runtimes": {"node": {}},
        "remote_components": ["ejs:github"],
    }
    if options.get("cookies_from_browser"):
        ydl_opts["cookiesfrombrowser"] = (options["cookies_from_browser"],)
    if options.get("cookies"):
        ydl_opts["cookiefile"] = options["cookies"]
    elif not options.get("cookies_from_browser"):
        default_cookies = settings.PIPELINE_DATA_DIR / DEFAULT_COOKIES_NAME
        if default_cookies.exists():
            ydl_opts["cookiefile"] = str(default_cookies)
    if extra:
        ydl_opts.update(extra)
    return ydl_opts


def _post_history(session, record: dict) -> None:
    try:
        session.post(server_url("/api/pipeline/audio-history/"), json=record)
    except Exception:
        pass


def generate_audio(options: dict, log: Log) -> None:
    import yt_dlp
    from pipeline.models import Video

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

    videos = list(
        Video.objects.exclude(video_id__isnull=True).exclude(video_id="").order_by("-number", "video_id")
    )
    if not videos:
        log("No Video rows found. Import video metadata first.")
        return

    already_present = skipped_failed = downloaded = failed = attempted = 0

    for video in videos:
        video_id = video.video_id

        if find_audio(video_id, inbox_dir, archive_dir) or video_id in downloaded_ids:
            already_present += 1
            continue

        if video_id in failed_ids and not retry_failures:
            skipped_failed += 1
            continue

        if limit is not None and attempted >= limit:
            break

        attempted += 1
        outtmpl = str(inbox_dir / video_filename(video))
        dl_opts = ydl_options(options, {"format": "bestaudio/best", "outtmpl": outtmpl})
        video_url = video.url or f"https://www.youtube.com/watch?v={video_id}"

        log(f"  [{video_id}] downloading audio...")
        try:
            with yt_dlp.YoutubeDL(dl_opts) as ydl:
                ydl.download([video_url])
        except yt_dlp.utils.DownloadError as e:
            failed += 1
            _post_history(session, {"video_id": video_id, "episode_number": video.number, "status": "failed", "error": str(e)})
            log.warning(f"  [{video_id}] failed: {e}")
            continue

        downloaded += 1
        _post_history(session, {"video_id": video_id, "episode_number": video.number, "status": "downloaded"})
        log(f"  [{video_id}] done")

    log.success(
        f"Done. {downloaded} downloaded, {already_present} already present, "
        f"{skipped_failed} skipped failures, {failed} failed."
    )
