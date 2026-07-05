# Kill Tony Set Annotation Prompt

You are annotating stand-up **sets** from *Kill Tony*. Many jokes you will see will be funny. Many will not be funny at all. It is not our job as annotators to judge. It's our job to try and figure out the intented funny of the joke as honestly as possible.

## Input

Each input file is a set JSON from `pipeline/data/set_inbox/`. 

## Output

Write the annotated file back to `pipeline/data/set_inbox/<same-filename>.json`, overwriting the unannotated source. The output adds `bit_meta` before `lines`, and each line gets `label`, `bit`, and `beat` fields.

Every beat has its own `premise` and `joke_type`.

## Line Labels

### `setup`
A line that establishes premise, scenario, observation, or context for a joke — building toward the laugh without delivering it.

### `punchline`
The line where the laugh lands. The reveal, twist, or payoff the setup was building toward.

### `tag`
An additional payoff in the same beat, riding on the laugh already in the room rather than a premise of its own. A tag can carry its own `setup`: a setup line followed by a tag belongs to the current beat, while a setup line followed by a punchline starts a new beat. So `punchline → setup → tag → setup → tag` is a single valid beat.

### `fluff`
Everything that is not setup, punchline, or tag: greetings, sign-offs, name introductions, verbal stumbles (`"Uh..."`), audio events (`"[squeals]"`), and crowd-acknowledgement filler (`"Hell yeah."`) that isn't doing comedic work.

## Labeling Rules

- **One punchline per beat.** If two adjacent lines both look like punchlines, one is probably a tag or setup. Exception: a transcription split across two lines can have two consecutive punchline labels.
- **A tag only exists after a punchline.** The beat's first payoff is the `punchline`; every later payoff is a `tag`. All a tag requires is a punchline earlier in the beat — a `setup` it rides, or crowd `fluff`, may sit between them.
- **A setup's beat is decided by what follows it.** A `setup` followed by a `tag` joins the current beat; a `setup` followed by a `punchline` starts a new one.
- **Sound effects are fluff.** `[squeals]`, `[music]`, etc.
- **Self-introductions are fluff** unless the name itself is the punchline.
- **Closers are fluff.** `"That's my time."`, `"Thank you guys."`
- **Misdirects turn on the frame-flip line.** Label the line where the audience realizes its assumption was wrong as the punchline.

## Bit and Beat Structure

### Hierarchy

- **Bit**: one or more beats that share a premise. Every bit has at least one beat.
- **Beat**: one setup/punchline/tags unit with its own specific comedic logic. Every beat must contain at least one `punchline` line.

### Bit numbers and beat numbers

Use sequential integers starting from 1. Assign `"bit": N` and `"beat": N` on every `punchline` line.

Set every `setup`, `tag`, and `fluff` line to `"bit": null, "beat": null`.

The import pipeline infers non-punchline ownership:
- A `setup` belongs to the next payoff line: if that payoff is a `tag`, the setup joins the current beat; if it is a `punchline`, the setup opens the new beat.
- A `tag` belongs to the most recent `punchline` or `tag`.
- A `fluff` line stays null unless it falls inside a bit or beat span created by setup/punchline/tag lines.

### Bit vs. multiple bits

**Shared subject matter does not equal shared premise.** Don't group beats just because they're about the same subject. Group them only when removing one would orphan the others.

The test: **can you extract a beat alone and still have it make sense?**
- If yes → it's its own bit
- If no (it depends on a premise established earlier) → same bit

**Watch for pronoun bridges.** If a comedian links two structurally independent jokes by using a pronoun callback (e.g. "him" referring to someone established in the prior joke), they are still separate bits. The test is whether the joke's comedic premise would survive a one-word change ("him" → "my son").

### `bit_meta`

> **IMPORTANT:** `bit_meta` MUST be a JSON object keyed by bit number as a string (e.g. `"1"`, `"2"`), NOT a JSON array. `beats` within each bit must also be a JSON object keyed by beat number as a string. Never use `[...]` for `bit_meta` or `beats`.

Every beat has `premise` and `joke_type`.

**Premise rules:**
- **Hard limit: 20 words maximum.** If your premise exceeds 20 words, you are describing the joke rather than 
stating its mechanism. Count the words and cut until you are at or under 20. Every word must be load-bearing.
- State the abstract comedic logic - *why is this funny*, not a recap of what was said.
- No pronouns tied to the comedian - no "he", "she", "they", "the comic".
- Use the most general form: `"Living in a car technically counts as homeownership."` not `"Living in a RAV4 technically counts as homeownership."`
- Build the premise using that joke type's formula.

