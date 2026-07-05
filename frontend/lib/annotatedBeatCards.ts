import type { Beat, BeatSearchItem, Line, Set } from "@/lib/serverApi";
import { buildBeatSearchHref, buildSetBeatHref } from "@/lib/bitLinks";
import { fmtDate } from "@/lib/killTonyDisplay";

export type AnnotatedBeatCardLine = {
  id: string | number;
  label: Line["label"];
  text: string;
};

export type AnnotatedBeatCardData = {
  href: string;
  jokeType?: string | null;
  comedianName: string;
  comedianAttributes?: Set["comedian"]["attributes"];
  meta: string;
  lines: AnnotatedBeatCardLine[];
  imageUrl?: string | null;
  fallbackVideoId?: string | null;
  imageAlt?: string;
};

export function combineConsecutiveSetupLines(lines: AnnotatedBeatCardLine[]): AnnotatedBeatCardLine[] {
  return lines.reduce<AnnotatedBeatCardLine[]>((combined, line) => {
    const previous = combined.at(-1);
    if (previous?.label === "setup" && line.label === "setup") {
      combined[combined.length - 1] = {
        ...previous,
        text: `${previous.text} ${line.text}`,
      };
      return combined;
    }
    combined.push(line);
    return combined;
  }, []);
}

function setMeta(set: Set): string {
  return `${set.video.title}${set.video.date ? ` / ${fmtDate(set.video.date)}` : ""}`;
}

export function beatLinesToCardLines(beat: Beat): AnnotatedBeatCardLine[] {
  return combineConsecutiveSetupLines(
    beat.lines
      .filter((line) => line.label !== "fluff")
      .map((line) => ({ id: line.id, label: line.label, text: line.text }))
  );
}

function normalizeLabel(label: string): Line["label"] | null {
  return label === "setup" || label === "punchline" || label === "tag" || label === "fluff"
    ? label
    : null;
}

export function beatSearchItemToCardLines(item: BeatSearchItem): AnnotatedBeatCardLine[] {
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

export function setBeatToCardData(set: Set, bitIndex: number, beatIndex: number): AnnotatedBeatCardData | null {
  const bit = set.bits[bitIndex];
  const beat = bit?.beats[beatIndex];
  if (!bit || !beat) return null;

  return {
    href: buildSetBeatHref(set, bit, beat),
    jokeType: beat.joke_type,
    comedianName: set.comedian.name,
    comedianAttributes: set.comedian.attributes,
    meta: setMeta(set),
    lines: beatLinesToCardLines(beat),
    imageUrl: set.image_url,
    fallbackVideoId: set.video.youtube_id,
    imageAlt: `${set.comedian.name} set image`,
  };
}

export function beatSearchItemToCardData(item: BeatSearchItem, set?: Set): AnnotatedBeatCardData {
  return {
    href: buildBeatSearchHref(item),
    jokeType: item.joke_type,
    comedianName: item.comedian,
    comedianAttributes: set?.comedian.attributes,
    meta: set ? setMeta(set) : `KT #${item.episode_number}`,
    lines: beatSearchItemToCardLines(item),
    imageUrl: set?.image_url,
    fallbackVideoId: set?.video.youtube_id,
    imageAlt: set ? `${set.comedian.name} set image` : undefined,
  };
}
