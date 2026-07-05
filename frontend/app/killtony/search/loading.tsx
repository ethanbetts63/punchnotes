import { Loader2 } from "lucide-react";

export default function SearchLoading() {
  return (
    <div className="min-h-screen bg-[#f7f7f7] text-black">
      <section className="bg-[#f7f7f7] text-black">
        <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
          <h1 className="text-center text-4xl font-bold leading-none tracking-normal text-black sm:text-5xl">
            Search
          </h1>
          <p className="mt-3 text-center text-sm font-bold uppercase text-stone-500">Loading results</p>
        </div>
      </section>

      <div className="mx-auto flex max-w-6xl items-center justify-center px-6 py-24">
        <Loader2 className="h-8 w-8 animate-spin text-stone-400" />
      </div>
    </div>
  );
}
