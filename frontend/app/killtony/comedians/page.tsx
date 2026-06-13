import { Suspense } from "react";
import { getServerComedians } from "@/lib/serverApi";
import ComedianPlaylists from "@/page_components/ComedianPlaylists";
import ComedianSearchFilters from "@/components/ComedianSearchFilters";
import ListPageHeader from "@/components/ListPageHeader";

export const metadata = {
  title: "Comedians - Kill Tony | PunchNotes",
};

export default async function ComediansBrowsePage() {
  const comedians = await getServerComedians();

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <Suspense>
          <ListPageHeader
            title="Comedians"
            searchPlaceholder="Search comedians..."
            searchPath="/killtony/comedians/search"
            controls={<ComedianSearchFilters />}
          />
        </Suspense>
      </div>

      {comedians && (
        <div className="mx-auto max-w-6xl pb-12">
          <ComedianPlaylists comedians={comedians} />
        </div>
      )}
    </div>
  );
}
