# Kill Tony Set Annotation Prompt

You are annotating stand-up **sets** from *Kill Tony* in a single pass: labeling every line and grouping lines into bits and beats simultaneously.

Annotate only the files you are explicitly given — do not process any files beyond those listed. Read and edit files one at a time, never in bulk. always run 3. Run python manage.py import_sets after each file so you know if you made any mistakes. Do not build any helper tools, do each annotation manually.

---

## Input

Each input file is a set JSON from `pipeline/data/2_set_inbox/`. Lines have an empty `label` field:

---

## Output

Write the annotated file to `pipeline/data/3_bit_annotated_set_inbox/<same-filename>.json`. The output adds `bit_meta` before `lines`, and each line gets `label`, `bit`, and `beat` fields.

Every beat has its own `premise`, `joke_type`, joke-type-specific premise fields, and `keys`. A bit gets a `summary` **only when it has more than one beat**. The summary is a **short as possible** umbrella description of the shared frame that makes those beats belong together. Single-beat bits must not have a summary because the beat premise already explains the whole bit.

After writing, delete the source file from `pipeline/data/2_set_inbox/`.

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
- **Beat**: one setup/punchline/tags unit with its own specific comedic logic. Every beat must contain at least one `punchline` line.

### Bit numbers and beat numbers

Use sequential integers starting from 1. Assign `"bit": N` and `"beat": N` on every `punchline` line.

Set every `setup`, `tag`, and `fluff` line to `"bit": null, "beat": null`.

The import pipeline infers non-punchline ownership:
- A `setup` belongs to the next `punchline`.
- A `tag` belongs to the most recent `punchline` or `tag`.
- A `fluff` line stays null unless it falls inside a bit or beat span created by setup/punchline/tag lines.

### Bit vs. multiple bits

**Shared subject matter does not equal shared premise.** Don't group beats just because they're about the same subject. Group them only when removing one would orphan the others.

The test: **can you extract a beat alone and still have it make sense?**
- If yes → it's its own bit
- If no (it depends on a premise established earlier) → same bit

**Watch for pronoun bridges.** If a comedian links two structurally independent jokes by using a pronoun callback (e.g. "him" referring to someone established in the prior joke), they are still separate bits. The test is whether the joke's comedic premise would survive a one-word change ("him" → "my son"), not whether the current performance depends on the prior line.

### `bit_meta`

> **IMPORTANT:** `bit_meta` MUST be a JSON object keyed by bit number as a string (e.g. `"1"`, `"2"`), NOT a JSON array. `beats` within each bit must also be a JSON object keyed by beat number as a string. Never use `[...]` for `bit_meta` or `beats`.

Every beat has `premise`, `joke_type`, the required fields for that joke type, and `keys`. A bit has a `summary` **only when it has multiple beats**. Single-beat bits must not have `summary`.

For multi-beat bits, every beat must still have its own premise. The bit summary is the broad shared frame; each beat premise is the specific comedic mechanism of that beat.

**Premise rules:**
- **Hard limit: 20 words maximum.** If your premise exceeds 20 words, you are describing the joke rather than stating its mechanism. Count the words and cut until you are at or under 20. Every word must be load-bearing.
- State the abstract comedic logic - *why is this funny*, not a summary of what was said.
- No pronouns tied to the comedian - no "he", "she", "they", "the comic".
- Use the most general form: `"Living in a car technically counts as homeownership."` not `"Living in a RAV4 technically counts as homeownership."`
- Build the premise from the required fields plus that joke type's formula words. Do not add extra explanation words.
- After writing the premise, copy those same field values into the beat JSON. The field values are the source of the premise.

**Joke type:** one of the nine accepted labels defined in the next section: `misdirect`, `reframe`, `phonetic-match`, `double-meaning`, `contradiction`, `analogy`, `hyperbole`, `elephant-in-the-room`, `anti-humor`. Pick the mechanism that best describes how the joke gets its laugh - the same mechanism the premise formula is built around.

Do not use joke types outside this list. If a joke seems to need a type that is not allowed, choose the closest allowed type and mention the uncertainty in your closing comments.

