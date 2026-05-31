import { Suspense } from "react";
import { getServerBits } from "@/lib/serverApi";
import BitPlaylists from "@/page_components/BitPlaylists";
import BrowseSearchBar from "@/components/BrowseSearchBar";
import BitSearchFilters from "@/components/BitSearchFilters";

export const metadata = {
  title: "Bits — Kill Tony | PunchNotes",
};

export default async function BitsPage() {
  const bits = await getServerBits();

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-stone-900">Bits</h1>
        </div>

        <Suspense>
          <BrowseSearchBar
            placeholder="Search bits…"
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
