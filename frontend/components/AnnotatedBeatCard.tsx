"use client";

import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import type { ComedianAttribute, Line } from "@/lib/serverApi";
import SetImage from "@/components/SetImage";
import { ATTRIBUTE_LABELS } from "@/lib/attributes";
import { lineLabelBadge } from "@/lib/killTonyDisplay";

export type AnnotatedBeatCardLine = {
  id: string | number;
  label: Line["label"];
  text: string;
};

export function combineConsecutiveSetupLines(lines: AnnotatedBeatCardLine[]): AnnotatedBeatCardLine[] {
  return lines.reduce<AnnotatedBeatCardLine[]>((combined, line) => {
    const previous = combined.at(-1);
    if (previous?.label === "setup" && line.label === "setup") {
      combined[combined.length - 1] = {
        ...previous,
        text: `${previous.text} ${line.text}`,
      };
      return combined;
    }
    combined.push(line);
    return combined;
  }, []);
}

function HighlightedText({ text, query }: { text: string; query?: string }) {
  const trimmed = query?.trim();
  if (!trimmed) return <>{text}</>;

  const escaped = trimmed.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const parts = text.split(new RegExp(`(${escaped})`, "ig"));

  return (
    <>
      {parts.map((part, index) =>
        part.toLowerCase() === trimmed.toLowerCase()
          ? <strong key={`${part}-${index}`} className="font-black">{part}</strong>
          : part
      )}
    </>
  );
}

type Props = {
  href: string;
  jokeType?: string | null;
  comedianName: string;
  comedianAttributes?: ComedianAttribute[];
  meta: string;
  lines: AnnotatedBeatCardLine[];
  imageUrl?: string | null;
  fallbackVideoId?: string | null;
  imageAlt?: string;
  query?: string;
};

export default function AnnotatedBeatCard({
  href,
  jokeType,
  comedianName,
  comedianAttributes = [],
  meta,
  lines,
  imageUrl,
  fallbackVideoId,
  imageAlt,
  query,
}: Props) {
  return (
    <Link
      href={href}
      className="group block h-full rounded-lg border border-stone-200 bg-white p-4 shadow-sm transition-colors hover:border-primary/40 hover:shadow-md"
    >
      <div className="flex items-start gap-4">
        {(imageUrl || fallbackVideoId) && (
          <SetImage
            imageUrl={imageUrl ?? null}
            fallbackVideoId={fallbackVideoId ?? null}
            alt={imageAlt ?? `${comedianName} set image`}
            className="hidden h-20 w-28 shrink-0 rounded-md bg-stone-950 sm:block"
            fit="contain"
            loading="lazy"
          />
        )}

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            {jokeType && (
              <span className="rounded-full bg-stone-950 px-2 py-0.5 text-[10px] font-bold text-white">
                {jokeType}
              </span>
            )}
            <ArrowUpRight className="h-3.5 w-3.5 text-stone-300 transition-colors group-hover:text-primary" />
          </div>

          <div className="mt-2 flex flex-wrap items-center gap-2">
            <h2 className="text-xl font-bold leading-tight tracking-tight text-stone-950 transition-colors group-hover:text-primary">
              {comedianName}
            </h2>
            {comedianAttributes
              .filter((attr) => attr in ATTRIBUTE_LABELS)
              .map((attr) => (
                <span key={attr} className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-bold text-stone-600">
                  {ATTRIBUTE_LABELS[attr]}
                </span>
              ))}
          </div>

          <p className="mt-1 truncate text-xs text-stone-500">{meta}</p>
        </div>
      </div>

      <div className="mt-4 space-y-1.5">
        {lines.map((line) => (
          <div
            key={line.id}
            className={`rounded px-2 py-1 text-sm leading-snug sm:flex sm:gap-2 sm:bg-transparent sm:p-0 ${lineLabelBadge[line.label]}`}
          >
            <span className="font-bold uppercase sm:hidden">
              {line.label}:{" "}
            </span>
            <span className={`mt-0.5 hidden w-20 shrink-0 rounded px-2 py-0.5 text-center text-[10px] font-bold uppercase sm:block ${lineLabelBadge[line.label]}`}>
              {line.label}
            </span>
            <p className={`inline text-stone-950 sm:block sm:text-sm sm:leading-snug ${line.label === "punchline" ? "font-bold" : "sm:text-stone-700"}`}>
              <HighlightedText text={line.text} query={query} />
            </p>
          </div>
        ))}
      </div>
    </Link>
  );
}
