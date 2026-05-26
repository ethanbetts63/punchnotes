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

Every beat has its own `premise`, `joke_type`, and `topics`. A bit gets its own `premise` **only when it has more than one beat** — the bit premise is the umbrella that ties multiple beats together. Single-beat bits don't need a bit premise because the beat premise already captures the joke's logic.

Field order on each beat: `premise`, `joke_type`, `topics`.

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
          "joke_type": "reframe",
          "topics": ["exes", "relationships"]
        }
      }
    },
    "2": {
      "premise": "Estonia drafts everyone America excludes.",
      "beats": {
        "1": {
          "premise": "A wheelchair-bound soldier doubles as a suicide grenade carrier.",
          "joke_type": "what-if",
          "topics": ["Estonia", "wheelchairs", "grenades"]
        },
        "2": {
          "premise": "'Special forces' can mean special-needs rather than elite.",
          "joke_type": "double-meaning",
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
- **Sight-dependent jokes can have implicit setup.** If the audience can see the setup, the first spoken comparison or reveal may be the punchline even without a verbal setup.
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

Every beat has `premise`, `joke_type`, and `topics`. A bit has its own `premise` **only when it has multiple beats** — the bit premise is the umbrella across them.

For multi-beat bits, every beat must still have its own premise. The bit premise is the broad theme; each beat premise is the specific comedic mechanism of that beat.

**Premise rules:**
- **Be as succinct as possible.** A premise should be one short sentence. If it runs over ~15 words, you're describing the joke instead of stating it. Cut every word that isn't load-bearing.
- State the abstract comedic logic — *why is this funny*, not a summary of what was said.
- No pronouns tied to the comedian — no "he", "she", "they", "the comic".
- Use the most general form: `"Living in a car technically counts as homeownership."` not `"Living in a RAV4 technically counts as homeownership."`

**Joke type:** one of the eight labels defined in the next section: `misdirect`, `reframe`, `phonetic-match`, `double-meaning`, `what-if`, `analogy`, `elephant-in-the-room`, `prop`. Pick the mechanism that best describes how the joke gets its laugh — the same mechanism the premise formula is built around.

Do not use joke types outside this list. If a joke seems to need a type that is not allowed, choose the closest allowed type and mention the uncertainty in your closing comments.

**Topics:** 1–4 short, specific, searchable nouns per beat. Prefer `"crackheads"` over `"people doing drugs"`.

### Joke types and premise formulas

Most jokes fall into one of these mechanisms. Each has its own premise shape. The value in the `joke_type` field uses the lowercase/hyphenated form shown next to each name.

**Misdirect** (`misdirect`) — assumption planted, then subverted.
> Formula: *X implies Y, not Z.*
> Example:
> - setup: `"My son just came out as trans."`
> - setup: `"Well, shouldn't call him my son anymore."`
> - punchline: `"Now that he's dead to me,"`
> Premise: `"Refusing to call a transitioning child your son implies a new title, not their disownment."`

**Reframe** (`reframe`) — hidden implication of a known thing is surfaced. No prior assumption is planted; the audience just hadn't considered this angle.
> Formula: state the hidden implication directly.
> Example:
> - setup: `"they got him on puberty blockers"`
> - punchline: `"or as pedophiles call them preservatives."`
> - tag: `"Fucking miracle medicine."`
> Premise: `"Pedophiles benefit from puberty blockers."`

**Phonetic match** (`phonetic-match`) — two *different* words sound alike, and both independently fit the context.
> Formula: state the sonic match and why both sides independently fit.
> Example:
> - setup: `"what do you call a little person with ADHD?"`
> - punchline: `"That's right, a fidget."`
> Premise: `"'Midget' and 'fidget' sound alike, and 'fidget' independently fits ADHD."`

**Double-meaning** (`double-meaning`) — the *same* words admit two readings, and the comedian deliberately picks the non-standard one. Hinges on semantic ambiguity, not phonetic similarity.
> Formula: *Taken literally, [phrase] has two meanings.*
> Example:
> - setup: `"'In case of fire, use stairs.'"`
> - punchline: `"Fuck that, let's use water."`
> Premise: `"Taken literally, 'In case of fire, use stairs' has two meanings."`

**What-if** (`what-if`) — a counterfactual scenario is posed and the joke comes from taking it seriously. Distinct from reframe: a reframe surfaces a *real* implication; a what-if *invents* one and runs with it.
> Formula: *What if [counterfactual]?* or state the hypothetical condition directly.
> Example:
> - setup: `"A guy stole my wallet."`
> - setup: `"He's like, ha ha, I have your wallet."`
> - punchline: `"I was like, ha ha, you have 8K of credit card debt."`
> Premise: `"What if stealing a credit card meant you also stole the debt."`

**Analogy** (`analogy`) — two different things are made funny by showing they share the same unexpected structure. The joke often uses "like," "as," "same as," "basically," or "prepared me for," but the comparison word is not required.
> Formula: *X is like Y because both share Z.*
> Example:
> - setup: `"But golfing prepared me for marriage,"`
> - setup: `"cause both involved me spending a lot of money"`
> - punchline: `"at something I'm not really good at."`
> - tag: `"And then waking up the next morning"`
> - tag: `"and deciding to try again, 'cause I like the challenge."`
> Premise: `"Golf is like marriage because both make failure expensive and repeatable."`

**Prop** (`prop`) — the joke depends on a literal object the comedian is using or presenting onstage. The object itself supplies essential setup or payoff, and the joke would not work from spoken text alone. This is rare: if you are unsure whether an object is truly being used as a prop, assume it is not and choose the closest other joke type.
> Formula: *This object reveals or creates [comic meaning].*
> Example:
> - setup: `"[comedian holds up a strange object]"`
> - punchline: `"This is what my dating life has come to."`
> Premise: `"A physical object can stand in for a failed dating life."`

**Elephant-in-the-room** (`elephant-in-the-room`) — taboo observation said aloud. The audience already knows the conclusion; the laugh comes from breaking the silence.
> Formula: *X is widely understood about Y but rarely said aloud.*
> Example:
> - setup: `"You know, these shootings are often done by the same race."`
> - punchline: `"I'm looking at you, honkies."`
> Premise: `"School shootings are widely associated with white shooters but rarely said aloud."`

### Boundary rules

- A new bit starts when the comedian introduces a new standalone premise that doesn't depend on the prior bit.
- A new beat starts when the comedian develops another setup/punchline unit under the current bit's premise.
- Multi-beat bits typically have a shared setup at the start that establishes the umbrella premise, then each beat is a different application of that premise.
- Do not merge separate bits just because they share a broad topic.
- Do not split a bit just because a new setup line appears after a punchline — decide whether it depends on the existing premise.
- Fluff that sits inside a bit's flow can receive that bit's number.
- Stage context can supply setup, but choose the joke type by mechanism. Most "I look like..." jokes are `analogy`, not `prop`.

---

## How to annotate

1. Read the whole set first. Get the joke structure in your head.
2. Identify each punchline — that's the anchor for each beat.
3. Walk backwards from each punchline labeling setup; walk forwards labeling tags.
4. Mark everything else fluff.
5. For each beat, identify the joke type (`misdirect`, `reframe`, `phonetic-match`, `double-meaning`, `what-if`, `analogy`, `elephant-in-the-room`, `prop`) and write a premise using its formula. Record the type in the beat's `joke_type` field. Do not invent other `joke_type` values.
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

### Full annotated set — Ari Mati (Estonia draft)

This set has three bits. Bits 1 and 2 are single-beat, so the premise lives on the beat. Bit 3 is multi-beat — a shared setup establishes "Estonia drafts everyone America excludes" as the umbrella, then four beats each apply that premise to a different group (wheelchair users, down syndrome people, reluctant conscripts, gay soldiers).

```json
{
  "type": "set_meta",
  "video_id": "_vmG4f4EtYo",
  "episode_title": "KT #764 - THEO VON + JELLY ROLL",
  "episode_url": "https://www.youtube.com/watch?v=_vmG4f4EtYo",
  "guests": ["Theo Von", "Jelly Roll"],
  "comedian_name": "Ari Mati",
  "comedian_type": "regular",
  "set_number": 13,
  "start_seconds": 7160,
  "bit_meta": {
    "1": {
      "beats": {
        "1": {
          "premise": "Earning citizenship right before a draft turns the milestone into a curse.",
          "joke_type": "misdirect",
          "topics": ["war", "citizenship", "draft"]
        }
      }
    },
    "2": {
      "beats": {
        "1": {
          "premise": "Expanding draft eligibility to older stoners produces a pathetic army.",
          "joke_type": "reframe",
          "topics": ["draft age", "marijuana convictions", "army"]
        }
      }
    },
    "3": {
      "premise": "Estonia drafts everyone America excludes.",
      "beats": {
        "1": {
          "premise": "Wheelchair soldiers with a grenade could kamikaze roll at the enemy.",
          "joke_type": "what-if",
          "topics": ["Estonia", "wheelchairs", "grenades"]
        },
        "2": {
          "premise": "'Special forces' fits literally when the soldiers are special-needs.",
          "joke_type": "double-meaning",
          "topics": ["special forces", "down syndrome", "wordplay"]
        },
        "3": {
          "premise": "Telling a down syndrome person someone killed Santa would make them mad.",
          "joke_type": "reframe",
          "topics": ["Santa Claus", "down syndrome", "conscription"]
        },
        "4": {
          "premise": "Without women in the military, straight soldiers would protect gay soldiers.",
          "joke_type": "reframe",
          "topics": ["gay soldiers", "base life", "military"]
        }
      }
    }
  },
  "lines": [
    {"text": "Are we doing good?", "label": "setup", "bit": 1, "beat": 1, "line_number": 3336, "start": 7160},
    {"text": "You shouldn't.", "label": "punchline", "bit": 1, "beat": 1, "line_number": 3338, "start": 7164},
    {"text": "The war is coming!", "label": "tag", "bit": 1, "beat": 1, "line_number": 3340, "start": 7168},
    {"text": "Fuck!", "label": "fluff", "bit": 1, "beat": 1, "line_number": 3341, "start": 7173},
    {"text": "Just my luck.", "label": "setup", "bit": 1, "beat": 1, "line_number": 3342, "start": 7175},
    {"text": "As soon as I get citizenship,", "label": "setup", "bit": 1, "beat": 1, "line_number": 3343, "start": 7178},
    {"text": "drafted.", "label": "punchline", "bit": 1, "beat": 1, "line_number": 3344, "start": 7180},
    {"text": "Just yesterday you guys know that America raised its age limit", "label": "setup", "bit": 2, "beat": 1, "line_number": 3345, "start": 7193},
    {"text": "to 42 for the draft and prior marijuana convictions don't matter.", "label": "setup", "bit": 2, "beat": 1, "line_number": 3346, "start": 7197},
    {"text": "Wow what an army you're building.", "label": "punchline", "bit": 2, "beat": 1, "line_number": 3347, "start": 7205},
    {"text": "Some fourty-year-old losers.", "label": "tag", "bit": 2, "beat": 1, "line_number": 3348, "start": 7208},
    {"text": "You know in Estonia we don't have any limits. We have compulsory military service.", "label": "setup", "bit": 3, "beat": 1, "line_number": 3349, "start": 7215},
    {"text": "We're too small to pick.", "label": "setup", "bit": 3, "beat": 1, "line_number": 3350, "start": 7226},
    {"text": "Everyone goes.", "label": "punchline", "bit": 3, "beat": 1, "line_number": 3351, "start": 7228},
    {"text": "Wheelchair people, we send them.", "label": "setup", "bit": 3, "beat": 1, "line_number": 3352, "start": 7231},
    {"text": "Oh yeah, we put a grenade in your lap and...", "label": "setup", "bit": 3, "beat": 1, "line_number": 3353, "start": 7234},
    {"text": "Come on!", "label": "punchline", "bit": null, "beat": null, "line_number": 3355, "start": 7239},
    {"text": "Down syndrome people, we send them.", "label": "setup", "bit": 3, "beat": 2, "line_number": 3356, "start": 7246},
    {"text": "Oh yeah, we have a whole squad.", "label": "setup", "bit": 3, "beat": 2, "line_number": 3357, "start": 7250},
    {"text": "Estonian special forces.", "label": "punchline", "bit": 3, "beat": 2, "line_number": 3358, "start": 7252},
    {"text": "You think special forces mean somebody repels down", "label": "setup", "bit": 3, "beat": 2, "line_number": 3360, "start": 7261},
    {"text": "and has night vision knives,", "label": "setup", "bit": 3, "beat": 2, "line_number": 3361, "start": 7263},
    {"text": "Nicholas with a soft serve ice cream?", "label": "punchline", "bit": 3, "beat": 2, "line_number": 3362, "start": 7266},
    {"text": "We send them!", "label": "tag", "bit": 3, "beat": 2, "line_number": 3364, "start": 7274},
    {"text": "We get them all together in a parking lot,", "label": "setup", "bit": 3, "beat": 3, "line_number": 3365, "start": 7276},
    {"text": "we connect them with a rope.", "label": "setup", "bit": 3, "beat": 3, "line_number": 3366, "start": 7278},
    {"text": "We look them in the eyes and we tell them,", "label": "setup", "bit": 3, "beat": 3, "line_number": 3368, "start": 7283},
    {"text": "Listen, they killed Santa Claus.", "label": "punchline", "bit": 3, "beat": 3, "line_number": 3369, "start": 7284},
    {"text": "Everybody goes!", "label": "tag", "bit": 3, "beat": 3, "line_number": 3371, "start": 7296},
    {"text": "Cripples, mentally challenged, even women.", "label": "tag", "bit": 3, "beat": 3, "line_number": 3372, "start": 7298},
    {"text": "Gay people, we send them.", "label": "setup", "bit": 3, "beat": 4, "line_number": 3374, "start": 7308},
    {"text": "I know you guys don't do that.", "label": "fluff", "bit": 3, "beat": 4, "line_number": 3375, "start": 7311},
    {"text": "By the way, the only way I'm going to war is if I have a gay squad mate.", "label": "setup", "bit": 3, "beat": 4, "line_number": 3376, "start": 7313},
    {"text": "I'm protecting that motherfucker more than the medic.", "label": "setup", "bit": 3, "beat": 4, "line_number": 3377, "start": 7320},
    {"text": "He's the only one sucking dick back at the base.", "label": "punchline", "bit": 3, "beat": 4, "line_number": 3378, "start": 7324},
    {"text": "Dylan get behind me!", "label": "tag", "bit": 3, "beat": 4, "line_number": 3379, "start": 7328},
    {"text": "I'm saving Dylan's life.", "label": "tag", "bit": 3, "beat": 4, "line_number": 3380, "start": 7331},
    {"text": "No faggot left behind.", "label": "tag", "bit": 3, "beat": 4, "line_number": 3381, "start": 7334},
    {"text": "Thank you so much. That's my time.", "label": "fluff", "bit": null, "beat": null, "line_number": 3382, "start": 7339}
  ]
}
```
