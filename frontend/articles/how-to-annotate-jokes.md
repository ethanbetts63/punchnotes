Why the hell would you bother to annotate a joke? Two reasons: it makes your writing better, and it's genuinely interesting to see what's under the hood. This article is a brief overview of our thoughts on joke annotation, followed by a condensed, human-readable version of what we give the AI to do annotations at scale.

Comedy, unlike most art forms, is incredibly structured. Every joke must have at least a setup and a punchline, in that order. Once you start pulling jokes apart line by line, you can't stop seeing the machinery — and you start noticing exactly where words are being wasted.

Because that's what annotation really teaches you: economy. Four times out of five, if it takes the comic more than five lines to get to the punch, the preceding lines could have been condensed. Those lines come in two flavors: fluff and setup.

**Fluff** is a line with no comedic bearing on the joke — but that doesn't automatically make it worthless. There's good fluff and bad fluff. Good fluff is the way Pat O'Neill opens a set with "Folks!": it does nothing for the joke that follows, but it gives the crowd a moment to settle and tune into his rhythm. Bad fluff is far more common — `"You know what I'm saying?"`, a repeated line, a nervous throat-clear — words that do nothing at all.

**Setups** are where the majority of wasted words hide. Every word in a good setup is load-bearing; remove one and you either destroy the meaning or make the joke hard to follow. It's one of the most noticeable differences in writing styles between comics. Some always run a long string of setups (Norm Macdonald); some are the opposite (Jimmy Carr). Both styles can be valid but a long string of setups is normally a red flag. 

That's the *why*. Here's the exact system we use — and hand, almost verbatim, to the AI.

---

## How to annotate

1. Read the whole set first. Get the joke structure in your head.
2. Identify each punchline — that's the anchor for each beat.
3. Walk backwards from each punchline labeling setup; walk forwards labeling tags and setups for tags.
4. Mark everything else fluff.
5. For each beat, identify the joke type and write a premise using the formula.
6. Group beats into bits by shared topic. Apply the extraction test: if a beat would survive standalone, it's its own bit.

---

## Line labels

### `setup`

A line that establishes premise, scenario, observation, or context for a joke — building toward the laugh without delivering it.

### `punchline`

The line where the laugh lands. The reveal, twist, or payoff the setup was building toward.

### `tag`

An additional payoff in the same beat, riding on the laugh already in the room rather than a premise of its own. A tag can carry its own `setup`: a setup line followed by a tag belongs to the current beat. So `setup → punchline → setup → tag → setup → tag` is a single valid beat just as `setup → punchline → tag → tag` is valid. 

### `fluff`

Everything that is not setup, punchline, or tag: greetings, sign-offs, name introductions, verbal stumbles (`"Uh..."`), audio events (`"[squeals]"`), and crowd-acknowledgement filler (`"Hell yeah."`) that isn't doing comedic work.

---

## Labeling rules

- **One punchline per beat.** If two adjacent lines both look like punchlines, one is probably a tag or setup.
- **A tag only exists after a punchline.** The beat's first payoff is the `punchline`; every later payoff is a `tag`. A tag can follow a `punchline`, another `tag`, or a `setup` that belongs to the same beat.
- **A setup's beat is decided by what follows it.** A `setup` followed by a `tag` joins the current beat; a `setup` followed by a `punchline` starts a new one.

---

## Bit and beat structure

### Hierarchy

- **Bit**: one or more beats that share a chain of setup. Every bit has at least one beat.
- **Beat**: one setup/punchline/tags unit with its own specific comedic logic. Every beat must contain at least one `punchline` line.

### Bit vs. multiple bits

**Shared subject matter does not equal shared premise.** Don't group beats just because they're about the same subject. Group them only when removing one would orphan the others.

The test: **can you extract a beat alone and still have it make sense?**

- If yes → it's its own bit
- If no (it depends on a premise established earlier) → same bit

### Boundary rules

- A bit is the smallest standalone segment of material that can be lifted out of the set and still make sense as its own joke sequence.
- Multi-beat bits typically have a shared setup at the start that establishes the umbrella premise, then each beat is a different application of that premise.

---

## Joke types and premise formulas

Writing the premise is the art of concretizing what is funny about a joke; it is not a summary. For every specific token in the setup, ask: swap it for another member of a broader class — does the joke still land via the identical mechanism? If yes, replace the token with the class. Repeat until the next swap up would break the joke. Duck→cow→horse all survive → animal. For example: `"Living in a car technically counts as homeownership."` not `"Living in a RAV4 technically counts as homeownership."` Likewise, avoid words like "he", "she", "they", "the comic". It is almost always unnecessary specification. Why is this important? If two jokes share the same generalized premise, they are the same joke, even if their length, style, and wording may be completely different.

### misdirect

An assumption is planted, then subverted.

Formula: *[bait] implies [implication], but reveals [reveal].*

Example:

- setup: `"My son just came out as trans."`
- setup: `"Well, shouldn't call him my son anymore."`
- punchline: `"Now that he's dead to me,"`

Premise: `"Refusing to call a transitioning child your son implies a new title, but reveals disownment."`

### reframe

A known thing is given a newly visible interpretation. No false assumption is planted and no wording ambiguity is required; the joke surfaces an alternate perspective to understand the same fact, object, behavior, or situation.

Formula: *[subject] could be [reframe].*

Example:

- setup: `"they got him on puberty blockers"`
- punchline: `"or as pedophiles call them preservatives."`

Premise: `"Puberty blockers could be beneficial to pedophiles."`

### phonetic-match

Two *different* words sound alike. Often both fit the context, but sometimes the resemblance alone is the joke.

