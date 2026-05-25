# Kill Tony Bit and Beat Annotation Prompt

You are adding the final semantic layer to annotated *Kill Tony* stand-up sets.

Process **one annotated set file at a time** from:

`C:\Users\ethan\coding\jokescore\data\annotated_set_inbox\`

Only annotate all of the sets for **one episode/video** at a time. Do not process every set in `annotated_set_inbox/` unless all of those files are from the same `video_id`; otherwise the work will be too large for your context.

For each processed file, write one bit annotation file with the same filename to:

`C:\Users\ethan\coding\jokescore\data\bit_annotation_inbox\`

Do not modify or delete the source annotated set file, except that you may correct a line's `label` if it is clearly wrong and the correction is needed for accurate bit/beat annotation.

---

## Input

Each input file is an annotated set JSON object with set metadata and a `lines` array. Each line has:

- `line_number`: original transcript line number
- `text`: caption text
- `label`: one of `setup`, `punchline`, `tag`, `fluff`

Use `line_number` as the only coordinate system. Do not use local array indexes.

---

## Joke Hierarchy

Top to bottom:

- **Set**: the full recorded appearance of the comic doing standup.
- **Bit**: a single beat or a sequence of beats that do not make sense without the context of a shared premise.
- **Beat**: a local joke unit inside a bit: setup + punchline + optional tags.
- **Line**: one caption line labeled as `fluff`, `setup`, `punchline`, or `tag`.

Topics are attributed at the **beat** level and are the salient topic or topics of the beat.

Premises are attributed at the **bit** level and are the smallest standalone "what this bit is about" statement that the audience needs in order for the beats to make sense.

---

## Your Task

Read the whole set first. Then group the set into bits and beats.

For each bit:

- Write a concise `premise`.
- Set `line_range` to the inclusive `[first_line_number, last_line_number]` for that bit.
- Add one or more beats.

For each beat:

- Set `line_range` to the inclusive `[first_line_number, last_line_number]` for that beat.
- Add `topics`: short, specific topic strings.

---

## Boundary Rules

- A new bit starts when the comedian introduces a new standalone premise.
- A new beat starts when the comedian develops another setup/punchline unit under the current bit's premise.
- Do not merge separate bits just because they share a broad topic.
- Do not split a bit just because a new `setup` line appears after a `punchline` or `tag`; decide whether it depends on the existing premise.
- Fluff can be included in a bit or beat range if it sits inside that bit's flow.
- Opening greetings, sign-offs, and dead air that do not belong to any bit may be omitted from all bit ranges.

---

## Output Format

Write exactly one JSON object:

```json
{
  "type": "set_bit_annotation",
  "source_file": "CnjJPpr10vM_set14_pat-oneill.json",
  "video_id": "CnjJPpr10vM",
  "comedian_name": "Pat O'Neill",
  "set_number": 14,
  "bits": [
    {
      "bit_id": "bit_001",
      "premise": "The comic's new girlfriend hates hearing about sexual habits from his ex.",
      "line_range": [3348, 3350],
      "beats": [
        {
          "beat_id": "bit_001_beat_001",
          "line_range": [3348, 3350],
          "topics": ["relationships", "exes", "sexual habits"]
        }
      ]
    }
  ]
}
```

IDs must be sequential and zero-padded:

- `bit_001`, `bit_002`, `bit_003`
- `bit_001_beat_001`, `bit_001_beat_002`

---

## Topic Guidance

Good topics are short and searchable:

- `streaming`
- `Twitch`
- `middle age`
- `crackheads`
- `dating`
- `parents`
- `work`

Avoid vague topics unless they are genuinely the point:

- `life`
- `people`
- `things`
- `comedy`

Use 1-4 topics per beat. Prefer specific nouns over full sentences.

---

## Premise Guidance

A good premise is specific enough to distinguish one bit from another bit on the same topic.

Topic:

`streaming`

Weak premise:

`Streaming is funny.`

Strong premise:

`Middle-aged men trying to become Twitch streamers are sad and unappealing.`

Another strong premise on the same topic:

`Crackheads would make entertaining livestreamers because their lives are chaotic.`

---

## Process Checklist

1. List files in `data/annotated_set_inbox/`. If empty, stop.
2. Pick one file.
3. Read the whole set before writing anything.
4. Identify bit premises.
5. Split each bit into beats.
6. Write `data/bit_annotation_inbox/<same-filename>.json`.
7. Leave the source annotated set file untouched.
8. Move to the next file only if explicitly asked.
