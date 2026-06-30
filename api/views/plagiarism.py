from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.beat_utils import describe_beat_lines
from api.hf_embeddings import embed_text
from api.set_slugs import set_public_slug
from api.similarity import find_similar_beats


class PlagiarismCheckView(APIView):
    def post(self, request):
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response({"error": "text is required"}, status=status.HTTP_400_BAD_REQUEST)

        cached = cache.get(f"plagiarism:{text}")
        if cached is not None:
            return Response({"query": text, "results": cached})

        try:
            query_vector = embed_text(text)
        except TimeoutError as e:
            return Response({"error": str(e)}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception as e:
            return Response({"error": f"Embedding failed: {e}"}, status=status.HTTP_502_BAD_GATEWAY)

        matches = find_similar_beats(query_vector)

        results = []
        for sim, beat in matches:
            beat_data = describe_beat_lines(beat)
            results.append({
                "similarity": round(sim, 4),
                "beat_id": beat.beat_id,
                "bit_id": beat.bit.bit_id,
                "joke_type": beat.joke_type,
                "comedian": beat.bit.set.comedian.name,
                "comedian_slug": beat.bit.set.comedian.slug,
                "episode_number": beat.bit.set.video.number,
                "set_slug": set_public_slug(beat.bit.set),
                "premise": beat.premise,
                "setup_lines": beat_data["setup_lines"],
                "punchline": beat_data["punchline"],
            })

        cache.set(f"plagiarism:{text}", results, timeout=None)
        return Response({"query": text, "results": results})
