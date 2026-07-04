import { FEATURED_BEATS } from "@/lib/playlists";
import { getServerSet, type Set } from "@/lib/serverApi";

export type FeaturedBeatEntry = {
  set: Set;
  bitIndex: number;
  beatIndex: number;
};

export async function getFeaturedBeatEntries(limit = 5): Promise<FeaturedBeatEntry[]> {
  const candidates = FEATURED_BEATS.slice(0, limit * 2);
  const sets = await Promise.all(candidates.map((c) => getServerSet(c.setSlug)));

  const entries: FeaturedBeatEntry[] = [];
  const seen = new Set<string>();
  for (let i = 0; i < candidates.length; i++) {
    const set = sets[i];
    if (!set) continue;
    const { bitIndex, beatIndex } = candidates[i];
    if (!set.bits[bitIndex]?.beats[beatIndex]) continue;
    const key = `${set.id}:${bitIndex}:${beatIndex}`;
    if (seen.has(key)) continue;
    seen.add(key);
    entries.push({ set, bitIndex, beatIndex });
    if (entries.length >= limit) break;
  }
  return entries;
}
