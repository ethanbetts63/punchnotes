import Image from "next/image";
import Link from "next/link";
import { Mic2, Search, Tv } from "lucide-react";
import type { ReactNode } from "react";

function BrowseButton({
  icon,
  title,
  detail,
  href,
  variant = "outline",
}: {
  icon: ReactNode;
  title: string;
  detail: string;
  href: string;
  variant?: "solid" | "outline";
}) {
  const variantClass =
    variant === "solid"
      ? "bg-primary hover:bg-primary/90"
      : "border border-white/10 bg-white/5 hover:bg-white/10";
  const iconWrapClass = variant === "solid" ? "bg-black/20" : "bg-white/10";

  return (
    <Link
      href={href}
      className={`flex items-center gap-3 rounded-2xl px-5 py-4 font-semibold text-white backdrop-blur-sm transition-transform hover:scale-[1.02] ${variantClass}`}
    >
      <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${iconWrapClass}`}>
        {icon}
      </span>
      <span className="text-left">
        <span className="block text-base leading-tight sm:text-sm">{title}</span>
        <span className="hidden text-xs font-normal text-white/80 sm:block">
          {detail}
        </span>
      </span>
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

      <h1 className="font-display text-5xl font-black tracking-tight text-white sm:text-6xl lg:text-[5.5rem]">
        The Kill Tony Archive
      </h1>

      <p className="mt-5 text-base leading-relaxed text-stone-300 sm:text-lg">
        Browse curated Kill Tony playlists or deepdive the archive to search your favorite sets, comedians, and jokes.
      </p>

      <div className="mt-8 grid grid-cols-2 gap-3">
        <BrowseButton
          icon={<Tv className="h-5 w-5" />}
          title="Browse Episodes"
          detail="Fan made playlists and search."
          href="/killtony/episodes"
          variant="solid"
        />
        <BrowseButton
          icon={<Search className="h-5 w-5" />}
          title="Browse Jokes"
          detail="Set transcripts, seachable and annotated."
          href="/killtony/jokes"
        />
        <BrowseButton
          icon={<Mic2 className="h-5 w-5" />}
          title="Browse Comedians"
          detail="Track regulars, bucket pulls, and standout appearances."
          href="/killtony/comedians"
        />
        <BrowseButton
          icon={<Search className="h-5 w-5" />}
          title="Browse Sets"
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

        <div className="bg-[radial-gradient(ellipse_at_top,rgba(180,20,20,0.18),transparent_55%),linear-gradient(180deg,#080b13_0%,#0d1018_100%)] px-6 py-10">
          {content}
        </div>
      </div>

      <div className="relative hidden overflow-hidden md:flex" style={{ minHeight: "clamp(580px, 86vh, 840px)" }}>
        <div className="relative flex w-1/2 items-center justify-center overflow-hidden px-10 py-16 lg:px-20">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,rgba(200,30,30,0.20),transparent_45%),linear-gradient(180deg,#080b13_0%,#0d1018_100%)]" />
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
