import Link from "next/link";
import { ArrowUpRight, Search } from "lucide-react";
import { getServerSearch, type SearchResponse, type SearchResult } from "@/lib/serverApi";

export const metadata = {
  title: "Search - Kill Tony | PunchPedia",
};

type Props = { searchParams: Promise<Record<string, string | string[] | undefined>> };

type SearchGroupKey = Exclude<keyof SearchResponse, "query" | "top_result">;

const GROUPS: { key: SearchGroupKey; title: string; description: string }[] = [
  { key: "comedians", title: "Comedians", description: "Guest comics and bucket pulls" },
  { key: "episodes", title: "Episodes", description: "KT numbers, titles, and metadata" },
  { key: "sets", title: "Sets", description: "Individual minutes and interviews" },
  { key: "bits", title: "Bits", description: "Larger joke ideas and recurring angles" },
  { key: "jokes", title: "Jokes", description: "Premises, punchlines, and tags" },
  { key: "topics", title: "Topics", description: "Subject tags across the archive" },
];

const TYPE_STYLES: Record<SearchResult["type"], string> = {
  comedian: "bg-red-600 text-white",
  episode: "bg-stone-950 text-white",
  set: "bg-amber-400 text-stone-950",
  bit: "bg-sky-500 text-white",
  joke: "bg-emerald-500 text-stone-950",
  topic: "bg-violet-500 text-white",
};

function typeLabel(type: SearchResult["type"]): string {
  switch (type) {
    case "comedian":
      return "Comedian";
    case "episode":
      return "Episode";
    case "set":
      return "Set";
    case "bit":
      return "Bit";
    case "joke":
      return "Joke";
    case "topic":
      return "Topic";
  }
}

function resultInitial(item: SearchResult): string {
  const label = item.title.trim() || typeLabel(item.type);
  return label.charAt(0).toUpperCase();
}

function ResultMark({ item, compact = false }: { item: SearchResult; compact?: boolean }) {
  return (
    <span
      className={`flex shrink-0 items-center justify-center font-black uppercase ${TYPE_STYLES[item.type]} ${
        compact ? "h-10 w-10 text-base" : "h-16 w-16 text-2xl sm:h-20 sm:w-20 sm:text-3xl"
      }`}
    >
      {resultInitial(item)}
    </span>
  );
}

function ResultTile({
  item,
  variant,
}: {
  item: SearchResult;
  variant: SearchGroupKey;
}) {
  const cardClass = {
    comedians: "min-h-44",
    episodes: "min-h-36 sm:min-h-40",
    sets: "min-h-52",
    bits: "min-h-48",
    jokes: "min-h-32",
    topics: "min-h-28",
  }[variant];
  const titleClass = {
    comedians: "text-xl",
    episodes: "text-2xl",
    sets: "text-lg",
    bits: "text-xl",
    jokes: "text-base",
    topics: "text-lg",
  }[variant];
  const markSize = variant === "episodes" || variant === "bits" ? false : true;

  return (
    <Link
      href={item.href}
      className={`group flex flex-col justify-between border border-stone-200 bg-white p-4 transition-colors hover:border-stone-950 hover:bg-stone-50 ${cardClass}`}
    >
      <div>
        <div className="mb-4 flex items-start justify-between gap-3">
          <ResultMark item={item} compact={markSize} />
          <ArrowUpRight className="h-4 w-4 shrink-0 text-stone-300 transition-colors group-hover:text-stone-700" />
        </div>
        <span className="text-[10px] font-black uppercase tracking-wide text-stone-400">
          {typeLabel(item.type)}
        </span>
        <p className={`mt-1 font-black leading-none tracking-tight text-stone-950 transition-colors group-hover:text-primary ${titleClass}`}>
          {item.title}
        </p>
        {item.subtitle && (
          <p className="mt-2 line-clamp-2 text-sm font-medium text-stone-500">
            {item.subtitle}
          </p>
        )}
      </div>
      {item.meta.length > 0 && (
        <p className="mt-5 flex flex-wrap gap-x-3 gap-y-1 text-[10px] font-bold uppercase tracking-wide text-stone-400">
          {item.meta.slice(0, variant === "episodes" || variant === "bits" ? 4 : 3).map((meta) => (
            <span key={meta}>{meta}</span>
          ))}
        </p>
      )}
    </Link>
  );
}

function sectionGridClass(groupKey: SearchGroupKey): string {
  switch (groupKey) {
    case "comedians":
      return "grid gap-3 sm:grid-cols-4";
    case "episodes":
      return "grid gap-3 sm:grid-cols-2";
    case "sets":
      return "grid gap-3 sm:grid-cols-3";
    case "bits":
      return "grid gap-3 sm:grid-cols-2";
    case "jokes":
      return "grid gap-3";
    case "topics":
      return "grid gap-3 sm:grid-cols-4";
  }
}

