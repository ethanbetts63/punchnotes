import Link from "next/link";
import type { BeatSearchItem } from "@/lib/serverApi";

type Props = { beats: BeatSearchItem[]; query?: string };

function HighlightedText({ text, query }: { text: string; query: string }) {
  if (!query.trim()) return <>{text}</>;

  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const pattern = new RegExp(`(${escaped})`, "ig");
  const parts = text.split(pattern);

  return (
    <>
      {parts.map((part, index) => (
        part.toLowerCase() === query.toLowerCase() ? <strong key={`${part}-${index}`}>{part}</strong> : part
      ))}
    </>
  );
}

export default function JokesList({ beats, query = "" }: Props) {
  const hasTextQuery = Boolean(query.trim());

  return (
    <div className="space-y-3">
      {beats.map((beat) => (
        <Link
          key={beat.id}
          href={`/killtony/sets/${beat.set_id}`}
          className="group block rounded-xl border border-stone-200 bg-white p-5 transition-all hover:border-primary/40 hover:shadow-sm"
        >
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <span className="text-sm font-semibold text-stone-900 transition-colors group-hover:text-primary">
              {beat.comedian}
            </span>
            <span className="text-stone-300">·</span>
            <span className="text-xs text-stone-400">Ep {beat.episode_number}</span>
            <span className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">{beat.joke_type}</span>
            {hasTextQuery && beat.matched_line_label && (
              <span className="text-xs uppercase text-stone-400">{beat.matched_line_label}</span>
            )}
          </div>
          {!hasTextQuery && beat.premise && (
            <p className="mb-3 text-sm italic text-stone-500">&ldquo;{beat.premise}&rdquo;</p>
          )}
          {hasTextQuery && beat.matched_line ? (
            <p className="text-sm text-stone-900">
              <HighlightedText text={beat.matched_line} query={query} />
            </p>
          ) : (
            <div className="space-y-1">
              {beat.setup_lines.map((line, i) => (
                <p key={i} className="text-sm text-stone-600">{line}</p>
              ))}
              {beat.punchline && (
                <p className="font-semibold text-stone-900">{beat.punchline}</p>
              )}
            </div>
          )}
        </Link>
      ))}
    </div>
  );
}
