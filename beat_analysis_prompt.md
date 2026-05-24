# Kill Tony Beat Analysis Prompt

You are labeling the comedic structure of a stand-up **set** from *Kill Tony*. Your goal is to partition the set into **beats** — labeled spans of text that together cover every word of the set with no gaps and no overlaps — and write one output file to `C:\Users\ethan\coding\jokescore\data\beat_inbox\`.

---

## Input

A set file at `C:\Users\ethan\coding\jokescore\data\set_inbox\<filename>.jsonl`.

**Line 1** is the set metadata — read it but do not include it in your output:

```json
{"type": "set_meta", "video_id": "CnjJPpr10vM", "episode_title": "KT #768 - SHANE GILLIS + JAMES MCCANN", "episode_url": "...", "guests": [...], "comedian_name": "Matt Worldly", "comedian_type": "bucket_pull", "set_number": 13, "start_seconds": 6872.8}
```

**Lines 2+** are caption segments:

```json
{"video_id": "CnjJPpr10vM", "text": ">> Um in high school, my art teacher was", "start": 6872.8, "duration": 4.72}
```

Strip the `>> ` prefix from `text` when it appears — it is an auto-caption artifact, not part of the spoken words.

---

## Your task

1. Read all caption lines in order.
2. Reconstruct the full set text by joining caption `text` fields (after stripping `>> `).
3. Partition that text into an ordered sequence of labeled beats. Every word must belong to exactly one beat — no word dropped, no word in two beats.
4. Write one JSONL line per beat to the output file.

---

## Beat types

### `premise`
The situation, observation, or story being established. Sets up a joke without delivering the payoff. Usually the longest beats. A set can be entirely premise with no punchline — that is valid data.

**Short example** (Pat O'Neal, set14):
> "my ex-girlfriend, she would love it when I spit in her mouth."

**Long example** (Matt Worldly, set13):
> "Um in high school, my art teacher was like, 'Hey, does anybody in here know how to speak Arabic?' And uh she was getting ready to train us for like a calligraphy lesson. And I was like, 'Fuck it.' I'm like, 'Yeah, I speak Arabic.' She goes, 'Go ahead, Matt. Speak some Arabic for us.'"

---

### `punchline`
The comedic payoff — the line the premise was building toward. Usually shorter than the premise. Arrives at a surprise, subverted expectation, or absurd reveal.

**Example** (Matt Worldly, set13):
> "I said, hell yeah, I learned it from Call of Duty. It means we've got control of a hostage."

**Example** (Cameron Shepherd, set02):
> "Robert Wadlow, world's tallest man, 15 in soft, the [__] end."

---

### `tag`
An additional punchline that riffs directly off the previous punchline without resetting to a new premise. A tag must reference something already said — if it introduces new material, it is a new `premise`, not a tag.

**Example** (Cameron Shepherd, set02 — follows the "15 in soft" punchline):
> "That's the end of the documentary."

**Example** (Pat O'Neal, set14 — follows the vomit punchline):
> "So next time I'm just going to let her sleep."

---

### `act_out`
A physical performance, vocal demonstration, or sound the comedian makes that is not a spoken joke. In the transcript these often appear as bracketed tokens or phonetic spellings.

**Example** (Matt Worldly, set13 — demonstrating fake Arabic):
> "[snorts]"

**Example** (any set):
> "[music]" / "[laughter]" / "[applause]"

Note: `[laughter]` and `[applause]` are crowd reactions auto-captured in the transcript. If one appears mid-sentence within a beat, fold it into that beat's text rather than splitting a sentence for it. Only make it its own `act_out` beat if it stands alone between two other beats.

---

### `crowd_work`
The comedian directly addressing, questioning, or reacting to the audience — breaking from their prepared material to interact with the room.

**Example** (Cameron Shepherd, set02):
> "Leapfrog naked, anyone ever tried it? No?"

**Example** (Dusty Carter, set11):
> "OTHER THAN THAT, I'M OKAY WITH IT."

---

### `transition`
Text that bridges between two bits, pivots to a new subject, or closes the set. Includes explicit closers and pivot phrases.

**Example** (closer):
> "That's my time."

**Example** (closer):
> "Okay, that's just true story, you guys."

**Example** (pivot between bits):
> "Speaking of drugs, they've been talking about legalizing marijuana in America."

---

## Mid-caption splits

A beat boundary will often fall in the middle of a caption line. When this happens, split the caption text at the natural sentence or clause boundary and assign each portion to the appropriate beat. Use the `start` timestamp of the first caption that contributes text to a beat as that beat's `start_seconds`.

**Example:** The caption `"like, \"Fuck it.\" I'm like, \"Yeah, I"` spans the end of a premise and the start of a new beat. Split it: `"like, 'Fuck it.'"` closes the previous beat; `"I'm like, 'Yeah, I speak Arabic.'"` opens the next.

---

## Edge cases

- **No punchline:** Some sets are entirely unstructured — label everything `premise`. This is valid and expected for weak sets.
- **Censored words:** `[ __ ]` represents bleeped profanity. Treat it as a word; copy it verbatim into `text`.
- **Bracketed audio events mid-sentence:** Fold `[laughter]`, `[applause]`, `[cheering]` into the surrounding beat rather than isolating them, unless they stand alone.
- **Tags vs. new premises:** If the follow-up line references the previous punchline, it's a `tag`. If it introduces fresh subject matter, start a new `premise`.

---

## Output specification

Write one file to:

```
C:\Users\ethan\coding\jokescore\data\beat_inbox\<video_id>_set<NN>_<comedian-slug>_beats.jsonl
```

Use the `video_id`, set number, and comedian slug from the input filename.

Each line is one beat:

```json
{"beat_number": 1, "beat_type": "premise", "text": "Um in high school, my art teacher was like, \"Hey, does anybody in here know how to speak Arabic?\" ...", "start_seconds": 6872.8}
```

Fields:
- `beat_number`: 1-indexed integer, sequential within the set
- `beat_type`: one of `premise`, `punchline`, `tag`, `act_out`, `crowd_work`, `transition`
- `text`: the full reconstructed text of this beat (may span multiple captions or be a portion of one)
- `start_seconds`: the `start` value of the first caption contributing text to this beat

**Completeness check:** after writing, mentally concatenate all `text` fields in `beat_number` order and verify it reproduces the full set text with no missing words.

---

## Worked example

Input set: `CnjJPpr10vM_set13_matt-worldly.jsonl`

Expected output beats (abridged):

| beat_number | beat_type | text (abbreviated) |
|---|---|---|
| 1 | premise | "Um in high school, my art teacher was like… 'Go ahead, Matt. Speak some Arabic for us.'" |
| 2 | act_out | "[snorts]" |
| 3 | premise | "and she gasped. She was like, oh my god… Do you know what it translates to?" |
| 4 | punchline | "I said, hell yeah, I learned it from Call of Duty. It means we've got control of a hostage." |
| 5 | transition | "Okay. That's just true story, you guys." |
