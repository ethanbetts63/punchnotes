from django.core.management.base import BaseCommand

from pipeline.log import Log


class Command(BaseCommand):
    help = "Generate pipeline data locally (audio, transcripts, ep metadata, set images, embeddings, comedian aliases)"

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--ep_meta", action="store_true", help="Scrape episode metadata to ep_meta_outbox/")
        group.add_argument("--audio", action="store_true", help="Download missing audio to audio_inbox/")
        group.add_argument("--restricted_audio", action="store_true", help="Retry failed audio downloads (with cookies)")
        group.add_argument("--transcripts", action="store_true", help="Generate transcripts from audio_inbox/")
        group.add_argument("--comedian_aliases", action="store_true", help="Fetch comedian candidates from server")
        group.add_argument("--set_images", action="store_true", help="Scrape missing set images to set_images_outbox/")
        group.add_argument("--embeddings", action="store_true", help="Compute beat embeddings and write to embeddings_outbox/")
        group.add_argument("--segment_embeddings", action="store_true", help="Compute segment-level beat embeddings and write to segment_embeddings_outbox/")
        group.add_argument("--embeddings_report", action="store_true", help="Generate joke similarity report from stored embeddings")
        group.add_argument("--segment_embeddings_report", action="store_true", help="Generate joke similarity report from stored segment embeddings")

        parser.add_argument("--video", help="Scrape metadata for a single video ID (ep_meta only)")
        parser.add_argument("--limit", type=int, help="Max items to process (audio, set_images)")
        parser.add_argument(
            "--cookies-from-browser",
            choices=["brave", "chrome", "chromium", "edge", "firefox", "opera", "safari", "vivaldi"],
            help="Pass browser cookies to yt-dlp (audio)",
        )
        parser.add_argument("--cookies", help="Path to a Netscape cookies.txt file (audio)")
        parser.add_argument("--offset", type=float, default=30, help="Seconds after set start to capture image")
        parser.add_argument("--clip-duration", type=float, default=0.05, help="Clip duration for image capture")
        parser.add_argument("--width", type=int, default=480, help="Output image width in pixels")
        parser.add_argument("--quality", type=int, default=4, help="ffmpeg JPEG quality")
        parser.add_argument("--local", action="store_true", help="Target local dev server (applies to: --audio, --comedian_aliases, --set_images, --embeddings, --segment_embeddings)")
        parser.add_argument("--batch-size", type=int, default=32, help="Embedding batch size (embeddings only)")
        parser.add_argument("--device", choices=["cpu", "cuda", "mps"], help="Embedding device override (embeddings only)")

    def handle(self, *args, **options):
        if options["local"]:
            if options.get("ep_meta") or options.get("transcripts"):
                self.stdout.write(self.style.WARNING("--local has no effect with --ep_meta or --transcripts"))
            from django.conf import settings
            settings.SERVER_BASE_URL = settings.LOCAL_SERVER_URL
        log = Log(self.stdout, self.style)

        if options["ep_meta"]:
            from pipeline.utils.generate.ep_meta import generate_ep_meta
            generate_ep_meta(options, log)

        elif options["audio"]:
            from pipeline.utils.generate.audio import generate_audio
            generate_audio(options, log)

        elif options["restricted_audio"]:
            from pipeline.utils.generate.audio import generate_audio
            generate_audio({**options, "retry_failures": True}, log)

        elif options["transcripts"]:
            from pipeline.utils.generate.transcripts import generate_transcripts
            generate_transcripts(options, log)

        elif options["comedian_aliases"]:
            from pipeline.utils.generate.comedian_aliases import generate_comedian_aliases
            generate_comedian_aliases(log)

        elif options["set_images"]:
            from pipeline.utils.generate.set_images import generate_set_images
            generate_set_images(options, log)

        elif options["embeddings"]:
            from pipeline.utils.generate.embeddings import generate_embeddings
            generate_embeddings(options, log)

        elif options["segment_embeddings"]:
            from pipeline.utils.generate.segment_embeddings import generate_segment_embeddings
            generate_segment_embeddings(options, log)

        elif options["embeddings_report"]:
            from pipeline.utils.generate.embeddings_report import generate_embeddings_report
            generate_embeddings_report(log)

        elif options["segment_embeddings_report"]:
            from pipeline.utils.generate.segment_embeddings_report import generate_segment_embeddings_report
            generate_segment_embeddings_report(log)
