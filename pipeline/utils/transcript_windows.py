import json
import re
from pathlib import Path

from pipeline.utils.filenames import safe_filename_part


ANNOTATION_RE = re.compile(
    r"^\s*(\[[\s\S]*?\]|\([\s\S]*?\))(\s*(\[[\s\S]*?\]|\([\s\S]*?\)))*\s*$"
)


def is_annotation_line(text: str) -> bool:
    return bool(ANNOTATION_RE.match(text))


def safe_transcript_title(doc: dict) -> str:
    return safe_filename_part(doc.get("episode_title") or doc.get("video_id") or "unknown")


def transcript_archive_filename(doc: dict) -> str:
    return f"{safe_transcript_title(doc)}.json"



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


def write_inbox_transcript(
    doc: dict,
    inbox_dir: Path,
    *,
    overwrite: bool = True,
) -> Path:
    inbox_dir.mkdir(parents=True, exist_ok=True)
    title = safe_transcript_title(doc)
    out_path = inbox_dir / f"{title}.txt"

    if overwrite and out_path.exists():
        out_path.unlink()

    lines = doc.get("lines", [])
    text = "\n".join(
        f"{line.get('line_number', i + 1)}: {line.get('text', '')}"
        for i, line in enumerate(lines)
        if not is_annotation_line(line.get("text", ""))
    )
    out_path.write_text(text, encoding="utf-8")
    return out_path
