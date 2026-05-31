import { Suspense } from "react";
import { getServerJokes, getServerTopics } from "@/lib/serverApi";
import JokesFilters from "@/components/JokesFilters";
import JokesList from "@/page_components/JokesList";

export const metadata = {
  title: "Jokes — Kill Tony | PunchPedia",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function JokesPage({ searchParams }: Props) {
  const sp = await searchParams;
  const qs = new URLSearchParams(sp).toString();
  const [jokes, topics] = await Promise.all([
    getServerJokes(qs),
    getServerTopics(),
  ]);

  const filterKey = qs;

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-stone-900">Jokes</h1>
          <p className="mt-2 text-stone-500">
            {jokes ? `${jokes.length} jokes` : ""}
            {sp.q ? ` matching "${sp.q}"` : ""}
            {sp.topic ? ` tagged "${sp.topic}"` : ""}
            {sp.joke_type ? ` · ${sp.joke_type}` : ""}
            {!jokes ? "Loading…" : ""}
          </p>
        </div>

        <Suspense>
          <JokesFilters topics={topics ?? []} />
        </Suspense>

        {!jokes ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No jokes found.</p>
          </div>
        ) : (
          <Suspense>
            <JokesList jokes={jokes} filterKey={filterKey} />
          </Suspense>
        )}
      </div>
    </div>
  );
}
