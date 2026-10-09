# Pipeline

Ingests and annotates Kill Tony stand-up sets into the DB.

---

## Directory structure

```
pipeline/
  management/commands/   # Three entry-point commands: generate, upload, update
                         # Plus normalize_archives, extract_set, reset_db
  utils/
    generate/            # Local-machine logic: scraping, downloading, embedding, etc.
    upload/              # Local-machine logic: POSTing files to the server inbox
    update/              # Server-side logic: reading inbox files into the DB
    (shared files)       # HTTP session, inbox runner, alias resolution, beats, etc.
  json_validation/       # JSON schema validation for annotated set files
  prompts/               # AI agent prompt files
  models/                # Django models (Video, Set, Comedian, Bit, Beat, Line)
  data/                  # Local data directories (not committed except private repo)
```

## Data directories (`pipeline/data/`)

| Directory | Purpose |
|---|---|
| `audio_inbox/` | Downloaded episode audio |
| `audio_archive/` | Audio that has been transcribed |
| `transcript_inbox/` | Stripped transcripts (`.txt`, line-number-prefixed) awaiting set extraction |
| `set_inbox/` | Extracted sets awaiting annotation (failed archive imports land here too) |
| `annotated_set_inbox/` | (server) Received annotated sets awaiting `update --annotated` |
| `bit_annotated_set_archive/` | Annotated sets — source of truth (private git) |
| `set_images_outbox/` | Scraped images awaiting upload |
| `set_images_inbox/` | (server) Received images awaiting `update --set_images` |
| `set_images_archive/` | Archived set images (untracked) |
| `segment_embeddings_outbox/` | Computed segment embeddings JSONL awaiting upload |
| `segment_embeddings_inbox/` | (server) Received JSONL awaiting `update --segment_embeddings` |
| `comedian_aliases_inbox/` | (server) Received relationships file awaiting `update --comedian_aliases` |
| `kt_ep_archive.jsonl` | Episode metadata archive — appended by `generate --ep_meta`, committed to git, read directly by `update --ep_meta` |
| `videos_to_scrape.jsonl` | (server) Queue of video IDs to fetch metadata for |
| `video_scrape_history.jsonl` | (server) Record of scrape attempts (success/failed) |
| `audio_fetch_history.jsonl` | (server) Record of audio download attempts |
| `similar_comedian_candidates.json` | Fuzzy-matched comedian name pairs for review (private git) |
| `comedian_name_relationships.json` | Reviewed alias/not-alias decisions (private git) |
| `segment_embedding_similarity_report.json` | Segment-level joke similarity report (private git) |

## Conventions

**generate / upload / update split** — `generate` and `upload` run on the local machine; `update` runs on the server. Each command takes a mutually exclusive flag (`--ep_meta`, `--audio`, etc.) selecting the task.

**Outbox / inbox / archive pattern** — `generate` writes files to an `*_outbox/` dir. `upload` POSTs them to the server, which writes them to an `*_inbox/` dir. `update` reads the inbox, ingests to DB, and archives. Upload does nothing except send files to the server inbox.

Segment embeddings are the exception: they are **not archived**. `upload --segment_embeddings` deletes the outbox file once every chunk has been accepted, and `update --segment_embeddings` deletes the inbox file once it has been ingested. The DB is the only store of the vectors — after `reset_db` they must be recomputed with `generate --segment_embeddings`.

**`--archive` flag** — `update --annotated`, `--ep_meta`, and `--set_images` support `--archive`, which reads from the local archive dir instead of the inbox. Used by `reset_db` to rebuild the DB from scratch without re-uploading anything.

**Annotated sets** — `upload --annotated` writes to `annotated_set_inbox/`. Run `update --annotated` to ingest from inbox (moves files to `bit_annotated_set_archive/`). Run `update --annotated --archive` to re-import from archive.

**Auth** — all pipeline API endpoints use `Authorization: Bearer <PIPELINE_API_KEY>`.

**Comedian name canonicalisation** — names are slugified on import and resolved through `pipeline/data/comedian_name_relationships.json` before DB upsert. The fuzzy candidate report (`similar_comedian_candidates.json`) is regenerated after every annotated set upload. Alias decisions are reviewed with `prompts/comedian_alias_review_prompt.md` then applied with `upload --comedian_aliases` + `update --comedian_aliases`.