For every specific token in the setup, ask: swap it for another member of a broader class — does the joke still land via the identical mechanism? If yes, replace the token with the class. Repeat until the next swap up would break the joke. Duck→cow→horse all survive → animal. Beak-rash→foot-cream survive → medicine.

### Joke types and premise formulas

All jokes must be assigned one of these types. **The way you write each beat premise must exactly match the formula given for its joke type. VERY IMPORTANT**

**misdirect** - an assumption is planted, then subverted. The setup steers you toward a specific conclusion; the punchline reveals it was wrong, and you *replace* your first reading with the real one — you were meant to be fooled. If your first reading of the setup is still true after the punchline and you've merely gained a new angle, it is a `reframe`, not a misdirect.
Formula: *[bait] implies [implication], but reveals [reveal].*
Required phrase markers: `implies`, `but reveals`.

Example:
- setup: `"My son just came out as trans."`
- setup: `"Well, shouldn't call him my son anymore."`
- punchline: `"Now that he's dead to me,"`

JSON fields: `{ "premise": "Refusing to call a transitioning child your son implies a new title, but reveals disownment.", "joke_type": "misdirect" }`

**reframe** - a known thing is given a newly visible interpretation. No false assumption is planted and no wording ambiguity is required: the setup is a plain, true statement, and the punchline overlays a second, equally-true way to see the same fact, object, behavior, or situation. Your first reading stays true — the joke *adds* an angle rather than replacing one. If the punchline instead makes your first reading wrong, it is a `misdirect`.
Formula: *[subject] could be [reframe].*
Required phrase marker: `could be`.

Example:
- setup: `"they got him on puberty blockers"`
- punchline: `"or as pedophiles call them preservatives."`

JSON fields: `{ "premise": "Puberty blockers could be beneficial to pedophiles.", "joke_type": "reframe" }`

**phonetic-match** - two *different* words sound alike. Often both fit the context, but sometimes the resemblance alone is the joke.
Formula without reason: *"[heard]" sounds like "[reheard]".*
Formula with reason: *"[heard]" sounds like "[reheard]", and "[reheard]" fits because [reason].*
Required phrase marker: `sounds like`. Add `fits because` only when a reason is present.

Example:
- setup: `"what do you call a little person with ADHD?"`
- punchline: `"That's right, a fidget."`

JSON fields: `{ "premise": "'Midget' sounds like 'fidget', and 'fidget' fits because ADHD.", "joke_type": "phonetic-match" }`

**double-meaning** - the *same* word or phrase admits two or more readings. Hinges on semantic ambiguity, not phonetic similarity. The ambiguous word or phrase must be preserved exactly from the transcript. Do not generalize, paraphrase, shorten, or clean it up unless removing surrounding non-ambiguous words leaves the same complete ambiguity intact.
Formula: *"[phrase]" can mean [expected] or [comic].*
Required phrase markers: `can mean`, `or`.

Example:
- setup: `"'In case of fire, use stairs.'"`
- punchline: `"Fuck that, let's use water."`

JSON fields: `{ "premise": "'In case of fire, use stairs' can mean use stairs during a fire or use stairs to fight a fire.", "joke_type": "double-meaning" }`

**contradiction** - one subject holds two positions that cannot both be true; the joke is the hypocrisy or exposed inconsistency.
Formula: *[subject] both [a] and yet [b].*
Required phrase markers: `both`, `and yet`.

Example:
- setup: `"My girlfriend thinks the godfather is too long,"`
- setup: `"But her story about when her coworker was bitchy to her two years ago is..."`
- punchline: `"the perfect length."`

JSON fields: `{ "premise": "Women both find good movies too long and yet tell long stories.", "joke_type": "contradiction" }`

**analogy**  - two different things are made funny by showing they share the same unexpected structure. The joke often uses "like," "as," "same as," "basically," or "prepared me for," but the comparison word is not required. Common for "looks like" roast type jokes.
Formula: *[X] is like [Y] because both [shared structure].*
Required phrase markers: `is like`, `because both`.

Example:
- setup: `"But golfing prepared me for marriage,"`
- setup: `"cause both involved me spending a lot of money"`
- punchline: `"at something I'm not really good at."`
- setup: `"And then waking up the next morning"`
- tag: `"and deciding to try again, 'cause I like the challenge."`