For every specific token in the setup, ask: swap it for another member of a broader class — does the joke still land via the identical mechanism? If yes, replace
the token with the class. Repeat until the next swap up would break the joke. Duck→cow→horse all survive → animal. Beak-rash→foot-cream survive → medicine.

When multiple joke types seem plausible, use this priority order:

1. If the laugh depends on sound similarity, use `phonetic-match`.
2. If the laugh depends on semantic ambiguity, use `double-meaning`.
3. If the laugh depends on a joke form refusing to deliver a clever payoff, use `anti-humor`.
4. If the laugh depends on expectation reversal, use `misdirect`.
5. If the laugh depends on a claim conflicting with evidence, use `contradiction`.
6. If the laugh depends on comparison, use `analogy`.
7. If the laugh depends on reinterpretation without comparison, use `reframe`.
8. If the laugh depends on absurd degree, use `hyperbole`.
9. If the laugh depends mainly on saying a taboo truth aloud, use `elephant-in-the-room`.

**Keys:** 1-4 short, specific, searchable nouns or noun phrases per beat. Keys are chosen last from the premise fields, never directly from the transcript. Prefer `"crackheads"` over `"people doing drugs"`.

Key source rules:
- `analogy`: copy `a`, `b`, and the core searchable phrase from `shared`. If `shared` begins with a helper verb like "involve", omit that helper verb from the key.
- `hyperbole`: copy `subject` and `extreme`. The `extreme` must be the shortest phrase that preserves the exaggerated endpoint.
- `phonetic-match`: copy `heard`; also copy `reason` when present; exclude `reheard`.
- `double-meaning`: copy `phrase`; exclude `senses`.
- `contradiction`: pick concrete nouns from `subject`, `a`, and `b`.
- `reframe`: pick concrete nouns from `subject` and `reframe`.
- `misdirect`: pick concrete nouns from `bait`; exclude `implication` and `reveal`.
- `elephant-in-the-room`: pick concrete nouns from `elephant`.
- `anti-humor`: pick concrete nouns from `frame`; exclude `answer`.


### Joke types and premise formulas

All jokes must be assigned one of these types. **The way you write each beat premise must exactly match the formula given for its joke type. VERY IMPORTANT**

After writing the premise, include the required field keys shown for that joke type. Field values must be the same distilled wording used in the premise.

**misdirect** - an assumption is planted, then subverted.
Fields: `bait`, `implication`, `reveal`.
Formula: *[bait] implies [implication], but reveals [reveal].*
Required phrase markers: `implies`, `but reveals`.

Example:
- setup: `"My son just came out as trans."`
- setup: `"Well, shouldn't call him my son anymore."`
- punchline: `"Now that he's dead to me,"`

Premise: `"Refusing to call a transitioning child your son implies a new title, but reveals disownment."`
JSON fields: `{ "premise": "Refusing to call a transitioning child your son implies a new title, but reveals disownment.", "joke_type": "misdirect", "bait": "refusing to call a transitioning child your son", "implication": "a new title", "reveal": "disownment", "keys": ["transitioning child"] }`

**reframe** - a known thing is given a newly visible interpretation. No false assumption is planted and no wording ambiguity is required; the joke surfaces an alternate perspective to understand the same fact, object, behavior, or situation.
Fields: `subject`, `reframe`.
Formula: *[subject] could be [reframe].*
Required phrase marker: `could be`.

Example:
- setup: `"they got him on puberty blockers"`
- punchline: `"or as pedophiles call them preservatives."`
- tag: `"Fucking miracle medicine."`

Premise: `"Puberty blockers could be beneficial to pedophiles."`
JSON fields: `{ "premise": "Puberty blockers could be beneficial to pedophiles.", "joke_type": "reframe", "subject": "puberty blockers", "reframe": "beneficial to pedophiles", "keys": ["puberty blockers", "pedophiles"] }`

