# Remove beat premise and joke type fields

Planning document for refactoring beat annotations so new AI output no longer generates
`premise` or `joke_type`, old archived JSON can still be reingested without losing
archive data, and public/frontend displays stop depending on those fields.

## Current shape

Beat metadata is currently generated, validated, stored, searched, serialized, and
displayed in several layers:

- Prompt contract: `pipeline/prompts/annotation_prompt.md` requires every beat to
  include `premise` and `joke_type`, then spends most of the prompt defining joke
  types, premise formulas, examples, and premise-writing rules.
- JSON validation: `pipeline/json_validation/beats.py`,
  `pipeline/json_validation/constants.py`, and `pipeline/json_validation/premises.py`
  validate joke type membership, joke-type-specific fields, premise formulas,
  premise length, and single-line punchline premise fallbacks.
- Ingestion: `pipeline/utils/update/records.py` imports `premise`, `joke_type`, and
  derived `joke_fields` into `Beat`.
- Storage: `pipeline/models/beat.py` has `premise`, `joke_type`, `joke_fields`, and
  `JOKE_TYPE_CHOICES`.
- API/search: serializers and querysets expose or filter by these fields, especially
  `api/serializers/set.py`, `api/serializers/joke.py`, `api/serializers/bit.py`,
  `api/views/querysets.py`, `api/views/search.py`, and `api/views/plagiarism.py`.
- Frontend: beat cards, set transcript panels, joke search filters, joke-type FAQ,
  joke-type playlists, plagiarism results, metadata copy, and articles refer to
  premises or joke types.
- Utility command: `pipeline/management/commands/beats_by_joke_type.py` and
  `pipeline/utils/beats_by_joke_type.py` exist only because `joke_type` exists.

## Recommended target

For the full removal path:

- New annotation JSON should only need `bit_meta` keys and `beats` keys to establish
  bit/beat structure. Beat metadata objects may be empty objects.
- Validation should require structural correctness only: valid line labels,
  punchline anchors, bit/beat numbering, `bit_meta` object shape, matching beat keys,
  and at least one punchline per beat.
- Validation and import should tolerate legacy fields under `bit_meta.*.beats.*`,
  including `premise`, `joke_type`, and joke-specific fields, without persisting them.
- Existing archived JSON should remain unchanged on disk.
- Reingesting old archived JSON should recreate beats, lines, segments, ratios, and
  search text, but should leave removed fields unset/absent in the database.
- Public API and frontend should treat a beat as line structure plus metadata such as
  performer, episode, set, bit id, beat id, line range, setup/punchline/tag lines, and
  similarity/search data.

## Implementation sequence

1. Prompt reduction

   Replace `pipeline/prompts/annotation_prompt.md` with a shorter contract focused on:

   - input/output file handling;
   - line labels;
   - setup/punchline/tag ownership rules;
   - bit vs beat grouping;
   - `bit_meta` shape;
   - process checklist.

   Remove:

   - all premise-writing rules;
   - all joke-type taxonomy text;
   - all premise formulas and JSON examples containing `premise`/`joke_type`;
   - steps telling the annotator to identify joke type or write a premise.

   The prompt can likely shrink by more than half. Keep the useful structural rules:
   one punchline per beat, setup ownership by following payoff, tag ownership, shared
   subject matter not being enough for same bit, and bit/beat numbering.

2. Validation simplification

   Refactor `pipeline/json_validation/beats.py` so `BeatMetaValidation` only validates:

   - `bit_meta` keys are positive integer strings;
   - each bit metadata value is an object;
   - `beats` is an object keyed by positive integer strings;
   - each beat metadata value is an object if present;
   - every punchline anchor has a matching beat metadata entry;
   - every beat metadata entry maps to at least one punchline line.

   Remove or retire:

   - `pipeline/json_validation/premises.py`;
   - `PREMISE_STRUCTURE_RULES`, `PREMISE_MAX_WORDS`, `BASE_BEAT_FIELDS`,
     `JOKE_TYPE_FIELDS`, `OPTIONAL_JOKE_TYPE_FIELDS` if no longer used;
   - `_validate_no_bit_level_premise`;
   - `_validate_fields`;
   - `_validate_premise`;
   - `_validate_phonetic_reason`;
   - the mutation call to `populate_single_line_punchline_premises` in
     `pipeline/json_validation/validator.py`.

   Legacy beat fields should be ignored, not rejected. That means removing the current
   "unexpected field" checks or replacing them with a permissive shape check.