JSON fields: `{ "premise": "Golf is like marriage because both involve expensive repeated failure.", "joke_type": "analogy" }`

**hyperbole** - one dimension of a subject is stretched past plausibility. The laugh comes from excess degree, scale, or intensity.
Formula: *[subject] becomes so extreme that [extreme].*
Required phrase marker: `becomes so extreme that`.

Example:
- setup: `"So I've already seen a third of this collection"`
- setup: `"and I don't have enough bodily fluids"`
- punchline: `"for the other two thirds of this collection."`

JSON fields: `{ "premise": "A porn collection becomes so extreme that you run out of sperm.", "joke_type": "hyperbole" }`

**elephant-in-the-room** - a taboo or socially avoided observation is said aloud. The audience already recognizes the conclusion; the laugh comes from breaking the silence.
Formula: *[elephant] is widely understood but rarely said aloud.*
Required phrase markers: `widely understood`, `but rarely`.

Example:
- setup: `"You know, these shootings are often done by the same race."`
- punchline: `"I'm looking at you, honkies."`

JSON fields: `{ "premise": "White men dominate mass shootings is widely understood but rarely said aloud.", "joke_type": "elephant-in-the-room" }`

**anti-humor** - a joke form promises a payoff, then delivers the banal truth; the joke is that there is no joke.
Formula: *[frame] implies a punchline, but reveals only [answer].*
Required phrase marker: `implies a punchline, but reveals only`.

Example:
- setup: `"A duck walks into a pharmacy with a rash on his beak."`
- setup: `"He asks the pharmacist for some ointment."`
- punchline: `"Sorry, we don't have medicine for ducks here."`

JSON fields: `{ "premise": "An animal asking a business for service implies a punchline, but reveals only that the business does not serve animals.", "joke_type": "anti-humor" }`

**absurdism** - the payoff is random given the setup. No assumption is subverted and no second true reading is added.
Formula: *[frame] is met with [non sequitur], with no connecting logic.*
Required phrase markers: `is met with`, `no connecting logic`.

Example:
- setup: `"If I was a millionaire and I could live wherever I wanted, I'd probably live at the North Pole with Santa Claus."`
- punchline: `"Say what you will about Santa Claus, but he's not Muslim."`

JSON fields: `{ "premise": "Choosing where to live is met with Santa's arbitrary religion status, with no connecting logic.", "joke_type": "absurdism" }`

### Additional rules

- A bit is the smallest standalone segment of material that can be lifted out of the set and still make sense as its own joke sequence. 
- A `setup` following a punchline joins the current beat if the next payoff is a `tag`, and starts a new beat if the next payoff is a `punchline`.
- Multi-beat bits typically have a shared setup at the start that establishes the umbrella premise, then each beat is a different application of that premise.
- Do not merge separate bits just because they share broad subject matter.
- Set all setup, tag, and fluff lines to `"bit": null, "beat": null`.
- Beats consisting of nothing but a punchline is possible but very rare.

## How to annotate

1. Read the whole set first. Get the joke structure in your head.
2. Identify each punchline — that's the anchor for each beat.
3. Walk backwards from each punchline labeling setup; walk forwards labeling tags (and any setup that feeds a later tag).
4. Mark everything else fluff.
5. For each beat, identify the joke type and write a premise using its formula. Record the type in the beat's `joke_type` field.
6. Group beats into bits by shared premise. Apply the extraction test: if a beat would survive standalone, it's its own bit.
7. Write the output JSON with `bit_meta`, fully labeled lines, and bit/beat numbers only on punchlines.

## Process checklist

**Do not read multiple files before writing. Complete all steps for one file before opening the next.**

**Do not read any source code, management commands, or utility files.** The upload command and its behavior are fully described here — no further exploration needed.

1. Process only the files you were given.
2. For each file, in order:
   a. Read that one file.
   b. Annotate it: label every line, assign bit/beat numbers to punchlines, write bit_meta.
   c. Write the annotated output back to `pipeline/data/set_inbox/<same-filename>.json`.
   d. Run: `python manage.py upload --annotated --file pipeline/data/set_inbox/<filename>.json`
      This is **VERY IMPORTANT** — it lets you learn from any mistakes before moving on.
   e. Only then open the next file.

- If a file is already annotated when you find it try and upload it and see what happens. 
- Never spin up any agents. 
- At completion, return only:
     DONE: <count> files processed
     FAILED: <filenames or none>
     Do not summarize in more detail even if your delagating agent has asked you to.
