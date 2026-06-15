from pipeline.utils.transcript_windows import build_transcript_windows


def _doc(n_lines, music_at=()):
    lines = [{"line_number": i, "text": f"line {i}", "start": i} for i in range(1, n_lines + 1)]
    for idx in music_at:
        lines[idx - 1]["text"] = "(upbeat music)"
    return {"video_id": "abc123", "lines": lines}


def test_windows_span_between_music_cues():
    doc = _doc(100, music_at=(40, 80))
    windows = build_transcript_windows(doc, overlap=25)

    assert len(windows) == 2
    assert windows[0]["window_start_line"] == 15
    assert windows[0]["music_cue_line"] == 40
    assert windows[0]["window_end_line"] == 80
    assert windows[0]["window_number"] == 1
    assert windows[1]["window_start_line"] == 55
    assert windows[1]["music_cue_line"] == 80
    assert windows[1]["window_end_line"] == 100
    assert windows[1]["window_number"] == 2


def test_skips_windows_shorter_than_minimum():
    doc = _doc(30, music_at=(1, 2, 11))
    windows = build_transcript_windows(doc, overlap=25, min_lines=20)

    assert len(windows) == 1
    assert windows[0]["window_number"] == 1
    assert windows[0]["window_start_line"] == 1
    assert windows[0]["window_end_line"] == 30


def test_returns_no_windows_without_music_cues():
    doc = _doc(10)
    assert build_transcript_windows(doc, overlap=25) == []