3. Ingestion changes

   Update `pipeline/utils/update/records.py`:

   - stop importing `JOKE_TYPE_FIELDS` and `OPTIONAL_JOKE_TYPE_FIELDS`;
   - delete `_extract_joke_fields`;
   - create `Beat` rows from bit/beat ownership, line ranges, and `search_text` only;
   - do not read `premise`, `joke_type`, or joke-specific fields from legacy JSON.

   This is the key point that preserves archive files while changing reingest behavior.
   Old JSON still contains the fields, validation accepts them, and import ignores them.

4. Model and database

   Remove from `pipeline/models/beat.py`:

   - `JOKE_TYPE_CHOICES`;
   - `premise`;
   - `joke_type`;
   - `joke_fields`.

   Then run `python manage.py makemigrations` rather than writing migration files by
   hand, per repo instruction.

   Admin cleanup:

   - update `pipeline/admin.py` list display, filters, and search fields.

5. API cleanup

   Remove fields from API payloads:

   - `api/serializers/set.py`: `BeatSerializer` should stop returning `premise` and
     `joke_type`.
   - `api/serializers/joke.py`: `BeatSearchSerializer` should stop returning them.
   - `api/serializers/bit.py`: remove `joke_types`; return beat identifiers/line
     summaries if still needed, but not premise/type payloads.
   - `api/views/plagiarism.py`: remove `premise` and `joke_type` from result objects.
   - `api/views/search.py`: remove joke type fallback titles and metadata.
   - `api/views/querysets.py`: remove `joke_type` filters and premise/joke-type search
     clauses. Keep search against `Beat.search_text`.

   Compatibility choice: either let obsolete `?joke_type=` query params be ignored, or
   return a 400. Ignoring is safer for old inbound links during rollout.

6. Frontend cleanup

   Remove direct display:

   - `frontend/components/AnnotatedBeatCard.tsx`: remove joke type badge.
   - `frontend/components/SetTranscript.tsx`: remove Beat Premise and Joke Type panels.
   - `frontend/app/joke-originality-checker/PlagiarismChecker.tsx`: remove fields and
     display blocks.
   - `frontend/lib/annotatedBeatCards.ts`: remove `jokeType`.
   - `frontend/lib/serverApi.ts`: update `Beat`, `BeatSearchItem`, `BitListItem`, and
     plagiarism result types.

   Remove joke-type discovery surfaces:

   - `frontend/lib/jokeTypes.ts`;
   - joke-type filter in `frontend/lib/searchConfigs.ts`;
   - joke-type FAQ and explanatory copy in `frontend/app/killtony/jokes/page.tsx`;
   - joke-type copy in `frontend/app/killtony/sets/[slug]/page.tsx`;
   - `frontend/app/killtony/jokes/JokePlaylists.tsx`, or rewrite it as a non-type-based
     curated examples component.

   Update content/SEO copy:

   - `frontend/public/llms.txt`;
   - `frontend/lib/seo.ts`;
   - `frontend/app/layout.tsx`;
   - `frontend/app/about/page.tsx`;
   - `frontend/app/killtony/page.tsx`;
   - `frontend/components/Footer.tsx`;
   - `frontend/components/BeatOfTheWeek.tsx`;
   - `frontend/components/PlagiarismHowItWorks.tsx`;
   - `frontend/app/joke-originality-checker/page.tsx`;
   - `frontend/articles/how-to-annotate-jokes.md`, if the public article should reflect
     the new annotation model.

7. Remove joke-type-only utilities

   Delete or deprecate:

   - `pipeline/management/commands/beats_by_joke_type.py`;
   - `pipeline/utils/beats_by_joke_type.py`;
   - `pipeline/tests/management/commands/test_beats_by_joke_type.py`.

   If there is still value in a "list beats" reporting command, rewrite it around
   search text, comedian, set, or joke-book filters instead.

