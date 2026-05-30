import { Suspense } from "react";
import { getServerSets } from "@/lib/serverApi";
import SetFilters from "@/components/SetFilters";
import SetList from "@/components/SetList";
import SetPlaylists from "@/components/SetPlaylists";
import BrowseSearchBar from "@/components/BrowseSearchBar";

export const metadata = {
  title: "Sets — Kill Tony | PunchPedia",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function SetsPage({ searchParams }: Props) {
  const sp = await searchParams;
  const trimmedQuery = (sp.q ?? "").trim();
  const isFiltered = !!(trimmedQuery || sp.attribute || sp.joke_book || sp.view);

  const qs = isFiltered ? new URLSearchParams(sp).toString() : "";
  const sets = await getServerSets(qs || undefined);

  const filterKey = qs;

  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-stone-900">Sets</h1>
          <p className="mt-2 text-stone-500">
            {sets ? `${sets.length} set${sets.length !== 1 ? "s" : ""}` : ""}
            {trimmedQuery ? ` matching "${trimmedQuery}"` : ""}
            {sp.attribute ? ` · ${sp.attribute.replace(/_/g, " ")}` : ""}
            {sp.joke_book ? ` · ${sp.joke_book} joke book` : ""}
            {!sets ? "Loading…" : ""}
          </p>
        </div>

        <Suspense>
          <BrowseSearchBar placeholder="Search sets…" />
        </Suspense>

        <Suspense>
          <SetFilters />
        </Suspense>

        {isFiltered ? (
          !sets || sets.length === 0 ? (
            <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
              <p className="text-stone-500">No sets found.</p>
            </div>
          ) : (
            <Suspense>
              <SetList sets={sets} filterKey={filterKey} />
            </Suspense>
          )
        ) : (
          sets && <SetPlaylists sets={sets} />
        )}
      </div>
    </div>
  );
}
