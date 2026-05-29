"""
Rename bit-level 'premise' keys to 'summary' in all annotated set files.
"""
import json
import sys
from pathlib import Path

INBOX = Path(__file__).parent.parent / "data" / "3_bit_annotated_set_inbox"
ARCHIVE = Path(__file__).parent.parent / "data" / "bit_annotated_set_archive"


def fix_file(path: Path) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    bit_meta = data.get("bit_meta")
    if not isinstance(bit_meta, dict):
        return False

    changed = False
    for bit_val in bit_meta.values():
        if not isinstance(bit_val, dict):
            continue
        if "premise" in bit_val and "beats" in bit_val:
            bit_val["summary"] = bit_val.pop("premise")
            changed = True

    if changed:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return changed


def main():
    dirs = [INBOX, ARCHIVE]
    total = 0
    for d in dirs:
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            if fix_file(f):
                print(f"Fixed: {f.name}")
                total += 1
    print(f"\nDone — {total} file(s) updated.")


if __name__ == "__main__":
    main()
