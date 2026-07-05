from pipeline.utils.report_format import format_report_json


def test_small_label_text_dict_stays_on_one_line():
    result = format_report_json({"label": "setup", "text": "hi"})
    assert result == '{"label": "setup", "text": "hi"}'


def test_list_of_strings_stays_on_one_line():
    result = format_report_json(["a", "b"])
    assert result == '["a", "b"]'


def test_nested_dict_is_multiline_and_indented():
    result = format_report_json({"pairs": [{"similarity": 1.0, "beat_a": {"id": 1}}]})
    assert result == (
        "{\n"
        '  "pairs": [\n'
        "    {\n"
        '      "similarity": 1.0,\n'
        '      "beat_a": {\n'
        '        "id": 1\n'
        "      }\n"
        "    }\n"
        "  ]\n"
        "}"
    )
