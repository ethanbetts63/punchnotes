"use client";

import React, { useState } from "react";
import Link from "next/link";
import { ArrowLeft, ArrowRight, ArrowUpRight } from "lucide-react";
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

export type BeatOfTheWeekEntry = {
  set: Set;
  bitIndex: number;
  beatIndex: number;
};

type Props = BeatOfTheWeekEntry & {
  entries?: BeatOfTheWeekEntry[];
  sidebar?: React.ReactNode;
};

export default function BeatOfTheWeek({ set, bitIndex, beatIndex, entries, sidebar }: Props) {
  const normalizedEntries = React.useMemo(() => {
    const initial = [{ set, bitIndex, beatIndex }, ...(entries ?? [])];
    const seen = new Set<string>();
    return initial.filter((entry) => {
      const key = `${entry.set.id}:${entry.bitIndex}:${entry.beatIndex}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }, [set, bitIndex, beatIndex, entries]);
  const uniqueEntries = React.useMemo(() => {
    const seen = new Set<string>();
    return normalizedEntries.filter((entry) => {
      const key = `${entry.set.id}:${entry.bitIndex}:${entry.beatIndex}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }, [normalizedEntries]);
  const [activeIndex, setActiveIndex] = useState(0);
  const activeEntry = uniqueEntries[activeIndex];
  const selected = activeEntry
    ? selectedBeat(activeEntry.set, activeEntry.bitIndex, activeEntry.beatIndex)
    : null;
  if (!selected) return null;

  const beatCount = activeEntry.set.bits.reduce((sum, bit) => sum + bit.beats.length, 0);
  const appearanceType = getAppearanceType(activeEntry.set.comedian.attributes);
  const visibleLines = selected.beat.lines.filter((line) => line.label !== "fluff");
  const canCycle = uniqueEntries.length > 1;

  function showPrevious() {
    setActiveIndex((current) => (current - 1 + uniqueEntries.length) % uniqueEntries.length);
  }

  function showNext() {
    setActiveIndex((current) => (current + 1) % uniqueEntries.length);
  }

  return (
    <section className="bg-white">
      <div className="flex items-start gap-6">
        <div className="min-w-0 flex-1">
          <div className="mb-4 flex max-w-3xl items-center justify-between gap-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.24em] text-primary">Beat of the week</p>
              <p className="mt-1 text-sm text-stone-500">
                Jump into a featured joke beat from the archive.
              </p>
            </div>
            {canCycle && (
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-stone-500">
                  {activeIndex + 1} / {uniqueEntries.length}
                </span>
                <button
                  type="button"
                  onClick={showPrevious}
                  className="flex h-9 w-9 items-center justify-center rounded-full border border-stone-200 text-stone-600 transition-colors hover:border-primary/40 hover:text-primary"
                  aria-label="Show previous featured beat"
                >
                  <ArrowLeft className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  onClick={showNext}
                  className="flex h-9 w-9 items-center justify-center rounded-full border border-stone-200 text-stone-600 transition-colors hover:border-primary/40 hover:text-primary"
                  aria-label="Show next featured beat"
                >
                  <ArrowRight className="h-4 w-4" />
                </button>
              </div>
            )}
          </div>

          <Link
            href={`/killtony/sets/${activeEntry.set.id}`}
            className="group block max-w-3xl rounded-lg border border-stone-200 bg-white p-4 shadow-sm transition-colors hover:border-primary/40 hover:shadow-md"
          >
            <div className="flex items-start gap-4">
              <SetImage
                imageUrl={activeEntry.set.image_url}
                fallbackVideoId={activeEntry.set.episode.youtube_id}
                alt={`${activeEntry.set.comedian.name} set image`}
                className="h-20 w-28 shrink-0 rounded-md bg-stone-950"
                fit="contain"
              />

              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  {selected.beat.joke_type && (
                    <span className="rounded-full bg-stone-950 px-2 py-0.5 text-[10px] font-bold text-white">
                      {selected.beat.joke_type}
                    </span>
                  )}
                  <ArrowUpRight className="h-3.5 w-3.5 text-stone-300 transition-colors group-hover:text-primary" />
                </div>

                <div className="mt-2 flex flex-wrap items-center gap-2">
                  <h2 className="text-xl font-bold leading-tight tracking-tight text-stone-950 transition-colors group-hover:text-primary">
                    {activeEntry.set.comedian.name}
                  </h2>
                  {appearanceType && (
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${comedianTypeClassName[appearanceType]}`}>
                      {comedianTypeLabel[appearanceType]}
                    </span>
                  )}
                </div>

                <p className="mt-1 truncate text-xs text-stone-500">
                  {activeEntry.set.episode.title}
                  {activeEntry.set.episode.date ? ` / ${fmtDate(activeEntry.set.episode.date)}` : ""}
                </p>
              </div>
            </div>

            <div className="mt-3 flex flex-wrap gap-1.5">
              <span className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-bold text-stone-700">
                Bit {selected.bitIdx + 1} / Beat {selected.beatIdx + 1}
              </span>
              <span className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-bold text-stone-700">
                {activeEntry.set.bits.length} bit{activeEntry.set.bits.length === 1 ? "" : "s"}
              </span>
              <span className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-bold text-stone-700">
                {beatCount} beat{beatCount === 1 ? "" : "s"}
              </span>
              <span className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-bold text-stone-700">
                Setup/punch {fmt2(activeEntry.set.hit_ratio)}
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
