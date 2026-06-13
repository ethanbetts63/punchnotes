import { Suspense } from "react";
import { getServerBeats } from "@/lib/serverApi";
import JokesFilters from "@/components/JokesFilters";
import JokesList from "@/page_components/JokesList";

export const metadata = {
  title: "Jokes - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function JokesPage({ searchParams }: Props) {
  const sp = await searchParams;
  const qs = new URLSearchParams(sp).toString();
  const beats = await getServerBeats(qs);
  const query = (sp.q ?? "").trim();

  const filterKey = qs;

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-stone-900">Jokes</h1>
          <p className="mt-2 text-stone-500">
            {beats ? `${beats.length} jokes` : ""}
            {sp.q ? ` matching "${sp.q}"` : ""}
            {sp.joke_type ? ` · ${sp.joke_type}` : ""}
            {!beats ? "Loading..." : ""}
          </p>
        </div>

        <Suspense>
          <JokesFilters />
        </Suspense>

        {!beats ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No jokes found.</p>
          </div>
        ) : (
          <Suspense>
            <JokesList beats={beats} filterKey={filterKey} query={query} />
          </Suspense>
        )}
      </div>
    </div>
  );
}
