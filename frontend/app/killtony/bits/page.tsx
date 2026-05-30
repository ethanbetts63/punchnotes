import { Suspense } from "react";
import { getServerBits } from "@/lib/serverApi";
import BitsFilters from "@/components/BitsFilters";
import BitsList from "@/components/BitsList";
import BitPlaylists from "@/components/BitPlaylists";
import BrowseSearchBar from "@/components/BrowseSearchBar";

export const metadata = {
  title: "Bits — Kill Tony | PunchPedia",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function BitsPage({ searchParams }: Props) {
  const sp = await searchParams;
  const trimmedQuery = (sp.q ?? "").trim();
  const isFiltered = !!(trimmedQuery || sp.joke_type || sp.topic || sp.view);

  // In filtered mode pass all active params; in browse mode fetch all for playlists.
  const qs = isFiltered ? new URLSearchParams(sp).toString() : "";
  const bits = await getServerBits(qs);

  const filterKey = qs;

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-stone-900">Bits</h1>
          <p className="mt-2 text-stone-500">
            {bits ? `${bits.length} bit${bits.length !== 1 ? "s" : ""}` : ""}
            {trimmedQuery ? ` matching "${trimmedQuery}"` : ""}
            {sp.topic ? ` tagged "${sp.topic}"` : ""}
            {sp.joke_type ? ` · ${sp.joke_type}` : ""}
            {!bits ? "Loading…" : ""}
          </p>
        </div>

        <Suspense>
          <BrowseSearchBar placeholder="Search bits…" />
        </Suspense>

        <Suspense>
          <BitsFilters hideSearch />
        </Suspense>

        {isFiltered ? (
          !bits || bits.length === 0 ? (
            <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
              <p className="text-stone-500">No bits found.</p>
            </div>
          ) : (
            <Suspense>
              <BitsList bits={bits} filterKey={filterKey} />
            </Suspense>
          )
        ) : (
          bits && <BitPlaylists bits={bits} />
        )}
      </div>
    </div>
  );
}
