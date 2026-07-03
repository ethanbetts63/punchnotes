"use client";

import { useState } from "react";
import Link from "next/link";
import { ChevronDown } from "lucide-react";
import type { BeatSearchItem } from "@/lib/serverApi";
import { formatJokeTileText, JOKE_TYPE_STYLES } from "@/lib/tiles";
import { buildBeatSearchHref } from "@/lib/bitLinks";
import { HighlightBody } from "@/components/MediaTile";

const DEFAULT_JOKE_STYLE = { badge: "bg-stone-950 text-white", accent: "border-l-stone-300" };

export default function JokeSearchResultCard({ item, query }: { item: BeatSearchItem; query?: string }) {
  const [expanded, setExpanded] = useState(false);
  const href = buildBeatSearchHref(item);
  const style = (item.joke_type && JOKE_TYPE_STYLES[item.joke_type]) || DEFAULT_JOKE_STYLE;

  const trimmedQuery = query?.trim();
  const showMatchedLine = trimmedQuery && item.matched_line;
  const punchline = item.punchline || item.matched_line || item.premise;
  const setup = item.setup_lines.join(" ");
  const summary = showMatchedLine ? null : formatJokeTileText({ punchline, setup, limit: 220 });

  return (
    <div className={`overflow-hidden rounded-lg border border-stone-200 bg-white border-l-4 ${style.accent} transition-shadow hover:shadow-sm`}>
      <div className="flex items-start gap-3 p-4">
        <Link href={href} className="group min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-sm font-bold text-stone-950 transition-colors group-hover:text-primary">
              {item.comedian}
            </p>
            <span className="text-xs text-stone-400">KT #{item.episode_number}</span>
            {item.joke_type && (
              <span className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-bold ${style.badge}`}>
                {item.joke_type}
              </span>
            )}
          </div>
          <p className="mt-2 text-base leading-snug text-stone-700">
            &ldquo;
            {showMatchedLine ? (
              <HighlightBody text={item.matched_line} query={trimmedQuery!} />
            ) : (
              <>
                {summary?.prefix}
                <span className="font-black text-stone-950">{summary?.highlight}</span>
              </>
            )}
            &rdquo;
          </p>
        </Link>

        <button
          type="button"
          onClick={() => setExpanded((value) => !value)}
          aria-expanded={expanded}
          aria-label={expanded ? "Collapse joke" : "Expand joke"}
          className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-stone-200 bg-white text-stone-500 transition-colors hover:border-stone-400 hover:text-stone-800"
        >
          <ChevronDown className={`h-4 w-4 transition-transform ${expanded ? "rotate-180" : ""}`} />
        </button>
      </div>

      {expanded && (
        <div className="border-t border-stone-100 bg-stone-50/60 px-4 pb-4 pt-3">
          <div className="space-y-1.5 text-sm leading-snug text-stone-700">
            {item.setup_lines.map((line, i) => (
              <p key={i}>{line}</p>
            ))}
            {item.punchline && <p className="font-bold text-stone-950">{item.punchline}</p>}
          </div>
          {item.premise && (
            <p className="mt-3 text-xs italic text-stone-500">{item.premise}</p>
          )}
          <Link
            href={href}
            className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-primary hover:underline"
          >
            Open full set →
          </Link>
        </div>
      )}
    </div>
  );
}
