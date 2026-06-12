"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, ArrowRight, Mic2, Search, Tv } from "lucide-react";

const steps = [
  {
    level: "01",
    title: "Pick an entry point.",
    description:
      "Browse curated playlists for episodes, comedians and sets. Or search to find something specific.",
    href: "/killtony/episodes",
    cta: "Browse archive",
    icon: Tv,
  },
  {
    level: "02",
    title: "Open the detail page.",
    description:
      "Each episodes page shows every set from the night. Comedian pages show all sets from that comic.",
    href: "/killtony/comedians",
    cta: "See comics",
    icon: Mic2,
  },
  {
    level: "03",
    title: "Drill into the joke.",
    description:
      "Quick jump to watch set clip and see the full transcript annotated.",
    href: "/killtony/sets",
    cta: "Explore sets",
    icon: Search,
  },
];

export default function HowItWorksPanel() {
  const [activeIndex, setActiveIndex] = useState(0);
  const step = steps[activeIndex];
  const Icon = step.icon;

  function showPrevious() {
    setActiveIndex((current) => (current - 1 + steps.length) % steps.length);
  }

  function showNext() {
    setActiveIndex((current) => (current + 1) % steps.length);
  }

  return (
    <aside className="rounded-2xl border border-white/10 bg-[linear-gradient(180deg,#0b1020_0%,#171d2c_100%)] p-5 shadow-[0_24px_80px_rgba(0,0,0,0.16)]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="font-bold uppercase tracking-[0.24em] text-primary">
            How it works
          </h2>
        </div>
        <span className="text-xs font-semibold text-white/55">
          {activeIndex + 1} / {steps.length}
        </span>
      </div>

      <div className="mt-5 rounded-2xl border border-white/10 bg-white/5 p-5">
        <div className="flex items-center justify-between gap-3">
          <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-primary/15 text-primary">
            <Icon className="h-5 w-5" />
          </span>
          <span className="text-sm font-bold tracking-[0.24em] text-white/45">{step.level}</span>
        </div>

        <h4 className="mt-5 text-xl font-bold tracking-tight text-white">{step.title}</h4>
        <p className="mt-3 text-sm leading-relaxed text-stone-300">{step.description}</p>

        <div className="mt-6 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={showPrevious}
              className="flex h-9 w-9 items-center justify-center rounded-full border border-white/10 text-stone-300 transition-colors hover:border-primary/40 hover:text-white"
              aria-label="Show previous step"
            >
              <ArrowLeft className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={showNext}
              className="flex h-9 w-9 items-center justify-center rounded-full border border-white/10 text-stone-300 transition-colors hover:border-primary/40 hover:text-white"
              aria-label="Show next step"
            >
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>

          <Link
            href={step.href}
            className="inline-flex items-center rounded-full border border-primary/30 bg-primary/12 px-4 py-2 text-xs font-bold uppercase tracking-[0.18em] text-primary transition-colors hover:bg-primary hover:text-white"
          >
            {step.cta}
          </Link>
        </div>
      </div>
    </aside>
  );
}
