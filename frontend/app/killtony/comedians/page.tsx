import { Suspense } from "react";
import { getServerComedians } from "@/lib/serverApi";
import ComedianControls from "@/components/ComedianControls";

export const metadata = {
  title: "Comedians — Kill Tony | PunchPedia",
};

type Props = { searchParams: Promise<Record<string, string | string[] | undefined>> };

export default async function ComediansPage({ searchParams }: Props) {
  const params = await searchParams;
  const rawQuery = params.q;
  const query = Array.isArray(rawQuery) ? rawQuery[0] ?? "" : rawQuery ?? "";
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
          <Suspense>
            <ComedianControls comedians={comedians} initialQuery={query} />
          </Suspense>
        )}
      </div>
    </div>
  );
}
