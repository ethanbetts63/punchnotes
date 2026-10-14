import Link from "next/link";
import { notFound } from "next/navigation";
import { getServerComedian, getServerComedians } from "@/lib/serverApi";
import type { SetInComedian } from "@/lib/serverApi";
import Breadcrumbs from "@/components/Breadcrumbs";
import ComedianImage from "@/components/ComedianImage";
import { ATTRIBUTE_LABELS } from "@/lib/attributes";
import { combineConsecutiveSetupLines } from "@/lib/annotatedBeatCards";
import { fmt2, fmtDate, getEpisodeGuests, getJokeBookSize, jokeBookLabel, lineLabelBadge } from "@/lib/killTonyDisplay";
import { getComedianFacts, getComedianIntroSummary, getComedianTitle } from "@/lib/killTonySummaries";
import { SITE_URL, buildBreadcrumbSchema, buildMetadata, isIndexedComedian } from "@/lib/seo";

type Props = { params: Promise<{ slug: string }> };

// The joke section shows the latest sets only; the appearance table above it lists every one.
const JOKE_SETS_SHOWN = 10;

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  const comedian = await getServerComedian(slug);
  if (!comedian) return { title: "Comedian Not Found | PunchNotes" };
  return buildMetadata({
    title: getComedianTitle(comedian),
    description: getComedianIntroSummary(comedian),
    canonicalPath: `/killtony/comedians/${comedian.slug}`,
    image: comedian.image_url,
    noindex: !isIndexedComedian(comedian),
  });
}

