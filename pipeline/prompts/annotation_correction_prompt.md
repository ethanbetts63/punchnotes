
  
  
  
  You have the following task for each file.
  1. Assess if the joke type should actually be a contradiction or antihumor (expect this change to be very rare)
  2. Rewrite the premise to match the formula for the given joke type. 
  3. Derive the typed fields from that rewritten premise
  4. Populate keys from those fields

The following should already be done in all files so you will not have to touch it: 
  - All line labels (setup/punchline/tag/fluff)
  - Bit/beat numbering on punchlines
  - Bit structure and grouping
  - Summaries

  **Premise rules:**
- **Hard limit: 20 words maximum.** If your premise exceeds 20 words, you are describing the joke rather than stating its mechanism. Count the words and cut until you are at or under 20. Every word must be load-bearing.
- State the abstract comedic logic - *why is this funny*, not a summary of what was said.
- No pronouns tied to the comedian - no "he", "she", "they", "the comic".
- Use the most general form: `"Living in a car technically counts as homeownership."` not `"Living in a RAV4 technically counts as homeownership."`
- Build the premise from the required fields plus that joke type's formula words. Do not add extra explanation words.
- After writing the premise, copy those same field values into the beat JSON. The field values are the source of the premise.

**Joke type:** one of the nine accepted labels defined in the next section: `misdirect`, `reframe`, `phonetic-match`, `double-meaning`, `contradiction`, `analogy`, `hyperbole`, `elephant-in-the-room`, `anti-humor`. Pick the mechanism that best describes how the joke gets its laugh - the same mechanism the premise formula is built around.

Do not use joke types outside this list. If a joke seems to need a type that is not allowed, choose the closest allowed type and mention the uncertainty in your closing comments.

For every specific token in the setup, ask: swap it for another member of a broader class — does the joke still land via the identical mechanism? If yes, replace the token with the class. Repeat until the next swap up would break the joke. Duck→cow→horse all survive → animal. Beak-rash→foot-cream survive → medicine.

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

**Keys:** 1-4 short, specific, searchable nouns or noun phrases per beat. Keys are chosen last from the premise field. never directly from the transcript. Prefer `"crackheads"` over `"people doing drugs"`.

Strip any leading helper or modal verb from shared before using it as a key ("involve", "involves", "are", "is", "could", "would", "can", "might"). The key must contain no unnecessary filler words.

Key source rules:
- `analogy`: copy `a`, `b`, and the core searchable phrase from `shared`. If `shared` begins with a helper verb like "involve", omit that helper verb from the key.
- `hyperbole`: copy `subject` and `extreme`. The `extreme` must be the shortest phrase that preserves the exaggerated endpoint.
- `phonetic-match`: copy `heard` and `reheard`; also copy `reason` when present.
- `double-meaning`: copy exact `phrase` and `comic`; exclude `expected`.
- `contradiction`: pick concrete nouns from `subject`, `a`, and `b`.
- `reframe`: pick concrete nouns from `subject` and `reframe`.
- `misdirect`: pick the shortest searchable phrase from each of `bait`, `implication`, and `reveal`.
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
JSON fields: `{ "premise": "Refusing to call a transitioning child your son implies a new title, but reveals disownment.", "joke_type": "misdirect", "bait": "refusing to call a transitioning child your son", "implication": "a new title", "reveal": "disownment", "keys": ["transitioning child", "new title", "disownment"] }`

**reframe** - a known thing is given a newly visible interpretation. No false assumption is planted and no wording ambiguity is required; the joke surfaces an alternate perspective to understand the same fact, object, behavior, or situation.
Fields: `subject`, `reframe`.
Formula: *[subject] could be [reframe].*
Required phrase marker: `could be`.

Example:
- setup: `"they got him on puberty blockers"`
- punchline: `"or as pedophiles call them preservatives."`

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
JSON fields: `{ "premise": "'Midget' sounds like 'fidget', and 'fidget' fits because ADHD.", "joke_type": "phonetic-match", "heard": "midget", "reheard": "fidget", "reason": "ADHD", "keys": ["midget", "fidget", "ADHD"] }`

**double-meaning** - the *same* word or phrase admits two or more readings, and the comedian deliberately picks the non-standard one. Hinges on semantic ambiguity, not phonetic similarity. The `phrase` field must preserve the exact ambiguous word or phrase from the transcript. Do not generalize, paraphrase, shorten, or clean it up unless removing surrounding non-ambiguous words leaves the same complete ambiguity intact.
Fields: `phrase`, `expected`, `comic`.
Formula: *"[phrase]" can mean [expected] or [comic].*
Required phrase markers: `can mean`, `or`.

Example:
- setup: `"'In case of fire, use stairs.'"`
- punchline: `"Fuck that, let's use water."`

Premise: `"'In case of fire, use stairs' can mean use stairs during a fire or use stairs to fight a fire."`
JSON fields: `{ "premise": "'In case of fire, use stairs' can mean use stairs during a fire or use stairs to fight a fire.", "joke_type": "double-meaning", "phrase": "In case of fire, use stairs", "expected": "use stairs during a fire", "comic": "use stairs to fight a fire", "keys": ["In case of fire, use stairs", "use stairs to fight a fire"] }`

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
JSON fields: `{ "premise": "Golf is like marriage because both involve expensive repeated failure.", "joke_type": "analogy", "a": "golf", "b": "marriage", "shared": "involve expensive repeated failure", "keys": ["golf", "marriage", "expensive repeated failure"] }`

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

---

## How to annotate


5. For each beat, identify the joke type (`misdirect`, `reframe`, `phonetic-match`, `double-meaning`, `contradiction`, `analogy`, `hyperbole`, `elephant-in-the-room`, `anti-humor`) and write a premise using its formula. Record the type in the beat's `joke_type` field. Do not invent other `joke_type` values.
6. Add the required field keys for that joke type using the same distilled wording from the premise.
7. Choose keys last from the allowed premise fields for that joke type.
10. Write the output JSON with `bit_meta`, fully labeled lines, and bit/beat numbers only on punchlines.

---

## After correcting each file

Run the import command on the single file to validate and archive it:

```
python manage.py import_sets --file pipeline/data/3_bit_annotated_set_inbox/<filename>.json
```

Do not read or write to multiple files at once. Fix one file. run the command. Then move on if it worked. \\
