import { Suspense } from "react";
import { getServerVideos } from "@/lib/serverApi";
import VideoPlaylists from "@/components/VideoPlaylists";
import FilterControls from "@/components/FilterControls";
import { EPISODE_SEARCH_CONFIG } from "@/lib/searchConfigs";
import ListPageHeader from "@/components/ListPageHeader";

export const metadata = {
  title: "Episodes - Kill Tony | PunchNotes",
};

export default async function EpisodesBrowsePage() {
  const episodes = await getServerVideos();

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <Suspense>
          <ListPageHeader
            title="Episodes"
            searchPlaceholder="Search episodes..."
            searchPath="/killtony/episodes/search"
            controls={<FilterControls config={EPISODE_SEARCH_CONFIG} />}
          />
        </Suspense>
      </div>

      {episodes && (
        <div className="mx-auto max-w-6xl pb-12">
          <h2 className="mb-6 px-6 text-2xl font-bold tracking-tight text-stone-950">
            Episode playlists
          </h2>
          <VideoPlaylists episodes={episodes} />
        </div>
      )}
    </div>
  );
}
