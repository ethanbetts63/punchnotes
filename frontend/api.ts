import { authedFetch } from "@/apiClient";
import type { BeatSearchItem, Comedian, Video, Set } from "@/lib/serverApi";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status}: ${text}`);
  }
  if (res.status === 204) return null as T;
  return res.json() as Promise<T>;
}

export async function getVideos(): Promise<Video[]> {
  const res = await authedFetch("/api/killtony/episodes/");
  return handleResponse<Video[]>(res);
}

export async function getVideo(slug: string): Promise<Video> {
  const res = await authedFetch(`/api/killtony/episodes/${slug}/`);
  return handleResponse<Video>(res);
}

export async function getComedians(): Promise<Comedian[]> {
  const res = await authedFetch("/api/killtony/comedians/");
  return handleResponse<Comedian[]>(res);
}

export async function getComedian(slug: string): Promise<Comedian> {
  const res = await authedFetch(`/api/killtony/comedians/${slug}/`);
  return handleResponse<Comedian>(res);
}

export async function getSet(slug: string): Promise<Set> {
  const res = await authedFetch(`/api/killtony/sets/${slug}/`);
  return handleResponse<Set>(res);
}

export async function searchJokes(params: Record<string, string>): Promise<BeatSearchItem[]> {
  const qs = new URLSearchParams(params).toString();
  const res = await authedFetch(`/api/killtony/jokes/?${qs}`);
  return handleResponse<BeatSearchItem[]>(res);
}
