"use client";

import { useRef, useState, useEffect, useCallback } from "react";
import { ArrowRight, ChevronLeft, ChevronRight } from "lucide-react";
import Link from "next/link";
import type { TileData } from "@/lib/tiles";
import MediaTile from "@/components/MediaTile";

function ScrollButton({ dir, onClick }: { dir: "left" | "right"; onClick: () => void }) {
  const Icon = dir === "left" ? ChevronLeft : ChevronRight;
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={`Scroll ${dir}`}
      className="group absolute bottom-3 top-0 z-10 flex w-12 items-center justify-center"
      style={{ [dir]: "1rem" }}
    >
      <span className="flex h-11 w-11 items-center justify-center rounded-full border border-white/90 bg-primary text-white shadow-xl shadow-stone-950/20 ring-1 ring-stone-950/10 transition-colors group-hover:bg-stone-950 group-focus-visible:outline-none group-focus-visible:ring-2 group-focus-visible:ring-primary/50">
        <Icon className="h-6 w-6" />
      </span>
    </button>
  );
}

type Props = {
  title: string;
  description?: string;
  href?: string;
  linkText?: string;
  items: TileData[];
  accentClass?: string;
  tileClass?: string;
};

export default function MediaCarousel({ title, description, href, linkText, items, accentClass, tileClass }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

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

  if (items.length === 0) return null;

  return (
    <section>
      <div className="mb-3 px-6">
        <div
          className={`flex flex-col gap-1 sm:flex-row sm:items-baseline sm:justify-between sm:gap-2 ${
            accentClass ? `border-l-4 pl-3 ${accentClass}` : ""
          }`}
        >
          <div>
            <h2 className="text-lg font-bold text-stone-950">{title}</h2>
            {description && <p className="mt-0.5 text-sm text-stone-500">{description}</p>}
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

      <div className="relative">
        {canScrollLeft && <ScrollButton dir="left" onClick={() => scroll(-1)} />}

        <div
          ref={scrollRef}
          className="carousel-scrollbar flex overflow-x-scroll px-4 pb-3 sm:px-6"
        >
          {items.map((item) => (
            <div
              key={item.href}
              className={tileClass ?? "w-1/2 shrink-0 px-1.5 first:pl-6 last:pr-6 sm:w-1/3 md:w-1/4 lg:w-1/5 xl:w-1/6"}
            >
              <MediaTile item={item} />
            </div>
          ))}
        </div>

        {canScrollRight && <ScrollButton dir="right" onClick={() => scroll(1)} />}
      </div>
    </section>
  );
}
