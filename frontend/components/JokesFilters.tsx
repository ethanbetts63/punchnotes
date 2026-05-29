"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState, useMemo } from "react";

const JOKE_TYPES = [
  "misdirect", "reframe", "phonetic-match", "double-meaning",
  "analogy", "hyperbole", "elephant-in-the-room",
];

type Props = { topics: string[] };

export default function JokesFilters({ topics }: Props) {
  const router = useRouter();
  const sp = useSearchParams();
  const currentType = sp.get("joke_type") ?? "";
  const currentTopic = sp.get("topic") ?? "";
  const currentQuery = sp.get("q") ?? "";
  const [topicSearch, setTopicSearch] = useState("");
  const [query, setQuery] = useState(currentQuery);

  function navigate(type: string, topic: string, nextQuery = currentQuery) {
    const params = new URLSearchParams();
    if (nextQuery.trim()) params.set("q", nextQuery.trim());
    if (type) params.set("joke_type", type);
    if (topic) params.set("topic", topic);
    const qs = params.toString();
    router.push(`/killtony/jokes${qs ? `?${qs}` : ""}`);
  }

  const filteredTopics = useMemo(() => {
    if (!topicSearch.trim()) return topics;
    const q = topicSearch.toLowerCase();
    return topics.filter((t) => t.toLowerCase().includes(q));
  }, [topics, topicSearch]);

  return (
    <div className="mb-6 space-y-4">
      <form
        onSubmit={(event) => {
          event.preventDefault();
          navigate(currentType, currentTopic, query);
        }}
        className="flex items-center gap-2 rounded-xl border border-stone-200 px-3 py-2 transition-colors focus-within:border-stone-400"
      >
        <svg className="h-3.5 w-3.5 shrink-0 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
        </svg>
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search jokes..."
          className="flex-1 bg-transparent text-sm text-stone-900 placeholder-stone-400 focus:outline-none"
        />
        {currentQuery && (
          <button
            type="button"
            onClick={() => {
              setQuery("");
              navigate(currentType, currentTopic, "");
            }}
            className="text-xs text-stone-400 transition-colors hover:text-stone-600"
          >
            Clear x
          </button>
        )}
      </form>

      {/* Joke type chips */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => navigate("", currentTopic)}
          className={`rounded-full px-3 py-1 text-xs font-medium border transition-colors ${
            !currentType
              ? "bg-stone-900 text-white border-stone-900"
              : "bg-white text-stone-600 border-stone-200 hover:border-stone-400"
          }`}
        >
          All types
        </button>
        {JOKE_TYPES.map((jt) => (
          <button
            key={jt}
            onClick={() => navigate(jt, currentTopic)}
            className={`rounded-full px-3 py-1 text-xs font-medium border transition-colors ${
              currentType === jt
                ? "bg-primary text-white border-primary"
                : "bg-white text-stone-600 border-stone-200 hover:border-stone-400"
            }`}
          >
            {jt}
          </button>
        ))}
      </div>

      {/* Topic filter */}
      <div className="rounded-xl border border-stone-200 overflow-hidden">
        <div className="flex items-center gap-2 border-b border-stone-200 px-3 py-2">
          <svg className="h-3.5 w-3.5 shrink-0 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
          </svg>
          <input
            type="text"
            value={topicSearch}
            onChange={(e) => setTopicSearch(e.target.value)}
            placeholder={`Filter topics… (${topics.length} total)`}
            className="flex-1 bg-transparent text-sm text-stone-900 placeholder-stone-400 focus:outline-none"
          />
          {currentTopic && (
            <button
              onClick={() => navigate(currentType, "")}
              className="text-xs text-stone-400 hover:text-stone-600 transition-colors"
            >
              Clear ×
            </button>
          )}
        </div>
        <div className="flex flex-wrap gap-1.5 p-3 max-h-40 overflow-y-auto">
          {filteredTopics.length === 0 ? (
            <p className="text-xs text-stone-400 py-1">No topics match.</p>
          ) : (
            filteredTopics.map((t) => (
              <button
                key={t}
                onClick={() => navigate(currentType, currentTopic === t ? "" : t)}
                className={`rounded-full px-2.5 py-0.5 text-xs font-medium border transition-colors ${
                  currentTopic === t
                    ? "bg-primary text-white border-primary"
                    : "bg-stone-50 text-stone-600 border-stone-200 hover:border-stone-400 hover:bg-white"
                }`}
              >
                {t}
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
