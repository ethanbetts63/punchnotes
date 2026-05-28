import { notFound } from "next/navigation";
import Link from "next/link";
import { getServerComedian } from "@/lib/serverApi";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  const comedian = await getServerComedian(slug);
  if (!comedian) return { title: "Comedian Not Found | JokeScore" };
  return {
    title: `${comedian.name} — Kill Tony | JokeScore`,
  };
}

export default async function ComedianDetailPage({ params }: Props) {
  const { slug } = await params;
  const comedian = await getServerComedian(slug);
  if (!comedian) notFound();

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-2 text-sm text-stone-400">
          <Link href="/killtony/comedians" className="hover:text-stone-600 transition-colors">
            ← Comedians
          </Link>
        </div>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-stone-900">{comedian.name}</h1>
          <p className="mt-2 text-stone-500">
            {comedian.appearances} appearance{comedian.appearances !== 1 ? "s" : ""} · {comedian.set_count} set{comedian.set_count !== 1 ? "s" : ""}
          </p>
        </div>

        <div className="rounded-xl border border-stone-200 bg-stone-50 p-8 text-center">
          <p className="text-stone-500">Set history and joke breakdown coming soon.</p>
        </div>
      </div>
    </div>
  );
}
