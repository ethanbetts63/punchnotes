import type { BitListItem } from "@/lib/serverApi";

export function buildBitSetHref(bit: BitListItem, beatIndex = 0): string {
  return `/killtony/sets/${bit.set_id}?bit=${bit.id}&beat=${beatIndex}`;
}
