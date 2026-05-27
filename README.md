# JokeScore

JokeScore is a system for measuring and analyzing stand-up comedy using audience reaction as a real-world signal for humor.

At its core, JokeScore processes recorded comedy sets and calculates metrics such as laughs per minute, joke density, laugh intensity, and joke efficiency by aligning transcripts with audience laughter. Sets are broken down hierarchically into bits, beats, and individual lines, allowing jokes to be analyzed structurally rather than as raw text.

The project starts with Kill Tony because it provides a uniquely useful dataset: short standardized sets, high performance variance, recurring comedians, live audience reactions, and explicit quality signals like joke book awards. From there, the system can expand into broader stand-up datasets and eventually become both a comedy analytics platform and a training dataset for AI systems that learn humor from actual audience response rather than text alone.

## Goals

JokeScore is designed to connect comedic structure to measurable audience response.

Short-term goals:

- Extract stand-up sets from full episode transcripts.
- Label each set line by comedic function.
- Group lines into bits and beats.
- Annotate each beat with premise, joke mechanism, and topics.
- Preserve interview boundaries and quality signals such as joke book awards.
- Align transcripts with laughter and applause events.

Long-term goals:

- Estimate premise originality across a large comedy corpus.
- Detect joke similarity and possible plagiarism.
- Identify overused topics and premises.
- Compare joke structures against audience reaction.
- Separate writing quality from delivery, room energy, and context.
- Train humor models on actual audience response rather than text-only examples.

## Data Model

JokeScore represents stand-up as a hierarchy:

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

Bucket-pull sets are short and standardized. Interviews happen immediately after the set. Tony and the panel often give a joke book award at the end of the interview: `small`, `medium`, or `large`. Joke book size is captured as a human-curated quality signal. If no current award is clear, the value is left `null`.

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
- Sight-dependent jokes can have implicit setup from stage context.
- Misdirects turn on the frame-flip line; label that line as the punchline.

## Joke Types

Each beat receives one joke mechanism.

### `misdirect`

An assumption is planted, then subverted.

Formula: `X implies Y, not Z.`

### `reframe`

A hidden implication of a known thing is surfaced. The audience did not necessarily hold the wrong assumption; they just had not considered this angle.

Formula: state the hidden implication directly.

### `phonetic-match`

Two different words sound alike, and both independently fit the context.

Formula: state the sonic match and why both sides fit.

### `double-meaning`

The same words admit two readings, and the comedian deliberately chooses the non-standard one.

Formula: `Taken literally, [phrase] has two meanings.`

### `what-if`

A counterfactual scenario is posed and taken seriously.

Formula: `What if [counterfactual]?`

### `analogy`

Two different things are made funny by showing that they share the same unexpected structure.

Formula: `X is like Y because both share Z.`

### `prop`

The joke depends on a literal object the comedian is using or presenting onstage.

Formula: `This object reveals or creates [comic meaning].`

### `elephant-in-the-room`

A taboo or obvious observation is said aloud. The audience already understands the conclusion; the laugh comes from breaking the silence.

Formula: `X is widely understood about Y but rarely said aloud.`

## Pipeline

The current workflow is:

1. Archive full episode transcripts.
2. Extract individual set windows.
3. Record set metadata, interview boundaries, and joke book awards.
4. Annotate lines as setup, punchline, tag, or fluff.
5. Group lines into bits and beats.
6. Add beat-level premises, joke types, and topics.
7. Import annotated sets into the database.
8. Use audience reaction data to score sets, beats, jokes, and tags.

## Why This Matters

Most comedy analysis stops at transcripts or high-level audience reaction. JokeScore is aimed at the semantic layer: how jokes are built, how often similar premises appear, and which structures reliably produce laughter.

Because the dataset includes both strong and weak performances, it can support deeper analysis of why material succeeds or fails. The same system can eventually compare joke writing, delivery, crowd work, room energy, originality, and audience response at scale.
