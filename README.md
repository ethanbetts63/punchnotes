jokescore

A system for measuring how funny stand-up comedy actually is.

The core idea is simple: calculate a comedian's laughs per minute (LPM) from a recorded set. From there, you can compare comics, compare different sets from the same comic, and even track how performance changes over time.

Beyond LPM, you could derive other metrics:

Words per minute vs laughs per minute
Words-per-laugh ratio
Average laugh duration/intensity
Performance heatmaps across a set
Joke/tag efficiency

You could then break sets down at the joke level, scoring individual jokes and tags based on audience response. That effectively gives jokes a measurable "weighting."

At scale, this becomes interesting for AI. Current language models can ingest huge numbers of jokes, but they don't inherently know what is actually funny. A large dataset with joke-level audience reaction scores could provide a real-world humor signal.

Another possible layer is premise rarity. If you maintained a large database of stand-up transcripts, you could estimate how common or overused a premise is, or even flag potential joke theft/similarity between comics.

There are also deeper questions:

How much of comedy is the written joke vs delivery/presentation?
How much does room energy affect results?
Why can the same set perform wildly differently in different rooms?
Existing Tools & Research

Some products already cover parts of this idea:

StandApp Comedy and Jokesmith provide automatic laughter detection, transcripts, LPM analytics, and audience-reaction heatmaps.
LaughTrack experimented with joke-level laugh scoring.
Gillick's laughter-detection library provides open-source laugh boundary models.

Recent datasets are making this more feasible:

StandUp4AI â€“ 3,617 stand-up videos with transcripts and laugh labels
TIC-TALK â€“ multimodal dataset with transcripts, body pose, and laughter events
SMILE â€“ laughter-labeled clips with contextual annotations
What Still Doesn't Exist

Most current systems stop at audience reaction analytics. The bigger semantic layer is still mostly untouched.

Major gaps:

Premise originality scoring
Joke similarity / plagiarism detection
WPM vs LPM analysis
Crowd-work detection
Applause/interruption tagging
Separating delivery quality from joke quality
AI-assisted callback or punchline generation trained on audience response
Opportunity

The strongest unexplored area is probably semantic comedy intelligence:

detecting similar jokes across the entire stand-up corpus
measuring how novel a premise is
understanding which joke structures consistently outperform others
training humor models on actual audience response instead of raw text alone

Most existing products are essentially analytics dashboards. None appear to combine:

large-scale stand-up datasets,
semantic similarity analysis,
audience reaction modeling,
and AI training pipelines.

That gap is where jokescore becomes interesting.


so far we are just targeting kill tony and premise rarity as a starting point.

Extensions

Ideas for future expansion once the core pipeline is stable.

Jokebook as a quality signal

At the end of each bucket pull interview, Tony awards the comedian a jokebook â€” small, medium, or large â€” based on how well they did. Occasionally none is given, either because the set was poor or because the comedian already received one in a prior appearance. This is one of the few ground-truth quality labels available in the dataset: an in-the-moment assessment from Tony and the panel, with immediate audience context. Recording jokebook size (small / medium / large / none) and the likely reason per appearance would give jokescore a human-curated label to validate LPM-based scoring against.

Interview preservation

The set extraction pipeline already identifies where each set ends and the interview begins â€” that boundary is a byproduct of work already being done. Right now the interview window is simply discarded. Capturing it costs almost nothing extra and preserves all the qualitative signal that follows a set: Tony's reaction, panel feedback, the comedian's backstory, and the jokebook award. A dedicated interview extraction step (parallel to the existing set prompt) could record jokebook size, whether the comedian has appeared before, years doing comedy, home city, and any notable panel reactions. This data doesn't belong in the set pipeline but it would be valuable to have archived for later analysis.

Audio-based laughter detection

Whisper's non-speech tokens ([laughter], [applause], â™ª) give a coarse signal, but purpose-built models like Gillick's laughter detection library could provide precise laughter timestamps and intensity scores. Layering that over the line-level transcript would enable true LPM calculation at the joke and line level rather than at the set level.

Crowd-work detection at scale

The line taxonomy already includes crowd_work as a type. Tracking the ratio of crowd_work lines to joke lines across a comedian's appearances over time would reveal how much of their performance depends on the room versus prepared material â€” a meaningful signal for separating delivery quality from joke quality, one of the major gaps identified above.

Premise originality scoring

With a large corpus of Kill Tony sets, semantic similarity between premises across comedians and across time could be computed. This would surface originality signals and flag potential joke similarity between comics â€” useful both as a dataset feature and as a standalone tool.

additional labeling depth. right now we are working with setup, punchline, tag and fluff. that covers everything. but theres more analysis you could do for instance a punchline or a tag could also be a callback. the fluff could be all sorts of things like a closing remark like thank you. the setup maybe could be thought of as a bridge in differnet contexts. 


Joke hierarchy: 
Top to bottom: 
Set - the full recorded appearance of the comic doing standup
Bit - a single beat or a sequence of beats that do not make sense without the context of a shared premise
Beat - a sequence of setup + punchline + tag (if present). The start of a beat is the first setup line following a punchline or tag in a set. 
Line - fluff, setup, punchline or tagline. 


Topics are attributed at the beat level and are the salient topic / topics of the beat. 
Premises are attributed at the bit level and are the smallest standalone â€œwhat this bit is aboutâ€ statement that the audience needs in order for the beats to make sense. 


reframe (or perspective shift). The joke takes something familiar (puberty blockers as medical care
  for trans kids) and reveals an angle from a stakeholder the audience hadn't been thinking about (pedophiles, for whom
  this is functionally great news). The laugh comes from suddenly seeing the implication that was always logically there
   but invisible.

     wordplay is that it requires two things to line up simultaneously to be funny:

  1. Phonetic match — "midget" and "fidget" near-rhyme
  2. Semantic match — "fidget" also independently fits the ADHD frame (via fidget spinners)

  - Elephant (in-the-room): X is widely understood about Y but rarely said aloud