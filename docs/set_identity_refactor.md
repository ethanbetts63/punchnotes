# Refactor: remove `set_number` entirely

## Background

`Set.set_number` (`pipeline/models/set.py:18`) is not stable — it's recomputed by
`resequence_video_sets()` (`pipeline/utils/update/records.py:61`) from `start_seconds`
every time a set is inserted/upserted for a video. Anything that treats `set_number` as
a durable identifier (embeds it in a filename, a public URL, or a natural key used to
look a record back up) silently breaks whenever an unrelated set earlier in the same
episode is added or reordered — the "same" number now points at a different set.

`start_seconds` (`pipeline/management/commands/extract_set.py:234`) is the actual
durable identity: it's the timestamp of the first transcript line assigned to the set,
fixed once at extraction time, re-derived from the same archived per-set JSON
(`pipeline/data_private/bit_annotated_set_archive/`) on every DB reset. `upsert_set()`
(`records.py:87`) already uses it this way — `video.sets.filter(start_seconds=...)` —
to find the same Set again across reimports.

**Decision: `set_number` is not being demoted to a display-only field — it is being
deleted entirely**, column and all. Nothing needs to show a set's ordinal position to
the user. Every current use — identity, ordering, and display — is replaced by
`start_seconds` (or dropped outright where it was only ever there to render a number).

One thing any replacement must preserve: a comedian can legitimately have more than one
set in the same episode (`MULTI_SET_ALLOWED_COMEDIANS`, checked in
`extract_set.py:220`), so a bare `{video_id}-{comedian_slug}` slug isn't always unique.
`start_seconds` disambiguates these fine since two sets never share a start time —
that's what the new uniqueness constraint enforces (see Schema, below).

## Inventory

### A. Identity/lookup uses — swap key to `start_seconds`

1. **Public Set URL slug** — `api/set_slugs.py:8-23` (`SET_SLUG_RE`, `set_public_slug()`,
   `_parse_set_slug()`). Currently builds/parses `{video_id}-set{NN}-{comedian_slug}`.
   New form: `{video_id}-{start_seconds}-{comedian_slug}` (or similar — exact format is
   an implementation detail, the only requirement is it no longer contains an ordinal).
   Consumed by:
   - `api/serializers/shared.py:9-13` (`PublicSetSlugMixin`, used by `set.py`,
     `comedian.py`, `video.py` serializers)
   - `api/serializers/bit.py:24`, `api/serializers/joke.py:28`
   - `api/views/search.py:156,183`
   - `api/views/plagiarism.py:66`
   **Highest priority** — this is the public, indexable URL for a set. Right now, when
   any set earlier in an episode gets renumbered, every *other* set's canonical URL in
   that episode silently starts resolving to different content. Unlike the image bug,
   this is user/SEO-visible in production today, with no error anywhere to notice it by.
   Changing the slug format is itself a breaking change for anyone with an old link
   bookmarked/indexed — decide whether that's acceptable or whether old-format slugs
   need a redirect/fallback lookup for some transition window.

2. **Beat slug** — `pipeline/utils/beats_by_joke_type.py:53-58` (`build_beat_slug()`),
   same `set{NN}` pattern and same fix, smaller surface (joke-type beat listings).

3. **Set image filenames + lookup** — the bug that started this investigation:
   `pipeline/utils/set_images.py` (`IMAGE_NAME_RE`, `parse_image_name`,
   `rename_set_image`), `pipeline/utils/update/set_images.py` (`ingest_set_image` looks
   up `Set.objects.get(video__number=, set_number=)`), `pipeline/utils/fix/set_image_archive.py`,
   `pipeline/utils/generate/set_images.py` (`default_output_path`),
   `pipeline/scripts/grab_set_image.py` (`default_output_path`, and its `--set-number`
   CLI flag — drop the flag entirely, nothing downstream needs it once filenames key
   off `start_seconds`).

