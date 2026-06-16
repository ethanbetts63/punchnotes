import json
from datetime import datetime, timezone

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from pipeline.auth import PipelineKeyPermission


class PipelineView(APIView):
    authentication_classes = []
    permission_classes = [PipelineKeyPermission]


class AnnotatedSetView(PipelineView):
    def post(self, request):
        from pipeline.utils.comedian_aliases import load_relationships
        from pipeline.utils.update.annotated import ingest_annotated_set
        defer_refresh = request.query_params.get("defer_refresh") == "1"
        try:
            result = ingest_annotated_set(request.data, load_relationships(), defer_refresh=defer_refresh)
            return Response(result)
        except Exception as e:
            return Response({"status": "error", "error": str(e)}, status=400)


class RefreshStatsView(PipelineView):
    def post(self, request):
        from pipeline.utils.update.annotated import refresh_all_stats
        try:
            refresh_all_stats()
            return Response({"status": "ok"})
        except Exception as e:
            return Response({"status": "error", "error": str(e)}, status=400)


class ComedianCandidatesView(PipelineView):
    def get(self, request):
        path = settings.PIPELINE_DATA_DIR / "similar_comedian_candidates.json"
        if not path.exists():
            return Response({"threshold": 80.0, "candidate_count": 0, "candidates": []})
        return Response(json.loads(path.read_text(encoding="utf-8")))


class ComedianAliasesView(PipelineView):
    def post(self, request):
        from pipeline.utils.comedian_aliases import validate_relationships
        inbox_dir = settings.PIPELINE_DATA_DIR / "comedian_aliases_inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)
        try:
            validate_relationships(request.data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        dest = inbox_dir / "comedian_name_relationships.json"
        dest.write_text(json.dumps(request.data, indent=2) + "\n", encoding="utf-8")
        return Response({"status": "ok"})


class AudioHistoryView(PipelineView):
    _HISTORY_NAME = "audio_fetch_history.jsonl"

    def _path(self):
        return settings.PIPELINE_DATA_DIR / self._HISTORY_NAME

    def get(self, request):
        path = self._path()
        downloaded: set[str] = set()
        failed: set[str] = set()
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                vid = record.get("video_id")
                if not vid:
                    continue
                status = record.get("status")
                if status == "downloaded":
                    downloaded.add(vid)
                    failed.discard(vid)
                elif status == "failed":
                    if vid not in downloaded:
                        failed.add(vid)
        return Response({"downloaded": list(downloaded), "failed": list(failed)})

    def post(self, request):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **request.data,
        }
        with self._path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        return Response({"status": "ok"})


class EpMetaView(PipelineView):
    def post(self, request):
        inbox_dir = settings.PIPELINE_DATA_DIR / "ep_meta_inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        dest = inbox_dir / f"ep_meta_{ts}.jsonl"
        content = request.body
        dest.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
        return Response({"status": "queued", "file": dest.name}, status=202)


class VideoScrapeQueueView(PipelineView):
    def _to_scrape_path(self):
        return settings.PIPELINE_DATA_DIR / "videos_to_scrape.jsonl"

    def _history_path(self):
        return settings.PIPELINE_DATA_DIR / "video_scrape_history.jsonl"

    def _read_jsonl(self, path):
        if not path.exists():
            return []
        records = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return records

    def get(self, request):
        from pipeline.models import Video

        to_scrape = self._read_jsonl(self._to_scrape_path())
        if not to_scrape:
            return Response({"videos": []})

        known = set(Video.objects.values_list("video_id", flat=True))
        for record in self._read_jsonl(self._history_path()):
            vid = record.get("video_id")
            if vid:
                known.add(vid)

        remaining = [r for r in to_scrape if r.get("video_id") not in known]

        if len(remaining) < len(to_scrape):
            self._to_scrape_path().write_text(
                "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in remaining),
                encoding="utf-8",
            )

        return Response({"videos": remaining})


class VideoScrapeResultView(PipelineView):
    def _history_path(self):
        return settings.PIPELINE_DATA_DIR / "video_scrape_history.jsonl"

    def post(self, request):
        video_id = request.data.get("video_id")
        status = request.data.get("status")
        if not video_id or status not in ("success", "failed"):
            return Response({"error": "video_id and status (success|failed) required"}, status=400)

        record = {
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "video_id": video_id,
            "status": status,
        }
        if request.data.get("error"):
            record["error"] = request.data["error"]

        with self._history_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

        return Response({"status": "ok"})


class MissingSetImagesView(PipelineView):
    def get(self, request):
        from pipeline.utils.update.set_images import missing_image_sets
        return Response({"sets": missing_image_sets()})


class SetImagesView(PipelineView):
    def post(self, request):
        inbox_dir = settings.PIPELINE_DATA_DIR / "set_images_inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)
        image_file = request.FILES.get("image")
        if not image_file:
            return Response({"error": "No image file provided."}, status=400)
        dest = inbox_dir / image_file.name
        with dest.open("wb") as f:
            for chunk in image_file.chunks():
                f.write(chunk)
        return Response({"status": "queued", "file": image_file.name}, status=202)


class UnembeddedBeatsView(PipelineView):
    def get(self, request):
        from pipeline.utils.update.embeddings import unembedded_beats
        return Response({"beats": unembedded_beats()})


class EmbeddingsView(PipelineView):
    def post(self, request):
        inbox_dir = settings.PIPELINE_DATA_DIR / "embeddings_inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        dest = inbox_dir / f"embeddings_{ts}.jsonl"
        content = request.body
        dest.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
        return Response({"status": "queued", "file": dest.name}, status=202)
