import { Suspense } from "react";
import { getServerComedians } from "@/lib/serverApi";
import ComedianFilters from "@/components/ComedianFilters";
import ComedianList from "@/components/ComedianList";
import ComedianPlaylists from "@/components/ComedianPlaylists";
import BrowseSearchBar from "@/components/BrowseSearchBar";

export const metadata = {
  title: "Comedians — Kill Tony | PunchPedia",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function ComediansPage({ searchParams }: Props) {
  const sp = await searchParams;
  const trimmedQuery = (sp.q ?? "").trim();
  const isFiltered = !!(trimmedQuery || sp.attribute || sp.joke_book);

  const qs = isFiltered ? new URLSearchParams(sp).toString() : "";
  const comedians = await getServerComedians(qs || undefined);

  const filterKey = qs;

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-stone-900">Comedians</h1>
          <p className="mt-2 text-stone-500">
            {comedians ? `${comedians.length} comedian${comedians.length !== 1 ? "s" : ""}` : ""}
            {trimmedQuery ? ` matching "${trimmedQuery}"` : ""}
            {sp.attribute ? ` · ${sp.attribute.replace(/_/g, " ")}` : ""}
            {sp.joke_book ? ` · ${sp.joke_book} joke book` : ""}
            {!comedians ? "Loading…" : ""}
          </p>
        </div>

        <Suspense>
          <BrowseSearchBar placeholder="Search comedians…" />
        </Suspense>

        <Suspense>
          <ComedianFilters />
        </Suspense>

        {isFiltered ? (
          !comedians || comedians.length === 0 ? (
            <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
              <p className="text-stone-500">No comedians found.</p>
            </div>
          ) : (
            <Suspense>
              <ComedianList comedians={comedians} filterKey={filterKey} />
            </Suspense>
          )
        ) : (
          comedians && <ComedianPlaylists comedians={comedians} />
        )}
      </div>
    </div>
  );
}
