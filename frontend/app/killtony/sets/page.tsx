import { Suspense } from "react";
import { getServerSets } from "@/lib/serverApi";
import SetPlaylists from "./SetPlaylists";
import SetSearchFilters from "@/components/SetSearchFilters";
import ListPageHeader from "@/components/ListPageHeader";

export const metadata = {
  title: "Sets - Kill Tony | PunchNotes",
};

export default async function SetsBrowsePage() {
  const sets = await getServerSets();

  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <Suspense>
          <ListPageHeader
            title="Sets"
            searchPlaceholder="Search sets..."
            searchPath="/killtony/sets/search"
            controls={<SetSearchFilters />}
          />
        </Suspense>
      </div>

      {sets && (
        <div className="mx-auto max-w-6xl pb-12">
          <SetPlaylists sets={sets} />
        </div>
      )}
    </div>
  );
}