**phonetic-match** - two *different* words sound alike. Often both fit the context, but sometimes the resemblance alone is the joke.
Fields: `heard`, `reheard`, optional `reason`.
Formula without reason: *"[heard]" sounds like "[reheard]".*
Formula with reason: *"[heard]" sounds like "[reheard]", and "[reheard]" fits because [reason].*
Required phrase marker: `sounds like`. Add `fits because` only when `reason` is present.

Example:
- setup: `"what do you call a little person with ADHD?"`
- punchline: `"That's right, a fidget."`

Premise: `"'Midget' sounds like 'fidget', and 'fidget' fits because ADHD."`
JSON fields: `{ "premise": "'Midget' sounds like 'fidget', and 'fidget' fits because ADHD.", "joke_type": "phonetic-match", "heard": "midget", "reheard": "fidget", "reason": "ADHD", "keys": ["midget", "ADHD"] }`

**double-meaning** - the *same* word or phrase admits two or more readings, and the comedian deliberately picks the non-standard one. Hinges on semantic ambiguity, not phonetic similarity.
Fields: `phrase`, `senses`.
Formula: *"[phrase]" can mean [sense 1] or [sense 2].*
Required phrase markers: `can mean`, `or`.

Example:
- setup: `"'In case of fire, use stairs.'"`
- punchline: `"Fuck that, let's use water."`

Premise: `"'Use stairs' can mean take the stairs or use stairs as the tool."`
JSON fields: `{ "premise": "'Use stairs' can mean take the stairs or use stairs as the tool.", "joke_type": "double-meaning", "phrase": "use stairs", "senses": ["take the stairs", "use stairs as the tool"], "keys": ["use stairs"] }`

**contradiction** - one subject holds two positions that cannot both be true; the joke is the hypocrisy or exposed inconsistency.
Fields: `subject`, `a`, `b`.
Formula: *[subject] both [a] and yet [b].*
Required phrase markers: `both`, `and yet`.

Example:
- setup: `"My girlfriend thinks the godfather is too long,"`
- setup: `"But her story about when her coworker was bitchy to her two years ago is..."`
- punchline: `"the perfect length."`

Premise: `"Women both find good movies too long and yet tell long stories."`
JSON fields: `{ "premise": "Women both find good movies too long and yet tell long stories.", "joke_type": "contradiction", "subject": "women", "a": "find good movies too long", "b": "tell long stories", "keys": ["women", "good movies", "long stories"] }`

**analogy**  - two different things are made funny by showing they share the same unexpected structure. The joke often uses "like," "as," "same as," "basically," or "prepared me for," but the comparison word is not required.
Fields: `a`, `b`, `shared`.
Formula: *[X] is like [Y] because both [shared structure].*
Required phrase markers: `is like`, `because both`.

Example:
- setup: `"But golfing prepared me for marriage,"`
- setup: `"cause both involved me spending a lot of money"`
- punchline: `"at something I'm not really good at."`
- tag: `"And then waking up the next morning"`
- tag: `"and deciding to try again, 'cause I like the challenge."`

Premise: `"Golf is like marriage because both involve expensive repeated failure."`
JSON fields: `{ "premise": "Golf is like marriage because both involve expensive repeated failure.", "joke_type": "analogy", "a": "golf", "b": "marriage", "shared": "expensive repeated failure", "keys": ["golf", "marriage", "expensive repeated failure"] }`

**hyperbole** - one dimension of a subject is stretched past plausibility. The laugh comes from excess degree, scale, or intensity.
Fields: `subject`, `extreme`.
Formula: *[subject] becomes so extreme that [extreme].*
Required phrase marker: `becomes so extreme that`.

Example:
- setup: `"So I've already seen a third of this collection"`
- setup: `"and I don't have enough bodily fluids"`
- punchline: `"for the other two thirds of this collection."`

Premise: `"A porn collection becomes so extreme that you run out of sperm."`
JSON fields: `{ "premise": "A porn collection becomes so extreme that you run out of sperm.", "joke_type": "hyperbole", "subject": "a porn collection", "extreme": "running out of sperm", "keys": ["porn collection", "running out of sperm"] }`

