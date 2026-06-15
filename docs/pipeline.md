# Pipeline

Ingests and annotates Kill Tony stand-up sets into the DB.

---

## Directory structure

```
pipeline/
  management/commands/   # Three entry-point commands: generate, upload, update
                         # Plus standalone commands (fetch_audio, import_set_images, etc.)
  utils/
    generate/            # Local-machine logic: scraping, downloading, embedding, etc.
    upload/              # Local-machine logic: POSTing outbox files to the server
    update/              # Server-side logic: reading inbox files into the DB
    (shared files)       # HTTP session, inbox runner, alias resolution, beats, etc.
  json_validation/       # JSON schema validation for annotated set files
  prompts/               # AI agent prompt files
  models/                # Django models (Video, Set, Comedian, Bit, Beat, Line)
  data/                  # Local data directories (not committed)
  scripts/               # One-off helper scripts (e.g. grab_set_image.py)
```

## Data directories (`pipeline/data/`)

| Directory | Purpose |
|---|---|
| `0_audio_inbox/` | Downloaded episode audio |
| `audio_archive/` | Audio that has been transcribed |
| `1_transcript_inbox/` | Raw transcripts awaiting set extraction |
| `2_set_inbox/` | Extracted sets awaiting annotation |
| `bit_annotated_set_archive/` | Annotated sets (source of truth, never rewritten) |
| `ep_meta_outbox/` | Episode metadata JSONL awaiting upload |
| `ep_meta_inbox/` | (server) Received JSONL awaiting `update --ep_meta` |
| `ep_meta_archive/` | Processed JSONL |
| `set_images_outbox/` | Scraped images awaiting upload |
| `set_images_inbox/` | (server) Received images awaiting `update --set_images` |
| `embeddings_outbox/` | Computed embeddings JSONL awaiting upload |
| `embeddings_inbox/` | (server) Received JSONL awaiting `update --embeddings` |
| `comedian_aliases_inbox/` | (server) Received relationships file awaiting `update --comedian_aliases` |
| `videos_to_scrape.jsonl` | (server) Queue of video IDs to fetch metadata for |
| `video_scrape_history.jsonl` | (server) Record of scrape attempts (success/failed) |
| `similar_comedian_candidates.json` | Fuzzy-matched comedian name pairs for review |
| `comedian_name_relationships.json` | Reviewed alias/not-alias decisions |

## Conventions

**generate / upload / update split** — `generate` and `upload` run on the local machine; `update` runs on the server. Each command takes a mutually exclusive flag (`--ep_meta`, `--audio`, etc.) selecting the task.

**Outbox / inbox / archive pattern** — `generate` writes files to an `*_outbox/` dir. `upload` POSTs them to the server API, which writes them to an `*_inbox/` dir. `update` reads the inbox, ingests to DB, and archives.

**Annotated sets are the exception** — `upload --annotated` ingests immediately (no separate update step) so the AI agent can receive structured errors inline.

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
python manage.py upload --ep_meta
python manage.py update --ep_meta
```
Purpose: pull the scrape queue from the server (`videos_to_scrape.jsonl`), fetch full metadata per video from YouTube, write timestamped JSONL to `ep_meta_outbox/`, upload to server, import to DB. Each result (success or failure) is reported back to the server and recorded in `video_scrape_history.jsonl` so the queue stays clean.

To scrape a single video without touching the queue:
```
python manage.py generate --ep_meta --video <video_id>
```

To seed the queue, add `{"video_id": "..."}` lines to `pipeline/data/videos_to_scrape.jsonl` on the server. The queue endpoint removes entries that are already in the DB or history before returning.

**2. Get transcripts:**
```
python manage.py generate --audio --limit 20
python manage.py generate --transcripts
pipeline/data/1_transcript_inbox/
```
Age restricted videos:

A. log in youtube, go to https://www.youtube.com/robots.txt, use "get cookies.txt LOCALLY" chrome extension and drop in `pipeline/data/`

B. Run `python manage.py generate --restricted_audio`

**3. AI Flow:**

A. AI coordinator receives: `prompts/spinup_prompt.md` (tell the coordinator to use `--local` if required)

B. If files in `1_transcript_inbox`, spins up agent with `prompts/transcript_analysis_prompt.md`

C. If file in `2_set_inbox`, spins up agent with `prompts/annotation_prompt`

D. Runs `python manage.py normalize_archive` to make json more human readable

E. After `upload --annotated`, review `pipeline/data/similar_comedian_candidates.json` with `prompts/comedian_alias_review_prompt.md`, save decisions in `pipeline/data/comedian_name_relationships.json` then run:
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
python manage.py generate --embeddings
python manage.py upload --embeddings
python manage.py update --embeddings
```
Purpose: fetches unembedded beats from server, computes embeddings locally, uploads to DB

**6. Optional maintenance/reset:**
```
python manage.py reset_db
```
Purpose: local dev only — wipes DB, clears caches and migration history, reimports from archive
