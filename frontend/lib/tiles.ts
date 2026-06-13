import type { SetListItem, Episode, Comedian } from "@/lib/serverApi";
import { getEpisodeGuestLabel, getJokeBookSize } from "@/lib/killTonyDisplay";

export type TileData = {
  href: string;
  imageUrl?: string | null;
  videoId?: string | null;
  eyebrow?: string;
  title: string;
  meta?: string;
  badges?: { label: string; className: string }[];
};

function fmtSeconds(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${m}:${String(s).padStart(2, "0")}`;
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
  large:  { label: "Large Joke Book",  className: "bg-red-100 text-red-700" },
};

export function setToTile(set: SetListItem): TileData {
  return {
    href: `/killtony/sets/${set.id}`,
    imageUrl: set.image_url,
    videoId: set.episode.youtube_id,
    eyebrow: `KT #${set.episode.number}`,
    title: set.comedian.name,
    meta: `Set ${set.set_number} · ${fmtSeconds(set.start_seconds)}`,
    badges: (() => { const jb = getJokeBookSize(set.attributes); return jb ? [jokeBookBadge[jb]] : []; })(),
  };
}

export function episodeToTile(ep: Episode): TileData {
  const meta = [
    fmtCompactDate(ep.date) || null,
    fmtCount(ep.large_joke_book_count, "big joke book"),
    fmtCount(ep.golden_ticket_count, "gold tick.", "gold tick."),
    fmtCount(ep.regular_count, "reg.", "regs."),
  ]
    .filter(Boolean)
    .join(" · ");

  return {
    href: `/killtony/episodes/${ep.id}`,
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
