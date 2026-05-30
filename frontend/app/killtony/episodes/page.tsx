import { Suspense } from "react";
import { getServerEpisodes } from "@/lib/serverApi";
import EpisodeList from "@/components/EpisodeList";
import EpisodePlaylists from "@/components/EpisodePlaylists";
import BrowseSearchBar from "@/components/BrowseSearchBar";

export const metadata = {
  title: "Episodes — Kill Tony | PunchPedia",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function EpisodesPage({ searchParams }: Props) {
  const sp = await searchParams;
  const trimmedQuery = (sp.q ?? "").trim();
  const isFiltered = !!trimmedQuery;

  const qs = isFiltered ? new URLSearchParams(sp).toString() : "";
  const episodes = await getServerEpisodes(qs || undefined);

  const filterKey = qs;

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-stone-900">Episodes</h1>
          <p className="mt-2 text-stone-500">
            {episodes ? `${episodes.length} episode${episodes.length !== 1 ? "s" : ""}` : ""}
            {trimmedQuery ? ` matching "${trimmedQuery}"` : ""}
            {!episodes ? "Loading…" : ""}
          </p>
        </div>

        <Suspense>
          <BrowseSearchBar placeholder="Search episodes…" />
        </Suspense>

        {isFiltered ? (
          !episodes || episodes.length === 0 ? (
            <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
              <p className="text-stone-500">No episodes found.</p>
            </div>
          ) : (
            <Suspense>
              <EpisodeList episodes={episodes} filterKey={filterKey} />
            </Suspense>
          )
        ) : (
          episodes && <EpisodePlaylists episodes={episodes} />
        )}
      </div>
    </div>
  );
}
