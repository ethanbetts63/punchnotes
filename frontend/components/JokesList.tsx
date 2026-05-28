"use client";

import Link from "next/link";
import { useState } from "react";
import type { Joke } from "@/lib/serverApi";
import { Badge } from "@/components/ui/badge";
import Paginator from "@/components/Paginator";

const PAGE_SIZE = 20;

type Props = { jokes: Joke[]; filterKey?: string };

export default function JokesList({ jokes, filterKey }: Props) {
  const [page, setPage] = useState(1);

  // reset to page 1 when filters change (filterKey changes on filter navigation)
  const [prevKey, setPrevKey] = useState(filterKey);
  if (filterKey !== prevKey) { setPrevKey(filterKey); setPage(1); }

  const totalPages = Math.ceil(jokes.length / PAGE_SIZE);
  const pageItems = jokes.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  if (jokes.length === 0) {
    return (
      <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
        <p className="text-stone-500">No jokes found.</p>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-3">
        {pageItems.map((joke) => (
          <Link
            key={joke.id}
            href={`/killtony/sets/${joke.set_id}`}
            className="group block rounded-xl border border-stone-200 bg-white p-5 transition-all hover:border-primary/40 hover:shadow-sm"
          >
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <span className="text-sm font-semibold text-stone-900 transition-colors group-hover:text-primary">
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
      <Paginator page={page} totalPages={totalPages} onPage={setPage} />
    </>
  );
}
