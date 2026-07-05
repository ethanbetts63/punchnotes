# Kill Tony Pipeline Spin-Up Prompt

You are coordinating the Kill Tony annotation pipeline. Work through the phases below in strict order, one phase at a time — never start a phase until the previous phase has fully completed. Within a phase, spin up only the number of concurrent agents specified for that phase — wait for that batch to finish before starting the next. Tell the agents to summarise only any issues they have with their task. No issues no summaries. After launching agents, wait silently until completion.

---

## Local Mode

If the user said to use `--local`, you are in local mode. Local mode affects:

- **Phase 2** — tell annotation agents to append `--local` to their upload command
- **Phase 3** — append `--local` to the `generate --comedian_aliases` command, and tell the alias review agent it is running in local mode

If the user said nothing about `--local`, do not mention it to any sub-agents.  

---

## Phase 1 — Transcript Analysis

Check `C:\Users\ethan\coding\punchnotes\pipeline\data\transcript_inbox\`.

If there are any `.txt` files there:

- Select the first 5 files.
- Spin up one medium sized agent. Tell it: the file list you are giving it is authoritative — do not list the inbox directory. Then give it the prompt at `C:\Users\ethan\coding\punchnotes\pipeline\prompts\transcript_analysis_prompt.md`. **YOU SHOULD NOT READ THIS PROMPT JUST PASS IT ON**
- Wait for it to finish all 5 files, then repeat for the next files.
- Continue until `transcript_inbox` is empty.

If `transcript_inbox` is empty, proceed to Phase 2.

---

## Phase 2 — Annotation

Check `C:\Users\ethan\coding\punchnotes\pipeline\data\set_inbox\`.

If there are any `.json` files there:

- Pick the first 10 files (sorted by filename). If fewer than 10 remain, take all of them.
- Spin up 2 medium level agents, tell them which files to process, and give them the prompt at `C:\Users\ethan\coding\punchnotes\pipeline\prompts\annotation_prompt.md`. If in local mode, tell the agent to use `--local` on the upload command. Otherwise, tell them that `--local` is available as a fallback — use it only if the upload command fails with a server connection error. **YOU SHOULD NOT READ THIS PROMPT JUST PASS IT ON**
- Wait for them to finish, then repeat for the next batch of 10.
- Continue until `set_inbox` is empty.

## Phase 3 — Comedian Alias Review

Once Phase 3 is complete, run:

```powershell
python manage.py generate --comedian_aliases
```

(Append `--local` if in local mode.)

Then spin up one medium sized agent and give it the prompt at `C:\Users\ethan\coding\punchnotes\pipeline\prompts\comedian_alias_review_prompt.md`. If in local mode, tell the agent it is running in local mode. Otherwise, tell it that `--local` is available as a fallback — use it only if a command fails with a server connection error.

## Phase 4 — Set Images

Once Phase 3 is complete, run the following commands in order:

```powershell
python manage.py generate --set_images
python manage.py upload --set_images
python manage.py update --set_images
```

This checks the server for missing comedian images, scrapes them locally, uploads them, and imports them to the DB.

## Phase 5 — Joke Similarity Scoring

Once Phase 4 is complete, run the following commands in order:

```powershell
python manage.py generate --embeddings
python manage.py upload --embeddings
python manage.py update --embeddings
python manage.py generate --embeddings_report
```

## Phase 6 — Clean and Push

Once Phase 5 is complete, run:

```powershell
python manage.py normalize_archives
```
and
```powershell
python manage.py archive --push
```

