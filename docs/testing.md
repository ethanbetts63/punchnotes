# Testing

## Stack

pytest + pytest-django. Install dev dependencies with:
```
pip install -r requirements-dev.txt
```

Run all tests:
```
pytest
```

## Structure

Tests live inside each app, mirroring the app's directory structure:

```
pipeline/tests/
  conftest.py                          # shared fixtures (comedian, video, standup_set)
  management/commands/
    test_extract_set.py
    test_find_similar_comedians.py
    test_generate_embedding_report.py
  utils/
    test_comedian_aliases.py
    test_similar_comedians.py
    test_transcript_windows.py
    test_ownership.py
    generate/
      test_embeddings.py
    update/
      test_records.py
  json_validation/
    test_validator.py

api/tests/
  conftest.py                          # api_client fixture (pre-authed pipeline client)
  views/
    test_search.py
    test_pipeline.py
```

## Conventions

- DB tests use `pytestmark = pytest.mark.django_db` at module level
- Tests that need a temp filesystem use pytest's built-in `tmp_path` fixture with `override_settings(PIPELINE_DATA_DIR=tmp_path)`
- No classes — flat functions unless grouping genuinely aids readability
- Shared model setup goes in `conftest.py` fixtures; one-off setup stays inline
- `django_assert_num_queries` for query count assertions (not `assertNumQueries`)
