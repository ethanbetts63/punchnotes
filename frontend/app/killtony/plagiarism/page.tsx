import { Suspense } from "react";
import PlagiarismChecker from "./PlagiarismChecker";

export const metadata = {
  title: "Joke Similarity Check - Kill Tony | PunchNotes",
};

export default function PlagiarismPage() {
  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6">
        <h1 className="mb-2 text-3xl font-black tracking-tight text-stone-950">
          Joke Similarity Check
        </h1>
        <p className="mb-8 text-stone-500">
          Paste a joke below to find the most similar jokes in the Kill Tony database.
        </p>
        <Suspense>
          <PlagiarismChecker />
        </Suspense>
      </div>
    </div>
  );
}
