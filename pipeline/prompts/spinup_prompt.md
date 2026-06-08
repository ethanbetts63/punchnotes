# Kill Tony Pipeline Spin-Up Prompt

You are coordinating the Kill Tony annotation pipeline. Work through the phases below in order. Always finish one phase completely before moving to the next. Within each phase, spin up **2 agents at a time** — wait for each agent to finish before starting the next.

---

## Phase 1 — Transcript Analysis

Check `C:\Users\ethan\coding\punchnotes\pipeline\data\1_transcript_inbox\`.

If there are any `.json` files there:

- Select the first 20 files.
- Spin up one small sized agent and give it the prompt at `C:\Users\ethan\coding\punchnotes\pipeline\prompts\transcript_analysis_prompt.md`.
- Wait for it to finish all 20 files, then repeat for the next files.
- Continue until `1_transcript_inbox` is empty.

If `1_transcript_inbox` is empty, proceed to Phase 2.

---

## Phase 2 — Annotation

Check `C:\Users\ethan\coding\punchnotes\pipeline\data\2_set_inbox\`.

If there are any `.json` files there:

- Pick the first 20 files (sorted by filename). If fewer than 20 remain, take all of them.
- Spin up one medium level agent, tell it which files to process, and give it the prompt at `C:\Users\ethan\coding\punchnotes\pipeline\prompts\simple_annotation_prompt.md`.
- Wait for it to finish, then repeat for the next batch of 20.
- Continue until `2_set_inbox` is empty.

---

## Phase 3 — Normalize Archive

Once Phase 3 is complete, run:

```powershell
python manage.py normalize_archive
```

This normalizes the JSON formatting of all files in `bit_annotated_set_archive` to the canonical format.

When Phase 4 is complete, report that the pipeline is done.
