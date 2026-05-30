import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { getServerSearch, type SearchResponse, type SearchResult } from "@/lib/serverApi";
import YoutubeThumbnail from "@/components/YoutubeThumbnail";

export const metadata = {
  title: "Search - Kill Tony | PunchPedia",
};

type Props = { searchParams: Promise<Record<string, string | string[] | undefined>> };

type SearchGroupKey = Exclude<keyof SearchResponse, "query" | "top_result">;
type DisplaySearchGroupKey = Exclude<SearchGroupKey, "jokes">;

const GROUPS: { key: DisplaySearchGroupKey; title: string; description: string }[] = [
  { key: "comedians", title: "Comedians", description: "Guest comics and bucket pulls" },
  { key: "episodes", title: "Episodes", description: "KT numbers, titles, and metadata" },
  { key: "sets", title: "Sets", description: "Individual minutes and interviews" },
  { key: "bits", title: "Bits", description: "Larger joke ideas and recurring angles" },
  { key: "topics", title: "Topics", description: "Subject tags across the archive" },
];

const MAIN_GROUPS: { key: DisplaySearchGroupKey; title: string }[] = [
  { key: "episodes", title: "Episodes" },
  { key: "comedians", title: "Comedians" },
  { key: "bits", title: "Bits" },
];

const SIDEBAR_GROUPS: { key: DisplaySearchGroupKey; title: string }[] = [
  { key: "sets", title: "Sets" },
  { key: "topics", title: "Topics" },
];

const ALWAYS_VISIBLE_GROUPS = new Set<DisplaySearchGroupKey>(["comedians", "episodes"]);

const TYPE_STYLES: Record<SearchResult["type"], string> = {
  comedian: "bg-[#ff1464] text-white",
  episode: "bg-black text-white",
  set: "bg-[#ffff64] text-black",
  bit: "bg-cyan-500 text-black",
  joke: "bg-emerald-400 text-black",
  topic: "bg-indigo-500 text-white",
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
  if (item.type === "episode") {
    const episodeNumber = item.meta[0]?.match(/#(\d+)/)?.[1] ?? item.title.match(/#(\d+)/)?.[1];
    if (episodeNumber) return episodeNumber;
  }
  const label = item.title.trim() || typeLabel(item.type);
  return label.charAt(0).toUpperCase();
}

function formattedMeta(item: SearchResult): string {
  return [typeLabel(item.type), ...item.meta].filter(Boolean).slice(0, 4).join(" / ");
}

function ResultMark({ item, featured = false }: { item: SearchResult; featured?: boolean }) {
  if (item.type === "episode") {
    return (
      <YoutubeThumbnail
        videoId={item.youtube_id}
        alt={item.title}
        className={featured ? "h-24 w-40 shrink-0 sm:h-28 sm:w-48" : "h-[75px] w-[133px] shrink-0"}
      />
    );
  }

  return (
    <span
      className={`flex shrink-0 items-center justify-center overflow-hidden font-black uppercase ${
        TYPE_STYLES[item.type]
      } ${featured ? "h-24 w-24 text-4xl sm:h-28 sm:w-28" : "h-[75px] w-[75px] text-2xl"}`}
    >
      {resultInitial(item)}
    </span>
  );
}

function ResultCard({
  item,
  featured = false,
  compact = false,
  textOnly = false,
}: {
  item: SearchResult;
  featured?: boolean;
  compact?: boolean;
  textOnly?: boolean;
}) {
  const subtitle = item.subtitle === typeLabel(item.type) ? "" : item.subtitle;
  const hideMark = compact || textOnly;

  return (
    <Link
      href={item.href}
      className={`group flex min-w-0 bg-white text-black transition-colors hover:bg-[#e9e9e9] ${
        compact ? "min-h-0" : featured ? "min-h-28" : "min-h-[75px]"
      }`}
    >
      {!hideMark && <ResultMark item={item} featured={featured} />}
      <div
        className={`flex min-w-0 flex-1 flex-col justify-between overflow-hidden ${
          compact ? "px-3 py-2" : featured ? "px-3 py-2.5" : "px-2.5 py-2"
        }`}
      >
        <div className="min-w-0">
          <div className="flex min-w-0 items-start justify-between gap-2">
            <p
              className={`min-w-0 overflow-hidden text-ellipsis break-words font-bold leading-none text-black ${
                compact ? "text-sm" : featured ? "text-xl sm:text-2xl" : "text-base"
              }`}
            >
              {item.title}
            </p>
            <ArrowUpRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-stone-400 opacity-0 transition-opacity group-hover:opacity-100" />
          </div>
          {subtitle && (
            <p
              className={`mt-1 overflow-hidden text-ellipsis break-words text-stone-500 ${
                featured ? "line-clamp-2 text-sm" : "line-clamp-1 text-xs"
              }`}
            >
              {subtitle}
            </p>
          )}
        </div>
        <p className={`truncate text-xs text-stone-500 ${compact ? "mt-1" : "mt-2"}`}>
          <span className="font-bold text-[#ff1464]">{typeLabel(item.type)}</span>
          {item.meta.length > 0 && <span> / {item.meta.slice(0, 3).join(" / ")}</span>}
        </p>
      </div>
    </Link>
  );
}

function ResultSection({
  groupKey,
  title,
  items,
  query,
}: {
  groupKey: DisplaySearchGroupKey;
  title: string;
  items: SearchResult[];
  query: string;
}) {
  if (items.length === 0 && !ALWAYS_VISIBLE_GROUPS.has(groupKey)) return null;
  const isBits = groupKey === "bits";

  return (
    <section className="scroll-mt-24" id={groupKey}>
      <div className="mb-2 mt-5 flex items-end justify-between gap-4 px-4 sm:px-0">
        <h2 className="text-xs font-bold uppercase text-stone-500">{title}</h2>
        <div className="flex items-center gap-3">
          <span className="text-xs text-stone-400">{items.length}</span>
          {items.length > 0 && (
            <Link
              href={refinedHref(groupKey, query)}
              className="text-xs font-bold text-stone-500 transition-colors hover:text-[#ff1464]"
            >
              Show more {title.toLowerCase()}
            </Link>
          )}
        </div>
      </div>
      <div className={`grid gap-2 ${isBits ? "" : "min-[850px]:grid-cols-2"}`}>
        {items.length > 0 ? (
          items.map((item) => (
            <ResultCard key={`${item.type}-${item.href}-${item.title}`} item={item} textOnly={isBits} />
          ))
        ) : (
          <div className="bg-white px-4 py-5 text-sm text-stone-500">
            No {title.toLowerCase()} matched this search.
          </div>
        )}
      </div>
    </section>
  );
}

function SidebarResultSection({
  groupKey,
  title,
  items,
  query,
}: {
  groupKey: DisplaySearchGroupKey;
  title: string;
  items: SearchResult[];
  query: string;
}) {
  if (items.length === 0) return null;

  return (
    <section className="mt-4 bg-white p-4 text-black" id={groupKey}>
      <div className="mb-2 flex items-end justify-between gap-3">
        <h2 className="text-xs font-bold uppercase text-stone-500">{title}</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-stone-400">{items.length}</span>
          <Link
            href={refinedHref(groupKey, query)}
            className="text-xs font-bold text-stone-500 transition-colors hover:text-[#ff1464]"
          >
            More
          </Link>
        </div>
      </div>
      <div className="grid gap-1.5">
        {items.map((item) => (
          <ResultCard key={`${item.type}-${item.href}-${item.title}`} item={item} compact />
        ))}
      </div>
    </section>
  );
}

function SearchEmptyState({ query }: { query: string }) {
  return (
    <div className="bg-white px-4 py-12 text-center text-black">
      <p className="text-xl font-bold">
        {query ? "No results found." : "Search the Kill Tony archive."}
      </p>
      <p className="mt-2 text-sm text-stone-500">
        Try a comedian, KT number, bit summary, set detail, or topic.
      </p>
    </div>
  );
}

function refinedHref(key: DisplaySearchGroupKey, query: string): string {
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
    <aside className="bg-white p-4 text-black">
      <h2 className="text-xs font-bold uppercase text-stone-500">Refine results</h2>
      <div className="mt-3 grid gap-1">
        {counts.map((group) => (
          <Link
            key={group.key}
            href={refinedHref(group.key, query)}
            className="flex items-center justify-between gap-3 px-0 py-2 text-sm transition-colors hover:text-[#ff1464]"
          >
            <span className="min-w-0">
              <span className="block truncate font-bold">{group.title}</span>
              <span className="block truncate text-xs text-stone-500">{group.description}</span>
            </span>
            <span className="shrink-0 text-xs text-stone-400">{group.count}</span>
          </Link>
        ))}
      </div>
    </aside>
  );
}

