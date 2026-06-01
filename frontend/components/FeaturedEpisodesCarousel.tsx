"use client";

import Link from "next/link";
import { ArrowLeft, ArrowRight, Play, Trophy } from "lucide-react";
import { useMemo, useState } from "react";
import type { Episode } from "@/lib/serverApi";
import YoutubeThumbnail from "@/components/YoutubeThumbnail";

type CategoryKey =
  | "ratio"
  | "bucket_pulls"
  | "golden_tickets"
  | "joke_books"
  | "regulars"
  | "sets";

type Category = {
  key: CategoryKey;
  label: string;
  eyebrow: string;
  metricLabel: string;
  metricValue: (episode: Episode) => number;
  metricDisplay: (episode: Episode) => string;
  eligible?: (episode: Episode) => boolean;
};

type FeaturedEpisode = {
  category: Category;
  episode: Episode;
};

const MIN_RATIO_VIEWS = 100_000;

const CATEGORIES: Category[] = [

  {
    key: "golden_tickets",
    label: "Most golden tickets",
    eyebrow: "Most golden ticket winners",
    metricLabel: "golden ticket winners",
    metricValue: (episode) => episode.golden_ticket_count,
    metricDisplay: (episode) => String(episode.golden_ticket_count),
  },
  {
    key: "bucket_pulls",
    label: "Most bucket pulls",
    eyebrow: "Most bucket pulls",
    metricLabel: "bucket pulls",
    metricValue: (episode) => episode.bucket_pull_count,
    metricDisplay: (episode) => String(episode.bucket_pull_count),
  },
  {
    key: "joke_books",
    label: "Most big joke books",
    eyebrow: "Most big joke books",
    metricLabel: "big joke books",
    metricValue: (episode) => episode.large_joke_book_count,
    metricDisplay: (episode) => String(episode.large_joke_book_count),
  },
  {
    key: "regulars",
    label: "Most regulars",
    eyebrow: "Most regulars",
    metricLabel: "regulars",
    metricValue: (episode) => episode.regular_count,
    metricDisplay: (episode) => String(episode.regular_count),
  },
  {
    key: "sets",
    label: "Most sets",
    eyebrow: "Most sets",
    metricLabel: "sets",
    metricValue: (episode) => episode.set_count,
    metricDisplay: (episode) => String(episode.set_count),
  },
    {
    key: "ratio",
    label: "Best like/view ratio",
    eyebrow: "Best like/view ratio",
    metricLabel: "like/view ratio",
    metricValue: (episode) =>
      episode.view_count && episode.like_count != null
        ? episode.like_count / episode.view_count
        : 0,
    metricDisplay: (episode) =>
      episode.view_count && episode.like_count != null
        ? `${((episode.like_count / episode.view_count) * 100).toFixed(1)}%`
        : "-",
    eligible: (episode) =>
      episode.view_count != null &&
      episode.view_count >= MIN_RATIO_VIEWS &&
      episode.like_count != null,
  },
];

const SUPPORTING_STATS: {
  key: string;
  label: string;
  value: (episode: Episode) => string | null;
}[] = [
  { key: "duration", label: "Duration", value: (episode) => fmtDuration(episode.duration_seconds) },
  { key: "sets", label: "Sets", value: (episode) => String(episode.set_count) },
  { key: "bucket_pulls", label: "Bucket pulls", value: (episode) => String(episode.bucket_pull_count) },
  { key: "joke_books", label: "Big joke books", value: (episode) => String(episode.large_joke_book_count) },
  { key: "golden_tickets", label: "Golden tickets", value: (episode) => String(episode.golden_ticket_count) },
  { key: "regulars", label: "Regulars", value: (episode) => String(episode.regular_count) },
  { key: "views", label: "Views", value: (episode) => episode.view_count == null ? null : fmtNumber(episode.view_count) },
  { key: "likes", label: "Likes", value: (episode) => episode.like_count == null ? null : fmtNumber(episode.like_count) },
];

function fmtNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

