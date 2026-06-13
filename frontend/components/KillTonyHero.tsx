import Image from "next/image";
import Link from "next/link";
import { Mic2, Search, Tv } from "lucide-react";
import type { ReactNode } from "react";

function FeaturePill({
  icon,
  title,
  detail,
  href,
}: {
  icon: ReactNode;
  title: string;
  detail: string;
  href: string;
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 backdrop-blur-sm transition-transform hover:scale-[1.02] hover:bg-white/10"
    >
      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/20 text-primary">
        {icon}
      </div>
      <div>
        <p className="text-sm font-semibold text-white">{title}</p>
        <p className="text-xs text-stone-300">{detail}</p>
      </div>
    </Link>
  );
}

export default function KillTonyHero() {
  const content = (
    <div className="max-w-[520px] text-center md:text-left">
      <div className="mb-4 flex items-center justify-center gap-3 md:justify-start">
        <span className="inline-block h-px w-8 bg-primary/60" />
        <span className="text-xs font-bold uppercase tracking-[0.24em] text-primary">
          Made by fans. Free to use.
        </span>
        <span className="inline-block h-px w-8 bg-primary/60" />
      </div>

      <h1 className="text-5xl font-black tracking-tight text-white sm:text-6xl lg:text-7xl">
        The Kill Tony Archive
      </h1>

      <p className="mt-5 text-base leading-relaxed text-stone-300 sm:text-lg">
        Browse curated Kill Tony playlists or deepdive the archive to search your favorite sets, comedians, and jokes.
      </p>

      <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center md:justify-start">
        <Link
          href="/killtony/episodes"
          className="flex items-center gap-3 rounded-2xl bg-primary px-5 py-4 font-semibold text-white transition-transform hover:scale-[1.02] hover:bg-primary/90"
        >
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-black/20">
            <Tv className="h-5 w-5" />
          </span>
          <span className="text-left">
            <span className="block text-sm leading-tight">Browse Episodes</span>
            <span className="block text-xs font-normal text-white/80">
              Fan made playlists and search.
            </span>
          </span>
        </Link>

        <Link
          href="/killtony/jokes"
          className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-5 py-4 font-semibold text-white backdrop-blur-sm transition-transform hover:scale-[1.02] hover:bg-white/10"
        >
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10">
            <Search className="h-5 w-5" />
          </span>
          <span className="text-left">
            <span className="block text-sm leading-tight">Browse Jokes</span>
            <span className="block text-xs font-normal text-stone-300">
              Set transcripts, seachable and annotated.
            </span>
          </span>
        </Link>
      </div>

      <div className="mt-8 grid gap-3 sm:grid-cols-2">
        <FeaturePill
          icon={<Mic2 className="h-5 w-5" />}
          title="Browse comedians"
          detail="Track regulars, bucket pulls, and standout appearances."
          href="/killtony/comedians"
        />
        <FeaturePill
          icon={<Search className="h-5 w-5" />}
          title="Browse sets"
          detail="Jump straight into individual performances."
          href="/killtony/sets"
        />
      </div>
    </div>
  );

  return (
    <section className="w-full border-b border-white/10 bg-black">
      <div className="md:hidden">
        <div className="relative h-[320px] overflow-hidden">
          <Image
            src="/killtony/home-hosts-image.jpg"
            alt="Tony Hinchcliffe and Brian Redban on the Kill Tony stage"
            fill
            sizes="100vw"
            fetchPriority="high"
            className="object-cover object-center"
          />
          <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(7,11,24,0.08),rgba(7,11,24,0.82)_70%,rgba(0,0,0,0.95))]" />
        </div>

        <div className="bg-[radial-gradient(circle_at_top,rgba(39,84,210,0.28),transparent_48%),linear-gradient(180deg,#080b13_0%,#121623_100%)] px-6 py-10">
          {content}
        </div>
      </div>

      <div className="relative hidden overflow-hidden md:flex" style={{ minHeight: "clamp(580px, 86vh, 840px)" }}>
        <div className="relative flex w-1/2 items-center justify-center overflow-hidden px-10 py-16 lg:px-20">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(39,84,210,0.35),transparent_34%),radial-gradient(circle_at_bottom_left,rgba(220,38,38,0.2),transparent_38%),linear-gradient(180deg,#080b13_0%,#121623_100%)]" />
          <div className="absolute inset-y-10 right-0 w-px bg-gradient-to-b from-transparent via-primary/50 to-transparent" />
          <div className="relative z-10">{content}</div>
        </div>

        <div className="relative flex-1">
          <Image
            src="/killtony/home-hosts-image.jpg"
            alt="Tony Hinchcliffe and Brian Redban on the Kill Tony stage"
            fill
            sizes="(min-width: 1280px) 58vw, 50vw"
            fetchPriority="high"
            className="object-cover object-center"
          />
          <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(8,11,19,0.08),rgba(8,11,19,0.24)_40%,rgba(8,11,19,0.54)_100%)]" />

          <div className="absolute bottom-10 left-10 rounded-3xl border border-white/10 bg-black/60 p-5 shadow-2xl backdrop-blur-md">
            <p className="text-xs font-bold uppercase tracking-[0.24em] text-primary">
              100% free.
            </p>
            <p className="mt-2 max-w-xs text-lg font-semibold text-white">
              Made by comedy nerds and Reddit consensus.
            </p>
            <p className="mt-1 text-sm text-stone-300">
              Explore playlists of comedians, episodes, and jokes. 
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
