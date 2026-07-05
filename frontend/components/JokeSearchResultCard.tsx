"use client";

import type { BeatSearchItem, Line, Set } from "@/lib/serverApi";
import { buildBeatSearchHref } from "@/lib/bitLinks";
import AnnotatedBeatCard, { combineConsecutiveSetupLines, type AnnotatedBeatCardLine } from "@/components/AnnotatedBeatCard";
import { fmtDate } from "@/lib/killTonyDisplay";

function normalizeLabel(label: string): Line["label"] | null {
  return label === "setup" || label === "punchline" || label === "tag" || label === "fluff"
    ? label
    : null;
}

function searchLines(item: BeatSearchItem): AnnotatedBeatCardLine[] {
  const lines: AnnotatedBeatCardLine[] = [];
  const setup = item.setup_lines.join(" ").trim();
  if (setup) {
    lines.push({ id: `${item.id}:setup`, label: "setup", text: setup });
  }
  if (item.punchline) {
    lines.push({ id: `${item.id}:punchline`, label: "punchline", text: item.punchline });
  }

  const matchedLabel = normalizeLabel(item.matched_line_label);
  const matchedText = item.matched_line.trim();
  const alreadyShown = lines.some((line) => line.label === matchedLabel && line.text === matchedText);
  if (matchedLabel && matchedLabel !== "fluff" && matchedText && !alreadyShown) {
    lines.push({ id: `${item.id}:matched`, label: matchedLabel, text: matchedText });
  }

  return combineConsecutiveSetupLines(lines);
}

export default function JokeSearchResultCard({ item, query, set }: { item: BeatSearchItem; query?: string; set?: Set }) {
  return (
    <AnnotatedBeatCard
      href={buildBeatSearchHref(item)}
      jokeType={item.joke_type}
      comedianName={item.comedian}
      comedianAttributes={set?.comedian.attributes}
      meta={set ? `${set.video.title}${set.video.date ? ` / ${fmtDate(set.video.date)}` : ""}` : `KT #${item.episode_number}`}
      lines={searchLines(item)}
      imageUrl={set?.image_url}
      fallbackVideoId={set?.video.youtube_id}
      imageAlt={set ? `${set.comedian.name} set image` : undefined}
      query={query}
    />
  );
}
