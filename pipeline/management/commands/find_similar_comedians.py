# This command is the discovery half of the comedian-name cleanup flow.
#
# The archive under pipeline/data/bit_annotated_set_archive is treated as raw
# source data and should not be rewritten when a name is misspelled. Instead,
# imports canonicalize names through pipeline/data/comedian_name_relationships.json.
#
# Flow:
#   1. import_sets loads known relationships and applies aliases before DB upsert.
#      This prevents approved spelling variants from creating duplicate comedians.
#   2. At the end of import_sets, this command scans the resulting Comedian rows
#      for fuzzy-similar names and writes unresolved pairs to
#      pipeline/data/similar_comedian_candidates.json.
#   3. An AI/human reviewer uses prompts/comedian_alias_review_prompt.md to mark
#      each pair as alias, not_alias, or uncertain in comedian_name_relationships.json.
#   4. Future imports skip already-decided pairs and apply approved aliases.
#
# Fuzzy matching is intentionally only used for candidate discovery. Runtime
# imports only trust explicit decisions in the relationship file, so a bad
# decision can be undone by editing that JSON and re-importing from the raw archive.

from django.core.management.base import BaseCommand

from pipeline.models import Comedian
from pipeline.utils.similar_comedians import THRESHOLD, find_candidates, write_candidate_report


class Command(BaseCommand):
    help = "Find likely duplicate comedian names using fuzzy matching."

    def handle(self, *args, **options):
        comedians = list(Comedian.objects.order_by("slug").values_list("name", "slug"))
        candidates = find_candidates(comedians, THRESHOLD)
        report_path = write_candidate_report(candidates)

        self.stdout.write(f"Comedians scanned: {len(comedians)}")
        self.stdout.write(f"Threshold: {THRESHOLD:.1f}")
        self.stdout.write(f"Candidate pairs: {len(candidates)}")
        self.stdout.write(f"Report written: {report_path}")
