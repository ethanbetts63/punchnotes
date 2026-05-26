# Kill Tony Set Annotation Prompt

You are labeling the comedic structure of stand-up **sets** from *Kill Tony*. Only annotate all of the sets for **one video** at a time. Do not process every set in `C:\Users\ethan\coding\jokescore\data\2_set_inbox\` unless all of those files are from the same video; otherwise the work will be too large for your context.

For each selected set file, fill in the empty `label` field on every line and write the annotated copy to `C:\Users\ethan\coding\jokescore\data\3_annotated_set_inbox\`.

---

## Input

Each set file is a JSON object with set metadata at the top level and a `lines` array of caption lines. Example:

```json
{
  "type": "set_meta",
  "video_id": "CnjJPpr10vM",
  "episode_title": "...",
  "episode_url": "...",
  "guests": ["Shane Gillis", "James McCann"],
  "comedian_name": "Pat O'Neill",
  "comedian_type": "regular",
  "set_number": 14,
  "start_seconds": 7450,
  "lines": [
    {"line_number": 1042, "text": "- Folks, my ex-girlfriend,", "start": 7450, "label": ""},
    {"line_number": 1043, "text": "she would love it when I spit in her mouth.", "start": 7453, "label": ""},
    ...
  ]
}
```

---

## Your task

For each selected set file from `2_set_inbox/`, replace the empty `label` value on every line:

- `label`: one of `setup`, `punchline`, `tag`, `fluff`

Write the result to `data/3_annotated_set_inbox/<same-filename>.json`. Preserve all original metadata and line fields verbatim; only replace each empty `label` value with one of the allowed labels.

**Process one set fully before moving to the next.** Read a file, label every line, write the output, delete the source file, then move on. Do not batch.

---

## Labels

### `setup`
A line that establishes premise, scenario, observation, or context for a joke. The line that builds toward the laugh without delivering it.

> "First time we hooked up, I didn't have a condom,"
> "so I tells her, 'Hey, you better not have herpes,'"

### `punchline`
The line where the laugh lands. The reveal, twist, or payoff the setup was building toward. Usually a sharp turn, surprise, or absurd reframe.

> "'because then I will have double herpes.'"
> "Robert Wadlow, world's tallest man, 15 inches soft, the fucking end."

### `tag`
An additional punchline that builds off the previous punchline without needing new setup. A tag rides on the laugh already in the room - if it introduces fresh material, it is a new `setup`, not a tag.

> "That's the end of the documentary." (after the Robert Wadlow punchline)
> "Y'all don't know how to act at all." (escalation of "y'all don't know how to act")

### `fluff`
Everything that is not setup, punchline, or tag. Greetings, sign-offs, name introductions, verbal stumbles (`"Uh..."`, `"Excuse-- fuck."`), audio events the comedian didn't produce (`"[squeals]"` from the kitten/bear), and crowd-acknowledgement filler (`"Hell yeah."`, `"Believe that."`) that isn't doing comedic work.

> "What's up, Austin?"
> "Okay, that's enough for me, thank you."
> "Anyway, my name is Brandon."

---

## How to label

1. Read the whole set first. Get the structure in your head before labeling line-by-line.
2. Identify each joke's punchline first - that's the anchor.
3. Walk backwards from the punchline labeling setup.
4. Walk forwards labeling any tags that ride the laugh.
5. Mark everything else fluff.

### Visual jokes and misdirects

- **Visual jokes can have implicit setup.** If the audience can see the setup, the first spoken comparison or reveal may be the `punchline` even without a verbal setup. Example: `"I know I look like I just fucked a pair of balloons."` can be a punchline because the setup is the comedian's visible appearance.
- **Misdirects turn on the frame-flip line.** Label the line where the audience realizes its assumption was wrong as the `punchline`. Example: after `"The first time I seen titties, I cried,"` the line `"I was looking in the mirror like,"` is the punchline because it reveals the joke is about male breasts, not a woman.
- **The next line after a misdirect is often a tag or continuation.** If it only extends the same reveal, label it `tag`; if the punchline sentence is split by transcription, a second `punchline` line can be acceptable.

### Rules of thumb

- **One punchline per joke.** If you find yourself labeling two adjacent lines as punchline, one of them is probably a tag (rides the previous laugh) or setup (sets up the real punchline). Occasionally, the transcription will split the punchline sentance over two lines which is a case where two punchline lines in a row is accebtable. 
- **Tags require an immediately preceding punchline or tag.** A line cannot tag a fluff or a setup.
- **Sound effects from the show (kitten, bear, music) are fluff.** They appear as `[squeals]`, `[music]`, etc.
- **Verbal stumbles and filler are fluff.** `"Uh..."`, `"Hell yeah."`, `"Believe that."`, `"You know what I mean?"` - when they're not part of an actual joke.
- **Self-introductions are fluff.** `"My name is Brandon."` is fluff unless the name itself is the punchline.
- **Closers are fluff.** `"That's my time."`, `"Thank you guys."`, `"Okay, that's enough for me, thank you."`

---

## Output format

For each input file `data/2_set_inbox/<name>.json`, write `data/3_annotated_set_inbox/<name>.json` with the same top-level metadata and each line labeled:

```json
{
  "line_number": 1043,
  "text": "she would love it when I spit in her mouth.",
  "start": 7453,
  "label": "setup"
}
```

After writing, **delete the source file from `2_set_inbox/`**. The annotated file in `3_annotated_set_inbox/` is the source of truth from this point on.

---

## Worked example 1 High-quality set (Pat O'Neill, `set14`)

A clean, well-structured set. Four discrete setup-to-punchline jokes with a sign-off.

```json
{"text": "- Folks, my ex-girlfriend,", "start": 7450, "label": "setup"}
{"text": "she would love it when I spit in her mouth.", "start": 7453, "label": "setup"}
{"text": "And my new girlfriend hates when I mention that.", "start": 7456, "label": "punchline"}
{"text": "First time we hooked up, I didn't have a condom,", "start": 7468, "label": "setup"}
{"text": "so I tells her, \"Hey, you better not have herpes,\"", "start": 7470, "label": "setup"}
{"text": "\"because then I will have double herpes.\"", "start": 7475, "label": "punchline"}
{"text": "Last weekend, she got so drunk, she threw up on my cock.", "start": 7486, "label": "setup"}
{"text": "Yeah, so next time, I'm just going to let her sleep.", "start": 7490, "label": "punchline"}
{"text": "- I was telling that story last night", "start": 7510, "label": "setup"}
{"text": "and this woman in the crowd called me toxic.", "start": 7511, "label": "setup"}
{"text": "I was like, that's pretty rich coming from somebody", "start": 7514, "label": "setup"}
{"text": "that bleeds out of their goddamn crotch.", "start": 7515, "label": "punchline"}
{"text": "Okay, that's enough for me, thank you.", "start": 7517, "label": "fluff"}
```

Note on 7510: "I was telling that story last night" arguably tags joke #3 (he's still on the vomit story) but has its own full setup-to-punchline arc with a new premise (audience reaction), so it's labeled setup.

---

## Worked example 2 - Medium-quality set (Liv Taylor, `set03`)

Some structure - two clear jokes land - but the set gets cut off by the kitten/bear and the third joke is interrupted.

```json
{"text": "What's up, Austin?", "start": 1379, "label": "fluff"}
{"text": "I've been here for about a year now.", "start": 1381, "label": "setup"}
{"text": "And there's one thing I knew about Texas", "start": 1384, "label": "setup"}
{"text": "before I live in here.", "start": 1386, "label": "setup"}
{"text": "It's hot, right?", "start": 1387, "label": "setup"}
{"text": "But it gets pretty cold at night.", "start": 1389, "label": "setup"}
{"text": "It got pretty cold during the winter.", "start": 1392, "label": "setup"}
{"text": "So cold that I needed help to sleep at night.", "start": 1394, "label": "setup"}
{"text": "So I started listening to Negro Spirituals.", "start": 1398, "label": "punchline"}
{"text": "Yeah, you're like, this crazy bitch has got like", "start": 1405, "label": "setup"}
{"text": "Wade in the water radio on Spotify.", "start": 1407, "label": "setup"}
{"text": "That's fucking crazy.", "start": 1411, "label": "setup"}
{"text": "No, it was just me being too lazy to change the battery", "start": 1412, "label": "setup"}
{"text": "in my smoke detector.", "start": 1417, "label": "punchline"}
{"text": "Hell yeah.", "start": 1422, "label": "fluff"}
{"text": "Uh...", "start": 1423, "label": "fluff"}
{"text": "Uh, I like to think that my dad was somebody to look up to", "start": 1425, "label": "setup"}
{"text": "as, like, an entrepreneur.", "start": 1430, "label": "setup"}
{"text": "It was just a really nice way of saying", "start": 1432, "label": "setup"}
{"text": "that he was a full-time crackhead.", "start": 1434, "label": "punchline"}
{"text": "I don't know if you know this, but, uh, Zip Recruiter...", "start": 1437, "label": "setup"}
{"text": "[squeals]", "start": 1440, "label": "fluff"}
{"text": "Uh, uh, uh...", "start": 1441, "label": "fluff"}
{"text": "Excuse-- fuck.", "start": 1443, "label": "fluff"}
{"text": "A sponsor of Kill Tony actually used to report", "start": 1447, "label": "setup"}
{"text": "the average salary.", "start": 1451, "label": "punchline"}
```

Notes:
- "So I started listening to Negro Spirituals" lands as the shock-turn punchline of the smoke-detector joke, but the smoke-detector reveal is the *real* punchline (recontextualizes it). For the one-punchline-per-joke rule, the shock line is labeled punchline of its own mini-beat and the reveal is the main punchline.
- "That's fucking crazy" (1411) is ambiguous - could be the comedian reading the room or part of the setup for the reveal. Labeled setup.
- The interrupted Zip Recruiter joke (1447-1451) never lands - she gets cut off and finishes hurriedly.

---

## Worked example 3 Low-quality set (Brandon Fields, `set08`)

Very little structure. Brandon admits he's high, rambles, never lands a clean punchline, addresses an audience member at the end.

```json
{"text": "Oh, my God.", "start": 3857, "label": "fluff"}
{"text": "I am high as alien pussy right now.", "start": 3859, "label": "setup"}
{"text": "Don't smoke weed before you do this.", "start": 3863, "label": "setup"}
{"text": "I'm telling you, it's not a good thing.", "start": 3865, "label": "setup"}
{"text": "Anyway, my name is Brandon.", "start": 3867, "label": "fluff"}
{"text": "Yeah, I'm a black guy with a white name, so, I mean.", "start": 3870, "label": "setup"}
{"text": "Believe it or not, I get judged more about what kind of phone I have", "start": 3873, "label": "setup"}
{"text": "more than being black these days.", "start": 3877, "label": "punchline"}
{"text": "Believe that.", "start": 3880, "label": "fluff"}
{"text": "It's like, \"Oh, you got an Android?\"", "start": 3882, "label": "setup"}
{"text": "\"Oh, this ugly nigga got an Android.", "start": 3884, "label": "setup"}
{"text": "I can't take it.\"", "start": 3888, "label": "setup"}
{"text": "Why y'all judge people off of their phones, man?", "start": 3890, "label": "setup"}
{"text": "'Cause I got an iPhone, I'm not cool.", "start": 3893, "label": "setup"}
{"text": "'Cause I don't have an iPhone, I'm not cool.", "start": 3895, "label": "setup"}
{"text": "Maybe? Alright, fuck y'all.", "start": 3898, "label": "fluff"}
{"text": "That is--anyway, yep, I got another white name.", "start": 3901, "label": "fluff"}
{"text": "Um, uh, white thing about me, uh, I could swim.", "start": 3905, "label": "punchline"}
{"text": "- I'm like that dude on House of Rest back there.", "start": 3912, "label": "setup"}
{"text": "That just left a stage.", "start": 3915, "label": "setup"}
{"text": "He was actually on House of Rest.", "start": 3916, "label": "setup"}
{"text": "I saw that ankle monitor and shit.", "start": 3918, "label": "setup"}
{"text": "Thank you, I'm Brandon.", "start": 3920, "label": "fluff"}
```

Notes:
- "more than being black these days" is the structural punchline of the phone bit but it doesn't actually land could also be read as setup leading nowhere. Call it punchline since it's the clearest candidate and seems like what the writer intended. .
- The whole Android section (3882-3895) is "setup, setup, setup, give up" no real punchline arrives, so everything is setup and the "Maybe? Alright, fuck y'all" is fluff (giving up on the bit).
- "Um, uh, white thing about me, uh, I could swim" is a tiny joke (swimming = white) buried in stumbles - labeled punchline.


---

## Process checklist

1. List files in `data/2_set_inbox/`. If empty, stop.
2. For the first file:
   - Read it.
   - Read the whole set and form a mental model of joke structure.
   - Label each line with `label`.
   - Write the annotated copy to `data/3_annotated_set_inbox/` with the same filename.
   - Delete the source file from `2_set_inbox/`.
3. Move to the next file. Repeat.
4. When `2_set_inbox/` is empty, stop.
