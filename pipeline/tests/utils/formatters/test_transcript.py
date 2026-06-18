import json

from pipeline.utils.formatters import serialize_transcript


def test_serialize_transcript_compacts_lines_with_transcript_field_order():
    data = {
        "video_id": "abc123",
        "episode_title": "Title",
        "lines": [{"duration": 2, "start": 1, "text": "hello", "line_number": 3}],
    }

    formatted = serialize_transcript(data)

    assert '    {"line_number": 3, "text": "hello", "start": 1, "duration": 2}' in formatted
    assert json.loads(formatted) == data
