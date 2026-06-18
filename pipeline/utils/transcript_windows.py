import json
import re
from pathlib import Path


FILENAME_INVALID_CHARS = str.maketrans({c: "-" for c in r'\/:*?"<>|'})

MUSIC_RE = re.compile(
    r"^\s*-?\s*[\[(]?\s*"
    r"(upbeat\s+music|music|intro\s+music|outro\s+music|theme\s+music|"
    r"band\s+plays|song|guitar|drumroll)"
    r"\s*[\])]?\s*$",
    re.IGNORECASE,
)


def safe_transcript_title(doc: dict) -> str:
    title = str(doc.get("episode_title") or doc.get("video_id") or "unknown").strip()
    return title.translate(FILENAME_INVALID_CHARS).strip().rstrip(".") or "unknown"


def transcript_archive_filename(doc: dict) -> str:
    return f"{safe_transcript_title(doc)}.json"


def transcript_window_filename(doc: dict, window_number: int) -> str:
    return f"{safe_transcript_title(doc)} - window{window_number:03d}.json"


def dump_transcript(doc: dict) -> str:
    non_lines = [(k, v) for k, v in doc.items() if k != "lines"]
    has_lines = "lines" in doc
    parts = ["{"]
    for i, (key, value) in enumerate(non_lines):
        comma = "," if i < len(non_lines) - 1 or has_lines else ""
        parts.append(f"  {json.dumps(key)}: {json.dumps(value, ensure_ascii=False)}{comma}")
    if has_lines:
        parts.append('  "lines": [')
        lines = doc["lines"]
        for i, line in enumerate(lines):
            comma = "," if i < len(lines) - 1 else ""
            parts.append(f"    {json.dumps(line, ensure_ascii=False)}{comma}")
        parts.append("  ]")
    parts.append("}")
    return "\n".join(parts)


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
            continue

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
