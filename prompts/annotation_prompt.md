# Kill Tony Set Annotation Prompt

You are annotating stand-up **sets** from *Kill Tony* in a single pass: labeling every line and grouping lines into bits and beats simultaneously.

Annotate only the files you are explicitly given — do not process any files beyond those listed.

---

## Input

Each input file is a set JSON from `data/2_set_inbox/`. Lines have an empty `label` field:

```json
{
  "type": "set_meta",
  "video_id": "...",
  "comedian_name": "...",
  ...
  "lines": [
    {"line_number": 101, "text": "My ex-girlfriend...", "start": 450, "label": ""}
  ]
}
```

---

## Output

Write the annotated file to `data/4_bit_annotated_set_inbox/<same-filename>.json`. The output adds `bit_meta` before `lines`, and each line gets `label`, `bit`, and `beat` fields. Field order on each line: `text`, `label`, `bit`, `beat`, `line_number`, `start`.

```json
{
  "type": "set_meta",
  "video_id": "...",
  "comedian_name": "...",
  ...
  "bit_meta": {
    "1": {
      "premise": "New partners hate hearing about an ex's sexual preferences.",
      "beats": {
        "1": {"topics": ["exes", "relationships"]}
      }
    }
  },
  "lines": [
    {"text": "My ex-girlfriend...", "label": "setup", "bit": 1, "beat": 1, "line_number": 101, "start": 450},
    {"text": "Thank you.", "label": "fluff", "bit": null, "beat": null, "line_number": 115, "start": 490}
  ]
}
```

After writing, delete the source file from `data/2_set_inbox/`.

---

## Line Labels

### `setup`
A line that establishes premise, scenario, observation, or context for a joke — building toward the laugh without delivering it.

### `punchline`
The line where the laugh lands. The reveal, twist, or payoff the setup was building toward.

### `tag`
An additional punchline that builds off the previous punchline without needing new setup. A tag rides on the laugh already in the room — if it introduces fresh material, it is a new `setup`, not a tag.

### `fluff`
Everything that is not setup, punchline, or tag: greetings, sign-offs, name introductions, verbal stumbles (`"Uh..."`), audio events (`"[squeals]"`), and crowd-acknowledgement filler (`"Hell yeah."`) that isn't doing comedic work.

---

## Labeling Rules

- **One punchline per joke.** If two adjacent lines both look like punchlines, one is probably a tag or setup. Exception: a transcription split across two lines can have two consecutive punchline labels.
- **Tags require an immediately preceding punchline or tag.** A line cannot tag a fluff or setup.
- **Sound effects are fluff.** `[squeals]`, `[music]`, etc.
- **Self-introductions are fluff** unless the name itself is the punchline.
- **Closers are fluff.** `"That's my time."`, `"Thank you guys."`
- **Visual jokes can have implicit setup.** If the audience can see the setup, the first spoken comparison or reveal may be the punchline even without a verbal setup.
- **Misdirects turn on the frame-flip line.** Label the line where the audience realizes its assumption was wrong as the punchline.

---

## Bit and Beat Structure

### Hierarchy

- **Bit**: a single premise or a sequence of beats that only make sense under a shared premise.
- **Beat**: one setup/punchline/tags unit inside a bit.

### Bit numbers and beat numbers

Use sequential integers starting from 1. Assign `"bit": N` and `"beat": N` on each line. Lines outside all bits (opening greetings, sign-offs) get `"bit": null, "beat": null`.

### `bit_meta`

For each bit, write a `premise` and a `beats` dict. For each beat, write `topics`.

**Premise rules:**
- State the abstract comedic logic, not a summary of what was said.
- No pronouns tied to the comedian — no "he", "she", "they", "the comic".
- As short as possible while keeping the meaning.
- Use the most general form: `"Living in a car technically counts as homeownership."` not `"Living in a RAV4 technically counts as homeownership."`

**Visual premises:** If a joke has no verbal setup, infer the visual from the punchline and state the connection as a universal truth. e.g. punchline `"I look like I just fucked a pair of balloons."` → premise `"Upright hair can look like static from sex with balloons."`

**Misdirect premises:** Name the assumption being exploited and the unexpected replacement. e.g. `"Talk of seeing tits implies a woman, not a man."`

**Topics:** 1–4 short, specific, searchable nouns per beat. Prefer `"crackheads"` over `"people doing drugs"`.

### Boundary rules

- A new bit starts when the comedian introduces a new standalone premise.
- A new beat starts when the comedian develops another setup/punchline unit under the current bit's premise.
- Do not merge separate bits just because they share a broad topic.
- Do not split a bit just because a new setup line appears after a punchline — decide whether it depends on the existing premise.
- Fluff that sits inside a bit's flow can receive that bit's number.

---

## How to annotate

1. Read the whole set first. Get the joke structure in your head.
2. Identify each punchline — that's the anchor for each beat.
3. Walk backwards from each punchline labeling setup; walk forwards labeling tags.
4. Mark everything else fluff.
5. Group beats into bits by shared premise.
6. Write the output JSON with `bit_meta` and fully labeled lines.

---

## Process checklist

1. Process only the files you were given. If none were given, stop.
2. For each file:
   - Read the whole set.
   - Annotate: label every line, assign bit/beat numbers, write bit_meta.
   - Write the output to `data/4_bit_annotated_set_inbox/<same-filename>.json`.
   - Delete the source file from `data/2_set_inbox/`.
3. Move to the next file. Repeat until all given files are done.

---

## Examples

