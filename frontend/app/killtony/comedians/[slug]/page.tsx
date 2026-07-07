import { Suspense } from "react";
import { notFound } from "next/navigation";
import { getServerComedian } from "@/lib/serverApi";
import Breadcrumbs from "@/components/Breadcrumbs";
import ComedianImage from "@/components/ComedianImage";
import { ATTRIBUTE_LABELS } from "@/lib/attributes";
import { fmt2 } from "@/lib/killTonyDisplay";
import { getComedianIntroSummary } from "@/lib/killTonySummaries";
import { buildMetadata } from "@/lib/seo";
import ComedianSetList from "./ComedianSetList";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  const comedian = await getServerComedian(slug);
  if (!comedian) return { title: "Comedian Not Found | PunchNotes" };
  const introSummary = getComedianIntroSummary(comedian);
  return buildMetadata({
    title: `${comedian.name} — Kill Tony | PunchNotes`,
    description: introSummary,
    canonicalPath: `/killtony/comedians/${comedian.slug}`,
    image: comedian.image_url,
  });
}

export default async function ComedianDetailPage({ params }: Props) {
  const { slug } = await params;
  const comedian = await getServerComedian(slug);
  if (!comedian) notFound();

  const sets =[...(comedian.sets ?? [])].sort(
    (a, b) => b.video.number - a.video.number
  );
  const introSummary = getComedianIntroSummary(comedian);
  const hideJokeBookAttributes =
    comedian.attributes.includes("golden_ticket") || comedian.attributes.includes("regular");

  return (
    <div className="bg-white min-h-screen">
      {/* Dark hero */}
      <div className="bg-stone-900 text-white">
        <div className="mx-auto max-w-5xl px-6 py-10">
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
                {comedian.name}
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

              <p className="mb-5 max-w-3xl text-sm leading-6 text-stone-300">
                {introSummary}
              </p>

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

      {/* Set history */}
      <div className="mx-auto max-w-5xl px-6 py-10">
        <h2 className="mb-4 text-lg font-semibold text-stone-900">Set history</h2>
        {sets.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No sets indexed yet.</p>
          </div>
        ) : (
          <Suspense>
            <ComedianSetList sets={sets} comedianName={comedian.name} />
          </Suspense>
        )}
      </div>
    </div>
  );
}
