import { Suspense } from "react";
import { getServerBits } from "@/lib/serverApi";
import BitPlaylists from "@/page_components/BitPlaylists";
import BrowseSearchBar from "@/components/BrowseSearchBar";
import BitSearchFilters from "@/components/BitSearchFilters";

export const metadata = {
  title: "Jokes - Kill Tony | PunchNotes",
};

export default async function BitsPage() {
  const bits = await getServerBits();

  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-stone-900">Jokes</h1>
          <p className="mt-2 text-stone-500">
            Browse joke cards from the archive, then jump into the full set with the selected beat highlighted.
          </p>
        </div>

        <Suspense>
          <BrowseSearchBar
            placeholder="Search jokes..."
            searchPath="/killtony/bits/search"
          />
        </Suspense>

        <Suspense>
          <BitSearchFilters />
        </Suspense>

        {bits && <BitPlaylists bits={bits} />}
      </div>
    </div>
  );
}