**elephant-in-the-room** - a taboo or socially avoided observation is said aloud. The audience already recognizes the conclusion; the laugh comes from breaking the silence.
Fields: `elephant`.
Formula: *[elephant] is widely understood but rarely said aloud.*
Required phrase markers: `widely understood`, `but rarely`.

Example:
- setup: `"You know, these shootings are often done by the same race."`
- punchline: `"I'm looking at you, honkies."`

Premise: `"White men dominate mass shootings is widely understood but rarely said aloud."`
JSON fields: `{ "premise": "White men dominate mass shootings is widely understood but rarely said aloud.", "joke_type": "elephant-in-the-room", "elephant": "white men dominate mass shootings", "keys": ["white men", "mass shootings"] }`

**anti-humor** - a joke form promises a payoff, then delivers the banal truth; the joke is that there is no joke.
Fields: `frame`, `answer`.
Formula: *[frame] implies a punchline, but reveals only [answer].*
Required phrase marker: `implies a punchline, but reveals only`.

Example:
- setup: `"A duck walks into a pharmacy with a rash on his beak."`
- setup: `"He asks the pharmacist for some ointment."`
- punchline: `"Sorry, we don't have medicine for ducks here."`

Premise: `"An animal asking a business for service implies a punchline, but reveals only that the business does not serve animals."`
JSON fields: `{ "premise": "An animal asking a business for service implies a punchline, but reveals only that the business does not serve animals.", "joke_type": "anti-humor", "frame": "an animal asking a business for service", "answer": "that the business does not serve animals", "keys": ["animal", "business"] }`

### Boundary rules

- A bit is the smallest standalone segment of material that can be lifted out of the set and still make sense as its own joke sequence. 
- A new beat starts at the first setup line following a punchline.
- Multi-beat bits typically have a shared setup at the start that establishes the umbrella premise, then each beat is a different application of that premise.
- Do not merge separate bits just because they share broad subject matter.
- Set all setup, tag, and fluff lines to `"bit": null, "beat": null`; the import pipeline normalises them from punchline anchors.
- Stage context can supply setup, but choose the joke type by mechanism. Most "I look like..." jokes are `analogy`, not `prop`.
- Do not use `act-out` as the `joke_type`. If a transcript includes embodied performance, choose the underlying text-visible mechanism.

---

## How to annotate

1. Read the whole set first. Get the joke structure in your head.
2. Identify each punchline — that's the anchor for each beat.
3. Walk backwards from each punchline labeling setup; walk forwards labeling tags.
4. Mark everything else fluff.
5. For each beat, identify the joke type (`misdirect`, `reframe`, `phonetic-match`, `double-meaning`, `contradiction`, `analogy`, `hyperbole`, `elephant-in-the-room`, `anti-humor`) and write a premise using its formula. Record the type in the beat's `joke_type` field. Do not invent other `joke_type` values.
6. Add the required field keys for that joke type using the same distilled wording from the premise.
7. Choose keys last from the allowed premise fields for that joke type.
8. Group beats into bits by shared premise. Apply the extraction test: if a beat would survive standalone, it's its own bit.
9. For multi-beat bits, write a short `summary` that captures the shared frame. Do not add `summary` to single-beat bits.
10. Write the output JSON with `bit_meta`, fully labeled lines, and bit/beat numbers only on punchlines.

---

## Process checklist

1. Process only the files you were given. 
2. For each file:
   - Read the whole set.
   - Annotate: label every line, assign bit/beat numbers to punchlines, write bit_meta.
   - Write the output to `pipeline/data/3_bit_annotated_set_inbox/<same-filename>.json`.
   - Delete the source file from `pipeline/data/2_set_inbox/`.
3. Run python manage.py import_sets. This is **VERY IMPORTANT** it helps you learn from any mistakes you may have made. 
4. Move to the next file. Repeat until all given files are done.

---

## Examples

### Full annotated set — Ari Mati (Estonia draft)

This set has three bits. Bits 1 and 2 are single-beat, so the premise lives only on the beat. Bit 3 is multi-beat, so it has a summary: "Estonia drafts everyone America excludes." The beats each apply that shared frame to a different group (wheelchair users, down syndrome people, reluctant conscripts, gay soldiers).

