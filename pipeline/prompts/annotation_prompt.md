# Kill Tony Set Annotation Prompt

You are annotating stand-up **sets** from *Kill Tony*. Many jokes you will see
will be funny. Many will not be funny at all. It is not our job as annotators
to judge. It is our job to identify the intended joke structure as honestly as
possible.

## Input

Each input file is a set JSON from `pipeline/data/set_inbox/`.

## Output

Write the annotated file back to `pipeline/data/set_inbox/<same-filename>.json`,
overwriting the unannotated source. The output adds `bit_meta` before `lines`,
and each line gets `label`, `bit`, and `beat` fields.

Every beat has one flat `joke_type` field. Do not write a `premise`. Do not
write joke-type-specific fields such as `bait`, `implication`, `reveal`,
`subject`, `reframe`, `heard`, `reheard`, `phrase`, `expected`, `comic`,
`a`, `b`, `shared`, `extreme`, `elephant`, `frame`, `answer`, or `reason`.

## Line Labels

### `setup`

A line that establishes scenario, observation, context, or expectation for a
joke without delivering the laugh.

### `punchline`

The line where the laugh lands. The reveal, twist, or payoff the setup was
building toward.

### `tag`

An additional payoff in the same beat, riding on the laugh already in the room.
A tag can carry its own `setup`: a setup line followed by a tag belongs to the
current beat, while a setup line followed by a punchline starts a new beat. So
`punchline -> setup -> tag -> setup -> tag` is a single valid beat.

### `fluff`

Everything that is not setup, punchline, or tag: greetings, sign-offs, name
introductions, verbal stumbles (`"Uh..."`), audio events (`"[squeals]"`), and
crowd-acknowledgement filler (`"Hell yeah."`) that is not doing comedic work.

## Labeling Rules

- **One punchline per beat.** If two adjacent lines both look like punchlines,
  one is probably a tag or setup. Exception: a transcription split across two
  lines can have two consecutive punchline labels.
- **A tag only exists after a punchline.** The beat's first payoff is the
  `punchline`; every later payoff is a `tag`. A setup or crowd fluff may sit
  between the punchline and a later tag.
- **A setup's beat is decided by what follows it.** A `setup` followed by a
  `tag` joins the current beat; a `setup` followed by a `punchline` starts a
  new one.
- **Sound effects are fluff.** `[squeals]`, `[music]`, etc.
- **Self-introductions are fluff** unless the name itself is the punchline.
- **Closers are fluff.** `"That's my time."`, `"Thank you guys."`
- **Misdirects turn on the frame-flip line.** Label the line where the audience
  realizes its assumption was wrong as the punchline.

## Bit and Beat Structure

### Hierarchy

- **Bit**: one or more beats that share necessary setup/context. Every bit has
  at least one beat.
- **Beat**: one setup/punchline/tags unit with its own specific comedic logic.
  Every beat must contain at least one `punchline` line.

### Bit numbers and beat numbers

Use sequential integers starting from 1. Assign `"bit": N` and `"beat": N` on
every `punchline` line.

Set every `setup`, `tag`, and `fluff` line to `"bit": null, "beat": null`.

The import pipeline infers non-punchline ownership:

- A `setup` belongs to the next payoff line: if that payoff is a `tag`, the
  setup joins the current beat; if it is a `punchline`, the setup opens the new
  beat.
- A `tag` belongs to the most recent `punchline` or `tag`.
- A `fluff` line stays null unless it falls inside a bit or beat span created
  by setup/punchline/tag lines.

### Bit vs. multiple bits

**Shared subject matter does not equal shared bit.** Do not group beats just
because they are about the same subject. Group them only when removing one
would orphan the others.

The test: **can you extract a beat alone and still have it make sense?**

- If yes -> it is its own bit.
- If no, because it depends on setup established earlier -> same bit.

**Watch for pronoun bridges.** If a comedian links two structurally independent
jokes by using a pronoun callback, they are still separate bits when the joke's
logic would survive a small wording change.

## Joke Types

Assign every beat one of these `joke_type` values:

- `misdirect`: an assumption is planted, then subverted.
- `reframe`: a known thing is given a newly visible interpretation.
- `phonetic-match`: two different words sound alike.
- `double-meaning`: the same word or phrase admits two or more readings.
- `contradiction`: one subject holds two positions that cannot both be true.
- `analogy`: two different things share the same unexpected structure.
- `hyperbole`: one dimension of a subject is stretched past plausibility.
- `elephant-in-the-room`: a taboo or avoided observation is said aloud.
- `anti-humor`: a joke form promises a payoff, then delivers the banal truth.

### `bit_meta`

> **IMPORTANT:** `bit_meta` MUST be a JSON object keyed by bit number as a
> string (e.g. `"1"`, `"2"`), NOT a JSON array. `beats` within each bit must
> also be a JSON object keyed by beat number as a string. Never use `[...]` for
> `bit_meta` or `beats`.

Each beat object contains only `joke_type`:

```json
{
  "bit_meta": {
    "1": {
      "beats": {
        "1": { "joke_type": "misdirect" }
      }
    }
  }
}
```

## Additional Rules

- A bit is the smallest standalone segment of material that can be lifted out
  of the set and still make sense as its own joke sequence.
- A `setup` following a punchline joins the current beat if the next payoff is
  a `tag`, and starts a new beat if the next payoff is a `punchline`.
- Multi-beat bits typically have shared setup at the start, then each beat is a
  different application or escalation of that context.
- Do not merge separate bits just because they share broad subject matter.
- Set all setup, tag, and fluff lines to `"bit": null, "beat": null`.
- Beats consisting of nothing but a punchline are possible but rare.

## How to Annotate

1. Read the whole set first. Get the joke structure in your head.
2. Identify each punchline. That is the anchor for each beat.
3. Walk backwards from each punchline labeling setup; walk forwards labeling
   tags and any setup that feeds a later tag.
4. Mark everything else fluff.
5. Assign each beat one `joke_type`.
6. Group beats into bits. Apply the extraction test: if a beat would survive
   standalone, it is its own bit.
7. Write the output JSON with `bit_meta`, fully labeled lines, and bit/beat
   numbers only on punchlines.

## Process Checklist

**Do not read multiple files before writing. Complete all steps for one file
before opening the next.**

**Do not read any source code, management commands, or utility files.** The
upload command and its behavior are fully described here; no further
exploration is needed.

1. Process only the files you were given.
2. For each file, in order:
   a. Read that one file.
   b. Annotate it: label every line, assign bit/beat numbers to punchlines,
      write `bit_meta`.
   c. Write the annotated output back to
      `pipeline/data/set_inbox/<same-filename>.json`.
   d. Run:
      `python manage.py upload --annotated --file pipeline/data/set_inbox/<filename>.json`
      This is **VERY IMPORTANT**. It lets you learn from any mistakes before
      moving on.
   e. Only then open the next file.

- If a file is already annotated, upload it and see what happens.
- Never spin up any agents.
- At completion, return only:
  `DONE: <count> files processed`
  `FAILED: <filenames or none>`
  Do not summarize in more detail.
