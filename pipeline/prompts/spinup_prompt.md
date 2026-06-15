# Kill Tony Pipeline Spin-Up Prompt

You are coordinating the Kill Tony annotation pipeline. Work through the phases below in order. Always finish one phase completely before moving to the next. Within each phase, spin up **1 agents at a time** — wait for each agent to finish before starting the next.

---

## Local Mode

If the user said to use `--local`, you are in local mode. Local mode affects:

- **Phase 2** — tell annotation agents to append `--local` to their upload command
- **Phase 4** — append `--local` to the `generate --comedian_aliases` command, and tell the alias review agent it is running in local mode

If the user said nothing about `--local`, do not mention it to any sub-agents.

---

## Phase 1 — Transcript Analysis

Check `C:\Users\ethan\coding\punchnotes\pipeline\data\1_transcript_inbox\`.

If there are any `.json` files there:

- Select the first 20 files.
- Spin up one small sized agent. Tell it: the file list you are giving it is authoritative — do not list the inbox directory. Then give it the prompt at `C:\Users\ethan\coding\punchnotes\pipeline\prompts\transcript_analysis_prompt.md`. **YOU SHOULD NOT READ THIS PROMPT JUST PASS IT ON**
- Wait for it to finish all 20 files, then repeat for the next files.
- Continue until `1_transcript_inbox` is empty.

If `1_transcript_inbox` is empty, proceed to Phase 2.

---

## Phase 2 — Annotation

Check `C:\Users\ethan\coding\punchnotes\pipeline\data\2_set_inbox\`.

If there are any `.json` files there:

- Pick the first 20 files (sorted by filename). If fewer than 20 remain, take all of them.
- Spin up one medium level agent, tell it which files to process, and give it the prompt at `C:\Users\ethan\coding\punchnotes\pipeline\prompts\annotation_prompt.md`. If in local mode, tell the agent to use `--local` on the upload command. Otherwise, tell it that `--local` is available as a fallback — use it only if the upload command fails with a server connection error. **YOU SHOULD NOT READ THIS PROMPT JUST PASS IT ON**
- Wait for it to finish, then repeat for the next batch of 20.
- Continue until `2_set_inbox` is empty.
- You can run phase 2 in parallel with phase 1 as soon as phase 2 has files to process.

---

## Phase 3 — Normalize Archive

Once Phase 2 is complete, run:

```powershell
python manage.py normalize_archive
```

This normalizes the JSON formatting of all files in `bit_annotated_set_archive` to the canonical format.

---

## Phase 4 — Comedian Alias Review

Once Phase 3 is complete, run:

```powershell
python manage.py generate --comedian_aliases
```

(Append `--local` if in local mode.)

Then spin up one medium sized agent and give it the prompt at `C:\Users\ethan\coding\punchnotes\pipeline\prompts\comedian_alias_review_prompt.md`. If in local mode, tell the agent it is running in local mode. Otherwise, tell it that `--local` is available as a fallback — use it only if a command fails with a server connection error.

When Phase 4 is complete, report that the pipeline is done.
