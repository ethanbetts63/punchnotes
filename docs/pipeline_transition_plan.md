# Pipeline Server/Local Transition Plan

## Overview

Split the pipeline between a local dev machine (heavy I/O, scraping, compute) and the
production server (DB, API, frontend). Three top-level management commands replace most
of the existing ad-hoc commands:

- `generate` — local only. Produces output files (audio, transcripts, annotated sets,
  set images, episode metadata, embeddings). All logic lives in a separate util module.
- `upload` — local only. Reads from a local outbox dir, POSTs to a server API endpoint,
  archives locally on success. All logic lives in a separate util module.
- `update` — server only. Reads from a server inbox dir, writes to the DB. All logic
  lives in a separate util module.

Most server/local-split tasks follow the three-step pattern:
`generate --<task>` → `upload --<task>` → `update --<task>`

**Exception — annotated sets:** `upload --annotated` triggers immediate server-side
ingestion and returns errors directly to the caller. There is no separate `update`
step for this task.

Tasks that are purely local (transcription, AI annotation, normalize_archive) keep their
existing commands or run inside the AI flow as before.

---

## Directory Layout Changes

### Local machine

New outbox dirs alongside existing inboxes:

```
pipeline/data/
  0_audio_inbox/              (unchanged — yt-dlp output)
  audio_archive/              (unchanged — local redundancy)
  1_transcript_inbox/         (unchanged — generate_transcripts output)
  transcript_archive/         (unchanged)
  2_set_inbox/                (unchanged — AI annotation output)
  bit_annotated_set_archive/  (unchanged — local copy after successful upload)
  ep_meta_outbox/             (NEW — generate --ep_meta output)
  set_images_outbox/          (NEW — generate --set_images output)
  set_images_archive/         (unchanged — local copy after upload)
  embeddings_outbox/          (NEW — generate --embeddings output)
  embeddings_archive/         (NEW — local copy after upload, keyed by ep.set.bit.beat)
  comedian_aliases_outbox/    (NEW — AI alias review output)
```

### Server

Inbox dirs consumed by `update`, plus server-side data files:

```
pipeline/data/
  ep_meta_inbox/
  set_images_inbox/
  embeddings_inbox/
  comedian_aliases_inbox/
  audio_fetch_history.jsonl   (NEW — gitignored, mirrors current local history file)
  similar_comedian_candidates.json  (written by find_similar_comedians post-import)
```

Note: annotated sets have no server inbox — they are ingested immediately on upload.

---

## Command Specifications

### `generate --ep_meta`
**Replaces:** `fetch_episodes --full`
**Local only.**
Scrapes Kill Tony episode metadata from YouTube (requires local cookies for age-gated
content). Writes output JSONL to `ep_meta_outbox/`.
Util module: `pipeline/local_utils/ep_meta.py`

### `upload --ep_meta`
**New.**
Reads JSONL from `ep_meta_outbox/`, POSTs to `/api/pipeline/ep-meta/` on the server.
Moves uploaded files to a local `ep_meta_archive/` on success.
Util module: `pipeline/local_utils/ep_meta.py`

### `update --ep_meta`
**Replaces:** `import_episodes_jsonl`
**Server only.**
Reads from `ep_meta_inbox/`, upserts Video rows. Moves processed files to a server-side
archive dir.
Util module: `pipeline/server_utils/ep_meta.py`

---

### `generate --audio`
**Replaces:** `fetch_audio --limit N`
**Local only.**
GETs `/api/pipeline/audio-history/` from the server to retrieve the list of video_ids
already downloaded or marked failed. Cross-references with the server DB to find video_ids
that have no transcript yet. Downloads missing audio into `0_audio_inbox/`. Records each
attempt (success or failure) back to the server via POST to `/api/pipeline/audio-history/`.

The server stores download history in `pipeline/data/audio_fetch_history.jsonl` —
same format as the current local file, gitignored. This replaces the local file check
against `0_audio_inbox` and `audio_archive`.

Util module: `pipeline/local_utils/audio.py`

### `generate --restricted_audio`
**Replaces:** `fetch_audio --retry-failures`
**Local only.**
Same as `generate --audio` but retries video_ids marked failed in the server history.
Cookies flow unchanged — local machine handles age-gated content.
Util module: `pipeline/local_utils/audio.py`

