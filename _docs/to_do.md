
  High
  - process_transcripts.py at the root — legacy script with its own find_sets and extract_joke_book functions that duplicate what the management
  commands now do, plus a hardcoded skip list of specific JSON files. Looks completely dead. Should be deleted.
  - beta_crape_podscripts.py — the beta_ prefix is misleading. Either it's in use (in which case rename it) or it's not (delete it). Having a
  management command with beta_ in production code is confusing.

  Medium
  - dump_transcript in transcript_windows.py and dump_set in extract_set.py are both custom JSON serializers doing essentially the same job — write
  a dict with a lines array in a specific pretty-print format. One shared serializer that takes a schema would eliminate the duplication.
  - Utility functions resolve_joke_book_attribute, find_source_line, and line_end_seconds all live inside extract_set.py rather than in
  pipeline/utils/. Management command files should be thin — logic belongs in utils where it can be tested independently.
  - SET_ATTRIBUTE_VALUES in models/set.py only contains joke book attributes, while the full allowed attribute list lives in extract_set.py and the
  prompt. No single source of truth for what's a valid attribute.

  Low
  - Double period typo in transcript_analysis_prompt.md line 101: "...by the transcript.."
  - JOKE_BOOK_MAP in extract_set.py maps "small" → "small_joke_book" etc — this pattern is also effectively repeated in records.py and the
  serializers. Could be a model-level constant.

  The biggest one by far is process_transcripts.py. Everything else is tidying.


  1. frontend/app/killtony/jokes/JokePlaylists.tsx:1 has a data-shape smell.
     It builds BeatSearchItem objects manually from set detail data. That was a pragmatic fix for the Vercel build issue, but longer term it would
     be cleaner to have one backend endpoint/query that can fetch exact curated beats by set_slug + bit_id + beat_id.



  - BIT_LISTS in frontend/lib/playlists.ts:128 may be unused based on the searches I saw. Worth confirming with rg "BIT_LISTS".

  