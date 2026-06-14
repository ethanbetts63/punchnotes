export const lineLabelBadge: Record<string, string> = {
  setup: "bg-blue-100 text-blue-700",
  punchline: "bg-amber-100 text-amber-700",
  tag: "bg-green-100 text-green-700",
  fluff: "bg-stone-100 text-stone-500",
};

export const jokeBookLabel: Record<string, string> = {
  small: "Small Joke Book",
  medium: "Medium Joke Book",
  large: "Large Joke Book",
};

export const darkJokeBookBadge: Record<string, string> = {
  small: "bg-stone-700 text-stone-200",
  medium: "bg-amber-800/70 text-amber-200",
  large: "bg-red-900/70 text-red-200",
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
  });
}

export function parseEpisodeGuestsFromTitle(title: string | null | undefined): string[] {
  if (!title) return [];
  const guestBlock = title.split(/\s[-–]\s/, 2)[1]?.trim();
  if (!guestBlock) return [];

  return guestBlock
    .split(/\s[-–]\s|\s*(?:,|&|\+)\s*/g)
    .map((guest) => guest.trim())
    .filter(Boolean);
}

export function getEpisodeGuests(
  episode: { guests?: string[] | null; title?: string | null }
): string[] {
  const guests = episode.guests?.map((guest) => guest.trim()).filter(Boolean) ?? [];
  return guests.length > 0 ? guests : parseEpisodeGuestsFromTitle(episode.title);
}

export function getEpisodeGuestLabel(
  episode: { guests?: string[] | null; title?: string | null },
  fallback = "No listed guests"
): string {
  const guests = getEpisodeGuests(episode);
  return guests.length > 0 ? guests.join(", ") : fallback;
}

export function getJokeBookSize(attributes: string[] | null | undefined): "small" | "medium" | "large" | null {
  if (!attributes) return null;
  if (attributes.includes("large_joke_book")) return "large";
  if (attributes.includes("medium_joke_book")) return "medium";
  if (attributes.includes("small_joke_book")) return "small";
  return null;
}
