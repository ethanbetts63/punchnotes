# Kill Tony Pipeline Spin-Up Prompt

You are coordinating the Kill Tony annotation pipeline. Work through the two phases below in order. Always finish one phase completely before moving to the next. Within each phase, spin up **one agent at a time** — wait for each agent to finish before starting the next.

---

## Phase 1 — Transcript Analysis

Check `C:\Users\ethan\coding\jokescore\data\1_transcript_inbox\`.

If there are any `.json` files there:

- Pick the first file.
- Spin up one agent and give it the prompt at `C:\Users\ethan\coding\jokescore\prompts\transcript_analysis_prompt.md`.
- Wait for it to finish, then repeat for the next file.
- Continue until `1_transcript_inbox` is empty.

If `1_transcript_inbox` is empty, proceed to Phase 2.

---

## Phase 2 — Set Annotation

Check `C:\Users\ethan\coding\jokescore\data\2_set_inbox\`.

If there are any `.json` files there:

- Pick the first 10 files (sorted by filename). If fewer than 10 remain, take all of them.
- Spin up one agent, tell it which files to process, and give it the prompt at `C:\Users\ethan\coding\jokescore\prompts\set_annotation_prompt.md`.
- Wait for it to finish, then repeat for the next batch of 10.
- Continue until `2_set_inbox` is empty.

---

## Phase 3 — Bit Annotation

Check `C:\Users\ethan\coding\jokescore\data\3_annotated_set_inbox\`.

If there are any `.json` files there:

- Pick the first 10 files (sorted by filename). If fewer than 10 remain, take all of them.
- Spin up one agent, tell it which files to process, and give it the prompt at `C:\Users\ethan\coding\jokescore\prompts\bit_annotation_prompt.md`.
- Wait for it to finish, then repeat for the next batch of 10.
- Continue until `3_annotated_set_inbox` is empty.

---

## Phase 4 — Database Import

Once `3_annotated_set_inbox` is empty and all Phase 3 agents are done, run:

```powershell
python manage.py import_lines
```

This will import everything from `4_bit_annotated_set_inbox` into the database and archive the files to `bit_annotated_set_archive`.

When Phase 4 is complete, report that the pipeline is done.
