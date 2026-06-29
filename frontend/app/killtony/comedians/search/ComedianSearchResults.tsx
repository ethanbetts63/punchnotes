import type { Comedian } from "@/lib/serverApi";
import { formatAttributeLabels } from "@/lib/attributes";
import { fmt2 } from "@/lib/killTonyDisplay";
import ComedianImage from "@/components/ComedianImage";
import SearchResultTile from "@/components/SearchResultTile";

export default function ComedianSearchResults({ comedians }: { comedians: Comedian[] }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {comedians.map((comedian) => (
        <SearchResultTile
          key={comedian.id}
          href={`/killtony/comedians/${comedian.slug}`}
          title={comedian.name}
          subtitle={formatAttributeLabels(comedian.attributes)}
          image={
            <ComedianImage
              imageUrl={comedian.image_url}
              name={comedian.name}
              className="absolute inset-0 h-full w-full"
            />
          }
          meta={
            <>
              {comedian.set_count} set{comedian.set_count !== 1 ? "s" : ""}
            </>
          }
          stats={[
            ...(comedian.avg_bits_per_set != null
              ? [{ label: "Bits/set", value: fmt2(comedian.avg_bits_per_set) }]
              : []),
            ...(comedian.avg_beats_per_set != null
              ? [{ label: "Beats/set", value: fmt2(comedian.avg_beats_per_set) }]
              : []),
            ...(comedian.avg_punch_density != null
              ? [{ label: "Punch density", value: fmt2(comedian.avg_punch_density) }]
              : []),
            ...(comedian.avg_tag_density != null
              ? [{ label: "Tag density", value: fmt2(comedian.avg_tag_density) }]
              : []),
          ]}
          badges={
            <>
              {comedian.has_small_joke_book && (
                <span className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-bold text-stone-600">
                  Small Joke Book
                </span>
              )}
              {comedian.has_medium_joke_book && (
                <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-700">
                  Medium Joke Book
                </span>
              )}
              {comedian.has_large_joke_book && (
                <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700">
                  Big Joke Book
                </span>
              )}
            </>
          }
        />
      ))}
    </div>
  );
}
