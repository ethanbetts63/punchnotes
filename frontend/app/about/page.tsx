import Link from "next/link";
import { BookOpen, ExternalLink, Mic2, Search, Sparkles } from "lucide-react";

export const metadata = {
  title: "About - PunchNotes",
  description:
    "What PunchNotes is, why it exists, and how the Kill Tony archive is organized.",
};

const otherSites = [
  {
    name: "Site name",
    description: "A short one-line description of the other project goes here.",
    href: "#",
  },
  {
    name: "Another site",
    description: "Use this space for the second related project.",
    href: "#",
  },
  {
    name: "Third project",
    description: "Optional third card if you want to point people somewhere else.",
    href: "#",
  },
];

const useCases = [
  {
    title: "For fans",
    description:
      "Find memorable sets, trace running bits, and jump back into jokes without digging through full episodes.",
    icon: <Search className="h-5 w-5" />,
  },
  {
    title: "For comics",
    description:
      "Study how short sets are built, where premises turn, and how crowds respond to different joke shapes.",
    icon: <Mic2 className="h-5 w-5" />,
  },
  {
    title: "For comedy nerds",
    description:
      "Explore patterns across performers, episodes, joke types, and audience reactions.",
    icon: <BookOpen className="h-5 w-5" />,
  },
];

function SectionHeading({
  eyebrow,
  title,
}: {
  eyebrow: string;
  title: string;
}) {
  return (
    <div>
      <p className="text-xs font-bold uppercase tracking-[0.22em] text-primary">
        {eyebrow}
      </p>
      <h2 className="mt-2 text-2xl font-bold tracking-tight text-stone-950 sm:text-3xl">
        {title}
      </h2>
    </div>
  );
}

export default function AboutPage() {
  return (
    <div className="bg-white">
      <section className="border-b border-stone-200 bg-stone-950 px-4 py-16 text-white sm:px-6 sm:py-20">
        <div className="mx-auto max-w-5xl">
          <div className="max-w-3xl">
            <p className="text-xs font-bold uppercase tracking-[0.24em] text-primary">
              Made by fans. Free to use.
            </p>
            <h1 className="mt-4 text-4xl font-black tracking-tight sm:text-5xl">
              About PunchNotes
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-relaxed text-stone-300">
              PunchNotes is a fan-made archive for exploring Kill Tony sets,
              comedians, episodes, jokes, transcripts, playlists, and comedy
              structure in one place.
            </p>
          </div>
        </div>
      </section>

      <section className="border-b border-stone-200 px-4 py-14 sm:px-6">
        <div className="mx-auto grid max-w-5xl gap-10 lg:grid-cols-[minmax(0,1fr)_320px]">
          <div className="max-w-2xl">
            <SectionHeading
              eyebrow="The idea"
              title="A searchable map of short-form stand-up"
            />
            <div className="mt-6 space-y-5 text-base leading-relaxed text-stone-600">
              <p>
                Kill Tony has become a huge living archive of comics trying
                ideas in public. The show is funny as entertainment, but it is
                also useful as a record of how jokes are introduced, shaped,
                recovered, abandoned, or sharpened in front of a real crowd.
              </p>
              <p>
                PunchNotes tries to make that archive easier to explore. Instead
                of only searching by episode or guest, you can browse comedians,
                individual sets, joke beats, transcripts, and playlists built
                around the moments people actually want to find again.
              </p>
            </div>
          </div>

          <aside className="rounded-lg border border-stone-200 bg-stone-50 p-5">
            <div className="flex h-11 w-11 items-center justify-center rounded-md bg-primary/10 text-primary">
              <Sparkles className="h-5 w-5" />
            </div>
            <h2 className="mt-4 text-lg font-bold text-stone-950">
              What the notes are for
            </h2>
            <p className="mt-3 text-sm leading-6 text-stone-600">
              The labels and breakdowns are meant to help people notice
              structure. They are not meant to flatten comedy into a formula or
              declare one official reading of a joke.
            </p>
          </aside>
        </div>
      </section>

      <section className="border-b border-stone-200 bg-stone-50 px-4 py-14 sm:px-6">
        <div className="mx-auto max-w-5xl">
          <SectionHeading eyebrow="Letter" title="A note from the developer" />
          <div className="mt-6 max-w-3xl rounded-lg border border-stone-200 bg-white p-6 text-base leading-relaxed text-stone-600 shadow-sm sm:p-8">
            <p>
              I built PunchNotes because I kept wanting a better way to study
              the mechanics of comedy without losing the fun of watching it.
              Stand-up is alive in the room, and the best moments are often
              messy, surprising, and hard to categorize. That is exactly why I
              wanted a tool that could help organize the material without
              pretending the organization is the whole point.
            </p>
            <p className="mt-5">
              The goal is simple: make it easier to find sets, follow comics,
              revisit jokes, and notice patterns in how premises become laughs.
              Sometimes that means a transcript. Sometimes it means a playlist.
              Sometimes it means breaking a joke into smaller beats so the turn
              is easier to see.
            </p>
            <p className="mt-5">
              This is a fan project first. It exists because the archive is
              worth exploring, and because comedy fans, writers, and performers
              all benefit from better ways to search, compare, and revisit the
              work.
            </p>
          </div>
        </div>
      </section>

      <section className="border-b border-stone-200 px-4 py-14 sm:px-6">
        <div className="mx-auto max-w-5xl">
          <SectionHeading eyebrow="Who it helps" title="Different ways in" />
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {useCases.map((item) => (
              <div
                key={item.title}
                className="rounded-lg border border-stone-200 bg-white p-5"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-md bg-stone-950 text-white">
                  {item.icon}
                </div>
                <h2 className="mt-4 text-lg font-bold text-stone-950">
                  {item.title}
                </h2>
                <p className="mt-2 text-sm leading-6 text-stone-600">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="border-b border-stone-200 bg-stone-950 px-4 py-14 text-white sm:px-6">
        <div className="mx-auto max-w-5xl">
          <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
            <SectionHeading eyebrow="More projects" title="Check out our other sites" />
            <p className="max-w-md text-sm leading-6 text-stone-400">
              Replace these cards with the other sites you want to promote. This
              section can stay small and direct.
            </p>
          </div>

          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {otherSites.map((site) => (
              <Link
                key={site.name}
                href={site.href}
                className="group rounded-lg border border-white/10 bg-white/5 p-5 transition-colors hover:border-primary/60 hover:bg-white/10"
              >
                <div className="flex items-start justify-between gap-4">
                  <h2 className="text-lg font-bold text-white">{site.name}</h2>
                  <ExternalLink className="mt-1 h-4 w-4 shrink-0 text-stone-500 transition-colors group-hover:text-primary" />
                </div>
                <p className="mt-3 text-sm leading-6 text-stone-400">
                  {site.description}
                </p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="px-4 py-12 sm:px-6">
        <div className="mx-auto max-w-5xl">
          <div className="max-w-3xl text-sm leading-6 text-stone-500">
            <h2 className="text-lg font-bold text-stone-950">
              Independent fan-made archive
            </h2>
            <p className="mt-3">
              PunchNotes is not affiliated with Kill Tony, the hosts, guests,
              production team, or any official channel. The site is an
              independent fan-made archive and analysis project.
            </p>
            <p className="mt-3">
              If something is missing, mislabeled, or transcribed incorrectly,
              the best version of this page should eventually include a simple
              way to send corrections.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
