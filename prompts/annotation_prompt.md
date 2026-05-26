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

Every beat has its own `premise` and `topics`. A bit gets its own `premise` **only when it has more than one beat** — the bit premise is the umbrella that ties multiple beats together. Single-beat bits don't need a bit premise because the beat premise already captures the joke's logic.

```json
{
  "type": "set_meta",
  "video_id": "...",
  "comedian_name": "...",
  ...
  "bit_meta": {
    "1": {
      "beats": {
        "1": {
          "premise": "New partners hate hearing about an ex's sexual preferences.",
          "topics": ["exes", "relationships"]
        }
      }
    },
    "2": {
      "premise": "Estonia drafts everyone America excludes.",
      "beats": {
        "1": {
          "premise": "A wheelchair-bound soldier doubles as a suicide grenade carrier.",
          "topics": ["Estonia", "wheelchairs", "grenades"]
        },
        "2": {
          "premise": "'Special forces' can mean special-needs rather than elite.",
          "topics": ["special forces", "down syndrome", "wordplay"]
        }
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

- **Bit**: one or more beats that share a premise. Every bit has at least one beat.
- **Beat**: one setup/punchline/tags unit with its own specific comedic logic.

### Bit numbers and beat numbers

Use sequential integers starting from 1. Assign `"bit": N` and `"beat": N` on each line. Lines outside all bits (opening greetings, sign-offs) get `"bit": null, "beat": null`.

### Bit vs. multiple bits

**Shared topic ≠ shared premise.** Don't group beats just because they're about the same subject. Group them only when removing one would orphan the others.

The test: **can you extract a beat alone and still have it make sense?**
- If yes → it's its own bit
- If no (it depends on a premise established earlier) → same bit

**Watch for pronoun bridges.** If a comedian links two structurally independent jokes by using a pronoun callback (e.g. "him" referring to someone established in the prior joke), they are still separate bits. The test is whether the joke's comedic premise would survive a one-word change ("him" → "my son"), not whether the current performance depends on the prior line.

### `bit_meta`

Every beat has `premise` and `topics`. A bit has its own `premise` **only when it has multiple beats** — the bit premise is the umbrella across them.

For multi-beat bits, every beat must still have its own premise. The bit premise is the broad theme; each beat premise is the specific comedic mechanism of that beat.

**Premise rules:**
- State the abstract comedic logic — *why is this funny*, not a summary of what was said.
- No pronouns tied to the comedian — no "he", "she", "they", "the comic".
- As short as possible while keeping the meaning.
- Use the most general form: `"Living in a car technically counts as homeownership."` not `"Living in a RAV4 technically counts as homeownership."`

**Topics:** 1–4 short, specific, searchable nouns per beat. Prefer `"crackheads"` over `"people doing drugs"`.

### Joke types and premise formulas

Most jokes fall into one of these mechanisms. Each has its own premise shape:

**Misdirect** — assumption planted, then subverted.
> Formula: *X implies Y, not Z.*
> Example:
> - setup: `"My son just came out as trans."`
> - setup: `"Well, shouldn't call him my son anymore."`
> - punchline: `"Now that he's dead to me,"`
> Premise: `"Refusing to call a transitioning child your son implies a new title, not their disownment."`

**Reframe** — hidden implication of a known thing is surfaced. No prior assumption is planted; the audience just hadn't considered this angle.
> Formula: state the hidden implication directly.
> Example:
> - setup: `"they got him on puberty blockers"`
> - punchline: `"or as pedophiles call them preservatives."`
> - tag: `"Fucking miracle medicine."`
> Premise: `"Pedophiles benefit from puberty blockers."`

**Phonetic match** — two *different* words sound alike, and both independently fit the context.
> Formula: state the sonic match and why both sides independently fit.
> Example:
> - setup: `"what do you call a little person with ADHD?"`
> - punchline: `"That's right, a fidget."`
> Premise: `"'Midget' and 'fidget' sound alike, and 'fidget' independently fits ADHD."`

**Double-meaning** — the *same* words admit two readings, and the comedian deliberately picks the non-standard one. Hinges on semantic ambiguity, not phonetic similarity.
> Formula: *Taken literally, [phrase] has two meanings.*
> Example:
> - setup: `"'In case of fire, use stairs.'"`
> - punchline: `"Fuck that, let's use water."`
> Premise: `"Taken literally, 'In case of fire, use stairs' has two meanings."`

**What-if** — a counterfactual scenario is posed and the joke comes from taking it seriously. Distinct from reframe: a reframe surfaces a *real* implication; a what-if *invents* one and runs with it.
> Formula: *What if [counterfactual]?* or state the hypothetical condition directly.
> Example:
> - setup: `"A guy stole my wallet."`
> - setup: `"He's like, ha ha, I have your wallet."`
> - punchline: `"I was like, ha ha, you have 8K of credit card debt."`
> Premise: `"What if stealing a credit card meant you also stole the debt."`

**Elephant-in-the-room** — taboo observation said aloud. The audience already knows the conclusion; the laugh comes from breaking the silence.
> Formula: *X is widely understood about Y but rarely said aloud.*
> Example:
> - setup: `"You know, these shootings are often done by the same race."`
> - punchline: `"I'm looking at you, honkies."`
> Premise: `"School shootings are widely associated with white shooters but rarely said aloud."`

**Visual jokes** — if the punchline relies on the comedian's appearance (no verbal setup), infer the visual and state the connection as a universal truth.
> Example:
> - punchline: `"I know I look like I just fucked a pair of balloons."`
> Premise: `"Upright hair can look like static from sex with balloons."`

### Boundary rules

- A new bit starts when the comedian introduces a new standalone premise that doesn't depend on the prior bit.
- A new beat starts when the comedian develops another setup/punchline unit under the current bit's premise.
- Multi-beat bits typically have a shared setup at the start that establishes the umbrella premise, then each beat is a different application of that premise.
- Do not merge separate bits just because they share a broad topic.
- Do not split a bit just because a new setup line appears after a punchline — decide whether it depends on the existing premise.
- Fluff that sits inside a bit's flow can receive that bit's number.

---

## How to annotate

1. Read the whole set first. Get the joke structure in your head.
2. Identify each punchline — that's the anchor for each beat.
3. Walk backwards from each punchline labeling setup; walk forwards labeling tags.
4. Mark everything else fluff.
5. For each beat, identify the joke type (misdirect / reframe / phonetic match / double-meaning / what-if / elephant / visual) and write a premise using its formula.
6. Group beats into bits by shared premise. Apply the extraction test: if a beat would survive standalone, it's its own bit.
7. For multi-beat bits, write a bit premise that captures the umbrella the beats share.
8. Write the output JSON with `bit_meta` and fully labeled lines.

---

## Process checklist

1. Process only the files you were given. 
2. For each file:
   - Read the whole set.
   - Annotate: label every line, assign bit/beat numbers, write bit_meta.
   - Write the output to `data/4_bit_annotated_set_inbox/<same-filename>.json`.
   - Delete the source file from `data/2_set_inbox/`.
3. Move to the next file. Repeat until all given files are done.

---

## Examples

