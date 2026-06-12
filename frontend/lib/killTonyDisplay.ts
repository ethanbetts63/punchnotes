import type { ComedianAttribute } from "@/lib/serverApi";

export type AppearanceAttribute = "bucket_pull" | "regular" | "golden_ticket" | "special";

const appearanceAttributes: AppearanceAttribute[] = ["bucket_pull", "regular", "golden_ticket", "special"];

export const lineLabelBadge: Record<string, string> = {
  setup: "bg-blue-100 text-blue-700",
  punchline: "bg-amber-100 text-amber-700",
  tag: "bg-green-100 text-green-700",
  fluff: "bg-stone-100 text-stone-500",
};

export const appearanceTypeLabel: Record<AppearanceAttribute, string> = {
  bucket_pull: "Bucket Pull",
  regular: "Regular",
  golden_ticket: "Golden Ticket",
  special: "Special",
};

export const lightAppearanceBadge: Record<AppearanceAttribute, string> = {
  bucket_pull: "bg-stone-100 text-stone-600",
  regular: "bg-blue-50 text-blue-600",
  golden_ticket: "bg-amber-100 text-amber-700",
  special: "bg-purple-50 text-purple-600",
};

export const darkAppearanceBadge: Record<AppearanceAttribute, string> = {
  bucket_pull: "bg-stone-700 text-stone-300",
  regular: "bg-blue-900/60 text-blue-200",
  golden_ticket: "bg-yellow-800/60 text-yellow-200",
  special: "bg-purple-900/60 text-purple-200",
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

export function getAppearanceType(
  attributes: readonly ComedianAttribute[] | undefined
): AppearanceAttribute | null {
  return appearanceAttributes.find((attr) => (attributes ?? []).includes(attr)) ?? null;
}
