import Link from "next/link";
import { ArrowRight, BookOpen, Mic2, Search, Sparkles } from "lucide-react";
import { SITE_URL, SITE_NAME, buildBreadcrumbSchema } from "@/lib/seo";

export const metadata = {
  title: "About - PunchNotes",
  description:
    "What PunchNotes is, why it exists, and how the Kill Tony archive is organized.",
};

const otherSites = [
  {
    name: "Splitcart",
    logoSrc: "/other-sites/splitcart_logo.png",
    description: "Compare grocery prices across major Australian supermarkets.",
    url: "https://www.splitcart.com.au",
  },
  {
    name: "FutureFlower",
    logoSrc: "/other-sites/futureflower_logo.png",
    description: "Flower delivery and subscription service.",
    url: "https://www.futureflower.app",
  },
  {
    name: "Scooter Shop",
    logoSrc: "/other-sites/scootershop_logo.webp",
    description: "Motorcycle and scooter sales, servicing, tyre fitting, and hire in Perth.",
    url: "https://www.scootershop.com.au",
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

const aboutSchema = {
  '@context': 'https://schema.org',
  '@type': 'AboutPage',
  name: 'About PunchNotes',
  description: 'What PunchNotes is, why it exists, and how the Kill Tony archive is organized.',
  url: `${SITE_URL}/about`,
  breadcrumb: buildBreadcrumbSchema([
    { name: 'Kill Tony', item: `${SITE_URL}/killtony` },
    { name: 'About', item: `${SITE_URL}/about` },
  ]),
  publisher: {
    '@type': 'Organization',
    name: SITE_NAME,
    url: SITE_URL,
  },
};

export default function AboutPage() {
  return (
    <>
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(aboutSchema) }}
    />
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
              I built PunchNotes for three reasons. The first is simple: people
              ask me all the time where to start with Kill Tony. They want to
              watch the show, but there are hundreds of episodes, and "just
              watch the latest one" is not a great answer. I wanted somewhere I
              could send people that pointed them toward banger episodes,
              standout sets, and the moments that actually explain why fans love
              the show.
            </p>
            <p className="mt-5">
              The second reason is search. If I am trying to remember which
              comic did a joke, what episode a set was on, or the exact wording
              of a line, there has never been a good way to find it. You can
              search YouTube titles, skim Reddit threads, or hope someone else
              remembers, but that does not help much when the thing you remember
              is buried inside a minute. PunchNotes is meant to make the archive
              searchable at the set and transcript level.
            </p>
            <p className="mt-5">
              The third reason is joke originality. This part may or may not be
              live yet when you are reading this, but it is a big part of where
              the project is going. When I write a joke I think is good, I want
              to know, with some degree of confidence, whether someone else has
              already done something similar. Right now the best tools are
              pretty bad: perform it and hope someone tells you, or Google a few
              phrases and hope..
            </p>

            <p className="mt-5">
              At its core, PunchNotes is for comedy fans and comedy nerds. And it's a work in progress. I hope it's useful and if you'd like to reach out or contribute I'll sign my personal email below. I'd love to hear from you.
            </p>
            <div className="mt-6 border-t border-stone-200 pt-5">
              <p className="font-semibold text-stone-950">Ethan Betts</p>
              <a
                href="mailto:ethanbetts63@gmail.com"
                className="text-sm font-medium text-primary transition-opacity hover:opacity-80"
              >
                ethanbetts63@gmail.com
              </a>
            </div>
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

      <section className="border-b border-stone-200 bg-white px-4 py-14 sm:px-6">
        <div className="mx-auto max-w-5xl">
          <h2 className="mb-8 text-center text-3xl font-bold text-stone-950">
            Liked this site? Check out some of our others!
          </h2>
          <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {otherSites.map((site) => (
              <div
                key={site.name}
                className="flex h-full flex-col rounded-lg border border-stone-200 bg-white p-6 shadow-sm"
              >
                <div className="mb-4 flex items-center">
                  <div className="mr-4 h-16 w-16 shrink-0">
                    <img
                      src={site.logoSrc}
                      alt={`${site.name} Logo`}
                      className="h-full w-full object-contain"
                    />
                  </div>
                  <div className="grow">
                    <h3 className="text-xl font-bold text-stone-950">
                      {site.name}
                    </h3>
                  </div>
                </div>
                <p className="mb-6 grow text-sm leading-6 text-stone-600">
                  {site.description}
                </p>
                <div className="mt-auto flex justify-end">
                  <a
                    href={site.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-primary/80"
                  >
                    Visit Site <ArrowRight className="h-4 w-4" />
                  </a>
                </div>
              </div>
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
    </>
  );
}
