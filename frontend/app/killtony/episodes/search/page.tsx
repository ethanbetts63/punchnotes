import { Suspense } from "react";
import Link from "next/link";
import { getServerEpisodes } from "@/lib/serverApi";
import BrowseSearchBar from "@/components/BrowseSearchBar";
import EpisodeSearchFilters from "@/components/EpisodeSearchFilters";
import EpisodeList from "@/page_components/EpisodeList";

export const metadata = {
  title: "Search Episodes — Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function EpisodeSearchPage({ searchParams }: Props) {
  const sp = await searchParams;
  const qs = new URLSearchParams(sp).toString();
  const episodes = await getServerEpisodes(qs || undefined);
  const trimmedQuery = (sp.q ?? "").trim();

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <Link
          href="/killtony/episodes"
          className="mb-6 inline-flex items-center gap-1.5 text-sm font-medium text-stone-500 transition-colors hover:text-stone-900"
        >
          ← Episodes
        </Link>

        <div className="mb-6 mt-4">
          <h1 className="text-3xl font-bold text-stone-900">Search Episodes</h1>
          <p className="mt-2 text-stone-500">
            {episodes
              ? `${episodes.length} episode${episodes.length !== 1 ? "s" : ""}${trimmedQuery ? ` matching "${trimmedQuery}"` : ""}`
              : "Loading…"}
          </p>
        </div>

        <Suspense>
          <BrowseSearchBar placeholder="Search episodes…" />
        </Suspense>

        <Suspense>
          <EpisodeSearchFilters />
        </Suspense>

        {!episodes || episodes.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No episodes found.</p>
          </div>
        ) : (
          <Suspense>
            <EpisodeList episodes={episodes} filterKey={qs} />
          </Suspense>
        )}
      </div>
    </div>
  );
}
