"use client";

import { Loader2 } from "lucide-react";
import { useSearchTransition } from "@/components/SearchTransition";

export function ResultsLoading() {
  return (
    <div className="flex items-center justify-center py-24">
      <Loader2 className="h-8 w-8 animate-spin text-stone-400" />
    </div>
  );
}

export default function SearchResults({ children }: { children: React.ReactNode }) {
  const { isPending } = useSearchTransition();
  if (isPending) return <ResultsLoading />;
  return <>{children}</>;
}
