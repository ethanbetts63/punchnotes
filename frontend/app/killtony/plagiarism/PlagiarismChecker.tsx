"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Loader2 } from "lucide-react";
import { compactOrdinalId } from "@/lib/bitLinks";

type BeatLine = {
  line_number: number;
  label: string;
  text: string;
};

type MatchedSegment = {
  text: string;
  line_start: number;
  line_end: number;
  similarity: number;
};

type PlagiarismMatch = {
  similarity: number;
  beat_id: string;
  bit_id: string;
  joke_type: string;
  comedian: string;
  comedian_slug: string;
  episode_number: number;
  set_slug: string;
  premise: string;
  lines: BeatLine[];
  matched_segments: MatchedSegment[];
};

// For each line, the highest score of any matched segment covering it (null if none).
function scoreByLine(match: PlagiarismMatch): Map<number, number> {
  const scores = new Map<number, number>();
  for (const segment of match.matched_segments) {
    for (let n = segment.line_start; n <= segment.line_end; n++) {
      const existing = scores.get(n);
      if (existing === undefined || segment.similarity > existing) {
        scores.set(n, segment.similarity);
      }
    }
  }
  return scores;
}

function buildBeatHref(match: PlagiarismMatch): string {
  const params = new URLSearchParams({
    bit: compactOrdinalId(match.bit_id),
    beat: compactOrdinalId(match.beat_id),
  });
  return `/killtony/sets/${match.set_slug}?${params.toString()}`;
}

function SimilarityBadge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    pct >= 85 ? "bg-red-100 text-red-700" :
    pct >= 75 ? "bg-amber-100 text-amber-700" :
    "bg-stone-100 text-stone-600";
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${color}`}>
      {pct}% similar
    </span>
  );
}

function LineRow({ line, score }: { line: BeatLine; score: number | undefined }) {
  const matched = score !== undefined;
  const isPunchline = line.label === "punchline";
  return (
    <div
      className={`flex items-start gap-2 rounded-md px-2 py-1 ${
        matched ? "bg-amber-50 ring-1 ring-amber-200" : ""
      }`}
    >
      <p className={`flex-1 text-sm ${isPunchline ? "font-semibold text-stone-900" : "text-stone-600"}`}>
        {line.text}
      </p>
      {matched && (
        <span className="mt-0.5 shrink-0 rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-semibold text-amber-700">
          {Math.round(score * 100)}%
        </span>
      )}
    </div>
  );
}

function MatchTile({ match }: { match: PlagiarismMatch }) {
  const lineScores = scoreByLine(match);
  return (
    <Link
      href={buildBeatHref(match)}
      className="group block rounded-xl border border-stone-200 bg-white p-5 transition-all hover:border-primary/40 hover:shadow-sm"
    >
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <span className="text-sm font-semibold text-stone-900 transition-colors group-hover:text-primary">
          {match.comedian}
        </span>
        <span className="text-stone-300">·</span>
        <span className="text-xs text-stone-400">Ep {match.episode_number}</span>
        {match.joke_type && (
          <span className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
            {match.joke_type}
          </span>
        )}
        <SimilarityBadge score={match.similarity} />
      </div>
      {match.premise && (
        <p className="mb-3 text-sm italic text-stone-500">&ldquo;{match.premise}&rdquo;</p>
      )}
      <div className="space-y-0.5">
        {match.lines.map((line) => (
          <LineRow key={line.line_number} line={line} score={lineScores.get(line.line_number)} />
        ))}
      </div>
    </Link>
  );
}

export default function PlagiarismChecker() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const qParam = searchParams.get("q") ?? "";

  const [text, setText] = useState(qParam);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<PlagiarismMatch[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runCheck = useCallback(async (query: string) => {
    const trimmed = query.trim();
    if (!trimmed) return;
    setLoading(true);
    setResults(null);
    setError(null);
    try {
      const res = await fetch("/api/plagiarism", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: trimmed }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error ?? "Something went wrong.");
      } else {
        setResults((data.results ?? []).slice(0, 3));
      }
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (qParam) {
      setText(qParam);
      runCheck(qParam);
    }
  }, [qParam, runCheck]);

  function handleCheck() {
    const trimmed = text.trim();
    if (!trimmed) return;
    if (trimmed === qParam) {
      runCheck(trimmed);
    } else {
      router.replace(`?q=${encodeURIComponent(trimmed)}`);
    }
  }

  return (
    <div className="space-y-4">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste a joke or premise here..."
        rows={5}
        className="w-full rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm text-stone-900 placeholder:text-stone-400 focus:border-primary/50 focus:outline-none focus:ring-2 focus:ring-primary/20 resize-none"
      />
      <button
        onClick={handleCheck}
        disabled={loading || !text.trim()}
        className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading && <Loader2 className="h-4 w-4 animate-spin" />}
        {loading ? "Checking…" : "Check"}
      </button>

      {loading && (
        <p className="mt-2 text-sm text-stone-400">
          Loading the similarity model — this can take up to a minute on first use.
        </p>
      )}

      {error && (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {results !== null && !loading && (
        <div className="mt-6">
          {results.length === 0 ? (
            <p className="text-stone-500">No similar jokes found above the similarity threshold.</p>
          ) : (
            <>
              <h2 className="mb-4 text-lg font-bold text-stone-900">
                {results.length === 1 ? "1 similar joke" : `${results.length} similar jokes`} found
              </h2>
              <div className="space-y-3">
                {results.map((match) => (
                  <MatchTile key={`${match.set_slug}-${match.beat_id}`} match={match} />
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
