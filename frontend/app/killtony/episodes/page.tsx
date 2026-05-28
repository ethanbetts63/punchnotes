import Link from "next/link";
import { getServerEpisodes } from "@/lib/serverApi";

export const metadata = {
  title: "Episodes — Kill Tony | JokeScore",
};

export default async function EpisodesPage() {
  const episodes = await getServerEpisodes();

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-stone-900">Episodes</h1>
          <p className="mt-2 text-stone-500">
            {episodes ? `${episodes.length} episodes indexed` : "Loading episodes…"}
          </p>
        </div>

        {!episodes || episodes.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No episodes indexed yet.</p>
          </div>
        ) : (
          <div className="divide-y divide-stone-100 rounded-xl border border-stone-200">
            {episodes.map((ep) => (
              <Link
                key={ep.id}
                href={`/killtony/episodes/${ep.id}`}
                className="flex items-center justify-between px-5 py-4 hover:bg-stone-50 transition-colors"
              >
                <div>
                  <span className="text-xs font-medium text-stone-400 uppercase tracking-wide">
                    Episode {ep.number}
                  </span>
                  <p className="mt-0.5 font-medium text-stone-900">
                    {ep.title || `Kill Tony #${ep.number}`}
                  </p>
                  <p className="text-sm text-stone-400">{ep.date}</p>
                </div>
                <div className="text-sm text-stone-400">
                  {ep.set_count} sets →
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
