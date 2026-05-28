import Link from "next/link";
import { getServerJokes } from "@/lib/serverApi";
import { Badge } from "@/components/ui/badge";

export const metadata = {
  title: "Jokes — Kill Tony | JokeScore",
};

type Props = { searchParams: Promise<Record<string, string>> };

const JOKE_TYPES = [
  "misdirect", "reframe", "phonetic-match", "double-meaning",
  "analogy", "hyperbole", "elephant-in-the-room",
];

export default async function JokesPage({ searchParams }: Props) {
  const sp = await searchParams;
  const qs = new URLSearchParams(sp).toString();
  const jokes = await getServerJokes(qs);

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-stone-900">Jokes</h1>
          <p className="mt-2 text-stone-500">Search every joke by premise, topic, or mechanism.</p>
        </div>

        {/* Filter chips */}
        <div className="mb-6 flex flex-wrap gap-2">
          <Link
            href="/killtony/jokes"
            className={`rounded-full px-3 py-1 text-xs font-medium border transition-colors ${
              !sp.joke_type
                ? "bg-stone-900 text-white border-stone-900"
                : "bg-white text-stone-600 border-stone-200 hover:border-stone-400"
            }`}
          >
            All types
          </Link>
          {JOKE_TYPES.map((jt) => (
            <Link
              key={jt}
              href={`/killtony/jokes?joke_type=${jt}`}
              className={`rounded-full px-3 py-1 text-xs font-medium border transition-colors ${
                sp.joke_type === jt
                  ? "bg-primary text-white border-primary"
                  : "bg-white text-stone-600 border-stone-200 hover:border-stone-400"
              }`}
            >
              {jt}
            </Link>
          ))}
        </div>

        {!jokes || jokes.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No jokes indexed yet.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {jokes.map((joke) => (
              <div
                key={joke.id}
                className="rounded-xl border border-stone-200 bg-white p-5"
              >
                <div className="mb-3 flex flex-wrap items-center gap-2">
                  <Link
                    href={`/killtony/comedians/${joke.comedian_slug}`}
                    className="text-sm font-semibold text-stone-900 hover:text-primary transition-colors"
                  >
                    {joke.comedian}
                  </Link>
                  <span className="text-stone-300">·</span>
                  <Link
                    href={`/killtony/sets/${joke.set_id}`}
                    className="text-xs text-stone-400 hover:text-stone-600 transition-colors"
                  >
                    Ep {joke.episode_number}
                  </Link>
                  <Badge variant="default">{joke.joke_type}</Badge>
                  {joke.topics.map((t) => (
                    <Badge key={t} variant="stone">{t}</Badge>
                  ))}
                </div>
                <p className="mb-3 text-sm italic text-stone-500">"{joke.premise}"</p>
                <div className="space-y-1">
                  {joke.setup_lines.map((line, i) => (
                    <p key={i} className="text-sm text-stone-600">{line}</p>
                  ))}
                  <p className="font-semibold text-stone-900">{joke.punchline}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