4. **Embeddings natural key** — `pipeline/utils/update/embeddings.py` `_parse_key()`
   (regex `ep(\d+)\.set(\d+)\.bit(\d+)\.beat(\d+)`) then
   `Beat.objects.get(bit__set__set_number=, bit__set__video__number=)`;
   `pipeline/utils/generate/embeddings.py` writes that same key from the *current*
   `bit__set__set_number` at generation time. **Worse failure mode than images**: if a
   resequence happens while an outbox/archive JSONL is still unimported, re-ingesting it
   doesn't just fail — it can silently attach an embedding to the *wrong* beat, if
   another set in the same episode happens to have a bit/beat with the same ordinal.
   No mismatch check catches this today (unlike `ingest_set_image`'s slug check).

5. **Segment embeddings natural key** — `pipeline/utils/update/segment_embeddings.py`
   (parse/lookup ~lines 68-100, 175-228), same shape and same risk as #4, for
   `BeatSegment`.

### B. Ordering — trivial swap

6. `pipeline/utils/beats_by_joke_type.py:69,90` — `order_by(..., "bit__set__set_number", ...)`
7. `pipeline/utils/update/embeddings.py:37`, `pipeline/utils/update/segment_embeddings.py`
   equivalents — swap to `start_seconds`. (`Set.Meta.ordering = ['start_seconds']`
   already, so this just brings these queries in line with the model default.)

### C. Schema — delete the column

8. `pipeline/models/set.py:18` — delete the `set_number` field.
9. `pipeline/models/set.py:33` — replace `unique_together = [['video', 'set_number']]`
   with `[['video', 'start_seconds']]` (the invariant `upsert_set` already assumes,
   just not DB-enforced yet).
10. `pipeline/utils/update/records.py:49-58` (`_apply_set_number`) and the two-pass
    renumbering in `resequence_video_sets` (`records.py:61-73`) — delete entirely, along
    with their call to `rename_set_image(set_obj, new_number)`. Once nothing is keyed
    on `set_number`, there is nothing left to resequence.
11. New migration to drop the column and old constraint, add the new one.

### D. Display uses — delete, don't just leave alone

12. Frontend: `frontend/lib/serverApi.ts` (4 type-def spots), `sets/[slug]/page.tsx:123`,
    `sets/search/SetSearchResults.tsx:31`, `episodes/[slug]/page.tsx:139`,
    `comedians/[slug]/ComedianSetList.tsx:36,42` — remove the `"Set {n}"` labels/alt-text
    and the `set_number` field from the TS types. (`ComedianSetList.tsx` renders a list
    of a comedian's sets across different videos — check what, if anything, replaces
    "Set N" there for basic list-item identification; likely nothing needs to, since the
    video title + start time are already shown alongside it per the other call sites.)
13. `pipeline/admin.py:25` — drop `set_number` from `list_display`.
14. `pipeline/utils/update/annotated.py:48` — drop `set_number` from the returned
    status dict (or replace with `start_seconds` if the caller wants a distinguishing
    value in the log line).
15. `api/serializers/set.py`, `comedian.py`, `video.py` — remove `set_number` from every
    `Meta.fields` list.

### E. Tests

Will need updating in lockstep with whichever production file each covers — no separate
design decision, just follow-through: `pipeline/tests/utils/update/test_set_images.py`,
`test_comedian_aliases.py`, `test_records.py`, `test_update_segment_embeddings.py`;
`pipeline/tests/management/commands/test_generate_segment_embedding_report.py`,
`test_beats_by_joke_type.py`, `test_generate_embedding_report.py`;
`pipeline/tests/utils/generate/test_embeddings.py`; `pipeline/tests/conftest.py` and
`api/tests/conftest.py` factories (these almost certainly construct `Set` objects by
passing `set_number=` — every factory call site needs it dropped); `api/tests/views/test_search.py`,
`test_comedian.py`, `test_set.py`, `test_bit.py`, `test_video.py`.

## Sequencing

1. Add the `(video, start_seconds)` uniqueness constraint alongside the existing
   `set_number` one (both live briefly) — purely additive, no behavior change.
2. Cut over the five identity/lookup sites (A1–A5) to `start_seconds`, independently,
   each shippable on its own:
   a. Set image filename/lookup (already scoped in the prior image-drift investigation)
   b. Set slug + beat slug (decide the redirect/compat question from A1 first)
   c. Embeddings key
   d. Segment embeddings key
3. Swap the two ordering call sites (B) to `start_seconds`.
4. Delete `_apply_set_number` / the renumbering pass in `resequence_video_sets` (C10) —
   only safe once A1–A5 no longer depend on `set_number` being kept in sync.
5. Remove all display uses (D) — frontend labels/types, admin column, serializer
   fields, log dict key.
6. Update tests alongside each cutover in steps 2 and 5.
7. Migration: drop the `set_number` column and its old unique constraint.
8. Backfill anything already on disk or published under the old scheme (image rename
   plan from the earlier discussion; resolve the old-slug compat question from A1).

## Risks worth flagging before starting

- **A1 (public slug)** is the biggest undiscovered instance of this bug class — it's
  live and silently redirecting users/search engines to the wrong set right now,
  whenever an episode's sets get renumbered. Worth prioritizing over the image work
  that originally surfaced this pattern. Changing the slug format is also the one
  externally-visible breaking change in this whole refactor — worth deciding up front
  whether old links just 404/redirect or need a compatibility lookup.
- **A4/A5 (embeddings)** can silently produce a *wrong* answer (mis-attached embedding),
  not just a missing one — worth auditing existing embeddings for episodes that have
  had any resequencing history before assuming current data is clean, not just fixing
  the ingestion path prospectively.
- Deleting `resequence_video_sets`'s renumbering pass (C10) removes the only code that
  currently keeps multiple sets in a video in a sensible order *for anything that still
  cares about order* (i.e. display lists) — confirm every list view already sorts by
  `start_seconds` at read time (the model's default `ordering` suggests yes) rather than
  relying on `set_number` having been pre-sorted into place.
