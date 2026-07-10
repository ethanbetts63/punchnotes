from hashlib import sha256

from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.beat_utils import beat_display_lines
from api.hf_embeddings import embed_texts
from api.segment_similarity import find_similar_beats_by_segments
from api.serializers.fields import absolute_media_url
from api.set_slugs import set_public_slug
from pipeline.utils.segmenting import segment_beat_lines


MAX_PLAGIARISM_TEXT_LENGTH = 2000
PLAGIARISM_CACHE_TIMEOUT = 60 * 60 * 24 * 7


def plagiarism_cache_key(text):
    # v2: results now include set image_url / youtube_id
    return f"plagiarism:v2:{sha256(text.encode('utf-8')).hexdigest()}"


def segment_query_text(text):
    numbered_lines = [
        (number, stripped)
        for number, line in enumerate(text.splitlines(), start=1)
        if (stripped := line.strip())
    ]
    if not numbered_lines:
        numbered_lines = [(1, text.strip())]
    return [segment.text for segment in segment_beat_lines(numbered_lines)]


class PlagiarismCheckView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "plagiarism"

    def post(self, request):
        raw_text = request.data.get("text")
        if raw_text is not None and not isinstance(raw_text, str):
            return Response({"error": "text must be a string"}, status=status.HTTP_400_BAD_REQUEST)

        text = (raw_text or "").strip()
        if not text:
            return Response({"error": "text is required"}, status=status.HTTP_400_BAD_REQUEST)
        if len(text) > MAX_PLAGIARISM_TEXT_LENGTH:
            return Response(
                {"error": f"text must be {MAX_PLAGIARISM_TEXT_LENGTH} characters or fewer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache_key = plagiarism_cache_key(text)
        cached = cache.get(cache_key)
        if cached is not None:
            return Response({"query": text, "results": cached})

        query_segments = segment_query_text(text)

        try:
            query_vectors = embed_texts(query_segments)
        except TimeoutError as e:
            return Response({"error": str(e)}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception as e:
            return Response({"error": f"Embedding failed: {e}"}, status=status.HTTP_502_BAD_GATEWAY)

        matches = find_similar_beats_by_segments(query_vectors)

        results = []
        for match in matches:
            beat = match["beat"]
            matched_segments = [
                {
                    "text": segment.text,
                    "line_start": segment.line_start,
                    "line_end": segment.line_end,
                    "similarity": round(score, 4),
                }
                for segment, score in match["segments"]
            ]
            results.append({
                "similarity": round(match["best"], 4),
                "beat_id": beat.beat_id,
                "bit_id": beat.bit.bit_id,
                "joke_type": beat.joke_type,
                "comedian": beat.bit.set.comedian.name,
                "comedian_slug": beat.bit.set.comedian.slug,
                "episode_number": beat.bit.set.video.number,
                "set_slug": set_public_slug(beat.bit.set),
                "image_url": absolute_media_url(beat.bit.set.image_url, request),
                "youtube_id": beat.bit.set.video.video_id,
                "premise": beat.premise,
                "lines": beat_display_lines(beat),
                "matched_segments": matched_segments,
            })

        cache.set(cache_key, results, timeout=PLAGIARISM_CACHE_TIMEOUT)
        return Response({"query": text, "results": results})