8. Tests

   Update validation tests in `pipeline/tests/json_validation/test_validator.py` to
   assert:

   - empty beat metadata objects are valid;
   - legacy `premise`, `joke_type`, and joke-specific fields are accepted and ignored;
   - bit/beat shape and punchline link errors still fire;
   - single-line punchline no longer mutates input to add a premise.

   Update ingestion tests:

   - `pipeline/tests/utils/update/test_annotated.py` should prove legacy JSON can be
     reingested and resulting beats have no removed metadata.
   - Any fixtures in `api/tests/conftest.py` and API view tests should stop creating
     beats with removed fields.

   Update API/frontend expectations:

   - API tests should stop asserting `premise`, `joke_type`, or `joke_types`.
   - Search tests should assert beat search still works through `search_text`/lines.
   - Plagiarism tests should assert result shape without removed fields.

## Dead-code and simplification opportunities

Full removal creates meaningful simplification:

- Most of `pipeline/json_validation/constants.py` can disappear or shrink to line label
  and encoded-text constants only.
- `pipeline/json_validation/premises.py` becomes dead.
- Joke-type-specific validation methods in `BeatMetaValidation` become dead.
- `Beat.joke_fields` becomes dead because its only source is joke-type-specific JSON.
- The `beats_by_joke_type` command and utility become dead.
- Frontend `jokeTypes.ts`, joke-type FAQ generation, type filter options, and type
  playlist styling become dead.
- Bit list filtering by `joke_type` and bit search by `premise`/`joke_type` disappear.
- Admin filter and search can be simpler.
- Annotation prompt gets much shorter and less brittle, which should reduce model
  correction loops.

Potential follow-up simplification after the main refactor:

- Reconsider whether `bit_meta` needs beat metadata objects at all. If line anchors are
  the source of truth, `bit_meta` could eventually become a compact structural map or be
  inferred entirely from line labels. Do not bundle that into this refactor unless the
  current archive format is being deliberately changed.

## Alternative: remove premise, keep joke type

This is materially smaller than full removal but keeps much of the complexity.

Keep:

- `Beat.joke_type` and `JOKE_TYPE_CHOICES`;
- joke-type filters and public joke-type pages/playlists, if still desired;
- `pipeline/utils/beats_by_joke_type.py` and command, but remove `premise` from reports;
- `frontend/lib/jokeTypes.ts`;
- `JOKE_TYPE_FILTER_OPTIONS` and `?joke_type=` URLs;
- API fields for `joke_type` and `joke_types`.

Remove:

- `Beat.premise`;
- premise display from set transcript and plagiarism results;
- premise search clauses;
- premise formatter ordering;
- `pipeline/json_validation/premises.py`;
- premise formula/length validation.

Prompt impact:

- The prompt still needs the joke-type taxonomy and examples.
- It can remove premise formulas and premise-writing rules.
- The annotation step becomes "assign a `joke_type` to each beat" rather than "write a
  premise using the type formula."

Validation impact:

- Keep validation that `joke_type` is one of the accepted values.
- Decide whether to keep or remove joke-specific extra fields like `bait`,
  `implication`, `reveal`, `subject`, etc.
- If the goal is pipeline simplification, remove the extra fields too and validate only
  `joke_type`; otherwise most of the current joke-type-specific validation remains.

Scope comparison:

- Remove premise only, keep joke type and no extra fields: medium scope. It touches
  prompt, validation, model/migration, import, API, frontend display, and tests, but
  preserves public joke-type navigation.
- Remove premise only, keep joke type plus extra fields: medium-large scope with less
  value. The premise disappears, but the validator still carries most taxonomy-specific
  machinery.
- Remove both premise and joke type: largest scope, but it deletes the most code and
  gives the cleanest annotation pipeline.

My recommendation is full removal if the long-term product no longer needs joke-type
navigation. If joke-type browsing remains a public feature worth preserving, remove
premise first and keep only a flat `joke_type` field, not the joke-specific extra fields.

## Rollout notes

- Make backend validation/import permissive before reingesting archived JSON.
- Remove API fields before frontend assumes they are gone, or deploy backend and
  frontend together.
- Consider temporarily ignoring stale `joke_type` query params to avoid breaking old
  links immediately.
- After the model migration, run a representative archive reingest against local data to
  prove old JSON is accepted and ignored fields do not reappear.
- Follow repo instruction: generate migrations with `python manage.py makemigrations`;
  do not hand-write migration files.
