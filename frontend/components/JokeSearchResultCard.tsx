"use client";

import type { BeatSearchItem, Set } from "@/lib/serverApi";
import AnnotatedBeatCard from "@/components/AnnotatedBeatCard";
import { beatSearchItemToCardData } from "@/lib/annotatedBeatCards";

export default function JokeSearchResultCard({ item, query, set }: { item: BeatSearchItem; query?: string; set?: Set }) {
  return (
    <AnnotatedBeatCard
      {...beatSearchItemToCardData(item, set)}
      query={query}
    />
  );
}
