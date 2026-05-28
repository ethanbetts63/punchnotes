import Link from "next/link";
import { Suspense } from "react";
import { getServerJokes, getServerTopics } from "@/lib/serverApi";
import { Badge } from "@/components/ui/badge";
import JokesFilters from "@/components/JokesFilters";

export const metadata = {
  title: "Jokes — Kill Tony | JokeScore",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function JokesPage({ searchParams }: Props) {
  const sp = await searchParams;
  const qs = new URLSearchParams(sp).toString();
  const [jokes, topics] = await Promise.all([
    getServerJokes(qs),
    getServerTopics(),
  ]);

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-stone-900">Jokes</h1>
          <p className="mt-2 text-stone-500">
            {jokes ? `${jokes.length} jokes` : ""}
            {sp.topic ? ` tagged "${sp.topic}"` : ""}
            {sp.joke_type ? ` · ${sp.joke_type}` : ""}
            {!jokes ? "Loading…" : ""}
          </p>
        </div>

        <Suspense>
          <JokesFilters topics={topics ?? []} />
        </Suspense>

        {!jokes || jokes.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No jokes found.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {jokes.map((joke) => (
              <Link
                key={joke.id}
                href={`/killtony/sets/${joke.set_id}`}
                className="group block rounded-xl border border-stone-200 bg-white p-5 hover:border-primary/40 hover:shadow-sm transition-all"
              >
                <div className="mb-3 flex flex-wrap items-center gap-2">
                  <span className="text-sm font-semibold text-stone-900 group-hover:text-primary transition-colors">
                    {joke.comedian}
                  </span>
                  <span className="text-stone-300">·</span>
                  <span className="text-xs text-stone-400">Ep {joke.episode_number}</span>
                  <Badge variant="default">{joke.joke_type}</Badge>
                  {joke.topics.map((t) => (
                    <Badge key={t} variant="stone">{t}</Badge>
                  ))}
                </div>
                {joke.premise && (
                  <p className="mb-3 text-sm italic text-stone-500">"{joke.premise}"</p>
                )}
                <div className="space-y-1">
                  {joke.setup_lines.map((line, i) => (
                    <p key={i} className="text-sm text-stone-600">{line}</p>
                  ))}
                  {joke.punchline && (
                    <p className="font-semibold text-stone-900">{joke.punchline}</p>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
