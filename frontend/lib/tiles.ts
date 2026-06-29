import type { BeatSearchItem, SetListItem, Video, Comedian } from "@/lib/serverApi";
import { buildBeatSearchHref } from "@/lib/bitLinks";
import { fmt2, getEpisodeGuestLabel, getJokeBookSize } from "@/lib/killTonyDisplay";

export type TileData = {
  variant?: "media" | "joke";
  href: string;
  imageUrl?: string | null;
  videoId?: string | null;
  eyebrow?: string;
  title: string;
  body?: string;
  bodyPrefix?: string;
  bodyHighlight?: string;
  meta?: string;
  badges?: { label: string; className: string }[];
  accentClass?: string;
};

export const JOKE_TYPE_STYLES: Record<string, { badge: string; accent: string }> = {
  misdirect:              { badge: "bg-red-500 text-white",       accent: "border-l-red-500" },
  reframe:                { badge: "bg-blue-500 text-white",      accent: "border-l-blue-500" },
  "phonetic-match":       { badge: "bg-amber-400 text-stone-900", accent: "border-l-amber-400" },
  "double-meaning":       { badge: "bg-violet-500 text-white",    accent: "border-l-violet-500" },
  contradiction:          { badge: "bg-orange-500 text-white",    accent: "border-l-orange-500" },
  analogy:                { badge: "bg-emerald-500 text-white",   accent: "border-l-emerald-500" },
  hyperbole:              { badge: "bg-pink-500 text-white",      accent: "border-l-pink-500" },
  "elephant-in-the-room": { badge: "bg-cyan-500 text-white",      accent: "border-l-cyan-500" },
};
const DEFAULT_JOKE_STYLE = { badge: "bg-stone-950 text-white", accent: "border-l-stone-300" };

export function formatJokeTileText({
  punchline,
  setup,
  limit = 150,
}: {
  punchline: string;
  setup: string;
  limit?: number;
}): { prefix?: string; highlight: string } {
  if (punchline.length > limit) {
    return {
      highlight: `${punchline.slice(0, limit - 3).trimEnd()}...`,
    };
  }

  const remaining = limit - punchline.length - 1;
  if (setup && remaining > 4) {
    const setupTail = setup.slice(-(remaining - 3)).trimStart();
    if (setupTail) {
      return {
        prefix: `...${setupTail} `,
        highlight: punchline,
      };
    }
  }

  return { highlight: punchline };
}

function fmtCount(count: number, singular: string, plural = `${singular}s`): string {
  return `${count} ${count === 1 ? singular : plural}`;
}

function fmtCompactDate(date: string | null): string {
  if (!date) return "";
  const d = new Date(date);
  const day = String(d.getDate()).padStart(2, "0");
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const year = String(d.getFullYear()).slice(-2);
  return `${day}/${month}/${year}`;
}

const jokeBookBadge: Record<string, { label: string; className: string }> = {
  small:  { label: "Small Joke Book",  className: "bg-stone-100 text-stone-600" },
  medium: { label: "Medium Joke Book", className: "bg-amber-100 text-amber-700" },
  large:  { label: "Big Joke Book",  className: "bg-red-100 text-red-700" },
};

export function setToTile(set: SetListItem): TileData {
  const meta = [
    `${set.bit_count} bit${set.bit_count !== 1 ? "s" : ""}`,
    `Punch density ${fmt2(set.punch_density)}`,
    `Tag density ${fmt2(set.tag_density)}`,
  ].join(" · ");

  return {
    href: `/killtony/sets/${set.slug}`,
    imageUrl: set.image_url,
    videoId: set.video.youtube_id,
    eyebrow: `KT #${set.video.number}`,
    title: set.comedian.name,
    meta,
    badges: (() => { const jb = getJokeBookSize(set.attributes); return jb ? [jokeBookBadge[jb]] : []; })(),
  };
}

export function episodeToTile(ep: Video): TileData {
  const meta = [
    fmtCompactDate(ep.date) || null,
    fmtCount(ep.large_joke_book_count, "big joke book"),
    fmtCount(ep.golden_ticket_count, "gold tick.", "gold tick."),
    fmtCount(ep.regular_count, "reg.", "regs."),
  ]
    .filter(Boolean)
    .join(" · ");

  return {
    href: `/killtony/episodes/${ep.slug}`,
    videoId: ep.youtube_id,
    eyebrow: `Episode ${ep.number}`,
    title: getEpisodeGuestLabel(ep, `Kill Tony #${ep.number}`),
    meta: meta || undefined,
  };
}

export function comedianToTile(c: Comedian): TileData {
  return {
    href: `/killtony/comedians/${c.slug}`,
    imageUrl: c.image_url,
    title: c.name,
    meta: `${c.set_count} set${c.set_count !== 1 ? "s" : ""}`,
  };
}

export function jokeToTile(joke: BeatSearchItem): TileData {
  const punchline = joke.punchline || joke.matched_line || joke.premise;
  const setup = joke.setup_lines.slice(0, 2).join(" ");
  const text = formatJokeTileText({ punchline, setup, limit: 115 });
  const style = (joke.joke_type && JOKE_TYPE_STYLES[joke.joke_type]) || DEFAULT_JOKE_STYLE;

  return {
    variant: "joke",
    href: buildBeatSearchHref(joke),
    title: joke.comedian,
    bodyHighlight: text.highlight,
    bodyPrefix: text.prefix,
    accentClass: style.accent,
    badges: joke.joke_type
      ? [{ label: joke.joke_type, className: style.badge }]
      : [],
  };
}
