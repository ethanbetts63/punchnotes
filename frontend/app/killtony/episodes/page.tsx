import { Suspense } from "react";
import { getServerEpisodes } from "@/lib/serverApi";
import EpisodePlaylists from "@/page_components/EpisodePlaylists";
import BrowseSearchBar from "@/components/BrowseSearchBar";
import EpisodeSearchFilters from "@/components/EpisodeSearchFilters";

export const metadata = {
  title: "Episodes — Kill Tony | PunchNotes",
};

export default async function EpisodesPage() {
  const episodes = await getServerEpisodes();

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-stone-900">Episodes</h1>
        </div>

        <Suspense>
          <BrowseSearchBar
            placeholder="Search episodes…"
            searchPath="/killtony/episodes/search"
          />
        </Suspense>

        <Suspense>
          <EpisodeSearchFilters />
        </Suspense>
      </div>

      {episodes && (
        <div className="mx-auto max-w-6xl pb-12">
          <EpisodePlaylists episodes={episodes} />
        </div>
      )}
    </div>
  );
}
