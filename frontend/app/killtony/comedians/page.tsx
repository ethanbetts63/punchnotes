import { Suspense } from "react";
import { getServerComedians } from "@/lib/serverApi";
import ComedianPlaylists from "@/components/ComedianPlaylists";
import BrowseSearchBar from "@/components/BrowseSearchBar";
import ComedianSearchFilters from "@/components/ComedianSearchFilters";

export const metadata = {
  title: "Comedians — Kill Tony | PunchPedia",
};

export default async function ComediansPage() {
  const comedians = await getServerComedians();

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-stone-900">Comedians</h1>
        </div>

        <Suspense>
          <BrowseSearchBar
            placeholder="Search comedians…"
            searchPath="/killtony/comedians/search"
          />
        </Suspense>

        <Suspense>
          <ComedianSearchFilters />
        </Suspense>

        {comedians && <ComedianPlaylists comedians={comedians} />}
      </div>
    </div>
  );
}
