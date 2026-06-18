from pipeline.utils.filenames import safe_filename_part


def test_safe_filename_part_replaces_invalid_chars():
    assert safe_filename_part('Title: "Test"') == "Title- -Test-"


def test_safe_filename_part_normalizes_empty_and_trailing_windows_chars():
    assert safe_filename_part("  ...  ") == "unknown"


def test_safe_filename_part_collapses_whitespace():
    assert safe_filename_part("Kill   Tony   Show") == "Kill Tony Show"
