import { FEATURED_BEATS } from "@/lib/playlists";
import { getServerSet, type Set } from "@/lib/serverApi";

export type FeaturedBeatEntry = {
  set: Set;
  bitIndex: number;
  beatIndex: number;
};

export async function getFeaturedBeatEntries(limit = 5): Promise<FeaturedBeatEntry[]> {
  const candidates = FEATURED_BEATS.slice(0, limit * 2);
  const sets = await Promise.all(candidates.map((c) => getServerSet(String(c.setId))));

  const entries: FeaturedBeatEntry[] = [];
  for (let i = 0; i < candidates.length; i++) {
    const set = sets[i];
    if (!set) continue;
    const { bitIndex, beatIndex } = candidates[i];
    if (!set.bits[bitIndex]?.beats[beatIndex]) continue;
    entries.push({ set, bitIndex, beatIndex });
    if (entries.length >= limit) break;
  }
  return entries;
}
