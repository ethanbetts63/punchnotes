import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import yt_dlp
from yt_dlp.utils import download_range_func


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = BASE_DIR / "pipeline" / "data" / "4_set_images_inbox"
YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
SLUG_RE = re.compile(r"[^a-z0-9]+")


def parse_time(value):
    text = str(value).strip()
    if not text:
        raise argparse.ArgumentTypeError("timestamp cannot be empty")

    if ":" not in text:
        try:
            seconds = float(text)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"invalid timestamp: {value}") from exc
        if seconds < 0:
            raise argparse.ArgumentTypeError("timestamp must be non-negative")
        return seconds

    parts = text.split(":")
    if len(parts) not in {2, 3}:
        raise argparse.ArgumentTypeError("timestamp must be seconds, MM:SS, or HH:MM:SS")

    try:
        numbers = [float(part) for part in parts]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid timestamp: {value}") from exc

    if any(number < 0 for number in numbers):
        raise argparse.ArgumentTypeError("timestamp must be non-negative")

    if len(numbers) == 2:
        minutes, seconds = numbers
        return minutes * 60 + seconds

    hours, minutes, seconds = numbers
    return hours * 3600 + minutes * 60 + seconds


def seconds_arg(seconds):
    return f"{seconds:.3f}".rstrip("0").rstrip(".")


def youtube_url(video_id=None, url=None):
    if url:
        return url
    if not YOUTUBE_ID_RE.match(video_id or ""):
        raise ValueError("--video-id must be an 11-character YouTube video ID")
    return f"https://www.youtube.com/watch?v={video_id}"


def slugify(value):
    return SLUG_RE.sub("-", value.lower()).strip("-") or "unknown"


def default_output_path(
    video_id,
    capture_seconds,
    episode_number=None,
    set_number=None,
    comic_name=None,
):
    if episode_number is not None and set_number is not None and comic_name:
        return DEFAULT_OUTPUT_DIR / f"KT{episode_number}_set{set_number:02d}_{slugify(comic_name)}.jpg"

    timestamp = str(int(round(capture_seconds))).zfill(5)
    return DEFAULT_OUTPUT_DIR / f"{video_id}_{timestamp}.jpg"


def ydl_options(args):
    options = {
        "format": "best[height<=480]/best[height<=720]/best",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    if args.cookies_from_browser:
        options["cookiesfrombrowser"] = (args.cookies_from_browser,)
    if args.cookies:
        options["cookiefile"] = args.cookies
    return options


def download_clip(source_url, args, clip_start, clip_end, temp_dir):
    output_template = str(temp_dir / "clip.%(ext)s")
    options = {
        **ydl_options(args),
        "outtmpl": output_template,
        "download_ranges": download_range_func(None, [(clip_start, clip_end)]),
        "external_downloader": {"default": "ffmpeg"},
        "force_keyframes_at_cuts": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([source_url])

    clips = [path for path in temp_dir.iterdir() if path.is_file()]
    if not clips:
        raise RuntimeError("yt-dlp did not write a temporary clip")
    return max(clips, key=lambda path: path.stat().st_size)


def grab_frame(video_path, relative_seconds, output_path, width, quality):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg was not found on PATH")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        seconds_arg(relative_seconds),
    ]

    command.extend(
        [
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            "-vf",
            f"scale={width}:-2",
            "-q:v",
            str(quality),
            str(output_path),
        ]
    )

    subprocess.run(command, check=True)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Grab a small still image from a YouTube video at a specific timestamp."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--video-id", help="YouTube video ID, e.g. dQw4w9WgXcQ")
    source.add_argument("--url", help="Full YouTube URL")
    parser.add_argument(
        "--timestamp",
        required=True,
        type=parse_time,
        help="Timestamp in seconds, MM:SS, or HH:MM:SS.",
    )
    parser.add_argument(
        "--offset",
        type=float,
        default=0,
        help="Seconds to add to --timestamp. Use 25-30 for mid-set capture.",
    )
    parser.add_argument(
        "--clip-duration",
        type=float,
        default=0.05,
        help="Temporary clip duration in seconds around the capture point.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output image path. Defaults to pipeline/data/4_set_images_inbox/{name}.jpg",
    )
    parser.add_argument("--episode-number", type=int, help="KT episode number for deterministic filename.")
    parser.add_argument("--set-number", type=int, help="Set number for deterministic filename.")
    parser.add_argument("--comic-name", help="Comic name for deterministic filename.")
    parser.add_argument("--width", type=int, default=480, help="Output width in pixels.")
    parser.add_argument(
        "--quality",
        type=int,
        default=4,
        help="ffmpeg JPEG quality, 2-5 is a useful range. Lower is higher quality.",
    )
    parser.add_argument(
        "--cookies-from-browser",
        choices=["brave", "chrome", "chromium", "edge", "firefox", "opera", "safari", "vivaldi"],
        help="Pass browser cookies to yt-dlp for age-gated videos.",
    )
    parser.add_argument("--cookies", help="Path to a Netscape cookies.txt file for yt-dlp.")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    capture_seconds = args.timestamp + args.offset
    if capture_seconds < 0:
        parser.error("--timestamp + --offset must be non-negative")
    if args.width < 1:
        parser.error("--width must be positive")
    if args.quality < 1:
        parser.error("--quality must be positive")
    if args.clip_duration <= 0:
        parser.error("--clip-duration must be positive")
    filename_parts = [args.episode_number is not None, args.set_number is not None, bool(args.comic_name)]
    if any(filename_parts) and not all(filename_parts):
        parser.error("--episode-number, --set-number, and --comic-name must be supplied together")

    source_url = youtube_url(video_id=args.video_id, url=args.url)
    output_path = args.output or default_output_path(
        args.video_id or "youtube",
        capture_seconds,
        args.episode_number,
        args.set_number,
        args.comic_name,
    )

    half_clip = args.clip_duration / 2
    clip_start = max(capture_seconds - half_clip, 0)
    clip_end = capture_seconds + half_clip
    relative_seconds = capture_seconds - clip_start

    with tempfile.TemporaryDirectory(prefix="punchnotes_frame_") as tmp:
        clip_path = download_clip(source_url, args, clip_start, clip_end, Path(tmp))
        grab_frame(clip_path, relative_seconds, output_path, args.width, args.quality)

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
