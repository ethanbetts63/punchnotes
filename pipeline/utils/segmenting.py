import re
from dataclasses import dataclass


DEFAULT_MIN_SEGMENT_WORDS = 12

_ABBREVIATIONS = {"mr", "mrs", "ms", "dr", "st", "vs", "etc", "jr", "sr", "prof", "rev"}
_SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"\'\[(])')


@dataclass(frozen=True)
class Segment:
    text: str
    line_start: int
    line_end: int


@dataclass(frozen=True)
class _Sentence:
    text: str
    line_start: int
    line_end: int
    word_count: int


def _join_lines(lines: list[tuple[int, str]]) -> tuple[str, list[tuple[int, int, int]]]:
    parts = []
    offsets = []
    cursor = 0
    for line_number, text in lines:
        text = text.strip()
        if not text:
            continue
        start = cursor
        parts.append(text)
        cursor += len(text)
        offsets.append((start, cursor, line_number))
        cursor += 1
    return " ".join(parts), offsets


def _line_range_for_span(offsets: list[tuple[int, int, int]], span_start: int, span_end: int) -> tuple[int, int]:
    matching = [line_number for start, end, line_number in offsets if end > span_start and start < span_end]
    return min(matching), max(matching)


def _sentence_spans(text: str) -> list[tuple[int, int]]:
    boundaries = []
    for match in _SENTENCE_SPLIT_RE.finditer(text):
        preceding_words = re.findall(r"[A-Za-z]+", text[:match.start()])
        if preceding_words and preceding_words[-1].lower() in _ABBREVIATIONS:
            continue
        boundaries.append((match.start(), match.end()))

    spans = []
    start = 0
    for split_start, split_end in boundaries:
        spans.append((start, split_start))
        start = split_end
    spans.append((start, len(text)))
    return [(s, e) for s, e in spans if text[s:e].strip()]


def segment_beat_lines(lines: list[tuple[int, str]], min_words: int = DEFAULT_MIN_SEGMENT_WORDS) -> list[Segment]:
    full_text, offsets = _join_lines(lines)
    if not full_text:
        return []

    sentences = []
    for span_start, span_end in _sentence_spans(full_text):
        sentence_text = full_text[span_start:span_end].strip()
        line_start, line_end = _line_range_for_span(offsets, span_start, span_end)
        sentences.append(_Sentence(
            text=sentence_text,
            line_start=line_start,
            line_end=line_end,
            word_count=len(sentence_text.split()),
        ))

    segments: list[Segment] = []
    buffer_parts: list[str] = []
    buffer_line_start = None
    buffer_line_end = None
    buffer_words = 0

    for sentence in sentences:
        if not buffer_parts:
            buffer_line_start = sentence.line_start
        buffer_parts.append(sentence.text)
        buffer_line_end = sentence.line_end
        buffer_words += sentence.word_count

        if buffer_words >= min_words:
            segments.append(Segment(text=" ".join(buffer_parts), line_start=buffer_line_start, line_end=buffer_line_end))
            buffer_parts = []
            buffer_words = 0

    if buffer_parts:
        leftover_text = " ".join(buffer_parts)
        if segments:
            previous = segments[-1]
            segments[-1] = Segment(
                text=f"{previous.text} {leftover_text}",
                line_start=previous.line_start,
                line_end=buffer_line_end,
            )
        else:
            segments.append(Segment(text=leftover_text, line_start=buffer_line_start, line_end=buffer_line_end))

    return segments
