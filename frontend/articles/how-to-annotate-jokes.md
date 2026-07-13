Why bother annotating a joke? Becuase it's incredibly interesting. 

If you disagree with that statement this article is not for you. This article is a human readable version of the documentation we use to annotate comedy at scale using LLMs. They're actually suprisingly good at it but with your big human brain, you'll be even better. 

Comedy, unlike most art forms, is incredibly structured. Every joke must have at least a setup and a punchline, in that order. Once you start pulling jokes apart line by line, you can't stop seeing the machinery. Economy of words, joke types, joke structure, etc. It's something you can normally get an ear for watching comedy but it's so much clearer when written down. 

If we only achieve one thing with this website, we would want it to the refinement of this ruleset. A fixed set of rules and definitions for understanding, writing and improving comedy. Comedy is like a sport without sport scientists. Comedians give each other pointers, the equivalent of a coach, but theres no way to measure and analyse performance in a structured and repeatable way. This ruleset is our attempt at the analysis part. We will tackle the measure part down the track.

That's the *why*. Here's the exact system we use, condensed and refined for your human eyes: 

---

## Overview - How to annotate

1. Read the whole set first. Get the joke structure in your head.
2. Identify each punchline — that's the anchor for each beat.
3. Walk backwards from each punchline labeling setup; walk forwards labeling tags and setups for tags.
4. Mark everything else fluff.
5. For each beat, identify the joke type.
6. Group beats into bits by shared topic. Apply the extraction test: if a beat would survive standalone, it's its own bit.

---

## Line labels

### `setup`

Where the majority of wasted words hide. Every word in a good setup is load-bearing; remove one and you either destroy the meaning or make the joke hard to follow. It's one of the most noticeable differences in writing styles between comics. Some always run a long string of setups (Norm Macdonald); some are the opposite (Jimmy Carr). Both styles can be valid but a long string of setups is normally a red flag. 


### `punchline`

The line where the laugh lands. The reveal, twist, or payoff the setup was building toward.

### `tag`

An additional payoff in the same beat, riding on the laugh already in the room rather than starting a new beat of its own. A tag can carry its own `setup`: a setup line followed by a tag belongs to the current beat. So `setup → punchline → setup → tag → setup → tag` is a single valid beat just as `setup → punchline → tag → tag` is valid. 

### `fluff`

A line with no comedic bearing on the joke — but that doesn't automatically make it worthless. There's good fluff and bad fluff. Good fluff is the way Pat O'Neill opens a set with "Folks!": it does nothing for the joke that follows, but it gives the crowd a moment to settle and tune into his rhythm. Bad fluff is far more common — `"You know what I'm saying?"`, a repeated line, a nervous throat-clear — words that do nothing at all.

---

## Labeling rules

- **One punchline per beat.** If two adjacent lines both look like punchlines, one is probably a tag or setup.
- **A tag only exists after a punchline.** The beat's first payoff is the `punchline`; every later payoff is a `tag`. All a tag requires is a punchline earlier in the beat — a `setup` it rides, or crowd `fluff`, may sit between them.
- **A setup's beat is decided by what follows it.** A `setup` followed by a `tag` joins the current beat; a `setup` followed by a `punchline` starts a new one.

---

## Bit and beat structure

### Hierarchy

- **Bit**: one or more beats that share a chain of setup. Every bit has at least one beat.
- **Beat**: one setup/punchline/tags unit with its own specific comedic logic. Every beat must contain at least one `punchline` line.

### Bit vs. multiple bits

**Shared subject matter does not equal shared bit.** Don't group beats just because they're about the same subject. Group them only when removing one would orphan the others.

The test: **can you extract a beat alone and still have it make sense?**

- If yes → it's its own bit
- If no (it depends on setup established earlier) → same bit

### Boundary rules

- A bit is the smallest standalone segment of material that can be lifted out of the set and still make sense as its own joke sequence.
- Multi-beat bits typically have a shared setup or topic but more importantly each beat relies on the context of the previous beat for the punchline to make sense. 

---

## Joke types

Joke types are a compact label for the mechanism of a beat. They are not meant to capture every detail of the joke; the transcript lines remain the source of truth. The label is useful for browsing and comparing broad joke shapes without adding a second layer of written analysis for every beat.

### misdirect

