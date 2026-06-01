# Kill Tony Comedian Alias Review Prompt

You are reviewing likely duplicate comedian names from punchnotes's Kill Tony database.

Read:

```text
C:\Users\ethan\coding\punchnotes\pipeline\data\similar_comedian_candidates.json
```

Update:

```text
C:\Users\ethan\coding\punchnotes\pipeline\data\comedian_name_relationships.json
```

Do not edit any files in:

```text
C:\Users\ethan\coding\punchnotes\pipeline\data\bit_annotated_set_archive
```

The archive is intentionally raw source data. Name cleanup happens through the relationship file so mistakes can be undone by editing that file and re-importing.

---

## Task

For each candidate pair, decide whether the two names are:

- `alias`: the two slugs refer to the same comedian
- `not_alias`: the two slugs refer to different people
- `uncertain`: you cannot confidently decide

Most candidate pairs are probably aliases, but the correct spelling may be unknowable from the local names alone. In that case, search the web with queries like:

```text
"Ari Matti" "Kill Tony"
"Ari Mati" "Kill Tony"
"Dedric Flynn" "Kill Tony"
"Dedrick Flynn" "Kill Tony"
```

Use the spelling that is best supported by reliable public results, the performer's own profiles, Kill Tony descriptions, or recurring consensus. If the two names are clearly the same person but the canonical spelling is still unclear after searching, put the pair in `uncertain`.

Do not guess. If common sense and web search do not make the relationship clear, use `uncertain`.

---

## Output Format

The relationship file must stay valid JSON with this shape:

```json
{
  "aliases": {
    "wrong-or-alternate-slug": {
      "canonical_slug": "correct-canonical-slug",
      "canonical_name": "Correct Canonical Name"
    }
  },
  "not_aliases": [
    {
      "slugs": ["first-slug", "second-slug"]
    }
  ],
  "uncertain": [
    {
      "slugs": ["first-slug", "second-slug"]
    }
  ]
}
```

Rules:

- Use slugs exactly as they appear in `similar_comedian_candidates.json`.
- For `aliases`, direction matters: map the incorrect or alternate slug to the canonical slug.
- For `not_aliases` and `uncertain`, direction does not matter.
- Do not create aliases outside the candidate list unless the candidate pair directly proves the relationship.
- Do not create cycles, such as `a -> b` and `b -> a`.
- Do not map a slug to itself.
- Preserve existing relationship decisions unless you have a clear reason to correct them.
