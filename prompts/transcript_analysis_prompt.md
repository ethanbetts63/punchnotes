# Kill Tony Set Boundary Prompt

You are finding stand-up **set boundaries** in one *Kill Tony* episode transcript.

Only process the first JSON file in `C:\Users\ethan\coding\jokescore\data\1_transcript_inbox\`. Do not process multiple episodes in one run.

Each transcript line has a stable `line_number`. Use those original line numbers as the source of truth.

---

## Your task

Read the transcript and identify each comedian's ~1-minute stand-up set. For each set, run the extraction command:

```powershell
python manage.py extract_set --transcript <path> --start-line <N> --end-line <N> --comedian-name "<Name>" --comedian-type <bucket_pull|regular|golden_ticket> --set-number <N> --interview-end-line <N> --joke-book <small|medium|large|null>
```

If a line inside the range is clearly Tony, a panel member, or other non-comedian speech, omit it with:

```powershell
--omit-lines 123,124
```

Audience reaction lines are filtered automatically by the command.

Also identify the final line of the comic's post-set interview and the joke book size Tony gives the comic at the end of the interview when it is clear. Use only the current appearance's award, not discussion of a previous appearance.

After all sets in the episode are extracted successfully, delete the processed transcript file from `1_transcript_inbox`.

---

## What counts as a set

A set is the comedian's stand-up monologue after Tony introduces them. Include bucket pulls, regulars doing a new minute, and golden ticket winners. Skip the intro block, sponsor reads, transition banter, and post-set interview.

One exception: if the comic is Timmy No-Breaks, the set starts when he comes on stage and finishes when he leaves; the interview portion is included. This is not true for any other comic.

Real set lengths are usually around 60 seconds, but can be roughly 30-180 seconds.

---

## Finding starts

A set starts on the first transcript line where the comedian is on the mic.

Useful cues immediately before a start:

- "your first / next / final bucket pull"
- "60 seconds going to [Name]"
- "Make some noise for [Name]"
- "[Name], everybody"
- "debut a brand new minute"
- a short music sting after Tony's intro

Common first lines include greetings, name acknowledgements, appearance jokes, prop jokes, or jumping directly into a premise.

---

## Finding ends

A set ends on the last line of the comedian's material before the interview begins.

Useful end cues:

- "Thank you", "That's my time", "I love you all"
- Tony says "[Name], everybody" or "All right, [Name]"
- Tony starts interviewing: "How long have you been doing stand-up?", "Where are you from?", "What do you do?"

Do not end a set just because the kitten sound or one-minute mark appears. If Tony lets the comedian finish a joke after a warning, include the final joke line.

---

## Joke book size

Bucket-pull comics often receive a joke book after their interview. Pass the value with `--joke-book` as:

- `small` for small, little, or smallest joke book
- `medium` for medium or medium-sized joke book
- `large` for big or large joke book
- `null` if no joke book is given, or if a joke book is mentioned but the size cannot be worked out confidently

Useful award cues:

- "Here's a big joke book."
- "There's a little joke book for you."
- "You're leaving here with a medium-sized jokebook."
- "You're our first Big Joke Book of the Night."
- "Here's the smallest joke book I could find."

Do not count prior-appearance questions or answers, such as "What size joke book did you get last time?", "Did you get a big joke book last time?", or "No, I got a big joke book." Do not count sponsor or meta mentions like "Bonsai makes our amazing joke books."

---

## Interview end

For every extracted set, pass `--interview-end-line` as the last transcript line belonging to that comic's post-set interview or exit. This is usually the line where Tony thanks the comic, says their name to the crowd, hands them a joke book, or immediately before Tony introduces the next comic, returns to show banter, or starts a sponsor/transition block.

If the interview end is uncertain, use the clearest last line before the next set starts. Do not include the next comic's intro or material.

For Timmy No-Breaks, use the final line of his included appearance.

---

## Rules

- Sets are monologues. Back-and-forth short-answer dialogue is usually interview, not set.
- Prefer Tony's introduced spelling for `--comedian-name`.
- Use `bucket_pull`, `regular`, or `golden_ticket` for `--comedian-type`.
- `--set-number` is 1-indexed in show order.
- If a boundary is uncertain, skip that set instead of extracting a bad range.