function episodeTitle(set: SetInComedian): string {
  return set.video.title?.replace(/^KT\s*#\d+\s*[-–]\s*/i, "") || `KT #${set.video.number}`;
}

export default async function ComedianDetailPage({ params }: Props) {
  const { slug } = await params;
  const [comedian, peers] = await Promise.all([getServerComedian(slug), getServerComedians()]);
  if (!comedian) notFound();

  const sets = [...(comedian.sets ?? [])].sort((a, b) => b.video.number - a.video.number);
  const facts = getComedianFacts(comedian, peers);
  const jokeSets = sets.filter((set) => set.sample_jokes?.length).slice(0, JOKE_SETS_SHOWN);
  const hideJokeBookAttributes =
    comedian.attributes.includes("golden_ticket") || comedian.attributes.includes("regular");
  const pageUrl = `${SITE_URL}/killtony/comedians/${comedian.slug}`;

  const schema = {
    "@context": "https://schema.org",
    "@type": "ProfilePage",
    url: pageUrl,
    name: getComedianTitle(comedian).replace(/ \| PunchNotes$/, ""),
    mainEntity: {
      "@type": "Person",
      name: comedian.name,
      url: pageUrl,
      jobTitle: "Stand-up comedian",
      description: facts.slice(0, 2).join(" "),
      ...(comedian.image_url ? { image: comedian.image_url } : {}),
    },
    breadcrumb: buildBreadcrumbSchema([
      { name: "Kill Tony", item: `${SITE_URL}/killtony` },
      { name: "Comedians", item: `${SITE_URL}/killtony/comedians` },
      { name: comedian.name, item: pageUrl },
    ]),
  };

  return (
    <div className="bg-white min-h-screen">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schema).replace(/</g, "\\u003c") }}
      />

      {/* Dark hero */}
      <div className="bg-stone-900 text-white">
        <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
          <Breadcrumbs
            tone="dark"
            className="mb-6"
            items={[
              { label: "Kill Tony", href: "/killtony" },
              { label: "Comedians", href: "/killtony/comedians" },
              { label: comedian.name },
            ]}
          />
          <div className="flex gap-8 items-start">

            <ComedianImage
              imageUrl={comedian.image_url}
              name={comedian.name}
              className="hidden aspect-video w-36 shrink-0 rounded-lg bg-stone-800 shadow-xl ring-1 ring-white/10 sm:block md:w-48"
            />

            {/* Info */}
            <div className="flex-1 min-w-0">
              <h1 className="text-3xl md:text-4xl font-bold text-white mb-1">
                {comedian.name} on Kill Tony
              </h1>

              <div className="flex flex-wrap gap-1.5 mb-5">
                {comedian.attributes
                  .filter((attr) => attr in ATTRIBUTE_LABELS)
                  .map((attr) => (
                    <span key={attr} className="rounded-full bg-stone-700 px-2.5 py-0.5 text-xs font-medium text-stone-300">
                      {ATTRIBUTE_LABELS[attr]}
                    </span>
                  ))}
                {!hideJokeBookAttributes && comedian.has_small_joke_book && (
                  <span className="rounded-full px-2.5 py-0.5 text-xs font-medium bg-stone-100 text-stone-500">
                    Small Joke Book
                  </span>
                )}
                {!hideJokeBookAttributes && comedian.has_medium_joke_book && (
                  <span className="rounded-full px-2.5 py-0.5 text-xs font-medium bg-amber-100 text-amber-700">
                    Medium Joke Book
                  </span>
                )}
                {!hideJokeBookAttributes && comedian.has_large_joke_book && (
                  <span className="rounded-full px-2.5 py-0.5 text-xs font-medium bg-red-100 text-primary">
                    Big Joke Book
                  </span>
                )}
              </div>

              {/* Stats */}
              <p className="text-sm text-stone-400">
                <span className="text-white">{comedian.set_count}</span> set{comedian.set_count !== 1 ? "s" : ""}
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{fmt2(comedian.avg_bits_per_set)}</span> bits/set
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{fmt2(comedian.avg_beats_per_set)}</span> beats/set
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{fmt2(comedian.avg_punch_density)}</span> punch density
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{fmt2(comedian.avg_tag_density)}</span> tag density
              </p>
            </div>

          </div>
        </div>
      </div>

      <div className="mx-auto max-w-5xl space-y-12 px-4 py-10 sm:px-6">
        {/* Facts */}
        <section>
          <h2 className="mb-3 text-lg font-semibold text-stone-900">About {comedian.name}&apos;s sets</h2>
          <div className="max-w-3xl space-y-3 text-sm leading-6 text-stone-700">
            {facts.map((fact) => (
              <p key={fact}>{fact}</p>
            ))}
          </div>
        </section>

        {/* Appearances */}
        <section>
          <h2 className="mb-4 text-lg font-semibold text-stone-900">Appearances</h2>
          {sets.length === 0 ? (
            <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
              <p className="text-stone-500">No sets indexed yet.</p>
            </div>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-stone-200">
              <table className="w-full min-w-[640px] text-left text-sm">
                <thead className="bg-stone-50 text-xs uppercase tracking-wide text-stone-500">
                  <tr>
                    <th scope="col" className="px-4 py-3 font-semibold">Episode</th>
                    <th scope="col" className="px-4 py-3 font-semibold">Date</th>
                    <th scope="col" className="px-4 py-3 font-semibold">Guest panel</th>
                    <th scope="col" className="px-4 py-3 text-right font-semibold">Bits</th>
                    <th scope="col" className="px-4 py-3 text-right font-semibold">Punch density</th>
                    <th scope="col" className="px-4 py-3 text-right font-semibold">Tag density</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100">
                  {sets.map((set) => {
                    const jokeBook = getJokeBookSize(set.attributes);
                    const guests = getEpisodeGuests(set.video);
                    return (
                      <tr key={set.id} className="align-top">
                        <td className="px-4 py-3">
                          <Link href={`/killtony/sets/${set.slug}`} className="font-semibold text-stone-900 hover:text-primary">
                            KT #{set.video.number}
                          </Link>
                          {jokeBook && (
                            <span className="ml-2 rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-700">
                              {jokeBookLabel[jokeBook]}
                            </span>
                          )}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 text-stone-600">{fmtDate(set.video.date) || "-"}</td>
                        <td className="px-4 py-3 text-stone-600">{guests.length ? guests.join(", ") : episodeTitle(set)}</td>
                        <td className="px-4 py-3 text-right tabular-nums text-stone-900">{set.bit_count}</td>
                        <td className="px-4 py-3 text-right tabular-nums text-stone-900">{fmt2(set.punch_density)}</td>
                        <td className="px-4 py-3 text-right tabular-nums text-stone-900">{fmt2(set.tag_density)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* Sample jokes */}
        {jokeSets.length > 0 && (
          <section>
            <h2 className="mb-1 text-lg font-semibold text-stone-900">Jokes from {comedian.name}&apos;s sets</h2>
            <p className="mb-6 text-sm text-stone-500">
              A few jokes from each {jokeSets.length < sets.length ? `of the latest ${jokeSets.length} sets` : "set"}.
              Open a set for the full transcript and every joke.
            </p>
            <div className="space-y-8">
              {jokeSets.map((set) => (
                <div key={set.id}>
                  <h3 className="mb-3 text-sm font-semibold text-stone-900">
                    <Link href={`/killtony/sets/${set.slug}`} className="hover:text-primary">
                      KT #{set.video.number}
                    </Link>
                    {set.video.date && <span className="ml-2 font-normal text-stone-500">{fmtDate(set.video.date)}</span>}
                  </h3>
                  <div className="grid gap-4 md:grid-cols-2">
                    {set.sample_jokes!.map((joke) => (
                      <div key={joke.beat_id} className="rounded-lg border border-stone-200 bg-white p-4 shadow-sm">
                        {joke.joke_type && (
                          <span className="mb-3 inline-block rounded-full bg-stone-950 px-2 py-0.5 text-[10px] font-bold text-white">
                            {joke.joke_type}
                          </span>
                        )}
                        <div className="space-y-1.5">
                          {combineConsecutiveSetupLines(
                            joke.lines.map((line, index) => ({ id: index, label: line.label, text: line.text })),
                          ).map((line) => (
                            <div key={line.id} className="flex gap-2 text-sm leading-snug">
                              <span className={`mt-0.5 w-20 shrink-0 rounded px-2 py-0.5 text-center text-[10px] font-bold uppercase ${lineLabelBadge[line.label]}`}>
                                {line.label}
                              </span>
                              <p className={line.label === "punchline" ? "font-bold text-stone-950" : "text-stone-700"}>
                                {line.text}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
