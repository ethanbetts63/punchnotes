# PunchPedia

PunchPedia is a system for analyzing/annotating stand-up comedy 

The project starts with Kill Tony because it provides a uniquely useful dataset: short standardized sets, high performance variance, recurring comedians, live audience reactions, and explicit quality signals like joke book awards. From there, the system can expand into broader stand-up datasets and eventually become both a comedy analytics platform and a training dataset for AI systems that learn humor from actual audience response rather than text alone.

## Goals

PunchPedia is designed to connect comedic structure to measurable audience response.

Short-term goals:
- Extract stand-up sets from full Kill Tony episode transcripts.
- Label each set line by comedic function.
- Group lines into bits and beats.
- Annotate each beat with premise, joke mechanism, and topics.
- Preserve interview boundaries and quality signals such as joke book awards.
- Align transcripts with laughter and applause events.
- Create a website focusing on the kill tony universe. 

Medium-term goals: 
- Expand database to include any youtube set
- Estimate premise originality across.
- Detect joke originality
- Sort topics by rarity.

Long-term goals:
- Analyse the audio and potentially video of a set to figure out for a given joke how loud the laugh was, how long the audience laughed, weighted values relative to previous sets in the same show or earlier jokes. etc. 

## Data Model

PunchPedia represents stand-up as a hierarchy:

- **Set**: one recorded appearance by a comic.
- **Bit**: one or more beats that share a premise.
- **Beat**: one setup, punchline, and optional tags with its own comedic logic.
- **Line**: a transcript line labeled by function.

Every annotated set stores:

- episode metadata
- comedian metadata
- set start time
- interview end line and timestamp
- joke book award size, when clear
- bit and beat metadata
- line-level labels

Every beat stores:

- `premise`: the abstract comedic logic of the beat
- `joke_type`: the mechanism that creates the laugh
- `topics`: short searchable topic labels

## Kill Tony Signals

Kill Tony adds useful structure that most stand-up datasets do not have.

Bucket-pull sets are short and standardized. Interviews happen immediately after the set. Tony and the panel often give a joke book award at the end of the interview: `small`, `medium`, or `large`. Joke book size is captured as a human-curated quality signal. If no current award is clear, the value is left `null`. This is just a signal. Bad sets followed by great interviews can still receive a big joke book and vice versa. Regardless, a small joke book is strongly correlated with a bad set.  

The archive also stores `interview_end_line` and `interview_end_seconds`, so interviews can later be extracted programmatically without re-analyzing the full episode transcript.

## Line Labels

Each transcript line is assigned one primary label.

### `setup`

A line that establishes premise, scenario, observation, or context for a joke. It builds toward the laugh without delivering it.

### `punchline`

The line where the laugh lands: the reveal, twist, or payoff the setup was building toward.

### `tag`

An additional punchline that builds off the previous punchline without requiring new setup. If the line introduces fresh material, it is a new `setup`, not a tag.

### `fluff`

Everything that is not setup, punchline, or tag: greetings, sign-offs, name introductions, verbal stumbles, audio events, and crowd-acknowledgement filler that is not doing comedic work.

## Labeling Rules

- One joke should usually have one punchline.
- Tags require an immediately preceding punchline or tag.
- Sound effects are fluff.
- Self-introductions are fluff unless the name itself is the joke.
- Closers such as "That's my time" and "Thank you" are fluff.
- Visually-dependent jokes can have implicit setup from stage context.

### Joke types and premise formulas

All jokes should be assigned one of these mechanisms. Each type has a preferred premise shape. The value in the `joke_type` field uses the lowercase/hyphenated form shown next to each name. **The way you write the premise must exactly match the formula given for each joke type.** 

**Misdirect** (`misdirect`) — an assumption is planted, then subverted.
Formula: *[setup] implies [expected interpretation], but [punchline reveals unexpected interpretation].*

Example:
- setup: `"My son just came out as trans."`
- setup: `"Well, shouldn't call him my son anymore."`
- punchline: `"Now that he's dead to me,"`

Premise: `"Refusing to call a transitioning child your son implies a new title, but reveals disownment."`

**Reframe** (`reframe`) — a known thing is given a newly visible interpretation. No false assumption is planted and no wording ambiguity is required; the joke surfaces an alternate perspective to understand the same fact, object, behavior, or situation.
Formula: *[known thing] could be [unexpected interpretation].*

Example:
- setup: `"they got him on puberty blockers"`
- punchline: `"or as pedophiles call them preservatives."`
- tag: `"Fucking miracle medicine."`

Premise: `"Puberty blockers could be beneficial to pedophiles."`

**Phonetic match** (`phonetic-match`) — two *different* words sound alike, and both independently fit the context.
Formula: *"[word A]" sounds like "[word B]", and [word B] fits because [reason].*

