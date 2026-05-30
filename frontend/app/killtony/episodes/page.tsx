import { Suspense } from "react";
import { getServerEpisodes } from "@/lib/serverApi";
import EpisodeControls from "@/components/EpisodeControls";
import EpisodePlaylists from "@/components/EpisodePlaylists";
import BrowseSearchBar from "@/components/BrowseSearchBar";

export const metadata = {
  title: "Episodes — Kill Tony | PunchPedia",
};

type Props = { searchParams: Promise<Record<string, string | string[] | undefined>> };

export default async function EpisodesPage({ searchParams }: Props) {
  const params = await searchParams;
  const rawQuery = params.q;
  const query = Array.isArray(rawQuery) ? rawQuery[0] ?? "" : rawQuery ?? "";
  const trimmedQuery = query.trim();
  const episodes = await getServerEpisodes();

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-stone-900">Episodes</h1>
          <p className="mt-2 text-stone-500">
            {episodes ? `${episodes.length} episodes indexed` : "Loading episodes…"}
          </p>
        </div>

        {!episodes || episodes.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No episodes indexed yet.</p>
          </div>
        ) : (
          <>
            <Suspense>
              <BrowseSearchBar placeholder={`Search ${episodes.length} episodes…`} />
            </Suspense>
            {trimmedQuery ? (
              <Suspense>
                <EpisodeControls episodes={episodes} initialQuery={trimmedQuery} hideSearch />
              </Suspense>
            ) : (
              <EpisodePlaylists episodes={episodes} />
            )}
          </>
        )}
      </div>
    </div>
  );
}