*No upload or update step — audio stays entirely local.*

---

### `generate --transcripts`
**Replaces:** `generate_transcripts`
**Local only. No change to logic.**
Reads from `0_audio_inbox/`, writes to `1_transcript_inbox/`. Transcript archive remains
local.

*No upload or update step — server never sees raw transcripts.*

---

### `upload --annotated --file <path>`
### `upload --annotated --dir <dir>`
**Replaces:** `import_sets --file <path>`
**Local only.**
Uploads annotated set JSON(s) to the server. Two modes:
- `--file <path>`: upload a single file from anywhere (used by the AI coordinator
  after each annotation).
- `--dir <dir>`: upload every `.json` file in the given directory (used for bulk
  re-imports from `bit_annotated_set_archive/`).

POSTs each file individually to `/api/pipeline/annotated-set/`. The server ingests
immediately (no separate update step) and returns structured validation errors or a
success summary — same signal the AI currently gets from the local `import_sets`
command. The AI corrects mistakes and retries as before.

On success, archives locally to `bit_annotated_set_archive/`.

Util module: `pipeline/local_utils/annotated.py`

**Server-side behaviour on POST `/api/pipeline/annotated-set/`:**
Runs the existing `import_lines` / `import_bits` / `refresh_*` logic inline. Runs
`find_similar_comedians` after each ingestion and updates
`pipeline/data/similar_comedian_candidates.json` on the server. Returns errors as JSON
with the same structure as the current management command stdout.

*The AI coordinator prompt (`spinup_prompt.md`) is updated to call
`upload --annotated --file <file>` instead of `import_sets --file <file>`.*

*No `update --annotated` command.*

---

### `generate --comedian_aliases`
**Replaces:** the AI reading `similar_comedian_candidates.json` locally
**Local only.**
GETs `/api/pipeline/comedian-candidates/` from the server to fetch the latest
`similar_comedian_candidates.json`. Saves it locally. The AI coordinator then runs the
existing `comedian_alias_review_prompt.md` flow, saves decisions to
`comedian_name_relationships.json`, and writes the file to `comedian_aliases_outbox/`.
Util module: `pipeline/local_utils/comedian_aliases.py`

### `upload --comedian_aliases`
**Local only.**
POSTs updated `comedian_name_relationships.json` from `comedian_aliases_outbox/` to
`/api/pipeline/comedian-aliases/`. Saves to `comedian_aliases_inbox/` on the server.
Util module: `pipeline/local_utils/comedian_aliases.py`

### `update --comedian_aliases`
**Server only.**
Reads the updated relationships from `comedian_aliases_inbox/`, then deduplicates the
Comedian table. For each alias → canonical mapping:
- Treat the canonical name entry as the source of truth.
- Merge any additional info from the alias entry into the canonical entry (attributes,
  image, stats).
- Re-point all Sets, Beats, and guest M2M relations from the alias entry to the
  canonical entry.
- Delete the now-empty alias Comedian record.

Updates the server's `comedian_name_relationships.json` used during future imports.
Util module: `pipeline/server_utils/comedian_aliases.py`

---

### `generate --set_images`
**Replaces:** `fetch_set_images`
**Local only.**
GETs `/api/pipeline/missing-set-images/` from the server (list of comedian slugs /
set identifiers with no image). Scrapes YouTube for each (cookies flow unchanged —
local machine handles age-gated content). Writes scraped images to `set_images_outbox/`.
Util module: `pipeline/local_utils/set_images.py`

### `upload --set_images`
**Local only.**
POSTs images from `set_images_outbox/` to `/api/pipeline/set-images/` on the server.
Archives locally to `set_images_archive/` on success.
Util module: `pipeline/local_utils/set_images.py`

### `update --set_images`
**Replaces:** `import_set_images`
**Server only.**
Reads from `set_images_inbox/`. Saves one image per comedian (reused across their sets)
to `frontend/public/set-images/` rather than per-set images, to control server storage.
Updates `Comedian.image_url` and `Comedian.image_set`. Moves originals to a server-side
archive.
Util module: `pipeline/server_utils/set_images.py`