Example:
- setup: `"what do you call a little person with ADHD?"`
- punchline: `"That's right, a fidget."`

Premise: `"'Midget' sounds like 'fidget', and 'fidget' fits ADHD."`

**Double-meaning** (`double-meaning`) — the *same* word or phrase admits two readings, and the comedian deliberately picks the non-standard one. Hinges on semantic ambiguity, not phonetic similarity.
Formula: *"[phrase]" can mean [meaning A] or [meaning B].*

Example:
- setup: `"'In case of fire, use stairs.'"`
- punchline: `"Fuck that, let's use water."`

Premise: `"'Use stairs' can mean take the stairs or use stairs as the tool."`

**Analogy** (`analogy`) — two different things are made funny by showing they share the same unexpected structure. The joke often uses "like," "as," "same as," "basically," or "prepared me for," but the comparison word is not required.
Formula: *[X] is like [Y] because both [shared structure].*

Example:
- setup: `"But golfing prepared me for marriage,"`
- setup: `"cause both involved me spending a lot of money"`
- punchline: `"at something I'm not really good at."`
- tag: `"And then waking up the next morning"`
- tag: `"and deciding to try again, 'cause I like the challenge."`

Premise: `"Golf is like marriage because both are difficult, expensive and repetitious."`

**Hyperbole** (`hyperbole`) — a feeling, trait, preference, or consequence is exaggerated past plausibility. The laugh comes from the excess of degree, scale, or intensity.
Formula: *[thing] is so [extreme quality] that [impossible or disproportionate result].*

Example:
- setup: `"So I've already seen a third of this collection"`
- setup: `"and I don't have enough bodily fluids"`
- punchline: `"for the other two thirds of this collection."`

Premise: `"A porn collection is so large that you could run out of sperm."`


**Elephant-in-the-room** (`elephant-in-the-room`) — a taboo or socially avoided observation is said aloud. The audience already recognizes the conclusion; the laugh comes from breaking the silence.
Formula: *[observation] is widely understood about [topic] but rarely said aloud.*

Example:
- setup: `"You know, these shootings are often done by the same race."`
- punchline: `"I'm looking at you, honkies."`

Premise: `"White shooters are widely associated with school shootings but rarely named aloud."`


### Not valid joke types

**Prop** (`prop`) — a literal object used or presented onstage. A prop can be the setup, punchline, or evidence, but the underlying joke type should still be one of the valid mechanisms above.

Example:
- setup: `"It's a mouse trap to trap gay mice, see"`
- punchline: `"[Pulls out mouse trap with a disco ball attached]"`

Premise: `"A mousetrap for gay mice could use nightlife stereotypes as bait."`
Joke type: `reframe`


**Act-out** (`act-out`) — embodied performance: a voice, scream, facial expression, mime, posture, movement, or physical imitation. An act-out can carry the setup or punchline, but the underlying joke type should still be one of the valid mechanisms above.

Example:
- setup: `"Wheelchair people, we send them."`
- setup: `"Oh yeah, we put a grenade in your lap and..."`
- punchline: `"Come on! [acts out racing a wheelchair into battle]"`

Premise: `"A wheelchair with a grenade could become a form of military charge."`
Joke type: `reframe`

**What-if** (`what-if`) — a premise framing, not a joke type. Almost any joke can be rewritten as "what if..." Omitting `what-if` forces the annotator to name the more precise mechanism: `reframe`, `hyperbole`, `analogy`, `double-meaning`, or another valid type.


## Pipeline

The current workflow is:

1. Download full episode audio files and process into transcripts.
2. Extract individual set windows.
3. Record set metadata, interview boundaries, and joke book awards.
4. Annotate lines as setup, punchline, tag, or fluff.
5. Group lines into bits and beats.
6. Add beat-level premises, joke types, and topics.
7. Import annotated sets into the database.
8. Use audience reaction data to score sets, beats, jokes, and tags.

## Why This Matters

Most comedy analysis stops at transcripts or high-level audience reaction. PunchPedia is aimed at the semantic layer: how jokes are built, how often similar premises appear, and which structures reliably produce laughter.

Because the dataset includes both strong and weak performances, it can support deeper analysis of why material succeeds or fails. The same system can eventually compare joke writing, delivery, crowd work, room energy, originality, and audience response at scale.

Even at this stage in the development the differences in annotating a good vs a bad set are quite interesting. The better the writing, the harder it is to figure out the premise but the easier line labeling becomes. I think this is becuase well written sets are well structured. Hence, its quite easy to tell a setup from a punch. But the complexity of the joke is often greater which means distilling the essence down into a premise line can often be quite tricky. 



RESET DB
  python manage.py reset_db          # offline: drop → migrate → import archived sets
  python manage.py fetch_episodes    # online:  sync episode metadata from YouTube