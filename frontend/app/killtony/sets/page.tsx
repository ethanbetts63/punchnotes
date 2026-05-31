import { Suspense } from "react";
import { getServerSets } from "@/lib/serverApi";
import SetPlaylists from "@/components/SetPlaylists";
import BrowseSearchBar from "@/components/BrowseSearchBar";
import SetSearchFilters from "@/components/SetSearchFilters";

export const metadata = {
  title: "Sets — Kill Tony | PunchPedia",
};

export default async function SetsPage() {
  const sets = await getServerSets();

  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-stone-900">Sets</h1>
        </div>

        <Suspense>
          <BrowseSearchBar
            placeholder="Search sets…"
            searchPath="/killtony/sets/search"
          />
        </Suspense>

        <Suspense>
          <SetSearchFilters />
        </Suspense>

        {sets && <SetPlaylists sets={sets} />}
      </div>
    </div>
  );
}
