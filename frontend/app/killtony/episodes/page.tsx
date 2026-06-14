import { Suspense } from "react";
import { getServerVideos } from "@/lib/serverApi";
import EpisodePlaylists from "@/components/EpisodePlaylists";
import EpisodeSearchFilters from "@/components/EpisodeSearchFilters";
import ListPageHeader from "@/components/ListPageHeader";

export const metadata = {
  title: "Episodes - Kill Tony | PunchNotes",
};

export default async function EpisodesBrowsePage() {
  const episodes = await getServerVideos();

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <Suspense>
          <ListPageHeader
            title="Episodes"
            searchPlaceholder="Search episodes..."
            searchPath="/killtony/episodes/search"
            controls={<EpisodeSearchFilters />}
          />
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
