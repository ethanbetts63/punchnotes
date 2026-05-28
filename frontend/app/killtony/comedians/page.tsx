import Link from "next/link";
import { getServerComedians } from "@/lib/serverApi";

export const metadata = {
  title: "Comedians — Kill Tony | JokeScore",
};

export default async function ComediansPage() {
  const comedians = await getServerComedians();

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-stone-900">Comedians</h1>
          <p className="mt-2 text-stone-500">
            {comedians ? `${comedians.length} comedians` : "Loading…"}
          </p>
        </div>

        {!comedians || comedians.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No comedians indexed yet.</p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {comedians.map((c) => (
              <Link
                key={c.id}
                href={`/killtony/comedians/${c.slug}`}
                className="group rounded-xl border border-stone-200 bg-white p-5 hover:border-primary/40 hover:shadow-sm transition-all"
              >
                <p className="font-semibold text-stone-900 group-hover:text-primary transition-colors">
                  {c.name}
                </p>
                <p className="mt-1 text-sm text-stone-400">
                  {c.appearances} appearance{c.appearances !== 1 ? "s" : ""} · {c.set_count} set{c.set_count !== 1 ? "s" : ""}
                </p>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
