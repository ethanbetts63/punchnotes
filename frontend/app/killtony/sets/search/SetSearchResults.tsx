import type { SetListItem } from "@/lib/serverApi";
import { ATTRIBUTE_LABELS } from "@/lib/attributes";
import { fmt2, fmtSeconds, getJokeBookSize, jokeBookLabel } from "@/lib/killTonyDisplay";
import SetImage from "@/components/SetImage";
import SearchResultTile from "@/components/SearchResultTile";

function comedianAttributes(set: SetListItem): string | undefined {
  const labels = (set.comedian.attributes as string[])
    .filter((attr) => attr in ATTRIBUTE_LABELS)
    .map((attr) => ATTRIBUTE_LABELS[attr]);
  return labels.length > 0 ? labels.join(" / ") : undefined;
}

export default function SetSearchResults({ sets }: { sets: SetListItem[] }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {sets.map((set) => {
        const jokeBook = getJokeBookSize(set.attributes);

        return (
          <SearchResultTile
            key={set.id}
            href={`/killtony/sets/${set.slug}`}
            eyebrow={`KT #${set.video.number}`}
            title={set.comedian.name}
            subtitle={set.video.title}
            image={
              <SetImage
                imageUrl={set.image_url}
                fallbackVideoId={set.video.youtube_id}
                alt={`${set.comedian.name} set image`}
                className="absolute inset-0 h-full w-full"
              />
            }
            meta={
              <>
                Set {set.set_number} / {fmtSeconds(set.start_seconds)}
                {comedianAttributes(set) ? ` / ${comedianAttributes(set)}` : ""}
              </>
            }
            stats={[
              { label: "Bits", value: set.bit_count },
              { label: "Punch density", value: fmt2(set.punch_density) },
              { label: "Tag density", value: fmt2(set.tag_density) },
            ]}
            badges={
              jokeBook ? (
                <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-700">
                  {jokeBookLabel[jokeBook]}
                </span>
              ) : undefined
            }
          />
        );
      })}
    </div>
  );
}
