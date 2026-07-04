export function fmtSeconds(seconds: number | null | undefined): string {
  if (seconds == null || !Number.isFinite(seconds)) return "-";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function fmtDuration(seconds: number | null): string {
  if (!seconds) return "-";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

export function fmtCompact(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

export const lineLabelBadge: Record<string, string> = {
  setup: "bg-blue-100 text-blue-700",
  punchline: "bg-amber-100 text-amber-700",
  tag: "bg-green-100 text-green-700",
  fluff: "bg-stone-100 text-stone-500",
};

export const jokeBookLabel: Record<string, string> = {
  small: "Small Joke Book",
  medium: "Medium Joke Book",
  large: "Big Joke Book",
};


export function fmt2(value: number | null): string {
  return value == null ? "-" : value.toFixed(2);
}

export function fmtDate(date: string | null): string {
  if (!date) return "";
  return new Date(date).toLocaleDateString("en-AU", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });
}

export function getEpisodeGuests(
  episode: { guests?: string[] | null; title?: string | null }
): string[] {
  return episode.guests?.map((guest) => guest.trim()).filter(Boolean) ?? [];
}

export function getEpisodeGuestLabel(
  episode: { guests?: string[] | null; title?: string | null },
  fallback = "No listed guests"
): string {
  const guests = getEpisodeGuests(episode);
  return guests.length > 0 ? guests.join(", ") : episode.title || fallback;
}

export function getJokeBookSize(attributes: string[] | null | undefined): "small" | "medium" | "large" | null {
  if (!attributes) return null;
  if (attributes.includes("large_joke_book")) return "large";
  if (attributes.includes("medium_joke_book")) return "medium";
  if (attributes.includes("small_joke_book")) return "small";
  return null;
}
