from pipeline.utils.segmenting import Segment, segment_beat_lines


def test_empty_lines_returns_no_segments():
    assert segment_beat_lines([], min_words=10) == []


def test_single_short_beat_returns_one_undersized_segment():
    lines = [(1, "Hi there everyone.")]
    result = segment_beat_lines(lines, min_words=10)
    assert result == [Segment(text="Hi there everyone.", line_start=1, line_end=1)]


def test_sentence_at_or_above_min_closes_immediately():
    lines = [(1, "This sentence right here has plenty of words in it.")]
    result = segment_beat_lines(lines, min_words=5)
    assert result == [
        Segment(text="This sentence right here has plenty of words in it.", line_start=1, line_end=1)
    ]


def test_two_short_sentences_after_a_closed_one_combine_together():
    lines = [
        (1, "First sentence closes here on its own already."),
        (2, "Short one."),
        (3, "Another short bit."),
    ]
    result = segment_beat_lines(lines, min_words=4)
    assert result == [
        Segment(text="First sentence closes here on its own already.", line_start=1, line_end=1),
        Segment(text="Short one. Another short bit.", line_start=2, line_end=3),
    ]


def test_trailing_short_leftover_merges_into_previous_segment():
    lines = [
        (1, "First sentence closes here on its own already."),
        (2, "Tiny."),
    ]
    result = segment_beat_lines(lines, min_words=4)
    assert result == [
        Segment(text="First sentence closes here on its own already. Tiny.", line_start=1, line_end=2)
    ]


def test_sentence_split_across_two_transcript_lines_stays_one_segment():
    lines = [
        (10, "And now we are proud to announce we are going back to Madison Square Garden for the third"),
        (11, "year in a row completely unprecedented, the world's greatest arena."),
    ]
    result = segment_beat_lines(lines, min_words=5)
    assert len(result) == 1
    assert result[0].line_start == 10
    assert result[0].line_end == 11
    assert "Madison Square Garden" in result[0].text
    assert "greatest arena" in result[0].text


def test_abbreviation_with_no_following_capital_does_not_force_a_split():
    lines = [(1, "The show starts at 10 a.m. sharp and ends at 10 p.m. tonight.")]
    result = segment_beat_lines(lines, min_words=3)
    assert len(result) == 1
    assert result[0].text == "The show starts at 10 a.m. sharp and ends at 10 p.m. tonight."


def test_known_title_abbreviation_does_not_split_before_proper_noun():
    lines = [(1, "Mr. Smith walked in. He said hello.")]
    result = segment_beat_lines(lines, min_words=1)
    assert len(result) == 2
    assert result[0].text == "Mr. Smith walked in."
    assert result[1].text == "He said hello."


def test_no_terminal_punctuation_is_treated_as_one_sentence():
    lines = [(1, "we ran a long line here with no punctuation at all whatsoever")]
    result = segment_beat_lines(lines, min_words=3)
    assert len(result) == 1
    assert result[0].text == "we ran a long line here with no punctuation at all whatsoever"


def test_blank_lines_are_skipped():
    lines = [(1, ""), (2, "  "), (3, "Real content finally shows up here.")]
    result = segment_beat_lines(lines, min_words=3)
    assert len(result) == 1
    assert result[0].line_start == 3
    assert result[0].line_end == 3
