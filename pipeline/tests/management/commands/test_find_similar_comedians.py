import json
from pathlib import Path

import pytest
from django.core.management import call_command
from django.test import override_settings


pytestmark = pytest.mark.django_db


def test_command_writes_candidate_report(tmp_path):
    from pipeline.models import Comedian
    Comedian.objects.create(name="Dedric Flynn", slug="dedric-flynn")
    Comedian.objects.create(name="Dedrick Flynn", slug="dedrick-flynn")
    Comedian.objects.create(name="Jack Shaw", slug="jack-shaw")

    with override_settings(PIPELINE_DATA_DIR=tmp_path, PIPELINE_PRIVATE_DATA_DIR=tmp_path):
        call_command("find_similar_comedians")

    report = json.loads((tmp_path / "similar_comedian_candidates.json").read_text(encoding="utf-8"))
    slugs = {(c["first"]["slug"], c["second"]["slug"]) for c in report["candidates"]}
    assert ("dedric-flynn", "dedrick-flynn") in slugs
    assert not any("jack-shaw" in str(pair) for pair in slugs)


def test_command_prints_counts(tmp_path, capsys):
    from pipeline.models import Comedian
    Comedian.objects.create(name="Dedric Flynn", slug="dedric-flynn")
    Comedian.objects.create(name="Dedrick Flynn", slug="dedrick-flynn")

    with override_settings(PIPELINE_DATA_DIR=tmp_path, PIPELINE_PRIVATE_DATA_DIR=tmp_path):
        call_command("find_similar_comedians")

    out = capsys.readouterr().out
    assert "Comedians scanned:" in out
    assert "Candidate pairs:" in out
