import re


INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def safe_filename_part(value: object) -> str:
    text = INVALID_FILENAME_CHARS.sub("-", str(value))
    text = re.sub(r"\s+", " ", text).strip()
    return text.rstrip(". ") or "unknown"