An assumption is planted, then subverted. The setup steers you toward a specific conclusion; the punchline reveals it was wrong, and you *replace* your first reading with the real one — you were meant to be fooled. Test: if your first reading of the setup is still true after the punchline and you've merely gained a new angle, it's a reframe, not a misdirect.

Example:

- setup: `"My son just came out as trans."`
- setup: `"Well, shouldn't call him my son anymore."`
- punchline: `"Now that he's dead to me,"`

### reframe

A known thing is given a newly visible interpretation. No false assumption is planted and no wording ambiguity is required: the setup is a plain, true statement, and the punchline overlays a second, equally-true way to see the same fact, object, behavior, or situation. Your first reading stays true — the joke *adds* an angle rather than replacing one. Test: if the punchline instead makes your first reading wrong, it's a misdirect.

Example:

- setup: `"they got him on puberty blockers"`
- punchline: `"or as pedophiles call them preservatives."`

### phonetic-match

Two *different* words sound alike. Often both fit the context, but sometimes the resemblance alone is the joke.

Example:

- setup: `"what do you call a little person with ADHD?"`
- punchline: `"That's right, a fidget."`

### double-meaning

The *same* word or phrase admits two or more readings. Hinges on semantic ambiguity, not phonetic similarity. The ambiguous word or phrase must be preserved exactly from the transcript. Do not generalize, paraphrase, shorten, or clean it up unless removing surrounding non-ambiguous words leaves the same complete ambiguity intact.

Example:

- setup: `"'In case of fire, use stairs.'"`
- punchline: `"Fuck that, let's use water."`

### contradiction

One subject holds two positions that cannot both be true; the joke is the hypocrisy or exposed inconsistency.

Example:

- setup: `"My girlfriend thinks the godfather is too long,"`
- setup: `"But her story about when her coworker was bitchy to her two years ago is..."`
- punchline: `"the perfect length."`

### analogy

Two different things are made funny by showing they share the same unexpected structure. The joke often uses "like," "as," "same as," "basically," or "prepared me for," but the comparison word is not required.

Example:

- setup: `"But golfing prepared me for marriage,"`
- setup: `"cause both involved me spending a lot of money"`
- punchline: `"at something I'm not really good at."`
- setup: `"And then waking up the next morning"`
- tag: `"and deciding to try again, 'cause I like the challenge."`

### hyperbole

One dimension of a subject is stretched past plausibility. The laugh comes from excess degree, scale, or intensity.

Example:

- setup: `"So I've already seen a third of this collection"`
- setup: `"and I don't have enough bodily fluids"`
- punchline: `"for the other two thirds of this collection."`

### elephant-in-the-room

A taboo or socially avoided observation is said aloud. The audience already recognizes the conclusion; the laugh comes from breaking the silence.

Example:

- setup: `"You know, these shootings are often done by the same race."`
- punchline: `"I'm looking at you, honkies."`

### anti-humor

A joke form promises a payoff, then delivers the banal truth; the joke is that there is no joke.

Example:

- setup: `"A duck walks into a pharmacy with a rash on his beak."`
- setup: `"He asks the pharmacist for some ointment."`
- punchline: `"Sorry, we don't have medicine for ducks here."`

### absurdism

The payoff is random given the setup. No assumption is subverted and no second true reading is added.

Example:

- setup: `"If I was a millionaire and I could live wherever I wanted, I'd probably live at the North Pole with Santa Claus."`
- punchline: `"Say what you will about Santa Claus, but he's not Muslim."`

---

## Methodology

Annotating jokes by hand is time consuming. The joke types above are, almost exactly, what we hand to an AI — the only difference is a few extra specifications about output format.

It turns out LLMs are surprisingly good at this kind of structured joke annotation. And because the structure has hard rules, we can catch the majority of the model's mistakes automatically and direct it to fix them on the spot. A tag with no preceding punchline, a beat with no punchline, or a missing joke type will trip validation and get bounced back immediately.

Almost every mistake that survives that process comes down to one of two things: bad transcription, or a lack of context — visual humor being the clearest case (more on that below). So the single best thing we can do to improve our annotations isn't to write more rules — it's to improve our transcriptions and the quality of the model doing the annotating. LLM's are generally very good at doing the line type labeling and beat/bit division, while joke type classification is still the part most likely to need human review.

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