Formula without reason: *"[heard]" sounds like "[reheard]".*

Formula with reason: *"[heard]" sounds like "[reheard]", and "[reheard]" fits because [reason].*

Example:

- setup: `"what do you call a little person with ADHD?"`
- punchline: `"That's right, a fidget."`

Premise: `"'Midget' sounds like 'fidget', and 'fidget' fits because ADHD."`

### double-meaning

The *same* word or phrase admits two or more readings. Hinges on semantic ambiguity, not phonetic similarity. The ambiguous word or phrase must be preserved exactly from the transcript. Do not generalize, paraphrase, shorten, or clean it up unless removing surrounding non-ambiguous words leaves the same complete ambiguity intact.

Formula: *"[phrase]" can mean [expected] or [comic].*

Example:

- setup: `"'In case of fire, use stairs.'"`
- punchline: `"Fuck that, let's use water."`

Premise: `"'In case of fire, use stairs' can mean use stairs during a fire or use stairs to fight a fire."`

### contradiction

One subject holds two positions that cannot both be true; the joke is the hypocrisy or exposed inconsistency.

Formula: *[subject] both [a] and yet [b].*

Example:

- setup: `"My girlfriend thinks the godfather is too long,"`
- setup: `"But her story about when her coworker was bitchy to her two years ago is..."`
- punchline: `"the perfect length."`

Premise: `"Women both find good movies too long and yet tell long stories."`

### analogy

Two different things are made funny by showing they share the same unexpected structure. The joke often uses "like," "as," "same as," "basically," or "prepared me for," but the comparison word is not required.

Formula: *[X] is like [Y] because both [shared structure].*

Example:

- setup: `"But golfing prepared me for marriage,"`
- setup: `"cause both involved me spending a lot of money"`
- punchline: `"at something I'm not really good at."`
- setup: `"And then waking up the next morning"`
- tag: `"and deciding to try again, 'cause I like the challenge."`

Premise: `"Golf is like marriage because both involve expensive repeated failure."`

### hyperbole

One dimension of a subject is stretched past plausibility. The laugh comes from excess degree, scale, or intensity.

Formula: *[subject] becomes so extreme that [extreme].*

Example:

- setup: `"So I've already seen a third of this collection"`
- setup: `"and I don't have enough bodily fluids"`
- punchline: `"for the other two thirds of this collection."`

Premise: `"A porn collection becomes so extreme that you run out of sperm."`

### elephant-in-the-room

A taboo or socially avoided observation is said aloud. The audience already recognizes the conclusion; the laugh comes from breaking the silence.

Formula: *[elephant] is widely understood but rarely said aloud.*

Example:

- setup: `"You know, these shootings are often done by the same race."`
- punchline: `"I'm looking at you, honkies."`

Premise: `"White men dominate mass shootings is widely understood but rarely said aloud."`

### anti-humor

A joke form promises a payoff, then delivers the banal truth; the joke is that there is no joke.

Formula: *[frame] implies a punchline, but reveals only [answer].*

Example:

- setup: `"A duck walks into a pharmacy with a rash on his beak."`
- setup: `"He asks the pharmacist for some ointment."`
- punchline: `"Sorry, we don't have medicine for ducks here."`

Premise: `"An animal asking a business for service implies a punchline, but reveals only that the business does not serve animals."`

---

## Methodology

Annotating jokes by hand is time consuming. The joke types above are, almost exactly, what we hand to an AI — the only difference is a few extra specifications about output format.

It turns out LLMs are surprisingly good at this kind of structured joke annotation. And because the premises are structured and we have hard rules about how a joke *must* be built, we can catch the majority of the model's mistakes automatically and direct it to fix them on the spot. A tag with no preceding punchline, a beat with no punchline, a premise that still names "he" or a specific brand — these all trip validation and get bounced back immediately.

Almost every mistake that survives that process comes down to one of two things: bad transcription, or a lack of context — visual humor being the clearest case (more on that below). So the single best thing we can do to improve our annotations isn't to write more rules — it's to improve our transcriptions and the quality of the model doing the annotating.

### Known caveats

There's a real trade-off in prompting an AI in depth. The more edge cases you make it aware of, the more edge cases it will correctly catch — but also the more false positives it will invent. So a lot of thought has gone into telling the model the *least* it needs to know to do the job to a standard we're happy with. Perfect is not the goal, because perfect isn't possible.

One concrete example: a beat with a punchline and one or more tags might genuinely have one joke type for the punch and different types for each tag. We could extend the prompt and validation to capture that — but it's a layer of complexity that adds minimal value, so every beat gets a single type. On its own that sounds like a compromise worth fixing. But there are many such small complexities, and we've deliberately accepted them as not worth the cost at this stage.

---

## A note on visual humor

Visual humor doesn't get its own category, because it doesn't need one. An act-out is not a joke type. The visual — a face, a gesture, a prop — is always playing the role of a setup, a punchline, or both, and whatever laugh it gets still runs through one of the mechanisms above.

A prop with an obvious expected use, suddenly used for the opposite, is a **misdirect**. The physical layer changes how the joke is *delivered*, not what makes it funny. When a visual bit fails to annotate cleanly, it's almost never because the joke types don't cover it — it's because the transcript couldn't see it.

---

## Conclusion

If you've read this far, I appreciate your time, and I hope it's been interesting. This isn't a perfect system, and I'd love input on how it could be improved — especially if you think I'm missing a joke type or have mis-defined one.

— Ethan Betts ([ethanbetts63@gmail.com](mailto:ethanbetts63@gmail.com))