function TopResult({ item }: { item: SearchResult }) {
  return (
    <section>
      <div className="mb-2 px-4 sm:px-0">
        <h2 className="text-xs font-bold uppercase text-stone-500">Top result</h2>
      </div>
      <ResultCard item={item} featured />
      <p className="mt-2 px-4 text-xs text-stone-500 sm:px-0">{formattedMeta(item)}</p>
    </section>
  );
}

export default async function SearchPage({ searchParams }: Props) {
  const params = await searchParams;
  const rawQuery = params.q;
  const query = Array.isArray(rawQuery) ? rawQuery[0] ?? "" : rawQuery ?? "";
  const trimmedQuery = query.trim();
  const results = trimmedQuery ? await getServerSearch(trimmedQuery) : null;
  const hasResults = results ? GROUPS.some(({ key }) => results[key].length > 0) : false;

  return (
    <div className="min-h-screen bg-[#f7f7f7] text-black">
      <section className="bg-[#f7f7f7] text-black">
        <div className="mx-auto max-w-6xl px-4 py-8 text-center sm:px-6">
          <h1 className="break-words text-4xl font-bold leading-none tracking-normal text-black sm:text-5xl">
            {trimmedQuery ? `"${trimmedQuery}"` : "Search"}
          </h1>
          <p className="mt-3 text-sm font-bold uppercase text-stone-500">All results</p>
        </div>
      </section>

      <div className="mx-auto grid max-w-6xl gap-6 px-0 py-6 sm:px-6 lg:grid-cols-[minmax(0,1fr)_300px]">
        <main className="min-w-0">
          {!trimmedQuery && <SearchEmptyState query="" />}
          {trimmedQuery && !results && (
            <div className="bg-white px-4 py-12 text-center">
              <p className="text-lg font-bold">Search is unavailable right now.</p>
            </div>
          )}
          {results && !hasResults && <SearchEmptyState query={trimmedQuery} />}
          {results && hasResults && (
            <>
              {results.top_result && <TopResult item={results.top_result} />}
              {MAIN_GROUPS.map(({ key, title }) => (
                <ResultSection
                  key={key}
                  groupKey={key}
                  title={title}
                  items={results[key]}
                  query={trimmedQuery}
                />
              ))}
            </>
          )}
        </main>
        <aside className="px-4 sm:px-0">
          <BrowseResults results={results} query={trimmedQuery} />
          {results && hasResults && SIDEBAR_GROUPS.map(({ key, title }) => (
            <SidebarResultSection
              key={key}
              groupKey={key}
              title={title}
              items={results[key]}
              query={trimmedQuery}
            />
          ))}
        </aside>
      </div>
    </div>
  );
}
