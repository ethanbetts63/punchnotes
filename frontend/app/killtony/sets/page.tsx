import { Suspense } from "react";
import { getServerSets } from "@/lib/serverApi";
import SetPlaylists from "./SetPlaylists";
import FilterControls from "@/components/FilterControls";
import { SET_SEARCH_CONFIG } from "@/lib/searchConfigs";
import ListPageHeader from "@/components/ListPageHeader";

export const metadata = {
  title: "Sets - Kill Tony | PunchNotes",
};

export default async function SetsBrowsePage() {
  const sets = await getServerSets();

  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <Suspense>
          <ListPageHeader
            title="Sets"
            searchPlaceholder="Search sets..."
            searchPath="/killtony/sets/search"
            controls={<FilterControls config={SET_SEARCH_CONFIG} />}
          />
        </Suspense>
      </div>

      {sets && (
        <div className="mx-auto max-w-6xl pb-12">
          <h2 className="mb-6 px-6 text-2xl font-bold tracking-tight text-stone-950">
            Set playlists
          </h2>
          <SetPlaylists sets={sets} />
        </div>
      )}
    </div>
  );
}
