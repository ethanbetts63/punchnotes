const API_BASE_URL = process.env.DJANGO_API_URL ?? "http://localhost:8000";
const REVALIDATE_SECONDS = 300;

async function serverFetch<T>(path: string): Promise<T | null> {
  const url = `${API_BASE_URL}${path}`;
  try {
    const res = await fetch(url, { next: { revalidate: REVALIDATE_SECONDS } });
    if (!res.ok) {
      console.error(`[serverFetch] ${res.status} ${res.statusText} — ${url}`);
      return null;
    }
    return res.json() as Promise<T>;
  } catch (err) {
    console.error(`[serverFetch] fetch failed — ${url}`, err);
    return null;
  }
}

export async function getServerEpisodes() {
  return serverFetch<Episode[]>("/api/killtony/episodes/");
}

export async function getServerEpisode(id: string) {
  return serverFetch<EpisodeDetail>(`/api/killtony/episodes/${id}/`);
}

export async function getServerComedians() {
  return serverFetch<Comedian[]>("/api/killtony/comedians/");
}

export async function getServerComedian(slug: string) {
  return serverFetch<ComedianDetail>(`/api/killtony/comedians/${slug}/`);
}

export async function getServerSet(id: string) {
  return serverFetch<Set>(`/api/killtony/sets/${id}/`);
}

export async function getServerJokes(params?: string) {
  const qs = params ? `?${params}` : "";
  return serverFetch<Joke[]>(`/api/killtony/jokes/${qs}`);
}

export async function getServerBits(params?: string) {
  const qs = params ? `?${params}` : "";
  return serverFetch<BitListItem[]>(`/api/killtony/bits/${qs}`);
}

export async function getServerTopics() {
  return serverFetch<string[]>("/api/killtony/topics/");
}

// --- types (minimal, expand as backend solidifies) ---

export type Episode = {
  id: number;
  number: number;
  title: string;
  date: string | null;
  youtube_id: string | null;
  set_count: number;
  duration_seconds: number | null;
  bucket_pull_count: number;
  golden_ticket_count: number;
  regular_count: number;
  large_joke_book_count: number;
  // populated when YouTube engagement data is fetched
  view_count: number | null;
  like_count: number | null;
  comment_count: number | null;
};

export type ComedianType = "bucket_pull" | "regular" | "golden_ticket" | "special";
export type ComedianAttribute =
  | "gay"
  | "lesbian"
  | "bisexual"
  | "man"
  | "woman"
  | "trans"
  | "white"
  | "black"
  | "asian"
  | "latino"
  | "middle_eastern"
  | "disabled"
  | "old"
  | "young"
  | "middle-age";
export type ComedianAttributeValue = ComedianAttribute | `nationality:${string}`;

export type SetInEpisode = {
  id: number;
  set_number: number;
  comedian: { id: number; name: string; slug: string; comedian_type: ComedianType; comedian_attributes: ComedianAttributeValue[] };
  joke_book: "small" | "medium" | "large" | null;
  bit_count: number;
  start_seconds: number;
  interview_end_seconds: number | null;
};

export type EpisodeDetail = {
  id: number;
  number: number;
  title: string;
  url: string;
  youtube_id: string;
  date: string | null;
  duration_seconds: number | null;
  bucket_pull_count: number;
  golden_ticket_count: number;
  regular_count: number;
  large_joke_book_count: number;
  view_count: number | null;
  like_count: number | null;
  comment_count: number | null;
  sets: SetInEpisode[];
};

export type Comedian = {
  id: number;
  name: string;
  slug: string;
  comedian_type: ComedianType | "";
  comedian_attributes: ComedianAttributeValue[];
  set_count: number;
  appearances: number;
  has_small_joke_book: boolean;
  has_medium_joke_book: boolean;
  has_large_joke_book: boolean;
  avg_hit_ratio: number | null;
  avg_punchline_tag_ratio: number | null;
  avg_bits_per_set: number | null;
  avg_beats_per_set: number | null;
};

export type SetInComedian = {
  id: number;
  set_number: number;
  episode: { id: number; number: number; title: string; youtube_id: string; date: string | null };
  joke_book: "small" | "medium" | "large" | null;
  hit_ratio: number | null;
  punchline_tag_ratio: number | null;
};

export type ComedianDetail = Comedian & {
  sets: SetInComedian[];
};

export type Beat = {
  id: number;
  premise: string;
  joke_type: string;
  topics: string[];
  lines: Line[];
};

export type Line = {
  id: number;
  text: string;
  label: "setup" | "punchline" | "tag" | "fluff";
};

export type SetComedian = {
  id: number;
  name: string;
  slug: string;
  comedian_type: ComedianType | "";
  comedian_attributes: ComedianAttributeValue[];
  set_count: number;
  appearances: number;
  avg_bits_per_set: number | null;
  avg_beats_per_set: number | null;
  avg_hit_ratio: number | null;
  avg_punchline_tag_ratio: number | null;
  has_small_joke_book: boolean;
  has_medium_joke_book: boolean;
  has_large_joke_book: boolean;
};

export type Set = {
  id: number;
  set_number: number;
  comedian: SetComedian;
  episode: { id: number; number: number; title: string; youtube_id: string; date: string | null };
  joke_book_award: "small" | "medium" | "large" | null;
  start_seconds: number;
  hit_ratio: number | null;
  punchline_tag_ratio: number | null;
  bits: Bit[];
};

export type Bit = {
  id: number;
  summary?: string;
  beats: Beat[];
};

export type BitListItem = {
  id: number;
  comedian: string;
  comedian_slug: string;
  episode_number: number;
  set_id: number;
  summary: string | null;
  topics: string[];
  joke_types: string[];
  beats_summary: { premise: string; joke_type: string }[];
};

export type Joke = {
  id: number;
  comedian: string;
  comedian_slug: string;
  episode_number: number;
  set_id: number;
  premise: string;
  joke_type: string;
  topics: string[];
  setup_lines: string[];
  punchline: string;
};