function fmtDuration(seconds: number | null): string {
  if (!seconds) return "-";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

function fmtDate(date: string | null): string {
  if (!date) return "";
  return new Date(date).toLocaleDateString("en-AU", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function episodeTitle(episode: Episode): string {
  return episode.title || `Kill Tony #${episode.number}`;
}

function winnerFor(category: Category, episodes: Episode[]): FeaturedEpisode | null {
  const eligible = category.eligible ? episodes.filter(category.eligible) : episodes;
  const episode = eligible.reduce<Episode | null>((best, item) => {
    if (!best) return item;
    const diff = category.metricValue(item) - category.metricValue(best);
    if (diff > 0) return item;
    if (diff === 0 && item.number > best.number) return item;
    return best;
  }, null);

  return episode ? { category, episode } : null;
}

function selectedStats(item: FeaturedEpisode) {
  const activeKey = item.category.key;
  return SUPPORTING_STATS
    .filter((stat) => stat.key !== activeKey)
    .map((stat) => ({ ...stat, display: stat.value(item.episode) }))
    .filter((stat) => stat.display != null)
    .slice(0, 4);
}

type Props = {
  episodes: Episode[];
};

export default function FeaturedEpisodesCarousel({ episodes }: Props) {
  const items = useMemo(
    () => CATEGORIES.map((category) => winnerFor(category, episodes)).filter((item): item is FeaturedEpisode => item != null),
    [episodes]
  );
  const [activeIndex, setActiveIndex] = useState(0);

  if (items.length === 0) return null;

  const active = items[Math.min(activeIndex, items.length - 1)];
  const stats = selectedStats(active);
  const title = episodeTitle(active.episode);

  function go(offset: number) {
    setActiveIndex((current) => (current + offset + items.length) % items.length);
  }

  return (
    <section className="border-b border-stone-200 bg-stone-50 px-4 py-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-3 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-primary">Episode finder</p>
            <h2 className="mt-1 text-lg font-bold tracking-tight text-stone-950 sm:text-xl">
              Good Kill Tony episodes to start with
            </h2>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => go(-1)}
              className="flex h-8 w-8 items-center justify-center rounded-md border border-stone-200 bg-white text-stone-600 transition-colors hover:border-stone-400 hover:text-stone-950"
              aria-label="Previous featured episode"
            >
              <ArrowLeft className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={() => go(1)}
              className="flex h-8 w-8 items-center justify-center rounded-md border border-stone-200 bg-white text-stone-600 transition-colors hover:border-stone-400 hover:text-stone-950"
              aria-label="Next featured episode"
            >
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>

        <div className="mb-4 flex gap-2 overflow-x-auto pb-1">
          {items.map((item, index) => (
            <button
              key={item.category.key}
              type="button"
              onClick={() => setActiveIndex(index)}
              className={`shrink-0 rounded-md border px-2.5 py-1.5 text-xs font-bold transition-colors ${
                index === activeIndex
                  ? "border-stone-950 bg-stone-950 text-white"
                  : "border-stone-200 bg-white text-stone-600 hover:border-stone-400 hover:text-stone-950"
              }`}
            >
              {item.category.label}
            </button>
          ))}
        </div>

        <div className="overflow-hidden rounded-lg border border-stone-200 bg-white shadow-sm">
          <div className="grid lg:grid-cols-[minmax(0,0.8fr)_minmax(360px,1.2fr)]">
            <Link
              href={`/killtony/episodes/${active.episode.id}`}
              className="group relative block min-h-40 bg-stone-950 sm:min-h-48 lg:min-h-full"
            >
              <YoutubeThumbnail
                videoId={active.episode.youtube_id}
                alt={title}
                className="h-full min-h-40 w-full bg-stone-950 sm:min-h-48"
                fit="contain"
              />
              <div className="absolute inset-0 bg-black/20 transition-colors group-hover:bg-black/10" />
              <div className="absolute left-3 top-3 flex items-center gap-1.5 rounded-md bg-black/80 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide text-white">
                <Trophy className="h-3.5 w-3.5 text-yellow-300" />
                {active.category.eyebrow}
              </div>
            </Link>

            <div className="flex min-w-0 flex-col p-4 sm:p-5">
              <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs font-bold uppercase tracking-wide text-stone-400">
                <span>Episode {active.episode.number}</span>
                {active.episode.date && <span>{fmtDate(active.episode.date)}</span>}
              </div>

              <h3 className="mt-1.5 text-lg font-bold leading-tight tracking-tight text-stone-950 sm:text-xl">
                <Link href={`/killtony/episodes/${active.episode.id}`} className="transition-colors hover:text-primary">
                  {title}
                </Link>
              </h3>

              <div className="mt-3 flex flex-wrap items-end gap-x-6 gap-y-3 border-y border-stone-200 py-3">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wide text-stone-400">
                    {active.category.metricLabel}
                  </p>
                  <p className="mt-0.5 text-3xl font-black leading-none tracking-normal text-stone-950">
                    {active.category.metricDisplay(active.episode)}
                  </p>
                </div>
                <dl className="grid flex-1 grid-cols-2 gap-x-5 gap-y-2 sm:grid-cols-4">
                  {stats.map((stat) => (
                    <div key={stat.key}>
                      <dt className="text-[11px] leading-tight text-stone-500">{stat.label}</dt>
                      <dd className="mt-0.5 text-sm font-bold tabular-nums text-stone-950">{stat.display}</dd>
                    </div>
                  ))}
                </dl>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                <Link
                  href={`/killtony/episodes/${active.episode.id}`}
                  className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-primary/90"
                >
                  <Play className="h-4 w-4" />
                  Open breakdown
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
