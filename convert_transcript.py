"""One-off script to convert CnjJPpr10vM.jsonl to the new JSON format."""
import json
from pathlib import Path


def dump_episode(doc):
    """Pretty-print top-level fields, one compact line per segment."""
    non_seg = [(k, v) for k, v in doc.items() if k != "segments"]
    has_segs = "segments" in doc
    parts = ["{"]
    for i, (k, v) in enumerate(non_seg):
        comma = "," if i < len(non_seg) - 1 or has_segs else ""
        parts.append(f"  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}{comma}")
    if has_segs:
        parts.append('  "segments": [')
        segs = doc["segments"]
        for i, s in enumerate(segs):
            comma = "," if i < len(segs) - 1 else ""
            parts.append(f"    {json.dumps(s, ensure_ascii=False)}{comma}")
        parts.append("  ]")
    parts.append("}")
    return "\n".join(parts)

src = Path(__file__).parent / "CnjJPpr10vM.jsonl"
archive_dir = Path(__file__).parent / "data" / "transcript_archive"
inbox_dir = Path(__file__).parent / "data" / "transcript_inbox"
archive_dir.mkdir(exist_ok=True)
inbox_dir.mkdir(exist_ok=True)

lines = [l for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
meta = json.loads(lines[0])
raw_segments = [json.loads(l) for l in lines[1:]]

base = {
    "type": meta["type"],
    "video_id": meta["video_id"],
    "episode_title": meta["episode_title"],
    "episode_url": meta["episode_url"],
}

# Archive: full precision, with duration
archive_doc = {
    **base,
    "segments": [
        {"text": s["text"], "start": s["start"], "duration": s["duration"]}
        for s in raw_segments
    ],
}
archive_path = archive_dir / f"{meta['video_id']}.json"
archive_path.write_text(dump_episode(archive_doc), encoding="utf-8")
print(f"Archive: {archive_path}")

# Inbox: floored start, no duration
inbox_doc = {
    **base,
    "segments": [
        {"text": s["text"], "start": int(s["start"])}
        for s in raw_segments
    ],
}
inbox_path = inbox_dir / f"{meta['video_id']}.json"
inbox_path.write_text(dump_episode(inbox_doc), encoding="utf-8")
print(f"Inbox:   {inbox_path}")
