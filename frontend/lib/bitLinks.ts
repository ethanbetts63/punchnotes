import type { Beat, BeatSearchItem, Bit, BitListItem, Set } from "@/lib/serverApi";

export function compactOrdinalId(value: string): string {
  const match = value.match(/(\d+)$/);
  return match ? match[1].padStart(3, "0") : value;
}

export function buildBitSetHref(bit: BitListItem, beatIndex = 0): string {
  const beat = bit.beats[beatIndex];
  const params = new URLSearchParams({ bit: compactOrdinalId(bit.bit_id) });
  if (beat) params.set("beat", compactOrdinalId(beat.beat_id));
  return `/killtony/sets/${bit.set_slug}?${params.toString()}`;
}

export function buildBeatSearchHref(beat: BeatSearchItem): string {
  const params = new URLSearchParams({
    bit: compactOrdinalId(beat.bit_id),
    beat: compactOrdinalId(beat.beat_id),
  });
  return `/killtony/sets/${beat.set_slug}?${params.toString()}`;
}

export function buildSetBeatHref(set: Set, bit: Bit, beat: Beat): string {
  const params = new URLSearchParams({
    bit: compactOrdinalId(bit.bit_id),
    beat: compactOrdinalId(beat.beat_id),
  });
  return `/killtony/sets/${set.slug}?${params.toString()}`;
}