---

### `generate --embeddings`
**Replaces:** `generate_embeddings`
**Local only.**
GETs `/api/pipeline/unembedded-beats/` from the server — returns a batch of beat records
(stable key + premise text) for beats with no embedding. Runs embedding model locally
(GPU). Writes key-value pairs to `embeddings_outbox/` as JSONL, keyed by
`ep{episode_number}.set{set_number}.bit{bit_number}.beat{beat_number}` (stable across
DB resets).
Util module: `pipeline/local_utils/embeddings.py`

### `upload --embeddings`
**Local only.**
POSTs JSONL from `embeddings_outbox/` to `/api/pipeline/embeddings/`. Archives locally
to `embeddings_archive/` on success. The local archive allows re-uploading all embeddings
after a server DB reset without recomputing.
Util module: `pipeline/local_utils/embeddings.py`

### `update --embeddings`
**Server only.**
Reads from `embeddings_inbox/`, writes embedding vectors to `Beat.embedding`. Resolves
the stable composite key (episode_number + set_number + bit_number + beat_number) back
to a DB PK.
Util module: `pipeline/server_utils/embeddings.py`

*`generate_embeddings_report` — deferred. Decide later whether it moves server-side or
stays local as a reporting tool.*

---

## AI Flow Changes (spinup_prompt.md)

- Step 3C: after annotation, call `upload --annotated --file <file>` instead of
  `import_sets --file <file>`. Error passthrough is identical.
- Step 3E: call `generate --comedian_aliases` to fetch candidates from the server, run
  the review, then call `upload --comedian_aliases`. The `update --comedian_aliases`
  command is run manually to trigger deduplication.

Steps 3A, 3B, 3D (normalize_archive) are unchanged — fully local.

---

## API Endpoints Required (server)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/pipeline/ep-meta/` | Receive episode metadata JSONL, write to inbox |
| GET | `/api/pipeline/audio-history/` | Return server-side audio_fetch_history.jsonl content |
| POST | `/api/pipeline/audio-history/` | Append a download attempt record to server history |
| POST | `/api/pipeline/annotated-set/` | Ingest immediately, return errors or success |
| GET | `/api/pipeline/comedian-candidates/` | Serve similar_comedian_candidates.json |
| POST | `/api/pipeline/comedian-aliases/` | Receive name relationships, write to inbox |
| GET | `/api/pipeline/missing-set-images/` | List comedians/sets with no image |
| POST | `/api/pipeline/set-images/` | Receive scraped images, write to inbox |
| GET | `/api/pipeline/unembedded-beats/` | Return beats with no embedding (stable key + text) |
| POST | `/api/pipeline/embeddings/` | Receive embedding key-value pairs, write to inbox |

All endpoints require API key authentication (shared secret in `.env`, sent as
`Authorization: Bearer <key>` header).

---

## Requirements Split

`requirements.txt` — server only. Excludes: yt-dlp, whisper/transcription libs,
embedding model libs, scraping tools not needed at runtime.

`dev_requirements.txt` — everything. Includes all of `requirements.txt` plus yt-dlp,
transcription, embedding, and scraping dependencies.

---

## Deferred / Out of Scope

- `generate_embeddings_report` — decide after embeddings pipeline is working.
- `reset_db` — keep a local-only dev version. Server reset path: wipe DB, then replay
  from local archives via `upload --annotated --dir bit_annotated_set_archive/` and
  `upload --embeddings` from `embeddings_archive/`.
- Transcript storage / monetisation — transcripts stay local for now.

---

## Build Order

1. API auth skeleton (shared secret middleware)
2. `upload --annotated` + POST endpoint (immediate ingest, errors returned) — core AI loop
3. `generate --comedian_aliases` + `upload --comedian_aliases` + `update --comedian_aliases` (dedup)
4. `generate --audio` + audio history endpoints (server-side history file)
5. `generate/upload --ep_meta` + `update --ep_meta`
6. `generate/upload/update --set_images` + endpoints
7. `generate/upload/update --embeddings` + endpoints
8. Requirements split
9. `reset_db` local-only version (last)