```json
{
  "type": "set_meta",
  "video_id": "_vmG4f4EtYo",
  "episode_title": "KT #764 - THEO VON + JELLY ROLL",
  "episode_url": "https://www.youtube.com/watch?v=_vmG4f4EtYo",
  "guests": ["Theo Von", "Jelly Roll"],
  "comedian_name": "Ari Mati",
  "comedian_type": "regular",
  "start_seconds": 7160,
  "bit_meta": {
    "1": {
      "beats": {
        "1": {
          "premise": "Earning citizenship implies a personal milestone, but the timing reveals it as a draft sentence.",
          "joke_type": "misdirect",
          "bait": "earning citizenship",
          "implication": "a personal milestone",
          "reveal": "a draft sentence",
          "keys": ["citizenship"]
        }
      }
    },
    "2": {
      "beats": {
        "1": {
          "premise": "Expanding draft eligibility to middle-aged stoners could be the worst army ever assembled.",
          "joke_type": "reframe",
          "subject": "expanding draft eligibility to middle-aged stoners",
          "reframe": "the worst army ever assembled",
          "keys": ["draft eligibility", "middle-aged stoners", "army"]
        }
      }
    },
    "3": {
      "summary": "Estonia drafts everyone America excludes.",
      "beats": {
        "1": {
          "premise": "Wheelchair soldiers with a grenade could be terrifying.",
          "joke_type": "reframe",
          "subject": "wheelchair soldiers with a grenade",
          "reframe": "kamikaze rollers",
          "keys": ["wheelchair soldiers", "grenades"]
        },
        "2": {
          "premise": "'Special forces' can mean elite operatives or literally special-needs soldiers.",
          "joke_type": "double-meaning",
          "phrase": "special forces",
          "senses": ["elite operatives", "literally special-needs soldiers"],
          "keys": ["special forces"]
        },
        "3": {
          "premise": "A dead Santa lie could be the most effective conscription tool for special-needs soldiers.",
          "joke_type": "reframe",
          "subject": "a dead Santa lie",
          "reframe": "the most effective conscription tool for special-needs soldiers",
          "keys": ["Santa", "conscription", "special-needs soldiers"]
        },
        "4": {
          "premise": "A gay soldier could be the best-protected person on base among sex-starved straight men.",
          "joke_type": "reframe",
          "subject": "a gay soldier",
          "reframe": "the best-protected person on base among sex-starved straight men",
          "keys": ["gay soldier", "base", "straight men"]
        }
      }
    }
  },
  "lines": [
    {"text": "Are we doing good?", "label": "setup", "bit": null, "beat": null, "line_number": 3336, "start": 7160},
    {"text": "You shouldn't.", "label": "punchline", "bit": 1, "beat": 1, "line_number": 3338, "start": 7164},
    {"text": "The war is coming!", "label": "tag", "bit": null, "beat": null, "line_number": 3340, "start": 7168},
    {"text": "Fuck!", "label": "fluff", "bit": null, "beat": null, "line_number": 3341, "start": 7173},
    {"text": "Just my luck.", "label": "setup", "bit": null, "beat": null, "line_number": 3342, "start": 7175},
    {"text": "As soon as I get citizenship,", "label": "setup", "bit": null, "beat": null, "line_number": 3343, "start": 7178},
    {"text": "drafted.", "label": "punchline", "bit": 1, "beat": 1, "line_number": 3344, "start": 7180},
    {"text": "Just yesterday you guys know that America raised its age limit", "label": "setup", "bit": null, "beat": null, "line_number": 3345, "start": 7193},
    {"text": "to 42 for the draft and prior marijuana convictions don't matter.", "label": "setup", "bit": null, "beat": null, "line_number": 3346, "start": 7197},
    {"text": "Wow what an army you're building.", "label": "punchline", "bit": 2, "beat": 1, "line_number": 3347, "start": 7205},
    {"text": "Some fourty-year-old losers.", "label": "tag", "bit": null, "beat": null, "line_number": 3348, "start": 7208},
    {"text": "You know in Estonia we don't have any limits. We have compulsory military service.", "label": "setup", "bit": null, "beat": null, "line_number": 3349, "start": 7215},
    {"text": "We're too small to pick.", "label": "setup", "bit": null, "beat": null, "line_number": 3350, "start": 7226},
    {"text": "Everyone goes.", "label": "punchline", "bit": 3, "beat": 1, "line_number": 3351, "start": 7228},
    {"text": "Wheelchair people, we send them.", "label": "setup", "bit": null, "beat": null, "line_number": 3352, "start": 7231},
    {"text": "Oh yeah, we put a grenade in your lap and...", "label": "setup", "bit": null, "beat": null, "line_number": 3353, "start": 7234},
    {"text": "Come on!", "label": "punchline", "bit": 3, "beat": 1, "line_number": 3355, "start": 7239},
    {"text": "Down syndrome people, we send them.", "label": "setup", "bit": null, "beat": null, "line_number": 3356, "start": 7246},
    {"text": "Oh yeah, we have a whole squad.", "label": "setup", "bit": null, "beat": null, "line_number": 3357, "start": 7250},
    {"text": "Estonian special forces.", "label": "punchline", "bit": 3, "beat": 2, "line_number": 3358, "start": 7252},
    {"text": "You think special forces mean somebody repels down", "label": "setup", "bit": null, "beat": null, "line_number": 3360, "start": 7261},
    {"text": "and has night vision knives,", "label": "setup", "bit": null, "beat": null, "line_number": 3361, "start": 7263},
    {"text": "Nicholas with a soft serve ice cream?", "label": "punchline", "bit": 3, "beat": 2, "line_number": 3362, "start": 7266},
    {"text": "We send them!", "label": "tag", "bit": null, "beat": null, "line_number": 3364, "start": 7274},
    {"text": "We get them all together in a parking lot,", "label": "setup", "bit": null, "beat": null, "line_number": 3365, "start": 7276},
    {"text": "we connect them with a rope.", "label": "setup", "bit": null, "beat": null, "line_number": 3366, "start": 7278},
    {"text": "We look them in the eyes and we tell them,", "label": "setup", "bit": null, "beat": null, "line_number": 3368, "start": 7283},
    {"text": "Listen, they killed Santa Claus.", "label": "punchline", "bit": 3, "beat": 3, "line_number": 3369, "start": 7284},
    {"text": "Everybody goes!", "label": "tag", "bit": null, "beat": null, "line_number": 3371, "start": 7296},
    {"text": "Cripples, mentally challenged, even women.", "label": "tag", "bit": null, "beat": null, "line_number": 3372, "start": 7298},
    {"text": "Gay people, we send them.", "label": "setup", "bit": null, "beat": null, "line_number": 3374, "start": 7308},
    {"text": "I know you guys don't do that.", "label": "fluff", "bit": null, "beat": null, "line_number": 3375, "start": 7311},
    {"text": "By the way, the only way I'm going to war is if I have a gay squad mate.", "label": "setup", "bit": null, "beat": null, "line_number": 3376, "start": 7313},
    {"text": "I'm protecting that motherfucker more than the medic.", "label": "setup", "bit": null, "beat": null, "line_number": 3377, "start": 7320},
    {"text": "He's the only one sucking dick back at the base.", "label": "punchline", "bit": 3, "beat": 4, "line_number": 3378, "start": 7324},
    {"text": "Dylan get behind me!", "label": "tag", "bit": null, "beat": null, "line_number": 3379, "start": 7328},
    {"text": "I'm saving Dylan's life.", "label": "tag", "bit": null, "beat": null, "line_number": 3380, "start": 7331},
    {"text": "No faggot left behind.", "label": "tag", "bit": null, "beat": null, "line_number": 3381, "start": 7334},
    {"text": "Thank you so much. That's my time.", "label": "fluff", "bit": null, "beat": null, "line_number": 3382, "start": 7339}
  ]
}
```
