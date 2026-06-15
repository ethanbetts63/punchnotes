import pytest
from django.core.management.base import CommandError

from pipeline.management.commands.extract_set import (
    WHISPER_ANNOTATION_RE,
    normalize_attributes,
    set_filename,
)


def test_attributes_are_deduplicated():
    assert normalize_attributes("gay, gay, GAY") == ["gay"]


def test_attributes_normalizes_spaces_and_case():
    assert normalize_attributes("Gay, Black") == ["gay", "black"]


def test_attributes_empty_returns_empty():
    assert normalize_attributes("") == []


def test_attributes_rejects_unknown():
    with pytest.raises(CommandError):
        normalize_attributes("funny")


def test_set_filename_basic():
    assert set_filename("KILL TONY #529 - WILLIAM MONTGOMERY", "Hans Kim") == \
        "KILL TONY #529 - WILLIAM MONTGOMERY - Hans Kim.json"


def test_set_filename_with_start_seconds():
    assert set_filename("KILL TONY #529 - WILLIAM MONTGOMERY", "Hans Kim", 424) == \
        "KILL TONY #529 - WILLIAM MONTGOMERY - Hans Kim (424s).json"


def test_set_filename_sanitizes_invalid_chars():
    assert set_filename('Title: "Test"', "Comic/Name") == "Title- -Test- - Comic-Name.json"


def test_whisper_annotation_re_matches_brackets():
    assert WHISPER_ANNOTATION_RE.match("[laughter]")
    assert WHISPER_ANNOTATION_RE.match("[upbeat music]")
    assert WHISPER_ANNOTATION_RE.match("(inaudible)")
    assert WHISPER_ANNOTATION_RE.match("  [music]  ")
    assert WHISPER_ANNOTATION_RE.match("[music] [laughter]")


def test_whisper_annotation_re_no_match_on_speech():
    assert not WHISPER_ANNOTATION_RE.match("Hello there")
    assert not WHISPER_ANNOTATION_RE.match("Hello [laughter]")
    assert not WHISPER_ANNOTATION_RE.match("[laughter] and more words")
