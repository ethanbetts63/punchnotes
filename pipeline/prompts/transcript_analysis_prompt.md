# Kill Tony Set Boundary Prompt

You are finding stand-up **set boundaries** in *Kill Tony* transcript inbox files.

You will be given an explicit list of files to process. Process only those files — do not list the inbox directory or process any files outside your list.

Each inbox file is a plain-text `.txt` file. Every line is formatted as:

```
{line_number}: {text}
```

Use the number at the start of each line as the line number — these are stable and must be passed exactly to the extraction command.

---

## Your task

For each file in your list: read the full file content sequentially from start to finish. Do not grep or search for keywords — read the whole transcript and reason over the full context to identify set boundaries. Identify each comedian's ~1-minute stand-up set. For each set, run the extraction command immediately:

```powershell
python manage.py extract_set --transcript "C:\Users\ethan\coding\punchnotes\pipeline\data_private\transcript_archive\<filename>.json" --start-line <N> --end-line <N> --comedian-name "<Name>" --interview-end-line <N> --joke-book <small|medium|large|null> --comedian-attributes "<attributes>"
```

The `--transcript` path must point to the archive JSON, not the inbox `.txt` file. The archive filename matches the inbox filename with `.txt` replaced by `.json`.

You should run this everytime you identify a set boundary not in bulk at the end.

If a line inside the range is clearly Tony, a panel member, or other non-comedian speech, omit it with:

```powershell
--omit-lines 123,124
```

Audience reaction lines are filtered automatically by the command.

Also identify the final line of the comic's post-set interview and the joke book size Tony gives the comic at the end of the interview when it is clear. Use only the current appearance's award, not discussion of a previous appearance.

Also identify the comedian appearance type and any clear comedian attributes stated or strongly supported by the transcript. Pass them as a comma-separated list with `--comedian-attributes`. Always include exactly one of `bucket_pull`, `regular`, `golden_ticket`, or `special`. If no other attributes are clear, pass only the appearance type.

After all complete sets in the current inbox file are extracted successfully, delete that processed `.txt` file from `transcript_inbox`.

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
- `large` for big or big joke book
- `null` if no joke book is given, or if a joke book is mentioned but the size cannot be worked out confidently

Useful award cues:

- "Here's a big joke book."
- "There's a little joke book for you."
- "You're leaving here with a medium-sized jokebook."
- "You're our first Big Joke Book of the Night."
- "Here's the smallest joke book I could find."

Do not count prior-appearance questions or answers, such as "What size joke book did you get last time?", "Did you get a big joke book last time?", or "No, I got a big joke book." Do not count sponsor or meta mentions like "Bonsai makes our amazing joke books."

---

## Comedian attributes

Only use attributes that are clear from the transcript. If unsure, leave the attribute out.

The appearance type must be exactly one of `bucket_pull`, `regular`, `golden_ticket`. Default to `bucket_pull`. Use `regular`, `golden_ticket` only when clearly indicated by the transcript..

Allowed attribute values:

- `bucket_pull`
- `regular`
- `golden_ticket`
- `special`
- `gay`
- `lesbian`
- `bisexual`
- `man`
- `woman`
- `trans`
- `white`
- `black`
- `asian`
- `latino`
- `middle_eastern`
- `disabled`
- `old`
- `young`
- `middle-age`

Do not infer attributes from name, accent, nationality, or a city/state alone.

---

## Interview end

For every extracted set, pass `--interview-end-line` as the last transcript line belonging to that comic's post-set interview or exit. This is usually the line where Tony thanks the comic, says their name to the crowd, hands them a joke book, or immediately before Tony introduces the next comic, returns to show banter, or starts a sponsor/transition block.

---

## Rules

- Sets are monologues. Back-and-forth short-answer dialogue is usually interview, not set.
- Prefer Tony's introduced spelling for `--comedian-name`.
- If you cannot confidently determine the performing comedian's name, do not extract the set. Intro phrasing is not a name — never pass text like "your next comedian", "put your hands together for him", or "friend of the show" as `--comedian-name`. 
- Use `bucket_pull`, `regular`, `golden_ticket`, or `special` in `--comedian-attributes`.
- Do not read any source code, test files, or management commands. The extract_set command signature above is the full contract — no further exploration needed.
- Never spin up any agents to do work for you. Never delegate. Never fork the job. Just do it yourself. 
