#!/usr/bin/env python
"""Process Kill Tony transcripts and extract sets."""

import json
import subprocess
import os
from pathlib import Path

INBOX_DIR = r"C:\Users\ethan\coding\punchnotes\pipeline\data\transcript_inbox"
FILES = [
    "Kill Tony #104 (Greg Fitzsimmons, Morgan Murphy).json",
    "Kill Tony #106 (Chris D'Elia, Neal Brennan).json",
    "Kill Tony #110 (Al Madrigal, Aasif Mandvi) - window002.json",
    "Kill Tony #112 (Jeff Ross, Dom Irrera) - window001.json",
    "Kill Tony #112 (Jeff Ross, Dom Irrera) - window003.json",
    "Kill Tony #116 (Ralphie May, Mike Lawrence) - window001.json",
    "Kill Tony #116 (Ralphie May, Mike Lawrence) - window002.json",
    "Kill Tony #117 (Sarah Silverman, Doug Benson, Bruce Buffer) - window002.json",
    "Kill Tony #117 (Sarah Silverman, Doug Benson, Bruce Buffer) - window003.json",
    "Kill Tony #122 (Sinbad, Jimmy Carr, Sebastian Maniscalco) - window001.json",
    "Kill Tony #122 (Sinbad, Jimmy Carr, Sebastian Maniscalco) - window002.json",
    "Kill Tony #134 (Stephen Glickman, Jesus Trejo) - window001.json",
    "Kill Tony #134 (Stephen Glickman, Jesus Trejo) - window002.json",
    "Kill Tony #134 (Stephen Glickman, Jesus Trejo) - window003.json",
    "Kill Tony #134 (Stephen Glickman, Jesus Trejo) - window004.json",
    "Kill Tony #134 (Stephen Glickman, Jesus Trejo) - window005.json",
    "Kill Tony #138 (Chris Tellez).json",
    "Kill Tony #144 (Doug Benson, Esther Ku, Greg Fitzsimmons) - window001.json",
    "Kill Tony #144 (Doug Benson, Esther Ku, Greg Fitzsimmons) - window002.json",
    "Kill Tony #144 (Doug Benson, Esther Ku, Greg Fitzsimmons) - window003.json",
]

def load_transcript(file_path):
    """Load JSON transcript."""
    with open(file_path, 'r') as f:
        return json.load(f)

def find_sets(lines):
    """Analyze lines to find set boundaries. Returns list of (start_line, end_line, interview_end_line, comedian_name, attributes)."""
    sets = []
    i = 0

    while i < len(lines):
        line = lines[i]
        text = line['text'].lower()

        # Look for set introductions: "Put your hands together for", "Make some noise for", etc.
        if any(intro in text for intro in ["put your hands together for", "make some noise for", "your first bucket pull", "your next", "60 seconds going to"]):
            # Extract comedian name from the intro line or next few lines
            if "put your hands together for" in text:
                name_part = line['text'].split("put your hands together for")[-1].strip()
                # Clean up the name
                name = name_part.split(",")[0].strip() if "," in name_part else name_part.strip()
                # Next line usually has applause/confirmation
                i += 1
                if i < len(lines):
                    i += 1  # Skip applause line

                # Now look for the actual start of the set
                set_start = i
                if i < len(lines) and "[" in lines[i]['text']:
                    i += 1
                    set_start = i

                # Find where the set ends (before interview)
                set_end = set_start
                interview_end = set_start

                # Look for end markers: "Thank you", "That's my time", Tony saying name, or short Q&A switching to interview
                for j in range(set_start, min(set_start + 200, len(lines))):
                    jtext = lines[j]['text'].lower()

                    # Check if this looks like interview/Q&A
                    if any(q in jtext for q in ["how long have you been", "where are you from", "what do you do", "what's your story", "how many times"]):
                        set_end = j - 1
                        break

                    # Check for set ending phrases
                    if any(end in jtext for end in ["thank you", "that's my time", "i love you all"]) or \
                       (len(jtext) < 50 and ("everybody" in jtext or ", everybody" in jtext)):
                        set_end = j
                        break

                    set_end = j

                # Find interview end (where next comic is introduced or back to show banter)
                interview_end = set_end
                for j in range(set_end, min(set_end + 100, len(lines))):
                    jtext = lines[j]['text'].lower()
                    if "put your hands together for" in jtext or "your next" in jtext or "all right" in jtext and "comedian" in jtext:
                        interview_end = j - 1
                        break
                    interview_end = j

                if set_start < set_end:
                    sets.append((set_start + 1, set_end + 1, interview_end + 1, name, "bucket_pull"))

                i = interview_end + 1
            else:
                i += 1
        else:
            i += 1

    return sets

def extract_joke_book(lines, interview_start, interview_end):
    """Find joke book size from interview section."""
    interview_text = " ".join(line['text'] for line in lines[interview_start:interview_end+1]).lower()

    if "big joke book" in interview_text or "big one" in interview_text:
        return "large"
    elif "medium" in interview_text:
        return "medium"
    elif "small" in interview_text or "little" in interview_text or "smallest" in interview_text:
        return "small"

    return "null"

def process_file(file_path):
    """Process a single transcript file."""
    print(f"Processing {os.path.basename(file_path)}...")

    try:
        transcript = load_transcript(file_path)
    except Exception as e:
        print(f"  Error loading: {e}")
        os.remove(file_path)
        return 0

    lines = transcript.get("lines", [])
    if not lines:
        print(f"  No lines found, deleting.")
        os.remove(file_path)
        return 0

    sets_found = 0
    sets = find_sets(lines)

    for start_line, end_line, interview_end_line, comedian_name, appearance_type in sets:
        joke_book = extract_joke_book(lines, end_line, interview_end_line)

        cmd = [
            "python", "manage.py", "extract_set",
            "--transcript", file_path,
            "--start-line", str(start_line),
            "--end-line", str(end_line),
            "--comedian-name", comedian_name,
            "--interview-end-line", str(interview_end_line),
            "--joke-book", joke_book,
            "--comedian-attributes", appearance_type
        ]

        print(f"  Extracting: {comedian_name} (lines {start_line}-{end_line})")
        try:
            result = subprocess.run(cmd, cwd=r"C:\Users\ethan\coding\punchnotes", capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                sets_found += 1
            else:
                print(f"    Command failed: {result.stderr}")
        except Exception as e:
            print(f"    Error: {e}")

    # Delete processed file
    try:
        os.remove(file_path)
        print(f"  Deleted {os.path.basename(file_path)}")
    except Exception as e:
        print(f"  Error deleting: {e}")

    return sets_found

def main():
    """Main processing loop."""
    os.chdir(r"C:\Users\ethan\coding\punchnotes")

    total_sets = 0
    results = {}

    for filename in FILES:
        file_path = os.path.join(INBOX_DIR, filename)
        if not os.path.exists(file_path):
            print(f"File not found: {filename}")
            results[filename] = "MISSING"
            continue

        try:
            sets = process_file(file_path)
            total_sets += sets
            results[filename] = f"DONE ({sets} sets)"
        except Exception as e:
            print(f"ERROR processing {filename}: {e}")
            results[filename] = f"ERROR: {e}"

    print("\n" + "="*60)
    print("COMPLETION REPORT")
    print("="*60)
    for filename, status in results.items():
        print(f"{filename}: {status}")
    print(f"\nTotal sets extracted: {total_sets}")

if __name__ == "__main__":
    main()
