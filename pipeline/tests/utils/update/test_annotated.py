import pytest

from pipeline.utils.update.annotated import ingest_annotated_set


pytestmark = pytest.mark.django_db


def test_ingest_annotated_set_requires_existing_video():
    data = {
        "video_id": "missing123",
        "comedian_name": "Test Comic",
        "start_seconds": 10,
        "lines": [
            {"line_number": 1, "text": "Setup.", "label": "setup", "bit": None, "beat": None},
            {"line_number": 2, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
        ],
        "bit_meta": {
            "1": {
                "beats": {
                    "1": {
                        "premise": "A setup could be a payoff.",
                        "joke_type": "reframe",
                        "subject": "a setup",
                        "reframe": "a payoff",
                    }
                }
            }
        },
    }

    with pytest.raises(ValueError, match="Run update --ep_meta"):
        ingest_annotated_set(data)