---

## Pipeline flow

(generate & upload are local, update is a server command)

env. requires `PIPELINE_API_KEY=<secret>` `SERVER_BASE_URL=https://server.com`
Adding `--local` to any upload or generate command will make it use dev server rather than production.

**1. Sync episode metadata (manual):**
```
python manage.py generate --ep_meta
# commit and push kt_ep_archive.jsonl
python manage.py update --ep_meta
```
Purpose: pull the scrape queue from the server (`videos_to_scrape.jsonl`), fetch full metadata per video from YouTube, append to `kt_ep_archive.jsonl`. Commit and push the archive, then run `update --ep_meta` on the server to read from it directly. Each result (success or failure) is reported back to the server and recorded in `video_scrape_history.jsonl` so the queue stays clean.

To scrape a single video without touching the queue:
```
python manage.py generate --ep_meta --video <video_id>
```

To seed the queue, add `{"video_id": "..."}` lines to `pipeline/data/videos_to_scrape.jsonl` on the server. The queue endpoint removes entries that are already in the DB or history before returning.

**2. Get transcripts:**
```
python manage.py generate --audio --limit 20
python manage.py generate --transcripts
pipeline/data/transcript_inbox/
```
Transcripts are archived as full JSON in `data_private/transcript_archive/`. A stripped `.txt` version (line number + text only, annotation lines removed) is written to `transcript_inbox/` for the AI to read. The `extract_set` command always reads from the archive, not the inbox.

Age restricted videos:

A. log in youtube, go to https://www.youtube.com/robots.txt, use "get cookies.txt LOCALLY" chrome extension and drop in `pipeline/data/`

B. Run `python manage.py generate --restricted_audio`

**3. AI Flow:**

A. AI coordinator receives: `prompts/spinup_prompt.md` (tell the coordinator to use `--local` if required)

B. If files in `transcript_inbox`, spins up agent with `prompts/transcript_analysis_prompt.md`

C. If files in `set_inbox`, spins up agent with `prompts/annotation_prompt`

D. Runs `python manage.py normalize_archives` to normalise JSON formatting in the archives

E. Run `upload --annotated` then `update --annotated` to ingest annotated sets into the DB

F. Review `pipeline/data/similar_comedian_candidates.json` with `prompts/comedian_alias_review_prompt.md`, save decisions in `pipeline/data/comedian_name_relationships.json` then run:
```
python manage.py upload --comedian_aliases
python manage.py update --comedian_aliases
```

**4. Fetch set images:**
```
python manage.py generate --set_images
python manage.py upload --set_images
python manage.py update --set_images
```
Purpose: checks server for missing comedian images, scrapes locally, uploads, imports to DB

**5. Joke similarity scoring:**
```
python manage.py generate --segment_embeddings
python manage.py upload --segment_embeddings
python manage.py update --segment_embeddings
python manage.py generate --segment_embeddings_report
```
Purpose: fetches unembedded segments from the server, computes embeddings locally with `all-mpnet-base-v2`, uploads to DB, then generates the similarity report.

Beats are embedded at the level of packed sentence-groups ("segments") rather than one vector per whole beat, so a reused punchline surrounded by a different setup still surfaces as a match. Segments are built once per beat and persisted to the `BeatSegment` table. `fluff` lines are excluded at segmentation time, so no segment text or embedding ever contains them; `setup`/`punchline`/`tag` labels are ignored.

The report compares every embedded segment against every other, skipping pairs from the same comedian, and keeps pairs at or above cosine 0.70. Joke type is not used to restrict comparisons — a beat labelled `misdirect` can match one labelled `reframe`. Segment pairs are collapsed to one row per beat pair, keeping the highest-scoring segment pair between those two beats.

**6. Optional maintenance/reset:**
```
python manage.py reset_db
```
Purpose: local dev only — wipes DB, clears caches and migration history, reimports everything from local archives (`bit_annotated_set_archive/`, `set_images_archive/`, `kt_ep_archive.jsonl`). Requires no server connection. Segment embeddings are not archived, so a reset DB has none until you re-run step 5.
