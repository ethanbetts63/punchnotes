import Link from "next/link";
import { getServerSearch, type SearchResult } from "@/lib/serverApi";

export const metadata = {
  title: "Search - Kill Tony | PunchPedia",
};

type Props = { searchParams: Promise<Record<string, string | string[] | undefined>> };

const GROUPS: { key: string; title: string }[] = [
  { key: "comedians", title: "Comedians" },
  { key: "episodes", title: "Episodes" },
  { key: "sets", title: "Sets" },
  { key: "bits", title: "Bits" },
  { key: "jokes", title: "Jokes" },
  { key: "topics", title: "Topics" },
];

function typeLabel(type: SearchResult["type"]): string {
  switch (type) {
    case "comedian": return "Comedian";
    case "episode": return "Episode";
    case "set": return "Set";
    case "bit": return "Bit";
    case "joke": return "Joke";
    case "topic": return "Topic";
  }
}

function ResultRow({ item }: { item: SearchResult }) {
  return (
    <Link
      href={item.href}
      className="group block border-t border-stone-200 px-4 py-3 transition-colors first:border-t-0 hover:bg-stone-50"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded bg-stone-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-stone-500">
              {typeLabel(item.type)}
            </span>
            <p className="truncate text-sm font-semibold text-stone-900 transition-colors group-hover:text-primary">
              {item.title}
            </p>
          </div>
          {item.subtitle && (
            <p className="mt-1 truncate text-xs text-stone-500">{item.subtitle}</p>
          )}
          {item.meta.length > 0 && (
            <p className="mt-1 flex flex-wrap gap-x-2 gap-y-0.5 text-xs text-stone-400">
              {item.meta.map((meta) => (
                <span key={meta}>{meta}</span>
              ))}
            </p>
          )}
        </div>
        <span className="mt-1 shrink-0 text-stone-300 transition-colors group-hover:text-stone-500">
          &rarr;
        </span>
      </div>
    </Link>
  );
}

function ResultSection({ title, items }: { title: string; items: SearchResult[] }) {
  if (items.length === 0) return null;

  return (
    <section className="rounded-lg border border-stone-200 bg-white">
      <div className="flex items-center justify-between border-b border-stone-200 px-4 py-3">
        <h2 className="text-sm font-bold uppercase tracking-wide text-stone-900">{title}</h2>
        <span className="text-xs text-stone-400">{items.length}</span>
      </div>
      <div>
        {items.map((item) => (
          <ResultRow key={`${item.type}-${item.href}-${item.title}`} item={item} />
        ))}
      </div>
    </section>
  );
}

export default async function SearchPage({ searchParams }: Props) {
  const params = await searchParams;
  const rawQuery = params.q;
  const query = Array.isArray(rawQuery) ? rawQuery[0] ?? "" : rawQuery ?? "";
  const trimmedQuery = query.trim();
  const results = trimmedQuery ? await getServerSearch(trimmedQuery) : null;
  const hasResults = results
    ? GROUPS.some(({ key }) => (results[key as keyof typeof results] as SearchResult[]).length > 0)
    : false;

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <div className="mb-8">
          <p className="text-xs font-semibold uppercase tracking-wide text-primary">
            Kill Tony search
          </p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-stone-900">
            {trimmedQuery ? `Search results for "${trimmedQuery}"` : "Search the archive"}
          </h1>
        </div>

        {!trimmedQuery && (
          <div className="rounded-lg border border-stone-200 bg-white p-8 text-center">
            <p className="text-sm text-stone-500">
              Search for comedians, episodes, sets, bits, jokes, or topics from the nav bar.
            </p>
          </div>
        )}

        {trimmedQuery && !results && (
          <div className="rounded-lg border border-stone-200 bg-white p-8 text-center">
            <p className="text-sm text-stone-500">Search is unavailable right now.</p>
          </div>
        )}

        {results && !hasResults && (
          <div className="rounded-lg border border-stone-200 bg-white p-8 text-center">
            <p className="text-sm text-stone-500">No results found.</p>
          </div>
        )}

        {results?.top_result && (
          <section className="mb-6 rounded-lg border border-stone-900 bg-stone-900 text-white">
            <div className="border-b border-white/10 px-4 py-3">
              <h2 className="text-sm font-bold uppercase tracking-wide">Top result</h2>
            </div>
            <Link
              href={results.top_result.href}
              className="group block px-5 py-5 transition-colors hover:bg-white/5"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <span className="rounded bg-white/10 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-stone-300">
                    {typeLabel(results.top_result.type)}
                  </span>
                  <p className="mt-2 text-xl font-bold tracking-tight transition-colors group-hover:text-yellow-300">
                    {results.top_result.title}
                  </p>
                  {results.top_result.subtitle && (
                    <p className="mt-1 text-sm text-stone-400">{results.top_result.subtitle}</p>
                  )}
                  {results.top_result.meta.length > 0 && (
                    <p className="mt-3 flex flex-wrap gap-x-3 gap-y-1 text-sm text-stone-400">
                      {results.top_result.meta.map((meta) => (
                        <span key={meta}>{meta}</span>
                      ))}
                    </p>
                  )}
                </div>
                <span className="mt-1 shrink-0 text-stone-500 transition-colors group-hover:text-white">
                  &rarr;
                </span>
              </div>
            </Link>
          </section>
        )}

        {results && hasResults && (
          <div className="grid gap-5">
            {GROUPS.map(({ key, title }) => (
              <ResultSection
                key={key}
                title={title}
                items={results[key as keyof typeof results] as SearchResult[]}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
