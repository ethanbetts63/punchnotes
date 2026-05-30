import React from "react";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import type { Beat, Bit, ComedianAttribute, Set } from "@/lib/serverApi";
import SetImage from "@/components/SetImage";

type SelectedBeat = {
  bit: Bit;
  beat: Beat;
  bitIdx: number;
  beatIdx: number;
};

const labelBadge: Record<string, string> = {
  setup: "bg-blue-100 text-blue-700",
  punchline: "bg-amber-100 text-amber-700",
  tag: "bg-green-100 text-green-700",
  fluff: "bg-stone-100 text-stone-500",
};

const comedianTypeLabel: Partial<Record<ComedianAttribute, string>> = {
  bucket_pull: "Bucket Pull",
  regular: "Regular",
  golden_ticket: "Golden Ticket",
  special: "Special",
};

const comedianTypeClassName: Partial<Record<ComedianAttribute, string>> = {
  bucket_pull: "bg-stone-100 text-stone-600",
  regular: "bg-blue-50 text-blue-600",
  golden_ticket: "bg-amber-100 text-amber-700",
  special: "bg-purple-50 text-purple-600",
};

function fmt2(value: number | null): string {
  return value == null ? "-" : value.toFixed(2);
}

function fmtDate(date: string | null): string {
  if (!date) return "";
  return new Date(date).toLocaleDateString("en-AU", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function getAppearanceType(attributes: readonly ComedianAttribute[]): ComedianAttribute | null {
  return attributes.find((attr) => attr in comedianTypeLabel) ?? null;
}

function selectedBeat(set: Set, bitIndex: number, beatIndex: number): SelectedBeat | null {
  const bit = set.bits[bitIndex];
  const beat = bit?.beats[beatIndex];
  if (!bit || !beat) return null;
  return { bit, beat, bitIdx: bitIndex, beatIdx: beatIndex };
}

type Props = {
  set: Set;
  bitIndex: number;
  beatIndex: number;
  sidebar?: React.ReactNode;
};

export default function BeatOfTheWeek({ set, bitIndex, beatIndex, sidebar }: Props) {
  const selected = selectedBeat(set, bitIndex, beatIndex);
  if (!selected) return null;

  const beatCount = set.bits.reduce((sum, bit) => sum + bit.beats.length, 0);
  const appearanceType = getAppearanceType(set.comedian.attributes);
  const visibleLines = selected.beat.lines.filter((line) => line.label !== "fluff");

  return (
    <section className="border-b border-stone-200 bg-white px-4 py-8">
      <div className="mx-auto flex max-w-6xl items-start gap-6">
        <div className="min-w-0 flex-1">
        <Link
          href={`/killtony/sets/${set.id}`}
          className="group block max-w-3xl rounded-lg border border-stone-200 bg-white p-4 shadow-sm transition-colors hover:border-primary/40 hover:shadow-md"
        >
          <div className="flex items-start gap-4">
            <SetImage
              imageUrl={set.image_url}
              fallbackVideoId={set.episode.youtube_id}
              alt={`${set.comedian.name} set image`}
              className="h-20 w-28 shrink-0 rounded-md bg-stone-950"
              fit="contain"
            />

            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <p className="text-xs font-bold uppercase tracking-wide text-primary">Beat of the week</p>
                {selected.beat.joke_type && (
                  <span className="rounded-full bg-stone-950 px-2 py-0.5 text-[10px] font-bold text-white">
                    {selected.beat.joke_type}
                  </span>
                )}
                <ArrowUpRight className="h-3.5 w-3.5 text-stone-300 transition-colors group-hover:text-primary" />
              </div>

              <div className="mt-2 flex flex-wrap items-center gap-2">
                <h2 className="text-xl font-bold leading-tight tracking-tight text-stone-950 transition-colors group-hover:text-primary">
                  {set.comedian.name}
                </h2>
                {appearanceType && (
                  <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${comedianTypeClassName[appearanceType]}`}>
                    {comedianTypeLabel[appearanceType]}
                  </span>
                )}
              </div>

              <p className="mt-1 truncate text-xs text-stone-500">
                {set.episode.title}
                {set.episode.date ? ` / ${fmtDate(set.episode.date)}` : ""}
              </p>
            </div>
          </div>

          <div className="mt-3 flex flex-wrap gap-1.5">
            <span className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-bold text-stone-700">
              Bit {selected.bitIdx + 1} / Beat {selected.beatIdx + 1}
            </span>
            <span className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-bold text-stone-700">
              {set.bits.length} bit{set.bits.length === 1 ? "" : "s"}
            </span>
            <span className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-bold text-stone-700">
              {beatCount} beat{beatCount === 1 ? "" : "s"}
            </span>
            <span className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-bold text-stone-700">
              Setup/punch {fmt2(set.hit_ratio)}
            </span>
          </div>

          <div className="mt-4 space-y-1.5">
            {visibleLines.map((line) => (
              <div key={line.id} className="flex gap-2">
                <span className={`mt-0.5 shrink-0 rounded px-1.5 py-0.5 text-[10px] font-bold uppercase ${labelBadge[line.label]}`}>
                  {line.label}
                </span>
                <p className={`text-sm leading-snug ${line.label === "punchline" ? "font-bold text-stone-950" : "text-stone-700"}`}>
                  {line.text}
                </p>
              </div>
            ))}
          </div>
        </Link>
        </div>
        {sidebar && (
          <div className="hidden w-72 shrink-0 lg:block">{sidebar}</div>
        )}
      </div>
    </section>
  );
}
