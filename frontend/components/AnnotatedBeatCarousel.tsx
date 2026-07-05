"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { ArrowRight, ChevronLeft, ChevronRight } from "lucide-react";
import type { Beat, Bit, Set } from "@/lib/serverApi";
import AnnotatedBeatCard, { combineConsecutiveSetupLines, type AnnotatedBeatCardLine } from "@/components/AnnotatedBeatCard";
import { fmtDate } from "@/lib/killTonyDisplay";

export type AnnotatedBeatEntry = {
  set: Set;
  bitIndex: number;
  beatIndex: number;
};

type SelectedBeat = {
  bit: Bit;
  beat: Beat;
};

function selectedBeat(set: Set, bitIndex: number, beatIndex: number): SelectedBeat | null {
  const bit = set.bits[bitIndex];
  const beat = bit?.beats[beatIndex];
  if (!bit || !beat) return null;
  return { bit, beat };
}

function compactOrdinalId(value: string): string {
  const match = value.match(/(\d+)$/);
  return match ? match[1].padStart(3, "0") : value;
}

function selectedBeatHref(set: Set, bit: Bit, beat: Beat): string {
  const params = new URLSearchParams({
    bit: compactOrdinalId(bit.bit_id),
    beat: compactOrdinalId(beat.beat_id),
  });
  return `/killtony/sets/${set.slug}?${params.toString()}`;
}

function ScrollButton({ dir, onClick }: { dir: "left" | "right"; onClick: () => void }) {
  const Icon = dir === "left" ? ChevronLeft : ChevronRight;
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={`Scroll ${dir}`}
      className="absolute bottom-0 top-0 z-10 hidden w-10 items-center justify-center sm:flex"
      style={{ [dir]: "0.5rem" }}
    >
      <span className="flex h-10 w-10 items-center justify-center rounded-full border border-stone-200 bg-white text-stone-600 shadow-md transition-colors hover:text-stone-950">
        <Icon className="h-5 w-5" />
      </span>
    </button>
  );
}

function displayedLines(beat: Beat): AnnotatedBeatCardLine[] {
  return combineConsecutiveSetupLines(
    beat.lines
      .filter((line) => line.label !== "fluff")
      .map((line) => ({ id: line.id, label: line.label, text: line.text }))
  );
}

type Props = {
  entries: AnnotatedBeatEntry[];
  title?: string;
  description?: string;
  href?: string;
  linkText?: string;
  accentClass?: string;
  headingClassName?: string;
  tileClassName?: string;
};

export default function AnnotatedBeatCarousel({
  entries,
  title,
  description,
  href,
  linkText,
  accentClass,
  headingClassName = "text-lg font-bold text-stone-950",
  tileClassName = "w-[88%] shrink-0 snap-start px-2 first:pl-4 last:pr-4 sm:w-[78%] md:w-[68%] lg:w-[72%] lg:first:pl-0 lg:last:pr-0 xl:w-[62%]",
}: Props) {
  const beatEntries = entries
    .map((entry) => ({ entry, selected: selectedBeat(entry.set, entry.bitIndex, entry.beatIndex) }))
    .filter((item): item is { entry: AnnotatedBeatEntry; selected: SelectedBeat } => Boolean(item.selected));
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  const updateArrows = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 4);
    setCanScrollRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 4);
  }, []);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    updateArrows();
    el.addEventListener("scroll", updateArrows, { passive: true });
    const ro = new ResizeObserver(updateArrows);
    ro.observe(el);
    return () => {
      el.removeEventListener("scroll", updateArrows);
      ro.disconnect();
    };
  }, [updateArrows]);

  function scroll(dir: 1 | -1) {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollBy({ left: dir * el.clientWidth, behavior: "smooth" });
  }

  if (beatEntries.length === 0) return null;

  return (
    <section>
      {title && (
        <div className="mb-4 px-6 lg:px-0">
          <div
            className={`flex flex-col gap-1 sm:flex-row sm:items-baseline sm:justify-between sm:gap-2 ${
              accentClass ? `border-l-4 pl-3 ${accentClass}` : ""
            }`}
          >
            <div className="max-w-2xl">
              <h2 className={headingClassName}>{title}</h2>
              {description && <p className="mt-2 text-sm leading-6 text-stone-600">{description}</p>}
            </div>
            {href && (
              <Link
                href={href}
                className="inline-flex shrink-0 items-center gap-1 text-xs font-bold text-stone-400 transition-colors hover:text-stone-950"
              >
                {linkText ?? "See all"}
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            )}
          </div>
        </div>
      )}

      <div className="relative -mx-4 lg:mx-0">
        {canScrollLeft && <ScrollButton dir="left" onClick={() => scroll(-1)} />}
        <div
          ref={scrollRef}
          className="flex snap-x snap-mandatory overflow-x-scroll [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
        >
          {beatEntries.map(({ entry, selected }) => (
            <div
              key={`${entry.set.slug}:${selected.bit.bit_id}:${selected.beat.beat_id}`}
              className={tileClassName}
            >
              <AnnotatedBeatCard
                href={selectedBeatHref(entry.set, selected.bit, selected.beat)}
                jokeType={selected.beat.joke_type}
                comedianName={entry.set.comedian.name}
                comedianAttributes={entry.set.comedian.attributes}
                meta={`${entry.set.video.title}${entry.set.video.date ? ` / ${fmtDate(entry.set.video.date)}` : ""}`}
                lines={displayedLines(selected.beat)}
                imageUrl={entry.set.image_url}
                fallbackVideoId={entry.set.video.youtube_id}
                imageAlt={`${entry.set.comedian.name} set image`}
              />
            </div>
          ))}
        </div>
        {canScrollRight && <ScrollButton dir="right" onClick={() => scroll(1)} />}
      </div>
    </section>
  );
}
