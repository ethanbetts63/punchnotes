import { BIT_LISTS } from "@/lib/playlists";
import { getServerBits, getServerSet, type Set } from "@/lib/serverApi";

const FEATURED_BIT_CANDIDATES = BIT_LISTS.flatMap((list) => list.ids);

export type FeaturedBeatEntry = {
  set: Set;
  bitIndex: number;
  beatIndex: number;
};

export async function getFeaturedBeatEntries(limit = 5): Promise<FeaturedBeatEntry[]> {
  const bits = await getServerBits();
  if (!bits?.length) return [];

  const candidateBits = [
    ...bits.filter((bit) => FEATURED_BIT_CANDIDATES.includes(bit.id)),
    ...bits.filter((bit) => !FEATURED_BIT_CANDIDATES.includes(bit.id)),
  ]
    .filter((bit) => bit.set_id != null)
    .slice(0, limit * 3);

  const setIds = [...new Set(candidateBits.map((bit) => bit.set_id))];
  const sets = await Promise.all(setIds.map((setId) => getServerSet(String(setId))));
  const setById = new Map(
    sets
      .filter((set): set is Set => set != null)
      .map((set) => [set.id, set])
  );

  const entries: FeaturedBeatEntry[] = [];
  for (const bit of candidateBits) {
    const set = setById.get(bit.set_id);
    if (!set) continue;

    const bitIndex = set.bits.findIndex((setBit) => setBit.id === bit.id);
    if (bitIndex < 0) continue;
    if ((set.bits[bitIndex]?.beats.length ?? 0) === 0) continue;

    entries.push({ set, bitIndex, beatIndex: 0 });
    if (entries.length >= limit) break;
  }

  return entries;
}