function ResultSection({
  groupKey,
  title,
  items,
}: {
  groupKey: SearchGroupKey;
  title: string;
  items: SearchResult[];
}) {
  if (items.length === 0) return null;

  return (
    <section className="border-b border-stone-300 pb-6">
      <div className="mb-4 flex items-end justify-between gap-4">
        <h2 className="text-xs font-black uppercase tracking-wide text-stone-950">{title}</h2>
        <span className="text-xs font-bold text-stone-400">{items.length}</span>
      </div>
      <div className={sectionGridClass(groupKey)}>
        {items.map((item) => (
          <ResultTile
            key={`${item.type}-${item.href}-${item.title}`}
            item={item}
            variant={groupKey}
          />
        ))}
      </div>
    </section>
  );
}

function SearchEmptyState({ query }: { query: string }) {
  return (
    <div className="border-y border-stone-300 py-12 text-center">
      <p className="text-lg font-black text-stone-950">
        {query ? "No results found." : "Search the Kill Tony archive."}
      </p>
      <p className="mt-2 text-sm text-stone-500">
        Try a comedian, KT number, joke premise, bit summary, or topic.
      </p>
    </div>
  );
}

function refinedHref(key: SearchGroupKey, query: string): string {
  const params = new URLSearchParams();
  if (query) params.set("q", query);
  const qs = params.toString();

  switch (key) {
    case "comedians":
      return `/killtony/comedians${qs ? `?${qs}` : ""}`;
    case "episodes":
      return `/killtony/episodes${qs ? `?${qs}` : ""}`;
    case "bits":
      return `/killtony/bits${qs ? `?${qs}` : ""}`;
    case "jokes":
      return `/killtony/jokes${qs ? `?${qs}` : ""}`;
    case "sets":
    case "topics":
      return `/killtony/search${qs ? `?${qs}` : ""}#${key}`;
  }
}

function BrowseResults({ results, query }: { results: SearchResponse | null; query: string }) {
  const counts = GROUPS.map((group) => ({
    ...group,
    count: results ? results[group.key].length : 0,
  }));

  return (
    <section className="border-b border-stone-300 pb-6">
      <div className="border-t-4 border-stone-950 pt-4">
        <h2 className="text-xs font-black uppercase tracking-wide text-stone-950">Browse results</h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-3">
          {counts.map((group) => (
            <Link
              key={group.key}
              href={refinedHref(group.key, query)}
              className="flex min-h-24 items-start justify-between gap-3 border border-stone-200 bg-white p-3 text-sm transition-colors hover:border-stone-950 hover:bg-stone-50"
            >
              <span>
                <span className="block font-bold text-stone-950">{group.title}</span>
                <span className="block text-xs text-stone-500">{group.description}</span>
              </span>
              <span className="shrink-0 text-xs font-black text-stone-400">{group.count}</span>
            </Link>
          ))}
        </div>
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
    ? GROUPS.some(({ key }) => results[key].length > 0)
    : false;

  return (
    <div className="min-h-screen bg-white">
      <section className="border-b border-stone-950 bg-amber-300">
        <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
          <p className="text-xs font-black uppercase tracking-wide text-stone-950">Kill Tony search</p>
          <h1 className="mt-2 text-3xl font-black leading-none tracking-tight text-stone-950 sm:text-5xl">
            {trimmedQuery ? `Search results for "${trimmedQuery}"` : "Search the archive"}
          </h1>
          <form action="/killtony/search" className="mt-6 flex max-w-2xl border-2 border-stone-950 bg-white">
            <label htmlFor="search-query" className="sr-only">Search query</label>
            <div className="flex min-w-0 flex-1 items-center gap-2 px-3">
              <Search className="h-4 w-4 shrink-0 text-stone-500" aria-hidden="true" />
              <input
                id="search-query"
                name="q"
                type="search"
                defaultValue={trimmedQuery}
                placeholder="Search comedians, episodes, bits, jokes..."
                className="h-11 min-w-0 flex-1 bg-transparent text-base font-semibold text-stone-950 placeholder:text-stone-400 focus:outline-none"
              />
            </div>
            <button
              type="submit"
              className="border-l-2 border-stone-950 bg-stone-950 px-4 text-sm font-black uppercase tracking-wide text-white transition-colors hover:bg-primary sm:px-6"
            >
              Search
            </button>
          </form>
        </div>
      </section>

      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <main className="grid gap-8">
          {!trimmedQuery && <SearchEmptyState query="" />}
          {trimmedQuery && !results && (
            <div className="border-y border-stone-300 py-12 text-center">
              <p className="text-lg font-black text-stone-950">Search is unavailable right now.</p>
            </div>
          )}
          {results && !hasResults && <SearchEmptyState query={trimmedQuery} />}
          {results && hasResults && (
            <>
              <BrowseResults results={results} query={trimmedQuery} />
              {GROUPS.map(({ key, title }) => (
                <div id={key} key={key} className="scroll-mt-24">
                  <ResultSection groupKey={key} title={title} items={results[key]} />
                </div>
              ))}
            </>
          )}
        </main>

      </div>
    </div>
  );
}
