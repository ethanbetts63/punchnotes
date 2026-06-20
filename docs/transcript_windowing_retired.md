# Transcript Windowing — Retired Code

## Original Code (verbatim)

From `pipeline/utils/transcript_windows.py`:

```python
MUSIC_RE = re.compile(
    r"^\s*-?\s*[\[(]?\s*"
    r"(upbeat\s+music|music|intro\s+music|outro\s+music|theme\s+music|"
    r"band\s+plays|song|guitar|drumroll)"
    r"\s*[\])]?\s*$",
    re.IGNORECASE,
)


def build_transcript_windows(
    doc: dict,
    overlap: int = 25,
    min_lines: int = 20,
) -> list[dict]:
    lines = doc["lines"]
    cue_indexes = [
        i for i, line in enumerate(lines)
        if MUSIC_RE.match(str(line.get("text", "")))
    ]
    if not cue_indexes:
        return []

    windows = []
    overlap = max(overlap, 0)
    for cue_pos, cue_index in enumerate(cue_indexes):
        start_index = max(cue_index - overlap, 0)
        if cue_pos < len(cue_indexes) - 1:
            next_cue_index = cue_indexes[cue_pos + 1]
            end_index = next_cue_index + 1
        else:
            end_index = len(lines)

        window_lines = lines[start_index:end_index]
        if len(window_lines) < min_lines:
            continue  # silently drops content

        windows.append(
            {
                **{k: v for k, v in doc.items() if k != "lines"},
                "window_number": len(windows) + 1,
                "window_start_line": window_lines[0].get("line_number", start_index + 1),
                "window_end_line": window_lines[-1].get("line_number", end_index),
                "music_cue_line": lines[cue_index].get("line_number", cue_index + 1),
                "lines": window_lines,
            }
        )

    return windows


def write_inbox_transcript_windows(
    doc: dict,
    inbox_dir: Path,
    *,
    overlap: int = 25,
    min_lines: int = 20,
    overwrite: bool = True,
) -> list[Path]:
    video_id = doc.get("video_id") or "unknown"
    inbox_dir.mkdir(parents=True, exist_ok=True)

    if overwrite:
        title = safe_transcript_title(doc)
        for path in [*inbox_dir.glob(f"{video_id}*.json"), *inbox_dir.glob(f"{title} - window*.json")]:
            path.unlink()

    windows = build_transcript_windows(doc, overlap=overlap, min_lines=min_lines)
    if not windows:
        out_path = inbox_dir / transcript_archive_filename(doc)
        out_path.write_text(dump_transcript(doc), encoding="utf-8")
        return [out_path]

    written = []
    for window in windows:
        window_num = int(window["window_number"])
        out_path = inbox_dir / transcript_window_filename(window, window_num)
        out_path.write_text(dump_transcript(window), encoding="utf-8")
        written.append(out_path)

    return written
```

---

## How It Worked

Every time a transcript was archived, the system detected music cue lines using `MUSIC_RE` — lines that matched phrases like `[music]`, `[upbeat music]`, `[band plays]`, etc. It then split the transcript at each cue, starting each window 25 lines before the cue to provide overlap context. Each window ran from that overlap point through to the next music cue line.

If no music cues were found at all, the full transcript was written as a single file. Otherwise the transcript was split into multiple numbered window files, each covering one segment between cues.

---

## What Changed

Windowing was replaced with a stripped full-transcript approach. Instead of splitting, the entire transcript is written to the inbox as a single file with all timing data (`start`, `duration`) and episode metadata (`episode_title`, `episode_url`, `publish_date`, `type`, `video_id`) removed. Each line is reduced to just its line number and text. The agent reads the full episode in one pass and runs `extract_set` against the original archive file, which retains all data.

---

## Data Loss Warning

The `min_lines=20` guard on line 70 silently dropped any window shorter than 20 lines. This means any comedian set that fell in a short gap between two music cues — fewer than 20 lines including the 25-line overlap — was permanently discarded and never written to the inbox. The agent never saw it and no error was raised.

Additionally, the 25-line overlap was an approximation. If a music cue landed in the middle of a set rather than immediately before it, the set would be split across two windows. The agent prompt instructed agents to ignore cut-off sets and rely on them appearing in full in the next window, but this depended on the overlap being sufficient. If the set was short and the cue fell unluckily, the set could be truncated in both windows.

A future cleanup pass reviewing processed episodes should be aware that sets may be missing or incomplete in the database for episodes processed under this windowing scheme.
