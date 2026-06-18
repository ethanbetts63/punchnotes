# PunchNotes

PunchNotes is a system for analyzing/annotating stand-up comedy 

The project starts with Kill Tony because it provides a uniquely useful dataset: short standardized sets, high performance variance, recurring comedians, live audience reactions, and explicit quality signals like joke book awards. From there, the system can expand into broader stand-up datasets and eventually become both a comedy analytics platform and a training dataset for AI systems that learn humor from actual audience response rather than text alone.

## Goals

PunchNotes is designed to connect comedic structure to measurable audience response.

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

PunchNotes represents stand-up as a hierarchy:

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

