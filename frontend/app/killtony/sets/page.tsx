import { Suspense } from "react";
import { getServerSets } from "@/lib/serverApi";
import SetControls from "@/components/SetControls";
import SetPlaylists from "@/components/SetPlaylists";
import BrowseSearchBar from "@/components/BrowseSearchBar";

export const metadata = {
  title: "Sets - Kill Tony | PunchPedia",
};

type Props = { searchParams: Promise<Record<string, string | string[] | undefined>> };

export default async function SetsPage({ searchParams }: Props) {
  const params = await searchParams;
  const rawQuery = params.q;
  const query = Array.isArray(rawQuery) ? rawQuery[0] ?? "" : rawQuery ?? "";
  const trimmedQuery = query.trim();
  const sets = await getServerSets();

  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-stone-900">Sets</h1>
          <p className="mt-2 text-stone-500">
            {sets ? `${sets.length} sets indexed` : "Loading sets..."}
          </p>
        </div>

        {!sets || sets.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No sets indexed yet.</p>
          </div>
        ) : (
          <>
            <Suspense>
              <BrowseSearchBar placeholder={`Search ${sets.length} sets…`} />
            </Suspense>
            <Suspense>
              <SetControls sets={sets} initialQuery={trimmedQuery} hideSearch>
                <SetPlaylists sets={sets} />
              </SetControls>
            </Suspense>
          </>
        )}
      </div>
    </div>
  );
}
