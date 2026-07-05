import type { ReactNode } from "react";
import AnnotatedBeatCarousel from "@/components/AnnotatedBeatCarousel";
import type { FeaturedBeatEntry } from "@/lib/featuredBeats";

type Props = FeaturedBeatEntry & {
  entries?: FeaturedBeatEntry[];
  sidebar?: ReactNode;
};

export default function BeatOfTheWeek({ set, bitIndex, beatIndex, entries, sidebar }: Props) {
  const beatEntries = [{ set, bitIndex, beatIndex }, ...(entries ?? [])];

  return (
    <section className="bg-white">
      <div className="flex items-start gap-6">
        <div className="min-w-0 flex-1">
          <AnnotatedBeatCarousel
            title="Featured Jokes"
            description="Every set is annotated line by line, from setup to punchline to tag, with the joke type called out on each beat."
            entries={beatEntries}
            headingClassName="text-3xl font-bold tracking-tight sm:text-4xl"
          />
        </div>
        {sidebar && (
          <div className="hidden w-72 shrink-0 lg:block">{sidebar}</div>
        )}
      </div>
    </section>
  );
}
