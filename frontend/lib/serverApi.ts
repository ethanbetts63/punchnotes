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

export async function getServerEpisodes(params?: string) {
  const qs = params ? `?${params}` : "";
  return serverFetch<Episode[]>(`/api/killtony/episodes/${qs}`);
}

export async function getServerEpisode(id: string) {
  return serverFetch<EpisodeDetail>(`/api/killtony/episodes/${id}/`);
}

export async function getServerComedians(params?: string) {
  const qs = params ? `?${params}` : "";
  return serverFetch<Comedian[]>(`/api/killtony/comedians/${qs}`);
}

export async function getServerComedian(slug: string) {
  return serverFetch<ComedianDetail>(`/api/killtony/comedians/${slug}/`);
}

export async function getServerSet(id: string) {
  return serverFetch<Set>(`/api/killtony/sets/${id}/`);
}

export async function getServerSets(params?: string) {
  const qs = params ? `?${params}` : "";
  return serverFetch<SetListItem[]>(`/api/killtony/sets/${qs}`);
}

export async function getServerBeats(params?: string) {
  const qs = params ? `?${params}` : "";
  return serverFetch<BeatSearchItem[]>(`/api/killtony/jokes/${qs}`);
}

export async function getServerBits(params?: string) {
  const qs = params ? `?${params}` : "";
  return serverFetch<BitListItem[]>(`/api/killtony/bits/${qs}`);
}

export async function getServerNavSearch(query: string) {
  const qs = new URLSearchParams({ q: query }).toString();
  return serverFetch<NavSearchResponse>(`/api/killtony/search/?${qs}`);
}

// --- types (minimal, expand as backend solidifies) ---

export type Episode = {
  id: number;
  number: number;
  title: string;
  date: string | null;
  youtube_id: string | null;
  guests: string[];
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
  view_like_ratio: number | null;
};

export type ComedianAttribute =
  | "bucket_pull"
  | "regular"
  | "golden_ticket"
  | "special"
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
export type SetInEpisode = {
  id: number;
  set_number: number;
  comedian: { id: number; name: string; slug: string; attributes: ComedianAttribute[]; image_url: string | null };
  attributes: string[];
  bit_count: number;
  start_seconds: number;
  interview_end_seconds: number | null;
  image_url: string | null;
  image_capture_seconds: number | null;
};

export type EpisodeDetail = {
  id: number;
  number: number;
  title: string;
  url: string;
  youtube_id: string;
  date: string | null;
  guests: string[];
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
  attributes: ComedianAttribute[];
  image_url: string | null;
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
  attributes: string[];
  hit_ratio: number | null;
  punchline_tag_ratio: number | null;
  image_url: string | null;
  image_capture_seconds: number | null;
};

export type ComedianDetail = Comedian & {
  sets: SetInComedian[];
};

export type Beat = {
  id: number;
  premise: string;
  joke_type: string;
  lines: Line[];
};

export type Line = {
  id: number;
  text: string;
  label: "setup" | "punchline" | "tag" | "fluff";
};

export type SetListItem = {
  id: number;
  set_number: number;
  comedian: SetListComedian;
  episode: { id: number; number: number; title: string; youtube_id: string; date: string | null };
  attributes: string[];
  start_seconds: number;
  interview_end_seconds: number | null;
  image_url: string | null;
  image_capture_seconds: number | null;
  hit_ratio: number | null;
  punchline_tag_ratio: number | null;
  bit_count: number;
};

export type SetListComedian = {
  id: number;
  name: string;
  slug: string;
  attributes: ComedianAttribute[];
  image_url: string | null;
  avg_bits_per_set: number | null;
  avg_beats_per_set: number | null;
  avg_hit_ratio: number | null;
  avg_punchline_tag_ratio: number | null;
  has_small_joke_book: boolean;
  has_medium_joke_book: boolean;
  has_large_joke_book: boolean;
};

export type SetComedian = {
  id: number;
  name: string;
  slug: string;
  attributes: ComedianAttribute[];
  image_url: string | null;
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
  attributes: string[];
  start_seconds: number;
  image_url: string | null;
  image_capture_seconds: number | null;
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
  joke_types: string[];
  beats_summary: { premise: string; joke_type: string }[];
  hit_ratio: number | null;
  punchline_tag_ratio: number | null;
};

export type BeatSearchItem = {
  id: number;
  comedian: string;
  comedian_slug: string;
  episode_number: number;
  set_id: number;
  premise: string;
  joke_type: string;
  setup_lines: string[];
  punchline: string;
  matched_line: string;
  matched_line_label: string;
};

export type NavSearchResultType = "comedian" | "episode" | "set" | "beat" | (string & {});

export type NavSearchResult = {
  type: NavSearchResultType;
  title: string;
  subtitle: string;
  href: string;
  meta: string[];
  score: number;
  youtube_id?: string | null;
  image_url?: string | null;
  matched_line_label?: string | null;
};

export type NavSearchResponse = {
  query: string;
  top_result: NavSearchResult | null;
  comedians: NavSearchResult[];
  episodes: NavSearchResult[];
  sets: NavSearchResult[];
  beats: NavSearchResult[];
};
