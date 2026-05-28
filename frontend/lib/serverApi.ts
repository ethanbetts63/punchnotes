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
  return serverFetch<Comedian>(`/api/killtony/comedians/${slug}/`);
}

export async function getServerSet(id: string) {
  return serverFetch<Set>(`/api/killtony/sets/${id}/`);
}

export async function getServerJokes(params?: string) {
  const qs = params ? `?${params}` : "";
  return serverFetch<Joke[]>(`/api/killtony/jokes/${qs}`);
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
};

export type ComedianType = "bucket_pull" | "regular" | "golden_ticket";

export type SetInEpisode = {
  id: number;
  set_number: number;
  comedian: { id: number; name: string; slug: string; comedian_type: ComedianType };
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
  sets: SetInEpisode[];
};

export type Comedian = {
  id: number;
  name: string;
  slug: string;
  set_count: number;
  appearances: number;
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

export type Set = {
  id: number;
  set_number: number;
  comedian: { id: number; name: string; slug: string };
  episode: { id: number; number: number; title: string; youtube_id: string; date: string | null };
  joke_book_award: "small" | "medium" | "large" | null;
  start_seconds: number;
  bits: Bit[];
};

export type Bit = {
  id: number;
  beats: Beat[];
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
