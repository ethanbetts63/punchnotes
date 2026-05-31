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


Pipeline flow:
  1. Sync episode metadata (manual):
     python manage.py fetch_episodes --full
     python manage.py import_episodes_jsonl
     Purpose: scrape Kill Tony episode metadata from YouTube into JSONL, then import/update 
  2. Get transcripts:
     python manage.py fetch_audio
     python manage.py generate_transcripts
     pipeline/data/1_transcript_inbox/
  3. AI Flow:
A. AI coordinator recieves: prompts/spinup_prompt.md
B. If files in 1_transcript_inbox, spins up agent with prompts/transcript_analysis_prompt.md
C. If file in 2_set_inbox, spins up agent with prompts/annotation_prompt
D. Runs python manage.py normalize_archive to make json more human readable
E. After import_sets, review pipeline/data/similar_comedian_candidates.json with prompts/comedian_alias_review_prompt.md and save decisions in pipeline/data/comedian_name_relationships.json. 
 4. Fetch set images (manual):
     Run python manage.py fetch_set_images
     Purpose: checks db for missing set images, scrapes and writes to data/4_set_images_inbox/
 5. Import set images (manual):
     python manage.py import_set_images 
     Purpose: copies accepted images to: frontend/public/set-images/
     Moves originals to: pipeline/data/set_images_archive/
  6. Optional maintenance/reset
      python manage.py reset_db
      Purpose: Wipes db, clears caches and migration history, reimports all data from archive. 
