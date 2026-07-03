const API_BASE_URL = process.env.DJANGO_API_URL ?? "http://localhost:8000";
const REVALIDATE_SECONDS = 300;

type ServerFetchOptions = {
  allowNotFound?: boolean;
};

async function serverFetch<T>(path: string): Promise<T>;
async function serverFetch<T>(path: string, options: { allowNotFound: true }): Promise<T | null>;
async function serverFetch<T>(path: string, options: ServerFetchOptions = {}): Promise<T | null> {
  const url = `${API_BASE_URL}${path}`;
  const res = await fetch(url, { next: { revalidate: REVALIDATE_SECONDS } });
  if (options.allowNotFound && res.status === 404) {
    return null;
  }
  if (!res.ok) {
    throw new Error(`[serverFetch] ${res.status} ${res.statusText} - ${url}`);
  }
  return res.json() as Promise<T>;
}

function paginate<T>(
  payload: T[],
  params: string,
  pageSize: number,
): PaginatedResponse<T> {
  const searchParams = new URLSearchParams(params);
  const page = Math.max(1, parseInt(searchParams.get("page") ?? "1", 10) || 1);
  const start = (page - 1) * pageSize;

  return {
    count: payload.length,
    results: payload.slice(start, start + pageSize),
  };
}

export async function getServerVideos(params?: string) {
  const qs = params ? `?${params}` : "";
  return serverFetch<Video[]>(`/api/killtony/episodes/${qs}`);
}

export async function getServerVideo(slug: string) {
  return serverFetch<VideoDetail>(`/api/killtony/episodes/${slug}/`, { allowNotFound: true });
}

export async function getServerComedians(params?: string) {
  const qs = params ? `?${params}` : "";
  return serverFetch<Comedian[]>(`/api/killtony/comedians/${qs}`);
}

export async function getServerComedian(slug: string) {
  return serverFetch<ComedianDetail>(`/api/killtony/comedians/${slug}/`, { allowNotFound: true });
}

export async function getServerSet(slug: string) {
  return serverFetch<Set>(`/api/killtony/sets/${slug}/`, { allowNotFound: true });
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

export async function getServerSetsPaginated(params: string, pageSize: number) {
  const payload = await serverFetch<SetListItem[]>(`/api/killtony/sets/?${params}`);
  return paginate(payload, params, pageSize);
}

export async function getServerVideosPaginated(params: string, pageSize: number) {
  const payload = await serverFetch<Video[]>(`/api/killtony/episodes/?${params}`);
  return paginate(payload, params, pageSize);
}

export async function getServerComediansPaginated(params: string, pageSize: number) {
  const payload = await serverFetch<Comedian[]>(`/api/killtony/comedians/?${params}`);
  return paginate(payload, params, pageSize);
}

export async function getServerBeatsPaginated(params: string) {
  return serverFetch<PaginatedResponse<BeatSearchItem>>(`/api/killtony/jokes/?${params}`);
}

// --- types (minimal, expand as backend solidifies) ---

export type PaginatedResponse<T> = {
  results: T[];
  count: number;
};

export type Video = {
  id: number;
  slug: string;
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
export type SetInVideo = {
  id: number;
  slug: string;
  set_number: number;
  comedian: { id: number; name: string; slug: string; attributes: ComedianAttribute[]; image_url: string | null };
  attributes: string[];
  bit_count: number;
  start_seconds: number;
  interview_end_seconds: number | null;
  image_url: string | null;
  image_capture_seconds: number | null;
  punch_density: number | null;
  tag_density: number | null;
};

export type VideoDetail = {
  id: number;
  slug: string;
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
  view_like_ratio: number | null;
  sets: SetInVideo[];
};

export type Comedian = {
  id: number;
  name: string;
  slug: string;
  attributes: ComedianAttribute[];
  image_url: string | null;
  set_count: number;
  has_small_joke_book: boolean;
  has_medium_joke_book: boolean;
  has_large_joke_book: boolean;
  avg_punch_density: number | null;
  avg_tag_density: number | null;
  avg_bits_per_set: number | null;
  avg_beats_per_set: number | null;
};

export type SetInComedian = {
  id: number;
  slug: string;
  set_number: number;
  video: { id: number; slug: string; number: number; title: string; youtube_id: string; date: string | null };
  attributes: string[];
  start_seconds: number;
  punch_density: number | null;
  tag_density: number | null;
  bit_count: number;
  image_url: string | null;
  image_capture_seconds: number | null;
};

export type ComedianDetail = Comedian & {
  sets: SetInComedian[];
};

export type Beat = {
  id: number;
  beat_id: string;
  premise: string;
  joke_type: string;
  line_start: number;
  line_end: number;
  lines: Line[];
};

export type Line = {
  id: number;
  line_number: number;
  text: string;
  label: "setup" | "punchline" | "tag" | "fluff";
  start_seconds: number | null;
};

export type SetListItem = {
  id: number;
  slug: string;
  set_number: number;
  comedian: SetListComedian;
  video: { id: number; slug: string; number: number; title: string; youtube_id: string; date: string | null };
  attributes: string[];
  start_seconds: number;
  interview_end_seconds: number | null;
  image_url: string | null;
  image_capture_seconds: number | null;
  punch_density: number | null;
  tag_density: number | null;
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
  avg_punch_density: number | null;
  avg_tag_density: number | null;
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
  avg_bits_per_set: number | null;
  avg_beats_per_set: number | null;
  avg_punch_density: number | null;
  avg_tag_density: number | null;
  has_small_joke_book: boolean;
  has_medium_joke_book: boolean;
  has_large_joke_book: boolean;
};

export type Set = {
  id: number;
  slug: string;
  set_number: number;
  comedian: SetComedian;
  video: { id: number; slug: string; number: number; title: string; youtube_id: string; date: string | null };
  attributes: string[];
  start_seconds: number;
  image_url: string | null;
  image_capture_seconds: number | null;
  punch_density: number | null;
  tag_density: number | null;
  bits: Bit[];
  lines?: Line[];
};

export type Bit = {
  id: number;
  bit_id: string;
  line_start: number;
  line_end: number;
  beats: Beat[];
};

export type BitListItem = {
  id: number;
  comedian: string;
  comedian_slug: string;
  episode_number: number;
  set_slug: string;
  bit_id: string;
  joke_types: string[];
  beats: { beat_id: string; premise: string; joke_type: string }[];
  punch_density: number | null;
  tag_density: number | null;
};

export type BeatSearchItem = {
  id: number;
  beat_id: string;
  bit_id: string;
  comedian: string;
  comedian_slug: string;
  episode_number: number;
  set_slug: string;
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
  comedians: NavSearchResult[];
  episodes: NavSearchResult[];
  sets: NavSearchResult[];
  beats: NavSearchResult[];
};

