# Kill Tony Set Extraction Prompt

You are extracting stand-up **sets** from a YouTube transcript of an episode of *Kill Tony*. Your goal is to produce one file per set in `C:\Users\ethan\coding\jokescore\data\set_inbox\`. Each output file contains only the comedian's ~1-minute set — no intro, no interview, no ads, no transition banter.

---

## Input

**Only process the first file in `data\transcript_inbox\`. Do not process multiple files in one run — one episode per invocation.**

A JSON transcript at `C:\Users\ethan\coding\jokescore\data\transcript_inbox\<video_id>.json`. It is a single JSON object with episode metadata at the top level and all caption segments in a `segments` array:

```json
{
  "type": "episode_meta",
  "video_id": "CnjJPpr10vM",
  "episode_title": "KT #768 - SHANE GILLIS + JAMES MCCANN",
  "episode_url": "https://www.youtube.com/watch?v=CnjJPpr10vM",
  "segments": [
    {"text": "[MUSIC]", "start": 0},
    {"text": "Yeah, those are my tits, make some noise everybody!", "start": 711},
    ...
  ]
}
```

---

## What you are extracting

A "set" is the **~1-minute stand-up performance** a comedian delivers after Tony introduces them. Real durations average 60 seconds but can be shorter or longer **30–180 seconds**. Extract every set — bucket pulls (open-mic'ers), regulars / golden ticket winners. Skip everything else: the post-set interview, the pre-show intro / band / guest / format-explainer block, sponsor/ad reads, and transition banter between sets.

---

## Show structure (use this to navigate)

1. **Intro block** — cold open + band intro + initial sponsor read + guest intro + format explainer ("over 250 souls signed up… 60 seconds uninterrupted… kitten means wrap it up… angry West Hollywood bear…"). **Sets never start before the format explainer ends.**
2. **Repeating loop**, runs ~4–8 times per show:
   - **(Optional)** A regular / golden ticket holder is introduced for a "new minute" — counts as a set.
   - **Bucket pull intro** — Tony names the next comedian ("your first/next/final bucket pull", "60 seconds going to [Name]", "Make some noise for [Name]").
   - **Set** — the comedian performs. *Extract this.*
   - **Interview** — Tony interviews the comedian on the couch. *Skip.*
   - **(Optional)** Ad read tucked in before the next bucket pull.
3. **Regular/Golden ticket winner close** last guest will almost always be a regular or golden ticket winner. After their set and interview there will be closing remarks. you can also skip this. 

---

## How to find set boundaries

### Set START — look backward from the comedian's first line of material

A set begins on the **first caption that is the comedian on the mic**. The captions immediately before it almost always include one of these Tony cues — note that auto-captions routinely mangle "bucket pull" to **"bucket pool" / "bucket bowl" / "bucket hole" / "bucket bull"**, so match loosely:

- "your first / next / final bucket pull"
- "60 seconds going to [Name]" / "60 seconds uninterrupted going to [Name]"
- "Make some noise for [Name]" / "Here comes [Name]" / "[Name], everybody"
- For regulars: "debut a brand new minute" / "[Name] doing a new minute"

A short music sting always plays right after Tony's intro and before the comedian's first line — a strong set-entry cue. These appear in various forms: `[music]`, `[MUSIC]`, or `(upbeat music)`. **Distinguish from show-open music:** `[MUSIC]` also appears in the first ~60 seconds during the band/intro block — and sometimes the transcriptoin tool will not pickup on the music so treat it as a great flag but the set may start without it. 

Common openers:
- Audience greeting: "What's up, Austin?" / "Hey, how we doing?"
- Acknowledging their own name: "That's right, Tom Frank."
- Jumping straight into a premise: "I uh recently saw the worst documentary of my life…"
- Self-referential line about appearance / a prop they brought
- "MAKE SOME NOISE EVERYBODY" *by* the comedian as they grab the mic (Tony's "Make some noise for [Name]" comes **before** the music — the comedian's identical phrasing comes after)

Include the comedian's opener (greeting, name acknowledgement, etc.) — it's part of the set.

### Set END — look for the close

A set ends on the **last caption of the comedian's material**, just before Tony begins the interview. End cues:

- **Comedian explicitly closes**: "Thank you guys for your time", "Thank you so much", "I love you all", "All right, thank you", sometimes ending by saying their own name.
- **Tony's wrap line**: "[Name], everybody", "[Name], ladies and gentlemen", "All right, [Name]", "That was exactly a minute, [Name]", "All right, that's all your time".
**Audio cues from the show:**

- **Kitten sound at 60 seconds.** Played every set at the 1-minute mark. **Not** a hard stop — comedians routinely keep going. Often missing from the transcript entirely, or appears as a stray `[music]` / odd punctuation. Do **not** end the set just because a minute has passed.
- **Bear sound (the "angry West Hollywood bear").** Only plays if the comedian runs ~10+ seconds past the minute. The comedian is forced to stop, but Tony will often invite them to land the punchline ("Hold on. Go ahead now. I want to hear the end of it." / "go ahead and finish your joke"). Include that final tag. The bear has been transcribed as `[screaming]` in at least one episode.

**Bracketed and parenthetical audio captions — what to do with them:**

- **Audience reactions → omit from output.** `(audience laughing)`, `(audience laughs)`, `(laughing)`, `(audience cheering)`, `[cheers and applause]`, `(audience applauding)` and similar forms appear throughout sets and interviews. These are crowd reactions, not spoken content — **do not include them in set output files** but the cheering might be indicative of an audience welcoming a comedian on stage so worth paying attention to.

**Interview-mode cues (these are AFTER the set — do not include):**
- "Welcome back, [Name]" / "Welcome, [Name]"
- "How long you been doing stand-up?" / "How old are you?" / "Where are you from?" / "What do you do for a living?"
- "I'm guessing it's your Kill Tony debut?"
- Any biographical question Tony asks the comedian

Back-and-forth dialogue with short turns ("Yeah." / "Okay." / "Where at?" / "San Diego." / "Nice.") = interview, not set.

### The "set or interview" tiebreaker

**Sets are monologues.** 99% of sets are uninterrupted. One continuous voice telling jokes = set. Dialogue with multiple short exchanges = interview. The 1% exception is a brief Tony timer-warning ("Is that it, [Name]? Uh it's like 10 seconds more. Go ahead.").

**When you are confident a caption inside the set range is Tony or a panel member, omit that caption from the output.** Goal: a clean transcript of just the comedian's minute. Only drop captions you're sure aren't the comedian; if in doubt, leave it in.

### Ads never appear inside a set

Ads contain product names, `/killtony` URLs, promo codes, and pitch language. They live at the ends of interviews / between segments, **never during a set**.

---

## Worked examples (use these as calibration if uncertain)

**Note: use `start` timestamps as anchors, not line numbers — line counts shift when bracketed captions are inserted.**

| Episode | Comedian | Type | Set start | Set end | Notes |
|---|---|---|---|---|---|
| `CnjJPpr10vM` | Martin Phillips | Regular / new minute | start: 387 ("- What's up?") | start: 445 ("Is that a minute?") | Tony intro ends "The great Martin Phillips." at start 380; `(upbeat music)` at start 383 = set-entry sting. Tony wraps "Exactly a minute, Martin Phillips." at start 449; "Come back, Martin." at start 454 starts interview. |
| `CnjJPpr10vM` | Cameron Shepherd | Bucket pull | start: 711 ("Yeah, those are my tits, make some noise everybody!") | start: 788 ("Thank you guys for your time, I love you all.") | Tony intro "Cameron Shepherd, everybody." at start 708. Interview begins shortly after start 788. |
---

## Output specification

For each set you identify, write a **new file** to:

```
C:\Users\ethan\coding\jokescore\data\set_inbox\<video_id>_set<NN>_<comedian-slug>.jsonl
```

Where:
- `<video_id>` matches the source filename (e.g., `CnjJPpr10vM`).
- `<NN>` is a two-digit, 1-indexed set number in show order (`01`, `02`, …).
- `<comedian-slug>` is the comedian's name, lowercased, spaces→hyphens, non-alphanumerics removed (e.g., `martin-phillips`, `cameron-shepherd`, `frankie-gonzalez`). If the name is unclear, use `unknown`.

**File contents:** a metadata line first, then the JSONL caption lines from the source transcript.

**Line 1 — set metadata** (write this yourself based on what you've identified):

```json
{"type": "set_meta", "video_id": "CnjJPpr10vM", "episode_title": "KT #768 - SHANE GILLIS + JAMES MCCANN", "episode_url": "https://www.youtube.com/watch?v=CnjJPpr10vM", "guests": ["Shane Gillis", "James McCann"], "comedian_name": "Cameron Shepherd", "comedian_type": "bucket_pull", "set_number": 2, "start_seconds": 711}
```

Fields:
- `type`: always `"set_meta"`
- `video_id`, `episode_title`, `episode_url`: copy from the transcript's top-level metadata
- `guests`: list of guest names parsed from the episode title (the names after the dash)
- `comedian_name`: the comedian's name as Tony introduces them (prefer Tony's intro spelling over auto-caption mangling)
- `comedian_type`: `"bucket_pull"` (random draw), `"regular"` (recurring comedian doing a new minute), or `"golden_ticket"` (golden ticket winner returning)
- `set_number`: 1-indexed position in the episode
- `start_seconds`: the `start` value from the first caption line of the set

**Lines 2+ — caption lines**: one segment object per line, copied verbatim from the source `segments` array. Each line is `{"text": "...", "start": <integer>}`. Two types of omissions are permitted: (1) segments you are confident are Tony or a panel member interjecting mid-set; (2) audience reaction segments — `(audience laughing)`, `(laughing)`, `[cheers and applause]`, `(audience applauding)`, `(audience cheering)` and similar forms. Do not omit in-set sound effects or props. If neither applies (the common case), these lines are a verbatim slice of the source array.

Example: `CnjJPpr10vM_set02_cameron-shepherd.jsonl` would have the `set_meta` line followed by segments with `start` 711 through 788, with any audience-reaction segments in that range dropped.

---

## Process checklist

1. Read the input JSON. Note the top-level `video_id`, `episode_title`, and `episode_url` — you will need these for every set's metadata. Parse the guest names from `episode_title` (they appear after the dash, separated by `+` or `&`). All caption segments are in the `segments` array.
2. Skip past the intro block (cold open → format explainer). Work through `segments` in order.
3. For each set in show order: find Tony's intro cue + comedian's name, determine `comedian_type`, mark the first caption of the comedian's monologue as the start, mark the last caption before the interview begins as the end, capture the name for the filename.
4. **As soon as you have identified the boundaries for a set, write its output file immediately** — do not mentally extract all sets first and then write them in bulk. Write each file the moment you have the start/end range and comedian name confirmed, then continue scanning for the next set. Expect 4–8 bucket pulls plus any "new minute" performances by regulars.
5. **Once all sets are written, delete the inbox transcript** — a full copy has already been saved to the archive, so the inbox copy is no longer needed.

## When in doubt

- **Err on the side of less, not more.** If a caption is ambiguous, leave it out rather than leak interview content.
- **Names get mangled** by auto-captions ("Frankie Gonzales" vs "Frankie Gonzalez", "Adam Malayev" vs "Adam Malaeb"). Pick the spelling Tony uses on the intro line.
- **If you can't confidently identify a set's boundaries, skip it** and note the uncertainty rather than emit a bad file.
