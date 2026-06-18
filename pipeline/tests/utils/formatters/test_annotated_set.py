import json

from pipeline.utils.formatters import serialize_annotated_set


def test_serialize_annotated_set_orders_core_fields_and_compacts_lines():
    data = {
        "lines": [{"start": 1, "line_number": 3, "label": "setup", "text": "hello"}],
        "comedian_name": "Comic",
        "video_id": "abc123",
        "type": "set_meta",
        "start_seconds": 1,
    }

    formatted = serialize_annotated_set(data)

    assert formatted.startswith('{\n  "type": "set_meta",\n  "video_id": "abc123",')
    assert '  "set_attributes": [],\n' in formatted
    assert '    {"text": "hello", "label": "setup", "line_number": 3, "start": 1}' in formatted
    assert json.loads(formatted) == {
        "type": "set_meta",
        "video_id": "abc123",
        "comedian_name": "Comic",
        "start_seconds": 1,
        "interview_end_line": None,
        "interview_end_seconds": None,
        "set_attributes": [],
        "comedian_attributes": [],
        "lines": [{"text": "hello", "label": "setup", "line_number": 3, "start": 1}],
    }
